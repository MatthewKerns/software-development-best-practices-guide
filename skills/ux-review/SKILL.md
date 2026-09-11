---
name: ux-review
description: |
  Drive a human through a manual UX verification pass of an app's user workflows,
  ONE SCREEN AT A TIME, in a named environment (prod | staging | local). Emits a
  fixed CONTEXT / ACTION / LOOK FOR / VERIFY block per screen, waits for the
  result, records it, then advances. Use when the user says "walk me through",
  "ux review", "manual verification", "verify the app", "what should I check",
  "walk staging", "walk prod", or invokes /ux-review. Walkthroughs are
  PRE-AUTHORED in the project (docs/ux-review/*.md) — this skill serves and
  drives them, it does not author them on demand. Reads docs/UX_REVIEW.md for
  the project layer; offers to scaffold it when missing.
allowed-tools: [Read, Bash, Grep, Glob, Edit, Write]
---

# UX Review — one screen at a time

Portable sibling of a project-local walkthrough driver. The thinking happens at
**authoring** time, in the project's walkthrough files; at **ask** time this skill
only resolves the environment, serves one screen, records the answer, and advances.

## Why this shape

Walkthroughs authored *when asked* cost the reviewer the authoring latency, hand them
the agent's reasoning instead of steps, and change shape every time. Inverting it makes
the walk fast, repeatable, and comparable across runs.

## 🔴 The output rule — this is the whole point

**One increment per turn. Never more.** A single screen block, ≤10 lines, then stop and
wait for the reviewer's reply.

Never: dump the whole walkthrough, explain your reasoning, restate the goal, add caveats
inline, or pre-answer a step they have not reached. Context they need goes in a ≤3-line
PREFLIGHT once, at the start, and nowhere else.

If you are writing a paragraph, you have already failed the skill.

## Step 0 — Resolve the environment before serving anything

A walk against the wrong build is worthless. Establish and state it in one line.

Read `docs/UX_REVIEW.md` → **Environments** for the resolve command per environment. If
the manifest is missing, detect what you can (dev-server port, a deployed URL in the
README or CI config) and **say which environment you believe you are on and how you
established it** — never leave it implicit.

Three traps, all learned the hard way and all project-independent:

- ⚠️ **Never resolve at the marketing root.** Many apps serve a static landing page at
  `/` that is byte-identical across environments and contains none of the app bundle.
  Resolve at a path that actually loads the application.
- ⚠️ **A 200 is not existence.** An SPA catch-all returns the same `index.html` for any
  unmatched path. Only size or content discriminates. A 200 on a route proves the server
  answered, not that the route exists or the app runs.
- ⚠️ **Prefer a bidirectional control.** To prove a build carries a change, find a string
  present in one environment and absent in the other, using the same probe. A single
  positive check proves the probe can fire; it does not make a zero meaningful.

Map the build to a commit if a deploy stamp exists, and **state the SHA the walkthrough
was authored against**. If they differ, say so in one line before starting — the walk may
be stale.

If the environment cannot be resolved, say so and stop. Do not walk an unidentified build.

## Step 1 — Load the walkthrough

Read `docs/ux-review/<name>.md`, chosen by what the reviewer asked for; the manifest names
the default. If the file does not exist, say `MISSING: docs/ux-review/<name>.md`, list what
does exist, and stop.

**Do not author one on the fly.** That is the latency this skill exists to remove, and an
improvised walk has none of the authoring standard's guarantees. A missing walkthrough for
a shipped feature is a process failure — report it as one.

(Scaffolding an empty *template* is not authoring — see the last section.)

## Step 2 — The increment format, fixed

Emit exactly this, nothing around it:

```
SCREEN 3/7 — Build progress
CONTEXT:  Analysis just started. This window has no data yet.
ACTION:   Watch from the moment you submit until real content replaces the opening.
LOOK FOR: • text appears progressively, not all at once
          • it says what it is doing — not a bare spinner
          • the next-step list appears only AFTER the opening finishes
VERIFY:   The wait felt narrated, not hung.  → reply pass / fail / note
⚠️ TRAP:  Needs a never-analysed input. A repeat replays from cache and skips this.
```

Field rules:

- **CONTEXT** — one line. Where they are and what state the app should be in. Not why it matters.
- **ACTION** — one line, one physical act. If it needs two, it is two screens.
- **LOOK FOR** — 2–4 bullets, each ≤1 line. **At least one must be what the screen
  COMMUNICATES** — the message, not the mechanics. *"Does the user learn what is happening
  and what to do next?"* is a first-class check, not a nicety.
- **VERIFY** — the binary pass condition plus the reply prompt. One line.
- **⚠️ TRAP** — only when a real one exists. Never invent one for symmetry.

## Step 3 — Loop

After each reply:

1. Record it (pass / fail / note + their words, verbatim, short).
2. **Advance one screen.** No summary between screens, no "great, next up we'll…".
3. On a `fail`, ask at most **one** clarifying question, then move on. Do not debug
   mid-walk — the walk's job is to find, not to fix. Log it and keep going.
4. On `skip`, record `NOT COVERED` with the reason and advance.

Honour `back`, `skip`, `stop`, and jumps (`screen 5`) without comment.

## Step 4 — Close

When the last screen is answered, emit:

- one line per screen: `n. <name> — pass | fail | not covered`
- the failures, with the reviewer's own words
- a **NOT COVERED** list — required, including anything the walk structurally cannot reach
- the artefact identity walked (environment, build, SHA)

Write it to the manifest's report path (default `docs/ux-review/reports/walk-<env>-<date>.md`)
**before** reporting. The walk is evidence, not a fix queue — hand failures to whoever owns
triage rather than fixing them inside the walk.

## What this skill does NOT do

Author walkthroughs · investigate failures · fix code · deploy · claim a screen passed that
the reviewer did not confirm. **A screen they did not answer is `NOT COVERED`, never assumed.**

## The authoring standard — what a walkthrough must satisfy

Apply this when writing or reviewing a walkthrough file. Reject on any of them.

1. **Every screen has all four fields.** A missing `VERIFY` makes the screen unfalsifiable;
   a missing `LOOK FOR` makes it a click-list, not a verification.
2. **At least one `LOOK FOR` per screen is about what the screen COMMUNICATES** — not
   whether it rendered. It is the check most likely to be skipped and most likely to matter.
3. **`VERIFY` is binary.** "Looks right" is not a pass condition. It must be answerable
   pass/fail by someone who has not read the code.
4. **`ACTION` is one physical act.** Two acts is two screens. This keeps increments small
   enough to read while clicking.
5. **Traps are real or absent.** Every `TRAP` cites the incident or measurement behind it.
6. **Anything that spends money is marked**, with what it costs, and is never a default step.
7. **The walkthrough names what it does NOT cover.** A walk implying completeness it lacks is
   worse than a short honest one.
8. **`authored-against:` SHA is present**, and the file is re-signed when the spec moves.

A walkthrough whose SHA is behind the environment being walked is served with a one-line
staleness warning, never silently.

## Who authors, who walks

Two jobs, deliberately separated — **nobody authors at ask time.**

| | owns | does |
|---|---|---|
| **Whoever builds the feature** | authoring | Writes `docs/ux-review/<name>.md` as a build deliverable, gated like tests. Keeping it current as the spec moves is theirs. |
| **This skill** | serving | Resolves the environment, serves one screen, records, advances. |

Where a project has a review role (QA lead, tech lead), that person signs a walkthrough
against the authoring standard before it is servable. Solo projects skip the sign-off and
keep the standard — it is a checklist, not a ceremony.

## The project layer — `docs/UX_REVIEW.md`

Facts only; this skill holds the logic. Minimum shape:

```markdown
# UX Review — project layer

## Environments
| env | resolve | notes |
|---|---|---|
| prod | `curl -s https://example.com/app \| grep -oE 'index-[A-Za-z0-9_-]+\.js'` | never resolve at `/` |
| staging | same against staging host | |
| local | dev server port; env must point at staging, never prod | |

## Walkthroughs
Location: `docs/ux-review/` · Default: `<name>`
| file | covers | authored-against |
|---|---|---|

## Reports
`docs/ux-review/reports/walk-<env>-<date>.md`

## Credentials
Where the shared test account lives. NEVER the credentials themselves.

## Known traps
Real, cited, project-specific gotchas a walker will otherwise hit.
```

## Scaffolding a project that has none

If `docs/UX_REVIEW.md` is missing, offer — once, in one line — to create it plus
`docs/ux-review/TEMPLATE.md` from `templates/` beside this skill. Creating an empty
structure is not authoring; filling it with invented steps is. Scaffold, then stop and let
the person who knows the feature write the screens.
