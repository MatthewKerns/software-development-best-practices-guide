# Claude Code Instructions - Data Input Pipeline

Python project with LangGraph/LangSmith for email processing and document analysis. Uses TDD, async patterns, and tool-based architecture.

**IMPORTANT CONTEXT: NO ACTIVE USERS**
- This system is in development with **ZERO active users**
- No backward compatibility required for migrations
- No gradual rollout or dual-mode support needed
- Direct replacement of legacy systems is acceptable
- Delete old code immediately after refactoring (DRY compliance)

## Development Environment

```bash
# Setup
python -m venv .venv && source .venv/bin/activate && pip install -e .[dev]

# Start server
langgraph dev

# Run tests
pytest -m "unit or integration" -q --cov=src --cov-fail-under=90
```

### Chrome DevTools MCP Integration

**Status**: ✅ Installed and Connected

Chrome DevTools MCP server enables AI assistants to debug web applications through live Chrome browser control.

**Quick Commands:**
```bash
# Verify MCP status
claude mcp list

# Add/remove MCP server
claude mcp add chrome-devtools npx chrome-devtools-mcp@latest
claude mcp remove chrome-devtools
```

**Key Capabilities:**
- Browser automation with Puppeteer
- Performance trace recording and analysis
- Network request inspection
- Console error debugging
- Screenshot capture for visual validation
- DOM inspection and manipulation

**Documentation**: See `docs/CHROME_DEVTOOLS_MCP_GUIDE.md` for complete guide

## Architecture Patterns

### LangGraph Tool Pattern (MANDATORY)
All external API integrations use LangGraph tool pattern, NOT dependency injection.

```python
@tool("api_operation")
async def api_operation_tool(param1: str, param2: str) -> dict:
    try:
        service = ExternalAPIService()
        result = await asyncio.to_thread(service.blocking_operation, param1, param2)
        return {"status": "success", "data": result}
    except Exception as e:
        return {"status": "error", "error": str(e)}
```

### DRY Compliance & Clean Code (MANDATORY)
- Search existing functionality before writing new code
- Use inheritance/composition over duplication
- Extract common patterns to utilities
- **Delete old implementations** when refactoring
- **Remove competing patterns** - only keep latest approach
- **No backwards compatibility** - remove deprecated code immediately

### Pre-emptive Duplication Detection (MANDATORY)

**CRITICAL: Identify duplication risks BEFORE implementation to save implementation + refactoring work**

When planning features, check for duplication during design - not after implementation. This prevents costly refactoring cycles.

#### Real Example: Duplication from "Backward Compatibility" Without Users

**What Happened:**
- Implemented tool response with both `exit_code` and `return_code`
- Both contained identical values (e.g., 0)
- Added `return_code` for "backward compatibility" when **zero users existed**
- Required refactoring to remove duplication

**Cost:**
- Implementation time: Added duplicate field
- Refactoring time: Removed duplication
- Test update time: Changed assertions
- Documentation time: Updated docs twice

**What Should Have Happened:**
- Planning phase: Check utility function returns (`FeedbackFormatter.format_command_output()`)
- Discovery: Already returns `exit_code`
- Decision: Don't add `return_code`
- Implementation: Use only `exit_code`
- Result: Zero refactoring needed

#### Pre-Implementation Duplication Checklist

Before implementing any feature, verify:

✅ **Field/Property Overlap**
- [ ] Will this combine outputs from multiple utilities?
- [ ] Have you READ each utility's actual return schema? (Don't assume - verify)
- [ ] Are there fields with same/similar names or values?
- [ ] Example: `FeedbackFormatter` returns `exit_code`, don't also add `return_code`

✅ **Backward Compatibility Reality Check (Pre-Launch Projects)**
- [ ] Is this codebase published? (npm, PyPI, GitHub release, production deployment)
- [ ] Do external users exist who depend on current API?
- [ ] **If NO to both → Don't add compatibility layers**
- [ ] Rule: **"Best implementations should be only implementations"**
- [ ] Context: **ZERO active users = ZERO backward compatibility needed**

✅ **Utility Function Inspection**
- [ ] Read the actual return value of utility functions BEFORE designing response schema
- [ ] Print/log utility outputs during planning to verify fields
- [ ] Don't duplicate what utilities already provide - extend only with new fields

✅ **Naming Consistency**
- [ ] Use consistent field names across entire codebase
- [ ] Check existing tools/utilities for naming patterns
- [ ] Example: Use `exit_code` everywhere, not `return_code` in some places and `exit_code` in others

#### Planning Phase Integration

**Phase 1: Design Review** (Before any code is written)
1. List all response fields the feature will return
2. Identify source of each field (utility output vs manual addition)
3. Read actual utility return schemas (don't assume)
4. Flag any field overlap or similar naming
5. Verify no backward compatibility for unpublished code

**Phase 2: Implementation Planning** (Creating task breakdown)
1. Document which utilities provide which fields
2. Verify no duplication between utility outputs and manual fields
3. Challenge every "just in case" or "for compatibility" field

**Phase 3: Pre-Commit Review** (Before committing code)
1. Test actual response structure with real utility outputs
2. Print response keys and verify no duplication
3. Check for fields with identical or highly similar values

#### Common Duplication Anti-Patterns

**Anti-Pattern 1: "Just In Case" Fields**
```python
# ❌ WRONG - Adding fields "just in case"
return {
    "exit_code": 0,
    "return_code": 0,      # "Just in case someone needs it"
    "status_code": 0,      # "For compatibility"
    "exitcode": 0          # "Alternative naming"
}

# ✅ CORRECT - Single, well-named field
return {
    "exit_code": 0         # Clear, consistent, DRY compliant
}
```

**Anti-Pattern 2: Utility Wrap-and-Duplicate**
```python
# ❌ WRONG - Re-adding fields already in utility output
formatted = FeedbackFormatter.format_command_output(cmd, stdout, stderr, exit_code)
return {
    **formatted,           # Contains exit_code
    "return_code": exit_code  # Duplicates what's in formatted!
}

# ✅ CORRECT - Trust the utility, extend only with NEW fields
formatted = FeedbackFormatter.format_command_output(cmd, stdout, stderr, exit_code)
return {
    **formatted,           # Use what it provides (exit_code included)
    "execution_time": time.time() - start_time  # Add ONLY new fields
}
```

**Anti-Pattern 3: Premature Deprecation (Pre-Launch)**
```python
# ❌ WRONG - Deprecating before anyone uses it
return {
    "exit_code": 0,
    "return_code": 0       # "Deprecated, use exit_code"
}
# Problem: No users exist to deprecate for!

# ✅ CORRECT - Best naming from day one
return {
    "exit_code": 0         # Best implementation is only implementation
}
```

**Anti-Pattern 4: Backward Compatibility Without Users**
```python
# ❌ WRONG - Compatibility layer when zero users exist
# Context: Unpublished codebase, no external dependencies
return {
    "new_field": value,
    "old_field": value     # "Keep for backward compatibility"
}

# ✅ CORRECT - Direct replacement (no users to break)
return {
    "new_field": value     # Single source of truth
}
```

#### Detection Tools & Techniques

**During Planning:**
```python
# ALWAYS inspect utility outputs during design
result = FeedbackFormatter.format_command_output(...)
print("Utility returns:", list(result.keys()))
# Use this to design your response schema without duplication
```

**During Implementation:**
```python
# Test response structure before committing
response = await execute_tool(...)
print("Response keys:", list(response.keys()))

# Check for value duplication
from collections import defaultdict
value_to_keys = defaultdict(list)
for key, value in response.items():
    value_to_keys[value].append(key)

for value, keys in value_to_keys.items():
    if len(keys) > 1:
        print(f"WARNING: {keys} all have value {value}")
```

**Before Commit:**
```python
# In tests, verify no duplicate values across fields
def test_no_duplicate_fields():
    response = tool.execute()
    value_counts = {}
    for key, value in response.items():
        if value in value_counts:
            pytest.fail(f"Duplicate value {value}: {key} and {value_counts[value]}")
        value_counts[value] = key
```

#### Success Metrics

**Planning Phase:**
- ✅ Schema review completed before any code written
- ✅ All utility return values documented
- ✅ Zero field overlap identified in design

**Implementation Phase:**
- ✅ Response structure tested before commit
- ✅ No fields with duplicate values
- ✅ Consistent naming across all tools

**Post-Implementation:**
- ✅ Zero refactoring needed to remove duplication
- ✅ No "backward compatibility" for unpublished code
- ✅ Documentation accurate (no deprecated fields)

**See Also:** DRY Compliance (line 67), Geist Analysis for detecting Ghost (hidden duplication), codebase-analyzer sub-agent for DRY compliance checks

## Development Practices

### TDD Approach
- **Development TDD**: Real components + real dependencies for new features
- **Unit TDD**: Real component + mocked dependencies for behavior testing
- **Test-Driven Gap Resolution**: When tests uncover implementation gaps, document them systematically and create comprehensive resolution plans (see `docs/quality-through-testing/TEST_DRIVEN_GAP_RESOLUTION.md`)
- **Direct debugging**: Debug statements in production code for quick validation

**Gap Resolution Protocol (MANDATORY when tests reveal issues):**
1. Document discovered gaps with GAP-[ID] format in `docs/decision-history/gaps/`
2. Categorize by severity (Critical/High/Medium/Low)
3. Create gap resolution plan following template
4. Use TDD loop (RED-GREEN-REFACTOR) to close each gap
5. Validate all gaps resolved before proceeding

### Async Compliance
All LangGraph workflows must be fully async:
`result = await asyncio.to_thread(blocking_operation, args)`

### Debugging Best Practices
**Check for compatibility conflicts:**
- Import conflicts: Verify latest implementations
- Method signature mismatches
- Deprecated class usage
- Legacy file paths

**Error debugging checklist:**
1. Search for competing implementations
2. Verify imports point to current modules
3. Check method signatures match
4. Confirm latest service constructors
5. Look for old configuration patterns

### Code Quality & Testing Standards
- Comments explain WHY, not WHAT
- Type hints everywhere
- Black formatting (88 chars)
- Docstrings with business context

**Test markers:** `@pytest.mark.unit` (mocked deps), `@pytest.mark.integration` (real deps), `@pytest.mark.node` (LangGraph), `@pytest.mark.live` (external)

Coverage: Integration 85%+, Unit 90%+

## File Organization

- Production: `src/` only
- Development: `dev-tools/scripts/`
- Tests: `dev-tools/test-results/`
- Logs: `logs/`
- CI/CD: `cicd/`

## Quick Commands

```bash
# Fast debugging: python -c "import sys; sys.path.append('src'); from module import test; print(test())"
langgraph dev  # Test environment
pytest -m "unit or integration" -x -q --cov=src --cov-fail-under=90  # TDD loop
black . && ruff check . && mypy src/  # Quality
find . -name "*.py" -exec basename {} \; | sort | uniq -d  # Duplication
```


## Key References

Tool Pattern (`docs/adr/ADR_005_*`), TDD (`code_quality_practices/TDD_*`), Async (`construction_best_practices/ASYNC_*`), Integration (`construction_best_practices/INTEGRATION_*`), **DB Migrations** (`docs/DATABASE_MIGRATION_GUIDE.md`)

## Common Patterns

**Email Processing:** Gmail tools in `src/workflow/steps/step01_extract_emails/`
**Database Operations:** Four-component architecture: operations + connection managers
**Database Migrations (MANDATORY):** 1. Follow `docs/DATABASE_MIGRATION_GUIDE.md` 2. Numbered SQL in `migrations/` 3. Test on dev first 4. Python for complex 5. Validation queries + logging 6. Update docs
**Pattern:** `asyncio, asyncpg; conn = await asyncpg.connect(os.getenv("NEON_DATABASE_URL"))` + error handling
**Error Handling:** Structured errors with recovery strategies, no backwards compatibility
**Test-Driven Gap Resolution (MANDATORY when tests fail):** 1. Document gaps with GAP-[ID] in `docs/decision-history/gaps/` 2. Categorize by severity 3. Create resolution plan 4. TDD loop to close gaps 5. Validate all resolved. **Reference:** `docs/quality-through-testing/TEST_DRIVEN_GAP_RESOLUTION.md`

## Context Window & Time Efficiency Optimization

**MANDATORY: Optimize for both time efficiency and context window usage in all agentic workflows**

**Complete Guide:** `06-collaborative-construction/AGENTIC_CODING_OPTIMIZATION.md`

### Quick Reference

**Parallel Execution (Time + Context Optimization):**
- Independent analysis (security, performance, requirements)
- Different documentation types (API, user, architecture)
- Separate verification domains (tests, coverage, benchmarks)
- Non-overlapping modules (frontend + backend)
- **Strategic refactoring: Refactor completed Module A while implementing Module B**

**Sequential Execution (Prevent Conflicts):**
- Same file modifications (merge conflict prevention)
- Data dependencies (Task B needs Task A output)
- Cross-cutting refactoring (affects all modules)
- Database migrations (order-dependent)

**Strategic Refactoring Pattern:**
```
Implement Module A
  ↓
┌─────────────────────────┬─────────────────────────┐
│ Refactor Module A       │ Implement Module B      │
│ (extract patterns)      │ (new functionality)     │
└─────────────────────────┴─────────────────────────┘
  ↓
Module C benefits from refactored patterns (faster implementation)
```

**Context Budgeting:**
- Coordination agent: ~20K (orchestration)
- Specialized agents: 15-80K each (focused tasks)
- Target: <200K per conversation turn
- Strategy: Distribute across N parallel agents

## Business Requirements & Implementation Planning

### Business Requirements Document (BRD)

**MANDATORY: Create BRD before implementation planning for features >3 days effort**

**Purpose:** Define WHAT needs to be built and WHY (business value), not HOW (technical implementation)

**Template:** `08-project-management/BRD_TEMPLATE.md`
**Guidelines:** `08-project-management/BRD_CREATION_GUIDELINES.md`

**Required Sections:**
- Document Control (version, approvals, change history)
- Executive Summary (problem, solution, business value, success metrics)
- Business Context (background, strategic alignment, constraints)
- Stakeholder Analysis (RACI matrix)
- Scope Definition (in-scope, out-of-scope, assumptions, dependencies)
- Requirements Specification (functional + non-functional with acceptance criteria)
- Geist Analysis (Ghost/Geyser/Gist)
- Use Cases (personas, scenarios, user stories)
- Traceability Matrix (requirements → business objectives → test cases)
- Acceptance Criteria (measurable, testable)
- Risk Assessment (technical, business, mitigation)

**BRD Workflow:** Stakeholder interviews → Geist analysis → Requirements specification → Validation sessions → Formal approval → Implementation planning begins

**BRD vs Implementation Plan:**
- **BRD**: Business stakeholders, WHAT/WHY, before development
- **Implementation Plan**: Developers/architects, HOW, after BRD approval

### Implementation Plan Requirements

**MANDATORY: Use template for plans >4 hours (created AFTER BRD approval)**

**Templates:** `docs/MARKDOWN_PLAN_TEMPLATE.md` + guide

**Required Metadata:** Plan Type, Author, Created, Updated, Version, Issue, Priority, Effort, Dependencies, <65k chars

**MANDATORY Sections for ALL Plans:**
- 📋 Overview with business context (WHY not just WHAT) - reference BRD
- 🎯 Requirements & Acceptance Criteria (specific, measurable) - from BRD
- 🧪 Test-Driven Development Approach (reference TDD_WORKFLOW_GUIDE.md)
- 🏗️ Implementation Plan (phases with validation steps)
- 📊 Quality Assurance & Validation (complete checklist)
- Server Startup Validation section with test commands
- Implementation Gap Analysis (detect mock implementations)
- File Organization Requirements (cleanup checklist)

**Locations:** `docs/plans/`, `dev-tools/scripts/investigation/`, `docs/adr/`, `dev-tools/test-results/`
**Requirements:** 85%+ coverage, tests pass, server starts, no mocks, <65k chars
**Process:** Read BRD → Technical Geist analysis → Architecture design → TDD approach → Implementation plan → Review

**Integration:** BRD → Implementation Plan → TDD → Validation → UAT → Production

## Geist-Driven Development Framework

**MANDATORY: Use this philosophical framework for all implementation, debugging, and problem analysis**

### Three-Dimensional Problem Analysis

**1. Ghost Analysis (Parallel Reality)**
- Unknown unknowns and assumptions
- Context gaps in understanding

**2. Geyser Analysis (Dynamic Forces)**
- Explosive forces driving change
- Emergent properties under pressure

**3. Gist Analysis (Essential Core)**
- Irreducible essence of what we're building
- Core problem vs distractions

### Debug Protocol: Three Questions
1. **Ghost**: What parallel reality am I not seeing?
2. **Geyser**: What forces am I not accounting for?
3. **Gist**: Am I solving the essential problem?

### Implementation Requirements
- Document Ghost findings, plan for Geyser forces, preserve Gist essence
- Use framework for tasks, debugging, and architecture

**Reference**: Applies Kant's phenomena/noumena and Hegel's dialectical spirit for deeper understanding.

## Implementation Verification & Definition of Done

**MANDATORY Verification Phases:**
1. **Requirements:** Document with acceptance criteria, stakeholders, Geist analysis, traceability matrix
2. **Implementation:** Quality gates (tests, lint, typecheck), security checklist, system integration
3. **Testing:** ≥85% coverage, end-to-end workflows, performance validation, server startup
4. **Completion:** Replace placeholders, error handling, environment configs, database migrations
5. **Documentation:** Update all docs, architecture decisions, API docs, deployment procedures
6. **Alignment:** Requirements→features mapping, quality/performance/security validated, user acceptance

**Artifacts:** `docs/verification/[feature]-{traceability,test-results,completion,acceptance}.md`

**Failure Protocol:** Document gaps → remediation → fix → re-run → do NOT mark complete until ALL pass

## Coordination Meta-Agent Architecture

**MANDATORY: Use coordination meta-agent for complex implementations (3+ sub-agents)**

Central orchestrator managing parallel execution, conflict resolution, and quality validation.

**Core Responsibilities:**
1. Parallel execution orchestration
2. Dependency & conflict management
3. Quality gate enforcement
4. Commit coordination across workstreams
5. Production readiness validation

**Use For:**
- Complex implementations (3+ sub-agents)
- Cross-cutting concerns (security, performance, testing)
- Production deployments
- Large refactoring efforts
- Multi-service integrations

**Strategy:** Sequential Planning → Hybrid Implementation → Parallel Verification

**Execution Rules:**
- **Always Parallel**: Independent analysis, docs, validation
- **Never Parallel**: Shared state or file conflicts
- **Conditional**: Based on dependency analysis

**Workflow:** User Request → Coordination Meta-Agent → Sub-Agent Orchestration → Production

**Execution Flow:**
1. Analyze complexity & determine sub-agent requirements
2. Create parallel execution strategy with dependency mapping
3. Launch and monitor multiple sub-agents
4. Detect and resolve conflicts
5. Aggregate quality gates
6. Ensure deployment-ready deliverables

## Sub-Agent Architecture

**MANDATORY: Use specialized sub-agents for complex implementations**

### Core Sub-Agents (Standard Implementation Flow)

#### Phase 1: Requirements & Planning (Sequential)
`requirements-analyzer → geist-analyzer → plan-validator → implementation-planner`

1. **requirements-analyzer**: Extract requirements, acceptance criteria, deliverables, stakeholders
2. **geist-analyzer**: Apply Ghost/Geyser/Gist analysis, **drives Feature Gap Resolution Workflow convergence**
3. **plan-validator**: Validate against CLAUDE.md template, check <65,536 chars
4. **implementation-planner**: Create phased plan, quality gates, testing strategy

#### Phase 2: Implementation (Hybrid)
**Parallel:** security-validator + codebase-analyzer + test-planner
**Sequential:** code-implementor → integration-tester → quality-gate-validator

5. **security-validator** (Parallel): Auth patterns, input validation, rate limiting
6. **codebase-analyzer** (Parallel): DRY compliance, existing patterns, dependencies
7. **test-planner** (Parallel): TDD approach ≥85% coverage, integration/unit test plans
8. **code-implementor** (Sequential): Implement following conventions, no backwards compatibility
9. **integration-tester** (Sequential): Test system integration, workflows, migrations
10. **quality-gate-validator** (Sequential): Lint, typecheck, ≥85% coverage, server startup

#### Phase 3: Verification & Delivery (Parallel)
`gap-analyzer + documentation-updater + performance-validator + traceability-mapper`

11. **gap-analyzer**: Replace placeholders, verify complete implementation, validate error handling, **core component in Feature Gap Resolution Workflow**
12. **documentation-updater**: Update technical/API/user docs, architecture decisions
13. **performance-validator**: Performance requirements, regression testing, benchmarks
14. **traceability-mapper**: Requirements matrix, test summary, completion report

### Specialized Sub-Agents (Domain-Specific)

#### Specialized Sub-Agents

**Database & Infrastructure:**
- **database-migrator**: Schema changes, migration risk assessment, rollback planning (Sequential only)
- **root-cause-finder**: Exhaustive failure analysis, multi-angle investigation (Parallel safe)

**UI & Frontend Quality:**
- **ui-bar-raiser**: Comprehensive UI testing, WCAG compliance, auto-recovery with root-cause-finder (Parallel). **Uses Chrome DevTools MCP** for live browser debugging, performance tracing, and network inspection
- **ui-playwright-integration**: Browser automation, accessibility snapshots (Parallel). **Integrates with Chrome DevTools MCP** for enhanced debugging
- **ui-quality-enhancer**: Component analysis, design system validation (Parallel)

**Development & Code Quality:**
- **code-conciser**: Redundancy removal, expression simplification (Sequential only)
- **refactoring-specialist**: Large-scale refactoring, architecture improvements (Strategic parallel at milestones, Sequential for cross-cutting)
  - **Strategic Parallel Mode**: Refactor completed Module A while implementing Module B (milestone-based)
  - **Sequential Mode**: Cross-cutting refactoring affecting all modules, API contract changes
  - **Reference**: `06-collaborative-construction/AGENTIC_CODING_OPTIMIZATION.md` for strategic refactoring patterns
- **tdd-implementor**: Red-Green-Refactor workflow, 85%+ coverage, **test-driven gap resolution** (Conditional parallel)
  - **Gap Resolution Mode**: When tests uncover implementation issues, systematically documents gaps (GAP-[ID]), creates resolution plans, and uses TDD loop to close each gap
  - **Deliverables**: Gap documentation in `docs/decision-history/gaps/`, comprehensive resolution plan, all gaps resolved with passing tests
  - **Reference**: `docs/quality-through-testing/TEST_DRIVEN_GAP_RESOLUTION.md`

**Validation & Completeness:**
- **exactly-right**: Comprehensive implementation validation and bug prevention after development phases. **MANDATORY coordination with requirements-analyzer and gap-analyzer for complete validation coverage.** Works in unison to ensure zero-defect code through systematic requirement verification, gap analysis, and implementation auditing (Sequential after implementation, Parallel with analysis agents)

### Agent Selection Guide

#### Decision Tree for Agent Usage

**Standard Implementation (3+ sub-agents):**
```
User Request → requirements-analyzer → geist-analyzer → implementation-planner
             ↓
Security + Codebase + TDD Analysis (Parallel)
             ↓
code-implementor → integration-tester → quality-gate-validator
             ↓
Gap + Docs + Performance + Traceability (Parallel)
```

**Specialized Domain Requirements:**

**Database Changes:**
- Schema modifications → `database-migrator` (replaces code-implementor)
- Migration complexity assessment → Risk-based approach (LOW/MEDIUM/HIGH/CRITICAL)

**Frontend/UI Work:**
- After implementation → `ui-bar-raiser` + `ui-playwright-integration` (parallel)
- Component optimization → `ui-quality-enhancer` (during implementation)
- User experience validation → Full UI suite (all three agents)

**Problem Investigation:**
- Mysterious failures → `root-cause-finder` (immediate, any phase)
- System integration issues → `root-cause-finder` + `integration-tester`
- Performance problems → `root-cause-finder` + `performance-validator`

**Feature Completion:**
- Incomplete implementations → **Feature Gap Resolution Workflow** (`geist-analyzer` + `gap-analyzer` + `tdd-implementor` + `ui-bar-raiser`)
- Missing requirements → Start with `geist-analyzer` gap detection mode
- Iterative development → Loop until Gist confirms feature complete
- **Production readiness validation** → **Coordinated Validation** (`exactly-right` + `requirements-analyzer` + `gap-analyzer` in parallel)

**Code Quality Focus:**
- Verbose/complex code → `code-conciser` (after implementation)
- Large refactoring → `refactoring-specialist` (replaces code-implementor)
- Test-first development → `tdd-implementor` (replaces integration-tester)

#### Usage Patterns by Context

- **New Feature:** Standard flow + security-validator; Add UI agents for UI components; Use database-migrator for schema changes
- **Bug Investigation:** root-cause-finder (immediate) → standard flow + affected domain agents
- **Performance:** root-cause-finder + performance-validator (parallel) → refactoring-specialist/code-conciser → ui-bar-raiser
- **Database Schema:** requirements-analyzer → geist-analyzer → database-migrator → integration-tester → quality-gate-validator
- **UI/UX Enhancement:** Standard planning → ui-quality-enhancer → full UI suite (ui-bar-raiser + ui-playwright-integration)

### Parallel Execution Strategy

**Complete Guide:** `06-collaborative-construction/AGENTIC_CODING_OPTIMIZATION.md`

**Always Parallel:**
- Security+Codebase+Test planning (Phase 2)
- Gap+Docs+Performance+Traceability (Phase 3)
- UI testing suite
- Problem investigation
- **Strategic refactoring: Refactor completed modules while implementing new modules (milestone-based)**

**Never Parallel:**
- Sequential dependencies, shared state/file conflicts
- Database operations
- **Cross-cutting refactoring (affects all modules)**

**Conditional:**
- Frontend+Backend (no shared state)
- DB+API (finalized schemas)
- Tests+Docs (stable scope)
- **Module-based refactoring (refactor Module A while implementing Module B if isolated)**

### Sub-Agent Coordination

**Management:** Central orchestrator plans parallel execution, manages conflicts, quality gates
**Handoffs:** Specific deliverables → validation → next phase (coordination meta-agent validates transitions)
**Communication:** Structured artifacts (JSON/Markdown), no direct inter-agent comms
**Error Handling:** Sequential failures stop chain, parallel failures isolated, auto rollback for critical failures

### Sub-Agent Deliverables Summary

**Core Agents (Standard Flow):**
- **Planning:** requirements-analyzer, geist-analyzer, implementation-planner → draft commits
- **Implementation:** security-validator, codebase-analyzer, test-planner (parallel) → code-implementor → integration-tester → quality-gate-validator → feat/test/quality commits
- **Verification:** gap-analyzer, documentation-updater, performance-validator, traceability-mapper (parallel) → quality/docs/perf/release commits

**Specialized Agents:**
- **database-migrator:** Migration scripts + rollback → `feat: migration`
- **root-cause-finder:** Analysis + fix recommendations → `debug: root cause`
- **UI Suite:** ui-bar-raiser, ui-playwright-integration, ui-quality-enhancer → `test: UI validation`
- **Code Quality:** code-conciser, refactoring-specialist, tdd-implementor → `refactor:`/`feat:` commits

**Critical:** All deliverables must pass success criteria before proceeding to next phase.

### Agent Usage Examples

#### Example 1: Database Schema Addition
```
User: "Add a user_preferences table with notification settings"
↓
requirements-analyzer → geist-analyzer → implementation-planner
↓
security-validator + codebase-analyzer + test-planner (Parallel)
↓
database-migrator (replaces code-implementor)
• Risk assessment: MEDIUM (new table, no data loss)
• Migration script with rollback
• Validation queries
↓
integration-tester → quality-gate-validator
↓
Verification phase (Parallel)
```

#### Example 2: UI Component Enhancement
```
User: "Improve the dashboard user experience"
↓
requirements-analyzer → geist-analyzer → implementation-planner
↓
security-validator + codebase-analyzer + test-planner (Parallel)
↓
ui-quality-enhancer (during implementation)
• Component analysis and improvements
• Design system compliance
↓
code-implementor → integration-tester → quality-gate-validator
↓
ui-bar-raiser + ui-playwright-integration (Parallel verification)
• WCAG compliance testing
• Browser automation validation
• Performance benchmarks
```

#### Example 3: Production Issue Investigation
```
User: "The API is responding slowly and users are complaining"
↓
root-cause-finder (immediate, any phase)
• Database query analysis
• Network latency investigation
• Memory usage patterns
• Cascade effect analysis
↓
Based on findings:
• Database issues → database-migrator for indexing
• Code issues → refactoring-specialist
• Infrastructure → performance-validator
↓
Integration testing + verification phase
```

#### Example 4: Large Codebase Refactoring
```
User: "Modernize the authentication system architecture"
↓
requirements-analyzer → geist-analyzer → implementation-planner
↓
security-validator + codebase-analyzer + test-planner (Parallel)
↓
refactoring-specialist (replaces code-implementor)
• CLAUDE.md compliance transformation
• Security improvements
• Maintainability enhancements
↓
tdd-implementor (replaces integration-tester)
• Red-Green-Refactor workflow
• Comprehensive test coverage
↓
quality-gate-validator + security-validator (parallel verification)
```

#### Example 5: New Feature with Full UI Testing
```
User: "Implement real-time chat feature"
↓
Standard planning phase (requirements → geist → planner)
↓
security-validator + codebase-analyzer + test-planner (Parallel)
↓
tdd-implementor (test-driven implementation)
↓
Full UI verification suite (Parallel):
• ui-bar-raiser: Accessibility + performance
• ui-playwright-integration: User flow automation
• ui-quality-enhancer: Component optimization
• performance-validator: Real-time performance
↓
Gap analysis + Documentation + Traceability (Parallel)
```

#### Example 6: UI Bar Raiser with Automated Recovery Workflow
```
User: "Validate enhanced review page with automated issue resolution"
↓
ui-bar-raiser (initial validation)
• Navigate to page with Playwright
• Take screenshots and accessibility snapshot
• Detect errors/issues
↓
ERROR DETECTED → Automatic Recovery Loop:
↓
root-cause-finder (spawned automatically)
• Analyze console errors
• Check network failures
• Investigate DOM issues
• Review cascade effects
↓
code-implementor or refactoring-specialist (based on findings)
• Implement fixes from root cause analysis
↓
ui-bar-raiser (re-validation)
• Retry validation with Playwright
• Confirm fixes resolved issues
• Continue until all tests pass
↓
SUCCESS → quality-gate-validator
```

#### Example 7: Feature Gap Resolution Workflow
```
User: "Complete the user dashboard with all required metrics"
↓
geist-analyzer (gap detection mode)
• Ghost: Unknown data dependencies
• Geyser: Performance constraints
• Gist: 10 metrics essential, 5 missing
↓
gap-analyzer (enumerate specific gaps)
• Revenue metric missing
• User activity graph incomplete
• Export functionality absent
↓
LOOP START (Iteration 1-5):
↓
tdd-implementor (for each gap)
• RED: Write failing tests for metric
• GREEN: Implement metric calculation
• REFACTOR: Optimize queries
↓
ui-bar-raiser (validate display)
• Check metric rendering
• Validate responsive design
• Test interactivity
↓
gap-analyzer (re-evaluate)
• Confirm gap resolved
• Check for cascading gaps
↓
geist-analyzer (convergence check)
• Ghost: All dependencies discovered
• Geyser: Performance acceptable
• Gist: 9/10 metrics complete
↓
LOOP CONTINUES (Iteration 6):
↓
tdd-implementor → ui-bar-raiser → gap-analyzer
↓
geist-analyzer (final validation)
• Gist: 10/10 metrics complete ✓
↓
CONVERGENCE ACHIEVED → Feature Complete
```

#### Example 8: Coordinated Implementation Validation (exactly-right + requirements-analyzer + gap-analyzer)
```
User: "Validate critical invoice data flow end-to-end is production-ready"
↓
Parallel comprehensive analysis:
• requirements-analyzer: Extract acceptance criteria for critical data flow
• gap-analyzer: Identify specific missing/broken data pipeline elements
• exactly-right: Audit current implementation against production standards
↓
Coordinated validation loop:
• requirements-analyzer maps critical fields (invoice_total, materials_total, etc.)
• gap-analyzer identifies 5/8 critical fields missing from UI display layer
• exactly-right validates data extraction → storage → API → UI pipeline integrity
↓
Unified remediation plan:
• exactly-right provides specific fixes for broken API data access patterns
• gap-analyzer confirms each gap resolution against acceptance criteria
• requirements-analyzer validates final implementation meets all requirements
↓
Production readiness verification:
• exactly-right: Zero-defect validation across all critical paths
• gap-analyzer: All data flow gaps resolved
• requirements-analyzer: 100% acceptance criteria satisfied
↓
PRODUCTION READY → Feature Complete with Full Data Visibility
```

#### Example 9: Test-Driven Gap Resolution Workflow
```
User: "Run comprehensive tests and fix all discovered implementation gaps"
↓
test-runner (execute full test suite)
• 127 tests run
• 15 tests failing
• Gaps discovered in authentication, data validation, edge cases
↓
gap-analyzer (categorize failures)
• CRITICAL: 2 gaps (authentication bypass, data loss potential)
• HIGH: 5 gaps (incomplete validation, missing error handling)
• MEDIUM: 6 gaps (edge cases)
• LOW: 2 gaps (enhancements)
↓
Create Gap Resolution Plan:
• Document all 15 gaps with GAP-[ID] format
• Prioritize: Critical → High → Medium → Low
• Create resolution plan in docs/decision-history/gaps/
• Estimated effort: 12 hours
↓
tdd-implementor (gap resolution mode)
FOR EACH GAP (prioritized order):
  ↓
  RED: Verify test fails for documented reason
  • GAP-001: test_auth_bypass fails - no token validation
  ↓
  GREEN: Minimal implementation
  • Add token validation to auth middleware
  • Test now passes
  ↓
  REFACTOR: Clean up code
  • Extract validation logic to utility
  • Add comprehensive error messages
  ↓
  gap-analyzer: Verify gap closed
  • GAP-001 status: RESOLVED
  • No new gaps introduced
  • All related tests passing
  ↓
  NEXT GAP → Repeat cycle
↓
Final Validation:
• exactly-right: Zero-defect validation
• gap-analyzer: All 15 gaps RESOLVED
• quality-gate-validator: 127/127 tests passing, 89% coverage
↓
Gap Resolution Report:
• All critical gaps resolved (2/2)
• All high priority gaps resolved (5/5)
• All medium gaps resolved (6/6)
• Low priority gaps resolved (2/2)
• Total resolution time: 11.5 hours
• Documentation: Complete gap history preserved
↓
TESTING COMPLETE → All Gaps Resolved
```

## UI Bar Raiser Automated Recovery Workflow

**MANDATORY: UI validation agents automatically spawn recovery agents on error detection**

### Automated Recovery Loop Architecture

The ui-bar-raiser agent includes intelligent error detection and automatic recovery through agent spawning:

**1. Initial Validation Phase**
```
ui-bar-raiser → Playwright navigation → Screenshot/snapshot → Error detection
```

**2. Error Detection Triggers** (via Chrome DevTools MCP)
- Console errors (JavaScript exceptions, warnings)
- Network failures (404s, 500s, timeouts)
- Accessibility violations (WCAG A/AA/AAA)
- Performance degradation (Core Web Vitals below threshold)
- Visual regression (screenshot comparison failures)
- DOM issues (missing elements, broken selectors)

**3. Automatic Recovery Workflow**
```
ERROR DETECTED
↓
ui-bar-raiser logs error details + context
↓
Spawns root-cause-finder with error context
↓
root-cause-finder performs exhaustive analysis:
• Console error stack traces
• Network request/response analysis
• DOM state investigation
• Browser compatibility checks
• Environmental factors
• Cascade effect analysis
↓
Returns fix recommendations
↓
Based on root cause type:
• JavaScript errors → code-implementor
• Performance issues → refactoring-specialist
• Accessibility → ui-quality-enhancer
• Integration failures → integration-tester
↓
Fix implementation
↓
ui-bar-raiser re-validation (automatic retry)
↓
LOOP until success or max retries (3)
```

**4. Recovery Strategies by Error Type**

| Error Type | Detection Method | Recovery Agent | Fix Strategy |
|------------|-----------------|----------------|--------------|
| JavaScript Exception | Console monitoring | root-cause-finder → code-implementor | Fix code logic, add error handling |
| Network Failure | Request interception | root-cause-finder → integration-tester | Fix API endpoints, add retries |
| Accessibility Violation | WCAG scanning | ui-quality-enhancer | Fix semantic HTML, ARIA labels |
| Performance Degradation | Metrics monitoring | root-cause-finder → refactoring-specialist | Optimize code, reduce bundle size |
| Visual Regression | Screenshot diff | ui-quality-enhancer | Fix CSS, responsive design |
| Missing Elements | DOM queries | root-cause-finder → code-implementor | Fix component rendering |

**5. Implementation Pattern**

```python
# UI Bar Raiser with Auto-Recovery
async def ui_bar_raiser_with_recovery():
    max_retries = 3
    retry_count = 0

    while retry_count < max_retries:
        validation_result = await run_ui_validation()

        if validation_result.success:
            return validation_result

        # Auto-spawn root-cause-finder
        root_cause = await spawn_agent('root-cause-finder', {
            'error_context': validation_result.errors,
            'screenshots': validation_result.screenshots,
            'console_logs': validation_result.console,
            'network_logs': validation_result.network
        })

        # Spawn appropriate fix agent
        fix_agent = determine_fix_agent(root_cause.findings)
        fix_result = await spawn_agent(fix_agent, root_cause.recommendations)

        if fix_result.success:
            retry_count += 1
            continue  # Retry validation
        else:
            break  # Manual intervention needed

    return validation_result
```

**6. Success Criteria for Recovery**
- All console errors resolved
- All network requests successful
- WCAG compliance achieved
- Performance benchmarks met
- Visual regression tests pass
- All user flows functional

**7. Coordination with Meta-Agent**

When ui-bar-raiser is part of a larger workflow:
```
coordination-meta-agent
↓
ui-bar-raiser (with auto-recovery enabled)
↓
If error → Automatic spawn root-cause-finder
↓
Coordination agent tracks spawned sub-agents
↓
Aggregates results from all agents
↓
Ensures no conflicts between parallel fixes
```

**8. Commit Protocol for Recovery**

```bash
# After successful recovery
git commit -m "fix: auto-recovery resolved [issue-type] in UI validation
• Issue: [description]
• Root cause: [finding]
• Fix applied: [solution]
• Validation: All UI tests now passing
• Recovery time: [duration]

Auto-recovered by ui-bar-raiser + root-cause-finder
Co-Authored-By: Claude <noreply@anthropic.com>"
```

## Feature Gap Resolution Workflow

**MANDATORY: Use automated feature gap resolution for incomplete implementations requiring iterative development**

### Automated Feature Completion Architecture

The Feature Gap Resolution Workflow combines Geist analysis, TDD implementation, and UI validation in an intelligent loop that continues until all requirements are satisfied and features are complete.

**1. Initial Gap Analysis Phase**
```
geist-analyzer → Identify gaps between requirements and current state
↓
gap-analyzer → Enumerate specific missing features/functionality
↓
requirements-analyzer → Map gaps to acceptance criteria
```

**2. Gap Detection Triggers**
- Missing functionality (features not implemented)
- Partial implementations (incomplete features)
- UI/UX gaps (interface elements missing)
- Integration gaps (disconnected workflows)
- Test coverage gaps (untested scenarios)
- Performance gaps (requirements not met)

**3. Automated Resolution Loop**
```
FEATURE GAPS DETECTED
↓
geist-analyzer performs three-dimensional gap analysis:
• Ghost: Unknown requirements and hidden dependencies
• Geyser: Forces preventing completion (technical debt, blockers)
• Gist: Essential features vs nice-to-haves
↓
Prioritize gaps by criticality
↓
FOR EACH CRITICAL GAP:
  ↓
  tdd-implementor creates tests first:
  • Write failing tests for missing functionality
  • Define expected behavior
  • Create test fixtures
  ↓
  tdd-implementor implements to pass tests:
  • RED: Tests fail (gap confirmed)
  • GREEN: Implement minimal code to pass
  • REFACTOR: Optimize implementation
  ↓
  ui-bar-raiser validates UI/UX:
  • Visual validation with Playwright
  • User flow testing
  • Accessibility checks
  • Performance metrics
  ↓
  gap-analyzer re-evaluates:
  • Check if gap is resolved
  • Identify any new gaps introduced
  • Validate against acceptance criteria
  ↓
LOOP until geist-analyzer confirms:
• Ghost: No hidden gaps remain
• Geyser: All forces addressed
• Gist: Essential features complete
```

**4. Gap Resolution Strategies**

| Gap Type | Detection Method | Resolution Agents | Success Criteria |
|----------|-----------------|-------------------|------------------|
| Missing Feature | Requirements mapping | geist → tdd-implementor → ui-bar-raiser | Feature fully functional with tests |
| Partial Implementation | Code coverage analysis | gap-analyzer → tdd-implementor | 100% feature coverage |
| UI/UX Gap | Visual comparison | ui-bar-raiser → ui-quality-enhancer → tdd-implementor | UI matches requirements |
| Integration Gap | Workflow testing | integration-tester → tdd-implementor | End-to-end flows work |
| Test Coverage Gap | Coverage metrics | tdd-implementor → integration-tester | ≥85% coverage achieved |
| Performance Gap | Benchmark testing | performance-validator → refactoring-specialist → tdd-implementor | Benchmarks met |

**5. Implementation Pattern**

```python
# Feature Gap Resolution Loop
async def feature_gap_resolution_workflow():
    max_iterations = 10  # Prevent infinite loops
    iteration_count = 0

    while iteration_count < max_iterations:
        # Initial Geist analysis for gaps
        geist_analysis = await spawn_agent('geist-analyzer', {
            'mode': 'gap_detection',
            'requirements': requirements_doc,
            'current_state': implementation_state
        })

        if geist_analysis.gist_complete:
            # All essential features implemented
            return {
                'status': 'feature_complete',
                'iterations': iteration_count,
                'gaps_resolved': geist_analysis.resolved_gaps
            }

        # Identify and prioritize gaps
        gaps = await spawn_agent('gap-analyzer', {
            'geist_findings': geist_analysis,
            'acceptance_criteria': requirements_doc.criteria
        })

        for gap in gaps.critical_gaps:
            # TDD implementation for each gap
            tdd_result = await spawn_agent('tdd-implementor', {
                'gap_description': gap,
                'test_requirements': gap.test_scenarios,
                'coverage_target': 85
            })

            if tdd_result.tests_passing:
                # UI validation for visual gaps
                if gap.requires_ui_validation:
                    ui_result = await spawn_agent('ui-bar-raiser', {
                        'feature': gap.feature_name,
                        'auto_recovery': True,
                        'acceptance_criteria': gap.ui_requirements
                    })

                    if not ui_result.success:
                        # UI gap detected, enhance and retry
                        await spawn_agent('ui-quality-enhancer', {
                            'component': gap.component,
                            'issues': ui_result.issues
                        })

        iteration_count += 1

    # Max iterations reached, manual intervention needed
    return {
        'status': 'incomplete',
        'iterations': iteration_count,
        'remaining_gaps': gaps.unresolved
    }
```

**6. Convergence Criteria**

The workflow continues until ALL of the following are met:
- **Ghost Analysis**: No unknown requirements or hidden dependencies
- **Geyser Analysis**: All blocking forces resolved or mitigated
- **Gist Analysis**: Core essential features 100% complete
- **Gap Analysis**: Zero critical gaps remaining
- **Test Coverage**: ≥85% for all new implementations
- **UI Validation**: All user flows functional and accessible
- **Performance**: All benchmarks met or exceeded

**7. Coordination with Meta-Agent**

```
coordination-meta-agent
↓
Initialize Feature Gap Resolution Workflow
↓
Parallel initial analysis:
• geist-analyzer (gap detection mode)
• gap-analyzer (current state assessment)
• requirements-analyzer (acceptance criteria mapping)
↓
Sequential resolution loop:
• tdd-implementor → ui-bar-raiser → gap-analyzer
↓
Convergence check:
• geist-analyzer (final validation)
↓
If not converged → Continue loop
If converged → Feature complete
```

**8. Commit Protocol for Gap Resolution**

```bash
# After each gap resolution
git commit -m "feat: resolve [gap-type] gap in [feature-name]
• Gap identified: [description]
• Geist analysis: Ghost=[finding] Geyser=[force] Gist=[essence]
• Resolution: TDD implementation with [n] tests
• UI validation: [status]
• Coverage: [percentage]%
• Remaining gaps: [count]

Gap resolved by geist-analyzer + tdd-implementor + ui-bar-raiser
Co-Authored-By: Claude <noreply@anthropic.com>"

# After full convergence
git commit -m "feat: feature-complete implementation of [feature-name]
• Iterations: [n] gap resolution cycles
• Gaps resolved: [list]
• Final Geist validation:
  - Ghost: All unknowns discovered and addressed
  - Geyser: All forces accounted for
  - Gist: Essential features 100% complete
• Test coverage: [percentage]%
• UI validation: All flows passing
• Performance: All benchmarks met

🎯 FEATURE COMPLETE via automated gap resolution
Co-Authored-By: Claude <noreply@anthropic.com>"
```

**9. Example Scenarios**

**Examples:** E-commerce checkout (5 loops: payment forms → gateway → confirmation), Dashboard metrics (8 loops: metrics + optimize performance)

### Anti-Patterns for Gap Resolution

**❌ Don't:**
- Skip Geist analysis before starting implementation
- Implement without TDD (breaks the resolution guarantee)
- Ignore UI validation for user-facing gaps
- Allow more than 10 iterations without escalation
- Resolve non-critical gaps before critical ones
- Disable gap re-evaluation after each fix

**✅ Do:**
- Always start with three-dimensional Geist analysis
- Use TDD for every gap resolution
- Validate UI after each user-facing implementation
- Prioritize critical gaps (Gist) over nice-to-haves
- Re-analyze after each resolution (gaps can cascade)
- Document the resolution journey for complex features

### Anti-Patterns to Avoid

**❌ Don't:**
- Use database-migrator in parallel with other implementation agents
- Skip root-cause-finder for mysterious production issues
- Run code-conciser and refactoring-specialist simultaneously **on same modules**
- Use UI agents without proper browser environment setup
- Ignore parallel safety flags in complex workflows
- Disable auto-recovery in production validation
- Exceed 3 auto-recovery attempts without escalation
- Skip Geist analysis for feature gap detection
- Implement features without TDD in gap resolution workflow
- **Wait until end to refactor everything (monolithic refactoring anti-pattern)**
- **Run cross-cutting refactoring in parallel (affects all modules)**

**✅ Do:**
- Use coordination meta-agent for 3+ specialized agents
- Leverage parallel execution for independent analysis/verification
- Replace standard agents with specialized ones when domain-specific
- Follow commit protocols for each agent type
- Validate success criteria before phase transitions
- Enable auto-recovery for UI validation workflows
- Document all auto-recovery actions for audit trail
- Use Feature Gap Resolution Workflow for incomplete implementations
- Always validate feature completeness with Geist analyzer
- **Use strategic refactoring: Refactor completed Module A while implementing Module B**
- **Checkpoint-based refactoring at milestones (prevents technical debt accumulation)**
- **See `06-collaborative-construction/AGENTIC_CODING_OPTIMIZATION.md` for optimization patterns**

## Commit Protocol

**When to Commit:** Analysis complete, implementation functional, quality gates pass

**Pre-Commit Validation:** Files compile, no credentials, tests pass, server starts, artifacts ok

**Commit Types:**
- **Draft:** `draft: [analysis-type] for [feature]` (planning phase)
- **Feature:** `feat: implement [feature] with [capability]` + security/testing details
- **Quality:** `quality: [feature] passes all quality gates` + metrics
- **Release:** `release: complete [feature] with full traceability` + production-ready status

**Failure Recovery:** Analyze → Fix → Re-validate → Retry → Escalate

### Intelligent Commit Strategy

**Phase-Based Protocol:** `Planning→Implementation→Verification→Documentation` = `Draft→Feature→Quality→Release`

**Auto Triggers:** Commit when sub-agent completes + quality gates pass

**Templates:** `[type]: [description]` + implementation/testing/security details + Claude co-author

**Branch Strategy:** `main → feature → drafts → squash → merge`

**Quality Gates:** Files compile, no vulnerabilities, coverage maintained, conventional commits

## Never Do

- Store credentials, create backwards compatibility wrappers
- Implement without reading existing code, checking DRY principles
- Create plans without template, >65k chars, missing metadata
- Skip server startup validation, Geist analysis
- Ignore Ghost/Geyser/Gist dimensions
- **CRITICAL: Leave old implementations - ALWAYS remove deprecated code**
- **CRITICAL: Complex implementations (3+ sub-agents) without coordination meta-agent**
- **CRITICAL: Skip coordination meta-agent for production deployments**

Remember: Direct debugging over tests. Check existing functionality first.