---
name: initiate-team-review
description: |
  Orchestrate a multi-agent, read-only code review by spawning specialist reviewer
  subagents in parallel, then synthesize their findings into a single consolidated
  report. Use when the user mentions team review, initiate review, multi-agent review,
  comprehensive review, peer review, panel review, or review with specialists. Discovers
  which reviewer agents are installed, suggests the relevant ones for the changed files,
  spawns them in parallel, and produces a prioritized findings report. Does not modify
  code.
allowed-tools: [Read, Glob, Grep, Bash, Task]
---

# Initiate Team Review

Run a multi-agent code review with specialist reviewers and produce a consolidated,
prioritized findings report. Every reviewer runs **read-only** — this skill investigates
and reports; it does not change code.

## How It Works

Specialist reviewer subagents each own a review lens (security, performance, frontend,
architecture, product, UX, devops/CI, API design, reliability). This skill points them
at the changed code, runs them in parallel, deduplicates and prioritizes what they find,
and hands back one report.

The available roster depends on which reviewer agents are installed in the environment
(under `agents/` or `.claude/agents/`). Discover them first; only spawn agents that
actually exist. Portable reviewers this skill expects (any subset may be present):

- `security-auditor`
- `performance-engineer`
- `frontend-architect`
- `technical-architect`
- `product-leader`
- `ux-usability-reviewer`
- `devops-cicd-specialist`
- `api-design-reviewer`
- `sre-reliability-engineer`

## Arguments

The invocation may include a scope hint:

- Empty: review the current branch's diff against the integration branch.
- `branch`: explicit branch diff against the integration branch.
- `conversation`: review files discussed in the current conversation.
- `<path>`: review only files under that path.

## Step 1: Gather Context (lightweight)

Collect just enough context to brief the reviewers. Do NOT read agent files, decision
records, or full diffs — the agents self-serve those.

**Determine the integration branch** (the branch feature work merges into):

```bash
git symbolic-ref refs/remotes/origin/HEAD 2>/dev/null | sed 's@^refs/remotes/origin/@@'
```

Common values: `main`, `master`, `develop`, `staging`. Call it `<base>`.

**Collect the change set:** current branch name, changed-file list (names only), a
compact commit log, and whether there are uncommitted changes.

```bash
git rev-parse --abbrev-ref HEAD
git diff --name-only <base>...HEAD
git log <base>..HEAD --oneline
git status --porcelain=v1
```

If the scope is a path, restrict the file list to that path. If `conversation`, gather
file paths from the conversation instead.

**Write a 2-3 sentence conversation summary** capturing intent, key decisions/trade-offs,
and any known issues.

**Find the feature plan, if any.** Look for a plan/spec matching the branch (e.g. under
`docs/`, `plans/`, `specs/`, or a linked ticket). Note the path; don't read the full
contents.

Handle edge cases sensibly: warn if on the integration branch itself, error on detached
HEAD, note if there are no changes.

## Step 2: Discover the Roster and Select Reviewers

List installed reviewer agents (glob `agents/*.md` and `.claude/agents/*.md`), then map
the changed files to relevant reviewers. Only suggest agents that are installed.

| Changed-file signal | Likely relevant reviewers |
|---|---|
| Auth, login, session, token, permissions code | security-auditor, api-design-reviewer |
| API routes / controllers / endpoints | api-design-reviewer, security-auditor |
| Services / business-logic layer | performance-engineer, technical-architect |
| Data models, schema, migrations | technical-architect, performance-engineer, security-auditor |
| External integrations / third-party clients | sre-reliability-engineer, security-auditor |
| Frontend pages / components / hooks | frontend-architect, ux-usability-reviewer |
| Forms, modals, data-driven views | ux-usability-reviewer, frontend-architect |
| Background jobs / pipelines / workers | sre-reliability-engineer, performance-engineer |
| CI workflows, Dockerfiles, deploy config, IaC | devops-cicd-specialist, sre-reliability-engineer |
| Anything touching a documented feature plan | product-leader |

**Always-relevant when installed:**
- `technical-architect`: cross-cutting architecture, coupling, decision-record compliance.
- `product-leader`: when a feature plan exists.

If a reviewer for a relevant lens is not installed, note the gap in the final report
("no security reviewer installed — security lens not covered") so the user knows what
wasn't checked.

Present the suggested reviewers (recommended ones marked) and let the user confirm or
adjust the selection. If the user gave no opportunity to choose (non-interactive), run
the recommended set.

## Step 3: Spawn Reviewers in Parallel (read-only)

Spawn each selected reviewer via the `Task` tool using its agent name as the subagent
type — the agent's own definition loads automatically. Pass only the review context, not
instructions on how to review; the agents know their job.

Batch up to ~8 in parallel; wait for a batch to finish before starting the next. Use this
prompt template per reviewer:

```
Task(
  description: "{agent-name} review",
  subagent_type: "{agent-name}",
  prompt: "Review the changes on branch `{branch}` (compared to `{base}`). This is a
read-only review — do not modify any files.

Changed files:
{file list — names only}

Recent commits:
{compact commit log}

Context: {2-3 sentence conversation summary}

Feature plan: {path if exists, or 'none'}

Focus on files relevant to your expertise. Read the files, grep for patterns, and
explore as needed. Report findings with file paths and line numbers, each with a
severity (critical / high / medium / low) and a concrete suggested fix."
)
```

If an agent fails or returns nothing, note it and continue.

## Step 4: Synthesize the Findings Report

Collect all reviewer outputs and produce one consolidated report.

- **Deduplicate:** the same issue flagged by multiple reviewers becomes one finding,
  credited to all, at the highest severity reported.
- **Prioritize:** group by severity (Critical → High → Medium → Low). Within severity,
  lead with anything that breaks correctness, security, or data integrity.
- **Categorize each finding:**
  - **Act Now** (the default — most findings): has a concrete fix, implementable without
    a major architectural decision.
  - **Plan Later** (high bar): requires a significant architectural decision spanning many
    layers or its own development cycle (e.g. "redesign the job pipeline", "migrate the
    auth system").
- **Note coverage gaps:** list any relevant lens that had no installed reviewer.

**Report shape:**

```
# Team Review — {branch}

## Summary
{1-3 sentences: overall health, count by severity, biggest risks}

## Act Now
### Critical
- [security-auditor] {finding} — {file}:{line} — {suggested fix}
### High
- ...
### Medium / Low
- ...

## Plan Later
- {finding} — {why it needs its own cycle}

## Coverage
- Reviewers run: {list}
- Lenses not covered (no agent installed): {list or "none"}

## Raw reviewer output
{collapsed/condensed per-agent output for traceability}
```

Write the report inline as the skill's output. If the user wants it persisted, save it to
a review file (e.g. `docs/reviews/<branch>-<date>.md`) — only when asked.

## Principles

1. **Read-only.** No file edits. The deliverable is the findings report.
2. **Agents are autonomous experts.** Point them at the work, not how to do it; they read
   their own decision records and decide what to look for.
3. **Orchestrator stays lean.** Don't read agent files, decision records, or full diffs —
   the agents self-serve. Preserve context budget for synthesis.
4. **Roster is dynamic.** Only spawn installed agents; report uncovered lenses.
5. **Most findings are Act Now.** Reserve Plan Later for genuine architectural decisions.
6. **Deduplicate with credit.** Merge overlapping findings, keep the highest severity.
