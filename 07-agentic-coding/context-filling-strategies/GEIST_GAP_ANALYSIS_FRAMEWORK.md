# Geist Gap Analysis Framework for Context Filling

**Purpose:** Use Ghost/Geyser/Gist philosophical framework to systematically identify and fill context gaps when working with AI coding assistants

**Author:** Software Development Best Practices
**Created:** 2025-10-21
**Version:** 1.0.0
**Status:** Active

---

## Overview

The Geist framework (Ghost/Geyser/Gist) provides a three-dimensional lens for identifying context gaps before they become implementation problems. Originally designed for debugging and feature completion, it's equally powerful for proactive context filling.

**Core Insight:** Context gaps exist in three dimensions:
1. **Ghost** - Unknown unknowns and hidden assumptions
2. **Geyser** - Dynamic forces and emergent pressures
3. **Gist** - Essential core vs distracting details

---

## The Three Dimensions of Context Gaps

### 1. Ghost Analysis - Parallel Reality

**Question:** What parallel reality am I not seeing?

**Context Gap Types:**

#### Hidden Assumptions
- Undocumented business rules
- Implicit dependencies between systems
- Assumed knowledge about user behavior
- Architectural decisions not captured in code

**Example - E-commerce Checkout:**
```
Ghost Gap Identified:
- Code assumes payment gateway always returns within 5 seconds
- Reality: Gateway can timeout after 30 seconds during high traffic
- Missing Context: Timeout handling requirements
- Fill Context: Provide timeout scenarios, retry policies, fallback behavior
```

#### Unknown Dependencies
- External API rate limits
- Database constraints not in schema
- Infrastructure limitations
- Third-party service SLAs

**Example - API Integration:**
```
Ghost Gap Identified:
- AI implements direct API calls without rate limiting
- Reality: API has 100 requests/minute limit
- Missing Context: Rate limit documentation
- Fill Context: Provide API docs, rate limit strategy, backoff policies
```

#### Undocumented Edge Cases
- Error states not in happy path
- Concurrent access patterns
- Data migration scenarios
- Backward compatibility requirements

**Proactive Ghost Detection:**
```
Before Implementation, Ask:
1. What assumptions am I making that might be wrong?
2. What dependencies exist that I haven't mentioned?
3. What edge cases might the AI not know about?
4. What production constraints aren't visible in code?
```

### 2. Geyser Analysis - Dynamic Forces

**Question:** What forces am I not accounting for?

**Context Gap Types:**

#### Performance Pressures
- Scale requirements (10 users vs 10,000 users)
- Latency constraints (API response time SLAs)
- Memory limitations (mobile vs server)
- Throughput expectations (requests per second)

**Example - Data Processing:**
```
Geyser Gap Identified:
- AI implements synchronous processing for file uploads
- Reality: Files can be 100MB+, blocking requests unacceptable
- Missing Context: Performance requirements
- Fill Context: Provide scale expectations, latency requirements, async patterns
```

#### Security Constraints
- Authentication requirements
- Authorization rules
- Data privacy regulations (GDPR, HIPAA)
- Input validation standards

**Example - User Data API:**
```
Geyser Gap Identified:
- AI exposes all user fields in API response
- Reality: PII must be redacted, GDPR compliance required
- Missing Context: Security and privacy requirements
- Fill Context: Provide PII field list, redaction rules, compliance docs
```

#### Technical Debt Pressures
- Legacy system constraints
- Migration requirements
- Deprecation schedules
- Backwards compatibility needs

**Proactive Geyser Detection:**
```
Before Implementation, Ask:
1. What performance requirements exist?
2. What security constraints apply?
3. What technical debt affects this feature?
4. What forces will pressure this code in production?
```

### 3. Gist Analysis - Essential Core

**Question:** Am I solving the essential problem?

**Context Gap Types:**

#### Problem Misunderstanding
- Implementing solution to wrong problem
- Over-engineering simple requirements
- Missing core business value
- Focusing on edge cases before main flow

**Example - Dashboard Feature:**
```
Gist Gap Identified:
- AI implements 20 different metric calculations
- Reality: Only 5 metrics are essential, rest are nice-to-haves
- Missing Context: Priority of requirements
- Fill Context: Provide MoSCoW prioritization (Must/Should/Could/Won't)
```

#### Scope Creep Prevention
- Core requirements vs enhancements
- MVP vs full feature set
- Critical path vs optimizations
- Must-have vs nice-to-have

**Proactive Gist Detection:**
```
Before Implementation, Ask:
1. What is the core problem we're solving?
2. What is the minimum viable solution?
3. What features are essential vs nice-to-have?
4. What can we defer to later iterations?
```

---

## Geist-Driven Context Filling Protocol

### Phase 1: Pre-Implementation Gap Analysis

**Step 1: Ghost Reconnaissance**
```
Checklist:
[ ] Document all assumptions explicitly
[ ] List known dependencies (internal and external)
[ ] Identify edge cases and error scenarios
[ ] Surface production constraints
[ ] Call out anything "everyone knows" but isn't documented
```

**Step 2: Geyser Force Mapping**
```
Checklist:
[ ] Define performance requirements (latency, throughput, scale)
[ ] Specify security constraints (auth, authz, privacy)
[ ] Document technical debt and legacy constraints
[ ] Identify compliance requirements (GDPR, HIPAA, SOC2)
[ ] List infrastructure limitations
```

**Step 3: Gist Clarification**
```
Checklist:
[ ] State the core problem in one sentence
[ ] List essential requirements (must-haves)
[ ] Separate nice-to-haves (should/could/won't)
[ ] Define success criteria
[ ] Identify critical path vs optimizations
```

### Phase 2: Context Provision to AI

**Format: Structured Context Document**

```markdown
# Feature: [Name]

## Problem Statement (Gist)
[One-sentence core problem]

**Essential Requirements:**
- [Must-have 1]
- [Must-have 2]

**Nice-to-Have (Defer if needed):**
- [Should-have 1]
- [Could-have 1]

## Constraints & Forces (Geyser)

**Performance:**
- Scale: [users, requests, data volume]
- Latency: [SLA requirements]
- Throughput: [requests per second]

**Security:**
- Authentication: [mechanism]
- Authorization: [rules]
- Privacy: [PII handling, compliance]

**Technical Debt:**
- Legacy constraints: [systems, APIs, patterns]
- Migration requirements: [compatibility needs]

## Context & Dependencies (Ghost)

**Assumptions:**
1. [Assumption 1 - call out explicitly]
2. [Assumption 2 - don't leave implicit]

**Dependencies:**
- Internal: [services, databases, APIs]
- External: [third-party APIs, rate limits, SLAs]

**Edge Cases:**
- [Error scenario 1]
- [Concurrent access pattern]
- [Data migration case]

**Production Constraints:**
- [Infrastructure limits]
- [Deployment windows]
- [Monitoring requirements]
```

### Phase 3: Gap Validation Loop

**After Initial Implementation:**
```
Geist Gap Check:
1. Ghost: Did implementation reveal hidden assumptions?
2. Geyser: Are forces accounted for (performance, security)?
3. Gist: Does solution address core problem?

If gaps detected → Fill context → Re-implement
```

---

## Real-World Examples

### Example 1: Authentication System

**Initial Request (Insufficient Context):**
> "Implement user authentication"

**Geist Gap Analysis:**

**Ghost Gaps:**
- Session management strategy (JWT vs server-side)
- Token expiration and refresh logic
- Multi-device login handling
- Password reset workflow

**Geyser Gaps:**
- Performance: Login latency SLA (<200ms)
- Security: Password hashing algorithm, rate limiting
- Scale: Concurrent sessions per user
- Compliance: Password complexity requirements

**Gist Gaps:**
- Core problem: Secure user identity verification
- Essential: Login, logout, session validation
- Nice-to-have: OAuth, 2FA, biometrics

**Geist-Informed Context Provision:**
```markdown
# Feature: User Authentication System

## Problem Statement (Gist)
Enable secure verification of user identity for protected resources.

**Essential Requirements (MVP):**
- Email/password login
- Session management (30-day expiration)
- Secure logout (token invalidation)

**Nice-to-Have (Phase 2):**
- OAuth providers (Google, GitHub)
- Two-factor authentication
- Biometric login (mobile)

## Constraints & Forces (Geyser)

**Performance:**
- Scale: 10,000 concurrent users
- Latency: Login < 200ms (p95)
- Throughput: 100 logins/second

**Security:**
- Password hashing: bcrypt (cost factor 12)
- Rate limiting: 5 failed attempts = 15-min lockout
- Session tokens: JWT with secure httpOnly cookies
- Privacy: GDPR-compliant (EU users)

**Technical Debt:**
- Must integrate with existing user database schema
- Legacy mobile app requires backwards-compatible API

## Context & Dependencies (Ghost)

**Assumptions:**
1. Email is unique identifier (no duplicate emails)
2. Email verification required before first login
3. HTTPS enforced for all auth endpoints

**Dependencies:**
- Internal: PostgreSQL user table, Redis for sessions
- External: SendGrid for password reset emails (500/day limit)

**Edge Cases:**
- Concurrent login attempts from different devices
- Password reset during active session
- Account locked, user attempts login

**Production Constraints:**
- Deploy during maintenance window (low traffic)
- Monitoring: Track failed login rates, session duration
```

### Example 2: Data Export Feature

**Initial Request (Insufficient Context):**
> "Add CSV export functionality"

**Geist Gap Analysis:**

**Ghost Gaps:**
- Data filtering requirements (export all vs filtered)
- Column selection (all fields vs user-selected)
- Large dataset handling (10 rows vs 1M rows)
- File delivery method (download vs email)

**Geyser Gaps:**
- Performance: Export time for large datasets
- Security: Authorization (who can export what data)
- Scale: Concurrent export requests
- Infrastructure: Storage for generated files

**Gist Gaps:**
- Core problem: Enable users to extract data for offline analysis
- Essential: Export filtered results, basic columns
- Nice-to-have: Scheduled exports, custom formatting

**Geist-Informed Context Provision:**
```markdown
# Feature: CSV Data Export

## Problem Statement (Gist)
Enable users to extract invoice data for offline analysis in Excel.

**Essential Requirements (MVP):**
- Export current filtered view (respects user filters)
- Standard columns: ID, Date, Amount, Status
- Download button triggers immediate CSV generation
- Max 10,000 rows per export

**Nice-to-Have (Phase 2):**
- User-selectable columns
- Scheduled exports (daily/weekly)
- Excel formatting (currency, dates)

## Constraints & Forces (Geyser)

**Performance:**
- Scale: Export up to 10,000 rows
- Latency: <5 seconds for 1,000 rows, <30 seconds for 10,000
- Throughput: Support 10 concurrent exports

**Security:**
- Authorization: Users can only export data they can view
- PII handling: Redact sensitive fields (SSN, credit card)
- Audit: Log all export actions (user, timestamp, row count)

**Technical Debt:**
- Reuse existing filter logic (don't duplicate)
- Integrate with current permissions system

## Context & Dependencies (Ghost)

**Assumptions:**
1. CSV format sufficient (no Excel .xlsx requirement)
2. UTF-8 encoding (international characters)
3. Filename format: invoices_YYYY-MM-DD_HH-MM-SS.csv

**Dependencies:**
- Internal: Invoice API (respects filters), S3 for temp storage
- External: None

**Edge Cases:**
- Export during filter with zero results (empty CSV)
- User cancels export mid-generation
- Export exceeds 10,000 row limit (error message)

**Production Constraints:**
- Export files auto-delete after 24 hours
- Monitor: Track export sizes, generation times
- Rate limiting: 5 exports per user per hour
```

---

## Integration with LLM Workflow

### Before Asking AI to Implement

**Geist Context Checklist:**
```
Ghost - Unknown Unknowns:
[ ] All assumptions documented
[ ] Dependencies listed
[ ] Edge cases identified
[ ] Production constraints shared

Geyser - Dynamic Forces:
[ ] Performance requirements defined
[ ] Security constraints specified
[ ] Technical debt acknowledged
[ ] Compliance needs stated

Gist - Essential Core:
[ ] Core problem stated clearly
[ ] Essential requirements prioritized
[ ] Nice-to-haves separated
[ ] Success criteria defined
```

**If any checkbox unchecked → Fill that context before proceeding**

### During Implementation

**Geist Gap Detection Questions:**

AI should ask these when context is insufficient:
```
Ghost Questions:
- "What should happen when [edge case]?"
- "Are there any constraints I should know about?"
- "What dependencies does this have?"

Geyser Questions:
- "What are the performance requirements?"
- "What security constraints apply?"
- "What scale should this handle?"

Gist Questions:
- "What is the core problem we're solving?"
- "Which features are essential vs nice-to-have?"
- "What does success look like?"
```

**Human Response Strategy:**
- Answer all Ghost questions (prevent bugs)
- Prioritize Geyser questions (prevent production issues)
- Clarify Gist questions (prevent scope creep)

---

## Measuring Gap Analysis Effectiveness

### Metrics

**Pre-Implementation:**
- **Ghost gaps found:** Assumptions, dependencies, edge cases identified before coding
- **Geyser gaps found:** Performance, security, technical debt constraints surfaced
- **Gist gaps found:** Problem clarifications, priority adjustments made

**Post-Implementation:**
- **Ghost bugs:** Issues from unknown unknowns (lower = better gap analysis)
- **Geyser failures:** Production issues from unaccounted forces (lower = better)
- **Gist rework:** Scope changes due to misunderstood core problem (lower = better)

**Success Indicators:**
- High pre-implementation gaps found (good - caught early)
- Low post-implementation bugs/failures/rework (good - nothing missed)
- Decreasing AI clarifying questions (good - better context provision)

---

## Anti-Patterns

### ❌ Don't: Assume AI Will Ask for Missing Context

**Problem:**
- AI may make reasonable-looking but incorrect assumptions
- Not all gaps trigger AI questions
- Some gaps only discovered during implementation

**Fix:**
- Proactively run Geist gap analysis before asking AI to implement
- Provide comprehensive context upfront
- Expect fewer questions = better context provision

### ❌ Don't: Provide Only Technical Context

**Problem:**
- Technical specs without business context (Gist missing)
- Performance numbers without scale reasoning (Geyser incomplete)
- Code patterns without production constraints (Ghost blind spots)

**Fix:**
- Include WHY (business context)
- Include FORCES (performance, security, scale)
- Include CONSTRAINTS (assumptions, dependencies, edge cases)

### ❌ Don't: Bury Essential Requirements in Details

**Problem:**
- Long requirements doc with no prioritization
- AI can't distinguish must-haves from nice-to-haves
- Scope creep or under-delivery

**Fix:**
- Lead with Gist (core problem, essential requirements)
- Clearly mark nice-to-haves
- State what can be deferred

---

## Templates

### Quick Geist Context Template

```markdown
# [Feature Name]

## Gist (Core Problem)
[One sentence: What problem are we solving?]

**Must Have:**
- [Essential requirement 1]
- [Essential requirement 2]

**Nice to Have (Defer if needed):**
- [Enhancement 1]

## Geyser (Forces)
- **Performance:** [scale, latency, throughput]
- **Security:** [auth, privacy, compliance]
- **Technical Debt:** [legacy constraints]

## Ghost (Hidden Context)
- **Assumptions:** [List explicitly]
- **Dependencies:** [Internal, external]
- **Edge Cases:** [Error scenarios]
- **Production:** [Infrastructure, monitoring]
```

### Comprehensive Geist Gap Analysis Template

See detailed examples above for complete format.

---

## References

- **Geist Framework Origins:** `../02-architecture-design/GEIST_DRIVEN_DEVELOPMENT.md`
- **Feature Gap Resolution:** `CLAUDE.md` - Feature Gap Resolution Workflow
- **Problem Identification:** `PROBLEM_IDENTIFICATION_FIRST.md`

---

**Next Steps:**
1. Practice Geist gap analysis on next feature request
2. Measure pre/post-implementation gap discovery rates
3. Refine templates based on real-world usage
4. Share findings with team for continuous improvement

---

**Version:** 1.0.0
**Last Updated:** 2025-10-21
**Status:** Active
