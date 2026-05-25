#!/usr/bin/env node
/**
 * bpg-sync — project the guide's filesystem-discovered Claude Code tooling
 * (skills, agents, hooks) into a target .claude/ directory.
 *
 * MCP can't register skills/agents (Claude Code discovers those from the filesystem),
 * so this CLI symlinks them from the installed guide package into either the user-global
 * ~/.claude or a project's ./.claude. Symlinks (default) mean `npm update` propagates.
 *
 * Usage:
 *   bpg-sync --global                 # link into ~/.claude   (benefits every project)
 *   bpg-sync --project .              # link into ./.claude   (committed with the repo)
 *   bpg-sync --project /path/to/repo
 *   bpg-sync --global --only skills,agents
 *   bpg-sync --project . --only hooks --mode copy
 *
 * Flags:
 *   --global            target ~/.claude
 *   --project <path>    target <path>/.claude
 *   --only a,b,c        subset of {skills,agents,hooks} (default: all three)
 *   --mode symlink|copy default symlink
 *   --dry-run           print actions without changing the filesystem
 */

import {
  existsSync, mkdirSync, readdirSync, lstatSync, rmSync, symlinkSync,
  cpSync, chmodSync,
} from "node:fs";
import { join, dirname, resolve } from "node:path";
import { fileURLToPath } from "node:url";
import { homedir } from "node:os";

const PKG_ROOT = join(dirname(fileURLToPath(import.meta.url)), "..");

const CATEGORIES = {
  skills: { src: join(PKG_ROOT, "skills"), destName: "skills" },
  agents: { src: join(PKG_ROOT, "agents"), destName: "agents" },
  hooks: { src: join(PKG_ROOT, "agentic-tooling", "hooks"), destName: "hooks" },
};

function parseArgs(argv) {
  const args = { global: false, project: null, only: null, mode: "symlink", dryRun: false, skipExisting: false };
  for (let i = 0; i < argv.length; i++) {
    const a = argv[i];
    if (a === "--global") args.global = true;
    else if (a === "--project") args.project = argv[++i];
    else if (a === "--only") args.only = argv[++i].split(",").map((s) => s.trim()).filter(Boolean);
    else if (a === "--mode") args.mode = argv[++i];
    else if (a === "--skip-existing") args.skipExisting = true;
    else if (a === "--dry-run") args.dryRun = true;
    else if (a === "-h" || a === "--help") args.help = true;
    else throw new Error(`Unknown argument: ${a}`);
  }
  return args;
}

function usage() {
  console.log(`bpg-sync — sync guide skills/agents/hooks into a .claude/ directory

  bpg-sync --global [--only skills,agents,hooks] [--mode symlink|copy] [--skip-existing] [--dry-run]
  bpg-sync --project <path> [--only ...] [--mode ...] [--skip-existing] [--dry-run]

Defaults: all categories, mode=symlink. Recommended: --global for skills/agents,
--project for hooks (hooks are referenced by the project's settings.json).
--skip-existing only adds missing items (safe against a curated ~/.claude); otherwise existing
targets are replaced.`);
}

/** Returns true if it created/replaced a link, false if skipped. */
function link(src, dest, mode, dryRun, skipExisting) {
  const present = existsSync(dest) || isSymlink(dest);
  if (skipExisting && present) { console.log(`  skip (exists) ${dest}`); return false; }
  if (dryRun) { console.log(`  [dry] ${mode} ${dest} -> ${src}`); return true; }
  if (present) rmSync(dest, { recursive: true, force: true });
  if (mode === "copy") {
    cpSync(src, dest, { recursive: true });
    if (dest.endsWith(".sh")) chmodSync(dest, 0o755);
  } else {
    symlinkSync(src, dest, "dir"); // junction-style for dirs; files still resolve on posix
  }
  console.log(`  ${mode === "copy" ? "copied" : "linked"} ${dest}`);
  return true;
}

function isSymlink(p) {
  try { return lstatSync(p).isSymbolicLink(); } catch { return false; }
}

function syncCategory(catKey, targetClaude, mode, dryRun, skipExisting) {
  const cat = CATEGORIES[catKey];
  if (!existsSync(cat.src)) { console.log(`  skip ${catKey}: source missing (${cat.src})`); return 0; }
  const destDir = join(targetClaude, cat.destName);
  if (!dryRun) mkdirSync(destDir, { recursive: true });
  let n = 0;
  for (const entry of readdirSync(cat.src)) {
    if (entry.startsWith(".")) continue;
    if (catKey === "hooks") {
      // hooks: only the executable hook scripts (skip README.md, settings.example.json)
      if (!entry.endsWith(".sh")) continue;
      const srcFile = join(cat.src, entry);
      if (!lstatSync(srcFile).isFile()) continue;
      if (link(srcFile, join(destDir, entry), mode, dryRun, skipExisting)) n++;
    } else {
      // skills/agents: link each top-level item (skill dir or agent .md)
      if (link(join(cat.src, entry), join(destDir, entry), mode, dryRun, skipExisting)) n++;
    }
  }
  return n;
}

function main() {
  let args;
  try { args = parseArgs(process.argv.slice(2)); }
  catch (e) { console.error(e.message); usage(); process.exit(2); }

  if (args.help) { usage(); return; }
  if (!args.global && !args.project) { console.error("Specify --global or --project <path>."); usage(); process.exit(2); }
  if (!["symlink", "copy"].includes(args.mode)) { console.error(`--mode must be symlink|copy`); process.exit(2); }

  const categories = args.only || Object.keys(CATEGORIES);
  for (const c of categories) if (!CATEGORIES[c]) { console.error(`Unknown category: ${c}`); process.exit(2); }

  const targetClaude = args.global ? join(homedir(), ".claude") : join(resolve(args.project), ".claude");
  if (!args.dryRun) mkdirSync(targetClaude, { recursive: true });

  console.log(`bpg-sync → ${targetClaude}  (mode=${args.mode}${args.skipExisting ? ", skip-existing" : ""}${args.dryRun ? ", dry-run" : ""})`);
  console.log(`source package: ${PKG_ROOT}`);
  let total = 0;
  for (const c of categories) { console.log(`• ${c}:`); total += syncCategory(c, targetClaude, args.mode, args.dryRun, args.skipExisting); }
  console.log(`Done — ${total} item(s) ${args.dryRun ? "would be " : ""}synced.`);
  if (categories.includes("hooks")) {
    console.log(`\nNote: wire hooks in the project's .claude/settings.json (see agentic-tooling/settings/settings.base.json).`);
  }
}

main();
