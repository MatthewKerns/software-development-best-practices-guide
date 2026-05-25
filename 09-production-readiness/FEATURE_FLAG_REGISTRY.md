# Feature Flag Registry Guide

## Overview

A feature flag registry is a single, version-controlled YAML file that is the **source of truth for every flag in the system**. It does not own targeting logic — your flag platform (PostHog, LaunchDarkly, a custom service) owns rollout percentages, cohorts, and per-org overrides. The registry owns **identity, type, ownership, intent, and expiry**, and a CI check enforces the one rule that flag debt reliably violates: release flags must not outlive their purpose.

**Key Principles:**
- **One file, one truth:** every flag the system reads is declared in one place, reviewed in code review, and diffable in git history.
- **Targeting stays in the platform:** rollout % and cohorts belong in the flag platform UI; the registry records *what the flag is* and *who owns it*, not *who currently has it on*.
- **Flags are temporary by default:** a release flag is a promise to delete the flag later. The registry makes that promise machine-enforceable.
- **CI is the cleanup mechanism:** an expired release flag fails the build, forcing a renew-or-remove decision instead of letting dead flags accumulate.

**Complexity Tiers:**
- **Small-Scale:** a handful of flags, manual review. The registry doubles as documentation.
- **Medium-Scale:** dozens of flags across multiple environments. CI expiry enforcement becomes essential.
- **Large-Scale:** flags spanning multiple platform projects, tiers, and teams. The registry is the contract that keeps ops, billing, and product flags from colliding.

---

## 1. Why a Single YAML Registry

Feature flags rot. Each one starts as a deliberate rollout mechanism and, if nothing forces a decision, quietly becomes a permanent `if` branch nobody dares delete. The two failure modes are well known:

1. **Flag debt:** flags that shipped to 100% months ago but still gate code, doubling the number of paths every test and reader must reason about.
2. **Shadow configuration:** flags scattered across env vars, hardcoded booleans, and platform UIs with no inventory — so nobody can answer "what controls this behavior?" without grepping the codebase.

A registry fixes both by centralizing flag *identity* while leaving *targeting* where it belongs:

| Concern | Owned by the registry (YAML) | Owned by the flag platform (UI/API) |
|---------|------------------------------|-------------------------------------|
| Flag exists / its canonical name | ✅ | — |
| Type, owner, description, intent | ✅ | — |
| Default state at code level | ✅ | — |
| Expiry / renewal commitment | ✅ | — |
| Rollout percentage | — | ✅ |
| Cohort / per-org targeting | — | ✅ |
| Live on/off per environment | — | ✅ |

This split is the whole point: code review catches "you added a flag without an owner or expiry," while ops keeps the freedom to flip cohorts at runtime without a deploy.

**The registry is platform-agnostic.** A `posthog_key` field is one binding; the same registry could carry a `launchdarkly_key`, a `flagsmith_id`, or nothing at all for flags resolved by a custom in-house service. The taxonomy and lifecycle below apply regardless of vendor.

---

## 2. The Flag Taxonomy

Every flag declares a **type**. The type determines its lifecycle expectations, who owns it, and whether CI enforces expiry. Three types cover the vast majority of real systems:

### 2.1 `ops` — Operational Toggles and Kill-Switches

Long-lived flags that control operational behavior: maintenance mode, a kill-switch for an integration, routing to a beta endpoint. These are **expected to be permanent** or to live as long as the subsystem they guard.

- **Owner:** the platform/infra team or the team that owns the subsystem.
- **Lifecycle:** no expiry. They are part of the operational toolkit.
- **CI:** not subject to expiry enforcement.
- **Examples:** `ops_maintenance_mode` (pre-auth kill-switch), `ops_amazon_oauth_beta_mode` (routes OAuth via a draft endpoint).

A kill-switch's most important property is its **fail-safe direction.** Document whether it fails *open* (feature stays on if the flag service is unreachable) or *closed* (feature disables). For a maintenance-mode or security gate, fail **closed**; for a non-critical enhancement, fail **open** so a flag-service outage doesn't take down the product.

### 2.2 `release` — Temporary Rollout Gates

Flags that gate a new feature during its rollout. They exist to ship code dark, ramp it via cohorts, and then **retire once the feature reaches GA**. These are the flags that become debt if left unmanaged.

- **Owner:** the product/feature team shipping the feature.
- **Lifecycle:** **must carry an `expires_at`.** When the feature graduates to GA, the flag and its branches are deleted.
- **CI:** **enforced** — an expired `release.*` flag without renewal fails the build.
- **Examples:** `release_profit_planning` (gates a beta page + nav, default 0% rollout), `mcp_server_enabled` (global kill-switch during an alpha, retires at GA).

A release flag often doubles as an emergency kill-switch during its life. That is fine — but its identity is still "temporary rollout gate," so it carries an expiry. The expiry window should cover the planned rollout plus a buffer for the GA decision (e.g., a 60-day runway covering an alpha plus the graduate-or-replace decision).

### 2.3 `entitlement` — Tier / Plan-Based Access

Flags that grant access based on a customer's plan or tier (Pro/Expert/Enterprise). These are **not rollout mechanisms** — they are a permanent product/billing matrix.

- **Owner:** the billing/monetization team.
- **Lifecycle:** permanent; changes when the plan matrix changes.
- **CI:** not subject to expiry enforcement.
- **Resolution:** often **matrix-only** — resolved by a tier-to-features lookup table in code, *not* a platform flag. Mark these `matrix_only: true` so readers know there is no platform key to look up.
- **Example:** `entitlement_mcp_access` (tiers `[Pro, Expert, Enterprise]`, resolved from a `TIER_FEATURES` table).

> **Taxonomy is the load-bearing decision.** When you can't decide a flag's type, you usually haven't decided its lifecycle. "Is this temporary?" → `release`. "Is this an operational lever?" → `ops`. "Is this who-paid-for-what?" → `entitlement`.

---

## 3. Required Fields

Every flag entry declares a minimum set of fields so the registry is self-documenting and CI-checkable.

| Field | Required | Applies to | Purpose |
|-------|:---:|------------|---------|
| `name` | always | all | Canonical, unique identifier. Convention: `<type>_<feature>` (e.g. `release_profit_planning`). |
| `type` | always | all | One of `ops` / `release` / `entitlement`. Drives lifecycle + CI. |
| `owner` | always | all | The team accountable. Not a person — a team, so ownership survives turnover. |
| `description` | always | all | What the flag controls, what it replaced, and its fail-safe direction. Multi-line YAML block. |
| `created_at` | always | all | ISO date the flag was added. Anchors age + expiry math. |
| `expires_at` | **release only** | `release` | ISO date after which CI fails unless renewed. The renew-or-remove deadline. |
| `posthog_key` (or vendor key) | when platform-bound | `ops`, `release` | The platform-side flag key. Omit for matrix-only flags. |
| `posthog_projects` (or env list) | when platform-bound | `ops`, `release` | Which platform projects/environments the flag exists in (e.g. staging + prod). |
| `<vendor>_default_rollout` | recommended | `release` | The intended default rollout % (e.g. `0` to ship dark). Documents intent vs. live state. |
| `backend_registry_default` | recommended | `release` | The code-level default the backend resolves to when the platform is unreachable. |
| `matrix_only` | when applicable | `entitlement` | `true` when resolved by an in-code table, not a platform flag. |
| `tiers` | entitlement only | `entitlement` | The plans that unlock the feature. |
| `hard_disabled_in` | when applicable | `ops` | Environments where the flag is force-disabled regardless of platform state. |
| `related_adr` | recommended | all | ADR(s) that decided this flag — links intent to the architecture record. |

**Field design guidance:**
- **`owner` is a team, never a person.** People leave; teams persist. A flag whose owner left the company is orphaned debt.
- **`description` should state what the flag *replaced*.** Flags frequently supersede an env-var anti-pattern or a per-row DB column; recording that prevents the old mechanism from creeping back.
- **`description` must state the fail-safe direction for any kill-switch.** "Fail-CLOSED on auth service unreachable" is operational gold at 2am.
- **Distinguish *intended default* from *live state*.** `default_rollout: 0` records intent ("ships dark"); the live rollout lives in the platform and may differ. Both are useful; don't conflate them.

---

## 4. The Flag Lifecycle

```
   CREATE ──► ROLL OUT ──► RAMP ──► GRADUATE ──► CLEAN UP
   (PR adds   (default     (cohorts  (decide:     (delete flag
    entry +    0%, ships    via       GA or kill)  + all branches
    expiry)    dark)        platform)              + registry row)
                                          │
                                          └──► RENEW (push expires_at
                                               out, document why)
```

### 4.1 Creation
A flag is born in a **pull request** that adds its registry entry alongside the code that reads it. Review checks: correct type, a real team owner, a clear description, and — for release flags — a sensible `expires_at`. The flag is also created in the platform (or the in-code matrix) with its default state.

### 4.2 Rollout (ship dark)
Release flags ship at **0% default rollout** so the code path is present but inert. This decouples *deploy* from *release*: the feature is in production but reaches no users until ops decides otherwise. The registry records the *intended* default; the platform holds the *live* value.

### 4.3 Ramp
Ops increases the rollout via the platform UI — percentage ramps, internal-staff cohorts, then named-customer cohorts — **without any code change or deploy.** The registry does not track these per-cohort moves; that churn belongs in the platform's audit log.

### 4.4 Graduation
When the feature is proven, make the **graduate-or-kill** decision:
- **Graduate to GA:** turn the feature on for everyone, then **delete the flag** — remove its registry row, its platform key, and every `if (flag)` branch in code. The feature is now just "how the product works."
- **Replace:** if the flag is superseded by a finer-grained mechanism (e.g. a per-endpoint grant table), retire the flag and document the replacement.

### 4.5 Cleanup
Deleting a flag means deleting **all** of it: registry row, platform key, and code branches. A flag removed from the registry but left in code is worse than no registry at all — it lies. Treat flag removal as a normal PR with its own diff.

### 4.6 Renewal
If a rollout legitimately needs longer than planned (an alpha extends, a GA decision slips), **push `expires_at` forward in a PR and say why** in the description or a comment. Renewal is a deliberate, reviewed act — not a silent bump to mute CI. The audit trail of *why* a flag was renewed is itself valuable.

---

## 5. CI Enforcement: Fail on Expired Release Flags

The single enforcement rule that keeps the registry honest:

> **CI fails when any `release.*` flag has an `expires_at` in the past and has not been renewed.**

This converts flag cleanup from "someone should really delete these someday" into a **blocking, unavoidable decision** at a predictable time. When the build goes red, the owning team must do one of three things — all of them healthy:

1. **Delete the flag** (the feature graduated; do the cleanup).
2. **Renew the flag** (push `expires_at` out, with a documented reason).
3. **Reclassify the flag** (it turned out to be an `ops` lever, not a temporary gate — change its type, which removes it from expiry enforcement).

### Why only release flags
`ops` and `entitlement` flags are expected to be long-lived, so expiry enforcement would only generate noise-renewals. Only `release` flags carry the "I will be deleted" promise, so only they are policed. A linter can additionally warn (not fail) when an `ops` flag is suspiciously old, but the hard gate is reserved for release flags.

### Reference check (language-agnostic pseudocode)

```python
# ci/check_flag_expiry.py — run in CI on every PR + on a daily schedule
import sys, datetime, yaml

def check(registry_path: str) -> int:
    today = datetime.date.today()
    flags = yaml.safe_load(open(registry_path))["flags"]
    expired = []
    for flag in flags:
        if flag.get("type") != "release":
            continue                       # only release flags are policed
        expires = flag.get("expires_at")
        if not expires:
            expired.append((flag["name"], "release flag missing expires_at"))
            continue
        if datetime.date.fromisoformat(str(expires)) < today:
            expired.append((flag["name"], f"expired {expires}"))
    for name, why in expired:
        print(f"::error:: feature flag '{name}': {why} — renew or remove")
    return 1 if expired else 0

if __name__ == "__main__":
    sys.exit(check("flag_registry.yaml"))
```

Wire it into the pipeline as a required check:

```yaml
# .github/workflows/flag-registry.yml
name: Feature Flag Registry
on:
  pull_request:
  schedule:
    - cron: "0 13 * * 1"   # Monday 13:00 UTC — catches flags that expire between PRs
jobs:
  check-expiry:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - run: python ci/check_flag_expiry.py
```

The **scheduled run matters as much as the PR run.** A flag can expire on a day when nobody opens a PR; the weekly cron guarantees the red build appears even during quiet periods, so cleanup never silently slips.

### Optional companion checks
Once the expiry gate is in place, cheap additional validations pay off:
- **Schema validation:** every flag has a valid `type`, a non-empty `owner`, and a `description`.
- **Name uniqueness + convention:** no duplicate `name`; names match `<type>_<slug>`.
- **Code/registry drift:** grep the codebase for flag-read call sites and assert every referenced key exists in the registry (and warn on registry keys with zero readers — candidate dead flags).

---

## 6. Tool-Agnostic Bindings

The registry's value is independent of the flag platform. Swap the binding fields to match your vendor:

| Platform | Identity field(s) in the registry | Notes |
|----------|-----------------------------------|-------|
| **PostHog** | `posthog_key`, `posthog_projects` | Targeting (rollout %, cohorts) lives in PostHog; registry holds intent + expiry. |
| **LaunchDarkly** | `launchdarkly_key`, `environments` | Same split; LD owns variations + rules, registry owns lifecycle. |
| **Flagsmith / Unleash / custom** | `<vendor>_id` or `service_key` | Any platform with a server-evaluated flag fits the same pattern. |
| **In-code matrix** | `matrix_only: true` | Entitlement-style flags resolved by a code table; no platform key at all. |

What stays constant across all of them: **name, type, owner, description, created_at, and (for release flags) expires_at.** Those fields — and the CI gate over them — are the portable core of the pattern.

---

## 7. Common Anti-Patterns

### ❌ Don't
- Gate features with bare env vars (`FEATURE_X_ENABLED=true`) — invisible to the registry, requires a deploy to flip, and has no owner or expiry.
- Create a release flag without an `expires_at` (it's just permanent debt with extra steps).
- Assign a *person* as `owner` (orphaned the moment they change teams).
- Delete a registry row but leave the `if (flag)` branches in code — the registry now lies.
- Renew an expiry silently to mute a red build without recording why.
- Track per-cohort rollout state in the YAML — that churn belongs in the platform.

### ✅ Do
- Add the registry entry in the same PR as the code that reads the flag.
- Default release flags to 0% rollout so deploy ≠ release.
- Make `owner` a team and `description` state what the flag replaced + its fail-safe direction.
- Run the expiry check on **both** PRs and a schedule.
- Treat flag removal as a normal, reviewed diff: registry row + platform key + code branches, together.
- Link each flag to the ADR that decided it (`related_adr`).

---

## Template

A ready-to-copy, project-agnostic starting point lives alongside this guide:

📄 **[flag_registry.template.yaml](flag_registry.template.yaml)** — commented template with one example per flag type (`ops`, `release`, `entitlement`) and placeholder fields.

---

## Related Documentation

### Within Production Readiness
- **[README.md](README.md)** — Area 5 (Deployment & Release) lists feature flags as a core capability.
- **[ROLLBACK_AND_RECOVERY.md](ROLLBACK_AND_RECOVERY.md)** — kill-switch flags are a first-class rollback mechanism: disabling a release flag is often faster and safer than a code rollback.
- **[PRODUCTION_READINESS_FRAMEWORK.md](PRODUCTION_READINESS_FRAMEWORK.md)** — deployment & release validation checklist.

### Related Guides
- **03-clean-architecture/** — resolve flags behind a thin interface so the platform binding is swappable (see the tool-agnostic bindings above).
- **09-production-readiness/SECURITY_HARDENING.md** — fail-closed direction for security-relevant kill-switches.

---

**Status:** Pattern documentation — single-YAML feature flag registry with CI expiry enforcement
**Last Updated:** 2026-05-25
**Maintainer:** Development Best Practices Repository
