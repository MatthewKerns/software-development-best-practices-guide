# Testing & Quality Assurance Guide — LangGraph/LangSmith Project

## 🧪 Comprehensive Testing Strategies & Quality Gates

**This guide provides detailed testing patterns, quality assurance processes, and CI/CD integration for our Python LangGraph project with LangSmith tracing.**

## 🆕 NEW: Comprehensive Testing Strategy Guidelines

**📖 Read [`TESTING_STRATEGY_GUIDELINES.md`](TESTING_STRATEGY_GUIDELINES.md)** for our updated comprehensive testing strategy that includes:

- **Clear definitions** of Unit, Integration, and Contract testing
- **LangGraph-specific testing patterns** for checkpoint resume functionality
- **Concrete examples** for each testing type with real code
- **Decision tree** for choosing the right test type
- **Quality gates** and automated enforcement

**This replaces the previous ad-hoc testing approach with a systematic strategy.**

---

## 1. Testing Architecture & Organization

### Repository Test Structure

```
tests/
├── unit/                    # Pure logic, no I/O (fast, <1ms per test)
│   ├── services/
│   │   ├── extraction/
│   │   │   ├── test_text_extraction.py
│   │   │   ├── test_field_parsing.py
│   │   │   └── test_validation.py
│   │   └── analysis/
│   ├── integrations/
│   │   ├── gmail/
│   │   └── sheets/
│   └── models/
├── nodes/                   # Single LangGraph nodes (medium, 100ms-1s per test)
│   ├── extraction/
│   │   ├── test_pdf_extraction_node.py
│   │   └── test_text_cleanup_node.py
│   ├── validation/
│   └── output/
├── graph/                   # Multi-node workflows (slow, 1s-10s per test)
│   ├── invoice_processing/
│   │   ├── test_happy_path.py
│   │   ├── test_error_handling.py
│   │   └── test_edge_cases.py
│   └── receipt_processing/
├── contracts/               # API adapter interface tests (medium, deterministic)
│   ├── gmail/
│   │   ├── test_gmail_client_contract.py
│   │   └── test_gmail_error_handling.py
│   └── sheets/
├── e2e/                     # End-to-end scenarios (very slow, 10s+ per test)
│   ├── test_complete_workflow.py
│   └── test_production_scenarios.py
└── _fixtures/               # Test data and utilities
    ├── pdfs/
    │   ├── sample_invoice.pdf
    │   ├── corrupted.pdf
    │   └── multilingual.pdf
    ├── emails/
    │   └── sample_email_data.json
    ├── expected_outputs/
    │   └── golden_master_results.json
    └── factories/
        ├── pdf_factory.py
        ├── email_factory.py
        └── state_factory.py
```

### Test Categories & Execution Speed

| Category | Speed Target | Purpose                        | Example                           |
| -------- | ------------ | ------------------------------ | --------------------------------- |
| Unit     | <1ms         | Pure logic validation          | `test_normalize_currency()`       |
| Node     | 100ms-1s     | Single LangGraph node behavior | `test_pdf_extraction_node()`      |
| Graph    | 1s-10s       | Multi-node workflow validation | `test_invoice_processing_graph()` |
| Contract | 100ms-1s     | API interface compliance       | `test_gmail_client_contract()`    |
| E2E      | 10s+         | Complete user scenarios        | `test_email_to_sheets_workflow()` |

---

## 2. pytest Markers & Test Classification

### Marker Definitions

```python
# pytest.ini configuration
[tool.pytest.ini_options]
markers = [
    "unit: Fast, pure logic tests with no I/O dependencies",
    "node: Single LangGraph node tests with mocked dependencies",
    "graph: Multi-node workflow tests using fake clients",
    "contract: API adapter interface compliance tests",
    "e2e: End-to-end scenario tests with real or realistic data",
    "slow: Tests taking >1 second to execute",
    "live: Tests that call external services (Gmail, OpenAI, etc.)",
    "integration: Tests involving multiple system components",
    "smoke: Basic functionality tests for CI/CD health checks",
    "regression: Tests for previously fixed bugs",
    "performance: Tests with timing and resource usage assertions"
]
```

### Marker Usage Examples

```python
@pytest.mark.unit
def test_currency_normalization():
    """Test pure function with no dependencies."""
    result = normalize_currency("$1,234.56")
    assert result == 1234.56

@pytest.mark.node
@pytest.mark.asyncio
async def test_pdf_extraction_node():
    """Test single LangGraph node with mocked dependencies."""
    with patch('src.services.extraction.extract_text') as mock_extract:
        mock_extract.return_value = "Sample invoice text"

        state = WorkflowState(pdf_data=b"fake pdf")
        result = await pdf_extraction_node(state)

        assert result.extracted_text == "Sample invoice text"

@pytest.mark.graph
@pytest.mark.slow
async def test_invoice_processing_workflow():
    """Test complete multi-node workflow."""
    # Uses fake clients, may take several seconds
    pass

@pytest.mark.contract
def test_gmail_client_interface():
    """Test that Gmail client implements expected interface."""
    client = GmailClient()
    assert hasattr(client, 'search_messages')
    assert callable(getattr(client, 'search_messages'))

@pytest.mark.e2e
@pytest.mark.live
@pytest.mark.slow
async def test_production_workflow():
    """Test complete workflow with real external services."""
    # Only run in specific CI environments
    pass
```

---

## 3. Mock Strategy & Test Doubles

### Hierarchy of Test Doubles

1. **Simple Fakes** (Preferred) - In-memory implementations
2. **Stubs** - Return predefined responses
3. **Spies** - Track method calls and arguments
4. **Mocks** - Verify interactions and behavior
5. **Real Objects** - Only when necessary (marked @live)

### Fake Client Implementation Patterns

```python
class FakeGmailClient:
    """Simple fake Gmail client for testing."""

    def __init__(self):
        self.messages = {
            "msg1": {
                "id": "msg1",
                "subject": "Invoice from Vendor Corp",
                "attachments": [{"name": "invoice.pdf", "data": b"fake pdf content"}]
            },
            "msg2": {
                "id": "msg2",
                "subject": "Receipt from Store",
                "attachments": []
            }
        }
        self.search_calls = []
        self.get_calls = []

    def search_messages(self, query: str) -> list[str]:
        """Return deterministic search results."""
        self.search_calls.append(query)

        if "has:attachment" in query:
            return ["msg1"]  # Only message with attachment
        return list(self.messages.keys())

    def get_message(self, msg_id: str) -> dict:
        """Return message data or raise for unknown IDs."""
        self.get_calls.append(msg_id)

        if msg_id not in self.messages:
            raise MessageNotFoundError(f"Message {msg_id} not found")

        return self.messages[msg_id]

    def download_attachment(self, attachment_id: str) -> bytes:
        """Return fake PDF content."""
        return b"fake pdf content for testing"

class FakeSheetsClient:
    """Simple fake Google Sheets client."""

    def __init__(self):
        self.rows = []
        self.append_calls = []

    def append_row(self, spreadsheet_id: str, range_name: str, values: list):
        """Store appended data for verification."""
        self.append_calls.append({
            "spreadsheet_id": spreadsheet_id,
            "range": range_name,
            "values": values
        })
        self.rows.append(values)

    def get_last_row(self) -> list:
        """Helper for test assertions."""
        return self.rows[-1] if self.rows else []

class FakeLLMClient:
    """Deterministic LLM client for testing."""

    def __init__(self):
        self.responses = {}
        self.call_history = []

    def set_response(self, prompt_pattern: str, response: str):
        """Configure response for specific prompt patterns."""
        self.responses[prompt_pattern] = response

    async def ainvoke(self, prompt: str) -> str:
        """Return pre-configured response based on prompt."""
        self.call_history.append(prompt)

        # Find matching response pattern
        for pattern, response in self.responses.items():
            if pattern in prompt:
                return response

        # Default response for unmatched prompts
        return "Default LLM response for testing"
```

### Dependency Injection for Testing

```python
# Production code with dependency injection
class InvoiceProcessor:
    def __init__(self,
                 gmail_client: GmailClient,
                 sheets_client: SheetsClient,
                 llm_client: ChatOpenAI):
        self.gmail = gmail_client
        self.sheets = sheets_client
        self.llm = llm_client

    async def process_invoices(self) -> ProcessingResult:
        messages = self.gmail.search_messages("has:attachment")
        # ... processing logic
        return result

# Test with fake dependencies
@pytest.mark.integration
async def test_invoice_processor_with_fakes():
    """Test processor with fake dependencies."""
    fake_gmail = FakeGmailClient()
    fake_sheets = FakeSheetsClient()
    fake_llm = FakeLLMClient()

    # Configure fake responses
    fake_llm.set_response("extract invoice", '{"vendor": "Test Corp", "amount": 123.45}')

    processor = InvoiceProcessor(fake_gmail, fake_sheets, fake_llm)
    result = await processor.process_invoices()

    # Verify behavior
    assert result.processed_count == 1
    assert len(fake_sheets.rows) == 1
    assert fake_sheets.rows[0][0] == "Test Corp"  # Vendor name
```

---

## 4. Test Data Management & Fixtures

### Deterministic Test Data

```python
@pytest.fixture
def sample_invoice_pdf() -> bytes:
    """Deterministic PDF content for testing."""
    return (Path(__file__).parent / "_fixtures" / "pdfs" / "sample_invoice.pdf").read_bytes()

@pytest.fixture
def sample_email_data() -> dict:
    """Deterministic email structure."""
    return {
        "id": "test_email_123",
        "threadId": "thread_456",
        "subject": "Invoice #INV-2025-001 from Acme Corp",
        "from": "billing@acmecorp.com",
        "date": "2025-08-11T10:30:00Z",
        "attachments": [
            {
                "filename": "invoice.pdf",
                "mimeType": "application/pdf",
                "size": 250000,
                "attachmentId": "att_789"
            }
        ]
    }

@pytest.fixture
def expected_invoice_data() -> dict:
    """Expected extraction result for sample invoice."""
    return {
        "vendor": "Acme Corporation",
        "invoice_number": "INV-2025-001",
        "amount": 1234.56,
        "date": "2025-08-01",
        "currency": "USD",
        "confidence": 0.95,
        "extraction_method": "llm_enhanced"
    }

# Parametrized fixtures for edge cases
@pytest.fixture(params=[
    ("empty.pdf", b""),
    ("corrupted.pdf", b"corrupted content"),
    ("large.pdf", b"x" * 30_000_000),  # 30MB file
    ("password_protected.pdf", b"encrypted content")
])
def edge_case_pdf(request) -> tuple[str, bytes]:
    """Parametrized fixture for PDF edge cases."""
    filename, content = request.param
    return filename, content
```

### Factory Pattern for Test Data

```python
class InvoiceDataFactory:
    """Factory for creating test invoice data."""

    @staticmethod
    def create_standard_invoice(**overrides) -> dict:
        """Create standard invoice data with optional overrides."""
        base_data = {
            "vendor": "Standard Vendor Inc",
            "invoice_number": "INV-2025-001",
            "amount": 1000.00,
            "date": "2025-08-01",
            "currency": "USD",
            "line_items": [
                {"description": "Service Fee", "amount": 800.00},
                {"description": "Tax", "amount": 200.00}
            ],
            "confidence": 0.85
        }
        base_data.update(overrides)
        return base_data

    @staticmethod
    def create_suspicious_invoice(**overrides) -> dict:
        """Create invoice with suspicious characteristics."""
        return InvoiceDataFactory.create_standard_invoice(
            amount=10000.00,  # High amount
            vendor="Unknown Vendor",  # Unfamiliar vendor
            confidence=0.65,  # Low confidence
            **overrides
        )

    @staticmethod
    def create_international_invoice(**overrides) -> dict:
        """Create invoice with international formatting."""
        return InvoiceDataFactory.create_standard_invoice(
            vendor="Société Européenne SARL",
            amount=1234.56,
            currency="EUR",
            date="01/08/2025",  # European date format
            **overrides
        )

class WorkflowStateFactory:
    """Factory for creating test workflow states."""

    @staticmethod
    def create_initial_state(**overrides) -> WorkflowState:
        """Create initial workflow state."""
        base_state = WorkflowState(
            user_id="test_user@example.com",
            cursor="initial",
            processed_count=0,
            errors=[],
            metadata={}
        )
        for key, value in overrides.items():
            setattr(base_state, key, value)
        return base_state

    @staticmethod
    def create_post_extraction_state(**overrides) -> WorkflowState:
        """Create state after PDF extraction."""
        return WorkflowStateFactory.create_initial_state(
            extracted_text="Sample invoice text...",
            pdf_metadata={"pages": 2, "size": 150000},
            confidence=0.8,
            **overrides
        )
```

---

## 5. LangSmith Integration Testing

### Trace Quality Assertions

```python
@pytest.mark.graph
async def test_invoice_processing_trace_quality():
    """Test that invoice processing generates high-quality traces."""

    with LangSmithTracer(project="test_invoice_processing") as tracer:
        state = WorkflowStateFactory.create_initial_state()
        result = await run_invoice_processing_graph(state)
        trace = tracer.get_current_trace()

    # Performance budgets
    assert trace.total_duration < 30.0, f"Processing took {trace.total_duration}s, expected <30s"
    assert trace.total_tokens < 15000, f"Used {trace.total_tokens} tokens, budget is 15000"

    # Security requirements
    assert trace.sensitive_fields_redacted, "Sensitive data must be redacted in traces"

    # Tool usage validation
    expected_tools = {"gmail.search", "gmail.get_message", "pdf.extract", "llm.invoke", "sheets.append"}
    actual_tools = set(trace.tool_calls.keys())
    unexpected_tools = actual_tools - expected_tools
    assert not unexpected_tools, f"Unexpected tools used: {unexpected_tools}"

    # Trace structure validation
    assert trace.has_proper_nesting(), "Trace spans should be properly nested"
    assert trace.all_spans_have_status(), "All spans should have completion status"

def assert_trace_performance(trace: LangSmithTrace, performance_budget: dict):
    """Assert trace meets performance requirements."""

    # Overall performance
    assert trace.total_duration <= performance_budget["max_duration"]
    assert trace.total_tokens <= performance_budget["max_tokens"]

    # Per-node performance budgets
    for node_name, budget in performance_budget.get("node_budgets", {}).items():
        node_span = trace.get_span_by_name(node_name)
        assert node_span.duration <= budget["max_duration"]

        if "max_tokens" in budget:
            assert node_span.token_count <= budget["max_tokens"]

@pytest.mark.graph
@pytest.mark.performance
async def test_node_performance_budgets():
    """Test individual node performance within budgets."""

    performance_budget = {
        "max_duration": 30.0,
        "max_tokens": 15000,
        "node_budgets": {
            "pdf_extraction_node": {"max_duration": 5.0},
            "llm_extraction_node": {"max_duration": 15.0, "max_tokens": 10000},
            "validation_node": {"max_duration": 2.0},
            "sheets_output_node": {"max_duration": 3.0}
        }
    }

    with LangSmithTracer() as tracer:
        await run_invoice_processing_graph(test_state)
        trace = tracer.get_current_trace()

    assert_trace_performance(trace, performance_budget)
```

### Dataset Integration for Regression Testing

```python
@pytest.mark.regression
@pytest.mark.slow
def test_extraction_against_golden_dataset():
    """Test extraction results against curated LangSmith dataset."""

    dataset = load_langsmith_dataset("invoice_extraction_golden_master")

    for example in dataset.examples:
        # Run extraction on example input
        result = extract_invoice_data(example.input_pdf)

        # Compare with expected output using business-appropriate tolerance
        assert_invoice_data_equivalent(result, example.expected_output)

def assert_invoice_data_equivalent(actual: dict, expected: dict, tolerance: dict = None):
    """Compare invoice data with configurable tolerance."""

    tolerance = tolerance or {
        "amount_tolerance": 0.01,
        "confidence_tolerance": 0.05,
        "date_tolerance_days": 0
    }

    # Exact matches for critical fields
    assert actual["vendor"] == expected["vendor"], "Vendor must match exactly"
    assert actual["invoice_number"] == expected["invoice_number"], "Invoice number must match exactly"

    # Tolerance for numeric fields
    amount_diff = abs(actual["amount"] - expected["amount"])
    assert amount_diff <= tolerance["amount_tolerance"], f"Amount difference {amount_diff} exceeds tolerance"

    confidence_diff = abs(actual["confidence"] - expected["confidence"])
    assert confidence_diff <= tolerance["confidence_tolerance"], f"Confidence difference {confidence_diff} exceeds tolerance"

    # Date comparison with tolerance
    actual_date = datetime.strptime(actual["date"], "%Y-%m-%d")
    expected_date = datetime.strptime(expected["date"], "%Y-%m-%d")
    date_diff = abs((actual_date - expected_date).days)
    assert date_diff <= tolerance["date_tolerance_days"], f"Date difference {date_diff} days exceeds tolerance"

@pytest.mark.integration
def test_langsmith_dataset_updates():
    """Test that dataset updates are properly tracked."""

    # When extraction logic changes, datasets should be updated
    # This test ensures we don't accidentally break existing behavior

    dataset_version = get_dataset_version("invoice_extraction_golden_master")
    code_version = get_extraction_code_version()

    # If code has changed significantly, dataset should be updated
    if code_version > dataset_version:
        pytest.skip("Dataset needs update for new extraction logic")

    # Run regression tests against current dataset
    test_extraction_against_golden_dataset()
```

---

## 6. Property-Based Testing with Hypothesis

### Testing Invariants Across Input Variations

```python
from hypothesis import given, strategies as st, assume
from hypothesis.stateful import RuleBasedStateMachine, rule, invariant

@given(
    pdf_size=st.integers(min_value=1000, max_value=5_000_000),
    corruption_level=st.floats(min_value=0.0, max_value=0.3),
    content_type=st.sampled_from(["invoice", "receipt", "statement", "contract"])
)
def test_extraction_robustness_invariants(pdf_size, corruption_level, content_type):
    """Test that extraction maintains invariants regardless of input characteristics."""

    # Generate test PDF with specified characteristics
    pdf_data = generate_test_pdf(
        size=pdf_size,
        corruption=corruption_level,
        content_type=content_type
    )

    try:
        result = extract_invoice_data(pdf_data)

        # Invariants that must always hold
        assert isinstance(result, dict), "Result must be a dictionary"
        assert "confidence" in result, "Result must include confidence score"
        assert 0.0 <= result["confidence"] <= 1.0, "Confidence must be between 0 and 1"

        # Business invariants
        if "amount" in result:
            assert isinstance(result["amount"], (int, float)), "Amount must be numeric"
            assert result["amount"] >= 0, "Amount cannot be negative"
            assert result["amount"] < 1_000_000, "Amount should be within reasonable range"

        if "date" in result:
            # Date should be parseable and reasonable
            parsed_date = datetime.strptime(result["date"], "%Y-%m-%d")
            assert parsed_date.year >= 2000, "Date should be reasonable"
            assert parsed_date <= datetime.now() + timedelta(days=30), "Date should not be far future"

    except (ValueError, PDFError, ExtractionError) as e:
        # Acceptable to fail on invalid inputs
        assert any(keyword in str(e).lower() for keyword in
                  ["invalid", "corrupt", "unsupported", "too large"]), \
               f"Exception should be descriptive: {e}"

@given(
    currency_string=st.text(min_size=1, max_size=20).filter(lambda x: any(c.isdigit() for c in x))
)
def test_currency_normalization_properties(currency_string):
    """Test currency normalization handles various string formats."""

    try:
        result = normalize_currency(currency_string)

        # Properties that should hold for valid results
        assert isinstance(result, (int, float)), "Result should be numeric"
        assert result >= 0, "Normalized currency should be non-negative"
        assert not math.isnan(result), "Result should not be NaN"
        assert not math.isinf(result), "Result should not be infinite"

    except ValueError:
        # Acceptable to reject invalid currency strings
        pass

class InvoiceProcessingStateMachine(RuleBasedStateMachine):
    """Stateful testing for invoice processing workflow."""

    def __init__(self):
        super().__init__()
        self.workflow_state = WorkflowStateFactory.create_initial_state()
        self.processed_invoices = []
        self.processing_errors = []

    @rule(pdf_data=st.binary(min_size=100, max_size=100000))
    def add_invoice(self, pdf_data):
        """Add an invoice to the processing queue."""
        try:
            result = process_invoice(pdf_data)
            self.processed_invoices.append(result)
        except Exception as e:
            self.processing_errors.append(e)

    @rule()
    def validate_state(self):
        """Validate current workflow state."""
        # State should always be consistent
        assert len(self.processed_invoices) >= 0
        assert all(isinstance(inv, dict) for inv in self.processed_invoices)

    @invariant()
    def processed_count_matches_list(self):
        """Invariant: processed count should match actual processed invoices."""
        assert len(self.processed_invoices) == self.workflow_state.processed_count

# Run stateful testing
TestInvoiceProcessing = InvoiceProcessingStateMachine.TestCase
```

---

## 7. Performance & Load Testing

### Performance Benchmarking

```python
import pytest
import time
from memory_profiler import profile

@pytest.mark.performance
@pytest.mark.slow
def test_extraction_performance_baseline():
    """Benchmark extraction performance for different PDF sizes."""

    test_cases = [
        ("small", 50_000),    # 50KB
        ("medium", 500_000),  # 500KB
        ("large", 2_000_000), # 2MB
        ("xlarge", 5_000_000) # 5MB
    ]

    performance_results = {}

    for size_category, size_bytes in test_cases:
        pdf_data = generate_test_pdf(size=size_bytes)

        start_time = time.time()
        result = extract_invoice_data(pdf_data)
        end_time = time.time()

        processing_time = end_time - start_time
        performance_results[size_category] = {
            "processing_time": processing_time,
            "size_bytes": size_bytes,
            "confidence": result.get("confidence", 0.0)
        }

        # Performance assertions based on size
        if size_category == "small":
            assert processing_time < 2.0, f"Small PDF took {processing_time}s, expected <2s"
        elif size_category == "medium":
            assert processing_time < 5.0, f"Medium PDF took {processing_time}s, expected <5s"
        elif size_category == "large":
            assert processing_time < 10.0, f"Large PDF took {processing_time}s, expected <10s"
        elif size_category == "xlarge":
            assert processing_time < 15.0, f"XLarge PDF took {processing_time}s, expected <15s"

    # Log performance results for tracking
    logger.info(f"Performance baseline results: {performance_results}")

@profile
def test_memory_usage_profile():
    """Profile memory usage during invoice processing."""

    # This will generate memory usage report
    large_pdf = generate_test_pdf(size=5_000_000)
    result = extract_invoice_data(large_pdf)

    # Memory usage should be reasonable (implementation-specific)
    assert result is not None

@pytest.mark.performance
@pytest.mark.parametrize("concurrent_requests", [1, 5, 10, 20])
async def test_concurrent_processing_performance(concurrent_requests):
    """Test performance under concurrent load."""

    pdf_data = generate_test_pdf(size=500_000)  # 500KB standard size

    async def process_single_invoice():
        return await extract_invoice_data_async(pdf_data)

    start_time = time.time()

    # Process multiple invoices concurrently
    tasks = [process_single_invoice() for _ in range(concurrent_requests)]
    results = await asyncio.gather(*tasks)

    end_time = time.time()
    total_time = end_time - start_time

    # Performance assertions
    assert len(results) == concurrent_requests, "All requests should complete"
    assert all(r.get("confidence", 0) > 0 for r in results), "All extractions should succeed"

    # Throughput should scale reasonably with concurrency
    throughput = concurrent_requests / total_time
    logger.info(f"Throughput with {concurrent_requests} concurrent requests: {throughput:.2f} req/s")

    # Minimum acceptable throughput (adjust based on infrastructure)
    min_throughput = 0.5  # 0.5 requests per second minimum
    assert throughput >= min_throughput, f"Throughput {throughput:.2f} below minimum {min_throughput}"
```

### Load Testing Scenarios

```python
@pytest.mark.performance
@pytest.mark.slow
async def test_sustained_load_processing():
    """Test processing under sustained load over time."""

    duration_minutes = 5
    target_rate = 2  # 2 invoices per minute

    start_time = time.time()
    processed_count = 0
    error_count = 0

    while time.time() - start_time < duration_minutes * 60:
        try:
            pdf_data = generate_test_pdf(size=random.randint(100_000, 1_000_000))
            result = await extract_invoice_data_async(pdf_data)
            processed_count += 1

            # Simulate realistic processing interval
            await asyncio.sleep(60 / target_rate)

        except Exception as e:
            error_count += 1
            logger.error(f"Processing error during load test: {e}")

    total_time = time.time() - start_time
    actual_rate = processed_count / (total_time / 60)
    error_rate = error_count / (processed_count + error_count) if processed_count + error_count > 0 else 0

    # Load test assertions
    assert actual_rate >= target_rate * 0.8, f"Actual rate {actual_rate:.2f} below 80% of target {target_rate}"
    assert error_rate < 0.05, f"Error rate {error_rate:.2%} exceeds 5% threshold"

    logger.info(f"Load test completed: {processed_count} processed, {error_count} errors, rate: {actual_rate:.2f}/min")
```

---

## 8. CI/CD Integration & Quality Gates

### Pre-commit Hooks

```bash
#!/bin/bash
# .git/hooks/pre-commit

echo "Running pre-commit quality checks..."

# 1. Fast unit tests (fail fast)
echo "Running unit tests..."
pytest -m unit -x -q
if [ $? -ne 0 ]; then
    echo "❌ Unit tests failed"
    exit 1
fi

# 2. Code formatting
echo "Checking code formatting..."
black --check .
if [ $? -ne 0 ]; then
    echo "❌ Code formatting issues found. Run 'black .' to fix."
    exit 1
fi

# 3. Import sorting
echo "Checking import organization..."
isort --check-only .
if [ $? -ne 0 ]; then
    echo "❌ Import sorting issues found. Run 'isort .' to fix."
    exit 1
fi

# 4. Type checking
echo "Running type checking..."
mypy src/
if [ $? -ne 0 ]; then
    echo "❌ Type checking failed"
    exit 1
fi

echo "✅ Pre-commit checks passed"
```

### GitHub Actions Workflow

```yaml
# .github/workflows/test.yml
name: Test Suite

on:
  push:
    branches: [main, develop]
  pull_request:
    branches: [main]

jobs:
  unit-tests:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        python-version: [3.9, 3.10, 3.11]

    steps:
      - uses: actions/checkout@v3

      - name: Set up Python ${{ matrix.python-version }}
        uses: actions/setup-python@v3
        with:
          python-version: ${{ matrix.python-version }}

      - name: Install dependencies
        run: |
          pip install -r requirements.txt
          pip install -r requirements-test.txt

      - name: Run unit tests
        run: pytest -m "unit" --cov=src --cov-report=xml

      - name: Upload coverage to Codecov
        uses: codecov/codecov-action@v3

  integration-tests:
    runs-on: ubuntu-latest
    needs: unit-tests

    steps:
      - uses: actions/checkout@v3
      - name: Set up Python
        uses: actions/setup-python@v3
        with:
          python-version: 3.11

      - name: Install dependencies
        run: |
          pip install -r requirements.txt
          pip install -r requirements-test.txt

      - name: Run integration tests
        run: pytest -m "node or graph and not slow and not live" -v

      - name: Run contract tests
        run: pytest -m "contract" -v

  performance-tests:
    runs-on: ubuntu-latest
    needs: integration-tests
    if: github.event_name == 'push' && github.ref == 'refs/heads/main'

    steps:
      - uses: actions/checkout@v3
      - name: Set up Python
        uses: actions/setup-python@v3
        with:
          python-version: 3.11

      - name: Install dependencies
        run: |
          pip install -r requirements.txt
          pip install -r requirements-test.txt

      - name: Run performance tests
        run: pytest -m "performance" --benchmark-json=benchmark.json

      - name: Store benchmark results
        uses: benchmark-action/github-action-benchmark@v1
        with:
          tool: "pytest"
          output-file-path: benchmark.json

  live-tests:
    runs-on: ubuntu-latest
    needs: integration-tests
    if: github.event_name == 'push' && github.ref == 'refs/heads/main'
    environment: production

    steps:
      - uses: actions/checkout@v3
      - name: Set up Python
        uses: actions/setup-python@v3
        with:
          python-version: 3.11

      - name: Install dependencies
        run: |
          pip install -r requirements.txt
          pip install -r requirements-test.txt

      - name: Run live integration tests
        env:
          OPENAI_API_KEY: ${{ secrets.OPENAI_API_KEY }}
          GOOGLE_CREDENTIALS: ${{ secrets.GOOGLE_CREDENTIALS }}
        run: pytest -m "live" -v --maxfail=3
```

### Quality Gate Configuration

```python
# scripts/quality_gates.py
"""Quality gate enforcement for CI/CD pipeline."""

import subprocess
import sys
from typing import Dict, List, NamedTuple

class QualityMetric(NamedTuple):
    name: str
    current_value: float
    threshold: float
    operator: str  # 'gte', 'lte', 'eq'

def check_test_coverage() -> QualityMetric:
    """Check test coverage meets minimum threshold."""
    result = subprocess.run([
        "pytest", "--cov=src", "--cov-report=term-missing", "--cov-fail-under=80"
    ], capture_output=True, text=True)

    # Parse coverage percentage from output
    coverage_line = [line for line in result.stdout.split('\n') if 'TOTAL' in line]
    if coverage_line:
        coverage_str = coverage_line[0].split()[-1].rstrip('%')
        coverage = float(coverage_str)
    else:
        coverage = 0.0

    return QualityMetric("test_coverage", coverage, 80.0, "gte")

def check_test_performance() -> List[QualityMetric]:
    """Check test execution performance."""
    result = subprocess.run([
        "pytest", "-m", "unit", "--durations=0"
    ], capture_output=True, text=True)

    # Extract test execution times
    unit_test_time = extract_total_test_time(result.stdout)

    return [
        QualityMetric("unit_test_time", unit_test_time, 30.0, "lte"),  # Max 30 seconds
    ]

def check_code_quality() -> List[QualityMetric]:
    """Check code quality metrics."""
    # Run complexity analysis
    complexity_result = subprocess.run([
        "radon", "cc", "src/", "--average"
    ], capture_output=True, text=True)

    avg_complexity = extract_average_complexity(complexity_result.stdout)

    return [
        QualityMetric("avg_complexity", avg_complexity, 10.0, "lte"),
    ]

def enforce_quality_gates() -> bool:
    """Enforce all quality gates."""
    metrics = []

    # Collect all metrics
    metrics.append(check_test_coverage())
    metrics.extend(check_test_performance())
    metrics.extend(check_code_quality())

    failed_metrics = []

    for metric in metrics:
        if not evaluate_metric(metric):
            failed_metrics.append(metric)

    if failed_metrics:
        print("❌ Quality gates failed:")
        for metric in failed_metrics:
            print(f"  {metric.name}: {metric.current_value} {metric.operator} {metric.threshold}")
        return False
    else:
        print("✅ All quality gates passed")
        return True

def evaluate_metric(metric: QualityMetric) -> bool:
    """Evaluate if metric meets threshold."""
    if metric.operator == "gte":
        return metric.current_value >= metric.threshold
    elif metric.operator == "lte":
        return metric.current_value <= metric.threshold
    elif metric.operator == "eq":
        return metric.current_value == metric.threshold
    else:
        raise ValueError(f"Unknown operator: {metric.operator}")

if __name__ == "__main__":
    success = enforce_quality_gates()
    sys.exit(0 if success else 1)
```

---

## 9. Test Maintenance & Continuous Improvement

### Test Metrics Dashboard

```python
def generate_test_metrics_report() -> dict:
    """Generate comprehensive test metrics report."""

    metrics = {
        "coverage": {
            "line_coverage": get_line_coverage(),
            "branch_coverage": get_branch_coverage(),
            "uncovered_lines": get_uncovered_lines()
        },
        "performance": {
            "test_execution_time": measure_test_execution_time(),
            "slowest_tests": get_slowest_tests(limit=10),
            "flaky_tests": identify_flaky_tests()
        },
        "quality": {
            "test_count_by_category": count_tests_by_marker(),
            "assertion_density": calculate_assertion_density(),
            "test_to_code_ratio": calculate_test_to_code_ratio()
        },
        "maintenance": {
            "skipped_tests": count_skipped_tests(),
            "xfail_tests": count_xfail_tests(),
            "todo_tests": find_todo_tests()
        }
    }

    return metrics

def identify_test_debt() -> List[str]:
    """Identify areas of test debt that need attention."""

    debt_items = []

    # Check for low coverage areas
    coverage_report = get_coverage_by_module()
    for module, coverage in coverage_report.items():
        if coverage < 70:
            debt_items.append(f"Low coverage in {module}: {coverage}%")

    # Check for slow tests
    slow_tests = get_tests_slower_than(threshold=5.0)
    if slow_tests:
        debt_items.append(f"{len(slow_tests)} tests taking >5 seconds")

    # Check for skipped/xfail tests
    skipped_count = count_skipped_tests()
    if skipped_count > 5:
        debt_items.append(f"{skipped_count} skipped tests need attention")

    return debt_items

def prioritize_test_improvements() -> List[Dict]:
    """Prioritize test improvements based on impact and effort."""

    improvements = [
        {
            "area": "Add unit tests for utilities",
            "impact": "high",    # Prevents regressions
            "effort": "low",     # Simple functions to test
            "priority": 1
        },
        {
            "area": "Optimize slow integration tests",
            "impact": "medium",  # Improves developer experience
            "effort": "medium",  # Requires analysis and optimization
            "priority": 2
        },
        {
            "area": "Add property-based tests for parsers",
            "impact": "high",    # Finds edge cases
            "effort": "high",    # Requires hypothesis knowledge
            "priority": 3
        }
    ]

    return sorted(improvements, key=lambda x: x["priority"])
```

### Automated Test Generation

```python
def generate_edge_case_tests(function_name: str, function_obj: callable) -> str:
    """Generate edge case tests for a given function."""

    # Analyze function signature
    sig = inspect.signature(function_obj)

    # Generate test cases based on parameter types
    test_cases = []

    for param_name, param in sig.parameters.items():
        if param.annotation == str:
            test_cases.extend([
                f'"{param_name}": ""',      # Empty string
                f'"{param_name}": None',    # None value
                f'"{param_name}": "x" * 1000',  # Very long string
            ])
        elif param.annotation in (int, float):
            test_cases.extend([
                f'"{param_name}": 0',       # Zero
                f'"{param_name}": -1',      # Negative
                f'"{param_name}": float("inf")',  # Infinity
            ])

    # Generate test template
    test_template = f"""
@pytest.mark.parametrize("invalid_input,expected_error", [
    {', '.join(f'({case}, ValueError)' for case in test_cases)}
])
def test_{function_name}_edge_cases(invalid_input, expected_error):
    '''Generated test for {function_name} edge cases.'''
    with pytest.raises(expected_error):
        {function_name}(**invalid_input)
"""

    return test_template
```

---

**Remember: Quality is not an accident - it's the result of intelligent effort. Build quality into your process, measure continuously, and improve relentlessly! 🧪📊✅**
