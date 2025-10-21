# Context Limits: Constraints and Mitigation Strategies

**Document Version:** 1.0
**Last Updated:** 2025-10-21
**Related:** [WHAT_IS_CONTEXT.md](./WHAT_IS_CONTEXT.md), [AGENTIC_CODING_OPTIMIZATION.md](../../06-collaborative-construction/AGENTIC_CODING_OPTIMIZATION.md), [EVOLVING_CAPABILITIES.md](./EVOLVING_CAPABILITIES.md)

---

## Table of Contents

1. [Context Window Constraints](#context-window-constraints)
2. [Context Overflow Scenarios](#context-overflow-scenarios)
3. [Auto-Compacting Behavior](#auto-compacting-behavior)
4. [Mitigation Strategies](#mitigation-strategies)
5. [Context Budget Planning](#context-budget-planning)
6. [Practical Examples](#practical-examples)

---

## Context Window Constraints

### Understanding Token Limits

Context windows define the maximum amount of information an AI model can process in a single conversation turn. These limits are measured in **tokens** - roughly 4 characters per token in English text.

**Current Model Comparison (2025):**

| Model | Context Window | Effective Working Space | Reserve for Response |
|-------|----------------|-------------------------|----------------------|
| Claude Sonnet 4.5 | 200,000 tokens | ~140,000 tokens | ~60,000 tokens |
| GPT-4 Turbo | 128,000 tokens | ~90,000 tokens | ~38,000 tokens |
| Claude Opus 3 | 200,000 tokens | ~140,000 tokens | ~60,000 tokens |
| GPT-4o | 128,000 tokens | ~90,000 tokens | ~38,000 tokens |

**Token Estimation Guidelines:**

- **Code:** ~1 token per 3-4 characters (includes syntax)
- **Prose:** ~1 token per 4-5 characters (natural language)
- **JSON/YAML:** ~1 token per 2-3 characters (structured data)
- **Tool outputs:** ~1 token per 3-4 characters (mixed content)

**Example Token Counts:**

```
Small file (100 lines): ~2,500 tokens
Medium file (500 lines): ~12,000 tokens
Large file (2000 lines): ~50,000 tokens
Entire conversation (50 turns): ~80,000-150,000 tokens
Full codebase scan: 200,000+ tokens (overflow risk)
```

### What Happens When Limits Are Exceeded

When a conversation approaches or exceeds the context window limit, AI systems employ **auto-compacting** mechanisms to preserve functionality:

**Phase 1: Warning Zone (80-90% capacity)**
- System begins prioritizing recent context
- Older messages marked for potential compression
- Performance may degrade slightly

**Phase 2: Auto-Compacting (90-100% capacity)**
- Oldest messages automatically summarized or removed
- System-generated context preserved (tool definitions, instructions)
- User messages and responses compressed
- Key decisions may be lost without explicit preservation

**Phase 3: Hard Limit (100%+ capacity)**
- Conversation may reset or truncate aggressively
- Critical context loss risk
- Requires manual intervention (agent delegation, context refresh)

---

## Context Overflow Scenarios

### Long Conversations (100+ Turns)

**Symptom:** AI "forgets" earlier decisions, repeats questions, loses task coherence.

**Example Scenario:**
```
Turn 1-20: Requirements analysis (30K tokens)
Turn 21-50: Implementation planning (50K tokens)
Turn 51-80: Code implementation (60K tokens)
Turn 81-100: Testing and debugging (70K tokens)
Total: 210K tokens → OVERFLOW at turn ~85
```

**Risk:** By turn 85, the AI may have lost context from turns 1-40, forgetting original requirements or architectural decisions.

### Large File Reads (Whole Codebase)

**Symptom:** Attempting to read entire codebase at once exceeds context limits.

**Example Scenario:**
```bash
# Anti-pattern: Reading all files at once
Read src/module_a.py (15K tokens)
Read src/module_b.py (20K tokens)
Read src/module_c.py (18K tokens)
Read src/module_d.py (22K tokens)
Read src/module_e.py (25K tokens)
Read tests/test_*.py (40K tokens)
Total: 140K tokens → Near limit with no room for analysis
```

**Risk:** No remaining context budget for analysis, responses, or tool usage.

### Verbose Tool Outputs (Large Logs)

**Symptom:** Tool outputs (test results, logs, build outputs) consume excessive context.

**Example Scenario:**
```bash
# Verbose test output
pytest --verbose
# Outputs 50K tokens of test results, stack traces, coverage reports

# Database migration logs
# Outputs 30K tokens of SQL execution logs

# Linter/formatter output
# Outputs 20K tokens of warnings and fixes

Total: 100K tokens from tool outputs alone
```

**Risk:** Tool outputs crowd out conversation history and working memory.

### Cumulative Context Buildup

**Symptom:** Incremental context accumulation over time leads to eventual overflow.

**Example Scenario:**
```
Initial context (instructions, env): 20K tokens
Each conversation turn: 3-5K tokens
After 40 turns: 20K + (40 × 4K) = 180K tokens
Approaching overflow without obvious cause
```

**Risk:** Silent degradation as older context gets compressed without user awareness.

---

## Auto-Compacting Behavior

### How LLMs Compress Context

When approaching context limits, AI systems use several strategies to preserve functionality while reducing token usage:

**1. Message Summarization**
- Older messages condensed into brief summaries
- Original detail lost, only high-level intent preserved
- Example: "User requested database migration" vs full migration plan

**2. Selective Removal**
- Non-critical messages removed entirely
- Older tool outputs prioritized for removal
- Intermediate analysis steps discarded

**3. Priority Preservation**
- System instructions always preserved (CLAUDE.md, tool definitions)
- Recent messages (last 10-20 turns) preserved in full
- Critical decisions explicitly marked for retention

### What Gets Removed First

**Removal Priority (First → Last):**

1. **Old tool outputs** (bash results, file reads from 30+ turns ago)
2. **Intermediate analysis** (exploratory code searches, failed attempts)
3. **Verbose responses** (long explanations, detailed walkthroughs)
4. **Historical context** (earlier requirements discussions)
5. **Recent tool outputs** (last 10 turns preserved)
6. **Recent user messages** (last 5-10 turns preserved)
7. **System instructions** (never removed - CLAUDE.md, tool definitions)

### Risks of Auto-Compacting

**Context Loss Examples:**

| What's Lost | Impact | Severity |
|-------------|--------|----------|
| Original requirements | Implement wrong feature | **Critical** |
| Architectural decisions | Violate design principles | **High** |
| Test strategy | Incomplete coverage | **High** |
| File paths/references | Can't locate code | **Medium** |
| Performance benchmarks | Can't validate improvements | **Medium** |
| Code review feedback | Repeat mistakes | **Low** |

**Detection Signs:**

- AI asks questions already answered
- Implements features inconsistent with earlier decisions
- Suggests approaches already rejected
- Loses track of task progress or status
- References files/functions that don't exist (from compacted context)

---

## Mitigation Strategies

### Strategy 1: Agent Delegation

**Concept:** Spawn fresh sub-agents with focused context instead of accumulating everything in one conversation.

**When to Use:**
- Complex implementations (3+ sub-tasks)
- Distinct work phases (planning → implementation → testing)
- Independent parallel work (frontend + backend)

**Implementation:**

```yaml
# Coordination Meta-Agent (20K tokens)
context:
  - User request summary
  - High-level plan
  - Sub-agent orchestration logic

# Sub-Agent 1: Requirements Analysis (15K tokens)
context:
  - User request (full detail)
  - Existing requirements docs
  - Analysis tools

# Sub-Agent 2: Code Implementation (60K tokens)
context:
  - Requirements summary (from Sub-Agent 1)
  - Relevant code files only
  - Implementation tools

# Sub-Agent 3: Testing (40K tokens)
context:
  - Implementation summary
  - Test files only
  - Testing tools

Total: 135K tokens distributed across 4 agents
vs. 135K tokens in single agent (near overflow)
```

**Benefits:**
- Fresh context for each phase
- Parallel execution saves time
- Isolated failures don't contaminate entire workflow
- Each agent stays within optimal context range (60-80K)

### Strategy 2: Context Refresh

**Concept:** Periodically summarize key decisions and start fresh conversation with summary.

**When to Use:**
- Long-running conversations (50+ turns)
- After major milestones (planning complete, implementation complete)
- When approaching 70-80% context capacity

**Implementation:**

```markdown
# Context Refresh Protocol

1. Identify milestone completion
2. Generate comprehensive summary:
   - Decisions made
   - Code changes implemented
   - Outstanding tasks
   - Critical context to preserve

3. Archive current conversation
4. Start fresh conversation with summary as first message
5. Continue from refreshed context state
```

**Example Summary Format:**

```markdown
# Context Refresh: Database Migration Implementation

## Completed Work
- Analyzed existing schema (users, posts, comments tables)
- Designed migration adding user_preferences table
- Implemented migration script with rollback
- Created validation queries

## Key Decisions
- Use JSONB for preferences storage (performance + flexibility)
- Add partial index on active users only
- Set default values for all fields (backward compatibility)

## Outstanding Tasks
- Integration testing with production data sample
- Performance benchmarking
- Documentation updates

## Critical Context
- Migration risk: MEDIUM (new table, no data modification)
- Rollback tested and validated
- Deployment window: Weekend maintenance
```

### Strategy 3: File References Over Full Content

**Concept:** Use file paths and line ranges instead of reading entire files.

**Anti-Pattern:**

```python
# Reads 50K tokens
Read src/module_a.py
Read src/module_b.py
Read src/module_c.py
Read tests/test_all.py

# Analyze all files...
```

**Better Pattern:**

```python
# Reference files without reading
Grep "class UserService" --files-with-matches
# Returns: src/services/user_service.py

# Read only relevant sections
Read src/services/user_service.py (lines 45-120)
# Reads 2K tokens instead of 15K
```

**Context Savings:**

| Approach | Tokens Used | Efficiency Gain |
|----------|-------------|-----------------|
| Read entire file | 15,000 tokens | Baseline |
| Read specific lines | 2,000 tokens | **7.5x improvement** |
| Reference path only | 50 tokens | **300x improvement** |

### Strategy 4: Incremental Loading

**Concept:** Load context incrementally as needed, not all upfront.

**Implementation Phases:**

**Phase 1: Discovery (Minimal Context)**
```bash
# Find relevant files (100 tokens)
Glob "**/*user*.py"

# Returns paths only
src/models/user.py
src/services/user_service.py
tests/test_user.py
```

**Phase 2: Selective Reading (Focused Context)**
```bash
# Read only the file we need to modify (3K tokens)
Read src/services/user_service.py

# Grep for specific patterns (500 tokens)
Grep "def authenticate" src/services/user_service.py -A 10
```

**Phase 3: Implementation (Controlled Context)**
```bash
# Edit specific sections (200 tokens output)
Edit src/services/user_service.py
old_string: "..."
new_string: "..."
```

**Total: 3,800 tokens vs 50,000 tokens for full codebase read**

### Strategy 5: Strategic Checkpoints

**Concept:** Archive context at milestones and create resumption points.

**Checkpoint Components:**

```markdown
# Checkpoint: [Feature Name] - [Phase]

## Timestamp
2025-10-21 14:30 UTC

## Context State
- Current working directory: /src/services
- Active branch: feature/user-auth
- Last commit: abc123f
- Files modified: user_service.py, auth_middleware.py

## Decisions Archive
1. Use JWT for authentication (vs session-based)
2. 15-minute token expiration (security requirement)
3. Refresh token rotation enabled

## Code State
- UserService.authenticate() implemented
- AuthMiddleware tests passing (12/12)
- Integration with existing user model complete

## Next Actions
1. Implement token refresh endpoint
2. Add rate limiting
3. Update API documentation

## Context Budget
- Used: 85,000 tokens
- Remaining: 115,000 tokens
- Recommendation: Checkpoint before next phase
```

**Checkpoint Triggers:**

- Every major milestone (requirements → planning → implementation → testing)
- Before context reaches 70% capacity (140K tokens for Claude Sonnet)
- After completing independent feature modules
- Before switching to different codebase area

---

## Context Budget Planning

### Estimating Tokens Before Operations

**Planning Checklist:**

```markdown
# Pre-Operation Context Budget

1. Current context usage: [X] tokens
2. Planned operation cost:
   - Read files: [Y] tokens
   - Tool outputs: [Z] tokens
   - Response generation: [40-60K] tokens
3. Total projected: X + Y + Z + 50K = [Total]
4. Context limit: 200K tokens
5. Remaining buffer: 200K - Total = [Buffer]

Decision:
- If Buffer > 60K → Proceed
- If Buffer 30-60K → Caution, consider cleanup
- If Buffer < 30K → STOP, delegate or checkpoint
```

**Example Calculation:**

```
Current usage: 90K tokens (conversation history)
Read 5 files: 5 × 10K = 50K tokens
Run tests: 20K tokens (output)
Response: 50K tokens (implementation + explanation)

Total: 90K + 50K + 20K + 50K = 210K tokens
Limit: 200K tokens
OVERFLOW RISK → Delegate to sub-agent instead
```

### Reserve Headroom for Responses

**Why Reserve 40-60K Tokens:**

- **Implementation responses:** 20-40K tokens (code + explanations)
- **Complex analysis:** 30-50K tokens (architectural decisions)
- **Error debugging:** 15-30K tokens (stack traces + fixes)
- **Tool usage:** 10-20K tokens (multiple tool calls)

**Buffer Strategies:**

| Buffer Size | Risk Level | Recommended Action |
|-------------|------------|-------------------|
| 80K+ tokens | **Low** | Safe to continue, full capabilities available |
| 60-80K tokens | **Medium** | Proceed with caution, avoid large file reads |
| 40-60K tokens | **High** | Checkpoint or delegate, minimal new context |
| <40K tokens | **Critical** | STOP - immediate checkpoint or agent delegation |

### Distribute Heavy Context Across Agents

**Optimal Context Distribution (from AGENTIC_CODING_OPTIMIZATION.md):**

**Coordination Meta-Agent:**
- Budget: 20-30K tokens
- Content: High-level plan, sub-agent coordination, decision summaries

**Analysis Agents (Parallel):**
- Budget: 15-25K tokens each
- Content: Focused domain analysis (security, performance, requirements)
- Total: 3 agents × 20K = 60K tokens

**Implementation Agents (Sequential):**
- Budget: 60-80K tokens each
- Content: Code files, tests, tool outputs
- Example: code-implementor (70K), integration-tester (65K)

**Verification Agents (Parallel):**
- Budget: 15-30K tokens each
- Content: Specific validation domains (docs, gaps, performance)
- Total: 4 agents × 20K = 80K tokens

**Total Distributed: 20K + 60K + 135K + 80K = 295K tokens**
**Across 9 parallel/sequential agents = avg 33K per agent**
**Well within limits vs 295K in single agent (overflow)**

### Refactoring Context Budget (60-120K Optimal)

From `AGENTIC_CODING_OPTIMIZATION.md`:

**Optimal Range for Refactoring Tasks:**
- **Minimum:** 60K tokens (small module refactoring)
- **Sweet Spot:** 80-100K tokens (balanced context + response room)
- **Maximum:** 120K tokens (large refactoring, requires careful planning)

**Why This Range:**

```
Module code: 30-50K tokens
Related tests: 15-25K tokens
Documentation: 5-10K tokens
Tool outputs: 10-15K tokens
Response room: 40-60K tokens
Total: 100-160K tokens

With 200K limit:
- 100K usage = 100K buffer (safe, optimal)
- 120K usage = 80K buffer (acceptable)
- 140K usage = 60K buffer (caution)
- 160K usage = 40K buffer (danger zone)
```

**Strategic Refactoring Pattern:**

```yaml
# Milestone-based refactoring (prevents monolithic overflow)

Milestone 1: Implement Module A
  context: 70K tokens
  ↓
Checkpoint & Refactor Module A (new agent)
  context: 90K tokens (Module A code + patterns)
  ↓
Milestone 2: Implement Module B (parallel to refactor)
  context: 70K tokens
  ↓
Module C Implementation (benefits from refactored patterns)
  context: 50K tokens (less code needed, reuses patterns)

vs. Monolithic Anti-Pattern:
  Implement A + B + C: 190K tokens
  Refactor everything: OVERFLOW
```

---

## Practical Examples

### Example 1: Long Conversation Mitigation

**Scenario:** 80-turn conversation approaching context limit.

**Detection:**
```
Turn 75: AI asks "What database are we using?" (already discussed turn 10)
Turn 78: Suggests architecture already rejected (turn 45)
Turn 80: Context usage warning: 175K/200K tokens
```

**Mitigation:**

```markdown
# Immediate Context Refresh

## Summary for New Context
- Database: PostgreSQL 15 with asyncpg
- Architecture: Four-component (operations + connection managers)
- Migration strategy: Numbered SQL files, Python for complex logic
- Current phase: Implementing user_preferences table
- Completed: Schema design, migration script, validation queries
- Next: Integration testing

## Start Fresh Conversation
[Paste summary above as first message]
"Continue from checkpoint: Implement integration testing for user_preferences migration"
```

**Result:** Context reduced from 175K to 5K tokens, preserving all critical decisions.

### Example 2: Large Codebase Analysis

**Scenario:** Need to analyze entire codebase (500 files, 200K+ tokens if fully read).

**Anti-Pattern:**
```bash
# Read all files
Read src/**/*.py
# OVERFLOW - impossible to fit in context
```

**Mitigation with Agent Delegation:**

```yaml
coordination-meta-agent:
  context: 20K
  task: Orchestrate codebase analysis

  sub-agents:
    codebase-analyzer-backend:
      context: 60K
      scope: src/services/, src/models/
      task: Analyze backend architecture

    codebase-analyzer-frontend:
      context: 50K
      scope: src/ui/, src/components/
      task: Analyze frontend patterns

    codebase-analyzer-tests:
      context: 40K
      scope: tests/
      task: Analyze test coverage

# Each agent reads only their scope
# Total: 20K + 60K + 50K + 40K = 170K distributed
# vs 200K+ in single agent (overflow)
```

### Example 3: Verbose Tool Output Management

**Scenario:** Test suite produces 40K tokens of output.

**Anti-Pattern:**
```bash
pytest --verbose --cov=src --cov-report=term-missing
# Output: 40K tokens (every test, every line coverage)
```

**Mitigation:**

```bash
# Use concise output
pytest -q --cov=src --cov-fail-under=85
# Output: 2K tokens (summary only)

# Only show failures
pytest -x --tb=short
# Output: 500 tokens per failure (stops at first failure)

# Capture to file, reference instead of reading
pytest --verbose > test-results.log
echo "Tests passed, see test-results.log for details"
# Output: 50 tokens (reference instead of full output)
```

**Context Savings: 40K → 500 tokens (80x improvement)**

### Example 4: Strategic Checkpoint Usage

**Scenario:** Multi-day feature implementation.

**Day 1: Requirements & Planning**
```
Turns 1-25: Requirements analysis, Geist analysis, planning
Context: 70K tokens
Action: Create checkpoint before implementation
```

**Checkpoint 1:**
```markdown
# Checkpoint: User Authentication - Planning Complete

## Decisions
- JWT authentication with 15-min expiration
- PostgreSQL for user storage
- Rate limiting: 5 attempts per minute

## Next Phase
Implementation (fresh agent with 70K available context)
```

**Day 2: Implementation**
```
Turns 1-30: Code implementation (fresh agent from checkpoint)
Context: 85K tokens
Action: Create checkpoint before testing
```

**Checkpoint 2:**
```markdown
# Checkpoint: User Authentication - Implementation Complete

## Completed
- UserService.authenticate() implemented
- JWT token generation/validation
- Database integration

## Next Phase
Testing (fresh agent with 85K available context)
```

**Result:** 3-day feature without single context overflow, each phase optimally scoped.

---

## Summary & Decision Tree

### Context Limit Mitigation Decision Tree

```
Is context usage > 70% (140K tokens)?
│
├─ YES → Choose mitigation strategy:
│   │
│   ├─ Long conversation (50+ turns)?
│   │   └─ → Strategy 2: Context Refresh
│   │
│   ├─ Complex implementation (3+ sub-tasks)?
│   │   └─ → Strategy 1: Agent Delegation
│   │
│   ├─ Large file analysis needed?
│   │   └─ → Strategy 3: File References + Strategy 4: Incremental Loading
│   │
│   └─ At milestone completion?
│       └─ → Strategy 5: Strategic Checkpoint
│
└─ NO → Continue with current approach
    │
    └─ But monitor and plan ahead:
        - Estimate upcoming operation costs
        - Reserve 40-60K for responses
        - Consider agent delegation for next phase
```

### Key Takeaways

1. **Proactive Management:** Monitor context usage, don't wait for overflow
2. **Agent Delegation:** Most effective for complex work (3+ sub-agents)
3. **Context Refresh:** Essential for conversations > 50 turns
4. **Incremental Loading:** Always prefer targeted reads over full scans
5. **Strategic Checkpoints:** Create resumption points at natural boundaries
6. **Budget Planning:** Reserve 40-60K tokens for responses
7. **Distributed Context:** Optimal range per agent: 60-100K tokens
8. **Refactoring Sweet Spot:** 80-100K tokens for balanced refactoring

### Optimization Patterns Reference

For comprehensive context optimization strategies including parallel execution, strategic refactoring timing, and pre-emptive import management, see:

**[AGENTIC_CODING_OPTIMIZATION.md](../../06-collaborative-construction/AGENTIC_CODING_OPTIMIZATION.md)**

Key patterns from optimization guide:
- **Parallel Execution:** Independent analysis, different docs, separate verification
- **Strategic Refactoring:** Refactor Module A while implementing Module B (milestone-based)
- **Context Budgeting:** Coordination agent ~20K, specialized agents 15-80K each
- **Optimal Ranges:** Refactoring 60-120K, implementation 60-80K, analysis 15-25K

---

**Next Steps:**
- Read [EVOLVING_CAPABILITIES.md](./EVOLVING_CAPABILITIES.md) to understand how context limits change over time
- Review [AGENTIC_CODING_OPTIMIZATION.md](../../06-collaborative-construction/AGENTIC_CODING_OPTIMIZATION.md) for advanced optimization patterns
- See [WHAT_IS_CONTEXT.md](./WHAT_IS_CONTEXT.md) for context window fundamentals
