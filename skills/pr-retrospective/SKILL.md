---
name: pr-retrospective
description: >
  Runs a structured retrospective on a merged or ready-to-merge PR. Scopes the
  PR window, inventories every artifact (commits, docs, specs, CI runs, Claude
  Code session JSONL files), detects friction patterns (scope creep, CI chasing,
  doc sprawl, walkthrough-discovered fixes, rework), and produces a markdown
  retrospective doc plus an Excel workbook with per-concern tabs. Optionally
  drafts an info-request/analyst-exchange packet for a second opinion. Use
  after a PR is merged or reaches "ready for review" to capture lessons and
  measurable refinements.
allowed-tools: [Agent, Bash, Read, Glob, Grep, Write, Edit, AskUserQuestion]
---

# PR Retrospective Skill

## Purpose

Produce a defensible retrospective for a PR — one where every friction finding is traceable to a commit, session, or doc — and produce a structured Excel workbook that captures the same findings in queryable form. Designed to make the retrospective *itself* reproducible so refinements can be measured on future PRs.

## When to Use

- "run a retrospective on PR #N"
- "let's retro PR #N"
- "/pr-retrospective"
- A PR just merged and you want to capture what worked and what didn't before memory fades
- You want to exchange retrospectives with an analyst (internal teammate or external) and need a consistent artifact to hand over

## When NOT to Use

- For a live, in-progress PR — use `pr-prep` first, then retro after merge
- For sub-PR-sized work (single commit bug fix) — the overhead isn't worth it
- As a generic "what went well" doc — this skill specifically analyzes friction, scope creep, and process drift; use a different template for positive-only reviews

---

## INPUTS

The skill needs the PR number. It will derive everything else automatically. Ask the user for these if not obvious:

| Input | Source | Default |
|---|---|---|
| PR number | user | required |
| Base branch | `gh pr view --json baseRefName` | `main` |
| Head branch | `gh pr view --json headRefName` | required |
| Window start | first commit timestamp on branch | `gh pr view --json commits \| first` |
| Window end | PR merge timestamp, or "all green" CI timestamp if unmerged | `gh pr view --json mergedAt,closedAt` |
| Worktree paths | detect from `git worktree list` + session `cwd` matches | auto |
| Output dir | user choice | `docs/pr-prep/retrospective-pr{N}/` |

---

## EXECUTION WORKFLOW

### Phase 1 — Scope the Window

Run in parallel to establish the retrospective window and confirm the PR exists.

```bash
# PR metadata
gh pr view $PR_NUM --json number,title,state,url,baseRefName,headRefName,createdAt,mergedAt,closedAt,additions,deletions,changedFiles,commits,reviews,files

# Commits on branch (pre-merge, for historical PRs use --base origin/main)
git log --reverse --format='%H|%ai|%s|%an' origin/main..$HEAD_BRANCH

# First commit timestamp = window start. Merge/close timestamp = window end.
# If PR is still open and passing, window end = timestamp of last green CI run.
```

Confirm with the user:
- "Retro window: {start} → {end} ({N} days)"
- "Base: {base}, head: {head}"
- "Proceed, adjust window, or abort?"

### Phase 2 — Inventory Artifacts in Parallel

Spawn four parallel Agent calls (general-purpose) to gather raw material. Each returns structured JSON the next phases consume.

**Agent 1 — Git history & diff stats:**
- All commits with sha, date, author, message, type (feat/fix/docs/test/ci/refactor/chore — classified by conventional-commits prefix or heuristics)
- Per-commit files changed, LOC added/removed
- Flag `fix(ci):` commits and their position in the timeline (before/after PR ready-for-review)
- Identify "merge" and "revert" commits explicitly

**Agent 2 — Docs & specs audit:**
- Inventory `docs/pr-prep/pr{N}/` and `_bmad-output/pr-prep/`: every file, size, last-modified, references from other files (to detect orphans)
- Inventory `docs/specs/*.md` where `mtime` falls inside the window: likely written mid-PR and signal ARCH-retro (should have been written upfront)
- Count how many times key facts (test counts, phase status) appear across docs — high repetition = sync bug risk

**Agent 3 — CI & PR timeline:**
- `gh pr checks $PR_NUM --json ...` — full CI run history
- First "all green" timestamp and count of reruns
- Reviews and review-request timestamps if any
- Identify the draft→ready transition if it happened

**Agent 4 — Claude Code session analysis:**
- Run `python3 $SKILL_DIR/scripts/analyze_sessions.py --pr-window START END --project-path $REPO_ROOT --out $WORK_DIR/sessions.json`
- See `scripts/analyze_sessions.py` for what it extracts (session count, messages, compaction events, top user prompts, tool-use frequency, files most edited per session)

### Phase 3 — Walkthrough-Discovered Fixes

If a manual walkthrough doc exists (`docs/pr-prep/pr{N}/manual-walkthrough.md` or `manual-walkthrough-progress.md`), extract its "Fixes landed during walkthrough" table. Each row becomes a Walkthrough Fixes tab entry.

If no walkthrough doc exists, derive the list heuristically: `fix(pr{N}): ...` commits landed after the first `docs(pr{N}): ...` commit.

For each fix, the retrospective needs:
- Short description
- Category (UX polish / API blocker / data blocker / ops tool / feature blocker / docs)
- Was it a genuine blocker? (Y/N — and if N, what's the minimum change needed to ship without it — e.g., docstring softening)
- Could it have deferred to a follow-up PR? (Y/N/Gray)

**The blocker-vs-deferrable call is a judgment call.** Do not guess silently. Either:
- Extract from the existing walkthrough doc if it already categorizes
- Or ask the user explicitly for each row
- Or make a best-effort categorization and flag it as "needs user review"

### Phase 4 — Friction Detection

For each signal below, measure it. Do not editorialize — report the number and let the refinement list interpret.

| Signal | How to measure | Where it lands |
|---|---|---|
| Scope creep | Commits added after walkthrough start that aren't in the original scope doc (if one exists) | Friction tab |
| CI chasing | Count of `fix(ci):` commits after draft→ready transition | Friction tab + CI Commits tab |
| Doc sprawl | Total files in `{docs/pr-prep/pr{N}/, _bmad-output/pr-prep/}` ÷ expected 6-artifact baseline | Docs tab |
| Parallel doc trees | Count of same key facts (test counts, phase status) appearing in 3+ files | Docs tab |
| Mid-PR specs | Count of `docs/specs/*.md` files created inside the window | Specs tab |
| Rework | Files edited in 3+ commits within window | Files Touched tab |
| PR body growth | Line count of PR description on day 1 vs final — if growing rather than re-cut, flag | Summary tab |
| Session compaction burden | Count of sessions with `isCompactSummary: true` vs total; median messages per session | Sessions tab |

### Phase 5 — Synthesize

Produce two outputs in the chosen output directory:

**5a. Markdown retrospective** at `docs/pr-prep/retrospective-pr{N}.md` using `templates/retrospective.md`.

Required sections (must all appear — leave "(none)" if empty rather than omitting):
1. **What Shipped** — context, scope, window
2. **What Landed Well** — positive findings (not just failures)
3. **Friction and Waste** — numbered list, each with evidence reference
4. **Claude Code Session Observations** — what the transcripts reveal that commits don't (reaching-near-done cycles, compaction density, etc.)
5. **Refinements** — lettered A, B, C…; each must specify measurement criteria
6. **Meta-Pattern** — one-line invariant that, if held, would have prevented the top friction items
7. **Recommended Next Step** — single concrete action

**5b. Excel workbook** at `docs/pr-prep/retrospective-pr{N}.xlsx` via `scripts/generate_report.py`.

Tabs (all mandatory; if no data, tab stays but with "(no data)" note):

| Tab | Contents |
|---|---|
| Summary | PR meta, window, commits, LOC, top-line verdict, friction score |
| Timeline | Chronological: commits, sessions, CI events, PR body revisions, walkthrough phase transitions |
| Commits | Every commit: sha, date, type, msg, LOC, files, is-walkthrough-fix, is-ci-fix, post-ready-state |
| Walkthrough Fixes | One row per fix: description, category, blocker Y/N, could-defer Y/N, source commit |
| CI Commits | One row per `fix(ci):` commit: cause, would-a-checklist-catch Y/N, post-ready |
| PR-Prep Docs | Every file: path, size, last-modified, useful-to-reviewer rating, keep-under-orchestrator-model Y/N |
| Specs Written | Every `docs/specs/*.md` created in window: path, target PR, signals-ARCH-retro |
| Sessions | Every JSONL: session id, date range, msg count, compacted Y/N, opening prompt, top 3 topics |
| Files Touched | Top 50 files by commit count inside window |
| Friction | Signals table from Phase 4 with measurements |
| Refinements | A, B, C… with measurement criteria and priority |

### Phase 6 — Optional Analyst Exchange

If the user wants an external second opinion (or they already have one to merge in), use `templates/info-request.md` to generate a structured question packet.

Typical flow:
1. Skill produces retrospective + Excel (Phase 5)
2. User shares both with an analyst (peer or external)
3. Analyst produces their own review — what they think the orchestrator/process system would have helped with
4. Skill runs a follow-up merge pass that resolves disagreements by calling out:
   - Where the analyst's estimates match the measured data
   - Where they diverge (and which source is authoritative)
   - What additional information would tighten the estimates

The info-request template has 10 sections — feature decomposition, walkthrough fixes breakdown, CI chasing cause, specific inline pull-forwards, walkthrough discovery counts, doc overhead hours, observability/validation, PII/compliance gaps, friction ranking, open-ended fit concerns. Customize sections based on what the retrospective surfaced.

### Phase 7 — Verify Measurability

Every refinement in the final doc must specify:
- **What metric** will tell us this refinement is working
- **What value** the metric takes now (before the refinement lands)
- **What value** it should take on the next PR if the refinement holds

Example (from PR #6):
> **Refinement B — Scope-freeze gate.** Metric: commits added after walkthrough start that aren't in the original scope doc. Current: 11 (PR #6). Target for PR #7: ≤ 2, each with explicit approval logged in the scope doc.

If you can't write a measurement, the refinement is vague — rewrite it or drop it.

---

## OUTPUTS

```
docs/pr-prep/
├── retrospective-pr{N}.md       # Main retrospective (markdown)
├── retrospective-pr{N}.xlsx     # Per-tab structured data (Excel)
└── retrospective-pr{N}/
    ├── raw/                     # Agent outputs (JSON) for reproducibility
    │   ├── commits.json
    │   ├── docs-audit.json
    │   ├── ci-timeline.json
    │   └── sessions.json
    ├── info-request.md          # Analyst question packet (if generated)
    └── analyst-reply.md         # Analyst's response draft (if generated)
```

---

## SCRIPTS

### `scripts/analyze_sessions.py`

Parses Claude Code session JSONL files and produces a structured summary.

**Location of session files:** `~/.claude/projects/<path-encoded-cwd>/*.jsonl`

- The `cwd` field in each message maps the session to a working directory
- Multiple project dirs exist per physical repo when worktrees are in use — script scans all dirs whose path starts with the project root
- Each JSONL has one message per line; types include `user`, `assistant`, `tool_use`, `tool_result`, `summary`, `permission-mode`, `file-history-snapshot`
- Compaction is detected via `isCompactSummary: true` or `subtype: compact_boundary`
- **Important:** JSONL retains the full pre-compaction exchange on disk even when the live session is compacted; script sees everything

**Output:** JSON file with per-session records — id, first/last timestamp, message counts by type, compacted boolean, opening user prompt, top N topics (via simple keyword extraction), files referenced in tool_use blocks, branch if present in `gitBranch` field.

### `scripts/generate_report.py`

Takes raw JSON from all four parallel agents + session data and produces the Excel workbook. Uses `openpyxl`.

Each tab has a fixed schema (see Phase 5 table). Missing data → "(no data)" row, not omitted tab.

---

## QUALITY BAR

The retrospective is good when:
1. Every friction finding has an evidence reference (commit SHA, session id, file path, or doc line)
2. Every refinement has a measurable success criterion
3. The Excel workbook answers "which commits were walkthrough fixes?" and "how many of our sessions compacted?" without re-reading the markdown
4. A reviewer who didn't live through the PR could pick up the markdown + Excel and understand both what happened and what to change next time
5. The meta-pattern (Section 6 of markdown) fits in one sentence

The retrospective is bad when:
- Friction items are stated without evidence ("we spent too much time on docs" without hours or file count)
- Refinements are vague ("we should do better with scope" without a metric)
- The session analysis is omitted because the JSONL was "too large to parse" — if the script fails on scale, fix the script
- The Excel duplicates data that's already clear in the markdown; every tab should add something the prose doesn't

---

## NOTES ON SESSION ANALYSIS

What the JSONL captures that commits don't:
- **"Reaching near-done" cycles.** User prompts like "are we ready", "is this done", "what's left" — count of these is a proxy for the recurring "almost there" morale drag
- **Compaction density.** Sessions that required compaction were doing a lot per session — worth surfacing per-feature vs per-PR
- **Tool churn.** High Bash/Read volume vs. Edit/Write volume reveals how much time went to investigation vs. implementation
- **Worktree hops.** Multiple `cwd` directories per person per day = context switches
- **Abandoned directions.** User prompts that redirect (`actually let's...`, `wait`, `never mind`) mark moments where the plan changed

Be respectful of the data: user prompts often contain raw thinking and are not suitable for external sharing without review. Default behavior: summarize; do not quote verbatim outside the user's own repo.
