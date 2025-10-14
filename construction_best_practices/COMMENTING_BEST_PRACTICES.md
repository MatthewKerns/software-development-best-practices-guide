# Code Commenting Best Practices — LangGraph/LangSmith Project

## 📝 MANDATORY: Comprehensive Commenting Guidelines

**This guide establishes mandatory commenting standards for maintainable, self-documenting code in our Python LangGraph project.**

---

## 1. Comment Hierarchy & Principles

### Priority Order for Code Documentation

1. **Self-documenting code** (clear names, simple logic) - **FIRST PRIORITY**
2. **Type hints and docstrings** (what the code does)
3. **Inline comments** (why the code does it)
4. **README files** (how to use the code)

### Core Commenting Philosophy

**Comments should explain the "WHY" not the "WHAT"**

- Focus on business reasoning and decision context
- Explain non-obvious technical choices
- Document edge cases and their handling
- Provide context for future maintainers

---

## 2. When to Comment (Required vs. Forbidden)

### ✅ **ALWAYS Comment:**

#### Business Logic Reasoning

```python
# ✅ GOOD: Explains business context
if confidence_score < 0.7:
    # Business rule: Low confidence invoices require manual review
    # to prevent incorrect data entry in accounting system
    return {"status": "manual_review", "reason": "low_confidence"}
```

#### Edge Case Handling

```python
# ✅ GOOD: Explains why edge case exists
if len(text) < 50:
    # PDFs with <50 chars often indicate extraction failure
    # (OCR issues, corrupted files, or image-only documents)
    logger.warning("Suspiciously short text extraction")
    return fallback_to_llm_extraction(pdf_data)
```

#### Performance Decisions

```python
# ✅ GOOD: Explains performance choice
llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)
# Temperature=0 ensures consistent output for same input,
# critical for invoice processing where variation could cause
# different field extractions from identical documents
```

#### Security Considerations

```python
# ✅ GOOD: Explains security requirement
user_id = request.headers.get('user_id')
# Required for audit trail per SOX compliance - all financial
# data access must be traceable to specific user accounts
```

#### Integration Complexities

```python
# ✅ GOOD: Explains API-specific pattern
async def search_gmail_messages(query: str):
    # Gmail API uses custom query syntax: 'has:attachment' not 'hasAttachment'
    # Pagination returns max 500 results per page
    # Rate limit: 250 queries/user/100 seconds
    gmail_query = f"has:attachment {query}"
```

#### Non-obvious Technical Decisions

```python
# ✅ GOOD: Explains library choice
from decimal import Decimal

def calculate_total(amounts: list[str]) -> Decimal:
    # Using Decimal instead of float to avoid floating-point precision issues
    # Critical for financial calculations where rounding errors are unacceptable
    return sum(Decimal(amount) for amount in amounts)
```

### ❌ **NEVER Comment:**

#### Obvious Code

```python
# ❌ BAD: States the obvious
i += 1  # Increment i
user_name = user.name  # Get user name
return result  # Return the result
```

#### Commented-Out Code

```python
# ❌ BAD: Use git history instead
# old_function_call()  # This was the old approach
# legacy_implementation()  # Remove this line
return new_function_call()
```

#### Redundant Information

```python
# ❌ BAD: Already clear from function name
def calculate_total_amount(invoices):
    # This function calculates the total amount
    pass
```

#### Outdated Information

```python
# ❌ BAD: Comment doesn't match code
# Uses Gmail API v1  (when code actually uses v2)
service = build('gmail', 'v2', credentials=creds)
```

---

## 3. Comments-First Pseudocode Pattern (MANDATORY)

### Process: Comments Before Implementation

**Before writing ANY implementation, write complete business logic as detailed comments:**

```python
async def extract_invoice_data(text: str) -> dict:
    """Extract structured data from invoice text."""

    # Step 1: Validate input text is not empty or corrupted
    # - Return error if None or empty string
    # - Log warning if text is suspiciously short (< 50 chars)
    # - Check for common OCR artifacts that indicate poor extraction

    # Step 2: Use LLM to extract structured fields
    # - Prompt engineering: Include few-shot examples for consistency
    # - Temperature=0 for deterministic results across runs
    # - Handle rate limiting with exponential backoff (max 3 retries)
    # - Set timeout of 30 seconds to prevent hanging requests

    # Step 3: Validate extracted fields against business rules
    # - Invoice number: Must be alphanumeric, 5-20 characters
    # - Amount: Must be positive number, reasonable range ($0.01-$1M)
    # - Date: Must be valid date, not future, within last 5 years
    # - Vendor: Must not be in blocked vendor list

    # Step 4: Return structured result with confidence scores
    # - Include field-level confidence for downstream decisions
    # - Flag potential issues for manual review queue
    # - Provide actionable error messages for failed extractions

    # Implementation starts here...
    pass
```

### Benefits of Comments-First Approach

1. **Forces clear thinking** before coding
2. **Documents design decisions** while they're fresh
3. **Guides implementation** step by step
4. **Serves as specification** for tests
5. **Makes code review easier** by explaining intent

---

## 4. Comment Quality Standards by Code Type

### Business Logic Comments

```python
def validate_invoice_amount(amount: float) -> bool:
    """Validate invoice amount meets business requirements."""

    # Business rule: Amounts over $10K require additional approval workflow
    # This prevents fraudulent or accidental high-value transactions
    if amount > 10000:
        logger.info(f"High-value invoice flagged: ${amount}")
        return False

    # Business rule: Round amounts over $500 often indicate manual entry errors
    # Real receipts rarely have perfectly round amounts at this scale
    if amount >= 500 and amount == int(amount):
        logger.warning(f"Suspicious round amount: ${amount}")
        return False

    return True
```

### Error Handling Comments

```python
try:
    result = await llm.ainvoke(prompt)
except RateLimitError:
    # Exponential backoff: Critical for production stability
    # OpenAI rate limits can cause cascading failures without proper handling
    # Max wait time of 30 seconds prevents indefinite blocking
    wait_time = min(2 ** retry_count, 30)
    await asyncio.sleep(wait_time)
    retry_count += 1
except TimeoutError:
    # Timeout after 30 seconds to prevent hanging workflows
    # Return partial result rather than failing entire pipeline
    logger.error("LLM request timed out, using fallback extraction")
    return fallback_extraction_result
```

### LangGraph Node Comments

```python
async def gmail_extraction_node(state: WorkflowState) -> WorkflowState:
    """Extract emails and attachments from Gmail API.

    Workflow context: First step in invoice processing pipeline.
    Must handle Gmail API quotas and authentication refresh.
    """

    # Gmail API has aggressive rate limiting (250 queries/user/100s)
    # Batch requests where possible to stay within limits
    # Use exponential backoff for quota exceeded errors

    # Authentication: Use service account for unattended operation
    # Falls back to OAuth if service account credentials unavailable
    # Refresh tokens automatically when they expire

    # Error recovery: Transient failures should retry with backoff
    # Permanent failures (auth, quota) should fail fast with clear messaging
    # Log all API interactions for debugging and audit purposes
```

### Data Processing Service Comments

```python
async def normalize_currency(amount_str: str) -> float:
    """Convert various currency formats to standardized float values.

    Business requirement: Handle international invoice formats from
    vendors in different countries with varying currency representations.
    """

    # Remove common currency symbols and formatting
    # Supports: $1,234.56, €1.234,56, 1234.56 USD, ¥1,234 etc.
    # Handle both comma and period as decimal separators

    # Validation: Must be positive, within reasonable business range
    # Reject negative amounts (could indicate credit memos needing special handling)
    # Flag amounts over $100K for additional review

    # Precision: Round to 2 decimal places for accounting system compatibility
    # Use Decimal type to avoid floating-point precision issues
```

### Integration Client Comments

```python
class GmailClient:
    """Gmail API client with robust error handling and rate limiting.

    Production requirements: Must handle quota exhaustion, auth refresh,
    and transient network failures without losing processing state.
    """

    async def search_messages(self, query: str) -> list[str]:
        # Gmail search uses custom query syntax different from standard email
        # Common gotchas: 'has:attachment' not 'hasAttachment'
        # Date format: 'after:2023/01/01' not 'after:2023-01-01'

        # Pagination: Gmail returns max 500 results per page
        # For large mailboxes, may need multiple API calls
        # Use pageToken for continuation across requests

        # Caching: Results can be cached for 5 minutes to reduce API calls
        # during development/testing cycles
        # Production should have shorter cache TTL (30 seconds)
```

---

## 5. Docstring Standards (Required)

### Function Docstrings

```python
async def extract_text_from_pdf(content: bytes, use_llm_fallback: bool = False) -> str:
    """Extract and clean text from PDF using hybrid pypdf + LLM approach.

    Business context: Invoice PDFs often have poor OCR quality that makes
    downstream data extraction unreliable. This hybrid approach uses fast
    local extraction with optional AI enhancement for better accuracy.

    Args:
        content: PDF file content as bytes. Must be valid PDF format.
        use_llm_fallback: If True, uses ChatGPT to clean/structure extracted text.
                         Requires OPENAI_API_KEY environment variable.
                         Increases processing time but improves accuracy.

    Returns:
        Cleaned text string ready for data extraction, or descriptive error message.
        Error messages are user-friendly and indicate next steps.
        Empty string indicates extraction failed but processing can continue.

    Raises:
        ValueError: Never raised - all errors are caught and returned as strings
                   to maintain consistent interface for workflow processing.
        PDFError: Only for corrupted files that cannot be processed at all.

    Example:
        >>> pdf_bytes = Path("invoice.pdf").read_bytes()
        >>> text = await extract_text_from_pdf(pdf_bytes, use_llm_fallback=True)
        >>> assert "INVOICE" in text.upper()

    Performance:
        - Standard PDFs: 1-3 seconds
        - With LLM fallback: 5-10 seconds
        - Memory usage: ~2x PDF file size
    """
```

### Class Docstrings

```python
class InvoiceExtractor:
    """Extracts structured data from invoice documents with confidence scoring.

    Business purpose: Automates accounts payable processing by converting
    unstructured invoice PDFs into structured data for ERP integration.

    Architecture: Uses hybrid approach combining pypdf extraction with
    LLM-based field identification and validation. Falls back to manual
    review for low-confidence extractions.

    Performance: Processes typical invoices in 2-5 seconds with 95% accuracy
    on invoices from known vendors. Unknown vendors may have lower accuracy.

    Attributes:
        llm: ChatOpenAI instance configured for consistent field extraction
        confidence_threshold: Minimum confidence for automatic processing (0.7)
        retry_count: Current retry attempt for rate limiting handling
        validation_rules: Business rules for field validation

    Example:
        >>> extractor = InvoiceExtractor(confidence_threshold=0.8)
        >>> result = await extractor.extract(pdf_bytes)
        >>> if result.confidence >= 0.8:
        ...     process_automatically(result.data)
        ... else:
        ...     queue_for_manual_review(result.data)
    """
```

### Test Function Docstrings

```python
@pytest.mark.asyncio
async def test_extract_invoice_handles_corrupted_pdf():
    """Test Given: corrupted PDF, When: extraction called, Then: graceful error handling.

    Real-world context: 15% of email attachments in production are corrupted
    during transmission. This test ensures we provide actionable error messages
    instead of letting exceptions propagate to users.

    Business impact: Unhandled PDF errors cause workflow failures and require
    manual intervention, reducing automation efficiency.
    """
    # Test implementation with business context explaining why this matters
```

---

## 6. Comment Maintenance & Review

### During Code Reviews

**Reviewers MUST verify:**

- [ ] **Comments explain "why" not "what"**
- [ ] **Business context is included for complex logic**
- [ ] **Comments are accurate after code changes**
- [ ] **Comments add value beyond what code expresses**
- [ ] **No commented-out code exists**
- [ ] **TODO comments are specific and actionable**

### During Refactoring

**Developers MUST:**

- [ ] **Update comments when logic changes**
- [ ] **Remove obsolete comments**
- [ ] **Add comments for new edge cases**
- [ ] **Ensure comment-to-code ratio stays reasonable (10-20%)**
- [ ] **Verify business context remains accurate**

### Comment Quality Checklist

```bash
# Before committing code, verify:
grep -r "# TODO\|# FIXME\|# XXX" src/ --exclude-dir=__pycache__

# ✅ Comments explain "why" not "what"
# ✅ Business context included for complex logic
# ✅ Error handling strategies documented
# ✅ Performance decisions explained
# ✅ All public functions have comprehensive docstrings
# ✅ TODO comments are specific and actionable
# ✅ No commented-out code (use git history)
# ✅ Comments updated when code changes
```

---

## 7. Comment Anti-Patterns (Forbidden)

### Common Anti-Patterns to Avoid

#### Obvious Comments

```python
# ❌ BAD: States the obvious
user_id = request.headers.get('user_id')  # Get user ID from headers
count = 0  # Initialize counter to zero
for item in items:  # Loop through items
    count += 1  # Increment count
```

#### Misleading Comments

```python
# ❌ BAD: Comment doesn't match code
# This function adds two numbers
def multiply(a, b):
    return a * b

# ❌ BAD: Outdated information
# Uses legacy API v1  (when code actually uses v3)
client = APIClient(version="v3")
```

#### Vague or Useless Comments

```python
# ❌ BAD: Provides no useful information
# TODO: Fix this  (No context about what needs fixing)
# HACK: This is a hack  (Doesn't explain why or what better solution would be)
# This is important  (Doesn't explain why it's important)
```

#### Excessive Comments

```python
# ❌ BAD: Over-commenting obvious code
def calculate_total(amounts):
    # Initialize total to zero
    total = 0
    # Loop through each amount
    for amount in amounts:
        # Add amount to total
        total += amount
    # Return the calculated total
    return total
```

### Better Alternatives

#### Self-Documenting Code

```python
# ✅ GOOD: Clear naming eliminates need for comments
def calculate_invoice_total_with_tax(line_items: list[InvoiceItem]) -> Decimal:
    subtotal = sum(item.amount for item in line_items)
    tax_rate = get_applicable_tax_rate(line_items[0].location)
    return subtotal * (1 + tax_rate)
```

#### Meaningful Business Context

```python
# ✅ GOOD: Explains business reasoning
user_id = request.headers.get('user_id')
# Required for audit trail per SOX compliance - all financial
# data access must be traceable to specific user accounts
```

#### Specific, Actionable TODOs

```python
# ✅ GOOD: Specific and actionable
# TODO: Implement exponential backoff for Gmail API rate limiting
# See: https://developers.google.com/gmail/api/guides/batch
# Target: Complete by Q2 2025 for production reliability
```

---

## 8. Advanced Commenting Patterns

### Error Context Comments

```python
async def process_invoice_workflow(state: WorkflowState):
    """Process invoice through complete workflow."""

    try:
        extracted_data = await extract_invoice_data(state.pdf_data)
    except ExtractionError as e:
        # Extraction failures often indicate:
        # 1. Corrupted PDF (20% of cases) - log and notify sender
        # 2. Unsupported format (15% of cases) - provide format guidance
        # 3. OCR quality issues (10% of cases) - suggest manual entry
        logger.error(f"Invoice extraction failed: {e}")
        return state.with_error("extraction_failed", str(e))
```

### Performance Comments

```python
def batch_process_invoices(invoices: list[Invoice]) -> list[ProcessedInvoice]:
    """Process multiple invoices efficiently."""

    # Batch size of 10 optimized based on:
    # - LLM API rate limits (60 RPM for GPT-4)
    # - Memory usage (each invoice ~2MB in memory)
    # - Timeout constraints (30s per batch max)
    batch_size = 10

    # Process in parallel within each batch for 3x speedup
    # Sequential processing across batches to respect rate limits
    results = []
    for batch in chunk_list(invoices, batch_size):
        batch_results = await asyncio.gather(*[
            process_single_invoice(invoice) for invoice in batch
        ])
        results.extend(batch_results)

    return results
```

### Configuration Comments

```python
class ExtractionConfig:
    """Configuration for invoice extraction with business justification."""

    # Confidence threshold based on 6 months of production data:
    # - 0.8+ threshold: 99.5% accuracy, 15% manual review rate
    # - 0.7+ threshold: 97.2% accuracy, 35% manual review rate
    # - 0.6+ threshold: 93.1% accuracy, 60% manual review rate
    CONFIDENCE_THRESHOLD = 0.7

    # Timeout set to prevent workflow blocking:
    # - 95th percentile processing time: 8 seconds
    # - 30 second timeout allows for occasional complex PDFs
    # - Longer timeouts cause user experience issues
    EXTRACTION_TIMEOUT = 30

    # Maximum file size based on infrastructure limits:
    # - Lambda memory limit: 3GB
    # - PDF processing requires ~3x file size in memory
    # - 25MB limit provides safe margin with good user experience
    MAX_PDF_SIZE_MB = 25
```

---

## 9. Tools & Automation

### Comment Quality Checking

```bash
# Check for comment anti-patterns
grep -r "# Get\|# Set\|# Initialize\|# Loop\|# Return" src/ --include="*.py"

# Find TODO/FIXME comments
grep -r "# TODO\|# FIXME\|# XXX\|# HACK" src/ --include="*.py"

# Check for commented-out code
grep -r "^[[:space:]]*# [[:space:]]*[a-zA-Z_].*(" src/ --include="*.py"
```

### Documentation Generation

```python
# Use tools like pydoc or sphinx to generate docs from docstrings
# Ensure docstrings are comprehensive enough for auto-generation

def generate_api_docs():
    """Generate API documentation from docstrings."""
    # pydoc can extract and format docstrings automatically
    # sphinx provides more advanced documentation generation
    pass
```

### Comment Metrics

```python
def analyze_comment_quality(file_path: str) -> dict:
    """Analyze comment quality metrics for a Python file."""

    with open(file_path) as f:
        lines = f.readlines()

    metrics = {
        "total_lines": len(lines),
        "comment_lines": sum(1 for line in lines if line.strip().startswith('#')),
        "docstring_lines": count_docstring_lines(lines),
        "code_lines": count_code_lines(lines),
    }

    metrics["comment_ratio"] = metrics["comment_lines"] / metrics["code_lines"]
    metrics["documentation_ratio"] = (metrics["comment_lines"] + metrics["docstring_lines"]) / metrics["total_lines"]

    # Target ratios based on project standards:
    # - Comment ratio: 0.1-0.2 (10-20% of code lines)
    # - Documentation ratio: 0.15-0.25 (15-25% of total lines)

    return metrics
```

---

## 10. Integration with Development Workflow

### Pre-commit Hooks

```bash
#!/bin/bash
# .git/hooks/pre-commit

# Check for comment quality
python scripts/check_comment_quality.py

# Verify no commented-out code
if grep -r "^[[:space:]]*# [[:space:]]*[a-zA-Z_].*(" src/ --include="*.py"; then
    echo "Error: Found commented-out code. Please remove or convert to proper comments."
    exit 1
fi

# Check for vague TODOs
if grep -r "# TODO: Fix\|# TODO: This\|# FIXME$" src/ --include="*.py"; then
    echo "Error: Found vague TODO comments. Please make them specific and actionable."
    exit 1
fi
```

### IDE Integration

```json
// VS Code settings for comment highlighting
{
  "better-comments.tags": [
    {
      "tag": "!",
      "color": "#FF2D00",
      "strikethrough": false,
      "backgroundColor": "transparent"
    },
    {
      "tag": "?",
      "color": "#3498DB",
      "strikethrough": false,
      "backgroundColor": "transparent"
    },
    {
      "tag": "//",
      "color": "#474747",
      "strikethrough": true,
      "backgroundColor": "transparent"
    },
    {
      "tag": "todo",
      "color": "#FF8C00",
      "strikethrough": false,
      "backgroundColor": "transparent"
    }
  ]
}
```

---

**Remember: Great comments explain WHY the code exists, not WHAT it does. They provide context that helps future developers (including yourself) understand the reasoning behind decisions! 📝🧠✅**
