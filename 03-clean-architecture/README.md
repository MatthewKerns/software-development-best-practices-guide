# Clean Architecture: SOLID Principles and Components

## Overview

This directory contains guides on architectural principles that govern how we structure systems at the component and module level. These guides cover the SOLID principles, component cohesion and coupling, and architectural boundaries that create maintainable, flexible systems.

## Why These Practices Matter

Architecture isn't just about high-level system design—it's about the principles that guide every design decision. Poor architectural practices lead to:
- Systems that are difficult to change
- Dependencies that create fragility
- Components that can't be tested in isolation
- Code that violates the Open-Closed Principle
- Abstractions that leak implementation details

Good architectural practices create:
- Systems that accommodate change easily
- Clear boundaries between components
- Code that's testable and maintainable
- Stable, flexible abstractions
- Components with clear responsibilities

## Source Materials

These guides are primarily informed by:

- **Clean Architecture** by Robert C. Martin (Chapters 7-21)
  - SOLID principles (SRP, OCP, LSP, ISP, DIP)
  - Component principles (REP, CCP, CRP)
  - Component coupling (ADP, SDP, SAP)
  - Architectural boundaries
  - Business rules and entities

- **Code Complete 2** by Steve McConnell (Chapters 5-6)
  - Design heuristics
  - Managing complexity
  - Information hiding

- **Clean Code** by Robert C. Martin (Chapter 10)
  - Class organization
  - Separation of concerns

## When to Use These Guides

**During System Design:**
- Planning module boundaries
- Defining component responsibilities
- Establishing dependency rules
- Creating architectural layers

**During Development:**
- Applying SOLID principles to classes
- Organizing code into components
- Managing dependencies
- Creating abstractions

**During Code Review:**
- Checking for SOLID violations
- Evaluating component boundaries
- Reviewing dependency directions
- Assessing abstraction quality

**When Refactoring:**
- Breaking monoliths into components
- Fixing dependency violations
- Improving abstraction stability
- Reorganizing architectural layers

## Guides in This Directory

### Coming Soon

**SOLID Principles:**
- **SINGLE_RESPONSIBILITY_PRINCIPLE.md** - One reason to change
- **OPEN_CLOSED_PRINCIPLE.md** - Open for extension, closed for modification
- **LISKOV_SUBSTITUTION_PRINCIPLE.md** - Substitutability of derived types
- **INTERFACE_SEGREGATION_PRINCIPLE.md** - Client-specific interfaces
- **DEPENDENCY_INVERSION_PRINCIPLE.md** - Depend on abstractions

**Component Principles:**
- **COMPONENT_COHESION.md** - REP, CCP, CRP principles
- **COMPONENT_COUPLING.md** - ADP, SDP, SAP principles
- **ARCHITECTURAL_BOUNDARIES.md** - Creating and maintaining boundaries
- **DEPENDENCY_MANAGEMENT.md** - Managing dependencies between components
- **PLUGIN_ARCHITECTURE.md** - Creating flexible, extensible systems

**Architectural Patterns:**
- **BUSINESS_RULES.md** - Entities and use cases
- **CLEAN_ARCHITECTURE_LAYERS.md** - The dependency rule
- **SCREAMING_ARCHITECTURE.md** - Architecture that reveals intent
- **HUMBLE_OBJECTS.md** - Separating testable from hard-to-test code

## Key Principles

### SOLID Principles

**Single Responsibility Principle (SRP)**
- A class should have one, and only one, reason to change
- Different actors should not cause the same class to change

**Open-Closed Principle (OCP)**
- Software entities should be open for extension, closed for modification
- Achieve through abstractions and polymorphism

**Liskov Substitution Principle (LSP)**
- Subtypes must be substitutable for their base types
- Inheritance should represent "is-a" relationships

**Interface Segregation Principle (ISP)**
- No client should depend on methods it doesn't use
- Split interfaces into client-specific contracts

**Dependency Inversion Principle (DIP)**
- High-level modules should not depend on low-level modules
- Both should depend on abstractions

### Component Principles

**Cohesion Principles**
- **REP**: Reuse/Release Equivalence Principle
- **CCP**: Common Closure Principle
- **CRP**: Common Reuse Principle

**Coupling Principles**
- **ADP**: Acyclic Dependencies Principle
- **SDP**: Stable Dependencies Principle
- **SAP**: Stable Abstractions Principle

## Quick Start Checklist

When designing components:
- [ ] Each component has a clear, single responsibility
- [ ] Dependencies point in one direction (toward stability)
- [ ] Business rules are isolated from implementation details
- [ ] Interfaces are segregated by client needs
- [ ] High-level policy doesn't depend on low-level details

When reviewing architecture:
- [ ] No circular dependencies between components
- [ ] Stable components are abstract
- [ ] Volatile components are concrete and depend on stable ones
- [ ] Clear boundaries separate concerns
- [ ] The dependency rule is not violated

When applying SOLID:
- [ ] Classes have one reason to change
- [ ] Behavior is extended without modifying existing code
- [ ] Derived classes are substitutable
- [ ] Interfaces are client-specific
- [ ] Dependencies point toward abstractions

## Related Resources

- **01-foundations/**: Basic coding principles
- **02-design-in-code/**: Construction-level design
- **04-quality-through-testing/**: Testing practices
- **05-refactoring-and-improvement/**: Improving code and architecture

## Contributing

These guides focus on architectural principles and component design:
- Reference Robert C. Martin's principles explicitly
- Provide concrete examples of violations and fixes
- Show how principles work together
- Include metrics for measuring adherence
- Keep examples simple and focused on the principle
