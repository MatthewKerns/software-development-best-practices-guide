# Code Construction Practices — Code Complete 2 Methodology

## 📝 Overview

**This guide applies Code Complete 2's systematic approach to code construction, focusing on defensive programming, error handling, robust software craftsmanship, and DRY (Don't Repeat Yourself) principles for our Python LangGraph project.**

Code construction is the heart of software development. This guide ensures every line of code is written with intention, clarity, robustness, and eliminates duplication through systematic DRY principles.

---

## 🎯 FOUNDATIONAL PRINCIPLE: Don't Repeat Yourself (DRY)

**DRY is the core philosophy that governs all code construction decisions.**

### The DRY Mindset

**Before writing ANY new code, ask these questions:**

1. **Does similar functionality already exist?** Search the codebase comprehensively
2. **Does this belong in an existing class?** Check if the responsibility aligns with existing components
3. **Can existing components be extended?** Consider inheritance or composition over duplication
4. **Is this a common pattern?** Extract repeated patterns into utilities or base classes

### DRY Implementation Strategy

```python
# ✅ GOOD: Centralized validation with single source of truth
class CommonValidators:
    """Single source of truth for all validation logic."""

    EMAIL_PATTERN = re.compile(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$')

    @staticmethod
    def validate_email(email: str) -> bool:
        """Centralized email validation used across all services."""
        if not email or not isinstance(email, str):
            return False
        return bool(CommonValidators.EMAIL_PATTERN.match(email.strip()))

    @staticmethod
    def validate_amount(amount: Any) -> Decimal:
        """Centralized amount validation with business rules."""
        if amount is None:
            raise ValidationError("Amount cannot be None")

        try:
            decimal_amount = Decimal(str(amount))
            if decimal_amount < 0:
                raise ValidationError(f"Amount must be non-negative: {amount}")
            if decimal_amount > Decimal('1000000'):
                raise ValidationError(f"Amount exceeds maximum: {amount}")
            return decimal_amount
        except (InvalidOperation, ValueError) as e:
            raise ValidationError(f"Invalid amount format: {amount}") from e

# Usage across multiple services - single source of truth
class InvoiceService:
    def process_invoice(self, invoice_data: dict):
        amount = CommonValidators.validate_amount(invoice_data['amount'])
        # No duplication of validation logic

class ReceiptService:
    def process_receipt(self, receipt_data: dict):
        amount = CommonValidators.validate_amount(receipt_data['total'])
        # Same validation, no code duplication

# ✅ GOOD: Base class eliminates common method duplication
class BaseDataService(ABC):
    """Abstract base eliminating CRUD operation duplication."""

    def __init__(self, database_client: Any, sheet_name: str):
        self.database_client = database_client
        self.sheet_name = sheet_name
        self.logger = logging.getLogger(self.__class__.__name__)

    async def save_record(self, record: Any) -> str:
        """Common save logic - single implementation for all services."""
        # Common validation, error handling, logging
        self.logger.info(f"Saving record to {self.sheet_name}")
        try:
            self.validate_record(record)
            result = await self._save_specific_record(record)
            self.log_operation("save", record.id, True)
            return result
        except Exception as e:
            self.log_operation("save", record.id, False)
            raise

    @abstractmethod
    async def _save_specific_record(self, record: Any) -> str:
        """Service-specific implementation - no duplication."""
        pass

# ❌ BAD: Repeated validation logic across services
class BadInvoiceService:
    def process_invoice(self, invoice_data: dict):
        # Duplicated email validation
        email = invoice_data['email']
        if not email or '@' not in email:
            raise ValueError("Invalid email")

        # Duplicated amount validation
        amount = invoice_data['amount']
        if not isinstance(amount, (int, float)) or amount < 0:
            raise ValueError("Invalid amount")

class BadReceiptService:
    def process_receipt(self, receipt_data: dict):
        # Same validation logic duplicated - violation of DRY
        email = receipt_data['customer_email']
        if not email or '@' not in email:
            raise ValueError("Invalid email")

        amount = receipt_data['total']
        if not isinstance(amount, (int, float)) or amount < 0:
            raise ValueError("Invalid amount")
```

### DRY Detection and Prevention

**Regular DRY audits:**

```bash
# Detect potential duplication patterns
grep -r "def validate_" src/ --include="*.py" | grep -v "__pycache__"
grep -r "class.*Service" src/ --include="*.py" | grep -v "__pycache__"
grep -r "async def save_" src/ --include="*.py" | grep -v "__pycache__"

# Look for repeated constants
grep -r "MAX_.*=" src/ --include="*.py" | grep -v "__pycache__"
grep -r "TIMEOUT.*=" src/ --include="*.py" | grep -v "__pycache__"
```

**Prevention checklist:**

- [ ] Search for existing similar functionality before coding
- [ ] Check if new functionality belongs in existing class
- [ ] Extract repeated patterns into base classes or utilities
- [ ] Use centralized constants instead of magic numbers
- [ ] Prefer composition/inheritance over code duplication

---

## 🛡️ Defensive Programming Principles

### 1. Assert Your Assumptions

```python
from typing import Optional
import logging

def process_invoice_amount(amount: Optional[float], currency: str = "USD") -> float:
    """Process invoice amount with defensive validations.

    Args:
        amount: Invoice amount in specified currency
        currency: Three-letter currency code (default: USD)

    Returns:
        Validated and normalized amount

    Raises:
        ValueError: If amount or currency is invalid
    """
    # Defensive assertions with clear error messages
    assert amount is not None, "Invoice amount cannot be None"
    assert isinstance(amount, (int, float)), f"Amount must be numeric, got {type(amount)}"
    assert amount >= 0, f"Invoice amount must be non-negative, got {amount}"
    assert len(currency) == 3, f"Currency must be 3-letter code, got '{currency}'"
    assert currency.isupper(), f"Currency code must be uppercase, got '{currency}'"

    # Business rule assertions
    assert amount <= 1_000_000, f"Amount {amount} exceeds maximum allowed (1M)"

    # Log successful validation for audit trail
    logging.debug(f"Validated invoice amount: {amount} {currency}")

    return float(amount)

def extract_vendor_from_text(text: str) -> Optional[str]:
    """Extract vendor name from invoice text with defensive checks."""
    # Input validation
    assert text is not None, "Text input cannot be None"
    assert isinstance(text, str), f"Text must be string, got {type(text)}"

    # Defensive programming: handle edge cases gracefully
    if not text.strip():
        logging.warning("Empty text provided for vendor extraction")
        return None

    if len(text) < 10:
        logging.warning(f"Text too short for reliable vendor extraction: {len(text)} chars")
        return None

    # Implementation continues with confidence that inputs are valid
    vendor_pattern = r'(?:from|vendor|bill\s+to):\s*([A-Za-z][A-Za-z\s&,.\''-]{2,50})'
    match = re.search(vendor_pattern, text, re.IGNORECASE)

    if match:
        vendor_name = match.group(1).strip()
        # Post-condition validation
        assert len(vendor_name) >= 2, f"Extracted vendor name too short: '{vendor_name}'"
        return vendor_name

    return None
```

### 2. Handle Errors at the Right Level

```python
class InvoiceProcessingError(Exception):
    """Base exception for invoice processing errors."""
    pass

class ExtractionTimeoutError(InvoiceProcessingError):
    """Raised when extraction takes too long."""
    pass

class ValidationError(InvoiceProcessingError):
    """Raised when business rule validation fails."""
    pass

async def process_single_invoice(invoice_data: dict) -> ProcessingResult:
    """Process one invoice with comprehensive error handling."""
    invoice_id = invoice_data.get('id', 'unknown')

    try:
        # Each step can raise specific exceptions
        validated_data = validate_invoice_data(invoice_data)
        extracted_fields = await extract_structured_data(validated_data)
        approval_result = await route_for_approval(extracted_fields)

        return ProcessingResult(
            success=True,
            invoice_id=invoice_id,
            result=approval_result
        )

    except ValidationError as e:
        # Business rule violations - log and return structured error
        logging.warning(f"Validation failed for invoice {invoice_id}: {e}")
        return ProcessingResult(
            success=False,
            invoice_id=invoice_id,
            error_type="validation_error",
            error_message=str(e),
            requires_manual_review=True
        )

    except ExtractionTimeoutError as e:
        # Timeout errors - retry with different strategy
        logging.error(f"Extraction timeout for invoice {invoice_id}: {e}")
        return ProcessingResult(
            success=False,
            invoice_id=invoice_id,
            error_type="timeout_error",
            error_message=str(e),
            should_retry=True,
            retry_strategy="use_fallback_extractor"
        )

    except Exception as e:
        # Unexpected errors - log full context and fail safely
        logging.error(
            f"Unexpected error processing invoice {invoice_id}: {e}",
            extra={
                'invoice_data_keys': list(invoice_data.keys()),
                'error_type': type(e).__name__,
                'stack_trace': traceback.format_exc()
            }
        )
        return ProcessingResult(
            success=False,
            invoice_id=invoice_id,
            error_type="system_error",
            error_message="Internal processing error",
            requires_manual_review=True
        )

async def process_invoice_batch(invoices: list[dict]) -> BatchResult:
    """Process multiple invoices with batch-level error handling."""
    # Defensive input validation
    assert isinstance(invoices, list), f"Expected list, got {type(invoices)}"
    assert len(invoices) > 0, "Invoice list cannot be empty"
    assert len(invoices) <= 100, f"Batch too large: {len(invoices)} (max 100)"

    results = []
    failed_count = 0

    for invoice in invoices:
        try:
            result = await process_single_invoice(invoice)
            results.append(result)

            if not result.success:
                failed_count += 1

        except Exception as e:
            # Catch-all for batch processing - don't let one failure stop the batch
            logging.error(f"Fatal error in batch processing: {e}")
            results.append(ProcessingResult(
                success=False,
                invoice_id=invoice.get('id', 'unknown'),
                error_type="fatal_error",
                error_message="Failed to process"
            ))
            failed_count += 1

    return BatchResult(
        total_processed=len(invoices),
        successful_count=len(invoices) - failed_count,
        failed_count=failed_count,
        results=results
    )
```

### 3. Fail Fast, Fail Safe

```python
def validate_llm_configuration(config: dict) -> None:
    """Validate LLM configuration at startup - fail fast if invalid."""
    required_keys = ['api_key', 'model_name', 'temperature', 'max_tokens']

    # Fail fast: check all requirements immediately
    for key in required_keys:
        if key not in config:
            raise ValueError(f"Missing required LLM config key: {key}")

    # Validate specific constraints
    if not config['api_key'].startswith(('sk-', 'test-')):
        raise ValueError("API key format invalid")

    if config['temperature'] < 0 or config['temperature'] > 1:
        raise ValueError(f"Temperature must be 0-1, got {config['temperature']}")

    if config['max_tokens'] < 1 or config['max_tokens'] > 4096:
        raise ValueError(f"max_tokens must be 1-4096, got {config['max_tokens']}")

    logging.info("LLM configuration validated successfully")

def safe_divide_amounts(dividend: float, divisor: float) -> Optional[float]:
    """Safely divide amounts with explicit zero handling."""
    # Fail safe: handle edge cases gracefully
    if divisor == 0:
        logging.warning(f"Division by zero attempted: {dividend} / {divisor}")
        return None

    if dividend == 0:
        return 0.0

    # Check for potential floating point issues
    if abs(divisor) < 1e-10:
        logging.warning(f"Divisor very close to zero: {divisor}")
        return None

    result = dividend / divisor

    # Validate result is reasonable
    if not math.isfinite(result):
        logging.error(f"Division produced invalid result: {dividend} / {divisor} = {result}")
        return None

    return result
```

---

## 🔧 Code Construction Patterns

### 1. Initialize Variables Completely

```python
# ✅ GOOD: Complete initialization with clear defaults
class InvoiceProcessor:
    def __init__(self, config: ProcessingConfig):
        # Initialize all instance variables explicitly
        self.config: ProcessingConfig = config
        self.llm_client: Optional[ChatOpenAI] = None
        self.processed_count: int = 0
        self.error_count: int = 0
        self.start_time: Optional[datetime] = None
        self.current_batch: list[Invoice] = []
        self.processing_state: ProcessingState = ProcessingState.IDLE
        self.retry_counts: dict[str, int] = {}

        # Validate configuration during initialization
        self._validate_configuration()

        # Initialize LLM client with error handling
        try:
            self._initialize_llm_client()
        except Exception as e:
            logging.error(f"Failed to initialize LLM client: {e}")
            self.llm_client = None

    def _validate_configuration(self) -> None:
        """Validate processing configuration completeness."""
        required_attrs = ['max_retries', 'timeout_seconds', 'batch_size']
        for attr in required_attrs:
            if not hasattr(self.config, attr):
                raise ValueError(f"Configuration missing required attribute: {attr}")

# ❌ BAD: Incomplete initialization leads to runtime errors
class BadInvoiceProcessor:
    def __init__(self, config):
        self.config = config
        # Missing initialization of other attributes
        # self.processed_count will cause AttributeError later
```

### 2. Use Meaningful Variable Scope

```python
def process_email_attachments(email_message: EmailMessage) -> list[ProcessingResult]:
    """Process all attachments in email with proper variable scoping."""

    # Function-level variables with clear purpose
    processing_results: list[ProcessingResult] = []
    attachment_count = len(email_message.attachments)
    processing_start_time = datetime.now()

    logging.info(f"Processing {attachment_count} attachments from email {email_message.id}")

    for attachment_index, attachment in enumerate(email_message.attachments):
        # Loop-level variables - limited scope
        attachment_name = attachment.filename or f"attachment_{attachment_index}"
        attachment_size_mb = len(attachment.content) / (1024 * 1024)

        # Nested scope for specific processing
        try:
            # Block-level variables for specific operation
            if attachment.content_type == 'application/pdf':
                extraction_config = PDFExtractionConfig(
                    use_ocr=True,
                    timeout_seconds=30,
                    quality_threshold=0.7
                )

                result = process_pdf_attachment(
                    content=attachment.content,
                    filename=attachment_name,
                    config=extraction_config
                )
            else:
                result = ProcessingResult(
                    success=False,
                    filename=attachment_name,
                    error_message=f"Unsupported file type: {attachment.content_type}"
                )

            processing_results.append(result)

        except Exception as e:
            # Error handling scope - capture context
            error_context = {
                'attachment_index': attachment_index,
                'attachment_name': attachment_name,
                'attachment_size_mb': attachment_size_mb,
                'error_type': type(e).__name__
            }

            logging.error(f"Failed to process attachment: {e}", extra=error_context)

            processing_results.append(ProcessingResult(
                success=False,
                filename=attachment_name,
                error_message=str(e)
            ))

    # Function conclusion - log summary
    successful_count = sum(1 for r in processing_results if r.success)
    processing_duration = datetime.now() - processing_start_time

    logging.info(
        f"Completed processing {attachment_count} attachments: "
        f"{successful_count} successful, {attachment_count - successful_count} failed. "
        f"Duration: {processing_duration.total_seconds():.2f}s"
    )

    return processing_results
```

### 3. Use Constants for Magic Numbers

```python
# ✅ GOOD: Constants with descriptive names and documentation
class ProcessingConstants:
    """Constants for invoice processing with business context."""

    # File size limits (in bytes)
    MAX_PDF_SIZE_BYTES = 25 * 1024 * 1024  # 25MB - email attachment limit
    MIN_PDF_SIZE_BYTES = 1024  # 1KB - smaller files likely corrupted

    # Processing timeouts (in seconds)
    PDF_EXTRACTION_TIMEOUT_SECONDS = 30  # Allow 30s for OCR processing
    LLM_REQUEST_TIMEOUT_SECONDS = 60  # OpenAI API can be slow
    TOTAL_PROCESSING_TIMEOUT_SECONDS = 300  # 5 minutes max per invoice

    # Retry configuration
    MAX_RETRY_ATTEMPTS = 3  # Retry up to 3 times for transient errors
    RETRY_BACKOFF_SECONDS = 2  # Start with 2s, then exponential backoff

    # Confidence thresholds
    AUTO_APPROVAL_CONFIDENCE = 0.9  # 90% confidence for auto-approval
    MANUAL_REVIEW_CONFIDENCE = 0.7  # 70% confidence requires review
    REJECTION_CONFIDENCE = 0.5  # Below 50% confidence gets rejected

    # Business limits
    AUTO_APPROVAL_AMOUNT_LIMIT = 10000.00  # $10K limit for auto-approval
    SMALL_INVOICE_AMOUNT = 100.00  # $100 - simplified processing

    # Text processing
    MIN_EXTRACTED_TEXT_LENGTH = 50  # Minimum chars for valid extraction
    MAX_VENDOR_NAME_LENGTH = 100  # Reasonable vendor name limit

def validate_pdf_size(file_size: int) -> bool:
    """Validate PDF file size against business constraints."""
    if file_size < ProcessingConstants.MIN_PDF_SIZE_BYTES:
        logging.warning(f"PDF too small: {file_size} bytes")
        return False

    if file_size > ProcessingConstants.MAX_PDF_SIZE_BYTES:
        logging.warning(f"PDF too large: {file_size / 1024 / 1024:.1f}MB")
        return False

    return True

async def extract_with_timeout(pdf_content: bytes) -> str:
    """Extract text with appropriate timeout."""
    try:
        return await asyncio.wait_for(
            extract_pdf_text(pdf_content),
            timeout=ProcessingConstants.PDF_EXTRACTION_TIMEOUT_SECONDS
        )
    except asyncio.TimeoutError:
        raise ExtractionTimeoutError(
            f"PDF extraction exceeded {ProcessingConstants.PDF_EXTRACTION_TIMEOUT_SECONDS}s limit"
        )

# ❌ BAD: Magic numbers scattered throughout code
async def bad_extract(pdf_content: bytes) -> str:
    if len(pdf_content) < 1024:  # What's special about 1024?
        return ""

    if len(pdf_content) > 26214400:  # What is this number?
        raise ValueError("File too large")

    return await asyncio.wait_for(
        extract_pdf_text(pdf_content),
        timeout=30  # Why 30 seconds?
    )
```

---

## 🧪 Code Quality Through Construction

### 1. Write Code for Readability First

```python
# ✅ GOOD: Optimized for human comprehension
def calculate_invoice_payment_terms(
    invoice_date: date,
    payment_terms_type: str,
    payment_terms_days: int,
    vendor_preferred_terms: Optional[dict] = None
) -> PaymentTermsResult:
    """Calculate payment due date and terms with clear business logic.

    Args:
        invoice_date: Date invoice was issued
        payment_terms_type: Type of payment terms ('net', 'due_on_receipt', etc.)
        payment_terms_days: Number of days for payment (e.g., 30 for Net 30)
        vendor_preferred_terms: Optional vendor-specific payment preferences

    Returns:
        PaymentTermsResult containing due date and payment instructions

    Business Rules:
        - Net terms: Payment due X days from invoice date
        - Due on receipt: Payment due immediately
        - Vendor preferences override standard terms if specified
        - Weekends and holidays extend due date to next business day
    """
    # Step 1: Validate inputs with clear error messages
    if invoice_date > date.today():
        raise ValueError(f"Invoice date {invoice_date} cannot be in the future")

    if payment_terms_days < 0:
        raise ValueError(f"Payment terms days must be non-negative, got {payment_terms_days}")

    # Step 2: Handle vendor-specific preferences
    if vendor_preferred_terms:
        if 'override_terms_days' in vendor_preferred_terms:
            payment_terms_days = vendor_preferred_terms['override_terms_days']
            logging.info(f"Using vendor preferred terms: {payment_terms_days} days")

    # Step 3: Calculate base due date based on terms type
    if payment_terms_type.lower() == 'due_on_receipt':
        base_due_date = invoice_date
        payment_instructions = "Payment due upon receipt"
    elif payment_terms_type.lower().startswith('net'):
        base_due_date = invoice_date + timedelta(days=payment_terms_days)
        payment_instructions = f"Net {payment_terms_days} - Payment due within {payment_terms_days} days"
    else:
        # Default to standard net terms
        base_due_date = invoice_date + timedelta(days=payment_terms_days)
        payment_instructions = f"Payment due within {payment_terms_days} days"

    # Step 4: Adjust for business days (no payments due on weekends)
    adjusted_due_date = adjust_to_next_business_day(base_due_date)

    # Step 5: Calculate days until due (for urgency flagging)
    days_until_due = (adjusted_due_date - date.today()).days
    is_overdue = days_until_due < 0
    is_due_soon = 0 <= days_until_due <= 3

    return PaymentTermsResult(
        due_date=adjusted_due_date,
        payment_instructions=payment_instructions,
        days_until_due=days_until_due,
        is_overdue=is_overdue,
        is_due_soon=is_due_soon,
        original_terms_type=payment_terms_type,
        terms_days=payment_terms_days
    )

def adjust_to_next_business_day(target_date: date) -> date:
    """Move date to next business day if it falls on weekend."""
    # Monday = 0, Sunday = 6
    while target_date.weekday() >= 5:  # Saturday or Sunday
        target_date += timedelta(days=1)
    return target_date

# ❌ BAD: Optimized for brevity at expense of clarity
def calc_terms(d, t, n, v=None):
    if d > date.today(): raise ValueError("bad date")
    if v and 'o' in v: n = v['o']
    dd = d + timedelta(days=n) if t != 'dor' else d
    while dd.weekday() >= 5: dd += timedelta(days=1)
    return dd, (dd - date.today()).days
```

### 2. Minimize Complexity Through Decomposition

```python
# ✅ GOOD: Complex operation broken into clear steps
async def process_invoice_end_to_end(email_message: EmailMessage) -> InvoiceProcessingResult:
    """Process invoice from email to final approval with clear step decomposition."""

    processing_context = ProcessingContext(
        email_id=email_message.id,
        timestamp=datetime.now(),
        step_results={}
    )

    try:
        # Step 1: Extract and validate attachments
        attachments = await extract_invoice_attachments(email_message)
        processing_context.step_results['attachment_extraction'] = {
            'count': len(attachments),
            'types': [a.content_type for a in attachments]
        }

        # Step 2: Convert attachments to text
        text_extractions = await convert_attachments_to_text(attachments)
        processing_context.step_results['text_extraction'] = {
            'successful_count': len([t for t in text_extractions if t.success]),
            'total_chars': sum(len(t.text) for t in text_extractions if t.success)
        }

        # Step 3: Extract structured data using LLM
        structured_data = await extract_structured_invoice_data(text_extractions)
        processing_context.step_results['data_extraction'] = {
            'confidence_score': structured_data.confidence,
            'fields_extracted': list(structured_data.fields.keys())
        }

        # Step 4: Validate business rules
        validation_result = await validate_invoice_business_rules(structured_data)
        processing_context.step_results['validation'] = {
            'is_valid': validation_result.is_valid,
            'error_count': len(validation_result.errors)
        }

        # Step 5: Route for approval based on amount and confidence
        approval_routing = await determine_approval_routing(structured_data, validation_result)
        processing_context.step_results['approval_routing'] = {
            'route': approval_routing.route_type,
            'requires_manual_review': approval_routing.requires_manual_review
        }

        # Step 6: Execute the determined workflow
        final_result = await execute_approval_workflow(
            structured_data,
            approval_routing,
            processing_context
        )

        return InvoiceProcessingResult(
            success=True,
            invoice_data=structured_data,
            approval_result=final_result,
            processing_context=processing_context
        )

    except Exception as e:
        # Log detailed context for debugging
        logging.error(
            f"Invoice processing failed at step: {processing_context.current_step}",
            extra={
                'email_id': email_message.id,
                'step_results': processing_context.step_results,
                'error': str(e),
                'error_type': type(e).__name__
            }
        )

        return InvoiceProcessingResult(
            success=False,
            error_message=str(e),
            processing_context=processing_context
        )

# Each step is a focused, testable function
async def extract_invoice_attachments(email_message: EmailMessage) -> list[Attachment]:
    """Extract and validate invoice attachments from email."""
    # Single responsibility: just handle attachment extraction
    pass

async def convert_attachments_to_text(attachments: list[Attachment]) -> list[TextExtraction]:
    """Convert PDF/image attachments to text."""
    # Single responsibility: just handle text conversion
    pass

# ❌ BAD: Monolithic function doing everything
async def process_invoice_monolith(email):
    # 200+ lines of mixed concerns
    # Extraction, validation, approval, notifications all mixed together
    # Impossible to test individual steps
    # Hard to debug when something fails
    pass
```

---

## 📊 Performance Through Good Construction

### 1. Efficient Resource Management

```python
import asyncio
from contextlib import asynccontextmanager
from typing import AsyncGenerator

class LLMClientPool:
    """Pool of LLM clients for efficient resource utilization."""

    def __init__(self, pool_size: int = 5):
        self.pool_size = pool_size
        self.available_clients: asyncio.Queue = asyncio.Queue(maxsize=pool_size)
        self.total_clients = 0
        self.active_requests = 0

    async def initialize_pool(self) -> None:
        """Initialize the client pool with proper error handling."""
        for i in range(self.pool_size):
            try:
                client = ChatOpenAI(
                    temperature=0,
                    timeout=ProcessingConstants.LLM_REQUEST_TIMEOUT_SECONDS,
                    max_retries=ProcessingConstants.MAX_RETRY_ATTEMPTS
                )
                await self.available_clients.put(client)
                self.total_clients += 1
                logging.debug(f"Initialized LLM client {i+1}/{self.pool_size}")

            except Exception as e:
                logging.error(f"Failed to initialize LLM client {i+1}: {e}")

        if self.total_clients == 0:
            raise RuntimeError("Failed to initialize any LLM clients")

        logging.info(f"LLM client pool initialized with {self.total_clients} clients")

    @asynccontextmanager
    async def get_client(self) -> AsyncGenerator[ChatOpenAI, None]:
        """Get an LLM client from pool with automatic return."""
        # Wait for available client with timeout
        try:
            client = await asyncio.wait_for(
                self.available_clients.get(),
                timeout=30.0  # Don't wait forever
            )
            self.active_requests += 1

            try:
                yield client
            finally:
                # Always return client to pool
                await self.available_clients.put(client)
                self.active_requests -= 1

        except asyncio.TimeoutError:
            raise RuntimeError("No LLM clients available - pool exhausted")

# Usage with automatic resource management
llm_pool = LLMClientPool(pool_size=3)

async def extract_data_with_pooling(text: str) -> dict:
    """Extract data using pooled LLM client."""
    async with llm_pool.get_client() as llm_client:
        # Client automatically returned to pool after use
        response = await llm_client.ainvoke(build_extraction_prompt(text))
        return parse_llm_response(response.content)

# ✅ GOOD: Efficient batch processing
async def process_multiple_invoices_efficiently(invoices: list[dict]) -> list[ProcessingResult]:
    """Process multiple invoices with controlled concurrency."""

    # Limit concurrent processing to prevent resource exhaustion
    semaphore = asyncio.Semaphore(3)  # Max 3 concurrent processing

    async def process_single_with_limit(invoice_data: dict) -> ProcessingResult:
        async with semaphore:
            return await process_single_invoice(invoice_data)

    # Process all invoices concurrently with controlled parallelism
    tasks = [process_single_with_limit(invoice) for invoice in invoices]
    results = await asyncio.gather(*tasks, return_exceptions=True)

    # Handle any exceptions that occurred
    processed_results = []
    for i, result in enumerate(results):
        if isinstance(result, Exception):
            logging.error(f"Invoice {i} processing failed: {result}")
            processed_results.append(ProcessingResult(
                success=False,
                invoice_id=invoices[i].get('id', f'index_{i}'),
                error_message=str(result)
            ))
        else:
            processed_results.append(result)

    return processed_results
```

### 2. Memory-Efficient Processing

```python
def process_large_pdf_streaming(pdf_path: Path) -> Iterator[str]:
    """Process large PDF files without loading entirely into memory."""

    # Process page by page to minimize memory usage
    with open(pdf_path, 'rb') as pdf_file:
        pdf_reader = PyPDF2.PdfReader(pdf_file)
        total_pages = len(pdf_reader.pages)

        logging.info(f"Processing {total_pages} pages from {pdf_path.name}")

        for page_num, page in enumerate(pdf_reader.pages):
            try:
                # Extract text from single page
                page_text = page.extract_text()

                # Clean and validate page text
                if page_text and len(page_text.strip()) > 10:
                    cleaned_text = clean_extracted_text(page_text)
                    yield f"Page {page_num + 1}: {cleaned_text}"

                # Yield control periodically for large documents
                if page_num % 10 == 0:
                    await asyncio.sleep(0)  # Allow other tasks to run

            except Exception as e:
                logging.warning(f"Failed to extract text from page {page_num + 1}: {e}")
                continue

async def extract_from_large_document(pdf_path: Path) -> dict:
    """Extract data from large document using streaming approach."""

    extracted_data = {
        'pages_processed': 0,
        'total_text_length': 0,
        'extracted_fields': {},
        'confidence_scores': []
    }

    # Process pages as stream to avoid memory issues
    for page_text in process_large_pdf_streaming(pdf_path):
        extracted_data['pages_processed'] += 1
        extracted_data['total_text_length'] += len(page_text)

        # Try to extract fields from each page
        page_fields = extract_fields_from_text(page_text)

        # Merge fields with confidence tracking
        for field_name, field_data in page_fields.items():
            if field_name not in extracted_data['extracted_fields']:
                extracted_data['extracted_fields'][field_name] = field_data
                extracted_data['confidence_scores'].append(field_data.get('confidence', 0))

        # Memory management: limit text accumulation
        if extracted_data['total_text_length'] > 100_000:  # 100KB limit
            logging.info("Text limit reached, stopping page processing")
            break

    return extracted_data
```

---

## 📋 Code Construction Checklist

### Pre-Implementation Checklist

**Design Decisions:**

- [ ] Function/class has single, clear responsibility
- [ ] Error handling strategy defined for all failure modes
- [ ] Resource management plan (memory, connections, files)
- [ ] Performance requirements identified and addressed
- [ ] Input validation and output guarantees specified

**Code Structure:**

- [ ] Variable names are self-explanatory and domain-appropriate
- [ ] Constants used for all magic numbers with business context
- [ ] Function length kept under 50 lines (complex functions decomposed)
- [ ] Nesting depth limited to 3 levels maximum
- [ ] All assumptions validated with assertions or checks

### During Implementation Checklist

**Defensive Programming:**

- [ ] All inputs validated at function boundaries
- [ ] Null/None values handled explicitly
- [ ] Error conditions caught at appropriate level
- [ ] Resources properly managed (files, connections, memory)
- [ ] Timeouts specified for all external operations

**Code Quality:**

- [ ] Each function does exactly one thing well
- [ ] Variable scope minimized to smallest necessary level
- [ ] Complex conditions extracted into well-named functions
- [ ] Business rules expressed as clear, testable conditions
- [ ] Logging added for debugging and audit trail

### Post-Implementation Checklist

**Verification:**

- [ ] All code paths tested with unit tests
- [ ] Error handling tested with failure scenarios
- [ ] Performance tested with realistic data volumes
- [ ] Memory usage verified for large inputs
- [ ] Integration tested with real dependencies

**Documentation:**

- [ ] Docstrings explain purpose, args, returns, and business context
- [ ] Complex algorithms documented with step-by-step comments
- [ ] Business rules documented with rationale
- [ ] Error conditions and recovery documented
- [ ] Performance characteristics documented

---

**Remember: Code construction is craftsmanship. Every line should be intentional, every function should be purposeful, and every class should represent a clear concept. Build code that your future self will thank you for! 🔨✨**
