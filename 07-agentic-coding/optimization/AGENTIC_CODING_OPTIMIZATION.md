# Context Window & Time Efficiency Optimization Guide

**Purpose:** Maximize parallel execution while managing context window constraints for agentic coding workflows

**Author:** Software Development Best Practices
**Created:** 2025-10-19
**Version:** 1.0.0
**Status:** Active

---

## Core Optimization Principles

### 1. Context Window Management Strategy

**Agent Delegation Pattern:**
- Each sub-agent spawned = fresh, isolated context window
- Coordination agent maintains minimal orchestration context (~20K)
- Specialized agents focus on specific tasks with targeted context (15-80K each)

**Communication via Artifacts:**
- Sub-agents communicate through structured outputs (JSON/Markdown files)
- Use file references instead of copying large content
- Coordination agent aggregates without loading full context

**Context Budget Formula:**
```
Total Conversation Context = Coordination Agent + Σ(Sub-Agent Contexts)
Target: Stay under 200K per conversation turn
Strategy: Distribute across N specialized agents running in parallel
```

**Optimal Refactoring Timing (Context Window Sweet Spot):**

The best time to refactor is when the context window contains rich pattern recognition data but allows sufficient headroom for completion:

```
Context Window Zones for Refactoring:

|--------------|-----------------|---------------------|------------|
0K            60K              120K                 180K        200K
│   Too Early  │  OPTIMAL ZONE   │  Acceptable but      │  Too Late  │
│   (No        │  (Rich context  │  risky (limited      │  (Auto-    │
│   patterns)  │  + headroom)    │  headroom)           │  compact)  │
└──────────────┴─────────────────┴──────────────────────┴────────────┘

Optimal Refactoring Window: 60-120K context usage
• Rich enough: Sufficient code patterns loaded for recognition
• Safe enough: 80-140K headroom prevents context overflow
• Efficient: Refactoring completes before auto-compacting
```

**Why This Window Works:**

1. **Pattern Recognition (60K+ context)**:
   - Multiple modules loaded → can identify DRY violations
   - Repeated code patterns become visible
   - Cross-module dependencies clear
   - Utility extraction opportunities evident

2. **Completion Safety (120K max usage)**:
   - 80K+ headroom for refactoring work
   - Room for import updates and validation
   - Buffer for test execution
   - Prevents mid-refactor context loss

3. **Auto-Compacting Prevention**:
   - Refactoring generates significant new context (import updates, extractions, tests)
   - Starting at 120K+ risks hitting 200K limit mid-refactor
   - Auto-compacting during refactor = lost pattern context
   - Lost context = incomplete or incorrect refactoring

**Timing Indicators for Refactoring:**

✅ **Good time to refactor:**
- 2-3 modules implemented (pattern recognition possible)
- Context usage: 60-120K (safe headroom)
- Duplicated code patterns visible across modules
- Before implementing next major module

❌ **Bad time to refactor:**
- Only 1 module implemented (no patterns yet)
- Context usage >150K (risky, low headroom)
- Mid-implementation (incomplete module state)
- Just after major context-heavy operations

### 2. Time Efficiency via Strategic Parallelization

**Independent Tasks → Parallel Execution:**
- No data dependencies = run simultaneously
- Different files/modules = parallel safe
- Analysis/verification phases = inherently parallel

**Dependent Tasks → Sequential Execution:**
- Output from Task A required as input to Task B = sequential
- Same file modifications = sequential (prevent conflicts)
- Schema-dependent operations = sequential (maintain integrity)

**Hybrid Execution Pattern:**
```
Phase 1: Planning (Sequential)
  requirements-analyzer → geist-analyzer → implementation-planner

Phase 2: Analysis (Parallel)
  security-validator + codebase-analyzer + test-planner + performance-analyzer

Phase 3: Implementation (Strategic Hybrid)
  code-implementor (Module A) ∥ code-implementor (Module B)
  ↓ (after milestone)
  refactoring-specialist (consolidate A+B patterns) ∥ test-runner (Module A+B)

Phase 4: Verification (Parallel)
  gap-analyzer + documentation-updater + performance-validator + traceability-mapper
```

---

## Decision Matrix: Parallel vs Sequential Execution

| Task Type | Execution Mode | Reasoning | Context Impact | Strategic Notes |
|-----------|---------------|-----------|----------------|-----------------|
| **Requirements Analysis** | Parallel | Independent aspects (security, performance, functionality) | Each agent: 15-25K context | Run all analyzers simultaneously |
| **Code Implementation (Same Module)** | Sequential | Same files, state dependencies | Single agent: 30-60K context | One agent per module/component |
| **Code Implementation (Different Modules)** | Parallel | No file conflicts, isolated changes | Multiple agents: 30-60K each | Frontend ∥ Backend ∥ Database |
| **Refactoring (During Implementation)** | **Strategic Parallel** | After milestone completion, refactor completed modules while implementing new ones | Refactor agent: 40-60K, Implementor: 30-50K | **Key insight: Refactor Module A while implementing Module B** |
| **Refactoring (Cross-Cutting)** | Sequential | Interdependent changes across modules | Single agent: 60-80K context | DRY violations, pattern extraction |
| **Database Migrations** | Sequential | Schema dependencies, data integrity | Single agent: 30-50K context | Order matters for rollback |
| **Testing (Unit Tests)** | Parallel | Isolated test suites, no shared state | Multiple agents: 20-40K each | Run test suites simultaneously |
| **Testing (Integration Tests)** | Sequential | Shared database, workflow dependencies | Single agent: 30-50K context | State setup matters |
| **Documentation Updates** | Parallel | Different doc types (API, user, architecture) | Multiple agents: 25-35K each | No file conflicts |
| **Security Validation** | Parallel | Independent security checks (auth, input, rate limiting) | Security agent: 20-30K context | Run with other analysis |
| **Performance Validation** | Parallel | Independent benchmarks and profiling | Performance agent: 25-35K context | Run with verification phase |
| **Gap Analysis** | Parallel | Different gap types (requirements, tests, implementation) | Gap agent: 15-25K context | Run with verification phase |

---

## Strategic Refactoring During Implementation

### Pattern: Continuous Refactoring with Parallel Implementation

**Traditional Approach (Slower):**
```
Implement Module A (20 min)
  ↓
Implement Module B (20 min)
  ↓
Implement Module C (20 min)
  ↓
Refactor all modules for DRY (30 min)
  ↓
Total: 90 minutes
```

**Optimized Approach (Faster):**
```
Implement Module A (20 min)
  ↓
┌─────────────────────────┬─────────────────────────┐
│ Refactor Module A       │ Implement Module B      │
│ (extract patterns)      │ (new functionality)     │
│ 15 min                  │ 20 min                  │
└─────────────────────────┴─────────────────────────┘
  ↓ (refactoring complete, Module B done)
┌─────────────────────────┬─────────────────────────┐
│ Implement Module C      │ Test Modules A+B        │
│ (using refactored base) │ (integration tests)     │
│ 15 min (faster!)        │ 10 min                  │
└─────────────────────────┴─────────────────────────┘
  ↓
Final refactor Module C (10 min)
  ↓
Total: 60 minutes (33% faster)
```

### Pre-Emptive Import Management During Refactoring

**CRITICAL: Update imports proactively when refactoring to prevent broken references**

Refactoring often moves code between files. Pre-emptive import updates prevent cascading failures:

**The Problem:**
```python
# Old Structure (before refactor):
# auth.py
def validate_token(token):
    # implementation

def create_session(user):
    # implementation

# api.py
from auth import validate_token, create_session
```

**Reactive Approach (WRONG - causes failures):**
```python
# Step 1: Extract to utils (imports break immediately!)
# auth_utils.py
def validate_token(token):
    # implementation moved here

# auth.py (still has create_session)
def create_session(user):
    # implementation

# api.py - BROKEN! validate_token import fails
from auth import validate_token, create_session  # ❌ validate_token no longer here
```

**Pre-Emptive Approach (CORRECT - maintains functionality):**
```python
# Step 1: Create new file with extracted code
# auth_utils.py
def validate_token(token):
    # implementation moved here

# Step 2: IMMEDIATELY update all imports before removing old code
# api.py - Updated imports first
from auth_utils import validate_token  # ✅ Updated proactively
from auth import create_session

# Step 3: NOW safe to remove from old location
# auth.py (cleaned up)
def create_session(user):
    # implementation
```

**Pre-Emptive Import Update Workflow:**

1. **Before Extraction:**
   - Search entire codebase for all imports of target code
   - Document every file that imports the code being moved
   - Plan import updates for each affected file

2. **During Extraction:**
   - Create new file with extracted code
   - **IMMEDIATELY update all imports** in consuming files
   - Verify imports resolve correctly (IDE checks, type checking)

3. **After Extraction:**
   - Remove code from old location
   - Run tests to validate no broken references
   - Commit atomically (extraction + import updates together)

**Automated Import Search Pattern:**

```bash
# Before refactoring utils.py → extract to validators.py
# Search for all imports of code being moved:

grep -r "from utils import.*validate" .
grep -r "from utils import \*" .
grep -r "import utils" .

# Document results:
# - api/routes.py: from utils import validate_email, validate_phone
# - services/user.py: from utils import validate_email
# - tests/test_api.py: from utils import validate_email, validate_phone

# Update ALL these files BEFORE removing validate_* from utils.py
```

**Import Update Checklist:**

- [ ] Search codebase for all imports of code being refactored
- [ ] Create list of files requiring import updates
- [ ] Create new file/location with extracted code
- [ ] Update imports in ALL consuming files (not just obvious ones)
- [ ] Verify imports resolve (IDE, linter, type checker)
- [ ] Run tests to confirm no import errors
- [ ] Remove code from old location only after imports updated
- [ ] Commit extraction + import updates atomically

**Anti-Pattern: Reactive Import Updates**

❌ **Don't:**
```
1. Extract code to new location
2. Remove from old location
3. See what breaks
4. Fix imports one by one as errors appear
```

This causes:
- Cascading test failures
- CI/CD pipeline failures
- Wasted context on error debugging
- Potential missed imports in untested code paths

✅ **Do:**
```
1. Search for all imports of target code
2. Create new location with extracted code
3. Update ALL imports pre-emptively
4. Verify imports resolve
5. Remove from old location
6. Tests pass on first run
```

**Context Window Benefit:**

Pre-emptive import updates prevent context waste:
- No context spent on "why are tests failing?"
- No context spent debugging import errors
- No context spent finding missed imports
- Refactoring completes in single pass without back-and-forth

### Strategic Refactoring Points (When to Parallelize)

**✅ Safe to Parallel:**
1. **After Module Completion:** Refactor completed Module A while implementing Module B
2. **Different Codebases:** Refactor frontend while implementing backend
3. **Pattern Extraction:** Extract utilities from Module A while building Module B
4. **Test Refactoring:** Refactor test utilities while implementing new features
5. **Documentation Refactoring:** Update docs for Module A while coding Module B
6. **Pre-emptive Import Updates:** Update all imports before removing old code (prevents breakage)

**❌ Must Be Sequential:**
1. **Cross-Module Dependencies:** Refactoring shared utilities that Module B depends on
2. **API Contract Changes:** Refactoring interfaces that affect multiple modules
3. **Architecture Shifts:** Moving from pattern X to pattern Y across codebase
4. **Breaking Changes:** Refactoring that requires coordinated updates everywhere
5. **Import Updates:** Must complete before removing old code (prevents cascading failures)

### Implementation Pattern: Strategic Refactoring Workflow

```python
# Coordination meta-agent orchestrates strategic refactoring with pre-emptive import updates

async def strategic_refactoring_workflow():
    # Phase 1: Implement first module
    module_a_result = await spawn_agent('code-implementor', {
        'module': 'authentication',
        'features': ['login', 'logout', 'session_management']
    })

    # Context check before refactoring
    context_usage = estimate_context_usage()
    if context_usage > 120_000:  # >120K = risky for refactoring
        raise ContextWindowError("Context too full for safe refactoring. Spawn new agent.")

    # Phase 2: PARALLEL - Refactor Module A + Implement Module B
    # Context usage: ~60-90K (safe zone for refactoring)
    refactor_task, implement_task = await asyncio.gather(
        spawn_agent('refactoring-specialist', {
            'scope': 'authentication_module',
            'target': 'extract_common_patterns',
            'outputs': ['auth_utils.py', 'session_manager.py'],
            # CRITICAL: Pre-emptive import management
            'pre_refactor_steps': [
                'search_all_imports',  # Find all files importing auth code
                'document_import_locations',  # List files to update
                'plan_import_updates'  # Plan new import statements
            ],
            'refactor_steps': [
                'create_new_files',  # auth_utils.py, session_manager.py
                'update_all_imports_first',  # Update imports BEFORE removing code
                'verify_imports_resolve',  # Check IDE/linter confirms imports work
                'remove_old_code',  # Only after imports updated
                'run_tests'  # Validate no import errors
            ]
        }),
        spawn_agent('code-implementor', {
            'module': 'authorization',
            'features': ['permissions', 'roles', 'access_control'],
            'dependencies': ['authentication']  # Uses completed auth module
        })
    )

    # Phase 3: PARALLEL - Test refactored code + Implement Module C
    test_task, implement_c_task = await asyncio.gather(
        spawn_agent('integration-tester', {
            'modules': ['authentication', 'authorization'],
            'test_refactored_patterns': True,
            'verify_imports': True  # Ensure all imports resolved correctly
        }),
        spawn_agent('code-implementor', {
            'module': 'audit_logging',
            'reuse_patterns': refactor_task.extracted_patterns  # Benefits from refactoring!
        })
    )

    # Phase 4: Final cross-cutting refactoring (SEQUENTIAL - affects all modules)
    # IMPORTANT: Pre-emptive import search critical for cross-cutting changes
    final_refactor = await spawn_agent('refactoring-specialist', {
        'scope': 'all_modules',
        'target': 'consolidate_error_handling',
        'modules': ['authentication', 'authorization', 'audit_logging'],
        'pre_refactor_steps': [
            'grep -r "from .* import.*Error" .',  # Find all error imports
            'grep -r "import.*exceptions" .',  # Find exception imports
            'document_all_error_usages'  # Map where errors are used
        ],
        'import_update_strategy': 'pre_emptive',  # Update before removing
        'atomic_commit': True  # Extraction + imports in one commit
    })

    return {
        'time_saved': '30%',
        'pattern': 'strategic_parallel_refactoring_with_import_safety',
        'modules_affected': ['auth', 'authz', 'audit'],
        'import_errors': 0,  # Pre-emptive updates prevent import failures
        'context_efficiency': 'high'  # No context wasted on debugging imports
    }
```

### Refactoring Coordination Rules

**Rule 1: Module Isolation**
- If Module A is complete and Module B doesn't depend on refactored parts → PARALLEL
- If Module B uses Module A's interfaces → SEQUENTIAL (refactor A first)

**Rule 2: Scope Analysis**
- Local refactoring (within one module) → PARALLEL with other module work
- Global refactoring (cross-cutting concerns) → SEQUENTIAL (all modules affected)

**Rule 3: Context Window Timing**
- **60-120K context usage**: OPTIMAL for refactoring (pattern recognition + headroom)
- **<60K context usage**: Too early (insufficient patterns visible)
- **>120K context usage**: Too risky (spawn new agent or delegate to specialized agent)

**Rule 4: Pre-Emptive Import Management**
- **Before extraction**: Search all imports of code being moved
- **During extraction**: Update imports BEFORE removing old code
- **After extraction**: Verify imports + run tests
- **Never**: Remove code first, fix imports reactively

**Rule 5: Milestone-Based Refactoring**
```
Milestone 1: Core features implemented (Context: ~70K)
  ↓
Refactor Agent (extract patterns + update imports) ∥ Implement Agent (additional features)
  ↓
Milestone 2: Advanced features implemented (Context: ~90K)
  ↓
Refactor Agent (consolidate patterns + update imports) ∥ Test Agent (comprehensive testing)
  ↓
Milestone 3: All features complete (Context: ~110K)
  ↓
Final Refactor (cross-cutting, sequential, pre-emptive import updates)
```

---

## Context Window Optimization Patterns

### Pattern A: Parallel Analysis, Sequential Implementation, Strategic Refactoring

```
User Request: "Build user management system with auth, roles, and audit"
↓
Spawn 4 parallel analyzers (Context Budget: 4 × 25K = 100K distributed):
  • requirements-analyzer (Context A: 20K - requirements docs)
  • security-validator (Context B: 30K - OWASP patterns, auth best practices)
  • performance-validator (Context C: 25K - user scale benchmarks)
  • codebase-analyzer (Context D: 25K - existing user-related code)
↓
Coordination agent aggregates (Context: 20K - synthesis only)
↓
STRATEGIC IMPLEMENTATION (Hybrid Parallel/Sequential):
┌─────────────────────────────────────┬─────────────────────────────────────┐
│ Implementation Agent 1              │ Implementation Agent 2              │
│ Module: Authentication              │ Module: Database Schema             │
│ Context: 40K (auth patterns + code) │ Context: 35K (schema + migrations)  │
│ Duration: 20 minutes                │ Duration: 20 minutes                │
└─────────────────────────────────────┴─────────────────────────────────────┘
↓ (Auth & DB complete - milestone reached)
┌─────────────────────────────────────┬─────────────────────────────────────┐
│ Refactoring Agent                   │ Implementation Agent 3              │
│ Refactor: Extract auth utilities    │ Module: Authorization (roles)       │
│ Context: 45K (auth code + patterns) │ Context: 40K (uses auth module)     │
│ Duration: 15 minutes                │ Duration: 18 minutes                │
└─────────────────────────────────────┴─────────────────────────────────────┘
↓ (Refactoring done, Authz complete)
┌─────────────────────────────────────┬─────────────────────────────────────┐
│ Implementation Agent 4              │ Testing Agent                       │
│ Module: Audit logging               │ Test: Auth + Authz integration      │
│ Context: 35K (reuses refactored!)   │ Context: 30K (test suites)          │
│ Duration: 12 min (faster via reuse) │ Duration: 10 minutes                │
└─────────────────────────────────────┴─────────────────────────────────────┘
↓
Spawn 4 parallel verifiers (Context Budget: 4 × 25K = 100K distributed):
  • gap-analyzer (Context E: 20K - requirements vs implementation)
  • documentation-updater (Context F: 30K - API docs + user guides)
  • performance-validator (Context G: 25K - load testing results)
  • security-validator (Context H: 25K - final security audit)
```

**Benefits:**
- Total context distributed: ~420K across all agents (vs 200K limit in single agent)
- Time saved: ~30% through strategic parallelization
- Code quality: Continuous refactoring prevents technical debt accumulation

### Pattern B: Task-Specific Agent Spawning with Refactoring Opportunities

```
Traditional Single-Agent Approach:
  One agent: Load entire codebase (180K) + new requirements (20K) = 200K
  Time: 60 minutes sequential work
  Risk: Context overflow, no parallelization

Optimized Multi-Agent Approach:
  Coordination agent: 15K (orchestration)

  Analysis Phase (PARALLEL - 10 min):
    • Agent 1: Requirements (15K context)
    • Agent 2: Security patterns (20K context)
    • Agent 3: Existing code analysis (40K context)

  Implementation Phase (STRATEGIC HYBRID - 30 min):
    • Agent 4: Implement Feature A (30K context) - 15 min
    • Agent 5 (parallel): Implement Feature B (30K context) - 15 min
    • Agent 6 (after A done): Refactor Feature A (35K context) - 10 min
      ∥ parallel with Agent 7: Test Feature B (25K context) - 10 min

  Verification Phase (PARALLEL - 10 min):
    • Agent 8: Documentation (25K context)
    • Agent 9: Final testing (30K context)
    • Agent 10: Gap analysis (20K context)

Total Time: 50 minutes (17% faster)
Total Context: ~285K distributed (no single agent overflow)
```

### Pattern C: Incremental Context Loading with Refactoring Checkpoints

```
For Large Codebases (>500 files):

Don't: Load entire codebase into one agent (context overflow)

Do: Incremental module-by-module with refactoring checkpoints

┌─────────────────────────────────────────────────────────────────┐
│ Coordination Agent (20K context - orchestration only)           │
└─────────────────────────────────────────────────────────────────┘
            ↓
┌─────────────────────────┬─────────────────────────┬────────────┐
│ Module A Analyzer       │ Module B Analyzer       │ Module C   │
│ (35K - auth code only)  │ (30K - API code only)   │ Analyzer   │
│                         │                         │ (25K)      │
└─────────────────────────┴─────────────────────────┴────────────┘
            ↓
┌──────────────────────────────────────────────────────────────────┐
│ Coordination Agent: Identify cross-module patterns (25K context) │
└──────────────────────────────────────────────────────────────────┘
            ↓
CHECKPOINT 1: Implement Modules A & B
┌─────────────────────────┬─────────────────────────────────────────┐
│ Implement Module A      │ Implement Module B                      │
│ (40K - focused context) │ (35K - focused context)                 │
└─────────────────────────┴─────────────────────────────────────────┘
            ↓
CHECKPOINT 2: Refactor A+B patterns while implementing C
┌─────────────────────────┬─────────────────────────────────────────┐
│ Refactor A+B            │ Implement Module C                      │
│ Extract shared utils    │ (30K - benefits from refactored base)   │
│ (50K - A+B patterns)    │                                         │
└─────────────────────────┴─────────────────────────────────────────┘
            ↓
CHECKPOINT 3: Parallel verification
┌──────────────┬──────────────┬──────────────┬──────────────────────┐
│ Test A+B+C   │ Update Docs  │ Security     │ Performance          │
│ (30K)        │ (25K)        │ Audit (20K)  │ Validation (25K)     │
└──────────────┴──────────────┴──────────────┴──────────────────────┘

Benefits:
• No single agent exceeds 50K context
• Continuous refactoring prevents technical debt
• Parallel execution at analysis and verification phases
• Strategic parallel refactoring during implementation
```

---

## Practical Execution Guidelines

### When to Use Parallel Execution

✅ **Independent Analysis Tasks:**
- Requirements analysis (security, performance, functionality)
- Different domains have no data dependencies
- Each analyzer produces independent recommendations

✅ **Non-Overlapping File Modifications:**
- Frontend team files + Backend team files (no conflicts)
- Module A implementation + Module B implementation (isolated)
- Test file updates + Documentation updates (different files)

✅ **Strategic Refactoring Opportunities:**
- **Refactor completed Module A while implementing Module B**
- Extract patterns from finished code while building new features
- Test refactoring (test utilities) while implementing features
- Documentation refactoring while coding continues

✅ **Verification & Validation:**
- Test execution (unit tests across modules)
- Documentation generation (API, user, architecture)
- Performance benchmarking (independent metrics)
- Security audits (different attack vectors)

### When to Use Sequential Execution

❌ **Same File Modifications:**
- Two agents editing the same source files = merge conflicts
- Database schema changes = order-dependent migrations

❌ **Data Dependencies:**
- Task B requires output/results from Task A
- Integration testing requires implementation completion
- Deployment steps have staged progression

❌ **Cross-Cutting Refactoring:**
- Changing API contracts across all modules
- Migrating from Pattern X to Pattern Y globally
- Updating shared utilities that all modules import

❌ **Stateful Operations:**
- Database migrations with schema dependencies
- Deployment with environment-specific configs
- Integration tests with shared database state

### When to Use Hybrid Execution (Strategic)

🔀 **Phase-Based Approach:**

**Phase 1: Planning (Sequential)**
```
requirements-analyzer
  ↓
geist-analyzer (analyzes requirements output)
  ↓
implementation-planner (creates plan from geist analysis)
```

**Phase 2: Analysis (Parallel)**
```
┌──────────────────────┬──────────────────────┬──────────────────────┐
│ security-validator   │ codebase-analyzer    │ performance-analyzer │
└──────────────────────┴──────────────────────┴──────────────────────┘
```

**Phase 3: Implementation (Strategic Hybrid)**
```
Implement Module A
  ↓
┌─────────────────────────┬─────────────────────────┐
│ Refactor Module A       │ Implement Module B      │
│ (extract patterns)      │ (new functionality)     │
└─────────────────────────┴─────────────────────────┘
  ↓
┌─────────────────────────┬─────────────────────────┐
│ Implement Module C      │ Test Modules A+B        │
│ (using refactored base) │ (integration tests)     │
└─────────────────────────┴─────────────────────────┘
```

**Phase 4: Verification (Parallel)**
```
┌──────────────┬──────────────┬──────────────┬──────────────────────┐
│ gap-analyzer │ docs-updater │ test-runner  │ performance-validator│
└──────────────┴──────────────┴──────────────┴──────────────────────┘
```

**Phase 5: Final Refactoring (Sequential if cross-cutting)**
```
refactoring-specialist
  ↓ (consolidate all patterns, DRY across modules)
Final validation
```

---

## Context Window Budgeting Examples

### Example 1: New Feature Implementation (Budget: 200K per turn)

**Option 1 - Single Agent (Inefficient):**
```
One agent does everything:
• Context usage: 180K (codebase + requirements + implementation)
• Time: 60 minutes (all sequential)
• Risk: Near context limit, no parallelization
```

**Option 2 - Multi-Agent Strategic (Efficient):**
```
Turn 1 - Analysis Phase (Parallel):
  Coordination agent: 15K
  + requirements-analyzer: 20K
  + security-validator: 25K
  + codebase-analyzer: 40K
  + performance-analyzer: 25K
  Total: 125K distributed | Time: 10 min

Turn 2 - Implementation Phase (Strategic Hybrid):
  Coordination agent: 15K
  + code-implementor Module A: 40K (12 min)

  Then parallel:
  + refactoring-specialist Module A: 45K (10 min)
  + code-implementor Module B: 35K (10 min)
  Total: 135K distributed | Time: 22 min

Turn 3 - Verification Phase (Parallel):
  Coordination agent: 15K
  + gap-analyzer: 20K
  + documentation-updater: 30K
  + test-runner: 35K
  + performance-validator: 25K
  Total: 125K distributed | Time: 12 min

Total Time: 44 minutes (27% faster)
Total Context: 385K across 3 turns, well-distributed
```

### Example 2: Large Codebase Refactoring (Budget: 200K per turn)

**Scenario:** Modernize authentication system across 50 files

**Traditional Approach:**
```
One agent loads all 50 files: 150K context
Risk: Context overflow, misses patterns, slow
Time: 90 minutes sequential refactoring
```

**Strategic Approach:**
```
Turn 1 - Module Analysis (Parallel):
  • Analyze auth module: 40K
  • Analyze session module: 35K
  • Analyze token module: 30K
  Total: 105K | Time: 15 min

Turn 2 - Strategic Refactoring (Hybrid):
  • Refactor auth module: 50K (20 min)
  Then parallel:
    • Refactor session module: 45K (15 min)
    • Test auth module: 30K (15 min)
  Total: 125K | Time: 35 min

Turn 3 - Integration (Sequential then Parallel):
  • Refactor shared utilities: 55K (20 min)
  Then parallel:
    • Integration testing: 40K (15 min)
    • Update documentation: 30K (15 min)
  Total: 125K | Time: 35 min

Turn 4 - Verification (Parallel):
  • Security audit: 25K
  • Performance testing: 30K
  • Gap analysis: 20K
  Total: 75K | Time: 12 min

Total Time: 97 minutes
Strategic refactoring: Refactored modules tested while other modules refactored
Context: Well-distributed, no overflow
```

---

## Anti-Patterns That Waste Context/Time

### ❌ Context Window Anti-Patterns

1. **Loading Entire Codebase:** Reading all files when only need specific modules
   - Fix: Use incremental loading, spawn agents per module

2. **No Agent Delegation:** One agent holds all context for entire workflow
   - Fix: Spawn specialized agents with focused context

3. **Copying Large Content:** Passing full file contents between agents
   - Fix: Use file paths and references

4. **Re-analyzing Same Code:** Multiple agents re-reading identical files
   - Fix: Cache analysis results, share via artifacts

5. **Monolithic Refactoring:** Refactor everything at the end sequentially
   - Fix: **Strategic refactoring during implementation at milestones**

### ❌ Time Efficiency Anti-Patterns

1. **Sequential Independent Tasks:** Running analysis tasks one-by-one
   - Fix: Parallelize all independent analysis

2. **No Strategic Refactoring:** Wait until end to refactor
   - Fix: **Refactor completed modules while implementing new ones**

3. **Blocking on Verification:** Wait for all tests before continuing
   - Fix: Run tests in parallel with documentation/other verification

4. **Single-Module Implementation:** Implement modules one at a time
   - Fix: Implement independent modules in parallel

5. **No Milestone Checkpoints:** Implement everything then refactor everything
   - Fix: **Checkpoint-based refactoring (refactor after each milestone)**

### ✅ Optimization Best Practices

1. **Context Distribution:**
   - Spawn N specialized agents vs 1 generalist
   - Each agent: 20-60K focused context
   - Coordination agent: <20K orchestration only

2. **Strategic Parallelization:**
   - Analysis: Always parallel (independent domains)
   - Implementation: Parallel modules, sequential within module
   - **Refactoring: Parallel with implementation when milestone-based**
   - Verification: Always parallel (independent checks)

3. **Artifact Communication:**
   - Agents write structured outputs (JSON/Markdown)
   - File paths instead of content copies
   - Coordination agent aggregates without full context

4. **Checkpoint-Based Refactoring:**
   - Milestone 1: Core features → Refactor patterns ∥ Implement advanced features
   - Milestone 2: Advanced features → Refactor patterns ∥ Test all features
   - Milestone 3: All features → Final cross-cutting refactor (sequential)

5. **Context Budgeting:**
   - Estimate context per agent before spawning
   - Stay under 200K per conversation turn
   - Distribute heavy context across multiple agents

6. **Continuous Refactoring:**
   - **Don't wait until the end** - refactor at strategic milestones
   - **Refactor completed work while implementing new work**
   - Prevents technical debt accumulation
   - Enables pattern reuse in later modules

---

## Quick Reference: Parallel vs Sequential Decision Tree

```
┌─────────────────────────────────────────────────────────────┐
│ Are the tasks modifying the SAME files?                    │
└─────────────────┬───────────────────────────────────────────┘
                  │
        ┌─────────┴─────────┐
        │                   │
       YES                 NO
        │                   │
        ↓                   ↓
   SEQUENTIAL      ┌────────────────────────────────────────┐
                   │ Does Task B require output from Task A?│
                   └────────┬───────────────────────────────┘
                            │
                  ┌─────────┴─────────┐
                  │                   │
                 YES                 NO
                  │                   │
                  ↓                   ↓
             SEQUENTIAL         ┌────────────────────────────┐
                                │ Is this cross-cutting      │
                                │ refactoring affecting all  │
                                │ modules?                   │
                                └────────┬───────────────────┘
                                         │
                               ┌─────────┴─────────┐
                               │                   │
                              YES                 NO
                               │                   │
                               ↓                   ↓
                          SEQUENTIAL         PARALLEL ✓
                                            (Strategic refactoring
                                             at milestones)
```

---

## Summary: Key Takeaways

1. **Context Window Optimization:**
   - Distribute context across specialized agents (15-60K each)
   - Coordination agent stays minimal (<20K)
   - Use file references, not content copies
   - Target: <200K per conversation turn
   - **Optimal refactoring window: 60-120K context** (pattern recognition + safe headroom)

2. **Time Efficiency Optimization:**
   - Parallelize: Analysis, verification, documentation, independent modules
   - Sequential: Same-file edits, data dependencies, cross-cutting refactoring
   - **Strategic Hybrid: Refactor completed modules while implementing new ones**

3. **Strategic Refactoring:**
   - **Milestone-based checkpoints** enable parallel refactoring
   - Refactor Module A while implementing Module B (if isolated)
   - **Optimal timing: 60-120K context usage** (rich patterns + completion headroom)
   - Prevents technical debt accumulation
   - Enables pattern reuse in subsequent modules
   - Cross-cutting refactoring stays sequential (affects all modules)
   - **Pre-emptive import updates ALWAYS** (update before removing code)

4. **Pre-Emptive Import Management:**
   - **Before refactoring**: Search entire codebase for all imports
   - **During refactoring**: Update ALL imports before removing old code
   - **After refactoring**: Verify imports + run tests
   - **Never**: Remove code first, fix imports reactively
   - **Benefit**: Zero import errors, no wasted context on debugging

5. **Context Window Timing for Refactoring:**
   - **Too Early (<60K)**: Insufficient pattern recognition
   - **Optimal (60-120K)**: Rich context + safe headroom
   - **Risky (>120K)**: Limited headroom, spawn new agent instead
   - **Too Late (>150K)**: High risk of auto-compacting mid-refactor

6. **Practical Guidelines:**
   - Always parallel: Analysis, verification, docs
   - **Strategic parallel: Refactoring at milestones during implementation**
   - Always sequential: Same files, data dependencies, cross-cutting changes
   - Budget context before spawning agents
   - **Check context usage before refactoring** (60-120K = green light)

5. **Anti-Pattern Avoidance:**
   - Don't: Monolithic refactoring at the end
   - Do: **Continuous refactoring at strategic milestones**
   - Don't: One agent with all context
   - Do: N specialized agents with focused context
   - Don't: Sequential independent tasks
   - Do: Maximize parallelization opportunities

---

**Next Steps:**
1. Update CLAUDE.md with strategic refactoring patterns
2. Add refactoring-specialist agent coordination rules
3. Document checkpoint-based refactoring workflow
4. Create examples of hybrid implementation + refactoring
