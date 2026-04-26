---
name: pr-prep
description: >
  Prepares a pull request by analyzing commits, detecting existing PRs, ingesting
  Feature Factory bucket artifacts, and spawning a parallel agent team to produce
  .feature-factory/_pr-prep/<pr-folder>/ deliverables: updated PRD, code/test audit,
  docs audit (with in-place fixes), manual testing guide, a ready-to-paste PR
  description, a documentation commit plan, Excalidraw architecture & flow diagrams,
  Playwright E2E regression tests, automated screenshots, walkthrough recordings with
  Remotion video presentation (perception holds, voiceover, test coverage diagram
  slides). Use when ready to open or update a PR.
allowed-tools: [Agent, Bash, Read, Glob, Grep, Write, Edit, AskUserQuestion]
---

# PR Prep Skill

## Purpose

Automate the analysis and documentation work needed before opening or updating a pull request. Spawns a parallel team of specialist agents — each owning a distinct concern — and assembles their outputs into a ready-to-use PR package in `.feature-factory/_pr-prep/<pr-folder>/`.

When the project uses the Feature Factory pipeline (`.feature-factory/<feature-slug>/` exists), pr-prep ingests the upstream bucket artifacts (`arch.md`, `func.md`, `errors.md`, `observability.md`, `review.md`, `runbook.md`) and uses them as authoritative source material for the audit, docs check, and PR description — never re-deriving findings the Feature Factory has already authored.

## When to Use

- "prep a PR for this branch"
- "get me ready to open a PR"
- "update the PR with these new commits"
- "/pr-prep"
- "run pr-prep"

---

## Output Locations

Per Spec 4 (`docs/specs/pr-prep-feature-factory-4-organization.md`), all pr-prep outputs are written under a single PR-scoped folder inside `.feature-factory/`. The legacy `_bmad-output/pr-prep/`, `docs/pr-prep/pr<N>/`, and project-root `screenshots/pr<N>/` paths are retired.

### Layout

```
.feature-factory/
├── <feature-slug>/                              ← per-feature artifacts (owned by orchestrators)
│   ├── arch.md
│   ├── func.md
│   ├── errors.md
│   ├── observability.md
│   ├── review.md
│   ├── runbook.md
│   └── pr-history.md                            ← pr-prep Phase 4 appends rows here
└── _pr-prep/                                    ← PR-scoped outputs (owned by pr-prep)
    └── pr-<N>-<short-feature-slug>/
        ├── manifest.yaml                        ← Spec 4 schema
        ├── feature-factory-context.md           ← Phase 2c digest (Spec 1)
        ├── updated-prd.md                       ← Agent 1
        ├── code-test-audit.md                   ← Agent 2
        ├── docs-audit.md                        ← Agent 3
        ├── manual-testing-guide.md              ← Agent 4
        ├── pr-description.md                    ← Agent 4
        ├── docs-commit-plan.md                  ← Phase 4.5 (Spec 3)
        ├── proposed-claude-md-edits.md          ← Phase 4.5 (only when multi-section CLAUDE.md edit proposed)
        ├── last-mile.md                         ← optional readiness doc
        └── evidence/
            ├── screenshots/                     ← Phase 5b
            ├── recordings/                      ← Phase 6 walkthrough .webm files
            └── google-drive-evidence.md         ← Phase 5
```

### `<pr-folder>` naming convention

`pr-<N>-<short-slug>/` where `<N>` is the GitHub PR number (or the pre-PR placeholder if no PR exists yet) and `<short-slug>` is a 2–4-word kebab-case abbreviation of the primary feature for this PR. For multi-feature PRs use the most representative feature; the `manifest.yaml` enumerates all.

Examples: `pr-9-catalog-sync-dropdown/`, `pr-12-merchant-onboarding/`.

### `manifest.yaml` schema

```yaml
pr_number: 9
branch: worktree-pr9-catalog-sync-dropdown
base: mcf-order-fulfillment
features:
  - catalog-sync-dropdown
created: 2026-04-25
status: in-progress  # in-progress | open | merged | closed
notes: |
  Cross-repo Remotion assets live at:
  ~/workspace/agency-operations/video-studio/public/pr9/
```

The `notes` field documents any cross-repo asset paths (e.g. Remotion `video-studio/public/pr<N>/` in agency-operations) that aren't co-located inside this PR folder.

### `pr-history.md` append behavior

Phase 4 (Synthesis) appends one row to `.feature-factory/<feature-slug>/pr-history.md` for **each feature listed in `manifest.yaml.features`**. Schema (matches the orchestrator skills' format):

```markdown
| PR | Status | Date | Branch | Summary | Audit folder |
|----|--------|------|--------|---------|--------------|
| #9 | in-progress | 2026-04-25 | <branch> | One-line PR summary | [`_pr-prep/pr-9-catalog-sync-dropdown/`](../_pr-prep/pr-9-catalog-sync-dropdown/) |
```

If `pr-history.md` is absent in a feature folder, pr-prep creates it with the schema header before appending the row.

### Evidence layout

- `evidence/screenshots/<scenario>/` — Phase 5b automated screenshots (one subfolder per test scenario)
- `evidence/recordings/` — Phase 6 walkthrough `.webm` files (raw input for Remotion)
- `evidence/google-drive-evidence.md` — Phase 5 distribution doc with Drive links

Cross-repo Remotion sources (`~/workspace/agency-operations/video-studio/public/pr<N>/` and `PR<N>TestEvidence.tsx`) remain in the agency-operations workspace; reference them from `manifest.yaml.notes`.

---

## EXECUTION WORKFLOW

### Phase 1 — Situation Assessment

Run these in parallel to understand the current state:

```bash
# What branch are we on and what commits are new since main?
git log origin/main..HEAD --oneline

# Is there already an open PR for this branch?
gh pr list --head "$(git branch --show-current)" --json number,title,url,state

# What's the most recent PR that could serve as a format template?
gh pr list --state merged --limit 3 --json number,title,url

# Detect potential base branches — recent merged/open PRs that this branch may stack on
gh pr list --state all --limit 10 --json number,title,state,headRefName,mergeCommit,baseRefName

# Check if there's a merge-base other than main that makes more sense
git merge-base origin/main HEAD
```

Also check for existing pr-prep outputs (under the new layout — see "Output Locations" above):
- Glob `.feature-factory/_pr-prep/pr-*-*/` to find any prior PR folders for this branch.
- If found, does `<pr-folder>/pr-description.md` already exist?
- Does `<pr-folder>/updated-prd.md` already exist?
- Read `<pr-folder>/manifest.yaml` if present — it tells you the PR number, base branch, and feature slugs already in use.
- What is the most recent PRD? Check `docs/plans/current/prd.md` and `_bmad-output/planning-artifacts/prd.md` (legacy planning artifact location, not retired).

### Phase 2 — Confirm Scope (Base Branch & Commit Range)

**This step is critical.** Before presenting the full assessment, confirm which code should be considered for this PR. This prevents wasted analysis on commits that belong to a prior PR.

**Detection logic:**
1. Count commits from `origin/main..HEAD`. If the count is large (>15), this branch likely stacks on a prior PR.
2. Check if any recent merged/open PRs share a common history with this branch (e.g., the branch was created from another feature branch, not main).
3. Look for clues: PR titles referencing "PR #N", branch names with version suffixes, or commit messages mentioning prior PRs.

Present the scope confirmation as the FIRST question:

```
📋 PR SCOPE CHECK

Branch: {branch-name}
Total commits since main: {N} commits

⚠️  This branch has {N} commits since main, which may include
work from prior PRs. Let me confirm what belongs to THIS PR:

  Option A (default): Diff against origin/main ({N} commits)
    → All changes since main — use if this is the only PR

  Option B: Diff against PR #{M}'s merge point ({X} commits)
    → Only changes added AFTER PR #{M} was submitted
    → Detected: PR #{M} "{title}" shares {Y} commits with this branch

  Option C: Custom base — specify a branch, tag, or commit SHA

Which base should I use? [A/B/C]
```

**If only a few commits since main (≤15) and no stacked PR detected**, simplify:

```
📋 PR SCOPE CHECK

Branch: {branch-name}
Commits since main: {N} commits
  - {commit 1 summary}
  - {commit 2 summary}
  - ...

Does this look right? These are the commits I'll analyze for this PR.
[yes / specify different base]
```

Wait for the user's answer before proceeding to the full assessment.

**Once scope is confirmed**, use the confirmed base for ALL subsequent commands:
- Replace `origin/main..HEAD` with `{confirmed-base}..HEAD` in all agent prompts
- Use `git diff {confirmed-base}...HEAD` instead of `git diff origin/main...HEAD`
- Store the confirmed base as `PR_BASE` and reference it throughout

### Phase 2b — Full Assessment

After scope is confirmed, present the full assessment:

```
📋 PR PREP ASSESSMENT

Branch: {branch-name}
Base: {confirmed-base} ({N} commits)
  - {commit 1 summary}
  - {commit 2 summary}
  - ...

Existing PR: {YES → PR #{N}: "{title}" / NO → none found}

Previous pr-prep outputs: {found / not found}
Template PR to follow: PR #{N} — "{title}"

I'll launch 4 parallel agents to produce (under `.feature-factory/_pr-prep/<pr-folder>/`):
  • feature-factory-context.md   — digest of upstream FF artifacts (Phase 2c, if present)
  • updated-prd.md               — PRD gap analysis
  • code-test-audit.md           — requirements coverage + test quality + FF cross-check
  • docs-audit.md                — docs accuracy (fixes applied in-place) + FF doc mapping
  • manual-testing-guide.md      — manual test scenarios (table format)
  • pr-description.md            — PR body (ready to paste into GitHub)

Then subsequent phases will produce:
  Phase 4.5 — Documentation Commit Plan (only when feature-factory-context.md exists):
  • <pr-folder>/docs-commit-plan.md          — per-artifact disposition table
  • Per-row CREATE/EDIT applied to docs/runbooks/, docs/features/, docs/architecture/, ADRs

  Phase 5a — Excalidraw Diagrams (via MCP):
  • <pr-folder>/evidence/screenshots/excalidraw-{name}.png   — Architecture & flow diagrams
  • video-studio/public/pr{N}/*.png                          — Diagram assets for Remotion (cross-repo)

  Phase 5b — Playwright E2E Tests & Screenshots (via MCP):
  • e2e/tests/s{N}-{name}.spec.ts                            — Regression test specs per scenario
  • <pr-folder>/evidence/screenshots/<scenario>/*.png        — Automated test screenshots

  Phase 6 — Walkthrough Recordings & Remotion Video:
  • e2e/tests/walkthrough.spec.ts                            — Playwright walkthrough recordings
  • <pr-folder>/evidence/recordings/*.webm                   — Raw walkthrough recordings
  • video-studio/src/pr{N}-video-config.ts                   — Config: timing, holds, VO, slides (cross-repo)
  • video-studio/src/PR{N}TestEvidence.tsx                   — Remotion video composition (cross-repo)

Generate assets (diagrams, E2E tests, video)?
  → [yes] Full run (Phases 5a + 5b + 6)
  → [no]  Analysis only (Phases 3 + 4 — fast iteration mode)
  → [assets-only] Skip to Phase 5a (analysis already done)

Proceed? — or specify a different template PR number.
```

Wait for user confirmation before launching agents. If user specifies a commit range (e.g. "just the last 3 commits" or "from abc123 to HEAD"), use that range in the agents' prompts.

**Asset generation gating:**
- If user chooses **"no"** (or `/pr-prep --skip-assets`): run only Phases 1–4 (analysis, audits, PR description). Skip Phases 5a, 5b, and 6 entirely. This is the fast iteration path — useful for early/mid-cycle PR prep when the code is still changing.
- If user chooses **"yes"**: run all phases including asset generation.
- If user chooses **"assets-only"** (or `/pr-prep --assets-only`): skip Phases 3–4 (assume analysis is already done from a previous run), jump straight to Phases 5a → 5b → 6.
- The Phase 4 summary should remind the user: "Run `/pr-prep --assets-only` when ready to generate diagrams, tests, and video."

---

### Phase 2c — Feature Factory Ingestion

Per Spec 1 — see `docs/specs/pr-prep-feature-factory-1-ingestion.md`. This phase consumes upstream Feature Factory bucket artifacts as authoritative source material so the parallel agents in Phase 3 verify (rather than re-derive) what the orchestrators already authored.

Skip this phase entirely if:
- The user passed `--no-feature-factory`, OR
- No `.feature-factory/<slug>/` folder exists (other than the reserved `guide/` and `_pr-prep/`).

#### Step 1 — Detect feature folders

Glob `.feature-factory/*/` from the project root. Exclude:
- `.feature-factory/guide/` (reserved for the best-practices guide submodule)
- `.feature-factory/_pr-prep/` (reserved for pr-prep's own outputs)

Build a list of candidate `<feature-slug>` folders, each with its last-modified timestamp (use `git log -1 --format=%ci -- .feature-factory/<slug>/` or `stat`).

#### Step 2 — Resolve slug

| Folders found | Behavior |
|---------------|----------|
| 0 | No-op. Log: "No feature-factory artifacts found; skipping Phase 2c." Continue to Phase 3 with no digest. |
| 1 | Use it automatically. Print: "Using feature-factory slug: `<slug>`." |
| 2+ | Print the list with last-modified timestamps and ask the user to select one (or type `none` to skip). Default in Spec 1: always-prompt initially; auto-detection from branch name is a future enhancement. |

If `manifest.yaml` for this PR's folder already exists and lists a `features:` array, use that list directly (multi-feature PRs read all listed folders).

#### Step 3 — Read bucket artifacts

For each selected slug, read each of the 6 bucket artifacts:
- `.feature-factory/<slug>/arch.md`
- `.feature-factory/<slug>/func.md`
- `.feature-factory/<slug>/errors.md`
- `.feature-factory/<slug>/observability.md`
- `.feature-factory/<slug>/review.md`
- `.feature-factory/<slug>/runbook.md`

Missing files are non-fatal — a feature may have skipped buckets. Log which buckets were absent.

#### Step 4 — Write the digest

Write `.feature-factory/_pr-prep/<pr-folder>/feature-factory-context.md` with this structure:

```markdown
# Feature Factory Context — <pr-folder>

**Slug(s):** <feature-slug>[, <slug2>, ...]
**Source:** .feature-factory/<feature-slug>/
**Buckets present:** arch ✓ | func ✓ | errors ✓ | observability ✓ | review ✓ | runbook ✓
**Buckets absent:** [list]
**Generated:** <ISO date>

## Architecture (from arch.md)
[Load-bearing decisions only — NOT a verbatim copy. One bullet per major decision.
 Include: decision, rationale-summary, and which modules are affected.]

## Functionality (from func.md)
[Shipped FRs with one-line summary each, plus any "implemented but undocumented" notes.]

## Error Handling (from errors.md)
[Failure-mode catalog summary: count + key categories. Pass the full table to Agent 2.]

## Observability (from observability.md)
[Metrics, log keys, dashboards added. Pass the full instrumentation list to Agent 2.]

## Review Findings (from review.md)
[Each finding with disposition claim:
 - "Fix in this PR" → Agent 2 must verify diff + test
 - "Track as follow-up" → Agent 2 must verify spec file exists in docs/specs/
 - "Deferred per spec" → cite the spec
 Stale-detection note (Spec 2 #4): if review.md mtime is older than HEAD commit,
 prepend a warning that the artifact may not reflect the latest diff.]

## Runbook (from runbook.md)
[Operational steps catalogued. Phase 4.5 will propose committing this content.]

## Open Items Across All Buckets
[Aggregate any item not marked resolved:
 - review.md issues without "VERIFIED" status
 - errors.md failure modes flagged "needs handling"
 - observability.md unimplemented metrics
 - runbook.md TODOs
 Each item gets a citation: source file + section.]
```

The digest is **load-bearing claims, not a verbatim copy**. The point is to give Phase 3 agents a fast read-once reference; they can drill into the source artifact when they need depth.

#### Step 5 — Initialize manifest if absent

If `.feature-factory/_pr-prep/<pr-folder>/manifest.yaml` does not yet exist, create it using the schema from "Output Locations" above:

```yaml
pr_number: <N>           # from gh pr list, or pre-PR placeholder
branch: <current-branch>
base: <confirmed-base from Phase 2>
features:
  - <feature-slug>
created: <ISO date>
status: in-progress
```

#### Step 6 — Wire the digest into Phase 3

Pass `feature-factory-context.md`'s absolute path to all 4 parallel agents in Phase 3 as **required reading** (loaded before primary research instructions). Each agent's prompt has bucket-specific verification responsibilities — see Phase 3 below.

#### CLI flag

`/pr-prep --no-feature-factory` skips Phase 2c even when a folder exists. Default behavior is opt-in: use feature-factory data when available.

---

### Phase 3 — Parallel Agent Team

Once confirmed, launch ALL FOUR agents simultaneously in a single message (parallel, not sequential):

---

#### Agent 1: PRD + Requirements Gap Analysis (Mary/John)

**Goal:** Read the existing PRD(s), map the complete feature lifecycle, identify gaps between requirements and code, and write an updated comprehensive PRD.

**Required reading (when present):** `.feature-factory/_pr-prep/<pr-folder>/feature-factory-context.md` — load FIRST, before any code reading. Per Spec 2 — see `docs/specs/pr-prep-feature-factory-2-enrichment.md`.

**Key instructions for this agent:**
- Read `docs/plans/current/prd.md`, `_bmad-output/planning-artifacts/prd.md`, any other PRD files found
- Read the main webhook endpoint file and data model files to understand what's actually implemented
- Map every external event type (webhooks, API responses, status transitions) against FRs
- For each FR: determine implementation status (✅ Implemented / ⚠️ Partial / ❌ Missing/Blocked)
- Note code file references for each implemented FR
- Flag any behavior discovered in code that is NOT in the PRD (undocumented features or bugs)
- Write to: `.feature-factory/_pr-prep/<pr-folder>/updated-prd.md`

**Feature Factory enrichment (when `feature-factory-context.md` is present):**
- Read `.feature-factory/<slug>/arch.md`. For each architectural decision, verify the resulting FR(s) in the PRD do not contradict it. Flag any FR that conflicts as `[FF-CONFLICT]` in the PRD's Open Spikes section.
- Read `.feature-factory/<slug>/func.md`. Verify the FR-to-implementation mapping covers everything `func.md` claims was built. If `func.md` lists shipped functionality not covered by an FR, ADD the FR (don't omit shipped behavior from the PRD).
- Tag each FR with its primary source: `**Source:** func.md`, `**Source:** arch.md`, or `**Source:** Code inspection` for FRs derived only from reading the diff.

**Output structure:**
```markdown
# [Project] PRD — [Feature/Lifecycle Name]
**Version:** N.0  **Date:** {today}  **Status:** Active

## Overview / Scope / Out of Scope

## Functional Requirements
### FR-XXX — [Title]
- **Description:** ...
- **Trigger/Event:** ...
- **Acceptance Criteria:** [testable by human using dev portal]
- **Implementation Status:** ✅/⚠️/❌
- **Code Reference:** path/to/file.py:line
- **Source:** func.md | arch.md | Code inspection

## Non-Functional Requirements
## Open Spikes / Unconfirmed Assumptions
[Include any [FF-CONFLICT] entries — FRs that contradict arch.md decisions.]
## Implementation Status Summary Table
```

---

#### Agent 2: Code & Test Audit (Murat/Amelia)

**Goal:** Audit whether code implements each FR and whether tests actually validate the implementation. When Feature Factory artifacts are present, additionally verify each `errors.md` failure mode has test coverage, each `observability.md` instrumentation item shipped, and each `review.md` finding's claimed disposition is real. **This is the highest-leverage enrichment** — Agent 2 is where PR #8's missed C-1/C-2/C-3 findings need to surface.

**Required reading (when present):** `.feature-factory/_pr-prep/<pr-folder>/feature-factory-context.md` — load FIRST. Per Spec 2 — see `docs/specs/pr-prep-feature-factory-2-enrichment.md`.

**Key instructions for this agent:**
- Read all PRD/requirements docs first
- Read the test directory structure — list all test files, categorize by type (unit/integration/e2e/prd_validation/contract)
- For each FR: find the implementing code AND the tests that cover it
- Assess test quality: Does the test verify behavior or just mock everything? Does it test error paths? Does it use `autospec=True`?
- Flag dead tests (ImportError, permanent skip without reason, tests against removed functions)
- Flag hollow tests (tests that pass but don't assert the right things)
- Flag false-confidence tests (mocking at wrong boundary, testing implementation not behavior)
- Write to: `.feature-factory/_pr-prep/<pr-folder>/code-test-audit.md`

**Feature Factory cross-check (when `feature-factory-context.md` is present):**

Add a top-level section to `code-test-audit.md` called **"Feature Factory Cross-Check"** containing the three tables below. Tag every cross-check finding with a `[FF]` prefix to distinguish it from primary-discovery findings (which keep the existing CRIT/HIGH/MED labels).

**Stale-detection guard:** Compare `.feature-factory/<slug>/review.md` mtime against the latest in-scope commit timestamp (`git log -1 --format=%ct {confirmed-base}..HEAD`). If `review.md` is older than the HEAD commit, **prepend a warning** to the cross-check section:
> ⚠️ **Feature-factory artifacts may be stale** — `review.md` is N hours older than the HEAD commit. Findings below may not reflect the latest diff.

**Table 1 — Failure-mode coverage (from `errors.md`):**

For each documented failure mode in `errors.md`, search tests for an assertion of the documented behavior. Produce:

```
| Failure mode (errors.md) | Documented response | Test? | File:line | Notes |
```

Failure modes without a test become `[FF] MISSING-TEST` entries in "Recommended Actions."

**Table 2 — Observability shipment (from `observability.md`):**

For each metric, structured log key, or dashboard entry in `observability.md`, search code for the corresponding instrumentation (grep metric name; grep log key). Produce:

```
| Item (observability.md) | Type | Shipped? | File:line | Notes |
```

Items not shipped become `[FF] NOT-SHIPPED` entries.

**Table 3 — Review-disposition verification (from `review.md`):**

For each finding in `review.md`, classify the disposition claim and verify it. Per Spec 2 #2: VERIFIED requires **both diff present AND test added**; if the diff is present but no test, mark `VERIFIED-NO-TEST` and add it to the coverage gaps:

| Disposition claim | Verification | Mark as |
|-------------------|--------------|---------|
| "Fix in this PR's review commit" | grep diff for the fix | `VERIFIED` (diff + test) / `VERIFIED-NO-TEST` (diff only) / `MISSING` (no diff) / `PARTIAL` (incomplete fix) |
| "Track as follow-up" | verify a spec file exists in `docs/specs/` | `VERIFIED` or `MISSING-SPEC` |
| "Deferred per spec" | verify the cited spec exists | `VERIFIED` or `MISSING-SPEC` |

Produce:

```
| Finding (review.md) | Disposition claim | Verified? | Evidence | Mark |
```

Any item flagged `[FF] MISSING` (a "Fix in this PR" claim with no corresponding code change in the diff) is a **pre-merge blocker** — Agent 4 will surface it under "⚠️ Pre-merge action required" in the PR description.

**Conflicting claims (Spec 2 #3):** If `arch.md` and the implementation disagree (e.g., arch says Redis cache, code uses in-memory), add a "FF Drift" subsection inside the cross-check listing each conflict. **Never silently override either source — surface the conflict and let the human resolve.**

**Output structure:**
```markdown
# Code & Test Audit
**Date:** {today}

## Feature Factory Cross-Check
[Only when feature-factory-context.md present.
 Stale-detection warning if applicable.
 Table 1 — Failure-mode coverage
 Table 2 — Observability shipment
 Table 3 — Review-disposition verification
 FF Drift subsection (any arch/code conflicts)]

## Requirements Coverage Matrix
| FR ID | Requirement | Code ✅/⚠️/❌ | Unit Tests | Integration | PRD Validation | Notes |

## Test Quality Assessment
### [Suite Name]
- Files, what it tests, quality (HIGH/MEDIUM/LOW), issues, gaps

## Critical Issues
[Dead tests, hollow tests, false-confidence, broken imports]
[Primary discoveries: CRIT/HIGH/MED labels]
[Cross-check findings: [FF] prefix]

## Recommended Actions (prioritized)
[Mix primary + [FF] items, ordered by severity]

## Summary Stats
```

---

#### Agent 3: Documentation Audit + In-Place Fixes (Paige)

**Goal:** Audit all documentation files for accuracy, fix inaccuracies in-place, and report what changed. When Feature Factory artifacts are present, additionally map each FF artifact to its committed-doc home (or flag as unmapped for Phase 4.5 to commit).

**Required reading (when present):** `.feature-factory/_pr-prep/<pr-folder>/feature-factory-context.md` — load FIRST. Per Spec 2 — see `docs/specs/pr-prep-feature-factory-2-enrichment.md`.

**Key instructions for this agent:**
- Read CLAUDE.md, all AGENTS.md files, README.md, and key docs/ files
- For each doc, verify against actual filesystem structure (use Glob to check paths exist)
- Check "fully implemented" sections — are they still accurate?
- Check "known gaps" sections — are gaps still gaps, or have they been closed?
- Check command references, file paths, architecture diagrams, migration status dates
- Fix every inaccuracy directly in the file using Edit tool
- Write audit report to: `.feature-factory/_pr-prep/<pr-folder>/docs-audit.md`

**Feature Factory enrichment (when `feature-factory-context.md` is present):**
- Read `.feature-factory/<slug>/runbook.md`. Verify its content is reflected somewhere committed:
  - New file in `docs/runbooks/` or `docs/features/<feature>-*.md`, OR
  - A section in `CLAUDE.md`, an `AGENTS.md`, or relevant `docs/` page
  If NOT mapped, add to "Items needing human input" with disposition: "runbook content unmapped to committed docs — Phase 4.5 will propose a commit plan."
- Read `.feature-factory/<slug>/arch.md`. Verify each architectural decision is reflected in `docs/architecture/ARCHITECTURE.md` or a new ADR in `docs/adr/`. If neither, flag for human input — Phase 4.5 will propose an ARCHITECTURE.md edit (per Spec 3 #4: never auto-create ADRs).
- Add a top-level **"Feature Factory Doc Mapping"** section to `docs-audit.md` with this table:

```
| FF artifact | Committed home | Status | Notes |
|-------------|----------------|--------|-------|
| arch.md | docs/architecture/ARCHITECTURE.md (`## Catalog Sync` section) | mapped | |
| runbook.md | (none) | unmapped | Phase 4.5 will propose docs/runbooks/<feature>.md |
| errors.md | (none) | unmapped | Phase 4.5 will propose docs/features/<feature>-error-handling.md |
| observability.md | (none) | unmapped | Phase 4.5 will propose docs/features/<feature>-observability.md |
| func.md | n/a | skip | Implementation summary; not user-facing |
| review.md | n/a | skip | Working artifact; resolved items captured in pr-description |
```

The "unmapped" items become inputs to Phase 4.5's commit plan.

**Output structure:**
```markdown
# Documentation Audit Report
**Date:** {today}

## Summary — [N] inaccuracies found, [N] fixed

## Feature Factory Doc Mapping
[Only when feature-factory-context.md present.
 Table mapping each FF artifact to committed-doc home or "unmapped".]

## Files Audited
| File | Issues Found | Fixed | Remaining |

## Changes Made
[Each change: file, what was wrong, what was written]

## Items Needing Human Input
[Things that need product/developer decision to resolve]
[Include any "unmapped" FF artifacts flagged for Phase 4.5]
```

---

#### Agent 4: Manual Testing Guide + PR Description (Bob/Sally)

**Goal:** Produce a comprehensive human-readable manual testing guide and a GitHub-ready PR description. When Feature Factory artifacts are present, synthesize the PR description from those authoritative sources rather than from commit messages alone.

**Required reading (when present):** `.feature-factory/_pr-prep/<pr-folder>/feature-factory-context.md` — load FIRST. Per Spec 2 — see `docs/specs/pr-prep-feature-factory-2-enrichment.md`.

**Key instructions for this agent:**

**Manual Testing Guide:**
- Read the PRD, main endpoint files, and frontend pages to understand all testable flows
- Cover every FR with at least one manual test scenario
- Structure as markdown tables: Scenario | Steps | Expected Result | Dev Portal Action | Pass/Fail
- No new UI components — test only what real customers see
- Include specific UI navigation (e.g. "Click Configuration → TikTok → Connect")
- Include specific dev portal actions (e.g. "In TikTok test shop, create order with status AWAITING_SHIPMENT")
- Include a Recording Guide section (what to capture for Google Drive folder)
- Write to: `.feature-factory/_pr-prep/<pr-folder>/manual-testing-guide.md`

**PR Description:**
- Fetch the template PR body via `gh pr view {template_pr_number} --json body`
- Follow that format exactly, adapting content for this branch's changes
- **Start with a "Related Docs" section at the very top** — a table linking to all key documents a reviewer needs. Include UX mockups, PRDs, requirements map, test evidence, and planning docs. Format:
  ```
  ## Related Docs

  | Document | Description |
  |----------|-------------|
  | [UX Design Directions](LINK) | Interactive HTML mockups for the feature UI |
  | [PRD](LINK) | Product requirements document |
  | [Requirements Map](LINK) | FR traceability — status, test coverage, spikes |
  | [Test Evidence (Screenshots)](LINK) | Test folders with screenshots + README explanations |
  | [Test Evidence INDEX](LINK) | Test case guide with PRD requirement traceability |
  | [Planning Documents](LINK) | All planning docs folder |
  ```
  Search `_bmad-output/planning-artifacts/` for UX mockup HTML files and upload to Google Drive if not already there. Check `<pr-folder>/evidence/google-drive-evidence.md` for existing Drive links.
- Replace individual video links with a single Google Drive folder block:
  ```
  📹 **[View all test recordings →](GOOGLE_DRIVE_FOLDER_LINK)**
  _(Videos organized by feature area — see Manual Testing Guide for scenario details)_
  ```
- Summarize commits into "What's Included" sections
- **Include a "What This PR Does NOT Include" section** — a table clarifying what is explicitly out of scope for this PR and where it's planned. This helps reviewers understand scope boundaries and prevents "why didn't you also do X?" questions. Read the PRD and prior PRs to identify deferred work, then present as:
  ```
  | Area | Status | Planned |
  |------|--------|---------|
  | [Feature X] | [Why it's not here] | [Next PR / Separate PR / Pre-launch] |
  ```
- **Frame testing issues as "caught and resolved"** — do not say "bugs found" in the summary line or imply outstanding defects. Use past tense ("sent" → "fixed") and label the section "Issues Caught and Resolved During Testing"
- Include a "What Changed Since PR #{template}" comparison table if updating an existing PR
- Include automated test plan checklist + manual test checklist referencing the guide sections
- Write to: `.feature-factory/_pr-prep/<pr-folder>/pr-description.md`

**Feature Factory enrichment (when `feature-factory-context.md` is present):**

Add these sections to the PR description, sourced from feature-factory artifacts (NOT invented from commit messages):

- **Architecture Decisions** — bulleted summary from `arch.md` (one bullet per major decision; cite the affected modules).
- **Error Handling** — high-level summary from `errors.md` (number of failure modes catalogued, key categories: transient retryable vs permanent vs auth-recoverable, etc.).
- **Observability** — summary from `observability.md` (metrics added, structured log keys, dashboards updated).
- **Issues Caught and Resolved** — sourced from `review.md` items marked "Fix in this PR" + verified shipped per Agent 2's Table 3. Frame in past tense; do NOT say "bugs found." Cite each finding's resolved file:line.
- **⚠️ Pre-merge action required** — only if Agent 2's Table 3 flagged any "Fix in this PR" item as `[FF] MISSING`. List each missing fix with citation; do NOT publish the PR until these are resolved.
- **Runbook entry** — link to the committed runbook location (after Phase 4.5 runs, this is `docs/runbooks/<feature>.md` or similar). If still uncommitted (Phase 4.5 deferred or rejected the runbook row), link to `.feature-factory/<slug>/runbook.md` with a note "TODO: commit before merge."

When `feature-factory-context.md` is absent, behavior is unchanged from today (synthesize from commits).

**Re-run trigger:** Phase 4.5 (when present) re-invokes Agent 4 after committing docs so the "Related Docs" and "Runbook entry" sections reference the new in-repo paths instead of working-artifact paths.

---

### Phase 4 — Synthesis & Summary

After all 4 agents complete, perform two synthesis steps:

**Step 1 — Append `pr-history.md` rows.** For each feature listed in `manifest.yaml.features` (Phase 2c):

1. Locate `.feature-factory/<feature-slug>/pr-history.md`. If absent, create it with the schema header from "Output Locations" above.
2. Append one row to the table:

```
| #N | in-progress | YYYY-MM-DD | <branch> | One-line summary | [`_pr-prep/pr-N-<short-slug>/`](../_pr-prep/pr-N-<short-slug>/) |
```

The orchestrator skills update the row's "Status" later as the PR moves through review → merge.

**Step 2 — Present consolidated summary:**

```
✅ PR PREP COMPLETE — .feature-factory/_pr-prep/<pr-folder>/

📄 Files produced:
  feature-factory-context.md — digest of <slug>/{arch,func,errors,observability,review,runbook}.md (if present)
  updated-prd.md             — [N] FRs: [N] implemented, [N] partial, [N] blocked
  code-test-audit.md         — [N]% FRs with full coverage, [N] critical test issues, [N] [FF] cross-check items
  docs-audit.md              — [N] inaccuracies fixed across [N] files; [N] FF artifacts unmapped
  manual-testing-guide.md    — [N] sections, ~[N] scenarios
  pr-description.md          — Ready to paste (replace GOOGLE_DRIVE_FOLDER_LINK)

🔗 Feature-factory back-references:
  Appended row to .feature-factory/<slug>/pr-history.md

🚨 Blockers to fix before opening PR:
  [List any CRITICAL gaps surfaced by agents]
  [List any [FF] MISSING items — "Fix in this PR" claims with no diff]

⚠️ Items needing your input:
  [Spikes, unconfirmed assumptions, open questions]
  [Unmapped FF artifacts → Phase 4.5 will propose a commit plan]

📋 Next steps:
  1. Complete your spikes (see Open Spikes in updated-prd.md)
  2. If feature-factory artifacts exist: review docs-commit-plan.md (Phase 4.5)
  3. Run manual tests from manual-testing-guide.md, capture screenshots
  4. When ready for assets: `/pr-prep --assets-only` (diagrams, E2E tests, video)
  5. Run Phase 5 to upload evidence and finalize PR
```

---

### Phase 4.5 — Documentation Commit Plan

Per Spec 3 — see `docs/specs/pr-prep-feature-factory-3-commit-plan.md`. This phase decides which Feature Factory artifacts should be promoted into committed project documentation, presents the plan for approval, and stages (but does not commit) the approved files.

**No-op when `feature-factory-context.md` is absent** — proceed to Phase 5a.

**Run between Phase 4 (Synthesis) and Phase 5a (Excalidraw).** Operate per-feature: if `manifest.yaml` lists multiple features, iterate through them, producing one section per feature in `docs-commit-plan.md`. Per Spec 3 #5: multi-feature PRs run Phase 4.5 once per slug; users wanting more granular processing re-run pr-prep with each slug.

#### Step 1 — Read inputs

- `.feature-factory/_pr-prep/<pr-folder>/feature-factory-context.md` (Phase 2c digest)
- `.feature-factory/<slug>/{arch,errors,observability,review,runbook,func}.md` (source artifacts)
- **Project doc convention discovery.** Glob each of these directories; presence of any files = "the convention is established":
  - `docs/runbooks/`
  - `docs/features/` — also inspect existing filenames to detect flat (`<feature>-<topic>.md`) vs subdirectory (`<feature>/<topic>.md`) naming
  - `docs/adr/`
  - `docs/architecture/`

If `docs/features/` exists with files using flat naming (e.g., `docs/features/catalog-sync-error-handling.md`), the proposal MUST follow that convention — propose `docs/features/<feature>-error-handling.md`, NOT `docs/features/<feature>/error-handling.md`. This matches the existing project convention; flat is the default per Spec 3 open-question #1 resolution.

#### Step 2 — Propose commit plan

Default dispositions per Spec 3:

| FF artifact | Default disposition | Default target | Notes |
|-------------|---------------------|----------------|-------|
| `arch.md` | EDIT existing | `docs/architecture/ARCHITECTURE.md` (single section) | Per Spec 3 #4: never auto-create an ADR. If user thinks one is warranted, they create it separately. |
| `func.md` | SKIP | n/a | Implementation summary; not user-facing. |
| `errors.md` | CREATE | `docs/features/<feature>-error-handling.md` (flat) | Falls back to a section in `CLAUDE.md` if `docs/features/` doesn't exist. |
| `observability.md` | CREATE | `docs/features/<feature>-observability.md` (flat) | Same fallback. |
| `review.md` | SKIP | n/a | Working artifact; resolved items captured in PR description by Agent 4. |
| `runbook.md` | CREATE | `docs/runbooks/<feature>.md` (new) | Falls back to a section in `docs/guides/troubleshooting.md` if `docs/runbooks/` doesn't exist. |

If `docs/runbooks/` and `docs/features/` are both absent, prompt: "This project doesn't have a runbook directory yet. Options: (a) create `docs/runbooks/<feature>.md`, (b) append to `docs/guides/troubleshooting.md`, (c) skip." Record the choice in `docs-commit-plan.md` for re-runs.

#### Step 3 — Write the plan

Write `.feature-factory/_pr-prep/<pr-folder>/docs-commit-plan.md`:

```markdown
# Documentation Commit Plan — <pr-folder>

**Generated:** <ISO date>
**Slug:** <feature-slug>
**Convention:** docs/features/ uses flat | subdirectory naming
**Status legend:** PROPOSED → APPROVED / REJECTED → APPLIED

| # | Source | Disposition | Target | Status | Diff scope |
|---|--------|-------------|--------|--------|------------|
| 1 | runbook.md | CREATE | docs/runbooks/<feature>.md | PROPOSED | new file |
| 2 | errors.md | CREATE | docs/features/<feature>-error-handling.md | PROPOSED | new file |
| 3 | observability.md | CREATE | docs/features/<feature>-observability.md | PROPOSED | new file |
| 4 | arch.md | EDIT existing | docs/architecture/ARCHITECTURE.md (`## Catalog Sync Flow`) | PROPOSED | single-section |
| 5 | func.md | SKIP | n/a | n/a | — |
| 6 | review.md | SKIP | n/a | n/a | — |
```

#### Step 4 — Present for approval

Print the table to the user and ask for per-row approval. Accepted commands:
- `approve all` — all PROPOSED rows → APPROVED
- `approve [1,3]` — specific rows by number
- `reject all` — all rows → REJECTED
- Per-row interactive: `Row 1 (runbook.md → docs/runbooks/<feature>.md): apply? [y/N]`

Update the Status column in `docs-commit-plan.md` after each decision.

#### Step 5 — Apply approved rows

For each APPROVED row:

**CREATE:** Copy/transform the feature-factory file into the target path with front-matter prepended:

```markdown
---
source: .feature-factory/<slug>/<artifact>.md
generated_by: pr-prep Phase 4.5
last_synced: <ISO date>
---

[verbatim content of the source artifact]
```

**EDIT existing:** Generate a focused diff (specific section update only). Display the diff to the user. Apply only on per-edit `y` confirmation. Never reformat unrelated content.

**SKIP:** No-op.

After successful application, mark the row APPLIED in `docs-commit-plan.md`.

#### Step 6 — Stale-overwrite protection

Before applying any CREATE/EDIT, check whether the target file already exists with `last_synced` front-matter. If the existing file's `last_synced` is **newer than** the source artifact's mtime, **abort that row** and add to "Items needing human resolution":

> ⚠️ `<target>` is newer than `.feature-factory/<slug>/<artifact>.md` — the committed file may have hand-edits. Resolve manually before re-running Phase 4.5.

Per Spec 3 #3: never overwrite hand-edits.

#### Step 7 — CLAUDE.md edit guardrails

If a proposed EDIT touches CLAUDE.md:

- **Single-section diffs only.** Per Spec 3 #2: if the diff touches more than one section, downgrade to "human review" — write the proposed change to `.feature-factory/_pr-prep/<pr-folder>/proposed-claude-md-edits.md` and STOP that row. Do not apply.
- **Per-edit approval required.** Always show the diff and request explicit `y` even for single-section edits.
- **Never bulk-rewrite CLAUDE.md.** It is the highest-leverage doc and the most fragile (Claude's own context anchor).

#### Step 8 — Re-run Agent 4 to update Related Docs

After all approved rows are applied, re-invoke Agent 4 (PR Description) so the "Related Docs" and "Runbook entry" sections in `pr-description.md` reference the newly committed in-repo paths instead of the working-artifact paths. The re-run only re-renders those sections; primary content from the first pass is preserved.

#### Step 9 — Stage, do not commit

Run `git add` on each APPLIED file. Do NOT run `git commit`. Per Spec 3 risk mitigations: pr-prep never writes commits — that's a developer responsibility.

Print a summary:

```
📚 PHASE 4.5 — DOCUMENTATION COMMIT PLAN COMPLETE

Plan written to: .feature-factory/_pr-prep/<pr-folder>/docs-commit-plan.md

✅ Applied (staged via git add):
  docs/runbooks/<feature>.md (new)
  docs/features/<feature>-error-handling.md (new)
  docs/features/<feature>-observability.md (new)

✏️  Edited:
  docs/architecture/ARCHITECTURE.md (one section)

⏭️  Skipped:
  func.md, review.md (per default disposition)

⚠️  Items needing human resolution:
  [Any stale-overwrite or multi-section CLAUDE.md proposals]

PR description has been re-rendered to reference new in-repo paths.
Review staged files with `git diff --cached`. Commit when ready.
```

---

### Phase 5a — Excalidraw Architecture & Flow Diagrams

Run after Phase 4 synthesis (and Phase 4.5 if feature-factory artifacts present). Creates visual diagrams for the PR using the Excalidraw MCP server. These diagrams serve as both PR documentation and Remotion video slide assets.

**Prerequisites:**
- Excalidraw MCP server configured in `.mcp.json` (local Express server, e.g. `http://localhost:3002`)
- User must have `http://localhost:3002` open in a browser tab for export to work
- If another agent is using the canvas, snapshot their scene first and restore after

**Step 1 — Plan Diagrams**

Based on the PRD and code audit, identify which diagrams would help reviewers understand the PR:

```
📐 EXCALIDRAW DIAGRAM PLAN

Based on this PR's changes, I recommend these diagrams:

  1. Architecture Overview — [system boundary diagram showing data flow]
  2. [Feature] Flow — [specific user/data flow for key feature]
  3. [Feature] State Machine — [if stateful transitions exist]
  4. Test Coverage Diagrams — one per automatable test scenario (S2, S3, etc.)

Proceed? (add/remove/adjust)
```

**Step 2 — Create Diagrams via MCP**

For each diagram, follow this process:

1. **Snapshot** any existing canvas content: `mcp__excalidraw__snapshot_scene({ name: "pre-pr{N}" })`
2. **Clear** the canvas: `mcp__excalidraw__clear_canvas()`
3. **Build** the diagram using `mcp__excalidraw__batch_create_elements()`
4. **Screenshot** to verify: `mcp__excalidraw__get_canvas_screenshot()`
5. **Iterate** — fix layout issues using `mcp__excalidraw__update_element()`
6. **Export** to PNG: `mcp__excalidraw__export_to_image({ format: "png", filePath: "..." })`
7. **Snapshot** the completed diagram: `mcp__excalidraw__snapshot_scene({ name: "pr{N}-{diagram-name}" })`
8. **Restore** the previous scene if another agent was using the canvas

**Excalidraw styling rules (clean technical style):**
- `roughness: 0` on all elements (not hand-drawn)
- `fontFamily: 3` (Cascadia mono) for all text
- Use the guide's color palette: blue (#1971c2/#a5d8ff) for process steps, green (#2f9e44/#b2f2bb) for success/validated, orange (#e8590c/#ffd8a8) for in-progress, red (#e03131/#ffc9c9) for errors, purple (#9c36b5/#eebefa) for special states, gray (#868e96/#e9ecef) for annotations
- Minimum shape size: 120x60px, minimum font: 14px, minimum spacing: 40px
- Always bind arrows with `startElementId`/`endElementId` — never use manual coordinates
- Use `strokeStyle: "dashed"` for async/optional flows
- Label every arrow with its relationship (HTTP, SDK, upsert, etc.)
- Add a legend text element at the bottom explaining colors and line styles
- No two elements should overlap — verify with screenshot after creation

**Output files:**
```
.feature-factory/_pr-prep/<pr-folder>/evidence/screenshots/excalidraw-{diagram-name}.png  — local archive
~/workspace/agency-operations/video-studio/public/pr{N}/{diagram-name}.png                — Remotion asset copy (cross-repo)
```

**Test coverage diagrams** — create one per automatable test scenario:
- Show the user flow being tested (start → actions → assertions → end)
- Color-code: green for happy path, red for error paths, orange for async
- Include the test spec filename and test count in a corner label
- These will be displayed as `TestCoverageSlide` components in the Remotion video

---

### Phase 5b — Playwright E2E Regression Tests & Screenshots

Run after Phase 4 synthesis (can overlap with Phase 5a). Creates targeted Playwright E2E test specs for automatable scenarios AND captures screenshots for PR evidence.

**Step 1 — Classify Test Scenarios**

Review the manual testing guide and classify each session:

| Category | Criteria | Action |
|----------|----------|--------|
| **Automatable** | Pure frontend flow, no external API dependency | Write Playwright spec |
| **Manual only** | Requires real OAuth redirect, external webhooks, or multi-day timing | Keep in manual guide |
| **Partial** | Backend logic testable via pytest, not browser | Write pytest, not Playwright |

Present the classification for user confirmation.

**Step 2 — Write E2E Test Specs**

For each automatable scenario, create `e2e/tests/s{N}-{name}.spec.ts`:

**Required patterns (follow existing specs as reference):**

- Import `{ test, expect } from '../fixtures/auth'` for authenticated tests
- Import `{ API_BASE_URL } from '../constants'`
- Use `authedPage` fixture (provides pre-authenticated page context)
- Seed data in `beforeEach` via API: `authedPage.request.post(\`\${API_BASE_URL}/api/v1/demo/seed-e2e-orders\`)`
- Use semantic selectors: `getByRole()`, `getByLabel()`, `getByText()` — not CSS selectors
- Use `test.skip(condition, reason)` for graceful handling when preconditions aren't met
- Keep assertions focused on observable UI state (visibility, text content, badge colors)
- Use `authedPage.on('dialog', d => d.accept())` for confirmation dialogs
- For file downloads, use `authedPage.waitForEvent('download')` and validate content
- For cross-page effects, navigate between pages within the same test

**Step 3 — Capture Screenshots via Playwright MCP**

Use the Playwright MCP server to capture targeted screenshots for PR evidence:

1. **Navigate** to the page: `mcp__playwright__browser_navigate({ url: "..." })`
2. **Interact** as needed: `mcp__playwright__browser_click()`, `mcp__playwright__browser_fill_form()`
3. **Screenshot**: `mcp__playwright__browser_take_screenshot({ fullPage: true })`
4. Save screenshots to `.feature-factory/_pr-prep/<pr-folder>/evidence/screenshots/{scenario}/`

**When to use Playwright MCP vs test recordings:**
- **Playwright MCP screenshots**: Static evidence of specific UI states (login page, error banners, empty states). Quick, targeted, no test infrastructure needed.
- **Test recordings (walkthrough.spec.ts)**: Dynamic flows showing user interaction over time. Used for Remotion video input.

**Output files:**
```
e2e/tests/s{N}-{name}.spec.ts                     — regression test specs
.feature-factory/_pr-prep/<pr-folder>/evidence/screenshots/{scenario}/*.png — targeted screenshots
```

---

### Phase 5 — Evidence & Distribution

Run after manual testing is complete and screenshots/evidence have been captured locally. This phase uploads everything to Google Drive, updates the requirements map, and cross-links all surfaces.

**Prerequisites:**
- User provides Google Drive folder URL (or ID) for test evidence
- Screenshots organized locally in per-test subfolders (e.g., `screenshots/pr5/A1/`, `screenshots/pr5/B3/`)
- Google Drive API credentials available at `~/workspace/api-integrations/google-drive/`

**Step 1 — Upload Test Evidence to Google Drive**

Use the Google Drive API via `~/workspace/api-integrations/google-drive/` project (OAuth2 credentials + `google-api-python-client`):

1. Create a subfolder in Drive for each test (A1, A2-A3, B1, etc.)
2. Upload all screenshots/evidence files to their corresponding subfolders
3. Create a README.txt in each subfolder explaining:
   - Test ID and name
   - Result (PASS/FAIL/SKIP)
   - Method (live pipeline, Playwright mock, DB-seeded, etc.)
   - What the screenshot shows and what to look for
   - PRD functional requirements covered
4. Upload all README.txt files to their Drive subfolders

**Step 2 — Create INDEX Google Doc**

Create `.feature-factory/_pr-prep/<pr-folder>/evidence/INDEX.md` locally with:
- PR title, branch, test date, result summary
- Links to: PRD, requirements map (Google Sheet), requirements map (xlsx), GitHub PR
- Per-test table with folder name, test name, PRD requirements, and result
- Paragraph description of each test
- PRD coverage summary table mapping each FR to test(s) and status

Upload INDEX.md to Drive as a native Google Doc (set `mimeType: application/vnd.google-apps.document`, upload with `mimetype: text/markdown`). This makes links clickable and formatting readable in Drive.

**Step 3 — Update Requirements Map**

If a requirements map spreadsheet exists in Drive:

1. If it's an uploaded .xlsx (not a native Google Sheet), copy it as a native Sheet first:
   ```python
   drive.files().copy(fileId=xlsx_id, body={
       'name': 'requirements_map',
       'mimeType': 'application/vnd.google-apps.spreadsheet'
   })
   ```
2. Update the native Google Sheet via Sheets API (`batchUpdate`):
   - **Requirements Map sheet**: Set Status and Notes columns for each FR based on PR coverage
   - **Research Spikes sheet**: Update resolved spikes, append newly resolved ones
   - **Task Traceability sheet**: Update backlog task statuses
3. Also update the .xlsx locally using openpyxl (`pip install openpyxl` in the api-integrations venv) and re-upload to Drive

**Step 4 — Create `google-drive-evidence.md` in pr-prep**

Write `.feature-factory/_pr-prep/<pr-folder>/evidence/google-drive-evidence.md` containing:
- Links to all Drive resources (screenshots folder, INDEX doc, planning docs folder)
- Links to each document (PRD versions, requirements map in both formats)
- Screenshot folder structure tree
- Summary of requirements map updates
- References to local copies

**Step 5 — Cross-Link All Surfaces**

Ensure all three surfaces reference each other:

1. **PR description** (`.feature-factory/_pr-prep/<pr-folder>/pr-description.md`):
   - Add "Test Evidence" section with links to Drive screenshots, requirements map, and PRD
   - Replace `GOOGLE_DRIVE_FOLDER_LINK` placeholder with actual folder URL
   - Apply to GitHub: `gh pr edit {N} --body "$(cat .feature-factory/_pr-prep/<pr-folder>/pr-description.md)"`

2. **INDEX Google Doc** (in Drive):
   - Links to PRD, requirements map (Sheet + xlsx), and GitHub PR

3. **Requirements map** (Google Sheet):
   - Each FR row has test IDs and notes referencing the PR

4. **test-results.md** (`.feature-factory/_pr-prep/<pr-folder>/test-results.md`):
   - Reference `google-drive-evidence.md` for Drive links
   - Update completion checklist

**Step 6 — Final Summary**

Present completion status:

```
✅ PR #N EVIDENCE & DISTRIBUTION COMPLETE

📁 Google Drive:
  Screenshots: {URL} ({N} folders, {N} files + {N} READMEs)
  INDEX Doc:   {URL}
  Requirements Map: {URL} (updated: {N} FRs done, {N} partial, {N} deferred)

🔗 Cross-references verified:
  PR description → Drive screenshots ✓
  PR description → Requirements map ✓
  INDEX doc → PRD, requirements map, GitHub PR ✓
  Requirements map → test IDs per FR ✓

📄 Local docs:
  .feature-factory/_pr-prep/<pr-folder>/evidence/google-drive-evidence.md ✓
  .feature-factory/_pr-prep/<pr-folder>/test-results.md (updated) ✓
  .feature-factory/_pr-prep/<pr-folder>/evidence/INDEX.md ✓

📋 Remaining:
  [Any items still pending — e.g., skipped tests, deferred spikes]
```

---

### Phase 6 — E2E Walkthrough Tests & Video Presentation

Run after Phase 4 synthesis (can overlap with Phase 5/5a/5b). Creates automated Playwright walkthrough tests that produce video recordings, then builds a Remotion composition with perception holds, voiceover segments, architecture diagrams, test coverage slides, and optional sandbox validation slides.

**Overview — Two-Stage Pipeline:**

1. **Playwright walkthrough tests** (`e2e/tests/walkthrough.spec.ts`) — scripted UI recordings with annotation overlays
2. **Remotion video studio** (`~/workspace/agency-operations/video-studio/`) — stitches recordings into a polished presentation with animated slides, perception holds (freeze-frames), and voiceover

**Architecture — Config-Driven Composition:**

The Remotion composition uses a **two-file pattern**:
- `pr{N}-video-config.ts` — **single source of truth** for all timing metadata (video files, durations, slide content, perception holds, voiceover offsets, diagram slides). Zero timing data in the component.
- `PR{N}TestEvidence.tsx` — **pure renderer** that imports config. Contains only React components and animation logic.

To adjust timing: edit the config file, not the component.

**Step 1 — Identify Walkthrough Scenarios**

Ask the user which feature areas from this PR should be recorded. Use the manual testing guide (`.feature-factory/_pr-prep/<pr-folder>/manual-testing-guide.md`) and PRD (`.feature-factory/_pr-prep/<pr-folder>/updated-prd.md`) as inputs.

Present a proposed video plan:

```
🎬 E2E WALKTHROUGH VIDEO PLAN

Based on this PR's changes, I recommend these walkthrough recordings:

  Video 1 — [Feature Area] (~Ns estimated)
    Steps: [brief flow description]
    Requirements covered: [FR-XXX, FR-YYY]
    Perception holds: [fast actions that need freeze-frames]

  Video 2 — [Feature Area] (~Ns estimated)
    Steps: [brief flow description]
    Requirements covered: [FR-XXX, FR-YYY]

  Architecture diagram slide: [diagram from Phase 5a]
  Test coverage slides: [N diagrams from Phase 5a]
  Sandbox validation slides: [if backend sandbox evidence exists]

  Total estimated: ~Ns of video + slides + holds + intro/outro = ~Ns final

Proceed with these, or adjust? (add/remove/reorder videos)
```

Wait for user confirmation before writing tests.

**Step 2 — Write/Update Walkthrough Spec**

Create or update `e2e/tests/walkthrough.spec.ts` following the established patterns:

**Required patterns (read the existing walkthrough.spec.ts as reference):**

- Import `annotate()` helper — injects a floating bar at the bottom of the viewport explaining each step. Use it before every meaningful UI action.
- Import `URL_OVERLAY_SCRIPT` — adds a fixed URL bar at the top showing the current route. Inject via `page.addInitScript()`.
- Use `STEP_PAUSE` constant (1200ms) between logical steps so viewers can follow.
- Use `VIDEO_DIR` for video output path.
- Each test = one continuous video recording covering an entire feature area.
- Tests are NOT regression tests — they are recording-optimized walkthroughs. Keep assertions light (visibility checks, not deep state validation). The individual spec files (`login.spec.ts`, `sku-mapping.spec.ts`, etc.) remain the source of truth for pass/fail.
- For tests that need unauthenticated state (e.g., login flow), use `browser.newContext()` directly with `recordVideo` option instead of `authedPage`.
- For authenticated tests, use the `authedPage` fixture.
- Seed test data via API calls at the start of each test (e.g., `POST /api/v1/demo/seed-e2e-data`). If a new seed endpoint is needed, create it in `backend/api/v1/endpoints/demo.py`.
- Use `slugify()` for filesystem-safe video filenames.
- Save videos in the `finally` block to ensure capture even on test failure.

**Annotation guidelines:**
- Lead with an emoji indicating the action type (🔐 auth, 📋 table, 🔍 search, ➕ create, 💾 save, ✅ success, ⚠️ warning, 🗑️ delete, etc.)
- Keep annotations under ~80 chars — they're displayed in a narrow bar
- Include the technical detail that makes it useful as PR evidence (e.g., "POST /api/v1/products/mappings" not just "Saving")
- For type-ahead demos, type characters slowly with 300ms delays between keystrokes
- Add longer pauses (2000ms) for important visual states the reviewer should study

**Step 3 — Run Walkthrough Tests & Capture Videos**

Guide the user through recording:

```bash
# Ensure full stack is running
docker compose up -d

# Run only the walkthrough tests (not regression specs)
cd e2e && npx playwright test tests/walkthrough.spec.ts --headed
```

Videos are saved to `e2e/test-results/videos/`. Verify each video was captured:

```bash
ls -la e2e/test-results/videos/*.webm
# Use ffprobe to get exact durations for Remotion
for f in e2e/test-results/videos/*.webm; do
  echo "$f: $(ffprobe -v error -show_entries format=duration -of csv=p=0 "$f")s"
done
```

If any test fails or a video looks wrong, iterate with the user — adjust the walkthrough spec and re-run.

**Step 4 — Create Remotion Video Config**

Create `~/workspace/agency-operations/video-studio/src/pr{N}-video-config.ts`:

```typescript
/**
 * PR #{N} Video Configuration — Single source of truth for all timing metadata.
 * The Remotion component is a pure renderer that imports this config.
 * To adjust timing: edit THIS file, not the component.
 */

// ── Types ──

export type PerceptionHold = {
  atSec: number;      // Source video timestamp to freeze on
  holdSec: number;    // How long to display frozen frame (output time)
  label: string;      // Overlay label (shown during freeze)
};

export type VOSegment = {
  file: string;
  offsetSec: number;  // Offset in SOURCE video time (remapped to output time)
};

export type VideoEntry = {
  file: string;
  srcDurationSec: number;  // From ffprobe
  num: number;
  title: string;
  subtitle: string;
  requirements: { id: string; name: string; tests: number }[];
  highlights: string[];
  perceptionHolds: PerceptionHold[];
};

// ── Video Entries ──
export const VIDEOS: VideoEntry[] = [
  // Fill from ffprobe durations and walkthrough plan
];

// ── Voiceover Configuration (optional) ──
export const VO_CONFIG = {
  intro: "pr{N}/voiceover/0-intro.mp3",
  outro: "pr{N}/voiceover/5-outro.mp3",
  titles: [/* one per video */],
  walkthroughs: [/* VOSegment[][] — one array per video */] as VOSegment[][],
} as const;

// ── Architecture Diagram Slide ──
export const DIAGRAM_SLIDE = {
  file: "pr{N}/architecture-diagram.png",  // From Phase 5a
  title: "System Architecture",
  durationSec: 7,
  vo: null as VOSegment | null,
} as const;

// ── Test Coverage Slides (from Phase 5a Excalidraw diagrams) ──
export type TestCoverageSlide = {
  file: string;
  title: string;
  subtitle: string;
};

export const TEST_COVERAGE_SLIDES: TestCoverageSlide[] = [
  // One per automatable test scenario from Phase 5b
];
export const TEST_COVERAGE_SLIDE_SECONDS = 4;

// ── Sandbox Validation Slides (if applicable) ──
export type SandboxSlide = {
  file: string;
  title: string;
  subtitle: string;
};

export const SANDBOX_SLIDES: SandboxSlide[] = [
  // Include if backend sandbox evidence exists (e.g., SP-API validated)
];
export const SANDBOX_SLIDE_SECONDS = 6;

// ── Timing Constants ──
export const FPS = 30;
export const SLIDE_SECONDS = 5;
export const SLIDE_SECONDS_VO = 9;  // Longer when voiceover needs time
export const OUTRO_SECONDS = 3;

// ── Derived Helpers ──

export function outputDuration(video: VideoEntry): number {
  const totalHoldTime = video.perceptionHolds.reduce((sum, h) => sum + h.holdSec, 0);
  return video.srcDurationSec + totalHoldTime;
}

export function srcToOutputTime(srcTimeSec: number, holds: PerceptionHold[]): number {
  let extra = 0;
  for (const h of holds) {
    if (h.atSec < srcTimeSec) extra += h.holdSec;
  }
  return srcTimeSec + extra;
}

export function totalDurationFrames(slideSeconds: number): number {
  const slideTime = slideSeconds * (1 + VIDEOS.length);
  const videoTime = VIDEOS.reduce((acc, v) => acc + outputDuration(v), 0);
  const diagramTime = DIAGRAM_SLIDE.durationSec;
  const testCoverageTime = TEST_COVERAGE_SLIDE_SECONDS * TEST_COVERAGE_SLIDES.length;
  const sandboxTime = SANDBOX_SLIDE_SECONDS * SANDBOX_SLIDES.length;
  return Math.ceil((slideTime + diagramTime + videoTime + testCoverageTime + sandboxTime + OUTRO_SECONDS) * FPS);
}
```

**Perception Holds — when and how to use:**

Perception holds freeze-frame fast UI actions so viewers can read them. Identify hold candidates by:

1. Extract frames at 2fps: `ffmpeg -i video.webm -vf fps=2 frames/frame_%04d.png`
2. Review frames for fast transitions: success banners, status changes, modal opens
3. Rule: **no two holds within 2s of each other** — merge to avoid freeze→flash→freeze jarring
4. Typical hold durations: 1.0s for simple states, 1.5s for banners, 2.0s for complex dialogs

**Step 5 — Create Remotion Composition**

Copy assets and create/update the composition:

```bash
mkdir -p ~/workspace/agency-operations/video-studio/public/pr{N}/
cp e2e/test-results/videos/*.webm ~/workspace/agency-operations/video-studio/public/pr{N}/
# Also archive the recordings under the PR folder
mkdir -p .feature-factory/_pr-prep/<pr-folder>/evidence/recordings/
cp e2e/test-results/videos/*.webm .feature-factory/_pr-prep/<pr-folder>/evidence/recordings/
# Copy diagram PNGs from Phase 5a
cp .feature-factory/_pr-prep/<pr-folder>/evidence/screenshots/excalidraw-*.png ~/workspace/agency-operations/video-studio/public/pr{N}/
```

Create `~/workspace/agency-operations/video-studio/src/PR{N}TestEvidence.tsx`:

Follow the established pattern from `PRTestEvidence.tsx` (PR6). The component should include:

- **HeldVideo** — renders video with perception hold freeze-frames using Remotion's `<Freeze>` component
- **IntroSlide** — PR title, branch name, stats badges (walkthroughs, FRs, tests, etc.)
- **DiagramSlide** — full-screen architecture diagram from Phase 5a
- **VideoTitleSlide** — per-video title with requirements badges and highlights
- **TestCoverageSlide** — split layout: diagram image left, title/subtitle/progress dots right
- **SandboxValidationSlide** — "Live Sandbox Validated" badge, operation matrix diagram, green glow theme
- **OutroSlide** — summary stats, PR reference

**Timeline segment order:**
```
Intro → Architecture Diagram → [Title Slide → Video] × N
  → Test Coverage × M → Sandbox Validation × K → Outro
```

Brand colors (dark tech theme):
```typescript
const C = {
  bg: "#0f172a", surface: "#1e293b", surface2: "#334155",
  text: "#e2e8f0", muted: "#94a3b8", accent: "#38bdf8",
  green: "#4ade80", yellow: "#fbbf24", border: "#475569",
};
```

Register in `Root.tsx` as `<Composition id="PR{N}-TestEvidence">`.

**Step 6 — Preview in Remotion Studio**

```bash
cd ~/workspace/agency-operations/video-studio && npm run dev
```

```
🎬 REMOTION PREVIEW CHECKLIST

Open http://localhost:3000 and select "PR{N}-TestEvidence"

  [ ] Intro slide stats are accurate (test counts, FR counts)
  [ ] Architecture diagram slide renders clearly
  [ ] Each title slide shows correct video number, title, requirements
  [ ] Videos play smoothly — perception holds freeze at correct moments
  [ ] Hold labels appear as subtle yellow overlay text during freeze
  [ ] No two holds cause freeze→flash→freeze jarring
  [ ] Test coverage slides show diagrams from Phase 5a
  [ ] Sandbox validation slide (if present) shows green "validated" badge
  [ ] Outro slide stats match intro
  [ ] Total duration is reasonable (~2-4 min for typical PR)

All good? I'll finalize the config and update the PR description.
```

**Step 7 — Record Voiceover (Optional)**

If voiceover is desired:

1. Create a script based on the video config's highlights and requirements
2. Record clips per section: `pr{N}/voiceover/0-intro.mp3`, `{N}-title.mp3`, `{N}-walkthrough-{a,b,c}.mp3`, `5-outro.mp3`
3. Measure clip durations and add offsets to `VO_CONFIG.walkthroughs` in the config file
4. Set `SLIDE_SECONDS_VO = 9` for longer title slides when VO needs time
5. Preview with `voiceover: true` prop in Remotion studio

**Step 8 — Render Final Video (Optional)**

```bash
cd ~/workspace/agency-operations/video-studio
npx remotion render PR{N}-TestEvidence out/pr{N}-test-evidence.mp4
# With voiceover:
npx remotion render PR{N}-TestEvidence out/pr{N}-test-evidence-vo.mp4 --props='{"voiceover":true}'
```

**Step 9 — Update PR Description**

Add a video evidence section to `.feature-factory/_pr-prep/<pr-folder>/pr-description.md`:

```markdown
## E2E Test Evidence

### Walkthrough Videos
Automated Playwright walkthrough tests with Remotion presentation.

| # | Video | Duration | Perception Holds | Requirements |
|---|-------|----------|-----------------|-------------|
| 1 | {title} | {src}s (+{holds}s holds) | {N} freeze-frames | {FR-XXX, FR-YYY} |

### Automated Test Coverage
| Suite | Tests | Spec File |
|-------|-------|-----------|
| {scenario} | {N} | `e2e/tests/s{N}-{name}.spec.ts` |

### Architecture & Flow Diagrams
| Diagram | Description |
|---------|-------------|
| [Architecture](.feature-factory/_pr-prep/<pr-folder>/evidence/screenshots/excalidraw-{name}.png) | System data flow |
| [Test Coverage](.feature-factory/_pr-prep/<pr-folder>/evidence/screenshots/excalidraw-s{N}-{name}.png) | E2E test flow |

### Sandbox Validation (if applicable)
| Operations Validated | Lifecycle Proven | Evidence |
|---------------------|-----------------|----------|
| {N} SP-API operations | {state machine} | `.feature-factory/_pr-prep/<pr-folder>/last-mile.md` |

📹 **[View test evidence video →](LINK)**
_(Remotion composition: `PR{N}-TestEvidence` in video-studio)_
```

**Final Summary:**

```
🎬 E2E WALKTHROUGH & VIDEO COMPLETE

📐 Excalidraw diagrams:
  {N} diagrams exported (architecture, test flows, sandbox lifecycle)
  .feature-factory/_pr-prep/<pr-folder>/evidence/screenshots/excalidraw-*.png
  ~/workspace/agency-operations/video-studio/public/pr{N}/*.png  (cross-repo)

🧪 E2E regression tests:
  {N} spec files, {N} total tests
  e2e/tests/s{N}-*.spec.ts

📂 Walkthrough spec:
  e2e/tests/walkthrough.spec.ts — {N} walkthrough tests

📂 Remotion composition:
  video-studio/src/pr{N}-video-config.ts — timing config
  video-studio/src/PR{N}TestEvidence.tsx — composition
  ~/workspace/agency-operations/video-studio/public/pr{N}/ — {N} video + {N} diagram assets (cross-repo)

🎬 Video timeline:
  Intro → Architecture Diagram ({N}s)
    → [Title → Video] × {N} ({N}s total + {N}s holds)
      → Test Coverage × {N} ({N}s)
        → Sandbox Validation × {N} ({N}s)
          → Outro
  Final: ~{total}s

📋 Next steps:
  1. Preview in Remotion studio (npm run dev)
  2. Record voiceover if desired (see Step 7)
  3. Render final MP4 (npx remotion render)
  4. Upload to Google Drive (Phase 5)
  5. Paste PR description (Phase 4 output)
```

---

## Configuration Notes

- **Output folder:** Always `.feature-factory/_pr-prep/<pr-folder>/` (per Spec 4) — overwrite existing files (they represent the latest analysis). The legacy `_bmad-output/pr-prep/` and `docs/pr-prep/pr<N>/` paths are retired.
- **`<pr-folder>` naming:** `pr-<N>-<short-feature-slug>/` — see "Output Locations" near the top of this file.
- **`manifest.yaml`:** Created by Phase 2c if absent. Lists PR number, branch, base, feature slugs, and any cross-repo asset paths in `notes`.
- **`pr-history.md`:** Phase 4 appends one row per feature listed in `manifest.yaml.features` to `.feature-factory/<feature-slug>/pr-history.md`.
- **Feature Factory ingestion (Phase 2c):** Auto-detects `.feature-factory/<slug>/` folders, prompts when 2+ exist, writes `feature-factory-context.md` digest. Skipped via `--no-feature-factory`. See Spec 1 — `docs/specs/pr-prep-feature-factory-1-ingestion.md`.
- **Docs commit plan (Phase 4.5):** Only runs when `feature-factory-context.md` is present. Proposes per-artifact dispositions; user approves per-row; pr-prep stages via `git add` but never commits. See Spec 3 — `docs/specs/pr-prep-feature-factory-3-commit-plan.md`.
- **`docs/features/` convention:** Phase 4.5 detects flat (`<feature>-<topic>.md`) vs subdirectory (`<feature>/<topic>.md`) naming and follows what the project already uses. Default is flat.
- **CLAUDE.md edits:** Phase 4.5 allows single-section diffs only with per-edit approval; multi-section proposals are written to `proposed-claude-md-edits.md` for human review.
- **Stale-overwrite protection:** Phase 4.5 aborts a row if the existing committed file's `last_synced` front-matter is newer than the source artifact — never overwrites hand-edits.
- **Template PR:** Default to the most recent merged PR. User can override by saying "use PR #N as template"
- **Commit range:** Confirmed in Phase 2 scope check. Default is `origin/main..HEAD`, but user may specify a different base (e.g., a prior PR's merge point for stacked PRs). All agents use the confirmed base — never hardcode `origin/main`
- **Google Drive link:** In Phase 4, use `GOOGLE_DRIVE_FOLDER_LINK` as placeholder. In Phase 5, replace with actual URL provided by user
- **Google Drive API:** Uses `~/workspace/api-integrations/google-drive/` project with OAuth2 credentials. Activate venv before running: `cd ~/workspace/api-integrations/google-drive && source .venv/bin/activate`
- **Google Sheets:** If the target spreadsheet is an uploaded .xlsx, copy it as a native Google Sheet first — the Sheets API cannot write to uploaded Office files
- **Docs fixes:** Agent 3 fixes in-place, does not create copies — the actual CLAUDE.md etc. are updated
- **Cross-repo Remotion assets:** `~/workspace/agency-operations/video-studio/public/pr<N>/` and `PR<N>TestEvidence.tsx` live in the agency-operations workspace, not this repo. Document the path in `manifest.yaml.notes`.
- **PR creation:** This skill prepares but does NOT open the PR. The developer pastes pr-description.md manually or runs `/commit` + `gh pr create` separately

## Example Invocations

```
/pr-prep                         — full run (analysis + Phase 4.5 + assets prompt)
/pr-prep --skip-assets           — analysis only (Phases 1–4.5), skip diagrams/video
/pr-prep --assets-only           — skip analysis, jump to diagrams/E2E/video (Phases 5a+5b+6)
/pr-prep --no-feature-factory    — skip Phase 2c ingestion + Phase 4.5 commit plan even if .feature-factory/<slug>/ exists
/pr-prep — use PR #2 as template
/pr-prep — only analyze the last 5 commits
/pr-prep — update existing PR #7
```

**Typical workflow:**
1. Early in development: `/pr-prep --skip-assets` (iterate on PRD, audits, PR description)
2. Mid-cycle after changes: `/pr-prep --skip-assets` (re-run analysis with updated code)
3. Before final PR: `/pr-prep --assets-only` (generate all visual assets)
4. Final pass: `/pr-prep` (full run to verify everything is aligned)
