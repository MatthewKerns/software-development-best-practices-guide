---
name: focus-worktree
description: |
  Point your local dev environment at a git worktree instead of the main checkout,
  without triggering a full rebuild. Use when user mentions focus worktree,
  switch worktree, serve worktree, localhost worktree, point docker to worktree,
  switch the dev server to a worktree, or make localhost show this worktree.
allowed-tools: [Bash, Read]
---

# Focus Worktree

Switch the local dev environment to serve code from a specific git worktree. The
goal is a fast switch (seconds), not a slow one (full rebuild), by reusing the
main checkout's cached build artifacts, dependencies, and runtime state.

This skill is stack-agnostic. The mechanics differ by toolchain — pick the section
that matches your project and skip the rest. The git-worktree identification steps
(1) are universal; the start/stop steps depend on your dev stack.

## When to Use

You have multiple git worktrees and want localhost to serve one of them right now.
Naively starting the dev server from a worktree directory often creates a *separate*
environment (new container project name, fresh `node_modules`, cold caches), forcing
a slow rebuild. The patterns below reuse the existing environment so the switch is
near-instant.

## Workflow

### 1. Identify the target worktree (universal)

```bash
git worktree list
```

Confirm which worktree path to focus. The first row is the main checkout.

### 2. Ensure required gitignored files exist in the worktree (universal)

Worktrees do not receive gitignored files such as `.env`. Symlink them from the
main checkout rather than copying — a copy goes stale when the source changes.

```bash
MAIN_REPO="$(git worktree list | head -1 | awk '{print $1}')"
WORKTREE="<worktree-path>"
[ ! -e "$WORKTREE/.env" ] && ln -sf "$MAIN_REPO/.env" "$WORKTREE/.env"
```

### 3. Stop the current dev process, then start it from the worktree

Use whichever section matches your stack.

---

#### Option A — Docker Compose

Running `docker compose up` from a worktree directory derives the Compose *project
name* from the directory, which creates a brand-new set of containers, volumes, and
networks and forces a full image rebuild (often minutes). Passing an explicit
`-p <project-name>` reuses the main checkout's cached images and volumes, making the
switch take seconds.

```bash
# Stop wherever it's currently running:
#   from main checkout:
docker compose down
#   from another worktree:
cd <previous-worktree-path> && docker compose -p <project-name> down

# Start from the target worktree with the SHARED project name:
cd <worktree-path> && docker compose -p <project-name> up -d
```

`<project-name>` is the stable name of your main checkout's Compose project (often
the repo directory name, or whatever `COMPOSE_PROJECT_NAME` is set to). The `-p`
flag is the critical part — without it Docker namespaces the project per directory
and rebuilds from scratch.

Verify cached images were reused (no build output in the `up` log) and services are
healthy:

```bash
docker compose -p <project-name> ps
```

To switch back to the main checkout:

```bash
cd <worktree-path> && docker compose -p <project-name> down
cd "$(git worktree list | head -1 | awk '{print $1}')" && docker compose up -d
```

---

#### Option B — Node dev server (Vite, Next.js, etc.)

```bash
# Stop the running dev server (Ctrl-C in its terminal, or kill the process).

# Reuse the main checkout's node_modules to skip a fresh install — symlink it
# (works for most setups; if your tooling dislikes a symlinked node_modules,
# run a normal `npm install` in the worktree instead):
MAIN_REPO="$(git worktree list | head -1 | awk '{print $1}')"
[ ! -e "<worktree-path>/node_modules" ] && ln -s "$MAIN_REPO/node_modules" "<worktree-path>/node_modules"

cd <worktree-path> && npm run dev
```

---

#### Option C — Makefile / custom script

If the project centralizes dev startup behind a Makefile or script, stop the current
instance and run the same target from the worktree:

```bash
cd <previous-location> && make dev-stop   # or the project's stop command
cd <worktree-path> && make dev            # or the project's start command
```

Pass through whatever flag your project uses to reuse the shared environment (the
Docker `-p` analogue), if one exists.

---

### 4. Confirm services are healthy

Hit the usual local URLs (e.g. `http://localhost:3000` for the frontend, the API
port, any log viewer) and confirm everything responds. Containers/processes should
reach a healthy state quickly since caches were reused.

## Common Pitfalls

| Pitfall | Why It Fails | Correct Approach |
|---------|--------------|------------------|
| `cd worktree && docker compose up` (no `-p`) | New project name → full rebuild, separate namespaces | Always pass `-p <project-name>` |
| Checking out the worktree's branch in the main checkout | Fails: "branch already used by worktree" | Run the dev server from the worktree directory directly |
| Copying `.env` / config instead of symlinking | Goes stale when the source changes | Use `ln -sf` |
| Running a fresh `npm install` per worktree | Slow, wastes disk | Symlink `node_modules` from the main checkout when your tooling allows |

## See Also

- `new-worktree` skill — create the worktree this skill switches to.
- `branch-prune` skill — clean up worktrees and branches when done.
