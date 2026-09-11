---
name: release-verify-local
description: |
  Stage 1 of the release pipeline: run a project's full local verification gates
  before a PR and produce a pass/fail evidence report. Use when the user says
  "verify before PR", "pre-PR check", "is this ready for a PR", "run the local
  gates", "release-verify-local", or is about to open a pull request. Reads the
  project's docs/RELEASE_PIPELINE.md for the gate list; falls back to detected
  standard gates (lint, typecheck, test, build) if the manifest is missing.
allowed-tools: [Read, Bash, Grep, Glob, Edit, Write]
---

# Release: Verify Local (pre-PR)

Goal: no PR opens without every local gate green (or its failure explicitly
understood as pre-existing baseline). Output is an evidence table the PR body
can carry.

## Procedure

1. **Load the project layer.** Read `docs/RELEASE_PIPELINE.md` → "Local
   verification gates". If missing, detect standard gates from `package.json`
   (or the project's build system): lint, typecheck, tests, production build —
   and offer to scaffold the manifest via `release-pipeline` afterward.
2. **Check the working tree context.**
   - Confirm the branch is up to date with the integration branch
     (`git fetch` + report behind/ahead). A PR from a stale branch verifies the
     wrong future merge state.
   - If in a git worktree, apply the manifest's worktree note (commonly: diff
     env keys against the primary checkout — a present-but-incomplete `.env`
     builds successfully while silently dropping flag-gated features).
3. **Run every gate**, capturing exit codes and the tail of failing output. Run
   independent gates in parallel where safe; never parallelize gates that write
   to the same artifacts.
4. **Classify failures.** Compare test failures against the manifest's baseline
   list: pre-existing baseline failures are reported but don't block; anything
   new blocks. If a gate hangs (0% CPU), kill and rerun once before declaring
   failure.
5. **Report** a table: gate → command → result → evidence (duration, failure
   excerpt). Verdict: `READY FOR PR` or `BLOCKED` with the specific failing
   gates.
6. **On READY, if asked to open the PR:** create it (`gh pr create`) with the
   evidence table in the body under a "Local verification" heading. On BLOCKED:
   fix and re-run, or report the blockers — never open the PR anyway.

## Rules

- A skipped gate is a failed gate — if a listed command can't run (missing dep,
  no env), that's a blocker to surface, not a row to omit.
- Report what actually happened: paste real failure output, never summarize a
  failure as "minor".
- Next stage after merge: `release-stage-verify`.
