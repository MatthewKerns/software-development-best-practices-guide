# Variable Naming Guide — Code Complete 2 Principles for Python LangGraph

## 📝 Overview

**This guide applies Code Complete 2's systematic approach to variable naming, adapted for our Python LangGraph/LangSmith project.**

Variable names are the most fundamental tool for making code self-documenting. Good names eliminate the need for explanatory comments and make code reviews more effective.

---

## 🎯 Core Naming Principles (Code Complete 2 Foundation)

### 1. Names Should Be Self-Explanatory

```python
# ❌ BAD: Cryptic, requires mental mapping
def process_data(d, t, r):
    if t > 0.7:
        return r.extract(d)
    else:
        return None

# ✅ GOOD: Self-explanatory, no mental mapping needed
def extract_invoice_data(pdf_content: bytes, confidence_threshold: float, extractor_service: InvoiceExtractor):
    if confidence_threshold > 0.7:
        return extractor_service.extract(pdf_content)
    else:
        return None
```

### 2. Use Problem Domain Terminology

```python
# ✅ GOOD: Uses business/domain language
class InvoiceProcessor:
    def __init__(self):
        self.pending_invoices: list[Invoice] = []
        self.processed_invoices: list[Invoice] = []
        self.vendor_lookup: dict[str, Vendor] = {}
        self.accounting_system: AccountingIntegration = None

    def validate_payment_terms(self, invoice: Invoice) -> ValidationResult:
        """Validate payment terms against business rules."""
        payment_due_date = invoice.issue_date + invoice.payment_terms
        current_date = datetime.now().date()

        if payment_due_date < current_date:
            return ValidationResult(
                is_valid=False,
                error_message="Invoice payment deadline has passed",
                requires_manual_review=True
            )
```

### 3. Avoid Mental Mapping and Abbreviations

```python
# ❌ BAD: Requires mental mapping
def calc_amt(inv_data):
    tax_rt = 0.08
    sub_tot = inv_data.get('st', 0)
    return sub_tot * (1 + tax_rt)

# ✅ GOOD: No mental mapping required
def calculate_total_amount(invoice_data: dict) -> float:
    tax_rate = 0.08
    subtotal = invoice_data.get('subtotal', 0)
    return subtotal * (1 + tax_rate)
```

---

## 📊 Variable Naming by Data Type

### Boolean Variables

```python
# ✅ GOOD: Boolean naming patterns
is_invoice_valid: bool = True
has_attachments: bool = False
can_auto_process: bool = True
should_notify_user: bool = False
contains_sensitive_data: bool = True

# Business context booleans
requires_manual_review: bool = False
exceeds_approval_threshold: bool = True
matches_purchase_order: bool = False

# Status flags
is_processing_complete: bool = False
has_extraction_errors: bool = True
is_vendor_approved: bool = True

# ❌ BAD: Unclear boolean meanings
flag: bool = True
status: bool = False
check: bool = True
```

### Collections and Containers

```python
# ✅ GOOD: Descriptive collection names
pending_invoice_queue: Queue[Invoice] = Queue()
processed_invoices_by_vendor: dict[str, list[Invoice]] = {}
failed_extraction_attempts: list[ExtractionAttempt] = []
vendor_approval_cache: dict[str, ApprovalStatus] = {}

# Business domain collections
accounts_payable_items: list[PayableItem] = []
expense_categories: set[str] = set()
audit_trail_entries: list[AuditEntry] = []

# ❌ BAD: Generic collection names
items: list = []
data: dict = {}
results: list = []
cache: dict = {}
```

### Numeric Variables

```python
# ✅ GOOD: Descriptive numeric names with units
invoice_amount_usd: float = 1234.56
processing_timeout_seconds: int = 30
retry_attempt_count: int = 0
confidence_score_percentage: float = 87.5
max_file_size_bytes: int = 25 * 1024 * 1024

# Business metrics
monthly_processing_volume: int = 1500
average_extraction_time_ms: float = 250.0
approval_threshold_dollars: float = 10000.00

# ❌ BAD: Ambiguous numeric names
amount: float = 1234.56  # What currency? What type of amount?
timeout: int = 30        # Seconds? Minutes? Milliseconds?
count: int = 5           # Count of what?
threshold: float = 0.8   # Threshold for what? What scale?
```

### String Variables

```python
# ✅ GOOD: Descriptive string names
vendor_company_name: str = "ACME Corporation"
invoice_number_formatted: str = "INV-2025-001234"
error_message_for_user: str = "Invoice validation failed"
email_subject_line: str = "Invoice Processing Complete"
file_path_absolute: str = "/path/to/invoice.pdf"

# Business context strings
purchase_order_reference: str = "PO-2025-5678"
accounting_code_string: str = "4000-OFFICE-SUPPLIES"
vendor_tax_id_number: str = "12-3456789"

# ❌ BAD: Generic string names
text: str = "some content"
message: str = "error occurred"
path: str = "/some/path"
code: str = "ABC123"
```

---

## 🔧 Function and Method Naming

### Action-Oriented Function Names

```python
# ✅ GOOD: Clear action verbs with specific objects
def extract_invoice_data_from_pdf(pdf_bytes: bytes) -> InvoiceData:
    """Extract structured invoice data from PDF content."""

def validate_vendor_tax_information(vendor: Vendor) -> ValidationResult:
    """Validate vendor tax ID and registration status."""

def send_processing_completion_notification(invoice: Invoice, recipient: str) -> bool:
    """Send email notification when invoice processing completes."""

def calculate_payment_due_date(invoice_date: date, payment_terms_days: int) -> date:
    """Calculate when payment is due based on invoice date and terms."""

# ❌ BAD: Vague action names
def process(data):
    """What kind of processing? What data?"""

def handle(item):
    """Handle how? What kind of item?"""

def do_stuff(thing):
    """Completely uninformative"""
```

### Query/Check Function Names

```python
# ✅ GOOD: Question-form function names
def is_invoice_number_duplicate(invoice_number: str, existing_invoices: list[str]) -> bool:
    """Check if invoice number already exists in system."""

def has_required_attachments(email_message: EmailMessage) -> bool:
    """Verify email contains expected invoice attachments."""

def can_auto_approve_payment(invoice: Invoice, approval_rules: ApprovalRules) -> bool:
    """Determine if invoice qualifies for automatic approval."""

def does_vendor_require_special_handling(vendor_code: str) -> bool:
    """Check if vendor has special processing requirements."""

# ❌ BAD: Unclear query names
def check_invoice(invoice):
    """Check what about the invoice?"""

def validate(data):
    """Validate what? Return what?"""
```

---

## 🏗️ Class and Module Naming

### Class Naming Conventions

```python
# ✅ GOOD: Noun-based class names representing concepts
class InvoiceDataExtractor:
    """Extracts structured data from invoice documents."""

class VendorValidationService:
    """Handles vendor information validation and verification."""

class PaymentApprovalWorkflow:
    """Manages the approval process for invoice payments."""

class EmailAttachmentProcessor:
    """Processes attachments from incoming emails."""

# Business domain classes
class AccountsPayableEntry:
    """Represents a single accounts payable transaction."""

class ExpenseCategory:
    """Categorizes expenses for accounting purposes."""

class AuditTrailRecorder:
    """Records audit trail events for compliance."""

# ❌ BAD: Vague class names
class Processor:
    """Processes what?"""

class Handler:
    """Handles what?"""

class Manager:
    """Manages what?"""

class Service:
    """Too generic - what service?"""
```

### Module and Package Naming

```python
# ✅ GOOD: Module organization with clear purposes
src/
├── invoice_processing/          # Main business domain
│   ├── extraction/             # Data extraction services
│   │   ├── pdf_extractor.py   # PDF-specific extraction
│   │   ├── ocr_processor.py   # OCR text processing
│   │   └── llm_enhancer.py    # LLM-based enhancement
│   ├── validation/             # Business rule validation
│   │   ├── vendor_validator.py
│   │   ├── amount_validator.py
│   │   └── date_validator.py
│   └── workflow/               # Process orchestration
│       ├── approval_workflow.py
│       └── notification_workflow.py
├── integrations/               # External system interfaces
│   ├── gmail_client.py
│   ├── sheets_client.py
│   └── accounting_system.py
└── utilities/                  # Cross-cutting concerns
    ├── logging_config.py
    ├── error_handlers.py
    └── performance_monitors.py

# ❌ BAD: Generic module names
src/
├── utils.py                    # Too generic
├── helpers.py                  # What kind of help?
├── misc.py                     # Miscellaneous is a code smell
└── stuff.py                    # Meaningless
```

---

## 🎯 Domain-Specific Naming Patterns

### LangGraph Node Naming

```python
# ✅ GOOD: LangGraph node naming with clear purpose
async def email_intake_and_parsing_node(state: WorkflowState) -> WorkflowState:
    """Parse incoming emails and extract invoice attachments."""

async def pdf_text_extraction_node(state: WorkflowState) -> WorkflowState:
    """Extract text content from PDF attachments using OCR."""

async def llm_data_structuring_node(state: WorkflowState) -> WorkflowState:
    """Use LLM to extract structured data from unstructured text."""

async def business_rule_validation_node(state: WorkflowState) -> WorkflowState:
    """Apply business rules to validate extracted invoice data."""

async def approval_routing_decision_node(state: WorkflowState) -> WorkflowState:
    """Route invoices to appropriate approval workflow based on amount."""

# ❌ BAD: Generic node names
async def process_email_node(state):
    """Too vague - process how?"""

async def llm_node(state):
    """What does the LLM do?"""

async def validation_node(state):
    """Validate what?"""
```

### Thread ID Naming (Critical for Multi-Threading Systems)

**Context**: In systems with multiple threading concepts (LangGraph workflows, Python threads, database connections, email threads), clear naming prevents confusion and bugs.

```python
# ✅ EXCELLENT: Domain-specific thread ID naming
def process_workflow_step(state: WorkflowState, config: RunnableConfig):
    # Extract LangGraph-specific thread ID for workflow resumption
    langgraph_thread_id = config.get("configurable", {}).get("thread_id", "unknown")

    # Use Gmail email ID for email tracking (NOT for workflow resumption)
    gmail_email_id = state.get("current_email_id")  # Format: "1989befbcac781be"

    # Email system thread (if tracking email conversations)
    email_system_thread_id = None  # Set by email service if needed

    # Database operation with clear context
    await store_invoice_data(
        invoice_number=invoice_number,
        workflow_thread_id=langgraph_thread_id,  # For workflow tracking
        email_reference_id=gmail_email_id        # For email correlation
    )

# ❌ DANGEROUS: Ambiguous thread naming that causes bugs
def process_workflow_step(state, config):
    # WRONG: Using email ID as thread ID breaks workflow resumption
    thread_id = state.get("current_email_id")  # This is NOT a UUID!

    # CONFUSING: What kind of thread?
    thread = get_thread_id()  # Python thread? LangGraph? Email?

    # BROKEN: Non-UUID thread ID breaks resumption
    await workflow.resume(thread_id=thread_id)  # FAILS - not proper UUID
```

### Real-World Thread ID Example from Our Codebase

```python
# ✅ PRODUCTION EXAMPLE: Clear separation of concerns
class WorkflowStep:
    async def send_analysis_email(self, state: WorkflowState, config: RunnableConfig):
        # LangGraph thread ID - MUST be UUID for resumption
        langgraph_thread_id = config.get("configurable", {}).get("thread_id", "unknown")

        # Gmail email ID - for email correlation (not workflow resumption)
        gmail_email_id = state.get("current_email_id")  # e.g., "1989befbcac781be"

        # Validate UUID format for resumption capability
        if len(langgraph_thread_id) != 36 or langgraph_thread_id.count('-') != 4:
            logger.warning(f"⚠️ Invalid UUID format: {langgraph_thread_id}")
            logger.warning("This may break workflow resumption functionality")

        # Use appropriate ID for each context
        await email_service.send_notification(
            email_reference=gmail_email_id,      # For Gmail API
            workflow_thread=langgraph_thread_id  # For LangGraph tracking
        )
```

### Error and Exception Naming

```python
# ✅ GOOD: Specific error classes with clear meaning
class InvoiceExtractionTimeoutError(Exception):
    """Raised when invoice data extraction exceeds time limit."""

class VendorNotFoundError(ValueError):
    """Raised when vendor lookup fails to find matching vendor."""

class InvalidInvoiceFormatError(ValueError):
    """Raised when invoice format doesn't match expected structure."""

class PaymentApprovalRequiredError(Exception):
    """Raised when invoice requires manual approval workflow."""

class DuplicateInvoiceNumberError(ValueError):
    """Raised when invoice number already exists in system."""

# ❌ BAD: Generic error names
class ProcessingError(Exception):
    """What kind of processing failed?"""

class DataError(Exception):
    """What's wrong with the data?"""

class SystemError(Exception):
    """Too generic - what system issue?"""
```

---

## 📏 Naming Length Guidelines

### The "Goldilocks Principle" for Name Length

```python
# ❌ TOO SHORT: Cryptic abbreviations
def proc_inv(d):
    amt = d.get('a', 0)
    vnd = d.get('v', '')
    return calc_tax(amt, vnd)

# ❌ TOO LONG: Unnecessarily verbose
def process_incoming_invoice_document_by_extracting_data_and_validating_business_rules(invoice_document_data):
    total_amount_including_taxes_and_fees = invoice_document_data.get('total_amount', 0)
    vendor_company_name_from_invoice_header = invoice_document_data.get('vendor_name', '')
    return calculate_tax_amount_based_on_vendor_location(total_amount_including_taxes_and_fees, vendor_company_name_from_invoice_header)

# ✅ JUST RIGHT: Descriptive but concise
def process_invoice_extraction(invoice_data: dict) -> ProcessingResult:
    total_amount = invoice_data.get('total_amount', 0)
    vendor_name = invoice_data.get('vendor_name', '')
    return calculate_vendor_tax(total_amount, vendor_name)
```

### Context-Dependent Length

```python
# ✅ GOOD: Shorter names in smaller scopes
def calculate_tax(amount: float, rate: float) -> float:
    # In a small function, 'amount' and 'rate' are clear enough
    return amount * rate

# ✅ GOOD: Longer names in larger scopes
class InvoiceProcessingWorkflow:
    def __init__(self):
        self.invoice_data_extractor = InvoiceDataExtractor()
        self.vendor_validation_service = VendorValidationService()
        self.payment_approval_engine = PaymentApprovalEngine()
        # Longer names needed for class-level scope
```

---

## 🧪 Testing Variable Names

### Test Function Naming

```python
# ✅ GOOD: Test names that read like specifications
class TestInvoiceValidation:
    def test_invoice_with_valid_data_passes_validation(self):
        """Test Given: valid invoice data, When: validated, Then: passes."""

    def test_invoice_with_negative_amount_fails_validation(self):
        """Test Given: negative amount, When: validated, Then: fails with amount error."""

    def test_invoice_with_future_date_fails_validation(self):
        """Test Given: future invoice date, When: validated, Then: fails with date error."""

    def test_invoice_with_unknown_vendor_requires_manual_review(self):
        """Test Given: unknown vendor, When: validated, Then: requires manual review."""

# Test fixture naming
@pytest.fixture
def valid_invoice_data() -> dict:
    """Provides complete, valid invoice data for testing."""
    return {
        'invoice_number': 'INV-2025-001',
        'vendor_name': 'ACME Corporation',
        'total_amount': 1234.56,
        'invoice_date': '2025-01-15'
    }

@pytest.fixture
def corrupted_pdf_bytes() -> bytes:
    """Provides corrupted PDF content for error testing."""
    return b'\x25\x50\x44\x46corrupted_content'
```

---

## 📋 Naming Checklists

### Before Committing Code - Name Review Checklist

**For Variables:**

- [ ] Name clearly indicates what the variable contains
- [ ] Units are specified for numeric values (seconds, bytes, etc.)
- [ ] Boolean variables use is/has/can/should prefixes
- [ ] Collections indicate what they contain (not just "list" or "dict")
- [ ] No mental mapping required to understand purpose

**For Functions:**

- [ ] Function name clearly states what action it performs
- [ ] Parameters have descriptive names that indicate their purpose
- [ ] Return value purpose is clear from function name
- [ ] Query functions use question form (is/has/can/does)
- [ ] Action functions use imperative verbs

**For Classes:**

- [ ] Class name represents a clear concept or entity
- [ ] Follows noun-based naming convention
- [ ] Clearly indicates the class's responsibility
- [ ] Distinguishable from similar classes in the system

**For Tests:**

- [ ] Test name describes the scenario being tested
- [ ] Follows Given/When/Then pattern in name or docstring
- [ ] Specific enough to understand failure without reading code
- [ ] Fixture names indicate what they provide

---

## 🎯 Code Complete 2 Naming Anti-Patterns to Avoid

### The "Mental Mapping" Anti-Pattern

```python
# ❌ BAD: Requires constant mental mapping
def process_data(d, c, t):
    # Developer must remember: d=data, c=config, t=threshold
    if d.confidence > t:
        return c.extractor.extract(d.content)
    return None

# ✅ GOOD: Self-explanatory, no mapping needed
def extract_high_confidence_data(invoice_data: InvoiceData,
                                extractor_config: ExtractorConfig,
                                confidence_threshold: float):
    if invoice_data.confidence > confidence_threshold:
        return extractor_config.extractor.extract(invoice_data.content)
    return None
```

### The "Misleading Name" Anti-Pattern

```python
# ❌ BAD: Name suggests different purpose than implementation
def get_user_data(user_id: str) -> dict:
    # Actually modifies user data and sends emails!
    user = database.fetch_user(user_id)
    user.last_accessed = datetime.now()
    database.update_user(user)
    send_welcome_email(user.email)
    return user.to_dict()

# ✅ GOOD: Name accurately reflects all actions
def fetch_user_and_update_access_time(user_id: str) -> dict:
    """Fetch user data, update last access time, and send welcome email if needed."""
    user = database.fetch_user(user_id)
    user.last_accessed = datetime.now()
    database.update_user(user)

    if should_send_welcome_email(user):
        send_welcome_email(user.email)

    return user.to_dict()
```

### The "Noise Word" Anti-Pattern

```python
# ❌ BAD: Noise words that add no information
invoice_data_info = {}          # "info" adds nothing
user_data_object = User()       # "object" is redundant
process_data_manager = ProcessManager()  # "data" and "manager" are noise

# ✅ GOOD: Meaningful, concise names
invoice_details = {}
user = User()
invoice_processor = InvoiceProcessor()
```

---

**Remember: Names are the foundation of self-documenting code. Invest time in choosing names that eliminate the need for explanatory comments and make your code immediately understandable to any developer! 📝✨**
