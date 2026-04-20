# Feature Factory — Full Skill Package

Six master orchestrator skills for the feature-delivery pipeline, plus integration notes for how they fit with the existing `pr-prep` skill.

---

## The System at a Glance

Every feature flows through six buckets, producing six artifacts, in one git worktree with one PR at the end:

```
ARCH ──► FUNC ──┬─► ERRORS ─┐
                ├─► OBSV ────┼─► DOCS ─► PR
                └─► REVIEW ──┘
                                           
Output:   arch.md ─► func.md + code ─► errors.md + code
          ─► observability.md + code ─► review.md + cleaner code
          ─► runbook.md + updated CLAUDE.md
```

ERRORS, OBSV, and REVIEW can run in parallel terminals after FUNC has produced working code. DOCS waits for ERRORS and OBSV to complete (it consumes their artifacts). The six artifacts live in `.feature-factory/` inside the feature's worktree.

---

## The Six Skills

| Skill | Bucket | Output | What it's for |
|-------|--------|--------|---------------|
| `arch-orchestrator` | Architecture & design | `arch.md` (ADR + dependency graph) | Where this feature fits; what it blocks and is blocked by; whether it's on the critical path |
| `func-orchestrator` | Functionality | working code + `func.md` | TDD through the happy path, with pre-emptive DRY check |
| `errors-orchestrator` | Error handling & retry | `errors.md` (error matrix) | Every failure mode enumerated, every retry policy decided, every PII field protected |
| `obsv-orchestrator` | Observability | `observability.md` + instrumented code | Golden Signals coverage, structured logs, metrics, alerts |
| `review-orchestrator` | Refactor & code review | cleaner code + `review.md` | Smell detection, SOLID validation, DRY check, adversarial review |
| `docs-orchestrator` | Runbook & documentation | `runbook.md` + updated docs | Per-error resolution, per-metric interpretation, updated CLAUDE.md |

---

## The Real Hard Bars

One feature per PR is the only non-negotiable size rule. LOC, file count, and commit count are **signals** that trigger a "justify or split" conversation — they're not pass/fail gates. A cross-file rename of 2000 LOC is trivial to review; a 50-line concurrency fix can take an hour. The signals exist to catch scope bundling early, not to force arbitrary splits.

The **artifact test** is the real scoping bar: does this PR have exactly one coherent `arch.md`? Does the error matrix cover one feature's failure modes? If the artifacts are singular, the PR size is right. If the artifacts are plural or blended, the PR is too big regardless of LOC.

---

## The Dependency Graph

The ARCH orchestrator's `arch.md` includes a required section that PR #6's retrospective revealed was missing from practice: an explicit dependency graph. For every feature:

- **Blocked By** — what must ship before this can
- **Blocks** — what's waiting on this
- **Critical Path Position** — is this on the critical path to the milestone?
- **External Dependencies** — APIs, credentials, infra that must be available

This section serves three purposes:
1. **Scope freeze reinforcement** — walkthrough-discovered items that aren't in the graph are new features, not extensions. Write a spec, pick a target PR.
2. **Critical path discipline** — if you're working non-critical-path features while the critical path waits, the ADR makes that trade-off explicit.
3. **Parallel planning** — `parallel-execution-planner` actually knows what can parallelize when the graph exists.

---

## Installation

### Personal (applies to all projects)
```bash
cp -r feature-factory-skills/*-orchestrator ~/.claude/skills/
```

### Project-specific
```bash
cp -r feature-factory-skills/*-orchestrator .claude/skills/
```

The orchestrator skills reference best-practices guides via relative paths like `01-foundations/ERROR_HANDLING.md`. For references to resolve, install the guide repo as a sibling or submodule:

```bash
# As a sibling of your workspace (recommended for cross-project use)
cd ~/workspace
git clone https://github.com/MatthewKerns/software-development-best-practices-guide.git

# Or as a submodule per project
git submodule add https://github.com/MatthewKerns/software-development-best-practices-guide.git docs/best-practices
```

If you install in a non-standard location, adjust the paths in each orchestrator's "Best Practices Reference" section.

---

## Usage

Orchestrators trigger automatically based on the description in their frontmatter. To invoke explicitly, mention the bucket:

- "Let's run the architecture review for F-14"
- "Implement this feature"
- "Design error handling for the TikTok returns flow"
- "What metrics should this have"
- "Review and clean this up"
- "Write the runbook"

The Clockify time-tracking convention also serves as a natural trigger:

```
{project} {feature-id} {bucket}: {description}
```

When you log `tiktok-mcf F-14 errors: enumerate API codes`, the ERRORS orchestrator is the one to activate.

---

## Tier Adjustment

Not every feature needs all six buckets:

| Tier | Examples | Required Buckets |
|------|----------|------------------|
| Critical Path | Core integrations, payment flows | All 6 |
| Standard | Internal tools, secondary integrations | ARCH, FUNC, ERRORS, REVIEW, DOCS |
| Quick | Bug fixes, copy changes | FUNC, REVIEW |

Mark the tier when starting the feature — the ADR's dependency graph position decides this. Critical path features get the full treatment; bug fixes can skip straight to FUNC + REVIEW.

---

## Integration with the Existing `pr-prep` Skill

See `INTEGRATION_WITH_PR_PREP.md` for the full picture. Short version:

- The orchestrators produce **per-feature artifacts** during development (`.feature-factory/*.md` in the feature worktree).
- The existing `pr-prep` skill produces **per-PR artifacts** at PR time (`_bmad-output/pr-prep/*.md`).
- The integration is that `pr-prep` should **consume the orchestrator artifacts** rather than regenerate parallel docs. When a feature is merged, its orchestrator artifacts get promoted into the PR's `docs/pr-prep/pr{N}/` folder.

This solves the retrospective's "two parallel document trees with unclear ownership" problem by making the orchestrator artifacts the single source of truth.

---

## Files in This Package

```
feature-factory-skills/
├── README.md                              ← this file
├── INTEGRATION_WITH_PR_PREP.md            ← how orchestrators + pr-prep fit together
├── arch-orchestrator/SKILL.md
├── func-orchestrator/SKILL.md
├── errors-orchestrator/SKILL.md
├── obsv-orchestrator/SKILL.md
├── review-orchestrator/SKILL.md
├── docs-orchestrator/SKILL.md
└── existing-pr-prep-skill/SKILL.md        ← current pr-prep skill, included for reference
```
