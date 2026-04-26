# Integration: Feature Factory ↔ pr-prep ↔ refactor-pipeline

This doc describes how the three skill families compose end-to-end during a feature build. It supersedes any older flow diagrams that referenced `_bmad-output/pr-prep/` or `docs/pr-prep/pr{N}/` — those paths are retired per pr-prep Spec 4 (artifact organization).

---

## The Canonical Layout

Everything for a feature lives under `.feature-factory/` at the project root:

```
.feature-factory/
├── guide/                                 ← (reserved) git submodule of best-practices guide, when used
├── <feature-slug>/                        ← per-feature folder (owned by FF orchestrators)
│   ├── arch.md                            ← arch-orchestrator
│   ├── func.md                            ← func-orchestrator
│   ├── errors.md                          ← errors-orchestrator
│   ├── observability.md                   ← obsv-orchestrator
│   ├── review.md                          ← review-orchestrator (refactor-pipeline appends here too)
│   ├── runbook.md                         ← docs-orchestrator
│   └── pr-history.md                      ← pr-prep (sole writer of new rows)
├── _pr-prep/                              ← (reserved) PR-scoped pr-prep outputs
│   └── pr-<N>-<short-slug>/
│       ├── manifest.yaml
│       ├── feature-factory-context.md     ← Phase 2c digest of upstream FF artifacts
│       ├── updated-prd.md                 ← Phase 3 Agent 1
│       ├── code-test-audit.md             ← Phase 3 Agent 2
│       ├── docs-audit.md                  ← Phase 3 Agent 3
│       ├── manual-testing-guide.md        ← Phase 3 Agent 4
│       ├── pr-description.md              ← Phase 4 synthesis
│       ├── docs-commit-plan.md            ← Phase 4.5 (per Spec 3)
│       ├── proposed-claude-md-edits.md    ← Phase 4.5 (only when multi-section CLAUDE.md edit proposed)
│       └── evidence/                      ← Phase 5b screenshots, Phase 6 recordings
└── _refactor/                             ← (reserved) standalone refactor-pipeline reports
    └── <YYYY-MM-DD-HHMMSS>/
        ├── smell-report.json
        ├── plan.md
        └── validation-report.md
```

**Reserved paths** (cannot be used as feature slugs): `guide/`, `_pr-prep/`, `_refactor/`.

---

## The Flow

```
                    ┌── During development (per feature) ──┐
                    │                                       │
ARCH ──► FUNC ─┬─► ERRORS ─┐                                │
               ├─► OBSV ────┼─► DOCS ──► (PR ready)         │
               └─► REVIEW ──┘    │                          │
                  │              │                          │
                  └─ may invoke refactor-pipeline           │
                     (appends ## Refactor Pass section      │
                      to <slug>/review.md when in FF context)│
                                                            │
                Artifacts in <slug>/:                       │
                arch.md, func.md, errors.md,                │
                observability.md, review.md, runbook.md     │
                    │                                       │
                    └────────── Feature complete ───────────┘
                                       │
                                       ▼
                       ┌── At PR time (per PR) ──────────────┐
                       │                                      │
                       │  pr-prep runs                        │
                       │  • Phase 1:  situation assessment    │
                       │  • Phase 2:  scope (base + commits)  │
                       │  • Phase 2c: detect FF artifacts,    │
                       │              write FF context digest │
                       │  • Phase 3:  4 parallel agents       │
                       │              consume FF artifacts as │
                       │              authoritative source    │
                       │  • Phase 4:  synthesis + appends     │
                       │              row to pr-history.md    │
                       │  • Phase 4.5: docs commit plan       │
                       │              (FF artifacts → docs/…) │
                       │  • Phase 5+ (opt-in): assets,        │
                       │              Excalidraw, E2E, video  │
                       │                                      │
                       │  Outputs to:                         │
                       │  .feature-factory/_pr-prep/          │
                       │    pr-<N>-<short-slug>/              │
                       └──────────────────────────────────────┘
```

---

## Ownership Rules

Single-writer rule — every artifact has exactly one owner. Other skills may read or update narrowly-defined fields, but never insert or rewrite content owned by another skill.

| Artifact | Owner | Other skills' rights |
|----------|-------|----------------------|
| `<slug>/arch.md` | arch-orchestrator | Multi-PR features: orchestrator appends `## PR #N update — YYYY-MM-DD` sections; never overwrites prior content |
| `<slug>/func.md` | func-orchestrator | Same append-only multi-PR rule |
| `<slug>/errors.md` | errors-orchestrator | Same append-only multi-PR rule |
| `<slug>/observability.md` | obsv-orchestrator | Same append-only multi-PR rule |
| `<slug>/review.md` | review-orchestrator | refactor-pipeline appends `## Refactor Pass — YYYY-MM-DD` sections; each new PR adds a `## PR #N Review` heading |
| `<slug>/runbook.md` | docs-orchestrator | Same append-only multi-PR rule |
| `<slug>/pr-history.md` | **pr-prep** (sole writer of new rows) | Orchestrators may update `Status` column on existing rows (e.g., `in-progress` → `merged`) but never insert new rows |
| `_pr-prep/pr-<N>-<short-slug>/` | pr-prep | All files inside |
| `_refactor/<timestamp>/` | refactor-pipeline | Standalone reports (when no FF context) |

---

## How pr-prep Consumes FF Artifacts (Phase 2c → 3)

Phase 2c (FF detection) reads every `.feature-factory/<slug>/` folder touched by the PR's commits and produces `feature-factory-context.md`. This file is the FIRST input to each Phase 3 agent. Agents read it before any code.

| pr-prep Agent | Reads from FF artifacts | Produces |
|---------------|-------------------------|----------|
| Agent 1 — PRD Gap | `arch.md` (decision, dependency graph), `func.md` (deviations) | `updated-prd.md` |
| Agent 2 — Code/Test Audit | `func.md` (impl summary), `review.md` ("Fix in this PR" claims, refactor-pass sections) | `code-test-audit.md` (Table 3 verifies review.md claims against the diff) |
| Agent 3 — Docs Audit | `runbook.md`, `arch.md`, `errors.md`, `observability.md` (maps each to a committed docs target; flags unmapped for Phase 4.5) | `docs-audit.md` |
| Agent 4 — Manual Testing | `errors.md` (negative paths), `observability.md` (what should be observable) | `manual-testing-guide.md` |

The agents **consolidate**, they don't re-derive. If FF artifacts are absent, agents fall back to deriving from code (legacy mode).

---

## How refactor-pipeline Composes With FF

`refactor-pipeline` runs in either of two contexts:

**Inside FF (most common):** invoked by review-orchestrator (or directly by the user during the REVIEW bucket). Appends a `## Refactor Pass — YYYY-MM-DD` section to the active feature's `review.md`. Detailed smell/plan/validation reports go to `.feature-factory/_refactor/<timestamp>/`. `refactor-validator` then cross-checks `review.md`'s `[CRITICAL]`/`[BLOCKER]`/`[ISSUE]` "Fix in this PR" claims against the diff and fails validation if any are unresolved.

**Standalone (outside FF):** invoked for ad-hoc cleanup outside an active feature. All outputs go to `.feature-factory/_refactor/<timestamp>/` if `.feature-factory/` exists; otherwise `_refactor-output/<timestamp>/` at project root. No `review.md` cross-check.

**Active feature detection:** the pipeline walks up to find `.feature-factory/`, then identifies the active feature slug. If exactly one feature folder exists (excluding reserved paths), that's it. If multiple, prefer the slug whose `pr-history.md` shows the most recent row in `in-progress` or `open` state. If still ambiguous, ask the user before writing.

---

## Multi-PR Features

A feature may ship across N PRs. Each bucket file (`arch.md`, `func.md`, `errors.md`, `observability.md`, `runbook.md`) accumulates `## PR #N update — YYYY-MM-DD` sections; nothing is overwritten. `review.md` accumulates `## PR #N Review` and `## Refactor Pass — YYYY-MM-DD` sections in chronological order. `pr-history.md` accumulates one row per PR (appended by pr-prep at synthesis time).

This makes the feature folder the single source of truth for the feature's history; reviewers can read the chain instead of hunting through merged PRs and historical chat logs.

---

## Multi-Feature PRs

A single PR may touch 2+ features. `manifest.yaml.features` lists them. pr-prep iterates per-feature in Phase 4.5 (one section per slug in `docs-commit-plan.md`) and appends one row to each feature's `pr-history.md`.

---

## Where Each Bucket's Output Goes At PR Time

Phase 4.5 (Documentation Commit Plan) is the bridge from working artifacts to committed project docs. Default dispositions per Spec 3:

| FF artifact | Default disposition | Default committed-doc target |
|-------------|---------------------|-------------------------------|
| `arch.md` | EDIT existing single section | `docs/architecture/ARCHITECTURE.md` (never auto-create an ADR) |
| `func.md` | SKIP (working artifact only) | — |
| `errors.md` | CREATE | `docs/features/<feature>-error-handling.md` (flat naming when `docs/features/` exists; falls back to a section in `CLAUDE.md`) |
| `observability.md` | CREATE | `docs/features/<feature>-observability.md` |
| `review.md` | SKIP (working artifact only) | — |
| `runbook.md` | CREATE | `docs/runbooks/<feature>.md` |

Each row gets per-approval prompting; nothing applies without explicit `y`. CLAUDE.md edits are gated additionally — single-section diffs only; multi-section edits downgrade to `proposed-claude-md-edits.md` for human review.

After Phase 4.5 completes, pr-prep re-renders `pr-description.md`'s "Related Docs" and "Runbook entry" sections so they reference the newly-committed in-repo paths instead of working-artifact paths.

---

## What Changed From the Original Design

The original integration spec (committed before pr-prep was rewritten) proposed promoting FF artifacts into `docs/pr-prep/pr{N}/` at PR time and deleting `_bmad-output/pr-prep/`. That promotion step has been retired:

- `_bmad-output/pr-prep/` is no longer used.
- `docs/pr-prep/pr{N}/` is no longer used.
- All pr-prep outputs stay under `.feature-factory/_pr-prep/pr-<N>-<short-slug>/`.
- Phase 4.5 is the new bridge: it proposes WHICH FF artifacts should be promoted into committed project documentation (`docs/runbooks/`, `docs/features/`, `docs/architecture/`, `CLAUDE.md`) on a per-row, per-approval basis, and stages (but never commits) those changes.

The "single source of truth" property is preserved: the `<slug>/` folder is the working source of truth during development; Phase 4.5 explicitly promotes selected content into committed-doc paths when ready, with hand-edit detection to avoid clobbering manual changes.

---

## Migration Path (for existing projects)

If a project still uses `_bmad-output/pr-prep/` or `docs/pr-prep/pr{N}/` from the legacy design:

1. **First run:** `mkdir -p .feature-factory/_pr-prep/` and let pr-prep populate it on the next run.
2. **Manual sweep:** copy any still-valuable content from `_bmad-output/pr-prep/` into the new layout under `.feature-factory/_pr-prep/pr-<N>-<short-slug>/`.
3. **Delete or `.gitignore`** the legacy `_bmad-output/pr-prep/` directory.

For ongoing/active features: when ARCH first runs, it auto-creates `.feature-factory/<feature-slug>/`. Existing `pr-history.md` from any prior tooling can be left in place; pr-prep will append rows to it.

---

## Spec References

The pr-prep skill cites four canonical specs in the consuming project's `docs/specs/`:

- **Spec 1** (`pr-prep-feature-factory-1-ingestion.md`) — Phase 2c FF detection and context digest format
- **Spec 2** (`pr-prep-feature-factory-2-enrichment.md`) — How Phase 3 agents consume FF context
- **Spec 3** (`pr-prep-feature-factory-3-commit-plan.md`) — Phase 4.5 disposition rules and CLAUDE.md guardrails
- **Spec 4** (`pr-prep-feature-factory-4-organization.md`) — Output layout under `.feature-factory/_pr-prep/`

If the consuming project doesn't have these spec files, pr-prep still operates from the defaults documented in its SKILL.md.
