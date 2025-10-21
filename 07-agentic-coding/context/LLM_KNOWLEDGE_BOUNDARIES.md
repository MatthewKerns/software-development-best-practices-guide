# LLM Knowledge Boundaries: What to Provide vs What to Assume

**Version:** 1.0.0
**Last Updated:** 2025-10-21
**Status:** Active
**Audience:** Developers using LLM assistants for coding tasks

## Executive Summary

Large Language Models (LLMs) like Claude possess extensive knowledge from training on vast corpora of text, including programming documentation, code repositories, and technical discussions. However, they have critical knowledge boundaries that developers must understand to work effectively with them. This guide explains what LLMs know from training, what they cannot know, and how to strategically fill knowledge gaps for optimal collaboration.

**Key Principle:** LLMs excel at reasoning over provided information but cannot retrieve specifics about your codebase, runtime state, or recent developments. Assume they know general programming concepts; always provide your specific context, requirements, and constraints.

**Cross-References:**
- `WHAT_IS_AN_LLM.md` - Foundation for understanding how training shapes knowledge
- `CONTEXT_GAP_INVESTIGATION.md` - Techniques for identifying missing information
- `EVOLVING_CAPABILITIES.md` - How knowledge boundaries shift over time

---

## 1. What LLMs Know from Training

LLMs are trained on massive datasets containing billions of tokens from diverse sources. This training provides broad but shallow knowledge across many domains, with deeper knowledge in well-documented areas.

### 1.1 General Programming Knowledge

**Common Languages and Syntax**

LLMs have strong knowledge of popular programming languages and their syntax:

- **High Proficiency**: Python, JavaScript/TypeScript, Java, C#, C++, Go, Rust, SQL, HTML/CSS
- **Moderate Proficiency**: Ruby, PHP, Swift, Kotlin, Scala, R, Julia, Shell scripting
- **Basic Proficiency**: Obscure languages, legacy systems (COBOL, Fortran), domain-specific languages

**What This Means:**
- You don't need to explain basic syntax: loops, conditionals, function definitions, class structures
- You can assume knowledge of language-specific idioms (Python list comprehensions, JavaScript promises, Go channels)
- You should still provide context for obscure language features or version-specific changes

**Example - No Explanation Needed:**
```python
# LLM knows this pattern without explanation
async def fetch_data(url: str) -> dict:
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            return await response.json()
```

**Example - Explanation Required:**
```python
# LLM needs context for your custom decorator
@retry_with_exponential_backoff(max_attempts=5, base_delay=2.0)
@require_authenticated_session(role="admin")
async def fetch_sensitive_data(url: str) -> dict:
    # What do these decorators do? Provide documentation or implementation
    ...
```

**Standard Libraries and Frameworks**

LLMs have comprehensive knowledge of popular libraries and frameworks:

- **Excellent Coverage**: React, Node.js, Django, Flask, FastAPI, Express, Spring Boot, ASP.NET Core
- **Good Coverage**: Less popular but well-documented frameworks (Svelte, Vue, Angular, Laravel)
- **Limited Coverage**: Internal company frameworks, custom tooling, recent framework versions post-training

**What This Means:**
- No need to explain React hooks, Express middleware, or Django ORM basics
- You can reference common patterns (REST APIs, authentication flows, database migrations) without detailed explanation
- You must provide documentation for internal frameworks or customizations

**Design Patterns and Algorithms**

LLMs understand classic computer science concepts:

- **Design Patterns**: Singleton, Factory, Observer, Strategy, Dependency Injection, Repository Pattern
- **Algorithms**: Sorting, searching, graph traversal, dynamic programming, common optimizations
- **Architecture Patterns**: MVC, MVVM, Microservices, Event-Driven, CQRS, Clean Architecture
- **Data Structures**: Arrays, linked lists, trees, graphs, hash tables, heaps, tries

**What This Means:**
- You can ask "implement the Strategy pattern for payment processing" without defining the pattern
- You don't need to explain Big-O notation or common algorithm trade-offs
- You should clarify domain-specific variations (e.g., "our Factory pattern includes audit logging")

### 1.2 Public Information

**Open-Source Patterns and Best Practices**

LLMs have absorbed patterns from millions of open-source repositories:

- **Common Code Patterns**: Error handling, logging, configuration management, testing strategies
- **API Design**: RESTful conventions, GraphQL schemas, gRPC service definitions
- **DevOps Practices**: CI/CD pipelines, containerization, infrastructure as code
- **Security Patterns**: Authentication/authorization, input validation, encryption, OWASP top 10

**Example - Known Pattern:**
```typescript
// LLM recognizes this as standard Express middleware pattern
app.use((req, res, next) => {
  console.log(`${req.method} ${req.path}`);
  next();
});
```

**Example - Needs Context:**
```typescript
// Your custom middleware needs explanation
app.use(trackUserJourney); // What does this do? How is it configured?
```

**Popular Library Documentation**

LLMs have extensive knowledge from official documentation, tutorials, and community resources:

- **Well-Documented Libraries**: NumPy, Pandas, TensorFlow, PyTorch, Lodash, Axios, Jest, Pytest
- **Framework Documentation**: Next.js, Create React App, Django Rest Framework, Spring Security
- **Tool Documentation**: Git, Docker, Kubernetes, Terraform, GitHub Actions

**What This Means:**
- You can reference standard library functions without explaining them
- You can assume knowledge of common configuration options (webpack config basics, pytest.ini settings)
- You must provide details for non-standard configurations or plugins

**Common Errors and Solutions**

LLMs have learned from Stack Overflow, GitHub issues, and debugging discussions:

- **Recognizable Errors**: "Cannot read property 'x' of undefined", "CORS error", "database connection refused"
- **Common Fixes**: Adding null checks, configuring CORS headers, checking connection strings
- **Debugging Patterns**: Using console.log, debugger statements, logging frameworks

**What This Means:**
- LLMs can suggest solutions to common error messages
- They understand typical debugging workflows
- They may not know about errors specific to your custom tooling or infrastructure

### 1.3 Training Data Limitations

**Training Cutoff Date**

Every LLM has a knowledge cutoff date beyond which it has no information:

- **Claude Sonnet 4.5 (2025-01-29)**: Knowledge cutoff is January 2025
- **Impact**: No knowledge of libraries released after cutoff, new language features, recent security vulnerabilities
- **Mitigation**: Always provide current documentation for recently updated dependencies

**Geographic and Language Biases**

Training data is not uniformly distributed:

- **English Dominance**: Most training data is in English; non-English documentation may be less represented
- **Western Bias**: More data from North America and Europe than other regions
- **Popular vs Niche**: Well-known technologies over-represented compared to niche tools

**What This Means:**
- Provide documentation for non-English projects or region-specific tools
- Explain domain-specific terminology that may not be widely documented online
- Verify assumptions when working with less common technologies

---

## 2. What LLMs Cannot Know

Understanding what LLMs definitively cannot know is crucial for effective collaboration. These are hard boundaries that no amount of training can overcome.

### 2.1 Your Codebase Specifics

**Custom Business Logic**

LLMs have zero knowledge of your proprietary algorithms, domain rules, or business workflows:

- **Business Rules**: "Users with premium tier get 3x rewards" - LLM cannot infer this
- **Domain Models**: Your entity relationships, state machines, workflow orchestration
- **Calculation Logic**: Pricing algorithms, tax calculations, commission structures
- **Integration Contracts**: How your systems communicate with partners

**Example - Must Provide:**
```python
# LLM needs context for your business logic
def calculate_invoice_total(invoice: Invoice) -> Decimal:
    """
    Calculate invoice total with business rules:
    - Materials cost + labor cost + overhead (15% of materials)
    - Discount: 10% for orders >$10k, 5% for repeat customers
    - Sales tax: 8.5% in California, 6% elsewhere
    - Rush fee: +25% if delivery <7 days
    """
    # LLM can implement this AFTER you explain the rules
    ...
```

**Internal APIs and Schemas**

Your API contracts, database schemas, and data models are invisible to LLMs:

- **API Endpoints**: `/api/v2/internal/analytics/user-journey` - LLM doesn't know this exists
- **Request/Response Schemas**: What fields are required? What types? What validation rules?
- **Database Tables**: Table names, column types, foreign keys, indexes, constraints
- **Internal Data Formats**: Custom serialization, proprietary protocols, internal message formats

**Decision Framework:**
- ✅ Assume: REST principles, JSON structure, SQL query syntax
- ❌ Assume: Your endpoint paths, your field names, your database schema

**Undocumented Conventions**

Team-specific practices, coding standards, and implicit knowledge:

- **Naming Conventions**: `_internal` prefix for private methods, `Dto` suffix for data transfer objects
- **File Organization**: Where do services go? Utilities? Configurations?
- **Error Handling**: Do you use exceptions or result types? Custom error codes?
- **Testing Patterns**: Mock vs integration test boundaries, fixture organization

**Example - Needs Documentation:**
```
Our codebase conventions:
- All database operations in `src/data_access/operations/`
- Services follow pattern: ServiceNameService with async methods
- Tests mirror source structure: `tests/unit/` and `tests/integration/`
- Error codes format: `[SERVICE]-[CODE]` (e.g., "AUTH-401", "DB-CONN-001")
```

### 2.2 Runtime Information

**Current File Contents**

LLMs cannot read files unless you explicitly provide them:

- **File System State**: What files exist? What are their contents?
- **Code Changes**: Recent commits, uncommitted modifications, local branches
- **Configuration Files**: `.env` values, `config.yaml` settings, database connection strings

**Critical Rule:** Always read and provide files before asking LLM to modify them. Use Read tool, provide file paths, show relevant sections.

**Example Workflow:**
```
❌ Bad: "Update the UserService to add email validation"
   → LLM doesn't know what UserService contains

✅ Good: "Here's the current UserService code: [content]. Update it to add email validation."
   → LLM can reason about specific implementation
```

**Environment Variables and System Configuration**

LLMs have no access to your runtime environment:

- **Environment Variables**: `DATABASE_URL`, `API_KEY`, `NODE_ENV`
- **System Configuration**: Installed packages, OS version, available memory
- **Deployment Context**: Dev vs staging vs production, cloud provider, region

**What to Provide:**
- Required environment variables and their purpose (not secret values!)
- System requirements and constraints
- Deployment target characteristics

**Database State and Application Data**

LLMs cannot query your database or inspect application state:

- **Current Data**: User records, transaction history, cached values
- **Data Volume**: Table row counts, query performance characteristics
- **Schema Evolution**: Migration history, pending changes, deprecated columns
- **Constraints**: Foreign keys, unique constraints, check constraints

**Example - Provide Context:**
```
Database context for optimization:
- `users` table: 2.5M rows, frequently queried by email (indexed)
- `transactions` table: 50M rows, growing 100k/day, partitioned by month
- `sessions` table: Redis-backed, 1M active sessions at peak
- Query timeout limit: 5 seconds
```

### 2.3 Recent Events Post-Training Cutoff

**New Library Versions and Features**

Any updates after training cutoff are unknown:

- **Breaking Changes**: API redesigns, deprecated methods, migration requirements
- **New Features**: Recently added functions, performance improvements, new patterns
- **Bug Fixes**: Patches for known issues, workarounds that are no longer needed

**Mitigation Strategy:**
- Check LLM's training cutoff date before assuming library knowledge
- Provide changelog excerpts for recently updated dependencies
- Link to current documentation for critical libraries

**Recent Best Practices and Security Advisories**

The field evolves constantly; LLMs lag behind:

- **Security Vulnerabilities**: CVEs discovered after training cutoff
- **Deprecated Patterns**: Practices that were fine but are now considered harmful
- **New Recommendations**: Performance optimizations, updated guidelines

**Example:**
```
# LLM trained before security advisory may suggest vulnerable pattern
# You must provide updated guidance:

"Note: bcrypt with cost <12 is now considered insufficient.
Use cost=12 minimum for new implementations (updated Jan 2025)."
```

**Emerging Technologies**

Technologies that emerged or gained traction after training:

- **New Frameworks**: Recently launched tools or platforms
- **Language Updates**: Features added in recent language versions
- **Platform Changes**: Cloud provider service updates, API changes

**Decision Framework:**
- If technology is >1 year old at training cutoff: Likely good coverage
- If technology is <6 months old at training cutoff: Provide documentation
- If technology is post-training cutoff: Assume zero knowledge

---

## 3. The Retrieval vs Reasoning Distinction

Understanding how LLMs process information reveals why some knowledge gaps matter more than others.

### 3.1 Retrieval: Finding Patterns from Training Data

**How Retrieval Works**

LLMs don't have perfect recall; they reconstruct knowledge from statistical patterns:

- **Pattern Matching**: Recognizing similar contexts in training data
- **Probabilistic Recall**: More common patterns recalled more accurately
- **Compression Artifacts**: Details may be lost or confused in training compression
- **Hallucination Risk**: When retrieval fails, LLMs may "confabulate" plausible-sounding but incorrect information

**Retrieval Strengths:**
- Common programming patterns (seen thousands of times in training)
- Well-documented libraries (extensive training examples)
- Standard algorithms (canonical implementations widely available)

**Retrieval Weaknesses:**
- Rare patterns (few training examples)
- Specific version details (training data mixed across versions)
- Precise API signatures (compressed representation loses exactness)

**Example - Strong Retrieval:**
```python
# LLM reliably retrieves this common pattern
def quicksort(arr):
    if len(arr) <= 1:
        return arr
    pivot = arr[len(arr) // 2]
    left = [x for x in arr if x < pivot]
    middle = [x for x in arr if x == pivot]
    right = [x for x in arr if x > pivot]
    return quicksort(left) + middle + quicksort(right)
```

**Example - Weak Retrieval:**
```python
# LLM may misremember specific parameter names or defaults
# Better to provide exact signature:
asyncpg.create_pool(
    dsn=None,
    *,
    min_size=10,      # Provide exact defaults
    max_size=10,      # Not "around 10"
    max_queries=50000,
    max_inactive_connection_lifetime=300.0,
    # ... other parameters
)
```

### 3.2 Reasoning: Applying Logic to New Situations

**How Reasoning Works**

LLMs excel at applying general principles to specific contexts:

- **Logical Inference**: Deriving conclusions from provided premises
- **Pattern Application**: Adapting known patterns to new requirements
- **Constraint Satisfaction**: Balancing multiple requirements simultaneously
- **Creative Combination**: Merging techniques in novel ways

**Reasoning Strengths:**
- Applying design patterns to your specific use case
- Adapting general algorithms to domain constraints
- Combining multiple techniques to solve complex problems
- Identifying trade-offs between competing requirements

**Example - Strong Reasoning:**
```
Prompt: "I have a user table with 10M rows. I need to find users who haven't
logged in for 90 days, but the query times out. How can I optimize this?"

LLM Reasoning Process:
1. Understands: Large table + time-based query + performance problem
2. Applies: Indexing knowledge, query optimization patterns
3. Considers: Batch processing, materialized views, archival strategies
4. Adapts: Recommendations specific to 10M row scale and 90-day timeframe
5. Suggests: Index on last_login, incremental approach, potential archival

No retrieval of your exact problem needed - reasoning over general principles.
```

### 3.3 Strategic Implications: Provide Specifics, Let LLM Reason

**Optimal Collaboration Pattern**

The most effective way to work with LLMs:

1. **You Provide**: Specific requirements, constraints, context, data about your system
2. **LLM Reasons**: Applies general knowledge to your specific situation
3. **You Validate**: Check reasoning against domain knowledge, test solutions

**Example Workflow:**
```
❌ Suboptimal:
"How do I optimize database queries?"
→ LLM retrieves generic advice (add indexes, use EXPLAIN, etc.)
→ May not apply to your specific situation

✅ Optimal:
"I have a PostgreSQL database with a 50M row transactions table.
Queries filtering by user_id + date_range take 15 seconds.
Current indexes: user_id (btree), created_at (btree).
Query pattern: SELECT * FROM transactions WHERE user_id = $1
AND created_at BETWEEN $2 AND $3 ORDER BY created_at DESC LIMIT 100.
How can I optimize this?"

→ LLM reasons about:
  - Composite index benefits (user_id, created_at)
  - Index-only scan potential
  - LIMIT optimization
  - Partitioning considerations for 50M rows
→ Specific, actionable recommendations for YOUR situation
```

**Why This Works Better:**

- **Reduces Hallucination**: Reasoning over provided facts vs retrieving uncertain details
- **Increases Relevance**: Solutions tailored to your constraints
- **Improves Accuracy**: LLMs better at logical deduction than perfect recall
- **Enables Validation**: You can verify reasoning logic more easily than check retrieved facts

---

## 4. Domain-Specific Knowledge Gaps

Different domains have unique knowledge boundaries that affect LLM effectiveness.

### 4.1 Industry-Specific Regulations and Standards

**Healthcare (HIPAA, HL7, FHIR)**

LLMs have general knowledge of healthcare regulations but lack specifics:

- **Know**: HIPAA exists, general privacy concepts, need for encryption
- **Don't Know**: Your specific HIPAA compliance requirements, Business Associate Agreements, audit procedures
- **Must Provide**: Specific compliance requirements, data classification levels, audit trail requirements

**Example - Provide Context:**
```
Healthcare compliance requirements for this feature:
- PHI data must be encrypted at rest (AES-256) and in transit (TLS 1.3)
- Access logs must retain: user, timestamp, action, resource, IP for 7 years
- Patient consent required before any data sharing
- Right to delete: Full data removal within 30 days of request
- Audit trail: Immutable log of all PHI access (who, when, what)
```

**Finance (PCI-DSS, SOX, AML)**

Financial regulations are complex and jurisdiction-dependent:

- **Know**: General concepts of payment security, data protection
- **Don't Know**: Your PCI-DSS scope, specific compliance level, auditor requirements
- **Must Provide**: Card data handling rules, tokenization requirements, audit scope

**Legal and Jurisdictional Rules**

Laws vary by country, state, and industry:

- **Know**: GDPR exists, general data protection principles
- **Don't Know**: Which jurisdictions your users are in, specific consent requirements, right-to-deletion workflows
- **Must Provide**: Applicable jurisdictions, specific legal requirements, data residency rules

### 4.2 Company-Specific Tools and Practices

**Internal Tools and Platforms**

Every company builds proprietary tooling:

- **Deployment Systems**: Custom CI/CD, internal Kubernetes setup, proprietary cloud
- **Monitoring and Observability**: Internal dashboards, custom metrics, alerting systems
- **Development Tools**: Code generators, testing frameworks, local development environments

**Example - Document Internal Tools:**
```
Internal tooling context:
- Deployment: Use `ship-it deploy --env staging --service user-api`
- Monitoring: Metrics in DataDog under namespace `prod.user-api.*`
- Logs: Centralized in Splunk, query: `index=prod service=user-api`
- Testing: Run `make test-integration` (spins up local Docker containers)
- Database migrations: `alembic upgrade head` (auto-run in CD pipeline)
```

**Team Conventions and Standards**

Implicit knowledge that team members share:

- **Code Review Standards**: What reviewers look for, approval requirements
- **Git Workflow**: Branch naming, commit message format, merge vs rebase
- **Documentation Expectations**: When to update docs, where to put them
- **On-Call Procedures**: Who to notify, escalation paths, incident response

**Example - Share Team Practices:**
```
Team conventions:
- Branch naming: feature/JIRA-123-short-description
- Commits: Conventional Commits format (feat:, fix:, docs:, etc.)
- PRs require: 2 approvals, passing CI, updated CHANGELOG.md
- Tests: 85% coverage minimum, integration tests for all API endpoints
- Docs: Update docs/ folder + inline docstrings for public APIs
```

**Tribal Knowledge**

Undocumented wisdom accumulated over time:

- **Known Issues**: "The cache invalidation sometimes fails on Tuesdays" (why?)
- **Workarounds**: "Always restart the worker after deploying API changes"
- **Historical Context**: "We chose MongoDB because of the 2019 scaling issues"

**Mitigation:** Document tribal knowledge when you encounter it. LLMs can help structure and formalize this documentation.

---

## 5. How to Fill Knowledge Gaps

Strategic approaches to providing LLMs with information they need while avoiding unnecessary explanation.

### 5.1 Assume LLM Knows (Safe Assumptions)

**Common Programming Patterns**

- **Data Structures**: Arrays, objects, maps, sets, lists
- **Control Flow**: Loops, conditionals, error handling
- **Functions**: Parameters, return values, closures, callbacks
- **OOP Concepts**: Classes, inheritance, interfaces, polymorphism
- **Async Patterns**: Promises, async/await, callbacks, event loops

**Popular Libraries (Well-Documented)**

- **Web Frameworks**: Express, Flask, Django, React, Vue, Angular
- **Databases**: PostgreSQL, MySQL, MongoDB, Redis
- **Testing**: Jest, Pytest, JUnit, Mocha
- **Utilities**: Lodash, Pandas, NumPy, Requests

**Standard Development Practices**

- **Version Control**: Git basics (commit, branch, merge, pull request)
- **Testing Concepts**: Unit tests, integration tests, mocks, fixtures
- **CI/CD Fundamentals**: Build pipelines, automated testing, deployment stages
- **Containerization**: Docker basics, image building, container orchestration concepts

### 5.2 Always Provide (Critical Context)

**Your Specific Requirements**

Every task needs explicit requirements:

- **Functional Requirements**: What should the feature do? What are the inputs and outputs?
- **Non-Functional Requirements**: Performance targets, security constraints, scalability needs
- **Business Rules**: Domain-specific logic, calculation formulas, validation rules
- **Edge Cases**: Unusual scenarios, error conditions, boundary cases

**Template for Requirements:**
```
Feature: [Name]

Functional Requirements:
- [Specific behavior 1]
- [Specific behavior 2]

Non-Functional Requirements:
- Performance: [target, e.g., <100ms response time]
- Security: [constraints, e.g., require authentication]
- Scalability: [needs, e.g., handle 10k requests/second]

Business Rules:
- [Domain logic 1]
- [Domain logic 2]

Edge Cases:
- [Scenario 1 and expected behavior]
- [Scenario 2 and expected behavior]
```

**Your Constraints and Limitations**

Context that shapes the solution:

- **Technology Stack**: Required languages, frameworks, libraries, versions
- **Infrastructure**: Cloud provider, available services, resource limits
- **Dependencies**: Third-party integrations, internal services, external APIs
- **Time/Budget**: Development timeline, resource availability

**Example:**
```
Constraints:
- Must use Python 3.11+ (deployed on AWS Lambda)
- Database: PostgreSQL 15 (AWS RDS, single instance, 16GB RAM)
- External APIs: Stripe for payments, SendGrid for email
- Performance: P95 response time <200ms
- Budget: Avoid additional infrastructure costs
```

**Your Current State**

Where you are starting from:

- **Existing Code**: Current implementation, recent changes, technical debt
- **Database Schema**: Current tables, relationships, indexes
- **APIs**: Existing endpoints, data models, authentication
- **Tests**: Current coverage, test strategy, known gaps

### 5.3 Test Assumptions (Verification Strategies)

**Ask What LLM Knows**

Before assuming, verify:

```
Examples:
"Are you familiar with LangGraph for workflow orchestration?"
"What do you know about PostgreSQL's LISTEN/NOTIFY feature?"
"Do you have knowledge of Rust's async/await as of version 1.75?"
```

**Provide References When Unsure**

If in doubt, include documentation:

```
"I'm using the @dataclass decorator. Here's the relevant Python documentation: [excerpt]"
"This project uses Poetry for dependency management. Key commands: [list]"
```

**Validate Generated Code**

Always review LLM output for correctness:

- **Run Tests**: Does the code pass your test suite?
- **Check Documentation**: Does it match the official library docs?
- **Review Logic**: Does the reasoning make sense for your domain?
- **Verify Security**: Are there any security implications?

**Iterative Refinement**

Use feedback loops to correct misunderstandings:

```
Iteration 1: "Create a user authentication system"
→ LLM generates generic JWT implementation

Iteration 2: "We use OAuth2 with Google as the provider. Here's our current config: [details]"
→ LLM adapts to specific OAuth2 flow

Iteration 3: "The token refresh isn't handling expired tokens correctly. Here's the error: [error]"
→ LLM fixes specific issue
```

---

## 6. Practical Guidelines

Decision frameworks and checklists for day-to-day LLM collaboration.

### 6.1 The Assumption Matrix

Use this matrix to quickly decide what to assume vs provide:

| Category | Assume LLM Knows | Always Provide |
|----------|------------------|----------------|
| **Language Syntax** | Python, JS, Java basics | Obscure languages, internal DSLs |
| **Libraries** | Popular frameworks (<1 year old at training) | Custom internal libraries, new releases |
| **Algorithms** | Sorting, searching, classic patterns | Your domain-specific algorithms |
| **Architecture** | REST, microservices, MVC | Your service architecture, internal APIs |
| **Database** | SQL syntax, common ORMs | Your schema, business logic, constraints |
| **Security** | OWASP principles, common patterns | Your security model, compliance needs |
| **Business Logic** | General e-commerce, SaaS patterns | Your pricing, rules, workflows |
| **Infrastructure** | Docker, Kubernetes concepts | Your deployment process, cloud setup |
| **Testing** | Unit/integration test concepts | Your test strategy, coverage requirements |
| **Documentation** | Code comment best practices | Your documentation standards, locations |

### 6.2 The Provide vs Assume Checklist

Before starting an LLM conversation, ask yourself:

**✅ What Should I Assume LLM Knows?**
- [ ] Common programming language syntax and idioms
- [ ] Standard library functions for popular languages
- [ ] Well-documented open-source frameworks
- [ ] Classic algorithms and data structures
- [ ] General software design patterns
- [ ] Common development practices (Git, testing, CI/CD concepts)

**❌ What Must I Provide?**
- [ ] Specific requirements and acceptance criteria
- [ ] My current codebase structure and conventions
- [ ] My database schema and business logic
- [ ] My API contracts and integration points
- [ ] My constraints (performance, security, infrastructure)
- [ ] My domain-specific terminology and rules
- [ ] Recent library changes if post-training cutoff
- [ ] Current file contents for modifications

### 6.3 Communication Templates

**Template: Providing Context for New Feature**
```
I need to implement [feature name].

REQUIREMENTS:
- Functional: [what it should do]
- Non-functional: [performance, security, etc.]
- Business rules: [domain logic]

CURRENT STATE:
- Relevant files: [list with brief descriptions]
- Database schema: [relevant tables and relationships]
- Existing APIs: [related endpoints]

CONSTRAINTS:
- Technology: [required stack]
- Performance: [targets]
- Integration: [dependencies]

QUESTIONS:
- [Any specific concerns or areas for LLM to focus on]
```

**Template: Debugging Assistance**
```
I'm encountering [problem description].

ERROR DETAILS:
- Error message: [exact error]
- Stack trace: [relevant portion]
- When it occurs: [reproduction steps]

CONTEXT:
- Relevant code: [code snippet or file]
- Recent changes: [what changed before error appeared]
- Environment: [OS, language version, dependencies]

ATTEMPTED SOLUTIONS:
- [What you've already tried]

What could be causing this, and how can I fix it?
```

**Template: Code Review Request**
```
Please review this code for [specific concerns: performance, security, maintainability].

CODE:
[code snippet]

CONTEXT:
- Purpose: [what this code does]
- Requirements: [what it needs to accomplish]
- Constraints: [any limitations or requirements]

SPECIFIC QUESTIONS:
- [Area 1 you want feedback on]
- [Area 2 you want feedback on]
```

### 6.4 Knowledge Gap Warning Signs

**Hallucination Indicators**

Watch for these signs that LLM is guessing rather than reasoning:

- **Overly Confident About Specifics**: "The API endpoint is definitely `/api/v2/users`" (when it should say "typically")
- **Precise Numbers Without Source**: "This function takes exactly 3.2ms" (without benchmarking)
- **Certain About Your Codebase**: "Your UserService class has a `validateEmail` method" (without seeing the code)
- **Version-Specific Claims**: "In version 2.4.1, the parameter is called `maxRetries`" (too specific for training data compression)

**Response Strategies:**
- Ask for reasoning: "How do you know that?"
- Request alternatives: "What if that's not the case?"
- Verify claims: "Let me check the actual code/documentation"
- Provide corrections: "Actually, in our codebase, it's [correct information]"

**Uncertainty Indicators (Good Signs)**

LLMs should express uncertainty about unknowable things:

- **Hedging Language**: "Typically", "Often", "In standard implementations"
- **Conditional Statements**: "If your API follows REST conventions, then..."
- **Requests for Clarification**: "Could you provide the current schema?"
- **Alternative Suggestions**: "Here are three approaches depending on your constraints"

These indicate the LLM is reasoning appropriately rather than hallucinating specifics.

---

## 7. Domain-Specific Knowledge Boundary Examples

Concrete examples across different domains to illustrate knowledge boundaries.

### 7.1 Web Development

**✅ LLM Knows:**
- React hooks (useState, useEffect, useContext)
- Express middleware pattern
- JWT authentication flow
- CORS configuration
- REST API principles
- Common HTTP status codes
- CSS Flexbox and Grid
- Webpack/Vite bundler concepts

**❌ LLM Doesn't Know:**
- Your component library and design system
- Your API endpoint paths and request/response schemas
- Your authentication flow specifics (OAuth provider, custom claims)
- Your state management structure (Redux store shape, Context providers)
- Your build configuration customizations
- Your deployment pipeline and environment variables
- Your error tracking and monitoring setup

**Example Prompt:**
```
I'm building a user dashboard with our React component library.

CONTEXT:
- Components: Use <Card>, <DataTable>, <Chart> from @company/ui-components
- API: GET /api/v2/user/{id}/dashboard returns { metrics: [], activities: [] }
- Auth: User object in React Context has { id, role, permissions }
- Styling: Tailwind CSS with custom theme in tailwind.config.js

REQUIREMENTS:
- Display metrics in Card grid (responsive: 1 col mobile, 3 col desktop)
- Show activity feed in DataTable (paginated, 20 per page)
- Chart showing metric trends (last 30 days)
- Only show admin metrics if user.role === 'admin'

Can you implement this dashboard component?
```

### 7.2 Data Science and Machine Learning

**✅ LLM Knows:**
- NumPy, Pandas, Scikit-learn basics
- Common ML algorithms (regression, classification, clustering)
- Train/test split, cross-validation concepts
- Overfitting, underfitting, regularization
- Common metrics (accuracy, precision, recall, F1, MSE)
- Data cleaning and preprocessing patterns
- Visualization with Matplotlib, Seaborn

**❌ LLM Doesn't Know:**
- Your dataset structure and domain
- Your feature engineering choices and business logic
- Your model performance requirements
- Your production serving infrastructure
- Your data pipeline and ETL processes
- Your experiment tracking and versioning
- Your specific data quality issues

**Example Prompt:**
```
I need to build a churn prediction model for our SaaS platform.

DATASET:
- Size: 100k users, 45 features
- Target: churned (binary: 0/1), 15% positive class
- Features: user_age_days, login_frequency, feature_usage (JSON), support_tickets, etc.
- Data quality: 5% missing values in login_frequency, support_tickets sometimes null

REQUIREMENTS:
- Model: Binary classification, optimize for recall (catch churners)
- Performance: Minimum 75% recall, acceptable precision >60%
- Interpretability: Need feature importance for business stakeholders
- Production: Model must predict in <50ms

CONSTRAINTS:
- Cannot use deep learning (interpretability requirement)
- Must handle missing values gracefully
- Feature 'feature_usage' is JSON, needs extraction

What approach would you recommend?
```

### 7.3 DevOps and Infrastructure

**✅ LLM Knows:**
- Docker basics (Dockerfile, images, containers)
- Kubernetes concepts (pods, services, deployments)
- CI/CD pipeline principles
- Infrastructure as Code concepts (Terraform, CloudFormation)
- Monitoring and logging principles
- Load balancing and auto-scaling concepts
- Basic AWS/GCP/Azure services

**❌ LLM Doesn't Know:**
- Your infrastructure architecture and topology
- Your deployment process and tooling
- Your monitoring and alerting setup
- Your network configuration and security groups
- Your disaster recovery and backup procedures
- Your cost optimization strategies
- Your compliance and security requirements

**Example Prompt:**
```
I need to deploy a Node.js API to our Kubernetes cluster.

INFRASTRUCTURE:
- Cluster: AWS EKS, 3 availability zones, 10-50 nodes (auto-scaling)
- Namespace: production
- Ingress: NGINX Ingress Controller with cert-manager (Let's Encrypt)
- Monitoring: Prometheus + Grafana
- Logging: Fluentd → CloudWatch Logs

SERVICE REQUIREMENTS:
- API: Node.js 18, PORT 3000, health check at /health
- Resources: 256Mi memory minimum, 1 CPU request, 2 CPU limit
- Scaling: 3-10 replicas based on CPU >70%
- Environment: DATABASE_URL (from Secret), API_KEY (from Secret), NODE_ENV=production
- Persistence: None (stateless)

DEPLOYMENT:
- Rolling update strategy, max unavailable 1, max surge 2
- Liveness probe: /health every 10s
- Readiness probe: /ready every 5s
- Expose: Internal service on port 80, Ingress at api.example.com

Can you create the Kubernetes manifests (Deployment, Service, HPA, Ingress)?
```

### 7.4 Database and Backend Systems

**✅ LLM Knows:**
- SQL syntax and common queries
- Database indexing concepts
- Transactions and ACID properties
- ORM patterns (SQLAlchemy, TypeORM, Prisma)
- Database normalization
- Common database patterns (connection pooling, prepared statements)
- NoSQL concepts (MongoDB, Redis)

**❌ LLM Doesn't Know:**
- Your database schema and relationships
- Your query patterns and performance characteristics
- Your data volume and growth rate
- Your indexing strategy
- Your migration history and procedures
- Your backup and recovery processes
- Your connection management approach

**Example Prompt:**
```
I need to optimize a slow query in our PostgreSQL database.

SCHEMA:
- orders table: 50M rows, 200k inserts/day
  Columns: id (PK), user_id (FK), created_at, status, total_amount
  Indexes: user_id (btree), created_at (btree)

- order_items table: 200M rows, 800k inserts/day
  Columns: id (PK), order_id (FK), product_id (FK), quantity, price
  Indexes: order_id (btree), product_id (btree)

SLOW QUERY:
SELECT o.*, COUNT(oi.id) as item_count, SUM(oi.price * oi.quantity) as total
FROM orders o
JOIN order_items oi ON oi.order_id = o.id
WHERE o.user_id = $1
  AND o.created_at >= NOW() - INTERVAL '90 days'
  AND o.status IN ('completed', 'shipped')
GROUP BY o.id
ORDER BY o.created_at DESC
LIMIT 20;

PERFORMANCE:
- Current: 8-12 seconds
- Target: <500ms
- Query pattern: Called on every user dashboard load (high frequency)

What optimization strategies would you recommend?
```

---

## 8. Testing Strategies for Verifying LLM Knowledge

Systematic approaches to validate what LLMs know and don't know.

### 8.1 Probing Questions

**Direct Knowledge Probes**

Ask explicitly about specific knowledge:

```
"What do you know about the FastAPI BackgroundTasks feature?"
"Are you familiar with PostgreSQL's LISTEN/NOTIFY mechanism?"
"Do you have information about the breaking changes in React 18?"
```

**Assess the response quality:**
- Detailed, accurate description → Likely has good knowledge
- Vague, general response → Limited training data
- Requests for more context → Appropriate uncertainty
- Overly confident but incorrect → Hallucination warning

**Boundary Probing**

Test the edges of knowledge:

```
"What was added in Python 3.11?" (Check if post-training cutoff)
"What are the differences between FastAPI v0.95 and v0.100?" (Version-specific details)
"How does [obscure library] handle [specific feature]?" (Niche knowledge test)
```

**Expected responses:**
- Within knowledge: Detailed, confident answers
- At boundary: Hedged language, requests for docs
- Beyond boundary: Clear statement of uncertainty or knowledge cutoff

### 8.2 Validation Workflows

**Three-Stage Verification**

1. **Generate**: Ask LLM to produce code/solution
2. **Explain**: Ask LLM to explain its reasoning
3. **Validate**: Check against documentation/tests

**Example:**
```
Stage 1 - Generate:
"Create a function to hash passwords using bcrypt in Python"

Stage 2 - Explain:
"Why did you choose those bcrypt parameters? What do they mean?"

Stage 3 - Validate:
- Check bcrypt documentation for correct API
- Verify cost factor recommendation is current
- Test with actual bcrypt library
```

**Comparative Validation**

Ask for multiple approaches and compare:

```
"What are three different ways to implement rate limiting in Express?"

Then for each approach:
- Research actual implementations
- Check community recommendations
- Test in your environment
- Assess which best fits your constraints
```

### 8.3 Feedback Loops

**Correction Protocol**

When LLM makes an error, provide explicit correction:

```
LLM: "Use the `asyncpg.connect()` method with the `max_connections` parameter"

You: "Actually, `asyncpg.connect()` creates a single connection.
The `create_pool()` method is what accepts `max_size` (not `max_connections`).
Here's the correct signature: [paste from docs]"

LLM: [Adjusts approach with correct information]
```

**Iterative Refinement**

Use multiple rounds to converge on correct solution:

```
Round 1: High-level approach (tests LLM's general reasoning)
Round 2: Specific implementation (provide your context)
Round 3: Edge cases and error handling (provide failure scenarios)
Round 4: Optimization and best practices (provide constraints)
```

Each round builds on previous knowledge and corrects misunderstandings.

---

## 9. Cross-References and Further Reading

### 9.1 Related Guides in This Repository

**Foundation:**
- `WHAT_IS_AN_LLM.md` - Understanding how training shapes knowledge boundaries
- `EVOLVING_CAPABILITIES.md` - How knowledge boundaries shift with new models

**Practical Application:**
- `CONTEXT_GAP_INVESTIGATION.md` - Systematic approaches to identifying missing information
- `../context-filling-strategies/EFFICIENT_CONTEXT_TRANSFER.md` - Efficient techniques for providing context
- `../context-filling-strategies/GEIST_GAP_ANALYSIS_FRAMEWORK.md` - Systematic context filling with Ghost/Geyser/Gist framework

**Advanced Topics:**
- `../optimization/AGENTIC_CODING_OPTIMIZATION.md` - Multi-agent workflows and context distribution
- `../optimization/CONTEXT_WINDOW_OPTIMIZATION.md` - Balancing what to provide vs assume given token limits

### 9.2 Key Principles Summary

**Core Mental Model:**

1. **General → Specific**: LLMs know general patterns, you provide specifics
2. **Reasoning > Retrieval**: LLMs better at logic over provided facts than perfect recall
3. **Public → Private**: LLMs know public information, you provide private context
4. **Old → New**: LLMs know past information, you provide recent updates
5. **Common → Rare**: LLMs know popular patterns, you provide niche details

**Decision Framework:**

```
Should I explain [X] to the LLM?

Is [X] a general programming concept?
  YES → Assume LLM knows
  NO → Continue

Is [X] well-documented in public resources?
  YES → Assume LLM knows (but verify version)
  NO → Continue

Is [X] specific to my codebase/domain/company?
  YES → Always provide
  NO → Continue

Was [X] released/updated after training cutoff?
  YES → Provide documentation
  NO → Assume LLM knows
```

---

## 10. Conclusion

Understanding LLM knowledge boundaries is fundamental to effective AI-assisted development. By recognizing what LLMs reliably know from training versus what you must provide, you can optimize your collaboration workflow, reduce hallucinations, and achieve better outcomes faster.

**Key Takeaways:**

1. **LLMs Have Extensive General Knowledge**: Trust their knowledge of common programming concepts, popular libraries, and standard patterns. Don't waste time explaining basics.

2. **LLMs Cannot Know Your Specifics**: Always provide your requirements, codebase details, business logic, and runtime context. This is not optional.

3. **Reasoning Beats Retrieval**: LLMs excel at applying general principles to your specific situation. Provide facts, let them reason.

4. **Training Cutoff Matters**: Check the cutoff date. Provide documentation for recently updated dependencies or new technologies.

5. **Verify, Don't Trust Blindly**: Test assumptions, validate generated code, and use feedback loops to correct misunderstandings.

6. **Domain-Specific Gaps Are Real**: Healthcare, finance, legal, and company-specific knowledge requires explicit context. Don't assume LLMs know your industry's nuances.

**Practical Workflow:**

1. Start with clear requirements and constraints
2. Assume LLM knows general concepts, provide your specifics
3. Ask probing questions to verify knowledge boundaries
4. Provide documentation when in doubt
5. Validate all generated code and reasoning
6. Iterate with corrections and refinements
7. Document tribal knowledge as you go

By mastering these knowledge boundaries, you transform LLM collaboration from trial-and-error into a strategic partnership where you provide the context and constraints while the LLM provides the reasoning and implementation—exactly what each party does best.

---

**Document Version:** 1.0.0
**Last Updated:** 2025-10-21
**Next Review:** 2025-11-21
**Feedback:** Submit issues or suggestions to the repository
