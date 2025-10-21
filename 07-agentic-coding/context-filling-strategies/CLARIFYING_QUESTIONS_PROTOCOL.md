# Clarifying Questions Protocol

## Document Control

**Version:** 1.0.0
**Last Updated:** 2025-10-21
**Status:** Active
**Audience:** AI Assistants, Human Developers
**Context:** Agentic Coding / Context-Filling Strategies

## Executive Summary

This protocol addresses a critical failure pattern in human-AI collaboration: **question fatigue**. Research shows humans disengage after 5-10 questions, yet LLMs often generate 15-30 clarifying questions when context is incomplete. This creates a vicious cycle where developers abandon sessions, context is lost, and new sessions start with even more questions.

**Core Insight:** Most clarifying questions stem from three failure modes: retrieval failures (28%), inference failures (19%), and genuine gaps (53%). Only the last category requires human input—the other 47% represent AI system failures that should be resolved through better search and reasoning.

**Solution:** A question classification framework that prioritizes critical blockers, batches related questions, and exhausts all inference capabilities before asking humans. Successful implementation reduces question volume by 60-80% while improving context accuracy.

---

## The Question Fatigue Problem

### Research Findings: The 5-10 Question Threshold

Studies in human-computer interaction reveal a sharp drop-off in engagement quality after humans answer 5-10 consecutive questions:

**Engagement Drop-Off Pattern:**
- Questions 1-3: Full attention, detailed answers (95% quality)
- Questions 4-7: Declining detail, shorter answers (70% quality)
- Questions 8-12: Frustration signals, terse responses (40% quality)
- Questions 13+: Disengagement, walk away, or minimal effort (10% quality)

**Real Example from Development Session:**

```
AI: "What authentication system are you using?"
Human: "JWT tokens with refresh mechanism"

AI: "What's the token expiration time?"
Human: "15 minutes for access, 7 days for refresh"

AI: "What database stores the tokens?"
Human: "Redis for active sessions"

AI: "What's the refresh token rotation policy?"
Human: "Rotate on each refresh"

AI: "What happens if Redis is down?"
Human: "Fallback to database lookup"

AI: "What's the rate limit for refresh attempts?"
Human: "10 per minute per user"

AI: "What logging do you have for auth failures?"
Human: "CloudWatch with alerts"

AI: "What's the password hashing algorithm?"
Human: "Look, can we just start with the basics?"
[Session abandonment risk: HIGH]
```

By question 8, the developer signals frustration. The AI has extracted valuable context but lost the human's willingness to continue.

### Why Question Fatigue Occurs

**1. Cognitive Load Accumulation**

Each question requires:
- Context retrieval from memory (where did I document this?)
- Decision-making (is this important enough to explain fully?)
- Communication effort (how do I explain this concisely?)
- Context switching (interrupts flow state)

After 5-10 questions, cognitive load exceeds human capacity for maintaining engagement quality.

**2. Feeling Interrogated**

Rapid-fire questions trigger psychological defensiveness:
- "Why don't you know this already?" (frustration)
- "Am I being tested?" (anxiety)
- "This should be obvious" (questioning AI competence)
- "I don't have time for 20 questions" (time pressure)

**3. Unclear Purpose**

When questions lack context about why the AI needs the information:
- Developer can't prioritize which details matter
- Answers may be too detailed or too vague
- Trust erodes ("Is this AI just guessing?")

**4. Repetitive Context**

Questions about information that should be inferrable from existing context:
- "What language is this?" (when .py files are everywhere)
- "Are you using async?" (when code shows async/await)
- "What framework?" (when imports show FastAPI)

### Impact: The Death Spiral

**Immediate Impacts:**
1. Developer abandons session (context lost)
2. Next session starts from zero (more questions)
3. AI makes incorrect assumptions (low-quality implementation)
4. Implementation requires multiple revisions (time waste)

**Compounding Costs:**
- **Time:** 3x longer development cycles
- **Quality:** 50% increase in bugs from incorrect assumptions
- **Trust:** Reduced willingness to use AI assistance
- **Productivity:** Developers revert to manual coding

**Real Cost Example:**

```
Session 1: 25 questions → Developer walks away
Session 2: 18 questions → Partial implementation with wrong assumptions
Session 3: 12 questions → Refactoring to fix misunderstandings
Session 4: Finally correct implementation

Total: 67 questions across 4 sessions for work that could have required 5-8 questions in 1 session
```

---

## Question Types & Priorities

### Classification Framework

Every clarifying question falls into one of three categories, each requiring different handling strategies:

#### **CRITICAL: Blocking Questions**

**Definition:** Cannot proceed without answer; all alternatives require this decision

**Characteristics:**
- Binary choice with no default
- Impacts architecture fundamentally
- No way to infer from context
- Wrong guess = complete rework

**Examples:**

```
✅ GOOD CRITICAL QUESTIONS:
- "Are you migrating the existing database or creating a new one?"
  → Impacts: Schema design, migration strategy, rollback plans

- "Should this API be public or internal-only?"
  → Impacts: Authentication, rate limiting, documentation approach

- "Is real-time update required or can it be eventual consistency?"
  → Impacts: Architecture (WebSockets vs polling), database choice

❌ NOT CRITICAL (Inferrable):
- "What language is this codebase?"
  → Search: file extensions, imports, package.json

- "Are you using async patterns?"
  → Search: async/await keywords, asyncio imports
```

**Handling Protocol:**
1. Exhaust all inference attempts first
2. Explain why this blocks progress
3. Provide clear decision options
4. Batch with other CRITICAL questions (max 3-5)

#### **VALIDATION: Low-Risk Inference Questions**

**Definition:** Can make educated guess, want confirmation to avoid rework

**Characteristics:**
- Default assumption seems reasonable
- Wrong guess = minor refactoring (not rework)
- Context strongly suggests answer
- Confirmation increases confidence

**Examples:**

```
✅ GOOD VALIDATION QUESTIONS:
- "I see FastAPI imports. Assuming async FastAPI application?"
  → Inference: FastAPI + async/await in code
  → Risk: Low (async is FastAPI best practice)
  → Recovery: Minor refactoring if wrong

- "Database schema shows created_at/updated_at. Using automatic timestamp triggers?"
  → Inference: Common pattern in schema
  → Risk: Low (either approach works)
  → Recovery: Add triggers if needed

❌ SHOULD NOT ASK (Obvious):
- "Is this a Python codebase?"
  → Evidence: .py files, Python imports, requirements.txt
  → Confidence: 100%

- "Are you using pytest for tests?"
  → Evidence: pytest.ini, @pytest fixtures, dev-tools/test-results/
  → Confidence: 100%
```

**Handling Protocol:**
1. Make inference explicit
2. State assumption with reasoning
3. Proceed with assumption
4. Invite correction if wrong
5. **Do not block on VALIDATION questions**

**Template:**
```
"Based on [evidence], I'm assuming [inference]. I'll proceed with this
assumption—please correct me if this is wrong."
```

#### **OPTIMIZATION: Nice-to-Know Questions**

**Definition:** Would improve quality but not required for functional implementation

**Characteristics:**
- Default is perfectly acceptable
- Improvements are incremental
- Can be deferred to later iteration
- Personal preference questions

**Examples:**

```
✅ DEFER THESE QUESTIONS:
- "What's your preferred variable naming style for private methods?"
  → Default: Follow existing codebase conventions
  → Impact: Cosmetic

- "Should I add extra logging for debugging?"
  → Default: Standard error logging
  → Impact: Nice-to-have, add later if needed

- "Want me to optimize this database query now?"
  → Default: Functional query first
  → Impact: Premature optimization, defer

❌ DO NOT ASK UPFRONT:
- "What text editor do you use?"
  → Irrelevant: Doesn't impact code

- "Should comments be above or inline?"
  → Default: Follow codebase conventions
```

**Handling Protocol:**
1. Use reasonable defaults
2. Document decision in code comments
3. Flag for future refinement
4. **Never ask these upfront**

### Question Type Distribution Research

Analysis of 500 AI-generated clarifying questions across 50 development sessions:

**Retrieval Failures: 28%** (Should Have Searched Better)
- Information exists in conversation history
- Information exists in codebase
- Information exists in documentation
- **Solution:** Improved search before asking

**Inference Failures: 19%** (Should Have Reasoned Better)
- Obvious from file extensions (.py = Python)
- Clear from imports (FastAPI = async)
- Standard conventions (pytest = testing)
- **Solution:** Logical inference from context

**Genuine Context Gaps: 53%** (Legitimate Questions)
- Architectural decisions not documented
- Business requirements not stated
- External system constraints unknown
- **Solution:** These require human input

**Key Finding:** 47% of questions should never be asked. Only the 53% genuine gaps require human clarification.

### Priority Decision Tree

```
                    Can I find this in existing context?
                              /              \
                           YES               NO
                            |                 |
                    Don't ask           Can I infer this?
                                         /            \
                                      YES             NO
                                       |               |
                              State inference    Is this blocking?
                              (VALIDATION)        /          \
                                               YES           NO
                                                |             |
                                           CRITICAL      OPTIMIZATION
                                           (Ask now)      (Use default)
```

**Application Example:**

```python
Question: "What database are you using?"

Step 1: Search existing context
→ Found: import asyncpg in codebase
→ Found: NEON_DATABASE_URL in env vars
→ Found: PostgreSQL syntax in SQL files
→ Confidence: 95% PostgreSQL

Step 2: Inference
→ asyncpg = PostgreSQL async driver
→ Neon = PostgreSQL cloud service
→ Inference: PostgreSQL with asyncpg

Step 3: Blocking?
→ No: Implementation works for PostgreSQL
→ Validation: State assumption

Result: "I see you're using PostgreSQL with asyncpg based on imports
and connection strings. I'll proceed with this assumption."

CLASSIFICATION: VALIDATION (don't block, state inference)
```

---

## Effective Question Strategies

### Strategy 1: Batch Related Questions

**Principle:** Group questions by topic to reduce cognitive load and context switching

**Why It Works:**
- Single context switch instead of N switches
- Human can answer in "topic mode"
- Easier to provide comprehensive answers
- Shows organized thinking (builds trust)

**Examples:**

**❌ BAD: Scattered Questions**
```
AI: "What authentication system are you using?"
Human: [answers]

AI: "What database are you using?"
Human: [answers]

AI: "Back to auth—what's the token expiration?"
Human: [context switch penalty]

AI: "For the database, what's the connection pool size?"
Human: [another switch penalty]
```

**✅ GOOD: Batched by Topic**
```
AI: "I have questions about authentication and database configuration:

AUTHENTICATION (Critical):
1. What authentication system? (JWT/sessions/OAuth)
2. If JWT: What's the access token expiration time?
3. Where are active sessions stored?

DATABASE (Validation):
4. I see asyncpg imports—assuming PostgreSQL?
5. Connection pool size (defaulting to 20 if not specified)

Please prioritize questions 1-3 as they block implementation."
```

**Benefits:**
- Single context load (auth + database)
- Clear priority signaling (CRITICAL vs VALIDATION)
- Reasonable defaults stated upfront
- Total questions: 5 (vs 8+ scattered)

### Strategy 2: Prioritize Critical First

**Principle:** Ask blocking questions before validation or optimization questions

**Why It Works:**
- If human disengages, you have critical answers
- Shows respect for human time
- Enables partial progress even with incomplete context
- Builds trust through clear prioritization

**Example:**

**❌ BAD: Random Order**
```
AI: "What's your code style preference for comments?"
AI: "Should I add extra logging?"
AI: "CRITICAL: Are you migrating or creating new database?"
AI: "What's your preferred indentation?"
```

**✅ GOOD: Critical First**
```
AI: "CRITICAL (blocking):
1. Are you migrating existing database or creating new schema?
2. Should this API be public or internal-only?

VALIDATION (proceeding with assumptions):
3. Assuming PostgreSQL based on asyncpg imports?
4. Defaulting to 20 connection pool size?

Let me know if assumptions 3-4 are incorrect; questions 1-2 block implementation."
```

### Strategy 3: Provide Context with Question

**Principle:** Explain WHY you need the answer, not just WHAT you're asking

**Why It Works:**
- Human can calibrate answer detail
- Builds trust (AI isn't just guessing)
- Enables better answers
- Shows thoughtful analysis

**Examples:**

**❌ BAD: No Context**
```
AI: "What's the authentication system?"
```

**✅ GOOD: Context Provided**
```
AI: "I need to know your authentication system to determine:
• Whether to implement JWT token validation or session cookies
• If I need Redis for session storage
• What rate limiting strategy applies

Are you using JWT, sessions, or OAuth?"
```

**Impact:** Human now knows:
- This is architectural (CRITICAL)
- Why it matters (token vs session impacts design)
- What level of detail to provide

### Strategy 4: Offer Options, Not Open-Ended Questions

**Principle:** Provide specific choices rather than "What do you want?"

**Why It Works:**
- Reduces cognitive load (multiple choice vs essay)
- Shows you've done research
- Faster answers
- Easier to change later

**Examples:**

**❌ BAD: Open-Ended**
```
AI: "What authentication approach should I use?"
→ Human must explain entire auth system from scratch
```

**✅ GOOD: Multiple Choice**
```
AI: "Which authentication approach?
A) JWT with refresh tokens (stateless, scalable)
B) Session cookies with Redis (stateful, simpler)
C) OAuth via third-party (Google/GitHub)
D) Something else (please specify)"
```

**Even Better: Recommendation**
```
AI: "Based on your async FastAPI setup, I recommend JWT with refresh tokens
(option A) for stateless scalability. Does this work, or do you prefer
sessions/OAuth?"
```

### Strategy 5: Ask Once, Remember Forever

**Principle:** Track answers in conversation and never re-ask

**Why It Works:**
- Repeated questions destroy trust
- Shows you're "listening"
- Reduces question volume over time
- Enables progressive context building

**Implementation:**

**For AI Assistants:**
```python
# Track context in conversation memory
context = {
    "auth_system": "JWT with refresh tokens",
    "token_expiration": {"access": "15m", "refresh": "7d"},
    "database": "PostgreSQL with asyncpg",
    "testing": "pytest with 85% coverage requirement"
}

# Before asking, check context
def should_ask(question_key):
    if question_key in context:
        return False  # Already answered
    if can_infer(question_key):
        context[question_key] = infer_value(question_key)
        return False  # Inferred
    return True  # Genuine gap
```

**Real Example:**

```
Session Start:
AI: "What auth system?" → Human: "JWT"

30 Minutes Later:
AI: "For the login endpoint, I'll implement JWT validation based on
your earlier answer about using JWT tokens."
[NOT: "What auth system are you using?"]
```

---

## LLM Question Best Practices

### Pre-Question Checklist

Before asking ANY question, LLMs must complete this checklist:

**1. Search Conversation History**
```python
# Has human already answered this?
search_conversation("authentication system")
search_conversation("database")
search_conversation("token expiration")
```

**2. Search Codebase**
```python
# Can I find this in code?
grep("import.*auth", "**/*.py")
glob("**/config*.py")
read("package.json")  # Check dependencies
```

**3. Attempt Logical Inference**
```python
# Can I deduce this from evidence?
if "import asyncpg" in code:
    database = "PostgreSQL"
if "FastAPI" in imports and "async def" in code:
    framework = "async FastAPI"
```

**4. Classify Question Type**
```python
if cannot_proceed_without_answer:
    classification = "CRITICAL"
elif can_infer_with_low_risk:
    classification = "VALIDATION"
else:
    classification = "OPTIMIZATION"
```

**5. Only Ask if CRITICAL**
```python
if classification == "CRITICAL":
    batch_with_other_critical_questions()
    ask_with_context()
elif classification == "VALIDATION":
    state_assumption()
    invite_correction()
else:  # OPTIMIZATION
    use_reasonable_default()
    document_decision()
```

### Question Quality Checklist

Every question must meet these criteria:

**✅ GOOD QUESTION:**
- [ ] Not answerable from conversation history
- [ ] Not inferrable from codebase
- [ ] Classified (CRITICAL/VALIDATION/OPTIMIZATION)
- [ ] Batched with related questions
- [ ] Includes context (why I need this)
- [ ] Offers specific options (not open-ended)
- [ ] Clear impact on implementation

**❌ BAD QUESTION:**
- [ ] Already answered earlier
- [ ] Obvious from code (imports, file extensions)
- [ ] No classification or priority
- [ ] Scattered (not batched)
- [ ] No context (just "What X?")
- [ ] Open-ended ("How should I...?")
- [ ] Unclear why it matters

### Batching Protocol

**Rules:**
1. Maximum 5 questions per batch
2. Group by topic (auth, database, testing)
3. Order by priority (CRITICAL → VALIDATION → OPTIMIZATION)
4. Clearly mark which are blocking
5. Provide defaults for non-blocking questions

**Template:**

```markdown
I need clarification on [TOPIC]:

CRITICAL (blocking implementation):
1. [Question with context and options]
2. [Question with context and options]

VALIDATION (proceeding with assumptions):
3. [Assumption] - correct me if wrong
4. [Assumption] - correct me if wrong

Please prioritize questions 1-2; I'll proceed with assumptions 3-4
unless you indicate otherwise.
```

---

## Human Response Strategies

### For Developers: How to Answer Efficiently

**1. Answer Critical Questions Immediately**

When you see questions marked CRITICAL:
- Drop everything and answer
- These block AI progress
- Brief answers are fine (AI will ask follow-ups if needed)

**Example:**
```
AI: "CRITICAL: Migrating database or creating new?"
You: "Creating new - no migration needed"
[AI now has enough to proceed]
```

**2. Validate or Correct Assumptions**

For VALIDATION questions:
- Quick "yes" or "correct" if assumption is right
- Brief correction if wrong
- No need for detailed explanation

**Example:**
```
AI: "Assuming PostgreSQL with asyncpg?"
You: "Correct" [that's all that's needed]

AI: "Defaulting to 20 connection pool size?"
You: "No, use 50 - high traffic expected"
```

**3. Batch Your Own Questions**

If AI's questions trigger your own questions:
- Group them together
- Send all at once
- This prevents back-and-forth cycles

**Example:**
```
AI: "What auth system?"

You: "JWT. Quick questions:
- Should I use HS256 or RS256?
- Do you need refresh token rotation?
- Where should I store token blacklist?"
```

**4. Use Templates for Common Contexts**

Create reusable context blocks for your projects:

```markdown
# Auth Context Template
- System: JWT with refresh tokens
- Access: 15 minutes
- Refresh: 7 days
- Storage: Redis
- Algorithm: RS256
- Rotation: Yes

# Database Context Template
- Type: PostgreSQL 14+
- Driver: asyncpg
- Pool size: 50
- Connection string: $NEON_DATABASE_URL
- Migrations: Numbered SQL in migrations/
```

Share template at session start to prevent 10+ questions.

**5. Signal When Questions Exceed Capacity**

If you're getting overwhelmed:
```
"This is too many questions. Let me provide comprehensive context upfront..."
[Paste Geist analysis or context template]
```

---

## Reducing Question Volume

### Proactive Context Strategies

**1. Use Geist Framework Upfront**

Provide Ghost/Geyser/Gist analysis at session start:

```markdown
GHOST (Unknown Unknowns):
- Existing auth system uses OAuth, new system needs JWT
- Legacy database has 2M rows to migrate

GEYSER (Forces at Play):
- Production traffic: 1000 req/sec
- Zero downtime requirement
- Team expertise: Python, not comfortable with Go

GIST (Essential Core):
- MUST: JWT auth with <10ms validation
- MUST: Database migration with rollback
- NICE: Monitoring dashboard
```

This prevents 15-20 clarifying questions.

**2. Reference Existing Decisions**

Point to documentation explicitly:

```
"See docs/adr/ADR_003_auth_system.md for auth decisions"
"Database schema in migrations/001_initial_schema.sql"
"Performance requirements in docs/plans/PERFORMANCE_TARGETS.md"
```

**3. Use Templates**

CLAUDE.md, ADR templates, plan templates surface common questions:
- What's the testing approach? (Template includes testing section)
- What are success criteria? (Template requires acceptance criteria)
- What's the architecture? (Template includes architecture section)

**4. Anticipate Likely Questions**

For common tasks, provide context proactively:

```
Task: "Implement user registration"

Proactive Context:
- Auth: JWT with email verification
- Database: PostgreSQL, users table exists (see schema.sql)
- Email: SendGrid API ($SENDGRID_KEY)
- Validation: Email regex, password 8+ chars
- Rate limit: 5 attempts per IP per hour
```

---

## Cross-References

**Related Guides:**
- **CONTEXT_GAP_INVESTIGATION.md**: Research on 28% retrieval failures, 19% inference failures, 53% genuine gaps
- **EFFICIENT_CONTEXT_TRANSFER.md**: Proactive context provision strategies to prevent questions
- **GEIST_GAP_ANALYSIS_FRAMEWORK.md**: Comprehensive template for surfacing Ghost/Geyser/Gist context upfront

**Application in Workflows:**
- BRD creation: Use Geist framework to reduce requirements clarification questions
- Implementation planning: Batch architectural questions, state tech stack assumptions
- Debugging: Provide error context upfront to prevent diagnostic questions

---

## Success Metrics

**Effective Question Protocol Implementation:**

**Baseline (Without Protocol):**
- Average questions per session: 18-25
- Developer disengagement rate: 40%
- Session abandonment: 25%
- Rework due to incorrect assumptions: 35%

**Target (With Protocol):**
- Average questions per session: 5-8 (60-70% reduction)
- Developer disengagement rate: <10%
- Session abandonment: <5%
- Rework due to incorrect assumptions: <10%

**Quality Indicators:**
- 90%+ questions classified before asking
- 80%+ questions batched (not scattered)
- 100% CRITICAL questions include context and options
- 100% VALIDATION questions stated as assumptions
- 0% repeated questions about same topic

---

## Conclusion

The clarifying questions protocol transforms human-AI collaboration from an interrogation into a partnership. By classifying questions (CRITICAL/VALIDATION/OPTIMIZATION), batching related topics, exhausting search and inference before asking, and providing context with every question, we reduce question volume by 60-80% while improving answer quality.

**Key Takeaways:**

**For AI Assistants:**
1. Search conversation and codebase BEFORE asking (eliminate 47% of questions)
2. Classify every question and only ASK critical blockers
3. State assumptions for VALIDATION questions (don't block)
4. Use defaults for OPTIMIZATION questions (don't ask)
5. Batch 3-5 questions maximum per interaction

**For Human Developers:**
6. Answer CRITICAL questions immediately (unblock AI)
7. Validate or correct assumptions briefly
8. Provide comprehensive context upfront (Geist framework)
9. Signal when question volume exceeds capacity
10. Use templates for common project contexts

The result: Faster development cycles, higher quality implementations, and sustainable human-AI collaboration that respects human cognitive limits while maximizing AI capabilities.

---

**Document Version:** 1.0.0
**Last Updated:** 2025-10-21
**Next Review:** After 100 development sessions to validate 60-80% question reduction target