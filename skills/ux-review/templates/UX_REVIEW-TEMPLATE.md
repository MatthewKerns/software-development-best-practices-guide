# UX Review — project layer

Facts only. The `/ux-review` skill holds the procedure; this file holds what is true
about **this** project. Keep it short enough that it stays current.

## Environments

How to establish which build is being walked. Resolve at a path that **loads the app** —
never at a marketing root, which is often byte-identical across environments.

| env | resolve | notes |
|---|---|---|
| prod | `curl -s https://<host>/<app-path> \| grep -oE 'index-[A-Za-z0-9_-]+\.js'` | |
| staging | same against the staging host | |
| local | dev server port | env must point at staging, never prod |

⚠️ A 200 is not existence — an SPA catch-all answers any unmatched path with the same
`index.html`. Discriminate by content or size.

**Deploy stamp** (optional): where to read the SHA currently deployed per environment, so a
walk can report the artefact identity rather than guessing it.

## Walkthroughs

Location: `docs/ux-review/` · Default when unspecified: `<name>`

| file | covers | authored-against |
|---|---|---|
| `<name>.md` | `<journey>` | `<sha>` |

## Reports

`docs/ux-review/reports/walk-<env>-<date>.md`

## Credentials

Where the shared test account is documented — **the pointer, never the credentials.**

## Known traps

Real, cited, project-specific gotchas a walker will otherwise hit. Each one names the
incident or measurement behind it. An uncited trap is noise; delete it.

| trap | evidence |
|---|---|
