# <Workflow name> — UX walkthrough

authored-against: <git SHA>
covers: <the user journey, in one line>
does NOT cover: <required — what this walk structurally cannot reach>

> Serve with `/ux-review`. One screen per turn. Every screen needs all four fields.
> Delete this quote block and the guidance comments once the file is real.

---

## SCREEN 1 — <short name>

CONTEXT:  <one line: where they are, what state the app should be in. Not why it matters.>
ACTION:   <one line, ONE physical act. If it needs two, it is two screens.>
LOOK FOR: • <observable thing 1>
          • <observable thing 2>
          • <REQUIRED: what the screen COMMUNICATES — does the user learn what is
            happening and what to do next?>
VERIFY:   <binary pass condition — answerable pass/fail by someone who has not read
          the code. "Looks right" is not one.>  → reply pass / fail / note

<!-- ⚠️ TRAP: only if a REAL one exists, and cite the incident or measurement behind
     it. Never invent one for symmetry. Delete this line if there is none. -->

<!-- 💰 COST: if this step spends money, say how much. Never a default step. -->

---

## SCREEN 2 — <short name>

CONTEXT:
ACTION:
LOOK FOR: •
          •
          • <what it communicates>
VERIFY:    → reply pass / fail / note

---

<!--
AUTHORING STANDARD — a screen is rejected on any of these:

1. Missing any of the four fields. No VERIFY = unfalsifiable. No LOOK FOR = a click-list.
2. No LOOK FOR bullet about what the screen COMMUNICATES.
3. VERIFY is not binary.
4. ACTION is more than one physical act.
5. A TRAP that is invented rather than cited.
6. A money-spending step that is unmarked or is a default.
7. No "does NOT cover" line at the top.
8. No authored-against SHA.
-->
