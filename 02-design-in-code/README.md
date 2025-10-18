# Design in Code: Construction-Level Design

## Overview

This directory contains guides on design decisions made during the coding process itself. These are not high-level architectural patterns, but rather the day-to-day design choices developers make while writing code: how to structure routines, manage complexity, handle coupling, and organize code at the construction level.

## Why These Practices Matter

Design decisions made during coding have immediate and lasting impact on code quality. Poor construction-level design leads to:
- Complex, hard-to-understand code
- Tight coupling that prevents change
- Hidden dependencies that cause bugs
- Code that's difficult to test
- Modules that do too much (or too little)

Good construction-level design creates code that is:
- Easy to understand and modify
- Loosely coupled and highly cohesive
- Testable and debuggable
- Appropriately sized and scoped
- Self-documenting through structure

## Source Materials

These guides synthesize principles from:

- **Code Complete 2** by Steve McConnell (Chapters 5-9, 24)
  - Design in construction
  - High-quality routines
  - Defensive programming
  - Managing complexity
  - Organizing straight-line code

- **Clean Code** by Robert C. Martin (Chapters 6-10)
  - Objects and data structures
  - Error handling
  - Boundaries
  - Unit testing
  - Classes

- **Clean Architecture** by Robert C. Martin (Chapters 7-11)
  - Component design principles
  - SRP, OCP, LSP, ISP, DIP (SOLID)
  - Component cohesion and coupling

## When to Use These Guides

**Before Writing Code:**
- Planning routine structure and responsibilities
- Deciding on error handling strategies
- Determining appropriate abstraction levels
- Choosing between objects and data structures

**During Development:**
- Structuring new routines and classes
- Managing dependencies between components
- Implementing defensive programming techniques
- Controlling complexity in algorithms

**During Code Review:**
- Evaluating routine quality and size
- Checking coupling and cohesion
- Assessing error handling approaches
- Reviewing abstraction levels

**When Refactoring:**
- Breaking apart large routines
- Reducing coupling between modules
- Improving cohesion within classes
- Simplifying complex control structures

## Guides in This Directory

### Coming Soon
- **ROUTINE_DESIGN.md** - Creating high-quality functions and methods
- **MANAGING_COMPLEXITY.md** - Techniques for keeping code understandable
- **DEFENSIVE_PROGRAMMING.md** - Assertions, error handling, and validation
- **COUPLING_AND_COHESION.md** - Managing dependencies and responsibilities
- **ABSTRACTION_LEVELS.md** - Working at consistent levels of abstraction
- **CONTROL_FLOW.md** - Conditional logic, loops, and branching
- **OBJECT_VS_DATA_STRUCTURE.md** - When to use which pattern
- **BOUNDARY_HANDLING.md** - Working with external code and APIs
- **CODE_ORGANIZATION.md** - Organizing code within files and modules

## Key Principles

### Routine Design
- **Single Responsibility**: Each routine does one thing well
- **Appropriate Size**: Short enough to understand, complete enough to be useful
- **Clear Interface**: Parameters and return values make sense
- **Minimal Coupling**: Few dependencies on other code

### Complexity Management
- **McCabe's Cyclomatic Complexity**: Keep decision points low
- **Nesting Depth**: Limit to 3-4 levels maximum
- **Fan-Out**: Limit number of other routines called
- **Abstraction Levels**: Stay consistent within each routine

### Defensive Programming
- **Assertions**: Document and verify assumptions
- **Validation**: Check inputs and preconditions
- **Error Handling**: Plan for and handle exceptions
- **Graceful Degradation**: Fail safely and informatively

## Quick Start Checklist

Before writing a new routine:
- [ ] Can you state its single responsibility in one sentence?
- [ ] Is the level of abstraction appropriate?
- [ ] Have you planned error handling?
- [ ] Will it be testable?

During implementation:
- [ ] Complexity stays manageable (cyclomatic < 10)
- [ ] Nesting depth stays low (< 4 levels)
- [ ] Parameters are clear and minimal (< 7)
- [ ] No hidden dependencies or side effects

During code review:
- [ ] Each routine has clear responsibility
- [ ] Error handling is comprehensive
- [ ] Coupling is minimal and intentional
- [ ] Code is at consistent abstraction levels

## Related Resources

- **01-foundations/**: Naming, formatting, and basic principles
- **03-clean-architecture/**: Higher-level architectural patterns
- **04-quality-through-testing/**: Testing practices
- **05-refactoring-and-improvement/**: Improving existing code
- **99-reference/**: Quick reference checklists

## Contributing

These guides focus on construction-level design decisions made while coding:
- Provide practical decision frameworks
- Include measurable criteria (complexity metrics, size limits)
- Show both good and bad examples
- Keep guidance language-agnostic when possible
