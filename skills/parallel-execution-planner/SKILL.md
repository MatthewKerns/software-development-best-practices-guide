---
name: parallel-execution-planner
description: Analyzes tasks to determine optimal parallel vs sequential execution strategy for agentic workflows. Use when planning multi-step implementations, coordinating multiple agents, or optimizing development time. Returns execution plan with time savings estimates and dependency analysis.
allowed-tools: [Read, Grep, Glob]
---

# Parallel Execution Planner

## Purpose

Helps developers and AI agents determine whether tasks should run in parallel or sequentially, maximizing time efficiency while preventing merge conflicts and dependency issues.

## When to Use This Skill

**Use this skill when:**
- Planning multi-step feature implementations
- Coordinating work across multiple agents or developers
- Analyzing whether tasks can run simultaneously
- Estimating time savings from parallelization
- Designing execution workflows for complex projects

**Examples:**
- "Should I implement frontend and backend in parallel?"
- "Can these 5 refactoring tasks run simultaneously?"
- "Analyze this implementation plan for parallelization opportunities"
- "What's the optimal execution order for these modules?"

## Decision Framework

### Always Parallel ✅

Tasks that are **safe to run simultaneously**:

**Independent Analysis:**
- Security analysis ∥ Performance analysis ∥ Code quality analysis
- Different documentation files (API docs ∥ User guide ∥ Architecture)
- Separate verification domains (Tests ∥ Coverage ∥ Benchmarks)

**Isolated Implementations:**
- Independent package builds (@package-a ∥ @package-b)
- Non-overlapping modules with finalized contracts
- Different test suites without shared state

**Reasons:** No data dependencies, different files, no merge conflicts

### Always Sequential ❌

Tasks that **must run in order**:

**Data Dependencies:**
- Database schema → Migration script → Integration tests
- Requirements analysis → Implementation planning
- API contract definition → Frontend + Backend implementation

**Same File Edits:**
- Feature implementation + Refactoring (same files = conflicts)
- Cross-cutting refactoring affecting all modules

**Coordinated Changes:**
- Shared type modifications across packages
- Breaking API changes with ripple effects
- Global pattern changes

**Reasons:** Output dependencies, merge conflicts, coordinated changes required

### Conditional Parallel ⚖️

Tasks that **require analysis**:

**Module Implementation** (if truly isolated):
- ✅ Parallel: Frontend ∥ Backend (if API contract finalized)
- ❌ Sequential: If contract still evolving

**Strategic Refactoring** (at checkpoints):
- ✅ Parallel: Refactor completed Module A ∥ Implement Module B
- ❌ Sequential: If Module A not stable yet

**Database + API** (if schema finalized):
- ✅ Parallel: DB Migration ∥ API Implementation
- ❌ Sequential: If schema changes expected

**Checklist for Conditional Tasks:**
- [ ] No data dependencies between tasks
- [ ] Different files will be modified (no merge conflicts)
- [ ] Not a cross-cutting concern (doesn't affect all modules)
- [ ] Modules are truly isolated (no hidden coupling)
- [ ] Contracts/interfaces are finalized (no breaking changes expected)
- [ ] Each task can be validated independently
- [ ] Convergence validation planned after parallel work

If **ALL** checks pass → Parallel safe. Otherwise → Sequential.

## Strategic Refactoring Pattern

### Checkpoint-Based Refactoring (30% time savings)

**Traditional Approach (Sequential):**
```
Day 1-2: Implement Module A
Day 3-4: Implement Module B
Day 5-6: Implement Module C
Day 7-8: Refactor everything (accumulated debt)
Total: 8 days
```

**Optimized Approach (Parallel at Checkpoints):**
```
Day 1-2: Implement Module A (complete & stable)
  ↓ CHECKPOINT
Day 3-4: Parallel Execution
  ┌────────────────────┬────────────────────┐
  │ Refactor Module A  │ Implement Module B │
  │ - Extract patterns │ - Use patterns     │
  └────────────────────┴────────────────────┘
  ↓ CHECKPOINT
Day 5-6: Parallel Execution
  ┌────────────────────┬────────────────────┐
  │ Refactor Module B  │ Implement Module C │
  │ - Optimize         │ - Benefit from opt │
  └────────────────────┴────────────────────┘
Total: 6 days (25% time savings, zero technical debt)
```

**Checkpoint Criteria:**
- All tests passing for completed module
- No known bugs or technical debt
- Clear patterns identified for extraction
- Next module is independent enough for parallel work

## Optimal Context Window for Refactoring

**Sweet Spot: 60-120K context usage**

```
0K -------- 60K -------- 120K -------- 180K -------- 200K
│  Too Early │  OPTIMAL   │  Acceptable  │  Too Late   │
```

**Why this works:**
- **60K+**: Enough patterns loaded for DRY recognition
- **120K max**: 80K+ headroom prevents context overflow
- **Efficiency**: Completes before auto-compacting at 200K

**Timing Indicators:**
✅ **Good**: 2-3 modules implemented, duplicated patterns visible
❌ **Bad**: Only 1 module (no patterns), >150K context (risky)

## Hybrid Execution Pattern

**Complete Workflow Template:**
```
SEQUENTIAL: Planning Phase
  requirements-analyzer → geist-analyzer → implementation-planner

PARALLEL: Analysis Phase
  ├─ security-validator (auth, input validation)
  ├─ codebase-analyzer (DRY compliance, patterns)
  └─ test-planner (TDD strategy, coverage)

HYBRID: Implementation Phase
  Sequential Core: code-implementor → integration-tester
  ↓ CHECKPOINT
  Strategic Parallel: refactor Module A ∥ implement Module B

PARALLEL: Verification Phase
  ├─ gap-analyzer (completeness, error handling)
  ├─ documentation-updater (API, user, architecture)
  ├─ performance-validator (benchmarks, regression)
  └─ traceability-mapper (requirements → features)
```

## Output Format

When analyzing a task list, provide:

### 1. Execution Strategy
```
PHASE 1: [Sequential/Parallel/Hybrid]
  Task A [Duration]
  Task B [Duration]
  Time: [Total time]

PHASE 2: [Sequential/Parallel/Hybrid]
  ├─ Task C ∥ Task D [Duration each]
  Time: [Max of parallel tasks]

Total Time: [Sum of phase times]
Time Savings: [% reduction vs sequential]
```

### 2. Dependency Analysis
- List data dependencies (A → B means B needs A's output)
- Identify file conflicts (same file edits)
- Note cross-cutting concerns

### 3. Risk Assessment
- **Low Risk**: Independent tasks, different files
- **Medium Risk**: Requires validation, conditional parallel
- **High Risk**: Sequential required, dependencies present

### 4. Checkpoint Recommendations
- When to refactor (context window, patterns visible)
- Validation gates between phases
- Convergence testing requirements

## Examples

### Example 1: New Feature Implementation

**Input:**
```
Tasks:
1. Design API contract
2. Implement backend endpoints
3. Implement frontend UI
4. Write integration tests
5. Update documentation
```

**Output:**
```
EXECUTION STRATEGY:

PHASE 1: Sequential (Design)
  1. Design API contract [4h]
  Time: 4 hours

PHASE 2: Parallel (Implementation)
  ├─ 2. Implement backend endpoints [16h]
  └─ 3. Implement frontend UI [16h]
  Time: 16 hours (not 32h!)

PHASE 3: Sequential (Testing)
  4. Write integration tests [8h]
  Time: 8 hours

PHASE 4: Parallel (Documentation)
  ├─ 5. Update API docs [4h]
  └─ 5. Update user guide [4h]
  Time: 4 hours

TOTAL: 32 hours (vs 48h sequential = 33% savings)

DEPENDENCIES:
  - API contract → Backend + Frontend (finalized first)
  - Backend + Frontend → Integration tests (need both complete)

RISKS: Low - Clear boundaries, finalized contract
```

### Example 2: Refactoring Project

**Input:**
```
Tasks:
1. Refactor authentication module
2. Refactor user profile module
3. Refactor admin features
4. Extract common utilities
5. Update all imports
```

**Output:**
```
EXECUTION STRATEGY:

PHASE 1: Sequential (Refactor Auth)
  1. Refactor authentication module [8h]
  Time: 8 hours
  → CHECKPOINT (stable, tests pass)

PHASE 2: Strategic Parallel
  ├─ 4a. Extract auth utilities [4h]
  └─ 2. Refactor user profile [8h]
  Time: 8 hours
  → CHECKPOINT

PHASE 3: Strategic Parallel
  ├─ 4b. Extract profile utilities [4h]
  └─ 3. Refactor admin features [8h]
  Time: 8 hours

PHASE 4: Sequential (Import Updates)
  5. Update all imports [4h]
  Time: 4 hours

TOTAL: 28 hours (vs 36h sequential = 22% savings)

DEPENDENCIES:
  - Auth → Utilities extraction (patterns identified)
  - Profile → Utilities extraction (patterns identified)
  - All refactoring → Import updates (last step)

RISKS: Medium - Cross-cutting import updates must be last

CHECKPOINT CRITERIA:
  ✅ All tests passing
  ✅ No technical debt
  ✅ Patterns clearly identified
  ✅ Next module independent
```

## References

- **[PARALLEL_EXECUTION_PATTERNS.md](../07-agentic-coding/optimization/PARALLEL_EXECUTION_PATTERNS.md)** - Comprehensive decision frameworks
- **[AGENTIC_CODING_OPTIMIZATION.md](../07-agentic-coding/optimization/AGENTIC_CODING_OPTIMIZATION.md)** - Context window management
- **[CONTEXT_WINDOW_OPTIMIZATION.md](../07-agentic-coding/optimization/CONTEXT_WINDOW_OPTIMIZATION.md)** - Optimal refactoring windows

## Success Metrics

**Time Efficiency:**
- 30-50% time reduction for parallelizable work
- 25-35% savings with strategic refactoring
- 60-75% savings for independent analysis tasks

**Quality Preservation:**
- Zero merge conflicts (proper isolation)
- Zero accumulated technical debt (checkpoint refactoring)
- All tests passing at checkpoints
