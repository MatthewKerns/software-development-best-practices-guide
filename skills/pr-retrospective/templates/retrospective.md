# PR #{PR_NUMBER} Retrospective — {TITLE}

**PR:** #{PR_NUMBER} — `{PR_TITLE_LINE}`
**Branch:** `{HEAD_BRANCH}` → `{BASE_BRANCH}`
**Window:** {WINDOW_START} → {WINDOW_END} ({DURATION_DAYS} days)
**Scale:** {COMMIT_COUNT} commits, ~{FILE_COUNT} files, +{ADDITIONS} / -{DELETIONS} lines
**Authors:** {AUTHORS}
**Sessions analyzed:** {SESSION_COUNT} Claude Code sessions ({COMPACTED_COUNT} compacted), {TOTAL_MESSAGES} total messages

---

## What Shipped

{WHAT_SHIPPED_BULLETS}

---

## What Landed Well

{WHAT_LANDED_WELL_BULLETS}

---

## Friction and Waste

Each item below has an evidence reference (commit SHA, session id, file path, or doc line). Items are not a morality judgment — they're diffs between what the process actually did and what a tighter version of it would have done.

{FRICTION_NUMBERED_LIST}

---

## Claude Code Session Observations

What the session transcripts reveal that commits alone don't:

- **Session count in window:** {SESSION_COUNT} across {WORKTREE_COUNT} worktrees
- **Compaction:** {COMPACTED_COUNT} of {SESSION_COUNT} sessions hit compaction — median messages per compacted session: {MEDIAN_COMPACTED_MSGS}
- **"Reaching near-done" prompts:** {NEAR_DONE_COUNT} across all sessions (proxy for the recurring "almost there" state)
- **Direction-change prompts:** {DIRECTION_CHANGE_COUNT} (`actually`, `wait`, `never mind` patterns)
- **Tool mix:** {TOP_TOOLS_SUMMARY}
- **Top files edited across sessions:** {TOP_FILES_SUMMARY}

{SESSION_NARRATIVE}

---

## Refinements

Every refinement has a measurable success criterion. Refinements without a metric are flagged and should either get one or be dropped.

{REFINEMENTS_LETTERED_LIST}

---

## Meta-Pattern

> {META_PATTERN_ONE_LINER}

{META_PATTERN_EXPLANATION}

---

## Recommended Next Step

{NEXT_STEP_ONE_CONCRETE_ACTION}

---

## Appendices

- **Raw data:** `docs/pr-prep/retrospective-pr{PR_NUMBER}/raw/`
  - `commits.json` — parsed git log
  - `docs-audit.json` — pr-prep doc inventory
  - `ci-timeline.json` — CI run history
  - `sessions.json` — Claude Code session summary
- **Structured data:** `docs/pr-prep/retrospective-pr{PR_NUMBER}.xlsx` (11 tabs)
- **Analyst exchange (if any):** `docs/pr-prep/retrospective-pr{PR_NUMBER}/info-request.md` + `analyst-reply.md`
