---
name: refactor-planner
description: Generates structured refactoring plans from code smell analysis. Use after running refactor-detector, when you have smell findings and need to decide what to refactor and in what order. Considers dependencies, parallelization opportunities, consumer impact, and risk. Produces dependency-ordered task lists with effort estimates. Triggers on "plan the refactoring", "create refactoring plan", "how should we refactor this", "prioritize these smells". This skill plans but does NOT execute — that's refactor-executor's job.
allowed-tools: [Read, Grep, Glob]
---

# Refactor Planner

Transform smell reports into actionable, dependency-ordered refactoring plans. Your sole responsibility is **planning** — deciding what to refactor, in what order, with what technique, and what the risks are. You do NOT detect smells (refactor-detector does that) and you do NOT execute changes (refactor-executor does that).

## Why Planning Matters

Refactoring without a plan leads to the three most common failures: (1) breaking consumers because you didn't map dependencies, (2) creating merge conflicts because you didn't identify parallelizable vs sequential work, and (3) scope creep because you didn't set clear boundaries. A good plan prevents all three.

## Planning Process

### 1. Ingest the Smell Report

Accept input from refactor-detector (structured JSON or human-readable report). Extract:
- Files with smells, sorted by severity
- Specific smell types and their catalog refactorings
- Cross-file patterns (duplication, shotgun surgery)

If no smell report exists, tell the user to run refactor-detector first, or offer to analyze inline.

### 2. Map the Dependency Graph

For each file with smells, determine:

**Consumers** — who imports/uses this file?
```bash
# Find all files that import from the target
grep -r "from.*target-file" src/ --include="*.ts" --include="*.tsx"
```

**Dependencies** — what does this file import?
Read the file's import statements.

**Public API surface** — what does this file export?
These exports are the contract with consumers. Changes to exports = breaking changes.

### 3. Classify Refactoring Independence

Group files into independence tiers:

| Tier | Definition | Implication |
|------|-----------|-------------|
| **Fully Independent** | Zero shared imports between target files | Can refactor in parallel (separate worktrees) |
| **Consumer-Independent** | Share consumers but don't import each other | Can parallel but must coordinate public API |
| **Dependent** | File A imports from File B | Must refactor in dependency order (B before A) |

### 4. Select Refactoring Techniques

For each smell, consult `references/refactoring-techniques.md` to select the appropriate technique. Consider:

- **Smell type** maps to specific catalog refactorings
- **File type** (component vs service vs hook) determines the structural pattern
- **Consumer count** determines how carefully you must preserve the public API
- **Test coverage** determines whether you need to add tests before refactoring

Read `references/refactoring-techniques.md` for the complete technique catalog with before/after examples and step sequences.

### 5. Order by Dependencies

Within each file's refactoring, tasks have internal dependencies:

```
Typical dependency order for service extraction:
1. Extract shared types/interfaces (no deps)
2. Extract utility functions (depends on types)
3. Extract sub-services (depends on types + utils)
4. Extract hooks (depends on services)
5. Recompose orchestrator (depends on all above)
6. Update consumers (depends on orchestrator API)
7. Tests + verification (depends on everything)
```

### 6. Identify Parallelization Opportunities

Look for tasks that can run simultaneously:
- Tasks at the same dependency level within a file
- Fully independent files (zero cross-imports)
- Tests can often run in parallel with other extractions

Build a timeline showing parallel lanes:

```
         T1              T2              T3              T4
Agent A: [types] [utils]  [service]       [hook]→[compose]  [tests]
Agent B: [types]          [adapter]       [normalize]→[compose] [tests]
         ^-- start simultaneously, zero cross-agent deps
```

### 7. Assess Risk

For each refactoring task:

| Risk Factor | Assessment |
|-------------|------------|
| Consumer count | How many files import the target? |
| API change | Does the public interface change? |
| Test coverage | Are there existing tests? |
| Complexity | How many responsibilities are being separated? |
| Merge conflict | Does this touch files others are editing? |

Risk level: LOW (internal only, tests exist), MEDIUM (API change with few consumers), HIGH (many consumers or no tests)

### 8. Produce the Refactoring Plan

Output format:

```markdown
# Refactoring Plan: [Scope]

## Context
[Brief summary of smell findings and rationale]

## Independence Analysis
| File | Consumers | Dependencies | Independence |
|------|-----------|-------------|-------------|
| ... | ... | ... | Fully Independent / Dependent on X |

## Parallelization Strategy
[Describe which files can be refactored in parallel, which must be sequential]

## Task Breakdown

### File: [path] (Current: N LOC -> Target: ~M LOC)

**Smells addressed:** [list]

| Task | Description | Depends On | Effort | Risk |
|------|-------------|------------|--------|------|
| T1 | Extract validation utils to src/utils/foo.ts | — | 30min | LOW |
| T2 | Extract FooService to src/services/FooService.ts | T1 | 1hr | MEDIUM |
| T3 | Extract useFoo hook | T2 | 45min | LOW |
| T4 | Recompose orchestrator | T1, T2, T3 | 30min | LOW |
| T5 | Tests + verification | T4 | 30min | LOW |

**Consumer impact:** [list which consumers need updating and how]
**Public API changes:** [list any breaking changes, or "None — public API preserved"]

## Merge Strategy
[Order of merging if multiple files, conflict risk assessment]

## Verification Checklist
- [ ] `npx tsc --noEmit` — zero type errors
- [ ] `npm run lint` — zero lint errors
- [ ] `npm test` — all tests pass
- [ ] Manual verification: [specific flows to test]
```

## Tradeoff Decisions

When planning, you'll face tradeoffs. Here's how to think about them:

**Depth vs breadth**: Should you fully decompose one god component, or do shallow fixes across 5 files? Prefer depth on HIGH/CRITICAL smells — a half-refactored god component is worse than an untouched one because now the logic is split but not cleanly separated.

**Preserve API vs clean API**: If the existing public API is messy but has many consumers, preserve it and add a clean internal layer. If few consumers, consider a clean break.

**Extract vs inline**: Not everything should be extracted. If a "smell" is only 60 lines and has one consumer, the overhead of a new file + interface might not be worth it. Use the Rule of Three — extract when duplication or complexity justifies it.

**Parallel agents vs sequential**: Parallel is faster but harder to coordinate. Use parallel only for fully independent files. If in doubt, go sequential — correctness over speed.

## References

- Read `references/refactoring-techniques.md` for the complete technique catalog
