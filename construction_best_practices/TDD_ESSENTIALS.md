# TDD Essentials (applied to LangGraph)

Here's a tight, practical TDD playbook tailored to a Python + LangGraph/LangSmith chatbot pipeline (like your invoicing/receipts project), plus copy-paste updates for your workflow and Copilot instructions.

## TDD Essentials (applied to LangGraph)

- **Start from behavior**: write a failing test that captures the user story ("Given emails with invoices, when the graph runs, then rows are appended to Google Sheets with normalized fields").
- **Make the test pass** with the minimal change.
- **Refactor** with tests green.
- **Keep tests fast and local** by default; quarantine networked tests behind markers.
- **Treat traces & datasets in LangSmith** as test oracles (assertions over tool calls, node outputs, and graph state).

## Test Types & Where They Fit

### 1. Unit tests (fast, lots)

Pure functions (parsers, normalizers, routing conditions, prompt builders).

- No I/O; use fakes for tool clients.

### 2. Node tests (component)

A single LangGraph node with its input schema and expected output/event.

- Validate retries, error handling, tool-calling shape.

### 3. Graph tests (integration)

Subgraphs or the full graph with faked external services.

- Assert on message flow, state transitions, and control edges.

### 4. Contract tests (adapters)

Gmail, Google Sheets, DB adapters using local fakes + a small number of live tests in CI nightly.

- Ensure our adapter conforms to the provider's API shape.

### 5. E2E scenario tests (few, slow)

Realistic datasets (LangSmith) that run the whole pipeline.

- Gate major releases only.

### 6. Non-functional tests

Performance (timeouts), idempotency (retries), and resilience (poison inputs).

## Practical Structure

```
repo/
  src/
    ... your code ...
  tests/
    unit/
      test_parsers.py
      test_normalize_invoice.py
    nodes/
      test_gmail_node.py
      test_extract_invoice_node.py
    graph/
      test_subgraph_ingest_to_sheet.py
    contracts/
      test_gmail_adapter_contract.py
      test_sheets_adapter_contract.py
    e2e/
      test_full_receipts_path.py
  tests/_fixtures/
    gmail_samples/
    html_receipts/
  conftest.py
  pyproject.toml (pytest config)
```

## Pytest Conventions

### Markers

- `@pytest.mark.unit`, `@pytest.mark.node`, `@pytest.mark.graph`, `@pytest.mark.contract`, `@pytest.mark.e2e`, `@pytest.mark.slow`, `@pytest.mark.live`

### Defaults

- Run unit + node on every change
- Graph on commit
- Contract (live) & e2e on CI nightly

### Options

- **Fail fast locally**: `-x -q`
- **Coverage threshold** (raise slowly): `--cov=src --cov-fail-under=80`

## LangGraph/LangSmith Specifics

### Node Contracts

For every node, define input/output schemas (pydantic). Unit/Node tests assert the schema and sentinel error cases.

### Tracing Assertions

Use LangSmith traces in graph/e2e tests to assert:

- tool call count & order
- redact status for sensitive fields
- latency budgets per node
- absence of unintended tools

### Datasets as Specs

Store canonical input/output pairs in a LangSmith dataset; e2e tests replay and compare with a tolerance (e.g., whitespace-insensitive, numeric deltas).

### State Invariants

Add helpers like `assert_state_keys(state, expected={"invoice_id","vendor","total"...})` after nodes.

## Fakes, Fixtures, and Determinism

- **Build fake clients**: FakeGmailClient, FakeSheetsClient, FakeStorage.
- **Use deterministic seeds** for any LLM sampling in tests (or stub model calls).
- **Record-replay** for occasional live adapter tests (e.g., vcr.py) but prefer handcrafted fixtures for privacy.
- **Property-based tests** (Hypothesis) for parsers & schema normalization.

## Definition of Done (DoD) for Features/Refactors

- ✅ Failing test written that captures acceptance criteria.
- ✅ Unit & node tests added/updated for new behavior & edge cases.
- ✅ Graph test (or updated dataset) covering the happy path.
- ✅ Live contract test added if a new external API is touched.
- ✅ Coverage unchanged or higher; no new xfail.
- ✅ Docs updated: node I/O schema and error policy.

## SOP: TDD Workflow for New Feature (and Updates)

### 1) Scope as Behavior

- Write a user story + Given/When/Then in the PR description.
- Extract acceptance criteria into 3–5 example cases.

### 2) Write Tests First

- Unit tests for pure logic involved.
- Node test showing the node's contract (input → output/error).
- If behavior crosses nodes, one graph test with fakes.

### 3) Make It Pass (Minimal)

- Implement just enough; keep log/traces on.
- Run `pytest -m "unit or node" -x`.

### 4) Refactor

- Improve naming, extract functions, consolidate prompts.
- Run full fast suite: `pytest -m "unit or node or graph and not slow"`.
- Ensure schema docs & type hints reflect reality.

### 5) Prove Integrations

- If adapter/API touched: run contract tests (fake + optional live).
- Update LangSmith dataset if outputs changed intentionally.

### 6) Commit & CI

- **Pre-commit**: style + unit/node/graph.
- **PR gates**: coverage ≥ threshold, no slow/live markers.
- **Nightly CI**: run contract(live) and e2e.

## Copilot Instruction Block

_Paste into your repo's "Copilot Instructions"_

```markdown
# Copilot — TDD-first Instructions (Python + LangGraph/LangSmith)

You are assisting on a Python LangGraph project with LangSmith tracing. ALWAYS follow TDD:

1. When I describe a feature or bug, FIRST generate tests:

   - Unit test for pure logic (pytest).
   - Node test for the affected LangGraph node with explicit input/output schema.
   - Graph test if behavior spans nodes, using fakes for external services.
   - Use markers: unit, node, graph, contract, e2e. Default to unit/node.

2. Test quality:

   - Create failing tests with clear Given/When/Then names.
   - Parameterize edge cases (empty, malformed, duplicate, oversized).
   - For parsers/normalizers, add property-based tests with Hypothesis.
   - For adapters, generate contract tests with local fakes; DO NOT call real services unless I say @live.

3. Stubs & Fakes:

   - Prefer simple fakes (FakeGmailClient, FakeSheetsClient, FakeDB).
   - Never import the real client in unit/node tests.
   - Provide minimal deterministic fixtures for inputs (sample emails, html receipts, json).

4. LangSmith:

   - Add assertions on traces in graph/e2e tests (tool call counts, ordering, no unintended tools).
   - Use datasets for canonical I/O; tests should fail if outputs materially change.

5. Naming & Layout:

   - Place tests under tests/{unit|nodes|graph|contracts|e2e}.
   - Use descriptive test names: test*{feature}*{case}.
   - Keep tests small and independent.

6. When implementing code to pass tests:

   - Make the smallest change.
   - Maintain pydantic schemas for node I/O; raise typed errors.
   - Keep prompts/config in code or fixtures so tests can assert on them.

7. After green:

   - Offer refactors guarded by existing tests.
   - Propose additional negative tests discovered during refactor.

8. Commands to run:
   - Fast loop: `pytest -m "unit or node" -q`
   - Broader: `pytest -m "unit or node or graph and not slow" -q`
   - Coverage: `pytest --cov=src --cov-report=term-missing`

Follow these unless I explicitly override.
```

## Ready-to-Use Pytest Setup Snippets

### pyproject.toml (pytest & coverage)

```toml
[tool.pytest.ini_options]
addopts = "-ra -q --strict-markers --cov=src --cov-report=term-missing"
testpaths = ["tests"]
markers = [
  "unit: fast, pure logic",
  "node: single LangGraph node",
  "graph: multiple nodes or subgraph",
  "contract: adapter interface tests",
  "e2e: end-to-end scenario tests",
  "slow: long-running",
  "live: calls external services"
]

[tool.coverage.report]
fail_under = 80
show_missing = true
```

### tests/conftest.py (examples)

```python
import os
import pytest

@pytest.fixture(autouse=True)
def deterministic_env(monkeypatch):
    monkeypatch.setenv("PYTHONHASHSEED", "0")
    monkeypatch.setenv("LLM_SEED", "42")  # if you gate sampling
    yield

@pytest.fixture
def fake_gmail():
    class FakeGmailClient:
        def search(self, query): return ["sample1.eml", "sample2.eml"]
        def read(self, msg_id): return open(f"tests/_fixtures/gmail_samples/{msg_id}", "rb").read()
    return FakeGmailClient()

@pytest.fixture
def fake_sheets():
    class FakeSheets:
        def append_rows(self, rows): self.rows = getattr(self, "rows", []) + rows
    return FakeSheets()
```

### Node test (pattern)

```python
import pytest

@pytest.mark.node
def test_extract_invoice_node_handles_missing_total(fake_gmail):
    # Given: an email without a total
    state = {"message_id": "missing_total.eml"}
    # When: node runs
    out = extract_invoice_node(state, gmail=fake_gmail)
    # Then: error policy applied
    assert out["status"] == "error"
    assert out["error_code"] == "MISSING_TOTAL"
```

### Graph test (pattern)

```python
import pytest

@pytest.mark.graph
def test_ingest_to_sheet_happy_path(fake_gmail, fake_sheets):
    state = {"cursor": "t0"}
    result, trace = run_ingest_graph(state, gmail=fake_gmail, sheets=fake_sheets, tracing=True)
    assert result["inserted"] == 2
    # Trace-level assertions
    assert trace.tool_calls == ["gmail.search","gmail.read","extract_invoice","sheets.append"]
```

## CI/Gates (fits your CodePipeline idea)

### Pre-commit hook

Run ruff/black + `pytest -m "unit or node"`.

### PR required checks

- `pytest -m "unit or node or graph and not slow and not live"`
- Coverage ≥ threshold.
- No snapshot drift (if you add snapshot tests).

### Nightly pipeline

- Run `pytest -m "contract or e2e or slow"`.
- Publish LangSmith report link & test flake stats.

## What to TDD First on Your Project (suggested)

- **Invoice parsing/normalization** (unit + property-based).
- **Gmail node error policy** (node).
- **Receipts → Sheets subgraph happy path** (graph).
- **Google Sheets adapter** (contract fake + 1 guarded live).
- **Idempotency**: running the graph twice doesn't duplicate rows (graph).
