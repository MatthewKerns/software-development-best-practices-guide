# Working with Strings Guide — Python LangGraph/LangSmith Project

## 📋 Overview

**This guide provides comprehensive standards for string handling, constants management, string operations, and regex patterns in our Python LangGraph project.**

String operations are critical in this project for:

- Processing email content and attachments
- Extracting structured data from unstructured text
- Validating and normalizing user inputs
- Building prompts for LLM interactions
- Handling API responses and error messages

---

## 📝 String Constants Management

### 1. Constants Organization Standards

#### **File Structure for Constants**

```python
# src/constants/
├── __init__.py
├── strings.py          # User-facing messages, templates
├── patterns.py         # Regex patterns and validation rules
├── formats.py          # Date/currency/number format strings
├── prompts.py          # LLM prompt templates
└── validation.py       # Validation error messages
```

#### **Constants Naming Conventions**

```python
# ✅ GOOD: Descriptive, hierarchical naming
class EmailConstants:
    """Email processing string constants."""

    # Error messages - use SCREAMING_SNAKE_CASE
    ERROR_INVALID_EMAIL_FORMAT = "Invalid email format: {email}"
    ERROR_ATTACHMENT_TOO_LARGE = "Attachment exceeds {max_size}MB limit"
    ERROR_UNSUPPORTED_FORMAT = "Unsupported attachment format: {format}"

    # Template strings - use SCREAMING_SNAKE_CASE
    SUBJECT_INVOICE_PROCESSED = "Invoice {invoice_id} processed successfully"
    BODY_EXTRACTION_FAILED = "Failed to extract data from {filename}: {reason}"

    # Validation patterns - group by domain
    PATTERN_EMAIL_VALIDATION = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    PATTERN_INVOICE_NUMBER = r'^[A-Z]{2,3}-\d{4,8}$'

    # Format strings - descriptive prefixes
    FORMAT_CURRENCY_USD = "${:,.2f}"
    FORMAT_DATE_ISO = "%Y-%m-%d"
    FORMAT_TIMESTAMP_LOG = "%Y-%m-%d %H:%M:%S"

# ❌ BAD: Vague, inconsistent naming
INVALID_EMAIL = "bad email"  # Too vague
ERR_MSG_1 = "Something went wrong"  # Non-descriptive
email_pattern = r'.*@.*'  # Inconsistent case, too permissive
```

### 2. When to Use Constants vs. Inline Strings

#### **✅ ALWAYS Use Constants For:**

```python
# User-facing messages (for internationalization/consistency)
ERROR_MESSAGES = {
    'validation_failed': "Document validation failed: {details}",
    'extraction_timeout': "Text extraction timed out after {seconds}s",
    'api_rate_limit': "API rate limit exceeded. Retry in {seconds}s"
}

# Regex patterns (for reusability and testing)
class ValidationPatterns:
    EMAIL = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    PHONE_US = r'^\+?1?[-.\s]?\(?([0-9]{3})\)?[-.\s]?([0-9]{3})[-.\s]?([0-9]{4})$'
    INVOICE_ID = r'^INV-\d{6,10}$'

# Configuration values
class ProcessingConfig:
    MAX_FILE_SIZE_MB = 25
    MAX_EXTRACTION_TIME_SECONDS = 30
    DEFAULT_RETRY_ATTEMPTS = 3

# LLM prompt templates
class PromptTemplates:
    EXTRACT_INVOICE_DATA = """
    Extract structured data from this invoice text:

    {invoice_text}

    Return JSON with fields: invoice_number, vendor, amount, date, line_items
    """
```

#### **✅ Acceptable Inline Strings:**

```python
# Simple debugging/logging (not user-facing)
logger.debug("Starting invoice extraction")
logger.info("Processing complete")

# Short, obvious string operations
filename = path.stem.lower()
extension = path.suffix.upper()

# Mathematical/technical constants that won't change
precision = 2  # decimal places for currency
buffer_size = 8192  # bytes
```

### 3. Constants Documentation Standards

```python
class InvoiceExtractionConstants:
    """String constants for invoice data extraction.

    This module centralizes all string literals used in the invoice
    processing workflow to ensure consistency and enable easy
    internationalization.

    Business Context:
    - Error messages must be user-friendly for accounting team
    - Validation patterns based on vendor requirements analysis
    - Prompt templates optimized for GPT-4 accuracy
    """

    # Validation error messages - returned to users
    ERROR_INVALID_AMOUNT = (
        "Invoice amount '{amount}' is invalid. "
        "Expected positive number with up to 2 decimal places."
    )
    # Business rule: Based on accounting team feedback that they need
    # specific guidance on what format is expected

    ERROR_FUTURE_DATE = (
        "Invoice date '{date}' cannot be in the future. "
        "Please verify the date and resubmit."
    )
    # Business rule: Future dates indicate data entry errors

    # Regex patterns - validated against production data samples
    PATTERN_INVOICE_AMOUNT = r'^\d{1,8}(\.\d{1,2})?$'
    # Supports amounts from $0.01 to $99,999,999.99
    # Based on analysis of 10K+ invoices in production

    PATTERN_VENDOR_CODE = r'^[A-Z]{2,4}-\d{3,6}$'
    # Format: 2-4 letter prefix, dash, 3-6 digits
    # Examples: ABC-123, CORP-456789
```

---

## 🔧 String Operations Guidelines

### 1. String Manipulation Best Practices

#### **Prefer f-strings for Formatting (Modern Python)**

```python
# ✅ GOOD: f-strings for readability and performance
def format_invoice_summary(invoice_id: str, amount: float, vendor: str) -> str:
    """Format invoice summary for display."""
    return f"Invoice {invoice_id}: ${amount:,.2f} from {vendor}"

def log_processing_status(count: int, duration: float) -> None:
    """Log processing completion status."""
    logger.info(f"Processed {count} invoices in {duration:.2f}s")

# ✅ GOOD: f-strings with expressions
def validate_file_size(size_bytes: int) -> str:
    """Generate file size validation message."""
    size_mb = size_bytes / (1024 * 1024)
    return f"File size: {size_mb:.1f}MB {'(within limit)' if size_mb <= 25 else '(exceeds limit)'}"
```

#### **Use .format() for Complex Templates**

```python
# ✅ GOOD: .format() for complex, reusable templates
class EmailTemplates:
    INVOICE_PROCESSED = """
    Dear {recipient_name},

    Your invoice has been processed successfully:

    Invoice ID: {invoice_id}
    Vendor: {vendor_name}
    Amount: {amount}
    Processing Date: {processed_date}

    {additional_notes}

    Best regards,
    Automated Invoice System
    """

def send_confirmation_email(invoice_data: dict) -> str:
    """Generate confirmation email body."""
    return EmailTemplates.INVOICE_PROCESSED.format(
        recipient_name=invoice_data['recipient'],
        invoice_id=invoice_data['id'],
        vendor_name=invoice_data['vendor'],
        amount=f"${invoice_data['amount']:,.2f}",
        processed_date=invoice_data['processed_at'].strftime('%Y-%m-%d'),
        additional_notes=invoice_data.get('notes', 'No additional notes.')
    )
```

#### **String Validation and Sanitization**

```python
def sanitize_filename(filename: str) -> str:
    """Sanitize filename for safe file system operations.

    Business context: User-uploaded files may contain unsafe characters
    that could cause security issues or file system errors.
    """
    # Remove/replace unsafe characters
    safe_chars = re.sub(r'[<>:"/\\|?*]', '_', filename)

    # Limit length to prevent path issues
    max_length = 255
    if len(safe_chars) > max_length:
        name, ext = os.path.splitext(safe_chars)
        safe_chars = name[:max_length - len(ext)] + ext

    # Ensure not empty after sanitization
    return safe_chars if safe_chars.strip() else "document"

def normalize_vendor_name(name: str) -> str:
    """Normalize vendor names for consistent processing.

    Business rule: Vendor names should be consistent across invoices
    to enable proper grouping and reporting.
    """
    # Basic cleaning
    normalized = name.strip().upper()

    # Remove common business suffixes for grouping
    suffixes = ['INC', 'LLC', 'LTD', 'CORP', 'CO']
    for suffix in suffixes:
        pattern = rf'\b{suffix}\.?\s*$'
        normalized = re.sub(pattern, '', normalized)

    # Normalize whitespace
    normalized = re.sub(r'\s+', ' ', normalized).strip()

    return normalized
```

#### **String Comparison Standards**

```python
def is_invoice_duplicate(new_invoice: str, existing_invoices: list[str]) -> bool:
    """Check if invoice number already exists.

    Business rule: Case-insensitive comparison prevents duplicate processing
    of invoices with inconsistent capitalization.
    """
    # Case-insensitive comparison
    new_invoice_normalized = new_invoice.strip().upper()
    existing_normalized = [inv.strip().upper() for inv in existing_invoices]

    return new_invoice_normalized in existing_normalized

def fuzzy_vendor_match(input_vendor: str, known_vendors: list[str], threshold: float = 0.8) -> str | None:
    """Find best matching vendor using fuzzy string matching.

    Business context: OCR and manual entry often introduce small typos
    in vendor names. Fuzzy matching helps maintain data consistency.
    """
    from difflib import SequenceMatcher

    input_normalized = normalize_vendor_name(input_vendor)
    best_match = None
    best_ratio = 0.0

    for vendor in known_vendors:
        vendor_normalized = normalize_vendor_name(vendor)
        ratio = SequenceMatcher(None, input_normalized, vendor_normalized).ratio()

        if ratio > best_ratio and ratio >= threshold:
            best_ratio = ratio
            best_match = vendor

    return best_match
```

### 2. Performance Considerations

#### **Efficient String Operations**

```python
# ✅ GOOD: Use join() for multiple concatenations
def build_search_query(terms: list[str]) -> str:
    """Build Gmail search query from terms."""
    # Efficient for multiple strings
    return ' AND '.join(f'"{term}"' for term in terms if term.strip())

# ❌ BAD: Multiple concatenations in loop
def build_query_bad(terms: list[str]) -> str:
    query = ""
    for term in terms:
        query += f' AND "{term}"'  # Creates new string each iteration
    return query.strip()

# ✅ GOOD: Use list comprehension + join for filtering
def format_invoice_lines(lines: list[dict]) -> str:
    """Format invoice line items for display."""
    formatted_lines = [
        f"  {line['description']}: ${line['amount']:.2f}"
        for line in lines
        if line['amount'] > 0  # Filter invalid amounts
    ]
    return '\n'.join(formatted_lines)

# ✅ GOOD: Use str.replace() for simple substitutions
def clean_extracted_text(text: str) -> str:
    """Clean common OCR artifacts from extracted text."""
    # Chain simple replacements for readability
    return (text
            .replace('\x00', '')  # Remove null bytes
            .replace('\r\n', '\n')  # Normalize line endings
            .replace('\r', '\n')
            .strip())
```

#### **Memory-Efficient String Processing**

```python
def process_large_text_file(file_path: Path) -> Iterator[str]:
    """Process large text files line by line to avoid memory issues.

    Business context: Invoice text files can be very large (OCR output).
    Generator pattern prevents loading entire file into memory.
    """
    with open(file_path, 'r', encoding='utf-8') as file:
        for line_num, line in enumerate(file, 1):
            # Clean and validate each line
            cleaned_line = line.strip()
            if cleaned_line and len(cleaned_line) > 3:  # Skip empty/short lines
                yield f"Line {line_num}: {cleaned_line}"

def extract_invoice_fields_streaming(text_lines: Iterator[str]) -> dict:
    """Extract fields from streaming text to handle large documents."""
    invoice_data = {'lines': [], 'total_lines': 0}

    for line in text_lines:
        invoice_data['total_lines'] += 1

        # Process line by line instead of loading all text
        if 'TOTAL:' in line.upper():
            amount_match = re.search(r'\$?(\d+(?:,\d{3})*(?:\.\d{2})?)', line)
            if amount_match:
                invoice_data['total_amount'] = amount_match.group(1)

        # Yield control periodically for large files
        if invoice_data['total_lines'] % 1000 == 0:
            logger.debug(f"Processed {invoice_data['total_lines']} lines...")

    return invoice_data
```

---

## 🎯 Regular Expressions Guidelines

### 1. Regex Pattern Standards

#### **Pattern Organization and Documentation**

```python
class ValidationPatterns:
    """Centralized regex patterns for data validation.

    All patterns are compiled for performance and thoroughly tested
    against production data samples.
    """

    # Email validation - RFC 5322 compliant subset
    EMAIL = re.compile(
        r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$',
        re.IGNORECASE
    )
    # Business rule: Simplified pattern for business email validation
    # Rejects obviously invalid emails while accepting common formats

    # Invoice number patterns by vendor
    INVOICE_ACME_CORP = re.compile(r'^ACME-\d{6}$')  # ACME-123456
    INVOICE_GENERIC = re.compile(r'^[A-Z]{2,4}-\d{4,8}$')  # ABC-1234

    # Currency amounts - supports various formats
    CURRENCY_AMOUNT = re.compile(
        r'^\$?(\d{1,3}(?:,\d{3})*(?:\.\d{2})?)$',
        re.IGNORECASE
    )
    # Matches: $1,234.56, 1234.56, $1234, 1,234

    # Date patterns - multiple formats
    DATE_MMDDYYYY = re.compile(r'^(0[1-9]|1[0-2])/(0[1-9]|[12]\d|3[01])/(\d{4})$')
    DATE_YYYY_MM_DD = re.compile(r'^(\d{4})-(0[1-9]|1[0-2])-(0[1-9]|[12]\d|3[01])$')

    # Phone numbers - US format variations
    PHONE_US = re.compile(
        r'^\+?1?[-.\s]?\(?([0-9]{3})\)?[-.\s]?([0-9]{3})[-.\s]?([0-9]{4})$'
    )
    # Matches: (555) 123-4567, 555-123-4567, +1-555-123-4567, etc.

class ExtractionPatterns:
    """Regex patterns for extracting data from unstructured text."""

    # Invoice total extraction - handles various formats
    TOTAL_AMOUNT = re.compile(
        r'(?:total|amount\s+due|balance\s+due):?\s*\$?(\d{1,8}(?:,\d{3})*(?:\.\d{2})?)',
        re.IGNORECASE | re.MULTILINE
    )

    # Vendor name extraction - from various contexts
    VENDOR_NAME = re.compile(
        r'(?:from|vendor|bill\s+to|sold\s+by):?\s*([A-Za-z][A-Za-z\s&,.'-]{2,50})',
        re.IGNORECASE
    )

    # PO number extraction
    PO_NUMBER = re.compile(
        r'(?:po|purchase\s+order)(?:\s+#?|\s*number\s*#?):\s*([A-Z0-9-]{3,20})',
        re.IGNORECASE
    )
```

#### **Regex Best Practices**

```python
def extract_invoice_data(text: str) -> dict:
    """Extract structured data from invoice text using regex patterns.

    Returns comprehensive extraction results with confidence indicators.
    """
    extracted_data = {}

    # ✅ GOOD: Use compiled patterns for performance
    total_match = ExtractionPatterns.TOTAL_AMOUNT.search(text)
    if total_match:
        # Clean and validate extracted amount
        amount_str = total_match.group(1).replace(',', '')
        try:
            extracted_data['total_amount'] = float(amount_str)
            extracted_data['total_confidence'] = 'high'
        except ValueError:
            extracted_data['total_confidence'] = 'low'
            logger.warning(f"Could not parse amount: {amount_str}")

    # ✅ GOOD: Use named groups for clarity
    vendor_pattern = re.compile(
        r'(?:vendor|from):\s*(?P<vendor_name>[A-Za-z][A-Za-z\s&,.'-]{2,50})',
        re.IGNORECASE
    )
    vendor_match = vendor_pattern.search(text)
    if vendor_match:
        extracted_data['vendor'] = vendor_match.group('vendor_name').strip()

    # ✅ GOOD: Handle multiple matches appropriately
    line_items = []
    line_pattern = re.compile(
        r'(\d+)\s+([A-Za-z][A-Za-z\s]{2,30})\s+\$?(\d+(?:\.\d{2})?)',
        re.MULTILINE
    )
    for match in line_pattern.finditer(text):
        quantity, description, price = match.groups()
        line_items.append({
            'quantity': int(quantity),
            'description': description.strip(),
            'price': float(price)
        })
    extracted_data['line_items'] = line_items

    return extracted_data

def validate_with_regex(value: str, pattern: re.Pattern, field_name: str) -> dict:
    """Validate a value against a regex pattern with detailed feedback.

    Returns validation result with actionable error messages.
    """
    if not isinstance(value, str):
        return {
            'is_valid': False,
            'error': f"{field_name} must be a string, got {type(value).__name__}",
            'value': value
        }

    match = pattern.fullmatch(value.strip())
    if match:
        return {
            'is_valid': True,
            'normalized_value': match.group(0),
            'groups': match.groups() if match.groups() else None
        }
    else:
        return {
            'is_valid': False,
            'error': f"{field_name} format is invalid: '{value}'",
            'pattern': pattern.pattern,
            'value': value
        }

# Example usage with comprehensive validation
def validate_invoice_number(invoice_num: str) -> dict:
    """Validate invoice number format with business-specific rules."""
    # First, try vendor-specific patterns
    if invoice_num.startswith('ACME-'):
        return validate_with_regex(
            invoice_num,
            ValidationPatterns.INVOICE_ACME_CORP,
            'ACME invoice number'
        )

    # Fall back to generic pattern
    return validate_with_regex(
        invoice_num,
        ValidationPatterns.INVOICE_GENERIC,
        'invoice number'
    )
```

### 2. Common Regex Patterns for This Project

#### **Email and Document Processing Patterns**

```python
class DocumentPatterns:
    """Regex patterns specific to document processing workflows."""

    # Email subject line patterns
    INVOICE_SUBJECT = re.compile(
        r'(?:invoice|bill|statement).*?(?:INV-?(\d+)|#(\d+))',
        re.IGNORECASE
    )

    RECEIPT_SUBJECT = re.compile(
        r'(?:receipt|purchase).*?(?:from\s+([A-Za-z\s&]+))',
        re.IGNORECASE
    )

    # File attachment patterns
    PDF_FILENAME = re.compile(
        r'^(.+)\.pdf$',
        re.IGNORECASE
    )

    IMAGE_FILENAME = re.compile(
        r'^(.+)\.(jpg|jpeg|png|gif|bmp|tiff)$',
        re.IGNORECASE
    )

    # Document content extraction
    DATE_IN_TEXT = re.compile(
        r'\b((?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\.?\s+\d{1,2},?\s+\d{4})\b',
        re.IGNORECASE
    )

    MONEY_AMOUNT = re.compile(
        r'\$(\d{1,3}(?:,\d{3})*(?:\.\d{2})?)',
        re.MULTILINE
    )

    # Tax ID and business numbers
    EIN_NUMBER = re.compile(r'\b\d{2}-\d{7}\b')  # XX-XXXXXXX
    SSN_NUMBER = re.compile(r'\b\d{3}-\d{2}-\d{4}\b')  # XXX-XX-XXXX
```

#### **LLM Prompt Processing Patterns**

````python
class PromptPatterns:
    """Patterns for processing LLM inputs and outputs."""

    # JSON extraction from LLM responses
    JSON_BLOCK = re.compile(
        r'```(?:json)?\s*(\{.*?\})\s*```',
        re.DOTALL | re.IGNORECASE
    )

    # Confidence score extraction
    CONFIDENCE_SCORE = re.compile(
        r'(?:confidence|certainty):\s*(\d+(?:\.\d+)?)\s*[%]?',
        re.IGNORECASE
    )

    # Field extraction from structured responses
    FIELD_VALUE_PAIR = re.compile(
        r'([A-Za-z_]+):\s*([^\n]+)',
        re.MULTILINE
    )

def extract_llm_json_response(response_text: str) -> dict:
    """Extract JSON from LLM response with fallback parsing.

    Business context: LLMs sometimes return JSON wrapped in markdown
    or with additional text. This handles common response formats.
    """
    # Try to extract JSON from code blocks first
    json_match = PromptPatterns.JSON_BLOCK.search(response_text)
    if json_match:
        try:
            return json.loads(json_match.group(1))
        except json.JSONDecodeError as e:
            logger.warning(f"Invalid JSON in code block: {e}")

    # Fallback: try to find JSON-like structure
    json_start = response_text.find('{')
    json_end = response_text.rfind('}')
    if json_start != -1 and json_end > json_start:
        try:
            return json.loads(response_text[json_start:json_end + 1])
        except json.JSONDecodeError:
            pass

    # Final fallback: extract field-value pairs
    pairs = PromptPatterns.FIELD_VALUE_PAIR.findall(response_text)
    return {field.lower(): value.strip() for field, value in pairs}
````

### 3. Regex Performance and Safety

#### **Performance Optimization**

```python
# ✅ GOOD: Compile patterns once, reuse many times
class CompiledPatterns:
    """Pre-compiled regex patterns for performance."""

    def __init__(self):
        # Compile all patterns at initialization
        self.email = re.compile(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$')
        self.phone = re.compile(r'^\+?1?[-.\s]?\(?([0-9]{3})\)?[-.\s]?([0-9]{3})[-.\s]?([0-9]{4})$')
        self.currency = re.compile(r'^\$?(\d{1,3}(?:,\d{3})*(?:\.\d{2})?)$')

    def validate_email(self, email: str) -> bool:
        """Fast email validation using pre-compiled pattern."""
        return bool(self.email.match(email.strip()))

# Global instance for reuse
PATTERNS = CompiledPatterns()

# ❌ BAD: Compiling patterns repeatedly
def validate_email_bad(email: str) -> bool:
    pattern = re.compile(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$')
    return bool(pattern.match(email))  # Compiles every time!
```

#### **Regex Safety - Preventing ReDoS**

```python
def safe_regex_search(pattern: str, text: str, timeout_seconds: float = 1.0) -> re.Match | None:
    """Safely execute regex search with timeout protection.

    Business context: User-provided text could contain pathological
    cases that cause regex to run indefinitely (ReDoS attacks).
    """
    import signal
    from contextlib import contextmanager

    @contextmanager
    def timeout_context(seconds):
        def timeout_handler(signum, frame):
            raise TimeoutError(f"Regex search timed out after {seconds}s")

        old_handler = signal.signal(signal.SIGALRM, timeout_handler)
        signal.alarm(int(seconds))
        try:
            yield
        finally:
            signal.alarm(0)
            signal.signal(signal.SIGALRM, old_handler)

    try:
        with timeout_context(timeout_seconds):
            return re.search(pattern, text)
    except TimeoutError:
        logger.warning(f"Regex search timed out: pattern={pattern[:50]}...")
        return None

# ✅ GOOD: Safe patterns that avoid catastrophic backtracking
SAFE_EMAIL_PATTERN = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'

# ❌ BAD: Patterns prone to catastrophic backtracking
UNSAFE_PATTERN = r'^(a+)+$'  # Exponential time complexity
UNSAFE_EMAIL = r'^([a-zA-Z0-9._%+-])*@([a-zA-Z0-9.-])*\.[a-zA-Z]{2,}$'  # Nested quantifiers
```

---

## 🔍 Text Processing for LLM Integration

### 1. Prompt Template Management

```python
class LLMPromptTemplates:
    """Centralized LLM prompt templates with consistent formatting."""

    EXTRACT_INVOICE_DATA = """
    You are an expert data extraction specialist. Extract structured information from this invoice text.

    Invoice Text:
    {invoice_text}

    Extract the following fields and return ONLY valid JSON:
    - invoice_number: string (alphanumeric ID)
    - vendor_name: string (company name)
    - total_amount: number (decimal value only, no currency symbols)
    - invoice_date: string (YYYY-MM-DD format)
    - line_items: array of objects with quantity, description, unit_price

    Rules:
    1. If a field cannot be determined, use null
    2. Amounts should be numbers without $ or commas
    3. Dates must be in YYYY-MM-DD format
    4. Return only the JSON object, no other text

    JSON:
    """

    CLASSIFY_DOCUMENT = """
    Analyze this document text and classify it into one of these categories:

    Categories:
    - invoice: Bill for goods/services with amount due
    - receipt: Proof of payment for completed transaction
    - statement: Account summary or periodic statement
    - contract: Legal agreement or terms document
    - other: Any document that doesn't fit above categories

    Document Text:
    {document_text}

    Respond with only the category name (lowercase, one word).

    Category:
    """

    VALIDATE_EXTRACTION = """
    Review this extracted data for accuracy and completeness:

    Original Text:
    {original_text}

    Extracted Data:
    {extracted_data}

    Validation Checklist:
    1. Are all required fields present and non-null?
    2. Do amounts appear correct and properly formatted?
    3. Are dates valid and in correct format?
    4. Does vendor name match what's in the document?

    Return JSON with:
    - is_valid: boolean
    - confidence_score: number (0.0 to 1.0)
    - issues: array of strings describing any problems
    - suggested_corrections: object with corrected values

    Validation Result:
    """

def format_extraction_prompt(invoice_text: str) -> str:
    """Format invoice extraction prompt with proper text cleaning."""
    # Clean and truncate text for optimal LLM processing
    cleaned_text = clean_text_for_llm(invoice_text)

    return LLMPromptTemplates.EXTRACT_INVOICE_DATA.format(
        invoice_text=cleaned_text
    )

def clean_text_for_llm(text: str, max_length: int = 4000) -> str:
    """Clean and prepare text for LLM processing.

    Business context: LLMs work better with clean, well-formatted text.
    Remove OCR artifacts and excessive whitespace.
    """
    # Remove common OCR artifacts
    cleaned = re.sub(r'[^\x20-\x7E\n]', '', text)  # Remove non-printable chars
    cleaned = re.sub(r'\n\s*\n\s*\n', '\n\n', cleaned)  # Collapse excessive newlines
    cleaned = re.sub(r' {3,}', ' ', cleaned)  # Collapse excessive spaces

    # Truncate if too long (preserve structure)
    if len(cleaned) > max_length:
        # Try to cut at a natural break (paragraph)
        truncate_point = cleaned.rfind('\n\n', 0, max_length)
        if truncate_point == -1:
            truncate_point = cleaned.rfind('\n', 0, max_length)
        if truncate_point == -1:
            truncate_point = max_length

        cleaned = cleaned[:truncate_point] + '\n[... text truncated ...]'

    return cleaned.strip()
```

### 2. Response Parsing and Validation

```python
def parse_llm_json_response(response: str, expected_schema: dict) -> dict:
    """Parse and validate LLM JSON response against expected schema.

    Business context: LLMs sometimes return malformed JSON or include
    extra text. This provides robust parsing with fallback options.
    """
    # Extract JSON from response
    extracted_data = extract_llm_json_response(response)

    # Validate against expected schema
    validation_errors = []
    cleaned_data = {}

    for field_name, field_config in expected_schema.items():
        field_type = field_config.get('type')
        required = field_config.get('required', False)
        default = field_config.get('default')

        if field_name in extracted_data:
            value = extracted_data[field_name]

            # Type validation and conversion
            try:
                if field_type == 'string':
                    cleaned_data[field_name] = str(value).strip()
                elif field_type == 'number':
                    cleaned_data[field_name] = float(value)
                elif field_type == 'integer':
                    cleaned_data[field_name] = int(float(value))
                elif field_type == 'boolean':
                    cleaned_data[field_name] = bool(value)
                elif field_type == 'array':
                    cleaned_data[field_name] = list(value) if isinstance(value, (list, tuple)) else [value]
                else:
                    cleaned_data[field_name] = value
            except (ValueError, TypeError) as e:
                validation_errors.append(f"Field '{field_name}': {e}")
                if default is not None:
                    cleaned_data[field_name] = default

        elif required:
            validation_errors.append(f"Required field '{field_name}' missing")
            if default is not None:
                cleaned_data[field_name] = default

        elif default is not None:
            cleaned_data[field_name] = default

    return {
        'data': cleaned_data,
        'errors': validation_errors,
        'is_valid': len(validation_errors) == 0
    }

# Example schema for invoice extraction
INVOICE_SCHEMA = {
    'invoice_number': {'type': 'string', 'required': True},
    'vendor_name': {'type': 'string', 'required': True},
    'total_amount': {'type': 'number', 'required': True},
    'invoice_date': {'type': 'string', 'required': True},
    'line_items': {'type': 'array', 'required': False, 'default': []},
    'confidence_score': {'type': 'number', 'required': False, 'default': 0.5}
}

def process_invoice_extraction_response(llm_response: str) -> dict:
    """Process LLM response for invoice data extraction."""
    parsed_result = parse_llm_json_response(llm_response, INVOICE_SCHEMA)

    if parsed_result['is_valid']:
        # Additional business validation
        data = parsed_result['data']

        # Validate invoice number format
        if not ValidationPatterns.INVOICE_GENERIC.match(data['invoice_number']):
            parsed_result['errors'].append(f"Invalid invoice number format: {data['invoice_number']}")

        # Validate amount is reasonable
        if data['total_amount'] <= 0 or data['total_amount'] > 1000000:
            parsed_result['errors'].append(f"Amount out of reasonable range: ${data['total_amount']}")

        # Validate date format
        try:
            datetime.strptime(data['invoice_date'], '%Y-%m-%d')
        except ValueError:
            parsed_result['errors'].append(f"Invalid date format: {data['invoice_date']}")

        parsed_result['is_valid'] = len(parsed_result['errors']) == 0

    return parsed_result
```

---

## 🧪 Testing String Operations

### 1. Unit Testing String Functions

````python
import pytest
from hypothesis import given, strategies as st

class TestStringValidation:
    """Test suite for string validation functions."""

    @pytest.mark.unit
    def test_sanitize_filename_removes_unsafe_chars(self):
        """Test Given: filename with unsafe chars, When: sanitized, Then: chars replaced."""
        unsafe_filename = 'invoice<>:|"?.pdf'
        result = sanitize_filename(unsafe_filename)

        assert result == 'invoice_______.pdf'
        assert not any(char in result for char in '<>:|"?')

    @pytest.mark.unit
    def test_normalize_vendor_name_removes_suffixes(self):
        """Test Given: vendor with suffix, When: normalized, Then: suffix removed."""
        vendor_with_suffix = "ACME Corporation Inc."
        result = normalize_vendor_name(vendor_with_suffix)

        assert result == "ACME CORPORATION"
        assert "INC" not in result

    @pytest.mark.unit
    @pytest.mark.parametrize("email,expected", [
        ("user@example.com", True),
        ("invalid.email", False),
        ("user@", False),
        ("@example.com", False),
        ("user@example", False),  # No TLD
    ])
    def test_email_validation(self, email: str, expected: bool):
        """Test email validation against various formats."""
        result = PATTERNS.validate_email(email)
        assert result == expected

    @given(st.text(min_size=1, max_size=100))
    @pytest.mark.unit
    def test_sanitize_filename_always_returns_safe_string(self, filename: str):
        """Property test: sanitized filename should always be file-system safe."""
        result = sanitize_filename(filename)

        # Should not contain unsafe characters
        unsafe_chars = '<>:"/\\|?*'
        assert not any(char in result for char in unsafe_chars)

        # Should not be empty
        assert len(result.strip()) > 0

        # Should not exceed max length
        assert len(result) <= 255

class TestRegexPatterns:
    """Test suite for regex pattern matching."""

    @pytest.mark.unit
    def test_invoice_number_pattern_matches_valid_formats(self):
        """Test invoice number pattern against known valid formats."""
        valid_numbers = [
            "INV-123456",
            "ACME-789012",
            "ABC-1234",
            "CORP-12345678"
        ]

        for number in valid_numbers:
            assert ValidationPatterns.INVOICE_GENERIC.match(number), f"Failed to match: {number}"

    @pytest.mark.unit
    def test_currency_pattern_handles_various_formats(self):
        """Test currency pattern against different amount formats."""
        test_cases = [
            ("$1,234.56", True, "1234.56"),
            ("1234.56", True, "1234.56"),
            ("$1234", True, "1234"),
            ("1,234", True, "1234"),
            ("invalid", False, None),
            ("$1,234.567", False, None),  # Too many decimal places
        ]

        for amount_str, should_match, expected_value in test_cases:
            match = ValidationPatterns.CURRENCY_AMOUNT.match(amount_str)

            if should_match:
                assert match is not None, f"Should match: {amount_str}"
                if expected_value:
                    extracted = match.group(1).replace(',', '')
                    assert extracted == expected_value
            else:
                assert match is None, f"Should not match: {amount_str}"

class TestLLMResponseParsing:
    """Test suite for LLM response parsing."""

    @pytest.mark.unit
    def test_extract_json_from_markdown_response(self):
        """Test JSON extraction from LLM response with markdown formatting."""
        response = '''
        Here's the extracted data:

        ```json
        {
            "invoice_number": "INV-123456",
            "total_amount": 1234.56,
            "vendor": "ACME Corp"
        }
        ```

        The extraction looks complete.
        '''

        result = extract_llm_json_response(response)

        assert result['invoice_number'] == "INV-123456"
        assert result['total_amount'] == 1234.56
        assert result['vendor'] == "ACME Corp"

    @pytest.mark.unit
    def test_parse_response_with_schema_validation(self):
        """Test response parsing with schema validation and type conversion."""
        response = '{"invoice_number": "INV-123", "total_amount": "1234.56", "missing_field": null}'

        result = parse_llm_json_response(response, INVOICE_SCHEMA)

        assert result['is_valid'] == False  # Missing required fields
        assert 'vendor_name' in str(result['errors'])
        assert result['data']['total_amount'] == 1234.56  # String converted to float
````

### 2. Integration Testing with String Operations

````python
class TestStringIntegration:
    """Integration tests for string operations in workflow context."""

    @pytest.mark.node
    async def test_text_extraction_and_validation_flow(self):
        """Test complete flow from text extraction to validation."""
        # Sample invoice text (would be extracted from PDF)
        invoice_text = """
        INVOICE

        Invoice Number: INV-123456
        From: ACME Corporation Inc.
        Date: 2025-01-15

        Total: $1,234.56
        """

        # Extract data using regex patterns
        extracted_data = extract_invoice_data(invoice_text)

        # Validate extracted data
        validation_result = validate_invoice_number(extracted_data.get('invoice_number', ''))

        assert validation_result['is_valid'] == True
        assert extracted_data['total_amount'] == 1234.56
        assert 'ACME' in extracted_data.get('vendor', '')

    @pytest.mark.graph
    async def test_end_to_end_string_processing(self, fake_llm):
        """Test end-to-end string processing through LLM workflow."""
        # Mock LLM response
        fake_llm.invoke.return_value = '''
        ```json
        {
            "invoice_number": "INV-123456",
            "vendor_name": "ACME Corp",
            "total_amount": 1234.56,
            "invoice_date": "2025-01-15"
        }
        ```
        '''

        # Process through workflow
        raw_text = "Sample invoice text..."
        cleaned_text = clean_text_for_llm(raw_text)
        prompt = format_extraction_prompt(cleaned_text)

        llm_response = fake_llm.invoke(prompt)
        parsed_result = process_invoice_extraction_response(llm_response)

        assert parsed_result['is_valid'] == True
        assert parsed_result['data']['invoice_number'] == "INV-123456"
        assert parsed_result['data']['total_amount'] == 1234.56
````

---

## 📊 Performance Monitoring

### 1. String Operation Metrics

```python
import time
import functools
from typing import Callable

def monitor_string_performance(func: Callable) -> Callable:
    """Decorator to monitor string operation performance."""
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        start_time = time.perf_counter()
        result = func(*args, **kwargs)
        end_time = time.perf_counter()

        # Log performance metrics
        duration = end_time - start_time
        if duration > 0.1:  # Log slow operations
            logger.warning(
                f"Slow string operation: {func.__name__} took {duration:.3f}s",
                extra={
                    'function': func.__name__,
                    'duration': duration,
                    'args_length': sum(len(str(arg)) for arg in args if isinstance(arg, str))
                }
            )

        return result
    return wrapper

@monitor_string_performance
def extract_large_document_data(text: str) -> dict:
    """Extract data from large documents with performance monitoring."""
    # Implementation with performance tracking
    pass
```

### 2. Memory Usage for Large Strings

```python
import tracemalloc
from contextlib import contextmanager

@contextmanager
def track_string_memory(operation_name: str):
    """Context manager to track memory usage of string operations."""
    tracemalloc.start()

    try:
        yield
    finally:
        current, peak = tracemalloc.get_traced_memory()
        tracemalloc.stop()

        # Log memory usage for large operations
        if peak > 10 * 1024 * 1024:  # 10MB threshold
            logger.info(
                f"High memory usage in {operation_name}: "
                f"current={current / 1024 / 1024:.1f}MB, peak={peak / 1024 / 1024:.1f}MB"
            )

def process_large_text_with_monitoring(text: str) -> dict:
    """Process large text with memory monitoring."""
    with track_string_memory("large_text_processing"):
        # Use generator patterns to minimize memory usage
        result = extract_invoice_fields_streaming(iter(text.splitlines()))
        return result
```

---

## 📋 String Operations Checklist

### **Before Writing String Code:**

- [ ] **Check for existing constants** in `src/constants/strings.py`
- [ ] **Use f-strings** for simple formatting, `.format()` for templates
- [ ] **Validate inputs** with appropriate regex patterns
- [ ] **Consider performance** for large strings (use generators/streaming)
- [ ] **Add business context** in comments explaining string operations

### **For Regex Patterns:**

- [ ] **Compile patterns** at module level for reuse
- [ ] **Use named groups** for complex extractions
- [ ] **Test against production data** samples
- [ ] **Document pattern purpose** and expected matches
- [ ] **Consider ReDoS safety** for user-provided input

### **For LLM Integration:**

- [ ] **Clean text** before sending to LLM
- [ ] **Use consistent prompt templates** from constants
- [ ] **Validate responses** against expected schema
- [ ] **Handle malformed JSON** gracefully
- [ ] **Log extraction confidence** for monitoring

### **For String Constants:**

- [ ] **Group related constants** in classes/modules
- [ ] **Use descriptive names** with context
- [ ] **Document business rules** behind constants
- [ ] **Make user-facing messages** actionable and clear
- [ ] **Consider internationalization** needs

---

**Remember: Consistent string handling is critical for data quality and user experience. Always validate, document patterns, and test with real data! 🎯📝✅**
