---
name: refactor-validator
description: Validates refactored code against SOLID principles, code smell thresholds, and before/after metrics. Use after refactor-executor completes to verify the refactoring achieved its goals without introducing new problems. Triggers on "validate the refactoring", "check refactoring quality", "did the refactoring work", "verify refactoring results", "post-refactoring check". Catches regressions, new smells, SOLID violations, and broken consumers. This is the quality gate before merging.
allowed-tools: [Read, Grep, Glob, Bash]
---

# Refactor Validator

Validate that refactored code meets quality standards and hasn't introduced new problems. Your sole responsibility is **validation** — checking the results against SOLID principles, smell thresholds, and before/after metrics. You do NOT detect initial smells (refactor-detector), plan refactoring (refactor-planner), or execute changes (refactor-executor).

## Why Post-Refactoring Validation Matters

Refactoring is supposed to improve code without changing behavior. But in practice, three things commonly go wrong: (1) new smells get introduced while fixing old ones (e.g., extracting a service creates a god-interface), (2) the public API subtly changes and breaks consumers, (3) the extraction doesn't go far enough and the original file is still too complex. This skill catches all three.

## Validation Process

### 1. Verify Build and Tests

Before any structural analysis, confirm the basics:

```bash
npx tsc --noEmit        # Zero type errors
npm run lint             # Zero lint errors
npm test                 # All tests pass
```

If any of these fail, report the failures and stop. Don't validate structure on broken code.

### 2. Before/After Metrics Comparison

For each refactored file, compare metrics:

| Metric | Before | After | Verdict |
|--------|--------|-------|---------|
| Lines of Code | 602 | 170 | PASS (72% reduction) |
| Function Count | 15 | 4 | PASS |
| Max Function Length | 87 | 25 | PASS |
| Responsibility Count | 7 | 1 | PASS |
| Import Count | 18 | 8 | PASS |

**Thresholds for "PASS"**:
- Component: <150 LOC, <5 functions, <30 max function length
- Service: <300 LOC, <10 public methods
- Hook: <200 LOC, <5 useState, <3 useEffect
- Utility: <100 LOC, pure functions only

### 3. SOLID Validation

Check each extracted module against SOLID principles. Read `references/solid-validation.md` for the complete validation criteria.

For each module, assess:

**Single Responsibility (SRP)**
- Can you describe what this module does in one sentence without "and"?
- Does it have exactly one reason to change?
- Would different stakeholders cause it to change?

**Open/Closed (OCP)**
- Can new behavior be added without modifying this code?
- Are extension points clear (interfaces, abstract classes)?

**Liskov Substitution (LSP)**
- If interfaces are used, can all implementations be swapped?
- Do implementations honor the contract?

**Interface Segregation (ISP)**
- Are interfaces focused (no methods clients don't use)?
- Would splitting the interface benefit any consumer?

**Dependency Inversion (DIP)**
- Do high-level modules depend on abstractions?
- Are concrete dependencies injected, not hardcoded?

### 4. New Smell Detection

Run the same detection criteria as refactor-detector on the NEW files:

- Are any extracted files already too large?
- Did extraction create unnecessary abstractions (Speculative Generality)?
- Is there new duplication between extracted modules?
- Are there circular dependencies between new modules?
- Did the orchestrator become a "traffic cop" that adds no value (Middle Man)?

### 5. Consumer Impact Verification

For each file that was refactored:

1. Find all consumers: `grep -r "from.*original-file" src/`
2. Check if consumers still compile: `npx tsc --noEmit`
3. Verify re-exports exist if the plan called for API preservation
4. Check for any `// @ts-ignore` or `as any` that was added to make things compile

### 6. Produce Validation Report

Output format:

```markdown
# Refactoring Validation Report

## Build Status
- TypeScript: PASS/FAIL
- Lint: PASS/FAIL
- Tests: PASS/FAIL (N passed, M failed)

## Before/After Metrics

### [filename]
| Metric | Before | After | Threshold | Verdict |
|--------|--------|-------|-----------|---------|
| LOC | 602 | 170 | <150 | PASS |
| ... | ... | ... | ... | ... |

**Total reduction**: N lines -> M lines (X% reduction)

## SOLID Compliance

### [module-name]
| Principle | Status | Notes |
|-----------|--------|-------|
| SRP | PASS | Single responsibility: "manages document upload state" |
| OCP | PASS | New document types can be added via validation config |
| LSP | N/A | No inheritance hierarchy |
| ISP | PASS | Interface has 4 focused methods |
| DIP | PASS | Depends on IDocumentUploadService interface |

## New Smell Check
- [ ] No extracted file exceeds thresholds
- [ ] No speculative generality (single-use abstractions justified)
- [ ] No new duplication between modules
- [ ] No circular dependencies
- [ ] No Middle Man anti-pattern

## Consumer Impact
- [consumer1.tsx]: Compiles, no changes needed (re-exports in place)
- [consumer2.tsx]: Updated import path, verified

## Overall Verdict: PASS / PASS WITH NOTES / FAIL

### Issues Found (if any)
1. [Issue description and recommendation]

### Recommendations (if any)
1. [Future improvement suggestion]
```

## Validation Severity

| Verdict | Criteria |
|---------|----------|
| **PASS** | All metrics within thresholds, SOLID compliant, no new smells, consumers unbroken |
| **PASS WITH NOTES** | Minor issues that don't block merge (e.g., a file is 160 lines vs 150 threshold) |
| **FAIL** | Build broken, tests failing, SOLID violations, new HIGH/CRITICAL smells, or broken consumers |

## References

- Read `references/solid-validation.md` for detailed SOLID validation criteria and decision trees
