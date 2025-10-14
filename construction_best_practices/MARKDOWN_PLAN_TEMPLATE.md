# [PLAN_TYPE] Plan: [DESCRIPTIVE_TITLE]

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

CHARACTER LIMIT REQUIREMENT:
This markdown file MUST remain under 65,536 characters total.
Current count: [Run: wc -c filename.md to check]
Use concise language and focus on essential information only.
-->

## 📋 Overview

**Purpose**: [Clear statement of what this plan aims to accomplish]  
**Approach**: [High-level methodology or strategy]  
**Success Criteria**: [Specific, measurable outcomes that define completion]

### Business Context

[Explain WHY this work is needed from a business perspective, not just WHAT will be done]

### Integration with Project Standards

**📖 Required Reading Before Implementation**:

- [ ] **Code Construction Guidelines**: [`construction_best_practices/CODE_CONSTRUCTION_GUIDE.md`](construction_best_practices/CODE_CONSTRUCTION_GUIDE.md)
- [ ] **README for Target Module**: [Link to relevant README]
- [ ] **Related Documentation**: [List any domain-specific docs]

---

## 🎯 Requirements & Acceptance Criteria

### Functional Requirements

1. **[Requirement Category 1]**

   - [ ] Specific deliverable 1
   - [ ] Specific deliverable 2
   - [ ] Specific deliverable 3

2. **[Requirement Category 2]**
   - [ ] Specific deliverable 1
   - [ ] Specific deliverable 2

### Non-Functional Requirements

- **Performance**: [Specific performance criteria]
- **Security**: [Security considerations and requirements]
- **Maintainability**: [Code quality and maintenance requirements]
- **Documentation**: [Documentation requirements]

### Acceptance Criteria

- [ ] All functional requirements implemented and tested
- [ ] Unit test coverage ≥85% for new/modified code
- [ ] All tests pass (unit, integration, e2e as applicable)
- [ ] Documentation updated (README, code comments, architecture docs)
- [ ] Code follows project standards (formatting, naming, construction practices)
- [ ] Security review completed (if applicable)
- [ ] Performance benchmarks met (if applicable)
- [ ] Server starts up successfully after changes

---

## 🧪 Test-Driven Development Approach

### Test Strategy

**📖 Reference**: [`construction_best_practices/TDD_WORKFLOW_GUIDE.md`](construction_best_practices/TDD_WORKFLOW_GUIDE.md)

1. **Test Categories**:

   - [ ] Unit tests (@pytest.mark.unit)
   - [ ] Node tests (@pytest.mark.node) - if LangGraph components
   - [ ] Integration tests (@pytest.mark.integration)
   - [ ] End-to-end tests (@pytest.mark.e2e) - if applicable

2. **Test Development Process**:
   - [ ] Write failing tests FIRST that capture acceptance criteria
   - [ ] Write comments-first pseudocode design
   - [ ] Implement minimal code to pass tests
   - [ ] Refactor with green tests

### Coverage Requirements

```bash
# Target coverage validation commands
pytest -m "unit or node" -q --cov=src --cov-fail-under=85
pytest --cov=src --cov-fail-under=85 --cov-report=html
```

---

## 🏗️ Implementation Plan

### Phase 1: [Phase Name] ([Estimated Time])

**Objective**: [What this phase accomplishes]

#### 1.1 [Subphase Name]

**Tasks**:

- [ ] Task 1 with acceptance criteria
- [ ] Task 2 with acceptance criteria
- [ ] Task 3 with acceptance criteria

**Implementation Notes**:

```bash
# Example commands or code snippets
command_example --flag value
```

**Validation**:

- [ ] Specific validation criteria
- [ ] Tests pass: `pytest path/to/tests/`
- [ ] Manual verification steps

#### 1.2 [Subphase Name]

[Repeat structure for each subphase]

### Phase 2: [Phase Name] ([Estimated Time])

[Repeat structure for each phase]

---

## 📊 Quality Assurance & Validation

### Code Quality Checklist

**Pre-Implementation**:

- [ ] README.md consulted for business context
- [ ] README created/updated for new modules or significant changes
- [ ] Appropriate guides referenced (TDD, Commenting, Testing, Architecture, etc.)

**During Implementation**:

- [ ] Comments-first pseudocode completed before coding
- [ ] Defensive programming practices applied
- [ ] Input validation and error handling implemented
- [ ] Variable names follow self-explanatory naming standards
- [ ] String operations follow constants and validation standards
- [ ] Backwards compatibility: not required

**Post-Implementation**:

- [ ] Remove old implementations and unit tests whose functionality we are
      replacing (if it applies for this task)
- [ ] All tests pass with appropriate markers (we should make sure as many tests pass as possible, and not use skip markers as much as possible - this ensures complete coverage with maximizes our chances that the code commit will not break the workflow execution)
- [ ] Business logic comments explain "why" decisions were made
- [ ] All public functions have comprehensive docstrings
- [ ] Coverage maintained or improved (≥85%)
- [ ] No duplicate files created
- [ ] Development files properly organized
- [ ] References updated after any file moves
- [ ] Root directory kept clean

### Implementation Gap Analysis

**Critical Final Step**: Before finalizing the commit, conduct a comprehensive analysis of plan vs. actual implementation to identify any remaining gaps.

**Gap Analysis Process**:

1. **Requirements Review**:

   - [ ] Compare implemented features against all functional requirements
   - [ ] Verify all acceptance criteria have been met
   - [ ] Check that all planned phases/tasks were completed

2. **Integration Assessment**:

   - [ ] Verify all planned integrations are functional end-to-end
   - [ ] Confirm all API endpoints are properly mounted and accessible
   - [ ] Test all workflow connections and data flow paths

3. **Testing Coverage Analysis**:

   - [ ] Ensure all new/modified components have corresponding tests
   - [ ] Verify integration tests cover all planned integration points
   - [ ] Confirm end-to-end tests validate complete user workflows

4. **🚨 Mock Implementation Detection (CRITICAL)**:

   - [ ] Search for mock/placeholder patterns in implementation
   - [ ] Verify all API endpoints have real business logic (not just success responses)
   - [ ] Check that external integrations actually connect to real services
   - [ ] Confirm database operations persist/retrieve actual data
   - [ ] Validate workflow steps perform intended business logic

   **Detection Commands**:

   ```bash
   grep -r "mock\|placeholder\|TODO\|FIXME" src/ --include="*.py"
   grep -r "return {}\|return \[\]\|return.*success.*true" src/ --include="*.py"
   ```

5. **Documentation Gap Check**:
   - [ ] All planned documentation updates completed
   - [ ] No broken cross-references or outdated information
   - [ ] Business context documented for future maintainers

**Gap Documentation**:

```markdown
## Implementation Status Assessment

### ✅ Fully Implemented

- [List completed requirements with brief validation notes]

### ⚠️ Partially Implemented

- [List partially completed items with specific gaps identified]

### ❌ Not Implemented

- [List unimplemented requirements with reasons/blockers]

### � Mock Implementations Found

- **API Endpoints**: [List endpoints with mock responses]
- **Service Methods**: [List service methods with placeholder logic]
- **Integration Points**: [List external integrations not fully implemented]
- **Database Operations**: [List DB operations that don't persist real data]
- **Workflow Steps**: [List LangGraph nodes with placeholder logic]

### �🔄 Next Steps Required

- [Prioritized list of remaining work for future implementation]

### 🧪 Validation Results

- [Summary of test results and any test gaps]
- [End-to-end workflow validation status]
```

**Handoff Requirements**:

- [ ] Clear documentation of implementation gaps for next developer
- [ ] Prioritized next steps with estimated effort
- [ ] Any blocking issues or dependencies identified
- [ ] Complete status summary for project stakeholders

### Integration Validation

- [ ] Branch organization - merge all separated commits created during development into one commit with one final commit message using git reset --soft

```bash
# Complete validation sequence
./dev-tools/scripts/prepare-commit.sh --skip-rebase

# Individual validation commands
black . && isort . && ruff check . && mypy src/
pytest -m "unit or node" -x -q --cov=src --cov-fail-under=85
pytest -m "not live" -v
```

### Server Startup Validation

**Critical Requirement**: Confirm server starts up successfully after all changes

```bash
# LangGraph server startup test
cd /path/to/project
source .venv/bin/activate
langgraph dev

# Expected: Server starts without critical errors
# Expected: Port binding successful
# Expected: Health endpoint responds
# Expected: No immediate crashes or exceptions
```

### Complete Workflow Testing

**Requirement**: Verify each node and component of the workflow executes successfully all the way through to the end of the workflow.

**Use existing testing tools and update as needed to ensure complete workflow execution:**

```bash
# Quick workflow validation (recommended for most implementations)
python dev-tools/scripts/testing/test-workflow.py --json

# Comprehensive end-to-end testing with multiple scenarios
python dev-tools/scripts/testing/test-langgraph-client.py --test-type full

# Automated testing with server startup and cleanup
./dev-tools/scripts/testing/quick-test-langgraph.sh empty

# Integration testing via pytest for workflow components
pytest tests/integration_tests/human_review/test_complete_workflow.py -v
```

**Success Criteria**:

- [ ] Workflow completes without errors (`status: "success"`)
- [ ] All workflow nodes execute successfully
- [ ] Test reaches the final workflow state
- [ ] No unhandled exceptions or interrupts
- [ ] Integration tests pass with proper component interaction

**Validation Process**:

1. [ ] Send test request using existing tools
2. [ ] Identify and fix any errors that prevent completion
3. [ ] Update node integration tests as needed for new/modified components
4. [ ] Repeat until complete workflow execution is verified

---

## 🔄 Risk Management & Contingency

### Identified Risks

1. **[Risk Category 1]**

   - **Risk**: [Description of potential issue]
   - **Impact**: [High/Medium/Low]
   - **Mitigation**: [Steps to prevent or address]

2. **[Risk Category 2]**
   - **Risk**: [Description of potential issue]
   - **Impact**: [High/Medium/Low]
   - **Mitigation**: [Steps to prevent or address]

### Rollback Strategy

- [ ] **Backup Plan**: [What to do if implementation fails]
- [ ] **Rollback Steps**: [Specific steps to undo changes]
- [ ] **Data Safety**: [How to protect data during rollback]

---

## 📚 Documentation Updates

### Required Documentation Updates

- [ ] **README Updates**: [List README files that need updates]
- [ ] **Architecture Documentation**: [Any architecture docs to update]
- [ ] **API Documentation**: [API docs if applicable]
- [ ] **User Documentation**: [User-facing docs if applicable]
- [ ] **Operations Documentation**: [Deployment/ops docs if applicable]

### Documentation Quality Standards

**📖 Reference**: [`construction_best_practices/README_GUIDANCE.md`](construction_best_practices/README_GUIDANCE.md)

- [ ] Documentation includes business context (WHY not just WHAT)
- [ ] Code examples are tested and working
- [ ] Cross-references are accurate and up-to-date
- [ ] Documentation follows project formatting standards

---

## 🔗 Dependencies & Integration

### Prerequisites

- [ ] [Dependency 1]: [Why needed and how to verify]
- [ ] [Dependency 2]: [Why needed and how to verify]

### Integration Points

- [ ] **[System/Component 1]**: [How this plan integrates]
- [ ] **[System/Component 2]**: [How this plan integrates]

### Impact Analysis

**Affected Components**:

- [Component 1]: [How it's affected]
- [Component 2]: [How it's affected]

**Breaking Changes**:

- [ ] No breaking changes expected
- [ ] Breaking changes identified and migration plan created

---

## 📈 Success Metrics & Monitoring

### Quantitative Metrics

- **Performance**: [Specific performance measurements]
- **Quality**: [Code quality metrics]
- **Coverage**: [Test coverage targets]
- **Reliability**: [Reliability measurements]

### Qualitative Metrics

- **Developer Experience**: [How this improves developer workflow]
- **Maintainability**: [How this improves code maintainability]
- **User Experience**: [How this improves user experience if applicable]

### Monitoring & Alerting

- [ ] **Monitoring Setup**: [What to monitor after implementation]
- [ ] **Alert Configuration**: [What alerts to configure]
- [ ] **Dashboard Updates**: [Dashboard updates needed]

---

## 🧹 Cleanup & Organization

### File Organization Requirements

**📖 Reference**: [`.github/copilot-instructions.md`](.github/copilot-instructions.md) - File Organization section

- [ ] **No duplicate files**: Run duplication detection commands
- [ ] **Proper organization**: Scripts in `dev-tools/scripts/`, logs in `logs/`, CI/CD in `cicd/`
- [ ] **Updated references**: All paths corrected after file moves
- [ ] **Clean root directory**: No development artifacts in project root

### Cleanup Checklist

- [ ] Remove temporary files and unused code
- [ ] Update import statements and references
- [ ] Clean up test files (remove debugging code)
- [ ] Remove commented-out code (unless needed for documentation)
- [ ] Ensure useful testing/utility scripts are preserved if valuable

---

## 🚀 Deployment & Release

### Deployment Checklist

- [ ] **Environment Preparation**: [Steps to prepare deployment environment]
- [ ] **Database Migrations**: [Any database changes needed]
- [ ] **Configuration Updates**: [Configuration changes needed]
- [ ] **Feature Flags**: [Feature flag considerations]

### Release Process

1. **Pre-Release Validation**:

   - [ ] All tests pass in CI/CD pipeline
   - [ ] Manual testing completed
   - [ ] Documentation reviewed and approved
   - [ ] Security review completed (if applicable)

2. **Release Execution**:

   - [ ] Deployment to staging environment
   - [ ] Staging validation
   - [ ] Production deployment
   - [ ] Post-deployment validation

3. **Post-Release Monitoring**:
   - [ ] Monitor application metrics
   - [ ] Check error rates and performance
   - [ ] Validate functionality in production
   - [ ] Monitor user feedback

---

## 📝 Implementation Log

### Progress Tracking

| Date         | Phase/Task | Status         | Notes                  |
| ------------ | ---------- | -------------- | ---------------------- |
| [YYYY-MM-DD] | Phase 1.1  | ✅ Complete    | [Implementation notes] |
| [YYYY-MM-DD] | Phase 1.2  | 🔄 In Progress | [Current status]       |
| [YYYY-MM-DD] | Phase 2.1  | ⏸️ Blocked     | [Blocking issue]       |

### Decisions & Rationale

**Decision Log**:

- **[Date]**: [Decision made] - [Rationale for decision]
- **[Date]**: [Decision made] - [Rationale for decision]

### Lessons Learned

- **What Worked Well**: [Successful approaches and techniques]
- **What Could Be Improved**: [Areas for improvement in future plans]
- **Recommendations**: [Recommendations for similar future work]

---

## 🔚 Plan Completion

### Final Validation Checklist

- [ ] **All acceptance criteria met**
- [ ] **Test coverage ≥85% achieved**
- [ ] **Documentation updated and reviewed**
- [ ] **Code quality standards met**
- [ ] **Server startup validated**
- [ ] **Integration testing completed**
- [ ] **Security review completed (if applicable)**
- [ ] **Performance benchmarks met (if applicable)**
- [ ] **Cleanup completed**
- [ ] **Deployment successful (if applicable)**
- [ ] **Character limit compliance**: Plan file is under 65,536 characters (`wc -c filename.md`)

### Sign-off

- [ ] **Technical Lead Approval**: [Name/Date]
- [ ] **Code Review Completed**: [PR#/Date]
- [ ] **QA Validation**: [Name/Date]
- [ ] **Documentation Review**: [Name/Date]

### Next Steps

- **Immediate Follow-up**: [Any immediate actions needed]
- **Future Enhancements**: [Planned future improvements]
- **Related Work**: [Links to related plans or issues]

---

**Plan Status**: [Draft | In Progress | Under Review | Approved | Complete]  
**Last Updated**: [YYYY-MM-DD]  
**Next Review Date**: [YYYY-MM-DD]
