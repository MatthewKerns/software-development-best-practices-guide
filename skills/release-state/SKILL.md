---
name: release-state
description: |
  One-command "where is everything?" report across a project's release
  pipeline: local worktrees/branches (dirty, unpushed, local-only), what's on
  GitHub (open PRs, unmerged branches), what's deployed to staging (stamp +
  served bundle), what's queued for prod, and what's actually live on prod
  (served bundle vs integration tip). Use when the user asks "where is
  everything", "release state", "what's deployed where", "what's local vs
  pushed vs staged vs prod", "env state", or at the start of a deploy or
  planning session. Read-only — it reports and flags; it never deploys,
  pushes, or deletes.
allowed-tools: [Read, Bash, Grep, Glob]
---

# Release State — the six-layer picture

Goal: answer "what exists where?" in one pass, with **served artifacts as
ground truth** — never commit history alone.

## Configuration (from the project)

Read `docs/RELEASE_PIPELINE.md` for: the integration branch, staging URL +
deploy-stamp path (e.g. `DEPLOYED.json` in the staging docroot, often also
served over HTTP), the prod URL, and the queue file path (default
`docs/release/DEPLOY_QUEUE.md`). If the manifest is missing, report the layers
you can (git/GitHub) and say explicitly which layers are unavailable and why.

## The six layers

**1. Local worktrees & branches.** Enumerate `git worktree list --porcelain`;
for each: branch, dirty-file count, last-commit age, and vs-origin state
(`origin/<branch>` missing → `NOT-ON-GITHUB`; else ahead-count → `unpushed:N`).
Report only worktrees that are dirty, unpushed, local-only, or active in the
last 7 days — the full list is noise.

```bash
python3 - <<'PY'
import subprocess, os
def run(*a, cwd=None): return subprocess.run(a, capture_output=True, text=True, cwd=cwd).stdout.strip()
wts = [l.split(' ',1)[1] for l in run('git','worktree','list','--porcelain').splitlines() if l.startswith('worktree ')]
print(f'{len(wts)} worktrees. Dirty / unpushed / local-only / active-in-7d:')
for wt in wts:
    br = run('git','branch','--show-current', cwd=wt) or '(detached)'
    dirty = len(run('git','status','--porcelain', cwd=wt).splitlines())
    age = run('git','log','-1','--format=%cr', cwd=wt)
    recent = any(u in age for u in ('minute','hour','day')) and 'week' not in age and 'month' not in age
    flag = ''
    if br != '(detached)':
        if not run('git','rev-parse','--verify','--quiet',f'origin/{br}', cwd=wt): flag = 'NOT-ON-GITHUB'
        else:
            c = run('git','rev-list','--left-right','--count',f'origin/{br}...HEAD', cwd=wt).split()
            if c and c[1] != '0': flag = f'unpushed:{c[1]}'
    if dirty or flag or recent:
        print(f'  {os.path.basename(wt):28s} {br:38s} {age:16s} {"dirty:"+str(dirty) if dirty else "":9s} {flag}')
PY
```

**2. GitHub.** `git fetch` first. Open PRs (`gh pr list --json
number,title,headRefName`), plus any branch from layer 1 that is ahead of the
integration branch but has no PR — name those explicitly ("work with no PR").

**3. Staging — deployed.** Read the deploy stamp (try
`curl -s <staging-url>/DEPLOYED.json` before SSH). Report sha/branch/bundle/
time/session. Cross-check the stamp's `bundle_hash` against the actually
served entry (`curl -s <staging-url>/<app-route> | grep -oE 'assets/index-[^"]+\.js'`).
Stamp≠served means someone deployed without stamping — say so.

**4. Prod queue.** Read the queue file; report entries by status
(`pending-staging` / `staging-verified` / `blocked`), and whether the newest
staging-verified SHA still equals the integration tip.

**5. Prod — deployed.** Fetch the served bundle hash from an app route on the
prod URL. Map it to a commit if a local `dist/assets/` or the queue's deploy
log records it. Report how far the integration tip is ahead of the deployed
SHA ("prod is N commits behind main: <one-line list>").

**6. Backend drift (if the project has separately-deployed functions).** Note
in-repo functions with uncommitted or unmerged changes — a worktree can hold
an edited function that was already deployed (or never deployed); flag both
directions as "function state unverifiable from git alone" unless a deploy
record exists.

## Hard-won rules (encode in every report)

- **Squash merges make ancestry lie.** `merge-base --is-ancestor` failing does
  NOT mean content diverged — verify with content diffs or bundle-marker greps
  before reporting "staging lacks main".
- **A 200 proves nothing on an SPA** — every unknown path serves the same
  fallback. Only served-bundle greps and stamps are evidence.
- **Never trust "merged" to mean "deployed"** — the served hash is the truth.
- Do not push, deploy, prune, or fix anything from this skill — hand findings
  to `release-stage-verify`, `release-deploy-prod`, or `branch-prune`.

## Output format

Lead with a one-paragraph verdict (is anything stranded, diverged, or
undeployed-but-believed-live?). Then one short section per layer, flagging:
stranded uncommitted work, local-only branches (laptop-loss risk), unpushed
commits, work with no PR, stamp/served mismatches, queue entries invalidated
by newer commits, and prod-behind-main deltas.
