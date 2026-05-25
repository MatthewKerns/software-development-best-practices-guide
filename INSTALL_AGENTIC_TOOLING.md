# Installing the Shared Agentic Tooling

This guide is the **single source** for agentic-coding tooling across projects. Instead of
copying skills/agents/hooks into every repo, projects consume them through three channels:

| Channel | Carries | Mechanism |
|---------|---------|-----------|
| **npm package** | everything (source of truth, versioned) | `npm i @matthewkerns/software-development-best-practices-guide` |
| **`mango-tools` MCP server** | reference knowledge (docs, checklists, patterns, AGENTS.md template) as resources + tools | `claude mcp add` once at user scope |
| **`bpg-sync` CLI** | skills, agents, hooks (filesystem-discovered — MCP can't serve these) | symlinks the package's files into `~/.claude` or `./.claude` |

> Why three? Claude Code discovers **skills/agents/hooks from the filesystem** — an MCP server
> can't register them. So MCP serves read-only knowledge + tools, while `bpg-sync` projects the
> filesystem artifacts. npm is the versioned source both read from.

## Prerequisites

`.npmrc` in the consuming project (or `~/.npmrc`) must point the scope at GitHub Packages:

```
@matthewkerns:registry=https://npm.pkg.github.com
//npm.pkg.github.com/:_authToken=${GITHUB_TOKEN}
```

## 1. Install the package

```bash
npm i -D @matthewkerns/software-development-best-practices-guide
# (a global install also works and makes the bins available everywhere:)
# npm i -g @matthewkerns/software-development-best-practices-guide
```

## 2. Register the `mango-tools` MCP server (once, user scope)

```bash
# If installed globally:
claude mcp add mango-tools --scope user -- mango-tools

# Otherwise resolve the named bin from the package via npx:
claude mcp add mango-tools --scope user -- npx -y -p @matthewkerns/software-development-best-practices-guide mango-tools
```

Verify: `claude mcp list` shows `mango-tools`. In a session the agent can then call
`list_patterns`, `get_best_practice`, `read_guide`, `get_checklist`, `scaffold_agents_md`,
and `validate_flag_registry` — no files copied into the repo.

## 3. Sync skills / agents / hooks with `bpg-sync`

```bash
# Skills + agents are best global (every project sees them):
npx bpg-sync --global --only skills,agents

# Hooks are best per-project (they're wired by the project's settings.json):
npx bpg-sync --project . --only hooks
```

Default mode is `symlink`, so `npm update` to a newer guide version propagates automatically.
Use `--mode copy` to vendor a frozen copy, and `--dry-run` to preview.

## 4. Wire hooks + settings (optional but recommended)

```bash
cp node_modules/@matthewkerns/software-development-best-practices-guide/agentic-tooling/settings/settings.base.json .claude/settings.json
# create .claude/settings/settings.<role>.json from agentic-tooling/settings/settings.profile.template.json
```

See `agentic-tooling/settings/README.md` and `agentic-tooling/hooks/README.md`.

## 5. Adopt the AGENTS.md hierarchy

Use the `scaffold_agents_md` MCP tool (or copy `07-agentic-coding/AGENTS.template.md`) to create a
root `AGENTS.md`, then a one-line `CLAUDE.md` containing `@AGENTS.md`. See
`07-agentic-coding/AGENT_INSTRUCTION_HIERARCHY.md`.
