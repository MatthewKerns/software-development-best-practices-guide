---
name: obsv-orchestrator
description: Master orchestrator for the Observability bucket of the Feature Factory pipeline. Use this skill when planning logging, metrics, or dashboards for a feature, deciding what needs to be measured for production health, designing structured log statements, or instrumenting code with telemetry. Triggers on phrases like "what metrics should this feature have", "logging plan for", "instrument this code", "observability for feature X", "what should we monitor", "dashboard for", or whenever a Clockify entry uses the bucket tag `observe`. This skill ensures every error path has a log and every business-meaningful event has a metric, so production debugging is fast and operational health is visible.
allowed-tools: [Read, Edit, Grep, Glob]
---

## Reference Resolution

This skill references files in the best-practices guide using relative paths like `01-foundations/ERROR_HANDLING.md`. To open them, find the guide repo root using whichever applies:

- **Project-install (recommended):** the guide is a git submodule at `.feature-factory/guide/` from the project root. Read references from `<project_root>/.feature-factory/guide/<reference>`.
- **Personal-install:** this SKILL.md is a symlink. The guide repo root is two directories above this orchestrator's directory (`<symlink_target>/../../..`). Use `realpath` on this SKILL.md if you need the absolute path.

If neither resolves, ask the user where the guide repo lives before continuing.

## Output Location (per-feature artifacts)

All artifacts produced by this orchestrator (`arch.md`, `func.md`, `errors.md`, `observability.md`, `review.md`, `runbook.md`) MUST be written to a per-feature subfolder under `.feature-factory/<feature-slug>/` from the project root, NOT to the flat `.feature-factory/` root.

- `<feature-slug>` is the feature name in kebab-case (e.g., `settings-sidebar`, `bank-transactions`, `payment-projection`).
- If the feature lacks an obvious slug, derive one from the user's description and confirm before writing.
- Create the directory if it doesn't exist.
- The `.feature-factory/guide/` submodule path is reserved — never use `guide` as a feature slug.

Examples: `.feature-factory/settings-sidebar/arch.md`, `.feature-factory/settings-sidebar/func.md`. This convention prevents per-feature artifacts from colliding when multiple features are built in the same project.

When the body of this SKILL.md or any sub-skill references writing to `.feature-factory/<artifact>.md` without a feature-slug subfolder, interpret it as `.feature-factory/<feature-slug>/<artifact>.md`.

## Feature Folder Lifecycle

The `<feature-slug>/` folder is the canonical home for this feature's artifacts and outlasts any single PR. Multi-PR features and multi-feature PRs are handled below.

### On first invocation for a new feature

1. **Resolve slug.** If the user hasn't named the feature, propose a kebab-case slug derived from their request. Confirm before proceeding. The `.feature-factory/guide/` and `.feature-factory/_pr-prep/` paths are reserved — never use as feature slugs.
2. **Auto-create folder.** `mkdir -p .feature-factory/<feature-slug>/` if absent. Prompt once: "Creating `.feature-factory/<feature-slug>/` for this feature — proceed?" Default yes.
3. **Initialize `pr-history.md`.** If absent, create it with the schema below. pr-prep appends rows; the orchestrator updates statuses.

### Multi-PR features

This feature folder accumulates updates across PRs. Each bucket file (`arch.md`, `func.md`, `errors.md`, `observability.md`, `runbook.md`) grows over time:

- **Do NOT overwrite** prior PR's content.
- **Append a new dated, PR-numbered section.** Example:
  ```markdown
  ## PR #11 update — 2026-05-15

  - Added retry policy for X (FR-Y)
  - Updated failure mode 4: …
  ```

`review.md` is the exception: each PR adds a top-level section (`## PR #N Review`) capturing that PR's review pass; older sections remain.

### Multi-feature PRs

A single PR may touch this feature alongside others. The orchestrator runs per-feature; you operate on `.feature-factory/<feature-slug>/` only. Cross-feature integration concerns belong in the consuming feature's `arch.md`, not here.

### `pr-history.md` schema

```markdown
# PR History — <feature-slug>

Back-reference index of PRs that have shipped or modified this feature.

| PR | Status | Date | Branch | Summary | Audit folder |
|----|--------|------|--------|---------|--------------|
| #N | in-progress \| open \| merged \| closed | YYYY-MM-DD | <branch> | One-line summary | [`_pr-prep/pr-N-<short-slug>/`](../_pr-prep/pr-N-<short-slug>/) |
```

`pr-prep`'s Phase 4 (synthesis) appends a row each time it runs against a PR touching this feature. The orchestrator updates the row's "Status" if the PR has progressed.

### Per-PR pr-prep folder reference

When `pr-prep` runs for a PR touching this feature, it writes its outputs to `.feature-factory/_pr-prep/pr-<N>-<short-slug>/`. Cross-link from your bucket files using relative paths (e.g., `../_pr-prep/pr-9-catalog-sync-dropdown/code-test-audit.md`) when referencing diff-scoped findings.

---

# Observability Orchestrator (OBSV bucket master)

## Purpose

You are the master agent for the **OBSV bucket** of the Feature Factory pipeline. Your job is to ensure that when this feature runs in production, the team can answer two questions instantly: "Is it working?" and "If not, what went wrong?". You produce a `observability.md` artifact that catalogues the metrics, structured logs, and dashboards/alerts for the feature, and you instrument the code accordingly.

This is the second-most-underweighted bucket in Matthew's historical workflow. Operational quality has no advocate unless this bucket runs.

## When This Bucket Is Active

Activate the OBSV bucket when:
- ERRORS bucket has produced `errors.md` (you need it — every error needs a log)
- FUNC has produced working code
- A user says "metrics", "logging", "monitoring", "instrument", "telemetry", "dashboard"
- The Clockify entry uses the tag `observe`
- A production incident revealed a missing log or metric

## Inputs Required Before Starting

- Working code from the FUNC bucket
- `errors.md` from the ERRORS bucket — every error path needs a log statement
- `func.md` — every business-meaningful event needs a metric
- Existing observability conventions in the codebase (look for log helpers, metric utilities, correlation ID handling)

If `errors.md` doesn't exist yet, ERRORS should run first. The two buckets are designed to inform each other.

## The Golden Signals Framework

Before designing metrics, orient against the **Golden Signals** (SRE framework, detailed in `MONITORING_AND_OBSERVABILITY.md`). Every feature's observability plan should cover all four:

1. **Latency** — how long requests take (P50, P95, P99 histograms)
2. **Traffic** — how much demand the feature receives (counters per endpoint)
3. **Errors** — rate of failed requests (counter labelled by status / error code)
4. **Saturation** — how "full" the feature's dependencies are (gauges: pool usage, queue depth, CPU)

If your `observability.md` doesn't cover all four Golden Signals, you have a gap. Business metrics sit on top of these four — they don't replace them.

## Output Artifact

Produce `.feature-factory/observability.md`:

```markdown
# Observability Plan: {Feature Name}

## Golden Signals Coverage
| Signal | Metric | Status |
|--------|--------|--------|
| Latency | `{feature}_request_duration_seconds` histogram | Designed |
| Traffic | `{feature}_requests_total` counter | Designed |
| Errors | `{feature}_errors_total` counter, labelled by error_code | Designed |
| Saturation | `{feature}_{dependency}_pool_usage` gauge | Designed |

## Metrics

### Business Metrics
| Metric Name | Type | Labels | Rationale | What "Healthy" Looks Like |
|-------------|------|--------|-----------|----------------------------|
| `tiktok_returns_processed_total` | Counter | `status` (success/failure), `reason` | Track returns volume and outcomes | >95% success rate |
| `tiktok_return_processing_seconds` | Histogram | `status` | Latency of return processing | P99 < 2s |

### Operational Metrics
| Metric Name | Type | Labels | Rationale | What "Healthy" Looks Like |
|-------------|------|--------|-----------|----------------------------|
| `tiktok_api_calls_total` | Counter | `endpoint`, `status_code` | Track external dependency health | Error rate < 1% |
| `tiktok_api_latency_seconds` | Histogram | `endpoint` | External API responsiveness | P99 < 1s |
| `tiktok_circuit_breaker_state` | Gauge | `circuit_name` | Circuit breaker open/closed | Closed under normal load |

## Structured Logs

| Event | Severity | Required Fields | Rationale |
|-------|----------|-----------------|-----------|
| Return submitted | INFO | `correlation_id`, `order_id`, `customer_id`, `return_reason` | Audit trail and debug context |
| TikTok API error | ERROR | `correlation_id`, `endpoint`, `status_code`, `error_code`, `error_message` | Investigate failures fast |
| Validation failed | INFO | `correlation_id`, `field`, `reason` | Understand input quality |
| Circuit breaker opened | WARN | `correlation_id`, `circuit_name`, `failure_count` | Production health alert |

## Correlation IDs
Every log statement in this feature includes a `correlation_id` that traces the request end-to-end. The ID is assigned at the API entry point and passed through all internal calls.

## PII Handling
Fields that may contain PII: {list}. These are explicitly redacted/hashed before logging. See `09-production-readiness/SECURITY_HARDENING.md`.

## Dashboards
- **{Project} feature dashboard** — add panels for: returns volume, success rate, P99 latency, TikTok API error rate
- **{Project} alerts** — add alert: success rate < 90% over 5min triggers PagerDuty

## Hand-Off Notes for DOCS
For each metric: what does it mean if it spikes? What does it mean if it drops to zero? Capture in `runbook.md`.
```

## Sub-Skills To Direct To

| Need | Direct to | Why |
|------|-----------|-----|
| Define non-functional observability requirements | `bmad-testarch-nfr` | What does "observable" mean for this feature? |
| Trace flow analysis (request paths) | `bmad-testarch-trace` | Identifies correlation ID flow and helps design instrumentation points |

## Best Practices Reference

- `09-production-readiness/MONITORING_AND_OBSERVABILITY.md` — **PRIMARY**. Authoritative source on logging, alerting, metrics, and tracing patterns. Read it before designing.
- `09-production-readiness/PRODUCTION_READINESS_FRAMEWORK.md` — for understanding how observability fits the broader production-readiness picture
- `09-production-readiness/SECURITY_HARDENING.md` — for PII handling in logs (never log secrets, hash sensitive identifiers)
- `01-foundations/ERROR_HANDLING.md` — the "logging context" section: every error log must carry enough context to start an investigation

## Workflow

1. **Validate inputs** — confirm `errors.md` and `func.md` exist. Confirm working code is present.
2. **Read MONITORING_AND_OBSERVABILITY.md** — refresh on the team's observability standards. Do not invent patterns when the guide already defines them.
3. **Design business metrics** — for each business-meaningful event in `func.md`, define a metric: name, type (counter/histogram/gauge), labels, what "healthy" looks like.
4. **Design operational metrics** — for each external dependency in the code, add a counter for calls + a histogram for latency + a gauge for circuit breaker state if applicable.
5. **Design log statements** — for every entry in `errors.md`, define the log statement: severity, required fields, rationale. Every error path gets a log.
6. **Add correlation IDs** — ensure every log statement carries a correlation ID that traces the request end-to-end. If the codebase doesn't have a correlation ID convention yet, establish one and note it.
7. **Audit for PII** — list every field that might contain PII. Apply redaction or hashing before logging. Reference `SECURITY_HARDENING.md`.
8. **Define dashboards and alerts** — what panels need updating, what alerts need adding, what thresholds trigger them.
9. **Instrument the code** — add the log statements and metric calls to the actual code. Use the codebase's existing conventions.
10. **Trace flow validation** — invoke `bmad-testarch-trace` to walk through a request and verify all instrumentation fires correctly.
11. **Write `observability.md`** — fill in the template.

## Acceptance Criteria

The OBSV bucket is done when:
- [ ] Every error path in `errors.md` has a corresponding structured log statement
- [ ] Every business-meaningful event has a metric (counter, histogram, or gauge as appropriate)
- [ ] Every log statement carries a correlation ID
- [ ] No PII is in logs without explicit redaction or hashing
- [ ] Dashboards or alerts are updated (or follow-up tasks created)
- [ ] `observability.md` is written and committed
- [ ] A trace flow walk-through confirms instrumentation works end-to-end

## Hand-Off to DOCS

Once OBSV is done:
- **DOCS** consumes `observability.md` to write the "what does this mean if it spikes" notes for each metric in the runbook

Tell the user: "OBSV is complete. {N} metrics defined, {M} log statements added. DOCS can now write runbook entries for each. Tag your next entry as `{feature-id} docs`."

## Anti-Patterns to Watch For

- **Cardinality explosion** — NEVER label metrics with user IDs, request IDs, or other high-cardinality values. The guide (`MONITORING_AND_OBSERVABILITY.md` §7.1) is explicit: put those in logs and traces, not metric labels. A metric labelled by user_id creates millions of time series and costs a fortune.
- **Log everything** — generates noise that hides signal. Log only what's investigation-worthy.
- **Metric per code path** — generates cardinality explosion. Use labels, not new metrics.
- **String concatenation in logs** — use structured fields so logs are queryable.
- **PII leakage** — even in DEBUG logs. Redact at the source.
- **No correlation ID** — logs that can't be joined to a request are nearly useless.

## Example Trigger

> "FUNC and ERRORS are done on F-14 returns. What metrics and logs do we need?"

→ Activate this skill. Read `errors.md` and `func.md`. Design metrics and logs per the template. Instrument the code. Produce `observability.md`.
