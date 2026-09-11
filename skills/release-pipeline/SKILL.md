---
name: release-pipeline
description: |
  Map and scaffolder for the whole release skill set — start here to know which
  deployment skill to use. Spine: release-verify-local (before commit/PR) →
  release-stage-verify (after merge) → release-queue → prod-deploy-review → release-deploy-prod.
  Plus deploy-all-to-staging (continuous staging loop) and staging-test-sweep
  (verify everything unverified), and the sub-skills deploy-edge-functions (no
  staging for that layer) and deploy-database (migrations, RLS, data ops). Use
  when the user asks "how do releases work", "which deploy skill", wants to set
  up or scaffold docs/RELEASE_PIPELINE.md, or invokes release-pipeline. Every
  stage skill reads that per-project manifest; this skill creates it.
allowed-tools: [Read, Write, Edit, Bash, Grep, Glob]
---

# Release Pipeline — Overview & Project Scaffolder

A two-layer release system:

- **Generic layer (these skills, synced from the guide):** the pipeline logic —
  what to verify, when to gate, how to queue, how to run the weekly deploy.
  Never contains project-specific commands.
- **Project layer (`docs/RELEASE_PIPELINE.md` in each repo):** the facts the
  generic skills must not guess — verification gates, deploy commands or runbook
  pointers, URLs, smoke routes, queue location, deploy cadence. Deploy commands
  are dangerous to infer (wrong rsync flags have destroyed staging content in
  real projects), so the deploy-stage skills **fail closed** without this file.

## The pipeline

**The spine — four stages, in order:**

| Stage | Skill | When |
|-------|-------|------|
| 1. Local verification | `release-verify-local` | Before **committing**, and before opening a PR |
| 2. Staging verification | `release-stage-verify` | After a PR merges |
| 3. Queue for prod | `release-queue` | After staging verification passes; inspect any time |
| 3.5 Pre-deploy gate | `prod-deploy-review` | Before the prod deploy. Classifies BLAST RADIUS, spawns only the reviewer lenses that radius warrants, emits GO / NO-GO / GO WITH CONDITIONS. Reviews and gates; never deploys. |
| 4. Production deploy | `release-deploy-prod` | On the project's deploy day |

**Two skills that keep staging honest:**

| Skill | Job |
|-------|-----|
| `deploy-all-to-staging` | Continuous loop: new commit → merge → deploy → verify, so staging always equals the integration branch. Deploys. |
| `staging-test-sweep` | Sweeps for **everything** nobody has verified, not one PR at a time. Read-only: verifies and reports, never deploys. |

They are a pair: the loop keeps staging *current*, the sweep proves what on it is
actually *exercised*. Neither substitutes for the other — a current staging full
of unverified changes is exactly how a stakeholder gets sent a broken URL.

**Sub-skills for layers that do not follow the SPA path** — hand off to these
rather than guessing, and note the loop deliberately refuses to deploy them:

| Layer | Skill | Why it is different |
|-------|-------|---------------------|
| Edge / serverless functions | `deploy-edge-functions` | Usually **no staging** — one backend serves every frontend, so deploying IS a prod change. Shadow-slug protocol, ask-first. |
| Database: migrations, RLS, data ops | `deploy-database` | Least reversible thing in any deploy. Human-gated, never automated. |

Flow: verified locally → committed → PR → merged → staging (loop) → swept →
queued as `staging-verified` → prod → logged with evidence.

## Where verification happens, and by whom

- **Before a commit** — the author, locally. Everything downstream trusts this.
- **After a deploy** — against the *served artifact*, which local gates cannot see.
- **Before a stakeholder looks** — the sweep, plus a human brief for the checks
  automation structurally cannot do (visual judgement, real devices, real email).

Confusing these is how "it passed" and "it works" drift apart.

## Scaffolding a project's manifest

When a project lacks `docs/RELEASE_PIPELINE.md`:

1. **Inspect before asking.** Read `package.json` scripts, existing deploy docs
   (`docs/DEPLOYMENT.md`, `README`, CI workflows), and `AGENTS.md`/`CLAUDE.md`
   testing protocols. Most answers are already written down.
2. **Point, don't duplicate.** If a deploy runbook already exists, the manifest
   links to it for command detail and holds only pipeline facts (gates list,
   URLs, queue path, cadence). Two copies of an rsync command will drift.
3. Fill `PROJECT_LAYER_TEMPLATE.md` (next to this SKILL.md) and write it to
   `docs/RELEASE_PIPELINE.md`. Ask the user only for facts you cannot find:
   typically the deploy day and anything undocumented about staging.
4. Seed the deploy queue file at the path the manifest declares
   (default `docs/release/DEPLOY_QUEUE.md`) with empty `## Queue` and
   `## Deploy log` sections.

## Rules that apply to every stage

- **Never guess deploy commands.** No manifest (and no runbook it points to) →
  stop and scaffold; do not reconstruct commands from memory or analogy.
- **Verify over HTTP, not on disk.** A deploy is verified only when the *served*
  artifact (bundle hash, health endpoint) matches what was built.
- **Build from the latest integration tip immediately before any deploy.**
  Deploying a stale build silently reverts other people's merged work
  (observed failure mode, not hypothetical).
- **Evidence or it didn't happen.** Every verification records what was run,
  against which commit, with what result — in the PR, the queue entry, or the
  deploy log.
- **Never infer deployed state from git.** Ancestry proves neither content nor
  deployment: manual deploys are untied to any ref, and the same fix often lands
  again under a different commit. Infer content from `git show <ref>:<path>`, and
  deployed behaviour from the **served artifact**.
- **Grep served artifacts for string literals, never symbol names.** Production
  bundles are minified, so a function name returns 0 hits whether or not the code
  is there. Include a control literal to prove the file is even bundled.
- **A gate that could not run is not a passed gate.** Say which one, why, and
  what evidence you have instead. Never silently substitute a weaker check — and
  be suspicious of a check that reports success suspiciously fast or cannot fail.
- **Verify the instrument before trusting it.** A green check is only evidence if
  it can go red. Type-check and test commands can be silently scoped to nothing.
- **Prefer behavioural verification with real data** for behavioural defects. A
  unit test encodes the author's assumption about the failure — which is the very
  thing that was wrong. Reproduce the user's actual condition, including
  first-time/empty state, which existing accounts cannot reproduce.
