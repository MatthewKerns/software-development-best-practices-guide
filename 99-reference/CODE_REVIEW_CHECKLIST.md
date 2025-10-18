# Code Review Checklist

**Quick reference for conducting thorough, effective code reviews.**

Based on: Code Complete 2 (Ch. 20-21), Clean Code

## Review Goals

- **Find defects** before they reach production
- **Share knowledge** across the team
- **Maintain standards** consistently
- **Improve code quality** incrementally
- **Mentor developers** through feedback

## Review Speed Guidelines

| Factor | Target | Note |
|--------|--------|------|
| **Review speed** | 200-400 LOC/hour | Slower for complex code |
| **Time per session** | 60-90 minutes max | Take breaks |
| **Lines per review** | < 400 LOC | Split larger changes |
| **Response time** | < 24 hours | Keep PRs flowing |

## Pre-Review Checklist (Author)

### Before Requesting Review
- [ ] Code compiles/builds successfully
- [ ] All tests pass locally
- [ ] Code follows team style guide
- [ ] No debugging code/console.logs
- [ ] No commented-out code
- [ ] Commit messages are clear
- [ ] PR description explains WHY (not just WHAT)
- [ ] Screenshots for UI changes
- [ ] Breaking changes documented

### Self-Review First
- [ ] Review your own diff before requesting review
- [ ] Check for obvious mistakes
- [ ] Ensure changes are focused
- [ ] Add comments where code isn't self-explanatory

## High-Level Review (5 minutes)

### Purpose and Scope
- [ ] PR description clear and complete
- [ ] Changes align with stated purpose
- [ ] Scope is reasonable (not too large)
- [ ] No unrelated changes mixed in
- [ ] Issue/ticket linked

### Architecture and Design
- [ ] Changes fit existing architecture
- [ ] No unnecessary complexity
- [ ] SOLID principles followed
- [ ] Appropriate design patterns used
- [ ] Dependencies point in right direction

## Detailed Code Review

### 1. Functionality (Does it work?)

#### Correctness
- [ ] Logic is correct
- [ ] Edge cases handled
- [ ] Boundary conditions checked
- [ ] Off-by-one errors avoided
- [ ] Null/undefined handled properly

#### Business Logic
- [ ] Requirements met
- [ ] Business rules correctly implemented
- [ ] Calculations accurate
- [ ] Validation appropriate

#### Error Handling
- [ ] Errors handled appropriately
- [ ] Error messages helpful
- [ ] No swallowed exceptions
- [ ] Proper logging
- [ ] Graceful degradation where appropriate

### 2. Testing (Is it tested?)

#### Test Coverage
- [ ] New code has tests
- [ ] Tests actually test the behavior
- [ ] Edge cases tested
- [ ] Error paths tested
- [ ] Coverage meets standards (85-90%)

#### Test Quality
- [ ] Tests are clear and focused
- [ ] Tests are independent
- [ ] Tests are repeatable
- [ ] Test names describe behavior
- [ ] No test duplication

#### Test Types
- [ ] Unit tests for logic
- [ ] Integration tests for interactions
- [ ] E2E tests for critical flows (if needed)

### 3. Readability (Can I understand it?)

#### Naming
- [ ] Names reveal intent
- [ ] Names are pronounceable
- [ ] Names are searchable
- [ ] No misleading names
- [ ] Consistent naming conventions

#### Functions
- [ ] Functions are small (< 20 lines)
- [ ] Functions do one thing
- [ ] Function names are verbs
- [ ] Few parameters (< 4)
- [ ] No flag arguments

#### Code Structure
- [ ] Logical organization
- [ ] Related code grouped together
- [ ] Appropriate abstraction levels
- [ ] No deep nesting (< 3 levels)
- [ ] Guard clauses for early returns

### 4. Maintainability (Can we change it?)

#### Code Smells
- [ ] No duplicate code
- [ ] No god classes/functions
- [ ] No feature envy
- [ ] No inappropriate intimacy
- [ ] No long parameter lists

#### Complexity
- [ ] Cyclomatic complexity reasonable
- [ ] No magic numbers
- [ ] Boolean expressions clear
- [ ] Switch statements appropriate (or use polymorphism)

#### Dependencies
- [ ] Minimal coupling
- [ ] High cohesion
- [ ] Dependency injection where appropriate
- [ ] No circular dependencies

### 5. Performance (Is it efficient?)

#### Efficiency
- [ ] No obvious performance issues
- [ ] Appropriate algorithms/data structures
- [ ] No unnecessary loops
- [ ] Database queries optimized
- [ ] Caching used appropriately

#### Scalability
- [ ] Handles expected load
- [ ] No memory leaks
- [ ] Resources cleaned up properly
- [ ] Asynchronous operations where needed

### 6. Security (Is it safe?)

#### Input Validation
- [ ] All inputs validated
- [ ] SQL injection prevented
- [ ] XSS prevented
- [ ] CSRF protection where needed
- [ ] Path traversal prevented

#### Authentication/Authorization
- [ ] Authentication required where needed
- [ ] Authorization checked
- [ ] Permissions validated
- [ ] Sensitive operations logged

#### Data Protection
- [ ] No sensitive data in logs
- [ ] Secrets not hardcoded
- [ ] Encryption used appropriately
- [ ] PII handled correctly

### 7. Documentation (Is it documented?)

#### Code Comments
- [ ] Comments explain WHY, not WHAT
- [ ] Complex algorithms documented
- [ ] Business rules documented
- [ ] No redundant comments
- [ ] No misleading comments

#### External Documentation
- [ ] API changes documented
- [ ] README updated if needed
- [ ] Migration guide for breaking changes
- [ ] Architecture decisions recorded (ADR)

## Language-Specific Checks

### Python
- [ ] Type hints used
- [ ] PEP 8 followed
- [ ] Context managers for resources (`with`)
- [ ] List comprehensions appropriate
- [ ] No mutable default arguments

### TypeScript/JavaScript
- [ ] Strict mode enabled
- [ ] Types defined (no `any`)
- [ ] Promises/async-await used correctly
- [ ] No `var` (use `const`/`let`)
- [ ] Optional chaining for null safety

### Java
- [ ] Proper exception hierarchy
- [ ] Resources closed (try-with-resources)
- [ ] Generics used appropriately
- [ ] Immutability where appropriate
- [ ] Streams over loops where clearer

## Common Issues to Catch

### Critical Issues (Must Fix)
- [ ] Security vulnerabilities
- [ ] Data corruption risks
- [ ] Memory leaks
- [ ] Race conditions
- [ ] Unhandled exceptions

### High Priority (Should Fix)
- [ ] Incorrect business logic
- [ ] Missing error handling
- [ ] Performance problems
- [ ] Broken tests
- [ ] SOLID violations

### Medium Priority (Consider Fixing)
- [ ] Code smells
- [ ] Unclear naming
- [ ] Missing tests
- [ ] Complex functions
- [ ] Duplicate code

### Low Priority (Nice to Have)
- [ ] Minor style issues
- [ ] Optimization opportunities
- [ ] Documentation improvements
- [ ] Refactoring suggestions

## Providing Feedback

### Feedback Principles
- **Be kind**: Focus on code, not person
- **Be specific**: Point to exact lines
- **Be constructive**: Suggest alternatives
- **Explain why**: Share reasoning
- **Ask questions**: "Could we..." vs "You should..."
- **Praise good code**: Positive reinforcement

### Feedback Examples

#### ❌ Poor Feedback
```
This is wrong.
Why did you do it this way?
This code is a mess.
```

#### ✅ Good Feedback
```
This function is doing multiple things. Could we extract the
validation logic into a separate function? This would make it
easier to test and follow the Single Responsibility Principle.

I like how you handled the edge case at line 42! This is a
subtle issue that's easy to miss.

Have you considered using a guard clause here instead of nested
if statements? It would reduce indentation and make the happy
path clearer.
```

### Comment Categories

Use labels to indicate priority:

```
[CRITICAL] Security: User input not validated
[BLOCKER] Tests: This breaks the payment flow test
[ISSUE] Bug: Off-by-one error in loop condition
[SUGGESTION] Refactor: Consider extracting this to a method
[QUESTION] Clarify: Is this handling the null case?
[NITPICK] Style: Variable name could be more descriptive
[PRAISE] Nice: Great use of the builder pattern here!
```

## Review Workflow

### 1. First Pass (10-15 min)
- [ ] Read PR description
- [ ] Review high-level design
- [ ] Check tests first
- [ ] Scan for obvious issues

### 2. Detailed Review (30-60 min)
- [ ] Go through each file carefully
- [ ] Check logic and edge cases
- [ ] Verify error handling
- [ ] Review test coverage
- [ ] Add inline comments

### 3. Summary (5-10 min)
- [ ] Overall assessment
- [ ] List of issues by priority
- [ ] Suggestions for improvement
- [ ] Approval decision

### Review States

**Approve:**
- Code is production-ready
- All critical issues resolved
- Meets team standards

**Request Changes:**
- Critical/high priority issues found
- Must be addressed before merge
- Re-review needed

**Comment:**
- Suggestions for improvement
- Non-blocking issues
- Questions for author

## Team Review Standards

### What to Review
- [ ] All production code
- [ ] Configuration changes
- [ ] Database migrations
- [ ] Infrastructure changes
- [ ] Documentation updates

### Review Exemptions (Team Decision)
- Small fixes (< 10 LOC)?
- Emergency hotfixes?
- Documentation-only?
- Automated refactorings?

### Review Requirements
- [ ] Minimum reviewers: 1-2
- [ ] Required approvals: 1-2
- [ ] Specific reviewers for:
  - Security changes
  - Database changes
  - API changes
  - Architecture changes

## Common Review Anti-Patterns

### Reviewer Anti-Patterns
- [ ] ❌ Rubber stamping (approving without reading)
- [ ] ❌ Nitpicking (only style comments)
- [ ] ❌ Ego (showing off knowledge)
- [ ] ❌ Inconsistency (different standards for different people)
- [ ] ❌ Delayed reviews (> 24 hours)

### Author Anti-Patterns
- [ ] ❌ Defensive (arguing every comment)
- [ ] ❌ Too large PRs (> 400 LOC)
- [ ] ❌ Multiple concerns in one PR
- [ ] ❌ No tests
- [ ] ❌ Ignoring feedback

## Review Metrics

### Effectiveness Metrics
- Defects found per review
- Defects escaped to production
- Time to review
- Review coverage percentage
- Re-review rate

### Quality Metrics
- Average comments per review
- Critical vs minor issues ratio
- Approval rate
- Time to address feedback

## Special Case Reviews

### Database Changes
- [ ] Migrations are reversible
- [ ] Indexes for new queries
- [ ] No data loss
- [ ] Performance impact assessed
- [ ] Backup plan documented

### API Changes
- [ ] Backward compatible or versioned
- [ ] Documentation updated
- [ ] Clients notified
- [ ] Examples provided
- [ ] Error responses documented

### Security-Sensitive Changes
- [ ] Security expert reviewed
- [ ] Threat model considered
- [ ] Authentication/authorization correct
- [ ] Input validation thorough
- [ ] Secrets management proper

### Performance-Critical Changes
- [ ] Benchmarks included
- [ ] Load testing done
- [ ] Caching strategy defined
- [ ] Database query performance
- [ ] Resource usage measured

## Review Tools

### Automated Checks (Before Human Review)
- [ ] CI/CD pipeline passes
- [ ] Linter passes
- [ ] Tests pass
- [ ] Code coverage meets threshold
- [ ] Security scan clean

### Review Platform Features
- Line-by-line comments
- Suggested changes
- Review threads
- Approval workflow
- Integration with CI/CD

## After Review

### Author Actions
- [ ] Address all critical/blocking issues
- [ ] Respond to questions
- [ ] Update based on feedback
- [ ] Mark conversations as resolved
- [ ] Request re-review if needed

### Reviewer Actions
- [ ] Review updated code
- [ ] Verify issues addressed
- [ ] Approve or request further changes
- [ ] Merge when approved (if authorized)

## Quick Decision Tree

```
Is this code production-ready?
    ✗ → What's blocking it?
        Security? → CRITICAL: Must fix
        Correctness? → BLOCKER: Must fix
        Tests? → ISSUE: Should fix
        Style? → SUGGESTION: Nice to have

    ✓ → Any suggestions for improvement?
        Major? → Comment with suggestions
        Minor? → Approve with minor comments
        None? → Approve with praise!
```

## References

- **Full Guide**: [06-collaborative-construction/](../06-collaborative-construction/)
- **Source**: Code Complete 2 (Ch. 20-21), Clean Code
- **Related**: [CODE_SMELLS_CHECKLIST.md](./CODE_SMELLS_CHECKLIST.md)

---

**Remember**: Code review is collaboration, not criticism. The goal is better code and better developers.
