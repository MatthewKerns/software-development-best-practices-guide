# Release Pipeline — <project name>

Project layer read by the `release-*` skills. Facts only — pipeline logic lives
in the generic skills. Keep command detail in the deploy runbook and link it
here; don't maintain two copies.

## Integration branch

`main` <!-- the branch PRs merge to and deploys build from -->

## Local verification gates

Commands run by `release-verify-local` before any PR. List every gate; note
known baseline failures so only NEW failures block.

```bash
npm run lint
npx tsc --noEmit
npm test
npm run build
```

- Baseline: <!-- e.g. "12 pre-existing test failures on main are baseline — see <link>" or "none" -->
- Worktree note: <!-- e.g. "diff env keys vs primary checkout before building" or "n/a" -->

## Staging

- Model: `deploy-target` <!-- or `branch` if PRs merge to a staging branch first -->
- URL: <!-- https://staging.example.com -->
- Deploy runbook: <!-- link to doc section, or inline commands if no runbook exists -->
- Verification: <!-- how to confirm the served build is the new build (bundle hash route, health endpoint) -->
- Smoke routes: <!-- routes/flows release-stage-verify must exercise -->
- Hazards: <!-- flags that must (not) be used, content that lives only on the server, etc. -->

## Production

- URL: <!-- https://example.com -->
- Deploy runbook: <!-- link to the authoritative runbook section -->
- Verification: <!-- served-bundle hash check, health endpoints, smoke routes -->
- Rollback: <!-- pointer to rollback artifacts/procedure -->
- Deploy stamp: <!-- path to the JSON stamp recording what is deployed, e.g.
     /home/<user>/deploy-stamps/prod.json. Payload: {sha, branch, bundle_hash,
     deployed_at, worktree, session}. MUST live OUTSIDE the web docroot.
     `release-deploy-prod`, `release-state` and `prod-deploy-review` all read this;
     it was depended on before it was ever a field here. -->

## Deploy queue

- Path: `docs/release/DEPLOY_QUEUE.md`

## Cadence

- Prod deploys: weekly, on <!-- day -->. Off-cadence deploys require explicit user request.

## Issue flagging

- Tracker: <!-- e.g. GitHub issues via `gh issue create` -->
- Label: <!-- e.g. `staging-blocker` -->
