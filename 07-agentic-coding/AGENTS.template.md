# Agent Development Instructions

<!--
  TEMPLATE — copy to your repo root as AGENTS.md and fill in the <PLACEHOLDERS>.
  Then create a sibling CLAUDE.md whose ENTIRE contents are:  @AGENTS.md
  Keep this file to UNIVERSAL rules; put area-specific rules in nested AGENTS.md files.
  See AGENT_INSTRUCTION_HIERARCHY.md for the full convention.
-->

## Scope

Universal rules for AI agents working on <PROJECT NAME — one line: what it is, who it's for>.
Area-specific rules live in local `AGENTS.md` files; this file holds the rules that apply everywhere.

## On Startup

- Load only this file via the `CLAUDE.md` reference.
- Load a local `AGENTS.md` when entering an area (the parent chain auto-loads via the `CLAUDE.md` hierarchy).
- Load a skill from `.claude/skills/` (or `~/.claude/skills/`) only when the task matches its description.
- Load `README.md` / long-form docs only when architecture detail is needed.
- Never bulk-load documentation.
- For generic engineering standards (naming, functions, testing, refactoring), consult the
  `mango-tools` MCP server or `node_modules/@matthewkerns/software-development-best-practices-guide/`
  instead of restating them here.

## Boundaries

### Always Do
- <e.g. Run the app/tests inside the project's standard environment (Docker / venv / etc.)>
- <e.g. Use the canonical data-access / API-client helper — never call the raw client directly>
- <e.g. Use the project's logging utility; scrub sensitive data before any log line>
- Use the task list for any work with >2 steps; maximize parallel execution via subagents.
- Run tests before human handoff.

### Ask First
- Adding new dependencies (any language).
- Adding/changing public API routes or auth/permission middleware.
- Changes to infrastructure, migrations, or third-party integrations.
- <project-specific "consult before touching" areas>

### Never Do
- Commit secrets or credentials.
- Deploy directly to staging/production — use CI/CD.
- <e.g. Hand-write schema changes instead of using the migration tool>
- <project-specific hard "no">

## Chosen Tools

Project-wide tool registry. Check here before proposing a new library (run a duplication check first).

| Category | Tool | Notes |
|----------|------|-------|
| Frontend framework | <e.g. React + Vite> | <constraints> |
| Styling | <e.g. Tailwind> | <no CSS modules, etc.> |
| API client | <canonical helper> | never call raw fetch/axios |
| Backend framework | <e.g. FastAPI / Express> | |
| Logging | <e.g. structlog / pino> | never raw print/console |
| ORM / migrations | <e.g. SQLAlchemy + Alembic> | no auto-create; migrate |
| Auth | <e.g. Clerk / Supabase Auth> | |
| Database | <e.g. PostgreSQL> | |
| Feature flags | <service + registry> | see feature flag registry |
| AI inference | <port/adapter> | never import vendor SDK directly |

## Task Management & Parallel Execution

- **RULE:** For >2 steps, create a task list before execution; keep status current.
- **RULE:** After creating tasks, launch independent ones as parallel subagents.
- **RULE:** Never parallelize edits to the same file.

## Git Workflow

```
<feature/* --> staging --> main   (adapt to your branch model)>
```
- Branch from <base>; PRs only to <protected branches>.
- Wait for human approval before commit/merge unless told otherwise.
- Delete feature branch after merge.
- **Worktrees:** use `git worktree add` for parallel dev (see the `new-worktree` / `focus-worktree` skills).

## Permission Profiles

Role profiles live in `.claude/settings/settings.<role>.json` and layer on top of the base
`.claude/settings.json`. The `security-check.sh` hook is always active.
- **<Permissive role>:** full access; the security hook + base deny list are the safety net.
- **<Restricted role>:** no infrastructure / auth-core / CI-CD edits; pushes and installs gated.

Branch protection: `<main/staging>` are hard-blocked for direct Write/Edit in all profiles.

## Testing Protocol (Before Human Handoff)

1. <Backend/unit tests: command>
2. <Lint: command>
3. Verify the functionality you can test.
4. Report what requires human verification.

## Documentation Areas

| Area | AGENTS.md Focus |
|------|-----------------|
| <src/services/> | <its local rules> |
| <src/components/> | <its local rules> |
| <feature flag registry> | source-of-truth identity/expiry for every flag |

## Skills Index

Skills live at `.claude/skills/{name}/SKILL.md` (project) or `~/.claude/skills/` (global).

| Skill | When to Use |
|-------|-------------|
| new-worktree / focus-worktree / branch-prune | git worktree lifecycle for parallel dev |
| initiate-team-review | spawn the specialist reviewer roster on a diff |
| <project skill> | <when> |

## Communication

- Show code examples over explanations.
- Comments explain *what* and *why*, not *how*.
- Surface blockers immediately.
- Provide specific test instructions before handoff.

## Meta

Generated: <date> | <how this file is maintained>
