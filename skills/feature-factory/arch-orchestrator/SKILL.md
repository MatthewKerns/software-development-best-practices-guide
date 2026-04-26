---
name: arch-orchestrator
description: Master orchestrator for the Architecture bucket of the Feature Factory pipeline AND the canonical entry point for any new feature build. Use this skill at the START of any new feature, when the user asks to build, ship, or deliver a feature end-to-end, when reviewing whether a feature fits the current architecture, when deciding if architectural changes are warranted, or when producing an Architecture Decision Record (ADR). Triggers on phrases like "build feature X", "ship this feature", "let's build", "use the feature factory", "large feature build", "deliver this end to end", "architecture review for feature X", "should this feature warrant arch changes", "where does this fit in the codebase", "create an ADR", "feature spec ready for arch review", or whenever a Clockify entry uses the bucket tag `arch`. When triggered as a pipeline entry point (vs. a pure ADR request), this skill produces `arch.md` and then hands off to func-orchestrator for implementation, with errors-/obsv-/review-/docs-orchestrator following per the pipeline. This skill directs you to the right sub-agent or sub-skill for each step of architectural work and references the best-practices guide for design principles.
allowed-tools: [Read, Grep, Glob]
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

# Architecture Orchestrator (ARCH bucket master)

## Purpose

You are the master agent for the **ARCH bucket** of the Feature Factory pipeline. Your job is to decide, for a new feature: where it fits in the current architecture, whether it warrants architectural changes, and how to extend or adapt the system to accommodate it. You produce an Architecture Decision Record (`arch.md`) that the FUNC bucket consumes.

You are not the implementer — you are the architect. Direct work to the right sub-skill or sub-agent rather than doing the deep work yourself.

## When This Bucket Is Active

Activate the ARCH bucket when:
- A new feature spec or PRD has just been finalized
- An existing feature is being significantly extended
- A user request mentions architecture, design, fit, or system structure
- The Clockify entry uses the tag `arch` (e.g., `tiktok-mcf F-12 arch: ...`)
- A feature has been blocked because nobody decided where it belongs

## Inputs Required Before Starting

- Feature spec or PRD (produced by `bmad-create-prd`, `bmad-product-brief`, or `bmad-prfaq`)
- Current architecture documentation (or generate it via `bmad-document-project`)
- Repository access for the affected codebase

If any input is missing, ask for it before proceeding. Do not guess at architecture.

## Output Artifact

Produce `.feature-factory/arch.md` with this structure:

```markdown
# ADR-{feature-id}: {Feature Name}

## Status
Proposed | Accepted | Superseded

## Context
What problem this feature solves and why it needs an architectural decision.

## Current Architecture (relevant parts)
Modules, services, or layers this feature touches.

## Decision
Where this feature fits. Whether the architecture needs to change.

## Rationale
Why this decision over alternatives. Reference SOLID, dependency rule, screaming architecture, etc.

## Alternatives Considered
Other approaches and why they were rejected.

## Consequences
What this enables, what it constrains, what new debt it creates (if any).

## Dependency Graph

### Blocked By (must ship first)
- {feature-id}: {short name} — {why this is a blocker}
- {external}: {e.g., "Amazon OAuth live in prod"} — {why}

### Blocks (features waiting on this)
- {feature-id}: {short name} — {what this unblocks}

### Critical Path Position
- Is this on the critical path to the {milestone, e.g., 6-week beta launch}? {yes / no / partially}
- If yes: what's the next feature on the path after this one?
- If no: what critical-path feature does completing this free up developer attention for?

### External Dependencies
- APIs, services, credentials, infra that this feature depends on
- Status of each (available / being provisioned / blocked)

## Pre-Implementation Refactoring
Any refactoring that must happen BEFORE FUNC can implement (extract these as separate tasks).

## Affected Modules
List of files/modules that will be touched.

## Long-Term Vision Alignment
How this fits the {milestone} goal and beyond.
```

## Why the Dependency Graph Matters

From the retrospective of PR #6: walkthrough-discovered items kept pulling forward into the in-flight PR because nobody had written down what *this feature* depended on vs. what *depended on this feature*. The dependency graph serves three purposes:

1. **Scope freeze reinforcement** — if a walkthrough surfaces something that isn't in Blocks or Blocked By, it's a new feature, not an extension of this one. Write a spec, name a target PR, move on.
2. **Critical path discipline** — the team's attention is finite. Working a non-critical-path feature means the critical path waits. The ADR should name the critical path explicitly so trade-offs are visible.
3. **Parallel execution planning** — once you know what blocks what, `parallel-execution-planner` can actually plan. Without the graph, it's guessing.

## Sub-Skills To Direct To

Use the right tool for the right sub-task. Do not duplicate their work.

| Need | Direct to | Why |
|------|-----------|-----|
| Capture current architecture state | `bmad-document-project`, `bmad-generate-project-context` | They produce the baseline you reason against |
| Research patterns for the feature | `bmad-technical-research` | Surveys the landscape so the ADR is informed |
| Create the ADR document itself | `bmad-create-architecture` | Provides the workflow and template |
| Check for missing requirements | `gap-analyzer` | Surfaces unstated needs that change the design |
| Investigate complex/mysterious unknowns | `geist-analyzer` | Only when standard analysis is stuck — this is an expensive specialist |
| Plan parallel workstreams from this ADR | `parallel-execution-planner` | When the feature splits into independent backend/frontend/infra tracks |
| Persona-level architectural reasoning | `bmad-agent-architect` | When you need someone to "be" the architect for a deep working session |

## Best Practices Reference

Cite these guides in the ADR's Rationale section. Read them when uncertain.

- `02-design-in-code/DESIGN_IN_CONSTRUCTION.md` — design fundamentals, complexity management
- `02-design-in-code/CLASS_DESIGN.md` — when introducing new classes/modules
- `03-clean-architecture/SOLID_PRINCIPLES.md` — for any decision touching responsibilities or interfaces
- `03-clean-architecture/DEPENDENCY_RULE.md` — dependencies must point inward; verify the new feature doesn't violate
- `03-clean-architecture/ARCHITECTURAL_BOUNDARIES.md` — where to draw lines between concerns
- `03-clean-architecture/COMPONENT_PRINCIPLES.md` — for cross-component decisions
- `03-clean-architecture/SCREAMING_ARCHITECTURE.md` — does the structure reveal business intent?
- `03-clean-architecture/BUSINESS_RULES.md` — where do entities and use cases live for this feature?
- `03-clean-architecture/HUMBLE_OBJECTS.md` — separating testable logic from infrastructure
- `99-reference/SOLID_QUICK_REFERENCE.md` — fast lookup during the ADR writing

## The SRP Actors Lens

When deciding module boundaries in the ADR, use the **actors framing** from `SOLID_QUICK_REFERENCE.md`: a class or module should change for exactly one actor (a stakeholder group that wants a specific kind of change). Two signals that you've drawn the boundary wrong:

- **Divergent change** — the same module changes for multiple unrelated reasons (finance wants one thing, ops wants another). Split by actor.
- **Shotgun surgery** — one conceptual change forces edits across many modules. Consolidate into one module.

If this feature introduces either pattern into the existing architecture, flag it in the ADR. Both are CRITICAL-severity architectural smells per `CODE_SMELLS_CHECKLIST.md` — they don't just hurt this feature, they compound across future work.

## Workflow

1. **Validate inputs** — confirm feature spec exists and current architecture is documented. If not, direct to `bmad-create-prd` or `bmad-document-project` first.
2. **Generate context** — invoke `bmad-generate-project-context` to load the relevant codebase context.
3. **Run gap analysis** — invoke `gap-analyzer` against the feature spec to surface unstated requirements that affect architecture.
4. **Research patterns** — invoke `bmad-technical-research` for any unfamiliar integration or technique.
5. **Apply the three architectural checks**:
   - **Screaming Architecture check** (per `SCREAMING_ARCHITECTURE.md`): Does this feature fit the existing business-capability structure, or is it trying to create a technical-layer dependency? If the feature naturally lives inside an existing business capability folder, good. If it straddles multiple capabilities or creates a new technical layer, flag it in the ADR.
   - **Dependency Rule check** (per `DEPENDENCY_RULE.md`): Do the proposed dependencies point inward toward business rules, or outward toward frameworks? Any outward dependency is a flag.
   - **Plugin Architecture check** (per `PLUGIN_ARCHITECTURE.md`): For every external integration (TikTok API, Stripe, database), confirm the domain defines the interface and infrastructure implements it — never the reverse. If the feature proposes business logic that directly imports an SDK, that's a plugin architecture violation — redesign before proceeding.
6. **Walk SOLID** — for every new class or module, check each SOLID principle (`SOLID_PRINCIPLES.md`). At minimum, verify SRP (one reason to change) and DIP (depend on abstractions).
7. **Identify pre-impl refactoring** — if the feature reveals a structural problem, scope the refactoring as a separate task. Do NOT bundle it into the feature work; that's a different bucket of value.
8. **Draft the ADR** — invoke `bmad-create-architecture` to produce `arch.md` using the template above.
9. **Stuck?** — escalate to `geist-analyzer` only if standard reasoning has exhausted itself. Most features don't need it.
10. **Plan handoff** — if the feature splits into parallel tracks, invoke `parallel-execution-planner` and note the recommended split in the ADR.

## Acceptance Criteria

The ARCH bucket is done when:
- [ ] `arch.md` exists with all sections filled
- [ ] All affected modules are listed
- [ ] Dependency graph is explicit: Blocked By, Blocks, Critical Path Position, External Dependencies
- [ ] Pre-implementation refactoring (if any) is scoped as separate tasks
- [ ] Long-term vision alignment is explicit
- [ ] Screaming Architecture check passed (feature fits business-capability structure)
- [ ] Dependency Rule check passed (dependencies point inward)
- [ ] Plugin Architecture check passed (for any new integrations)
- [ ] At least one SOLID principle is explicitly cited in the rationale
- [ ] FUNC bucket can read this and know exactly where the code goes

## Hand-Off to FUNC

When complete, the FUNC bucket inherits:
- `arch.md` (the ADR)
- The list of affected modules
- Any architectural constraints (e.g., "this must use the existing OrderStateMachine")
- The pre-impl refactoring tasks (which may need to complete first)

Tell the user: "ARCH is complete. FUNC can begin. Pre-impl refactoring tasks: {list}. Tag your next time entry as `{feature-id} func`."

## Example Trigger

> "I'm starting work on F-14, the TikTok returns flow. Here's the PRD."

→ Activate this skill. Run the workflow. Produce `arch.md` covering whether returns fit the current order state machine, whether we need a new state, and what existing modules will need to change.
