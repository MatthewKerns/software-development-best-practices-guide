---
name: review-orchestrator
description: Master orchestrator for the Refactor & Code Review bucket of the Feature Factory pipeline. Use this skill when reviewing a feature's code for quality before merging, running refactoring passes, checking SOLID compliance, hunting for code smells or duplication, or preparing the diff for human review. Triggers on phrases like "review this code", "refactor before merging", "is this code clean", "check for smells", "SOLID check", "make this reviewable", "polish before PR", or whenever a Clockify entry uses the bucket tag `review`. This skill is your strongest bucket — Matthew already has 12+ specialized refactoring skills installed; this orchestrator routes to the right one for each smell or violation found.
allowed-tools: [Read, Edit, Grep, Glob, Bash]
---

# Review Orchestrator (REVIEW bucket master)

## Purpose

You are the master agent for the **REVIEW bucket** of the Feature Factory pipeline. Your job is to take the feature's code (now functional, error-handled, and observable) and make it clean, well-factored, SOLID-compliant, and reviewable. You produce cleaner code plus a `review.md` summary of what was found and fixed.

This is the bucket where Matthew's tooling is strongest — there are 12+ specialized refactoring skills available. Your role is to route work to the right one rather than do the deep analysis yourself.

## When This Bucket Is Active

Activate the REVIEW bucket when:
- FUNC + ERRORS + OBSV have produced code (all the additions are in)
- A user says "review", "refactor", "clean up", "smells", "SOLID check", "polish"
- Before opening a PR
- The Clockify entry uses the tag `review`
- Code review feedback identifies issues that need addressing

## Inputs Required Before Starting

- The full diff of changes for this feature (FUNC + ERRORS + OBSV combined)
- `func.md`, `errors.md`, `observability.md` — for context on what was intended
- Access to the feature branch

## Output Artifact

Produce `.feature-factory/review.md`:

```markdown
# Review Summary: {Feature Name}

## Smells Detected and Resolved
| Smell | Location | Refactoring Applied | Outcome |
|-------|----------|--------------------|---------| 
| Long method (87 lines) | `returns_handler.ts:45` | Extract Method × 4 | 4 focused methods, max 22 lines |
| Duplicated retry logic | `tiktok_client.ts:30`, `webhook_handler.ts:55` | Extract `RetryPolicy` class | Single source of truth |
| Feature envy | `Order.getCustomerDiscount()` | Move Method to Customer | Better encapsulation |

## SOLID Compliance Check
| Principle | Status | Notes |
|-----------|--------|-------|
| SRP | ✅ Pass | All classes have single responsibility |
| OCP | ✅ Pass | Payment processor uses strategy pattern |
| LSP | ⚠️ Issue | TikTokReturn doesn't fully substitute Return — see follow-up ticket |
| ISP | ✅ Pass | No fat interfaces |
| DIP | ✅ Pass | All deps via interfaces |

## DRY Compliance Check
- Pre-emptive check (FUNC bucket): {found/not found similar code}
- Post-implementation check: {duplications removed during review}

## Security Review
- Input validation: ✅ at API boundary
- Secrets: ✅ none in logs (per OBSV)
- Auth: ✅ checked at entry point
- Open issues: {none | list}

## Diff Quality
- Files changed: {N}
- Lines: +{added} / -{removed}
- Logical commits: {N} (recommend: 1 commit per concern)
- Reviewable: ✅ Yes

## Follow-Up Tickets Created
- LSP issue with TikTokReturn — {ticket}
- {others}

## Hand-Off to DOCS
Code is clean. Architecture decisions documented in arch.md. Errors and observability artifacts ready for runbook generation.
```

## Sub-Skills To Direct To

Matthew's installed skills are heavily concentrated in this bucket. Use them.

| Need | Direct to | Why |
|------|-----------|-----|
| **Full refactoring pipeline** (orchestrates detect→plan→execute→validate) | `refactor-pipeline` | Your default for any non-trivial cleanup |
| Detect structural quality issues | `refactor-detector` | Surface what needs work |
| Plan a refactoring | `refactor-planner` | Sequence the changes safely |
| Execute a refactoring | `refactor-executor` | Apply the changes |
| Validate refactoring didn't break behavior | `refactor-validator` | Tests still pass, behavior preserved |
| Identify code smells | `code-smell-detector` | Long methods, large classes, duplication, feature envy |
| SOLID principle validation | `solid-validator` | All five SOLID principles checked |
| Pre-emptive duplication detection | `dry-compliance-checker` | Run AGAIN here if FUNC didn't — catches missed reuse |
| Focused simplification | `simplify` | Smaller, targeted cleanups |
| Persona-level review | `bmad-code-review` | Structured code review pass |
| Adversarial review (try to break it) | `bmad-review-adversarial-general` | The "what if I'm hostile" pass |
| Edge case hunting | `bmad-review-edge-case-hunter` | Catch edge cases that slipped past ERRORS |
| Course-correct if review reveals a wrong direction | `bmad-correct-course` | Reset before going further |
| Preview commit/diff before pushing | `bmad-checkpoint-preview` | Final check |
| Security-specific review | `security-review` | Auth, input validation, secrets, injection |
| PR review (if code was already pushed) | `review` | The PR-level review skill |

## Best Practices Reference

- `05-refactoring-and-improvement/CODE_SMELLS.md` — **PRIMARY**. Catalog of smells with refactorings.
- `05-refactoring-and-improvement/REFACTORING_CATALOG.md` — patterns: Extract Method, Move Method, Introduce Parameter Object, etc.
- `05-refactoring-and-improvement/REFACTORING_WORKFLOW.md` — safe refactoring process
- `05-refactoring-and-improvement/CONTINUOUS_IMPROVEMENT.md` — broader improvement practices
- `06-collaborative-construction/CODE_REVIEWS.md` — review checklist, what to look for
- `03-clean-architecture/SOLID_PRINCIPLES.md` — SOLID details
- `03-clean-architecture/HUMBLE_OBJECTS.md` — separating testable logic from infrastructure
- `99-reference/CODE_REVIEW_CHECKLIST.md` — fast lookup
- `99-reference/CODE_SMELLS_CHECKLIST.md` — fast lookup
- `99-reference/REFACTORING_CHECKLIST.md` — fast lookup
- `99-reference/SOLID_QUICK_REFERENCE.md` — fast lookup

## The Real PR Size Bar

There is one hard rule for PR size: **one feature per PR**. That's the bar. A PR with one arch.md, one func.md, one errors.md, one observability.md, one review.md, one runbook.md is the right size — regardless of LOC, regardless of file count.

**LOC and file count are signals, not pass/fail.** They trigger a "justify or split" conversation, not an automatic rejection. From `CODE_REVIEW_CHECKLIST.md`:

| Signal | Threshold | What it *might* mean | What to check |
|--------|-----------|----------------------|---------------|
| Net LOC > 400 | Trip | Reviewer attention may degrade | Is the change genuinely one feature? Or is this bundling? |
| Files changed > 20 | Trip | Cross-cutting change | Rename or mechanical? Or multiple concerns? |
| Commits > 15 | Trip | Long development window | Could earlier commits have shipped as their own PR? |
| Test file count / code file count < 0.3 | Trip | Under-tested | Is the missing coverage justified? |

These signals are useful because they're fast to check. But they can all be wrong. A cross-file rename is low-risk at 2000 LOC; a subtle algorithm change is high-risk at 50. The signals exist to trigger the conversation — the conversation settles it.

**The real scoping test is the artifact test**: does this PR have exactly one coherent arch.md? Does the error matrix cover one feature's failure modes, or three? Does the runbook read as "here's one thing and how to operate it," or as a mini-documentation package? If the artifacts are singular, the PR size is right. If the artifacts are plural or blended, the PR is too big regardless of LOC.

## Review Pace, Not Review Size

From `CODE_REVIEW_CHECKLIST.md`: 200–400 LOC/hour is the sustainable review pace. This is about reviewer cognitive load, not about PR size. A 1500-LOC rename reviews at 800+ LOC/hour because it's mechanical. A 150-LOC state machine change might review at 75 LOC/hour. Track the pace during REVIEW — if you're going faster than the material supports, you're rubber-stamping; slower, and the change is too tangled.

## Severity Taxonomy for Findings

Every finding in `review.md` uses one of these labels (from `CODE_REVIEW_CHECKLIST.md`). The label determines whether REVIEW is done or not:

| Label | Meaning | Must fix before merge? |
|-------|---------|------------------------|
| `[CRITICAL]` | Security, data corruption, or a CRITICAL smell (Divergent Change, Shotgun Surgery, Swallowed Exceptions per `CODE_SMELLS_CHECKLIST.md`) | Yes |
| `[BLOCKER]` | Tests fail, broken happy path, incorrect business logic | Yes |
| `[ISSUE]` | Bug in edge case, missing error handling, SOLID violation | Yes |
| `[SUGGESTION]` | Refactor opportunity, cleaner approach available | No — follow-up ticket |
| `[QUESTION]` | Clarification needed | No — resolve inline |
| `[NITPICK]` | Style, naming polish | No — author's discretion |
| `[PRAISE]` | Call out genuinely good work | No — just encouragement |

REVIEW is done when all `[CRITICAL]`, `[BLOCKER]`, and `[ISSUE]` findings are either fixed or have follow-up tickets with accepted rationale. Lower-severity findings can ship.

## The Rule of Three for Refactoring

Per `REFACTORING_CHECKLIST.md`: first time, write it. Second time, wince and duplicate. **Third time, refactor.** Use this to decide whether to extract a common pattern during REVIEW — two instances is not enough signal; three is. Don't let the REVIEW bucket become speculative generalization.

## Workflow

1. **Validate inputs** — confirm `func.md`, `errors.md`, `observability.md` exist. Get the full diff.
2. **Smell detection pass** — invoke `code-smell-detector` against the diff. Catalogue findings by severity.
3. **SOLID validation pass** — invoke `solid-validator` against new/modified classes. Note violations.
4. **Humble Objects check** — per `HUMBLE_OBJECTS.md`: is business logic separated from hard-to-test infrastructure (DB, external APIs, UI, time, randomness)? If business logic is tangled with infrastructure calls, that's a testability flag. The fix is usually to extract a testable component (presenter, use case, pure entity) that the humble component calls. Note violations in `review.md` even if you don't fix them this round.
5. **DRY check pass** — invoke `dry-compliance-checker` against the diff. Even if FUNC ran it pre-emptively, run again post-implementation to catch new duplication.
6. **Decide what to fix vs defer** — for each finding:
   - HIGH severity → fix now (use `refactor-pipeline` or `simplify`)
   - MEDIUM severity → fix if time permits, otherwise create follow-up ticket
   - LOW severity → create follow-up ticket
7. **Refactor** — invoke `refactor-pipeline` for non-trivial cleanups. It orchestrates detect → plan → execute → validate. Tests must stay green throughout.
8. **Adversarial review** — invoke `bmad-review-adversarial-general` to attack the code as a hostile reviewer would.
9. **Edge case hunt** — invoke `bmad-review-edge-case-hunter` to catch edge cases that slipped past ERRORS.
10. **Security review** — invoke `security-review` for any code touching auth, input validation, or sensitive data.
11. **Diff hygiene** — split the diff into logical commits if it's not already. Each commit should represent one concern (e.g., "Add returns endpoint", "Add error handling", "Add metrics", "Refactor: extract RetryPolicy"). Use `bmad-checkpoint-preview` to verify.
12. **Write `review.md`** — capture what was found and what was fixed.

## Acceptance Criteria

The REVIEW bucket is done when:
- [ ] **Artifact test passed**: this PR has one coherent arch.md, func.md, errors.md, observability.md, review.md, runbook.md (not two, not a blended mini-package)
- [ ] All `[CRITICAL]` findings fixed (no Divergent Change, Shotgun Surgery, or Swallowed Exceptions left in the diff)
- [ ] All `[BLOCKER]` findings fixed (tests pass, happy path works, business logic correct)
- [ ] All `[ISSUE]` findings fixed or have follow-up tickets with accepted rationale
- [ ] If LOC / file count / commit count tripwires are exceeded, `review.md` explicitly justifies why this is still one feature
- [ ] DRY violations are resolved or explicitly accepted (Rule of Three applied)
- [ ] SOLID compliance verified (or violations are documented with follow-up tickets)
- [ ] Function/file lengths within team standards (per `CODE_FORMATTING.md` and `FUNCTIONS_AND_ROUTINES.md`)
- [ ] Diff is reviewable — split into logical commits, each commit has a clear single purpose
- [ ] Security review passed
- [ ] All tests still green
- [ ] `review.md` written with findings labelled by severity

## Hand-Off to DOCS

Once REVIEW is done:
- **DOCS** can now write the runbook entries and update project documentation knowing the code is stable

Tell the user: "REVIEW is complete. {N} smells fixed, {M} follow-up tickets created. Code is clean and reviewable. DOCS can finalize. Tag your next entry as `{feature-id} docs`."

## When NOT to Refactor

The REVIEW bucket can become a black hole if you let it. Stop refactoring when:
- Tests are green AND the diff is reviewable
- Remaining smells are in code outside this feature's scope (note them, don't fix them here)
- Time-to-ship pressure outweighs polish (note debt, ship, fix later)

## Example Trigger

> "FUNC, ERRORS, and OBSV are all done on F-14 returns. Review and clean it up before PR."

→ Activate this skill. Run smell detector, SOLID validator, DRY check. Refactor. Adversarial review. Security review. Produce `review.md`.
