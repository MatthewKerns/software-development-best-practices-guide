# Markdown Plan Template Usage Guidelines

## 📋 Overview

**This guide explains how to use the standardized markdown plan template to ensure consistent, comprehensive planning that follows project best practices.**

The template is designed to enforce:
- **Code Construction Best Practices** integration
- **Test-Driven Development** approach
- **Documentation-first** workflow
- **Quality assurance** standards
- **Server startup validation**
- **File organization** requirements

---

## 🎯 When to Use the Template

### Plan Types and Template Usage

| Plan Type | Template Usage | File Location | Example |
|-----------|----------------|---------------|---------|
| **Implementation Plans** | Required | `docs/implementation/` | Feature development, UI changes, system integrations |
| **Investigation Plans** | Required | `dev-tools/scripts/investigation/` | Bug analysis, performance investigation, research |
| **Architecture Plans** | Required | `docs/adr/` | Architectural decisions, system design changes |
| **Testing Plans** | Required | `dev-tools/test-results/` | Test strategy, testing framework changes |
| **Operations Plans** | Required | `cicd/` | Deployment, CI/CD, infrastructure changes |

### Mandatory Template Use

**The template MUST be used for:**
- All new feature implementations
- Architecture changes or decisions
- Investigation of complex issues
- Testing strategy changes
- Any work requiring >4 hours of effort

**The template MAY be simplified for:**
- Simple bug fixes (<2 hours)
- Documentation-only updates
- Configuration changes

---

## 🏗️ Template Structure Guide

### Metadata Section (Required)

```markdown
<!-- 
METADATA SECTION - Fill in all required fields
Plan Type: [Implementation | Investigation | Architecture | Testing | Operations]
Author: [Your Name]
Created: [YYYY-MM-DD]
Last Updated: [YYYY-MM-DD]
Version: [1.0.0]
Related Issue: [#123]
Priority: [High | Medium | Low]
Estimated Effort: [Hours/Days]
Dependencies: [List any prerequisites]
-->
```

**Metadata Guidelines:**
- **Plan Type**: Choose the most specific type that applies
- **Version**: Use semantic versioning (1.0.0, 1.1.0, 2.0.0)
- **Estimated Effort**: Be realistic; add 25% buffer for unexpected issues
- **Dependencies**: List technical and business dependencies

### Core Sections (All Required)

#### 1. Overview Section
- **Purpose**: Clear, one-sentence statement of goals
- **Approach**: High-level strategy (not implementation details)
- **Success Criteria**: Specific, measurable outcomes
- **Business Context**: WHY this work matters (not just WHAT)

#### 2. Requirements & Acceptance Criteria
- Break down into functional and non-functional requirements
- Use checkboxes for trackable deliverables
- Include specific acceptance criteria for each requirement
- Always include coverage and testing requirements

#### 3. Test-Driven Development Approach
- **MANDATORY**: Reference TDD workflow guide
- Define test strategy BEFORE implementation planning
- Specify test categories and markers
- Include coverage validation commands

#### 4. Implementation Plan
- Break work into phases and subphases
- Include time estimates for each phase
- Provide validation steps for each phase
- Include example commands and code snippets

#### 5. Quality Assurance & Validation
- **MANDATORY**: Include complete quality checklist
- Specify validation commands and procedures
- **CRITICAL**: Include server startup validation
- Reference all relevant quality guides

### Optional Sections (Use When Applicable)

#### Risk Management & Contingency
- Include for complex or high-risk implementations
- Always include rollback strategy for production changes
- Identify technical and business risks

#### Documentation Updates
- Required when creating new modules or changing APIs
- Include specific documentation files to update
- Reference documentation quality standards

#### Dependencies & Integration
- Required when work affects multiple systems
- Include impact analysis for affected components
- Identify any breaking changes

---

## 📝 Content Guidelines

### Writing Style Standards

**Tone**: Professional, clear, and actionable
**Perspective**: Use imperative mood for actions ("Implement", "Test", "Validate")
**Clarity**: Prefer simple, direct language over complex technical jargon
**Specificity**: Provide concrete examples and specific criteria

### Formatting Conventions

#### Headings Hierarchy
```markdown
# Plan Title (H1)
## Major Sections (H2)
### Subsections (H3)
#### Sub-subsections (H4)
```

#### Code Blocks
```markdown
# Command examples with comments
command --flag value  # Explanation of what this does

# Multi-line code blocks with syntax highlighting
```python
def example_function():
    """Example with proper docstring."""
    return "formatted_correctly"
```

#### Links and References
```markdown
# Internal project links (preferred)
[Guide Name](path/to/guide.md)

# External links (when necessary)
[External Resource](https://example.com)

# Issue references
Fixes #123
Related to #456
```

#### Task Lists and Progress Tracking
```markdown
# Standard checkbox format
- [ ] Incomplete task
- [x] Completed task

# Progress tracking with status indicators
| Task | Status | Notes |
|------|--------|-------|
| Implementation | ✅ Complete | Merged in PR #123 |
| Testing | 🔄 In Progress | 80% coverage achieved |
| Documentation | ⏸️ Blocked | Waiting for API finalization |
```

### Decision Documentation Standards

**Decision Format**:
```markdown
**Decision**: [What was decided]
**Rationale**: [Why this decision was made]
**Alternatives Considered**: [Other options that were evaluated]
**Trade-offs**: [What we're gaining vs. what we're sacrificing]
**Implementation Impact**: [How this affects implementation]
```

**Context Requirements**:
- Include business context for all decisions
- Explain trade-offs and alternatives considered
- Document assumptions and constraints
- Reference relevant architectural principles

---

## 🔄 Template Workflow

### 1. Plan Creation Process

```bash
# Step 1: Copy template to appropriate location
cp construction_best_practices/MARKDOWN_PLAN_TEMPLATE.md docs/implementation/MY_FEATURE_PLAN.md

# Step 2: Fill in metadata section completely
# Step 3: Customize sections for your specific plan type
# Step 4: Remove unused optional sections
# Step 5: Review checklist compliance before starting work
```

### 2. Required Reading Before Using Template

**MANDATORY**: Read these guides before creating any plan:
- [`construction_best_practices/CODE_CONSTRUCTION_GUIDE.md`](CODE_CONSTRUCTION_GUIDE.md)
- [`construction_best_practices/TDD_WORKFLOW_GUIDE.md`](TDD_WORKFLOW_GUIDE.md)
- [`construction_best_practices/README_GUIDANCE.md`](README_GUIDANCE.md)
- Target module README for business context

### 3. Plan Review Process

#### Self-Review Checklist

Before submitting plan for review:
- [ ] All metadata fields completed
- [ ] Business context clearly explained
- [ ] Test strategy defined before implementation
- [ ] Quality checklist included and customized
- [ ] Server startup validation included
- [ ] File organization requirements addressed
- [ ] Acceptance criteria are specific and measurable
- [ ] Time estimates are realistic with buffer

#### Peer Review Guidelines

**Reviewers should validate:**
- Business context is clear and compelling
- Technical approach is sound and follows project standards
- Test strategy is comprehensive and follows TDD principles
- Quality requirements are appropriate and measurable
- Risk assessment is thorough (for complex plans)
- Documentation plan is adequate

#### Approval Criteria

Plans must be approved before implementation begins if:
- Estimated effort >8 hours
- Changes affect multiple systems
- Introduces new architectural patterns
- Has potential for breaking changes
- Requires database migrations

---

## 🎨 Plan Type Customizations

### Implementation Plans

**Focus Areas**:
- Feature specifications and user stories
- Technical architecture and design patterns
- Database schema changes
- API design and contracts
- UI/UX considerations

**Required Sections**:
- Test-Driven Development Approach
- Implementation Plan with phases
- Quality Assurance & Validation
- Server Startup Validation

**Optional Sections**:
- Risk Management (for complex features)
- Dependencies & Integration
- Deployment & Release

### Investigation Plans

**Focus Areas**:
- Problem statement and symptoms
- Investigation methodology
- Data collection and analysis plan
- Hypothesis testing approach
- Recommendations and next steps

**Required Sections**:
- Investigation methodology
- Quality assurance for analysis
- Documentation of findings

**Optional Sections**:
- Implementation plan (if investigation leads to changes)
- Risk management (for production investigations)

### Architecture Plans

**Focus Areas**:
- Architecture decision records (ADRs)
- System design and component interactions
- Technology choices and trade-offs
- Migration strategies
- Long-term implications

**Required Sections**:
- Context and problem statement
- Decision rationale with alternatives
- Implementation impact analysis
- Quality and validation approach

**Optional Sections**:
- Migration planning
- Risk assessment
- Monitoring and metrics

---

## 🧪 Example Templates

### Quick Implementation Plan Template

For simple features (2-8 hours):

```markdown
# Implementation Plan: [Feature Name]

## Overview
**Purpose**: [One sentence goal]
**Acceptance Criteria**: [Specific, testable outcomes]

## TDD Approach
- [ ] Write failing tests first
- [ ] Implement minimal code to pass
- [ ] Coverage target: 85%

## Implementation Steps
1. [ ] [Step 1 with validation]
2. [ ] [Step 2 with validation]
3. [ ] [Step 3 with validation]

## Quality Validation
- [ ] Tests pass: `pytest path/to/tests/`
- [ ] Coverage: `pytest --cov=src --cov-fail-under=85`
- [ ] Server starts: `langgraph dev`
- [ ] Code quality: `black . && ruff check .`

## Server Startup Validation
```bash
langgraph dev
# Expected: Server starts without errors
```
```

### Investigation Plan Template

For bug analysis and research:

```markdown
# Investigation Plan: [Issue Description]

## Problem Statement
**Symptoms**: [What we're observing]
**Impact**: [Business/technical impact]
**Context**: [When/where it occurs]

## Investigation Methodology
1. [ ] [Data collection step]
2. [ ] [Analysis approach]
3. [ ] [Hypothesis testing]

## Expected Outcomes
- [ ] Root cause identified
- [ ] Reproduction steps documented
- [ ] Fix recommendations provided
```

---

## ✅ Template Compliance Validation

### Automated Checks

```bash
# Validate plan structure
./dev-tools/scripts/validation/validate-plan-template.sh docs/implementation/

# Check for required sections
grep -q "## 🧪 Test-Driven Development Approach" plan.md || echo "Missing TDD section"

# Verify server startup validation
grep -q "Server Startup Validation" plan.md || echo "Missing server validation"
```

### Manual Validation Checklist

Before using any plan:
- [ ] All required sections present
- [ ] Metadata completely filled out
- [ ] Business context clearly explained
- [ ] Test strategy defined
- [ ] Quality checklist customized
- [ ] Server startup validation included
- [ ] Acceptance criteria specific and measurable
- [ ] File organization addressed

---

## 🚀 Integration with Development Workflow

### Copilot Instructions Integration

The template is designed to work seamlessly with our Copilot instructions:

1. **Documentation-First**: Template enforces README consultation
2. **TDD Workflow**: Template includes mandatory TDD section
3. **Quality Standards**: Template includes complete quality checklist
4. **File Organization**: Template enforces proper file placement

### Git Workflow Integration

```bash
# Create plan before starting work
cp construction_best_practices/MARKDOWN_PLAN_TEMPLATE.md docs/implementation/feature-x-plan.md

# Fill out plan and get approval
git add docs/implementation/feature-x-plan.md
git commit -m "plan: Add implementation plan for feature X"

# Implement following the plan
# ... implementation work ...

# Validate completion against plan
./dev-tools/scripts/prepare-commit.sh
```

### CI/CD Integration

Plans can be validated in CI/CD pipeline:
- Check that implementation plans exist for large PRs
- Validate plan structure and required sections
- Ensure acceptance criteria are met before merge

---

## 📊 Best Practices and Anti-Patterns

### Best Practices ✅

- **Start with business context**: Always explain WHY before WHAT
- **Be specific with acceptance criteria**: Use measurable, testable criteria
- **Include realistic time estimates**: Add 25% buffer for unexpected issues
- **Plan for testing first**: Define test strategy before implementation
- **Document decisions and trade-offs**: Future maintainers will thank you
- **Keep plans updated**: Update as implementation progresses
- **Use checkboxes for tracking**: Makes progress visible and satisfying

### Anti-Patterns ❌

- **Implementation without planning**: No plan for >4 hour tasks
- **Vague acceptance criteria**: "Make it work" is not acceptance criteria
- **Skipping test strategy**: TDD section is mandatory
- **Missing business context**: Technical details without business rationale
- **Unrealistic estimates**: Overly optimistic timelines
- **Stale plans**: Plans that don't match actual implementation
- **Template cargo-culting**: Including sections just because they're in template

---

## 🔗 Related Resources

### Project Documentation
- [Code Construction Guide](CODE_CONSTRUCTION_GUIDE.md)
- [TDD Workflow Guide](TDD_WORKFLOW_GUIDE.md)
- [README Guidance](README_GUIDANCE.md)
- [Testing Quality Guide](TESTING_QUALITY_GUIDE.md)

### External Resources
- [Architecture Decision Records (ADRs)](https://adr.github.io/)
- [Writing Good User Stories](https://www.mountaingoatsoftware.com/agile/user-stories)
- [Test-Driven Development Best Practices](https://martinfowler.com/bliki/TestDrivenDevelopment.html)

### Template Files
- [Base Template](MARKDOWN_PLAN_TEMPLATE.md)
- [Example Implementation Plan](../docs/implementation/EXAMPLE_IMPLEMENTATION_PLAN.md)
- [Example Investigation Plan](../dev-tools/scripts/investigation/EXAMPLE_INVESTIGATION_PLAN.md)

---

**Last Updated**: 2025-01-25  
**Version**: 1.0.0  
**Maintained by**: Development Team