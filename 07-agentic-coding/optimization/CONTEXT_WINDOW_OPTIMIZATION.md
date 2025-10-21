# Context Window Optimization

**Note:** This topic is comprehensively covered in **[Agentic Coding Optimization](AGENTIC_CODING_OPTIMIZATION.md)**.

---

## Quick Reference

For detailed coverage of context window optimization, see the comprehensive guide: **[AGENTIC_CODING_OPTIMIZATION.md](AGENTIC_CODING_OPTIMIZATION.md)**

### Core Topics Covered

**Context Window Management Strategy** (Lines 14-75)
- Agent delegation pattern (fresh isolated contexts)
- Context budgeting formula (<200K per turn)
- Communication via artifacts (not large content copies)
- Optimal refactoring timing: 60-120K context usage

**Key Formula:**
```
Total Context = Coordination Agent (~20K) + Σ(Sub-Agent Contexts)
Target: <200K per conversation turn
Strategy: Distribute across N specialized agents in parallel
```

**Optimal Refactoring Window:**
```
Context Window Zones:
0K -------- 60K -------- 120K -------- 180K -------- 200K
│  Too Early │  OPTIMAL   │  Acceptable  │  Too Late   │
│  (No       │  (Rich     │  (Limited    │  (Auto-     │
│   patterns)│  context + │   headroom)  │  compact)   │
│            │  headroom) │              │             │

Sweet Spot: 60-120K context usage
• Rich enough: Sufficient patterns for DRY recognition
• Safe enough: 80-140K headroom prevents overflow
• Efficient: Completes before auto-compacting
```

**Time Efficiency via Strategic Parallelization** (Lines 87-114)
- Independent tasks → Parallel execution
- Dependent tasks → Sequential execution
- Hybrid execution pattern for implementation phases

**Strategic Refactoring During Implementation** (Lines 137-441)
- Refactor completed Module A while implementing Module B
- Checkpoint-based refactoring at milestones
- Pre-emptive import management (update before removing code)
- Saves 30-40% time vs sequential approach

**Context Budgeting Examples** (Lines 674-759)
- New feature implementation (single vs multi-agent)
- Large codebase refactoring (strategic approach)
- Budget allocation by phase

---

## When to Read the Full Guide

Read **[AGENTIC_CODING_OPTIMIZATION.md](AGENTIC_CODING_OPTIMIZATION.md)** when you need:

✅ **Parallel vs Sequential Decisions:**
- Decision matrix for parallelization (lines 118-133)
- Quick reference decision tree (lines 836-870)

✅ **Strategic Refactoring Patterns:**
- Continuous refactoring workflow (lines 139-173)
- Milestone-based refactoring (lines 429-441)
- Pre-emptive import management (lines 175-307)

✅ **Context Budget Planning:**
- Phase-based context allocation
- Agent specialization strategies
- Incremental loading patterns (lines 525-573)

✅ **Multi-Agent Coordination:**
- Coordination meta-agent patterns
- Sub-agent context distribution
- Artifact communication (lines 21-24)

✅ **Anti-Patterns to Avoid:**
- Context window anti-patterns (lines 765-778)
- Time efficiency anti-patterns (lines 780-798)

---

## Quick Start Checklist

**For Context Window Management:**
- [ ] Estimate context before operations
- [ ] Keep single agent context <80K for safety
- [ ] Reserve 40-60K headroom for responses
- [ ] Use file references, not full content copies
- [ ] Spawn fresh agents when approaching 150K

**For Parallel Execution:**
- [ ] Identify independent tasks (analysis, verification, docs)
- [ ] Check for file conflicts (same files = sequential)
- [ ] Check for data dependencies (output needed = sequential)
- [ ] Maximize parallelization where safe

**For Strategic Refactoring:**
- [ ] Check context usage (60-120K = optimal window)
- [ ] Refactor completed modules while implementing new ones
- [ ] Search all imports before extracting code
- [ ] Update imports BEFORE removing old code
- [ ] Use checkpoint-based refactoring at milestones

---

## See Also

**Related Optimization Topics:**
- **[PARALLEL_EXECUTION_PATTERNS.md](PARALLEL_EXECUTION_PATTERNS.md)** - Decision frameworks for parallelization
- **[HUMAN_COMPUTE_TIME_OPTIMIZATION.md](HUMAN_COMPUTE_TIME_OPTIMIZATION.md)** - Where humans add the most value

**Context Management:**
- **[../context/CONTEXT_LIMITS.md](../context/CONTEXT_LIMITS.md)** - Understanding constraints
- **[../context/WHAT_IS_CONTEXT.md](../context/WHAT_IS_CONTEXT.md)** - Context window basics

**Context Filling:**
- **[../context-filling-strategies/EFFICIENT_CONTEXT_TRANSFER.md](../context-filling-strategies/EFFICIENT_CONTEXT_TRANSFER.md)** - Best practices for providing context

---

**Full Guide:** [AGENTIC_CODING_OPTIMIZATION.md](AGENTIC_CODING_OPTIMIZATION.md) (~932 lines, comprehensive coverage)

**Version:** 1.0.0
**Last Updated:** 2025-10-21
**Status:** Active (Redirect to comprehensive guide)
