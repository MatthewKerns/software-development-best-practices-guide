---
name: new-worktree
description: |
  Create a new git worktree off the latest integration branch with a short, relevant
  branch name inferred from the user's context. Stops after creating the worktree —
  does NOT ask Socratic questions, does NOT plan, does NOT start coding. Use when
  user says new worktree, create worktree, spin up a worktree, start a branch for X,
  make a worktree for X, or new-worktree.
allowed-tools: [Bash, Read]
---

# New Worktree

Create an isolated worktree off the freshest integration branch and stop. The user's
next message will contain detailed instructions; your job here is only to set up
the workspace.

## Hard Rules

- **DO NOT** ask clarifying questions about the work itself
- **DO NOT** invoke brainstorming, feature-planning, or any Socratic skill
- **DO NOT** start editing code, reading source files, or planning the implementation
- **DO NOT** run baseline tests or boot the dev stack here — that's a separate, optional step (see "Optional: Start Your Dev Stack" below). The user boots it when ready.
- **DO** pick a reasonable branch name from the small amount of context the user gave
- **DO** stop after reporting the worktree path

## Determine the Integration Branch

Worktrees should branch from the repo's integration branch — the branch feature work
merges into. This is project-specific:

```bash
# Most repos: the default branch (main, or sometimes master)
git symbolic-ref refs/remotes/origin/HEAD 2>/dev/null | sed 's@^refs/remotes/origin/@@'
```

Common values: `main`, `master`, `develop`, `staging`, `trunk`. If the repo uses a
staging/develop integration branch instead of the default branch, prefer that. When
in doubt, use the default branch the command above reports. Below, `<base>` refers
to this branch.

## Workflow

1. **Pick a branch name.** Use `feature/<kebab-case-slug>` derived from the user's
   one-line context. Keep it 2-5 words. If the user gave no context, use
   `feature/scratch-<YYYYMMDD>`. Do not ask the user to confirm the name unless
   they explicitly asked you to. (Adapt the `feature/` prefix to the repo's
   convention if it uses something else, e.g. `feat/`, `fix/`.)

2. **Fetch latest base and create the worktree:**

   ```bash
   git fetch origin <base> --quiet
   git worktree add .worktrees/<slug> -b feature/<slug> origin/<base>
   ```

   If `.worktrees/` is not yet gitignored, add it to `.gitignore` first (one line:
   `.worktrees/`) so worktree contents never get committed to the parent branch.
   Many teams keep worktrees under `.worktrees/`; a sibling directory
   (`../<repo>-<slug>`) also works if you prefer worktrees outside the repo tree.

3. **Handle name collisions.** If `git worktree add` fails because the branch or
   directory already exists:
   - Branch exists, no worktree → add a worktree onto the existing branch:
     `git worktree add .worktrees/<slug> feature/<slug>`
   - Directory exists → pick a suffixed slug (`<slug>-2`) and retry.
   - Branch already checked out in another worktree → report the existing path
     and stop; do not force.

4. **All subsequent file edits MUST target absolute paths inside the
   worktree** (`.worktrees/<slug>/...`). Editing inside the worktree keeps the
   parent checkout clean and lets you work on multiple branches at once without
   stashing. You do NOT need to restart your tooling — just keep editing inside
   the worktree path.

5. **Report and stop.** One or two sentences:

   ```
   Worktree ready at .worktrees/<slug> on feature/<slug> (tracking origin/<base>).
   All edits should target .worktrees/<slug>/... — ready for your instructions.
   ```

   Do not propose next steps, do not ask what to build, do not read any files.

## Optional: Start Your Dev Stack

If — and only if — the user explicitly asks to boot the app in the new worktree,
run the project's start command from inside the worktree directory. This is
project-specific; pick whichever applies (and skip entirely otherwise):

```bash
# Node / web app
cd .worktrees/<slug> && npm install && npm run dev

# Docker Compose stack — reuse the main project's name to avoid a full rebuild
# (see the focus-worktree skill for the full rationale)
cd .worktrees/<slug> && docker compose -p <project-name> up -d

# Python service
cd .worktrees/<slug> && <your venv + run command>

# Makefile-driven
cd .worktrees/<slug> && make dev
```

Worktrees do not inherit gitignored files like `.env`. If the stack needs one,
symlink it from the main checkout rather than copying (copies go stale):

```bash
MAIN_REPO="$(git worktree list | head -1 | awk '{print $1}')"
[ ! -e ".worktrees/<slug>/.env" ] && ln -sf "$MAIN_REPO/.env" ".worktrees/<slug>/.env"
```

## Naming Examples

| User context | Branch name |
|---|---|
| "fixing a UI bug on the dashboard page" | `feature/dashboard-ui-fix` |
| "updating seed data" | `feature/seed-data-updates` |
| "experimenting with the chart component" | `feature/chart-experiment` |
| (no context) | `feature/scratch-YYYYMMDD` |

## Red Flags — Stop If You Catch Yourself

- About to ask "what specifically should I change?" → **Stop.** Create the worktree and wait.
- About to invoke a brainstorming or feature-planning skill → **Stop.** Wrong skill.
- About to read source files to "understand the area" → **Stop.** Not your job here.
- About to run the test suite or boot the dev stack unprompted → **Stop.** Optional, and only on explicit request.
