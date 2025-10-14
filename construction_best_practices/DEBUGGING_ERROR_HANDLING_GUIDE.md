# Debugging and Error Handling Guide — Code Complete 2 Methodology

## 🐛 Overview

**This guide applies Code Complete 2's systematic approach to debugging and error handling, creating robust, maintainable error recovery for our Python LangGraph project.**

Effective debugging and error handling are essential skills that separate professional developers from amateurs. This guide ensures every error is handled gracefully and every bug is systematically eliminated.

---

## 🔍 Systematic Debugging Approach

### 1. Scientific Method for Bug Hunting

```python
import logging
import traceback
from datetime import datetime
from typing import Any, Dict, Optional
from dataclasses import dataclass

@dataclass
class DebuggingContext:
    """Structured context for systematic debugging."""
    function_name: str
    input_parameters: Dict[str, Any]
    expected_behavior: str
    observed_behavior: str
    timestamp: datetime
    stack_trace: Optional[str] = None
    environment_info: Optional[Dict[str, str]] = None

def debug_invoice_extraction_failure(invoice_data: dict, extraction_result: Any) -> DebuggingContext:
    """Create systematic debugging context for extraction failures."""

    context = DebuggingContext(
        function_name="extract_invoice_data",
        input_parameters={
            'invoice_data_keys': list(invoice_data.keys()),
            'invoice_data_size': len(str(invoice_data)),
            'invoice_id': invoice_data.get('id', 'unknown')
        },
        expected_behavior="Extract vendor, amount, date, and line items from invoice text",
        observed_behavior=f"Extraction returned: {type(extraction_result)} with content: {str(extraction_result)[:100]}...",
        timestamp=datetime.now(),
        environment_info={
            'python_version': sys.version,
            'llm_model': os.getenv('LLM_MODEL', 'unknown'),
            'available_memory_mb': psutil.virtual_memory().available // 1024 // 1024
        }
    )

    # Hypothesis-driven debugging
    logging.error(
        f"Invoice extraction debugging context",
        extra={
            'debugging_context': context.__dict__,
            'hypotheses_to_test': [
                'Input text too short or empty',
                'LLM prompt template formatting issue',
                'Response parsing regex failure',
                'Network timeout during LLM call'
            ]
        }
    )

    return context

def test_debugging_hypotheses(context: DebuggingContext, invoice_data: dict) -> Dict[str, bool]:
    """Test specific hypotheses about what might be causing the bug."""

    test_results = {}

    # Hypothesis 1: Input validation
    invoice_text = invoice_data.get('extracted_text', '')
    test_results['text_too_short'] = len(invoice_text.strip()) < 50
    test_results['text_contains_invoice_keywords'] = any(
        keyword in invoice_text.lower()
        for keyword in ['invoice', 'bill', 'total', 'amount', 'vendor']
    )

    # Hypothesis 2: Data format issues
    test_results['has_required_fields'] = all(
        field in invoice_data
        for field in ['extracted_text', 'filename', 'content_type']
    )

    # Hypothesis 3: External service availability
    try:
        response = requests.get('https://api.openai.com/v1/models', timeout=5)
        test_results['llm_service_available'] = response.status_code == 200
    except:
        test_results['llm_service_available'] = False

    # Log test results for systematic analysis
    logging.info(
        f"Debugging hypothesis test results",
        extra={
            'function': context.function_name,
            'timestamp': context.timestamp.isoformat(),
            'test_results': test_results
        }
    )

    return test_results
```

### 2. Rubber Duck Debugging with Code

```python
class RubberDuckDebugger:
    """Implement rubber duck debugging as systematic code review."""

    def __init__(self, function_name: str):
        self.function_name = function_name
        self.explanation_log = []

    def explain_step(self, step_description: str, variables: Dict[str, Any]) -> None:
        """Explain what this step does and current variable state."""
        explanation = {
            'step': step_description,
            'variables': {k: str(v)[:100] for k, v in variables.items()},
            'timestamp': datetime.now().isoformat()
        }
        self.explanation_log.append(explanation)

        # Log explanation for review
        logging.debug(
            f"Rubber duck explanation: {step_description}",
            extra={
                'function': self.function_name,
                'variables': explanation['variables']
            }
        )

    def question_assumption(self, assumption: str, evidence: Any) -> None:
        """Question an assumption with evidence."""
        logging.debug(
            f"Questioning assumption: {assumption}",
            extra={
                'function': self.function_name,
                'evidence': str(evidence)[:200]
            }
        )

    def get_debugging_summary(self) -> Dict[str, Any]:
        """Get complete debugging session summary."""
        return {
            'function': self.function_name,
            'steps_explained': len(self.explanation_log),
            'explanation_log': self.explanation_log,
            'session_duration': 'completed'
        }

def extract_vendor_with_debugging(invoice_text: str) -> Optional[str]:
    """Extract vendor name with systematic debugging approach."""

    duck = RubberDuckDebugger('extract_vendor_with_debugging')

    # Step 1: Validate input
    duck.explain_step(
        "Validating input text for vendor extraction",
        {'text_length': len(invoice_text), 'text_preview': invoice_text[:100]}
    )

    if not invoice_text or len(invoice_text.strip()) < 10:
        duck.question_assumption(
            "Text should contain vendor information",
            f"Text too short: {len(invoice_text)} chars"
        )
        return None

    # Step 2: Apply extraction pattern
    vendor_patterns = [
        r'(?:from|vendor|bill\s+to):\s*([A-Za-z][A-Za-z\s&,.\''-]{2,50})',
        r'vendor:\s*([A-Za-z][A-Za-z\s&,.\''-]{2,50})',
        r'from:\s*([A-Za-z][A-Za-z\s&,.\''-]{2,50})'
    ]

    for pattern_index, pattern in enumerate(vendor_patterns):
        duck.explain_step(
            f"Trying vendor pattern {pattern_index + 1}",
            {'pattern': pattern, 'text_sample': invoice_text[:200]}
        )

        match = re.search(pattern, invoice_text, re.IGNORECASE)
        if match:
            vendor_name = match.group(1).strip()
            duck.explain_step(
                f"Pattern {pattern_index + 1} matched",
                {'vendor_name': vendor_name, 'match_position': match.span()}
            )

            # Validate extracted vendor name
            if len(vendor_name) >= 2 and not vendor_name.isdigit():
                duck.explain_step(
                    "Vendor name validation passed",
                    {'final_vendor': vendor_name}
                )
                return vendor_name
            else:
                duck.question_assumption(
                    "Extracted text should be a valid vendor name",
                    f"Invalid vendor: '{vendor_name}'"
                )

    # No pattern matched
    duck.explain_step(
        "No vendor patterns matched - extraction failed",
        {'patterns_tried': len(vendor_patterns)}
    )

    # Log complete debugging session
    logging.warning(
        "Vendor extraction failed with complete debugging context",
        extra=duck.get_debugging_summary()
    )

    return None
```

---

## 🚨 Comprehensive Error Handling

### 1. Error Taxonomy and Recovery Strategies

```python
from enum import Enum
from typing import Union, Callable, Awaitable

class ErrorSeverity(Enum):
    """Classification of error severity levels."""
    LOW = "low"           # Warning level - log and continue
    MEDIUM = "medium"     # Recoverable - retry or fallback
    HIGH = "high"         # Serious - fail operation but continue processing
    CRITICAL = "critical" # Fatal - stop all processing

class ErrorCategory(Enum):
    """Categories of errors for appropriate handling."""
    USER_INPUT = "user_input"           # Invalid user data
    EXTERNAL_SERVICE = "external_service"  # API/service failures
    SYSTEM_RESOURCE = "system_resource"    # Memory, disk, network
    BUSINESS_RULE = "business_rule"        # Validation failures
    CONFIGURATION = "configuration"       # Setup/config issues
    UNEXPECTED = "unexpected"              # Unknown errors

@dataclass
class ErrorContext:
    """Comprehensive error context for analysis and recovery."""
    error_type: type
    error_message: str
    severity: ErrorSeverity
    category: ErrorCategory
    recovery_strategy: str
    context_data: Dict[str, Any]
    timestamp: datetime
    function_name: str
    can_retry: bool = False
    retry_count: int = 0
    max_retries: int = 3

class SmartErrorHandler:
    """Intelligent error handling with recovery strategies."""

    def __init__(self):
        self.error_patterns = {
            # Network/API errors - retry with backoff
            (requests.exceptions.RequestException, 'openai'): {
                'severity': ErrorSeverity.MEDIUM,
                'category': ErrorCategory.EXTERNAL_SERVICE,
                'recovery': 'retry_with_exponential_backoff',
                'can_retry': True,
                'max_retries': 3
            },

            # Validation errors - log and return structured error
            (ValueError, 'validation'): {
                'severity': ErrorSeverity.MEDIUM,
                'category': ErrorCategory.BUSINESS_RULE,
                'recovery': 'return_validation_error',
                'can_retry': False
            },

            # Memory errors - try garbage collection and retry once
            (MemoryError,): {
                'severity': ErrorSeverity.HIGH,
                'category': ErrorCategory.SYSTEM_RESOURCE,
                'recovery': 'garbage_collect_and_retry',
                'can_retry': True,
                'max_retries': 1
            },

            # Configuration errors - fail fast
            (KeyError, 'config'): {
                'severity': ErrorSeverity.CRITICAL,
                'category': ErrorCategory.CONFIGURATION,
                'recovery': 'fail_fast_with_clear_message',
                'can_retry': False
            }
        }

    def handle_error(self,
                    error: Exception,
                    context: Dict[str, Any],
                    function_name: str) -> ErrorContext:
        """Handle error with appropriate recovery strategy."""

        # Identify error pattern
        error_config = self._identify_error_pattern(error, context)

        error_context = ErrorContext(
            error_type=type(error),
            error_message=str(error),
            severity=error_config['severity'],
            category=error_config['category'],
            recovery_strategy=error_config['recovery'],
            context_data=context,
            timestamp=datetime.now(),
            function_name=function_name,
            can_retry=error_config.get('can_retry', False),
            max_retries=error_config.get('max_retries', 0)
        )

        # Log error with full context
        self._log_error_with_context(error_context)

        return error_context

    def _identify_error_pattern(self, error: Exception, context: Dict[str, Any]) -> Dict[str, Any]:
        """Identify which error pattern matches this error."""

        for pattern_key, config in self.error_patterns.items():
            error_types = pattern_key if isinstance(pattern_key, tuple) else (pattern_key,)

            # Check if error type matches
            if isinstance(error, error_types[0]):
                # Check context clues if specified
                if len(error_types) > 1:
                    context_clue = error_types[1]
                    if context_clue in str(error).lower() or context_clue in str(context).lower():
                        return config
                else:
                    return config

        # Default handling for unrecognized errors
        return {
            'severity': ErrorSeverity.HIGH,
            'category': ErrorCategory.UNEXPECTED,
            'recovery': 'log_and_reraise',
            'can_retry': False
        }

    def _log_error_with_context(self, error_context: ErrorContext) -> None:
        """Log error with comprehensive context for debugging."""

        log_level = {
            ErrorSeverity.LOW: logging.WARNING,
            ErrorSeverity.MEDIUM: logging.ERROR,
            ErrorSeverity.HIGH: logging.ERROR,
            ErrorSeverity.CRITICAL: logging.CRITICAL
        }[error_context.severity]

        log_level(
            f"Error in {error_context.function_name}: {error_context.error_message}",
            extra={
                'error_context': {
                    'error_type': error_context.error_type.__name__,
                    'severity': error_context.severity.value,
                    'category': error_context.category.value,
                    'recovery_strategy': error_context.recovery_strategy,
                    'can_retry': error_context.can_retry,
                    'retry_count': error_context.retry_count,
                    'context_data': error_context.context_data,
                    'timestamp': error_context.timestamp.isoformat()
                }
            }
        )

# Usage example with comprehensive error handling
error_handler = SmartErrorHandler()

async def extract_invoice_with_smart_error_handling(invoice_data: dict) -> Union[dict, ErrorContext]:
    """Extract invoice data with intelligent error recovery."""

    context = {
        'invoice_id': invoice_data.get('id', 'unknown'),
        'data_size': len(str(invoice_data)),
        'extraction_method': 'llm_enhanced'
    }

    try:
        # Primary extraction attempt
        result = await primary_extraction_method(invoice_data)
        return result

    except Exception as e:
        # Handle error intelligently
        error_context = error_handler.handle_error(e, context, 'extract_invoice_with_smart_error_handling')

        # Execute recovery strategy
        if error_context.can_retry and error_context.retry_count < error_context.max_retries:
            return await retry_with_recovery_strategy(invoice_data, error_context)
        else:
            return error_context

async def retry_with_recovery_strategy(invoice_data: dict, error_context: ErrorContext) -> Union[dict, ErrorContext]:
    """Execute appropriate recovery strategy based on error context."""

    if error_context.recovery_strategy == 'retry_with_exponential_backoff':
        # Wait with exponential backoff
        wait_time = 2 ** error_context.retry_count
        await asyncio.sleep(wait_time)

        # Update retry count and try again
        error_context.retry_count += 1
        return await extract_invoice_with_smart_error_handling(invoice_data)

    elif error_context.recovery_strategy == 'garbage_collect_and_retry':
        # Force garbage collection and retry once
        import gc
        gc.collect()
        error_context.retry_count += 1
        return await extract_invoice_with_smart_error_handling(invoice_data)

    elif error_context.recovery_strategy == 'return_validation_error':
        # Return structured validation error
        return {
            'success': False,
            'error_type': 'validation_error',
            'error_message': error_context.error_message,
            'requires_manual_review': True
        }

    else:
        # Default: return error context for caller to handle
        return error_context
```

### 2. Proactive Error Prevention

```python
class InputValidator:
    """Comprehensive input validation to prevent errors before they occur."""

    @staticmethod
    def validate_invoice_data(data: Any) -> Dict[str, Any]:
        """Validate invoice data comprehensively to prevent downstream errors."""

        validation_result = {
            'is_valid': True,
            'errors': [],
            'warnings': [],
            'normalized_data': {}
        }

        # Type validation
        if not isinstance(data, dict):
            validation_result['errors'].append(
                f"Expected dict, got {type(data).__name__}"
            )
            validation_result['is_valid'] = False
            return validation_result

        # Required field validation
        required_fields = ['extracted_text', 'filename', 'content_type']
        for field in required_fields:
            if field not in data:
                validation_result['errors'].append(f"Missing required field: {field}")
                validation_result['is_valid'] = False
            elif data[field] is None:
                validation_result['errors'].append(f"Field {field} cannot be None")
                validation_result['is_valid'] = False

        if not validation_result['is_valid']:
            return validation_result

        # Content validation
        extracted_text = data['extracted_text']
        if len(extracted_text.strip()) < 20:
            validation_result['warnings'].append(
                f"Extracted text very short: {len(extracted_text)} chars"
            )

        # Filename validation
        filename = data['filename']
        if not filename.lower().endswith(('.pdf', '.png', '.jpg', '.jpeg')):
            validation_result['warnings'].append(
                f"Unexpected file type: {filename}"
            )

        # Normalize data to prevent processing errors
        validation_result['normalized_data'] = {
            'extracted_text': extracted_text.strip(),
            'filename': filename.strip(),
            'content_type': data['content_type'].lower().strip(),
            'file_size': data.get('file_size', 0),
            'extraction_confidence': data.get('extraction_confidence', 0.5)
        }

        return validation_result

    @staticmethod
    def validate_llm_response(response: Any, expected_schema: Dict[str, type]) -> Dict[str, Any]:
        """Validate LLM response to prevent parsing errors."""

        validation_result = {
            'is_valid': True,
            'errors': [],
            'parsed_data': {}
        }

        # Basic type check
        if not isinstance(response, (dict, str)):
            validation_result['errors'].append(
                f"Expected dict or str, got {type(response).__name__}"
            )
            validation_result['is_valid'] = False
            return validation_result

        # Parse if string
        if isinstance(response, str):
            try:
                response = json.loads(response)
            except json.JSONDecodeError as e:
                validation_result['errors'].append(f"Invalid JSON: {e}")
                validation_result['is_valid'] = False
                return validation_result

        # Schema validation
        for field_name, expected_type in expected_schema.items():
            if field_name not in response:
                validation_result['errors'].append(f"Missing field: {field_name}")
                continue

            field_value = response[field_name]
            if not isinstance(field_value, expected_type):
                validation_result['errors'].append(
                    f"Field {field_name}: expected {expected_type.__name__}, got {type(field_value).__name__}"
                )

        validation_result['is_valid'] = len(validation_result['errors']) == 0
        validation_result['parsed_data'] = response

        return validation_result

def process_with_proactive_validation(invoice_data: Any) -> Union[dict, str]:
    """Process invoice with comprehensive upfront validation."""

    # Validate input thoroughly before processing
    validation_result = InputValidator.validate_invoice_data(invoice_data)

    if not validation_result['is_valid']:
        error_message = "Input validation failed: " + "; ".join(validation_result['errors'])
        logging.error(error_message, extra={'validation_errors': validation_result['errors']})
        return error_message

    # Log warnings but continue processing
    if validation_result['warnings']:
        logging.warning(
            "Input validation warnings",
            extra={'validation_warnings': validation_result['warnings']}
        )

    # Use normalized data for processing
    normalized_data = validation_result['normalized_data']

    # Process with confidence that data is valid
    try:
        result = extract_fields_from_validated_data(normalized_data)
        return result
    except Exception as e:
        # This should be rare due to proactive validation
        logging.error(f"Unexpected error after validation: {e}")
        return f"Processing error: {e}"
```

---

## 📊 Debugging Tools and Utilities

### 1. Debugging Decorators

```python
import functools
import time
from typing import Callable, Any

def debug_function_calls(include_args: bool = True, include_result: bool = False):
    """Decorator to debug function calls with detailed logging."""

    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            function_id = f"{func.__module__}.{func.__name__}"
            start_time = time.time()

            # Log function entry
            log_data = {'function': function_id, 'start_time': start_time}

            if include_args:
                log_data['args'] = [str(arg)[:100] for arg in args]
                log_data['kwargs'] = {k: str(v)[:100] for k, v in kwargs.items()}

            logging.debug(f"ENTER {function_id}", extra=log_data)

            try:
                result = func(*args, **kwargs)
                end_time = time.time()
                duration = end_time - start_time

                # Log successful exit
                exit_data = {
                    'function': function_id,
                    'duration_seconds': duration,
                    'success': True
                }

                if include_result:
                    exit_data['result'] = str(result)[:200]

                logging.debug(f"EXIT {function_id}", extra=exit_data)
                return result

            except Exception as e:
                end_time = time.time()
                duration = end_time - start_time

                # Log exception
                error_data = {
                    'function': function_id,
                    'duration_seconds': duration,
                    'success': False,
                    'error_type': type(e).__name__,
                    'error_message': str(e)
                }

                logging.error(f"ERROR {function_id}", extra=error_data)
                raise

        return wrapper
    return decorator

def debug_state_changes(state_attrs: list[str]):
    """Decorator to debug state changes in class methods."""

    def decorator(method: Callable) -> Callable:
        @functools.wraps(method)
        def wrapper(self, *args, **kwargs):
            # Capture state before
            before_state = {attr: getattr(self, attr, None) for attr in state_attrs}

            logging.debug(
                f"STATE BEFORE {method.__name__}",
                extra={'before_state': before_state}
            )

            try:
                result = method(self, *args, **kwargs)

                # Capture state after
                after_state = {attr: getattr(self, attr, None) for attr in state_attrs}

                # Log changes
                changes = {}
                for attr in state_attrs:
                    if before_state[attr] != after_state[attr]:
                        changes[attr] = {
                            'before': before_state[attr],
                            'after': after_state[attr]
                        }

                logging.debug(
                    f"STATE AFTER {method.__name__}",
                    extra={'after_state': after_state, 'changes': changes}
                )

                return result

            except Exception as e:
                logging.error(
                    f"STATE ERROR in {method.__name__}: {e}",
                    extra={'before_state': before_state}
                )
                raise

        return wrapper
    return decorator

# Usage examples
class InvoiceProcessor:
    def __init__(self):
        self.processed_count = 0
        self.error_count = 0
        self.current_invoice_id = None

    @debug_state_changes(['processed_count', 'error_count', 'current_invoice_id'])
    def process_invoice(self, invoice_data: dict) -> dict:
        """Process invoice with state change debugging."""
        self.current_invoice_id = invoice_data.get('id')

        try:
            result = self._do_processing(invoice_data)
            self.processed_count += 1
            return result
        except Exception as e:
            self.error_count += 1
            raise

@debug_function_calls(include_args=True, include_result=True)
def extract_vendor_name(text: str) -> Optional[str]:
    """Extract vendor name with call debugging."""
    # Function implementation
    pass
```

### 2. Runtime Diagnostics

```python
import psutil
import threading
from dataclasses import dataclass
from typing import Dict

@dataclass
class SystemDiagnostics:
    """System resource diagnostics for debugging performance issues."""
    cpu_percent: float
    memory_percent: float
    memory_available_mb: int
    disk_usage_percent: float
    active_threads: int
    open_files: int
    timestamp: datetime

class DiagnosticCollector:
    """Collect system diagnostics for debugging complex issues."""

    def __init__(self):
        self.diagnostics_history = []
        self.collection_interval = 5  # seconds
        self._collecting = False
        self._collection_thread = None

    def start_collection(self) -> None:
        """Start collecting diagnostics in background."""
        if self._collecting:
            return

        self._collecting = True
        self._collection_thread = threading.Thread(target=self._collect_loop)
        self._collection_thread.daemon = True
        self._collection_thread.start()

        logging.info("Started diagnostic collection")

    def stop_collection(self) -> None:
        """Stop collecting diagnostics."""
        self._collecting = False
        if self._collection_thread:
            self._collection_thread.join(timeout=1)

        logging.info("Stopped diagnostic collection")

    def _collect_loop(self) -> None:
        """Background loop to collect diagnostics."""
        while self._collecting:
            try:
                diagnostics = self._collect_current_diagnostics()
                self.diagnostics_history.append(diagnostics)

                # Keep only last 100 entries
                if len(self.diagnostics_history) > 100:
                    self.diagnostics_history.pop(0)

            except Exception as e:
                logging.warning(f"Failed to collect diagnostics: {e}")

            time.sleep(self.collection_interval)

    def _collect_current_diagnostics(self) -> SystemDiagnostics:
        """Collect current system diagnostics."""
        memory = psutil.virtual_memory()
        disk = psutil.disk_usage('/')

        return SystemDiagnostics(
            cpu_percent=psutil.cpu_percent(),
            memory_percent=memory.percent,
            memory_available_mb=memory.available // 1024 // 1024,
            disk_usage_percent=disk.percent,
            active_threads=threading.active_count(),
            open_files=len(psutil.Process().open_files()),
            timestamp=datetime.now()
        )

    def get_diagnostics_summary(self) -> Dict[str, Any]:
        """Get summary of collected diagnostics for debugging."""
        if not self.diagnostics_history:
            return {'error': 'No diagnostics collected'}

        cpu_values = [d.cpu_percent for d in self.diagnostics_history]
        memory_values = [d.memory_percent for d in self.diagnostics_history]

        return {
            'collection_period': {
                'start': self.diagnostics_history[0].timestamp.isoformat(),
                'end': self.diagnostics_history[-1].timestamp.isoformat(),
                'sample_count': len(self.diagnostics_history)
            },
            'cpu_usage': {
                'min': min(cpu_values),
                'max': max(cpu_values),
                'avg': sum(cpu_values) / len(cpu_values)
            },
            'memory_usage': {
                'min': min(memory_values),
                'max': max(memory_values),
                'avg': sum(memory_values) / len(memory_values)
            },
            'current_state': self.diagnostics_history[-1].__dict__
        }

# Usage for debugging performance issues
diagnostics = DiagnosticCollector()

async def debug_performance_issue():
    """Debug performance issue with comprehensive diagnostics."""

    # Start collecting diagnostics
    diagnostics.start_collection()

    try:
        # Run the problematic operation
        start_time = time.time()
        result = await problematic_operation()
        end_time = time.time()

        # Stop collecting and analyze
        diagnostics.stop_collection()

        # Log comprehensive debugging information
        logging.info(
            f"Performance debugging completed",
            extra={
                'operation_duration': end_time - start_time,
                'system_diagnostics': diagnostics.get_diagnostics_summary(),
                'operation_result': str(result)[:100]
            }
        )

    except Exception as e:
        diagnostics.stop_collection()

        # Log error with system context
        logging.error(
            f"Operation failed with system context",
            extra={
                'error': str(e),
                'system_diagnostics': diagnostics.get_diagnostics_summary()
            }
        )
        raise
```

---

## 📋 Debugging and Error Handling Checklist

### Pre-Development Error Prevention

**Design Phase:**

- [ ] Identify all possible failure modes for each function
- [ ] Define error recovery strategies for each failure type
- [ ] Specify input validation requirements
- [ ] Plan logging strategy for debugging complex workflows
- [ ] Design error propagation strategy (when to catch, when to propagate)

**Input Validation:**

- [ ] Validate all inputs at function boundaries
- [ ] Check for None/null values explicitly
- [ ] Validate data types and ranges
- [ ] Sanitize string inputs to prevent injection attacks
- [ ] Validate business rules before processing

### During Development Debugging

**Systematic Debugging:**

- [ ] Use scientific method: hypothesis, test, analyze
- [ ] Create reproducible test cases for bugs
- [ ] Log sufficient context for post-mortem analysis
- [ ] Use rubber duck debugging for complex logic
- [ ] Add debugging decorators for function call tracing

**Error Handling Implementation:**

- [ ] Catch specific exception types, not generic Exception
- [ ] Handle errors at the appropriate level
- [ ] Provide meaningful error messages to users
- [ ] Log full context for debugging (but not sensitive data)
- [ ] Implement retry logic for transient failures

### Post-Development Verification

**Error Handling Testing:**

- [ ] Test all error paths with unit tests
- [ ] Verify error messages are helpful and actionable
- [ ] Test retry logic with simulated failures
- [ ] Verify sensitive data is not logged in errors
- [ ] Test error recovery strategies work as expected

**Production Monitoring:**

- [ ] Set up alerts for critical errors
- [ ] Monitor error rates and patterns
- [ ] Review error logs regularly for improvement opportunities
- [ ] Track error resolution times
- [ ] Update error handling based on production experience

---

**Remember: Good debugging is systematic, and good error handling is proactive. Plan for failure, make debugging easy, and always provide a path to recovery! 🔍🛡️**
