---
name: refactor-pipeline
description: Orchestrates the full refactoring workflow by composing refactor-detector, refactor-planner, refactor-executor, and refactor-validator into a holistic pipeline. Use when the user wants a complete refactoring workflow from analysis through execution and validation. Triggers on "run the refactoring pipeline", "full refactoring workflow", "refactor this end to end", "analyze and refactor", "complete refactoring cycle". Also triggers when the user invokes individual refactoring skills in sequence — offer to orchestrate the full pipeline instead. This is the entry point for comprehensive refactoring work.
allowed-tools: [Read, Grep, Glob, Edit, Write, Bash, Agent]
---

# Refactor Pipeline

Orchestrate the full refactoring workflow: detect smells, plan fixes, execute changes, validate results. This skill composes the four specialized refactoring skills into a coherent pipeline, managing handoffs and ensuring insights from each phase inform the next.

## Output Location (Feature Factory aware)

This pipeline is FF-aware. When invoked inside a project that uses the Feature Factory layout (`.feature-factory/<feature-slug>/` exists), append findings to that feature's `review.md` rather than producing standalone reports.

**FF context detection:**
1. Walk up from the current working directory to the project root (the directory containing `.feature-factory/`).
2. Identify the active feature slug:
   - If `.feature-factory/` contains exactly one feature folder (other than reserved `guide/`, `_pr-prep/`, `_refactor/`), that's the active feature.
   - If multiple, prefer the slug whose `pr-history.md` shows the most recent row in `in-progress` or `open` state.
   - If still ambiguous, **ask the user** which feature this refactoring belongs to before writing any output.

**FF-context outputs (preferred):**
- Append a section to `.feature-factory/<feature-slug>/review.md`:

  ```markdown
  ## Refactor Pass — YYYY-MM-DD

  **Scope:** {files analyzed}
  **Smells fixed:** {count by severity, using labels from CODE_REVIEW_CHECKLIST.md — [CRITICAL]/[BLOCKER]/[ISSUE]/[SUGGESTION]/[NITPICK]}
  **SOLID issues addressed:** {count}
  **Before/after metrics:** LOC {before} → {after} ({pct}%); functions {before} → {after}
  **Validator verdict:** PASS | PASS WITH NOTES | FAIL

  See `.feature-factory/_refactor/YYYY-MM-DD-HHMMSS/` for the full smell report, plan, and validation report.
  ```

- Detailed reports (smell JSON, refactoring plan, validation report) still go to `.feature-factory/_refactor/<timestamp>/` so `review.md` stays scannable.

**Standalone outputs (no FF context):**
- All reports go to `.feature-factory/_refactor/<timestamp>/` if `.feature-factory/` exists, or `_refactor-output/<timestamp>/` at project root otherwise.

**Why this matters:** when the pipeline runs inside an FF feature, `refactor-validator` cross-checks the `## Refactor Pass` section's findings against the diff. Standalone runs skip that cross-check (no `review.md` to verify against).

## Why an Orchestrator Exists

Each refactoring skill is focused by design (SRP for skills). But refactoring is inherently a connected workflow — the detector's findings constrain the planner's options, the planner's dependency analysis constrains the executor's parallelism, and the validator's findings might send you back to the executor. This orchestrator manages those connections so insights don't get lost between phases.

## Pipeline Phases

```
Phase 1: DETECT          Phase 2: PLAN           Phase 3: EXECUTE        Phase 4: VALIDATE
┌──────────────┐    ┌──────────────────┐    ┌──────────────────┐    ┌──────────────────┐
│ refactor-     │───>│ refactor-        │───>│ refactor-        │───>│ refactor-        │
│ detector      │    │ planner          │    │ executor         │    │ validator        │
│               │    │                  │    │                  │    │                  │
│ Smell Report  │    │ Refactoring Plan │    │ Code Changes     │    │ Validation Report│
│ (JSON + text) │    │ (tasks + deps)   │    │ (commits)        │    │ (pass/fail)      │
└──────────────┘    └──────────────────┘    └──────────────────┘    └──────────────────┘
                                                                           │
                                                                     FAIL? ↓ Loop back
                                                                    to PLAN or EXECUTE
```

## Running the Pipeline

### Step 1: Scope Agreement

Before starting, confirm with the user:
- **What to analyze**: specific files, a directory, or let detection decide
- **Depth**: quick scan (HIGH/CRITICAL only) or comprehensive (all severities)
- **Execution mode**:
  - **Full auto**: detect → plan → execute → validate without stopping
  - **Review gates**: pause after each phase for user approval (recommended for first run)
  - **Plan only**: detect + plan, but don't execute yet

Default to **review gates** unless the user explicitly asks for full auto.

### Step 2: Detection Phase

Invoke refactor-detector (or use the `/code-smell-detector` skill):

**Input**: files/scope to analyze
**Output**: structured smell report (JSON + human-readable summary)

Present the smell report to the user. Key information to highlight:
- Total smell count by severity
- Top 3 priority targets
- Any CRITICAL findings that need immediate attention

**Gate**: "Here are the findings. Should I proceed to planning, or would you like to adjust the scope?"

### Step 3: Planning Phase

Invoke refactor-planner with the smell report:

**Input**: smell report from Phase 1
**Output**: structured refactoring plan with dependency-ordered tasks

Before presenting, enrich the plan with cross-phase insights:
- If detection found cross-file duplication, ensure the plan addresses it holistically
- If detection found a polling bug, ensure the plan prioritizes it (CRITICAL)
- If multiple files are independent, ensure the plan leverages parallelism

Present the plan to the user. Key information to highlight:
- Parallelization opportunities (saves time)
- Risk assessment per task
- Consumer impact (will anything break?)
- Estimated effort

**Gate**: "Here's the refactoring plan. Should I proceed with execution, or adjust anything?"

### Step 4: Execution Phase

Invoke refactor-executor with the approved plan.

**Parallelization decision**:
- If the plan identifies fully independent files → spawn parallel agents (one per file) in isolated worktrees
- If files are dependent → execute sequentially in dependency order
- Always run tests after each task within each agent

**Monitoring during execution**:
- Track which tasks are complete
- If an agent hits a problem, don't block others — note it and continue
- Collect before/after metrics from each agent

**When using parallel agents**:
```
Use the Agent tool with:
- subagent_type: "general-purpose" (or appropriate type)
- isolation: "worktree" for independent files
- Each agent gets: the plan for its file(s) + the executor skill context
```

### Step 5: Validation Phase

Invoke refactor-validator on all changed files:

**Input**: the changed files, the original plan, before/after metrics from execution
**Output**: validation report (pass/fail with details)

### Step 6: Handle Validation Results

**If PASS**:
- Present the validation report
- Summarize total improvement (before/after metrics)
- Suggest merge strategy if multiple branches

**If PASS WITH NOTES**:
- Present findings
- Ask user if notes are acceptable or need addressing
- If addressing, loop back to executor for targeted fixes

**If FAIL**:
- Present specific failures
- Determine which phase to loop back to:
  - Build/test failures → executor (fix the code)
  - New smells introduced → planner (revise the approach)
  - SOLID violations → executor (restructure)
- Loop with the specific failure context so the phase knows what to fix

## Inter-Skill Communication Protocol

When one phase produces an insight that another phase needs:

### Detection → Planning Insights
- Cross-file duplication patterns → planner should address holistically
- Dependency fan-out metrics → planner should consider extraction boundaries
- CRITICAL smells → planner must prioritize these first

### Planning → Execution Insights
- Independence tiers → executor knows what to parallelize
- Consumer lists → executor knows what API to preserve
- Risk assessments → executor knows where to be extra careful

### Execution → Validation Insights
- Before/after metrics collected during execution → validator uses for comparison
- Any workarounds or compromises made → validator knows to check specifically
- Files that changed unexpectedly → validator examines for collateral damage

### Validation → Feedback Loop
- Specific failures → sent back to the responsible phase with full context
- "Almost there" results → targeted fix instructions for executor
- New smells detected → re-plan just the affected modules

## When to Skip Phases

- **Skip detection** if the user already has a smell report or knows exactly what to refactor
- **Skip planning** if the user provides a plan or the refactoring is simple (single extract)
- **Skip validation** only if explicitly asked (not recommended)
- **Never skip execution** — that's the actual work

## Quick Start: Common Workflows

### "This file is too big, help me refactor it"
1. Run detector on the file → identify responsibilities
2. Run planner → create extraction plan
3. Run executor → extract and recompose
4. Run validator → verify quality

### "We have 3 files that need refactoring"
1. Run detector on all 3 → identify independence
2. Run planner → create parallel plan if independent
3. Spawn 3 executor agents in worktrees → parallel execution
4. Merge branches
5. Run validator on merged result

### "Just do a quick cleanup"
1. Run detector (HIGH/CRITICAL only)
2. Skip full planning → use detector's suggested refactorings directly
3. Run executor on top priorities
4. Run validator

## Pipeline Completion Summary

After the full pipeline completes, present:

```markdown
# Refactoring Pipeline Complete

## Scope
[What was analyzed and refactored]

## Results
| File | Before (LOC) | After (LOC) | Reduction | Smells Fixed |
|------|-------------|------------|-----------|-------------|
| ... | ... | ... | ...% | N smells |

**Total**: N files, X → Y lines (Z% reduction), M smells resolved

## Quality
- Build: PASS
- Tests: PASS (N tests)
- SOLID: X/5 average
- New smells: 0

## Merge Strategy
[How to merge if multiple branches]
```
