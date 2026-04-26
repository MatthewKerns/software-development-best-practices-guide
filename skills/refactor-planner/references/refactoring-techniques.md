# Refactoring Techniques Catalog

Based on: Refactoring by Martin Fowler, Clean Code (Ch. 17)

## Technique Selection Guide

| Smell | Primary Technique | When to Use |
|-------|------------------|-------------|
| Long Function | EXTRACT_METHOD | Function >50 lines with identifiable sections |
| God Class | EXTRACT_CLASS | Class >300 lines with >2 responsibilities |
| God Component | EXTRACT_COMPONENT + EXTRACT_HOOK | Component >150 lines mixing UI + logic |
| Duplicate Code | EXTRACT_METHOD or EXTRACT_CLASS | Same logic in 2+ places |
| Feature Envy | MOVE_METHOD | Method uses foreign data more than own |
| Long Parameters | INTRODUCE_PARAMETER_OBJECT | >3 parameters that travel together |
| Deep Nesting | GUARD_CLAUSES + EXTRACT_METHOD | >3 nesting levels |
| Type Branching | REPLACE_CONDITIONAL_WITH_POLYMORPHISM | Switch/if-else on type codes |
| Mixed Hook | EXTRACT_HOOK + EXTRACT_SERVICE | Hook >200 lines with unrelated state |
| Monolithic Service | EXTRACT_SERVICE + FACADE | Service >300 lines ignoring sub-services |

## Core Techniques

### EXTRACT_METHOD
**Steps:**
1. Identify code fragment that can be grouped
2. Create new method with intention-revealing name
3. Copy extracted code to new method
4. Replace original code with method call
5. Pass needed variables as parameters
6. Run tests

### EXTRACT_CLASS
**Steps:**
1. Identify subset of responsibilities to extract
2. Create new class with focused name
3. Move relevant fields and methods
4. Create interface if the class will have multiple consumers
5. Update original class to delegate to new class
6. Update consumers (if API changed)
7. Run tests

### EXTRACT_COMPONENT (React-specific)
**Steps:**
1. Identify self-contained UI section (has clear props boundary)
2. Create new component file
3. Define props interface with only needed data
4. Move JSX and related handlers
5. Import and use new component in parent
6. Run tests

### EXTRACT_HOOK (React-specific)
**Steps:**
1. Identify state + effects that form a cohesive unit
2. Create new hook file with `use` prefix
3. Move useState, useEffect, handlers, and derived state
4. Return only what the component needs (the public API)
5. Replace original code with hook call
6. Run tests

### EXTRACT_SERVICE
**Steps:**
1. Identify operations that form a cohesive service boundary
2. Define interface for the service contract
3. Create service class implementing the interface
4. Move methods and private helpers
5. Wire original class to delegate to new service
6. Update dependency injection / service provider
7. Run tests

### MOVE_METHOD
**Steps:**
1. Examine data the method uses — which class owns most of it?
2. Copy method to target class
3. Adjust for the new context (this/self references)
4. Replace original with delegation or remove it
5. Run tests

### INTRODUCE_PARAMETER_OBJECT
**Steps:**
1. Create a class/interface for the parameter group
2. Add the new parameter object to function signature
3. Update callers to construct the object
4. Remove old individual parameters
5. Move behavior into the parameter object if appropriate
6. Run tests

### GUARD_CLAUSES
**Steps:**
1. Identify the deepest nested path (the "happy path")
2. Invert conditions for early returns
3. Remove else branches where possible
4. Flatten the nesting structure
5. Run tests

### REPLACE_CONDITIONAL_WITH_POLYMORPHISM
**Steps:**
1. Create abstract base class/interface
2. Create subclass for each conditional branch
3. Move branch logic into corresponding subclass
4. Replace conditional with polymorphic dispatch
5. Run tests

## Service Extraction Pattern (from CLAUDE.md)

For monolithic services, follow this proven decomposition:

```
Monolithic Service (N lines)
  -> Extract shared types/interfaces
  -> Extract sub-service A (focused responsibility)
  -> Extract sub-service B (focused responsibility)
  -> Extract sub-service C (focused responsibility)
  -> Recompose: main service delegates to sub-services (~N/3 lines)
```

Each sub-service:
- Implements a focused interface
- Has a single clear responsibility
- Can be tested independently
- Can be mocked for testing the orchestrator

## Component Composition Pattern (from CLAUDE.md)

For god components:

```
God Component (N lines)
  -> Extract validation utils (pure functions)
  -> Extract types/interfaces (shared types)
  -> Extract sub-components (focused UI pieces)
  -> Extract custom hook (state + side effects)
  -> Recompose: thin orchestrator (~N/4 lines)
```

The orchestrator:
- Calls the hook for state
- Renders sub-components with props from hook
- Contains no business logic
- Is easy to read top-to-bottom

## Safety Checklist

### Before Each Technique
- [ ] Tests exist and pass for the code being refactored
- [ ] You understand the current behavior completely
- [ ] You've identified all consumers of the public API
- [ ] You're working on a dedicated branch

### During Each Technique
- [ ] One small change at a time
- [ ] Run tests after each change
- [ ] Preserve behavior (no feature changes mixed in)
- [ ] Commit at each working state

### After Each Technique
- [ ] All tests pass
- [ ] No new smells introduced
- [ ] Public API preserved (or consumers updated)
- [ ] Type-check passes (`npx tsc --noEmit`)
- [ ] Lint passes (`npm run lint`)

## When NOT to Extract

Not every smell requires extraction:
- **60-line function with one responsibility**: Fine. Don't extract for length alone.
- **Data class**: Sometimes a DTO is just a DTO. Only move behavior if it reduces coupling.
- **Single-use abstraction**: Don't create interfaces for classes with exactly one implementation unless DIP requires it.
- **Rule of Three**: Don't extract on first duplication. Wait for the third occurrence.
