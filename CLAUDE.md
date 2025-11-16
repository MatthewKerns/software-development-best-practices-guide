# Claude Code Instructions - Data Input Pipeline

Python project with LangGraph/LangSmith for email processing. Uses TDD, async patterns, tool-based architecture.

**CONTEXT: NO ACTIVE USERS** - Zero backward compatibility needed. Delete old code immediately.

## Quick Setup

```bash
python -m venv .venv && source .venv/bin/activate && pip install -e .[dev]
langgraph dev  # Start server
pytest -m "unit or integration" -q --cov=src --cov-fail-under=90
```

### Chrome DevTools MCP Integration
**Status**: ✅ Installed and Connected

Enables AI debugging of web applications through live Chrome browser control.

**Key Capabilities:**
- Browser automation with Puppeteer
- Performance trace recording and analysis
- Network request inspection (headers, payloads, timing)
- Console error debugging with stack traces
- Screenshot capture for visual validation
- DOM inspection and manipulation
- WCAG accessibility scanning

**Quick Commands:**
```bash
claude mcp list  # Verify status
claude mcp add chrome-devtools npx chrome-devtools-mcp@latest
```

**Guide**: `docs/CHROME_DEVTOOLS_MCP_GUIDE.md`

## Architecture Patterns (MANDATORY)

### LangGraph Tool Pattern
```python
@tool("api_operation")
async def api_operation_tool(param1: str) -> dict:
    service = ExternalAPIService()
    result = await asyncio.to_thread(service.blocking_op, param1)
    return {"status": "success", "data": result}
```

### DRY Compliance & Pre-emptive Duplication Detection
- Search existing code before implementing
- Delete old implementations when refactoring
- No backward compatibility - direct replacement
- **Use `dry-compliance-checker` skill** for pre-emptive duplication detection

**Pre-Implementation Checklist:**
1. **Field/Property Overlap**: Will this combine outputs? Read utility return schemas - don't assume
2. **Backward Compatibility Reality**: Is codebase published? Do external users exist? If NO → Don't add compatibility layers
3. **Utility Function Inspection**: Print/log utility outputs during planning to verify fields
4. **Naming Consistency**: Use consistent field names across entire codebase

**Common Anti-Patterns:**
```python
# ❌ WRONG - "Just in case" fields
return {"exit_code": 0, "return_code": 0, "status_code": 0}

# ✅ CORRECT - Single, well-named field
return {"exit_code": 0}

# ❌ WRONG - Re-adding fields already in utility output
formatted = FeedbackFormatter.format_command_output(cmd, stdout, stderr, exit_code)
return {**formatted, "return_code": exit_code}  # Duplicates what's in formatted!

# ✅ CORRECT - Trust the utility, extend only with NEW fields
return {**formatted, "execution_time": time.time() - start_time}
```

**Real Example Cost**: Implemented both `exit_code` and `return_code` for "backward compatibility" when zero users existed → wasted implementation + refactoring + test update + docs update time

## Development Practices

### TDD (MANDATORY)
- **Development TDD**: Real components + dependencies
- **Unit TDD**: Real component + mocked dependencies
- **Test markers**: `@pytest.mark.{unit|integration|node|live}`
- **Coverage**: Integration 85%+, Unit 90%+
- **Gap Resolution**: Document gaps (GAP-[ID]), TDD loop to close
- **Use `tdd-workflow-assistant` skill** for Red-Green-Refactor guidance

### Async Compliance
All LangGraph: `result = await asyncio.to_thread(blocking_op, args)`

### Code Quality
- Type hints everywhere
- Comments explain WHY
- Black formatting (88 chars)
- **Use `code-smell-detector` + `solid-validator` skills**

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

## Claude Skills (7 Available)

Auto-invoked capabilities from repository best practices:
- `parallel-execution-planner`: Parallel vs sequential optimization (30-50% time savings)
- `geist-analyzer`: Ghost/Geyser/Gist three-dimensional problem analysis
- `gap-analyzer`: Continuous gap detection vision→implementation
- `tdd-workflow-assistant`: Red-Green-Refactor automation
- `dry-compliance-checker`: Pre-emptive duplication detection (save 2-8 hrs/feature)
- `code-smell-detector`: Refactoring opportunity identification
- `solid-validator`: SOLID principles validation

## Geist-Driven Development (MANDATORY)

Three-dimensional problem analysis for all tasks:

**1. Ghost** (Parallel Reality): Unknown unknowns, assumptions, context gaps
**2. Geyser** (Dynamic Forces): Explosive forces, emergent properties
**3. Gist** (Essential Core): Irreducible essence, core problem vs distractions

**Debug Protocol:**
1. Ghost: What parallel reality am I not seeing?
2. Geyser: What forces am I not accounting for?
3. Gist: Am I solving the essential problem?

**Use `geist-analyzer` skill** for automated analysis.

## Implementation Planning

### BRD (Business Requirements Document)
**MANDATORY for features >3 days effort** - Define WHAT/WHY before HOW

**Purpose**: Define WHAT needs to be built and WHY (business value), not HOW (technical implementation)

**Template**: `08-project-management/BRD_TEMPLATE.md`
**Guidelines**: `08-project-management/BRD_CREATION_GUIDELINES.md`

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

**BRD Workflow**: Stakeholder interviews → Geist analysis → Requirements specification → Validation sessions → Formal approval → Implementation planning begins

**BRD vs Implementation Plan:**
- **BRD**: Business stakeholders, WHAT/WHY, before development
- **Implementation Plan**: Developers/architects, HOW, after BRD approval

### Implementation Plans
**MANDATORY for plans >4 hours** (after BRD approval)
- **Template**: `docs/MARKDOWN_PLAN_TEMPLATE.md`
- **Required Metadata**: Plan Type, Author, Created, Updated, Version, Issue, Priority, Effort, Dependencies, <65k chars
- **MANDATORY Sections**: Overview with business context (WHY), Requirements & Acceptance Criteria, TDD Approach, Implementation Plan (phases), QA & Validation checklist, Server Startup Validation, Gap Analysis, File Organization
- **Locations**: `docs/plans/`, `docs/adr/`, `dev-tools/scripts/investigation/`, `dev-tools/test-results/`
- **Requirements**: 85%+ coverage, tests pass, server starts, no mocks, <65k chars

## File Organization

- **Production**: `src/` only
- **Development**: `dev-tools/scripts/`
- **Tests**: `dev-tools/test-results/`
- **Logs**: `logs/`
- **CI/CD**: `cicd/`
- **Plans**: `docs/plans/`, `docs/adr/`
- **Verification**: `docs/verification/[feature]-{traceability,test-results,completion,acceptance}.md`

## Sub-Agent Architecture (MANDATORY for 3+ agents)

### Core Flow (Standard Implementation)

**Phase 1: Planning (Sequential)**
```
requirements-analyzer → geist-analyzer → plan-validator → implementation-planner
```

**Phase 2: Implementation (Hybrid)**
```
Parallel: security-validator + codebase-analyzer + test-planner
Sequential: code-implementor → integration-tester → quality-gate-validator
```

**Phase 3: Verification (Parallel)**
```
gap-analyzer + documentation-updater + performance-validator + traceability-mapper
```

### Specialized Agents

**Database & Infrastructure:**
- `database-migrator`: Schema changes, risk assessment, rollback planning (Sequential only)
- `root-cause-finder`: Exhaustive failure analysis, multi-angle investigation (Parallel safe)

**UI & Frontend Quality:**
- `ui-bar-raiser`: UI testing, WCAG compliance, auto-recovery with root-cause-finder (Parallel). **Uses Chrome DevTools MCP**
- `ui-playwright-integration`: Browser automation, accessibility snapshots (Parallel)
- `ui-quality-enhancer`: Component analysis, design system validation (Parallel)

**Development & Code Quality:**
- `code-conciser`: Redundancy removal, expression simplification (Sequential only)
- `refactoring-specialist`: Large-scale refactoring (Strategic parallel at milestones, Sequential for cross-cutting)
- `tdd-implementor`: Red-Green-Refactor, 85%+ coverage, test-driven gap resolution (Conditional parallel)

**Validation & Completeness:**
- `exactly-right`: Comprehensive validation after development. **MANDATORY coordination with requirements-analyzer + gap-analyzer** (Sequential after implementation, Parallel with analysis agents)

### Agent Selection Decision Tree

**Standard Implementation (3+ sub-agents):**
```
requirements-analyzer → geist-analyzer → implementation-planner
→ [Parallel: security + codebase + test-planner]
→ code-implementor → integration-tester → quality-gate-validator
→ [Parallel: gap + docs + performance + traceability]
```

**Specialized Domain:**
- **Database changes** → Replace code-implementor with `database-migrator`
- **Frontend/UI** → Add UI suite (ui-bar-raiser + ui-playwright-integration + ui-quality-enhancer) in verification
- **Mysterious failures** → `root-cause-finder` immediate (any phase)
- **Feature gaps** → `geist-analyzer` + `gap-analyzer` + `tdd-implementor` + `ui-bar-raiser` (iterative loop)
- **Production readiness** → `exactly-right` + `requirements-analyzer` + `gap-analyzer` (parallel coordination)
- **Verbose code** → `code-conciser` (after implementation)
- **Large refactoring** → `refactoring-specialist` (replaces code-implementor)

### Parallel Execution Strategy

**Complete Guide**: `06-collaborative-construction/AGENTIC_CODING_OPTIMIZATION.md`
**Use `parallel-execution-planner` skill** for automated analysis

**Always Parallel:**
- Independent analysis (security, performance, requirements)
- Different docs (API, user, architecture)
- Separate verification domains
- Non-overlapping modules
- **Strategic refactoring: Refactor Module A while implementing Module B**

**Never Parallel:**
- Same file modifications
- Data dependencies
- Cross-cutting refactoring
- Database migrations

**Context Budgeting:**
- **Coordination agent**: ~20K tokens (orchestration)
- **Specialized agents**: 15-80K each (focused tasks)
- **Target**: <200K per conversation turn
- **Strategy**: Distribute across N parallel agents

### Coordination Meta-Agent (MANDATORY for 3+ agents)

Central orchestrator managing parallel execution, conflict resolution, quality validation.

**Core Responsibilities:**
1. Analyze complexity & determine sub-agent requirements
2. Create parallel execution strategy with dependency mapping
3. Launch and monitor multiple sub-agents
4. Detect and resolve conflicts (file/state/timing)
5. Aggregate quality gates across all agents
6. Ensure deployment-ready deliverables

**Use For:**
- Complex implementations (3+ sub-agents)
- Cross-cutting concerns (security, performance, testing)
- **Production deployments** (8-area validation framework)
- Large refactoring efforts
- Multi-service integrations

**Strategy**: Sequential Planning → Hybrid Implementation → Parallel Verification

**Execution Rules:**
- **Always Parallel**: Independent analysis, docs, validation
- **Never Parallel**: Shared state or file conflicts
- **Conditional**: Based on dependency analysis

**Workflow**: User Request → Coordination Meta-Agent → Sub-Agent Orchestration → Production

**Execution Flow:**
1. Analyze complexity & determine sub-agent requirements
2. Create parallel execution strategy with dependency mapping
3. Launch and monitor multiple sub-agents
4. Detect and resolve conflicts
5. Aggregate quality gates
6. Ensure deployment-ready deliverables

### Sub-Agent Coordination Patterns

**Management**: Central orchestrator plans parallel execution, manages conflicts, enforces quality gates

**Handoffs**: Specific deliverables → validation → next phase (coordination meta-agent validates transitions)

**Communication**: Structured artifacts (JSON/Markdown), no direct inter-agent communication

**Error Handling**:
- Sequential failures stop chain
- Parallel failures isolated
- Auto rollback for critical failures

**Sub-Agent Deliverables Summary:**
- **Planning**: requirements-analyzer, geist-analyzer, implementation-planner → draft commits
- **Implementation**: security-validator, codebase-analyzer, test-planner (parallel) → code-implementor → integration-tester → quality-gate-validator → feat/test/quality commits
- **Verification**: gap-analyzer, documentation-updater, performance-validator, traceability-mapper (parallel) → quality/docs/perf/release commits
- **Specialized**: database-migrator (migration scripts), root-cause-finder (analysis), UI Suite (test validation), Code Quality (refactor/feat commits)

## Production Readiness (MANDATORY)

**Framework**: `09-production-readiness/` - 8-area validation

**8 Areas:**
1. Infrastructure Resilience
2. Security Posture
3. Performance & Scalability
4. Monitoring & Observability
5. Deployment & Release
6. Data Integrity
7. Cost Optimization
8. Compliance Readiness

**Guides by Scale:**
- **Small** (<10K visitors, static sites): `SMALL_SCALE_READINESS.md` (4-8 hrs)
- **Medium** (10K-100K users, dynamic apps): `MEDIUM_SCALE_READINESS.md` (2-3 weeks)
- **Large** (100K+ users, multi-repo): `LARGE_SCALE_READINESS.md` (1-2 months)

**Operational Guides:**
- `PRODUCTION_READINESS_FRAMEWORK.md` - 8-area checklist with scoring
- `PRODUCTION_DEPLOYMENT_CHECKLIST.md` - Pre-deployment validation
- `ROLLBACK_AND_RECOVERY.md` - Disaster recovery procedures
- `MONITORING_AND_OBSERVABILITY.md` - Observability setup
- `SECURITY_HARDENING.md` - Security hardening checklist
- `PERFORMANCE_BENCHMARKS.md` - Performance standards
- `COST_OPTIMIZATION.md` - Cost management
- `COMPLIANCE_READINESS.md` - Regulatory standards

**Workflow**:
```
Pre-Production (1-2 weeks): 8-area assessment + gap-analyzer
Pre-Deployment (1-3 days): Checklist + rollback test + monitoring
Deployment: Blue-green + 24/7 monitoring (48-72 hrs)
```

**Coordination Meta-Agent (MANDATORY for production)**:
```
Parallel Verification Phase:
• security-validator → SECURITY_HARDENING.md checks
• performance-validator → PERFORMANCE_BENCHMARKS.md validation
• gap-analyzer → Missing production requirements
• exactly-right → Zero-defect validation

Sequential Release Phase:
• database-migrator → Schema changes with rollback
• deployment-orchestrator → Blue-green or canary deployment
• monitoring-validator → Observability stack operational

Production Validation Phase (Parallel):
• exactly-right → Critical paths validation
• ui-bar-raiser → User flows functional
• performance-validator → Benchmarks met
```

**Success Criteria (ALL must be met):**
- ✅ All 8 production readiness areas validated
- ✅ Critical path test coverage ≥85%
- ✅ Security scan: Zero critical/high vulnerabilities
- ✅ Performance benchmarks met
- ✅ Monitoring and alerting configured
- ✅ Rollback procedures tested
- ✅ Disaster recovery plan validated
- ✅ Team trained on incident response
- ✅ Stakeholder approval obtained

## Feature Gap Resolution Workflow

**MANDATORY for incomplete implementations**

**Use `gap-analyzer` + `geist-analyzer` skills** for automated gap detection and convergence validation.

```
geist-analyzer (gap detection) → gap-analyzer (enumerate) → requirements-analyzer (map criteria)
↓
LOOP (max 10 iterations):
  tdd-implementor (RED-GREEN-REFACTOR) →
  ui-bar-raiser (validate UI/UX) →
  gap-analyzer (re-evaluate) →
  geist-analyzer (check convergence)
↓
COMPLETE when: Ghost=resolved, Geyser=addressed, Gist=100% complete
```

**Convergence Criteria**: No unknown requirements + all blocking forces resolved + essential features 100% + zero critical gaps + ≥85% coverage + all flows functional

## UI Bar Raiser Auto-Recovery

**MANDATORY for UI validation**

**Workflow**:
```
ui-bar-raiser → Error detection (console, network, accessibility, performance)
↓
Auto-spawn root-cause-finder (exhaustive analysis)
↓
Spawn fix agent (code-implementor, refactoring-specialist, ui-quality-enhancer, integration-tester)
↓
ui-bar-raiser re-validation
↓
LOOP until success (max 3 retries)
```

**Uses Chrome DevTools MCP** for live browser debugging, performance tracing, network inspection.

## Implementation Verification & Definition of Done

**MANDATORY Verification Phases:**
1. **Requirements**: Document with acceptance criteria, stakeholders, Geist analysis, traceability matrix
2. **Implementation**: Quality gates (tests, lint, typecheck), security checklist, system integration
3. **Testing**: ≥85% coverage, end-to-end workflows, performance validation, server startup
4. **Completion**: Replace placeholders, error handling, environment configs, database migrations
5. **Documentation**: Update all docs, architecture decisions, API docs, deployment procedures
6. **Alignment**: Requirements→features mapping, quality/performance/security validated, user acceptance

**Artifacts**: `docs/verification/[feature]-{traceability,test-results,completion,acceptance}.md`

**Failure Protocol**: Document gaps → remediation → fix → re-run → **do NOT mark complete until ALL pass**

## Commit Protocol

**When to Commit**: Analysis complete, implementation functional, quality gates pass

**Pre-Commit Validation**: Files compile, no credentials, tests pass, server starts, artifacts ok

**Git Safety Protocol:**
- NEVER update git config
- NEVER run destructive commands (push --force, hard reset) unless explicitly requested
- NEVER skip hooks (--no-verify, --no-gpg-sign) unless requested
- NEVER force push to main/master (warn user if requested)
- Avoid `git commit --amend` unless: (1) user explicitly requested OR (2) adding edits from pre-commit hook
- Before amending: ALWAYS check authorship (`git log -1 --format='%an %ae'`)
- NEVER commit changes unless user explicitly asks

**Phases**: Planning→Implementation→Verification→Documentation = Draft→Feature→Quality→Release

**Commit Types:**
- `draft:` `draft: [analysis-type] for [feature]` (planning phase)
- `feat:` `feat: implement [feature] with [capability]` + security/testing details
- `quality:` `quality: [feature] passes all quality gates` + metrics
- `release:` `release: complete [feature] with full traceability` + production-ready status

**Commit Template Format:**
```bash
git commit -m "$(cat <<'EOF'
[type]: [description]

• Implementation: [details]
• Testing: [coverage/results]
• Security: [checks completed]

🤖 Generated with [Claude Code](https://claude.com/claude-code)

Co-Authored-By: Claude <noreply@anthropic.com>
EOF
)"
```

**Failure Recovery**: Analyze → Fix → Re-validate → Retry → Escalate

**Branch Strategy**: `main → feature → drafts → squash → merge`

## Common Patterns

**Email Processing**: Gmail tools in `src/workflow/steps/step01_extract_emails/`

**Database Operations**: Four-component architecture: operations + connection managers
```python
import asyncio
import asyncpg
conn = await asyncpg.connect(os.getenv("NEON_DATABASE_URL"))
```

**Database Migrations (MANDATORY):**
1. Follow `docs/DATABASE_MIGRATION_GUIDE.md`
2. Numbered SQL in `migrations/` directory
3. Test on dev first
4. Python for complex migrations
5. Validation queries + logging
6. Update documentation

**Error Handling**: Structured errors with recovery strategies, no backwards compatibility

**Test-Driven Gap Resolution (MANDATORY when tests fail):**
1. Document gaps with GAP-[ID] in `docs/decision-history/gaps/`
2. Categorize by severity (Critical/High/Medium/Low)
3. Create resolution plan following template
4. Use TDD loop (RED-GREEN-REFACTOR) to close each gap
5. Validate all gaps resolved before proceeding
6. Reference: `docs/quality-through-testing/TEST_DRIVEN_GAP_RESOLUTION.md`

## Agent Usage Examples

### Example 1: Database Schema Change
```
User: "Add user_preferences table with notification settings"

requirements-analyzer → geist-analyzer → implementation-planner
↓
[Parallel: security-validator + codebase-analyzer + test-planner]
↓
database-migrator (replaces code-implementor)
• Risk assessment: MEDIUM (new table, no data loss)
• Migration script with rollback
• Validation queries
↓
integration-tester → quality-gate-validator
↓
[Parallel: gap-analyzer + documentation-updater + performance-validator + traceability-mapper]
```

### Example 2: Feature Gap Resolution
```
User: "Complete the dashboard with all required metrics"

geist-analyzer (gap detection)
• Ghost: Unknown data dependencies
• Geyser: Performance constraints
• Gist: 10 metrics essential, 5 missing
↓
gap-analyzer (enumerate gaps)
• Revenue metric missing
• User activity graph incomplete
• Export functionality absent
↓
LOOP (Iterations 1-6):
  tdd-implementor (RED-GREEN-REFACTOR for each gap)
  → ui-bar-raiser (validate display/accessibility/performance)
  → gap-analyzer (confirm gap closed, check cascading gaps)
  → geist-analyzer (convergence check: 9/10, then 10/10 ✓)
↓
CONVERGENCE ACHIEVED → Feature Complete
```

### Example 3: Production Issue Investigation
```
User: "API responding slowly, users complaining"

root-cause-finder (immediate)
• Database query analysis: N+1 query detected
• Network latency: Within normal range
• Memory usage: Spike during peak hours
• Cascade effects: Database connection pool exhaustion
↓
Based on findings:
  database-migrator (add indexes)
  → refactoring-specialist (optimize queries)
  → performance-validator (validate improvements)
↓
integration-tester + quality-gate-validator
↓
[Parallel verification: gap-analyzer + documentation-updater]
```

## Quick Commands

```bash
langgraph dev
pytest -m "unit or integration" -x -q --cov=src --cov-fail-under=90
black . && ruff check . && mypy src/
find . -name "*.py" -exec basename {} \; | sort | uniq -d  # Duplication check
```

## Key References

- **Tool Pattern**: `docs/adr/ADR_005_*`
- **TDD**: `code_quality_practices/TDD_*`
- **Async**: `construction_best_practices/ASYNC_*`
- **DB Migrations**: `docs/DATABASE_MIGRATION_GUIDE.md`
- **Production**: `09-production-readiness/`
- **Agentic Optimization**: `06-collaborative-construction/AGENTIC_CODING_OPTIMIZATION.md`
- **Gap Resolution**: `docs/quality-through-testing/TEST_DRIVEN_GAP_RESOLUTION.md`
- **Chrome DevTools MCP**: `docs/CHROME_DEVTOOLS_MCP_GUIDE.md`

## Anti-Patterns to Avoid

**❌ Don't:**
- Store credentials or create backward compatibility wrappers
- Implement without reading existing code (DRY check)
- Create plans without template or >65k chars
- Skip server startup validation or Geist analysis
- Leave old implementations - DELETE deprecated code
- Complex implementations (3+ agents) without coordination meta-agent
- Skip production readiness for deployments (8-area assessment)
- Deploy without coordination meta-agent validation
- Use database-migrator in parallel with other implementation agents
- Skip root-cause-finder for mysterious production issues
- Run code-conciser and refactoring-specialist simultaneously on same modules
- Use UI agents without proper browser environment setup
- Ignore parallel safety flags in complex workflows
- Disable auto-recovery in production validation
- Exceed 3 auto-recovery attempts without escalation
- Skip Geist analysis for feature gap detection
- Implement features without TDD in gap resolution workflow
- Wait until end to refactor everything (monolithic refactoring anti-pattern)
- Run cross-cutting refactoring in parallel (affects all modules)

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
- Use strategic refactoring: Refactor completed Module A while implementing Module B
- Checkpoint-based refactoring at milestones (prevents technical debt accumulation)

**Remember**: Direct debugging over tests. Check existing functionality first. Use skills proactively.
