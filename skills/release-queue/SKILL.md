---
name: release-queue
description: |
  Stage 3 of the release pipeline: inspect and manage the production deploy
  queue — what's staging-verified and ready to ship, what's blocked and why,
  what shipped when. Use when the user asks "what's queued for prod", "deploy
  queue status", "what's ready to ship", "add this to the deploy queue",
  "what's blocking the release", or "release-queue". The queue file lives at
  the path declared in the project's docs/RELEASE_PIPELINE.md (default
  docs/release/DEPLOY_QUEUE.md).
allowed-tools: [Read, Bash, Grep, Glob, Edit, Write]
---

# Release: Prod Deploy Queue

Goal: a single durable answer to "what ships in the next prod deploy, and is it
safe?" — kept in the repo so it survives sessions and is visible in review.

## Queue file format

One markdown file (path from the manifest) with two sections:

```markdown
## Queue

| Date | Tip SHA | PRs / changes | Status | Evidence / issue |
|------|---------|---------------|--------|------------------|
| 2026-07-28 | abc1234 | #142 checkout fix, #145 copy | staging-verified | bundle 9f3c…, smoke 5/5 |

## Deploy log

| Date | SHA deployed | Entries shipped | Served hash | Notes |
```

Statuses: `pending-staging` → `staging-verified` | `blocked` (must link its
issue) → `deployed` (moves to the deploy log).

## Operations

- **Status** (default): read the queue, report entries by status, and lead with
  the verdict — "N entries ready for the next prod deploy; M blocked on
  <issues>". Cross-check: does the newest `staging-verified` SHA still equal
  the integration tip? If commits landed after it, say so — those commits are
  unverified and stage 2 must re-run before they can ship.
- **Add**: normally `release-stage-verify` appends entries; add manually only
  with explicit evidence, and mark entries without staging evidence
  `pending-staging`, never `staging-verified`.
- **Unblock**: when a linked issue closes, the entry returns to
  `pending-staging` — resolution is not verification; staging must pass again.
- **Prune/repair**: fix malformed entries, but never delete history — the
  deploy log is the audit trail.

## Rules

- Only `staging-verified` entries are eligible for `release-deploy-prod`.
- The queue records facts, not intentions: every status change cites its
  evidence (verification results, issue link, deploy log row).
- If the queue file doesn't exist, scaffold it (empty sections) at the
  manifest's declared path; if there's no manifest, run `release-pipeline`
  first.
