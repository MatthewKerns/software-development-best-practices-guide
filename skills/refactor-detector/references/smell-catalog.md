# Smell Catalog — Detection Criteria & Severity Matrix

Based on: Clean Code (Chapter 17), Refactoring by Martin Fowler

## Severity Classification

| Severity | Criteria | Action Timeline |
|----------|----------|-----------------|
| CRITICAL | Actively causes bugs, blocks features, or creates cascading changes | Fix before next feature |
| HIGH | Significantly impairs maintainability or testability | Fix in current sprint |
| MEDIUM | Reduces code clarity or violates principles but doesn't block work | Plan for next refactoring cycle |
| LOW | Minor style/structure issues | Fix opportunistically (Boy Scout Rule) |

## Function-Level Smells

### Long Function
- **Detection**: Function > 50 lines (strict) or > 30 lines with multiple abstraction levels
- **Indicators**: Multiple comment blocks explaining sections, >3 nesting levels, >5 local variables
- **Severity**: HIGH if >80 lines, MEDIUM if 50-80 lines
- **Catalog refactoring**: EXTRACT_METHOD, REPLACE_TEMP_WITH_QUERY

### Too Many Parameters
- **Detection**: >3 parameters in function signature
- **Indicators**: Parameters that travel together, same param groups in multiple functions
- **Severity**: MEDIUM (>3 params), HIGH (>6 params)
- **Catalog refactoring**: INTRODUCE_PARAMETER_OBJECT, PRESERVE_WHOLE_OBJECT

### Flag Arguments
- **Detection**: Boolean parameter that controls branching behavior
- **Indicators**: `if (flag)` at top of function, function does two different things
- **Severity**: MEDIUM
- **Catalog refactoring**: SPLIT_FUNCTION

### Dead Code
- **Detection**: Unreachable paths, unused functions, commented-out blocks
- **Indicators**: No callers (grep confirms), `// TODO: remove`, commented blocks >5 lines
- **Severity**: LOW (unused functions), MEDIUM (large commented blocks that confuse)
- **Catalog refactoring**: DELETE

### Duplicate Code
- **Detection**: Same or near-identical logic in 2+ places
- **Indicators**: Copy-paste patterns, similar structure with minor variations
- **Severity**: HIGH (3+ copies), MEDIUM (2 copies)
- **Catalog refactoring**: EXTRACT_METHOD, FORM_TEMPLATE_METHOD

## Class/Module-Level Smells

### God Class/Component
- **Detection**: Class >300 lines (service) or >150 lines (component) or >200 lines (hook)
- **Indicators**: >10 public methods, >7 instance variables, multiple unrelated responsibilities
- **Severity**: HIGH if >2x threshold, CRITICAL if >3x threshold
- **Catalog refactoring**: EXTRACT_CLASS, EXTRACT_COMPONENT

### Feature Envy
- **Detection**: Method uses another module's data more than its own
- **Indicators**: Excessive getter/property chains from imported objects, method "reaches into" foreign state
- **Severity**: MEDIUM
- **Catalog refactoring**: MOVE_METHOD, EXTRACT_METHOD

### Inappropriate Intimacy
- **Detection**: Two modules access each other's internal details
- **Indicators**: Circular imports, accessing private/internal members, mutual modification of state
- **Severity**: HIGH
- **Catalog refactoring**: MOVE_METHOD, EXTRACT_CLASS, HIDE_DELEGATE

### Divergent Change
- **Detection**: One class changes for many different reasons
- **Indicators**: Multiple unrelated git change patterns, different "actors" driving changes
- **Severity**: CRITICAL (SRP violation with active consequences)
- **Catalog refactoring**: EXTRACT_CLASS

### Shotgun Surgery
- **Detection**: One logical change requires modifications in many files
- **Indicators**: Related logic scattered across >3 files, no single point of change
- **Severity**: CRITICAL
- **Catalog refactoring**: MOVE_METHOD, INLINE_CLASS

### Data Class
- **Detection**: Class with only fields and getters/setters, no behavior
- **Indicators**: Other classes manipulate its data, no methods beyond accessors
- **Severity**: LOW (DTOs are fine), MEDIUM (if behavior should live here)
- **Catalog refactoring**: MOVE_METHOD (move behavior to data class)

## Structure Smells

### Deep Nesting
- **Detection**: >3 levels of indentation
- **Indicators**: Nested if/for/while, complex conditional trees
- **Severity**: MEDIUM (4 levels), HIGH (5+ levels)
- **Catalog refactoring**: GUARD_CLAUSES, EXTRACT_METHOD

### Primitive Obsession
- **Detection**: Using primitives instead of small objects for domain concepts
- **Indicators**: Related primitives passed together, validation logic repeated for same primitive
- **Severity**: MEDIUM
- **Catalog refactoring**: REPLACE_DATA_VALUE_WITH_OBJECT

### Data Clumps
- **Detection**: Same group of data items appearing together in multiple places
- **Indicators**: 3+ params that travel together, repeated field groups
- **Severity**: MEDIUM
- **Catalog refactoring**: EXTRACT_CLASS, INTRODUCE_PARAMETER_OBJECT

### Switch/Type Code Branching
- **Detection**: Switch/if-else chains on type discriminators
- **Indicators**: Same switch in multiple places, adding types requires changing switches
- **Severity**: HIGH (if duplicated), MEDIUM (if single location)
- **Catalog refactoring**: REPLACE_CONDITIONAL_WITH_POLYMORPHISM

### Magic Numbers/Strings
- **Detection**: Unexplained literal values in code
- **Indicators**: Numbers without named constants, repeated string literals
- **Severity**: LOW
- **Catalog refactoring**: REPLACE_MAGIC_WITH_NAMED_CONSTANT

### Speculative Generality
- **Detection**: Abstractions with single implementations, unused parameters, "future-proofing"
- **Indicators**: Abstract class with one subclass, interfaces nobody else implements, params always null
- **Severity**: LOW (minor), MEDIUM (if adds significant complexity)
- **Catalog refactoring**: COLLAPSE_HIERARCHY, INLINE_CLASS, REMOVE_PARAMETER

## React/Frontend-Specific Smells

### Prop Drilling
- **Detection**: Props passed through >2 intermediate components without use
- **Indicators**: Component accepts prop only to pass it down, prop threading across levels
- **Severity**: MEDIUM (3 levels), HIGH (4+ levels)
- **Catalog refactoring**: EXTRACT_CONTEXT, COMPOSE_COMPONENTS

### Side Effects in Render/setState
- **Detection**: Side effects (toasts, API calls, state updates) inside setState callbacks or render
- **Indicators**: Toast calls inside `setState(prev => {...; toast(); return ...})`, API calls in render
- **Severity**: HIGH (causes unpredictable behavior)
- **Catalog refactoring**: EXTRACT_EFFECT, MOVE_SIDE_EFFECT

### Mixed Concerns in Hook
- **Detection**: Hook manages unrelated state, mixes sync logic with UI state
- **Indicators**: Hook >200 lines, multiple unrelated useEffect, mixed localStorage + API + UI state
- **Severity**: HIGH
- **Catalog refactoring**: EXTRACT_HOOK, EXTRACT_SERVICE

### Polling Dependency Bug
- **Detection**: useEffect polling that includes mutable state in dependency array
- **Indicators**: `useEffect(() => { setInterval(...) }, [stateVar])` — restarts interval on every state change
- **Severity**: CRITICAL (causes performance/behavior bugs)
- **Catalog refactoring**: USE_REF_FOR_POLLING

## Error Handling Smells

### Swallowed Exceptions
- **Detection**: Empty catch blocks, catch-and-ignore patterns
- **Severity**: CRITICAL (hides bugs)
- **Catalog refactoring**: HANDLE_OR_PROPAGATE

### Inconsistent Error Handling
- **Detection**: Same error type handled differently across similar operations
- **Indicators**: Some methods toast, some throw, some return null, some log
- **Severity**: HIGH
- **Catalog refactoring**: NORMALIZE_ERROR_HANDLING

## Severity Priority Matrix

| Severity | Smell | Impact | Fix Effort |
|----------|-------|--------|------------|
| CRITICAL | Divergent Change | High | Medium |
| CRITICAL | Shotgun Surgery | High | High |
| CRITICAL | Swallowed Exceptions | High | Low |
| CRITICAL | Polling Dependency Bug | High | Low |
| HIGH | God Class/Component | Medium | Medium-High |
| HIGH | Duplicate Code (3+) | Medium | Low-Medium |
| HIGH | Side Effects in setState | Medium | Low |
| HIGH | Inconsistent Error Handling | Medium | Medium |
| HIGH | Deep Nesting (5+) | Medium | Low |
| MEDIUM | Long Function (50-80) | Low-Medium | Low |
| MEDIUM | Feature Envy | Low-Medium | Medium |
| MEDIUM | Too Many Parameters | Low | Low |
| MEDIUM | Primitive Obsession | Low | Low |
| LOW | Magic Numbers | Low | Low |
| LOW | Dead Code (small) | Low | Low |
| LOW | Speculative Generality | Low | Low |
