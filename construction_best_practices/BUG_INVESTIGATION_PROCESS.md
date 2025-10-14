# 🐞 Bug Investigation Process

This document describes the standardized process for investigating bugs in the Financial Document Processing Pipeline.  
The mission is to **uncover context gaps, capture all potential hypotheses, refine root causes, test fixes, and document learnings**.

---

## 🎯 Investigation Philosophy

**Bugs are knowledge discovery missions.** Every bug investigation should:

- **Start with unknowns** - Identify what we don't know first
- **Capture all hypotheses** - Even weak ones provide learning value
- **Test systematically** - Use scientific method for investigation
- **Document learnings** - Build institutional knowledge for future debugging

---

## 🔄 Debugging Flow Diagram

```mermaid
flowchart TD

A[🐞 Bug Reported] --> B[Identify Context Gaps]
B --> C[Prioritize Unknowns<br/>(Most Unknown → Less Unknown)]
C --> D[Investigate Each Area<br/>Fill Context Gaps]
D --> H[Note Down All Potential Hypotheses]
H --> E[Refine & Rank Top 3 Root Cause Hypotheses]
E --> F[Test Fix for Most Likely Cause]
F --> G{Fix Successful?}

G -->|Yes| I[✅ Document Fix<br/>Close Issue]
G -->|No| J[❌ Record What Didn't Work<br/>Remaining Context Gaps]
J --> D

style A fill:#ffcccc
style I fill:#ccffcc
style J fill:#ffffcc
```

---

## 📋 Bug Investigation Issue Template

### 1. Context & Observations

**Observed Behavior:**  
*Describe exactly what is happening - include error messages, unexpected outputs, system behavior*

**Expected Behavior:**  
*Describe what should happen instead - reference requirements, user stories, or system specifications*

**Environment:**  
- **System**: Development/Staging/Production
- **LangGraph Server**: Port 2024 status and logs
- **API Server**: Port 8000 status and logs  
- **Frontend**: Port 3000 status and logs
- **Database**: PostgreSQL/Google Sheets connection status
- **Storage**: Local/S3 configuration
- **Dependencies**: Python version, key package versions
- **Recent Changes**: Last deployment, configuration changes, code updates

**Reproduction Steps:**
1. Step 1...
2. Step 2...
3. Step 3...

**Frequency:** Always/Sometimes/Rare (include percentage if known)

---

### 2. Unknowns & Context Gaps (Prioritized)

*List what we don't know, starting with the biggest unknowns that would most impact our understanding*

- [ ] **Biggest Unknown #1:** *e.g., "Why does the email extraction fail only for certain Gmail accounts?"*
- [ ] **Biggest Unknown #2:** *e.g., "What causes the database connection timeout in production but not development?"*
- [ ] **Smaller Unknowns:** *e.g., "Are there specific document formats that trigger the OCR failure?"*

**Investigation Priority Matrix:**

| Unknown | Impact | Effort | Priority |
|---------|--------|--------|----------|
| Unknown #1 | High | Medium | 🔴 Critical |
| Unknown #2 | Medium | Low | 🟡 Important |
| Unknown #3 | Low | High | 🟢 Nice-to-have |

---

### 3. Investigation Notes & Hypotheses

*As you investigate, jot down **all potential hypotheses**, even weak ones. Mark evidence that supports or eliminates them.*

#### Unknown #1 Investigation: *[Description]*
**Investigation Methods:**
- [ ] Log analysis: `grep -r "error_pattern" logs/`
- [ ] Database queries: Check for data inconsistencies
- [ ] Network analysis: Test API connectivity
- [ ] Code review: Examine recent changes in related modules

**Findings:**
- *Finding 1: Evidence found in logs/langgraph-server.log*
- *Finding 2: Database query shows...*

**Possible Hypotheses:**
- **H1:** *Hypothesis description* ✅ Supported by evidence / ❌ Eliminated by evidence / ❓ Needs more investigation
- **H2:** *Hypothesis description* ✅ Supported by evidence / ❌ Eliminated by evidence / ❓ Needs more investigation

#### Unknown #2 Investigation: *[Description]*
**Investigation Methods:**
- [ ] Performance monitoring: Check resource usage
- [ ] Configuration review: Compare dev vs prod settings
- [ ] Dependency analysis: Check for version conflicts

**Findings:**
- *Finding 1: ...*
- *Finding 2: ...*

**Possible Hypotheses:**
- **H3:** *Hypothesis description* ✅/❌/❓
- **H4:** *Hypothesis description* ✅/❌/❓

---

### 4. Refined Root Causes (Top 3)

After investigation, rank the **three most likely root causes** based on evidence:

1. **Most Likely Cause:** *Description* 
   - **Evidence:** *What supports this hypothesis*
   - **Confidence:** High/Medium/Low
   - **Test Plan:** *How to verify this is the root cause*

2. **Possible Cause #2:** *Description*
   - **Evidence:** *What supports this hypothesis*
   - **Confidence:** High/Medium/Low
   - **Test Plan:** *How to verify this is the root cause*

3. **Possible Cause #3:** *Description*
   - **Evidence:** *What supports this hypothesis*
   - **Confidence:** High/Medium/Low
   - **Test Plan:** *How to verify this is the root cause*

---

### 5. Fix & Testing Plan

**Proposed Fix:** *Detailed description of the solution*

**Implementation Steps:**
- [ ] Step 1: *e.g., Update configuration in src/config/settings.py*
- [ ] Step 2: *e.g., Add error handling in src/workflow/steps/step01_extract_emails/main.py*
- [ ] Step 3: *e.g., Update tests in tests/unit_tests/workflow/steps/test_extract_emails.py*

**Test Plan:**
- [ ] **Unit Tests:** Write/update tests to cover the bug scenario
- [ ] **Integration Tests:** Verify fix works with real dependencies
- [ ] **Regression Tests:** Ensure fix doesn't break existing functionality
- [ ] **Performance Tests:** Verify fix doesn't impact system performance
- [ ] **Manual Testing:** Test the exact reproduction steps

**Rollback Plan:**
- [ ] Identify rollback steps if fix causes new issues
- [ ] Document configuration changes that need reverting
- [ ] Test rollback procedure in development environment

---

### 6. Results & Report

**✅ What worked:**
- *Successful fixes and their impact*
- *Root cause confirmation*
- *Performance improvements*

**❌ What didn't work:**
- *Failed attempts and why they failed*
- *Hypotheses that were eliminated*
- *Approaches that caused new issues*

**🔄 Remaining context gaps:**
- *Unknowns that still need investigation*
- *Areas where more monitoring is needed*
- *Technical debt identified during investigation*

**➡️ Next steps:**
- *Follow-up tasks*
- *Monitoring improvements*
- *Process improvements*
- *Documentation updates*

**📊 Impact Assessment:**
- **Users Affected:** Number/percentage of users impacted
- **System Performance:** Before/after metrics
- **Business Impact:** Revenue, user experience, operational efficiency
- **Technical Debt:** New debt created or existing debt resolved

---

### 7. Meta Information

**Reported by:** *Name/Role*  
**Date Reported:** *YYYY-MM-DD*  
**Date Resolved:** *YYYY-MM-DD*  
**Investigation Time:** *Hours spent*  
**Severity:** Critical/High/Medium/Low  
**Priority:** P0/P1/P2/P3  

**Links/References:**
- GitHub Issue: #XXX
- LangSmith Traces: [trace_id]
- Related Bugs: #XXX, #YYY
- Documentation: [link]
- Monitoring Dashboards: [link]

**Tags:** *e.g., email-processing, database, authentication, performance*

---

## 🔧 Investigation Tools & Commands

### Quick Diagnostic Commands

```bash
# System Health Check
./dev-tools/scripts/health-check.sh

# Log Analysis
tail -f logs/langgraph-server.log | grep -i error
tail -f logs/api-server.log | grep -i error
grep -r "ERROR\|CRITICAL" logs/ --include="*.log" | tail -20

# Service Status
curl -s http://localhost:2024/health || echo "LangGraph server down"
curl -s http://localhost:8000/health || echo "API server down"
curl -s http://localhost:3000 || echo "Frontend server down"

# Database Connectivity
python -c "
from src.config.dependencies import get_database_client
client = get_database_client()
print('Database connection:', 'OK' if client.test_connection() else 'FAILED')
"

# Performance Monitoring
ps aux | grep -E "(langgraph|uvicorn|node)" | grep -v grep
netstat -tulpn | grep -E "(2024|8000|3000)"
```

### Investigation Patterns

#### Email Processing Issues
```bash
# Check Gmail API connectivity
python dev-tools/scripts/test-gmail-connection.py

# Analyze email extraction logs
grep -r "extract_emails" logs/ --include="*.log" | tail -10

# Test email parsing
python -c "
from src.integrations.gmail.client import GmailClient
client = GmailClient()
emails = client.get_new_emails('has:attachment')
print(f'Found {len(emails)} emails')
"
```

#### Database Issues
```bash
# Test database operations
python scripts/test_neon_connection.py --quick

# Check for connection leaks
grep -r "connection.*timeout" logs/ --include="*.log"

# Analyze query performance
grep -r "slow.*query" logs/ --include="*.log"
```

#### LangGraph Workflow Issues
```bash
# Check workflow state
curl -s http://localhost:2024/threads | jq '.[] | select(.status=="error")'

# Analyze node execution
grep -r "node.*failed" logs/ --include="*.log"

# Check for blocking calls
grep -r "blocking.*call" logs/ --include="*.log"
```

---

## 🧪 Testing Integration

### Bug Reproduction Tests

**Always write a failing test that reproduces the bug before fixing it.**

```python
# Example bug reproduction test
@pytest.mark.integration
async def test_bug_reproduction_email_extraction_timeout():
    """
    Bug #123: Email extraction times out for large attachments
    
    This test reproduces the exact conditions that cause the timeout.
    """
    # Arrange: Create conditions that trigger the bug
    large_attachment_email = create_test_email_with_large_pdf(size_mb=50)
    
    # Act: Execute the failing operation
    with pytest.raises(TimeoutError, match="Email extraction timeout"):
        result = await extract_emails_node(WorkflowState(
            query="has:attachment",
            timeout_seconds=30  # This should timeout
        ))
    
    # Assert: Verify the bug is reproduced
    assert "timeout" in str(result.error).lower()
```

### Fix Validation Tests

```python
@pytest.mark.integration
async def test_bug_fix_email_extraction_handles_large_attachments():
    """
    Bug #123 Fix: Email extraction now handles large attachments with streaming
    
    This test verifies the fix works correctly.
    """
    # Arrange: Same conditions as bug reproduction
    large_attachment_email = create_test_email_with_large_pdf(size_mb=50)
    
    # Act: Execute with the fix
    result = await extract_emails_node(WorkflowState(
        query="has:attachment",
        timeout_seconds=300,  # Increased timeout
        use_streaming=True    # New streaming feature
    ))
    
    # Assert: Verify the fix works
    assert result.error is None
    assert len(result.extracted_documents) > 0
    assert result.processing_time < 300  # Within timeout
```

---

## 📚 Integration with Project Standards

### Code Quality During Bug Fixes

**Follow all standard development practices during bug investigation:**

- **TDD Approach:** Write failing tests first, then fix
- **Comments-First:** Document the bug and fix reasoning
- **DRY Compliance:** Don't duplicate bug fixes across modules
- **Async Compliance:** Ensure fixes don't introduce blocking calls
- **Coverage:** Maintain test coverage during bug fixes

### Documentation Updates

**Update relevant documentation after bug fixes:**

- [ ] **README.md:** Update if bug affects setup or usage
- [ ] **API Documentation:** Update if bug affects API behavior
- [ ] **Troubleshooting Guide:** Add common issues and solutions
- [ ] **Architecture Docs:** Update if bug reveals design issues

### Process Improvements

**Use bug investigations to improve development processes:**

- **Monitoring:** Add alerts for conditions that caused the bug
- **Testing:** Improve test coverage for bug-prone areas
- **Code Review:** Update checklists to catch similar issues
- **Documentation:** Improve setup guides to prevent configuration bugs

---

## 🎯 Success Metrics

### Investigation Quality

- **Time to Root Cause:** How quickly was the actual cause identified?
- **Hypothesis Accuracy:** How many hypotheses were correct vs eliminated?
- **Fix Success Rate:** Did the first fix attempt resolve the issue?
- **Regression Prevention:** Did the fix introduce new bugs?

### Process Improvement

- **Knowledge Capture:** How well was the investigation documented?
- **Reusability:** Can this investigation help with future similar bugs?
- **Process Refinement:** What process improvements were identified?
- **Team Learning:** What did the team learn from this investigation?

---

## 🔄 Continuous Improvement

### Post-Investigation Review

After resolving each bug, conduct a brief review:

1. **What went well?** Effective investigation techniques, good hypotheses
2. **What could improve?** Missed clues, inefficient approaches
3. **Process updates:** Changes to make future investigations faster
4. **Knowledge sharing:** Lessons learned for the team

### Investigation Pattern Library

Build a library of common investigation patterns:

- **Email Processing Bugs:** Common causes and diagnostic approaches
- **Database Issues:** Connection, performance, and data integrity problems
- **LangGraph Workflow Bugs:** State management, node failures, async issues
- **Authentication Problems:** OAuth, token management, permission issues
- **Performance Issues:** Memory leaks, slow queries, blocking calls

---

**Remember: Every bug is an opportunity to improve our understanding of the system and our debugging processes. Treat investigations as learning experiences that make the entire team more effective! 🔍📚✨**