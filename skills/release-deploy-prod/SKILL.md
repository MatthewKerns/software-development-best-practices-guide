---
name: release-deploy-prod
description: |
  Stage 4 of the release pipeline: the weekly production deploy ritual —
  preflight the queue, rebuild from the verified integration tip, deploy per the
  project's prod runbook, verify the served build over HTTP, and record the
  deploy. Use when the user says "prod deploy", "ship to production", "weekly
  deploy", "release day", or "release-deploy-prod". Requires the project's
  docs/RELEASE_PIPELINE.md — fails closed without it. Only staging-verified
  queue entries ship.
allowed-tools: [Read, Bash, Grep, Glob, Edit, Write]
---

# Release: Prod Deploy (weekly)

Goal: production changes ship on a predictable weekly cadence, only after
staging verification, with the deploy itself verified and logged.

## Preflight (all must pass before any deploy command runs)

1. **Manifest.** Read `docs/RELEASE_PIPELINE.md` → "Production", "Cadence",
   "Deploy queue". Missing → **STOP** and scaffold via `release-pipeline`.
2. **Cadence.** If today isn't the manifest's deploy day, confirm the user
   explicitly wants an off-cadence deploy before proceeding.
3. **Queue.** Read the queue: at least one `staging-verified` entry; report any
   `blocked`/`pending-staging` entries as explicitly NOT shipping.
4. **Tip match.** `git fetch`; the integration tip must equal the newest
   `staging-verified` SHA. If commits landed since staging verification, stop
   and run `release-stage-verify` against the new tip first — never ship
   unverified commits, and never deploy an old SHA while newer commits sit on
   the branch (the next builder would silently revert or ship them blind).
5. **Target state — what is actually on prod right now.** Tip-match compares
   git to the queue; it says nothing about the box. Read prod's deploy stamp
   (manifest path — **never inside the web docroot**; see `release-stage-verify`
   → "Where the stamp lives") and the served
   bundle hash:
   - Stamp SHA **not an ancestor** of the tip you are about to ship
     (`git merge-base --is-ancestor <deployed-sha> <tip>`) → **STOP.** Prod is
     carrying work your build does not contain; shipping reverts it *for
     customers*. Report whose commits would be lost and merge them first.
   - **No stamp** → backfill one before going further, per
     `release-stage-verify` → "Initializing a stamp on an already-live target".
     Do not skip this because a deploy is pending: an unstamped prod is exactly
     the case where the guard is most needed and least available.
   - **`sha: null` (backfilled, provenance unknown)** → the ancestry check
     cannot run. Identify what is serving (diff the served bundle for strings
     unique to recent commits), report it, and get explicit operator
     confirmation before overwriting. Never treat unknown as safe.
   - **Served hash unrecognised / doesn't match the stamp** → someone deployed
     outside this pipeline *after* the last stamped deploy. Stop and identify
     it. Do not assume the queue's newest entry is what's serving.

## Deploy

6. **Rebuild from the verified tip immediately before deploying** — from a
   checkout of the integration branch, fast-forwarded, with the build env the
   manifest requires. A build made earlier (or from a stale tree) silently
   reverts other sessions' merged work when the deploy mirrors files.
7. **Execute the manifest's prod runbook exactly**, including every listed
   component (e.g. app bundle AND gateway/services if their code changed) and
   every hazard note verbatim.

   **If the manifest names a prod deploy script, that IS the runbook — run it
   rather than the raw commands.** On this project:

   ```bash
   npm run deploy:prod -- --confirm <short-sha> \
                          --literal "<string unique to this deploy>" \
                          --control "<string that certainly already exists>"
   ```

   It enforces, and refuses on, every precondition this skill describes: clean
   tree, HEAD an ancestor of the integration branch, fresh build, complete build
   env, stamp ancestry, a printed deletion list, and a confirmation naming the
   exact commit. It also writes the stamp and verifies the served bundle, so
   steps 8 and 10 below are partly done for you — check its output rather than
   repeating the work.

   **`--confirm` is the human gate, not a formality.** It must carry the SHA the
   human approved. Never supply it from a previous approval, and never re-use one
   after new commits land — an approval names one commit and expires with it.

## Verify & record

8. **Verify over HTTP:** the manifest's production verification steps — served
   bundle hash matches the build, health endpoints respond, smoke routes work.
   Where possible confirm the deployed artifact contains this deploy's changes
   (e.g. grep the served bundle for a string unique to a shipped commit).
9. **On failure: roll back** per the manifest's rollback pointer, verify the
   rollback took over HTTP, then file an issue (manifest's tracker/label) and
   mark the queue entries `blocked`. A failed deploy left half-applied is worse
   than a clean rollback.
10. **On success: stamp and record.** Write the deploy stamp to prod
   (`{sha, branch, bundle_hash, deployed_at, worktree, session}`) so the next
   deploy's preflight can see what it would be overwriting. Then move shipped
   entries to the queue file's `## Deploy log` with date, SHA, served hash, and
   notes; mark them `deployed`. Report what shipped and what remains queued or
   blocked.

## Rules

- Nothing ships without a `staging-verified` queue entry — including "tiny"
  fixes; they go through stages 1–3 like everything else.
- The deploy is done when HTTP verification passes, the stamp is written, and
  the log row exists — not when the copy command exits.
- **Verification is a snapshot.** Re-fetch the served hash before re-asserting
  "it's live in prod" in any later message, summary, or customer-facing note —
  a shared target can be overwritten silently between the check and the claim.
- **An unstamped target is an unknown target.** If prod carries no stamp, treat
  the next deploy as potentially destructive and identify what is serving first.
