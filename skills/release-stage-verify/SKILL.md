---
name: release-stage-verify
description: |
  Stage 2 of the release pipeline: after a PR merges, deploy the integration
  branch to staging, verify the served build over HTTP, run the project's smoke
  routes, flag issues if verification fails, and on success add the change to
  the prod deploy queue as staging-verified. Use when the user says "deploy to
  staging", "verify on staging", "stage this", "staging check", or
  "release-stage-verify", or right after merging a PR. Requires the project's
  docs/RELEASE_PIPELINE.md — fails closed without it (deploy commands are never
  guessed).
allowed-tools: [Read, Bash, Grep, Glob, Edit, Write]
---

# Release: Stage & Verify (post-merge)

Goal: every merged change gets exercised on staging before it can queue for
prod, and staging failures become tracked issues instead of surprises.

## Procedure

1. **Load the project layer.** Read `docs/RELEASE_PIPELINE.md` → "Staging".
   Missing manifest or missing staging runbook → **STOP**: offer to scaffold via
   `release-pipeline`. Never reconstruct deploy commands from memory — wrong
   flags on a copy-based deploy can destroy server-only content.
2. **Sync to the integration tip.** `git fetch`; confirm the local integration
   branch fast-forwards to origin. Record the tip SHA — this is what staging
   verification will vouch for. If the staging model is `branch`, merge the PR
   to the staging branch per the manifest instead.
3. **Pre-flight the target — do not deploy blind.** Staging is usually one
   shared mutable box with last-write-wins semantics. Before pushing anything,
   read the deploy stamp already on the target (see "Where the stamp lives"):
   - **No stamp** → someone deployed without this skill. Record what's served
     (bundle hash) so the overwrite is at least attributable, and continue.
   - **Stamp present** → if its SHA is **not an ancestor of what you are about
     to deploy** (`git merge-base --is-ancestor <deployed-sha> <your-sha>`),
     **HALT**. You are about to revert someone else's work. Report whose,
     which commits would be lost, and offer to merge their SHA in first. Only
     the operator may authorize deploying anyway.
   - Ancestor check passes → proceed.
4. **Build and deploy** exactly per the manifest's staging runbook, respecting
   its hazards verbatim (e.g. a "never use --delete" note exists because
   content lives only on the server).
5. **Stamp the deploy.** Immediately after deploying, write a machine-readable
   stamp to the project's stamp path (see "Where the stamp lives") containing
   at minimum:
   `{sha, branch, bundle_hash, deployed_at, worktree, session}`. This is what
   makes step 3 possible for the next person, and turns "who reverted me" from
   forensics into a lookup. A deploy without a stamp is an anonymous deploy.
6. **Verify over HTTP, not on disk:**
   - The manifest's verification step (typically: fetch an app route, confirm
     the served bundle hash matches the local build; check health endpoints).
   - Exercise every listed smoke route/flow. Use the project's browser-QA setup
     if the manifest points to one for authenticated flows.
7. **On failure — flag it:**
   - File an issue per the manifest's tracker/label (e.g. `gh issue create
     --label staging-blocker`) with: tip SHA, what failed, expected vs actual,
     repro route.
   - Add or update the queue entry (manifest's queue path) with status
     `blocked` linking the issue.
   - Report the blocker; do not queue for prod.
8. **On success — queue it.** Append to the queue file's `## Queue` table:
   date, tip SHA, PRs included (`git log --oneline <last-deployed>..<tip>` or
   since the previous entry), status `staging-verified`, evidence (bundle
   hash / health results, smoke routes exercised, timestamp).

## Where the stamp lives

**Never inside a web-served docroot.** The stamp records branch names, local
worktree paths and session ids — put it under the docroot and it is public.
Confirmed the hard way 2026-07-28: a stamp written to `/opt/<site>/` was
immediately fetchable at `https://<site>/DEPLOYED.json`.

Use a sibling directory the deploy user owns and no vhost serves — e.g.
`/home/<deploy-user>/deploy-stamps/<target>.json`. Record the path in the
project manifest. Two further reasons this is the right home: a mirroring
deploy (`rsync --delete`) would wipe a stamp that sits in the docroot, and a
docroot stamp gets clobbered by the very deploy it is meant to describe.

**Verify after writing**, once: `curl` the public URL where the stamp would sit
and confirm it does not return the stamp's contents. A 200 alone proves nothing
— SPA fallbacks return `index.html` for any unmatched path, so check the
*body*, not the status code.

## Initializing a stamp on an already-live target

The stamp is written by the deploy step, so a target deployed to before this
pipeline existed has none — and stays unstamped until its next pipeline deploy,
which is exactly when you need the guard. **Backfill it once, immediately**,
rather than waiting:

1. Fetch the served bundle hash.
2. Try to establish provenance: find which local worktree's `dist/` contains
   that artifact, and whether its `dist` mtime is **newer** than its HEAD commit
   (if HEAD is newer, the build predates it — that SHA is NOT what's serving).
3. Write the stamp with whatever is **provable**. If the SHA cannot be
   established, record `"sha": null` and `"provenance": "backfilled"` — never
   guess. A guessed SHA is worse than none: `merge-base --is-ancestor` will
   return a confident wrong answer and wave through the exact revert the check
   exists to stop.

**`sha: null` semantics:** treat as "unknown target". The ancestry check cannot
run, so the pre-deploy branch is: identify what is serving (diff the served
bundle against your build for strings unique to recent commits), report it, and
get operator confirmation before overwriting. The stamp still earns its place —
it records the bundle hash and timestamp, so the *next* deploy can tell whether
anything changed under it.

## Rules

- Verification vouches for a specific SHA. If anything merges after the deploy,
  the vouch doesn't transfer — re-run against the new tip.
- **Verification is a snapshot, not a standing fact.** It describes the box at
  one instant. On a shared target it can be false minutes later, and nothing
  notifies you — the next write is silent.
- **Re-verify before every re-assertion.** Any time you say "it's live on
  staging" — in a later message, a status summary, a Slack draft, a handoff —
  re-fetch the served bundle hash *at that moment* and confirm it still matches
  the build you verified. Do not carry an earlier PASS forward as present tense.
  The cost is one `curl`; the cost of skipping it is telling someone a link
  works when it has silently reverted.
- **Re-verify before pointing a third party at it.** Before a stakeholder,
  client, or tester is given a staging URL, re-check immediately — an
  overwritten staging URL in front of the person who asked for the feature
  reads as "you didn't build it", which is more expensive than the deploy.
- Two people deploying the same target can race. The stamp (step 5) plus the
  ancestry check (step 3) is how that race is *detected and halted* rather than
  noticed afterwards. If the served hash doesn't match your build at any point
  **after** your deploy, you were overwritten: fetch the current stamp, merge
  that SHA into yours, rebuild, redeploy — never blind-rsync over it, which
  just reverses the clobber.
- **A shared staging box is not owned by whoever wrote last.** Losing a deploy
  costs the work plus the credibility of every "it's live" you have said.
- Next stages: `release-queue` (inspect), `release-deploy-prod` (weekly ship).

## Field note — why these rules exist (2026-07-28, idea-brand-coach)

Two sessions, two worktrees, one `/opt/ideabrandcoach-staging`. Session A
deployed and verified at 17:10 (15/15 checks green). Session B rebuilt from a
worktree lacking A's commits and rsynced at 17:14. Everything A shipped —
a new route, a whole feature, copy fixes — vanished from staging. Nobody
noticed for over an hour, and in that window A told the operator it was live
**and the operator sent a stakeholder the URL.** The stakeholder had just asked
"what happened to the thing I spec'd?", so the reverted link answered his
question wrongly, in the most damaging way available.

Both sessions were careful. Neither had a way to see the other. The stamp and
the ancestry check are that way; the re-verify rule is what catches it when
someone deploys without them.
