# Project Architecture Guide — LangGraph/LangSmith Project

## 🏗️ Comprehensive Architecture Standards & Patterns

**This guide defines the architectural standards, coding conventions, and design patterns for our Python LangGraph project with LangSmith tracing.**

---

## 1. Python Code Standards & Conventions

### Import Structure (2025 Style)

```python
"""Module docstring describing the module's purpose and key components.

This module handles invoice data extraction using a hybrid approach
combining pypdf for fast extraction with LLM fallback for complex documents.
"""

# Standard library imports (alphabetical)
import asyncio
import logging
import os
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Dict, List, Optional, Sequence, Union

# Third-party imports (alphabetical by package)
import httpx
import pytest
from langchain_openai import ChatOpenAI
from googleapiclient.discovery import build
from pydantic import BaseModel, Field, validator

# Local imports (relative imports, then absolute)
from ..models.state import WorkflowState
from ..models.schemas import InvoiceData, ValidationResult
from .base_extractor import BaseExtractor
from .validation import BusinessRuleValidator

# Module-level constants
logger = logging.getLogger(__name__)

DEFAULT_CONFIDENCE_THRESHOLD = 0.7
MAX_RETRY_ATTEMPTS = 3
```

### Type Hints & Documentation Standards

```python
from typing import Dict, List, Optional, Union, Literal, TypedDict
from decimal import Decimal

# Use modern type hint syntax (Python 3.9+)
def process_invoices(pdf_files: list[bytes]) -> list[dict[str, Any]]:
    """Process multiple invoice PDFs and return structured data.

    Args:
        pdf_files: List of PDF file contents as bytes

    Returns:
        List of dictionaries containing extracted invoice data

    Raises:
        ValidationError: When PDF format is invalid
        ProcessingError: When extraction fails after retries
    """
    pass

# Use TypedDict for structured dictionaries
class InvoiceExtraction(TypedDict):
    vendor: str
    amount: Decimal
    date: str
    invoice_number: str
    confidence: float
    extraction_method: Literal["pypdf", "llm_enhanced", "manual_fallback"]

# Use Literal for constrained string values
ProcessingStatus = Literal["pending", "processing", "completed", "failed", "manual_review"]

def update_processing_status(invoice_id: str, status: ProcessingStatus) -> None:
    """Update invoice processing status with type safety."""
    pass

# Use Optional for nullable values, Union for multiple types
def extract_amount(text: str, currency: Optional[str] = None) -> Union[Decimal, None]:
    """Extract monetary amount from text with optional currency conversion."""
    pass
```

### Code Quality Standards

```python
# Black formatting (88 character line limit)
def extract_invoice_fields_with_business_validation(
    pdf_content: bytes,
    extraction_config: ExtractionConfig,
    business_rules: BusinessRuleValidator,
) -> InvoiceExtractionResult:
    """Extract and validate invoice fields according to business rules.

    Long function signatures are formatted with one parameter per line
    for better readability and cleaner diffs.
    """
    pass

# isort import organization
# Groups: stdlib, third-party, local
# Alphabetical within groups
# No trailing commas in import lists

# flake8 linting compliance
# - No unused imports or variables
# - No line length violations (88 chars)
# - No complex expressions that hurt readability

# mypy type checking
# - All public functions have type hints
# - No 'Any' types without justification
# - Strict mode enabled for new modules
```

### Docstring Standards (PEP 257 + Business Context)

```python
class InvoiceProcessor:
    """Processes invoice documents with confidence scoring and business validation.

    This class implements a hybrid extraction strategy that combines fast pypdf
    processing with LLM-enhanced extraction for complex or scanned documents.

    Business Context:
        Used in accounts payable automation to convert unstructured invoice PDFs
        into structured data for ERP integration. Maintains 95% accuracy on
        invoices from known vendors.

    Architecture:
        - Primary extraction: pypdf for standard digital PDFs
        - Fallback extraction: ChatGPT for poor quality/scanned PDFs
        - Validation: Business rules + confidence scoring
        - Output: Structured data with field-level confidence

    Performance:
        - Standard invoices: 2-5 seconds processing time
        - Complex invoices: 5-15 seconds with LLM fallback
        - Memory usage: ~3x PDF file size during processing

    Attributes:
        llm_client: ChatOpenAI instance for enhanced extraction
        confidence_threshold: Minimum confidence for auto-approval (default 0.7)
        business_validator: Validates extracted data against business rules
        extraction_stats: Tracks processing metrics for monitoring

    Example:
        >>> processor = InvoiceProcessor(confidence_threshold=0.8)
        >>> pdf_data = Path("invoice.pdf").read_bytes()
        >>> result = await processor.process(pdf_data)
        >>> if result.confidence >= 0.8:
        ...     approve_for_processing(result.data)
        ... else:
        ...     queue_for_manual_review(result.data, result.issues)
    """

    def __init__(
        self,
        llm_client: ChatOpenAI,
        confidence_threshold: float = 0.7,
        business_validator: Optional[BusinessRuleValidator] = None,
    ):
        """Initialize invoice processor with configuration.

        Args:
            llm_client: Configured ChatOpenAI instance for enhanced extraction.
                       Should use temperature=0 for consistent results.
            confidence_threshold: Minimum confidence score for automatic approval.
                                 Based on production data: 0.7 = 35% manual review,
                                 0.8 = 15% manual review, 0.9 = 5% manual review.
            business_validator: Optional validator for business rules.
                              If None, uses default validation rules.
        """
        self.llm_client = llm_client
        self.confidence_threshold = confidence_threshold
        self.business_validator = business_validator or BusinessRuleValidator()
        self.extraction_stats = ExtractionStats()

        # Configure LLM for consistent extraction
        if hasattr(llm_client, 'temperature') and llm_client.temperature != 0:
            logger.warning("LLM temperature should be 0 for consistent extraction results")

    async def process(self, pdf_data: bytes) -> InvoiceExtractionResult:
        """Process invoice PDF and return structured data with confidence scoring.

        Implements hybrid extraction strategy:
        1. Attempt fast pypdf extraction
        2. Assess extraction quality
        3. Fall back to LLM enhancement if needed
        4. Apply business rule validation
        5. Calculate confidence scores

        Args:
            pdf_data: PDF file content as bytes. Must be valid PDF format.
                     Size limit: 25MB for performance reasons.

        Returns:
            InvoiceExtractionResult containing:
            - extracted_data: Structured invoice fields
            - confidence: Overall confidence score (0.0-1.0)
            - field_confidence: Per-field confidence scores
            - validation_issues: List of business rule violations
            - processing_metadata: Extraction method, timing, etc.

        Raises:
            ValidationError: PDF format invalid or exceeds size limits
            ExtractionError: All extraction methods failed
            TimeoutError: Processing exceeded 30 second timeout

        Example:
            >>> result = await processor.process(pdf_bytes)
            >>> print(f"Extracted: {result.extracted_data}")
            >>> print(f"Confidence: {result.confidence:.2%}")
            >>> if result.validation_issues:
            ...     print(f"Issues: {result.validation_issues}")
        """
        # Implementation follows...
        pass
```

---

## 2. LangGraph/LangSmith Architecture Patterns

### Node Contract Standards

```python
from pydantic import BaseModel, Field
from typing import Dict, Any
from enum import Enum

class NodeStatus(str, Enum):
    """Standard status values for node execution."""
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    RETRYING = "retrying"

class WorkflowState(BaseModel):
    """Standard workflow state schema for all nodes.

    This schema ensures consistent state management across
    all nodes in the invoice processing graph.
    """

    # Core workflow tracking
    user_id: str = Field(..., description="User identifier for audit trail")
    workflow_id: str = Field(..., description="Unique workflow instance ID")
    node_sequence: list[str] = Field(default_factory=list, description="Sequence of completed nodes")

    # Processing status
    status: NodeStatus = Field(default=NodeStatus.PENDING, description="Current processing status")
    error_count: int = Field(default=0, description="Number of errors encountered")
    last_error: Optional[str] = Field(default=None, description="Most recent error message")

    # Data payload (varies by workflow stage)
    pdf_data: Optional[bytes] = Field(default=None, description="Original PDF content")
    extracted_text: Optional[str] = Field(default=None, description="Extracted text from PDF")
    invoice_data: Optional[Dict[str, Any]] = Field(default=None, description="Structured invoice data")

    # Confidence and validation
    confidence: float = Field(default=0.0, ge=0.0, le=1.0, description="Overall confidence score")
    validation_status: Optional[str] = Field(default=None, description="Validation result status")
    validation_issues: list[str] = Field(default_factory=list, description="List of validation issues")

    # Processing metadata
    processing_start_time: Optional[datetime] = Field(default=None, description="Processing start timestamp")
    processing_duration: Optional[float] = Field(default=None, description="Processing duration in seconds")
    extraction_method: Optional[str] = Field(default=None, description="Method used for extraction")

    # Output tracking
    sheets_row_id: Optional[str] = Field(default=None, description="ID of created sheets row")
    notification_sent: bool = Field(default=False, description="Whether notification was sent")

    class Config:
        """Pydantic configuration."""
        use_enum_values = True
        validate_assignment = True
        extra = "forbid"  # Prevent additional fields

# Node implementation template
async def pdf_extraction_node(state: WorkflowState) -> WorkflowState:
    """Extract text and metadata from PDF document.

    Node Responsibilities:
    - Validate PDF format and size
    - Extract text using hybrid pypdf + LLM approach
    - Calculate extraction confidence
    - Update state with results
    - Handle errors gracefully with retry logic

    Input State Requirements:
    - pdf_data: Must be present and valid PDF bytes
    - user_id: Required for audit trail

    Output State Updates:
    - extracted_text: Extracted text content
    - pdf_metadata: Document metadata (pages, size, etc.)
    - confidence: Extraction confidence score
    - extraction_method: Method used (pypdf, llm_enhanced, etc.)
    - status: Updated to completed or failed

    Error Handling:
    - Corrupted PDFs: Return error with actionable message
    - Size limits: Reject files >25MB with clear guidance
    - Extraction failures: Try fallback methods before failing

    Performance Requirements:
    - Standard PDFs: Complete within 5 seconds
    - Complex PDFs: Complete within 15 seconds with LLM
    - Memory usage: Maximum 3x PDF file size
    """

    # Input validation
    if not state.pdf_data:
        state.status = NodeStatus.FAILED
        state.last_error = "PDF data is required for extraction"
        return state

    # Size validation
    if len(state.pdf_data) > 25 * 1024 * 1024:  # 25MB limit
        state.status = NodeStatus.FAILED
        state.last_error = "PDF file too large (>25MB). Please use a smaller file."
        return state

    state.status = NodeStatus.PROCESSING
    state.processing_start_time = datetime.utcnow()

    try:
        # Primary extraction attempt
        extraction_result = await extract_text_from_pdf(state.pdf_data)

        # Update state with results
        state.extracted_text = extraction_result.text
        state.confidence = extraction_result.confidence
        state.extraction_method = extraction_result.method
        state.status = NodeStatus.COMPLETED

        # Add to node sequence
        state.node_sequence.append("pdf_extraction_node")

    except Exception as e:
        state.status = NodeStatus.FAILED
        state.error_count += 1
        state.last_error = f"PDF extraction failed: {str(e)}"
        logger.error(f"PDF extraction error for user {state.user_id}: {e}", exc_info=True)

    finally:
        # Calculate processing duration
        if state.processing_start_time:
            duration = (datetime.utcnow() - state.processing_start_time).total_seconds()
            state.processing_duration = duration

    return state
```

### Tracing & Dataset Integration

```python
from langsmith import traceable
from langsmith.client import Client
from typing import Dict, Any

# LangSmith client configuration
langsmith_client = Client(
    api_url="https://api.smith.langchain.com",
    api_key=os.getenv("LANGSMITH_API_KEY")
)

@traceable(
    project_name="invoice_processing",
    tags=["pdf_extraction", "production"],
)
async def extract_invoice_data_with_tracing(
    pdf_data: bytes,
    extraction_config: ExtractionConfig
) -> InvoiceExtractionResult:
    """Extract invoice data with comprehensive LangSmith tracing.

    This function wraps the extraction process with detailed tracing
    for monitoring, debugging, and performance analysis.
    """

    # Trace input metadata (excluding sensitive data)
    trace_metadata = {
        "pdf_size_bytes": len(pdf_data),
        "extraction_method": extraction_config.method,
        "confidence_threshold": extraction_config.confidence_threshold,
        "user_id_hash": hash_user_id(extraction_config.user_id),  # Anonymized
    }

    with langsmith_client.trace(
        name="invoice_extraction",
        inputs=trace_metadata,
        project="invoice_processing"
    ) as trace:

        try:
            # Step 1: PDF text extraction
            with trace.child("pdf_text_extraction"):
                text_result = await extract_text_from_pdf(pdf_data)
                trace.add_outputs({"text_length": len(text_result.text)})

            # Step 2: Structured data extraction
            with trace.child("structured_extraction"):
                structured_result = await extract_structured_data(
                    text_result.text,
                    extraction_config
                )
                trace.add_outputs({
                    "fields_extracted": len(structured_result.data),
                    "confidence": structured_result.confidence
                })

            # Step 3: Business validation
            with trace.child("business_validation"):
                validation_result = await validate_business_rules(structured_result.data)
                trace.add_outputs({
                    "validation_passed": validation_result.is_valid,
                    "issues_count": len(validation_result.issues)
                })

            # Combine results
            final_result = InvoiceExtractionResult(
                data=structured_result.data,
                confidence=structured_result.confidence,
                validation_result=validation_result,
                processing_metadata=text_result.metadata
            )

            # Trace final outputs (with sensitive data redaction)
            trace.add_outputs({
                "success": True,
                "final_confidence": final_result.confidence,
                "requires_manual_review": final_result.confidence < extraction_config.confidence_threshold,
                "vendor_extracted": bool(final_result.data.get("vendor")),  # Boolean, not actual value
                "amount_extracted": bool(final_result.data.get("amount")),
            })

            return final_result

        except Exception as e:
            # Trace errors with context
            trace.add_outputs({
                "success": False,
                "error_type": type(e).__name__,
                "error_message": str(e)
            })
            raise

# Dataset integration for regression testing
def create_langsmith_dataset_entry(
    pdf_data: bytes,
    expected_output: InvoiceExtractionResult,
    description: str
) -> None:
    """Add test case to LangSmith dataset for regression testing."""

    dataset_name = "invoice_extraction_golden_master"

    # Create anonymized input for dataset
    input_data = {
        "pdf_metadata": {
            "size_bytes": len(pdf_data),
            "page_count": get_pdf_page_count(pdf_data),
            "has_text_layer": has_text_layer(pdf_data),
        },
        "extraction_settings": {
            "method": "hybrid",
            "confidence_threshold": 0.7
        }
    }

    # Create expected output (with sensitive data anonymized)
    expected_data = {
        "vendor": anonymize_vendor_name(expected_output.data["vendor"]),
        "amount": expected_output.data["amount"],  # Keep for accuracy testing
        "invoice_number": anonymize_invoice_number(expected_output.data["invoice_number"]),
        "date": expected_output.data["date"],
        "confidence": expected_output.confidence,
        "validation_passed": expected_output.validation_result.is_valid
    }

    # Add to dataset
    langsmith_client.create_example(
        dataset_name=dataset_name,
        inputs=input_data,
        outputs=expected_data,
        metadata={
            "description": description,
            "source": "production_data",
            "anonymized": True,
            "created_date": datetime.utcnow().isoformat()
        }
    )
```

### State Management & Validation

```python
def validate_workflow_state(state: WorkflowState, expected_stage: str) -> None:
    """Validate workflow state meets requirements for given processing stage.

    This helper ensures state consistency across node transitions
    and provides clear error messages for debugging.
    """

    stage_requirements = {
        "post_pdf_extraction": {
            "required_fields": ["extracted_text", "pdf_metadata", "confidence"],
            "confidence_min": 0.1,  # Even failed extractions should have some confidence
            "status_allowed": [NodeStatus.COMPLETED, NodeStatus.FAILED]
        },
        "post_structured_extraction": {
            "required_fields": ["invoice_data", "confidence", "extraction_method"],
            "confidence_min": 0.0,
            "status_allowed": [NodeStatus.COMPLETED, NodeStatus.FAILED]
        },
        "post_validation": {
            "required_fields": ["validation_status", "validation_issues"],
            "confidence_min": 0.0,
            "status_allowed": [NodeStatus.COMPLETED, NodeStatus.FAILED]
        },
        "post_output": {
            "required_fields": ["sheets_row_id"],
            "confidence_min": 0.0,
            "status_allowed": [NodeStatus.COMPLETED]
        }
    }

    requirements = stage_requirements.get(expected_stage)
    if not requirements:
        raise ValueError(f"Unknown workflow stage: {expected_stage}")

    # Check required fields
    missing_fields = []
    for field in requirements["required_fields"]:
        if not hasattr(state, field) or getattr(state, field) is None:
            missing_fields.append(field)

    if missing_fields:
        raise WorkflowStateError(
            f"Missing required fields for {expected_stage}: {missing_fields}"
        )

    # Check confidence bounds
    if state.confidence < requirements["confidence_min"]:
        raise WorkflowStateError(
            f"Confidence {state.confidence} below minimum {requirements['confidence_min']} for {expected_stage}"
        )

    # Check status
    if state.status not in requirements["status_allowed"]:
        raise WorkflowStateError(
            f"Status {state.status} not allowed for {expected_stage}. Allowed: {requirements['status_allowed']}"
        )

class WorkflowStateError(Exception):
    """Exception for workflow state validation errors."""
    pass

# State transition helpers
def transition_state_to_processing(state: WorkflowState, node_name: str) -> WorkflowState:
    """Standard state transition when starting node processing."""
    state.status = NodeStatus.PROCESSING
    state.processing_start_time = datetime.utcnow()
    return state

def transition_state_to_completed(state: WorkflowState, node_name: str) -> WorkflowState:
    """Standard state transition when completing node successfully."""
    state.status = NodeStatus.COMPLETED
    state.node_sequence.append(node_name)

    if state.processing_start_time:
        duration = (datetime.utcnow() - state.processing_start_time).total_seconds()
        state.processing_duration = duration

    return state

def transition_state_to_failed(state: WorkflowState, node_name: str, error_message: str) -> WorkflowState:
    """Standard state transition when node fails."""
    state.status = NodeStatus.FAILED
    state.error_count += 1
    state.last_error = error_message

    if state.processing_start_time:
        duration = (datetime.utcnow() - state.processing_start_time).total_seconds()
        state.processing_duration = duration

    logger.error(f"Node {node_name} failed for workflow {state.workflow_id}: {error_message}")
    return state
```

---

## 3. Integration Architecture Patterns

### API Client Design Standards

```python
from abc import ABC, abstractmethod
from typing import Protocol, runtime_checkable
import httpx
from tenacity import retry, stop_after_attempt, wait_exponential

@runtime_checkable
class EmailClientProtocol(Protocol):
    """Protocol defining email client interface for dependency injection."""

    async def search_messages(self, query: str) -> list[str]:
        """Search for messages matching query, return message IDs."""
        ...

    async def get_message(self, message_id: str) -> dict:
        """Get message details by ID."""
        ...

    async def download_attachment(self, attachment_id: str) -> bytes:
        """Download attachment content."""
        ...

class BaseAPIClient(ABC):
    """Abstract base class for API clients with common functionality.

    Provides standard patterns for:
    - Authentication management
    - Rate limiting and retries
    - Error handling and logging
    - Request/response tracing
    """

    def __init__(
        self,
        base_url: str,
        credentials: dict,
        timeout: float = 30.0,
        max_retries: int = 3
    ):
        self.base_url = base_url
        self.credentials = credentials
        self.timeout = timeout
        self.max_retries = max_retries
        self._client = httpx.AsyncClient(timeout=timeout)
        self._logger = logging.getLogger(self.__class__.__name__)

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=1, max=10)
    )
    async def _make_request(
        self,
        method: str,
        endpoint: str,
        **kwargs
    ) -> httpx.Response:
        """Make HTTP request with authentication, retries, and error handling."""

        url = f"{self.base_url}/{endpoint.lstrip('/')}"

        # Add authentication headers
        headers = kwargs.get("headers", {})
        headers.update(self._get_auth_headers())
        kwargs["headers"] = headers

        self._logger.debug(f"Making {method} request to {url}")

        try:
            response = await self._client.request(method, url, **kwargs)
            response.raise_for_status()
            return response

        except httpx.HTTPStatusError as e:
            self._logger.error(f"HTTP {e.response.status_code} error: {e.response.text}")

            # Handle specific error cases
            if e.response.status_code == 401:
                await self._refresh_credentials()
                raise AuthenticationError("Authentication failed, credentials refreshed")
            elif e.response.status_code == 429:
                raise RateLimitError("Rate limit exceeded, retry with backoff")
            else:
                raise APIError(f"API request failed: {e.response.status_code}")

        except httpx.TimeoutException:
            self._logger.error(f"Request timeout for {url}")
            raise TimeoutError("Request timed out")

    @abstractmethod
    async def _get_auth_headers(self) -> dict:
        """Get authentication headers for requests."""
        pass

    @abstractmethod
    async def _refresh_credentials(self) -> None:
        """Refresh authentication credentials."""
        pass

class GmailClient(BaseAPIClient):
    """Gmail API client with robust error handling and rate limiting.

    Production Requirements:
    - Handle quota exhaustion gracefully
    - Refresh OAuth tokens automatically
    - Batch requests where possible
    - Maintain request logs for debugging

    Rate Limits:
    - 250 queries per user per 100 seconds
    - 1 billion quota units per day
    - Batch operations reduce quota usage
    """

    def __init__(self, credentials: dict, user_email: str):
        super().__init__(
            base_url="https://gmail.googleapis.com/gmail/v1",
            credentials=credentials,
            timeout=30.0,
            max_retries=3
        )
        self.user_email = user_email
        self._access_token = None
        self._token_expires_at = None

    async def search_messages(
        self,
        query: str,
        max_results: int = 500,
        include_spam_trash: bool = False
    ) -> list[str]:
        """Search Gmail messages with optimized query patterns.

        Query Optimization Tips:
        - Use 'has:attachment' for attachment filtering
        - Use 'after:YYYY/MM/DD' for date ranges (not 'newer_than')
        - Combine filters: 'has:attachment after:2025/01/01 subject:invoice'
        - Avoid wildcards (*) which are slow and quota-expensive

        Args:
            query: Gmail search query using Gmail search syntax
            max_results: Maximum number of results (default 500, max 500 per request)
            include_spam_trash: Include spam and trash in results

        Returns:
            List of message IDs matching the query

        Raises:
            RateLimitError: When quota is exceeded
            AuthenticationError: When authentication fails
            APIError: For other API errors
        """

        params = {
            "q": query,
            "maxResults": min(max_results, 500),  # Gmail API limit
            "includeSpamTrash": include_spam_trash
        }

        try:
            response = await self._make_request(
                "GET",
                f"users/{self.user_email}/messages",
                params=params
            )

            data = response.json()
            messages = data.get("messages", [])
            message_ids = [msg["id"] for msg in messages]

            # Handle pagination if needed
            next_page_token = data.get("nextPageToken")
            if next_page_token and len(message_ids) < max_results:
                # Recursively fetch additional pages
                remaining = max_results - len(message_ids)
                additional_ids = await self._fetch_next_page(
                    query, next_page_token, remaining
                )
                message_ids.extend(additional_ids)

            self._logger.info(f"Found {len(message_ids)} messages for query: {query}")
            return message_ids

        except Exception as e:
            self._logger.error(f"Search failed for query '{query}': {e}")
            raise

    async def get_message(
        self,
        message_id: str,
        format: str = "full",
        metadata_headers: list[str] = None
    ) -> dict:
        """Get Gmail message with specified format and metadata.

        Args:
            message_id: Gmail message ID
            format: Message format (minimal, full, raw, metadata)
            metadata_headers: List of headers to include (when format=metadata)

        Returns:
            Message data with thread, headers, body, and attachments
        """

        params = {"format": format}
        if metadata_headers:
            params["metadataHeaders"] = metadata_headers

        try:
            response = await self._make_request(
                "GET",
                f"users/{self.user_email}/messages/{message_id}",
                params=params
            )

            message_data = response.json()

            # Enrich with attachment information
            attachments = self._extract_attachment_info(message_data)
            message_data["attachments_processed"] = attachments

            return message_data

        except Exception as e:
            self._logger.error(f"Failed to get message {message_id}: {e}")
            raise

    async def download_attachment(
        self,
        message_id: str,
        attachment_id: str
    ) -> bytes:
        """Download Gmail message attachment.

        Args:
            message_id: Gmail message ID containing the attachment
            attachment_id: Specific attachment ID to download

        Returns:
            Attachment content as bytes
        """

        try:
            response = await self._make_request(
                "GET",
                f"users/{self.user_email}/messages/{message_id}/attachments/{attachment_id}"
            )

            attachment_data = response.json()

            # Gmail returns base64url-encoded data
            import base64
            encoded_data = attachment_data["data"]
            # Add padding if needed for base64 decoding
            padding = 4 - len(encoded_data) % 4
            if padding != 4:
                encoded_data += "=" * padding

            decoded_data = base64.urlsafe_b64decode(encoded_data)

            self._logger.debug(f"Downloaded attachment {attachment_id}, size: {len(decoded_data)} bytes")
            return decoded_data

        except Exception as e:
            self._logger.error(f"Failed to download attachment {attachment_id}: {e}")
            raise

    def _extract_attachment_info(self, message_data: dict) -> list[dict]:
        """Extract attachment metadata from message data."""

        attachments = []
        payload = message_data.get("payload", {})

        # Recursive function to find attachments in parts
        def extract_from_parts(parts):
            for part in parts:
                if part.get("filename"):
                    # This part has a filename, likely an attachment
                    body = part.get("body", {})
                    if body.get("attachmentId"):
                        attachments.append({
                            "filename": part["filename"],
                            "mimeType": part.get("mimeType"),
                            "size": body.get("size", 0),
                            "attachmentId": body["attachmentId"]
                        })

                # Check nested parts
                nested_parts = part.get("parts", [])
                if nested_parts:
                    extract_from_parts(nested_parts)

        # Start extraction from payload
        if payload.get("parts"):
            extract_from_parts(payload["parts"])

        return attachments

    async def _get_auth_headers(self) -> dict:
        """Get OAuth2 authentication headers."""

        if not self._access_token or self._token_expired():
            await self._refresh_credentials()

        return {"Authorization": f"Bearer {self._access_token}"}

    async def _refresh_credentials(self) -> None:
        """Refresh OAuth2 access token."""

        # Implementation depends on OAuth flow used
        # This is a simplified version
        refresh_token = self.credentials.get("refresh_token")
        client_id = self.credentials.get("client_id")
        client_secret = self.credentials.get("client_secret")

        if not all([refresh_token, client_id, client_secret]):
            raise AuthenticationError("Missing OAuth credentials for token refresh")

        # Make token refresh request
        token_url = "https://oauth2.googleapis.com/token"
        data = {
            "grant_type": "refresh_token",
            "refresh_token": refresh_token,
            "client_id": client_id,
            "client_secret": client_secret
        }

        async with httpx.AsyncClient() as client:
            response = await client.post(token_url, data=data)
            response.raise_for_status()

            token_data = response.json()
            self._access_token = token_data["access_token"]
            expires_in = token_data.get("expires_in", 3600)
            self._token_expires_at = datetime.utcnow() + timedelta(seconds=expires_in)

            self._logger.info("OAuth token refreshed successfully")

    def _token_expired(self) -> bool:
        """Check if current access token is expired."""
        if not self._token_expires_at:
            return True
        return datetime.utcnow() >= self._token_expires_at

# Custom exceptions for API client
class APIError(Exception):
    """Base exception for API errors."""
    pass

class AuthenticationError(APIError):
    """Exception for authentication failures."""
    pass

class RateLimitError(APIError):
    """Exception for rate limit violations."""
    pass
```

### Service Layer Architecture

```python
from typing import Protocol, runtime_checkable
from dataclasses import dataclass
from enum import Enum

class ServiceResult(Enum):
    """Standard result types for service operations."""
    SUCCESS = "success"
    FAILURE = "failure"
    PARTIAL_SUCCESS = "partial_success"
    REQUIRES_RETRY = "requires_retry"

@dataclass
class ServiceResponse:
    """Standard response format for service operations."""
    result: ServiceResult
    data: Any = None
    error_message: Optional[str] = None
    error_code: Optional[str] = None
    metadata: dict = None

    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}

@runtime_checkable
class ExtractionServiceProtocol(Protocol):
    """Protocol for text extraction services."""

    async def extract_text(self, pdf_data: bytes) -> ServiceResponse:
        """Extract text from PDF data."""
        ...

    async def extract_fields(self, text: str) -> ServiceResponse:
        """Extract structured fields from text."""
        ...

class TextExtractionService:
    """Service for extracting text and structured data from PDFs.

    Implements hybrid extraction strategy with multiple fallback options
    for maximum reliability and accuracy.

    Service Architecture:
    - Primary: pypdf for fast digital PDF text extraction
    - Fallback 1: OCR with pytesseract for scanned documents
    - Fallback 2: LLM-enhanced extraction for complex layouts
    - Quality assessment at each stage to determine best result
    """

    def __init__(
        self,
        llm_client: ChatOpenAI,
        ocr_enabled: bool = True,
        quality_threshold: float = 0.7
    ):
        self.llm_client = llm_client
        self.ocr_enabled = ocr_enabled
        self.quality_threshold = quality_threshold
        self._logger = logging.getLogger(__name__)

    async def extract_text(self, pdf_data: bytes) -> ServiceResponse:
        """Extract text using hybrid approach with quality assessment.

        Strategy:
        1. Attempt fast pypdf extraction
        2. Assess text quality (length, readability, structure)
        3. If quality insufficient, try OCR extraction
        4. If still poor quality, use LLM enhancement
        5. Return best result with confidence score

        Args:
            pdf_data: PDF file content as bytes

        Returns:
            ServiceResponse with extracted text and metadata
        """

        if not pdf_data or len(pdf_data) == 0:
            return ServiceResponse(
                result=ServiceResult.FAILURE,
                error_message="PDF data is empty",
                error_code="EMPTY_INPUT"
            )

        # Size validation (25MB limit)
        if len(pdf_data) > 25 * 1024 * 1024:
            return ServiceResponse(
                result=ServiceResult.FAILURE,
                error_message="PDF file too large (>25MB)",
                error_code="FILE_TOO_LARGE"
            )

        extraction_attempts = []

        # Attempt 1: Fast pypdf extraction
        try:
            pypdf_result = await self._extract_with_pypdf(pdf_data)
            extraction_attempts.append(pypdf_result)

            # Check if quality is sufficient
            if pypdf_result.metadata.get("quality_score", 0) >= self.quality_threshold:
                self._logger.info("pypdf extraction quality sufficient")
                return pypdf_result

        except Exception as e:
            self._logger.warning(f"pypdf extraction failed: {e}")

        # Attempt 2: OCR extraction (if enabled and pypdf quality poor)
        if self.ocr_enabled:
            try:
                ocr_result = await self._extract_with_ocr(pdf_data)
                extraction_attempts.append(ocr_result)

                if ocr_result.metadata.get("quality_score", 0) >= self.quality_threshold:
                    self._logger.info("OCR extraction quality sufficient")
                    return ocr_result

            except Exception as e:
                self._logger.warning(f"OCR extraction failed: {e}")

        # Attempt 3: LLM-enhanced extraction
        try:
            # Use best previous attempt as input for LLM enhancement
            best_attempt = max(extraction_attempts,
                             key=lambda x: x.metadata.get("quality_score", 0))

            llm_result = await self._enhance_with_llm(
                pdf_data,
                best_attempt.data if best_attempt.data else ""
            )

            self._logger.info("Using LLM-enhanced extraction")
            return llm_result

        except Exception as e:
            self._logger.error(f"LLM enhancement failed: {e}")

        # If all methods failed, return best attempt or error
        if extraction_attempts:
            best_result = max(extraction_attempts,
                            key=lambda x: x.metadata.get("quality_score", 0))
            best_result.result = ServiceResult.PARTIAL_SUCCESS
            return best_result
        else:
            return ServiceResponse(
                result=ServiceResult.FAILURE,
                error_message="All extraction methods failed",
                error_code="EXTRACTION_FAILED"
            )

    async def _extract_with_pypdf(self, pdf_data: bytes) -> ServiceResponse:
        """Extract text using pypdf library."""

        import pypdf
        from io import BytesIO

        try:
            pdf_reader = pypdf.PdfReader(BytesIO(pdf_data))

            # Extract text from all pages
            text_parts = []
            for page in pdf_reader.pages:
                page_text = page.extract_text()
                if page_text.strip():
                    text_parts.append(page_text)

            full_text = "\n\n".join(text_parts)

            # Assess text quality
            quality_score = self._assess_text_quality(full_text)

            metadata = {
                "method": "pypdf",
                "page_count": len(pdf_reader.pages),
                "text_length": len(full_text),
                "quality_score": quality_score,
                "extraction_time": time.time()
            }

            return ServiceResponse(
                result=ServiceResult.SUCCESS,
                data=full_text,
                metadata=metadata
            )

        except Exception as e:
            return ServiceResponse(
                result=ServiceResult.FAILURE,
                error_message=f"pypdf extraction failed: {str(e)}",
                error_code="PYPDF_ERROR"
            )

    def _assess_text_quality(self, text: str) -> float:
        """Assess extracted text quality using multiple heuristics.

        Quality indicators:
        - Text length (longer usually better for invoices)
        - Ratio of alphanumeric to special characters
        - Presence of common invoice keywords
        - Line structure and formatting

        Returns:
            Quality score between 0.0 and 1.0
        """

        if not text or len(text.strip()) == 0:
            return 0.0

        score = 0.0

        # Length score (invoices typically have substantial text)
        length_score = min(len(text) / 1000, 1.0)  # Normalize to 1000 chars
        score += length_score * 0.3

        # Character composition score
        alphanumeric_chars = sum(1 for c in text if c.isalnum())
        char_ratio = alphanumeric_chars / len(text) if text else 0
        score += char_ratio * 0.3

        # Invoice keyword presence
        invoice_keywords = [
            "invoice", "bill", "total", "amount", "date", "vendor",
            "payment", "due", "subtotal", "tax", "description"
        ]
        text_lower = text.lower()
        keyword_count = sum(1 for keyword in invoice_keywords if keyword in text_lower)
        keyword_score = min(keyword_count / len(invoice_keywords), 1.0)
        score += keyword_score * 0.4

        return min(score, 1.0)
```

---

## 4. Error Handling & Resilience Patterns

### Comprehensive Error Hierarchy

```python
class ProcessingError(Exception):
    """Base exception for processing errors with context."""

    def __init__(
        self,
        message: str,
        error_code: str = None,
        context: dict = None,
        retry_after: int = None
    ):
        super().__init__(message)
        self.message = message
        self.error_code = error_code or self.__class__.__name__.upper()
        self.context = context or {}
        self.retry_after = retry_after
        self.timestamp = datetime.utcnow()

    def to_dict(self) -> dict:
        """Convert exception to dictionary for serialization."""
        return {
            "error_type": self.__class__.__name__,
            "error_code": self.error_code,
            "message": self.message,
            "context": self.context,
            "retry_after": self.retry_after,
            "timestamp": self.timestamp.isoformat()
        }

class ValidationError(ProcessingError):
    """Errors related to data validation."""
    pass

class ExtractionError(ProcessingError):
    """Errors during text or data extraction."""
    pass

class APIError(ProcessingError):
    """Errors from external API calls."""
    pass

class RateLimitError(APIError):
    """Specific error for rate limiting."""

    def __init__(self, message: str, retry_after: int = 60):
        super().__init__(
            message=message,
            error_code="RATE_LIMIT_EXCEEDED",
            retry_after=retry_after
        )

class ConfigurationError(ProcessingError):
    """Errors in system configuration."""
    pass

# Error context builders
def build_pdf_error_context(pdf_data: bytes) -> dict:
    """Build error context for PDF processing errors."""
    return {
        "pdf_size_bytes": len(pdf_data) if pdf_data else 0,
        "pdf_is_empty": not pdf_data or len(pdf_data) == 0,
        "pdf_starts_with_header": pdf_data.startswith(b"%PDF") if pdf_data else False
    }

def build_api_error_context(
    endpoint: str,
    status_code: int = None,
    response_text: str = None
) -> dict:
    """Build error context for API errors."""
    return {
        "endpoint": endpoint,
        "status_code": status_code,
        "response_preview": response_text[:200] if response_text else None,
        "is_client_error": 400 <= status_code < 500 if status_code else False,
        "is_server_error": 500 <= status_code < 600 if status_code else False
    }
```

### Retry and Circuit Breaker Patterns

```python
from tenacity import (
    retry,
    stop_after_attempt,
    wait_exponential,
    retry_if_exception_type,
    before_sleep_log
)
import asyncio
from functools import wraps

class CircuitBreaker:
    """Circuit breaker for external service calls."""

    def __init__(
        self,
        failure_threshold: int = 5,
        timeout: int = 60,
        expected_exception: type = Exception
    ):
        self.failure_threshold = failure_threshold
        self.timeout = timeout
        self.expected_exception = expected_exception
        self.failure_count = 0
        self.last_failure_time = None
        self.state = "closed"  # closed, open, half-open

    def __call__(self, func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            if self.state == "open":
                if self._should_attempt_reset():
                    self.state = "half-open"
                else:
                    raise APIError(
                        f"Circuit breaker open for {func.__name__}",
                        error_code="CIRCUIT_BREAKER_OPEN"
                    )

            try:
                result = await func(*args, **kwargs)
                self._on_success()
                return result

            except self.expected_exception as e:
                self._on_failure()
                raise

        return wrapper

    def _should_attempt_reset(self) -> bool:
        """Check if enough time has passed to attempt reset."""
        if not self.last_failure_time:
            return True
        return (datetime.utcnow() - self.last_failure_time).seconds >= self.timeout

    def _on_success(self):
        """Reset circuit breaker on successful call."""
        self.failure_count = 0
        self.state = "closed"

    def _on_failure(self):
        """Increment failure count and open circuit if threshold reached."""
        self.failure_count += 1
        self.last_failure_time = datetime.utcnow()

        if self.failure_count >= self.failure_threshold:
            self.state = "open"

# Example usage with retry and circuit breaker
class ResilientExtractionService:
    """Extraction service with comprehensive error handling."""

    def __init__(self, llm_client: ChatOpenAI):
        self.llm_client = llm_client
        self._logger = logging.getLogger(__name__)

    @CircuitBreaker(failure_threshold=3, timeout=300)  # 5 minute timeout
    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=1, max=10),
        retry=retry_if_exception_type((RateLimitError, TimeoutError)),
        before_sleep=before_sleep_log(logging.getLogger(), logging.WARNING)
    )
    async def extract_with_llm(self, text: str) -> dict:
        """Extract structured data using LLM with resilience patterns."""

        try:
            # Construct prompt for extraction
            prompt = self._build_extraction_prompt(text)

            # Call LLM with timeout
            result = await asyncio.wait_for(
                self.llm_client.ainvoke(prompt),
                timeout=30.0
            )

            # Parse and validate result
            structured_data = self._parse_llm_response(result)

            return structured_data

        except asyncio.TimeoutError:
            raise TimeoutError(
                "LLM extraction timed out after 30 seconds",
                context={"text_length": len(text)}
            )

        except Exception as e:
            # Convert various LLM errors to our error types
            if "rate limit" in str(e).lower():
                raise RateLimitError(
                    "LLM rate limit exceeded",
                    retry_after=60
                )
            elif "authentication" in str(e).lower():
                raise APIError(
                    "LLM authentication failed",
                    error_code="AUTH_FAILED"
                )
            else:
                raise ExtractionError(
                    f"LLM extraction failed: {str(e)}",
                    context={"text_length": len(text)}
                )
```

---

## 5. Configuration Management

### Environment-Based Configuration

```python
from pydantic import BaseSettings, Field, validator
from typing import Optional, List
import os
from pathlib import Path

class DatabaseConfig(BaseSettings):
    """Database configuration settings."""

    host: str = Field(..., env="DB_HOST")
    port: int = Field(5432, env="DB_PORT")
    database: str = Field(..., env="DB_NAME")
    username: str = Field(..., env="DB_USERNAME")
    password: str = Field(..., env="DB_PASSWORD")
    pool_size: int = Field(10, env="DB_POOL_SIZE")
    max_overflow: int = Field(20, env="DB_MAX_OVERFLOW")

    @property
    def connection_string(self) -> str:
        """Build database connection string."""
        return f"postgresql://{self.username}:{self.password}@{self.host}:{self.port}/{self.database}"

class LLMConfig(BaseSettings):
    """LLM service configuration."""

    api_key: str = Field(..., env="OPENAI_API_KEY")
    model: str = Field("gpt-4o-mini", env="LLM_MODEL")
    temperature: float = Field(0.0, env="LLM_TEMPERATURE")
    max_tokens: int = Field(4000, env="LLM_MAX_TOKENS")
    timeout: float = Field(30.0, env="LLM_TIMEOUT")
    max_retries: int = Field(3, env="LLM_MAX_RETRIES")

    @validator("temperature")
    def validate_temperature(cls, v):
        if not 0.0 <= v <= 2.0:
            raise ValueError("Temperature must be between 0.0 and 2.0")
        return v

    @validator("max_tokens")
    def validate_max_tokens(cls, v):
        if v <= 0 or v > 32000:
            raise ValueError("Max tokens must be between 1 and 32000")
        return v

class ProcessingConfig(BaseSettings):
    """Invoice processing configuration."""

    confidence_threshold: float = Field(0.7, env="CONFIDENCE_THRESHOLD")
    max_pdf_size_mb: int = Field(25, env="MAX_PDF_SIZE_MB")
    enable_ocr: bool = Field(True, env="ENABLE_OCR")
    batch_size: int = Field(10, env="BATCH_SIZE")
    processing_timeout: float = Field(300.0, env="PROCESSING_TIMEOUT")

    # Business rules
    max_invoice_amount: float = Field(100000.0, env="MAX_INVOICE_AMOUNT")
    suspicious_amount_threshold: float = Field(500.0, env="SUSPICIOUS_AMOUNT_THRESHOLD")
    allowed_currencies: List[str] = Field(["USD", "EUR", "GBP"], env="ALLOWED_CURRENCIES")

    @validator("confidence_threshold")
    def validate_confidence_threshold(cls, v):
        if not 0.0 <= v <= 1.0:
            raise ValueError("Confidence threshold must be between 0.0 and 1.0")
        return v

class AppConfig(BaseSettings):
    """Main application configuration."""

    # Environment
    environment: str = Field("development", env="ENVIRONMENT")
    debug: bool = Field(False, env="DEBUG")
    log_level: str = Field("INFO", env="LOG_LEVEL")

    # Service configurations
    database: DatabaseConfig = DatabaseConfig()
    llm: LLMConfig = LLMConfig()
    processing: ProcessingConfig = ProcessingConfig()

    # External services
    gmail_credentials_path: Optional[Path] = Field(None, env="GMAIL_CREDENTIALS_PATH")
    sheets_credentials_path: Optional[Path] = Field(None, env="SHEETS_CREDENTIALS_PATH")
    langsmith_api_key: Optional[str] = Field(None, env="LANGSMITH_API_KEY")

    # Performance settings
    max_concurrent_extractions: int = Field(5, env="MAX_CONCURRENT_EXTRACTIONS")
    worker_count: int = Field(4, env="WORKER_COUNT")

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False

    @validator("environment")
    def validate_environment(cls, v):
        allowed_envs = ["development", "staging", "production"]
        if v not in allowed_envs:
            raise ValueError(f"Environment must be one of {allowed_envs}")
        return v

    @property
    def is_production(self) -> bool:
        """Check if running in production environment."""
        return self.environment == "production"

    @property
    def is_development(self) -> bool:
        """Check if running in development environment."""
        return self.environment == "development"

# Global configuration instance
config = AppConfig()

# Configuration factory for testing
def create_test_config(**overrides) -> AppConfig:
    """Create configuration for testing with overrides."""

    test_settings = {
        "environment": "test",
        "debug": True,
        "log_level": "DEBUG",
        "database": {
            "host": "localhost",
            "database": "test_db",
            "username": "test_user",
            "password": "test_pass"
        },
        "llm": {
            "api_key": "test_key",
            "model": "gpt-3.5-turbo",
            "timeout": 10.0
        },
        "processing": {
            "confidence_threshold": 0.5,  # Lower for testing
            "max_pdf_size_mb": 5,  # Smaller for testing
            "processing_timeout": 30.0
        }
    }

    # Apply overrides
    test_settings.update(overrides)

    return AppConfig(**test_settings)
```

---

## 8. Async Programming Architecture for LangGraph

### 8.1 Async Design Principles

**LangGraph requires full async compliance for production workflows.** All I/O operations must be properly async to avoid blocking the event loop.

#### Core Async Principles:

1. **Async-First Design**: Design all workflow components with async in mind
2. **I/O Boundary Management**: Clearly identify and wrap all I/O operations
3. **Error Propagation**: Maintain error handling through async boundaries
4. **Performance Consideration**: Balance async overhead with responsiveness
5. **Testing Strategy**: Comprehensive async testing at all levels

### 8.2 Async Patterns for External APIs

#### Google API Client Pattern:

```python
"""Async wrapper pattern for Google API clients."""

import asyncio
from typing import Any, Dict, List, Optional
from googleapiclient.discovery import build
from google.auth.credentials import Credentials

class AsyncGoogleAPIClient:
    """Base class for async Google API clients."""

    def __init__(self, service_name: str, version: str, credentials: Credentials):
        self._service_name = service_name
        self._version = version
        self._credentials = credentials
        self._service: Optional[Any] = None

    async def initialize(self) -> None:
        """Initialize the Google API service asynchronously."""
        if self._credentials.expired and self._credentials.refresh_token:
            # Wrap blocking credential refresh
            await asyncio.to_thread(self._credentials.refresh, Request())

        # Wrap blocking service build
        self._service = await asyncio.to_thread(
            build,
            self._service_name,
            self._version,
            credentials=self._credentials,
            cache_discovery=False  # Avoid additional blocking calls
        )

    async def _execute_api_call(self, request) -> Dict[str, Any]:
        """Execute API request asynchronously."""
        try:
            return await asyncio.to_thread(request.execute)
        except Exception as e:
            logger.error(f"❌ API call failed: {e}")
            raise APIError(f"Google API request failed: {e}")

class AsyncGmailClient(AsyncGoogleAPIClient):
    """Async Gmail API client."""

    def __init__(self, credentials: Credentials):
        super().__init__("gmail", "v1", credentials)

    async def get_messages(self, query: str, max_results: int = 10) -> List[Dict[str, Any]]:
        """Get Gmail messages matching query asynchronously."""
        request = self._service.users().messages().list(
            userId='me',
            q=query,
            maxResults=max_results
        )
        return await self._execute_api_call(request)

    async def send_email(self, message_data: Dict[str, Any]) -> Dict[str, Any]:
        """Send email asynchronously."""
        request = self._service.users().messages().send(
            userId='me',
            body=message_data
        )
        return await self._execute_api_call(request)
```

#### Database Operations Pattern:

```python
"""Async database operation patterns."""

import asyncio
from typing import Any, Dict, List, Optional

class AsyncDatabaseClient:
    """Async database client for Google Sheets backend."""

    async def save_record(self, table: str, data: Dict[str, Any]) -> bool:
        """Save record to database table asynchronously."""
        try:
            # Wrap blocking Google Sheets API call
            result = await asyncio.to_thread(
                self._service.worksheets[table].insert_rows,
                [data],
                value_input_option='RAW'
            )

            logger.info(f"✅ Record saved to {table}: {data.get('id', 'unknown')}")
            return True

        except Exception as e:
            logger.error(f"❌ Failed to save record to {table}: {e}")
            raise DatabaseError(f"Save operation failed: {e}")

    async def get_records(self, table: str, filters: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """Retrieve records from database table asynchronously."""
        try:
            # Wrap blocking Google Sheets API call
            records = await asyncio.to_thread(
                self._service.worksheets[table].get_all_records
            )

            # Apply filters if provided
            if filters:
                records = [r for r in records if self._matches_filters(r, filters)]

            logger.info(f"✅ Retrieved {len(records)} records from {table}")
            return records

        except Exception as e:
            logger.error(f"❌ Failed to retrieve records from {table}: {e}")
            raise DatabaseError(f"Query operation failed: {e}")

    async def update_record(self, table: str, record_id: str, updates: Dict[str, Any]) -> bool:
        """Update record in database table asynchronously."""
        try:
            # Find and update record
            records = await self.get_records(table, {"id": record_id})
            if not records:
                raise DatabaseError(f"Record {record_id} not found in {table}")

            # Wrap blocking update operation
            result = await asyncio.to_thread(
                self._service.worksheets[table].update_rows,
                records[0]["_row_number"],
                [updates]
            )

            logger.info(f"✅ Record {record_id} updated in {table}")
            return True

        except Exception as e:
            logger.error(f"❌ Failed to update record {record_id} in {table}: {e}")
            raise DatabaseError(f"Update operation failed: {e}")
```

### 8.3 LangGraph Node Async Patterns

#### Workflow Node Implementation:

```python
"""Async patterns for LangGraph workflow nodes."""

async def process_documents_node(state: WorkflowState) -> WorkflowState:
    """
    Process documents asynchronously in LangGraph workflow.

    Business Context: Document processing step requiring async I/O operations.
    Must maintain async compliance for LangGraph execution.
    """
    try:
        # Get async-enabled dependencies
        database_client = dependencies.get("database_client")
        document_processor = dependencies.get("document_processor")

        # Process documents asynchronously
        processed_docs = []
        for doc in state.documents:
            # Each document processing operation is async
            result = await document_processor.process_document(doc)
            processed_docs.append(result)

            # Log progress to database asynchronously
            await database_client.save_record("processing_log", {
                "document_id": doc.id,
                "status": "processed",
                "timestamp": datetime.utcnow().isoformat(),
                "workflow_id": state.workflow_id
            })

        # Update state with results
        state.processed_documents = processed_docs
        state.current_step = "documents_processed"

        # Save workflow progress asynchronously
        await database_client.save_record("workflow_progress", {
            "workflow_id": state.workflow_id,
            "step": "process_documents",
            "documents_processed": len(processed_docs),
            "timestamp": datetime.utcnow().isoformat()
        })

        logger.info(f"✅ Processed {len(processed_docs)} documents successfully")
        return state

    except Exception as e:
        logger.error(f"❌ Document processing failed: {e}")
        state.error = f"Document processing error: {e}"
        state.current_step = "process_documents_failed"
        return state

async def send_notifications_node(state: WorkflowState) -> WorkflowState:
    """
    Send notifications asynchronously in LangGraph workflow.

    Business Context: Notification system for workflow status updates.
    Requires async email sending and database logging.
    """
    try:
        # Get async-enabled clients
        email_client = dependencies.get("email_client")
        database_client = dependencies.get("database_client")

        # Send notifications asynchronously
        notifications_sent = []
        for recipient in state.notification_recipients:
            # Async email sending
            result = await email_client.send_notification(
                to_email=recipient.email,
                subject=f"Workflow {state.workflow_id} Status Update",
                template="workflow_status",
                data={
                    "workflow_id": state.workflow_id,
                    "status": state.current_step,
                    "documents_count": len(state.processed_documents)
                }
            )

            if result:
                notifications_sent.append(recipient.email)

                # Log notification to database asynchronously
                await database_client.save_record("notifications", {
                    "workflow_id": state.workflow_id,
                    "recipient": recipient.email,
                    "status": "sent",
                    "timestamp": datetime.utcnow().isoformat()
                })

        state.notifications_sent = notifications_sent
        state.current_step = "notifications_complete"

        logger.info(f"✅ Sent {len(notifications_sent)} notifications")
        return state

    except Exception as e:
        logger.error(f"❌ Notification sending failed: {e}")
        state.error = f"Notification error: {e}"
        state.current_step = "notifications_failed"
        return state
```

### 8.4 Dependency Injection for Async Components

#### Async Dependency Setup:

```python
"""Async dependency injection pattern for LangGraph workflows."""

from typing import Dict, Any
import asyncio

class AsyncDependencyContainer:
    """Container for async-enabled dependencies."""

    def __init__(self):
        self._dependencies: Dict[str, Any] = {}
        self._initialized = False

    async def initialize(self) -> None:
        """Initialize all async dependencies."""
        if self._initialized:
            return

        try:
            # Initialize async database client
            database_client = AsyncDatabaseClient()
            await database_client.initialize()
            self._dependencies["database_client"] = database_client

            # Initialize async email client
            email_client = AsyncEmailClient()
            await email_client.initialize()
            self._dependencies["email_client"] = email_client

            # Initialize async Gmail client
            gmail_client = AsyncGmailClient()
            await gmail_client.initialize()
            self._dependencies["gmail_client"] = gmail_client

            # Initialize async document processor
            document_processor = AsyncDocumentProcessor()
            await document_processor.initialize()
            self._dependencies["document_processor"] = document_processor

            self._initialized = True
            logger.info("✅ All async dependencies initialized")

        except Exception as e:
            logger.error(f"❌ Dependency initialization failed: {e}")
            raise DependencyError(f"Failed to initialize async dependencies: {e}")

    def get(self, name: str) -> Any:
        """Get dependency by name."""
        if not self._initialized:
            raise DependencyError("Dependencies not initialized. Call initialize() first.")

        if name not in self._dependencies:
            raise DependencyError(f"Dependency '{name}' not found")

        return self._dependencies[name]

    async def cleanup(self) -> None:
        """Cleanup all dependencies."""
        for name, dependency in self._dependencies.items():
            if hasattr(dependency, 'cleanup'):
                try:
                    await dependency.cleanup()
                    logger.debug(f"✅ Cleaned up {name}")
                except Exception as e:
                    logger.warning(f"⚠️ Failed to cleanup {name}: {e}")

        self._dependencies.clear()
        self._initialized = False

# Global dependency container
dependencies = AsyncDependencyContainer()
```

### 8.5 Async Testing Patterns

#### Async Test Infrastructure:

```python
"""Async testing patterns for LangGraph components."""

import pytest
import asyncio
from unittest.mock import AsyncMock, patch

@pytest.mark.asyncio
async def test_async_database_operations():
    """Test async database operations."""
    # Setup async test database
    test_db = AsyncDatabaseClient()
    await test_db.initialize()

    # Test async save operation
    test_data = {"id": "test_123", "name": "Test Record"}
    result = await test_db.save_record("test_table", test_data)
    assert result is True

    # Test async retrieve operation
    records = await test_db.get_records("test_table", {"id": "test_123"})
    assert len(records) == 1
    assert records[0]["name"] == "Test Record"

    # Cleanup
    await test_db.cleanup()

@pytest.mark.asyncio
async def test_workflow_node_async_execution():
    """Test async workflow node execution."""
    # Mock async dependencies
    mock_database = AsyncMock()
    mock_email = AsyncMock()

    with patch('dependencies.get') as mock_deps:
        mock_deps.side_effect = lambda name: {
            'database_client': mock_database,
            'email_client': mock_email
        }[name]

        # Test workflow node
        initial_state = WorkflowState(
            workflow_id="test_workflow",
            documents=[Document(id="doc_1", content="test")]
        )

        result_state = await process_documents_node(initial_state)

        # Verify async operations were called
        mock_database.save_record.assert_called()
        assert result_state.current_step == "documents_processed"

@pytest.mark.asyncio
async def test_no_blocking_calls():
    """Test that no blocking calls occur during execution."""
    import warnings

    # Capture blocking call warnings
    with warnings.catch_warnings(record=True) as warning_list:
        warnings.simplefilter("always")

        # Run complete workflow
        await run_complete_workflow()

        # Check for blocking call warnings
        blocking_warnings = [
            w for w in warning_list
            if "Blocking call" in str(w.message)
        ]

        assert len(blocking_warnings) == 0, f"Found blocking calls: {blocking_warnings}"

class AsyncTestFixtures:
    """Reusable async test fixtures."""

    @pytest.fixture
    async def async_dependencies():
        """Provide initialized async dependencies for testing."""
        deps = AsyncDependencyContainer()
        await deps.initialize()
        yield deps
        await deps.cleanup()

    @pytest.fixture
    async def mock_async_database():
        """Provide mock async database client."""
        mock_db = AsyncMock(spec=AsyncDatabaseClient)
        mock_db.save_record.return_value = True
        mock_db.get_records.return_value = []
        return mock_db

    @pytest.fixture
    async def workflow_test_state():
        """Provide test workflow state."""
        return WorkflowState(
            workflow_id="test_workflow_123",
            documents=[],
            current_step="initialized"
        )
```

### 8.6 Async Performance and Monitoring

#### Performance Monitoring:

```python
"""Async performance monitoring patterns."""

import time
import asyncio
from functools import wraps
from typing import Callable, Any

def async_performance_monitor(operation_name: str):
    """Decorator to monitor async operation performance."""
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def wrapper(*args, **kwargs) -> Any:
            start_time = time.time()

            try:
                result = await func(*args, **kwargs)
                duration = time.time() - start_time

                logger.info(f"✅ {operation_name} completed in {duration:.2f}s")

                # Log performance metrics
                await log_performance_metric(
                    operation=operation_name,
                    duration=duration,
                    status="success"
                )

                return result

            except Exception as e:
                duration = time.time() - start_time

                logger.error(f"❌ {operation_name} failed after {duration:.2f}s: {e}")

                # Log performance metrics for failures
                await log_performance_metric(
                    operation=operation_name,
                    duration=duration,
                    status="error",
                    error=str(e)
                )

                raise

        return wrapper
    return decorator

async def log_performance_metric(operation: str, duration: float, status: str, error: str = None):
    """Log performance metrics asynchronously."""
    metric_data = {
        "operation": operation,
        "duration": duration,
        "status": status,
        "timestamp": datetime.utcnow().isoformat()
    }

    if error:
        metric_data["error"] = error

    # Log to database asynchronously
    try:
        database_client = dependencies.get("database_client")
        await database_client.save_record("performance_metrics", metric_data)
    except Exception as e:
        logger.warning(f"⚠️ Failed to log performance metric: {e}")

# Usage example
@async_performance_monitor("email_extraction")
async def extract_emails_with_monitoring(query: str) -> List[Dict[str, Any]]:
    """Extract emails with performance monitoring."""
    gmail_client = dependencies.get("gmail_client")
    return await gmail_client.get_messages(query)
```

### 8.7 Async Error Handling and Recovery

#### Comprehensive Async Error Handling:

```python
"""Async error handling and recovery patterns."""

from typing import Optional, Dict, Any, Callable
import asyncio
from enum import Enum

class AsyncOperationResult:
    """Result wrapper for async operations with error context."""

    def __init__(self, success: bool, data: Any = None, error: Optional[Exception] = None):
        self.success = success
        self.data = data
        self.error = error
        self.timestamp = datetime.utcnow()

class RetryStrategy(Enum):
    """Retry strategies for async operations."""
    EXPONENTIAL_BACKOFF = "exponential_backoff"
    FIXED_DELAY = "fixed_delay"
    NO_RETRY = "no_retry"

async def async_retry_operation(
    operation: Callable,
    max_attempts: int = 3,
    strategy: RetryStrategy = RetryStrategy.EXPONENTIAL_BACKOFF,
    base_delay: float = 1.0
) -> AsyncOperationResult:
    """
    Execute async operation with retry logic.

    Business Context: Resilient async operations for critical workflow steps.
    """
    last_error = None

    for attempt in range(max_attempts):
        try:
            result = await operation()
            return AsyncOperationResult(success=True, data=result)

        except Exception as e:
            last_error = e
            logger.warning(f"⚠️ Attempt {attempt + 1}/{max_attempts} failed: {e}")

            if attempt < max_attempts - 1:  # Don't delay after last attempt
                delay = calculate_retry_delay(attempt, strategy, base_delay)
                await asyncio.sleep(delay)

    return AsyncOperationResult(success=False, error=last_error)

def calculate_retry_delay(attempt: int, strategy: RetryStrategy, base_delay: float) -> float:
    """Calculate delay for retry attempt."""
    if strategy == RetryStrategy.EXPONENTIAL_BACKOFF:
        return base_delay * (2 ** attempt)
    elif strategy == RetryStrategy.FIXED_DELAY:
        return base_delay
    else:
        return 0.0

# Circuit breaker pattern for async operations
class AsyncCircuitBreaker:
    """Circuit breaker for async operations."""

    def __init__(self, failure_threshold: int = 5, timeout: float = 60.0):
        self.failure_threshold = failure_threshold
        self.timeout = timeout
        self.failure_count = 0
        self.last_failure_time: Optional[datetime] = None
        self.state = "closed"  # closed, open, half_open

    async def call(self, operation: Callable) -> AsyncOperationResult:
        """Execute operation through circuit breaker."""
        if self.state == "open":
            if self._should_attempt_reset():
                self.state = "half_open"
            else:
                return AsyncOperationResult(
                    success=False,
                    error=Exception("Circuit breaker is open")
                )

        try:
            result = await operation()
            self._on_success()
            return AsyncOperationResult(success=True, data=result)

        except Exception as e:
            self._on_failure()
            return AsyncOperationResult(success=False, error=e)

    def _should_attempt_reset(self) -> bool:
        """Check if circuit breaker should attempt reset."""
        if self.last_failure_time is None:
            return True

        time_since_failure = datetime.utcnow() - self.last_failure_time
        return time_since_failure.total_seconds() >= self.timeout

    def _on_success(self):
        """Handle successful operation."""
        self.failure_count = 0
        self.state = "closed"

    def _on_failure(self):
        """Handle failed operation."""
        self.failure_count += 1
        self.last_failure_time = datetime.utcnow()

        if self.failure_count >= self.failure_threshold:
            self.state = "open"
```

### 8.8 Async Architecture Checklist

#### Pre-Development Checklist:

- [ ] **Identify all I/O operations** that need async wrapping
- [ ] **Design async interfaces** for all external service clients
- [ ] **Plan dependency injection** for async components
- [ ] **Define error handling** strategies for async operations
- [ ] **Create async testing** infrastructure

#### Development Checklist:

- [ ] **All I/O operations** use `asyncio.to_thread()` or native async
- [ ] **All async methods** have `async def` signatures
- [ ] **All async calls** use `await` keyword
- [ ] **Error handling** preserved through async boundaries
- [ ] **Performance monitoring** added for critical async operations

#### Validation Checklist:

- [ ] **LangGraph server starts** without `--allow-blocking` flag
- [ ] **Complete workflows execute** without blocking call errors
- [ ] **All tests pass** in async execution environment
- [ ] **Performance metrics** are within acceptable thresholds
- [ ] **Error handling** works correctly in async context

---

**Remember: Async architecture enables LangGraph's native execution environment while preserving business logic and error handling patterns. Design for async-first, wrap blocking operations appropriately, and test thoroughly in async context! �⚡✅**
