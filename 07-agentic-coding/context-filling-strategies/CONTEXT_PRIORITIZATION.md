# Context Prioritization Framework

**Last Updated:** 2025-10-21
**Status:** Active
**Applies To:** All agentic coding workflows requiring context transfer

## Overview

In agentic coding workflows, you face an infinite amount of context you *could* provide to an AI assistant, but limited time and attention to provide it. Not all context is equally valuable—some information blocks progress entirely if missing, while other details can be inferred or safely deferred. This guide provides a systematic framework for prioritizing what context to provide first, what to defer, and what to omit entirely.

**Core Principle:** Maximize AI productivity by frontloading blocking, high-impact context while deferring or omitting low-impact details that can be inferred, chosen automatically, or provided on request.

## The Context Prioritization Problem

### The Challenge

When initiating an agentic coding task, you have access to:
- Complete codebase history and architecture
- All business requirements and constraints
- Edge cases, error scenarios, and failure modes
- Performance benchmarks and optimization goals
- Historical decisions and rationale
- Team conventions and style preferences
- Documentation, comments, and institutional knowledge

**The problem:** Providing all this context upfront is impossible and counterproductive. You need a framework to decide what context enables immediate progress versus what can wait.

### Why Prioritization Matters

**Without prioritization:**
- AI assistants receive overwhelming, unfocused context dumps
- Critical blocking information gets buried in low-priority details
- Implementation stalls waiting for decisions that could have been made upfront
- Time wasted clarifying details the AI could have inferred

**With systematic prioritization:**
- AI assistants receive just enough context to start productive work
- Blocking decisions and constraints provided immediately
- Low-priority details deferred until relevant or requested
- Faster time-to-first-output with fewer clarification cycles

### The 80/20 Rule for Context

**80% of productivity** comes from **20% of context:**
- Core problem statement (what are we building and why?)
- Critical constraints (security, performance, compatibility)
- Blocking decisions (multiple valid approaches requiring human judgment)

**Remaining 20% of productivity** requires **80% of context:**
- Edge cases and error handling nuances
- Historical context and architectural rationale
- Optimization details and performance tuning
- Style preferences and naming conventions

**Strategy:** Provide the critical 20% immediately, defer the remaining 80% until needed.

## MoSCoW Prioritization for Context

Adapt the MoSCoW prioritization framework (Must, Should, Could, Won't) to context provision:

### Must Have Context (Priority 1)

**Definition:** Information without which the AI cannot proceed or will make fundamentally wrong decisions.

**Characteristics:**
- Blocks implementation if missing
- Affects architectural decisions
- Involves security or data integrity
- Has multiple valid approaches requiring human judgment

**Examples:**
- "We must support OAuth 2.0 authentication (not session-based)"
- "Database must handle 10,000 concurrent users (not just 100)"
- "Payment processing must be PCI-DSS compliant"
- "Use REST API (not GraphQL) to maintain consistency with existing services"

**Provision Strategy:** Provide immediately in initial task description.

### Should Have Context (Priority 2)

**Definition:** Important information that improves quality but can be inferred from existing patterns or has reasonable defaults.

**Characteristics:**
- Improves implementation quality
- Can be inferred from codebase analysis
- Has reasonable defaults if unspecified
- Matters for optimization but not core functionality

**Examples:**
- "Follow existing error handling patterns (see src/utils/errors.py)"
- "Aim for <200ms response time (match current endpoints)"
- "Include comprehensive logging (like other payment operations)"
- "Support edge case: user has no email address"

**Provision Strategy:** Provide if time allows, or when AI asks, or during review phase.

### Could Have Context (Priority 3)

**Definition:** Nice-to-know details with minimal impact on implementation decisions.

**Characteristics:**
- Minimal impact on core functionality
- Can be easily changed later
- Stylistic or preferential rather than functional
- AI can choose reasonable defaults

**Examples:**
- "Variable naming preference: snake_case vs camelCase" (linter enforces)
- "Use logger.info vs logger.debug for this specific message"
- "Add comment explaining algorithm" (AI can decide)
- "Historical note: we tried approach X in 2023 but deprecated it"

**Provision Strategy:** Defer unless specifically relevant or requested. Trust linters and code review to catch issues.

### Won't Have Context (Out of Scope)

**Definition:** Information that is irrelevant, outdated, or actively harmful to provide.

**Characteristics:**
- Not related to current task
- Outdated or deprecated information
- Would confuse or mislead the AI
- Covers future plans not yet approved

**Examples:**
- Implementation details of unrelated features
- Deprecated approaches no longer in use
- Speculative future requirements
- Internal team politics or organizational context

**Provision Strategy:** Actively exclude from context. Mention only to clarify what NOT to do.

## Priority Dimensions

Use these dimensions to classify context into priority levels:

### Impact Dimension

**High Impact → Priority 1:**
- Affects core architecture or API contracts
- Changes data models or database schemas
- Impacts security or compliance posture
- Influences technology stack choices

**Medium Impact → Priority 2:**
- Affects performance or scalability
- Influences UX or user-facing behavior
- Impacts maintainability or testability

**Low Impact → Priority 3:**
- Code organization preferences
- Comment or documentation style
- Variable naming conventions

### Risk Dimension

**High Risk → Priority 1:**
- Security vulnerabilities (auth, encryption, injection attacks)
- Data loss or corruption potential
- Privacy or compliance violations (GDPR, HIPAA, PCI-DSS)
- Financial transactions or billing logic

**Medium Risk → Priority 2:**
- Performance degradation under load
- Error handling gaps causing poor UX
- Integration failures with external systems

**Low Risk → Priority 3:**
- Logging verbosity levels
- UI aesthetic preferences
- Non-critical optimization opportunities

### Ambiguity Dimension

**High Ambiguity (Multiple Valid Approaches) → Priority 1:**
- Authentication strategy: sessions vs tokens vs OAuth
- Database choice: SQL vs NoSQL
- API style: REST vs GraphQL vs RPC
- State management: Redux vs Context vs MobX

**Medium Ambiguity (Preferred Approach Exists) → Priority 2:**
- Error handling pattern (use existing utility)
- Testing approach (follow established conventions)
- Folder structure (match current organization)

**Low Ambiguity (Single Obvious Approach) → Priority 3:**
- Import order (linter enforces)
- Brace style (formatter enforces)
- Comment format (convention is clear)

### Complexity Dimension

**High Complexity → Priority 1:**
- Multi-service distributed transactions
- Real-time data synchronization
- Complex business logic with many edge cases
- Performance-critical algorithms

**Medium Complexity → Priority 2:**
- Standard CRUD operations with validation
- Typical error handling and recovery
- Common integration patterns

**Low Complexity → Priority 3:**
- Simple utility functions
- Straightforward UI components
- Basic configuration changes

## Context Prioritization Framework

### Priority 1: Provide Immediately (Blocking Context)

**Core Problem Statement (Gist):**
```
"Implement user authentication to allow secure access to protected resources."
```

**Critical Constraints (Geyser Forces):**
- **Security:** "Must use OAuth 2.0 with JWT tokens (not sessions)"
- **Performance:** "Must handle 10,000 concurrent auth requests"
- **Compliance:** "Must be GDPR-compliant (no PII in tokens)"
- **Compatibility:** "Must integrate with existing User service API"

**Blocking Decisions (Multiple Valid Approaches):**
- **Technology choice:** "Use Auth0 managed service (not custom implementation)"
- **Token storage:** "Store tokens in httpOnly cookies (not localStorage)"
- **Refresh strategy:** "Implement sliding window refresh (not fixed expiration)"

**High-Risk Areas:**
- **Data integrity:** "Never expose user passwords or email addresses in logs"
- **Financial impact:** "Authentication failures must not lock out paying users"

**Format for Priority 1 Context:**
```markdown
## Task: Implement User Authentication

**Core Problem (Gist):**
Allow users to securely access protected resources with modern authentication.

**Critical Constraints (Geyser):**
- Security: OAuth 2.0 with JWT tokens (MANDATORY)
- Performance: 10,000 concurrent auth requests
- Compliance: GDPR-compliant (no PII in tokens)
- Integration: Must work with existing User service at /api/users

**Blocking Decisions:**
- Use Auth0 managed service (not custom implementation)
- Store tokens in httpOnly cookies (not localStorage due to XSS risk)
- Implement sliding window token refresh (15-minute windows)

**High-Risk Areas:**
- NEVER log passwords, tokens, or email addresses
- Authentication failures must not lock out paying users
```

### Priority 2: Provide If Time Allows (Important Context)

**Edge Cases and Error Scenarios (Ghost):**
- "Handle case where user has no email address (use username)"
- "Account for token refresh during network outage (queue requests)"
- "Support users with multiple active sessions (allow up to 5)"

**Optimization Requirements:**
- "Aim for <200ms authentication response time (match current API)"
- "Cache token validation results for 30 seconds to reduce database load"
- "Pre-fetch user permissions during authentication to reduce round-trips"

**Historical Context and Rationale:**
- "We previously used session-based auth but migrated to JWT in v2.0 for scalability"
- "Auth0 was chosen over custom implementation after security audit in 2024"
- "httpOnly cookies prevent XSS attacks that affected our previous localStorage approach"

**Integration Details:**
- "User service expects Authorization: Bearer <token> header"
- "Follow existing error response format: {status, error, message, details}"
- "Include request tracing headers (X-Request-ID) for debugging"

**Format for Priority 2 Context:**
```markdown
## Additional Context (Provide if needed)

**Edge Cases (Ghost):**
- Users without email addresses exist (use username as fallback)
- Network outages during token refresh (queue and retry up to 3 times)
- Multiple concurrent sessions (allow up to 5 per user)

**Performance Optimization:**
- Target: <200ms response time (current API average: 180ms)
- Cache token validation for 30s (reduces DB load by ~60%)
- Pre-fetch permissions during auth (eliminates second API call)

**Historical Context:**
- v1.0 used sessions (didn't scale beyond 1,000 users)
- v2.0 migrated to JWT (current architecture)
- Auth0 adopted Q1 2024 after security audit

**Integration Patterns:**
- Use existing error format: {status, error, message, details}
- Include X-Request-ID header for distributed tracing
- Follow User service API conventions (see docs/api/USER_SERVICE.md)
```

### Priority 3: Defer or Provide on Request (Low-Priority Context)

**Implementation Details AI Can Choose:**
- "Use descriptive variable names" (AI knows this)
- "Add code comments where helpful" (AI can decide)
- "Organize imports logically" (linter enforces)

**Stylistic Preferences:**
- "Prefer const over let for immutable variables" (linter enforces)
- "Use arrow functions for callbacks" (team convention, not critical)
- "Limit line length to 88 characters" (formatter enforces)

**Future Considerations:**
- "We may add biometric authentication in v3.0" (not relevant now)
- "Consider passwordless auth for enterprise tier" (future feature)
- "Explore WebAuthn for 2FA" (research phase, not implementation)

**Format for Priority 3 Context:**
```markdown
## Deferred Context (Provide only if asked)

**Code Style:**
(Omit - linters and formatters enforce conventions)

**Future Considerations:**
(Omit unless relevant to current architecture decisions)

**Historical Details:**
(Omit unless needed to understand current implementation)
```

## Decision Trees for Prioritization

### Is This Blocking?

```
Does the AI need this information to start implementation?
│
├─ YES: Can the AI proceed without it?
│   │
│   ├─ NO → Priority 1 (Must Have)
│   │   Examples: API choice, security requirements, data model
│   │
│   └─ YES: Will wrong assumption cause major rework?
│       │
│       ├─ YES → Priority 1 (Must Have)
│       │   Examples: Performance SLA, compliance requirements
│       │
│       └─ NO → Priority 2 (Should Have)
│           Examples: Optimization hints, edge case handling
│
└─ NO: Is this context high-risk?
    │
    ├─ YES → Priority 1 (Must Have)
    │   Examples: Security constraints, data integrity rules
    │
    └─ NO → Priority 2 or 3 (Could Have or Won't Have)
        Examples: Code style, historical notes
```

### Is This High-Risk?

```
Does this involve security, data loss, or compliance?
│
├─ YES → Priority 1 (Must Have)
│   Examples: Authentication approach, PII handling, financial logic
│
└─ NO: Does this affect multiple systems or users?
    │
    ├─ YES: Is recovery easy if wrong?
    │   │
    │   ├─ NO → Priority 1 (Must Have)
    │   │   Examples: Database migrations, API contracts
    │   │
    │   └─ YES → Priority 2 (Should Have)
    │       Examples: Feature flags, A/B testing
    │
    └─ NO → Priority 3 (Could Have or Won't Have)
        Examples: Single component change, isolated utility
```

### Multiple Valid Approaches?

```
Are there multiple technically valid implementations?
│
├─ YES: Does the choice affect other systems?
│   │
│   ├─ YES → Priority 1 (Must Have Decision)
│   │   Examples: API protocol (REST vs GraphQL), DB choice
│   │
│   └─ NO: Is there strong team preference?
│       │
│       ├─ YES → Priority 2 (Should Have)
│       │   Examples: Testing framework, state management
│       │
│       └─ NO → Priority 3 (AI Can Choose)
│           Examples: Variable names, comment style
│
└─ NO: Only one reasonable approach?
    │
    └─ Priority 3 (AI Will Infer)
        Examples: Import order, formatting, standard patterns
```

### Can AI Infer from Existing Code?

```
Is this pattern already established in the codebase?
│
├─ YES: Is the pattern obvious and consistent?
│   │
│   ├─ YES → Priority 3 (AI Can Infer)
│   │   Examples: Error handling, logging patterns
│   │
│   └─ NO: Multiple conflicting patterns exist?
│       │
│       └─ Priority 1 or 2 (Clarify Preferred Approach)
│           Examples: "Use new error handler, not deprecated one"
│
└─ NO: New pattern being introduced?
    │
    ├─ Important architectural decision?
    │   │
    │   ├─ YES → Priority 1 (Must Have)
    │   │   Examples: New database client, auth strategy
    │   │
    │   └─ NO → Priority 2 (Should Have)
    │       Examples: New utility function, helper class
    │
    └─ Minor addition?
        │
        └─ Priority 3 (AI Can Choose)
            Examples: Small helper, internal utility
```

## Practical Examples

### Example 1: Authentication Implementation

**Task:** "Implement user authentication for the web application"

**Priority 1 Context (Provide Immediately):**

```markdown
## Authentication Implementation

**Core Problem (Gist):**
Users need secure authentication to access protected resources.

**Critical Constraints (Geyser):**
- MUST use OAuth 2.0 with JWT tokens (company security standard)
- MUST be GDPR-compliant (no PII in tokens)
- MUST handle 10,000 concurrent requests (current peak: 8,000)
- MUST integrate with existing User service API at /api/users

**Blocking Decisions:**
- Use Auth0 managed service (approved by security team, not custom JWT)
- Store tokens in httpOnly cookies (prevents XSS attacks per security audit)
- Implement 15-minute sliding window refresh (balances security and UX)

**High-Risk Requirements:**
- NEVER log passwords, tokens, or email addresses
- Failed authentication must NOT lock out paying customers
- Token validation failures must fail securely (deny access, not allow)
```

**Priority 2 Context (Provide if time allows or when asked):**

```markdown
**Edge Cases (Ghost):**
- Handle users without email addresses (10% of user base uses username-only)
- Support users with multiple concurrent sessions (limit: 5 per user)
- Account for token refresh during network outages (queue and retry up to 3 times)

**Performance Optimization:**
- Target <200ms authentication response time (current API avg: 180ms)
- Cache token validation results for 30 seconds (reduces DB calls by 60%)
- Pre-fetch user permissions during auth (eliminates second round-trip)

**Integration Patterns:**
- Follow existing error response format: {status, error, message, details}
- Include X-Request-ID header for distributed tracing (see OBSERVABILITY.md)
- Use standardized rate limiting (same as other API endpoints)

**Historical Context:**
- v1.0 used session-based auth (didn't scale past 1,000 users)
- v2.0 migrated to JWT in Q2 2024
- Auth0 adopted after external security audit identified custom JWT risks
```

**Priority 3 Context (Defer unless requested):**

```markdown
**Code Style:**
(Omit - Black formatter and Ruff linter enforce all conventions)

**Future Plans:**
- May add biometric auth in v3.0 (research phase, not approved)
- Considering WebAuthn for enterprise 2FA (Q3 2026 roadmap)

**Team Preferences:**
(Omit - follow existing patterns in src/auth/)
```

### Example 2: Data Export Feature

**Task:** "Add data export functionality for user reports"

**Priority 1 Context (Provide Immediately):**

```markdown
## Data Export Feature

**Core Problem (Gist):**
Users need to export their report data in multiple formats for external analysis.

**Critical Constraints (Geyser):**
- MUST support CSV and JSON formats (customer requirement)
- MUST handle exports up to 100,000 rows (current largest report: 75,000)
- MUST be GDPR-compliant (only export data user has permission to access)
- MUST complete within 30 seconds or provide async download link

**Blocking Decisions:**
- Use streaming export (not in-memory) to handle large datasets
- Store exports in S3 with 24-hour expiration (not permanent storage)
- Implement row-level permission checks (not table-level)

**High-Risk Requirements:**
- MUST verify user permissions for every exported row
- MUST NOT include soft-deleted or archived data
- MUST sanitize data to prevent CSV injection attacks
```

**Priority 2 Context (Provide if time allows or when asked):**

```markdown
**Edge Cases (Ghost):**
- Handle reports with no data (return empty file with headers)
- Support special characters in data (proper CSV escaping)
- Account for concurrent export requests from same user (queue, limit to 3)
- Handle exports interrupted by network failure (resumable downloads)

**Performance Optimization:**
- Target <5 seconds for exports under 10,000 rows
- Use pagination (1,000 rows per chunk) for streaming
- Pre-generate exports for common reports (cache for 1 hour)

**Integration Patterns:**
- Follow existing async job pattern (see src/jobs/async_job_handler.py)
- Use standard notification system for "Export ready" emails
- Store export metadata in exports table (track user, timestamp, row count)

**UX Requirements:**
- Show progress indicator for exports >5 seconds
- Send email notification when export ready (for async exports)
- Provide "Download" and "Copy Link" options
```

**Priority 3 Context (Defer unless requested):**

```markdown
**File Naming:**
(AI can choose reasonable format: report_name_YYYY-MM-DD.csv)

**Code Organization:**
(Follow existing pattern in src/features/reports/)

**Future Enhancements:**
- May add Excel format in v2.1 (not committed)
- Considering scheduled exports (research phase)
```

### Example 3: Performance Optimization Task

**Task:** "Optimize the dashboard loading time"

**Priority 1 Context (Provide Immediately):**

```markdown
## Dashboard Performance Optimization

**Core Problem (Gist):**
Dashboard currently loads in 3.5 seconds; need <1 second for acceptable UX.

**Critical Constraints (Geyser):**
- MUST maintain current functionality (all 12 widgets)
- MUST support 5,000 concurrent dashboard loads
- MUST work with existing API endpoints (no breaking changes)
- MUST preserve real-time data updates (no stale caching)

**Blocking Decisions:**
- Use React Query for data fetching (replace custom fetch logic)
- Implement parallel API calls (not sequential waterfall)
- Use skeleton loaders (not blank screen during load)

**Performance Targets:**
- <1 second for initial render (critical)
- <500ms for widget updates (critical)
- <100ms for user interactions (critical)
```

**Priority 2 Context (Provide if time allows or when asked):**

```markdown
**Current Performance Analysis:**
- Initial load: 3.5s (target: <1s)
  - API calls: 2.1s (sequential, should be parallel)
  - Component rendering: 0.8s (re-rendering unnecessarily)
  - Bundle size: 0.6s (large unused dependencies)

**Optimization Opportunities (Ghost):**
- 6 of 12 API calls can run in parallel
- 4 components re-render on every state change (use React.memo)
- Bundle includes unused Material-UI components (tree-shake)
- No code splitting (load all widgets upfront)

**Testing Requirements:**
- Maintain 85% test coverage
- Add performance regression tests (Lighthouse CI)
- Test on slow 3G network (mobile users: 40% of traffic)

**Compatibility:**
- Must work on IE11 (5% of user base, enterprise customers)
- Must support screen readers (WCAG AA compliance)
```

**Priority 3 Context (Defer unless requested):**

```markdown
**Historical Context:**
- Dashboard built in v1.0 (2022) when user base was 1,000
- Performance was acceptable until 2024 growth (now 50,000 users)
- Previous optimization attempt in Q2 2024 improved from 5s to 3.5s

**Future Plans:**
- May redesign dashboard in v3.0 (2026 roadmap)
- Considering switching to Next.js SSR (research phase)
```

## Layered Context Provision Strategy

### Layer 1: Initial Context (Enable AI to Start)

**Provide in first message:**
- Core problem statement (Gist)
- Critical constraints and requirements (Geyser)
- Blocking decisions and technology choices
- High-risk areas requiring special attention

**Goal:** AI can begin implementation immediately with correct architecture and approach.

**Example:**
```markdown
Implement user authentication using Auth0 OAuth 2.0 with JWT tokens stored in httpOnly cookies. Must handle 10,000 concurrent requests and be GDPR-compliant (no PII in tokens). Token refresh uses 15-minute sliding windows. NEVER log passwords or tokens.
```

### Layer 2: Contextual Details (Provide When Asked or Relevant)

**Provide when:**
- AI asks clarifying questions
- Implementation reaches phase where context matters (e.g., error handling)
- Code review reveals missing considerations

**Contains:**
- Edge cases and error scenarios (Ghost)
- Optimization requirements and performance targets
- Integration patterns and existing code conventions
- Historical context and rationale for decisions

**Example:**
```markdown
For edge cases: Support users without email addresses (use username fallback). Allow up to 5 concurrent sessions per user. For performance: Aim for <200ms response time, cache token validation for 30s. We migrated from sessions to JWT in v2.0 due to scaling issues at 1,000+ users.
```

### Layer 3: On-Demand Details (Provide Only If Requested)

**Provide only when:**
- AI explicitly asks
- Code review identifies specific gap
- Unusual circumstance requires clarification

**Contains:**
- Implementation preferences AI can infer
- Code style and formatting (enforced by linters)
- Future considerations not affecting current design
- Nice-to-have optimizations

**Example:**
```markdown
Code style is enforced by Black and Ruff, so no specific guidance needed. Future v3.0 may add biometric auth, but doesn't affect current OAuth implementation. Use descriptive variable names and add comments where logic is non-obvious.
```

## Integration with Geist Framework

### Ghost Analysis Informs Priority 2 Context

**Ghost (Unknown Unknowns)** reveals edge cases and hidden requirements:

- "What assumptions am I making that might not hold?"
- "What edge cases exist in production but not in my mental model?"
- "What parallel realities (error states, race conditions) am I not seeing?"

**Prioritization:**
- Critical Ghost findings (security, data loss) → Priority 1
- Important Ghost findings (UX degradation, performance) → Priority 2
- Minor Ghost findings (rare edge cases) → Priority 3

**Example:**
```markdown
Ghost Analysis: "What if user has no email address?"
→ Priority 2 (affects 10% of users, has workaround: use username)

Ghost Analysis: "What if token refresh fails during auth check?"
→ Priority 1 (affects security: must fail securely, not allow access)
```

### Geyser Analysis Informs Priority 1 Constraints

**Geyser (Dynamic Forces)** reveals pressures and constraints:

- "What forces (scale, security, compliance) drive requirements?"
- "What pressures will cause system to fail if not addressed?"
- "What explosive growth or change is anticipated?"

**Prioritization:**
- All Geyser forces → Priority 1 (by definition, these are critical constraints)

**Example:**
```markdown
Geyser Analysis: "Must handle 10,000 concurrent auth requests"
→ Priority 1 (current peak: 8,000, system will fail without proper scaling)

Geyser Analysis: "GDPR compliance required"
→ Priority 1 (legal/regulatory constraint, non-negotiable)
```

### Gist Analysis Defines Core Problem (Always Priority 1)

**Gist (Essential Core)** defines what we're actually building:

- "What is the irreducible essence of this feature?"
- "What is the core problem versus nice-to-have additions?"
- "What must be present for this to be considered 'done'?"

**Prioritization:**
- Gist → Always Priority 1 (the foundation for all other context)

**Example:**
```markdown
Gist: "Secure user authentication to access protected resources"
→ Priority 1 (the core problem statement)

NOT Gist: "Beautiful login UI with animations"
→ Priority 3 (nice-to-have, not essential)
```

## Anti-Patterns to Avoid

### ❌ The Context Dump

**Symptom:** Providing 5,000 words of context before AI can start.

**Problem:** AI overwhelmed, critical details buried, slower time-to-first-output.

**Fix:** Use layered approach—Priority 1 upfront (200-400 words), Priority 2 on request.

### ❌ The Assumption Trap

**Symptom:** Assuming AI knows team conventions, omitting critical constraints.

**Problem:** AI makes incorrect architectural decisions, major rework required.

**Fix:** Always provide Priority 1 context explicitly, even if it seems obvious.

### ❌ The Over-Specification

**Symptom:** Dictating every implementation detail, variable name, comment.

**Problem:** Wastes time on low-priority details, doesn't leverage AI strengths.

**Fix:** Provide constraints and goals (Priority 1), let AI choose implementation (Priority 3).

### ❌ The Historical Novel

**Symptom:** Explaining 5 years of architectural evolution before defining task.

**Problem:** AI confused by deprecated information, unclear what's current.

**Fix:** Start with current state (Priority 1), add historical context only if it informs decisions (Priority 2).

### ❌ The Missing Ghost

**Symptom:** Providing happy-path requirements, omitting error scenarios and edge cases.

**Problem:** Implementation works for common cases, fails in production edge cases.

**Fix:** Use Ghost analysis to identify critical edge cases (Priority 1) and important edge cases (Priority 2).

### ❌ The Deferred Blocker

**Symptom:** Treating blocking decision as "we'll figure it out later" (Priority 3).

**Problem:** AI starts implementation, hits blocker, requires rework.

**Fix:** Identify blocking decisions upfront with decision trees, provide as Priority 1.

## Summary: Quick Reference Guide

### Priority 1 (Must Have) - Provide Immediately

✅ **Always Include:**
- Core problem statement (Gist)
- Critical constraints (Geyser: security, performance, compliance)
- Blocking decisions (multiple valid approaches requiring judgment)
- High-risk areas (security, data integrity, financial)
- Technology choices and architectural decisions

🎯 **Target:** 200-400 words, enables AI to start immediately

### Priority 2 (Should Have) - Provide If Time Allows

✅ **Include When Possible:**
- Edge cases and error scenarios (Ghost)
- Optimization requirements and performance targets
- Integration patterns and existing conventions
- Historical context and decision rationale

🎯 **Target:** 300-600 words, improves quality and reduces iterations

### Priority 3 (Could Have) - Defer or Omit

✅ **Provide Only If Asked:**
- Implementation details AI can choose
- Code style preferences (linter-enforced)
- Future considerations not affecting current design
- Nice-to-have optimizations

🎯 **Target:** Minimal or zero words upfront, provided on request

### Priority Decision Checklist

Ask yourself:

1. **Is this blocking?** If AI can't proceed → Priority 1
2. **Is this high-risk?** If security/data loss → Priority 1
3. **Multiple valid approaches?** If requires judgment → Priority 1
4. **Can AI infer from codebase?** If clear pattern exists → Priority 3
5. **Is this edge case critical?** If affects many users or high risk → Priority 2
6. **Is this stylistic?** If linter enforces → Priority 3

### Integration with Workflow

**Planning Phase:**
- Extract Gist → Priority 1
- Identify Geyser forces → Priority 1
- Document Ghost findings → Priority 2 (critical ones → Priority 1)

**Implementation Phase:**
- Provide Priority 1 in initial task description
- Keep Priority 2 ready for when AI asks or reaches relevant phase
- Defer Priority 3 unless specifically requested

**Review Phase:**
- Check if Priority 1 context was sufficient (AI didn't make wrong architectural decisions)
- Identify missing Priority 2 context that caused quality issues
- Confirm Priority 3 deferrals were appropriate (no critical details omitted)

## Conclusion

Context prioritization is not about withholding information—it's about providing the *right* information at the *right* time to maximize AI productivity. By frontloading blocking, high-impact context (Priority 1) and deferring low-impact details (Priority 3), you enable AI assistants to start productive work immediately while maintaining the flexibility to provide additional context as needed.

**Key Takeaways:**

1. **Use MoSCoW framework** to classify context into Must/Should/Could/Won't Have
2. **Apply decision trees** to systematically determine priority levels
3. **Provide layered context** starting with Priority 1, adding Priority 2 when relevant
4. **Integrate with Geist framework** (Ghost → P2, Geyser → P1, Gist → P1)
5. **Avoid anti-patterns** like context dumps, over-specification, and missing blockers

**Next Steps:**
- Apply framework to your next agentic coding task
- Document what context was actually needed vs. what you provided
- Refine your prioritization based on real-world outcomes
- Share learnings with team to improve collective context provision

---

## Related Documentation

- **[EFFICIENT_CONTEXT_TRANSFER.md](./EFFICIENT_CONTEXT_TRANSFER.md)** - How to transfer context efficiently once priorities are determined
- **[PROBLEM_IDENTIFICATION_FIRST.md](./PROBLEM_IDENTIFICATION_FIRST.md)** - Understanding the problem before prioritizing context
- **[GEIST_GAP_ANALYSIS_FRAMEWORK.md](./GEIST_GAP_ANALYSIS_FRAMEWORK.md)** - Ghost/Geyser/Gist framework for comprehensive analysis
- **[Sub-Agent Architecture](../../CLAUDE.md#sub-agent-architecture)** - Geist analyzer and requirements analyzer patterns

---

**Document Metadata:**
- **Word Count:** ~6,800 words (comprehensive guide)
- **Target Audience:** Technical leads, product managers, AI-assisted developers
- **Maintenance:** Review quarterly, update based on workflow learnings
- **Version:** 1.0.0
