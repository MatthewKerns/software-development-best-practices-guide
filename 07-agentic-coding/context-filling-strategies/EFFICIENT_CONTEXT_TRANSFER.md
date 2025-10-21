# Efficient Context Transfer: Maximizing LLM Understanding

## Overview

Efficient context transfer is the art of providing LLMs with exactly the information they need, in the format that maximizes understanding, without overwhelming their context window. Poor context transfer wastes tokens on irrelevant details, forces LLMs to infer critical information, and leads to misaligned implementations. This guide provides systematic techniques for transferring context efficiently.

**Key Insight:** The goal is not to transfer all available context, but to transfer the right context in the right format at the right time.

## Principles of Efficient Context Transfer

### 1. Structured Over Unstructured

LLMs process structured information more efficiently than free-form prose. Use templates, tables, lists, and hierarchical structures.

**Bad (Unstructured):**
```
The system needs to handle user authentication and we want it to be secure
but also fast and we're using JWT tokens and the database is PostgreSQL
and we need to support both email and OAuth login methods and there's a
rate limit we need to implement too.
```

**Good (Structured):**
```markdown
## Authentication Requirements

### Technology Stack
- Auth Method: JWT tokens
- Database: PostgreSQL
- Login Methods: Email + OAuth

### Functional Requirements
1. User login via email/password
2. User login via OAuth (Google, GitHub)
3. Token generation and validation
4. Session management

### Non-Functional Requirements
- Security: OWASP Top 10 compliant
- Performance: <100ms token validation
- Rate Limiting: 5 failed attempts per 15 minutes
```

### 2. Explicit Over Implicit

Don't make the LLM infer critical information. State assumptions, constraints, and requirements explicitly.

**Bad (Implicit):**
```
Implement the payment processing.
```

**Good (Explicit):**
```markdown
## Payment Processing Implementation

### Explicit Constraints
- **MUST NOT** store credit card numbers (PCI DSS compliance)
- **MUST** use Stripe API (organizational standard)
- **MUST** handle async webhook callbacks
- **MUST** support USD, EUR, GBP currencies

### Explicit Assumptions
- Stripe account already configured
- Webhook endpoint will be `/api/webhooks/stripe`
- Payment failures retry 3 times with exponential backoff
- Users can have multiple payment methods

### Edge Cases to Handle
- Network timeout during payment
- Partial refunds
- Currency conversion failures
- Duplicate webhook delivery
```

### 3. Prioritized Over Comprehensive

Provide the most critical information first. If context runs out, you want the LLM to have seen the essentials.

**Bad (Chronological/Random Order):**
```markdown
- The button should be blue
- We're using React 18
- The system processes invoices
- Performance is critical
- The button triggers invoice generation
- We have 10,000 users
```

**Good (Prioritized by Importance):**
```markdown
## Critical Context (Must Know)
1. **Core Function:** Generate invoices from order data
2. **Performance Requirement:** <2s generation time (SLA)
3. **Scale:** 10,000 active users, 50k invoices/month

## Important Context (Should Know)
4. **Tech Stack:** React 18, Node.js, PostgreSQL
5. **UI Requirements:** Blue CTA button, accessible (WCAG AA)

## Nice-to-Know Context
6. **Future Plans:** PDF export feature planned for Q2
```

### 4. Referenced Over Copied

Use file paths and function names instead of copying entire code blocks when possible.

**Bad (Copied Content):**
```markdown
Here's the entire authentication service code:
[500 lines of code]

Now implement the rate limiting feature.
```

**Good (Referenced Content):**
```markdown
## Relevant Context

### Existing Implementation
- Auth logic: `src/services/AuthService.ts` (see `validateToken()` method)
- User model: `src/models/User.ts` (has `loginAttempts` field)
- Current rate limit: None (this is the gap)

### Implementation Requirements
Add rate limiting to `AuthService.login()`:
- Track failed attempts in `User.loginAttempts`
- Reset counter after successful login
- Block after 5 failures for 15 minutes
- Follow pattern from `src/middleware/RateLimiter.ts` (used for API routes)
```

## The Geist Framework for Context

The Geist framework provides a three-dimensional analysis for comprehensive context transfer.

### Gist: What & Why (Core Problem)

**Template:**
```markdown
## Gist Analysis: [Feature/Problem Name]

### What (Irreducible Essence)
- Core problem: [One sentence describing the essential issue]
- Desired outcome: [Specific, measurable result]
- Success criteria: [How we know it's solved]

### Why (Business Value)
- User impact: [Who benefits and how]
- Business value: [Revenue, efficiency, compliance]
- Priority: [Critical/High/Medium/Low with justification]
```

**Example:**
```markdown
## Gist Analysis: Invoice Data Visibility

### What
- Core problem: Users cannot see material costs breakdown in invoices
- Desired outcome: Display 8 critical cost fields in invoice UI
- Success criteria: All fields visible, updates in real-time

### Why
- User impact: 10,000 contractors need cost visibility for job bidding
- Business value: Reduces support tickets by 40% (historical data)
- Priority: Critical - blocks Q1 revenue feature (contract bidding)
```

### Geyser: Forces (Constraints & Pressures)

**Template:**
```markdown
## Geyser Analysis: [Feature/Problem Name]

### Technical Forces
- Performance constraints: [Response times, throughput limits]
- Scalability requirements: [Current and projected load]
- Technology limitations: [What the stack can/cannot do]

### Business Forces
- Timeline pressure: [Deadlines and why they matter]
- Budget constraints: [Resource limitations]
- Stakeholder expectations: [What different groups need]

### External Forces
- Regulatory requirements: [Compliance mandates]
- Market pressure: [Competitive factors]
- User behavior patterns: [How users actually use the system]
```

**Example:**
```markdown
## Geyser Analysis: Real-Time Invoice Updates

### Technical Forces
- Performance: Must update <200ms (user perception threshold)
- Scale: 10k concurrent users, 50k invoices/month
- Tech limitation: Current REST API requires full page reload

### Business Forces
- Timeline: Q1 feature release (8 weeks remaining)
- Budget: Cannot add new infrastructure costs
- Stakeholders: Sales team promised this to key client

### External Forces
- Regulatory: GDPR compliance for data updates
- Market: Competitors have real-time updates (table stakes)
- User behavior: Users refresh page every 30s (server load issue)
```

### Ghost: Hidden Context (Assumptions & Dependencies)

**Template:**
```markdown
## Ghost Analysis: [Feature/Problem Name]

### Unknown Unknowns (What We Don't Know We Don't Know)
- Data assumptions: [What we assume about data quality/format]
- Integration assumptions: [What we assume about external systems]
- User assumptions: [What we assume about user behavior]

### Hidden Dependencies
- Technical dependencies: [Libraries, services, infrastructure]
- Data dependencies: [Required data, data flow]
- Team dependencies: [Other teams, approval processes]

### Edge Cases & Exceptions
- Error scenarios: [What can go wrong]
- Data anomalies: [Unexpected data patterns]
- User edge cases: [Unusual but valid usage patterns]
```

**Example:**
```markdown
## Ghost Analysis: Invoice Cost Breakdown Display

### Unknown Unknowns
- Data assumption: Costs always have 8 fields (WRONG - varies by invoice type)
- Integration assumption: Real-time API exists (WRONG - batch updates only)
- User assumption: All users need all fields (WRONG - role-based needs)

### Hidden Dependencies
- Technical: Requires database schema migration (discovered late)
- Data: Depends on accounting system sync (24-hour lag)
- Team: Finance approval needed for cost field visibility (compliance)

### Edge Cases
- Partial cost data (some fields missing)
- Historical invoices (different schema)
- Multi-currency costs (conversion rates)
- Negative costs (refunds/credits)
```

### Complete Geist Context Template

```markdown
# Geist Analysis: [Feature/Problem Name]

## Gist: Core Essence
**What:** [One sentence core problem]
**Why:** [One sentence business value]
**Success:** [One sentence measurable outcome]

## Geyser: Driving Forces
**Performance:** [Critical constraints]
**Scale:** [Current and projected]
**Timeline:** [Deadlines and why]
**Compliance:** [Regulatory requirements]

## Ghost: Hidden Context
**Assumptions:** [What we're assuming that might be wrong]
**Dependencies:** [Technical, data, team]
**Edge Cases:** [What can break]

## Convergence: Implementation Guidance
**Must Have:** [Critical requirements]
**Should Have:** [Important but not blocking]
**Could Have:** [Nice-to-have enhancements]
**Won't Have:** [Explicitly out of scope]
```

## Context Transfer Techniques

### 1. Upfront Loading

Provide comprehensive context before asking for implementation. Prevents back-and-forth clarification rounds.

**Pattern:**
```markdown
# [Feature Name] Implementation Request

## Complete Context Package

### Business Context (Why)
[Geist Gist analysis]

### Technical Context (How)
[Architecture, tech stack, patterns]

### Constraints (Boundaries)
[Geist Geyser analysis]

### Hidden Context (Risks)
[Geist Ghost analysis]

### Request
Now implement [specific task] following the above context.
```

**When to Use:**
- Complex features (3+ files)
- New developers onboarding
- Cross-team implementations
- Production-critical changes

### 2. Layered Approach

Start with essential context, provide details on request. Efficient for iterative development.

**Pattern:**
```markdown
## Layer 1: Essential Context (Always Provide)
- Core problem: [One sentence]
- Tech stack: [3-5 key technologies]
- Critical constraint: [One dealbreaker]

## Layer 2: Implementation Details (Provide If Asked)
- Architecture patterns
- Existing similar implementations
- Detailed requirements

## Layer 3: Edge Cases (Provide If Needed)
- Error scenarios
- Data anomalies
- Integration failures
```

**When to Use:**
- Simple features (1-2 files)
- Well-understood domains
- Experienced developers
- Prototyping/exploration

### 3. Examples Over Explanation

Show concrete examples instead of abstract explanations. LLMs learn patterns faster from examples.

**Bad (Abstract Explanation):**
```markdown
Implement error handling following our standard pattern where we catch
exceptions, log them with context, and return user-friendly messages
while preserving stack traces for debugging.
```

**Good (Concrete Example):**
```markdown
## Error Handling Pattern

### Example from AuthService.ts (Lines 45-60)
```typescript
async login(email: string, password: string): Promise<AuthResult> {
  try {
    const user = await this.userRepo.findByEmail(email);
    if (!user) {
      throw new AuthenticationError('Invalid credentials');
    }
    // ... rest of logic
  } catch (error) {
    logger.error('Login failed', {
      email,
      error: error.message,
      stack: error.stack
    });

    if (error instanceof AuthenticationError) {
      return { success: false, message: error.message };
    }

    return { success: false, message: 'Login failed. Please try again.' };
  }
}
```

### Follow This Pattern For Invoice Processing
- Try/catch around all async operations
- Log with context (invoice_id, user_id)
- Return user-friendly messages
- Preserve stack traces in logs
```

**When to Use:**
- Explaining coding patterns
- Onboarding new team members
- Documenting architectural decisions
- Teaching domain-specific conventions

### 4. Incremental Refinement

Start broad, narrow down based on LLM responses. Efficient for exploratory tasks.

**Pattern:**
```markdown
## Round 1: Broad Context
Implement invoice cost breakdown display.

## LLM Response Analysis
[Review what LLM asks about]

## Round 2: Targeted Context
[Provide only the missing context LLM needs]

## Round 3: Edge Case Context
[Add edge cases if implementation looks complete]
```

**When to Use:**
- Exploratory features
- Refactoring existing code
- Performance optimization
- Unclear requirements

## Efficient Context Formats

### 1. Structured Markdown

Use headings, lists, code blocks, and tables for maximum clarity.

**Template:**
```markdown
# Feature: [Name]

## Overview
[2-3 sentence summary]

## Requirements
### Functional
- [ ] Requirement 1
- [ ] Requirement 2

### Non-Functional
| Category | Requirement | Target |
|----------|-------------|--------|
| Performance | Response time | <200ms |
| Security | Authentication | JWT + refresh |
| Scalability | Concurrent users | 10,000 |

## Implementation Guidance
### File Structure
```
src/
  features/
    invoice/
      InvoiceDisplay.tsx  <- Add cost breakdown here
      InvoiceService.ts   <- Add API call here
```

### Code Patterns
```typescript
// Follow this pattern for data fetching
const { data, loading, error } = useInvoiceData(invoiceId);
```

## Acceptance Criteria
1. User sees 8 cost fields
2. Updates in real-time
3. Handles missing data gracefully
```

### 2. Decision Records

Document what was decided and why. Prevents LLM from revisiting settled decisions.

**Template:**
```markdown
## Decision Record: [Decision Name]

**Status:** Accepted | Proposed | Deprecated
**Date:** YYYY-MM-DD
**Deciders:** [Who decided]

### Context
[What problem this decision addresses]

### Decision
[What we decided to do]

### Consequences
**Positive:**
- Benefit 1
- Benefit 2

**Negative:**
- Trade-off 1
- Trade-off 2

### Alternatives Considered
1. **Alternative 1:** [Why rejected]
2. **Alternative 2:** [Why rejected]
```

**Example:**
```markdown
## Decision Record: Use WebSocket for Real-Time Invoice Updates

**Status:** Accepted
**Date:** 2025-01-15
**Deciders:** Engineering team, Product lead

### Context
Users refresh invoice page every 30s to see updates, causing unnecessary
server load. Need real-time updates without polling.

### Decision
Implement WebSocket connection for invoice updates instead of REST polling
or Server-Sent Events (SSE).

### Consequences
**Positive:**
- Bi-directional communication (can push updates to specific users)
- Lower latency than polling (immediate updates)
- Reduced server load (no repeated requests)

**Negative:**
- More complex infrastructure (WebSocket server required)
- Connection management complexity (reconnection logic)
- Harder to debug than REST APIs

### Alternatives Considered
1. **REST Polling:** Rejected - causes server load issues
2. **Server-Sent Events (SSE):** Rejected - one-way only, less flexible
3. **GraphQL Subscriptions:** Rejected - not using GraphQL elsewhere
```

### 3. Code Comments as Context

Embed context directly in code for maintenance and future LLM interactions.

**Pattern:**
```typescript
/**
 * Invoice Cost Breakdown Display
 *
 * CONTEXT: Users need visibility into 8 critical cost fields for job bidding.
 * Business impact: Reduces support tickets by 40% (historical data).
 *
 * CONSTRAINTS:
 * - Must render in <200ms (user perception threshold)
 * - Must handle missing fields gracefully (historical invoices)
 * - Must update in real-time via WebSocket (ADR-2025-001)
 *
 * EDGE CASES:
 * - Partial cost data: Display available fields, show "N/A" for missing
 * - Multi-currency: Convert to user's preferred currency
 * - Negative costs: Display as credits with distinct styling
 *
 * @see src/models/Invoice.ts for data structure
 * @see docs/adr/ADR-2025-001-websocket-updates.md for real-time decision
 */
export function InvoiceCostBreakdown({ invoice }: Props) {
  // Implementation here
}
```

### 4. Visual Diagrams

Use ASCII diagrams or reference image diagrams for architectural context.

**Data Flow Example:**
```markdown
## Invoice Cost Data Flow

```
User Action               Backend Processing           Display Update
-----------               ------------------           --------------

Click Invoice    ────>    Load from DB        ────>    Show Loading

                          Calculate Costs     ────>    Show Skeleton
                          (8 fields)

                          WebSocket Push      ────>    Update UI
                          (real-time)                  (<200ms)

Modify Cost      ────>    Validate           ────>    Optimistic UI

                          Save to DB         ────>    Confirm Save

                          Broadcast Update   ────>    Update Other
                          (WebSocket)                 Users' Views
```

```

**Architecture Example:**
```markdown
## System Architecture

```
┌─────────────┐
│   Browser   │
│  (React UI) │
└──────┬──────┘
       │ HTTP/WS
       │
┌──────▼──────────────────────────────┐
│     API Gateway (Node.js)           │
│  ┌──────────┐    ┌──────────────┐   │
│  │   REST   │    │  WebSocket   │   │
│  │ Endpoints│    │   Server     │   │
│  └────┬─────┘    └──────┬───────┘   │
└───────┼──────────────────┼───────────┘
        │                  │
        │ SQL              │ Pub/Sub
        │                  │
┌───────▼──────────────────▼───────────┐
│        PostgreSQL Database           │
│  ┌─────────────┐  ┌──────────────┐  │
│  │   Invoices  │  │  Real-Time   │  │
│  │    Table    │  │   Updates    │  │
│  └─────────────┘  └──────────────┘  │
└──────────────────────────────────────┘
```

```

## Anti-Patterns to Avoid

### 1. Dumping Entire Codebase

**Problem:** Wastes context window, makes LLM lose focus.

**Bad:**
```markdown
Here's our entire codebase (50,000 lines):
[Massive code dump]

Now fix the login bug.
```

**Good:**
```markdown
## Login Bug Context

### Relevant Files
- `src/services/AuthService.ts` (lines 45-120) - Where bug occurs
- `src/models/User.ts` (lines 20-30) - User model with loginAttempts field

### Bug Description
Login fails after 3 attempts instead of 5 (rate limit threshold).

### Hypothesis
`AuthService.ts:67` checks `loginAttempts >= 3` but should be `>= 5`.

### Validation
Test: `tests/auth.test.ts:line 156` expects 5 attempts.
```

### 2. Assuming LLM Knows Your Domain

**Problem:** LLM makes wrong assumptions about domain-specific terms.

**Bad:**
```markdown
Update the invoice GL code mapping.
```

**Good:**
```markdown
## Task: Update Invoice GL Code Mapping

### Domain Context
- **GL Code:** General Ledger code (accounting category)
- **In our system:** 5-digit numeric code (e.g., 10000 = Revenue)
- **Mapping:** Invoice line items → GL codes for accounting system
- **Current issue:** New product categories don't have GL codes

### Task Details
Add GL code mappings for 3 new product categories:
1. "Software Licenses" → GL code 40500
2. "Cloud Services" → GL code 40600
3. "Support Contracts" → GL code 40700

### Implementation Location
File: `src/config/gl-codes.ts`
Pattern: Add to `GL_CODE_MAPPING` object following existing format
```

### 3. Verbose Prose Instead of Structured Info

**Problem:** Hard to parse, easy to miss key details.

**Bad:**
```markdown
So we need to implement this feature where users can see their invoice
costs and it should be fast because users are complaining about performance
and we also need to make sure it works with historical invoices which
might not have all the fields and also we need to support multiple
currencies which is important for our international users and the data
comes from the accounting system which updates every 24 hours but we
want to show it in real-time so we need to cache it somehow and also...
```

**Good:**
```markdown
## Invoice Cost Display Feature

### Requirements (Prioritized)
1. **Must Have:**
   - Display 8 cost fields
   - <200ms render time
   - Handle missing fields (historical invoices)

2. **Should Have:**
   - Multi-currency support
   - Real-time updates (within 1 minute)

3. **Could Have:**
   - Cost trend visualization

### Technical Constraints
- Data source: Accounting system (24-hour batch updates)
- Solution: Cache in PostgreSQL, update via scheduled job
- Historical data: Some invoices missing 2-3 fields (display "N/A")

### Performance Targets
| Metric | Target | Current | Gap |
|--------|--------|---------|-----|
| Render time | <200ms | 450ms | -250ms |
| Data freshness | <1 min | 24 hours | Major |
```

### 4. Reactive Instead of Proactive Context

**Problem:** Wastes time in back-and-forth clarification.

**Bad Pattern:**
```
You: Implement invoice cost display.
LLM: What fields should be displayed?
You: These 8 fields.
LLM: What about missing data?
You: Show "N/A".
LLM: Performance requirements?
You: <200ms.
[5 more rounds of clarification]
```

**Good Pattern:**
```markdown
# Invoice Cost Display Implementation

## Complete Specification

### Display Fields (8 total)
1. Materials cost
2. Labor cost
3. Equipment cost
4. Overhead cost
5. Tax amount
6. Discount amount
7. Subtotal
8. Total

### Data Handling
- **Missing fields:** Display "N/A" (common in historical invoices)
- **Multi-currency:** Convert to user's preferred currency
- **Negative values:** Display as credits with distinct color

### Performance
- **Target:** <200ms render time
- **Current:** 450ms (needs optimization)
- **Strategy:** Virtualize list, lazy load details

### Technical Details
- **Component:** `src/components/InvoiceCostBreakdown.tsx`
- **Data hook:** `useInvoiceData(invoiceId)` (already exists)
- **Styling:** Follow design system in `src/styles/components.css`

### Acceptance Criteria
- [ ] All 8 fields display correctly
- [ ] Missing data shows "N/A"
- [ ] Renders in <200ms (measured with React Profiler)
- [ ] Passes accessibility audit (WCAG AA)
```

## Context Transfer Checklist

Use this checklist before providing context to LLMs:

### Essential Context (Always Provide)

- [ ] **Problem statement clear?**
  - One sentence describing core issue
  - Business impact quantified
  - User pain point identified

- [ ] **Requirements prioritized?**
  - Must have / Should have / Could have / Won't have
  - Success criteria measurable
  - Acceptance criteria testable

- [ ] **Constraints specified?**
  - Performance targets with metrics
  - Security requirements explicit
  - Timeline and resource limits clear

### Important Context (Usually Provide)

- [ ] **Assumptions documented?**
  - Technical assumptions stated
  - Data assumptions validated
  - User behavior assumptions checked

- [ ] **Dependencies listed?**
  - Technical dependencies (libraries, services)
  - Data dependencies (required data, sources)
  - Team dependencies (approvals, integrations)

- [ ] **Edge cases identified?**
  - Error scenarios documented
  - Data anomalies considered
  - User edge cases planned for

### Supporting Context (Provide If Relevant)

- [ ] **Examples provided?**
  - Code examples for patterns
  - Similar implementations referenced
  - Before/after scenarios shown

- [ ] **Architecture context?**
  - System diagram or description
  - Data flow visualization
  - Integration points mapped

- [ ] **Historical context?**
  - Why this problem exists
  - Previous solution attempts
  - Decision records referenced

### Quality Checks

- [ ] **Format optimized?**
  - Structured (headings, lists, tables)
  - Prioritized (critical info first)
  - Concise (no unnecessary details)

- [ ] **Completeness verified?**
  - Can LLM implement without asking clarifying questions?
  - Are all unknowns explicitly stated?
  - Are success criteria clear?

- [ ] **Efficiency validated?**
  - Using references instead of full code dumps?
  - Examples instead of abstract explanations?
  - Layered approach for complex features?

## Efficiency Templates

### Quick Feature Request Template

Use for simple features (1-2 files, <1 hour implementation):

```markdown
# [Feature Name]

**What:** [One sentence]
**Why:** [One sentence business value]
**Where:** [File path]
**Pattern:** [Similar implementation reference]

## Requirements
- [ ] Requirement 1
- [ ] Requirement 2

## Constraints
- Performance: [Target]
- Security: [Requirement]
```

### Complex Feature Request Template

Use for complex features (3+ files, >1 hour implementation):

```markdown
# [Feature Name] - Complete Context

## Geist Analysis

### Gist (Essence)
**What:** [Core problem]
**Why:** [Business value]
**Success:** [Measurable outcome]

### Geyser (Forces)
**Performance:** [Constraints]
**Scale:** [Current and projected]
**Timeline:** [Deadline and why]

### Ghost (Hidden Context)
**Assumptions:** [What might be wrong]
**Dependencies:** [Technical, data, team]
**Edge Cases:** [What can break]

## Technical Specification

### Architecture
[Diagram or description]

### Implementation Locations
```
src/
  feature/
    ComponentA.tsx  <- Add logic here
    ServiceB.ts     <- Add API call here
```

### Code Patterns
```typescript
// Follow this pattern
[Example code]
```

## Requirements & Acceptance

### Must Have (Critical)
- [ ] Requirement 1
- [ ] Requirement 2

### Should Have (Important)
- [ ] Requirement 3

### Acceptance Criteria
1. [Testable criterion 1]
2. [Testable criterion 2]

## Quality Targets

| Category | Target | How to Verify |
|----------|--------|---------------|
| Performance | <200ms | React Profiler |
| Security | OWASP Top 10 | Security scan |
| Coverage | >85% | Jest report |
```

### Bug Fix Request Template

```markdown
# Bug: [Short Description]

## Current Behavior
[What happens now - with error messages]

## Expected Behavior
[What should happen]

## Root Cause (If Known)
[File:line - hypothesis]

## Reproduction Steps
1. Step 1
2. Step 2
3. Bug occurs

## Relevant Context
- **Files:** [List 2-3 files max]
- **Recent changes:** [Related commits]
- **Environment:** [Production/staging/local]

## Fix Requirements
- [ ] Fix bug
- [ ] Add test to prevent regression
- [ ] Update related documentation
```

## Cross-References

- **[GEIST_GAP_ANALYSIS_FRAMEWORK.md](./GEIST_GAP_ANALYSIS_FRAMEWORK.md)** - Complete Geist analysis methodology and templates
- **[CONTEXT_PRIORITIZATION.md](./CONTEXT_PRIORITIZATION.md)** - Detailed prioritization strategies for context filling
- **[PROBLEM_IDENTIFICATION_FIRST.md](./PROBLEM_IDENTIFICATION_FIRST.md)** - Understanding problems before providing context
- **[AGENTIC_CODING_OPTIMIZATION.md](../optimization/AGENTIC_CODING_OPTIMIZATION.md)** - Context window optimization for multi-agent workflows

## Key Takeaways

1. **Structure trumps volume** - Well-organized minimal context beats comprehensive chaos
2. **Explicit beats implicit** - State assumptions, don't make LLM infer critical info
3. **Prioritize ruthlessly** - Most important context first, details on request
4. **Show, don't tell** - Examples are more efficient than explanations
5. **Reference, don't copy** - File paths beat full code dumps
6. **Use Geist framework** - Gist + Geyser + Ghost ensures comprehensive coverage
7. **Provide proactively** - Answer questions before they're asked
8. **Validate efficiency** - If LLM asks clarifying questions, your context transfer failed

**Remember:** The goal is not to transfer all context, but to transfer the right context efficiently. Every token counts.
