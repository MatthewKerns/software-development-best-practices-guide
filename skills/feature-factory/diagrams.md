# Integration Diagrams: Feature Factory ↔ pr-prep ↔ refactor-pipeline

Four mermaid diagrams describing how the three skill families compose end-to-end. GitHub renders these natively. For an offline / self-contained view with the same diagrams, open [`diagrams.html`](./diagrams.html) in a browser.

Reading order if you're new to the wiring:
1. **Timeline** — when each skill family fires
2. **Ownership** — who writes what, who reads what
3. **pr-prep ↔ FF handshake** — how Phase 2c and Phase 3 consume FF artifacts
4. **refactor-pipeline ↔ FF** — the new 1.4.1 wiring

---

## 1. End-to-end timeline — when each skill family fires

```mermaid
flowchart TB
    subgraph DEV["DEVELOPMENT (per feature, in feature worktree)"]
        ARCH[arch-orchestrator]
        FUNC[func-orchestrator]
        ERR[errors-orchestrator]
        OBS[obsv-orchestrator]
        REV[review-orchestrator]
        DOC[docs-orchestrator]
        ARCH --> FUNC
        FUNC --> ERR
        FUNC --> OBS
        FUNC --> REV
        ERR --> DOC
        OBS --> DOC
        REV --> DOC
    end

    subgraph RP["REFACTOR PIPELINE (called by REVIEW or ad-hoc)"]
        RD[refactor-detector]
        RPL[refactor-planner]
        RX[refactor-executor]
        RV[refactor-validator]
        RD --> RPL --> RX --> RV
        RV -. fail loops back .-> RPL
    end

    subgraph PRP["PR TIME (per PR)"]
        P12["Phase 1-2<br/>Scope + base branch"]
        P2C["Phase 2c<br/>Detect FF artifacts"]
        P3["Phase 3<br/>4 parallel agents"]
        P4["Phase 4<br/>Synthesis +<br/>append pr-history row"]
        P45["Phase 4.5<br/>Docs commit plan"]
        P5["Phase 5+<br/>(opt-in) assets, E2E, video"]
        P12 --> P2C --> P3 --> P4 --> P45 --> P5
    end

    REV -. invokes when non-trivial cleanup .-> RP
    DOC ==>|feature complete, ready for PR| PRP
```

---

## 2. Artifact ownership — who writes what, who reads what

```mermaid
flowchart LR
    subgraph FOLDER[".feature-factory/&lt;slug&gt;/"]
        A[arch.md]
        F[func.md]
        E[errors.md]
        O[observability.md]
        R[review.md]
        RB[runbook.md]
        PH[pr-history.md]
    end

    arch[arch-orchestrator] -- writes --> A
    func[func-orchestrator] -- writes --> F
    errs[errors-orchestrator] -- writes --> E
    obsv[obsv-orchestrator] -- writes --> O
    rev[review-orchestrator] -- writes --> R
    docs[docs-orchestrator] -- writes --> RB

    rpipe[refactor-pipeline] -- appends '## Refactor Pass' --> R
    rval[refactor-validator] -. reads 'Fix in this PR' claims .-> R

    pp[pr-prep] == sole writer of new rows ==> PH
    arch -. may update Status only .-> PH
    rev -. may update Status only .-> PH

    pp -- reads all 6 .md as authoritative --> FOLDER
```

Solid arrows = writes / reads. Bold double arrow = exclusive ownership. Dotted arrows = update-narrowly-only.

---

## 3. pr-prep ↔ FF handshake (Phase 2c → Phase 3)

```mermaid
flowchart TB
    subgraph FF["FF artifacts (input)"]
        A[arch.md]
        F[func.md]
        E[errors.md]
        O[observability.md]
        R[review.md]
        RB[runbook.md]
    end

    P2C["Phase 2c<br/>FF detection"]
    CTX["feature-factory-<br/>context.md<br/>(digest, written first)"]

    A --> P2C
    F --> P2C
    E --> P2C
    O --> P2C
    R --> P2C
    RB --> P2C
    P2C --> CTX

    subgraph AGENTS["Phase 3 — 4 parallel agents"]
        AG1["Agent 1<br/>PRD gap"]
        AG2["Agent 2<br/>Code/test audit<br/>verifies review.md claims"]
        AG3["Agent 3<br/>Docs audit<br/>maps FF → docs targets"]
        AG4["Agent 4<br/>Manual testing"]
    end

    CTX --> AG1
    CTX --> AG2
    CTX --> AG3
    CTX --> AG4
    A -. additional read .-> AG1
    F -. additional read .-> AG1
    F -. additional read .-> AG2
    R -. additional read .-> AG2
    RB -. additional read .-> AG3
    A -. additional read .-> AG3
    E -. additional read .-> AG3
    O -. additional read .-> AG3
    E -. additional read .-> AG4
    O -. additional read .-> AG4

    AG1 --> SYN["Phase 4 synthesis<br/>pr-description.md +<br/>append pr-history.md row"]
    AG2 --> SYN
    AG3 --> SYN
    AG4 --> SYN

    SYN --> P45["Phase 4.5<br/>per-row approval to commit<br/>FF artifacts into docs/"]
    P45 -. EDIT .-> ARCH_DOC["docs/architecture/<br/>ARCHITECTURE.md"]
    P45 -. CREATE .-> RUNBOOK["docs/runbooks/<br/>&lt;feature&gt;.md"]
    P45 -. CREATE .-> ERR_DOC["docs/features/<br/>&lt;feature&gt;-error-handling.md"]
    P45 -. CREATE .-> OBS_DOC["docs/features/<br/>&lt;feature&gt;-observability.md"]
```

---

## 4. refactor-pipeline FF-context decision (the 1.4.1 wiring)

```mermaid
flowchart TD
    Start([refactor-pipeline invoked]) --> Walk[Walk up from cwd<br/>find .feature-factory/]
    Walk --> Exists{".feature-factory/<br/>exists?"}
    Exists -->|no| OutA["Standalone:<br/>_refactor-output/&lt;ts&gt;/"]
    Exists -->|yes| Count{How many<br/>feature folders?<br/>(excluding reserved)}
    Count -->|0| OutB[".feature-factory/<br/>_refactor/&lt;ts&gt;/"]
    Count -->|1| Active[Active feature<br/>identified]
    Count -->|2+| Hist{Any pr-history.md<br/>has 'in-progress' or<br/>'open' top row?}
    Hist -->|exactly one| Active
    Hist -->|ambiguous| Ask[Ask the user<br/>which feature]
    Ask --> Active

    Active --> Append["Append to<br/>.feature-factory/&lt;slug&gt;/review.md<br/><br/>## Refactor Pass — YYYY-MM-DD<br/>scope / smells / SOLID / metrics / verdict"]
    Append --> Detail["Detail reports to<br/>.feature-factory/_refactor/&lt;ts&gt;/<br/>(smell-report.json, plan.md,<br/>validation-report.md)"]
    Detail --> Validate["refactor-validator<br/>cross-checks review.md<br/>'Fix in this PR' claims<br/>against the diff"]
    Validate --> Pass{All claims<br/>resolved?}
    Pass -->|yes| OK[PASS]
    Pass -->|"[CRITICAL]/[BLOCKER]<br/>unresolved"| Fail[FAIL]
    Pass -->|"[ISSUE]<br/>unresolved"| Notes[PASS WITH NOTES]
    Fail -. loops back .-> Active
```

---

## See also

- [`INTEGRATION_WITH_PR_PREP.md`](./INTEGRATION_WITH_PR_PREP.md) — the canonical integration spec (ownership rules, layout, dispositions)
- [`README.md`](./README.md) — the Feature Factory skill family overview
- [`USER_GUIDE.md`](./USER_GUIDE.md) — how to drive the pipeline as a user
