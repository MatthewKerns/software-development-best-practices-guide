---
name: prod-deploy-review
description: |
  Pre-production GO/NO-GO gate. Classifies a change by BLAST RADIUS, spawns only the
  reviewer subagents that radius warrants, runs the deterministic checks agents cannot do
  (staging parity, rollback, served-artefact verification), and emits a verdict with
  evidence attached. Use before any production deploy, or when the user says
  "is this safe to deploy", "prod deploy check", "pre-deploy review",
  "risk of deploying this", "check before we ship", "what could this break",
  or "prod-deploy-review". Reads
  docs/RELEASE_PIPELINE.md for project facts. It reviews and gates; it NEVER deploys — hand
  off to release-deploy-prod once the verdict is GO.
allowed-tools: [Read, Bash, Grep, Glob, Task]
---

# Pre-deploy review — blast radius first, then the right lenses

Stage 3.5 of the release pipeline: between `release-queue` and `release-deploy-prod`.

`initiate-team-review` asks *is this code good?* This asks a different question: **is it safe
to ship this, now, to this environment, and can we get back?** A change can be excellent code
and still be a bad deploy — unexercised against real data, unrecoverable, or shipping beside a
migration nobody read.

This is the executable form of the pre-deployment gate described in
`09-production-readiness/README.md` → "Phase 2: Pre-Deployment Validation".

## Reference Resolution

This skill references files in the best-practices guide using relative paths like
`09-production-readiness/PRODUCTION_READINESS_FRAMEWORK.md`. To open them, find the guide repo
root using whichever applies:

- **Project-install:** the guide is a git submodule at `.feature-factory/guide/` from the
  project root. Read references from `<project_root>/.feature-factory/guide/<reference>`.
- **Personal-install:** this SKILL.md is a symlink. The guide repo root is two directories
  above this skill's directory (`<symlink_target>/../..`). Use `realpath` on this SKILL.md if
  you need the absolute path.

If neither resolves, ask the user where the guide repo lives before continuing.

**Read before judging:**

- `09-production-readiness/PRODUCTION_READINESS_FRAMEWORK.md` §5 Deployment & Release —
  **PRIMARY**. The authoritative checklist for CI/CD, rollback, progressive rollout and
  deployment validation, and the source of the severity vocabulary below.
- `09-production-readiness/ROLLBACK_AND_RECOVERY.md` §2.1 Forward-Compatible Migrations — read
  this whenever the blast radius includes schema. Expand/migrate/contract is the pattern; a
  migration that is not forward-compatible is not rollback-safe.

## 🔴 Two rules that make this skill worth running

**This skill never deploys.** Assessment and action stay separate on purpose: an agent that
both judges risk and performs the deploy will talk itself into shipping. It emits a verdict;
a human, or the project's deploy skill, acts on it.

**Absence of evidence is NO-GO, not GO.** "I could not check X" and "X is fine" are different
verdicts. Every check that could not be run is named in the output. A gate that goes green when
it cannot see is worse than no gate.

## Severity

Use the framework's definitions verbatim — do not invent a second vocabulary:

> **Critical:** Launch blocker — will cause major outage, data loss, or security breach
> **High:** Serious issue — will cause frequent problems or degraded user experience
> **Medium:** Important issue — should fix soon but not a launch blocker
> **Low:** Nice-to-have — optimize over time, low immediate risk

Any **Critical** finding is a NO-GO. **High** is GO WITH CONDITIONS at best.

## Step 0 — Establish what and where

Read `docs/RELEASE_PIPELINE.md` → `## Production` (URL, deploy runbook, verification, rollback,
deploy stamp), plus `## Staging`, `## Cadence` and `## Deploy queue`. Deploy facts reconstructed
from memory are how a wrong `rsync` flag destroys content — if a fact is missing, carry it into
`NOT CHECKED` rather than guessing it.

State in one line: the exact commit, the target environment, and how you established both.

Then resolve three things **before** any agent is spawned:

1. **The real diff.** What ships is the commit measured against *what that environment is
   currently running* — not against `main`, and not "the PR". Read the deploy stamp
   (`## Production` → Deploy stamp; semantics in `release-stage-verify` § "Where the stamp
   lives") and diff against that SHA.
2. **⚠️ Squash-merge makes ancestry lie.** A squashed commit carries a different SHA, so
   `merge-base --is-ancestor` and `git cherry` both report present content as missing. Compare
   CONTENT — tree hashes, or a string literal in the artefact. *"N commits behind" is the most
   confident-sounding wrong number available.*
3. **Merged ≠ deployed.** Confirm what the environment runs by reading the artefact, never by
   reading merge state. Six merged PRs sitting undeployed looks identical to six shipped ones
   from the GitHub UI.

## Step 1 — Classify by blast radius

This is what makes lens selection targeted rather than a shotgun. Walk the diff and answer each
with file:line evidence.

| dimension | the question | lenses |
|---|---|---|
| **Data writes** | any `insert` / `update` / `upsert` / `delete` path touched? | `security-auditor`, `technical-architect` |
| **Schema / migration** | DDL, RLS change, or backfill? | `database-migrator` is an ACTION agent, not a review lens — see below |
| **Auth / permissions** | auth flow, token handling, RLS predicate, role check? | `security-auditor` |
| **Money** | debits credits, charges, or spends on a paid API? | `security-auditor`, `product-leader` |
| **External calls** | new/changed third-party call, timeout, retry? | `sre-reliability-engineer` |
| **Deploy machinery** | CI config, container build, IaC, deploy script? | `devops-cicd-specialist` |
| **API surface** | endpoint shape, status codes, pagination, idempotency? | `api-design-reviewer` |
| **Customer-visible output** | copy, prompts, claims — anything a user reads? | `product-leader`, `ux-usability-reviewer` |
| **Query/render cost** | new N+1, unbounded read, re-render path? | `performance-engineer` |
| **Irreversibility** | undoable by redeploying the previous artefact alone? | if no — **Critical**, say so loudly |

**A diff touching no write path is a materially smaller risk than one that does**, and saying
so precisely — *"every edit is in prompt assembly; zero write paths changed"* — is worth more
than a generic "looks fine".

**⚠️ Schema changes have no read-only lens in the roster.** `database-migrator` acts; it does
not review. When the radius includes schema, say plainly that the **data-integrity lens is
uncovered**, apply `ROLLBACK_AND_RECOVERY.md` §2.1 yourself, and never bundle a migration with
an app deploy.

**Declare every uncovered lens.** If a relevant reviewer is not installed, report the gap —
*"no security reviewer installed; security lens not covered"* — rather than omitting it
silently.

## Step 2 — Spawn the selected lenses, in parallel

Glob `agents/*.md` and `.claude/agents/*.md`; **only spawn agents that are installed**. Spawn
via `Task` using the agent name as the subagent type — its definition loads itself. Pass review
context, not instructions on how to review; the agents know their job. Batch up to ~8.

Give every agent three things or its findings will be untethered:
- the **exact diff** and the base it is measured against
- **which environment** this ships to, and what data lives there
- its **specific question** — never "review this"

Good per-lens questions:
- *security* — "Does this widen what an unauthenticated or cross-tenant caller can reach?"
- *reliability* — "What happens to an in-flight request during the swap? Failure mode if the
  new call times out?"
- *architect* — "Can this corrupt or orphan an existing row? Is the write idempotent on retry?"
- *product* — "Does this change what a customer is told, and is the new claim supportable?"

**Then verify each finding yourself before reporting it.** `initiate-team-review` dedupes but
does not verify; this gate must. A subagent finding is a hypothesis, and agents produce
confident wrong numbers. Deduplicate across lenses — one finding, credited to all, at the
highest severity reported.

## Step 3 — The deterministic checks no agent can do

1. **Staging parity.** Has *this exact commit* been exercised on staging — not a similar one?
   Verify by content in the served artefact, never by a version number or a deploy log.
2. **Rollback.** Name the artefact you would redeploy and confirm it exists **now**. "We can
   roll back" without naming the file is not a rollback plan. The framework's bar: executable
   in under five minutes, and tested.
3. **Serving check, bidirectionally.** Grep the deployed artefact for a string that exists ONLY
   in the new version, and one that exists ONLY in the old. A single positive check proves the
   probe can fire; it does not make a zero meaningful.
4. **A control on every probe.** If a control returns zero, the probe is broken and every other
   zero in that run is meaningless.
   ⚠️ **`grep -c` counts matching LINES, not occurrences** — on a bundled or minified artefact
   that is a present/absent signal only, never a frequency.
5. **Exit codes lie.** Deploy scripts routinely exit `0` having deployed nothing. Read the
   summary line — `deployed 0/4` — not `$?`.
6. **Credentials.** A stale token in the shell can override the working one in a project env
   file, producing an auth failure that reads as a permissions problem. Check presence and
   length; **never print a value.**
7. **Distrust sibling premises.** A deploy skill's stated assumptions age badly — one in this
   family still opens "the platform gives you NO staging environment" long after a staging
   project existed. Re-read the project layer rather than trusting a neighbour's preamble.

## Step 4 — The verdict

Emit exactly this shape, and nothing around it:

```
VERDICT: GO | NO-GO | GO WITH CONDITIONS
  commit:       <sha> → <environment>   (currently running: <sha>)
  blast radius: <dimensions that came back yes, or "none — read-only change">
  lenses run:   <agent — one-line conclusion, per lens>
  uncovered:    <relevant lenses with no installed agent, or "none">
  findings:     <Critical/High only, with file:line; or "none above Medium">
  rollback:     <named artefact, confirmed present>
  staging:      <verified by content | NOT verified — a NO-GO condition>
  NOT CHECKED:  <required — every check that could not be run, and why>

  → hand off to release-deploy-prod (or the project's serverless deploy skill)
```

`GO WITH CONDITIONS` is the honest verdict when the change is sound but something around it is
not — a stranded migration, an unverified sibling, a rollback you could not confirm. Name the
condition; never round it up to GO.

## What this skill does NOT do

Deploy · merge · modify code · approve its own verdict · substitute for a human on an ask-first
production change. **A NO-GO it cannot justify with evidence is a guess, not a verdict — say
which.**
