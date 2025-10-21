# Problem Identification First: Understanding Before Implementing

**Status**: Active
**Last Updated**: 2025-10-21
**Applies To**: All development workflows, especially agentic AI coding
**Prerequisites**: [WHY_CONTEXT_MATTERS.md](./WHY_CONTEXT_MATTERS.md)

## Table of Contents

1. [The Problem Identification Principle](#the-problem-identification-principle)
2. [Problem Framing Techniques](#problem-framing-techniques)
3. [Avoiding the XY Problem](#avoiding-the-xy-problem)
4. [Requirements Gathering Process](#requirements-gathering-process)
5. [Efficient Problem Understanding](#efficient-problem-understanding)
6. [Providing Problem Context to AI](#providing-problem-context-to-ai)
7. [Practical Templates and Checklists](#practical-templates-and-checklists)

## The Problem Identification Principle

### Know the Problem Before Solving It

The most common failure mode in software development is not poor implementation—it's solving the wrong problem. This principle is especially critical when working with AI agents, where incomplete problem understanding leads to:

- **Context Waste**: AI generates solutions to the wrong problem, consuming tokens inefficiently
- **Implementation Churn**: Multiple refactoring cycles as the real problem emerges
- **Technical Debt**: Premature solutions that don't address root causes
- **Scope Creep**: Unclear problem boundaries lead to over-engineering

**The Core Principle**: Spend 70% of your time understanding the problem, 30% implementing the solution. Most developers invert this ratio, leading to costly rework.

### Most Time Should Be Spent Understanding, Not Coding

Consider two approaches to adding user notification preferences:

**Approach A: Jump to Implementation (Anti-Pattern)**
```
Developer: "I need to add a notifications table to the database."
↓
AI: Creates table schema
↓
Developer: "Actually, we need notification channels too."
↓
AI: Adds channels table
↓
Developer: "Wait, users want per-channel frequency settings."
↓
AI: Refactors entire schema (3rd iteration)
↓
Total Time: 4 hours of implementation churn
```

**Approach B: Problem-First (Best Practice)**
```
Developer Thinks:
• What problem am I solving? (Users complain about too many emails)
• What do users actually need? (Control frequency and channels)
• What constraints exist? (Must support email, SMS, push, Slack)
• What does success look like? (90% reduction in support tickets)

Developer → AI: "Users need granular control over notification frequency
across multiple channels (email, SMS, push, Slack). Problem: 80% of support
tickets complain about notification overload. Success: Users can set daily
digest vs real-time per channel. Constraint: Must migrate 100K existing users."
↓
AI: Generates comprehensive schema with migration plan (1st iteration)
↓
Total Time: 1 hour understanding + 30 minutes implementation = 1.5 hours
```

**Time Savings**: 2.5 hours (63% reduction) + better solution quality

### Correct Problem → Efficient Context Filling → Right Solution

The problem identification → context filling → solution pipeline works like this:

```
1. PROBLEM IDENTIFICATION (Know what you're solving)
   ↓
2. CONTEXT FILLING (Provide relevant information)
   ↓
3. SOLUTION GENERATION (AI implements correctly first time)
```

**Each stage multiplies efficiency:**
- Correct problem identification: 3x better context filling
- Efficient context filling: 5x better solution quality
- Right solution first time: 10x reduction in rework

**Combined Effect**: 150x improvement in development velocity for complex features

## Problem Framing Techniques

### Five Whys: Dig to Root Cause

The Five Whys technique reveals root causes by repeatedly asking "Why?" until you uncover the fundamental problem.

**Example: Slow API Response Times**

```
Problem Surface: "API is slow"

Why #1: Why is the API slow?
→ Database queries are taking 5+ seconds

Why #2: Why are database queries slow?
→ Missing indexes on frequently queried columns

Why #3: Why are indexes missing?
→ Database schema was designed before we knew query patterns

Why #4: Why didn't we know query patterns?
→ We never analyzed actual user behavior in production

Why #5: Why didn't we analyze user behavior?
→ We don't have observability tooling in place

ROOT CAUSE: Lack of observability prevents data-driven schema optimization
```

**Now the Real Problem**: Not "add indexes" (symptom) but "implement observability to identify performance bottlenecks systematically" (root cause).

**Implementation Difference**:
- **Symptom Solution**: Add 3 indexes (fixes this case, repeats for next slow query)
- **Root Cause Solution**: Add query performance monitoring + automated index recommendations (prevents future occurrences)

### Problem Statement: One Clear Sentence

A well-crafted problem statement contains:
1. **Who** is affected
2. **What** is the problem
3. **Why** it matters
4. **Context** for scope

**Template**: "[Who] cannot [what] because [why], resulting in [impact]."

**Examples**:

**Bad (Vague)**:
- "The dashboard is slow"
- "Users want better notifications"
- "We need to improve the API"

**Good (Specific)**:
```
"Account managers cannot load customer dashboards in under 10 seconds
because we're loading all historical transactions synchronously,
resulting in $50K/month lost deals from poor demo experiences."
```

```
"Mobile users cannot receive real-time order updates because our
notification system batches messages every 15 minutes, resulting in
30% negative reviews citing poor delivery tracking."
```

```
"External API consumers cannot integrate with our system because we
lack versioned API documentation, resulting in zero third-party
integrations after 6 months of public availability."
```

### Success Criteria: What Does "Done" Look Like?

Define measurable outcomes before implementation:

**SMART Success Criteria Template**:
- **Specific**: Exactly what will change
- **Measurable**: Quantifiable metrics
- **Achievable**: Technically feasible
- **Relevant**: Solves the actual problem
- **Time-bound**: When success is measured

**Example: Dashboard Performance Problem**

**Bad Success Criteria**:
- "Dashboard is faster"
- "Users are happy with performance"
- "Load times improved"

**Good Success Criteria**:
```
1. PERFORMANCE: Dashboard loads in <3 seconds for 95th percentile users
2. BUSINESS IMPACT: Demo-to-close rate increases from 15% to 25%
3. USER SATISFACTION: Performance-related support tickets drop by 80%
4. TECHNICAL VALIDATION: All Core Web Vitals in "Good" range
5. MEASUREMENT WINDOW: Validated over 30 days post-deployment
```

### Constraints: What Can't We Change?

Identifying constraints early prevents wasted effort on infeasible solutions.

**Constraint Categories**:

1. **Technical Constraints**
   - Legacy system integrations (must support SOAP API)
   - Technology stack limitations (must use Python 3.9, can't upgrade)
   - Performance requirements (must handle 10K req/sec)
   - Security requirements (HIPAA compliance, PCI-DSS)

2. **Business Constraints**
   - Budget ($10K maximum for implementation)
   - Timeline (must ship before Q4 board meeting)
   - Backward compatibility (100K active users can't break)
   - Regulatory (must maintain audit logs for 7 years)

3. **Team Constraints**
   - Skillset (team doesn't know Rust, can't introduce it)
   - Availability (only 2 weeks of developer time)
   - Support burden (must be maintainable by 1 person)

4. **Operational Constraints**
   - Zero downtime deployments required
   - Must run on existing infrastructure
   - Can't introduce new third-party dependencies
   - Must support offline mode

**Constraint Documentation Example**:
```markdown
## Constraints for User Authentication Redesign

### Technical
- MUST: Support existing LDAP integration (5,000 enterprise users)
- MUST: Maintain <200ms authentication latency
- CANNOT: Break mobile app API (no forced upgrade path)

### Business
- BUDGET: $15K maximum (includes testing and deployment)
- TIMELINE: 6 weeks (hard deadline for SOC 2 audit)
- COMPATIBILITY: Zero breaking changes for current users

### Team
- SKILLSET: Team familiar with Node.js, not Go
- AVAILABILITY: 1.5 developers for 6 weeks
- ON-CALL: Must be debuggable by ops team (no black boxes)

### Operational
- DEPLOYMENT: Must support blue-green deployment
- MONITORING: Must integrate with existing DataDog setup
- COMPLIANCE: Must log all authentication attempts for audit
```

## Avoiding the XY Problem

### X: Actual Problem, Y: Attempted Solution

**The XY Problem** occurs when you ask about your attempted solution (Y) instead of describing your actual problem (X). This causes helpers (including AI) to waste time on the wrong question.

**Structure**:
1. User has problem X
2. User thinks solution Y will work
3. User asks about how to implement Y
4. Helper provides guidance on Y
5. Y doesn't solve X (or solves it poorly)
6. User frustrated, helper confused

### Anti-Pattern: Asking About Y Instead of Stating X

**Example 1: Log Parsing**

**XY Problem (Asking About Y)**:
```
User: "How do I parse this log file format? I need to extract timestamps
using regex."

AI: "Here's a regex pattern for ISO timestamps: \d{4}-\d{2}-\d{2}T\d{2}..."

User: "That doesn't work, my timestamps are in a different format."

AI: "Try this pattern instead: \d{2}/\d{2}/\d{4}..."

User: "Still not working, the logs have multiple timestamp formats..."
```

**Direct Problem Statement (Stating X)**:
```
User: "I need to identify database queries that take longer than 5 seconds.
Our application logs queries with timestamps and execution times, but the
format varies across different services. What's the best approach?"

AI: "Instead of parsing logs manually, I recommend:
1. Use structured logging (JSON) for consistent parsing
2. Use a log aggregation tool (ELK, Splunk) with built-in query analysis
3. Or, instrument your database with query performance monitoring

For immediate needs without changing infrastructure, here's a Python script
using the 'loguru' library that handles multiple timestamp formats..."
```

**Result**: User gets a better solution (structured logging + monitoring) instead of a fragile regex.

**Example 2: Database Performance**

**XY Problem**:
```
User: "How do I increase the PostgreSQL connection pool size to 500?"

AI: "Add max_connections=500 to postgresql.conf, but be aware this
increases memory usage significantly."

User implements, application still slow and now database crashes under load.

ACTUAL PROBLEM (X): Application making too many sequential queries (N+1 problem)
ATTEMPTED SOLUTION (Y): More connections
REAL SOLUTION: Fix N+1 queries with eager loading
```

**Direct Problem Statement**:
```
User: "Our application becomes unresponsive when 100+ users are active.
Database CPU spikes to 100%, and we see 'connection pool exhausted' errors.
Currently using default PostgreSQL settings with 20 connections. What's
causing the bottleneck?"

AI: "This sounds like an N+1 query problem rather than connection limits.
Before increasing connections:
1. Enable query logging and analyze query patterns
2. Check for N+1 queries using an ORM query counter
3. Review your application's connection pooling settings

Increasing max_connections to 500 will likely make the problem worse by
overwhelming the database. Let's identify the root cause first..."
```

### How to Recognize the XY Problem

**Warning Signs You're Asking About Y**:
- Your question is about a very specific technical detail
- You can't explain WHY you need this specific thing
- You're stuck on one particular approach
- The helper's answer doesn't solve your real problem
- You find yourself saying "but I specifically need to do X" without explaining why

**Self-Check Questions**:
1. Am I asking about a solution or describing a problem?
2. Can I explain the business/user need behind this request?
3. Am I open to alternative approaches?
4. Have I explained the constraints that led me to this approach?

**How to Avoid the XY Problem**:

**Template for Problem-First Communication**:
```markdown
## The Actual Problem (X)
[What are you trying to achieve from a user/business perspective?]

## What I've Tried (Y)
[Your attempted solution and why it seemed like a good approach]

## Why I'm Stuck
[What's not working or what's unclear about implementing Y]

## Constraints
[Technical, business, or timeline constraints that limit solutions]

## Question
[Specific question about Y, BUT you're open to alternatives]
```

**Example**:
```markdown
## The Actual Problem (X)
Users complain that email notifications arrive 15-30 minutes after events
occur, but they need real-time updates for critical alerts (payment failures,
security events).

## What I've Tried (Y)
I'm trying to set up a cron job that runs every minute to check for new
events and send emails. I'm struggling with how to prevent duplicate sends
if the cron job takes longer than 60 seconds.

## Why I'm Stuck
I can't figure out how to implement distributed locking in our current stack,
and I'm worried about race conditions between cron instances.

## Constraints
- Can't add new infrastructure (no message queues, no Redis)
- Must use existing PostgreSQL database
- Must work with our current Python Flask application
- Timeline: Need solution in 2 weeks

## Question
How do I implement distributed locking for a cron job using PostgreSQL?
BUT I'm open to alternative approaches if there's a better way to achieve
real-time notifications within our constraints.
```

**AI Response**: Will likely suggest database-level advisory locks, PostgreSQL NOTIFY/LISTEN, or challenge the "no new infrastructure" constraint with lightweight alternatives like SQLite-based queues.

## Requirements Gathering Process

### Stakeholder Interviews: What Do Users Need?

Effective stakeholder interviews uncover the real problem, not just stated wants.

**Interview Structure**:

1. **Current State Analysis** (20% of time)
   - How do you currently accomplish [task]?
   - What tools/processes do you use?
   - How long does it take?
   - Walk me through a typical scenario

2. **Pain Point Identification** (40% of time)
   - What's frustrating about the current process?
   - Where do you get stuck?
   - What workarounds have you created?
   - What would you change if you could wave a magic wand?

3. **Success Definition** (20% of time)
   - How would you know this problem is solved?
   - What would "10x better" look like?
   - What metrics matter to you?

4. **Constraint Discovery** (20% of time)
   - What can't change?
   - What integrations must continue working?
   - What compliance requirements apply?
   - What's your budget/timeline?

**Example Interview: Sales Dashboard Redesign**

**Bad Questions**:
- "Do you want real-time data?"
- "Should we add more charts?"
- "What color scheme do you prefer?"

**Good Questions**:
```
1. "Walk me through how you prepare for a customer meeting using the
   current dashboard."

2. "When was the last time the dashboard didn't have the information you
   needed? What was missing?"

3. "If you could only see 3 metrics before a customer call, what would
   they be and why?"

4. "What decisions are you trying to make with this data?"

5. "How do you currently work around dashboard limitations?"
```

**What You'll Discover**:
- They don't need real-time data (update once per day is fine)
- They need comparisons to last month (not available now)
- They waste 15 minutes per meeting manually calculating close probability
- They use a spreadsheet alongside the dashboard (workaround)

**Requirements That Emerge**:
```markdown
## Discovered Requirements

### Critical (Must Have)
- Month-over-month comparison metrics
- Automated close probability calculation
- Export to spreadsheet (support existing workflow)

### Important (Should Have)
- Daily data refresh (not real-time)
- Historical trend visualization

### Nice to Have (Could Have)
- Real-time updates
- Customizable color schemes
```

### Existing System Analysis: What's Already There?

Before designing new solutions, understand the existing system to avoid:
- Reinventing existing functionality
- Breaking undocumented dependencies
- Ignoring successful patterns
- Disrupting working processes

**Existing System Analysis Checklist**:

1. **Architecture Review**
   - [ ] Read architecture documentation (if it exists)
   - [ ] Map data flow through the system
   - [ ] Identify integration points
   - [ ] Document technology stack

2. **Code Archaeology**
   - [ ] Search for similar existing features
   - [ ] Review recent changes in related areas
   - [ ] Identify patterns and conventions
   - [ ] Check for deprecated approaches

3. **Dependency Mapping**
   - [ ] What other systems depend on this component?
   - [ ] What external services does this component use?
   - [ ] What database tables/schemas are involved?
   - [ ] What APIs are exposed?

4. **Performance Baseline**
   - [ ] Current response times
   - [ ] Current resource usage
   - [ ] Current error rates
   - [ ] Current scalability limits

**Tools for System Analysis**:
```bash
# Find similar functionality
grep -r "notification" src/ --include="*.py"
rg "email.*send" -t python

# Analyze database usage
grep -r "User.notifications" src/

# Check API dependencies
grep -r "requests.post" src/ | grep "api"

# Review recent changes
git log --since="6 months ago" --grep="notification" --oneline
```

### Edge Case Identification: What Can Go Wrong?

Edge cases are where bugs hide. Identify them during problem definition, not during bug fixing.

**Edge Case Discovery Framework**:

1. **Boundary Conditions**
   - What happens at zero? (empty lists, no data, zero quantity)
   - What happens at maximum? (rate limits, storage limits, integer overflow)
   - What happens at minimum? (negative numbers, underflow)

2. **Invalid Input**
   - Malformed data (wrong type, wrong format)
   - Missing required data
   - Contradictory data
   - Malicious input (injection attacks)

3. **Timing Issues**
   - Race conditions (concurrent access)
   - Timeout scenarios (slow networks, unresponsive services)
   - Retry logic (idempotency, duplicate processing)

4. **State Transitions**
   - What happens when state changes mid-operation?
   - What if external dependency fails partway through?
   - How do you handle partial success?

5. **Scale Edge Cases**
   - One user vs 1,000,000 users
   - One record vs 1,000,000 records
   - One request/second vs 10,000 requests/second

**Example: User Notification Preferences**

**Basic Happy Path**:
```
User clicks "Enable email notifications" → Preference saved → Emails sent
```

**Edge Cases to Consider**:
```markdown
## Boundary Conditions
- User has zero notification preferences set (first-time user)
- User enables all notification types (maximum)
- User has notification preferences but email is unverified

## Invalid Input
- User provides malformed email address
- User submits preference for non-existent notification type
- User tries to set negative notification frequency

## Timing Issues
- User changes preferences while notification is being sent
- User unsubscribes during bulk email send
- User deletes account while preference update is processing

## State Transitions
- User's email becomes invalid after setting preferences
- User's account is suspended mid-notification
- Email service is down when notification fires

## Scale Edge Cases
- What if 100K users all change preferences simultaneously?
- What if user has 10,000 queued notifications?
- What if bulk preference update affects 1M users?
```

### Constraint Discovery: Performance, Security, Technical Debt

Uncover hidden constraints that will impact your solution.

**Constraint Discovery Questions**:

**Performance Constraints**:
- What are the current response time requirements?
- What are the throughput requirements (requests/sec)?
- What are the resource limits (CPU, memory, storage)?
- What are the latency requirements (p50, p95, p99)?
- What are the scalability requirements (current vs 5 years)?

**Security Constraints**:
- What compliance standards apply (GDPR, HIPAA, SOC 2, PCI-DSS)?
- What data classification levels exist (public, internal, confidential)?
- What authentication/authorization is required?
- What audit logging is required?
- What encryption is required (at rest, in transit)?

**Technical Debt Constraints**:
- What legacy systems must we integrate with?
- What deprecated technologies are still in use?
- What known technical debt affects this area?
- What refactoring has been deferred?
- What workarounds are currently in place?

**Example: Payment Processing Feature**

```markdown
## Performance Constraints
- Must process payment in <500ms (user expectation)
- Must handle 1,000 concurrent checkouts (Black Friday peak)
- Must queue retries without blocking user flow

## Security Constraints
- PCI-DSS Level 1 compliance required
- Cannot store credit card numbers (tokenization required)
- Must log all payment attempts for fraud analysis
- Must support 3D Secure authentication
- Must encrypt all PII at rest and in transit

## Technical Debt Constraints
- Legacy checkout flow uses SOAP API (can't change immediately)
- Current payment gateway has 99.5% SLA (must handle downtime)
- Existing database schema doesn't support multi-currency (known issue)
- No feature flagging system (can't do gradual rollout)
- Deployment requires 2-hour maintenance window (limitation)
```

## Efficient Problem Understanding

### Research Existing Solutions

Before implementing, research what already exists:

**Internal Research**:
1. **Codebase Search**: Does similar functionality exist?
   ```bash
   # Search for similar features
   rg "payment.*process" -t python
   rg "notification.*send" -t js

   # Find related utilities
   find src/ -name "*payment*" -o -name "*checkout*"
   ```

2. **Documentation Review**: What's already documented?
   - API documentation
   - Architecture decision records (ADRs)
   - Design documents
   - Past implementation plans

3. **Git History**: What attempts have been made?
   ```bash
   git log --all --grep="payment processing"
   git log --all -- src/payments/
   ```

**External Research**:
1. **Industry Standards**: How do others solve this?
   - Check competitor implementations
   - Review industry best practices
   - Read relevant RFCs/specifications

2. **Open Source**: What libraries/frameworks exist?
   - Search GitHub for similar solutions
   - Review popular libraries in your language
   - Check package managers (npm, PyPI, etc.)

3. **Community Knowledge**: What do experts recommend?
   - StackOverflow for common patterns
   - Framework documentation
   - Blog posts from experienced developers

**Time-Boxing Research**:
- Spend 2 hours on research before implementation
- Document findings for future reference
- Don't over-research: 80% understanding is sufficient

### Read Relevant Docs and Code

Systematic documentation and code review prevents duplicate work.

**Documentation Reading Priority**:

1. **README files** (10 minutes)
   - Project overview
   - Setup instructions
   - Architecture summary

2. **API documentation** (30 minutes)
   - Existing endpoints
   - Data models
   - Authentication patterns

3. **Architecture Decision Records** (30 minutes)
   - Past decisions affecting this area
   - Rationale for current approaches
   - Deprecated patterns to avoid

4. **Related implementation plans** (30 minutes)
   - Similar features implemented recently
   - Patterns to follow
   - Pitfalls to avoid

**Code Reading Strategy**:

```python
# Step 1: Find entry points
# Search for similar feature endpoints or commands
rg "def process_payment" -A 5

# Step 2: Trace data flow
# Follow the data from input to storage
# Note: Read files identified in Step 1

# Step 3: Identify patterns
# Look for consistent approaches
# - Error handling patterns
# - Validation patterns
# - Testing patterns
# - Logging patterns

# Step 4: Check for utilities
# Don't reinvent existing helpers
rg "class PaymentValidator"
rg "def format_currency"
```

**Code Reading Checklist**:
- [ ] How is similar functionality currently implemented?
- [ ] What validation is performed?
- [ ] What error handling exists?
- [ ] What testing patterns are used?
- [ ] What logging is implemented?
- [ ] What configuration is required?

### Ask Clarifying Questions Early

Don't make assumptions. Ask questions during problem identification, not during implementation.

**When to Ask Questions**:
- **Immediately**: When requirements are unclear
- **During research**: When documentation contradicts code
- **Before implementation**: When multiple approaches are possible
- **Never**: After you've already implemented the wrong solution

**Question Categories**:

**Scope Questions**:
- What's in scope for this iteration?
- What's explicitly out of scope?
- What's the minimum viable solution?
- What can be deferred to future iterations?

**Requirement Questions**:
- What does "fast enough" mean in milliseconds?
- What does "highly available" mean in uptime percentage?
- What does "secure" mean in specific controls?
- What does "scalable" mean in user count?

**Technical Questions**:
- What's the preferred approach (library X vs library Y)?
- What's the existing pattern for similar features?
- What are the performance requirements?
- What are the testing requirements?

**Process Questions**:
- Who needs to review this?
- What's the deployment process?
- What's the rollback plan?
- What's the monitoring strategy?

**Example: Clarifying Questions for "Add Real-Time Notifications"**

**Vague Request**: "Add real-time notifications"

**Clarifying Questions**:
```markdown
## Scope Questions
Q: What types of notifications need to be real-time?
A: Payment confirmations and security alerts only (not marketing)

Q: What delivery channels? (Email, SMS, push, in-app)
A: In-app only for v1, email/SMS for v2

Q: What does "real-time" mean? (<1 second, <5 seconds, <1 minute?)
A: User should see notification within 5 seconds of event

## Requirement Questions
Q: What happens if user is offline when notification is sent?
A: Queue notification, deliver when they come online

Q: How long should notifications persist?
A: 30 days, then archive

Q: Do we need notification read/unread tracking?
A: Yes, critical for user experience

## Technical Questions
Q: Do we have existing WebSocket infrastructure?
A: No, need to implement

Q: Can we use a third-party service (Pusher, Ably)?
A: Budget exists, but prefer self-hosted for data privacy

Q: What's the expected concurrency (simultaneous connected users)?
A: 10K during peak hours

## Process Questions
Q: Can we do a gradual rollout (feature flag)?
A: Yes, release to 10% of users first

Q: What monitoring is needed?
A: Delivery rate, latency, connection count

Q: What's the rollback plan if WebSockets cause issues?
A: Must be able to disable and fall back to polling
```

**Result**: Clear requirements that prevent building the wrong solution.

### Document Understanding Before Coding

Capture your problem understanding in a structured format before writing code.

**Problem Understanding Document Template**:

```markdown
# Problem Understanding: [Feature Name]

**Date**: YYYY-MM-DD
**Author**: [Your Name]
**Status**: Draft | Under Review | Approved

## 1. Problem Statement
[One clear sentence describing the problem]

**Who**: [Users/stakeholders affected]
**What**: [The problem they're experiencing]
**Why**: [Business/user impact]

## 2. Root Cause Analysis
[Five Whys or other analysis showing you understand the real problem]

## 3. Success Criteria
[Measurable outcomes that define "done"]

- [ ] [Specific measurable criterion 1]
- [ ] [Specific measurable criterion 2]
- [ ] [Specific measurable criterion 3]

## 4. Constraints
### Technical
- [List technical constraints]

### Business
- [List business constraints]

### Timeline
- [List timeline constraints]

## 5. Existing System Analysis
**Current Implementation**: [Description]
**Related Components**: [List]
**Dependencies**: [List]

## 6. Edge Cases
- [Edge case 1]
- [Edge case 2]
- [Edge case 3]

## 7. Open Questions
- [ ] [Question 1]
- [ ] [Question 2]
- [ ] [Question 3]

## 8. Alternatives Considered
1. **Approach A**: [Description] - Rejected because [reason]
2. **Approach B**: [Description] - Rejected because [reason]
3. **Approach C**: [Description] - **Selected** because [reason]

## 9. Validation
**Stakeholder**: [Name] - Approved on [date]
**Tech Lead**: [Name] - Approved on [date]
```

**Benefits of Documentation**:
- **Shared Understanding**: Team alignment on the problem
- **Future Reference**: Why decisions were made
- **Scope Prevention**: Clear boundaries prevent feature creep
- **Onboarding**: New team members understand context
- **AI Context**: Perfect input for AI implementation agents

## Providing Problem Context to AI

### State the Problem, Not Just the Solution

When working with AI agents, problem context enables better solutions than solution requests.

**Anti-Pattern (Solution Request)**:
```
"Add a Redis cache to the user profile endpoint."
```

**Best Practice (Problem Statement)**:
```
"The user profile endpoint returns in 2.5 seconds on average, but our
requirement is <500ms. Profiling shows 90% of time is spent in database
queries fetching user metadata that changes infrequently. We have 100K
active users and expect 10x growth this year. What's the best approach
to meet our performance requirements while supporting this growth?"
```

**What AI Can Do With Problem Context**:
- Suggest alternatives (maybe database indexes solve it without cache)
- Identify trade-offs (cache invalidation complexity)
- Propose right-sized solutions (maybe local memory cache is sufficient)
- Ask clarifying questions (what's the read/write ratio?)

### Include WHY (Business Context)

Business context helps AI prioritize features and make trade-off decisions.

**Without Business Context**:
```
"Implement a notification system with email and SMS support."
```

**AI Response**: Generic notification system with all features, over-engineered

**With Business Context**:
```
"We're losing 40% of users in the onboarding flow because they forget to
verify their email addresses. We need a notification system to send
verification reminders. Email is critical (100% of users), SMS is nice-to-have
(only 30% of users provide phone numbers). This is a P0 issue blocking our
Q4 growth goals. We have 2 weeks to implement before investor demo."
```

**AI Response**: Focuses on email reliability, suggests simple SMTP for v1, defers SMS to v2, proposes 1-week implementation plan

**Business Context Elements**:
1. **User Impact**: How many users affected? What's the user experience impact?
2. **Business Impact**: Revenue, growth, compliance, competitive advantage
3. **Priority**: P0 (critical), P1 (high), P2 (medium), P3 (low)
4. **Timeline**: Why does this need to be done now? What's the deadline?
5. **Success Metrics**: How will we measure if this solves the problem?

### Provide Constraints and Requirements

Constraints guide AI toward feasible solutions.

**Complete Context Example**:
```markdown
## Problem
Users abandon checkout because payment processing takes 15+ seconds,
resulting in 25% cart abandonment rate and $500K/month lost revenue.

## Business Context
- Payment confirmation is #1 UX complaint (400 support tickets/month)
- Competitors process payments in <3 seconds
- Must ship before Black Friday (8 weeks away)
- Each 1-second improvement = estimated $50K/month revenue increase

## Current State
- Using legacy payment gateway with SOAP API
- Synchronous processing blocks UI thread
- No retry logic (users hit submit multiple times, causing duplicates)
- Current average: 15 seconds (p50), 30 seconds (p95)

## Requirements
- MUST: Payment confirmation in <3 seconds (p95)
- MUST: PCI-DSS compliant
- MUST: Support existing payment gateway (can't switch)
- SHOULD: Handle duplicate submissions gracefully
- SHOULD: Provide progress feedback during processing

## Constraints
- TECHNICAL: Must use Python/Flask (existing stack)
- TECHNICAL: Cannot store credit card data (tokenization required)
- BUSINESS: $20K budget maximum
- TIMELINE: 8 weeks to production
- TEAM: 1.5 developers available
- OPERATIONAL: Must support rollback without data loss

## Success Criteria
- [ ] p95 payment processing time <3 seconds
- [ ] Zero duplicate charges from double-submission
- [ ] Cart abandonment rate drops below 15%
- [ ] Support tickets drop by 50%
- [ ] 99.9% payment success rate maintained
```

**AI Can Now**:
- Suggest asynchronous processing with webhooks
- Recommend idempotency tokens for duplicate prevention
- Propose progress indicators for UX during processing
- Calculate if timeline is feasible
- Flag risks (PCI-DSS compliance review time)

### Share Edge Cases and Concerns

Edge cases and concerns help AI generate robust solutions.

**Example: User Role Management**

**Without Edge Cases**:
```
"Implement user role management with admin, manager, and user roles."
```

**AI Response**: Basic RBAC implementation

**With Edge Cases**:
```markdown
## Problem
We need role-based access control to prevent users from accessing
admin-only features. Currently, everyone has full access.

## Edge Cases I'm Concerned About

### User State Transitions
- What happens if admin demotes themselves to user?
- What if a user's role changes while they're logged in?
- What if we delete a role that users currently have?

### Permission Edge Cases
- Can a manager promote another user to admin?
- What if a user has multiple roles (manager + admin)?
- What happens to resources created by a user who's demoted?

### Data Consistency
- What if role change fails partway through (user updated, not cache)?
- What if user has open sessions on multiple devices?
- What if role permissions change while user is mid-operation?

### Security Concerns
- How do we prevent privilege escalation attacks?
- How do we audit role changes?
- How do we handle API authentication vs UI authentication?

### Migration Edge Cases
- How do we assign roles to 10,000 existing users?
- What's the default role for legacy users?
- How do we test without affecting production users?

## Constraints
- Must not break existing authentication (OAuth2)
- Must support fine-grained permissions in future
- Must be performant (<50ms authorization check)
```

**AI Can Now**:
- Design role transition logic
- Implement session invalidation on role change
- Suggest role hierarchy to prevent self-demotion
- Propose migration strategy with default roles
- Add comprehensive audit logging
- Include test cases for all edge cases

## Practical Templates and Checklists

### Problem Framing Template

```markdown
# Problem Framing: [Feature/Issue Name]

## One-Sentence Problem Statement
[Who] cannot [what] because [why], resulting in [impact].

## Five Whys Analysis
**Surface Problem**: [Initial symptom]

**Why #1**: [First-level cause]
**Why #2**: [Second-level cause]
**Why #3**: [Third-level cause]
**Why #4**: [Fourth-level cause]
**Why #5**: [Root cause]

**Root Cause**: [Final answer]

## Success Criteria (SMART)
- [ ] **Specific**: [Exactly what will change]
- [ ] **Measurable**: [Quantifiable metric with target]
- [ ] **Achievable**: [Why this is technically feasible]
- [ ] **Relevant**: [How this solves the problem]
- [ ] **Time-bound**: [When success will be measured]

## Constraints
### Technical
- [Constraint 1]
- [Constraint 2]

### Business
- [Constraint 1]
- [Constraint 2]

### Timeline
- [Constraint 1]
- [Constraint 2]

## Validation
- [ ] Stakeholder agreement on problem statement
- [ ] Success criteria approved
- [ ] Constraints documented and accepted
- [ ] Edge cases identified
```

### Requirements Gathering Checklist

```markdown
# Requirements Gathering Checklist

## Stakeholder Interviews
- [ ] Identified all stakeholders (users, business, technical)
- [ ] Conducted interviews with each stakeholder group
- [ ] Documented current state and pain points
- [ ] Defined success criteria from each perspective
- [ ] Validated understanding with stakeholders

## Existing System Analysis
- [ ] Reviewed architecture documentation
- [ ] Analyzed relevant code sections
- [ ] Mapped dependencies and integrations
- [ ] Documented current performance baselines
- [ ] Identified technical debt affecting this feature

## Edge Case Identification
- [ ] Documented boundary conditions (zero, max, min)
- [ ] Identified invalid input scenarios
- [ ] Listed timing and concurrency issues
- [ ] Defined state transition edge cases
- [ ] Considered scale edge cases (1x to 1000x)

## Constraint Discovery
- [ ] Performance requirements documented (latency, throughput)
- [ ] Security requirements identified (compliance, encryption)
- [ ] Technical debt constraints acknowledged
- [ ] Operational constraints listed (deployment, monitoring)
- [ ] Budget and timeline constraints confirmed

## Research Completed
- [ ] Searched codebase for similar functionality
- [ ] Reviewed internal documentation
- [ ] Researched external solutions and best practices
- [ ] Identified reusable libraries/frameworks
- [ ] Documented alternatives considered

## Validation
- [ ] All clarifying questions answered
- [ ] Problem understanding documented
- [ ] Requirements reviewed with stakeholders
- [ ] Technical feasibility confirmed
- [ ] Ready to proceed with implementation planning
```

### XY Problem Detection Checklist

```markdown
# XY Problem Detection Checklist

## Before Asking for Help

### Question Self-Check
- [ ] Am I asking about a specific solution (Y)?
- [ ] Have I explained the underlying problem (X)?
- [ ] Can I articulate WHY I need this specific thing?
- [ ] Am I open to alternative approaches?

### Context Completeness
- [ ] I've described the user/business need
- [ ] I've explained what I've already tried
- [ ] I've listed the constraints limiting my options
- [ ] I've shared relevant technical details

## Red Flags (You Might Have an XY Problem)

- [ ] I'm asking "How do I do [very specific thing]?" without explaining why
- [ ] I can't explain the business context
- [ ] I'm stuck on one particular approach
- [ ] I'm frustrated that helpers aren't answering my exact question
- [ ] I'm saying "I specifically need X" without explaining the need

## Reformulation Template

If you answered "yes" to any red flags, reformulate using this template:

### The Actual Problem (X)
**User Need**: [What user/business outcome am I trying to achieve?]
**Current Situation**: [How do things work now?]
**Problem**: [What's not working or what's the gap?]

### My Attempted Solution (Y)
**Approach**: [What I'm trying to do]
**Rationale**: [Why I thought this would work]
**Stuck Point**: [What's not working or what I don't understand]

### Constraints
**Technical**: [Stack, integrations, performance]
**Business**: [Budget, timeline, compliance]
**Team**: [Skills, availability]

### Open Question
**Specific**: [My question about Y]
**General**: "But I'm open to alternative approaches if there's a better way to achieve [X] within my constraints."
```

### AI Context Provision Template

```markdown
# AI Context for [Feature Name]

## Problem Statement
[One clear sentence: Who + What + Why + Impact]

## Business Context
**User Impact**: [How many users? What's the experience impact?]
**Business Impact**: [Revenue? Growth? Compliance? Competition?]
**Priority**: P0 | P1 | P2 | P3
**Timeline**: [Why now? What's the deadline?]
**Success Metrics**: [How do we measure success?]

## Current State
**Current Implementation**: [What exists today?]
**Performance**: [Current metrics]
**Problems**: [What's broken or inadequate?]
**Workarounds**: [How do users cope today?]

## Requirements
### Must Have
- [Requirement 1]
- [Requirement 2]

### Should Have
- [Requirement 1]
- [Requirement 2]

### Nice to Have
- [Requirement 1]
- [Requirement 2]

## Constraints
### Technical
- Stack: [Languages, frameworks]
- Integrations: [Must support/integrate with]
- Performance: [Latency, throughput, scale]
- Security: [Compliance, standards]

### Business
- Budget: [Maximum cost]
- Timeline: [Deadline and milestones]
- Compatibility: [Backward compatibility requirements]

### Team
- Skills: [Team expertise]
- Availability: [Developer time]
- Support: [Ongoing maintenance capacity]

## Edge Cases and Concerns
- [Edge case 1]
- [Edge case 2]
- [Security concern 1]
- [Performance concern 1]

## Success Criteria
- [ ] [Measurable criterion 1]
- [ ] [Measurable criterion 2]
- [ ] [Measurable criterion 3]

## Additional Context
**Related Features**: [Links to similar implementations]
**Past Attempts**: [What's been tried before and why it didn't work]
**Alternatives Considered**: [Other approaches and why rejected]
```

## Cross-References

This guide is part of the Context Filling Strategies framework:

- **[WHY_CONTEXT_MATTERS.md](./WHY_CONTEXT_MATTERS.md)**: Understanding the impact of context on code quality
- **[GEIST_GAP_ANALYSIS_FRAMEWORK.md](./GEIST_GAP_ANALYSIS_FRAMEWORK.md)**: Systematic three-dimensional context filling using Ghost/Geyser/Gist analysis
- **[CLARIFYING_QUESTIONS_PROTOCOL.md](./CLARIFYING_QUESTIONS_PROTOCOL.md)**: Framework for asking effective clarifying questions

**Related Workflows**:
- **BRD Creation**: `/08-project-management/BRD_CREATION_GUIDELINES.md`
- **Implementation Planning**: `/docs/MARKDOWN_PLAN_TEMPLATE.md`
- **TDD Workflow**: `/code_quality_practices/TDD_WORKFLOW_GUIDE.md`

## Summary

Problem identification is not a preliminary step—it's the foundation of efficient development. By investing 70% of time in understanding the problem, you achieve:

- **3x faster implementation** (right solution first time)
- **5x better code quality** (addresses root causes)
- **10x reduction in rework** (no solving wrong problems)
- **150x overall efficiency** (multiplier effect across stages)

**Key Principles**:
1. Use Five Whys to find root causes
2. Write one-sentence problem statements
3. Define SMART success criteria
4. Document constraints early
5. Avoid the XY Problem by stating problems, not solutions
6. Gather requirements systematically
7. Research existing solutions before implementing
8. Ask clarifying questions immediately
9. Document understanding before coding
10. Provide complete context to AI agents

**Problem-first development is context-efficient development.**
