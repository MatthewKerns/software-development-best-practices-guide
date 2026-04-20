# Feature Factory — User Guide

A practical, end-to-end walkthrough of the six orchestrator skills that make up the Feature Factory pipeline. Read this when you want to go from "I have a feature idea" to "merged PR with runbook" without losing context between phases.

---

## TL;DR

One feature → one git worktree → six artifacts → one PR.

| # | Bucket | Skill | Output | What it answers |
|---|--------|-------|--------|------------------|
| 1 | **ARCH** | `arch-orchestrator` | `arch.md` | Where does this feature fit? What does it block and what is blocking it? |
| 2 | **FUNC** | `func-orchestrator` | `func.md` + code | Does the happy path work under TDD? |
| 3 | **ERRORS** | `errors-orchestrator` | `errors.md` | What can fail, how do we catch it, what do we retry? |
| 4 | **OBSV** | `obsv-orchestrator` | `observability.md` | Is it working? If not, what went wrong? |
| 5 | **REVIEW** | `review-orchestrator` | cleaner code + `review.md` | Is the code SOLID, DRY, and reviewable? |
| 6 | **DOCS** | `docs-orchestrator` | `runbook.md` + updated CLAUDE.md | Can a teammate resolve this at 2am without asking? |

ERRORS, OBSV, and REVIEW can run in parallel after FUNC. DOCS runs last (it consumes ERRORS + OBSV).

---

## Installation

### Option A — Personal install (all projects on your machine)

```bash
cp -r skills/feature-factory/*-orchestrator ~/.claude/skills/
```

### Option B — Project-scoped install

```bash
mkdir -p .claude/skills
cp -r skills/feature-factory/*-orchestrator .claude/skills/
```

### Option C — Already in this repo

If you're working inside this repository, the orchestrators are already discoverable in `skills/feature-factory/`. Claude Code auto-loads skills from standard locations; if yours aren't loading, symlink or copy them into `.claude/skills/` as above.

### Best-practices guide reference

The orchestrators link to guides in this repo using relative paths like `01-foundations/ERROR_HANDLING.md`. Keep the repo as:

- a **sibling** of your working project (`~/workspace/software-development-best-practices-guide`), or
- a **git submodule** at `docs/best-practices/`, or
- adjust the paths inside each orchestrator's "Best Practices Reference" section.

---

## The Tier Decision (do this first)

Not every feature needs all six buckets. Pick the tier before you start.

| Tier | Examples | Buckets you run |
|------|----------|------------------|
| **Critical Path** | Core integrations, payment flows, auth, data pipelines | All 6 (ARCH → FUNC → ERRORS + OBSV + REVIEW → DOCS) |
| **Standard** | Internal tools, secondary integrations, dashboards | ARCH, FUNC, ERRORS, REVIEW, DOCS (skip OBSV if internal-only) |
| **Quick** | Bug fixes, copy changes, config tweaks | FUNC + REVIEW only |

The ADR's dependency-graph position (produced by ARCH) usually decides this automatically — if the feature is on the critical path, it's Critical Path tier.

---

## The Standard Flow (Critical Path / Standard tier)

### Step 0 — Create a worktree for the feature

```bash
git worktree add ../my-repo-F-14 -b feature/F-14-tiktok-returns
cd ../my-repo-F-14
mkdir .feature-factory
```

All six artifacts live in `.feature-factory/` inside the worktree.

### Step 1 — ARCH (sequential, first)

**Trigger:** "architecture review for F-14" or "where does this fit"

**Inputs:** PRD or feature spec, current architecture docs.

**What you get:** `.feature-factory/arch.md` — an ADR containing:
- Decision (what architectural choice is being made and why)
- Affected modules
- **Dependency graph** (Blocked By / Blocks / Critical Path Position / External Dependencies)
- Alternatives considered
- Consequences

**Do not skip the dependency graph.** Everything downstream — scope freezing, parallel planning, PR scope validation — depends on it being explicit.

### Step 2 — FUNC (sequential, after ARCH)

**Trigger:** "implement F-14", "TDD this feature", "build the backend"

**Inputs:** `arch.md`.

**What happens:**
1. Pre-emptive DRY check (search for existing implementations before writing new ones)
2. Red → Green → Refactor TDD loop for the happy path
3. Commits with passing tests

**What you get:** Working code + `.feature-factory/func.md` (what was built, test coverage, deviations from arch).

### Step 3 — ERRORS + OBSV + REVIEW (parallel, after FUNC)

Open three terminals or three Claude Code sessions in the same worktree.

#### ERRORS
**Trigger:** "design error handling for F-14", "what could go wrong", "enumerate TikTok API error codes"

**What you get:** `.feature-factory/errors.md` with an error matrix — every failure mode, trigger, handling strategy, retry policy, user-facing message, PII fields redacted.

#### OBSV
**Trigger:** "what metrics should F-14 have", "instrument this code", "logging plan for"

**Inputs:** `errors.md` (every error needs a log).

**What you get:** `.feature-factory/observability.md` — Golden Signals coverage (latency, traffic, errors, saturation), structured log statements, metrics, alerts, dashboards.

#### REVIEW
**Trigger:** "review this code", "refactor before PR", "SOLID check"

**What happens:** Routes to your existing refactoring skills (`code-smell-detector`, `solid-validator`, `dry-compliance-checker`, etc.) and applies findings.

**What you get:** Cleaner code + `.feature-factory/review.md` (findings by severity, what was fixed, follow-up tickets).

### Step 4 — DOCS (sequential, after ERRORS and OBSV)

**Trigger:** "write the runbook", "docs for F-14", "update CLAUDE.md"

**Inputs:** `errors.md` + `observability.md` (plus `arch.md` for architectural context).

**What you get:** `.feature-factory/runbook.md` — per-error resolution entries, per-metric interpretation, on-call decision tree, plus updated `CLAUDE.md` and API docs.

### Step 5 — Open the PR

The PR description is **generated from the six artifacts**, not hand-assembled. See `INTEGRATION_WITH_PR_PREP.md` for the template and how `pr-prep` consumes these artifacts instead of regenerating parallel docs.

---

## The Quick Flow (bug fix tier)

```
FUNC (write failing test → fix → green) → REVIEW (smell check → clean) → PR
```

No ADR, no error matrix, no runbook update. If the bug reveals a missing error case or a missing metric, promote the fix to Standard tier and run ERRORS/OBSV.

---

## How to invoke an orchestrator

Three ways:

1. **Natural-language trigger** (auto-detected from frontmatter):
   - "Let's run the architecture review for F-14"
   - "Implement this feature"
   - "Design error handling for the TikTok returns flow"
   - "What metrics should this have"
   - "Review and clean this up"
   - "Write the runbook"

2. **Clockify-style tag** (if you track time):

   ```
   {project} {feature-id} {bucket}: {description}
   tiktok-mcf F-14 errors: enumerate API codes
   ```

3. **Explicit Skill invocation** — `/arch-orchestrator`, `/func-orchestrator`, etc. (requires the orchestrator to be installed as a slash command, not just a skill).

---

## Running the Parallel Phase Safely

ERRORS, OBSV, and REVIEW are **conditionally parallel**:

- ✅ Safe when they touch different files. ERRORS adds retry decorators, OBSV adds log statements, REVIEW refactors internal helpers.
- ❌ Not safe when all three want to rewrite the same function. In that case, run sequentially: ERRORS → OBSV → REVIEW.

**Rule of thumb:** run parallel by default; if you see merge conflicts in `.feature-factory/` or in the code, fall back to sequential.

---

## Integration with `pr-prep`

The orchestrators produce **per-feature artifacts** during development (`.feature-factory/*.md` in the worktree). The existing `pr-prep` skill produces **per-PR artifacts** at PR time (`_bmad-output/pr-prep/*.md`).

At PR time, `pr-prep` should **consume** the orchestrator artifacts, not regenerate them. Promote them to `docs/pr-prep/pr{N}/` as the single source of truth. See `INTEGRATION_WITH_PR_PREP.md` for the full migration path and the 5 specific changes to `pr-prep`.

---

## Common Failure Modes (and how to avoid them)

| Symptom | Root cause | Fix |
|---------|------------|-----|
| ERRORS skipped, production pages at 2am | FUNC shipped without the error matrix | Make ERRORS non-skippable for Critical Path tier — ARCH's dependency graph flags this |
| Runbook is stale the day after merge | DOCS ran before ERRORS/OBSV settled | DOCS must run **last**; if ERRORS or OBSV change post-DOCS, re-run DOCS |
| PR is too big to review | Multiple features bundled into one worktree | Apply the **artifact test**: if `arch.md` covers more than one decision, split the PR |
| Two parallel doc trees drift | `pr-prep` regenerated what orchestrators already wrote | Promote orchestrator artifacts to `docs/pr-prep/pr{N}/` and delete `_bmad-output/pr-prep/` |
| Orchestrator references fail to resolve | Guide repo not installed as sibling/submodule | Clone it at `~/workspace/software-development-best-practices-guide` or adjust paths |
| Team bypasses orchestrators because "too heavy" | All features forced through Critical Path tier | Tier-adjust: bug fixes are FUNC + REVIEW only |

---

## The One Non-Negotiable Rule

**One feature per PR.** LOC count, file count, and commit count are signals — they trigger a "justify or split" conversation, not a hard block. The real test is the **artifact test**: does this PR have exactly one coherent `arch.md`? If yes, size is fine. If the artifacts are plural or blended, the PR is too big regardless of line count.

---

## Example: F-14 TikTok Returns Flow

```
# Day 1 — ARCH
$ cd ../repo-F-14
> "architecture review for F-14 TikTok returns"
  → .feature-factory/arch.md (Critical Path, blocked by F-12 auth, blocks F-15)

# Day 2 — FUNC
> "implement F-14 with TDD"
  → code + .feature-factory/func.md (8 files, 94% coverage)

# Day 3 — ERRORS + OBSV + REVIEW in three terminals
Terminal A: > "error matrix for F-14 TikTok returns"
            → .feature-factory/errors.md (14 failure modes, 4 retry policies)
Terminal B: > "observability plan for F-14"
            → .feature-factory/observability.md (3 metrics, 2 alerts, 1 dashboard)
Terminal C: > "review F-14 code for smells"
            → cleaner code + .feature-factory/review.md (2 SOLID fixes, 1 DRY extraction)

# Day 4 — DOCS
> "write runbook for F-14"
  → .feature-factory/runbook.md + updated CLAUDE.md

# Day 4 — PR
> /pr-prep
  → consumes all 6 artifacts, generates PR body, promotes artifacts to docs/pr-prep/pr42/
```

Four days, six artifacts, one merged PR, zero midnight pages.

---

## Reference

- `README.md` — system overview
- `INTEGRATION_WITH_PR_PREP.md` — how the orchestrators + `pr-prep` fit together
- `{bucket}-orchestrator/SKILL.md` — per-bucket skill definition, triggers, and detailed workflow
- `06-collaborative-construction/AGENTIC_CODING_OPTIMIZATION.md` — parallel-execution strategy the orchestrators build on
- `10-geist-gap-analysis-framework/` — Geist analysis (used inside ARCH's decision process)
