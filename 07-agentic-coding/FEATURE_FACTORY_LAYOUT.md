# Feature Factory Layout: The `.feature-factory/` Directory Contract

## Document Control

- **Version**: 1.0.0
- **Created**: 2026-05-25
- **Status**: Active
- **Audience**: AI agents, developers, technical leads

## Table of Contents

1. [Overview](#overview)
2. [The Canonical Layout](#the-canonical-layout)
3. [The Per-Feature Folder](#the-per-feature-folder)
4. [The `_pr-prep/` Artifact Set](#the-_pr-prep-artifact-set)
5. [Reserved Paths and Conventions](#reserved-paths-and-conventions)
6. [Per-Run Artifacts (Autonomous Execution)](#per-run-artifacts-autonomous-execution)
7. [How the Pieces Connect](#how-the-pieces-connect)

## Overview

`.feature-factory/` is a project-root directory that holds the **durable, file-based memory of the feature-delivery pipeline**. Every feature flows through six buckets — Architecture, Functionality, Errors, Observability, Review, Docs — and each bucket produces one Markdown artifact. Those artifacts live in a per-feature folder. At PR time, a separate `_pr-prep/` tree captures PR-scoped deliverables (PRD updates, audits, the PR description, evidence).

This document is the **contract**: what folders exist, what each file is for, and which orchestrator owns each one. It pairs with the Feature Factory skill package (`skills/feature-factory/`), which defines the orchestrators that *write* these files, and with the `pr-prep` skill, which writes the `_pr-prep/` set.

**Why a file contract matters:**
- **Single source of truth** — one feature's architecture, error matrix, and runbook live in one predictable place, not scattered across wikis and PR comments.
- **Resumable context** — an agent (or a teammate at 2am) can rehydrate everything known about a feature by reading its folder.
- **Stable handoffs** — the DOCS bucket consumes the ERRORS and OBSV artifacts; `pr-prep` consumes all six. Fixed filenames make those handoffs deterministic.

---

## The Canonical Layout

Everything for the pipeline lives under `.feature-factory/` at the project root:

```
.feature-factory/
├── README.md                         ← index of features / phases (hand-maintained)
├── guide/                            ← (reserved) git submodule of the best-practices guide, when used
│
├── <feature-slug>/                   ← PER-FEATURE folder (one per feature; owned by FF orchestrators)
│   ├── arch.md                       ← arch-orchestrator  (Architecture bucket)
│   ├── func.md                       ← func-orchestrator  (Functionality bucket)
│   ├── errors.md                     ← errors-orchestrator (Error Handling bucket)
│   ├── observability.md              ← obsv-orchestrator   (Observability bucket)
│   ├── review.md                     ← review-orchestrator (Refactor & Review bucket)
│   └── runbook.md                    ← docs-orchestrator   (Runbook & Docs bucket)
│
├── _pr-prep/                         ← (reserved) PR-scoped pr-prep outputs
│   └── <pr-slug>/                    ← one folder per PR
│       ├── manifest.yaml             ← PR metadata: number, branch, base, commit, features, status
│       ├── updated-prd.md            ← refreshed product requirements for the PR
│       ├── code-test-audit.md        ← code + test coverage audit
│       ├── docs-audit.md             ← documentation audit (with in-place fixes noted)
│       ├── manual-testing-guide.md   ← step-by-step manual verification
│       ├── pr-description.md         ← human-readable PR write-up
│       ├── pr-body.md                ← ready-to-paste PR body (the description trimmed for the PR field)
│       └── evidence/
│           └── screenshots/          ← captured UI evidence (and recordings, when produced)
│
└── _refactor/                        ← (reserved) standalone refactor-pipeline reports
    └── <YYYY-MM-DD-HHMMSS>/
        ├── smell-report.json
        ├── plan.md
        └── validation-report.md
```

> **Note on filenames.** The six buckets map to **canonical filenames** `arch.md`, `func.md`, `errors.md`, `observability.md`, `review.md`, `runbook.md`. "obsv" and "docs" are *bucket* names, not file names — their files on disk are `observability.md` and `runbook.md` respectively. Use the canonical filenames so downstream consumers (DOCS bucket, `pr-prep`) find them deterministically.

---

## The Per-Feature Folder

One folder per feature, named with a short kebab-case slug (e.g. `settings-sidebar`, `bank-transactions`). Each file is the output of exactly one orchestrator bucket, so ownership is unambiguous:

| File | Bucket | Orchestrator | One-line purpose |
|------|--------|--------------|------------------|
| `arch.md` | Architecture & design | `arch-orchestrator` | The ADR: where this feature fits, what it blocks / is blocked by, its critical-path position, and the dependency graph. |
| `func.md` | Functionality | `func-orchestrator` | The implementation map: TDD contracts, story breakdown, and the happy-path build (with a pre-emptive DRY check). |
| `errors.md` | Error handling & retry | `errors-orchestrator` | The error matrix: every failure mode enumerated, each retry policy decided, each PII field protected. |
| `observability.md` | Observability | `obsv-orchestrator` | The telemetry plan: Golden-Signals coverage, structured log statements, metrics, and alerts. |
| `review.md` | Refactor & code review | `review-orchestrator` | The review record: smells found, SOLID/DRY validation, adversarial review notes. (The refactor-pipeline appends a `## Refactor Pass` section here when run in feature-factory context.) |
| `runbook.md` | Runbook & documentation | `docs-orchestrator` | The operational doc: per-error resolution steps, per-metric interpretation, and the list of doc/CLAUDE.md updates the feature requires. |

**Tier adjustment.** Not every feature needs all six files. A critical-path feature produces all six; a standard internal tool may skip `observability.md`; a bug fix may produce only `func.md` + `review.md`. The folder is allowed to be partial — its completeness reflects the feature's tier. (See `skills/feature-factory/README.md` → "Tier Adjustment.")

**Sibling ADRs.** A multi-item phase consolidates into one `arch.md`; a complex sub-feature can get its own sibling ADR file next to it (e.g. `adr-fc-bank-api.md`). Cite real file paths (with line numbers when referencing existing code) inside the ADR.

---

## The `_pr-prep/` Artifact Set

`_pr-prep/` is **PR-scoped**, not feature-scoped — one folder per pull request, named after the PR. Where the per-feature folder accumulates during development, this set is produced (often by a parallel agent team) when a PR is being opened or updated. The `pr-prep` skill is the sole writer.

| File / folder | Purpose |
|---------------|---------|
| `manifest.yaml` | PR metadata: `pr_number`, `branch`, `base`, `commit`, `features` list, `created`, `status`, and free-form `notes`. The index for the whole folder. |
| `updated-prd.md` | The product requirements refreshed to match what the PR actually ships (reconciles drift between the original spec and the implementation). |
| `code-test-audit.md` | Audit of the code change and its test coverage — gaps, risks, and what's verified. |
| `docs-audit.md` | Audit of documentation impact; notes in-place doc fixes the PR should carry. |
| `manual-testing-guide.md` | Step-by-step manual verification a reviewer can follow to exercise the change. |
| `pr-description.md` | The full human-readable write-up of the PR (context, what changed, why, how tested). |
| `pr-body.md` | The ready-to-paste PR body — the description distilled to what goes in the PR field. |
| `evidence/screenshots/` | Captured UI evidence (e.g. before/after screenshots); also holds walkthrough recordings when produced. |

Not every PR produces every file — an analysis-only or assets-skipped run records that in `manifest.yaml` `notes` and omits the artifacts it didn't generate. The manifest is always present and is the authoritative record of what the folder contains.

---

## Reserved Paths and Conventions

Three top-level names under `.feature-factory/` are **reserved** and cannot be used as feature slugs:

- `guide/` — reserved for a git submodule of the best-practices guide, when a project vendors it in.
- `_pr-prep/` — PR-scoped pr-prep outputs.
- `_refactor/` — standalone refactor-pipeline reports (`smell-report.json`, `plan.md`, `validation-report.md`), timestamped per run.

**Conventions:**
- Feature folders are kebab-case slugs; phase-style projects may prefix them (`phase-a-calendar`, `phase-b-security`).
- The leading-underscore prefix (`_pr-prep`, `_refactor`) marks **machine/tooling** folders, distinguishing them from human-named feature slugs.
- Each artifact ends with a one-line summary; ADRs cite file paths (with line numbers) when referencing existing code.

---

## Per-Run Artifacts (Autonomous Execution)

When a feature is executed by the autonomous code-kanban runner (see [AUTONOMOUS_CODE_KANBAN.md](AUTONOMOUS_CODE_KANBAN.md)), each agent run writes its own artifacts **inside the task's worktree**, under a per-run subfolder:

```
<worktree>/.feature-factory/code-kanban-run/<run_id>/
```

This keeps run logs and run-scoped outputs isolated per execution (and per worktree), separate from the durable per-feature folder in the host repo. The convention reuses the same `.feature-factory/` root so an agent operating in a worktree finds a familiar contract.

---

## How the Pieces Connect

The layout encodes the pipeline's data flow:

```
During development (per feature, in the feature's worktree):

  ARCH ──► FUNC ─┬─► ERRORS ─┐
                 ├─► OBSV ────┼─► DOCS ──► (PR ready)
                 └─► REVIEW ──┘
                     │
                     └─ refactor-pipeline may append "## Refactor Pass" to review.md

  Writes:  <feature-slug>/{arch,func,errors,observability,review,runbook}.md

At PR time (per PR):

  pr-prep runs ─► consumes the six per-feature artifacts
              └─► writes _pr-prep/<pr-slug>/{manifest.yaml, updated-prd.md,
                  code-test-audit.md, docs-audit.md, manual-testing-guide.md,
                  pr-description.md, pr-body.md, evidence/screenshots/}
```

- **ERRORS, OBSV, and REVIEW** can run in parallel after FUNC produces working code; **DOCS** waits for ERRORS and OBSV because `runbook.md` consumes their artifacts.
- **`pr-prep` consumes, it does not regenerate.** Rather than producing a parallel document tree, `pr-prep` ingests the per-feature artifacts as upstream context, so the feature folder remains the single source of truth. (See `skills/feature-factory/INTEGRATION_WITH_PR_PREP.md`.)

---

## Related Documentation

- **skills/feature-factory/README.md** — the six orchestrator skills that write the per-feature artifacts, plus tier adjustment rules.
- **skills/feature-factory/INTEGRATION_WITH_PR_PREP.md** — the full feature-factory ↔ pr-prep ↔ refactor-pipeline wiring and the authoritative reserved-path list.
- **skills/feature-factory/diagrams.md** — mermaid diagrams of the timeline, artifact ownership, and pr-prep handshake.
- **[AUTONOMOUS_CODE_KANBAN.md](AUTONOMOUS_CODE_KANBAN.md)** — how a `ready` task is executed in a worktree, where per-run artifacts (`code-kanban-run/<run_id>/`) land.
- **skills/pr-prep/** — the skill that produces the `_pr-prep/<pr-slug>/` artifact set.

---

**Status:** Pattern documentation — the `.feature-factory/` directory contract
**Last Updated:** 2026-05-25
**Maintainer:** Development Best Practices Repository
