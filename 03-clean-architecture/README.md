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

### Comprehensive Guides (Available Now)

**Foundational Principles:**
- **[SOLID_PRINCIPLES.md](SOLID_PRINCIPLES.md)** - Complete guide to all 5 SOLID principles (SRP, OCP, LSP, ISP, DIP)
- **[COMPONENT_PRINCIPLES.md](COMPONENT_PRINCIPLES.md)** - Complete guide to component cohesion (REP, CCP, CRP) and coupling (ADP, SDP, SAP)
- **[DEPENDENCY_RULE.md](DEPENDENCY_RULE.md)** - The fundamental rule of clean architecture: dependencies point inward

**Architectural Patterns:**
- **[PLUGIN_ARCHITECTURE.md](PLUGIN_ARCHITECTURE.md)** - Building flexible, extensible systems with dependency inversion
- **[ARCHITECTURAL_BOUNDARIES.md](ARCHITECTURAL_BOUNDARIES.md)** - Where to draw lines that separate concerns
- **[SCREAMING_ARCHITECTURE.md](SCREAMING_ARCHITECTURE.md)** - Making architecture reveal business intent, not frameworks
- **[BUSINESS_RULES.md](BUSINESS_RULES.md)** - Entities and use cases: the heart of clean architecture
- **[HUMBLE_OBJECTS.md](HUMBLE_OBJECTS.md)** - Separating testable logic from hard-to-test infrastructure

### Future Guides (Optional)

**Individual SOLID Principle Guides:**
- **SINGLE_RESPONSIBILITY_PRINCIPLE.md** - Deep dive into SRP (extracted from SOLID_PRINCIPLES.md)
- **OPEN_CLOSED_PRINCIPLE.md** - Deep dive into OCP (extracted from SOLID_PRINCIPLES.md)
- **LISKOV_SUBSTITUTION_PRINCIPLE.md** - Deep dive into LSP (extracted from SOLID_PRINCIPLES.md)
- **INTERFACE_SEGREGATION_PRINCIPLE.md** - Deep dive into ISP (extracted from SOLID_PRINCIPLES.md)
- **DEPENDENCY_INVERSION_PRINCIPLE.md** - Deep dive into DIP (extracted from SOLID_PRINCIPLES.md)

**Additional Component Guides:**
- **DEPENDENCY_MANAGEMENT.md** - Advanced dependency management strategies

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
