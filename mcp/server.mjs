#!/usr/bin/env node
/**
 * mango-tools — MCP server for the software-development-best-practices-guide.
 *
 * Serves the guide's knowledge (reference docs, checklists, patterns, the AGENTS.md
 * template) as MCP resources + tools so any Claude Code / Codex / Gemini session can
 * query the single shared source instead of copying files into each project.
 *
 * Register once (user scope). Reliable form (after `npm i -g @matthewkerns/software-development-best-practices-guide`):
 *   claude mcp add mango-tools --scope user -- mango-tools
 * Or without a global install (resolves the named bin from the package via npx):
 *   claude mcp add mango-tools --scope user -- npx -y -p @matthewkerns/software-development-best-practices-guide mango-tools
 *
 * Tools are the workhorse (always available). Resource registration is wrapped so a
 * minor SDK API drift can't prevent the server from starting.
 */

import { McpServer, ResourceTemplate } from "@modelcontextprotocol/sdk/server/mcp.js";
import { StdioServerTransport } from "@modelcontextprotocol/sdk/server/stdio.js";
import { z } from "zod";
import { readFileSync, readdirSync, statSync, existsSync } from "node:fs";
import { join, relative, dirname, sep } from "node:path";
import { fileURLToPath } from "node:url";
import yaml from "js-yaml";

const __dirname = dirname(fileURLToPath(import.meta.url));
const GUIDE_ROOT = join(__dirname, "..");

const SECTION_DIRS = [
  "01-foundations",
  "02-design-in-code",
  "03-clean-architecture",
  "04-quality-through-testing",
  "05-refactoring-and-improvement",
  "06-collaborative-construction",
  "07-agentic-coding",
  "08-project-management",
  "09-production-readiness",
  "10-geist-gap-analysis-framework",
  "99-reference",
  "agentic-tooling",
];

const MAX_TEXT = 12000; // cap returned file bodies to keep responses lean

/** Recursively collect *.md files under a directory, returned as guide-relative paths. */
function walkMarkdown(absDir, acc = []) {
  if (!existsSync(absDir)) return acc;
  for (const entry of readdirSync(absDir)) {
    if (entry.startsWith(".") || entry === "node_modules") continue;
    const abs = join(absDir, entry);
    const st = statSync(abs);
    if (st.isDirectory()) walkMarkdown(abs, acc);
    else if (entry.endsWith(".md")) acc.push(relative(GUIDE_ROOT, abs));
  }
  return acc;
}

/** All markdown files the guide exposes, as guide-relative paths. */
function allGuideDocs() {
  const docs = [];
  for (const d of SECTION_DIRS) walkMarkdown(join(GUIDE_ROOT, d), docs);
  return docs.sort();
}

/** Safe read of a guide-relative path; refuses to escape GUIDE_ROOT. */
function readGuideFile(relPath) {
  const clean = relPath.replace(/^[/\\]+/, "");
  const abs = join(GUIDE_ROOT, clean);
  if (!abs.startsWith(GUIDE_ROOT + sep) && abs !== GUIDE_ROOT) {
    throw new Error(`Path escapes guide root: ${relPath}`);
  }
  if (!existsSync(abs) || !statSync(abs).isFile()) {
    throw new Error(`Not found: ${relPath}`);
  }
  const body = readFileSync(abs, "utf8");
  return body.length > MAX_TEXT
    ? body.slice(0, MAX_TEXT) + `\n\n…[truncated ${body.length - MAX_TEXT} chars — read the file directly for the rest]`
    : body;
}

/** First markdown heading or first non-empty line, used as a summary. */
function firstLine(relPath) {
  try {
    const body = readFileSync(join(GUIDE_ROOT, relPath), "utf8");
    const h = body.split("\n").find((l) => l.startsWith("#"));
    return (h || body.split("\n").find((l) => l.trim()) || relPath).replace(/^#+\s*/, "").trim();
  } catch {
    return relPath;
  }
}

/** Keyword score of a file for a query (title matches weigh more than body). */
function scoreDoc(relPath, terms) {
  let body = "";
  try {
    body = readFileSync(join(GUIDE_ROOT, relPath), "utf8").toLowerCase();
  } catch {
    return 0;
  }
  const name = relPath.toLowerCase();
  let score = 0;
  for (const t of terms) {
    if (!t) continue;
    if (name.includes(t)) score += 10;
    const matches = body.split(t).length - 1;
    score += Math.min(matches, 20);
  }
  return score;
}

const server = new McpServer({ name: "mango-tools", version: "1.5.0" });

/* ----------------------------- Tools ----------------------------- */

server.tool(
  "list_patterns",
  "List everything the best-practices guide offers: reference sections, skills, agents, agentic-tooling templates, and quick-reference checklists. Call this first to discover what's available.",
  {},
  async () => {
    const sections = SECTION_DIRS.filter((d) => existsSync(join(GUIDE_ROOT, d)));
    const skills = existsSync(join(GUIDE_ROOT, "skills"))
      ? readdirSync(join(GUIDE_ROOT, "skills")).filter((e) => statSync(join(GUIDE_ROOT, "skills", e)).isDirectory())
      : [];
    const agents = existsSync(join(GUIDE_ROOT, "agents"))
      ? readdirSync(join(GUIDE_ROOT, "agents")).filter((e) => e.endsWith(".md")).map((e) => e.replace(/\.md$/, ""))
      : [];
    const checklists = existsSync(join(GUIDE_ROOT, "99-reference"))
      ? readdirSync(join(GUIDE_ROOT, "99-reference")).filter((e) => e.endsWith(".md"))
      : [];
    const catalog = {
      sections,
      skills,
      agents,
      checklists,
      doc_count: allGuideDocs().length,
      usage: "Use get_best_practice(topic) to search, read_guide(path) to read a specific file, get_checklist(name) for a quick-reference, scaffold_agents_md() for the AGENTS.md template, validate_flag_registry(path) to lint a flag registry.",
    };
    return { content: [{ type: "text", text: JSON.stringify(catalog, null, 2) }] };
  }
);

server.tool(
  "get_best_practice",
  "Search the guide for a topic (e.g. 'error handling', 'variable naming', 'TDD', 'SOLID', 'feature flags', 'worktree'). Returns the best-matching document's content plus other relevant file paths.",
  { topic: z.string().describe("Topic or keywords to search for") },
  async ({ topic }) => {
    const terms = topic.toLowerCase().split(/\s+/).filter(Boolean);
    const ranked = allGuideDocs()
      .map((p) => ({ p, s: scoreDoc(p, terms) }))
      .filter((x) => x.s > 0)
      .sort((a, b) => b.s - a.s);
    if (ranked.length === 0) {
      return { content: [{ type: "text", text: `No guide document matched "${topic}". Try list_patterns to see available sections.` }] };
    }
    const top = ranked[0].p;
    const others = ranked.slice(1, 6).map((x) => `- ${x.p} — ${firstLine(x.p)}`).join("\n");
    const text = `# Best match: ${top}\n\n${readGuideFile(top)}\n\n---\n## Other relevant docs\n${others || "(none)"}`;
    return { content: [{ type: "text", text }] };
  }
);

server.tool(
  "read_guide",
  "Read a specific guide document by its guide-relative path (e.g. '01-foundations/VARIABLE_NAMING.md', '07-agentic-coding/AGENTS.template.md').",
  { path: z.string().describe("Guide-relative path to a .md file") },
  async ({ path }) => {
    try {
      return { content: [{ type: "text", text: readGuideFile(path) }] };
    } catch (e) {
      return { content: [{ type: "text", text: `Error: ${e.message}` }], isError: true };
    }
  }
);

server.tool(
  "get_checklist",
  "Return a quick-reference checklist from 99-reference/ by fuzzy name (e.g. 'code review', 'variable naming', 'tdd', 'function design').",
  { name: z.string().describe("Checklist name or keywords") },
  async ({ name }) => {
    const dir = join(GUIDE_ROOT, "99-reference");
    if (!existsSync(dir)) return { content: [{ type: "text", text: "No 99-reference directory found." }], isError: true };
    const files = readdirSync(dir).filter((e) => e.endsWith(".md"));
    const terms = name.toLowerCase().split(/\s+/).filter(Boolean);
    const best = files
      .map((f) => ({ f, s: terms.reduce((acc, t) => acc + (f.toLowerCase().includes(t) ? 1 : 0), 0) }))
      .sort((a, b) => b.s - a.s)[0];
    if (!best || best.s === 0) {
      return { content: [{ type: "text", text: `No checklist matched "${name}". Available:\n${files.map((f) => "- " + f).join("\n")}` }] };
    }
    return { content: [{ type: "text", text: readGuideFile(`99-reference/${best.f}`) }] };
  }
);

server.tool(
  "scaffold_agents_md",
  "Return the project-agnostic AGENTS.md template (plus the one-line CLAUDE.md pointer convention) to start an agent-instruction hierarchy in a new project.",
  { projectType: z.string().optional().describe("Optional hint, e.g. 'react+supabase', 'fastapi', 'cli' — used only to annotate the template") },
  async ({ projectType }) => {
    const tmpl = readGuideFile("07-agentic-coding/AGENTS.template.md");
    const note = projectType
      ? `\n\n<!-- requested projectType hint: ${projectType} — fill the <PLACEHOLDERS> accordingly -->\n`
      : "";
    const claudePointer = "Create a sibling CLAUDE.md whose ENTIRE contents are:\n\n    @AGENTS.md\n";
    return { content: [{ type: "text", text: `${claudePointer}\n---\n${tmpl}${note}` }] };
  }
);

server.tool(
  "validate_flag_registry",
  "Lint a feature-flag registry YAML file: checks required fields per flag and flags any release.* entry past its expires_at date. Pass an absolute path to the flag_registry.yaml.",
  { path: z.string().describe("Absolute path to a flag_registry.yaml") },
  async ({ path }) => {
    if (!existsSync(path)) return { content: [{ type: "text", text: `File not found: ${path}` }], isError: true };
    let doc;
    try {
      doc = yaml.load(readFileSync(path, "utf8"));
    } catch (e) {
      return { content: [{ type: "text", text: `YAML parse error: ${e.message}` }], isError: true };
    }
    const flags = Array.isArray(doc) ? doc : Array.isArray(doc?.flags) ? doc.flags : Object.values(doc || {});
    const required = ["name", "type", "owner", "description"];
    const findings = [];
    const now = new Date();
    for (const f of flags) {
      if (!f || typeof f !== "object") continue;
      const id = f.name || "(unnamed)";
      for (const r of required) if (!(r in f)) findings.push(`MISSING_FIELD: ${id} has no '${r}'`);
      const kind = String(f.type || "");
      if (kind.startsWith("release")) {
        if (!f.expires_at) findings.push(`MISSING_EXPIRY: release flag '${id}' needs expires_at`);
        else if (new Date(f.expires_at) < now) findings.push(`EXPIRED: release flag '${id}' expired ${f.expires_at} — renew or remove`);
      }
    }
    const summary = findings.length === 0
      ? `OK — ${flags.length} flag(s), no issues.`
      : `${findings.length} issue(s) across ${flags.length} flag(s):\n` + findings.map((x) => "- " + x).join("\n");
    return { content: [{ type: "text", text: summary }], isError: findings.some((f) => f.startsWith("EXPIRED")) };
  }
);

/* --------------------------- Resources --------------------------- */
/* Wrapped: tools above are the primary interface; resources are a bonus. */
try {
  server.resource(
    "guide-docs",
    new ResourceTemplate("guide:///{+path}", {
      list: async () => ({
        resources: allGuideDocs().map((p) => ({
          uri: `guide:///${p}`,
          name: p,
          description: firstLine(p),
          mimeType: "text/markdown",
        })),
      }),
    }),
    { title: "Best-Practices Guide Docs", description: "Markdown reference docs from the shared guide" },
    async (uri, variables) => {
      const p = Array.isArray(variables.path) ? variables.path.join("/") : variables.path;
      return { contents: [{ uri: uri.href, mimeType: "text/markdown", text: readGuideFile(p) }] };
    }
  );
} catch (e) {
  console.error(`[mango-tools] resource registration skipped: ${e.message}`);
}

/* ----------------------------- Boot ------------------------------ */
const transport = new StdioServerTransport();
await server.connect(transport);
console.error(`[mango-tools] ready — guide root: ${GUIDE_ROOT}`);
