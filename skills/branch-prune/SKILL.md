---
name: branch-prune
description: |
  Audit every local git branch and worktree against the integration branch, render a
  single compact chart (behind / ahead / worktree / dirty / last commit / advice), and
  emit copy-paste bash commands to remove worktrees and delete branches the user
  decides to prune. Use when the user mentions branch cleanup, prune branches, branch
  audit, worktree cleanup, "what branches can I delete", stale branches, or branch-prune.
allowed-tools: [Bash]
---

# Branch Prune

One-shot branch + worktree cleanup audit. Produce a single chart and the bash
commands to act on it. Do not execute any destructive operation — the user
copy-pastes the commands themselves.

## Determine the Integration Branch

Compare every local branch against the repo's **integration branch** — the branch
feature work merges into. This is project-specific; detect it once at the start:

```bash
git symbolic-ref refs/remotes/origin/HEAD 2>/dev/null | sed 's@^refs/remotes/origin/@@'
```

Common values: `main`, `master`, `develop`, `staging`, `trunk`. If the repo uses a
dedicated integration branch (e.g. `develop` or `staging`) that differs from the
default branch, prefer that. Below, `<base>` refers to this branch. Substitute it
everywhere the commands say `<base>`.

## Hard Rules

- **DO NOT** run `git branch -d`, `git worktree remove`, or `git push --delete`
- **DO NOT** stash, commit, or modify files in any worktree
- **DO NOT** ask clarifying questions before running the read-only audit — just
  run it and present the chart
- **DO** compare every local branch to `<base>` (the integration branch)
- **DO** flag any worktree with uncommitted changes as `DIRTY(<count>)` and
  refuse to suggest auto-deleting it without an investigate step

## Workflow

### 1. Gather data (read-only, parallel)

Run these in a single message:

```bash
git fetch --all --prune
```

```bash
git worktree list
```

```bash
for b in $(git branch --format='%(refname:short)'); do
  ahead_behind=$(git rev-list --left-right --count <base>...$b 2>/dev/null)
  echo "$b|$ahead_behind"
done
```

`git rev-list --left-right --count <base>...$b` returns `<behind> <ahead>` —
left side = commits on `<base>` not on branch (behind), right side = commits on
branch not on `<base>` (ahead).

```bash
for wt in $(git worktree list --porcelain | awk '/^worktree /{print $2}'); do
  echo "=== $wt ==="
  git -C "$wt" status --porcelain=v1 2>/dev/null | wc -l | tr -d ' '
done
```

```bash
git for-each-ref --format='%(refname:short) %(committerdate:short)' refs/heads/ | sort -k2
```

**Detect merged PR numbers.** Scan the integration branch's merge commits —
GitHub's default merge subject is `Merge pull request #NNN from <owner>/<branch>`.
Portable pipeline (works on macOS BSD sed; macOS default awk lacks gawk's array
capture, so avoid `match($0, /…/, m)`):

```bash
git log <base> --merges --pretty=format:'%s' | \
  grep -E '^Merge pull request #[0-9]+ from ' | \
  while IFS= read -r line; do
    pr=$(echo "$line"     | sed -E 's/^Merge pull request #([0-9]+) from .*/\1/')
    branch=$(echo "$line" | sed -E 's|^Merge pull request #[0-9]+ from [^/]+/||')
    echo "$branch|#$pr"
  done
```

Output is `<branch>|#<NNN>` pairs you index into when filling the chart's
`PR` column.

If a branch is not in that map, leave the PR column as `—`. For branches with
0 ahead but no merge-commit match (squash-merged), try
`gh pr list --state merged --search "head:<branch>" --json number --limit 1`
when `gh` is available — but only run this lookup for branches you're about
to mark `Delete` (don't blast the API for every branch).

### 2. Render the chart

Single markdown table with these exact columns and short header names so it
renders as a real grid (wide tables wrap into lists in narrow terminals):

| Branch | Bhd | Ahd | Worktree | Dirty | Last | PR | Advice |

Rules:

- `Worktree`: the directory name only (e.g. `bugs-may-13`), or `—` if no
  worktree. For top-level worktrees outside `.worktrees/`, show the full
  relative path.
- `Dirty`: `clean`, `DIRTY(N)` where N = uncommitted file count, or `—` if no
  worktree.
- `Last`: `MM-DD` only (skill is single-year; year clutters the column).
- `PR`: `#NNN` if the branch was merged into `<base>` via a known PR, otherwise
  `—`. Source: the merge-commit scan above, with optional `gh pr list`
  fallback for squash-merged branches.
- `Advice` — pick one per row. **Hard rule: a branch with `Ahd > 0` is NEVER
  eligible for the bulk-delete sections.** Even one unmerged commit means
  work could be lost.
  - `Delete` — `Ahd == 0` AND (no worktree OR worktree is clean). Goes in
    the bulk-delete blocks.
  - `Delete (merged)` — same gate as `Delete`, but a PR number is known.
  - `INVESTIGATE` — `Ahd > 0` for any reason. Listed in the hold-off section
    with a one-line reason. Never appears in the bulk-delete commands. This
    covers stale-but-ahead branches (e.g. 555 behind / 37 ahead) the same way
    it covers active ones.
  - `KEEP — active` — recent commits + dirty worktree, or actively-in-progress
    work the user is clearly still using.
  - Dirty worktrees with `Ahd == 0` still go in the **dirty-worktrees-review**
    block (not the bulk block), so the user diffs the uncommitted changes
    before they vanish.

### 3. Emit the cleanup commands

Four sections, in this order, each in its own fenced bash block. **Every
name in these blocks must have `Ahd == 0`.** Anything with commits ahead of
`<base>` belongs in the hold-off list (step 4), not here.

1. **Remove clean worktrees** — `git worktree remove <path>` per row, one per
   line. Only rows where `Ahd == 0` AND `Dirty == clean`.
2. **Dirty worktrees needing review** — for each `Ahd == 0` worktree with
   uncommitted changes, emit a `git -C <path> diff` line followed by
   `git worktree remove --force <path>`. Do NOT bundle these with the clean
   removals. Dirty worktrees with `Ahd > 0` do NOT go here — they go in the
   hold-off list.
3. **Delete local branches** — `git branch -d <name>` per row (lowercase `-d`
   on purpose; refuses unmerged branches as a safety net — never use `-D`).
   Only branches where `Ahd == 0`. Run AFTER worktree removal (a branch in
   use by a worktree can't be deleted). If `-d` refuses, that's a signal to
   investigate the branch, not to escalate to `-D`.
4. **Delete remote branches** — a single
   `git push origin --delete <name> <name> ...` line, filtered to branches
   whose remote tracking ref still exists AND `Ahd == 0`. Skip branches
   already pruned by step 1's `git fetch --prune`.

Section 4's filter: only include `<name>` if `origin/<name>` appears in
`git branch -r` output (which is already accurate after the initial
`fetch --prune`).

### 4. Hold-off list

Below the four command blocks, list every branch marked `INVESTIGATE` as
bullet points with a one-line reason ("37 commits ahead", "325 uncommitted
files", etc). These are the ones that require a human decision.

## Output Shape

Keep the response tight:

1. Single chart.
2. Four command blocks.
3. Hold-off bullet list.
4. One-sentence summary (`X keep, Y investigate, Z deletes`).

No preamble, no methodology explanation, no per-branch prose paragraphs.

## Red Flags

- About to execute `git branch -d` or `git worktree remove` yourself → **Stop.**
  Emit the command only.
- About to emit `git branch -D` instead of `-d` → **Stop.** The skill uses
  lowercase `-d` as a safety rail; if `-d` refuses, that's the user's signal
  to investigate, not your signal to force.
- About to ask "which branches do you want to delete?" before running the
  audit → **Stop.** Run the audit first; the chart is the answer.
- About to bundle dirty-worktree removals into the safe block → **Stop.**
  Dirty worktrees go in their own block with a `diff` line first.
- About to put a branch with `Ahd > 0` into any of the four cleanup blocks
  → **Stop.** Ahead-of-integration commits mean potential lost work; the branch
  goes in the hold-off list instead, no exceptions.
- About to skip the `git fetch --prune` step → **Stop.** Stale remote refs
  give wrong advice.
