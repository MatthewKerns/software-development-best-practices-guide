# Async Programming Guide for LangGraph Workflows

## 📋 Overview

**This guide provides comprehensive patterns and best practices for async programming in LangGraph workflows, based on real-world experience migrating blocking operations to async-compliant code.**

### Why Async Matters in LangGraph

LangGraph's native execution environment requires **full async compliance** for production workflows. Blocking calls will cause workflow failures and prevent proper execution without the `--allow-blocking` development flag.

### LangGraph Dependency Injection Pattern

**CRITICAL**: LangGraph has a built-in dependency injection system that properly handles blocking calls during initialization:

#### Proper Architecture:

1. **Graph Factory Function** (`graph()`) - Creates graph structure only, no dependency initialization
2. **Dependencies File** (`dependencies_file` in `langgraph.json`) - LangGraph calls this to initialize dependencies
3. **Node Functions** - Receive dependencies via config parameter at runtime

```python
# ✅ CORRECT: Graph factory creates structure only
def graph():
    """Factory function for LangGraph server."""
    return _create_graph_structure_only()

def _create_graph_structure_only():
    """Create graph structure without initializing dependencies."""
    workflow = StateGraph(State)
    # Add nodes directly - dependencies injected at runtime
    workflow.add_node("process_data", process_data_node)
    return workflow.compile()

# ✅ CORRECT: Dependencies initialized separately by LangGraph
async def get_config() -> Dict[str, Any]:
    """LangGraph calls this to initialize dependencies (blocking calls OK here)."""
    deps = await initialize_dependencies()  # Blocking calls allowed
    return {"configurable": deps}
```

#### What NOT to do:

```python
# ❌ WRONG: Don't initialize dependencies in graph factory
def graph():
    deps = asyncio.run(initialize_dependencies())  # Nested event loop error
    return create_graph(deps)
```

### Key Principles

1. **All I/O operations must be async** - Database calls, API requests, file operations
2. **Use `asyncio.to_thread()` for synchronous libraries** - Google API clients, external SDKs
3. **Use LangGraph dependency injection** - Don't initialize dependencies in graph factory
4. **Preserve business logic** - Async migration should not change functionality
5. **Maintain error handling** - Async wrappers must preserve exception handling
6. **Test thoroughly** - Async code behavior can differ from synchronous equivalents

---

## 🚫 Common Blocking Call Patterns

### Blocking Database Operations

```python
# ❌ BLOCKING - Will fail in LangGraph
def save_data(self, data):
    result = self._service.worksheets['Invoice'].insert_rows([data])
    return result

# ❌ BLOCKING - Direct API calls
def get_emails(self):
    messages = self._gmail_service.users().messages().list(userId='me').execute()
    return messages
```

### Blocking Authentication

```python
# ❌ BLOCKING - OAuth token refresh
def refresh_token(self):
    self._credentials.refresh(Request())
    service = build('gmail', 'v1', credentials=self._credentials)
    return service
```

### Blocking File Operations

```python
# ❌ BLOCKING - File I/O without async
def read_config(self):
    with open('config.json', 'r') as f:
        return json.load(f)
```

---

## ✅ Async Migration Patterns

### 1. Database Operations with asyncio.to_thread()

```python
# ✅ ASYNC COMPLIANT - Proper async database operations
async def save_data(self, data: Dict[str, Any]) -> bool:
    """
    Save data to Google Sheets database asynchronously.

    Business Context: Stores workflow data for audit trail and business reporting.
    Uses asyncio.to_thread() to wrap blocking Google Sheets API calls.
    """
    try:
        result = await asyncio.to_thread(
            self._service.worksheets['Invoice'].insert_rows,
            [data],
            value_input_option='RAW'
        )
        logger.info(f"✅ Data saved successfully: {result}")
        return True
    except Exception as e:
        logger.error(f"❌ Failed to save data: {e}")
        raise DatabaseError(f"Save operation failed: {e}")

async def get_data(self, query_params: Dict[str, Any]) -> List[Dict[str, Any]]:
    """
    Retrieve data from Google Sheets database asynchronously.

    Business Context: Queries business data for workflow decision making.
    """
    try:
        result = await asyncio.to_thread(
            self._service.worksheets['Invoice'].get_all_records
        )
        logger.info(f"✅ Retrieved {len(result)} records")
        return result
    except Exception as e:
        logger.error(f"❌ Failed to retrieve data: {e}")
        raise DatabaseError(f"Query operation failed: {e}")
```

### 2. API Client Operations

```python
# ✅ ASYNC COMPLIANT - Gmail API operations
async def get_new_emails(self, query: str, max_results: int = 10) -> List[Dict[str, Any]]:
    """
    Retrieve new emails from Gmail API asynchronously.

    Business Context: Email extraction for document processing workflow.
    Uses asyncio.to_thread() to wrap blocking Gmail API calls.
    """
    try:
        # Wrap the blocking Gmail API call
        messages_result = await asyncio.to_thread(
            self._gmail_service.users().messages().list,
            userId='me',
            q=query,
            maxResults=max_results
        )

        # Execute the API call asynchronously
        messages_data = await asyncio.to_thread(messages_result.execute)

        logger.info(f"✅ Retrieved {len(messages_data.get('messages', []))} emails")
        return messages_data.get('messages', [])

    except Exception as e:
        logger.error(f"❌ Failed to retrieve emails: {e}")
        raise EmailAPIError(f"Gmail API call failed: {e}")

async def send_email(self, to_email: str, subject: str, body: str) -> bool:
    """
    Send email via Gmail API asynchronously.

    Business Context: Notification system for workflow status updates.
    """
    try:
        message = self._create_message(to_email, subject, body)

        # Wrap the blocking send operation
        result = await asyncio.to_thread(
            self._gmail_service.users().messages().send,
            userId='me',
            body=message
        )

        # Execute the send operation asynchronously
        sent_message = await asyncio.to_thread(result.execute)

        logger.info(f"✅ Email sent successfully: {sent_message['id']}")
        return True

    except Exception as e:
        logger.error(f"❌ Failed to send email: {e}")
        raise EmailAPIError(f"Email send operation failed: {e}")
```

### 3. Authentication and Service Building

```python
# ✅ ASYNC COMPLIANT - OAuth authentication
async def get_authenticated_service(self, service_name: str, version: str) -> Any:
    """
    Build authenticated Google API service asynchronously.

    Business Context: Secure API access for business operations.
    Handles token refresh and service initialization without blocking.
    """
    try:
        # Refresh credentials if needed (blocking operation)
        if self._credentials.expired and self._credentials.refresh_token:
            await asyncio.to_thread(self._credentials.refresh, Request())
            logger.info("🔄 OAuth credentials refreshed")

        # Build service client (blocking operation)
        service = await asyncio.to_thread(
            build,
            service_name,
            version,
            credentials=self._credentials,
            cache_discovery=False  # Avoid additional blocking calls
        )

        logger.info(f"✅ {service_name} service built successfully")
        return service

    except Exception as e:
        logger.error(f"❌ Failed to build {service_name} service: {e}")
        raise AuthenticationError(f"Service authentication failed: {e}")
```

### 4. File Operations

```python
# ✅ ASYNC COMPLIANT - File I/O operations
import aiofiles

async def read_config_file(self, config_path: str) -> Dict[str, Any]:
    """
    Read configuration file asynchronously.

    Business Context: Load application configuration without blocking workflow.
    """
    try:
        async with aiofiles.open(config_path, 'r') as f:
            content = await f.read()
            config = json.loads(content)

        logger.info(f"✅ Configuration loaded from {config_path}")
        return config

    except Exception as e:
        logger.error(f"❌ Failed to read config from {config_path}: {e}")
        raise ConfigurationError(f"Config file read failed: {e}")

async def write_log_file(self, log_path: str, log_data: Dict[str, Any]) -> bool:
    """
    Write log data to file asynchronously.

    Business Context: Audit logging for compliance and debugging.
    """
    try:
        async with aiofiles.open(log_path, 'a') as f:
            log_entry = json.dumps(log_data) + '\n'
            await f.write(log_entry)

        logger.info(f"✅ Log written to {log_path}")
        return True

    except Exception as e:
        logger.error(f"❌ Failed to write log to {log_path}: {e}")
        raise LoggingError(f"Log write operation failed: {e}")
```

---

## 🔧 Migration Workflow

### Step 1: Identify Blocking Operations

```bash
# Search for common blocking patterns
grep -r "\.execute()" src/ --include="*.py"
grep -r "\.request()" src/ --include="*.py"
grep -r "requests\." src/ --include="*.py"
grep -r "open(" src/ --include="*.py"
grep -r "json\.load" src/ --include="*.py"
grep -r "\.refresh(" src/ --include="*.py"
```

### Step 2: Test for Blocking Calls at Runtime

```bash
# Run LangGraph without --allow-blocking to detect issues
langgraph dev

# Look for these error patterns in logs:
# "Blocking call to socket.socket.connect"
# "Blocking call to ssl.SSLSocket.send"
# "Blocking call to ssl.SSLSocket.recv"
```

### Step 3: Apply Async Patterns

1. **Wrap with asyncio.to_thread()** for synchronous library calls
2. **Use async/await** for naturally async operations
3. **Add async to method signatures** and ensure callers await
4. **Preserve error handling** patterns in async wrappers
5. **Update docstrings** to reflect async behavior

### Step 4: Validate Migration

```python
# Test async compliance
async def test_async_compliance():
    """Test that all operations are properly async."""
    try:
        # Test database operations
        result = await database_client.save_data(test_data)
        assert result is True

        # Test API operations
        emails = await gmail_client.get_new_emails("test query")
        assert isinstance(emails, list)

        # Test authentication
        service = await auth_client.get_authenticated_service("gmail", "v1")
        assert service is not None

        logger.info("✅ All async operations validated")

    except Exception as e:
        logger.error(f"❌ Async validation failed: {e}")
        raise
```

---

## 🚨 Common Pitfalls and Solutions

### Pitfall 1: Forgetting to Await

```python
# ❌ WRONG - Missing await
async def process_data():
    result = save_data(data)  # Missing await!
    return result

# ✅ CORRECT - Proper await
async def process_data():
    result = await save_data(data)
    return result
```

### Pitfall 2: Mixing Sync and Async Context

```python
# ❌ WRONG - Calling async from sync context
def sync_function():
    result = await async_function()  # SyntaxError!
    return result

# ✅ CORRECT - Use asyncio.run for sync entry point
def sync_function():
    result = asyncio.run(async_function())
    return result

# ✅ BETTER - Make the whole chain async
async def async_function():
    result = await other_async_function()
    return result
```

### Pitfall 3: Not Handling Async Exceptions

```python
# ❌ WRONG - Exception handling not preserved
async def unsafe_operation():
    result = await asyncio.to_thread(risky_operation)
    return result  # Exceptions bubble up uncaught

# ✅ CORRECT - Proper async exception handling
async def safe_operation():
    try:
        result = await asyncio.to_thread(risky_operation)
        return result
    except SpecificException as e:
        logger.error(f"❌ Known error occurred: {e}")
        raise BusinessLogicError(f"Operation failed: {e}")
    except Exception as e:
        logger.error(f"❌ Unexpected error: {e}")
        raise SystemError(f"Unexpected failure: {e}")
```

### Pitfall 4: Blocking in Async Context

```python
# ❌ WRONG - Blocking operation in async function
async def bad_async_function():
    time.sleep(1)  # Blocks the entire event loop!
    result = requests.get("http://api.example.com")  # Blocking HTTP call!
    return result

# ✅ CORRECT - Proper async equivalents
async def good_async_function():
    await asyncio.sleep(1)  # Non-blocking sleep
    async with aiohttp.ClientSession() as session:
        async with session.get("http://api.example.com") as response:
            result = await response.json()
    return result
```

---

## 📋 Async Code Review Checklist

### Before Merging Async Code:

- [ ] **All method signatures** use `async def` for async operations
- [ ] **All async calls** are properly awaited with `await`
- [ ] **Blocking operations** are wrapped with `asyncio.to_thread()`
- [ ] **Error handling** is preserved in async wrappers
- [ ] **Documentation** reflects async behavior and business context
- [ ] **Tests pass** without `--allow-blocking` flag
- [ ] **Runtime testing** shows no blocking call errors
- [ ] **Performance** is acceptable (async overhead is minimal)

### Async-Specific Tests:

```python
@pytest.mark.asyncio
async def test_async_database_operation():
    """Test database operations work in async context."""
    client = DatabaseClient()

    # Test async save
    result = await client.save_data({"test": "data"})
    assert result is True

    # Test async retrieve
    data = await client.get_data({"query": "test"})
    assert isinstance(data, list)

@pytest.mark.asyncio
async def test_no_blocking_calls():
    """Ensure no blocking calls during workflow execution."""
    with pytest.warns(None) as warning_list:
        await run_complete_workflow()

    # Check for blocking call warnings
    blocking_warnings = [w for w in warning_list if "Blocking call" in str(w.message)]
    assert len(blocking_warnings) == 0, f"Found blocking calls: {blocking_warnings}"
```

---

## 🎯 LangGraph-Specific Patterns

### Workflow Node Implementation

```python
# ✅ CORRECT - LangGraph node with proper async patterns
async def extract_emails_node(state: WorkflowState) -> WorkflowState:
    """
    Extract emails from Gmail for document processing workflow.

    Business Context: Entry point for document processing pipeline.
    Requires async compliance for LangGraph execution.
    """
    try:
        # Get dependencies (injected as async-compliant clients)
        gmail_client = dependencies.get("gmail_client")
        database_client = dependencies.get("database_client")

        # Perform async email extraction
        emails = await gmail_client.get_new_emails(
            query=state.email_query,
            max_results=state.max_emails
        )

        # Log workflow start to database asynchronously
        workflow_record = {
            "workflow_id": state.workflow_id,
            "step": "extract_emails",
            "email_count": len(emails),
            "timestamp": datetime.utcnow().isoformat()
        }

        await database_client.save_workflow_record(workflow_record)

        # Update state with extracted emails
        state.emails = emails
        state.current_step = "extract_emails_complete"

        logger.info(f"✅ Extracted {len(emails)} emails successfully")
        return state

    except Exception as e:
        logger.error(f"❌ Email extraction failed: {e}")
        state.error = f"Email extraction error: {e}"
        state.current_step = "extract_emails_failed"
        return state
```

### Dependency Injection for Async Clients

```python
# ✅ CORRECT - Async-compliant dependency setup
async def setup_dependencies() -> Dict[str, Any]:
    """
    Initialize all async-compliant clients for workflow.

    Business Context: Provides authenticated API clients for workflow operations.
    All clients are configured for async operation with proper error handling.
    """
    dependencies = {}

    try:
        # Initialize async Gmail client
        gmail_auth = GmailAuthClient()
        gmail_service = await gmail_auth.get_authenticated_service()
        gmail_client = GmailClient(gmail_service)
        dependencies["gmail_client"] = gmail_client

        # Initialize async database client
        sheets_auth = GoogleOAuthService()
        sheets_service = await sheets_auth.get_authenticated_service("sheets", "v4")
        database_client = GoogleSheetsDatabase(sheets_service)
        await database_client.initialize()  # Async initialization
        dependencies["database_client"] = database_client

        logger.info("✅ All dependencies initialized successfully")
        return dependencies

    except Exception as e:
        logger.error(f"❌ Dependency initialization failed: {e}")
        raise DependencyError(f"Failed to setup async dependencies: {e}")
```

---

## 📚 Reference Implementation Examples

### Complete Async Database Client

**File**: `src/services/database/implementations/google_sheets.py`

Key patterns implemented:

- All database operations wrapped with `asyncio.to_thread()`
- Proper error handling preserved through async migration
- Business context maintained in docstrings
- Token operations made atomic and async

### Complete Async Gmail Client

**File**: `src/integrations/gmail/gmail_client.py`

Key patterns implemented:

- OAuth authentication flow made async
- All Gmail API calls wrapped appropriately
- Email sending and retrieval operations async-compliant
- Integration with centralized OAuth service

### Complete Async Email Service

**File**: `src/services/email/analysis_review_email_service.py`

Key patterns implemented:

- Email composition and sending fully async
- Token generation integrated with async database
- HTML email creation with proper async patterns

---

## 🔍 Debugging Async Issues

### Common Error Messages and Solutions

**Error**: `RuntimeWarning: coroutine 'function_name' was never awaited`

```python
# ❌ Problem: Missing await
result = async_function()

# ✅ Solution: Add await
result = await async_function()
```

**Error**: `Blocking call to socket.socket.connect`

```python
# ❌ Problem: Synchronous API call
result = api_client.make_request()

# ✅ Solution: Wrap with asyncio.to_thread()
result = await asyncio.to_thread(api_client.make_request)
```

**Error**: `Cannot call async function from sync context`

```python
# ❌ Problem: Async call in sync function
def sync_function():
    return await async_function()

# ✅ Solution: Make function async or use asyncio.run()
async def async_function():
    return await other_async_function()
```

### Debugging Tools

```python
# Add to identify blocking operations
import warnings
warnings.filterwarnings("error", message=".*Blocking call.*")

# Log async context information
import asyncio

async def debug_async_context():
    loop = asyncio.get_running_loop()
    logger.debug(f"Running in event loop: {loop}")
    logger.debug(f"Loop is running: {loop.is_running()}")
```

---

## 📈 Performance Considerations

### Async Performance Best Practices

1. **Batch operations** when possible to reduce async overhead
2. **Use connection pooling** for frequent API calls
3. **Avoid mixing blocking and async** code in performance-critical paths
4. **Monitor async task execution** time and optimize bottlenecks

### Performance Testing

```python
import time
import asyncio

async def performance_test_async_operations():
    """Test performance of async operations vs blocking."""

    # Test async operations
    start_time = time.time()
    tasks = [async_database_operation() for _ in range(10)]
    await asyncio.gather(*tasks)
    async_time = time.time() - start_time

    logger.info(f"Async operations completed in {async_time:.2f}s")

    # Performance should be reasonable (not worse than 2x blocking time)
    assert async_time < ACCEPTABLE_ASYNC_OVERHEAD_THRESHOLD
```

---

## � FastAPI Event Loop Compatibility

### Critical: Module Import Async Compatibility

**Problem**: When LangGraph workflow modules are imported by FastAPI servers, `asyncio.run()` calls at module import time fail because FastAPI already runs an event loop.

**Error Pattern**:

```bash
❌ LangGraph server startup failure due to improper dependency injection pattern
❌ asyncio.run() cannot be called from a running event loop
```

### Solution: Context-Aware Async Initialization

Use thread-based async initialization that detects event loop context:

```python
# ✅ CORRECT: Context-aware async initialization
import asyncio
import concurrent.futures
import threading

# At module level (e.g., in workflow/graph.py)
try:
    # Check if we're already in an event loop (e.g., FastAPI)
    try:
        loop = asyncio.get_running_loop()

        # We're in an event loop, run in separate thread
        def run_in_thread():
            # Create new event loop in separate thread
            new_loop = asyncio.new_event_loop()
            asyncio.set_event_loop(new_loop)
            try:
                return new_loop.run_until_complete(async_initialization())
            finally:
                new_loop.close()

        # Execute in thread pool to avoid blocking main event loop
        with concurrent.futures.ThreadPoolExecutor() as executor:
            future = executor.submit(run_in_thread)
            result = future.result(timeout=30)  # Timeout protection

    except RuntimeError:
        # No running loop, safe to use asyncio.run() (standalone/tests)
        result = asyncio.run(async_initialization())

    # Use result for module-level initialization
    workflow_graph = result

except Exception as initialization_error:
    logger.warning(f"Async initialization failed: {initialization_error}")
    workflow_graph = None  # Graceful fallback
```

### Key Benefits

1. **Universal Compatibility**: Works in FastAPI, LangGraph, and test contexts
2. **Thread Isolation**: Separate event loop prevents conflicts
3. **Graceful Fallback**: Handles both event loop and standalone contexts
4. **Timeout Protection**: Prevents indefinite hangs during initialization
5. **Error Isolation**: Initialization failures don't crash server startup

### FastAPI Integration Pattern

```python
# src/api/app.py - FastAPI app with LangGraph workflow import
from fastapi import FastAPI

# This import now works because graph.py uses LangGraph dependency injection pattern
from src.workflow.graph import workflow_graph  # ✅ No event loop conflicts

app = FastAPI()

@app.on_event("startup")
async def startup_event():
    """FastAPI startup with pre-initialized workflow graph."""
    if workflow_graph is None:
        logger.warning("Workflow graph not available - running in degraded mode")
    else:
        logger.info("✅ FastAPI server ready with LangGraph workflow")

@app.get("/workflow/status")
async def workflow_status():
    """API endpoint using the imported workflow graph."""
    return {
        "workflow_available": workflow_graph is not None,
        "import_context": "fastapi_event_loop"
    }
```

### Testing the Pattern

```python
# Test that the pattern works in different contexts
import asyncio
import pytest

def test_standalone_import():
    """Test module import without running event loop."""
    # This should use asyncio.run() path
    from src.workflow.graph import workflow_graph
    assert workflow_graph is not None

@pytest.mark.asyncio
async def test_event_loop_import():
    """Test module import from within event loop."""
    # This should use thread-based path

    # Simulate importing from within async context
    exec("from src.workflow.graph import workflow_graph")

    # Should succeed without event loop conflicts
    assert True  # If we get here, no event loop conflicts occurred
```

### Deployment Verification

```bash
# Verify dual server startup works
source .venv/bin/activate

# Start LangGraph server (standalone context)
langgraph dev &  # Uses asyncio.run() path

# Start FastAPI server (event loop context)
uvicorn src.api.app:app --reload &  # Uses thread-based path

# Both should start successfully
✅ LangGraph Studio: http://localhost:2024
✅ FastAPI Docs: http://localhost:8000/docs
```

---

## �🎉 Success Criteria

### Async Migration Complete When:

- ✅ **LangGraph server starts** without `--allow-blocking` flag
- ✅ **Complete workflow executes** without blocking call errors
- ✅ **All database operations** work correctly in async context
- ✅ **All API operations** work correctly in async context
- ✅ **Error handling** functions properly in async context
- ✅ **Performance** is acceptable for business requirements
- ✅ **Tests pass** in async execution environment
- ✅ **Documentation** reflects async patterns and business context

---

**Remember: Async migration preserves business logic while enabling LangGraph's native execution environment. Focus on wrapping I/O operations appropriately while maintaining the existing error handling and business context patterns.**
