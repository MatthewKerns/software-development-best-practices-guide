---
name: errors-orchestrator
description: Master orchestrator for the Error Handling & Retry bucket of the Feature Factory pipeline. Use this skill when designing error handling for a feature, enumerating failure modes for an integration, deciding retry policies, building an error matrix, or hardening code against production failures. Triggers on phrases like "what could go wrong with this feature", "design error handling for X", "enumerate error codes from {API}", "retry strategy for", "make this code production-safe", "error matrix for the integration", or whenever a Clockify entry uses the bucket tag `errors`. This skill turns happy-path code into resilient code by systematically cataloguing failures and prescribing handling strategies.
allowed-tools: [Read, Edit, Grep, Glob, WebFetch]
---

# Error Handling Orchestrator (ERRORS bucket master)

## Purpose

You are the master agent for the **ERRORS bucket** of the Feature Factory pipeline. Your job is to take working happy-path code and make it resilient: enumerate every way it can fail, design how each failure is caught and recovered from, and instrument the code with the appropriate error-handling pattern. You produce an error matrix (`errors.md`) that the OBSV bucket uses to decide what to log and the DOCS bucket uses to write runbook entries.

This is the highest-leverage bucket Matthew has historically underweighted. The moment right after FUNC builds something is when context about what could go wrong is freshest. Capture it now or lose it forever.

## When This Bucket Is Active

Activate the ERRORS bucket when:
- FUNC has produced working code with a passing happy path
- A user says "what could go wrong", "harden this", "error handling for", "retry policy"
- An integration with an external API (TikTok, Stripe, etc.) is being added or extended
- A production incident revealed a missing error path
- The Clockify entry uses the tag `errors`

## Inputs Required Before Starting

- Working code from the FUNC bucket
- `func.md` summary of what was built
- Integration API documentation for any external calls (TikTok docs, Stripe docs, etc.)
- Knowledge of upstream failure modes (or willingness to research them)

If integration docs aren't available, fetch them. Do not guess at error codes or retry semantics.

## Output Artifact

Produce `.feature-factory/errors.md` containing the error matrix:

```markdown
# Error Matrix: {Feature Name}

## Scope
What code paths this matrix covers.

## Strategy: Correctness vs Robustness
- **Critical paths (correctness-first)**: {list} — fail loudly on error rather than produce wrong results.
- **Optional paths (robustness-first)**: {list} — degrade gracefully rather than fail the request.
- **Rationale**: {why this split fits the feature}

## External Failure Sources

### {Integration Name 1, e.g., TikTok Order API}

| Error Code | Meaning | Retry? | Backoff | Handling Strategy | User-Facing Behavior | Log Severity |
|------------|---------|--------|---------|-------------------|----------------------|--------------|
| 429 | Rate limited | Yes | Exponential, max 5 | Queue and retry | Silent retry, then "try again later" if exhausted | WARN |
| 5xx | Server error | Yes | Exponential, max 3 | Circuit breaker after 3 consecutive | "TikTok temporarily unavailable" | ERROR |
| 401 | Auth failed | No | — | Refresh token, retry once | "Session expired, please reconnect" | ERROR |
| ... | ... | ... | ... | ... | ... | ... |

## Internal Failure Sources

### Validation
- Empty input: throw `ValidationError`, 400 response, INFO log
- Out-of-range value: throw `ValidationError`, 400 response, INFO log

### Data Integrity
- Missing referenced entity: throw `NotFoundError`, 404 response, WARN log
- Concurrent modification: retry once with fresh fetch, then conflict response, WARN log

### Network / Timeouts
- Connection refused: retry with backoff, fail to user after 3 attempts, ERROR log
- Slow response (>5s): timeout and log, return cached or fail, ERROR log

## Retry Policy Summary
- Default: 3 attempts, exponential backoff starting at 1s, max 30s
- Idempotent operations: retry freely
- Non-idempotent: never retry without explicit idempotency token

## Catch Strategy
List of try/catch placements added to the code, with rationale.

## Open Questions
Anything that requires a product or business decision before final implementation.
```

## Sub-Skills To Direct To

| Need | Direct to | Why |
|------|-----------|-----|
| Define non-functional requirements (resilience targets) | `bmad-testarch-nfr` | Establishes what "good" means for this feature's reliability |
| Design tests for error paths | `bmad-testarch-test-design` | Every error in the matrix needs a test |
| Hunt for unconsidered edge cases | `bmad-review-edge-case-hunter` | The "what else could go wrong" pass |
| Investigate complex/mysterious failure modes | `geist-analyzer` | Use sparingly — only when standard analysis is stuck |
| Verify completeness of error handling | `gap-analyzer` | After the first pass, check what's missing |

## Best Practices Reference

These are your authoritative sources. The repo guides on error handling are exceptional — lean on them.

- `01-foundations/ERROR_HANDLING.md` — **PRIMARY**. The robustness vs correctness tradeoff, exception design, defining exceptions for callers, no null returns.
- `01-foundations/DEFENSIVE_PROGRAMMING.md` — **PRIMARY**. Validate at boundaries, assertions for programming errors, barricades, when defensive depth matters.
- `09-production-readiness/SECURITY_HARDENING.md` — for any error path involving auth, input validation, or sensitive data. Apply the "filter sensitive data" pattern (§5.1) to every log statement in an error path.
- `09-production-readiness/ROLLBACK_AND_RECOVERY.md` — for failures that need transactional rollback or recovery procedures. Note especially §2.1 on **expand-contract migrations**: any feature touching the database schema must use backward-compatible migrations so error handling includes graceful rollback paths.
- `99-reference/ERROR_HANDLING_CHECKLIST.md` — fast lookup during the matrix build

## Workflow

1. **Validate inputs** — confirm working code exists and integration docs are accessible.
2. **Choose strategy: correctness vs robustness** (per `ERROR_HANDLING_CHECKLIST.md`). This is a foundational decision that shapes every row of the matrix:
   - **Correctness** — fail rather than give a wrong answer. Use for financial, medical, legal, or anything where a silent wrong result is worse than a loud failure. Payment processing, tax calculation, inventory writes.
   - **Robustness** — continue with degraded service rather than fail. Use for analytics, UI niceties, recommendation engines, logging. Better to lose a data point than crash the request.
   - **Hybrid (most features)** — critical paths are correctness-first; optional paths are robustness-first. State the split explicitly in `errors.md` so reviewers can verify.
3. **Define resilience targets** — invoke `bmad-testarch-nfr` to establish what "good error handling" means for this feature (e.g., 99.9% success rate, P99 latency < 500ms, zero data loss on transient failures).
4. **Enumerate external failure sources** — for each external call in the code, fetch the integration's error code documentation. List every error code the integration can return.
5. **Enumerate internal failure sources** — walk the code and identify validation failures, data integrity issues, network/timeout failures, concurrency issues.
6. **Separate programming errors from runtime errors** — per `ERROR_HANDLING.md`, use **assertions** for programming errors (invariants, preconditions, postconditions) and **exceptions** for runtime errors (user input, external failures). Do not use exceptions for bugs.
7. **Edge case hunt** — invoke `bmad-review-edge-case-hunter` to surface failure modes that aren't obvious from code reading.
8. **Design the matrix** — for each failure source, decide: retry policy, handling strategy, user-facing behavior, log severity. Apply patterns from `ERROR_HANDLING.md` and `DEFENSIVE_PROGRAMMING.md`.
9. **Apply barricade pattern** — identify the bucket boundaries (API entry points, integration call sites). Validate at the boundary, trust internally.
10. **Instrument the code** — add try/catch with the designed strategies. Each catch block must preserve context (don't swallow exceptions; wrap and rethrow with detail).
11. **Stuck on a complex failure?** — escalate to `geist-analyzer` only if the failure mode is genuinely mysterious.
12. **Completeness check** — invoke `gap-analyzer` to verify nothing was missed.
13. **Write `errors.md`** — fill in the matrix template, including the correctness/robustness decision from step 2.

## Acceptance Criteria

The ERRORS bucket is done when:
- [ ] Every external call in the new code has a documented failure handling strategy
- [ ] Every retry policy has explicit max attempts and backoff (no infinite retries, no silent retries on non-idempotent ops)
- [ ] User-facing errors are actionable (not raw stack traces)
- [ ] Error context is preserved through wrapping (no lost stack traces)
- [ ] Validation happens at barricades, not scattered through internals
- [ ] Sensitive data is never included in error messages (per SECURITY_HARDENING.md)
- [ ] `errors.md` is written and committed
- [ ] Tests exist for at least the high-severity error paths

## Hand-Off to OBSV and DOCS

Once ERRORS is done:
- **OBSV** consumes `errors.md` to decide what each error path needs to log, with what fields, at what severity. Every entry in your matrix becomes a log statement.
- **DOCS** consumes `errors.md` to write a runbook entry for each error: "If you see error X, check log field Y, likely cause is Z, resolution is W."

Tell the user: "ERRORS is complete. Error matrix has {N} entries. OBSV and DOCS can use this directly. Tag your next entries as `{feature-id} observe` or `{feature-id} docs`."

## Example Trigger

> "FUNC is done on F-14 returns. Now design the error handling — what can go wrong with the TikTok returns API?"

→ Activate this skill. Fetch TikTok API error code docs. Enumerate. Design matrix. Instrument code. Produce `errors.md`.
