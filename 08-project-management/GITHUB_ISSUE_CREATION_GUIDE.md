# GitHub Issue Creation Guide

**Purpose**: Comprehensive guidance for creating well-structured GitHub issues that integrate with our TDD workflow and documentation standards.

**Date**: August 22, 2025  
**Version**: 1.0.0  
**Integration**: Works with Copilot instructions and markdown plan templates

## 📋 Overview

This guide establishes standards for creating GitHub issues that align with our project's documentation-first, TDD approach. All issues should follow these patterns to ensure consistency, clarity, and actionable outcomes.

## 🎯 Issue Types & Templates

### Issue Type Classification

| Issue Type          | Purpose                                   | Template                | Estimated Effort | Assignment     |
| ------------------- | ----------------------------------------- | ----------------------- | ---------------- | -------------- |
| **Bug Report**      | Production issues, errors, failures       | Bug Template            | 1-8 hours        | GitHub Copilot |
| **Feature Request** | New functionality, enhancements           | Feature Template        | 4-40 hours       | GitHub Copilot |
| **Investigation**   | Research, analysis, decision-making       | Investigation Template  | 2-16 hours       | GitHub Copilot |
| **Implementation**  | Planned development work                  | Implementation Template | 8-80 hours       | GitHub Copilot |
| **Documentation**   | Docs updates, guides, README improvements | Documentation Template  | 1-8 hours        | GitHub Copilot |
| **Refactoring**     | Code quality, performance, architecture   | Refactoring Template    | 4-32 hours       | GitHub Copilot |

## 📝 Universal Issue Standards

### Required Elements (All Issues)

1. **Clear, Descriptive Title**

   - Format: `[Type]: Specific action or problem description`
   - Examples:
     - `[Bug]: Token validation returns 500 error instead of 400`
     - `[Feature]: Add GitHub MCP integration to chat interface`
     - `[Investigation]: Evaluate MCP vs direct API performance impact`

2. **Comprehensive Description**

   - Business context and motivation
   - Technical requirements or problem details
   - Acceptance criteria or success metrics
   - Reference to relevant documentation

3. **Proper Labels**

   - Issue type: `bug`, `enhancement`, `investigation`, `documentation`
   - Priority: `priority:high`, `priority:medium`, `priority:low`
   - Effort: `effort:small` (1-4h), `effort:medium` (4-16h), `effort:large` (16h+)
   - Component: `api`, `workflow`, `database`, `frontend`, `docs`

4. **Assignment**

   - Default: Assign to @github-copilot[bot]
   - Human review: Add `needs-human-review` label when appropriate

5. **Project Integration**
   - Link to project board
   - Reference related issues, PRs, or documentation
   - Connect to relevant milestones

## 🐛 Bug Report Template

````markdown
# [Bug]: [Concise problem description]

## 📋 Bug Description

**Summary**: Brief description of the issue

**Impact**: How this affects users/system functionality

**Frequency**: How often this occurs (always, intermittent, specific conditions)

## 🔄 Reproduction Steps

1. Step one with specific commands/actions
2. Step two with expected vs actual results
3. Step three with environment details

```bash
# Include exact commands that reproduce the issue
command --with --specific --flags
```
````

## 🎯 Expected vs Actual Behavior

**Expected**: What should happen
**Actual**: What actually happens
**Evidence**: Error messages, logs, screenshots

## 🔧 Environment Details

- **OS**: macOS/Linux/Windows version
- **Python**: Version and virtual environment
- **Node.js**: Version (if applicable)
- **Dependencies**: Relevant package versions
- **Configuration**: Environment variables, config files

## 📊 Technical Investigation

**Error Details**:

```
[Include full error messages, stack traces, relevant logs]
```

**System State**:

- Server status: Running/Stopped/Error
- Database connections: Active/Failed
- External service status: Connected/Timeout/Error

## 🔍 Initial Analysis

**Suspected Cause**: Initial hypothesis about root cause
**Affected Components**: List of system components involved
**Potential Impact**: Scope of users/functionality affected

## ✅ Acceptance Criteria

- [ ] Issue reproduces reliably
- [ ] Root cause identified
- [ ] Fix implemented with tests
- [ ] No regression in existing functionality
- [ ] Documentation updated if needed

## 📚 Related Documentation

- Link to relevant READMEs, ADRs, or implementation plans
- Reference to error handling guides
- Related issues or PRs

## 🏷️ Labels

`bug`, `priority:high`, `effort:medium`, `[component]`

---

**Assignment**: @github-copilot[bot]
**Estimated Effort**: [X hours based on complexity]

````

## 🚀 Feature Request Template

```markdown
# [Feature]: [Specific feature or enhancement description]

## 📋 Feature Overview

**Summary**: Clear, concise description of the requested feature

**Business Value**: Why this feature is needed and its impact

**User Story**: As a [user type], I want [functionality] so that [benefit]

## 🎯 Requirements & Acceptance Criteria

### Functional Requirements

- [ ] Requirement 1 with specific behavior
- [ ] Requirement 2 with measurable outcome
- [ ] Requirement 3 with technical specification

### Non-Functional Requirements

- [ ] Performance: Specific latency/throughput targets
- [ ] Security: Authentication/authorization requirements
- [ ] Compatibility: System/browser/version support
- [ ] Scalability: Expected load/user capacity

## 🏗️ Technical Approach

**Architecture Overview**:
- High-level design approach
- Integration points with existing system
- New components or services needed

**Implementation Strategy**:
- Step-by-step development approach
- Dependencies and prerequisites
- Risk mitigation strategies

## 🧪 Testing Strategy

**Test Coverage Requirements**:
- [ ] Unit tests (≥90% coverage for new code)
- [ ] Integration tests for external service connections
- [ ] End-to-end tests for user workflows
- [ ] Performance tests for scalability requirements

**Test Scenarios**:
- Happy path testing
- Edge case validation
- Error condition handling
- Security boundary testing

## 📊 Success Metrics

**Development Metrics**:
- Code coverage percentage
- Performance benchmarks
- Security scan results

**Business Metrics**:
- User adoption rate
- Feature usage statistics
- Impact on system performance

## 🔄 Implementation Plan

**Phase 1**: [Initial implementation - X hours]
- Core functionality development
- Basic testing and validation

**Phase 2**: [Enhancement and optimization - X hours]
- Advanced features
- Performance optimization
- Comprehensive testing

**Phase 3**: [Production hardening - X hours]
- Security review
- Documentation completion
- Deployment preparation

## 📚 Reference Documentation

- [`construction_best_practices/TDD_WORKFLOW_GUIDE.md`](../construction_best_practices/TDD_WORKFLOW_GUIDE.md)
- [`construction_best_practices/CODE_CONSTRUCTION_GUIDE.md`](../construction_best_practices/CODE_CONSTRUCTION_GUIDE.md)
- Related ADRs or implementation plans
- External API documentation

## 🏷️ Labels

`enhancement`, `priority:medium`, `effort:large`, `[component]`

---

**Assignment**: @github-copilot[bot]
**Estimated Effort**: [X hours based on scope]
````

## 🔍 Investigation Template

```markdown
# [Investigation]: [Research question or decision to be made]

## 📋 Investigation Overview

**Purpose**: Clear statement of what needs to be investigated

**Decision Context**: Why this investigation is needed now

**Scope**: Boundaries of what will and won't be investigated

## ❓ Key Questions

1. **Primary Question**: Main question to be answered
2. **Secondary Questions**: Supporting questions for comprehensive analysis
3. **Success Criteria**: How we'll know the investigation is complete

## 🔬 Investigation Approach

**Research Methods**:

- [ ] Literature review of existing documentation
- [ ] Technical experimentation and prototyping
- [ ] Performance benchmarking and analysis
- [ ] Stakeholder interviews or requirements gathering
- [ ] Competitive analysis or industry research

**Investigation Phases**:

### Phase 1: Background Research (X hours)

- Review existing documentation and prior work
- Identify knowledge gaps and assumptions
- Establish baseline measurements

### Phase 2: Experimentation (X hours)

- Implement proof-of-concept solutions
- Conduct performance testing
- Validate technical feasibility

### Phase 3: Analysis & Recommendation (X hours)

- Compare options and trade-offs
- Document findings and recommendations
- Prepare decision documentation

## 📊 Success Metrics

**Investigation Completeness**:

- [ ] All key questions answered with evidence
- [ ] Trade-offs clearly documented
- [ ] Recommendations supported by data
- [ ] Decision criteria clearly defined

**Quality Standards**:

- [ ] Findings reproducible by others
- [ ] Assumptions explicitly stated
- [ ] Risks and mitigation strategies identified
- [ ] Implementation roadmap provided

## 📝 Deliverables

1. **Investigation Report**: Comprehensive findings document
2. **Decision Documentation**: ADR or recommendation memo
3. **Implementation Plan**: Next steps if investigation supports proceeding
4. **Reference Materials**: Code samples, benchmarks, prototypes

## 🔄 Follow-up Actions

**If Investigation Supports Proceeding**:

- Create implementation issues
- Update project roadmap
- Communicate decision to stakeholders

**If Investigation Recommends Against**:

- Document rationale and alternatives
- Update project priorities
- Consider alternative approaches

## 📚 Reference Documentation

- Related ADRs and prior investigations
- Technical documentation and specifications
- [`construction_best_practices/TDD_WORKFLOW_GUIDE.md`](../construction_best_practices/TDD_WORKFLOW_GUIDE.md)

## 🏷️ Labels

`investigation`, `priority:high`, `effort:medium`, `[component]`

---

**Assignment**: @github-copilot[bot]
**Estimated Effort**: [X hours based on complexity]
```

## 📋 Implementation Template

```markdown
# [Implementation]: [Specific development work to be completed]

## 📋 Implementation Overview

**Summary**: Clear description of what will be implemented

**Business Context**: Why this implementation is needed

**Dependencies**: Prerequisites and related work

## 🎯 Scope & Requirements

### In Scope

- [ ] Specific feature/component 1
- [ ] Specific feature/component 2
- [ ] Testing and documentation

### Out of Scope

- [ ] Related work for future iterations
- [ ] Non-essential enhancements
- [ ] Performance optimizations (unless specified)

## 🏗️ Technical Implementation Plan

### Architecture & Design

**Component Overview**:

- New components to be created
- Existing components to be modified
- Integration points and dependencies

**Design Patterns**:

- Architectural patterns to follow
- Code organization principles
- Error handling strategies

### Implementation Phases

**Phase 1: Foundation (X hours)**

- [ ] Core infrastructure setup
- [ ] Basic functionality implementation
- [ ] Initial testing framework

**Phase 2: Feature Development (X hours)**

- [ ] Main feature implementation
- [ ] Integration with existing systems
- [ ] Comprehensive testing

**Phase 3: Production Readiness (X hours)**

- [ ] Error handling and edge cases
- [ ] Performance optimization
- [ ] Documentation and deployment

## 🧪 Test-Driven Development Approach

**Testing Strategy**:

- [ ] Unit tests for all new functions (≥90% coverage)
- [ ] Integration tests for external service connections
- [ ] Contract tests for API interfaces
- [ ] End-to-end tests for user workflows

**TDD Workflow**:

1. Write failing tests that capture requirements
2. Implement minimal code to pass tests
3. Refactor with green tests
4. Repeat for each feature increment

**Reference**: [`construction_best_practices/TDD_WORKFLOW_GUIDE.md`](../construction_best_practices/TDD_WORKFLOW_GUIDE.md)

## 📊 Quality Assurance

### Code Quality Requirements

- [ ] All code follows project style guidelines
- [ ] Type hints for all function signatures
- [ ] Comprehensive docstrings with business context
- [ ] Error handling with proper recovery strategies

### Performance Requirements

- [ ] Response time targets met
- [ ] Memory usage within acceptable limits
- [ ] No performance regression in existing features

### Security Requirements

- [ ] Input validation and sanitization
- [ ] Proper authentication and authorization
- [ ] Security scan results reviewed

## ✅ Definition of Done

### Implementation Complete

- [ ] All planned features implemented
- [ ] Tests pass with required coverage
- [ ] Code reviewed and approved
- [ ] Documentation updated

### Production Ready

- [ ] Security review completed
- [ ] Performance benchmarks met
- [ ] Error handling validated
- [ ] Deployment scripts tested

### Integration Validated

- [ ] Server startup successful after changes
- [ ] No breaking changes to existing APIs
- [ ] End-to-end workflow functions correctly

## 📚 Reference Documentation

**Required Reading**:

- [`construction_best_practices/CODE_CONSTRUCTION_GUIDE.md`](../construction_best_practices/CODE_CONSTRUCTION_GUIDE.md)
- [`construction_best_practices/TDD_WORKFLOW_GUIDE.md`](../construction_best_practices/TDD_WORKFLOW_GUIDE.md)
- Related README files for components being modified

**Implementation Templates**:

- [`construction_best_practices/MARKDOWN_PLAN_TEMPLATE.md`](../construction_best_practices/MARKDOWN_PLAN_TEMPLATE.md)

## 🏷️ Labels

`implementation`, `priority:medium`, `effort:large`, `[component]`

---

**Assignment**: @github-copilot[bot]
**Estimated Effort**: [X hours based on scope]
```

## 📚 Documentation Template

```markdown
# [Documentation]: [Specific documentation work to be completed]

## 📋 Documentation Overview

**Purpose**: What documentation needs to be created or updated

**Target Audience**: Who will use this documentation

**Integration**: How this fits with existing documentation

## 📝 Documentation Scope

### Content to Create/Update

- [ ] README files for new components
- [ ] API documentation updates
- [ ] User guides or tutorials
- [ ] Architecture decision records (ADRs)

### Documentation Standards

- [ ] Follow project README guidance
- [ ] Include business context and motivation
- [ ] Provide working code examples
- [ ] Test all code samples for accuracy

## 🎯 Content Requirements

### Structure & Organization

- Clear hierarchical organization
- Consistent formatting and style
- Cross-references to related documentation
- Proper file organization in documentation directories

### Content Quality

- Business context for technical decisions
- Step-by-step instructions with examples
- Troubleshooting guides for common issues
- Links to relevant construction best practices

## ✅ Quality Checklist

### Content Validation

- [ ] All code examples tested and working
- [ ] Links verified and functional
- [ ] Grammar and spelling checked
- [ ] Technical accuracy validated

### Integration Validation

- [ ] Consistent with existing documentation style
- [ ] Properly linked from relevant README files
- [ ] Updated in appropriate documentation indices
- [ ] Version control and change tracking in place

## 📚 Reference Standards

**Documentation Guidelines**:

- [`construction_best_practices/README_GUIDANCE.md`](../construction_best_practices/README_GUIDANCE.md)
- [`construction_best_practices/COMMENTING_BEST_PRACTICES.md`](../construction_best_practices/COMMENTING_BEST_PRACTICES.md)

## 🏷️ Labels

`documentation`, `priority:low`, `effort:small`, `[component]`

---

**Assignment**: @github-copilot[bot]
**Estimated Effort**: [X hours based on scope]
```

## 🔄 Refactoring Template

```markdown
# [Refactoring]: [Specific code improvement or restructuring]

## 📋 Refactoring Overview

**Purpose**: What code quality improvements will be made

**Motivation**: Why this refactoring is needed now

**Scope**: What code will be affected

## 🎯 Refactoring Goals

### Code Quality Improvements

- [ ] Reduce code complexity and duplication
- [ ] Improve readability and maintainability
- [ ] Enhance performance or efficiency
- [ ] Strengthen error handling

### Architecture Improvements

- [ ] Better separation of concerns
- [ ] Improved modularity and reusability
- [ ] Enhanced testability
- [ ] Reduced technical debt

## 🔧 Refactoring Approach

**Safety First Principles**:

- Only refactor with green tests
- Make one change at a time
- Preserve external behavior
- Validate each step before proceeding

**Refactoring Techniques**:

- Extract Method/Function for complex logic
- Extract Class for related functionality
- Move Method to appropriate class
- Rename for clarity and consistency

**Reference**: [`construction_best_practices/REFACTORING_BEST_PRACTICES.md`](../construction_best_practices/REFACTORING_BEST_PRACTICES.md)

## 🧪 Testing Strategy

### Pre-Refactoring

- [ ] Comprehensive test suite in place
- [ ] All tests passing before changes
- [ ] Performance baseline established
- [ ] Behavior documentation complete

### During Refactoring

- [ ] Tests remain green after each change
- [ ] New tests added for improved coverage
- [ ] Performance monitored for regressions
- [ ] External interfaces preserved

### Post-Refactoring

- [ ] Final test suite validation
- [ ] Performance comparison to baseline
- [ ] Integration testing complete
- [ ] Code review and approval

## ✅ Success Criteria

### Code Quality Metrics

- [ ] Reduced cyclomatic complexity
- [ ] Eliminated code duplication
- [ ] Improved test coverage
- [ ] Enhanced code readability

### System Health

- [ ] No functional regressions
- [ ] Performance maintained or improved
- [ ] Error handling enhanced
- [ ] Documentation updated

## 🏷️ Labels

`refactoring`, `priority:medium`, `effort:medium`, `[component]`

---

**Assignment**: @github-copilot[bot]
**Estimated Effort**: [X hours based on scope]
```

## 🤖 Copilot Integration Guidelines

### Issue Creation Workflow

1. **Initial Analysis**: Copilot analyzes the request and determines issue type
2. **Template Selection**: Choose appropriate template based on issue classification
3. **Content Generation**: Fill template with specific details and context
4. **Quality Review**: Ensure all required elements are included
5. **Issue Creation**: Submit with proper labels and assignment

### Copilot Responsibilities

**Content Generation**:

- Write clear, comprehensive issue descriptions
- Include all required template sections
- Reference relevant documentation and guides
- Estimate effort based on scope and complexity

**Quality Assurance**:

- Validate all links and references
- Ensure consistency with project standards
- Include proper labels and metadata
- Follow TDD and documentation-first principles

**Follow-up Management**:

- Update issues with progress and findings
- Link related issues and pull requests
- Close issues with summary of completed work
- Update project documentation as needed

## 📋 Issue Labels Reference

### Type Labels

- `bug` - Production issues, errors, failures
- `enhancement` - New features and improvements
- `investigation` - Research and analysis work
- `documentation` - Documentation updates
- `refactoring` - Code quality improvements

### Priority Labels

- `priority:critical` - Blocking production issues
- `priority:high` - Important work, next sprint
- `priority:medium` - Standard priority work
- `priority:low` - Nice-to-have improvements

### Effort Labels

- `effort:small` - 1-4 hours of work
- `effort:medium` - 4-16 hours of work
- `effort:large` - 16+ hours of work

### Component Labels

- `api` - API endpoints and middleware
- `workflow` - Business workflow components
- `database` - Database operations and storage
- `frontend` - UI components and static files
- `docs` - Documentation and guides
- `infrastructure` - CI/CD, deployment, configuration

### Status Labels

- `needs-human-review` - Requires human input
- `blocked` - Waiting on external dependencies
- `in-progress` - Currently being worked on
- `ready-for-review` - Implementation complete, needs review

## 🔗 Integration with Project Workflow

### With Construction Best Practices

- All issues reference relevant construction guides
- Implementation issues include TDD workflow requirements
- Documentation standards enforced in all templates

### With Markdown Planning

- Investigation issues produce ADRs or implementation plans
- Implementation issues reference plan templates
- All work follows documentation-first approach

### With GitHub Workflow

- Issues automatically assigned to Copilot
- Labels enable project management and filtering
- Links connect issues to PRs and documentation

## 📚 Reference Documentation

**Construction Best Practices**:

- [`TDD_WORKFLOW_GUIDE.md`](TDD_WORKFLOW_GUIDE.md)
- [`CODE_CONSTRUCTION_GUIDE.md`](CODE_CONSTRUCTION_GUIDE.md)
- [`COMMENTING_BEST_PRACTICES.md`](COMMENTING_BEST_PRACTICES.md)
- [`README_GUIDANCE.md`](README_GUIDANCE.md)
- [`REFACTORING_BEST_PRACTICES.md`](REFACTORING_BEST_PRACTICES.md)

**Markdown Planning**:

- [`MARKDOWN_PLAN_TEMPLATE.md`](MARKDOWN_PLAN_TEMPLATE.md)
- [`MARKDOWN_PLAN_TEMPLATE_USAGE.md`](MARKDOWN_PLAN_TEMPLATE_USAGE.md)

---

**Version**: 1.0.0  
**Last Updated**: August 22, 2025  
**Maintained By**: Development Team  
**Integration**: GitHub Copilot Instructions, Construction Best Practices
