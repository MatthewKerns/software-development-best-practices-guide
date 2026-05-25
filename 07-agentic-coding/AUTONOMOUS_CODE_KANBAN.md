# Autonomous Code Kanban: Executing Agents on Git Worktrees

## Document Control

- **Version**: 1.0.0
- **Created**: 2026-05-25
- **Status**: Active
- **Audience**: AI agents, developers, tooling engineers

## Table of Contents

1. [Overview](#overview)
2. [The Reference Architecture](#the-reference-architecture)
3. [The ICodeAgentRunner Plugin Interface](#the-icodeagentrunner-plugin-interface)
4. [The WorktreeManager](#the-worktreemanager)
5. [The RunScheduler](#the-runscheduler)
6. [Kanban Stages and the Execution Gate](#kanban-stages-and-the-execution-gate)
7. [Sandboxing the Run](#sandboxing-the-run)
8. [Configuration Surface](#configuration-surface)
9. [Putting It Together](#putting-it-together)
10. [Anti-Patterns](#anti-patterns)

## Overview

This guide documents a **portable pattern** for building autonomous code execution on top of two primitives almost every team already has: **git worktrees** and the **Claude CLI/SDK**. The goal is a system where a refined spec on a kanban board can be turned into a running coding agent — in its own isolated checkout — with one button press, while keeping concurrency safe, runs auditable, and the execution backend swappable.

It is described as a reference architecture, not a framework. The pieces (a runner interface, a worktree manager, a scheduler, a staged board with a gate) compose into something you can rebuild in any language or web stack. The examples use Python signatures because they read clearly; the pattern is not Python-specific.

**The core idea:**
> A coding task is "ready" only when its spec is complete. Once ready, executing it means: resolve an isolated git worktree for the task, snapshot prior work, spawn an agent backend against that worktree under a concurrency policy, and stream its events back for observation — with the backend chosen by configuration, not hardcoded.

**Why this matters for agentic coding:**
- **Isolation:** each task runs in its own worktree, so parallel agents never collide in one working tree.
- **Resumability:** the same worktree is reused across runs, so iterative refinement builds forward instead of starting over.
- **Swappability:** a plugin interface lets you start with a local CLI subprocess and later move to a cloud SDK runner with zero use-case changes.
- **Safety:** a gate keeps half-specified tasks from ever reaching an agent; a scheduler keeps concurrent runs from corrupting git state.

---

## The Reference Architecture

Four collaborators, each with one responsibility:

```
        ┌─────────────────────────────────────────────────────────┐
        │                     Kanban Board                          │
        │   backlog ──► ready ──► executing ──► review ──► done      │
        │                  │                                         │
        │          EXECUTE GATE: non-empty spec                      │
        │          + all open questions answered                     │
        │          + stage == "ready"                                │
        └──────────────────────────┬──────────────────────────────┘
                                    │ press Execute (per task)
                                    ▼
                          ┌───────────────────┐
                          │   RunScheduler     │  cross-task parallelism
                          │  (BoundedSemaphore │  + per-task FIFO Lock
                          │   + per-task Lock) │
                          └─────────┬─────────┘
                  resolve_or_create │  start(run, on_event, cwd)
              pre_run_snapshot      ▼
        ┌──────────────────┐   ┌──────────────────────────────────┐
        │ WorktreeManager  │──►│        ICodeAgentRunner            │
        │ git worktree per │   │  (plugin: local_cli | agent_sdk |  │
        │ task, snapshot,  │   │   future cloud)                    │
        │ remove           │   │  start / cancel / status           │
        └──────────────────┘   └──────────────────────────────────┘
                                    │ streamed events
                                    ▼
                          on_event({"type": "stdout"|"status"|"exit"|...})
```

The **board** decides *whether* a task may run. The **WorktreeManager** decides *where* it runs. The **RunScheduler** decides *when* and *how many at once*. The **runner** decides *how* the agent is actually driven. Keeping these separate is what makes the system safe to extend.

---

## The ICodeAgentRunner Plugin Interface

The runner is the **seam** where execution backends plug in. Use cases and UI code depend only on this interface; they never know whether the agent is a local subprocess or a cloud API. Shape the contract to match the run/cancel/retrieve surface of whatever cloud backend you might adopt later, so adding that backend is a pure addition rather than an interface change.

```python
from typing import Callable, Protocol

class ICodeAgentRunner(Protocol):
    """Plug-in point for any backend that takes a prompt and runs an agent.

    Implementations MUST honor the tool allowlist carried on the run record.
    """

    def start(
        self,
        run: CodeExecutionRun,            # carries prompt, allowed_tools, ids
        on_event: Callable[[dict], None], # invoked per streamed event
        cwd: str | None = None,           # the task's worktree path
    ) -> None:
        """Kick off the run. `on_event` is called for each streamed event:
        {"type": "status", ...}, {"type": "stdout", ...},
        {"type": "exit", "status": ..., "exit_code": ...}. May run
        synchronously or on a background thread."""

    def cancel(self, run_id: str) -> bool:
        """Best-effort cancel. True if a cancel signal was delivered."""

    def status(self, run_id: str) -> str:
        """Runner's current view of a run: queued | running | succeeded |
        failed | cancelled."""
```

### Pluggable backends

A small factory selects the implementation from configuration (one environment variable), so the rest of the system is backend-agnostic:

```python
def build_runner(data_dir: str) -> ICodeAgentRunner:
    backend = env("CODE_RUNNER", default="local_cli")
    if backend == "local_cli":
        # Shells out to the installed `claude` CLI in the worktree, feeds the
        # prompt over stdin, parses --output-format=stream-json line by line,
        # and re-emits each JSON object through on_event. Inherently
        # single-host (local subprocess + filesystem).
        return LocalClaudeCliRunner(cli_path=which("claude"), log_dir=...)
    if backend == "agent_sdk":
        # Drives the Anthropic SDK directly with a tool-use loop; tools
        # (Read/Write/Edit/Bash/Glob/Grep) are dispatched in-process against
        # the worktree. Use when you want first-class access to the tool loop
        # (richer UIs, halt-on-gate behavior).
        return AgentSdkRunner(client=..., model=env("AGENT_SDK_MODEL"))
    if backend == "cloud_sdk":
        raise NotImplementedError("planned cloud path — pure addition later")
    raise ValueError(f"unknown CODE_RUNNER: {backend!r}")
```

**Two reference backends:**

| Backend | How it drives the agent | When to use |
|---------|------------------------|-------------|
| `local_cli` | Subprocess: `claude --print --verbose --output-format stream-json --allowedTools …`; prompt over stdin; parse `stream-json` lines → `on_event`. | Default. Laptop-local, zero extra deps beyond the installed CLI. |
| `agent_sdk` | In-process SDK tool-use loop; you dispatch each tool against the worktree. | When you need to intercept the tool loop (live UIs, hard gates mid-run). |
| `cloud_sdk` | Future: remote managed-agent API. | When you outgrow single-host execution. The interface already fits. |

The key discipline: **the interface is the contract, the env var is the switch, and the use cases import neither concrete class.**

---

## The WorktreeManager

Each task gets its **own long-lived git worktree** the first time it executes. Successive runs against the same task reuse that worktree so iterative refinement builds forward. The manager has exactly three operations.

```python
class WorktreeManager:
    def __init__(self, repo_root: str, worktree_base: str, base_branch: str = "main"): ...

    def resolve_or_create(self, task_id: str, slug: str) -> tuple[str, str]:
        """Return (worktree_path, branch_name), creating both on first call.
        Path: <worktree_base>/<task_id> — OUTSIDE the main repo, so the
        parent checkout's `git status` never sees it.
        Branch: <prefix>/<slug>, disambiguated to <prefix>/<slug>-<task_id>
        when the bare slug already exists."""

    def pre_run_snapshot(self, worktree_path: str, prev_run_id: str) -> None:
        """Before a new run, auto-commit any uncommitted changes from the
        previous run (git add -A && git commit --allow-empty) so the next
        run starts from a clean tree and prior work is preserved in history."""

    def remove(self, task_id: str) -> None:
        """Forcibly remove the worktree and delete its branch. No-op if
        absent. Falls back to rmtree if `git worktree remove` fails."""
```

**Design points that make this safe:**
- **Worktrees live outside the main repo** (`<worktree_base>/<task_id>`). If they lived inside, the parent checkout's `git status` would be polluted by every agent's scratch work.
- **One worktree per task, reused across runs.** This is what gives resumable, forward-building iteration — the agent picks up where the last run left off.
- **Pre-run snapshot** auto-commits leftover changes before each new run. Nothing the agent did last time is lost, and every run begins from a committed baseline.
- **Branch-name disambiguation** prevents two tasks with the same title slug from colliding on a branch name.
- **Per-client / per-repo targeting (optional extension):** resolve which repo a task's worktree comes off of (e.g., a task tied to an external project gets its worktree off *that* repo, falling back to the host repo when unset).

---

## The RunScheduler

The scheduler enforces two interlocking concurrency guarantees. Get these wrong and concurrent agents will corrupt git's index; get them right and you can fan out safely.

```python
class RunScheduler:
    def __init__(self, runner: ICodeAgentRunner, max_concurrent: int = 3):
        self._semaphore = BoundedSemaphore(max_concurrent)   # cross-task cap
        self._task_locks: dict[str, Lock] = {}               # per-task FIFO
        self._executor = ThreadPool(max_workers=max_concurrent * 2)

    def submit(self, run, on_event) -> Future:
        return self._executor.submit(self._execute, run, on_event)

    def _execute(self, run, on_event) -> None:
        task_lock = self._task_locks.setdefault(run.task_id, Lock())
        with task_lock:                 # (1) per-task serialization, FIFO
            self._semaphore.acquire()   # (2) global capacity cap
            try:
                self._runner.start(run, on_event, cwd=getattr(on_event, "cwd", None))
            finally:
                self._semaphore.release()
```

**Guarantee 1 — Cross-task parallelism (BoundedSemaphore):** up to `max_concurrent` runs execute simultaneously *across different tasks*. The semaphore caps total concurrency even under burst submission, so the host isn't overwhelmed.

**Guarantee 2 — Per-task serialization (per-task Lock):** a second run submitted for the *same* task waits behind any in-flight run for that task. This is essential — two concurrent runs in the *same worktree* would race on git's index and corrupt it. The per-task lock makes same-task runs strictly FIFO.

Note the **lock-then-semaphore order**: acquire the per-task lock first (queue behind same-task work), *then* acquire a global slot. This ensures a queued same-task run doesn't hold a scarce semaphore slot while it waits.

The scheduler **does not mutate run records** — it only invokes the runner and surfaces a `Future`. Mapping streamed events back to persistence is the use case's job. This keeps the scheduler a pure concurrency primitive.

---

## Kanban Stages and the Execution Gate

Tasks move through a small, ordered set of stages:

```
backlog ──► ready ──► executing ──► review ──► done
```

- **backlog** — captured, not yet specified.
- **ready** — spec is complete and validated; eligible to execute.
- **executing** — an agent run is in flight.
- **review** — run finished; awaiting human review / PR prep.
- **done** — merged / closed.

### The execution gate (the most important rule)

> **Execute is refused unless the task has a non-empty refined spec, every open question is answered, and the stage is `ready`.**

This gate is what makes autonomy *safe*: it prevents an agent from ever being fired against an ambiguous target. The spec is drafted and refined (often via a per-task refinement chat) *before* any code is written, so the agent ships against a validated outcome rather than guessing.

```python
def validate_for_execute(spec: CodeTaskSpec) -> None:
    if not spec.spec_markdown.strip():
        raise ValidationError("spec is empty — refine before executing")
    unanswered = [q for q in spec.open_questions if not q.get("answered")]
    if unanswered:
        raise ValidationError(f"{len(unanswered)} open question(s) unanswered")
    if spec.kanban_stage != "ready":
        raise ValidationError(f"stage must be 'ready' (currently {spec.kanban_stage!r})")
```

Optional **hard gates** layer on top of this base check for higher-risk tasks (e.g., require TDD, require design approval, block destructive operations, enforce a cost cap). The base gate above is the non-negotiable minimum; hard gates are per-task opt-ins the operator confirms.

---

## Sandboxing the Run

A `local_cli` runner spawns an agent on the host, so constrain it. Three guardrails matter most:

1. **Timeout with graceful kill.** Enforce a wall-clock limit (`CODE_RUN_TIMEOUT_SECONDS`). At the deadline send `SIGTERM`, then `SIGKILL` after a short grace window. A watcher thread that cancels itself when the run finishes normally keeps this cheap.
2. **Environment allowlist.** The subprocess receives **only** a curated set of env vars (`ANTHROPIC_API_KEY`, `HOME`, `PATH`, locale, scratch dirs). Everything else — your app secrets, cloud credentials, third-party API keys — is **scrubbed**, so a compromised or confused agent run cannot exfiltrate them.
3. **Network audit log.** When the stream contains a `WebSearch`/`WebFetch` tool-use event, record the URL/query to the run log and re-emit a synthetic audit event. After the run, the operator can see exactly which external sites the agent contacted.

These guardrails are properties of the *runner*, not the scheduler or board, which keeps the security surface in one place.

---

## Configuration Surface

The entire system is steered by a handful of environment variables — no code changes to switch backends, caps, or limits:

| Variable | Default | Controls |
|----------|---------|----------|
| `CODE_RUNNER` | `local_cli` | Which `ICodeAgentRunner` backend (`local_cli` / `agent_sdk` / future cloud). |
| `CLAUDE_CLI_PATH` | `which("claude")` | Path to the `claude` binary for the local-CLI backend. |
| `AGENT_SDK_MODEL` | a current model id | Model used by the SDK backend. |
| `WORKTREE_BASE` | sibling dir of the repo | Where per-task worktrees are created (outside the main repo). |
| `CODE_KANBAN_BASE_BRANCH` | `main` | Branch new worktrees are cut from. |
| `MAX_CONCURRENT_RUNS` | `3` | Scheduler's cross-task semaphore cap. |
| `CODE_RUN_TIMEOUT_SECONDS` | `3600` | Per-run wall-clock limit before SIGTERM→SIGKILL. |

(Prefix the names with your project's namespace, e.g. `MANGO_*`, to avoid collisions.) The principle: **everything operationally variable is an env var; nothing operationally variable is hardcoded.**

---

## Putting It Together

The end-to-end flow when an operator presses **Execute** on a `ready` card:

1. **Gate** — `validate_for_execute(spec)` runs. Empty spec, unanswered questions, or wrong stage → refuse with a clear message.
2. **Resolve worktree** — `WorktreeManager.resolve_or_create(task_id, slug)` returns `(path, branch)`, creating the isolated checkout on first run.
3. **Snapshot** — `pre_run_snapshot(path, prev_run_id)` commits any leftover changes from the previous run.
4. **Schedule** — the use case builds a `CodeExecutionRun` (prompt + tool allowlist + ids) and calls `scheduler.submit(run, on_event)`. The scheduler acquires the per-task lock, then a semaphore slot.
5. **Run** — the configured `ICodeAgentRunner.start(run, on_event, cwd=path)` drives the agent in the worktree, streaming events.
6. **Observe + persist** — `on_event` callbacks stream to the UI (e.g. via SSE) and the use case maps events to the run record; per-run artifacts land under `<worktree>/.feature-factory/...` (see [FEATURE_FACTORY_LAYOUT.md](FEATURE_FACTORY_LAYOUT.md)).
7. **Advance** — on success the card moves to `review`; a PR-prep pass can follow.

This is how a refined kanban card becomes a running, isolated, auditable coding agent — built entirely on git worktrees and the Claude CLI/SDK, with the backend chosen by configuration.

---

## Anti-Patterns

### ❌ Don't
- Run agents in the main working tree (parallel runs collide; `git status` is polluted).
- Hardcode the execution backend (you lose the ability to move to a cloud runner without rewrites).
- Allow same-task runs to execute concurrently (they race on git's index in the shared worktree).
- Fire an agent against an empty or half-answered spec (the gate exists precisely to stop this).
- Pass the full parent environment to a local subprocess (secrets leak to the agent).
- Let the scheduler mutate run records (mixes concurrency control with persistence; keep it pure).

### ✅ Do
- Give every task its own worktree, reused across runs, outside the main repo.
- Depend only on the `ICodeAgentRunner` interface; select the concrete backend via one env var.
- Use a BoundedSemaphore for cross-task parallelism and a per-task Lock for same-task FIFO.
- Enforce the spec/questions/stage gate as the non-negotiable execute precondition.
- Scrub the subprocess environment to an allowlist and audit network tool use.
- Make caps, timeouts, paths, and backend all environment-configurable.

---

## Related Documentation

- **[FEATURE_FACTORY_LAYOUT.md](FEATURE_FACTORY_LAYOUT.md)** — the `.feature-factory/` artifact contract that per-run outputs and feature ADRs follow.
- **[optimization/PARALLEL_EXECUTION_PATTERNS.md](optimization/PARALLEL_EXECUTION_PATTERNS.md)** — when to fan out work; complements the scheduler's concurrency model.
- **09-production-readiness/SECURITY_HARDENING.md** — env-scrubbing and sandboxing principles for host-spawned processes.
- **skills/feature-factory/** — the orchestrator skills that produce the per-feature artifacts an executed task consumes and emits.

---

**Status:** Pattern documentation — autonomous code execution on git worktrees + Claude CLI/SDK
**Last Updated:** 2026-05-25
**Maintainer:** Development Best Practices Repository
