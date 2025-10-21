# What is Context? Understanding LLM Memory and Information Retrieval

## Overview

When working with Large Language Models (LLMs) like Claude, understanding **context** is fundamental to effective agentic coding. Context is the LLM's "working memory" during a conversation—everything it can "see" and reference when generating responses. Unlike humans who retain long-term memories across sessions, LLMs have a fixed-size context window that resets between conversations.

This guide explains what context is, how it works, why it matters for software development, and how to manage it effectively.

## Context Window Basics

### What is a Context Window?

A **context window** is the maximum amount of information an LLM can process and remember during a single conversation. Think of it as the LLM's "working memory" or "attention span."

**Key Characteristics:**
- **Fixed Size**: Each model has a maximum context capacity (e.g., Claude Sonnet: 200,000 tokens)
- **Temporary**: Context only exists for the duration of one conversation session
- **Sequential**: Information flows chronologically—earlier messages are as important as recent ones
- **Exhaustible**: Once full, older information may be truncated or compressed

**Human Analogy:**
Imagine reading a long novel while trying to answer questions about it. Your "context window" is how much of the novel you can actively hold in your mind at once. If the novel is too long, you might forget details from early chapters when you reach the end.

### Measured in Tokens, Not Words

Context capacity is measured in **tokens**, not words, characters, or lines of code. This is a critical distinction for developers.

**Token Definition:**
A token is a chunk of text that the LLM's tokenizer breaks language into. Tokens can be:
- Whole words: `"function"` = 1 token
- Parts of words: `"tokenization"` = 2-3 tokens (`token`, `ization`)
- Punctuation: `";"` = 1 token
- Spaces and newlines: Often 1 token each

**Why Tokens Matter:**
Different types of content consume tokens at different rates:
- Natural language: ~4 characters per token (rough average)
- Code: ~3-4 characters per token (varies by language)
- JSON/structured data: ~2-3 characters per token (lots of punctuation)

### Example: Code Tokenization

Let's see how a simple function breaks down into tokens:

```javascript
function validateEmail(email) {
  const regex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
  return regex.test(email);
}
```

**Token Breakdown (approximate):**
```
function        → 1 token
validateEmail   → 2-3 tokens (validate + Email)
(               → 1 token
email           → 1 token
)               → 1 token
{               → 1 token
\n              → 1 token
const           → 1 token
regex           → 1 token
=               → 1 token
/^[^\s@]+...$/  → 8-12 tokens (regex pattern)
;               → 1 token
\n              → 1 token
return          → 1 token
regex           → 1 token
.               → 1 token
test            → 1 token
(               → 1 token
email           → 1 token
)               → 1 token
;               → 1 token
\n              → 1 token
}               → 1 token
```

**Total: ~30-35 tokens** for a 3-line function (~100 characters)

**Key Insight:** A 200K token context window can hold roughly:
- 150,000-180,000 words of plain text
- 10,000-15,000 lines of code (depending on complexity)
- 50-100 medium-sized source files

## What Goes in Context

Every piece of information the LLM "sees" during a conversation consumes context. Understanding what fills your context budget is crucial for effective agentic coding.

### 1. Conversation History

**Every message exchanged between you and the LLM is stored in context:**

- **User messages**: Your questions, instructions, and requests
- **Assistant messages**: The LLM's responses, explanations, and code suggestions
- **Multi-turn context**: The entire conversation thread from start to current message

**Example Context Growth:**
```
Turn 1: User asks question (50 tokens) + Assistant responds (500 tokens) = 550 tokens
Turn 2: User follows up (30 tokens) + Assistant responds (400 tokens) = 430 tokens
Turn 3: User requests code (40 tokens) + Assistant writes code (800 tokens) = 840 tokens

Total accumulated context: 1,820 tokens (and growing with each turn)
```

**Why This Matters:**
Long conversations accumulate context quickly. A 50-turn debugging session can consume 50,000-100,000 tokens just in conversation history before any files are read.

### 2. System Prompts and Instructions

**System-level context includes:**

- **CLAUDE.md**: Project-specific instructions and patterns (often 5,000-15,000 tokens)
- **Built-in prompts**: Tool descriptions, guidelines, safety instructions (10,000-20,000 tokens)
- **Environment info**: Working directory, git status, platform details (200-500 tokens)

**Example from CLAUDE.md:**
```
# Claude Code Instructions - Data Input Pipeline
Python project with LangGraph/LangSmith for email processing...

**IMPORTANT CONTEXT: NO ACTIVE USERS**
- This system is in development with **ZERO active users**
...
```

This single instruction file can consume 10,000+ tokens, but provides crucial context for every decision the LLM makes.

### 3. File Contents (Read Tool)

**When you or the LLM reads a file, its entire content enters context:**

```python
# User: "Read src/utils/email_validator.py"
# LLM uses Read tool → Entire file enters context

# File: 250 lines of Python code
# Token cost: ~3,000-5,000 tokens
```

**Strategic Reading:**
Reading 20 files at 3,000 tokens each = 60,000 tokens consumed. This is why selective reading and glob patterns matter.

**Best Practice:**
```python
# ❌ INEFFICIENT: Read entire codebase
Read("src/module1.py")  # 5,000 tokens
Read("src/module2.py")  # 4,000 tokens
Read("src/module3.py")  # 6,000 tokens
# Total: 15,000 tokens for potentially irrelevant info

# ✅ EFFICIENT: Search first, then read selectively
Grep("def process_email", "src/")  # 50 tokens to find relevant file
Read("src/email_processor.py")     # 4,000 tokens for exact file needed
# Total: 4,050 tokens
```

### 4. Tool Outputs

**Every tool execution result is added to context:**

**Bash Tool Output:**
```bash
# Command: pytest tests/ -v
# Output: 50 lines of test results
# Token cost: ~500-800 tokens
```

**Grep Tool Output:**
```bash
# Pattern: "async def"
# Results: 25 matching files with snippets
# Token cost: ~1,000-2,000 tokens
```

**Glob Tool Output:**
```bash
# Pattern: "**/*.py"
# Results: 150 Python file paths
# Token cost: ~800-1,200 tokens
```

**Accumulated Tool Context:**
A debugging session with 10 bash commands, 5 grep searches, and 3 glob patterns can add 10,000-15,000 tokens before any implementation begins.

### 5. Documentation and External References

**When retrieving documentation or web content:**

- **WebFetch results**: Full web pages converted to markdown (5,000-20,000 tokens per page)
- **API documentation**: Referenced specs and schemas (2,000-10,000 tokens)
- **Error messages and stack traces**: Debugging context (500-2,000 tokens per error)

**Example WebFetch:**
```
WebFetch("https://docs.langchain.com/langgraph/...")
→ Converts HTML to markdown
→ Adds 15,000 tokens to context
→ LLM can now reference this documentation
```

## Context Retrieval: How LLMs Find Information

Understanding how LLMs retrieve information from context explains why some queries work better than others.

### Attention Mechanisms

LLMs use **attention mechanisms** to "search" through context and identify relevant information for the current query.

**How Attention Works:**
1. **Query Formation**: When asked a question, the LLM creates an internal "query" representation
2. **Key Matching**: Every piece of context has "keys" (semantic markers)
3. **Attention Scores**: The model calculates relevance scores between query and context keys
4. **Weighted Retrieval**: Higher-scoring context segments influence the response more

**Simplified Example:**
```
User Query: "What's the email validation regex?"

Context Segments:
[1] function validateEmail(email) { ... }        → Attention Score: 0.95 (HIGH)
[2] const regex = /^[^\s@]+@[^\s@]+$/;          → Attention Score: 0.98 (HIGHEST)
[3] async def send_email(to, subject): ...      → Attention Score: 0.30 (LOW)
[4] # Email validation using regex patterns     → Attention Score: 0.85 (HIGH)

Response focuses on segments [2] and [1] because of high attention scores.
```

### Why Retrieval Fails

**Common Retrieval Failure Scenarios:**

**1. Needle in a Haystack**
```
Context: 100,000 tokens of code
Critical Info: 50-token function buried in middle
Problem: Low attention score due to surrounding "noise"

Solution: Use Grep to surface relevant code first
```

**2. Context Truncation**
```
Context Window: 200,000 tokens
Conversation + Files: 210,000 tokens
Problem: Oldest 10,000 tokens truncated (may contain critical setup info)

Solution: Refresh context or summarize early conversation
```

**3. Semantic Distance**
```
User Query: "Why is the API slow?"
Context: Detailed code but no performance metrics or profiling data
Problem: No semantically relevant context to retrieve

Solution: Add performance data via tool execution (Bash: time commands)
```

**4. Conflicting Information**
```
Context:
[Earlier] "Use sync database calls"
[Later] "Use async database calls"

Problem: Conflicting instructions → LLM may retrieve wrong guidance

Solution: Update CLAUDE.md to clarify current approach
```

### Retrieval Best Practices

**✅ Make Information Retrievable:**

1. **Use Clear Headings and Markers**
```python
# ✅ GOOD: Easy to retrieve
## Email Validation Logic
def validate_email(email: str) -> bool:
    """Validates email format using regex."""
    ...

# ❌ BAD: Buried in unstructured code
def x(e):  # Email check
    ...
```

2. **Add Context Markers**
```python
# ✅ GOOD: Semantic markers aid retrieval
# CRITICAL: This function handles payment processing
# SECURITY: Validates all inputs before processing
def process_payment(amount, card_token):
    ...

# ❌ BAD: No semantic markers
def f(a, c):
    ...
```

3. **Provide Cross-References**
```markdown
✅ GOOD: Helps LLM connect related concepts
See ASYNC_PATTERNS.md for background on asyncio usage.
Related: EMAIL_VALIDATION.md, API_INTEGRATION.md

❌ BAD: Isolated information without connections
Here's some code...
```

## Context Management Strategies

Effective context management is critical for long-running agentic coding sessions.

### Strategy 1: Keep Context Focused

**Goal**: Only include information relevant to the current task.

**Techniques:**

**Use Grep Before Read:**
```python
# ❌ INEFFICIENT: Read everything
for file in glob("**/*.py"):
    Read(file)  # May read 50+ files (150,000 tokens)

# ✅ EFFICIENT: Search first, read second
Grep("class EmailValidator", "**/*.py")  # Identify relevant file
Read("src/validators/email.py")          # Read only what's needed
```

**Selective Tool Output:**
```bash
# ❌ VERBOSE: Full test output (5,000 tokens)
pytest tests/ -v

# ✅ CONCISE: Summary only (500 tokens)
pytest tests/ -q --tb=short
```

**Targeted Questions:**
```
❌ BROAD: "Explain the entire codebase"
   → Forces LLM to read/process everything

✅ FOCUSED: "Explain the email validation logic in src/validators/email.py"
   → LLM reads only relevant file
```

### Strategy 2: Use References Instead of Full Content

**Goal**: Reference information without loading it into context.

**File Path References:**
```markdown
✅ EFFICIENT: Reference without reading
The email validator is in `src/validators/email.py`.
The tests are in `tests/test_email_validator.py`.

Token cost: ~20 tokens

❌ INEFFICIENT: Load full content
Here's the email validator code: [paste 200 lines]
Here are the tests: [paste 300 lines]

Token cost: ~8,000 tokens
```

**Documentation Links:**
```markdown
✅ EFFICIENT: Link to docs
See LangGraph documentation at https://docs.langchain.com/langgraph

Token cost: ~15 tokens

❌ INEFFICIENT: Copy entire doc section
Here's the full LangGraph documentation: [paste 5,000 words]

Token cost: ~7,000 tokens
```

**Summarization:**
```markdown
✅ EFFICIENT: Summarize key points
The codebase uses:
- LangGraph for workflows
- Async patterns throughout
- TDD with 85%+ coverage

Token cost: ~30 tokens

❌ INEFFICIENT: Full architectural overview
[Paste entire ARCHITECTURE.md - 10,000 tokens]
```

### Strategy 3: Periodic Context Refresh

**Goal**: Reset context when it becomes cluttered or contradictory.

**When to Refresh:**
- After 30-50 conversation turns
- When debugging reveals conflicting information
- Before starting a new major feature
- When context exceeds 150,000 tokens

**How to Refresh:**

**1. Start New Conversation**
```markdown
Old conversation: 180,000 tokens (cluttered with debugging history)
→ Start fresh conversation
→ New context: 20,000 tokens (clean slate)
→ Bring only essential context forward via CLAUDE.md
```

**2. Summarize and Continue**
```markdown
User: "Summarize the key decisions from this conversation"
LLM: "Summary: [500 tokens of key points]"

User: "Let's continue with these decisions in mind" (start new conversation)
→ Reference summary in new conversation (500 tokens vs 180,000 tokens)
```

**3. Extract to Documentation**
```markdown
During conversation:
- Discover 5 architectural decisions (scattered across 20,000 tokens)

After conversation:
- Write ADR documenting decisions (1,500 tokens)
- Future conversations reference ADR (minimal context)
```

### Strategy 4: Optimize Tool Usage

**Goal**: Minimize token consumption from tool outputs.

**Bash Tool Optimization:**
```bash
# ❌ VERBOSE: Outputs 10,000 tokens
langgraph dev --verbose

# ✅ CONCISE: Outputs 500 tokens
langgraph dev --quiet 2>&1 | grep -E "(ERROR|WARNING|Started)"
```

**Grep Tool Optimization:**
```bash
# ❌ UNFILTERED: Returns 100 matches (8,000 tokens)
Grep("import", "**/*.py")

# ✅ FILTERED: Returns 10 matches (800 tokens)
Grep("from langgraph.prebuilt import", "src/workflow/")
```

**Read Tool Optimization:**
```python
# ❌ READ ENTIRE FILE: 5,000 tokens
Read("src/large_module.py")

# ✅ READ SPECIFIC SECTION: 500 tokens
Read("src/large_module.py", offset=100, limit=50)  # Lines 100-150 only
```

### Strategy 5: Leverage Context Budgeting

**Goal**: Allocate context budget across multiple agents or tasks.

**Context Budget Example (200K tokens):**
```
System Prompts + CLAUDE.md:     20,000 tokens  (10%)
Conversation History:           30,000 tokens  (15%)
Essential Files (5 files):      25,000 tokens  (12.5%)
Tool Outputs:                   15,000 tokens  (7.5%)
Reserve for Implementation:    110,000 tokens  (55%)

Total Used:  200,000 tokens (100%)
```

**Multi-Agent Context Distribution:**
```
Coordination Meta-Agent:        20,000 tokens  (orchestration only)
Security Validator Agent:       40,000 tokens  (security analysis + code)
Code Implementor Agent:         60,000 tokens  (implementation + tests)
Documentation Agent:            30,000 tokens  (docs + examples)

Total Parallel Context: 150,000 tokens across 4 agents
vs Sequential Context: 200,000 tokens single agent
```

## Practical Context Management Tips

### For Developers Using Agentic Coding

**1. Start with Context-Efficient Queries**
```
❌ "Review my entire codebase and suggest improvements"
   → Requires reading 100+ files (300,000+ tokens) - exceeds window

✅ "Review src/validators/email.py for security issues"
   → Reads 1 file (~3,000 tokens) - focused and efficient
```

**2. Use Incremental Disclosure**
```
Turn 1: "What validation libraries does the project use?"
        → LLM uses Grep (500 tokens context)

Turn 2: "Show me the email validation implementation"
        → LLM reads specific file (3,000 tokens context)

Turn 3: "Add phone validation following the same pattern"
        → LLM has relevant context (4,000 tokens total)

vs

Turn 1: "Implement phone validation"
        → LLM must search entire codebase (50,000+ tokens)
```

**3. Maintain Context Continuity**
```
✅ GOOD: Clear references to prior context
"Based on the email validator we just reviewed, add phone validation"
→ LLM knows to reference recent conversation

❌ BAD: Ambiguous context switches
"Add phone validation" (after discussing unrelated database code)
→ LLM may miss relevant validation patterns
```

**4. Monitor Context Consumption**
```python
# After reading multiple files, check context load
User: "How many files have we read so far?"
LLM: "We've read 8 files totaling approximately 35,000 tokens"

# Decide whether to continue or refresh
If tokens > 150,000:
    → Start new conversation with summary
Else:
    → Continue current conversation
```

### For Teams Building Agentic Systems

**1. Design Context-Aware Architectures**
```python
# ✅ EFFICIENT: Agents have focused contexts
security_agent.context = ["security_guidelines.md", "auth_code.py"]
# ~10,000 tokens

# ❌ INEFFICIENT: Agents have overlapping full contexts
all_agents.context = ["entire_codebase/*"]
# ~500,000 tokens per agent (exceeds window)
```

**2. Implement Context Budgeting**
```python
CONTEXT_BUDGET = 200_000  # tokens

def allocate_context(task_complexity):
    if task_complexity == "simple":
        return {
            "system": 10_000,
            "history": 20_000,
            "files": 30_000,
            "reserve": 140_000
        }
    elif task_complexity == "complex":
        return {
            "system": 20_000,
            "history": 50_000,
            "files": 80_000,
            "reserve": 50_000
        }
```

**3. Create Context-Efficient Documentation**
```markdown
✅ EFFICIENT: Modular documentation with clear structure
/docs
  /api - API reference (3,000 tokens per module)
  /guides - Implementation guides (2,000 tokens per guide)
  /architecture - High-level overviews (5,000 tokens)

→ LLM reads only relevant docs for task

❌ INEFFICIENT: Monolithic documentation
/docs
  EVERYTHING.md (50,000 tokens)

→ LLM must load entire doc even for small queries
```

## Context and LLM Capabilities

Understanding context limitations helps set realistic expectations for what LLMs can accomplish.

### What LLMs Can Do with Context

**✅ Excellent Context Utilization:**
- Retrieve specific functions from recently read files
- Apply patterns from CLAUDE.md consistently
- Reference conversation history for follow-up questions
- Connect related concepts across multiple files (if in context)
- Generate code following established codebase patterns

**Example:**
```
Context: CLAUDE.md (async patterns) + email_validator.py (validation pattern)

User: "Create a phone validator"

LLM can:
- Apply async patterns from CLAUDE.md ✓
- Follow validation structure from email_validator.py ✓
- Use same error handling approach ✓
- Maintain consistent style ✓

Result: Context-aware, pattern-consistent implementation
```

### What LLMs Cannot Do with Context

**❌ Context Limitations:**
- Remember information from previous conversations (no long-term memory)
- Access files not explicitly read into context
- "Know" about codebase changes made outside conversation
- Retrieve information beyond context window (truncated early messages)
- Maintain context across multiple simultaneous conversations

**Example:**
```
Previous Conversation: Implemented feature X with approach Y

New Conversation (next day):
User: "Update feature X"

LLM:
- Has NO memory of previous conversation ✗
- Cannot reference approach Y unless re-provided ✗
- Must re-read all relevant files ✗

Solution: Provide context via CLAUDE.md or ADR documentation
```

## Summary: Context Management Checklist

**For Every Agentic Coding Session:**

✅ **Before Starting:**
- [ ] Estimate context budget needed for task
- [ ] Identify essential files and documentation
- [ ] Check CLAUDE.md is up-to-date with current patterns

✅ **During Development:**
- [ ] Use Grep/Glob before Read (search first, load second)
- [ ] Read only relevant files (avoid "just in case" reading)
- [ ] Request concise tool outputs (--quiet, --summary flags)
- [ ] Monitor context accumulation (ask LLM for token estimates)

✅ **For Long Sessions:**
- [ ] Refresh context after 30-50 turns
- [ ] Summarize key decisions before context refresh
- [ ] Extract learnings to documentation (reduce future context needs)
- [ ] Start new conversations for new features (clean slate)

✅ **For Multi-Agent Systems:**
- [ ] Allocate context budget across agents
- [ ] Design agents with focused, non-overlapping contexts
- [ ] Use coordination agent with minimal context (orchestration only)
- [ ] Share context via artifacts (JSON, Markdown) not full histories

## Conclusion

Context is the foundation of effective LLM-driven development. By understanding how context windows work, what consumes context tokens, and how LLMs retrieve information, you can:

- **Design more efficient agentic workflows** that maximize context utility
- **Avoid context exhaustion** in complex, long-running sessions
- **Improve LLM accuracy** by providing focused, relevant context
- **Scale agentic systems** through intelligent context distribution

The key principle: **Context is finite and precious—use it strategically.**

## Cross-References

- **[WHAT_IS_AN_LLM.md](./WHAT_IS_AN_LLM.md)** - How LLMs process context and generate responses
- **[CONTEXT_LIMITS.md](./CONTEXT_LIMITS.md)** - Technical constraints and boundaries of context windows
- **[EFFICIENT_CONTEXT_TRANSFER.md](../context-filling-strategies/EFFICIENT_CONTEXT_TRANSFER.md)** - Advanced strategies for context optimization
- **[AGENTIC_CODING_OPTIMIZATION.md](../optimization/AGENTIC_CODING_OPTIMIZATION.md)** - Context budgeting in multi-agent systems

---

**Version:** 1.0.0
**Last Updated:** 2025-10-21
**Author:** Software Development Best Practices Guide
**Related ADRs:** ADR_005 (Tool Pattern), ADR_007 (Context Management)
