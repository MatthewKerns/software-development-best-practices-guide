# Design in Code: Construction-Level Design Practices

## Overview

This directory contains comprehensive guides for design decisions made during code construction. While architecture establishes system-wide structure, design in construction focuses on the daily choices developers make: how to structure classes, organize functions, choose abstractions, and create maintainable code.

Design happens continuously during coding. Every class you create, every function you write, every abstraction you introduce is a design decision that shapes the quality and maintainability of your codebase.

## Guides in This Directory

### 1. [Design in Construction](DESIGN_IN_CONSTRUCTION.md)
**Foundation**: Comprehensive construction-level design principles

**Key Topics**:
- Levels of design (system, subsystem, class, routine, internal)
- Managing complexity through abstraction
- Information hiding and encapsulation
- Coupling and cohesion
- Design heuristics and patterns
- Integration with Geist Framework (Ghost/Geyser/Gist)

**When to Read**: Before starting any significant implementation, when designing new components, when refactoring complex code.

**Word Count**: ~6,500 words | **Examples**: 65+ in Python, TypeScript, Java

### 2. [Pseudocode Programming Process](PSEUDOCODE_PROGRAMMING.md)
**Technique**: Write comments first, code second

**Key Topics**:
- Pseudocode-first workflow
- Design through comments
- Iterative refinement techniques
- Pseudocode at different abstraction levels
- Integration with Geist analysis

**When to Read**: Before implementing any non-trivial function, when stuck on algorithm design, when reviewing complex code.

**Word Count**: ~6,000 words | **Examples**: 55+ in Python, TypeScript, Java

### 3. [Class Design](CLASS_DESIGN.md)
**Building Blocks**: Creating high-quality, maintainable classes

**Key Topics**:
- Class organization and structure
- Single Responsibility Principle
- Class cohesion and coupling
- Open-Closed Principle
- Valid reasons to create classes
- Encapsulation and information hiding
- Inheritance vs. composition

**When to Read**: When creating new classes, when classes feel too large or unfocused, during code reviews.

**Word Count**: ~6,800 words | **Examples**: 70+ in Python, TypeScript, Java

### 4. [Working Classes](WORKING_CLASSES.md)
**Practical Implementation**: Day-to-day class construction techniques

**Key Topics**:
- Constructor design and initialization
- Immutability patterns
- Deep copy vs. shallow copy
- Abstract Data Types (ADTs)
- Designing for testability
- Resource management
- Dependency injection

**When to Read**: When implementing classes, when fixing bugs related to initialization or state, when improving testability.

**Word Count**: ~6,200 words | **Examples**: 60+ in Python, TypeScript, Java

### 5. [UI Design Best Practices](UI_DESIGN_BEST_PRACTICES.md)
**Interface Design**: Building beautiful, accessible, maintainable user interfaces

**Key Topics**:
- Atomic Design methodology (Atoms → Molecules → Organisms → Templates → Pages)
- Visual hierarchy and layout systems
- 8pt spacing & sizing systems
- Typography scales and line height
- HSL color management & comprehensive palettes
- Component design patterns
- WCAG 2.2 accessibility compliance
- Responsive design principles
- Framework-agnostic approaches

**When to Read**: Before designing UI components, when establishing design systems, during UI code reviews, when improving accessibility.

**Word Count**: ~9,500 words | **Source**: Atomic Design (Brad Frost), Refactoring UI (Wathan & Schoger), WCAG 2.2

## How to Use These Guides

### For New Developers
1. Start with **Design in Construction** for foundational principles
2. Read **Class Design** to understand how to structure classes
3. Practice with **Pseudocode Programming** on your next function
4. Reference **Working Classes** when implementing
5. Study **UI Design Best Practices** before building user interfaces

### For Experienced Developers
- Use **Pseudocode Programming** for complex algorithms
- Refer to **Design in Construction** when making architectural decisions
- Check **Class Design** during code reviews
- Apply **Working Classes** patterns for testability and maintainability
- Follow **UI Design Best Practices** for design system development

### For Code Reviews
1. **Class Design**: Is the class focused? Does it have one responsibility?
2. **Design in Construction**: Are abstractions appropriate? Is complexity managed?
3. **Working Classes**: Are constructors correct? Is the class testable?
4. **Pseudocode Programming**: Could the approach have been clearer with design-first thinking?
5. **UI Design Best Practices**: Does the UI follow Atomic Design? Is it accessible (WCAG 2.2)? Does spacing use the 8pt grid?

## Quick Reference

### Design Heuristics
- **Manage Complexity**: Hide complexity behind abstractions
- **Information Hiding**: Expose minimal, stable interfaces
- **Loose Coupling**: Minimize dependencies between modules
- **Strong Cohesion**: Keep related responsibilities together
- **Design for Change**: Isolate likely changes behind boundaries

### Class Design Principles
- **Small Classes**: Measured by responsibilities, not lines of code
- **Single Responsibility**: One reason to change
- **High Cohesion**: Methods use most instance variables
- **Open-Closed**: Open for extension, closed for modification
- **Minimal Interface**: Make everything private by default

### Construction Techniques
- **Comments First**: Design with pseudocode before coding
- **Immutable by Default**: Prefer immutability for value objects
- **Dependency Injection**: Pass dependencies, don't create them
- **Fail Fast**: Validate in constructors, establish invariants
- **Resource Management**: Acquire in constructor, release in cleanup

### UI Design Principles
- **Atomic Design**: Build systems from atoms → molecules → organisms → templates → pages
- **8pt Grid System**: Use multiples of 8 for all spacing and sizing
- **Visual Hierarchy**: Size, weight, color (not size alone)
- **HSL Colors**: Comprehensive palettes with 9+ shades per color
- **WCAG 2.2 Compliance**: 4.5:1 contrast, keyboard accessible, 24×24px touch targets
- **Mobile-First**: Design for smallest screens, enhance for larger

## Integration with Other Sections

### Foundations (01-foundations/)
Design in construction builds on:
- **Variable Naming**: Classes and functions need good names
- **Functions and Routines**: Class methods should follow function principles
- **Error Handling**: Classes must handle errors appropriately

### Clean Architecture (03-clean-architecture/)
Construction-level design implements:
- **SOLID Principles**: Classes embody SOLID at implementation level
- **Dependency Rule**: Construction enforces architectural dependencies
- **Boundaries**: Classes create and respect boundaries

### Quality Through Testing (04-quality-through-testing/)
Construction enables testing:
- **Testability**: Well-designed classes are easy to test
- **Dependency Injection**: Enables mocking and isolation
- **Immutability**: Simplifies test fixtures

### Geist Framework Integration

All design-in-code guides integrate the Geist Framework:

**Ghost (Unknown Unknowns)**:
- Design for requirements you don't know yet
- Create extension points for future needs
- Use pseudocode to reveal hidden requirements

**Geyser (Dynamic Forces)**:
- Design for scalability from the start
- Anticipate growth and pressure points
- Build performance into construction decisions

**Gist (Essential Essence)**:
- Focus on essential complexity
- Eliminate accidental complexity
- Keep classes focused on core responsibilities

## Common Questions

**Q: When should I use pseudocode?**
A: For any non-trivial function (complex algorithm, multiple edge cases, unfamiliar domain, team collaboration needed). Skip it for one-liners and simple operations.

**Q: How do I know if my class is too large?**
A: If you can't describe its purpose in 25 words without using "and," "or," or "but," it's too large. Measure by responsibilities, not lines of code.

**Q: Should I always make classes immutable?**
A: Make value objects (Money, Date, etc.) immutable always. For entities (User, Order), use immutability when thread-safety or simplicity is more important than performance.

**Q: How much design should I do upfront?**
A: Enough to clarify the approach (pseudocode for algorithm, class responsibilities defined), but not so much that you're designing features you don't need yet (YAGNI).

**Q: When should I create a new class?**
A: When you need to model a concept (real or abstract), reduce/isolate complexity, hide implementation details, limit effects of changes, or group related operations.

## Examples and Code Samples

All guides contain 40-70 code examples each:
- **Language Coverage**: Python, TypeScript, Java (backend guides); HTML, CSS, JavaScript (UI guide)
- **Patterns**: Both anti-patterns (what not to do) and good patterns (what to do)
- **Annotations**: Explanations of why changes improve the code
- **Real-World**: Generic examples applicable to any domain

Total across all guides: **300+ code examples**

## Further Reading

### Primary Sources
- **Code Complete 2** (Chapters 5-7) - Steve McConnell
  - Design in construction
  - High-quality routines
  - Working classes

- **Clean Code** (Chapters 3, 10) - Robert C. Martin
  - Functions
  - Classes

- **Atomic Design** - Brad Frost
  - Component hierarchy methodology
  - Design systems thinking

- **Refactoring UI** - Adam Wathan & Steve Schoger
  - Visual hierarchy and spacing
  - Typography and color systems

### Related Books
- **Design Patterns** - Gang of Four
- **Refactoring** - Martin Fowler
- **Effective Java** - Joshua Bloch
- **Domain-Driven Design** - Eric Evans

### Related Guides in This Repository
- **01-foundations/FUNCTIONS_AND_ROUTINES.md**: Function-level design
- **03-clean-architecture/SOLID_PRINCIPLES.md**: Architectural principles
- **04-quality-through-testing/**: Testing well-designed classes
- **10-geist-gap-analysis-framework/**: Philosophical foundation for design decisions

## Contributing

When adding to these guides:
1. Follow the established structure (Overview, Why It Matters, Source Materials, etc.)
2. Include code examples in Python, TypeScript, and Java
3. Show both anti-patterns and good patterns
4. Integrate with Geist Framework (Ghost/Geyser/Gist)
5. Keep examples generic and domain-agnostic
6. Aim for 5,000-7,000 words per guide

---

**Remember**: Design happens during construction, not before or after. Every line of code you write is a design decision. Make those decisions deliberately, with clear principles guiding you. These guides provide the foundation for making excellent construction-level design choices that result in maintainable, testable, and reliable software.
