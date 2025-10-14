# GitHub Copilot Instructions — TDD-First Development (Python + LangGraph/LangSmith)

## 📋 Overview

**You are assisting on a Python project with LangSmith tracing. ALWAYS follow TDD principles and comprehensive documentation practices.**

**🎯 CRITICAL: This project uses LangGraph Tool Pattern Architecture (ADR 005) - ALL external API integrations MUST use tool calling pattern, NOT dependency injection.**

### Quick Environment Setup

```bash
# One-command reproducible environment
python -m venv .venv && source .venv/bin/activate && pip install -e .[dev]

# Start development server
langgraph dev
```

### Dependencies & Cache Management

- **Virtual environments**: Disposable (.venv/, venv/)
- **Download caches**: Shared (~/.cache/pip)
- **Tool caches**: Excluded from git (.pytest_cache/, .mypy_cache/)
- **Reference**: `code_quality_practices/python-dependency-cache-guidance.md`

---

## 🔧 MANDATORY: LangGraph Tool Pattern Architecture

**CRITICAL: ALL external API integrations use LangGraph tool pattern (ADR 005). This is the ONLY accepted pattern for new development.**

### 🎯 **Architecture Decision Context**

**Tool pattern is the preferred LangGraph architecture because:**
- ✅ **Idiomatic LangGraph usage** - Follows framework best practices
- ✅ **Agent readiness** - Direct transition to agent tool calling
- ✅ **Better async compliance** - Eliminates blocking operation concerns
- ✅ **Improved testing** - Tools are independently testable
- ✅ **Clean separation** - External dependencies encapsulated in tools

### 🏗️ **Standard Tool Pattern**

**ALL external API integrations MUST follow this pattern:**

```python
# ✅ CORRECT: LangGraph Tool Pattern
from langchain_core.tools import tool
import asyncio

@tool("api_operation")
async def api_operation_tool(param1: str, param2: str) -> dict:
    """
    Tool description for LLM understanding.
    
    Args:
        param1: Description of parameter
        param2: Description of parameter
        
    Returns:
        dict: Standard response format with status and data
    """
    try:
        # Initialize service within tool
        service = ExternalAPIService()
        await service.initialize()
        
        # Perform operation with async compliance
        result = await asyncio.to_thread(service.blocking_operation, param1, param2)
        
        return {
            "status": "success",
            "data": result,
            "tool_execution": "async_compliant"
        }
        
    except Exception as e:
        logger.error(f"Tool api_operation failed: {e}")
        return {
            "status": "error",
            "error": str(e),
            "tool_execution": "failed"
        }

# Usage in workflow step
async def workflow_step(state: State, config: RunnableConfig) -> State:
    """Workflow step using tool pattern."""
    
    # Extract parameters from state
    input_data = state.get('input_field')
    
    # Call tool
    result = await api_operation_tool.ainvoke({
        "param1": input_data,
        "param2": "configuration_value"
    })
    
    # Process result and update state
    updated_state = dict(state)
    
    if result.get("status") == "success":
        updated_state['output_field'] = result.get("data")
        updated_state['errors'] = []
    else:
        updated_state['errors'] = state.get('errors', []) + [result.get("error")]
    
    return updated_state
```

### ❌ **Deprecated Pattern - DO NOT USE**

```python
# ❌ DEPRECATED: Dependency Injection Pattern
async def workflow_step(state: State, config: RunnableConfig) -> State:
    # Get dependencies from config - NO LONGER USED
    client = config.get("configurable", {}).get("api_client")
    
    # Direct client usage - AVOID THIS PATTERN
    result = await client.perform_operation(param)
    
    return updated_state
```

### 🧪 **Tool Testing Pattern**

```python
@pytest.mark.asyncio
async def test_api_tool_success():
    """Test tool with successful execution."""
    
    # Arrange
    input_params = {"param1": "test_value", "param2": "test_config"}
    
    # Act
    result = await api_operation_tool.ainvoke(input_params)
    
    # Assert
    assert result["status"] == "success"
    assert "data" in result
    assert result["tool_execution"] == "async_compliant"

@pytest.mark.asyncio 
async def test_api_tool_error_handling():
    """Test tool error handling."""
    
    # Arrange
    invalid_params = {"param1": None, "param2": "test"}
    
    # Act
    result = await api_operation_tool.ainvoke(invalid_params)
    
    # Assert
    assert result["status"] == "error"
    assert "error" in result
```

### 📚 **Tool Pattern References**

**MUST READ before implementing any external API integration:**
- **📖 ADR 005**: `docs/adr/ADR_005_LANGGRAPH_TOOL_PATTERN_ARCHITECTURE.md`
- **📖 Migration Plan**: `LANGGRAPH_TOOL_PATTERN_MIGRATION_PLAN.md`
- **📖 Step 01 Example**: `src/workflow/steps/step01_extract_emails/` (Gmail tools reference implementation)

---

## 🚀 MANDATORY: Leverage Hierarchy & Intelligent Task Routing

**CRITICAL: Understanding leverage hierarchy is fundamental to maximizing development ROI and preventing waste.**

### 🎯 How the System Works

#### 1. Intelligent Task Routing Based on Leverage

**Automatic routing prevents massive waste by directing tasks to highest-leverage activities first:**

- **Ambiguous specifications** → Automatically routes to **Research** to prevent 10,000+ lines of wrong solutions
- **Infrastructure keywords** → Prioritizes **Research** to prevent 100,000+ lines of architectural mistakes
- **Complex implementations** → Always starts with **research/planning** based on complexity levels
- **Simple tasks** → Still validates specifications to prevent waste

#### 2. Agent Leverage Understanding

**Research Agent (Dr. Context) - Highest Leverage Tier**

- **Leverage Multiplier**: 1 hour research = saves 1,000+ lines of misguided implementation
- **Operates knowing**: Infrastructure impact analysis and specification validation are critical
- **Uses leverage escalation rules**: Stops work when clarity is needed
- **Primary Focus**: Context validation, specification clarity, system understanding

**Planning Agent (Aristotle) - Critical Leverage Tier**

- **Leverage Multiplier**: 1 bad line of plan = 10-100 bad lines of implementation
- **Operates knowing**: Validates specifications FIRST before any planning
- **Primary Focus**: Preventing wrong solution directions, architectural alignment
- **Quality Gates**: Won't plan without clear research findings

**Implementation Agent (Leonardo) - Execution Tier**

- **Leverage Multiplier**: 1:1 (implementation directly creates value)
- **Operates knowing**: He validates the entire upstream chain before coding
- **Quality Gates**: Refuses to implement without proper research findings and clear plans
- **Protection Strategy**: Demands quality upstream work to protect leverage value

#### 3. Automatic Leverage Validation

**Context Validation Pipeline**: Prevents misunderstanding propagation across leverage tiers

**Specification Clarity Gates**: Stops work when requirements are unclear - forces upstream clarification

**System Understanding Assessment**: Ensures architectural clarity before downstream work

**ROI-Based Prioritization**: Automatically optimizes conversation flow for maximum leverage

### 💡 Real-World Impact Examples

**The system now automatically detects and prevents:**

| User Request                    | Automatic Routing                                    | Leverage Protection                          |
| ------------------------------- | ---------------------------------------------------- | -------------------------------------------- |
| "Improve the user interface"    | → Routes to **Research** for specification clarity   | Prevents 10,000+ lines wrong direction       |
| "Add API endpoint"              | → Routes to **Research** for infrastructure analysis | Prevents 100,000+ lines architectural issues |
| "Fix the login bug"             | → Routes to **Research** for system understanding    | Prevents 1,000+ lines misguided debugging    |
| "Implement user authentication" | → **Research** → **Planning** → **Implementation**   | Preserves full leverage chain                |

### 🎪 The Leverage Cascade in Action

**When a task comes in, the system:**

1. **Analyzes leverage opportunities** across all hierarchy levels
2. **Calculates ROI** for each potential activity
3. **Routes to highest leverage agent first**
4. **Validates leverage chain** before lower-tier work
5. **Prevents waste** through intelligent escalation rules

### 🧠 Leverage Decision Matrix

| Task Complexity | Specification Clarity | Infrastructure Impact | Route To           | Reasoning                                    |
| --------------- | --------------------- | --------------------- | ------------------ | -------------------------------------------- |
| **High**        | **Unclear**           | **High**              | **Research**       | Max leverage: Prevent architectural mistakes |
| **High**        | **Clear**             | **High**              | **Planning**       | High leverage: Prevent implementation errors |
| **Medium**      | **Unclear**           | **Medium**            | **Research**       | High leverage: Clarify before planning       |
| **Medium**      | **Clear**             | **Low**               | **Planning**       | Medium leverage: Plan then implement         |
| **Low**         | **Clear**             | **Low**               | **Implementation** | Direct implementation acceptable             |
| **Any**         | **Unclear**           | **Any**               | **Research**       | Always clarify specifications first          |

### 🎯 Leverage Escalation Rules

**Research Level Escalation:**

- **STOP** implementation when specifications are ambiguous
- **ESCALATE** to research when infrastructure keywords detected
- **VALIDATE** system understanding before any downstream work

**Planning Level Escalation:**

- **REFUSE** to plan without clear research findings
- **VALIDATE** architectural alignment before implementation planning
- **ENSURE** implementation feasibility before committing to approach

**Implementation Level Escalation:**

- **DEMAND** clear specifications and validated plans
- **PROTECT** development time by refusing unclear requirements
- **VALIDATE** entire upstream chain before coding

### 💰 ROI Understanding Across Tiers

**Research Tier ROI:**

- **Investment**: 1-2 hours investigation
- **Savings**: 100-1000 hours of wrong implementation
- **Multiplier**: 50x-500x return on time invested

**Planning Tier ROI:**

- **Investment**: 2-4 hours planning
- **Savings**: 20-200 hours of implementation rework
- **Multiplier**: 10x-50x return on time invested

**Implementation Tier ROI:**

- **Investment**: 1 hour implementation
- **Value**: 1 hour of working functionality
- **Multiplier**: 1x (direct value creation)

### 🚦 Quality Gates & Checkpoints

**Pre-Research Gates:**

- [ ] **Task complexity assessment** completed
- [ ] **Specification clarity evaluation** done
- [ ] **Infrastructure impact analysis** required
- [ ] **Leverage opportunity identification** complete

**Pre-Planning Gates:**

- [ ] **Research findings** documented and validated
- [ ] **System understanding** confirmed
- [ ] **Architectural constraints** identified
- [ ] **Implementation feasibility** assessed

**Pre-Implementation Gates:**

- [ ] **Clear specifications** validated
- [ ] **Detailed plans** reviewed and approved
- [ ] **Upstream quality** verified
- [ ] **Leverage chain integrity** confirmed

### 🎭 Agent Personality & Leverage Awareness

**Research Agent Characteristics:**

- **Mindset**: "1 hour of research saves 1000 hours of wrong implementation"
- **Behavior**: Methodical, thorough, context-obsessed
- **Decision Making**: Always asks "What don't we know that could derail everything?"
- **Quality Standard**: Won't proceed without comprehensive understanding

**Planning Agent Characteristics:**

- **Mindset**: "1 bad line of plan creates 100 bad lines of code"
- **Behavior**: Systematic, validation-focused, architecture-aware
- **Decision Making**: "Is this plan based on solid research and clear requirements?"
- **Quality Standard**: Refuses to plan without validated research findings

**Implementation Agent Characteristics:**

- **Mindset**: "I protect development time by demanding upstream quality"
- **Behavior**: Quality-gate enforcement, upstream validation
- **Decision Making**: "Are research and planning complete and validated?"
- **Quality Standard**: Won't implement without clear, validated upstream work

### 🔄 Continuous Leverage Optimization

**System Learning:**

- **Tracks** which leverage decisions prevented waste
- **Measures** ROI of research and planning investments
- **Optimizes** routing algorithms based on success patterns
- **Improves** quality gates based on failure analysis

**Feedback Loops:**

- **Implementation feedback** → Planning process improvement
- **Planning feedback** → Research process refinement
- **Research feedback** → Specification clarification methods
- **Overall feedback** → Leverage hierarchy optimization

---

## ⚡ MANDATORY: Fast Development & Debugging Practices

**CRITICAL: Prioritize development velocity by using direct debugging approaches instead of creating separate test files for quick validation.**

### 🚀 **Direct Debugging Over Test Files**

**When investigating issues or testing functionality:**

#### Quick Debugging Reference

1. **📝 Add debug statements directly to production code** - Use logging or print statements in the actual file
2. **🔧 Test in real environment** - Use LangGraph server, API endpoints, or actual workflow execution
3. **🎯 Focus on production context** - Test where the code actually runs, not in isolation
4. **⚡ Iterate rapidly** - Make changes and test immediately without creating test infrastructure
5. **🧹 Clean up debug statements** after validation (or leave useful ones as permanent logging)

#### Direct Debugging Principles

- **AVOID creating test files for quick validation** - They slow down development significantly
- **USE the actual production environment** - LangGraph server, real workflows, live endpoints
- **ADD debug logging to real files** - Temporary or permanent debug statements in production code
- **TEST in context** - Use the same environment where the code will actually run
- **VALIDATE quickly** - Get immediate feedback without test infrastructure overhead

#### Direct Debugging Examples

```python
# ✅ FAST: Add debug statements directly to production code
class ModelServiceFactory:
    @classmethod
    def _initialize_default_registry(cls) -> None:
        """Initialize registry with debug output."""
        try:
            from .implementations.ollama_service import OllamaModelService
            
            # DEBUG: Add temporary debugging
            print(f"🔧 About to register LOCAL_OLLAMA...")
            cls._registry[ModelType.LOCAL_OLLAMA] = OllamaModelService
            print(f"✅ LOCAL_OLLAMA registered: {ModelType.LOCAL_OLLAMA in cls._registry}")
            
            # Debug at end of method
            print(f"📋 Final registry: {list(cls._registry.keys())}")
            
        except Exception as e:
            print(f"❌ Registration failed: {e}")

# ✅ FAST: Test directly in production environment
# Instead of creating test files, use:
# - LangGraph server: langgraph dev
# - API calls: curl localhost:2024/...
# - Direct imports: python -c "import module; test_function()"

# ❌ SLOW: Creating separate test files for quick validation
class TestModelServiceFactory:
    def test_registry_initialization(self):
        # This approach is too slow for rapid development
        pass
```

### 📜 **Script-Based Testing for Complex Validation**

**For complex testing or validation that requires multiple operations, create temporary script files instead of long inline commands:**

#### Script-Based Testing Principles

- **AVOID long inline Python commands** - They are error-prone and hard to debug
- **CREATE temporary script files** - More reliable execution and easier debugging
- **CLEAN UP scripts after use** - Remove temporary files to keep workspace clean
- **USE meaningful script names** - Make purpose clear (e.g., `test_api_cleanup.py`)

#### Script-Based Testing Examples

```python
# ✅ FAST & RELIABLE: Create temporary script file
# File: test_api_cleanup.py
#!/usr/bin/env python3
"""Test script for API cleanup validation."""

import asyncio
import requests
import sys
sys.path.append('src')

from src.services.database.pending_reviews_service import PendingReviewsService

async def test_service_methods():
    """Test the simplified service methods."""
    print("🔧 Testing service...")
    service = PendingReviewsService()
    
    # Test method exists
    method = getattr(service, 'get_pending_review', None)
    if method:
        print('✅ get_pending_review method exists')
    else:
        print('❌ get_pending_review method missing')

def test_api_endpoints():
    """Test API endpoints."""
    print("🌐 Testing API...")
    try:
        response = requests.get("http://localhost:8000/health", timeout=5)
        print(f"✅ API accessible: {response.status_code}")
    except Exception as e:
        print(f"❌ API error: {e}")

async def main():
    await test_service_methods()
    test_api_endpoints()
    print("✅ Test completed!")

if __name__ == "__main__":
    asyncio.run(main())
```

```bash
# Usage pattern:
# 1. Create script
# 2. Run script
python test_api_cleanup.py

# 3. Clean up script
rm test_api_cleanup.py

# ❌ AVOID: Long inline commands
python -c "import sys; sys.path.append('src'); from src.services... [500+ characters]"
```

#### Script vs Inline Decision Matrix

| Situation | Approach | Reasoning |
|-----------|----------|-----------|
| **Single import test** | Inline command | Quick one-liner |
| **Multi-step validation** | Script file | More reliable execution |
| **Complex async operations** | Script file | Better error handling |
| **API testing** | Script file | Timeout and exception handling |
| **Service integration testing** | Script file | Multiple dependencies |
| **Quick syntax check** | Inline command | Simple validation |

#### When to Use Each Approach

| Situation | Approach | Reasoning |
|-----------|----------|-----------|
| **Quick validation** | Direct debug statements | 10x faster iteration |
| **Issue investigation** | Debug in production files | Real environment context |
| **Functionality verification** | Test in actual server/workflow | Authentic execution context |
| **Rapid prototyping** | Print/log statements | Immediate feedback |
| **Complex integration** | TDD with real components | Systematic development |
| **Business logic** | Formal tests | Long-term maintainability |
| **Multi-step testing** | **Script files** | **Reliable execution & debugging** |

---

## 🧪 MANDATORY: Test-Driven Development Workflow

**CRITICAL: We use TWO DISTINCT TDD approaches depending on the context:**

### 🛠️ **TDD for Development** (Integration & System Testing)

**When developing NEW functionality or major changes:**

#### Quick Development TDD Reference

1. **📖 Read README.md** for the target directory first
2. **✅ Write integration tests** using **REAL components** and **REAL dependencies**
3. **📝 Write comments-first pseudocode** design
4. **⚡ Implement complete working code** that passes integration tests
5. **🔄 Refactor with green tests** ensuring entire system still works

#### Development TDD Principles

- **USE REAL COMPONENTS**: Test the actual class/function being developed
- **USE REAL DEPENDENCIES**: Include databases, APIs, file systems, network calls
- **PASS TEST DATA**: Use realistic test data that exercises the full code path
- **VERIFY SYSTEM INTEGRATION**: Ensure new changes don't break existing functionality
- **ITERATE ON REAL BEHAVIOR**: Develop until the entire system produces expected results

#### Development TDD Example

```python
# ✅ DEVELOPMENT TEST - Uses real components and dependencies
@pytest.mark.integration
async def test_email_service_sends_actual_email_with_two_links():
    """Development test: Real email service with real Gmail client."""
    # Arrange: Real service with real Gmail client
    email_service = AnalysisReviewEmailService(real_config, real_gmail_client)
    await email_service.initialize()  # Real database connection

    # Act: Call real method with test data
    result = await email_service.send_review_notification(
        thread_id="test_thread_123",
        document_data=test_invoice_data,  # Real test data
        reviewer_email="test@company.com"
    )

    # Assert: Real email sent, real database updated
    assert result is True
    assert_email_contains_two_links(sent_email)
    assert_database_has_pending_review("test_thread_123")
```

### 🔬 **TDD for Unit Testing** (Isolated Component Testing)

**When creating focused unit tests for specific behaviors:**

#### Quick Unit TDD Reference

1. **📖 Identify the single behavior** to test
2. **✅ Write unit tests** using **REAL component** but **MOCKED dependencies**
3. **📝 Write focused test scenarios** for edge cases
4. **⚡ Verify isolated behavior** works correctly
5. **🔄 Test error handling** and boundary conditions

#### Unit TDD Principles

- **USE REAL COMPONENT**: Test the actual class/method implementation
- **MOCK DEPENDENCIES**: Isolate external systems (databases, APIs, network)
- **FOCUS ON BEHAVIOR**: Test one specific behavior or business rule
- **VERIFY ISOLATION**: Ensure component works regardless of external state
- **TEST EDGE CASES**: Cover error conditions, null inputs, boundary values

#### Unit TDD Example

```python
# ✅ UNIT TEST - Real component, mocked dependencies
@pytest.mark.unit
async def test_email_service_handles_gmail_failure_gracefully():
    """Unit test: Real email service with mocked Gmail client."""
    # Arrange: Real service with mocked dependencies
    mock_gmail = Mock(spec=GmailClient)
    mock_gmail.send_email.return_value = False  # Simulate failure

    email_service = AnalysisReviewEmailService(config, mock_gmail)

    # Act: Call real method
    result = await email_service.send_review_notification(
        thread_id="test_thread_123",
        document_data=test_invoice_data,
        reviewer_email="test@company.com"
    )

    # Assert: Real component handles failure correctly
    assert result is False
    mock_gmail.send_email.assert_called_once()
```

### 📊 **When to Use Each Approach**

| Context                     | TDD Approach    | Components | Dependencies | Purpose                    |
| --------------------------- | --------------- | ---------- | ------------ | -------------------------- |
| **New Feature Development** | Development TDD | Real       | Real         | Ensure system integration  |
| **Major Refactoring**       | Development TDD | Real       | Real         | Verify no regressions      |
| **Bug Investigation**       | Development TDD | Real       | Real         | Reproduce real-world issue |
| **Behavior Verification**   | Unit TDD        | Real       | Mocked       | Test isolated logic        |
| **Error Handling**          | Unit TDD        | Real       | Mocked       | Test edge cases            |
| **Performance Testing**     | Unit TDD        | Real       | Mocked       | Measure component speed    |

### Detailed Guidance

**📖 Read `code_quality_practices/TDD_WORKFLOW_GUIDE.md`** for comprehensive TDD process including:

- Development TDD vs Unit TDD decision matrix
- Integration testing patterns with real dependencies
- Mock strategy for unit test isolation
- Test organization and execution patterns
- LangSmith integration and dataset management
- Property-based testing with Hypothesis
- Performance testing and quality gates

### Detailed Guidance

**📖 Read `code_quality_practices/TDD_WORKFLOW_GUIDE.md`** for comprehensive TDD process including:

- Development TDD vs Unit TDD decision matrix
- Integration testing patterns with real dependencies
- Mock strategy for unit test isolation
- Test organization and execution patterns
- LangSmith integration and dataset management
- Property-based testing with Hypothesis
- Performance testing and quality gates

---

## 📝 MANDATORY: Code Commenting Standards

**Always write comments-first pseudocode before implementation.**

### Quick Commenting Reference

- **Comments explain WHY, not WHAT**
- **Write complete business logic as comments first**
- **Include business context for complex decisions**
- **Document error handling strategies**
- **Comprehensive docstrings for all public functions**

### Detailed Guidance

**📖 Read `code_quality_practices/COMMENTING_BEST_PRACTICES.md`** for comprehensive commenting standards including:

- Comment hierarchy and quality standards
- Comments-first pseudocode patterns
- Docstring standards with business context
- Comment maintenance and review processes
- Anti-patterns to avoid
- Tools and automation for comment quality

---

## 🧪 Testing & Quality Assurance

### Quick Testing Reference

```python
# Test markers organized by TDD approach
@pytest.mark.unit           # Unit tests: Real component, mocked dependencies
@pytest.mark.integration    # Development tests: Real components + real dependencies
@pytest.mark.node           # Single LangGraph node with real data
@pytest.mark.graph          # Multiple nodes or subgraph integration
@pytest.mark.contract       # API adapter interface tests
@pytest.mark.e2e            # End-to-end scenario tests
@pytest.mark.slow           # Long-running tests
@pytest.mark.live           # Calls external services
```

### Test Execution Commands

```bash
# Development TDD loop - Integration tests with real dependencies
pytest -m "integration or node" -q

# Unit TDD loop - Fast isolated behavior tests
pytest -m "unit" -q

# Coverage check with fail gate
pytest --cov=src --cov-fail-under=90

# Full test suite (excluding live services)
pytest -m "not live" -v

# Graph and contract tests (nightly)
pytest -m "graph or contract" -v

# End-to-end tests with external services
pytest -m "e2e or live" --tb=long
```

### Testing Philosophy

**Development Tests (Integration)**:

- Use **real components** and **real dependencies**
- Test entire workflows and system integration
- Verify new features work with existing system
- Catch regressions in the complete system

**Unit Tests (Isolated)**:

- Use **real component** but **mock dependencies**
- Test specific behaviors in isolation
- Verify edge cases and error handling
- Fast feedback on component logic

### Coverage Requirements

**📖 Read `code_quality_practices/COVERAGE_REQUIREMENTS_UPDATED.md`** for updated coverage standards including:

- Module-specific coverage targets and thresholds
- Coverage measurement and reporting strategies
- Quality gates and enforcement mechanisms
- Coverage improvement workflows and tactics

### Detailed Guidance

**📖 Read `code_quality_practices/TESTING_QUALITY_GUIDE.md`** for comprehensive testing guidance including:

- Test architecture and organization patterns
- Mock strategy and test doubles
- LangSmith integration testing
- Property-based testing with Hypothesis
- Performance and load testing
- CI/CD integration and quality gates

---

## 🔬 LangSmith & LangGraph Practices

### Quick LangSmith Reference

```python
# Deterministic LLM calls for testing
from langsmith import wrappers
import os

# Set deterministic seed for reproducible tests
os.environ["LANGCHAIN_PROJECT"] = "test-project"
os.environ["LANGCHAIN_SEED"] = "42"

# Use LangSmith datasets as test oracles
from langsmith import Client
client = Client()
dataset = client.read_dataset(dataset_name="validation_set")
```

### LangGraph Node Testing Patterns

```python
# Test individual nodes with schema validation
@pytest.mark.node
def test_extraction_node_schema():
    """Test node I/O schema contracts."""
    input_state = ExtractionState(documents=[...])
    result = extraction_node(input_state)

    # Validate output schema
    assert isinstance(result, ExtractionState)
    assert result.extracted_data is not None

# Test state transitions and invariants
@pytest.mark.graph
def test_workflow_state_invariants():
    """Test that state transitions maintain invariants."""
    initial_state = WorkflowState(status="pending")
    final_state = run_workflow(initial_state)

    # State invariants
    assert final_state.status in ["completed", "failed"]
    assert final_state.created_at == initial_state.created_at
```

### LangSmith Dataset Integration

- **Use datasets as test oracles** for regression testing
- **Update datasets intentionally** when output format changes
- **Link traces in CI** for debugging failed tests
- **Version control dataset changes** with schema migrations

### Prompt Engineering Standards

```python
# Version and seed prompts for reproducibility
PROMPT_VERSION = "v1.2.0"
EXTRACTION_PROMPT = f"""
# Version: {PROMPT_VERSION}
# Purpose: Extract structured data from documents
# Last updated: 2025-01-15

Extract the following information...
"""

# Deterministic LLM configuration
llm = ChatOpenAI(
    model="gpt-4-turbo",
    temperature=0,  # Deterministic output
    seed=42,        # Reproducible results
    max_retries=3,
)
```

---

## ⚡ Async Programming for LangGraph

### CRITICAL: LangGraph Async Compliance

**LangGraph requires full async compliance for production workflows.** All I/O operations must be properly async to avoid blocking the event loop.

### Quick Async Patterns

```python
# ✅ CORRECT: Async database operations
async def save_to_database(self, data):
    """Save data asynchronously using asyncio.to_thread()."""
    result = await asyncio.to_thread(
        self._service.worksheets['TableName'].insert_rows,
        [data], value_input_option='RAW'
    )
    return result

# ✅ CORRECT: Async API calls
async def get_emails(self, query):
    """Get emails from Gmail API asynchronously."""
    messages = await asyncio.to_thread(
        self._gmail_service.users().messages().list,
        userId='me', q=query
    )
    return await asyncio.to_thread(messages.execute)

# ✅ CORRECT: LangGraph workflow node
async def process_documents_node(state: WorkflowState) -> WorkflowState:
    """Process documents in LangGraph workflow with async compliance."""
    try:
        # All I/O operations must be async
        gmail_client = dependencies.get("gmail_client")
        database_client = dependencies.get("database_client")

        # Async email processing
        emails = await gmail_client.get_new_emails(state.query)

        # Async database logging
        await database_client.save_workflow_record({
            "step": "process_documents",
            "email_count": len(emails)
        })

        state.emails = emails
        return state

    except Exception as e:
        state.error = f"Processing failed: {e}"
        return state
```

### Quick Detection & Fixing

```bash
# Test for blocking calls
langgraph dev  # Should start without --allow-blocking

# Search for blocking patterns
grep -r "\.execute()" src/ --include="*.py"
grep -r "requests\." src/ --include="*.py"
```

### Common Error Fixes

**Error**: `Blocking call to socket.socket.connect`

```python
# ❌ Problem: Synchronous API call
result = api_client.make_request()

# ✅ Solution: Wrap with asyncio.to_thread()
result = await asyncio.to_thread(api_client.make_request)
```

**Error**: `coroutine 'function_name' was never awaited`

```python
# ❌ Problem: Missing await
result = async_function()

# ✅ Solution: Add await
result = await async_function()
```

### Detailed Guidance

**📖 Read `construction_best_practices/ASYNC_PROGRAMMING_LANGGRAPH_GUIDE.md`** for comprehensive async programming including:

- Complete async migration patterns for Google APIs
- LangGraph node implementation patterns
- **LangGraph dependency injection** - Use `dependencies_file` for initialization
- Error handling in async context
- Performance monitoring for async operations
- Testing strategies for async code

**📖 Use `construction_best_practices/ASYNC_QUICK_REFERENCE.md`** for quick async patterns and debugging.

---

## 🏗️ Architecture & Code Standards

### Quick Standards Reference

```python
# Modern import structure (2025 style)
import os
from pathlib import Path
from typing import Any, Optional, Sequence

import pytest
from langchain_openai import ChatOpenAI

from ..models.state import WorkflowState
from .base_extractor import BaseExtractor
```

### 🎯 **MANDATORY: Don't Repeat Yourself (DRY) Principles**

**DRY is the foundational principle governing ALL code construction decisions.**

#### **Pre-Implementation DRY Checklist**

**Before writing ANY new code:**

- [ ] **Search existing codebase** for similar functionality
- [ ] **Check responsibility alignment** - Does this belong in an existing class?
- [ ] **Consider inheritance/composition** - Can existing components be extended?
- [ ] **Identify common patterns** - Should this be extracted to utilities?
- [ ] **Look for magic numbers** - Use centralized constants instead

#### **DRY Implementation Patterns**

```python
# ✅ GOOD: Base class eliminates duplication
class BaseEmailService(ABC):
    """Single source of truth for email operations."""

    async def send_email_safely(self, recipient: str, subject: str, content: str) -> bool:
        """Common email sending logic - no duplication across services."""
        # Common validation, error handling, retry logic
        pass

    @abstractmethod
    async def send_review_notification(self, thread_id: str, data: dict) -> bool:
        """Service-specific implementation."""
        pass

# ✅ GOOD: Centralized validation utilities
class CommonValidators:
    """Single source of truth for validation logic."""

    @staticmethod
    def validate_email(email: str) -> bool:
        """Used across all services - no validation duplication."""
        pass

# ❌ BAD: Duplicated functionality across services
class DuplicateEmailService1:
    async def send_email(self, recipient: str, subject: str, content: str) -> bool:
        # Repeated validation and sending logic
        pass

class DuplicateEmailService2:
    async def send_message(self, recipient: str, subject: str, content: str) -> bool:
        # Same logic duplicated - DRY violation
        pass
```

#### **DRY Detection Commands**

```bash
# Detect potential duplication patterns
grep -r "class.*Service" src/ --include="*.py" | sort
grep -r "def validate_" src/ --include="*.py" | sort
grep -r "async def save_" src/ --include="*.py" | sort
find . -name "*.py" -exec basename {} \; | sort | uniq -d  # Duplicate filenames
```

#### **DRY Decision Matrix**

| Situation                        | Action                                           | Reasoning                       |
| -------------------------------- | ------------------------------------------------ | ------------------------------- |
| **Similar method exists**        | Extend existing class or create base class       | Maintain single source of truth |
| **Repeated validation logic**    | Extract to `CommonValidators` utility            | Centralize business rules       |
| **Similar class responsibility** | Merge into single class or inheritance hierarchy | Align with domain concepts      |
| **Magic numbers repeated**       | Create named constants with business context     | Make business rules explicit    |
| **Common error patterns**        | Create error handling mixins                     | Standardize error handling      |

### Code Quality Requirements

- **Black** formatting (88 char line limit)
- **Type hints** everywhere with modern syntax
- **Pydantic schemas** for all LangGraph node I/O
- **Comprehensive docstrings** with business context
- **DRY compliance** - no duplicated functionality

### Detailed Guidance

**📖 Read `code_quality_practices/ARCHITECTURE_GUIDE.md`** for comprehensive architecture guidance including:

- Python code standards and conventions
- LangGraph/LangSmith architecture patterns
- Integration client design patterns
- Error handling and resilience patterns
- Configuration management strategies

---

## 🔄 Refactoring Best Practices

### Quick Refactoring Reference

- **Only refactor with green tests**
- **Make one change at a time**
- **Preserve external behavior**
- **Use design patterns appropriately**

### Detailed Guidance

**📖 Read `code_quality_practices/REFACTORING_BEST_PRACTICES.md`** for comprehensive refactoring guidance including:

- Core refactoring principles and safety nets
- Python-specific refactoring techniques
- Design pattern applications (Strategy, Factory, Observer, Template Method)
- Code smell detection and solutions
- Advanced refactoring strategies
- Success measurement and validation

---

## 🧵 Working with Strings

### Quick String Standards Reference

- **Use f-strings** for simple formatting: `f"Invoice {id}: ${amount:,.2f}"`
- **Constants for all user-facing text** and regex patterns
- **Validate inputs** with compiled regex patterns
- **Clean text before LLM processing** (remove OCR artifacts)
- **Use generators** for large text processing

### Detailed Guidance

**📖 Read `code_quality_practices/WORKING_WITH_STRINGS_GUIDE.md`** for comprehensive string handling including:

- String constants organization and naming conventions
- String operations and performance guidelines
- Regex patterns for document processing and validation
- LLM prompt templates and response parsing
- Text cleaning and normalization strategies
- Testing string operations with property-based testing

---

## 🏷️ Variable Naming Standards

### Quick Naming Reference

- **Self-explanatory names** eliminate mental mapping
- **Use domain terminology** from business context
- **Boolean variables** use `is_`, `has_`, `can_`, `should_` prefixes
- **Include units** for numeric values: `timeout_seconds`, `size_bytes`
- **Action verbs** for functions: `extract_`, `validate_`, `calculate_`

### Detailed Guidance

**📖 Read `code_quality_practices/VARIABLE_NAMING_GUIDE.md`** for comprehensive naming standards including:

- Code Complete 2 naming principles and patterns
- Domain-specific naming for LangGraph/LangSmith
- Variable naming by data type and scope
- Function and class naming conventions
- Anti-patterns to avoid and naming checklists

---

## 🔨 Code Construction Practices

### Quick Construction Reference

- **Defensive programming** with input validation and assertions
- **Fail fast, fail safe** with proper error boundaries
- **Single responsibility** per function and class
- **Resource management** with proper cleanup and timeouts
- **Constants for magic numbers** with business context
- **NO backwards compatibility wrappers** - Fix calling code instead of adding compatibility methods

### ⚠️ CRITICAL: No Backwards Compatibility Wrappers

**ALWAYS replace components completely instead of adding compatibility layers.**

**Core Principle**: When refactoring to improve architecture, REPLACE the old implementation entirely rather than wrapping it for compatibility.

❌ **Bad Approach - Compatibility Wrappers:**

```python
class UnifiedDatabaseService:
    """Compatibility wrapper around old DatabaseService."""
    def __init__(self):
        self.old_service = OldDatabaseService()  # Keeps old code alive
        self.new_manager = NewOperationsManager()

    async def save_workflow(self, state):
        # Delegates to old system - no real improvement
        return await self.old_service.save_complete_workflow(state)

async def _initialize_client(self):
    """Legacy compatibility method."""
    # Compatibility wrapper code that adds confusion
```

✅ **Good Approach - Complete Replacement:**

```python
class DatabaseService:
    """Clean new implementation using four-component architecture."""
    def __init__(self):
        self.operations_manager = DatabaseOperationsManager()
        self.connection_manager = DatabaseConnectionManager()
        # Only new components - old code completely removed

    async def save_workflow(self, state):
        # Direct implementation using new architecture
        return await self.operations_manager.save_workflow(state)

# Update all calling code to use new interface
database_service = DatabaseService()  # No old dependencies
```

**Why complete replacement matters:**

- **Eliminates technical debt**: Old code is completely removed, not hidden
- **Forces proper architecture**: Can't rely on old patterns as crutches
- **Cleaner testing**: Only test new implementation, not compatibility layers
- **Better performance**: No overhead from delegation or compatibility checks
- **Clearer intent**: Code reflects actual architecture, not historical artifacts
- **Easier maintenance**: Single implementation to maintain and understand

**Replacement Strategy:**

1. **Build new implementation** with complete functionality
2. **Update all calling code** to use new interface directly
3. **Remove old implementation** entirely (archive if needed for reference)
4. **Update tests** to validate new implementation only
5. **Update documentation** to reflect new architecture

**When this applies:**

- Database service refactoring (current work)
- Email service decomposition
- API client replacements
- Workflow step modernization
- Any architectural improvement where old and new serve same purpose

### Detailed Guidance

**📖 Read `code_quality_practices/CODE_CONSTRUCTION_GUIDE.md`** for systematic construction including:

- Code Complete 2 defensive programming principles
- Systematic error handling and recovery strategies
- Performance-conscious construction patterns
- Resource management and memory efficiency
- Code quality verification checklists

---

## 🐛 Debugging and Error Handling

### Quick Debugging Reference

- **Scientific method** for systematic bug hunting
- **Comprehensive error context** for effective debugging
- **Proactive input validation** to prevent errors
- **Structured logging** with debugging information
- **Error recovery strategies** based on error classification

### 🔍 **MANDATORY: Bug Investigation Process**

**For ALL bug investigations, use the standardized bug investigation process.**

#### Quick Bug Investigation Reference

1. **📋 Create investigation issue** using standardized template
2. **🎯 Identify context gaps** - List what we don't know first
3. **📊 Prioritize unknowns** - Focus on biggest impact areas
4. **🔬 Investigate systematically** - Fill context gaps with evidence
5. **💡 Capture all hypotheses** - Even weak ones provide learning value
6. **🏆 Rank top 3 root causes** - Based on evidence and confidence
7. **🧪 Test fixes systematically** - Write failing tests first
8. **📚 Document learnings** - Build institutional knowledge

#### Bug Investigation Template Structure

```markdown
# Bug Investigation: [Title]

## 1. Context & Observations

- Observed Behavior: [What's happening]
- Expected Behavior: [What should happen]
- Environment: [System details, recent changes]
- Reproduction Steps: [1, 2, 3...]

## 2. Unknowns & Context Gaps (Prioritized)

- [ ] Biggest Unknown #1: [High impact unknown]
- [ ] Biggest Unknown #2: [Medium impact unknown]
- [ ] Smaller Unknowns: [Lower impact areas]

## 3. Investigation Notes & Hypotheses

- Unknown #1 Investigation: [Methods, findings, hypotheses]
- Unknown #2 Investigation: [Methods, findings, hypotheses]

## 4. Refined Root Causes (Top 3)

1. Most Likely Cause: [Evidence, confidence, test plan]
2. Possible Cause #2: [Evidence, confidence, test plan]
3. Possible Cause #3: [Evidence, confidence, test plan]

## 5. Fix & Testing Plan

- Proposed Fix: [Solution description]
- Implementation Steps: [Detailed steps]
- Test Plan: [Unit, integration, regression tests]
- Rollback Plan: [Safety measures]

## 6. Results & Report

- ✅ What worked: [Successful fixes]
- ❌ What didn't work: [Failed attempts]
- 🔄 Remaining context gaps: [Still unknown]
- ➡️ Next steps: [Follow-up tasks]
```

#### Investigation Tools & Commands

```bash
# System Health Check
./dev-tools/scripts/health-check.sh

# Log Analysis
tail -f logs/langgraph-server.log | grep -i error
grep -r "ERROR\|CRITICAL" logs/ --include="*.log" | tail -20

# Service Status
curl -s http://localhost:2024/health || echo "LangGraph server down"
curl -s http://localhost:8000/health || echo "API server down"

# Database Connectivity
python -c "from src.config.dependencies import get_database_client; client = get_database_client(); print('Database:', 'OK' if client.test_connection() else 'FAILED')"
```

### Detailed Guidance

**📖 Read `construction_best_practices/BUG_INVESTIGATION_PROCESS.md`** for comprehensive bug investigation including:

- Complete investigation workflow with mermaid diagram
- Standardized issue template with priority matrix
- Investigation tools and diagnostic commands
- Testing integration with bug reproduction tests
- Success metrics and continuous improvement processes

**📖 Read `code_quality_practices/DEBUGGING_ERROR_HANDLING_GUIDE.md`** for complete error handling including:

- Systematic debugging methodologies
- Error taxonomy and recovery strategies
- Debugging tools and utilities
- Runtime diagnostics and monitoring
- Error prevention and testing strategies

---

## 📚 README Documentation Standards

### Quick README Reference

- **Create README before coding** - Documentation-first approach
- **Update README with every change** - Keep documentation current
- **Include business context** - Explain WHY, not just WHAT
- **Test all code examples** - Ensure samples work
- **Update top-level README** for major changes

### Detailed Guidance

**📖 Read `code_quality_practices/README_GUIDANCE.md`** for comprehensive documentation standards including:

- README creation and maintenance workflow
- Standard templates and structure patterns
- Content quality standards and checklists
- Module-specific README patterns
- Integration with TDD workflow
- Automated validation and tooling

---

## 📋 MANDATORY: Markdown Plan Creation Templates

**For ALL implementation and investigation work, use standardized markdown plan templates.**

### Quick Plan Template Reference

- **Implementation Plans**: Use [`construction_best_practices/MARKDOWN_PLAN_TEMPLATE.md`](construction_best_practices/MARKDOWN_PLAN_TEMPLATE.md)
- **Investigation Plans**: Use template with investigation-specific sections
- **All Plans Must Include**: TDD approach, Code Construction guidelines reference, 85%+ coverage requirement, server startup validation

### Template Requirements

**Every markdown plan MUST:**

1. **Reference Code Construction Best Practices Guidelines** - [`construction_best_practices/CODE_CONSTRUCTION_GUIDE.md`](construction_best_practices/CODE_CONSTRUCTION_GUIDE.md)
2. **Read and understand all required context** - Relevant documentation and code
3. **Include Test-Driven Development approach** - [`construction_best_practices/TDD_WORKFLOW_GUIDE.md`](construction_best_practices/TDD_WORKFLOW_GUIDE.md)
4. **Ensure 85%+ unit test coverage** - Specific coverage validation commands
5. **Include server startup validation** - Confirm server starts after changes
6. **Follow file organization guidelines** - Clean up unused files, proper organization

### Template Usage Guidelines

**📖 Read `construction_best_practices/MARKDOWN_PLAN_TEMPLATE_USAGE.md`** for comprehensive template guidance including:

- When and how to use templates for different plan types
- Template structure and customization guidelines
- Content standards and formatting conventions
- Quality assurance and review processes
- Integration with project development workflow

### Plan Type Organization

| Plan Type                | Template Usage | File Location                      |
| ------------------------ | -------------- | ---------------------------------- |
| **Implementation Plans** | Required       | `docs/implementation/`             |
| **Investigation Plans**  | Required       | `dev-tools/scripts/investigation/` |
| **Architecture Plans**   | Required       | `docs/adr/`                        |
| **Testing Plans**        | Required       | `dev-tools/test-results/`          |
| **Operations Plans**     | Required       | `cicd/`                            |

### Example Templates

- **Implementation Example**: [`docs/implementation/EXAMPLE_IMPLEMENTATION_PLAN.md`](docs/implementation/EXAMPLE_IMPLEMENTATION_PLAN.md)
- **Investigation Example**: [`dev-tools/scripts/investigation/EXAMPLE_INVESTIGATION_PLAN.md`](dev-tools/scripts/investigation/EXAMPLE_INVESTIGATION_PLAN.md)

---

## ✅ Definition of Done Checklist

For ANY feature or refactor:

**Pre-Implementation:**

- [ ] **README.md consulted** for business context
- [ ] **README created/updated** for new modules or significant changes
- [ ] **Markdown plan created** using standardized template for work >4 hours
- [ ] **Plan references Code Construction Guidelines** and required context documentation
- [ ] **Appropriate guide referenced** (TDD, Commenting, Testing, Architecture, Naming, Construction, Debugging, Strings, README, or Refactoring)
- [ ] **DRY analysis completed** - searched for existing similar functionality

**DRY Compliance:**

- [ ] **No duplicated business logic** - checked for existing similar functionality
- [ ] **Existing components evaluated** - determined if new functionality belongs in existing class
- [ ] **Base classes considered** - used inheritance/composition instead of duplication
- [ ] **Common patterns extracted** - repeated logic moved to utilities or base classes
- [ ] **Magic numbers eliminated** - used named constants with business context
- [ ] **Validation logic centralized** - used common validators instead of inline validation

**TDD Process:**

- [ ] **Development TDD for new features** - Integration tests using real components and real dependencies
- [ ] **Unit TDD for behaviors** - Unit tests using real component but mocked dependencies
- [ ] **Direct debugging used for quick validation** - Debug statements in production code instead of separate test files
- [ ] **Production environment testing** - Verified functionality in LangGraph server or actual runtime
- [ ] **Failing tests written FIRST** that capture acceptance criteria
- [ ] **Comments-first implementation design** completed before coding
- [ ] **Test approach documented** - Clear distinction between development vs unit tests vs direct debugging

**Code Quality:**

- [ ] **Development tests pass** - Integration tests with real system components
- [ ] **Unit tests pass** - Isolated behavior tests with mocked dependencies
- [ ] **Production environment validated** - Functionality verified in actual runtime (LangGraph server, API endpoints)
- [ ] **Debug statements cleaned up** - Temporary debug code removed or converted to permanent logging
- [ ] **All tests have appropriate markers** (@pytest.mark.integration vs @pytest.mark.unit)
- [ ] **Business logic comments** explain "why" decisions were made
- [ ] **All public functions** have comprehensive docstrings
- [ ] **README documentation** updated with examples and business context
- [ ] **Coverage maintained or higher** (≥85% integration, ≥90% unit)
- [ ] **Variable names** follow self-explanatory naming standards
- [ ] **String operations** follow constants and validation standards
- [ ] **Error handling** implemented with proper recovery strategies

**Async Compliance (for LangGraph workflows):**

- [ ] **All I/O operations** use `asyncio.to_thread()` or native async
- [ ] **All async methods** have `async def` signatures
- [ ] **All async calls** use `await` keyword
- [ ] **LangGraph server starts** without `--allow-blocking` flag
- [ ] **No blocking call errors** in workflow execution logs

**File Organization:**

- [ ] **No duplicate files** - Run duplication detection commands
- [ ] **Development files organized** - Scripts in `dev-tools/scripts/`, logs in `logs/`, CI/CD in `cicd/`
- [ ] **References updated** - All paths corrected after file moves
- [ ] **Root directory clean** - No development artifacts in project root

**Integration:**

- [ ] **LangSmith datasets** updated if outputs changed intentionally
- [ ] **Performance benchmarks** maintained

---

## 📚 Complete Reference Documentation

### 🚀 Foundational Concepts

| Guide                                | Purpose                               | When to Use                       |
| ------------------------------------ | ------------------------------------- | --------------------------------- |
| **LEVERAGE_HIERARCHY_SYSTEM**        | Task routing and ROI optimization     | For EVERY task and decision       |
| **DESIGN_INVESTIGATION_GUIDANCE.md** | Architectural decision investigations | For technology and design choices |

### 🧪 Development Process Guides

| Guide                                       | Purpose                               | When to Use                       |
| ------------------------------------------- | ------------------------------------- | --------------------------------- |
| **TDD_WORKFLOW_GUIDE.md**                   | Comprehensive TDD process             | For ALL code changes              |
| **INTEGRATION_PLAYBOOK_GUIDE.md**           | External service integration playbook | For ALL external API integrations |
| **INTEGRATION_PLAYBOOK_QUICK_REFERENCE.md** | Integration process quick reference   | During active integration work    |
| **ASYNC_PROGRAMMING_LANGGRAPH_GUIDE.md**    | Complete async programming patterns   | For ALL LangGraph development     |
| **ASYNC_QUICK_REFERENCE.md**                | Quick async patterns & debugging      | When fixing blocking calls        |
| **COMMENTING_BEST_PRACTICES.md**            | Complete commenting standards         | When writing ANY code             |
| **TESTING_QUALITY_GUIDE.md**                | Testing patterns & quality gates      | When writing tests or CI/CD       |
| **COVERAGE_REQUIREMENTS_UPDATED.md**        | Coverage standards & enforcement      | When improving test coverage      |

### 🏗️ Architecture & Quality Guides

| Guide                                 | Purpose                                 | When to Use                         |
| ------------------------------------- | --------------------------------------- | ----------------------------------- |
| **ARCHITECTURE_GUIDE.md**             | Code standards & design patterns        | When designing components           |
| **WORKING_WITH_STRINGS_GUIDE.md**     | String handling & regex patterns        | When processing text data           |
| **VARIABLE_NAMING_GUIDE.md**          | Code Complete 2 naming standards        | When naming ANY code element        |
| **CODE_CONSTRUCTION_GUIDE.md**        | Defensive programming principles        | When writing robust code            |
| **BUG_INVESTIGATION_PROCESS.md**      | Standardized bug investigation workflow | When investigating ANY bug or issue |
| **DEBUGGING_ERROR_HANDLING_GUIDE.md** | Systematic debugging & error recovery   | When debugging or handling errors   |
| **README_GUIDANCE.md**                | Documentation standards & maintenance   | When creating/updating READMEs      |
| **REFACTORING_BEST_PRACTICES.md**     | Safe refactoring techniques             | When improving existing code        |

### Project-Specific References

- **TDD Essentials**: `TDD-essentials.md` (project root)
- **Workflow Patterns**: `src/workflow/steps/README.md`
- **Integration Patterns**: `src/integrations/README.md`
- **Service Architecture**: `src/services/README.md`
- **Testing Conventions**: `tests/unit_tests/README.md`

---

## ⚡ Quick Commands

```bash
# **FAST DEBUGGING**: Direct debugging without test files (PREFERRED)
python -c "import sys; sys.path.append('src'); from module import function; print(function())"  # Quick validation
langgraph dev  # Test in real production environment
curl -X POST "http://localhost:2024/runs/stream" -H "Content-Type: application/json" -d '{"assistant_id": "workflow", "input": {"test": true}}'  # Real workflow test

# **FAST & RELIABLE**: Script-based testing for multi-step validation (RECOMMENDED)
# 1. Create script file with meaningful name
cat > test_feature.py << 'EOF'
#!/usr/bin/env python3
import sys; sys.path.append('src')
from src.module import function
print("Testing:", function())
EOF
# 2. Run script
python test_feature.py
# 3. Clean up
rm test_feature.py

# **NEW**: Complete Definition of Done automation (RECOMMENDED)
./dev-tools/scripts/prepare-commit.sh                                    # Validate everything + git pull --rebase
./dev-tools/scripts/prepare-commit.sh --auto-commit --message "feat: ..."  # Full automation with rebase
./dev-tools/scripts/prepare-commit.sh --skip-rebase                      # Skip rebase if already synced

# **NEW**: Git workflow improvements (one-time setup)
./dev-tools/scripts/setup-git-config.sh                                  # Configure better git workflow
git squash-last-two                                                      # Combine last two commits easily
git quick-commit "message"                                               # Stage all + commit in one command

# **NEW**: Commit squashing (interactive rebases don't work in AI environments)
git reset --soft HEAD~N                                                  # Squash last N commits into staging
git commit -m "comprehensive message"                                    # Create single commit with all changes
# Example: git reset --soft HEAD~6 && git commit -m "feat: major feature implementation"

# Fast TDD loop with coverage gate (ONLY for business logic, not quick debugging)
pytest -m "unit or node" -x -q --cov=src --cov-fail-under=90

# Coverage check with detailed report
pytest --cov=src --cov-fail-under=90 --cov-report=html

# Code quality and security check
black . && isort . && ruff check . && mypy src/ && bandit -r src/

# Security vulnerability scan
pip-audit --desc && safety check

# Pre-commit hook validation
pre-commit run --all-files

# Comment quality check
grep -r "# TODO\|# FIXME\|# XXX" src/ --exclude-dir=__pycache__

# LangSmith trace cleanup (test mode)
export LANGCHAIN_PROJECT="test-$(date +%s)" && pytest -m "graph or e2e"

# DRY Detection Commands (duplication prevention)
grep -r "class.*Service" src/ --include="*.py" | sort              # Find service classes
grep -r "def validate_" src/ --include="*.py" | sort               # Find validation methods
grep -r "async def (save_|get_|update_|delete_)" src/ --include="*.py" | sort  # Find CRUD patterns
find . -name "*.py" -exec basename {} \; | sort | uniq -d         # Find duplicate filenames
grep -r "MAX_.*=" src/ --include="*.py" | sort                     # Find repeated constants
grep -r "TIMEOUT.*=" src/ --include="*.py" | sort                  # Find timeout constants

# File Organization & Duplication Management
./dev-tools/scripts/check_duplicates.sh  # Detect duplicate files (cache-aware)
./dev-tools/scripts/cleanup-temp-files.sh --dry-run  # Preview temporary file cleanup
./dev-tools/scripts/cleanup-temp-files.sh --force    # Non-interactive cleanup (CI/CD safe)

# Manual verification that git tracking is clean
git status --ignored  # Verify no caches tracked by git

# File duplication detection and cleanup
find . -name "*.py" -type f -exec basename {} \; | sort | uniq -d
find . -name "*.md" -type f -exec basename {} \; | sort | uniq -d
find . -name "*.yml" -o -name "*.yaml" -type f -exec basename {} \; | sort | uniq -d
```

---

## 🧹 MANDATORY: File Organization & Duplication Prevention

**Always maintain clean project organization and prevent file duplications.**

### Quick Organization Reference

- **Scripts/utilities**: Use `dev-tools/scripts/` directory
- **Test results**: Use `dev-tools/test-results/` directory
- **Logs**: Use `logs/` directory
- **CI/CD**: Use `cicd/` directory
- **Development artifacts**: Keep separate from production code

### File Duplication Detection Commands

```bash
# Detect duplicate filenames across project
find . -name "*.py" -type f -exec basename {} \; | sort | uniq -d
find . -name "*.md" -type f -exec basename {} \; | sort | uniq -d
find . -name "*.sh" -type f -exec basename {} \; | sort | uniq -d

# Find specific duplicated files
find . -name "buildspec.yml" -type f
find . -name "*CI_CD*" -type f
find . -name "*test-*.sh" -type f

# Check for development files in root that should be organized
ls -la | grep -E "\.(py|txt|log)$" | grep -E "(test_|run_|update_|.*\.log|.*results\.txt)"
```

### Cleanup Workflow

When file duplications are detected:

1. **Identify the authoritative version**:

   - Check modification dates: `ls -la <duplicate_files>`
   - Compare content: `diff <file1> <file2>`
   - Verify functionality: Ensure the correct version works

2. **Remove duplicates systematically**:

   - Keep the version in the proper organized location
   - Remove versions from incorrect locations (usually root directory)
   - Update any references to the old paths

3. **Update documentation and references**:

   - Check for hardcoded paths in scripts and documentation
   - Update README files if structure changed
   - Verify CI/CD scripts reference correct paths

4. **Verify cleanup**:
   - Run duplication detection commands again
   - Test affected functionality
   - Ensure no broken references remain

### Organization Guidelines

- **Production code**: `src/` directory only
- **Test suite**: `tests/` directory only
- **Development scripts**: `dev-tools/scripts/` directory
- **CI/CD infrastructure**: `cicd/` directory
- **Logs and artifacts**: `logs/` and `dev-tools/test-results/`
- **Documentation**: Root level for main docs, subdirectories for specific docs

### Prevention Checklist

- [ ] **Before creating new files**: Check if similar file exists elsewhere
- [ ] **After moving files**: Remove old versions and update references
- [ ] **During development**: Use organized directories from the start
- [ ] **Before committing**: Run duplication detection commands
- [ ] **During code reviews**: Verify file organization follows guidelines

---

**Remember: For quick validation, use direct debugging in production code instead of separate test files. For systematic development, use TDD with real components. Always add comments-first pseudocode before implementation. Reference the detailed guides for comprehensive guidance on each aspect of development! ⚡🧪📝✅**

---

## 🔗 MANDATORY: External Service Integration Playbook

**CRITICAL: All external service integrations must follow the Integration Playbook process.**

### 🎯 **When to Use Integration Playbook**

**ALWAYS use when integrating**:

- External REST APIs or GraphQL services
- Third-party SDKs or libraries with network calls
- Webhook endpoints from external services
- Message queues or event streams
- External databases or storage services
- Authentication providers (OAuth, SAML, JWT)

### 🚀 **Quick Integration Reference**

**Before coding ANY external service integration**:

1. **📋 Create GitHub Issue** using `.github/ISSUE_TEMPLATE/integration.yml`
2. **📖 Read Integration Playbook** (`construction_best_practices/INTEGRATION_PLAYBOOK_GUIDE.md`)
3. **✅ Complete Definition of Ready** checklist before writing code
4. **🔄 Follow 11-Step Process** for systematic integration
5. **✅ Complete Definition of Done** before deployment

### 📊 **Integration Quality Standards**

**Every external integration must have**:

- **Contract tests**: Validate request/response schemas
- **Semantic tests**: Verify cause→effect behaviors across API calls
- **Resilience tests**: Handle rate limits, timeouts, retries
- **Security compliance**: Secrets management, data classification
- **Documentation**: README with quickstart + troubleshooting
- **Runbook**: Operations guide with monitoring and rollback procedures

### 🧪 **Integration TDD Approach**

**Use Development TDD for integrations**:

```python
@pytest.mark.integration
@pytest.mark.live  # Real external service calls
async def test_end_to_end_document_processing():
    """Development TDD: Real integration with real external service."""
    # Arrange: Real service configuration
    processor = DocumentProcessor(real_config, real_api_client)

    # Act: Real API calls to external service
    job = await processor.submit_document(test_pdf)
    result = await processor.wait_for_completion(job.id)

    # Assert: Real response validation
    assert result.status == "COMPLETED"
    assert result.extracted_data.invoice_number
```

**Use Unit TDD for integration components**:

```python
@pytest.mark.unit
def test_request_mapper_with_mocked_service():
    """Unit TDD: Test mapping logic with mocked dependencies."""
    # Arrange: Real mapper, mocked external service
    mapper = RequestMapper(config)
    mock_api = Mock(spec=ExternalAPIClient)

    # Act: Real mapping logic
    payload = mapper.create_request(document)

    # Assert: Validate mapping without external calls
    assert payload["input_type"] == "pdf"
    assert "options" in payload
```

### 📁 **Integration File Structure**

**Every integration must follow this structure**:

```
integrations/<service>/
├── 00-scope.md                    # Objectives and constraints
├── context-gaps.md                # Investigation log
├── README.md                      # Quickstart and troubleshooting
├── RUNBOOK.md                     # Operations and monitoring
├── config.example.yaml            # Configuration template
├── diagrams/state-and-sequence.md # State and sequence diagrams
├── src/
│   ├── client.py                  # Integration client
│   ├── models.py                  # Domain models
│   ├── constants.py               # Business constants
│   └── mappers.py                 # Request/response mapping
└── tests/
    ├── test_contract.py           # Schema validation
    ├── test_semantics.py          # Stateful behavior
    ├── test_resilience.py         # Error handling
    └── test_performance.py        # Load and timing
```

### ⚠️ **Integration Anti-Patterns to Avoid**

❌ **Don't do this**:

- Skip semantic contract testing (only test happy path)
- Hardcode API keys or secrets in code
- Ignore rate limits and retry logic
- Missing monitoring and alerting
- No rollback plan or feature flags

✅ **Do this instead**:

- Test all stateful API interactions with real service calls
- Use vault/environment variables for secrets management
- Implement exponential backoff with jitter for retries
- Add comprehensive logging with request tracing
- Feature flags with gradual rollout plan

### 🎯 **Integration Success Criteria**

**Before any integration goes to production**:

- [ ] **95%+ test coverage** including contract, semantic, and resilience tests
- [ ] **Documentation complete** with README, runbook, and troubleshooting guide
- [ ] **Security review passed** for data classification and secrets management
- [ ] **Performance validated** against SLA requirements
- [ ] **Monitoring configured** with alerts and dashboards
- [ ] **Rollback plan tested** with feature flag kill switch

### 🔄 **Integration with Existing Workflow**

**Integration Playbook works with our standards**:

- **TDD Workflow**: Use Development TDD for integration tests, Unit TDD for components
- **Code Construction**: Apply defensive programming for external service calls
- **Error Handling**: Use systematic debugging for integration failures
- **Documentation**: Follow README guidance for integration documentation

---
