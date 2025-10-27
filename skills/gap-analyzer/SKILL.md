---
name: gap-analyzer
description: Conducts continuous gap analysis from vision to implementation, identifying missing requirements, incomplete features, testing gaps, and documentation deficiencies. Use after major implementations, before releases, or when features feel incomplete. Returns structured gap report with action items.
allowed-tools: [Read, Grep, Glob]
---

# Gap Analyzer

## Purpose

Systematically identifies gaps between vision/requirements and actual implementation, ensuring features are truly complete before shipping.

## When to Use This Skill

**Use this skill when:**
- Features feel "complete" but something seems missing
- Before major releases or deployments
- After large implementations to validate completeness
- When requirements are vague or incomplete
- Investigating why features aren't shipping
- Post-implementation validation

**Examples:**
- "Analyze this feature for completeness gaps"
- "What's missing from this implementation?"
- "Validate requirements coverage before release"
- "Why does this feature feel incomplete?"
- "Identify gaps between spec and code"

## Gap Analysis Dimensions

### 1. Requirements Gap

**What it finds:**
- Features in specs but not implemented
- User needs not captured in requirements
- Edge cases not documented
- Non-functional requirements missing
- Acceptance criteria unclear

**Analysis Questions:**
- [ ] Are all specified features implemented?
- [ ] Are user stories complete with acceptance criteria?
- [ ] Are edge cases documented?
- [ ] Are performance requirements specified?
- [ ] Are security requirements captured?
- [ ] Are error scenarios defined?

**Example:**
```
REQUIREMENTS GAP: User Authentication

Documented Requirements:
✅ Login with email/password
✅ Password reset
✅ Session management

Missing Requirements (GAPS):
❌ OAuth integration (mentioned in marketing deck)
❌ Two-factor authentication (security best practice)
❌ Account lockout policy (not specified)
❌ Password complexity rules (assumed but not documented)
❌ Session timeout duration (unclear)
❌ Multi-device login handling (not addressed)

Actions:
- Document OAuth requirement or defer
- Define 2FA requirements with security team
- Specify lockout policy (attempts, duration)
- Document password rules (length, complexity)
- Define session timeout (30min? 24hr?)
- Clarify multi-device expectations
```

### 2. Implementation Gap

**What it finds:**
- Required code missing or incomplete
- Partial implementations ("TODO" markers)
- Mocked/stubbed functionality not implemented
- Integration points not connected
- Configuration missing

**Analysis Questions:**
- [ ] Are all code paths implemented (no TODOs)?
- [ ] Are mocks replaced with real implementations?
- [ ] Are all integrations connected?
- [ ] Is configuration complete?
- [ ] Are database migrations applied?
- [ ] Are API endpoints fully functional?

**Example:**
```
IMPLEMENTATION GAP: Payment Processing

Implemented:
✅ Credit card payment flow
✅ Order creation
✅ Success confirmation

Gaps (INCOMPLETE):
❌ TODO: Implement retry logic for failed payments
❌ MOCK: Payment gateway integration (using stub)
❌ Missing: Webhook handling for async payment status
❌ Missing: Refund processing
❌ Missing: Payment method storage for recurring
❌ Config: Production API keys not set

Actions:
- Implement payment retry with exponential backoff
- Replace mock with real gateway integration
- Add webhook endpoint for payment status updates
- Implement refund flow (critical for customer service)
- Add payment method tokenization
- Document production configuration requirements
```

### 3. Testing Gap

**What it finds:**
- Missing test coverage
- Untested edge cases
- No integration tests
- Performance testing missing
- Security testing gaps

**Analysis Questions:**
- [ ] Is unit test coverage ≥85%?
- [ ] Are edge cases tested?
- [ ] Are integration tests present?
- [ ] Are error scenarios tested?
- [ ] Is performance tested?
- [ ] Is security validated?

**Example:**
```
TESTING GAP: File Upload Feature

Existing Tests:
✅ Unit tests for happy path (78% coverage)
✅ Basic integration test

Gaps (MISSING TESTS):
❌ Edge case: File too large (>100MB)
❌ Edge case: Invalid file type
❌ Edge case: Upload interrupted mid-stream
❌ Edge case: Duplicate file name
❌ Security: Malicious file upload (virus scan)
❌ Performance: Concurrent uploads (100+ users)
❌ Integration: S3 upload failure handling

Target Coverage: 85% (currently 78%)

Actions:
- Add file size validation tests
- Test invalid file type rejection
- Test upload interruption handling
- Test duplicate name resolution
- Add virus scanning tests
- Performance test with 100 concurrent uploads
- Test S3 failure scenarios (network, auth, quota)
```

### 4. Documentation Gap

**What it finds:**
- Missing API documentation
- Outdated architecture diagrams
- No user guides
- Deployment instructions incomplete
- Code comments insufficient

**Analysis Questions:**
- [ ] Is API documentation complete?
- [ ] Are architecture diagrams current?
- [ ] Are user guides written?
- [ ] Are deployment steps documented?
- [ ] Are code comments adequate?
- [ ] Are examples provided?

**Example:**
```
DOCUMENTATION GAP: REST API

Existing Docs:
✅ Basic API overview
✅ Authentication guide

Gaps (MISSING DOCS):
❌ Endpoint reference incomplete (12 of 25 endpoints)
❌ Request/response examples missing
❌ Error codes not documented
❌ Rate limiting not explained
❌ Webhook documentation absent
❌ SDK usage examples missing
❌ Architecture diagram outdated (pre-microservices)

Actions:
- Document all 25 endpoints with examples
- Create error code reference table
- Explain rate limits (requests/min, quotas)
- Write webhook integration guide
- Provide SDK examples (Python, JavaScript, Ruby)
- Update architecture diagram (current microservices)
```

### 5. Error Handling Gap

**What it finds:**
- Exceptions not caught
- Error messages unclear
- No fallback mechanisms
- Partial error handling
- Silent failures

**Analysis Questions:**
- [ ] Are all exceptions caught?
- [ ] Are error messages user-friendly?
- [ ] Are fallbacks implemented?
- [ ] Are errors logged properly?
- [ ] Are failures recoverable?
- [ ] Are users notified of errors?

**Example:**
```
ERROR HANDLING GAP: Data Import Feature

Implemented Error Handling:
✅ File parsing errors caught
✅ Basic validation errors shown

Gaps (MISSING HANDLING):
❌ Database connection failure → silent fail
❌ Network timeout → no retry
❌ Partial import success → no rollback
❌ Validation errors → no line numbers
❌ Large file processing → no progress indicator
❌ Import failures → no notification email

Actions:
- Add database connection error handling + retry
- Implement network timeout retry with backoff
- Add transaction rollback for partial failures
- Include line numbers in validation errors
- Add progress bar for large imports
- Send email notification on failure
```

### 6. Performance Gap

**What it finds:**
- Slow queries
- N+1 database problems
- Missing indexes
- No caching
- Inefficient algorithms

**Analysis Questions:**
- [ ] Are response times acceptable (<500ms)?
- [ ] Are queries optimized?
- [ ] Are indexes present?
- [ ] Is caching implemented?
- [ ] Are algorithms efficient?
- [ ] Is concurrent load tested?

**Example:**
```
PERFORMANCE GAP: Dashboard Page

Current Performance:
- Page load: 4.2 seconds (target: <1s)
- Database queries: 47 queries per request
- No caching

Gaps (BOTTLENECKS):
❌ N+1 query problem in user list (1 + N queries)
❌ Missing index on created_at column
❌ Large JSON responses not paginated
❌ No Redis caching for frequently accessed data
❌ Unoptimized image loading (no CDN)
❌ JavaScript bundle too large (2.4MB)

Actions:
- Fix N+1 with eager loading (reduce 47 → 3 queries)
- Add composite index on (user_id, created_at)
- Implement pagination (50 items per page)
- Add Redis cache for dashboard stats (1hr TTL)
- Move images to CDN with lazy loading
- Code-split JavaScript (reduce to <500KB initial)
```

## Gap Analysis Workflow

### Complete Analysis Process

**Step 1: Scope Definition** (5 minutes)
```
Define what to analyze:
- Feature: [Name of feature]
- Requirements: [Link to specs/stories]
- Implementation: [Code location]
- Deadline: [Target ship date]
```

**Step 2: Requirements Review** (15 minutes)
```
- Read all requirements documents
- List expected features
- Identify acceptance criteria
- Note any ambiguities
```

**Step 3: Implementation Audit** (30 minutes)
```
- Review code for completeness
- Check for TODO/FIXME markers
- Verify all integrations
- Test manually through all flows
```

**Step 4: Testing Validation** (20 minutes)
```
- Check test coverage percentage
- Review test cases for edge cases
- Verify integration tests exist
- Run full test suite
```

**Step 5: Documentation Check** (15 minutes)
```
- Review API docs
- Check user guides
- Verify code comments
- Validate deployment docs
```

**Step 6: Gap Report Generation** (15 minutes)
```
- Categorize all gaps
- Prioritize by severity
- Estimate effort to close
- Create action items
```

**Total Time**: ~2 hours for comprehensive analysis

## Output Format

When conducting gap analysis, provide:

### Gap Analysis Report

```
GAP ANALYSIS REPORT
Feature: [Feature Name]
Date: [Analysis Date]
Analyst: [Agent/Person]
Status: [READY | NOT READY | NEEDS WORK]

EXECUTIVE SUMMARY
----------------
Overall Completeness: [X]%
Critical Gaps: [N]
Recommended Action: [SHIP | FIX GAPS | DEFER]
Time to Resolution: [X hours/days]

GAP BREAKDOWN
-------------

1. REQUIREMENTS GAP [Severity: HIGH/MEDIUM/LOW]
   Missing:
   - [ ] [Requirement 1]
   - [ ] [Requirement 2]

   Actions:
   - [Action 1] (Est: Xh)
   - [Action 2] (Est: Xh)

2. IMPLEMENTATION GAP [Severity: HIGH/MEDIUM/LOW]
   Incomplete:
   - [ ] [Code gap 1]
   - [ ] [Code gap 2]

   Actions:
   - [Action 1] (Est: Xh)
   - [Action 2] (Est: Xh)

3. TESTING GAP [Severity: HIGH/MEDIUM/LOW]
   Coverage: [X]% (Target: 85%)
   Missing Tests:
   - [ ] [Test 1]
   - [ ] [Test 2]

   Actions:
   - [Action 1] (Est: Xh)
   - [Action 2] (Est: Xh)

4. DOCUMENTATION GAP [Severity: HIGH/MEDIUM/LOW]
   Missing Docs:
   - [ ] [Doc 1]
   - [ ] [Doc 2]

   Actions:
   - [Action 1] (Est: Xh)
   - [Action 2] (Est: Xh)

5. ERROR HANDLING GAP [Severity: HIGH/MEDIUM/LOW]
   Unhandled:
   - [ ] [Error scenario 1]
   - [ ] [Error scenario 2]

   Actions:
   - [Action 1] (Est: Xh)
   - [Action 2] (Est: Xh)

6. PERFORMANCE GAP [Severity: HIGH/MEDIUM/LOW]
   Bottlenecks:
   - [ ] [Performance issue 1]
   - [ ] [Performance issue 2]

   Actions:
   - [Action 1] (Est: Xh)
   - [Action 2] (Est: Xh)

PRIORITIZED ACTION PLAN
------------------------
CRITICAL (Block Ship):
1. [Action] (Est: Xh)
2. [Action] (Est: Xh)

HIGH (Should Fix):
3. [Action] (Est: Xh)
4. [Action] (Est: Xh)

MEDIUM (Can Defer):
5. [Action] (Est: Xh)
6. [Action] (Est: Xh)

LOW (Future Enhancement):
7. [Action] (Est: Xh)

SHIP READINESS
--------------
Blocking Issues: [N]
Time to Ship-Ready: [X hours]
Recommended Ship Date: [Date]
```

## Severity Levels

**CRITICAL** (Blocks Ship):
- Core functionality missing
- Data loss risk
- Security vulnerabilities
- Legal/compliance violations

**HIGH** (Should Fix):
- Poor user experience
- Performance issues
- Missing error handling
- Incomplete documentation

**MEDIUM** (Can Defer):
- Nice-to-have features
- Minor edge cases
- Documentation polish
- Performance optimizations

**LOW** (Future Enhancement):
- Feature requests
- Code cleanup
- Additional documentation
- Further optimizations

## References

- **[CONTINUOUS_GAP_ANALYSIS.md](../../10-geist-gap-analysis-framework/CONTINUOUS_GAP_ANALYSIS.md)** - Detailed framework
- **[GEIST_DESIGN_INVESTIGATION_FRAMEWORK.md](../../10-geist-gap-analysis-framework/GEIST_DESIGN_INVESTIGATION_FRAMEWORK.md)** - Investigation techniques

## Success Metrics

**Completeness:**
- 0 critical gaps before ship
- ≥85% test coverage
- All requirements implemented
- Documentation complete

**Time Efficiency:**
- 2 hours for comprehensive analysis
- Prevents shipping incomplete features
- Reduces post-launch bug reports
