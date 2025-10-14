# Software Development Best Practices Guide

A comprehensive collection of software engineering best practices, coding guidelines, and AI agent instructions developed through 7+ years of professional experience, including work at Amazon and startup environments.

## Overview

This repository contains battle-tested guidelines for building maintainable, scalable, and production-ready software. It emphasizes leveraging AI coding agents (Claude Code, GitHub Copilot) while maintaining rigorous quality standards.

## Philosophy

**AI as a Force Multiplier**: AI coding agents excel at generating 80-90% of code quickly, but require human oversight for the critical 10-20% that can make or break a project. As software engineers, our role has evolved to be more reading-heavy—validating AI outputs with the same rigor we'd apply to any code review.

## Repository Contents

### 📋 Agent Instructions

- **[CLAUDE.md](./CLAUDE.md)** - Comprehensive instructions for Claude Code
  - LangGraph tool pattern architecture (mandatory)
  - TDD workflow (development vs unit testing)
  - DRY compliance and clean code principles
  - Async programming patterns
  - Sub-agent architecture and coordination
  - Geist framework (Ghost/Geyser/Gist analysis)

- **[copilot-instructions.md](./copilot-instructions.md)** - GitHub Copilot configuration
  - Leverage hierarchy and intelligent task routing
  - Fast development and debugging practices
  - Test-driven development workflow
  - Code construction and quality standards

### 🏗️ Construction Best Practices

Located in `construction_best_practices/`:

- **ARCHITECTURE_GUIDE.md** - Code standards and design patterns
- **CODE_CONSTRUCTION_GUIDE.md** - Defensive programming principles (Code Complete 2)
- **TDD_WORKFLOW_GUIDE.md** - Comprehensive test-driven development process
- **ASYNC_PROGRAMMING_LANGGRAPH_GUIDE.md** - Async patterns for LangGraph workflows
- **INTEGRATION_PLAYBOOK_GUIDE.md** - External service integration best practices
- **REFACTORING_BEST_PRACTICES.md** - Safe refactoring techniques
- **DEBUGGING_ERROR_HANDLING_GUIDE.md** - Systematic debugging and error recovery
- **BUG_INVESTIGATION_PROCESS.md** - Standardized bug investigation workflow
- **COMMENTING_BEST_PRACTICES.md** - Comments-first development approach
- **VARIABLE_NAMING_GUIDE.md** - Code Complete 2 naming standards
- **WORKING_WITH_STRINGS_GUIDE.md** - String handling and regex patterns
- **README_GUIDANCE.md** - Documentation standards and maintenance
- **MARKDOWN_PLAN_TEMPLATE.md** - Implementation plan templates

## Core Principles

### 1. Don't Repeat Yourself (DRY)
- Search existing functionality before writing new code
- Use inheritance/composition over duplication
- Extract common patterns to utilities
- Delete old implementations when refactoring
- No backwards compatibility wrappers

### 2. Test-Driven Development
- Write tests first that capture acceptance criteria
- **Development TDD**: Real components + real dependencies for integration
- **Unit TDD**: Real component + mocked dependencies for behavior testing
- Maintain 85%+ integration coverage, 90%+ unit coverage

### 3. Clean Architecture
- Clear separation of concerns (data → domain → application → UI)
- Dependencies point inward
- Depend on abstractions, not concretions
- Single responsibility per module

### 4. Defensive Programming
- Input validation with proper error boundaries
- Fail fast with comprehensive error context
- Structured logging with debugging information
- Resource management with timeouts

### 5. Comments Explain Why
- Comments explain WHY, not WHAT
- Write comments-first pseudocode before implementation
- Include business context for complex decisions
- Comprehensive docstrings for all public functions

### 6. Quality Over Speed
- Type hints everywhere
- Self-explanatory variable names
- Small functions (<20 lines)
- Single responsibility
- Optimize for readability and maintainability

## Three-Dimensional Problem Analysis (Geist Framework)

When approaching any problem, use this framework for comprehensive understanding:

1. **Ghost Analysis (Parallel Reality)** - What am I not seeing? What assumptions am I making?
2. **Geyser Analysis (Dynamic Forces)** - What forces am I not accounting for? What explosive changes exist?
3. **Gist Analysis (Essential Core)** - What's the irreducible essence? Am I solving the essential problem?

## Key Practices

- **Pre-Implementation DRY Analysis** - Search for existing similar functionality first
- **Comments-First Design** - Write complete business logic as comments before coding
- **Development TDD** - Real components + real dependencies for new features
- **Unit TDD** - Real component + mocked dependencies for behavior tests
- **Async Compliance** - All I/O operations use proper async patterns
- **Security First** - Input validation, authentication, secrets management, rate limiting
- **Complete Replacement Over Compatibility** - Replace old code entirely, no wrappers

## Foundational References

These principles are grounded in time-tested software engineering books:

- **Code Complete 2** (Steve McConnell) - Defensive programming and code construction
- **Clean Code** (Robert C. Martin) - SOLID principles and meaningful names
- **Clean Architecture** (Robert C. Martin) - Dependency inversion and stable abstractions
- **Head First Design Patterns** (Freeman & Robson) - Practical pattern applications

## Usage

### For New Projects

1. Copy `CLAUDE.md` and/or `copilot-instructions.md` to your project root (or `.github/` for Copilot)
2. Review and customize based on your tech stack
3. Reference specific guides in `construction_best_practices/` as needed

### For AI Agents

These files are designed to be read by AI coding agents to understand your development standards:

- **Claude Code**: Automatically reads `CLAUDE.md` from project root
- **GitHub Copilot**: Automatically reads `.github/copilot-instructions.md`

### For Teams

Use these guidelines to:
- Establish consistent coding standards
- Onboard new team members
- Create project-specific coding guidelines
- Build institutional knowledge

## Technology Context

While these guidelines were developed in the context of:
- **Languages**: Python, TypeScript, Java
- **Frameworks**: LangGraph/LangChain, Next.js, Spring Boot
- **Platforms**: AWS, Node.js

The principles are **technology-agnostic** and applicable to any modern software development project.

## Definition of Done

Every feature or refactor must meet:

- [ ] DRY analysis completed - no duplicated functionality
- [ ] Development TDD for new features (integration tests with real dependencies)
- [ ] Unit TDD for behaviors (isolated tests with mocked dependencies)
- [ ] Comments explain "why" decisions were made
- [ ] All public functions have comprehensive docstrings
- [ ] Coverage maintained or higher (≥85% integration, ≥90% unit)
- [ ] Variable names follow self-explanatory naming standards
- [ ] Error handling with proper recovery strategies
- [ ] No duplicate files - proper file organization
- [ ] README documentation updated

## Contributing

This is a living document. As software engineering practices evolve and new patterns emerge, these guidelines are updated to reflect current best practices.

## License

MIT License - Feel free to use these guidelines in your own projects.

## Author

**Matthew Kerns**
- 7+ years of professional software engineering experience
- Former Amazon Software Development Engineer
- Startup founder and technical leader
- Portfolio: [matthewkerns.dev](https://matthewkerns.dev)
- GitHub: [@MatthewKerns](https://github.com/MatthewKerns)

---

**Remember**: The goal is to create codebases that any professional developer can understand and extend with confidence. Prioritize code readability and maintainability over cleverness.
