# Code Quality Practices Documentation

This directory contains comprehensive guides for maintaining high code quality standards in our Python LangGraph/LangSmith project.

## 📚 Available Guidance Documents

### Development Workflow & Standards

- **[ARCHITECTURE_GUIDE.md](ARCHITECTURE_GUIDE.md)** - System architecture principles and patterns (includes async programming for LangGraph)
- **[TDD_WORKFLOW_GUIDE.md](TDD_WORKFLOW_GUIDE.md)** - Test-driven development process
- **[TESTING_QUALITY_GUIDE.md](TESTING_QUALITY_GUIDE.md)** - Comprehensive testing standards
- **[INTEGRATION_PLAYBOOK_GUIDE.md](INTEGRATION_PLAYBOOK_GUIDE.md)** - External service integration playbook (11-step process)
- **[ASYNC_PROGRAMMING_LANGGRAPH_GUIDE.md](ASYNC_PROGRAMMING_LANGGRAPH_GUIDE.md)** - Comprehensive async programming for LangGraph workflows
- **[ASYNC_QUICK_REFERENCE.md](ASYNC_QUICK_REFERENCE.md)** - Quick async patterns and debugging reference

### Code Construction & Quality

- **[CODE_CONSTRUCTION_GUIDE.md](CODE_CONSTRUCTION_GUIDE.md)** - Writing maintainable Python code
- **[COMMENTING_BEST_PRACTICES.md](COMMENTING_BEST_PRACTICES.md)** - Effective code documentation
- **[VARIABLE_NAMING_GUIDE.md](VARIABLE_NAMING_GUIDE.md)** - Consistent naming conventions
- **[WORKING_WITH_STRINGS_GUIDE.md](WORKING_WITH_STRINGS_GUIDE.md)** - String handling best practices

### Development Environment & Tools

- **[python-dependency-cache-guidance.md](python-dependency-cache-guidance.md)** - Dependency management and caching
- **[DEBUGGING_ERROR_HANDLING_GUIDE.md](DEBUGGING_ERROR_HANDLING_GUIDE.md)** - Error handling strategies
- **[REFACTORING_BEST_PRACTICES.md](REFACTORING_BEST_PRACTICES.md)** - Safe refactoring techniques

### Project Management & Documentation

- **[README_GUIDANCE.md](README_GUIDANCE.md)** - Writing effective README files
- **[COVERAGE_REQUIREMENTS_UPDATED.md](COVERAGE_REQUIREMENTS_UPDATED.md)** - Code coverage standards
- **[MARKDOWN_PLAN_TEMPLATE.md](MARKDOWN_PLAN_TEMPLATE.md)** - Standardized planning template
- **[MARKDOWN_PLAN_TEMPLATE_USAGE.md](MARKDOWN_PLAN_TEMPLATE_USAGE.md)** - Template usage guidelines

## 🎯 How to Use These Guides

### For Development Workflow

1. **Start with TDD_WORKFLOW_GUIDE.md** - Essential for all code changes
2. **Check INTEGRATION_PLAYBOOK_GUIDE.md** - Required for all external service integrations
3. **Check ASYNC_PROGRAMMING_LANGGRAPH_GUIDE.md** - Required for LangGraph workflow development
4. **Create plan with MARKDOWN_PLAN_TEMPLATE.md** - Required for work >4 hours
5. **Reference COMMENTING_BEST_PRACTICES.md** - Required for all implementations
6. **Check specific guides** based on your task:
   - External service integration → INTEGRATION_PLAYBOOK_GUIDE.md
   - Async operations in LangGraph → ASYNC_PROGRAMMING_LANGGRAPH_GUIDE.md or ASYNC_QUICK_REFERENCE.md
   - Working with text/strings → WORKING_WITH_STRINGS_GUIDE.md
   - Writing tests → TESTING_QUALITY_GUIDE.md
   - Designing architecture → ARCHITECTURE_GUIDE.md
   - Improving existing code → REFACTORING_BEST_PRACTICES.md

### For Planning & Investigation

1. **Use MARKDOWN_PLAN_TEMPLATE.md** for all implementation plans
2. **Reference MARKDOWN_PLAN_TEMPLATE_USAGE.md** for template guidelines
3. **Include mandatory sections**: TDD approach, Code Construction guidelines, server startup validation
4. **Follow file organization**: Plans in appropriate directories (docs/implementation/, dev-tools/scripts/investigation/, etc.)

### For Code Reviews

- Use these guides as checklists to ensure code quality standards
- Reference specific sections when providing feedback
- Validate that code follows the documented patterns and practices

### For Onboarding

- New team members should read TDD_WORKFLOW_GUIDE.md first
- Then review COMMENTING_BEST_PRACTICES.md and ARCHITECTURE_GUIDE.md
- Refer to other guides as needed for specific tasks

## 🔄 Integration with Main Instructions

These detailed guides are referenced by the main `.github/copilot-instructions.md` file, which provides:

- Quick reference sections for daily development
- Links to comprehensive guidance in these files
- Definition of Done checklists
- Essential commands and workflows

## �️ Usage Examples

### Setting Up Development Environment

```bash
# Quick start with dependency management
python -m venv .venv
source .venv/bin/activate
pip install -e .[dev]

# Reference: python-dependency-cache-guidance.md
```

### Running TDD Workflow

```bash
# Start with failing tests (see TDD_WORKFLOW_GUIDE.md)
pytest tests/unit_tests/test_new_feature.py::test_should_fail -v

# Follow TDD cycle: Red → Green → Refactor
pytest -m "unit or node" --cov=src --cov-fail-under=90
```

### Code Quality Checks

```bash
# Pre-commit validation (automated via hooks)
pre-commit run --all-files

# Manual quality checks
ruff check . && black --check . && mypy src/
```

### Environment Cleanup

```bash
# Safe cache cleanup (see python-dependency-cache-guidance.md)
./dev-tools/scripts/cleanup-caches.sh

# Check for file duplications
./dev-tools/scripts/check_duplicates.sh
```

## �📝 Maintenance

- **Keep guides up-to-date** with project evolution
- **Add examples** from real project code when patterns emerge
- **Update cross-references** when guide structure changes
- **Validate practices** against actual development workflow

---

**Remember: These guides serve as the single source of truth for code quality standards. Always reference the appropriate guide before starting any development work! 📖✅**
