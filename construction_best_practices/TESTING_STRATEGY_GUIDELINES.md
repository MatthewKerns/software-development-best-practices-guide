# Testing Strategy Guidelines — Unit, Integration & Contract Testing

**Date**: August 24, 2025  
**Purpose**: Comprehensive testing strategy for LangGraph/LangSmith workflow with clear guidelines for unit, integration, and contract testing patterns.

## 📋 Overview

This guide establishes **clear standards** for when to use each type of test and provides **concrete patterns** for testing LangGraph checkpoint resume functionality and workflow components.

### Testing Philosophy

Following the **Test Pyramid** approach with LangGraph-specific considerations:

```
        /\
       /  \
      / E2E \ ← Few, expensive, realistic scenarios
     /______\
    /        \
   /Integration\ ← Some, test component interactions
  /__________\
 /            \
/  Unit Tests  \ ← Many, fast, isolated logic
\______________/
```

**Key Principle**: **Test behavior, not implementation details**

---

## 🧪 Unit Testing Guidelines

### Definition & Scope

**Unit Tests** verify **isolated business logic** with **no external dependencies**.

### When to Use Unit Tests

- ✅ **Pure functions** with deterministic inputs/outputs
- ✅ **Business logic** calculations and validations
- ✅ **Data transformations** and parsing
- ✅ **Error handling** and edge cases
- ✅ **State transitions** in isolated components

### Unit Test Characteristics

- **Speed**: < 1ms per test
- **Dependencies**: None (all mocked)
- **Scope**: Single function or class method
- **Deterministic**: Same input always produces same output
- **Independent**: Can run in any order

### Unit Test Patterns

#### Example 1: Pure Business Logic

```python
# src/services/validation/currency_validator.py
def normalize_currency(currency_string: str) -> float:
    """Convert various currency formats to normalized float value."""
    # Remove currency symbols and spaces
    cleaned = re.sub(r'[^\d.,+-]', '', currency_string)

    # Handle comma as decimal separator (European format)
    if ',' in cleaned and '.' in cleaned:
        # Assume comma is thousands separator if dot comes after
        if cleaned.rindex(',') < cleaned.rindex('.'):
            cleaned = cleaned.replace(',', '')
        else:
            # Comma is decimal separator
            cleaned = cleaned.replace('.', '').replace(',', '.')
    elif ',' in cleaned:
        # Single comma - could be decimal or thousands
        if len(cleaned.split(',')[1]) <= 2:
            cleaned = cleaned.replace(',', '.')  # Decimal separator
        else:
            cleaned = cleaned.replace(',', '')   # Thousands separator

    return float(cleaned)

# tests/unit_tests/services/validation/test_currency_validator.py
@pytest.mark.unit
class TestCurrencyValidator:
    """Unit tests for currency validation logic."""

    @pytest.mark.parametrize("input_currency,expected", [
        ("$1,234.56", 1234.56),
        ("€1.234,56", 1234.56),  # European format
        ("1,234", 1234.0),       # Thousands separator
        ("1,23", 1.23),          # Decimal separator
        ("-$500.00", -500.0),    # Negative amount
        ("1234", 1234.0),        # Plain number
    ])
    def test_normalize_currency_valid_formats(self, input_currency, expected):
        """Test currency normalization for valid formats."""
        result = normalize_currency(input_currency)
        assert result == expected

    @pytest.mark.parametrize("invalid_input", [
        "",                      # Empty string
        "abc",                   # No numbers
        "$",                     # Only symbol
        "1.2.3",                # Multiple decimals
        "1,2,3.45.67",          # Invalid format
    ])
    def test_normalize_currency_invalid_formats(self, invalid_input):
        """Test currency normalization rejects invalid formats."""
        with pytest.raises(ValueError):
            normalize_currency(invalid_input)
```

#### Example 2: State Machine Logic

```python
# src/workflow/state_manager.py
class WorkflowStateManager:
    """Manages workflow state transitions."""

    def can_resume_after_step(self, current_step: str, target_step: str) -> bool:
        """Check if workflow can resume from target step given current state."""
        step_order = [
            "extract_emails",
            "extract_text",
            "classify_documents",
            "extract_data",
            "analyze_data",
            "send_email",
            "human_review",
            "update_database"
        ]

        try:
            current_index = step_order.index(current_step)
            target_index = step_order.index(target_step)

            # Can only resume from earlier or same step
            return target_index <= current_index
        except ValueError:
            return False

# tests/unit_tests/workflow/test_state_manager.py
@pytest.mark.unit
class TestWorkflowStateManager:
    """Unit tests for workflow state management logic."""

    def setup_method(self):
        """Set up test instance."""
        self.state_manager = WorkflowStateManager()

    @pytest.mark.parametrize("current_step,target_step,expected", [
        ("human_review", "send_email", True),      # Resume from earlier step
        ("human_review", "human_review", True),    # Resume from same step
        ("send_email", "human_review", False),     # Cannot skip forward
        ("extract_data", "extract_emails", True),  # Resume from beginning
        ("invalid_step", "send_email", False),     # Invalid current step
        ("send_email", "invalid_step", False),     # Invalid target step
    ])
    def test_can_resume_after_step(self, current_step, target_step, expected):
        """Test step resume validation logic."""
        result = self.state_manager.can_resume_after_step(current_step, target_step)
        assert result == expected
```

#### Example 3: ResumeController Business Logic

```python
# tests/unit_tests/workflow/checkpoint_manager/test_resume_controller_business_logic.py
@pytest.mark.unit
class TestResumeControllerBusinessLogic:
    """Unit tests for ResumeController pure business logic."""

    def test_determine_resume_action_approve(self):
        """Test action determination for approval scenario."""
        from src.workflow.checkpoint_manager.resume_controller import ResumeController

        # Test the pure logic method (not the async workflow method)
        controller = ResumeController(mock_checkpoint_manager=Mock())

        action = controller._determine_resume_action(
            user_action="approve",
            current_step="send_analysis_result_email"
        )

        assert action == {
            "type": "resume_after_current",
            "target_step": "analysis_review_decision",
            "state_updates": {}
        }

    def test_determine_resume_action_modify(self):
        """Test action determination for modify scenario."""
        controller = ResumeController(mock_checkpoint_manager=Mock())

        action = controller._determine_resume_action(
            user_action="modify",
            current_step="send_analysis_result_email",
            feedback="Update vendor name to 'Acme Corp'"
        )

        assert action == {
            "type": "restart_from_step",
            "target_step": "analyze_data",
            "state_updates": {
                "human_feedback": "Update vendor name to 'Acme Corp'",
                "modification_requested": True
            }
        }

    @pytest.mark.parametrize("invalid_action", ["invalid", "", None, 123])
    def test_determine_resume_action_invalid(self, invalid_action):
        """Test action determination with invalid inputs."""
        controller = ResumeController(mock_checkpoint_manager=Mock())

        with pytest.raises(ValueError, match="Invalid action"):
            controller._determine_resume_action(invalid_action, "send_analysis_result_email")
```

---

## 🔗 Integration Testing Guidelines

### Definition & Scope

**Integration Tests** verify **component interactions** and **data flow** between system parts.

### When to Use Integration Tests

- ✅ **LangGraph node execution** with real state management
- ✅ **Checkpoint persistence** and resume operations
- ✅ **Service collaborations** (database + email services)
- ✅ **API endpoint behavior** with real request/response cycles
- ✅ **Error propagation** across component boundaries

### Integration Test Characteristics

- **Speed**: 100ms - 10s per test
- **Dependencies**: Real components, fake external services
- **Scope**: Multiple components working together
- **State**: May require setup/teardown
- **Isolation**: Tests don't interfere with each other

### Integration Test Patterns

#### Example 1: LangGraph Checkpoint Integration

```python
# tests/integration_tests/workflow/test_langgraph_checkpoint_integration.py
@pytest.mark.integration
@pytest.mark.checkpoint
class TestLangGraphCheckpointIntegration:
    """Integration tests for LangGraph checkpoint persistence and resume."""

    @pytest.fixture
    async def workflow_graph(self):
        """Create real workflow graph with SQLite checkpointer."""
        from src.workflow.graph import create_graph_async
        return await create_graph_async()

    @pytest.fixture
    def test_thread_id(self):
        """Generate unique thread ID for test isolation."""
        return f"test-thread-{uuid.uuid4()}"

    async def test_checkpoint_persistence_across_interrupt(self, workflow_graph, test_thread_id):
        """Test that checkpoints persist workflow state across interrupts."""
        # Start workflow and run until interrupt
        config = {"configurable": {"thread_id": test_thread_id}}
        initial_state = WorkflowState(
            user_id="test@example.com",
            analysis_result={"vendor": "Test Corp", "amount": 123.45}
        )

        # Run workflow until human review interrupt
        result = await workflow_graph.ainvoke(initial_state, config)

        # Verify workflow stopped at interrupt point
        assert result["current_step"] == "send_analysis_result_email"
        assert "human_feedback" not in result

        # Verify checkpoint was created
        checkpoints = await workflow_graph.astream_checkpoints(config)
        checkpoint_list = [cp async for cp in checkpoints]

        assert len(checkpoint_list) > 0
        latest_checkpoint = checkpoint_list[0]
        assert latest_checkpoint.values["current_step"] == "send_analysis_result_email"

        # Resume workflow from checkpoint
        updated_state = {**result, "human_feedback": "Approved"}
        resumed_result = await workflow_graph.ainvoke(updated_state, config)

        # Verify workflow completed from resume point
        assert resumed_result["current_step"] == "update_database"
        assert resumed_result["human_feedback"] == "Approved"

    async def test_resume_controller_with_real_checkpoints(self, workflow_graph, test_thread_id):
        """Test ResumeController with real LangGraph checkpoints."""
        from src.workflow.checkpoint_manager.resume_controller import ResumeController
        from src.workflow.checkpoint_manager.checkpoint_manager import CheckpointManager

        # Create real checkpoint manager with the workflow's checkpointer
        checkpoint_manager = CheckpointManager(workflow_graph.checkpointer)
        resume_controller = ResumeController(checkpoint_manager)

        # Set up initial workflow state
        config = {"configurable": {"thread_id": test_thread_id}}
        initial_state = WorkflowState(
            user_id="test@example.com",
            analysis_result={"vendor": "Test Corp", "amount": 123.45}
        )

        # Run workflow to interrupt
        await workflow_graph.ainvoke(initial_state, config)

        # Test approve scenario with real checkpoints
        resume_result = await resume_controller.resume_after_email_step(
            thread_id=test_thread_id,
            feedback="Integration test approval"
        )

        assert resume_result["status"] == "resumed"
        assert resume_result["target_step"] == "analysis_review_decision"

        # Verify workflow state was properly updated
        final_state = await workflow_graph.aget_state(config)
        assert final_state.values["human_feedback"] == "Integration test approval"
```

#### Example 2: Database Service Integration

```python
# tests/integration_tests/services/test_database_service_integration.py
@pytest.mark.integration
@pytest.mark.database
class TestDatabaseServiceIntegration:
    """Integration tests for database service with Google Sheets."""

    @pytest.fixture
    async def database_service(self):
        """Create database service with test Google Sheets client."""
        from src.services.database.services import create_database_service

        # Use test credentials and spreadsheet
        service = create_database_service(
            database_type="google_sheets",
            auth_mode="service_account",
            test_mode=True
        )
        await service.initialize()
        return service

    @pytest.fixture
    def test_data(self):
        """Sample invoice data for testing."""
        return {
            "vendor": "Integration Test Corp",
            "invoice_number": "INT-2025-001",
            "amount": 999.99,
            "date": "2025-08-24",
            "confidence": 0.95
        }

    async def test_store_and_retrieve_invoice_data(self, database_service, test_data):
        """Test storing and retrieving invoice data through service."""
        # Store data
        store_result = await database_service.store_invoice_data(test_data)

        assert store_result["status"] == "success"
        assert "row_id" in store_result

        # Retrieve data to verify storage
        retrieved_data = await database_service.get_invoice_data(
            store_result["row_id"]
        )

        assert retrieved_data["vendor"] == test_data["vendor"]
        assert retrieved_data["amount"] == test_data["amount"]
        assert retrieved_data["invoice_number"] == test_data["invoice_number"]

    async def test_database_error_handling(self, database_service):
        """Test database service error handling with invalid data."""
        invalid_data = {
            "vendor": "",  # Missing required field
            "amount": "invalid",  # Invalid type
        }

        with pytest.raises(ValidationError) as exc_info:
            await database_service.store_invoice_data(invalid_data)

        assert "vendor" in str(exc_info.value)
        assert "amount" in str(exc_info.value)
```

#### Example 3: API Integration Testing

```python
# tests/integration_tests/api/test_human_review_api_integration.py
@pytest.mark.integration
@pytest.mark.api
class TestHumanReviewAPIIntegration:
    """Integration tests for human review API with ResumeController."""

    @pytest.fixture
    async def api_client(self):
        """Create test API client."""
        from src.api.app import create_app
        from httpx import AsyncClient

        app = create_app()
        async with AsyncClient(app=app, base_url="http://test") as client:
            yield client

    @pytest.fixture
    async def test_workflow_thread(self, api_client):
        """Set up workflow thread ready for human review."""
        # Start workflow via API
        response = await api_client.post("/api/workflow/start", json={
            "user_id": "integration-test@example.com",
            "input_data": {"test": "integration"}
        })

        thread_data = response.json()
        thread_id = thread_data["thread_id"]

        # Wait for workflow to reach human review step
        await self._wait_for_interrupt(api_client, thread_id)

        return thread_id

    async def test_approve_workflow_integration(self, api_client, test_workflow_thread):
        """Test complete approve workflow through API."""
        thread_id = test_workflow_thread

        # Send approval through API
        response = await api_client.post("/api/human-review/resume-workflow", json={
            "thread_id": thread_id,
            "action": "approve",
            "feedback": "API integration test approval"
        })

        assert response.status_code == 200
        result = response.json()

        assert result["status"] == "success"
        assert result["action"] == "resumed_after_email"
        assert "thread_id" in result

        # Verify workflow completed successfully
        status_response = await api_client.get(f"/api/workflow/status/{thread_id}")
        status_data = status_response.json()

        assert status_data["status"] == "completed"
        assert status_data["final_step"] == "update_database"

    async def test_modify_workflow_integration(self, api_client, test_workflow_thread):
        """Test complete modify workflow through API."""
        thread_id = test_workflow_thread

        # Send modification request through API
        response = await api_client.post("/api/human-review/resume-workflow", json={
            "thread_id": thread_id,
            "action": "modify",
            "feedback": "Change vendor name to 'Modified Corp'"
        })

        assert response.status_code == 200
        result = response.json()

        assert result["status"] == "success"
        assert result["action"] == "restarted_at_analyze_data"

        # Verify workflow restarted with updated data
        status_response = await api_client.get(f"/api/workflow/status/{thread_id}")
        status_data = status_response.json()

        assert status_data["status"] == "running"
        assert status_data["current_step"] == "analyze_data"
        assert "Modified Corp" in str(status_data["state"]["human_feedback"])

    async def _wait_for_interrupt(self, api_client, thread_id, timeout=30):
        """Helper to wait for workflow to reach interrupt point."""
        import asyncio

        for _ in range(timeout):
            response = await api_client.get(f"/api/workflow/status/{thread_id}")
            status = response.json()

            if status["status"] == "interrupted":
                return

            await asyncio.sleep(1)

        raise TimeoutError(f"Workflow {thread_id} did not reach interrupt within {timeout}s")
```

---

## 📋 Contract Testing Guidelines

### Definition & Scope

**Contract Tests** verify **API interfaces** and **external service integrations** work correctly.

### When to Use Contract Tests

- ✅ **LangGraph HTTP API calls** (threads, runs, checkpoints)
- ✅ **External service adapters** (Gmail, Google Sheets, OpenAI)
- ✅ **API request/response formats** match expectations
- ✅ **Error handling** for external service failures
- ✅ **Authentication flows** and token management

### Contract Test Characteristics

- **Speed**: 100ms - 1s per test
- **Dependencies**: Real API calls to external services (or realistic mocks)
- **Scope**: Interface compliance and data contracts
- **Focus**: Request/response formats, not business logic
- **Isolation**: Each test verifies one interface contract

### Contract Test Patterns

#### Example 1: LangGraph HTTP API Contract

```python
# tests/contract_tests/langgraph/test_langgraph_api_contract.py
@pytest.mark.contract
@pytest.mark.langgraph
class TestLangGraphAPIContract:
    """Contract tests for LangGraph HTTP API compliance."""

    @pytest.fixture
    def langgraph_client(self):
        """HTTP client for LangGraph server."""
        import httpx
        return httpx.AsyncClient(base_url="http://127.0.0.1:2024")

    async def test_create_thread_contract(self, langgraph_client):
        """Test thread creation API contract."""
        # Test thread creation request format
        response = await langgraph_client.post("/threads", json={
            "thread_id": f"contract-test-{uuid.uuid4()}",
            "metadata": {"test": "contract"}
        })

        assert response.status_code == 200

        # Verify response contract
        thread_data = response.json()
        required_fields = ["thread_id", "created_at", "metadata"]
        for field in required_fields:
            assert field in thread_data, f"Missing required field: {field}"

        # Verify data types
        assert isinstance(thread_data["thread_id"], str)
        assert isinstance(thread_data["created_at"], str)
        assert isinstance(thread_data["metadata"], dict)

    async def test_run_workflow_contract(self, langgraph_client):
        """Test workflow run API contract."""
        # Create thread first
        thread_response = await langgraph_client.post("/threads", json={
            "thread_id": f"run-test-{uuid.uuid4()}"
        })
        thread_id = thread_response.json()["thread_id"]

        # Test run creation request format
        run_response = await langgraph_client.post(f"/threads/{thread_id}/runs", json={
            "assistant_id": "workflow",
            "input": {
                "user_id": "contract-test@example.com",
                "messages": [],
                "analysis_result": {"test": "contract"}
            }
        })

        assert run_response.status_code == 200

        # Verify run response contract
        run_data = run_response.json()
        required_fields = ["run_id", "thread_id", "assistant_id", "status", "created_at"]
        for field in required_fields:
            assert field in run_data, f"Missing required field: {field}"

        # Verify status is valid enum value
        valid_statuses = ["queued", "in_progress", "completed", "failed", "cancelled"]
        assert run_data["status"] in valid_statuses

    async def test_checkpoint_api_contract(self, langgraph_client):
        """Test checkpoint retrieval API contract."""
        # Create thread and start run
        thread_response = await langgraph_client.post("/threads", json={
            "thread_id": f"checkpoint-test-{uuid.uuid4()}"
        })
        thread_id = thread_response.json()["thread_id"]

        # Get checkpoints for thread
        checkpoint_response = await langgraph_client.get(f"/threads/{thread_id}/history")

        assert checkpoint_response.status_code == 200

        # Verify checkpoint response contract
        checkpoint_data = checkpoint_response.json()
        assert isinstance(checkpoint_data, list)

        if checkpoint_data:  # If checkpoints exist
            checkpoint = checkpoint_data[0]
            required_fields = ["checkpoint_id", "thread_id", "created_at", "values"]
            for field in required_fields:
                assert field in checkpoint, f"Missing required field: {field}"

    async def test_error_response_contract(self, langgraph_client):
        """Test error response format contract."""
        # Make request to non-existent thread
        response = await langgraph_client.get("/threads/non-existent-thread/history")

        assert response.status_code == 404

        # Verify error response contract
        error_data = response.json()
        required_fields = ["error", "message"]
        for field in required_fields:
            assert field in error_data, f"Missing required error field: {field}"

        assert isinstance(error_data["error"], str)
        assert isinstance(error_data["message"], str)
```

#### Example 2: Gmail API Contract

```python
# tests/contract_tests/integrations/test_gmail_api_contract.py
@pytest.mark.contract
@pytest.mark.gmail
@pytest.mark.live  # Calls real Gmail API
class TestGmailAPIContract:
    """Contract tests for Gmail API integration."""

    @pytest.fixture
    def gmail_client(self):
        """Gmail client with test credentials."""
        from src.integrations.gmail.client import GmailClient
        return GmailClient()

    def test_search_messages_contract(self, gmail_client):
        """Test Gmail search API request/response contract."""
        # Test basic search
        results = gmail_client.search_messages("has:attachment", max_results=5)

        # Verify response contract
        assert isinstance(results, list)
        assert len(results) <= 5

        if results:
            message_id = results[0]
            assert isinstance(message_id, str)
            assert len(message_id) > 0

    def test_get_message_contract(self, gmail_client):
        """Test Gmail get message API contract."""
        # Get a sample message (assuming test account has messages)
        search_results = gmail_client.search_messages("has:attachment", max_results=1)

        if not search_results:
            pytest.skip("No messages available for contract testing")

        message_id = search_results[0]
        message = gmail_client.get_message(message_id)

        # Verify message response contract
        required_fields = ["id", "threadId", "snippet", "payload"]
        for field in required_fields:
            assert field in message, f"Missing required field: {field}"

        # Verify payload structure
        payload = message["payload"]
        assert "headers" in payload
        assert isinstance(payload["headers"], list)

        # Verify header structure
        if payload["headers"]:
            header = payload["headers"][0]
            assert "name" in header
            assert "value" in header

    def test_attachment_download_contract(self, gmail_client):
        """Test Gmail attachment download API contract."""
        # Find message with attachment
        search_results = gmail_client.search_messages("has:attachment", max_results=5)

        attachment_found = False
        for message_id in search_results:
            message = gmail_client.get_message(message_id)

            # Look for attachment in message parts
            attachments = gmail_client._extract_attachments(message)
            if attachments:
                attachment = attachments[0]

                # Test download contract
                attachment_data = gmail_client.download_attachment(
                    message_id, attachment["attachment_id"]
                )

                # Verify download response contract
                assert isinstance(attachment_data, bytes)
                assert len(attachment_data) > 0

                attachment_found = True
                break

        if not attachment_found:
            pytest.skip("No attachments available for contract testing")

    def test_error_handling_contract(self, gmail_client):
        """Test Gmail API error response contract."""
        # Test with invalid message ID
        with pytest.raises(GmailAPIError) as exc_info:
            gmail_client.get_message("invalid-message-id")

        error = exc_info.value
        assert hasattr(error, 'status_code')
        assert hasattr(error, 'message')
        assert error.status_code in [400, 404]  # Expected error codes
```

#### Example 3: OpenAI API Contract

```python
# tests/contract_tests/integrations/test_openai_api_contract.py
@pytest.mark.contract
@pytest.mark.openai
@pytest.mark.live  # Calls real OpenAI API
class TestOpenAIAPIContract:
    """Contract tests for OpenAI API integration."""

    @pytest.fixture
    def openai_client(self):
        """OpenAI client for testing."""
        from langchain_openai import ChatOpenAI
        return ChatOpenAI(
            model="gpt-3.5-turbo",
            temperature=0,
            max_tokens=100  # Limit tokens for testing
        )

    async def test_chat_completion_contract(self, openai_client):
        """Test OpenAI chat completion API contract."""
        from langchain_core.messages import HumanMessage

        # Test basic completion
        messages = [HumanMessage(content="Extract the vendor name from this text: Invoice from Acme Corp")]

        response = await openai_client.ainvoke(messages)

        # Verify response contract
        assert hasattr(response, 'content')
        assert isinstance(response.content, str)
        assert len(response.content) > 0

        # Verify response contains expected content
        assert "Acme Corp" in response.content

    async def test_structured_output_contract(self, openai_client):
        """Test OpenAI structured output contract."""
        from langchain_core.output_parsers import JsonOutputParser
        from pydantic import BaseModel, Field

        class InvoiceData(BaseModel):
            vendor: str = Field(description="Vendor name")
            amount: float = Field(description="Invoice amount")

        parser = JsonOutputParser(pydantic_object=InvoiceData)

        chain = openai_client | parser

        response = await chain.ainvoke(
            "Extract: Invoice from Acme Corp for $123.45"
        )

        # Verify structured response contract
        assert isinstance(response, dict)
        assert "vendor" in response
        assert "amount" in response
        assert isinstance(response["vendor"], str)
        assert isinstance(response["amount"], (int, float))

    async def test_error_handling_contract(self, openai_client):
        """Test OpenAI API error handling contract."""
        from langchain_core.messages import HumanMessage

        # Test with excessively long input (should trigger rate limiting or context limit)
        very_long_message = HumanMessage(content="x" * 100000)

        with pytest.raises((Exception)) as exc_info:
            await openai_client.ainvoke([very_long_message])

        # Verify error has proper attributes
        error = exc_info.value
        assert hasattr(error, '__str__')  # Error should be descriptive

        error_str = str(error).lower()
        expected_error_types = ["token", "limit", "context", "length", "rate"]
        assert any(error_type in error_str for error_type in expected_error_types)
```

---

## 🎯 Test Organization & Execution Strategy

### Test Suite Organization

```
tests/
├── unit_tests/                    # @pytest.mark.unit
│   ├── services/                  # Business logic, pure functions
│   ├── models/                    # Data validation, transformations
│   └── utils/                     # Helper functions, calculations
├── integration_tests/             # @pytest.mark.integration
│   ├── workflow/                  # LangGraph node/graph interactions
│   ├── api/                       # API endpoint behavior
│   └── services/                  # Service collaborations
├── contract_tests/                # @pytest.mark.contract
│   ├── langgraph/                 # LangGraph HTTP API contracts
│   ├── integrations/              # External service contracts
│   └── api/                       # Our API contracts
└── e2e_tests/                     # @pytest.mark.e2e
    ├── scenarios/                 # Complete user workflows
    └── performance/               # Load and performance tests
```

### Execution Commands

```bash
# TDD Development Loop (run frequently)
pytest -m "unit" -x -q                           # Fast unit tests only

# Pre-commit Validation (before committing)
pytest -m "unit or integration" --cov=src        # Unit + integration tests

# CI/CD Pipeline (automated testing)
pytest -m "unit or integration or contract"      # All tests except e2e

# Nightly/Release Testing (comprehensive)
pytest -m "not live" -v                          # All tests except live services
pytest -m "e2e or live" --tb=long                # End-to-end with real services

# Performance Testing (as needed)
pytest -m "performance" --benchmark-json=results.json

# Debugging Specific Areas
pytest -m "checkpoint" -v -s                     # Checkpoint-related tests only
pytest -m "langgraph" -v -s                      # LangGraph API tests only
pytest -k "resume" -v -s                         # Tests with "resume" in name
```

### Coverage Requirements by Test Type

| Test Type   | Coverage Target | Scope                    |
| ----------- | --------------- | ------------------------ |
| Unit        | 95%+            | Business logic functions |
| Integration | 80%+            | Component interactions   |
| Contract    | 100%            | API interface compliance |
| E2E         | 60%+            | Critical user paths      |

---

## 📈 Quality Gates & Continuous Improvement

### Automated Quality Checks

```python
# tests/quality/test_quality_gates.py
@pytest.mark.quality
class TestQualityGates:
    """Automated quality gate enforcement."""

    def test_unit_test_coverage_gate(self):
        """Ensure unit test coverage meets minimum threshold."""
        coverage_report = get_coverage_report()
        unit_coverage = coverage_report.get_coverage_for_markers(["unit"])

        assert unit_coverage >= 95.0, f"Unit test coverage {unit_coverage}% below 95% threshold"

    def test_integration_test_performance_gate(self):
        """Ensure integration tests complete within time budget."""
        test_durations = get_test_durations_by_marker("integration")
        slow_tests = [t for t in test_durations if t.duration > 10.0]

        assert len(slow_tests) == 0, f"Found {len(slow_tests)} integration tests >10s: {slow_tests}"

    def test_contract_test_completeness_gate(self):
        """Ensure all external APIs have contract tests."""
        external_clients = discover_external_clients()
        contract_tests = discover_contract_tests()

        missing_contracts = []
        for client in external_clients:
            if client not in contract_tests:
                missing_contracts.append(client)

        assert len(missing_contracts) == 0, f"Missing contract tests for: {missing_contracts}"
```

### Test Metrics Dashboard

```python
def generate_testing_strategy_metrics():
    """Generate metrics for testing strategy effectiveness."""

    return {
        "test_distribution": {
            "unit_tests": count_tests_by_marker("unit"),
            "integration_tests": count_tests_by_marker("integration"),
            "contract_tests": count_tests_by_marker("contract"),
            "e2e_tests": count_tests_by_marker("e2e")
        },
        "performance": {
            "unit_test_avg_time": get_avg_test_time("unit"),
            "integration_test_avg_time": get_avg_test_time("integration"),
            "total_test_suite_time": get_total_test_time()
        },
        "quality": {
            "unit_coverage": get_coverage_by_marker("unit"),
            "integration_coverage": get_coverage_by_marker("integration"),
            "contract_completeness": calculate_contract_completeness()
        },
        "reliability": {
            "flaky_test_count": count_flaky_tests(),
            "passing_rate": calculate_passing_rate(),
            "false_positive_rate": calculate_false_positive_rate()
        }
    }
```

---

## 📚 Key Takeaways

### Testing Strategy Decision Tree

```
Is it isolated business logic?
├─ YES → Unit Test (fast, deterministic, no I/O)
└─ NO → Does it involve multiple components?
    ├─ YES → Integration Test (component interactions)
    └─ NO → Does it verify an external API?
        ├─ YES → Contract Test (API compliance)
        └─ NO → Does it test a complete user scenario?
            ├─ YES → E2E Test (full workflow)
            └─ NO → Consider if test is needed
```

### Best Practices Summary

1. **Start with Unit Tests** - Test business logic first, fast feedback loop
2. **Integration Tests for Workflows** - Test LangGraph nodes and component interactions
3. **Contract Tests for APIs** - Verify external service interfaces work correctly
4. **E2E Tests for Critical Paths** - Test complete user scenarios sparingly
5. **Mock External Dependencies** - Use fakes/stubs for fast, reliable tests
6. **Test Behavior, Not Implementation** - Focus on what the code should do
7. **Maintain Test Quality** - Refactor tests as you refactor code

### Testing Anti-Patterns to Avoid

- ❌ **Testing Implementation Details** - Don't test private methods or internal structure
- ❌ **Slow Unit Tests** - Unit tests should be < 1ms, use mocks for I/O
- ❌ **Integration Tests for Business Logic** - Use unit tests for pure logic
- ❌ **No Contract Tests** - External APIs need interface verification
- ❌ **Too Many E2E Tests** - They're slow and brittle, use sparingly
- ❌ **Flaky Tests** - Fix immediately, don't ignore or skip
- ❌ **Poor Test Data Management** - Use factories and fixtures for consistent data

---

**Remember: The goal is confident, maintainable code with fast feedback loops. Choose the right test type for each scenario! 🧪⚡🎯**
