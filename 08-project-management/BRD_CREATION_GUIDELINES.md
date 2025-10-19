# Business Requirements Document (BRD) Creation Guidelines

## Overview

This guide provides comprehensive instructions for creating Business Requirements Documents (BRDs) that align with Geist-driven development, Test-Driven Development (TDD), and quality assurance best practices. A well-crafted BRD serves as the foundation for successful project execution, ensuring all stakeholders share a common understanding of what needs to be built and why.

**Reference Standard:** Based on industry-standard BRD practices adapted for modern software development workflows.

**Integration with Development Workflow:**
- BRD → Geist Analysis → Implementation Plan → TDD → Validation
- Requirements traceability from BRD through to test coverage
- Continuous validation against business objectives

---

## Table of Contents

1. [Document Purpose and Scope](#document-purpose-and-scope)
2. [Document Structure](#document-structure)
3. [Requirements Specification](#requirements-specification)
4. [Geist-Driven Requirements Analysis](#geist-driven-requirements-analysis)
5. [Use Case Documentation](#use-case-documentation)
6. [Functional vs Non-Functional Requirements](#functional-vs-non-functional-requirements)
7. [Traceability Matrix](#traceability-matrix)
8. [Validation and Verification](#validation-and-verification)
9. [BRD Template Usage](#brd-template-usage)
10. [Best Practices](#best-practices)

---

## Document Purpose and Scope

### What is a BRD?

A Business Requirements Document (BRD) is a formal document that captures business objectives, stakeholder needs, and detailed requirements for a software project. It serves as:

- **Communication tool** between business stakeholders and technical teams
- **Contract baseline** defining what will be delivered
- **Reference document** for implementation planning and testing
- **Validation criteria** for project completion

### When to Create a BRD

Create a BRD for:
- **New features** requiring 3+ development days
- **System integrations** with external services or APIs
- **Architecture changes** impacting multiple system components
- **Regulatory compliance** initiatives requiring documentation
- **Client-requested features** needing formal acceptance criteria
- **Complex workflows** spanning multiple user roles or systems

### BRD vs Implementation Plan

| Document Type | Purpose | Audience | When Created |
|--------------|---------|----------|--------------|
| **BRD** | Define WHAT and WHY | Business stakeholders, Product owners | Before development begins |
| **Implementation Plan** | Define HOW | Developers, Architects | After BRD approval |

**Key Distinction:** BRD focuses on business value and requirements; Implementation Plan focuses on technical approach and execution.

---

## Document Structure

### Required Sections

Every BRD must include the following sections:

#### 1. **Document Control**
```markdown
**Document Title:** [Feature/Project Name] Business Requirements Document
**Version:** X.Y (semantic versioning)
**Date:** YYYY-MM-DD
**Author:** [Name, Role]
**Stakeholders:** [List of key stakeholders]
**Status:** [Draft | Under Review | Approved | Superseded]
**Approvers:** [Names and approval dates]

**Change History:**
| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0 | 2025-01-15 | Jane Doe | Initial draft |
| 1.1 | 2025-01-20 | Jane Doe | Updated based on stakeholder feedback |
```

#### 2. **Executive Summary**
- **Business Problem:** 2-3 sentence description of the problem being solved
- **Proposed Solution:** High-level solution approach
- **Business Value:** Expected ROI, efficiency gains, or strategic benefits
- **Effort Estimate:** High-level time and resource requirements
- **Success Metrics:** 3-5 key performance indicators (KPIs)

#### 3. **Business Context**
- **Background:** Current state and why change is needed
- **Strategic Alignment:** How this supports business objectives
- **Market Drivers:** Competitive landscape, customer demands, regulatory requirements
- **Constraints:** Budget, timeline, technical, regulatory limitations

#### 4. **Stakeholder Analysis**
- **Primary Stakeholders:** Decision makers and direct beneficiaries
- **Secondary Stakeholders:** Affected parties and support teams
- **Roles and Responsibilities:** RACI matrix (Responsible, Accountable, Consulted, Informed)

#### 5. **Scope Definition**
- **In Scope:** Specific features, functions, and deliverables included
- **Out of Scope:** Explicitly state what will NOT be included
- **Assumptions:** Conditions assumed to be true for planning purposes
- **Dependencies:** External systems, teams, or projects this depends on

#### 6. **Requirements Specification** (See detailed section below)
- Functional Requirements
- Non-Functional Requirements
- Technical Requirements
- Security Requirements
- Compliance Requirements

#### 7. **Use Cases** (See detailed section below)
- User Personas
- Scenarios and Workflows
- User Stories

#### 8. **Geist Analysis** (See detailed section below)
- Ghost Analysis: Unknown unknowns
- Geyser Analysis: Forces and pressures
- Gist Analysis: Essential core

#### 9. **Acceptance Criteria**
- Measurable, testable criteria for feature acceptance
- Success scenarios and edge cases
- Performance benchmarks

#### 10. **Risk Assessment**
- Technical Risks
- Business Risks
- Mitigation Strategies

#### 11. **Appendices**
- Glossary of Terms
- References and Supporting Documents
- Data Models and Wireframes

---

## Requirements Specification

### Requirement Formatting Standard

Each requirement must follow this format:

```markdown
**[REQ-ID]:** [Requirement Type]-[Category]-[Number]

**Priority:** [Critical | High | Medium | Low]

**Description:** Clear, concise statement of the requirement using SHALL/SHOULD/MAY language.

**Rationale:** WHY this requirement exists (business justification).

**Acceptance Criteria:**
- [ ] Specific, testable criterion 1
- [ ] Specific, testable criterion 2
- [ ] Specific, testable criterion 3

**Dependencies:** [Related requirements or external dependencies]

**Test Cases:** [Reference to test scenarios]

**Geist Classification:** [Ghost | Geyser | Gist]
```

#### Example Requirements

**Example 1: Functional Requirement**
```markdown
**[REQ-FR-AUTH-001]:** User Authentication

**Priority:** Critical

**Description:** The system SHALL require users to authenticate with email and password before accessing protected resources.

**Rationale:** Protect sensitive user data and ensure compliance with data privacy regulations (GDPR, CCPA).

**Acceptance Criteria:**
- [ ] Login form accepts email and password
- [ ] Successful authentication redirects to dashboard
- [ ] Failed authentication displays error message
- [ ] Account locked after 5 failed attempts
- [ ] Session expires after 30 minutes of inactivity

**Dependencies:**
- REQ-NFR-SEC-001 (Password encryption)
- REQ-FR-AUTH-002 (Password reset flow)

**Test Cases:** TC-AUTH-001 through TC-AUTH-008

**Geist Classification:** Gist (essential security requirement)
```

**Example 2: Non-Functional Requirement**
```markdown
**[REQ-NFR-PERF-001]:** API Response Time

**Priority:** High

**Description:** The system SHALL respond to API requests within 200ms for 95% of requests under normal load.

**Rationale:** Ensure responsive user experience and meet SLA commitments to enterprise customers.

**Acceptance Criteria:**
- [ ] P95 latency ≤ 200ms for read operations
- [ ] P95 latency ≤ 500ms for write operations
- [ ] Load test with 1000 concurrent users validates performance
- [ ] Performance monitoring dashboards track latency in production

**Dependencies:**
- REQ-TECH-INFRA-001 (Database indexing strategy)
- REQ-TECH-INFRA-002 (Caching layer implementation)

**Test Cases:** TC-PERF-001 through TC-PERF-005

**Geist Classification:** Geyser (performance pressure under load)
```

### Requirement Language Standards

Use precise, unambiguous language:

- **SHALL:** Mandatory requirement (must be implemented)
- **SHOULD:** Recommended requirement (implement unless strong reason not to)
- **MAY:** Optional requirement (implement if time/budget permits)
- **WILL:** Statement of fact or future action (not a requirement)

**Good Requirements:**
- ✅ "The system SHALL validate email format before accepting user registration"
- ✅ "The API SHOULD return results in JSON format"
- ✅ "Users MAY customize their dashboard layout"

**Poor Requirements:**
- ❌ "The system will be fast" (vague, not measurable)
- ❌ "Users want to export data" (not a requirement, just a desire)
- ❌ "The UI should look good" (subjective, not testable)

---

## Geist-Driven Requirements Analysis

### Three-Dimensional Requirements Framework

Apply Geist analysis to all requirements to uncover hidden complexities and validate essential features.

#### 1. Ghost Analysis: Unknown Unknowns

**Purpose:** Identify assumptions, missing information, and hidden dependencies that could derail the project.

**Questions to Ask:**
- What are we assuming about user behavior?
- What external systems or data sources do we depend on?
- What edge cases might we be overlooking?
- What happens if our assumptions are wrong?
- What context gaps exist in our understanding?

**Documentation Format:**
```markdown
### Ghost Analysis: Unknown Unknowns

**Assumptions:**
1. Users have reliable internet connectivity
2. Third-party API uptime is 99.9%
3. Users understand industry-specific terminology

**Missing Information:**
1. Exact data volume for initial migration (estimate: 10M records)
2. Peak concurrent user load (estimate: 5,000 users)
3. Integration API rate limits (pending vendor confirmation)

**Hidden Dependencies:**
1. Email service provider for notifications
2. Payment gateway compliance requirements
3. Legacy system data format compatibility

**Mitigation Strategies:**
1. Build offline mode for connectivity issues
2. Implement circuit breaker for API failures
3. Create glossary and in-app help tooltips
```

#### 2. Geyser Analysis: Forces and Pressures

**Purpose:** Identify dynamic forces, explosive growth scenarios, and pressure points that could impact the system.

**Questions to Ask:**
- What happens under peak load or viral growth?
- What regulatory or compliance pressures exist?
- What competitive pressures drive feature urgency?
- What technical debt or legacy constraints create friction?
- What organizational dynamics affect delivery?

**Documentation Format:**
```markdown
### Geyser Analysis: Dynamic Forces

**Performance Pressures:**
- Black Friday traffic spike: 50x normal load expected
- Real-time processing requirement during trading hours
- Database query performance degrades with >1M records

**Regulatory Forces:**
- GDPR compliance deadline: 3 months
- SOC 2 audit requirements
- PCI-DSS for payment processing

**Competitive Pressures:**
- Competitor launched similar feature last month
- Customer churn risk if not delivered by Q2
- Market expectation for mobile-first experience

**Technical Forces:**
- Legacy monolith architecture limits scalability
- Team skill gap in React (training required)
- Database migration during implementation

**Mitigation Strategies:**
1. Horizontal scaling architecture from day one
2. Compliance review in every sprint
3. MVP approach to beat competitor to market
4. Microservices pattern for new features
5. Parallel training program for team
```

#### 3. Gist Analysis: Essential Core

**Purpose:** Distill requirements to their irreducible essence, separating must-haves from nice-to-haves.

**Questions to Ask:**
- What is the ONE thing this feature must accomplish?
- If we could only build 20% of this, what would it be?
- What's the minimum viable solution that delivers business value?
- Which requirements are truly essential vs just desired?
- What would make this feature a success in users' eyes?

**Documentation Format:**
```markdown
### Gist Analysis: Essential Core

**Essential Features (MVP):**
1. User can authenticate securely
2. User can create and save a document
3. User can share document with collaborators
4. System auto-saves every 5 seconds

**Non-Essential but Valuable:**
1. Version history beyond 30 days
2. Advanced formatting options
3. Real-time collaboration cursor
4. Mobile app (web mobile-responsive sufficient for MVP)

**Nice-to-Have (Future Iterations):**
1. AI-powered writing suggestions
2. Integration with third-party tools
3. Custom branding/white-label

**Core Value Proposition:**
"Enable teams to collaboratively create and securely share documents with zero data loss."

**Success Definition:**
- 80% of users successfully create first document within 5 minutes
- <1% data loss rate
- 4+ out of 5 user satisfaction rating
```

### Integrating Geist Analysis with Requirements

Each requirement should be tagged with its Geist classification:

- **Gist Requirements:** Essential, cannot be compromised
- **Geyser Requirements:** Driven by external forces, may have flexibility in approach
- **Ghost Requirements:** Based on assumptions, need validation and contingency plans

**Example Prioritization Matrix:**

| Requirement ID | Type | Geist | Priority | Effort | Risk |
|---------------|------|-------|----------|--------|------|
| REQ-FR-AUTH-001 | Functional | Gist | Critical | 5 days | Low |
| REQ-NFR-PERF-001 | Non-Functional | Geyser | High | 8 days | Medium |
| REQ-FR-EXPORT-003 | Functional | Ghost | Medium | 3 days | High |

---

## Use Case Documentation

### User Personas

Define 3-5 primary user personas:

```markdown
### Persona: Sarah - Project Manager

**Demographics:**
- Age: 35-45
- Role: Senior Project Manager
- Experience: 10+ years in technology projects
- Technical Skill: Intermediate (comfortable with software tools, not a developer)

**Goals:**
- Track project progress in real-time
- Identify risks and blockers early
- Generate executive-level reports quickly
- Collaborate with distributed teams

**Pain Points:**
- Current tools require manual data entry
- Too many tools to check for status updates
- Difficult to see big picture across projects
- Reports take hours to compile

**Use Case Priorities:**
1. Dashboard with project health indicators (Critical)
2. Automated status reports (High)
3. Risk identification and alerts (High)
4. Cross-project resource allocation view (Medium)

**Quote:** "I need to see everything in one place, not jump between five different tools."
```

### Use Case Scenarios

Document 5-10 primary use cases:

```markdown
### Use Case: UC-001 - User Registration

**Actor:** New User (Unregistered)

**Preconditions:**
- User has valid email address
- User has internet connection
- Registration system is operational

**Main Success Scenario:**
1. User navigates to registration page
2. System displays registration form (email, password, name)
3. User enters required information
4. User clicks "Create Account" button
5. System validates email format and password strength
6. System creates user account in database
7. System sends verification email to user
8. System displays "Please check your email" message
9. User clicks verification link in email
10. System activates account and redirects to dashboard

**Postconditions:**
- User account is created and activated
- User is logged in
- Audit log records account creation event

**Alternative Flows:**

**Alt 3a: Email already registered**
- System displays "Email already in use" error
- User can choose "Forgot Password" or use different email

**Alt 5a: Invalid email format**
- System displays inline validation error
- User corrects email format
- Continue from step 4

**Alt 5b: Weak password**
- System displays password strength requirements
- User strengthens password
- Continue from step 4

**Alt 9a: Verification link expired**
- System displays "Link expired" message
- System offers to resend verification email
- Continue from step 7

**Exception Flows:**

**Exception: Database unavailable**
- System displays "Service temporarily unavailable" error
- System logs error for operations team
- User can retry or contact support

**Business Rules:**
- BR-001: Email must be unique in the system
- BR-002: Password must be minimum 12 characters with uppercase, lowercase, number, and special character
- BR-003: Verification link expires after 24 hours
- BR-004: Account activation required before first login

**Non-Functional Requirements:**
- Response time: < 2 seconds for form submission
- Concurrency: Support 100 simultaneous registrations
- Security: Password must be hashed with bcrypt (cost factor 12)
- Accessibility: WCAG 2.1 Level AA compliance

**Related Requirements:**
- REQ-FR-AUTH-001 (User Authentication)
- REQ-NFR-SEC-002 (Password Security)
- REQ-FR-EMAIL-001 (Email Verification)

**Test Cases:**
- TC-UC001-001: Happy path registration
- TC-UC001-002: Duplicate email handling
- TC-UC001-003: Invalid email format
- TC-UC001-004: Weak password rejection
- TC-UC001-005: Verification link expiration
```

### User Stories Format

Supplement use cases with agile user stories:

```markdown
### User Story: US-042

**As a** project manager
**I want to** export project status reports to PDF
**So that** I can share updates with executives who prefer printed documents

**Priority:** Medium
**Story Points:** 5
**Sprint:** Sprint 12

**Acceptance Criteria:**
- [ ] GIVEN I am viewing a project dashboard
      WHEN I click "Export to PDF" button
      THEN a PDF report is generated within 5 seconds
- [ ] GIVEN the PDF report is generated
      WHEN I open the PDF
      THEN it contains project name, status, milestones, and risk summary
- [ ] GIVEN I want to customize the report
      WHEN I access export options
      THEN I can select which sections to include
- [ ] GIVEN the report contains sensitive data
      WHEN I export to PDF
      THEN the PDF is password-protected with user-defined password

**Dependencies:**
- US-038: Dashboard visualization complete
- TECH-DEBT-005: PDF generation library integration

**Technical Notes:**
- Use Puppeteer for PDF generation
- Consider implementing report template system for future customization
- Ensure PDF/A compliance for archival purposes

**Definition of Done:**
- [ ] Code reviewed and approved
- [ ] Unit tests pass (≥90% coverage)
- [ ] Integration tests pass
- [ ] Accessibility tested (PDF screen reader compatible)
- [ ] Performance tested (generates 10-page report in <5 seconds)
- [ ] Documentation updated
- [ ] Accepted by Product Owner
```

---

## Functional vs Non-Functional Requirements

### Functional Requirements (FR)

**Definition:** Specific behaviors, features, or functions the system must perform.

**Categories:**
1. **Business Logic:** Rules, calculations, data processing
2. **User Interface:** Screens, forms, navigation, workflows
3. **Data Management:** CRUD operations, data validation, data transformation
4. **Integration:** External systems, APIs, third-party services
5. **Reporting:** Reports, exports, analytics

**Template:**
```markdown
**[REQ-FR-[CATEGORY]-###]:** [Requirement Title]

**Priority:** [Critical | High | Medium | Low]

**Description:** The system SHALL [action] when [condition] so that [business outcome].

**Acceptance Criteria:**
- [ ] Criterion 1
- [ ] Criterion 2
```

**Examples:**
- REQ-FR-CALC-001: System SHALL calculate invoice total as sum of line items plus applicable taxes
- REQ-FR-UI-005: System SHALL display validation errors inline next to form fields
- REQ-FR-DATA-012: System SHALL archive records older than 7 years to cold storage
- REQ-FR-INT-003: System SHALL sync customer data with Salesforce every 15 minutes

### Non-Functional Requirements (NFR)

**Definition:** Quality attributes, constraints, and system characteristics that define how the system performs.

**Categories:**

#### 1. Performance Requirements
```markdown
**[REQ-NFR-PERF-###]:**

- Response time: API calls complete in <200ms (P95)
- Throughput: Handle 10,000 requests/second
- Resource utilization: CPU <70% under normal load
- Scalability: Support 100,000 concurrent users
```

#### 2. Security Requirements
```markdown
**[REQ-NFR-SEC-###]:**

- Authentication: Multi-factor authentication for admin users
- Authorization: Role-based access control (RBAC)
- Encryption: TLS 1.3 for data in transit, AES-256 for data at rest
- Audit: Log all data access with user identity and timestamp
- Vulnerability: OWASP Top 10 compliance
```

#### 3. Reliability/Availability Requirements
```markdown
**[REQ-NFR-REL-###]:**

- Uptime: 99.9% availability (43 minutes downtime/month max)
- Recovery Time Objective (RTO): <1 hour
- Recovery Point Objective (RPO): <15 minutes data loss max
- Backup: Daily automated backups with 30-day retention
- Failover: Automatic failover to standby instance within 5 minutes
```

#### 4. Usability Requirements
```markdown
**[REQ-NFR-USE-###]:**

- Learnability: New users complete first task within 10 minutes
- Efficiency: Power users complete common tasks in <3 clicks
- Error handling: Clear error messages with recovery suggestions
- Accessibility: WCAG 2.1 Level AA compliance
- Internationalization: Support English, Spanish, French, German
```

#### 5. Maintainability Requirements
```markdown
**[REQ-NFR-MAINT-###]:**

- Code quality: ≥85% test coverage, linting passes
- Documentation: All APIs documented with OpenAPI spec
- Monitoring: Application performance monitoring (APM) integrated
- Logging: Structured logging with correlation IDs
- Deployment: Zero-downtime blue-green deployments
```

#### 6. Compliance Requirements
```markdown
**[REQ-NFR-COMP-###]:**

- GDPR: Right to access, rectification, erasure, data portability
- HIPAA: PHI encryption, audit trails, access controls
- SOC 2: Security, availability, confidentiality controls
- PCI-DSS: Cardholder data protection (if applicable)
```

### Functional vs Non-Functional Decision Tree

```
Is the requirement describing...

WHAT the system does?
└─ YES → Functional Requirement
   Examples: "Calculate tax", "Send email", "Display chart"

└─ NO → Is it describing HOW WELL the system does it?
   └─ YES → Non-Functional Requirement
      Examples: "Calculate in <100ms", "99.9% email delivery", "Chart loads in 2s"
```

---

## Traceability Matrix

### Purpose

A traceability matrix ensures:
1. Every requirement is linked to business objectives
2. Every requirement has associated test cases
3. Requirements coverage is complete
4. Impact analysis for changes is possible

### Traceability Matrix Structure

```markdown
## Requirements Traceability Matrix

| Req ID | Requirement Summary | Business Objective | Design Spec | Test Case(s) | Implementation Status | Verification Status |
|--------|---------------------|-------------------|-------------|--------------|----------------------|---------------------|
| REQ-FR-AUTH-001 | User login | BO-SEC-001 | ARCH-AUTH-001 | TC-AUTH-001, TC-AUTH-002, TC-AUTH-003 | Complete | Verified |
| REQ-NFR-PERF-001 | API response time | BO-UX-002 | ARCH-PERF-001 | TC-PERF-001, TC-PERF-002 | Complete | Verified |
| REQ-FR-REPORT-005 | PDF export | BO-REPORT-001 | DESIGN-EXPORT-001 | TC-REPORT-010 | In Progress | Not Tested |
```

### Bidirectional Traceability

**Forward Traceability:** Business Objective → Requirement → Design → Implementation → Test
**Backward Traceability:** Test → Implementation → Design → Requirement → Business Objective

```markdown
### Example: Forward Traceability

**Business Objective:** BO-SEC-001 - Protect sensitive customer data from unauthorized access

↓ drives ↓

**Requirements:**
- REQ-FR-AUTH-001: User authentication with email/password
- REQ-FR-AUTH-002: Password reset flow
- REQ-NFR-SEC-001: Password encryption with bcrypt
- REQ-NFR-SEC-002: Account lockout after 5 failed attempts

↓ implemented by ↓

**Design Specifications:**
- ARCH-AUTH-001: Authentication service architecture
- DESIGN-UI-LOGIN: Login screen wireframes

↓ coded in ↓

**Implementation:**
- src/services/auth/authentication_service.py
- src/api/routes/auth_routes.py
- src/ui/components/LoginForm.tsx

↓ verified by ↓

**Test Cases:**
- TC-AUTH-001: Valid login credentials
- TC-AUTH-002: Invalid password
- TC-AUTH-003: Account lockout after 5 attempts
- TC-AUTH-004: Password reset email sent
```

### Impact Analysis Matrix

When requirements change, use traceability to assess impact:

```markdown
### Change Impact Analysis: REQ-FR-AUTH-001

**Proposed Change:** Add biometric authentication option

**Impact Assessment:**

**Requirements Impacted:**
- REQ-FR-AUTH-001: Update to include biometric option
- NEW: REQ-FR-AUTH-008: Biometric enrollment flow
- NEW: REQ-NFR-SEC-010: Biometric data encryption

**Design Changes Required:**
- ARCH-AUTH-001: Update authentication flow diagram
- DESIGN-UI-LOGIN: Add biometric option to login screen
- NEW: DESIGN-UI-BIOMETRIC: Biometric enrollment UI

**Implementation Effort:**
- Estimated: 40 hours (2 weeks)
- Files affected: 8 files
- New dependencies: FaceID SDK, TouchID SDK

**Test Cases Impacted:**
- TC-AUTH-001: Update to include biometric path
- NEW: TC-AUTH-020 through TC-AUTH-025: Biometric test scenarios

**Risks:**
- Cross-platform compatibility (iOS vs Android)
- Biometric SDK licensing costs
- User adoption (older devices without biometric sensors)

**Recommendation:** Approve with phased rollout (iOS first, Android in Q2)
```

---

## Validation and Verification

### Validation vs Verification

- **Validation:** Are we building the RIGHT thing? (Does it meet business needs?)
- **Verification:** Are we building the thing RIGHT? (Does it meet specifications?)

### Validation Activities

**1. Stakeholder Review Sessions**
```markdown
### Validation Session: BRD Review

**Date:** 2025-01-25
**Attendees:** Product Owner, Business Analyst, 3 Key Stakeholders, Tech Lead

**Agenda:**
1. Review executive summary and business objectives
2. Walk through functional requirements
3. Review use cases and user stories
4. Validate acceptance criteria
5. Confirm priorities and effort estimates

**Outcomes:**
- [x] Business objectives accurately reflect strategic goals
- [x] Functional requirements complete and unambiguous
- [x] Acceptance criteria measurable and testable
- [ ] Performance requirements need clarification (Action: BA to follow up)
- [x] Stakeholders approve proceeding to implementation planning

**Approval Signatures:**
- Jane Smith, Product Owner - Approved 2025-01-25
- Bob Johnson, VP Engineering - Approved 2025-01-25
- Sara Lee, Finance Director - Approved 2025-01-26
```

**2. Requirements Inspection Checklist**
```markdown
### BRD Quality Checklist

**Completeness:**
- [ ] All required sections present
- [ ] All requirements have unique IDs
- [ ] All requirements have priorities assigned
- [ ] All requirements have acceptance criteria
- [ ] Traceability matrix complete

**Clarity:**
- [ ] Requirements use SHALL/SHOULD/MAY consistently
- [ ] No ambiguous terms (e.g., "fast", "user-friendly")
- [ ] Technical terms defined in glossary
- [ ] All acronyms spelled out on first use

**Consistency:**
- [ ] No contradicting requirements
- [ ] Terminology consistent throughout
- [ ] Priorities aligned with business objectives

**Testability:**
- [ ] All requirements verifiable through testing
- [ ] Acceptance criteria are measurable
- [ ] Success metrics defined

**Feasibility:**
- [ ] Technical team confirms feasibility
- [ ] Effort estimates reasonable
- [ ] Dependencies identified and manageable
- [ ] Risks assessed and mitigated
```

### Verification Activities

**1. Requirements Review**
- Peer review by another Business Analyst
- Technical review by architect/senior developer
- Compliance review by legal/security teams (if applicable)

**2. Prototype Validation**
- Create mockups or wireframes for UI requirements
- Build proof-of-concept for high-risk technical requirements
- Conduct user testing with prototypes

**3. Test Case Derivation**
- Create test scenarios for each requirement
- Ensure ≥85% test coverage for critical requirements
- Map test cases back to requirements in traceability matrix

**4. Acceptance Test Planning**
```markdown
### Acceptance Test Plan

**Objective:** Verify that implemented features meet all BRD requirements

**Test Approach:**
- Unit testing: Verify individual components (dev team)
- Integration testing: Verify system interactions (QA team)
- User acceptance testing (UAT): Verify business value (stakeholders)

**UAT Test Scenarios:**

**Scenario 1: End-to-End User Registration Flow**
- Preconditions: User has valid email
- Steps: [Detailed steps from UC-001]
- Expected Results: Account created, verification email sent, user logged in
- Pass Criteria: All acceptance criteria from REQ-FR-AUTH-001 met

**Scenario 2: Performance Under Load**
- Preconditions: System deployed to staging environment
- Steps: Run load test with 5,000 concurrent users
- Expected Results: P95 latency <200ms, no errors
- Pass Criteria: All acceptance criteria from REQ-NFR-PERF-001 met

**UAT Schedule:**
- Week 1: Test scenarios 1-5 (Core authentication flows)
- Week 2: Test scenarios 6-10 (Data management features)
- Week 3: Test scenarios 11-15 (Reporting and exports)
- Week 4: Regression testing and defect fixes

**UAT Sign-Off Criteria:**
- [ ] 100% of critical requirements verified
- [ ] ≥95% of high-priority requirements verified
- [ ] All blocking defects resolved
- [ ] Performance benchmarks met
- [ ] Security requirements validated
- [ ] Stakeholders approve for production release
```

---

## BRD Template Usage

### Using the BRD Template

A complete BRD template is provided in `08-project-management/BRD_TEMPLATE.md`.

**Steps to Create a New BRD:**

1. **Copy the template:**
   ```bash
   cp 08-project-management/BRD_TEMPLATE.md docs/plans/[FEATURE_NAME]_BRD.md
   ```

2. **Fill in document control information:**
   - Update title, version, date, author, stakeholders
   - Set initial status to "Draft"

3. **Complete executive summary:**
   - Describe business problem in 2-3 sentences
   - Outline proposed solution
   - Quantify expected business value
   - Provide high-level effort estimate

4. **Document business context:**
   - Research background and current state
   - Align with strategic business objectives
   - Identify market drivers and constraints

5. **Conduct stakeholder analysis:**
   - Identify all affected parties
   - Create RACI matrix

6. **Define scope clearly:**
   - List specific in-scope items
   - Explicitly state out-of-scope items
   - Document assumptions and dependencies

7. **Specify requirements:**
   - Write functional requirements (WHAT system does)
   - Write non-functional requirements (HOW WELL system performs)
   - Assign unique IDs and priorities
   - Define acceptance criteria for each requirement

8. **Perform Geist analysis:**
   - Conduct Ghost analysis (unknowns)
   - Conduct Geyser analysis (forces)
   - Conduct Gist analysis (essence)

9. **Document use cases:**
   - Create user personas
   - Write detailed use case scenarios
   - Convert to user stories for agile teams

10. **Build traceability matrix:**
    - Link requirements to business objectives
    - Map requirements to test cases

11. **Define acceptance criteria:**
    - Write measurable, testable criteria
    - Define performance benchmarks
    - Identify success metrics

12. **Assess risks:**
    - Identify technical and business risks
    - Develop mitigation strategies

13. **Review and validate:**
    - Conduct peer review
    - Stakeholder validation sessions
    - Obtain formal approvals

14. **Maintain version control:**
    - Update change history for all revisions
    - Increment version number appropriately
    - Track approval dates

### BRD File Organization

```
docs/
├── plans/
│   ├── [FEATURE_NAME]_BRD.md          # Business Requirements Document
│   ├── [FEATURE_NAME]_IMPL_PLAN.md    # Implementation Plan (created after BRD)
│   └── [FEATURE_NAME]_TEST_PLAN.md    # Test Plan (derived from BRD)
└── verification/
    ├── [FEATURE_NAME]_traceability.md # Requirements Traceability Matrix
    ├── [FEATURE_NAME]_test_results.md # Test execution results
    └── [FEATURE_NAME]_acceptance.md   # UAT sign-off documentation
```

---

## Best Practices

### DO: Best Practices for BRD Creation

1. **Start with WHY:** Always explain business value and rationale
2. **Be specific and measurable:** Avoid vague terms; use quantifiable metrics
3. **Use consistent terminology:** Create glossary for domain-specific terms
4. **Involve stakeholders early:** Validate assumptions before deep investment
5. **Perform Geist analysis:** Uncover hidden complexities and validate priorities
6. **Link requirements to business objectives:** Maintain traceability
7. **Define clear acceptance criteria:** Make requirements testable
8. **Assess risks proactively:** Identify mitigation strategies early
9. **Version control rigorously:** Track all changes with justification
10. **Review with technical team:** Ensure feasibility before commitment
11. **Keep it concise:** Use appendices for detailed technical specs
12. **Update continuously:** BRD is a living document throughout project lifecycle

### DON'T: Common Anti-Patterns

1. **Don't write implementation details in BRD:** Focus on WHAT and WHY, not HOW
2. **Don't use ambiguous language:** Avoid "fast", "easy", "user-friendly" without metrics
3. **Don't skip Geist analysis:** Ghost/Geyser/Gist uncovers critical issues
4. **Don't mix requirements with design:** Save technical architecture for implementation plan
5. **Don't ignore non-functional requirements:** Performance, security, usability are critical
6. **Don't create requirements in isolation:** Collaborate with stakeholders and technical team
7. **Don't forget traceability:** Every requirement must link to business objective and test case
8. **Don't write untestable requirements:** Acceptance criteria must be measurable
9. **Don't underestimate effort:** Include buffer for unknowns (Ghost analysis helps)
10. **Don't skip validation sessions:** Stakeholder buy-in prevents costly rework
11. **Don't use BRD as contract weapon:** Foster collaboration, not adversarial relationships
12. **Don't let BRD become stale:** Update as project evolves and new information emerges

### Quality Indicators for a Good BRD

**A high-quality BRD exhibits:**

✅ **Clarity:** Any stakeholder can understand requirements without interpretation
✅ **Completeness:** No missing information needed for implementation
✅ **Consistency:** No contradictions or conflicting requirements
✅ **Correctness:** Requirements accurately reflect business needs
✅ **Traceability:** Clear links from business objectives → requirements → tests
✅ **Testability:** All requirements have measurable acceptance criteria
✅ **Feasibility:** Technical team confirms requirements are achievable
✅ **Prioritization:** Clear distinction between must-haves and nice-to-haves (Gist analysis)
✅ **Risk awareness:** Potential issues identified with mitigation plans
✅ **Stakeholder alignment:** All key stakeholders reviewed and approved

### BRD Review Checklist

Use this checklist before submitting BRD for approval:

```markdown
## BRD Quality Assurance Checklist

### Document Structure
- [ ] All required sections present and complete
- [ ] Document control information filled out
- [ ] Change history tracked
- [ ] Version number follows semantic versioning

### Executive Summary
- [ ] Business problem clearly stated (2-3 sentences)
- [ ] Proposed solution described at high level
- [ ] Business value quantified with metrics
- [ ] Effort estimate provided (high-level)
- [ ] Success metrics defined (3-5 KPIs)

### Business Context
- [ ] Background explains current state and need for change
- [ ] Strategic alignment with business objectives documented
- [ ] Market drivers and competitive landscape addressed
- [ ] Constraints (budget, timeline, technical, regulatory) identified

### Stakeholder Analysis
- [ ] Primary and secondary stakeholders identified
- [ ] RACI matrix created and reviewed with stakeholders
- [ ] Roles and responsibilities clearly defined

### Scope Definition
- [ ] In-scope items specifically listed
- [ ] Out-of-scope items explicitly stated
- [ ] Assumptions documented
- [ ] Dependencies on external systems/teams identified

### Requirements Specification
- [ ] All requirements have unique IDs (REQ-XX-XXX-###)
- [ ] Priorities assigned (Critical/High/Medium/Low)
- [ ] SHALL/SHOULD/MAY language used consistently
- [ ] Rationale (WHY) provided for each requirement
- [ ] Acceptance criteria defined and testable
- [ ] Dependencies between requirements documented
- [ ] Functional requirements cover all in-scope features
- [ ] Non-functional requirements address performance, security, usability, etc.

### Geist Analysis
- [ ] Ghost analysis identifies unknown unknowns and assumptions
- [ ] Geyser analysis identifies forces, pressures, and constraints
- [ ] Gist analysis distills essential core from nice-to-haves
- [ ] Each requirement tagged with Geist classification

### Use Cases
- [ ] User personas created for primary users (3-5 personas)
- [ ] Use case scenarios documented with preconditions, main flow, alternatives, exceptions
- [ ] User stories created in agile format (As a... I want... So that...)
- [ ] Acceptance criteria for each user story

### Traceability Matrix
- [ ] Requirements linked to business objectives
- [ ] Requirements mapped to test cases
- [ ] Forward and backward traceability demonstrated

### Acceptance Criteria
- [ ] Measurable, testable criteria defined for feature acceptance
- [ ] Success scenarios and edge cases covered
- [ ] Performance benchmarks specified

### Risk Assessment
- [ ] Technical risks identified and assessed
- [ ] Business risks identified and assessed
- [ ] Mitigation strategies defined for high-priority risks

### Validation
- [ ] Peer review completed by another BA or technical writer
- [ ] Technical review completed by architect or senior developer
- [ ] Stakeholder validation sessions conducted
- [ ] All feedback incorporated and change history updated

### Language and Style
- [ ] No ambiguous or vague terms (e.g., "fast", "user-friendly")
- [ ] Technical terms defined in glossary
- [ ] Consistent terminology throughout document
- [ ] Acronyms spelled out on first use
- [ ] Active voice used for requirements (system SHALL...)

### Completeness
- [ ] No TBD or placeholder sections remain
- [ ] All questions resolved or documented as risks
- [ ] Appendices include glossary, references, supporting documents

### Approvals
- [ ] All required approvers identified
- [ ] Approval signatures and dates recorded
- [ ] BRD status updated to "Approved" after all sign-offs

### Integration with Development Workflow
- [ ] BRD approved before implementation planning begins
- [ ] Requirements ready for Geist analysis in implementation planning
- [ ] Test cases can be derived directly from requirements
- [ ] Traceability supports TDD workflow

**Final Check:**
- [ ] BRD meets all quality indicators (clarity, completeness, consistency, etc.)
- [ ] Document is ready for implementation planning phase
- [ ] All stakeholders confirm understanding and agreement

**Reviewer Name:** _________________________
**Review Date:** _________________________
**Status:** [ ] Approved  [ ] Approved with Minor Changes  [ ] Needs Revision
```

---

## Integration with Development Workflow

### BRD → Implementation Workflow

```
1. BRD Creation and Approval
   ├─ Stakeholder interviews and requirements gathering
   ├─ Geist analysis (Ghost/Geyser/Gist)
   ├─ Requirements specification
   ├─ Use case documentation
   ├─ Validation sessions
   └─ Formal approval

2. Implementation Planning (After BRD Approval)
   ├─ Read BRD and extract requirements
   ├─ Conduct technical Geist analysis
   ├─ Create architecture design
   ├─ Define TDD approach (test-first)
   ├─ Create implementation plan (<65k chars, use template)
   └─ Review and approval

3. TDD Implementation (Red-Green-Refactor)
   ├─ Write failing tests based on BRD acceptance criteria (RED)
   ├─ Implement minimum code to pass tests (GREEN)
   ├─ Refactor for quality and maintainability (REFACTOR)
   ├─ Validate against BRD requirements
   └─ Update traceability matrix

4. Quality Assurance & Validation
   ├─ Integration testing (≥85% coverage)
   ├─ Performance benchmarking (meet NFRs)
   ├─ Security validation
   ├─ UI/UX testing (ui-bar-raiser agent)
   └─ Gap analysis (identify incomplete implementations)

5. User Acceptance Testing (UAT)
   ├─ Execute UAT scenarios from BRD
   ├─ Verify acceptance criteria met
   ├─ Stakeholder sign-off
   └─ Production release approval

6. Documentation & Traceability
   ├─ Update traceability matrix
   ├─ Document test results
   ├─ Record acceptance sign-offs
   └─ Archive BRD and related artifacts
```

### BRD and TDD Integration

**Test-Driven Development starts with BRD acceptance criteria:**

```markdown
### BRD Requirement:
**[REQ-FR-CALC-001]:** Invoice Total Calculation

**Acceptance Criteria:**
- [ ] System calculates invoice total as sum of line items
- [ ] System applies tax rate based on customer location
- [ ] System rounds total to 2 decimal places
- [ ] System handles empty invoice (total = $0.00)

### TDD Implementation:

**RED Phase (Write Failing Tests):**
```python
def test_invoice_total_with_line_items():
    """Test invoice total calculation matches BRD REQ-FR-CALC-001."""
    invoice = Invoice()
    invoice.add_line_item(amount=100.00)
    invoice.add_line_item(amount=50.00)

    assert invoice.calculate_total() == 150.00  # FAILS - not implemented yet

def test_invoice_applies_tax_by_location():
    """Test tax calculation based on location (REQ-FR-CALC-001)."""
    invoice = Invoice(customer_state="CA")  # CA has 9.5% tax
    invoice.add_line_item(amount=100.00)

    expected_total = 100.00 * 1.095  # $109.50
    assert invoice.calculate_total() == expected_total  # FAILS

def test_invoice_rounds_to_two_decimals():
    """Test rounding to 2 decimal places (REQ-FR-CALC-001)."""
    invoice = Invoice()
    invoice.add_line_item(amount=10.005)  # Would round to 10.01

    assert invoice.calculate_total() == 10.01  # FAILS
```

**GREEN Phase (Minimal Implementation):**
```python
class Invoice:
    def __init__(self, customer_state=None):
        self.line_items = []
        self.customer_state = customer_state
        self.tax_rates = {"CA": 0.095, "NY": 0.08}  # Simplified

    def add_line_item(self, amount: float):
        self.line_items.append(amount)

    def calculate_total(self) -> float:
        subtotal = sum(self.line_items)
        tax_rate = self.tax_rates.get(self.customer_state, 0.0)
        total = subtotal * (1 + tax_rate)
        return round(total, 2)  # Round to 2 decimals
```

**REFACTOR Phase (Improve Quality):**
```python
class Invoice:
    """Calculate invoice totals per BRD REQ-FR-CALC-001."""

    TAX_RATES = {
        "CA": Decimal("0.095"),
        "NY": Decimal("0.08"),
        # ... other states
    }

    def __init__(self, customer_state: Optional[str] = None):
        self.line_items: List[Decimal] = []
        self.customer_state = customer_state

    def add_line_item(self, amount: Union[float, Decimal]) -> None:
        """Add line item to invoice."""
        self.line_items.append(Decimal(str(amount)))

    def calculate_total(self) -> Decimal:
        """Calculate total with tax, rounded to 2 decimal places.

        Implements BRD REQ-FR-CALC-001 acceptance criteria.
        """
        subtotal = sum(self.line_items)
        tax_rate = self.TAX_RATES.get(self.customer_state, Decimal("0.0"))
        total = subtotal * (Decimal("1.0") + tax_rate)
        return total.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
```

**Traceability Update:**
```markdown
| Req ID | Requirement | Test Case | Implementation | Status |
|--------|------------|-----------|----------------|--------|
| REQ-FR-CALC-001 | Invoice total calculation | TC-CALC-001, TC-CALC-002, TC-CALC-003 | src/invoicing/invoice.py:42 | Verified |
```
```

### BRD and Sub-Agent Coordination

**When using sub-agents for implementation:**

1. **requirements-analyzer sub-agent** reads BRD
   - Extracts all requirements and acceptance criteria
   - Creates structured requirements list for implementation

2. **geist-analyzer sub-agent** performs deep analysis
   - Validates Ghost/Geyser/Gist from BRD
   - Identifies implementation risks and gaps

3. **tdd-implementor sub-agent** implements with tests
   - Derives test cases from BRD acceptance criteria
   - Follows RED-GREEN-REFACTOR cycle
   - Updates traceability matrix

4. **gap-analyzer sub-agent** validates completeness
   - Compares implementation to BRD requirements
   - Identifies missing or partial implementations
   - Ensures all acceptance criteria met

5. **exactly-right sub-agent** final validation
   - Zero-defect audit against BRD requirements
   - Production-readiness checklist
   - Sign-off before release

---

## Conclusion

A well-crafted Business Requirements Document is the foundation for successful software delivery. By following these guidelines and integrating Geist-driven analysis, you ensure that:

1. **Business value is clear:** Every requirement traces back to business objectives
2. **Scope is managed:** In-scope and out-of-scope items are explicit
3. **Quality is testable:** Acceptance criteria enable TDD and validation
4. **Risks are mitigated:** Ghost/Geyser/Gist analysis uncovers hidden complexities
5. **Stakeholders are aligned:** Formal validation and approval processes
6. **Traceability is maintained:** Requirements → Design → Implementation → Tests

**Remember:** The BRD is not a one-time document. It's a living artifact that evolves as the project progresses and new information emerges. Update it continuously, maintain version control, and use it as the single source of truth for what you're building and why.

**Next Steps After BRD Approval:**
1. Create Implementation Plan (use `docs/MARKDOWN_PLAN_TEMPLATE.md`)
2. Conduct technical Geist analysis for architecture decisions
3. Derive test cases from BRD acceptance criteria
4. Begin TDD implementation (RED-GREEN-REFACTOR)
5. Validate against BRD throughout development
6. Conduct UAT with stakeholders
7. Obtain final acceptance sign-off

For template and examples, see:
- **BRD Template:** `08-project-management/BRD_TEMPLATE.md`
- **Implementation Plan Template:** `docs/MARKDOWN_PLAN_TEMPLATE.md`
- **Geist Analysis Guide:** `07-geist-framework/` (if exists)
- **TDD Workflow:** `03-development-workflow/tdd/TDD_WORKFLOW_GUIDE.md`
- **Traceability Matrix Examples:** `docs/verification/*_traceability.md`

---

**Document Version:** 1.0
**Last Updated:** 2025-01-19
**Author:** Software Development Best Practices Guide
**Status:** Active
