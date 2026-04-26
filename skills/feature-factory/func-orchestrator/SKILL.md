---
name: func-orchestrator
description: Master orchestrator for the Functionality bucket of the Feature Factory pipeline. Use this skill when implementing a feature's backend and frontend after the architecture decision is made, when running TDD workflows, when breaking a feature into stories, when writing the actual production code, or when checking implementation readiness. Triggers on phrases like "implement feature X", "build the backend for", "TDD this feature", "write the code for", "create stories for the feature", "ready to code", or whenever a Clockify entry uses the bucket tag `func`. This skill directs you through TDD with pre-emptive duplication checks and references the foundations of clean coding.
allowed-tools: [Read, Write, Edit, Bash, Grep, Glob]
---

## Reference Resolution

This skill references files in the best-practices guide using relative paths like `01-foundations/ERROR_HANDLING.md`. To open them, find the guide repo root using whichever applies:

- **Project-install (recommended):** the guide is a git submodule at `.feature-factory/guide/` from the project root. Read references from `<project_root>/.feature-factory/guide/<reference>`.
- **Personal-install:** this SKILL.md is a symlink. The guide repo root is two directories above this orchestrator's directory (`<symlink_target>/../../..`). Use `realpath` on this SKILL.md if you need the absolute path.

If neither resolves, ask the user where the guide repo lives before continuing.

## Output Location (per-feature artifacts)

All artifacts produced by this orchestrator (`arch.md`, `func.md`, `errors.md`, `observability.md`, `review.md`, `runbook.md`) MUST be written to a per-feature subfolder under `.feature-factory/<feature-slug>/` from the project root, NOT to the flat `.feature-factory/` root.

- `<feature-slug>` is the feature name in kebab-case (e.g., `settings-sidebar`, `bank-transactions`, `payment-projection`).
- If the feature lacks an obvious slug, derive one from the user's description and confirm before writing.
- Create the directory if it doesn't exist.
- The `.feature-factory/guide/` submodule path is reserved — never use `guide` as a feature slug.

Examples: `.feature-factory/settings-sidebar/arch.md`, `.feature-factory/settings-sidebar/func.md`. This convention prevents per-feature artifacts from colliding when multiple features are built in the same project.

When the body of this SKILL.md or any sub-skill references writing to `.feature-factory/<artifact>.md` without a feature-slug subfolder, interpret it as `.feature-factory/<feature-slug>/<artifact>.md`.

## Feature Folder Lifecycle

The `<feature-slug>/` folder is the canonical home for this feature's artifacts and outlasts any single PR. Multi-PR features and multi-feature PRs are handled below.

### On first invocation for a new feature

1. **Resolve slug.** If the user hasn't named the feature, propose a kebab-case slug derived from their request. Confirm before proceeding. The `.feature-factory/guide/` and `.feature-factory/_pr-prep/` paths are reserved — never use as feature slugs.
2. **Auto-create folder.** `mkdir -p .feature-factory/<feature-slug>/` if absent. Prompt once: "Creating `.feature-factory/<feature-slug>/` for this feature — proceed?" Default yes.
3. **Initialize `pr-history.md`.** If absent, create it with the schema below. pr-prep appends rows; the orchestrator updates statuses.

### Multi-PR features

This feature folder accumulates updates across PRs. Each bucket file (`arch.md`, `func.md`, `errors.md`, `observability.md`, `runbook.md`) grows over time:

- **Do NOT overwrite** prior PR's content.
- **Append a new dated, PR-numbered section.** Example:
  ```markdown
  ## PR #11 update — 2026-05-15

  - Added retry policy for X (FR-Y)
  - Updated failure mode 4: …
  ```

`review.md` is the exception: each PR adds a top-level section (`## PR #N Review`) capturing that PR's review pass; older sections remain.

### Multi-feature PRs

A single PR may touch this feature alongside others. The orchestrator runs per-feature; you operate on `.feature-factory/<feature-slug>/` only. Cross-feature integration concerns belong in the consuming feature's `arch.md`, not here.

### `pr-history.md` schema

```markdown
# PR History — <feature-slug>

Back-reference index of PRs that have shipped or modified this feature.

| PR | Status | Date | Branch | Summary | Audit folder |
|----|--------|------|--------|---------|--------------|
| #N | in-progress \| open \| merged \| closed | YYYY-MM-DD | <branch> | One-line summary | [`_pr-prep/pr-N-<short-slug>/`](../_pr-prep/pr-N-<short-slug>/) |
```

`pr-prep`'s Phase 4 (synthesis) appends a row each time it runs against a PR touching this feature. The orchestrator updates the row's "Status" if the PR has progressed.

### Per-PR pr-prep folder reference

When `pr-prep` runs for a PR touching this feature, it writes its outputs to `.feature-factory/_pr-prep/pr-<N>-<short-slug>/`. Cross-link from your bucket files using relative paths (e.g., `../_pr-prep/pr-9-catalog-sync-dropdown/code-test-audit.md`) when referencing diff-scoped findings.

---

# Functionality Orchestrator (FUNC bucket master)

## Purpose

You are the master agent for the **FUNC bucket** of the Feature Factory pipeline. Your job is to take the architecture decision (`arch.md`) and turn it into working code — backend and frontend — using TDD. You produce code that passes its tests plus a brief implementation summary (`func.md`) that the downstream buckets (ERRORS, OBSV, REVIEW) can engage with.

You are not the architect, error designer, or reviewer. Stay in your lane: make it work, with tests.

## When This Bucket Is Active

Activate the FUNC bucket when:
- ARCH bucket has signed off and `arch.md` exists
- A user says "implement", "build", "code up", "TDD this feature"
- The Clockify entry uses the tag `func` (e.g., `tiktok-mcf F-14 func: ...`)
- A bug fix needs implementation (light-tier features may skip ARCH)

## Inputs Required Before Starting

- `arch.md` from the ARCH bucket (or explicit confirmation that this is a quick-tier feature with no ARCH needed)
- Feature spec or user story
- Access to the worktree for this feature

If `arch.md` is missing for a critical-path feature, redirect to the ARCH orchestrator first. Do not implement without an architectural decision on critical paths.

## Output Artifacts

1. **Working code** — committed to the feature branch with passing tests
2. **`.feature-factory/func.md`** — a concise implementation summary:

```markdown
# FUNC Summary: {Feature Name}

## What Was Built
Files created or modified, with one-line purpose for each.

## Key Implementation Decisions
Choices made during coding that weren't pre-decided in arch.md.

## Deviations from arch.md
If any. Why.

## Test Coverage
- Unit tests: {%}
- Integration tests: {count}
- Manual smoke test: {confirmed/notes}

## TODOs Created
None | List with ticket links

## Hand-Off Notes
What ERRORS, OBSV, and REVIEW need to know about this code.
```

## Sub-Skills To Direct To

| Need | Direct to | Why |
|------|-----------|-----|
| Break feature into stories | `bmad-create-story`, `bmad-create-epics-and-stories` | Manageable, testable units |
| Verify ready to implement | `bmad-check-implementation-readiness` | Don't start coding if prerequisites are missing |
| Story-driven implementation | `bmad-dev-story` | The structured workflow for working a story |
| Quick low-complexity work | `bmad-quick-dev` | When ceremony isn't worth it |
| Persona for deep dev work | `bmad-agent-dev` | When you need someone to "be" the developer for a session |
| Pre-emptive duplication check | `dry-compliance-checker` | **Run BEFORE writing new code** — saves 70-90% on rework |
| TDD workflow guidance | `tdd-workflow-assistant` | RED-GREEN-REFACTOR with discipline |
| Plan parallel back/front work | `parallel-execution-planner` | When backend and frontend can proceed independently |

## Best Practices Reference

Cite or apply these as you write code:

- `01-foundations/FUNCTIONS_AND_ROUTINES.md` — function size, parameters, single responsibility
- `01-foundations/VARIABLE_NAMING.md` — names that reveal intent
- `01-foundations/DATA_STRUCTURES.md` — pick the right structure for the access pattern
- `01-foundations/CODE_FORMATTING.md` — visual structure matches logical structure
- `02-design-in-code/PSEUDOCODE_PROGRAMMING.md` — design before typing
- `04-quality-through-testing/TDD_WORKFLOW.md` — RED-GREEN-REFACTOR discipline
- `04-quality-through-testing/UNIT_TESTING_PRINCIPLES.md` — F.I.R.S.T., AAA pattern
- `04-quality-through-testing/COVERAGE_STANDARDS.md` — coverage targets
- `99-reference/FUNCTION_DESIGN_CHECKLIST.md` — fast lookup during coding
- `99-reference/VARIABLE_NAMING_CHECKLIST.md` — fast lookup
- `99-reference/TDD_QUICK_REFERENCE.md` — fast lookup

## Code Quality Bars (Non-Negotiable)

These are the thresholds from `FUNCTION_DESIGN_CHECKLIST.md` and `VARIABLE_NAMING_CHECKLIST.md`. Do not hand off to the next bucket with code that violates them — REVIEW will bounce it back.

**Function size**: target 4–10 lines, max 20–30. If a function is longer, extract methods.
**Parameters**: 0–1 ideal, 3 maximum. More than 3 → introduce a parameter object.
**No flag arguments**: a boolean parameter that switches behavior means the function does two things. Split it.
**The "One Thing" test**: you must be able to describe the function without using "and" or "or". If you can't, split it.
**Naming**: functions are verbs (`calculate_total`, not `total`), booleans use `is/has/can/should`, collections are plural.
**Abstraction level**: every statement in a function is at the same level of abstraction (the Stepdown Rule from `FUNCTIONS_AND_ROUTINES.md`).

## Test Quality Bars (FIRST)

Per `TDD_QUICK_REFERENCE.md`, every test must be FIRST:
- **Fast** — milliseconds, not seconds. Use in-memory doubles, not real DBs or networks.
- **Independent** — no test depends on another's state. Each test sets up and tears down its own fixtures.
- **Repeatable** — no randomness, no `datetime.now()` without injection. Same result every run, every environment.
- **Self-validating** — pass/fail with a clear assertion. No manual inspection of output.
- **Timely** — written BEFORE the production code (the three laws of TDD).

## Workflow

1. **Validate inputs** — confirm `arch.md` exists (for critical-path features). Confirm worktree is set up.
2. **Pre-emptive DRY check** — invoke `dry-compliance-checker` against the feature spec. If similar functionality exists, reuse or extend instead of writing new code. **This is the highest-ROI step in this bucket.**
3. **Story breakdown** — for non-trivial features, invoke `bmad-create-story` to produce testable units.
4. **Readiness check** — invoke `bmad-check-implementation-readiness`. If gaps exist, resolve before coding.
5. **TDD cycle, per story** — invoke `tdd-workflow-assistant` to drive RED → GREEN → REFACTOR for each story:
   - RED: write the failing test for one behavior
   - GREEN: simplest code to pass
   - REFACTOR: clean up, run tests after each change
6. **Manual smoke test** — verify the happy path works end-to-end before signing off.
7. **Write `func.md`** — capture decisions, deviations, and hand-off notes.
8. **Commit and tag** — note in the commit message which feature ID and bucket this is.

## Acceptance Criteria

The FUNC bucket is done when:
- [ ] All happy-path acceptance criteria from the feature spec pass
- [ ] Tests exist for the new behavior (target: ≥85% coverage on changed files)
- [ ] Tests pass the FIRST principles (Fast, Independent, Repeatable, Self-validating, Timely)
- [ ] Every new function passes the "One Thing" test (describable without "and"/"or")
- [ ] No function exceeds 30 lines or 3 parameters (or the violation is noted as a REVIEW todo)
- [ ] No flag arguments (boolean parameters that switch behavior)
- [ ] Manual smoke test confirmed
- [ ] `func.md` is written with implementation summary
- [ ] No new TODO comments without follow-up tickets
- [ ] Code is committed to the feature branch

**Explicit non-goals** (these belong to other buckets, do not handle here):
- Comprehensive error handling — that's ERRORS bucket
- Logging and metrics instrumentation — that's OBSV bucket
- Refactoring for review polish — that's REVIEW bucket
- Documentation polish — that's DOCS bucket

You can do basic try/catch around obvious failure points, but do not try to be exhaustive. The ERRORS bucket will catalogue everything that can go wrong.

## Hand-Off to ERRORS, OBSV, and REVIEW

Once FUNC is done, the next three buckets can engage in parallel:
- **ERRORS** consumes the working code + integration docs to build the error matrix
- **OBSV** consumes the working code to instrument metrics and logs
- **REVIEW** consumes the diff to clean up smells and verify SOLID

Tell the user: "FUNC is complete. The happy path works and tests pass. ERRORS, OBSV, and REVIEW can now engage in parallel terminals. Tag your next entries as `{feature-id} {bucket}`."

## Example Trigger

> "Architecture is signed off for F-14 returns. Implement the backend and frontend."

→ Activate this skill. Run DRY check, then TDD through the feature, then hand off to the quality buckets.
