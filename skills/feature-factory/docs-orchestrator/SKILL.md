---
name: docs-orchestrator
description: Master orchestrator for the Runbook & Documentation bucket of the Feature Factory pipeline. Use this skill when writing the runbook entry for a new feature, updating API or feature documentation, updating CLAUDE.md after architectural changes, drafting docs that answer "if you see error X, what do you do", or finalizing all documentation before merging. Triggers on phrases like "write the runbook", "document this feature", "update CLAUDE.md", "docs for the PR", "what should the runbook say about", or whenever a Clockify entry uses the bucket tag `docs`. This skill produces the final layer of the feature — documentation that lets a future teammate (or future you at 2am) resolve issues without asking anyone.
allowed-tools: [Read, Write, Edit, Grep, Glob]
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
3. **Don't create `pr-history.md`.** pr-prep is the sole writer of new rows — it has the PR number, branch, and date that the schema needs. If `pr-history.md` already exists, the orchestrator may **update** the `Status` column for prior rows (e.g., `in-progress` → `merged`) when the user moves a PR forward, but never inserts new rows. The schema below is reference-only so the orchestrator can validate format if asked.

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

# Documentation Orchestrator (DOCS bucket master)

## Purpose

You are the master agent for the **DOCS bucket** of the Feature Factory pipeline. Your job is to ensure that when a teammate (or future you) hits an issue with this feature at 2am, they can resolve it without asking anyone. You produce a `runbook.md` that maps every error to a resolution, plus updates to API docs, feature docs, and `CLAUDE.md` if the architecture meaningfully changed.

This is the bucket that pays itself back tenfold during operations. Skipping it is a gift to your future self in the form of midnight pages.

## When This Bucket Is Active

Activate the DOCS bucket when:
- ERRORS and OBSV have produced their artifacts (you need both)
- A user says "runbook", "document", "update docs", "CLAUDE.md update"
- Before opening the final PR
- The Clockify entry uses the tag `docs`

## Inputs Required Before Starting

- `arch.md` — for documentation of architectural decisions
- `errors.md` — every error needs a runbook entry
- `observability.md` — every metric needs a "what does it mean" note
- `func.md` — for the feature description and API surface
- `review.md` — for any open follow-up tickets that should be documented
- Existing `CLAUDE.md`, runbook, and project docs

If `errors.md` or `observability.md` are missing, send those buckets back to finish first. Without them, the runbook is hollow.

## Output Artifacts

1. **`.feature-factory/runbook.md`** — operational runbook for the feature:

```markdown
# Runbook: {Feature Name}

## Overview
What this feature does in one paragraph. Who uses it. Why it matters.

## API Surface
Endpoints, parameters, expected responses. Link to API docs for detail.

## Operational Notes
- Normal load: {expected request rate}
- Normal latency: {expected P99}
- Dependencies: {external services this feature relies on}
- Quotas/limits: {known caps}

## Error Resolution Guide

### Error: TikTok 429 Rate Limited
- **Log signature**: `tiktok_api_error{status_code="429"}`
- **Likely cause**: We're sending too many requests. Check if order volume spiked or if a retry storm is in progress.
- **Investigation steps**:
  1. Check `tiktok_api_calls_total` rate over the last hour
  2. Check `tiktok_circuit_breaker_state` — if open, the system is already self-protecting
  3. Look for correlation IDs in WARN-level logs around the spike
- **Resolution**:
  - If single spike: wait it out (circuit breaker handles)
  - If sustained: rate-limit at our edge, contact TikTok for quota increase
- **Escalation**: After 30min sustained, page on-call

### Error: TikTok 401 Auth Failed
- **Log signature**: `tiktok_api_error{status_code="401"}`
- **Likely cause**: OAuth token expired or revoked
- **Investigation steps**: ...
- **Resolution**: ...

[continue for every error in errors.md]

## Metrics Interpretation

### tiktok_returns_processed_total
- **What it spike means**: Increased return volume. Check if it correlates with a product launch, a quality issue, or a fraud pattern.
- **What dropping to zero means**: Returns flow is broken. Check `tiktok_api_error` rate and `tiktok_circuit_breaker_state`.
- **Normal range**: {N} per hour during business hours

[continue for every metric in observability.md]

## Known Issues / Open Tickets
- {ticket 1}
- {ticket 2}

## Related Documentation
- ADR: link to arch.md
- API docs: link
- Architecture diagram: link
```

2. **Updated API/feature documentation** — wherever the team's docs live (could be docs/, README.md, an external system)

3. **Updated `CLAUDE.md`** — if the architecture meaningfully changed (new module, new pattern, new convention)

## Sub-Skills To Direct To

| Need | Direct to | Why |
|------|-----------|-----|
| Persona for technical writing | `bmad-agent-tech-writer` | When you need someone to "be" the writer for a deep doc session |
| Document the project state | `bmad-document-project` | For broader docs updates beyond runbook |
| Split a doc that's grown too large | `bmad-shard-doc` | When the runbook is becoming unwieldy |
| Index existing docs | `bmad-index-docs` | When adding navigation or finding cross-refs |
| Editorial review of prose | `bmad-editorial-review-prose` | Polish the writing |
| Editorial review of structure | `bmad-editorial-review-structure` | Verify the docs are well-organized |
| Initialize/update CLAUDE.md | `init` | The Claude Code skill for CLAUDE.md management |

## Best Practices Reference

- `01-foundations/COMMENTS_AND_DOCUMENTATION.md` — **PRIMARY**. When to comment, what to document, anti-patterns. The "comment the why, not the what" principle applies to runbooks too.
- `09-production-readiness/MONITORING_AND_OBSERVABILITY.md` — runbook patterns for operational docs
- `08-project-management/MARKDOWN_PLAN_TEMPLATE.md` — markdown template conventions
- `08-project-management/MARKDOWN_PLAN_TEMPLATE_USAGE.md` — how to use the template
- `06-collaborative-construction/INTEGRATION_PLAYBOOK_GUIDE.md` — for documenting integrations specifically

## Workflow

1. **Validate inputs** — confirm `errors.md`, `observability.md`, `func.md`, and `arch.md` all exist.
2. **Read the inputs in full** — the runbook is a synthesis, not a fresh investigation.
3. **Draft the runbook structure** — start with the template above. Use `bmad-shard-doc` if the runbook is going to be large.
4. **Per-error entries** — for each row in `errors.md`, write a runbook entry: log signature, likely cause, investigation steps, resolution, escalation criteria.
5. **Per-metric entries** — for each metric in `observability.md`, write the "what does this mean if it spikes / drops" interpretation.
6. **API/feature docs** — update wherever the team's docs live. New endpoints, changed parameters, deprecations.
7. **CLAUDE.md update** — if the architecture changed (new module, new pattern, new convention introduced), update CLAUDE.md so Claude Code instances pick up the new context. Use the `init` skill.
8. **Editorial pass** — invoke `bmad-editorial-review-prose` to polish writing and `bmad-editorial-review-structure` to verify organization.
9. **Teammate test** — read the runbook as if you're a teammate at 2am with no context. Could you resolve a TikTok 429 error using only this doc? If not, fix it.

## Acceptance Criteria

The DOCS bucket is done when:
- [ ] Every error in `errors.md` has a runbook entry with cause, investigation steps, resolution, escalation
- [ ] Every metric in `observability.md` has a "what does this mean" note
- [ ] API/feature documentation reflects the new functionality
- [ ] `CLAUDE.md` is updated if architecture meaningfully changed
- [ ] The "could a teammate use this without asking me" test passes
- [ ] `runbook.md` is written and committed

## Hand-Off to PR Assembly

Once DOCS is done, all bucket artifacts exist (`arch.md`, `func.md`, `errors.md`, `observability.md`, `review.md`, `runbook.md`). The PR-prep step (`pr-prep` skill, possibly extended) can now assemble the PR body with sections from each bucket.

Tell the user: "DOCS is complete. All six bucket artifacts exist. Ready for PR assembly. Run `pr-prep` to build the PR body."

## Anti-Patterns to Watch For

- **Wall-of-text runbooks** — nobody reads them at 2am. Use scannable structure: headings per error, bullet points for steps.
- **Documentation that just restates code** — useless. The runbook should add operational context the code can't.
- **Stale docs** — if the feature changes after the runbook is written, the runbook must be updated. This is part of every future iteration.
- **CLAUDE.md drift** — if you don't update it when architecture changes, future Claude sessions will reason from outdated context.

## Example Trigger

> "REVIEW is done on F-14 returns. Write the runbook and update docs."

→ Activate this skill. Read `arch.md`, `errors.md`, `observability.md`, `func.md`. Produce `runbook.md` with per-error entries and per-metric interpretations. Update CLAUDE.md if architecture changed. Editorial pass. Hand off to PR assembly.
