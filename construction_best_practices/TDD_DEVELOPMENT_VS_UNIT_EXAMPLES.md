# TDD Development vs Unit Testing Examples

## Real-World Example: Email Service with Two-Link Template

This document demonstrates the practical difference between **Development TDD** and **Unit TDD** using our recent email service implementation.

---

## 🛠️ Development TDD Example (Integration Testing)

**Context**: Implementing new feature - email template with two distinct links

**Purpose**: Ensure the complete email workflow works with real system integration

### Development Test Implementation

```python
"""Development TDD: Real components, real dependencies, full integration."""

@pytest.mark.integration
async def test_email_service_sends_two_link_email_complete_workflow():
    """Development test: Complete email workflow with real components and dependencies."""

    # ✅ REAL CONFIGURATION - Actual service configuration
    config = {
        "spark_ui_base_url": "http://localhost:3000",
        "default_reviewer_email": "reviewer@company.com",
        "link_expiration_hours": 24
    }

    # ✅ REAL GMAIL CLIENT - Actual Gmail integration (or real test client)
    gmail_client = GmailClient(oauth_credentials)

    # ✅ REAL EMAIL SERVICE - The actual component being developed
    email_service = AnalysisReviewEmailService(config, gmail_client)

    # ✅ REAL INITIALIZATION - Connect to actual databases and services
    success = await email_service.initialize()
    assert success, "Email service should initialize with real dependencies"

    # ✅ REAL TEST DATA - Realistic document data that exercises full path
    document_data = {
        "type": "Invoice",
        "invoice_uuid": "test-invoice-abc123",
        "vendor": "ABC Construction Company",
        "invoice_total": 2750.50,
        "confidence_score": 0.72,
        "invoice_description": "Construction materials and labor"
    }

    # ✅ REAL SECURE TOKEN SERVICE - Actual token generation
    secure_url = await email_service._token_service.generate_secure_email_link(
        thread_id="test_thread_123",
        assistant_id="test_assistant_456",
        document_data=document_data
    )

    # ACT: Call the real method with real data
    result = await email_service.send_review_notification(
        thread_id="test_thread_123",
        document_data=document_data,
        reviewer_email="integration.test@company.com"
    )

    # ✅ ASSERT REAL SYSTEM BEHAVIOR
    assert result is True, "Email should be sent successfully through real Gmail"

    # ✅ VERIFY REAL EMAIL WAS SENT
    sent_emails = gmail_client.get_sent_emails(limit=1)
    latest_email = sent_emails[0]

    # ✅ VERIFY REAL EMAIL CONTENT - Both links present
    assert "View Invoice Details" in latest_email.html_body
    assert "Pending Invoices Dashboard" in latest_email.html_body
    assert "test-invoice-abc123" in latest_email.html_body
    assert secure_url in latest_email.html_body
    assert "http://localhost:3000/api/human-review/dashboard" in latest_email.html_body

    # ✅ VERIFY REAL DATABASE INTEGRATION
    token_record = await email_service._token_service.get_token_by_thread_id("test_thread_123")
    assert token_record is not None, "Token should be stored in real database"
    assert token_record["consumed"] == False, "Token should not be consumed yet"

    # ✅ VERIFY REAL SYSTEM INTEGRATION - Dashboard actually accessible
    import httpx
    dashboard_response = await httpx.AsyncClient().get("http://localhost:8000/api/human-review/dashboard")
    assert dashboard_response.status_code == 200, "Dashboard should be accessible"
```

### Development TDD Characteristics

- **Real Integration**: Tests the complete workflow from input to email delivery
- **Real Dependencies**: Uses actual Gmail client, database connections, token service
- **Real Data Flow**: Exercises the full code path with realistic test data
- **System Verification**: Ensures new feature works with existing system components
- **End-to-End Validation**: Verifies email delivery, database updates, and UI accessibility

---

## 🔬 Unit TDD Example (Isolated Testing)

**Context**: Testing specific behavior - email template generation logic

**Purpose**: Verify isolated component behavior with mocked dependencies

### Unit Test Implementation

```python
"""Unit TDD: Real component, mocked dependencies, isolated behavior."""

@pytest.mark.unit
def test_email_template_generates_two_links_correctly():
    """Unit test: Template generation with mocked dependencies."""

    # ✅ REAL COMPONENT - Test the actual email service
    email_service = AnalysisReviewEmailService(test_config)

    # ✅ MINIMAL TEST DATA - Just what's needed for this behavior
    document_data = {
        "type": "Invoice",
        "invoice_uuid": "test-invoice-456",
        "vendor": "Test Vendor Corp",
        "invoice_total": 1500.00,
        "confidence_score": 0.85
    }

    secure_url = "https://localhost:3000/review?token=mock_secure_token_123"
    reviewer_email = "unit.test@company.com"

    # ACT: Call the real template generation method
    html_template = email_service._create_secure_review_email_template(
        document_data, secure_url, reviewer_email
    )

    # ✅ ASSERT ISOLATED BEHAVIOR - Template generation logic
    assert isinstance(html_template, str), "Should return HTML string"
    assert len(html_template) > 500, "Should generate substantial HTML content"

    # ✅ VERIFY SPECIFIC BEHAVIOR - Two distinct links
    assert "View Invoice Details" in html_template, "Must contain invoice details link"
    assert "Pending Invoices Dashboard" in html_template, "Must contain dashboard link"

    # ✅ VERIFY URL CONSTRUCTION - Correct URL patterns
    assert secure_url in html_template, "Must include provided secure URL"
    assert "api/human-review/dashboard" in html_template, "Must include dashboard URL"

    # ✅ VERIFY DATA INCLUSION - All document data present
    assert "test-invoice-456" in html_template, "Must include invoice UUID"
    assert "Test Vendor Corp" in html_template, "Must include vendor name"
    assert "$1500.00" in html_template or "$1,500.00" in html_template, "Must include formatted amount"
    assert "85.0%" in html_template or "85%" in html_template, "Must include confidence"

    # ✅ VERIFY HTML STRUCTURE - Valid HTML output
    assert "<!DOCTYPE html>" in html_template, "Must be complete HTML document"
    assert "<head>" in html_template and "</head>" in html_template, "Must have HTML head"
    assert "<style>" in html_template, "Must include CSS styling"
    assert "background-color:" in html_template, "Must have button styling"


@pytest.mark.unit
async def test_email_service_handles_gmail_failure_gracefully():
    """Unit test: Error handling with mocked Gmail failure."""

    # ✅ MOCK DEPENDENCIES - Isolate external systems
    mock_gmail = Mock(spec=GmailClient)
    mock_gmail.send_email.return_value = False  # Simulate Gmail failure

    mock_token_service = Mock()
    mock_token_service.generate_secure_email_link = AsyncMock(
        return_value="https://test.com/mock-secure-link"
    )

    # ✅ REAL COMPONENT - Test actual email service behavior
    email_service = AnalysisReviewEmailService(test_config, mock_gmail)
    email_service._token_service = mock_token_service

    document_data = {"type": "Invoice", "vendor": "Test Vendor"}

    # ACT: Call real method with mocked dependencies
    result = await email_service.send_review_notification(
        thread_id="test_thread_error",
        document_data=document_data,
        reviewer_email="error.test@company.com"
    )

    # ✅ ASSERT ISOLATED ERROR HANDLING
    assert result is False, "Should return False when Gmail fails"
    mock_gmail.send_email.assert_called_once(), "Should attempt to send email"

    # ✅ VERIFY GRACEFUL DEGRADATION - No exceptions raised
    # The test passing means no unhandled exceptions occurred


@pytest.mark.unit
def test_email_template_handles_missing_data_gracefully():
    """Unit test: Template generation with incomplete data."""

    # ✅ REAL COMPONENT
    email_service = AnalysisReviewEmailService({})

    # ✅ EDGE CASE DATA - Missing fields
    incomplete_data = {"type": "Invoice"}  # Missing vendor, amount, etc.

    # ACT: Real method with edge case data
    html_template = email_service._create_secure_review_email_template(
        incomplete_data, "https://test.com/token", "test@example.com"
    )

    # ✅ ASSERT GRACEFUL HANDLING
    assert isinstance(html_template, str), "Should still generate template"
    assert "Invoice" in html_template, "Should include available data"
    assert "Unknown Vendor" in html_template or "N/A" in html_template, "Should handle missing vendor"
    assert len(html_template) > 100, "Should generate meaningful content despite missing data"
```

### Unit TDD Characteristics

- **Isolated Testing**: Tests specific component behavior without external dependencies
- **Mocked Dependencies**: Gmail client, token service, database connections are mocked
- **Focused Behavior**: Each test verifies one specific aspect of component logic
- **Edge Case Coverage**: Tests error conditions, missing data, boundary values
- **Fast Feedback**: Runs quickly without network calls or database connections

---

## 📊 Comparison Summary

| Aspect             | Development TDD                                | Unit TDD                                           |
| ------------------ | ---------------------------------------------- | -------------------------------------------------- |
| **Purpose**        | System integration & feature completion        | Isolated behavior verification                     |
| **Components**     | Real email service + real dependencies         | Real email service + mocked dependencies           |
| **Test Data**      | Complete realistic document data               | Minimal data for specific behavior                 |
| **Dependencies**   | Real Gmail, database, token service            | Mocked Gmail, database, token service              |
| **Scope**          | Full workflow from input to email delivery     | Template generation, error handling, edge cases    |
| **Execution Time** | Slower (seconds) - real I/O operations         | Faster (milliseconds) - no I/O                     |
| **Failure Causes** | Integration issues, system regressions         | Component logic bugs, edge case failures           |
| **When to Use**    | New features, major changes, bug investigation | Behavior verification, error handling, performance |

---

## 🎯 Practical Guidelines

### Use Development TDD When:

- ✅ Implementing new features (like two-link email template)
- ✅ Making major refactoring changes
- ✅ Investigating bugs that may involve multiple components
- ✅ Verifying that changes don't break existing workflows
- ✅ Testing with realistic data and scenarios

### Use Unit TDD When:

- ✅ Verifying specific component behaviors
- ✅ Testing error handling and edge cases
- ✅ Ensuring component logic is correct regardless of external state
- ✅ Creating fast-running tests for development iteration
- ✅ Testing input validation and boundary conditions

### Both Approaches Should:

- ✅ Test the **REAL COMPONENT** being developed
- ✅ Use descriptive test names that explain the behavior
- ✅ Have clear arrange/act/assert structure
- ✅ Include comprehensive assertions that verify expected behavior
- ✅ Be maintainable and serve as documentation

---

**Remember**: The goal is to have confidence that your code works correctly both in isolation (unit tests) and as part of the larger system (development tests). Both approaches are essential for comprehensive test coverage.
