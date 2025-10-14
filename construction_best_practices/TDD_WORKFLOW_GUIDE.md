# TDD Workflow Guide — LangGraph/LangSmith Project

## 🧪 MANDATORY: Test-Driven Development Process

**This guide provides comprehensive TDD workflow for Python LangGraph projects with LangSmith tracing.**

**CRITICAL: We use TWO DISTINCT TDD approaches depending on the context:**

---

## 🛠️ TDD for Development (Integration & System Testing)

**Use when developing NEW functionality, major changes, or investigating bugs**

### 🎯 Purpose

- Ensure new functionality integrates with the existing system
- Verify that changes don't break existing workflows
- Test entire data flow from input to output
- Validate real-world scenarios and edge cases

### 📋 Development TDD Process

1. **📖 Read README.md** for the target directory first
2. **🔍 Understand system context** - How does this component fit in the larger workflow?
3. **✅ Write integration tests** using **REAL components** and **REAL dependencies**
4. **📝 Write comments-first pseudocode** design
5. **⚡ Implement complete working code** that passes integration tests
6. **🔄 Refactor with green tests** ensuring entire system still works

### 🏗️ Development Test Characteristics

```python
# ✅ DEVELOPMENT TEST EXAMPLE
@pytest.mark.integration
async def test_email_service_complete_workflow():
    """Development test: Full email workflow with real components."""
    # REAL CONFIG - Use actual configuration
    config = {
        "spark_ui_base_url": "http://localhost:3000",
        "default_reviewer_email": "reviewer@company.com"
    }

    # REAL GMAIL CLIENT - Use actual Gmail integration
    gmail_client = GmailClient(oauth_credentials)

    # REAL EMAIL SERVICE - The component we're developing
    email_service = AnalysisReviewEmailService(config, gmail_client)

    # REAL INITIALIZATION - Connect to actual databases/services
    success = await email_service.initialize()
    assert success, "Email service should initialize with real dependencies"

    # REAL TEST DATA - Realistic document data
    document_data = {
        "type": "Invoice",
        "invoice_uuid": "test-invoice-abc123",
        "vendor": "ABC Construction Company",
        "invoice_total": 2750.50,
        "confidence_score": 0.72
    }

    # ACT: Call the real method with test data
    result = await email_service.send_review_notification(
        thread_id="test_thread_123",
        document_data=document_data,
        reviewer_email="test@company.com"
    )

    # ASSERT: Verify real system behavior
    assert result is True, "Email should be sent successfully"

    # VERIFY INTEGRATION: Check that the email contains expected elements
    sent_emails = gmail_client.get_sent_emails(limit=1)
    latest_email = sent_emails[0]
    assert "View Invoice Details" in latest_email.body
    assert "Pending Invoices Dashboard" in latest_email.body
    assert "test-invoice-abc123" in latest_email.body
```

### ✅ Development Test Principles

- **REAL COMPONENTS**: Always test the actual class/function being developed
- **REAL DEPENDENCIES**: Include actual databases, APIs, file systems, network calls
- **REAL DATA FLOW**: Use realistic test data that exercises the complete code path
- **SYSTEM INTEGRATION**: Verify that changes work with the existing system
- **END-TO-END VALIDATION**: Test from input to final output/side effect

---

## 🔬 TDD for Unit Testing (Isolated Component Testing)

**Use when creating focused tests for specific behaviors, edge cases, or error handling**

### 🎯 Purpose

- Isolate and verify specific component behaviors
- Test edge cases and error conditions
- Ensure component logic is correct regardless of external state
- Provide fast feedback during development iterations

### 📋 Unit TDD Process

1. **📖 Identify the single behavior** to test
2. **🔍 Define the component boundaries** - What should be real vs mocked?
3. **✅ Write unit tests** using **REAL component** but **MOCKED dependencies**
4. **📝 Write focused test scenarios** for edge cases
5. **⚡ Verify isolated behavior** works correctly
6. **🔄 Test error handling** and boundary conditions

### 🏗️ Unit Test Characteristics

```python
# ✅ UNIT TEST EXAMPLE
@pytest.mark.unit
async def test_email_service_handles_gmail_failure_gracefully():
    """Unit test: Test component behavior when dependency fails."""
    # MOCK DEPENDENCIES - Isolate external systems
    mock_gmail = Mock(spec=GmailClient)
    mock_gmail.send_email.return_value = False  # Simulate failure

    mock_token_service = Mock()
    mock_token_service.generate_secure_email_link = AsyncMock(
        return_value="https://test.com/secure-link"
    )

    # REAL COMPONENT - Test the actual email service
    email_service = AnalysisReviewEmailService(test_config, mock_gmail)
    email_service._token_service = mock_token_service

    # TEST DATA - Minimal data needed for this behavior
    document_data = {"type": "Invoice", "vendor": "Test Vendor"}

    # ACT: Call the real method
    result = await email_service.send_review_notification(
        thread_id="test_thread_123",
        document_data=document_data,
        reviewer_email="test@company.com"
    )

    # ASSERT: Verify isolated behavior
    assert result is False, "Service should return False when Gmail fails"
    mock_gmail.send_email.assert_called_once()

    # VERIFY ERROR HANDLING: Component handles failure gracefully
    # No exceptions should be raised, just return False
```

### ✅ Unit Test Principles

- **REAL COMPONENT**: Always test the actual class/method implementation
- **MOCK DEPENDENCIES**: Isolate external systems (databases, APIs, network)
- **FOCUSED BEHAVIOR**: Test one specific behavior or business rule
- **ISOLATED VERIFICATION**: Component works regardless of external state
- **EDGE CASE COVERAGE**: Test error conditions, null inputs, boundary values

---

## 📊 When to Use Each Approach

| Context                     | TDD Approach    | Components | Dependencies | Test Focus              |
| --------------------------- | --------------- | ---------- | ------------ | ----------------------- |
| **New Feature Development** | Development TDD | Real       | Real         | System integration      |
| **Major Refactoring**       | Development TDD | Real       | Real         | No regressions          |
| **Bug Investigation**       | Development TDD | Real       | Real         | Reproduce real issue    |
| **Behavior Verification**   | Unit TDD        | Real       | Mocked       | Isolated logic          |
| **Error Handling**          | Unit TDD        | Real       | Mocked       | Edge cases              |
| **Performance Testing**     | Unit TDD        | Real       | Mocked       | Component speed         |
| **API Contract Testing**    | Unit TDD        | Real       | Mocked       | Input/output validation |

---

## 🚀 Test Execution Commands

### Development TDD Commands (Integration Testing)

```bash
# Development TDD loop - Integration tests with real dependencies
pytest -m "integration or node" -q

# Run integration tests with verbose output
pytest -m "integration" -v

# Development testing with coverage (ensure system integration)
pytest -m "integration or node" --cov=src --cov-fail-under=85

# Full development test suite
pytest -m "integration or node or graph" -v
```

### Unit TDD Commands (Isolated Testing)

```bash
# Unit TDD loop - Fast isolated behavior tests
pytest -m "unit" -q

# Unit tests with coverage (focus on component logic)
pytest -m "unit" --cov=src --cov-fail-under=90

# Unit tests for specific module
pytest tests/unit_tests/services/email/ -m "unit" -v

# Fast feedback loop for specific test
pytest tests/unit_tests/services/email/test_analysis_review_email_service_actual_functionality.py::TestAnalysisReviewEmailServiceActualFunctionality::test_email_template_contains_two_required_links -v
```

### Combined Testing Commands

```bash
# Full test suite (excluding live external services)
pytest -m "not live" -v

# All tests with coverage gate
pytest --cov=src --cov-fail-under=90

# Nightly/CI comprehensive testing
pytest -m "graph or contract or e2e" -v

# Live external service tests (use sparingly)
pytest -m "live" --tb=long
```

---

## 1. Documentation-First Approach

### 📖 README Discovery Process

**Before writing ANY code or tests:**

1. **Read the corresponding README.md file** for your target directory:

   - `src/integrations/auth/oauth.py` → Read `src/integrations/auth/README.md`
   - `src/services/extraction/text_extraction.py` → Read `src/services/extraction/README.md`
   - `src/workflow/steps/` → Read `src/workflow/steps/README.md`
   - **Unit test updates** → Read nearest `tests/unit_tests/{area}/README.md`

2. **Update README.md if needed** based on implementation discoveries

3. **Extract behavior requirements** using Given/When/Then format from README context

### 🎯 Requirement Extraction Patterns

```markdown
# Example: From src/services/extraction/README.md

"Invoice extraction should handle corrupted PDFs gracefully"

# Extracted Requirements:

- Given: corrupted PDF attachment, When: extraction attempted, Then: graceful error returned
- Given: valid PDF with poor quality scan, When: extracted, Then: LLM fallback used
- Given: PDF with mixed languages, When: processed, Then: primary language detected
```

---

## 2. Red-Green-Refactor TDD Cycle

### 🔄 Mandatory Process for ALL Changes

**Before ANY refactoring or code improvement:**

- **📖 FIRST read `.github/REFACTORING_BEST_PRACTICES.md`**
- Follow Red-Green-Refactor with proper safety nets
- Use design patterns and techniques from refactoring guide

### Step-by-Step TDD Process

#### **Step 1: Scope as Behavior**

- Write user story in PR description with Given/When/Then format
- Extract 3-5 acceptance criteria from README.md context
- Define clear behavior boundaries

**Example User Story:**

```markdown
As an invoice processing system
I want to gracefully handle corrupted PDF attachments
So that users receive actionable error messages instead of system crashes

Acceptance Criteria:

1. Given corrupted PDF, When processed, Then specific error message returned
2. Given PDF with password protection, When accessed, Then auth error handled
3. Given extremely large PDF, When processed, Then size limit validation applied
```

#### **Step 2: Write Failing Tests FIRST**

**Test Categories by Scope:**

1. **Unit Tests** - Pure logic, no I/O

   ```python
   @pytest.mark.unit
   def test_normalize_currency_handles_international_formats():
       """Test Given: €1.234,56 format, When: normalized, Then: 1234.56 returned."""
       result = normalize_currency("€1.234,56")
       assert result == 1234.56
   ```

2. **Node Tests** - Single LangGraph node with explicit I/O schema

   ```python
   @pytest.mark.node
   async def test_pdf_extraction_node_schema_compliance():
       """Test Given: valid input state, When: node executed, Then: output schema valid."""
       input_state = WorkflowState(pdf_data=sample_pdf_bytes)
       result = await pdf_extraction_node(input_state)

       # Assert schema compliance
       assert isinstance(result, WorkflowState)
       assert "extracted_text" in result
       assert result.confidence >= 0.0
   ```

3. **Graph Tests** - Multiple nodes, use fakes for external services

   ```python
   @pytest.mark.graph
   async def test_invoice_processing_pipeline():
       """Test Given: email with invoice, When: full graph, Then: structured output."""
       # Use fake clients to avoid external calls
       with patch_gmail_client(), patch_sheets_client():
           result = await run_invoice_graph(initial_state)
           assert result.status == "completed"
   ```

4. **Contract Tests** - API adapter interfaces

   ```python
   @pytest.mark.contract
   def test_gmail_client_interface_compliance():
       """Test Given: Gmail client, When: called, Then: expected interface honored."""
       client = GmailClient()
       # Test interface without calling real API
       assert hasattr(client, 'search_messages')
       assert hasattr(client, 'get_message')
   ```

5. **E2E Tests** - Only when absolutely necessary (rare, slow)
   ```python
   @pytest.mark.e2e
   @pytest.mark.slow
   async def test_complete_invoice_workflow_integration():
       """Test real end-to-end invoice processing workflow."""
       # Only for critical happy path validation
   ```

#### **Step 3: Proper pytest Markers**

```python
# Marker definitions and usage
@pytest.mark.unit      # Fast, pure logic, no I/O
@pytest.mark.node      # Single LangGraph node tests
@pytest.mark.graph     # Multiple nodes or subgraph tests
@pytest.mark.contract  # Adapter interface tests
@pytest.mark.e2e       # End-to-end scenario tests
@pytest.mark.slow      # Long-running tests (>1 second)
@pytest.mark.live      # Calls external services
```

#### **Step 4: Test Quality Requirements**

**Failing Test Characteristics:**

- Clear Given/When/Then test names
- Edge case parameterization (empty, malformed, duplicate, oversized)
- Property-based tests for parsers/normalizers using Hypothesis
- Contract tests with local fakes (never real services unless `@live`)

**Example Edge Case Coverage:**

```python
@pytest.mark.parametrize("invalid_input", [
    "",  # Empty string
    None,  # None value
    b"corrupted pdf content",  # Invalid PDF
    b"x" * 50_000_000,  # Oversized content
    "text with unicode: 🚀📊💻",  # Unicode handling
])
def test_pdf_extraction_handles_edge_cases(invalid_input):
    """Test edge cases that commonly occur in production."""
    with pytest.raises((ValueError, PDFError)):
        extract_text_from_pdf(invalid_input)
```

#### **Step 5: Mock Strategy**

**Preferred Approach: Simple Fakes**

```python
# ✅ GOOD: Simple, predictable fakes
class FakeGmailClient:
    def __init__(self):
        self.messages = {"msg1": {"subject": "Invoice", "attachments": ["inv.pdf"]}}

    def search_messages(self, query: str) -> list[str]:
        return ["msg1", "msg2"]

    def get_message(self, msg_id: str) -> dict:
        return self.messages.get(msg_id, {})

# ❌ AVOID: Complex mocking that's hard to understand
@patch('gmail.service.users().messages().list')
@patch('gmail.service.users().messages().get')
def test_with_complex_mocks(mock_get, mock_list):
    # Hard to understand, fragile, tied to implementation
```

**Mock ALL External Dependencies:**

- File I/O operations
- Network requests
- Time/date functions
- API clients
- Database connections

**Deterministic Test Fixtures:**

```python
@pytest.fixture
def sample_invoice_pdf():
    """Deterministic PDF content for testing."""
    return Path("tests/fixtures/sample_invoice.pdf").read_bytes()

@pytest.fixture
def sample_email_data():
    """Deterministic email structure."""
    return {
        "id": "test_email_123",
        "subject": "Invoice from Vendor Corp",
        "attachments": [{"name": "invoice.pdf", "size": 150000}]
    }
```

#### **Step 6: LangSmith Integration Testing**

**Trace Assertions in Graph/E2E Tests:**

```python
@pytest.mark.graph
async def test_invoice_processing_trace_quality():
    """Test Given: invoice workflow, When: executed, Then: trace meets quality standards."""

    with langsmith_tracer() as tracer:
        result = await run_invoice_workflow(test_state)
        trace = tracer.get_trace()

    # Assert trace characteristics
    assert trace.tool_call_count <= 5  # Performance budget
    assert trace.total_tokens < 10000  # Token budget
    assert "gmail.search" in trace.tool_calls
    assert trace.sensitive_fields_redacted  # Security requirement

    # Assert no unintended tool usage
    forbidden_tools = ["file_system", "internet_search"]
    assert not any(tool in trace.tool_calls for tool in forbidden_tools)
```

**Dataset Usage for Canonical I/O:**

```python
def test_extraction_output_consistency():
    """Test against LangSmith dataset to detect output drift."""

    dataset = load_langsmith_dataset("invoice_extraction_golden")

    for example in dataset.examples[:10]:  # Sample for speed
        result = extract_invoice_data(example.input)

        # Allow for minor variations, fail on material changes
        assert_invoice_equivalent(result, example.expected_output)

def assert_invoice_equivalent(actual, expected):
    """Compare with business-appropriate tolerance."""
    assert actual["vendor"] == expected["vendor"]  # Exact match
    assert abs(actual["amount"] - expected["amount"]) < 0.01  # Float tolerance
    assert actual["confidence"] >= expected["confidence"] - 0.05  # Model variance
```

#### **Step 7: Comments-First Implementation Design**

**Before ANY coding, write complete business logic as comments:**

```python
async def extract_invoice_data(pdf_bytes: bytes) -> InvoiceData:
    """Extract structured invoice data from PDF bytes."""

    # Step 1: Input validation and preprocessing
    # - Validate PDF format and size limits (< 25MB for performance)
    # - Log extraction attempt with PDF metadata for audit trail
    # - Handle edge cases: empty files, password-protected, corrupted

    # Step 2: Text extraction with fallback strategy
    # - Primary: Fast pypdf extraction for standard PDFs
    # - Fallback: LLM-enhanced extraction for poor quality/scanned PDFs
    # - Quality assessment: Determine if text extraction confidence is sufficient

    # Step 3: Structured field extraction
    # - Use LLM with temperature=0 for consistent results
    # - Include few-shot examples in prompt for better accuracy
    # - Extract core fields: vendor, amount, date, invoice_number
    # - Calculate field-level confidence scores

    # Step 4: Business rule validation
    # - Amount: Must be positive, within reasonable range ($0.01-$100K)
    # - Date: Valid format, not future-dated, within business range
    # - Vendor: Not in blocked vendor list, reasonable name format

    # Step 5: Return structured result with metadata
    # - Include extraction confidence and validation status
    # - Flag items requiring manual review (low confidence, unusual patterns)
    # - Provide actionable error messages for failed extractions

    # Implementation follows...
    pass
```

**Comment Quality Standards:**

- Explain business reasoning and requirements
- Document edge case handling strategies
- Include performance and security considerations
- Provide context for non-obvious technical decisions

#### **Step 8: Minimal Implementation**

**Make smallest change to pass tests:**

```python
# Start with simplest implementation that passes tests
def extract_invoice_data(pdf_bytes: bytes) -> dict:
    # Implement just enough to make failing test pass
    if not pdf_bytes:
        raise ValueError("PDF data cannot be empty")

    # Add minimal logic incrementally
    return {"status": "extracted", "confidence": 0.8}
```

**Development Guidelines:**

- Keep logs/traces enabled during development
- Maintain pydantic schemas for all node I/O
- Raise typed errors (not generic exceptions)
- Keep prompts/config in code so tests can assert on them

#### **Step 9: Refactor with Green Tests**

**Only refactor when all tests pass:**

- Improve naming and function extraction
- Consolidate prompts and configuration
- **All refactors must be guarded by existing tests**
- **Reference `.github/REFACTORING_BEST_PRACTICES.md`** for techniques

**Refactoring Safety Net:**

```bash
# Before refactoring
pytest -m "unit or node" -q  # Ensure green tests

# After each refactor step
pytest -m "unit or node" -q  # Verify no regression
git add -A && git commit -m "Refactor: extract validation function"
```

#### **Step 10: Integration Validation**

**Final validation steps:**

- Run contract tests if adapter/API touched
- Update LangSmith datasets when outputs change intentionally
- Verify performance hasn't regressed
- Check integration with downstream systems

---

## 3. Test Structure & Organization

### Repository Test Structure

```
tests/
├── unit/                    # Pure logic, no I/O
│   ├── services/
│   ├── integrations/
│   └── models/
├── nodes/                   # Single LangGraph nodes
│   ├── extraction/
│   ├── validation/
│   └── output/
├── graph/                   # Multi-node workflows
│   ├── invoice_processing/
│   └── receipt_processing/
├── contracts/               # API adapter tests
│   ├── gmail/
│   └── sheets/
├── e2e/                     # End-to-end scenarios
└── _fixtures/               # Test data
    ├── pdfs/
    ├── emails/
    └── expected_outputs/
```

### Test Naming Conventions

**File Naming:**

- `test_{feature}_{case}.py` - Specific feature and case
- `test_integration_{system}.py` - Integration tests
- `test_contract_{adapter}.py` - Contract tests

**Class Naming:**

- `TestInvoiceExtraction` - Feature-based grouping
- `TestErrorHandling` - Behavior-based grouping
- `TestPerformance` - Quality-based grouping

**Method Naming:**

- `test_{feature}_{specific_case}` - Clear behavior description
- `test_given_{condition}_when_{action}_then_{outcome}` - BDD style

### Directory Mirroring Requirements

**Every `src/` directory MUST have corresponding `tests/unit_tests/` structure:**

```
src/services/extraction/text_extraction.py
→ tests/unit_tests/services/extraction/test_text_extraction.py

src/integrations/gmail/client.py
→ tests/unit_tests/integrations/gmail/test_client.py
```

---

## 4. Test Execution & Commands

### Fast Development Loop

```bash
# Core TDD cycle - run constantly during development
pytest -m "unit or node" -q

# With coverage for completeness check
pytest -m "unit or node" --cov=src --cov-report=term-missing
```

### Broader Testing

```bash
# Before committing changes
pytest -m "unit or node or graph and not slow" -q

# Full test suite (CI/CD)
pytest -m "not live" -v

# Live integration tests (separate run)
pytest -m live -v
```

### Specific Test Categories

```bash
pytest -m unit -v           # Unit tests only
pytest -m node -v           # Node tests only
pytest -m graph -v          # Graph tests only
pytest -m contract -v       # Contract tests only
pytest -m "slow or live" -v # Integration tests
```

### Performance & Quality Checks

```bash
# Coverage enforcement
pytest --cov=src --cov-fail-under=80

# Performance benchmarking
pytest --benchmark-only

# Test timing analysis
pytest --durations=10
```

---

## 5. State Management & Assertions

### Workflow State Validation Helpers

```python
def assert_workflow_state_valid(state: WorkflowState, stage: str):
    """Assert workflow state meets requirements for given stage."""

    if stage == "post_extraction":
        required_keys = {"extracted_text", "confidence", "pdf_metadata"}
        missing = required_keys - set(state.keys())
        assert not missing, f"Missing required keys for {stage}: {missing}"

        assert isinstance(state.confidence, float)
        assert 0.0 <= state.confidence <= 1.0

    elif stage == "post_validation":
        required_keys = {"invoice_data", "validation_status", "flags"}
        missing = required_keys - set(state.keys())
        assert not missing, f"Missing required keys for {stage}: {missing}"

        assert state.validation_status in ["valid", "invalid", "review_required"]

def assert_langsmith_trace_quality(trace):
    """Assert LangSmith trace meets quality standards."""

    # Performance budgets
    assert trace.total_duration < 30.0, "Processing should complete within 30 seconds"
    assert trace.total_tokens < 15000, "Token usage should stay within budget"

    # Security requirements
    assert trace.sensitive_data_redacted, "Sensitive data must be redacted"

    # Tool usage validation
    expected_tools = {"gmail.search", "pdf.extract", "llm.invoke"}
    actual_tools = set(trace.tool_calls)
    assert actual_tools.issubset(expected_tools), f"Unexpected tools used: {actual_tools - expected_tools}"
```

### Error Handling Patterns

```python
@pytest.mark.unit
def test_error_handling_provides_actionable_messages():
    """Test Given: various error conditions, When: handled, Then: actionable messages returned."""

    test_cases = [
        (b"", "PDF data cannot be empty. Please attach a valid PDF file."),
        (b"not_pdf", "Invalid PDF format. Please ensure file is a valid PDF document."),
        (b"x" * 50_000_000, "PDF file too large (>25MB). Please use a smaller file."),
    ]

    for invalid_input, expected_message in test_cases:
        with pytest.raises(ValueError, match=expected_message):
            extract_invoice_data(invalid_input)
```

---

## 6. Definition of Done (DoD) Checklist

### For ANY Feature or Refactor:

**Pre-Implementation:**

- [ ] **README.md consulted** for business context and requirements
- [ ] **Behavior requirements extracted** using Given/When/Then format
- [ ] **Acceptance criteria defined** (3-5 specific examples)

**Test-First Development:**

- [ ] **Failing tests written FIRST** that capture acceptance criteria
- [ ] **Comments-first implementation design** completed before coding
- [ ] **Edge cases identified** and parameterized in tests

**Implementation Quality:**

- [ ] **Unit & node tests** added/updated for new behavior & edge cases
- [ ] **Graph test** (or updated dataset) covering happy path
- [ ] **Contract test** added if new external API touched
- [ ] **All tests pass** with appropriate markers

**Code Quality:**

- [ ] **Business logic comments** explain "why" decisions were made
- [ ] **Complex algorithms** documented with step-by-step comments
- [ ] **Error handling comments** explain recovery strategies
- [ ] **All public functions** have comprehensive docstrings with business context

**Integration & Validation:**

- [ ] **Coverage unchanged or higher** (no regression, no new xfail)
- [ ] **LangSmith datasets** updated if outputs changed intentionally
- [ ] **Performance benchmarks** maintained (no significant regression)
- [ ] **README.md updated** if patterns or usage changed

---

## 7. Advanced TDD Techniques

### Property-Based Testing with Hypothesis

```python
from hypothesis import given, strategies as st

@given(
    pdf_size=st.integers(min_value=1000, max_value=1_000_000),
    content_type=st.sampled_from(["invoice", "receipt", "statement"])
)
def test_extraction_invariants(pdf_size, content_type):
    """Test that extraction maintains invariants across input variations."""

    pdf_data = generate_test_pdf(size=pdf_size, content=content_type)

    try:
        result = extract_document_data(pdf_data)

        # Invariants that must always hold
        assert isinstance(result, dict)
        assert "confidence" in result
        assert 0.0 <= result["confidence"] <= 1.0

        if result.get("amount"):
            assert isinstance(result["amount"], (int, float))
            assert result["amount"] >= 0

    except (ValueError, DocumentError):
        # Acceptable to fail on invalid inputs
        pass
```

### Mutation Testing for Test Quality

```python
# Use mutmut or similar tools to verify test quality
# Tests should fail when code is mutated

def test_amount_validation_catches_mutations():
    """Test that amount validation logic is thoroughly tested."""

    # This test should fail if validation logic is mutated
    invalid_amounts = [-1, 0, float('inf'), float('nan')]

    for amount in invalid_amounts:
        with pytest.raises(ValueError):
            validate_invoice_amount(amount)
```

### Characterization Testing for Legacy Code

```python
def test_legacy_extraction_behavior():
    """Capture current behavior before refactoring legacy code."""

    # Record exact current behavior for regression detection
    legacy_input = load_fixture("legacy_test_case.pdf")
    current_output = legacy_extract_function(legacy_input)

    # Store snapshot for comparison during refactoring
    expected_structure = {
        "vendor": str,
        "amount": float,
        "confidence": float,
        "metadata": dict
    }

    for key, expected_type in expected_structure.items():
        assert key in current_output
        assert isinstance(current_output[key], expected_type)
```

---

## 8. Continuous Improvement

### Test Metrics to Track

```python
def analyze_test_quality():
    """Analyze test suite quality metrics."""

    metrics = {
        "coverage_percentage": get_test_coverage(),
        "test_execution_time": measure_test_speed(),
        "flaky_test_rate": calculate_flaky_tests(),
        "test_to_code_ratio": count_test_vs_source_lines(),
        "assertion_density": count_assertions_per_test(),
    }

    # Set quality gates
    assert metrics["coverage_percentage"] >= 80
    assert metrics["test_execution_time"] < 60  # seconds for full suite
    assert metrics["flaky_test_rate"] < 0.05   # < 5% flaky tests

    return metrics
```

### Test Debt Management

```bash
# Identify test debt
grep -r "@pytest.mark.skip\|@pytest.mark.xfail" tests/ | wc -l

# Find slow tests
pytest --durations=0 | grep "SLOW"

# Check test coverage gaps
pytest --cov=src --cov-report=html
# Review coverage report for gaps
```

---

**Remember: TDD is not just about testing - it's a design methodology that leads to better, more maintainable code. Always start with failing tests! 🧪✅**
