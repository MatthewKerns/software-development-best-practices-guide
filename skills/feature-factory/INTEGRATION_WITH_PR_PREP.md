# Integration: Orchestrators ↔ `pr-prep` Skill

## The Problem This Document Solves

The existing `pr-prep` skill produces artifacts in `_bmad-output/pr-prep/`. The orchestrators produce artifacts in `.feature-factory/` inside each feature's worktree. Without explicit integration, these two document trees duplicate effort, drift out of sync, and create exactly the "which version is current?" problem that PR #6's retrospective called out.

This doc defines how the two fit together so that orchestrator artifacts are the single source of truth, and `pr-prep` consumes them rather than regenerating parallel docs.

---

## The Flow

```
                ┌──── During development (per feature) ────┐
                │                                          │
  ARCH ──► FUNC ─┬─► ERRORS ─┐                             │
                ├─► OBSV ────┼─► DOCS                      │
                └─► REVIEW ──┘                             │
                                                           │
  Artifacts in feature worktree:                           │
  .feature-factory/arch.md                                 │
  .feature-factory/func.md                                 │
  .feature-factory/errors.md                               │
  .feature-factory/observability.md                        │
  .feature-factory/review.md                               │
  .feature-factory/runbook.md                              │
                │                                          │
                └─────────── Feature complete ─────────────┘
                                   │
                                   ▼
                      ┌── At PR time (per PR) ──┐
                      │                         │
                      │   pr-prep skill runs    │
                      │                         │
                      │   CONSUMES the six      │
                      │   artifacts to produce: │
                      │                         │
                      │   - PR description      │
                      │   - docs audit          │
                      │   - testing guide       │
                      │                         │
                      └─────────────────────────┘
                                   │
                                   ▼
            ┌── Promote artifacts to docs/pr-prep/pr{N}/ ──┐
            │                                               │
            │  docs/pr-prep/pr{N}/arch.md                   │
            │  docs/pr-prep/pr{N}/func.md                   │
            │  docs/pr-prep/pr{N}/errors.md                 │
            │  docs/pr-prep/pr{N}/observability.md          │
            │  docs/pr-prep/pr{N}/review.md                 │
            │  docs/pr-prep/pr{N}/runbook.md                │
            │  docs/pr-prep/pr{N}/pr-description.md         │
            │                                               │
            │  _bmad-output/pr-prep/ is deleted             │
            │                                               │
            └───────────────────────────────────────────────┘
```

---

## How the Six Artifacts Map to `pr-prep`'s Agent Outputs

The existing `pr-prep` skill launches four parallel agents. Here's how their responsibilities should change when the orchestrator artifacts already exist:

| `pr-prep` Agent | Current Behavior | New Behavior with Orchestrators |
|-----------------|------------------|----------------------------------|
| **Agent 1 (PRD Gap Analysis)** | Reads PRD, maps FRs against code, produces `updated-prd.md` | Still does PRD gap analysis, but reads `arch.md` first for the decision record — no need to re-derive architectural intent from code |
| **Agent 2 (Code/Test Audit)** | Produces `code-test-audit.md` from scratch | Reads `func.md` (implementation summary) + `review.md` (quality findings) — produces a **consolidated** audit that cites the existing artifacts, doesn't duplicate them |
| **Agent 3 (Docs Audit)** | Finds stale docs, fixes in-place | Reads `runbook.md` for the new operational truth, updates any other docs (CLAUDE.md, READMEs) to match — the runbook is authoritative |
| **Agent 4 (Manual Testing Guide)** | Generates scenarios from scratch | Reads `errors.md` (for negative-path tests) + `observability.md` (for "what should be observable"), produces a testing guide that maps to the already-enumerated failure modes |

The key shift: `pr-prep` agents stop generating information and start **consolidating** what the orchestrators already captured during development.

---

## Specific Changes to the `pr-prep` Skill

These are the adjustments to the existing `pr-prep/SKILL.md` that would integrate the orchestrators. None of these require rewriting the skill — they're additions to existing phases.

### Change 1: Phase 1 — Detect orchestrator artifacts

Add to the "Situation Assessment" checks:

```bash
# Are there orchestrator artifacts for features in this PR?
for worktree in $(git worktree list --porcelain | grep worktree | awk '{print $2}'); do
  if [ -d "$worktree/.feature-factory" ]; then
    echo "Found orchestrator artifacts in $worktree:"
    ls "$worktree/.feature-factory/"
  fi
done
```

If orchestrator artifacts exist for any feature in the PR's commits, flag this in Phase 2b's assessment so the user knows the pr-prep run will be **consumption mode**, not **generation mode**.

### Change 2: Phase 2 — Scope check references the dependency graph

If `.feature-factory/arch.md` exists for the feature(s) in this PR, read the dependency graphs. Use them to validate:

- Is every "Blocked By" entry actually merged or included in this PR?
- Is every commit in the PR range covered by one of the ADRs?
- Are there commits in the range that touch files outside the affected modules listed in the ADRs?

Any mismatch surfaces as a scope drift flag before agents run.

### Change 3: Phase 2b — Default to `--skip-assets`, not full run

From the retrospective: "the pr-prep skill assumes assets before scope is locked. Phases 5a/5b/6 are heavy work with strong format opinions." The default should be analysis-only; assets are an explicit opt-in.

Change the Phase 2b prompt to default to `no` for asset generation. Make `--with-assets` the explicit flag for the heavy path.

### Change 4: Phase 4 — Promote artifacts, delete `_bmad-output/` copies

At the end of Phase 4 (after the PR description is finalized), prompt:

```
📁 ARTIFACT PROMOTION

The following orchestrator artifacts will be promoted to docs/pr-prep/pr{N}/:
  .feature-factory/arch.md            → docs/pr-prep/pr{N}/arch.md
  .feature-factory/func.md            → docs/pr-prep/pr{N}/func.md
  .feature-factory/errors.md          → docs/pr-prep/pr{N}/errors.md
  .feature-factory/observability.md   → docs/pr-prep/pr{N}/observability.md
  .feature-factory/review.md          → docs/pr-prep/pr{N}/review.md
  .feature-factory/runbook.md         → docs/pr-prep/pr{N}/runbook.md
  _bmad-output/pr-prep/pr-description.md → docs/pr-prep/pr{N}/pr-description.md

After promotion, _bmad-output/pr-prep/ will be deleted (single source of truth in docs/pr-prep/pr{N}/).

Proceed? [yes / no / skip-delete]
```

This is the "shrink, don't grow" acid test from the retrospective, applied to pr-prep itself.

### Change 5: PR Description Template — generated from artifacts, not hand-assembled

The PR description should include a standard section per bucket, generated by reading the artifact headers:

```markdown
## Architecture
See [arch.md](docs/pr-prep/pr{N}/arch.md) for the full ADR.
- **Decision**: {one-line from arch.md's Decision section}
- **Critical Path**: {from dependency graph}
- **Affected Modules**: {from arch.md}

## Implementation Summary
See [func.md](docs/pr-prep/pr{N}/func.md) for details.
- **What was built**: {one-line from func.md's What Was Built}
- **Tests**: {coverage from func.md}
- **Deviations from arch**: {from func.md}

## Error Handling
See [errors.md](docs/pr-prep/pr{N}/errors.md) for the full error matrix.
- **Strategy**: {correctness / robustness / hybrid — from errors.md}
- **External failure sources covered**: {count from matrix}
- **PII fields redacted**: {from matrix}

## Observability
See [observability.md](docs/pr-prep/pr{N}/observability.md) for the full plan.
- **Golden Signals coverage**: {from observability.md's coverage table}
- **Metrics added**: {count}
- **Alerts added**: {list}

## Review Findings
See [review.md](docs/pr-prep/pr{N}/review.md) for the full review.
- **Critical / Blocker / Issue findings fixed**: {counts}
- **Follow-up tickets created**: {count with links}

## Runbook
See [runbook.md](docs/pr-prep/pr{N}/runbook.md) for operational guidance.
- **Error resolution entries**: {count}
- **Metric interpretation entries**: {count}
```

This is the retrospective's "Phase table is the single status rollup" recommendation — the PR body is a view over the artifacts, never a separate activity log that drifts.

---

## Addressing the Retrospective's Refinements (A–I)

The retrospective listed nine refinements to the pr-prep skill. Here's how the orchestrator integration addresses each:

| # | Retrospective Refinement | How orchestrator integration helps |
|---|---------------------------|-------------------------------------|
| A | Collapse the doc tree to one source of truth per artifact | ✅ Orchestrator artifacts in `.feature-factory/` are promoted to `docs/pr-prep/pr{N}/`; `_bmad-output/` is deleted at Phase 4 end |
| B | Phase 0 — Scope freeze before any analysis | ✅ The ADR in `arch.md` is the scope freeze; pr-prep's Phase 2 validates the PR against the dependency graph |
| C | "Diff since last prep" refresh mode | ✅ When orchestrator artifacts exist, pr-prep runs in consumption mode (refresh the PR body from artifacts, don't regenerate) |
| D | Phase table is the single status rollup | ✅ PR description is generated from artifact headers, never hand-assembled |
| E | Split the skill in two (`pr-prep` vs `pr-prep-assets`) | ⚠️ Complementary change — Phase 2b default becomes `--skip-assets`; `--with-assets` is explicit opt-in |
| F | Commit cadence rule for docs | ⚠️ Complementary change to pr-prep — suggest squash when 3+ docs-only commits pile up |
| G | Move "Decisions made" to top of progress doc | ✅ The ADR in `arch.md` puts the Decision in the third section; runbook's error resolution is at the top |
| H | CI-first discipline while draft | ⚠️ Not solved by orchestrators — push-on-commit is a git workflow discipline |
| I | Every deferral names a target PR | ✅ The ADR's dependency graph requires target-PR naming for blocked/blocking features |

Five of nine are structurally addressed by the integration. Three more (E, F, H) are complementary pr-prep changes that don't conflict with the orchestrators — they can be adopted independently.

---

## Migration Strategy

You don't need to adopt this all at once. A staged path:

### Stage 1: Run orchestrators on one new feature
Pick F-12 or F-14 (TikTok MCF). Run it through the six buckets. Don't change pr-prep yet. See what the artifacts look like in practice.

### Stage 2: Manually consolidate at PR time
When that feature's PR is being prepared, copy the six artifacts into `docs/pr-prep/pr{N}/` by hand and write the PR body against them. Don't run pr-prep yet. Note where manual consolidation feels forced vs. natural.

### Stage 3: Update pr-prep to detect and consume orchestrator artifacts
Apply Changes 1–5 above. Run pr-prep on a new PR that has orchestrator artifacts. Iterate.

### Stage 4: Deprecate parallel doc generation
Once pr-prep reliably consumes artifacts, `_bmad-output/pr-prep/` becomes scratch space that's always deleted at the end of each run. No more "which doc is current?"

---

## Open Questions for the Developer

Before committing to this integration, some things worth checking:

1. **Worktree convention**: the orchestrators assume one git worktree per feature. Is that how features are actually developed currently, or does most work happen on a shared branch?

2. **Artifact location**: `.feature-factory/` is a proposal. If the repo already has a conventional location for per-feature docs (like `docs/features/{feature-id}/`), align with that instead.

3. **Tier handling in pr-prep**: a "quick" tier feature (bug fix) has only `func.md` + `review.md`. pr-prep needs to handle missing artifacts gracefully — not error out when there's no `arch.md`.

4. **Multi-feature PRs**: if a PR legitimately bundles 2–3 closely-related features (each with their own orchestrator artifacts), pr-prep needs to consume all of them and produce a PR body that covers the bundle coherently. This is a real case that needs design.

5. **Stale artifacts**: if a feature's worktree is abandoned but the artifacts remain, there should be a cleanup rule. Otherwise `.feature-factory/` accumulates garbage.

These don't need answers before Stage 1 — they're questions that'll surface naturally during the staged migration.
