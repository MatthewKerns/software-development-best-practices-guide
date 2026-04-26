---
name: refactor-detector
description: Analyzes code for structural quality issues and produces a machine-readable smell report. Use when reviewing code quality, before refactoring, when code feels wrong or bloated, during technical debt assessment, or when planning refactoring work. ALSO trigger proactively when the same bug or issue keeps recurring in a file or module — repeated bugs are a strong signal that code structure is obscuring the root cause and a smell analysis would help. Triggers on phrases like "analyze for smells", "code quality check", "what's wrong with this code", "find refactoring targets", "technical debt scan", "we keep hitting this bug", "this area keeps breaking". This skill focuses ONLY on detection — it does not plan or execute refactoring. Its output is a structured JSON smell report consumed by refactor-planner.
allowed-tools: [Read, Grep, Glob]
---

# Refactor Detector

Analyze code for structural quality issues and produce a structured smell report. Your sole responsibility is **detection** — identifying what's wrong and where. You do NOT plan fixes or execute refactoring.

## How Detection Works

Code smells are surface indicators of deeper structural problems. A 600-line component isn't bad because it's long — it's bad because length correlates with multiple responsibilities, tangled dependencies, and untestable logic. Your job is to find these indicators, measure them, and classify their severity so the downstream planner can make informed tradeoff decisions.

## Recurring Bugs as a Smell Signal

When the same area of code keeps producing bugs or the same issue keeps coming back after being "fixed," that's often the strongest smell signal of all. The bug isn't the problem — the code structure is making the bug invisible or easy to reintroduce. In these cases:

1. **Identify the bug cluster** — which files/functions are involved in the recurring issue?
2. **Analyze why the structure hides the bug** — is it because responsibilities are tangled (Divergent Change)? Because the fix requires changes in too many places (Shotgun Surgery)? Because side effects are hidden in unexpected locations (Side Effects in setState)?
3. **Classify the structural cause** — map the recurring bug to a smell from the catalog
4. **Elevate severity** — a smell that's causing actual bugs is at least HIGH, often CRITICAL, regardless of what the metric-based severity would be

## Detection Process

### 1. Scope the Analysis

Determine what to analyze:
- If the user points to specific files, analyze those
- If the user says "analyze this module/directory", glob for source files and analyze each
- If no scope is given, look at git-modified files or ask

### 2. Collect Metrics Per File

For each file, measure:

| Metric | How to Measure | Threshold |
|--------|---------------|-----------|
| Lines of Code | Count non-blank, non-comment lines | Component >150, Service >300, Hook >200 |
| Method/Function Count | Count exported + internal functions | >10 public methods |
| Max Function Length | Longest function body | >50 lines |
| Max Nesting Depth | Deepest indentation level | >3 levels |
| Parameter Count | Largest parameter list | >3 params |
| Import Count | Number of import statements | >15 imports |
| Dependency Fan-out | Distinct modules imported | >8 modules |

### 3. Detect Smells

Check each file against the smell catalog in `references/smell-catalog.md`. For each detected smell:

1. **Classify** — which smell pattern does this match?
2. **Locate** — exact file:line range
3. **Measure** — the metric that triggered detection (e.g., "87 lines, threshold 50")
4. **Severity** — CRITICAL, HIGH, MEDIUM, or LOW based on the priority matrix
5. **Evidence** — the specific code patterns that indicate this smell

Read `references/smell-catalog.md` for the complete catalog of smells, their detection criteria, and severity classification.

### 4. Identify Cross-File Patterns

After individual file analysis, look for:
- **Duplication across files** — similar logic in multiple places
- **Shotgun surgery** — would changing one concept require touching many files?
- **Feature envy** — files that import heavily from one module (they might belong there)
- **Circular dependencies** — A imports B imports A

### 5. Produce the Smell Report

Output a structured report in this exact format:

```json
{
  "analysis_scope": "description of what was analyzed",
  "timestamp": "ISO 8601",
  "files_analyzed": 5,
  "summary": {
    "total_smells": 12,
    "by_severity": { "CRITICAL": 1, "HIGH": 3, "MEDIUM": 5, "LOW": 3 },
    "top_3_priorities": ["file1.ts: God Component", "file2.ts: Monolithic Service", "file3.ts: Duplicated Logic"]
  },
  "files": [
    {
      "path": "src/components/BigComponent.tsx",
      "metrics": {
        "loc": 602,
        "functions": 15,
        "max_function_length": 87,
        "max_nesting": 4,
        "max_params": 6,
        "imports": 18
      },
      "smells": [
        {
          "id": "smell-001",
          "type": "GOD_COMPONENT",
          "severity": "HIGH",
          "location": { "start_line": 1, "end_line": 602 },
          "metric": "602 LOC (threshold: 150)",
          "evidence": "Handles upload UI, drag-drop, file validation, API calls, polling, status rendering, and delete operations",
          "responsibilities": ["upload UI", "drag-drop handling", "file validation", "API communication", "polling", "status rendering", "delete operations"],
          "suggested_refactoring": "EXTRACT_CLASS"
        }
      ]
    }
  ],
  "cross_file_patterns": [
    {
      "type": "DUPLICATION",
      "locations": ["src/a.ts:30-45", "src/b.ts:25-40"],
      "description": "Retry logic duplicated across services"
    }
  ]
}
```

Also produce a human-readable summary in this format:

```
CODE SMELL ANALYSIS: [Scope Description]

METRICS SUMMARY
---------------
Files analyzed: N
Total smells: N (CRITICAL: N, HIGH: N, MEDIUM: N, LOW: N)

TOP PRIORITIES
--------------
1. [SEVERITY] file.ts — Smell Type (metric)
2. [SEVERITY] file.ts — Smell Type (metric)
3. [SEVERITY] file.ts — Smell Type (metric)

DETAILED FINDINGS
-----------------
[Per-file breakdown with evidence]
```

## Important Boundaries

- Do NOT suggest specific refactoring plans — that's refactor-planner's job
- Do NOT execute any code changes — that's refactor-executor's job
- Do NOT validate SOLID compliance — that's refactor-validator's job
- Your output should be facts and measurements, not opinions about how to fix things
- When you note a "suggested_refactoring" in the JSON, use the catalog name (EXTRACT_METHOD, EXTRACT_CLASS, MOVE_METHOD, etc.) — this is a classification hint, not a plan

## References

- Read `references/smell-catalog.md` for the complete smell catalog with detection criteria and severity matrix
