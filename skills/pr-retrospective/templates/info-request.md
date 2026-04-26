# PR #{PR_NUMBER} — Developer Information Request

**Purpose:** Answers tighten the retrospective's time-savings estimates, sharpen blocker-vs-deferrable calls, and identify which specific friction points the proposed process changes would or wouldn't have caught.

**Format:** Fill in directly, or send the answers as a single message. Short answers are fine — the goal is ground truth, not prose. Sections 2, 3, and 5 have the highest signal-per-word ratio.

---

## 1. Feature Decomposition

**1a. How many distinct features were in PR #{PR_NUMBER}?** (Rough count — just trying to understand shape.)

**1b. If you had to split PR #{PR_NUMBER} into separate PRs today, where would the natural seams be?**

| PR | Features / changes | Why this grouping |
|----|---------------------|-------------------|
| #{PR_NUMBER}a | | |
| #{PR_NUMBER}b | | |
| #{PR_NUMBER}c | | |

**1c. For each seam — why didn't it split that way in practice?** (Real blockers, cross-feature test coupling, time pressure?)

---

## 2. Walkthrough-Discovered Fixes

The retrospective identified {WALKTHROUGH_FIX_COUNT} fixes that landed inline during walkthrough. For each:

| # | Description | Category | Was it a real blocker? |
|---|-------------|----------|------------------------|
{WALKTHROUGH_FIXES_TABLE_PLACEHOLDER}

**Summary: of these, which would you actually defer to a follow-up PR if asked at the time?** (Hindsight is allowed.)

---

## 3. CI-Chasing Commits

{CI_CHASING_CONTEXT}

**3a. What caused the local-vs-CI drift?**
- [ ] Local dev DB had uncommitted schema changes
- [ ] Migration was correct but prod role setup differed from local
- [ ] Manual hotfix to prod that never came back to main
- [ ] Migration order-of-operations issue
- [ ] Something else: ___________

**3b. Was there a runbook or doc describing the relevant setup, or was it tribal knowledge?**

**3c. For each of the {CI_COMMIT_COUNT} commits, what did it fix?**

| Commit | Fix |
|--------|-----|
{CI_COMMITS_TABLE_PLACEHOLDER}

**3d. Would a pre-push checklist have caught all of them?** (What fraction?)

---

## 4. Scope Pull-Forwards

The retrospective flagged {PULL_FORWARD_COUNT} items pulled forward from planned follow-up PRs.

**4a. Why were they pulled in rather than staying in their planned PR?** (Genuine dependency? Reviewer feedback? Opportunistic?)

**4b. In hindsight, would it have shipped faster as separate PRs first?**

**4c. Did the pulled-forward features have error handling / runbook / observability docs before they were pulled in, or did those get retrofitted?**

---

## 5. Walkthrough Process Itself

**5a. How many items did the walkthrough discover?**

**5b. Split estimate:**
- [ ] ___ would have been genuine P0 blockers → stay in PR
- [ ] ___ would have deferred with a spec → follow-up PR
- [ ] ___ would have been "fix inline because 5 minutes" gray area

**5c. Which walkthrough fixes were blockers vs. polish?**

| Item | Blocker? | Could have waited? |
|------|----------|---------------------|
{WALKTHROUGH_FIXES_SUMMARY_TABLE}

---

## 6. Documentation Overhead

**6a. Roughly how many total hours went into PR-prep doc writing/maintenance?** (Rough estimate — an hour? A day? A week?)

**6b. Of the {PREP_DOC_COUNT} files, which were genuinely useful to a reviewer vs. ceremonial?**

{PREP_DOCS_TABLE_PLACEHOLDER}

---

## 7. Observability / Validation Matrix

**7a. Where does the validation matrix live — in the PR, a doc, Notion, somewhere in `docs/`?**

**7b. Does it have any monitoring / alerting tied to it, or is it purely one-time validation?**

**7c. If the upstream API changes a response schema tomorrow, where would that show up first — log? metric? user complaint?**

---

## 8. Compliance / PII

**8a. When was the PII / compliance gap first noticed internally?** (Day X of the PR? PR-prep time? Earlier but unescalated?)

**8b. What fields / capabilities were flagged?** (High-level.)

**8c. Is there a canonical list anywhere of "which fields are PII"?**

---

## 9. Ranking

**9a. Which friction point cost the most *calendar time*?** (Pick one)

**9b. Which cost the most *cognitive load / morale*?** (Pick one — may differ from 9a)

**9c. Which would you most want solved next, and how would you measure success?**

---

## 10. Open-Ended

**10a. Is there anything in PR #{PR_NUMBER} that the analysis missed that the proposed process would clearly help or hurt?**

**10b. Is there anything in the proposed process that would clearly NOT fit how your team actually works?**

---

## Format for Sending Back

- Fill in directly in this markdown
- Bullet answers in a single message (reference question numbers)
- Partial answers fine — Sections 2, 3, 5 sharpen estimates the most
