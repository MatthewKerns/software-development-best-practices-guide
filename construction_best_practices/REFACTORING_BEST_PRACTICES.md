# Python Refactoring Best Practices — LangGraph/LangSmith Project

## 🔄 Core Refactoring Principles

### 1. Red-Green-Refactor Cycle

**ALWAYS refactor only when tests are green.**

- **Red**: Write failing test that captures desired behavior
- **Green**: Write minimal code to make test pass
- **Refactor**: Improve code structure while keeping tests green
- **Never refactor with failing tests** - fix tests first

### 2. Small, Incremental Changes

**Make one change at a time with immediate test verification.**

```python
# ✅ GOOD: Single responsibility refactor
def extract_invoice_fields(text: str) -> dict:
    """Extract structured fields from invoice text."""
    # Step 1: Validate input (single responsibility)
    validated_text = _validate_invoice_text(text)

    # Step 2: Extract fields (single responsibility)
    raw_fields = _extract_raw_fields(validated_text)

    # Step 3: Clean and normalize (single responsibility)
    return _normalize_extracted_fields(raw_fields)

# ❌ BAD: Multiple changes at once
def process_invoice_mega_function(text, config, db, email_client):
    # Doing validation, extraction, normalization, saving, and emailing
    # Too many responsibilities - hard to test and maintain
```

### 3. Preserve External Behavior

**Public interfaces must remain unchanged during refactoring.**

- Internal implementation can change freely
- Public method signatures should stay the same
- Return types and error conditions must be preserved
- Documentation should reflect actual behavior

---

## 🐍 Python-Specific Refactoring Techniques

### 1. Extract Function/Method

**When to use**: Functions > 20 lines or doing multiple things

```python
# ✅ BEFORE: Long function doing multiple things
def process_email_attachment(attachment_data: bytes) -> dict:
    """Process email attachment and extract invoice data."""

    # Extract to separate function
    text = _extract_text_from_pdf(attachment_data)

    # Extract to separate function
    validated_fields = _validate_extracted_fields(text)

    # Extract to separate function
    normalized_data = _normalize_invoice_data(validated_fields)

    return normalized_data

def _extract_text_from_pdf(pdf_data: bytes) -> str:
    """Extract text from PDF using pypdf + LLM fallback."""
    # Single responsibility: PDF text extraction
    pass

def _validate_extracted_fields(text: str) -> dict:
    """Validate extracted invoice fields meet business rules."""
    # Single responsibility: Field validation
    pass

def _normalize_invoice_data(fields: dict) -> dict:
    """Normalize invoice data for consistent processing."""
    # Single responsibility: Data normalization
    pass
```

### 2. Extract Class

**When to use**: Related functions operating on same data

```python
# ✅ AFTER: Cohesive class with single responsibility
class InvoiceProcessor:
    """Processes invoice documents with validation and normalization."""

    def __init__(self, llm_client: ChatOpenAI, confidence_threshold: float = 0.7):
        self.llm = llm_client
        self.confidence_threshold = confidence_threshold
        self._validation_rules = self._load_validation_rules()

    def process(self, pdf_data: bytes) -> dict:
        """Main processing pipeline for invoice data."""
        text = self._extract_text(pdf_data)
        fields = self._extract_fields(text)
        validated = self._validate_fields(fields)
        return self._normalize_data(validated)

    def _extract_text(self, pdf_data: bytes) -> str:
        # Implementation details hidden from public interface
        pass
```

### 3. Replace Magic Numbers with Named Constants

**Improve readability and maintainability**

```python
# ✅ GOOD: Named constants with business context
class InvoiceConfig:
    """Business rules and thresholds for invoice processing."""

    # Confidence thresholds based on production data analysis
    MIN_CONFIDENCE_AUTO_APPROVE = 0.85
    MIN_CONFIDENCE_MANUAL_REVIEW = 0.70
    MIN_CONFIDENCE_REJECT = 0.50

    # Business validation limits
    MAX_REASONABLE_AMOUNT = 10000.00  # Amounts over $10k need approval
    MIN_INVOICE_AGE_DAYS = 1          # Can't be future-dated
    MAX_INVOICE_AGE_DAYS = 90         # Older than 90 days needs review

    # Performance limits
    MAX_PDF_SIZE_MB = 25              # File size limit for processing
    LLM_TIMEOUT_SECONDS = 30          # Prevent hanging requests

def validate_invoice_amount(amount: float) -> bool:
    """Validate invoice amount meets business rules."""
    return 0.01 <= amount <= InvoiceConfig.MAX_REASONABLE_AMOUNT
```

### 4. Replace Conditional with Polymorphism

**Use for complex conditional logic based on types**

```python
# ✅ GOOD: Strategy pattern for different processing approaches
from abc import ABC, abstractmethod

class TextExtractor(ABC):
    """Abstract base for different text extraction strategies."""

    @abstractmethod
    def extract(self, pdf_data: bytes) -> str:
        """Extract text from PDF data."""
        pass

    @abstractmethod
    def confidence_score(self) -> float:
        """Return confidence score for this extraction method."""
        pass

class PyPDFExtractor(TextExtractor):
    """Fast local PDF text extraction using pypdf."""

    def extract(self, pdf_data: bytes) -> str:
        # Fast local extraction - good for simple PDFs
        pass

    def confidence_score(self) -> float:
        return 0.8  # Good for most standard PDFs

class LLMEnhancedExtractor(TextExtractor):
    """AI-enhanced extraction for complex/scanned PDFs."""

    def extract(self, pdf_data: bytes) -> str:
        # LLM-enhanced extraction - better quality but slower
        pass

    def confidence_score(self) -> float:
        return 0.95  # Higher quality but more expensive

class HybridExtractor(TextExtractor):
    """Combines multiple extraction methods for best results."""

    def __init__(self):
        self.fast_extractor = PyPDFExtractor()
        self.enhanced_extractor = LLMEnhancedExtractor()

    def extract(self, pdf_data: bytes) -> str:
        # Try fast method first, fall back to enhanced if needed
        text = self.fast_extractor.extract(pdf_data)
        if self._is_low_quality(text):
            text = self.enhanced_extractor.extract(pdf_data)
        return text
```

---

## 🏗️ Design Pattern Applications

### 1. Strategy Pattern

**Use for**: Different algorithms/approaches for same task

```python
class InvoiceValidationStrategy(ABC):
    """Strategy for different validation approaches."""

    @abstractmethod
    def validate(self, invoice_data: dict) -> ValidationResult:
        pass

class StandardValidation(InvoiceValidationStrategy):
    """Standard business rule validation."""

    def validate(self, invoice_data: dict) -> ValidationResult:
        # Standard validation rules
        pass

class StrictValidation(InvoiceValidationStrategy):
    """Enhanced validation for high-value invoices."""

    def validate(self, invoice_data: dict) -> ValidationResult:
        # Additional checks for amounts > $5000
        pass

class InvoiceProcessor:
    def __init__(self, validation_strategy: InvoiceValidationStrategy):
        self.validator = validation_strategy

    def process(self, data: dict) -> dict:
        result = self.validator.validate(data)
        # Process based on validation result
        return result
```

### 2. Factory Pattern

**Use for**: Creating complex objects with different configurations

```python
class ExtractorFactory:
    """Factory for creating appropriate text extractors."""

    @staticmethod
    def create_extractor(pdf_type: str, use_llm: bool = False) -> TextExtractor:
        """Create appropriate extractor based on PDF characteristics."""

        if pdf_type == "scanned" or use_llm:
            return LLMEnhancedExtractor()
        elif pdf_type == "complex":
            return HybridExtractor()
        else:
            return PyPDFExtractor()

    @staticmethod
    def create_for_file_size(size_mb: float) -> TextExtractor:
        """Create extractor optimized for file size."""

        if size_mb > 10:
            # Large files need efficient processing
            return PyPDFExtractor()
        else:
            # Small files can use enhanced processing
            return LLMEnhancedExtractor()
```

### 3. Observer Pattern

**Use for**: Event-driven processing and notifications

```python
from typing import List, Protocol

class InvoiceProcessingObserver(Protocol):
    """Observer interface for invoice processing events."""

    def on_processing_started(self, invoice_id: str) -> None:
        pass

    def on_processing_completed(self, invoice_id: str, result: dict) -> None:
        pass

    def on_processing_failed(self, invoice_id: str, error: str) -> None:
        pass

class LangSmithTracer:
    """Observer that logs events to LangSmith."""

    def on_processing_started(self, invoice_id: str) -> None:
        # Log start event to LangSmith
        pass

    def on_processing_completed(self, invoice_id: str, result: dict) -> None:
        # Log success metrics to LangSmith
        pass

class EmailNotifier:
    """Observer that sends email notifications."""

    def on_processing_failed(self, invoice_id: str, error: str) -> None:
        # Send failure notification email
        pass

class InvoiceProcessor:
    def __init__(self):
        self.observers: List[InvoiceProcessingObserver] = []

    def add_observer(self, observer: InvoiceProcessingObserver) -> None:
        self.observers.append(observer)

    def _notify_started(self, invoice_id: str) -> None:
        for observer in self.observers:
            observer.on_processing_started(invoice_id)
```

### 4. Template Method Pattern

**Use for**: Common algorithm structure with varying steps

```python
class BaseDocumentProcessor(ABC):
    """Template for processing different document types."""

    def process_document(self, data: bytes) -> dict:
        """Template method defining processing steps."""

        # Common preprocessing
        validated_data = self._validate_input(data)

        # Vary by document type
        extracted_text = self._extract_text(validated_data)
        structured_data = self._parse_structure(extracted_text)

        # Common postprocessing
        normalized_data = self._normalize_output(structured_data)

        return normalized_data

    def _validate_input(self, data: bytes) -> bytes:
        """Common validation logic."""
        if not data or len(data) == 0:
            raise ValueError("Empty document data")
        return data

    def _normalize_output(self, data: dict) -> dict:
        """Common normalization logic."""
        # Standard field cleanup and formatting
        return data

    @abstractmethod
    def _extract_text(self, data: bytes) -> str:
        """Extract text - varies by document type."""
        pass

    @abstractmethod
    def _parse_structure(self, text: str) -> dict:
        """Parse structure - varies by document type."""
        pass

class InvoiceProcessor(BaseDocumentProcessor):
    """Processor specialized for invoice documents."""

    def _extract_text(self, data: bytes) -> str:
        # Invoice-specific text extraction
        pass

    def _parse_structure(self, text: str) -> dict:
        # Invoice-specific field parsing
        pass

class ReceiptProcessor(BaseDocumentProcessor):
    """Processor specialized for receipt documents."""

    def _extract_text(self, data: bytes) -> str:
        # Receipt-specific text extraction
        pass

    def _parse_structure(self, text: str) -> dict:
        # Receipt-specific field parsing
        pass
```

---

## 🔧 Refactoring Process & Workflow

### 1. Preparation Phase

**Establish safety net before making changes**

```bash
# 1. Ensure all tests pass
pytest -m "unit or node" -q

# 2. Check test coverage for target code
pytest --cov=src/services/extraction --cov-report=term-missing

# 3. Create feature branch
git checkout -b refactor/extract-invoice-processor

# 4. Commit current state as baseline
git add -A && git commit -m "Baseline before refactoring invoice processor"
```

### 2. Analysis Phase

**Understand current code before changing it**

```python
# Use semantic search to understand usage patterns
from tools import semantic_search

# Find all usages of function to be refactored
usages = semantic_search("extract_invoice_data usage patterns")

# Identify dependencies and coupling
dependencies = semantic_search("invoice extraction dependencies")

# Look for similar patterns that might need unified approach
patterns = semantic_search("text extraction patterns")
```

### 3. Incremental Refactoring Steps

**Make one change at a time with test verification**

```bash
# Step 1: Extract one function
# - Write tests for new function
# - Extract function
# - Run tests to verify no regression
pytest tests/unit_tests/services/extraction/ -v

# Step 2: Extract another function
# - Repeat process
pytest tests/unit_tests/services/extraction/ -v

# Step 3: Create class if multiple related functions
# - Group related functions into class
# - Preserve public interface
pytest tests/unit_tests/services/extraction/ -v

# Commit after each successful step
git add -A && git commit -m "Extract validate_invoice_fields function"
```

### 4. Testing During Refactoring

**Ensure behavior preservation throughout process**

```python
# Add characterization tests before refactoring
def test_current_behavior_baseline():
    """Capture current behavior before refactoring."""
    # Record exact current outputs for regression detection
    input_data = load_test_fixture("sample_invoice.pdf")
    result = extract_invoice_data(input_data)

    # Assert on specific current behavior
    assert result["vendor"] == "Expected Vendor Name"
    assert result["amount"] == 123.45
    assert result["confidence"] >= 0.8

# Property-based tests for invariants
from hypothesis import given, strategies as st

@given(pdf_content=st.binary(min_size=100, max_size=10000))
def test_extraction_invariants(pdf_content):
    """Test that extraction maintains invariants regardless of input."""
    try:
        result = extract_invoice_data(pdf_content)

        # Invariants that must always hold
        assert isinstance(result, dict)
        assert "confidence" in result
        assert 0.0 <= result["confidence"] <= 1.0

        if result.get("amount"):
            assert isinstance(result["amount"], (int, float))
            assert result["amount"] >= 0

    except ValueError:
        # Acceptable to raise ValueError for invalid inputs
        pass
```

### 5. Validation Phase

**Verify refactoring success**

```bash
# 1. All existing tests still pass
pytest tests/ -v

# 2. No performance regression
pytest tests/ --benchmark-only

# 3. Coverage maintained or improved
pytest --cov=src --cov-report=term-missing --cov-fail-under=80

# 4. Integration tests pass
pytest -m "graph or contract" -v

# 5. Manual verification of key workflows
python testing_scripts/test_workflow_integration.py
```

---

## 💨 Code Smell Detection & Solutions

### 1. Long Methods/Functions

**Smell**: Functions > 20 lines or multiple responsibilities

```python
# 🚨 SMELL: Long function doing too much
def process_invoice(pdf_data, config, db_client, email_client):
    # 50+ lines doing validation, extraction, saving, emailing
    pass

# ✅ SOLUTION: Extract smaller functions
def process_invoice(pdf_data: bytes) -> dict:
    """Main invoice processing pipeline."""
    text = extract_text_from_pdf(pdf_data)
    fields = extract_invoice_fields(text)
    validated = validate_invoice_data(fields)
    return normalize_invoice_format(validated)
```

### 2. Duplicate Code

**Smell**: Same logic repeated in multiple places

```python
# 🚨 SMELL: Duplicate validation logic
def process_invoice(data):
    if not data or len(data) == 0:
        raise ValueError("Empty data")
    # ... rest of processing

def process_receipt(data):
    if not data or len(data) == 0:
        raise ValueError("Empty data")
    # ... rest of processing

# ✅ SOLUTION: Extract common function
def validate_document_data(data: bytes) -> bytes:
    """Validate document data is not empty."""
    if not data or len(data) == 0:
        raise ValueError("Document data cannot be empty")
    return data

def process_invoice(data: bytes) -> dict:
    validated_data = validate_document_data(data)
    # ... invoice-specific processing

def process_receipt(data: bytes) -> dict:
    validated_data = validate_document_data(data)
    # ... receipt-specific processing
```

### 3. Long Parameter Lists

**Smell**: Functions with > 4 parameters

```python
# 🚨 SMELL: Too many parameters
def extract_invoice_data(pdf_data, llm_client, confidence_threshold,
                        max_retries, timeout, validation_rules,
                        output_format, error_handler):
    pass

# ✅ SOLUTION: Configuration object
@dataclass
class ExtractionConfig:
    """Configuration for invoice data extraction."""
    confidence_threshold: float = 0.7
    max_retries: int = 3
    timeout_seconds: int = 30
    output_format: str = "json"
    validation_enabled: bool = True

def extract_invoice_data(pdf_data: bytes,
                        llm_client: ChatOpenAI,
                        config: ExtractionConfig) -> dict:
    """Extract invoice data with configurable parameters."""
    pass
```

### 4. Feature Envy

**Smell**: Method using lots of methods from another class

```python
# 🚨 SMELL: InvoiceProcessor doing lots of PDF operations
class InvoiceProcessor:
    def process(self, pdf_client: PDFClient, data: bytes):
        # Feature envy - should be in PDFClient
        text = pdf_client.extract_text(data)
        pages = pdf_client.get_page_count(data)
        metadata = pdf_client.get_metadata(data)
        quality = pdf_client.assess_quality(data)
        # ... more PDF operations

# ✅ SOLUTION: Move behavior to appropriate class
class PDFClient:
    def extract_document_info(self, data: bytes) -> DocumentInfo:
        """Extract all relevant PDF information in one call."""
        return DocumentInfo(
            text=self.extract_text(data),
            page_count=self.get_page_count(data),
            metadata=self.get_metadata(data),
            quality_score=self.assess_quality(data)
        )

class InvoiceProcessor:
    def process(self, pdf_client: PDFClient, data: bytes):
        doc_info = pdf_client.extract_document_info(data)
        # Now work with structured document info
```

### 5. Data Clumps

**Smell**: Same group of parameters appearing together

```python
# 🚨 SMELL: Same parameters always passed together
def validate_amount(amount, currency, decimal_places):
    pass

def format_amount(amount, currency, decimal_places):
    pass

def convert_amount(amount, currency, decimal_places, target_currency):
    pass

# ✅ SOLUTION: Create value object
@dataclass
class Money:
    """Value object representing monetary amount."""
    amount: Decimal
    currency: str
    decimal_places: int = 2

    def validate(self) -> bool:
        return self.amount >= 0 and len(self.currency) == 3

    def format(self) -> str:
        return f"{self.amount:.{self.decimal_places}f} {self.currency}"

    def convert_to(self, target_currency: str, exchange_rate: float) -> 'Money':
        new_amount = self.amount * Decimal(str(exchange_rate))
        return Money(new_amount, target_currency, self.decimal_places)
```

---

## 🚀 Advanced Refactoring Strategies

### 1. Branch by Abstraction

**For large changes that need gradual migration**

```python
# Step 1: Create abstraction layer
class TextExtractor(ABC):
    @abstractmethod
    def extract(self, data: bytes) -> str:
        pass

# Step 2: Implement new version alongside old
class LegacyPyPDFExtractor(TextExtractor):
    def extract(self, data: bytes) -> str:
        # Existing pypdf implementation
        pass

class NewHybridExtractor(TextExtractor):
    def extract(self, data: bytes) -> str:
        # New implementation with LLM fallback
        pass

# Step 3: Use feature flag to gradually migrate
class ExtractionService:
    def __init__(self, use_new_extractor: bool = False):
        if use_new_extractor:
            self.extractor = NewHybridExtractor()
        else:
            self.extractor = LegacyPyPDFExtractor()

    def extract_text(self, data: bytes) -> str:
        return self.extractor.extract(data)

# Step 4: Gradually roll out new implementation
# Step 5: Remove old implementation when migration complete
```

### 2. Strangler Fig Pattern

**For replacing legacy systems piece by piece**

```python
# Gradually replace old monolithic function
class LegacyInvoiceProcessor:
    def process_everything(self, data: bytes) -> dict:
        # Old monolithic implementation
        pass

class ModernInvoiceProcessor:
    def __init__(self, use_new_extraction: bool = False,
                 use_new_validation: bool = False):
        self.legacy = LegacyInvoiceProcessor()
        self.use_new_extraction = use_new_extraction
        self.use_new_validation = use_new_validation

    def process(self, data: bytes) -> dict:
        if self.use_new_extraction:
            text = self._extract_text_modern(data)
        else:
            text = self.legacy._extract_text_legacy(data)

        if self.use_new_validation:
            validated = self._validate_modern(text)
        else:
            validated = self.legacy._validate_legacy(text)

        return validated
```

### 3. Parallel Change

**For changing interfaces safely**

```python
# Step 1: Add new method alongside old one
class InvoiceExtractor:
    def extract_data(self, pdf_path: str) -> dict:
        """Legacy method - deprecated, use extract_from_bytes."""
        with open(pdf_path, 'rb') as f:
            return self.extract_from_bytes(f.read())

    def extract_from_bytes(self, pdf_data: bytes) -> dict:
        """New preferred method accepting bytes directly."""
        # New implementation
        pass

# Step 2: Migrate callers to new method
# Step 3: Mark old method as deprecated
# Step 4: Remove old method after migration complete
```

---

## 🧪 Refactoring with Tests

### 1. Characterization Tests

**Capture current behavior before refactoring**

```python
class TestCurrentBehavior:
    """Capture exact current behavior before refactoring."""

    def test_extract_invoice_current_output(self):
        """Record current output format for regression detection."""
        # Load real test data that represents current system
        pdf_data = load_fixture("real_invoice_sample.pdf")

        # Capture exact current behavior
        result = extract_invoice_data(pdf_data)

        # Assert on specific current structure
        expected_keys = {"vendor", "amount", "date", "invoice_number", "confidence"}
        assert set(result.keys()) == expected_keys

        # Assert on data types
        assert isinstance(result["amount"], float)
        assert isinstance(result["confidence"], float)
        assert 0.0 <= result["confidence"] <= 1.0

        # Store snapshot for comparison
        self._save_baseline_snapshot(result)

    def test_error_conditions_current_behavior(self):
        """Capture current error handling behavior."""
        # Test current error handling
        with pytest.raises(ValueError, match="Invalid PDF format"):
            extract_invoice_data(b"not a pdf")

        # Test empty input handling
        with pytest.raises(ValueError, match="Empty data"):
            extract_invoice_data(b"")
```

### 2. Golden Master Testing

**Verify refactoring preserves outputs for large input sets**

```python
def test_golden_master_invoice_extraction():
    """Verify refactoring preserves outputs across sample set."""

    # Load suite of test invoices
    test_cases = load_invoice_test_suite()

    for test_case in test_cases:
        # Get current system output (golden master)
        expected_output = test_case.expected_result

        # Run refactored system
        actual_output = extract_invoice_data(test_case.pdf_data)

        # Compare with tolerance for minor differences
        assert_invoice_data_equivalent(expected_output, actual_output)

def assert_invoice_data_equivalent(expected: dict, actual: dict):
    """Compare invoice data with business-appropriate tolerance."""

    # Exact match for critical fields
    assert expected["vendor"] == actual["vendor"]
    assert expected["invoice_number"] == actual["invoice_number"]

    # Tolerance for floating point amounts
    assert abs(expected["amount"] - actual["amount"]) < 0.01

    # Tolerance for confidence scores (algorithm may vary slightly)
    assert abs(expected["confidence"] - actual["confidence"]) < 0.05
```

### 3. Property-Based Testing During Refactoring

**Ensure invariants hold throughout refactoring**

```python
from hypothesis import given, strategies as st

@given(
    pdf_size=st.integers(min_value=100, max_value=1000000),
    corruption_level=st.floats(min_value=0.0, max_value=0.3)
)
def test_extraction_robustness_properties(pdf_size, corruption_level):
    """Test that extraction maintains robustness properties."""

    # Generate test PDF data
    pdf_data = generate_test_pdf(size=pdf_size, corruption=corruption_level)

    try:
        result = extract_invoice_data(pdf_data)

        # Invariants that must always hold after refactoring
        assert isinstance(result, dict), "Result must be dictionary"
        assert "confidence" in result, "Must include confidence score"
        assert 0.0 <= result["confidence"] <= 1.0, "Confidence in valid range"

        # Business invariants
        if "amount" in result:
            assert result["amount"] >= 0, "Amount cannot be negative"
            assert result["amount"] < 1000000, "Amount should be reasonable"

    except (ValueError, PDFError) as e:
        # Acceptable to fail on invalid inputs
        assert "invalid" in str(e).lower() or "corrupt" in str(e).lower()
```

---

## 📊 Measuring Refactoring Success

### 1. Code Quality Metrics

**Track improvement in measurable ways**

```bash
# Complexity metrics before/after refactoring
pip install radon
radon cc src/services/extraction/ --show-complexity

# Maintainability index
radon mi src/services/extraction/

# Lines of code and function length distribution
radon raw src/services/extraction/
```

### 2. Test Quality Improvements

**Ensure refactoring improves testability**

```bash
# Test coverage should improve
pytest --cov=src/services/extraction --cov-report=term-missing

# Test execution time should not increase significantly
pytest tests/unit_tests/services/extraction/ --benchmark-only

# Number of test cases per function (should increase with better separation)
grep -r "def test_" tests/unit_tests/services/extraction/ | wc -l
```

### 3. Dependency and Coupling Analysis

**Refactoring should reduce coupling**

```python
# Analyze import dependencies
def analyze_coupling():
    """Analyze coupling between modules."""

    # Count imports between modules
    extraction_imports = grep_search("from.*extraction.*import", include_pattern="src/**")

    # Measure fan-in/fan-out
    # High fan-in = many modules depend on this (should be stable)
    # High fan-out = this module depends on many others (should be refactored)

    return coupling_metrics

# Track cyclomatic complexity
def measure_complexity():
    """Measure code complexity before/after refactoring."""

    # Use radon or similar tool to measure complexity
    # Target: Functions with complexity > 10 should be refactored
    pass
```

### 4. Performance Impact Assessment

**Ensure refactoring doesn't hurt performance**

```python
import time
import pytest

@pytest.mark.benchmark
def test_extraction_performance_baseline():
    """Benchmark extraction performance after refactoring."""

    # Load realistic test data
    test_pdf = load_fixture("typical_invoice_5pages.pdf")

    # Measure performance
    start_time = time.time()
    result = extract_invoice_data(test_pdf)
    end_time = time.time()

    # Performance should not regress
    processing_time = end_time - start_time
    assert processing_time < 5.0, f"Processing took {processing_time}s, expected < 5s"

    # Quality should be maintained
    assert result["confidence"] >= 0.7, "Quality should not decrease"
```

### 5. Business Value Validation

**Verify refactoring delivers business benefits**

```python
def validate_business_improvements():
    """Validate that refactoring delivers business value."""

    # Maintainability: Time to add new features should decrease
    # Reliability: Error rates should decrease or stay same
    # Performance: Processing time should not increase
    # Testability: Time to write tests should decrease

    metrics = {
        "test_coverage": get_test_coverage(),
        "average_function_length": get_average_function_length(),
        "cyclomatic_complexity": get_average_complexity(),
        "coupling_between_objects": measure_coupling(),
        "defect_rate": calculate_defect_rate(),
    }

    return metrics
```

---

## 🎯 Refactoring Checklist

### Pre-Refactoring

- [ ] **All tests passing** - never refactor with failing tests
- [ ] **Test coverage ≥ 80%** for code being refactored
- [ ] **Performance baseline** established
- [ ] **Git baseline commit** created
- [ ] **README.md consulted** for business context

### During Refactoring

- [ ] **One change at a time** - commit after each successful step
- [ ] **Tests run after each change** - immediate feedback
- [ ] **Public interfaces preserved** - no breaking changes
- [ ] **Comments updated** - keep documentation in sync
- [ ] **Business logic comments** explain "why" decisions

### Post-Refactoring

- [ ] **All tests still pass** - behavior preserved
- [ ] **Test coverage maintained/improved** - no regression
- [ ] **Performance not degraded** - within acceptable bounds
- [ ] **Code complexity reduced** - measurable improvement
- [ ] **Documentation updated** - reflects new structure
- [ ] **Integration tests pass** - no hidden breakage

### Quality Gates

- [ ] **Cyclomatic complexity ≤ 10** per function
- [ ] **Function length ≤ 20 lines** for most functions
- [ ] **Class responsibilities clear** - single responsibility
- [ ] **Coupling reduced** - fewer dependencies
- [ ] **Duplication eliminated** - DRY principle followed

---

## 📚 Further Reading & Tools

### Essential Tools

- **pytest**: Testing framework with excellent refactoring support
- **black**: Code formatting for consistency
- **radon**: Code complexity analysis
- **rope**: Python refactoring library
- **vulture**: Dead code detection

### Key Resources

- **"Refactoring: Improving the Design of Existing Code"** by Martin Fowler
- **"Working Effectively with Legacy Code"** by Michael Feathers
- **"Clean Code"** by Robert Martin
- **Python-specific**: "Effective Python" by Brett Slatkin

### Project-Specific Context

- **LangGraph Documentation**: Understanding node behavior for refactoring
- **LangSmith Tracing**: Using traces to verify behavior preservation
- **TDD Essentials**: Follow TDD cycle during refactoring
- **Project README files**: Business context for refactoring decisions

---

**Remember: Refactoring is an investment in future development velocity. Always refactor with tests, make small changes, and measure the impact! 🚀**
