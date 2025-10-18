# Geist Framework: Specialized Investigation and Gap Analysis

## Overview

The Geist Framework is a **specialized philosophical technique** for investigating complex software problems, understanding incomplete implementations, and analyzing gaps in features or requirements. It provides three distinct but interconnected dimensions: Ghost (parallel realities and unknowns), Geyser (dynamic forces and pressures), and Gist (essential core and meaning).

## When to Use This Framework

**This is NOT a day-to-day coding framework.** Use Geist specifically for:

- **Implementation gap analysis**: Understanding why features are incomplete
- **Complex feature planning**: Investigating multi-dimensional requirements
- **Mysterious debugging**: When the obvious causes don't explain the problem
- **Architectural investigations**: Understanding forces affecting system design
- **Post-mortem analysis**: Deep diving into what went wrong

**Do NOT use Geist for:**
- Basic variable naming (use Clean Code and Code Complete principles)
- Simple function design (use SOLID and Clean Code)
- Routine refactoring (use standard refactoring patterns)
- Everyday code review (use established checklists)

## Why This Framework Matters

When standard problem-solving approaches fail or when dealing with incomplete implementations, the Geist Framework helps developers:
- **Uncover hidden assumptions** (Ghost): What are we not seeing?
- **Understand dynamic forces** (Geyser): What pressures are driving change?
- **Focus on essentials** (Gist): What truly matters vs. what's noise?

This three-dimensional view is valuable for:
- Understanding why implementations keep failing
- Discovering missing requirements in complex features
- Planning features with many unknowns
- Investigating systemic issues
- Analyzing forces preventing progress

## Philosophical Foundation

The Geist Framework synthesizes concepts from:

- **Immanuel Kant**: Phenomena (what we perceive) vs. Noumena (things-in-themselves)
  - Ghost dimension: The reality we cannot directly perceive
  - What assumptions and unknowns lie beneath the surface?

- **Georg Wilhelm Friedrich Hegel**: Dialectical process and spirit (Geist)
  - Geyser dimension: Forces in tension driving evolution
  - What contradictions and pressures are creating change?

- **Phenomenology**: Returning to "the things themselves"
  - Gist dimension: Essential nature stripped of incidental details
  - What is the irreducible core we're actually solving for?

## The Three Dimensions

### Ghost: Parallel Reality (Unknown Unknowns)

**What it reveals:**
- Hidden assumptions in requirements
- Unstated dependencies
- Context that isn't visible in code
- Future needs not yet articulated
- Knowledge that exists in people's heads but not documentation

**Key questions:**
- What parallel reality am I not seeing?
- What assumptions am I making unconsciously?
- What context is missing from this picture?
- What do users need but haven't told us?
- What will we discover only after shipping?

**When to apply:**
- During requirements gathering
- When designs feel incomplete
- Before committing to architectural decisions
- When investigating mysterious bugs
- During post-mortems

### Geyser: Dynamic Forces (Explosive Change)

**What it reveals:**
- Pressures building under the surface
- Forces that will drive evolution
- Tensions between competing needs
- Scalability constraints
- External factors affecting the system

**Key questions:**
- What forces am I not accounting for?
- What pressures are building beneath the surface?
- What will cause this design to break?
- What growth will we need to accommodate?
- What external changes will impact us?

**When to apply:**
- During architecture design
- When planning for scale
- Before performance optimization
- When evaluating technical debt
- During capacity planning

### Gist: Essential Core (Irreducible Essence)

**What it reveals:**
- Core problem vs. incidental complexity
- Essential features vs. nice-to-haves
- What truly needs to be solved
- Where effort should focus
- What can be eliminated or simplified

**Key questions:**
- Am I solving the essential problem?
- What is the irreducible core of this feature?
- What complexity is accidental vs. essential?
- What can be removed without losing value?
- What truly matters to users?

**When to apply:**
- When requirements seem bloated
- During feature prioritization
- When code feels overly complex
- Before starting implementation
- When deciding what to refactor

## Current Guides

### Available Now
- **GEIST_DESIGN_INVESTIGATION_FRAMEWORK.md** - Comprehensive framework documentation
- **GEIST_COPILOT_INSTRUCTIONS.md** - Using Geist with AI assistants
- **DESIGN_INVESTIGATION_GUIDANCE.md** - Applying Geist to design investigations
- **CONTINUOUS_GAP_ANALYSIS.md** ✨ **NEW** - Systematic gap analysis from vision to implementation

### Coming Soon
- **GEIST_REQUIREMENTS_ANALYSIS.md** - Three-dimensional requirements gathering
- **GEIST_DEBUGGING_PROTOCOL.md** - Using Geist for problem investigation
- **GEIST_ARCHITECTURE_DECISIONS.md** - Applying framework to architectural choices
- **GEIST_FEATURE_PRIORITIZATION.md** - Using Gist for prioritization
- **GEIST_CODE_REVIEW.md** - Three-dimensional code review approach

## When to Apply to Other Practices

The Geist Framework is **occasionally useful** for investigating complex problems in other practices. Use it sparingly:

### With Foundations (01-foundations/)
**Rarely needed.** Most naming problems are solved with Clean Code principles.
- Use Geist only when: Domain concepts are unclear or multiple stakeholders have conflicting terminology

### With Design (02-design-in-code/)
**Occasionally useful.** Apply when standard design patterns aren't working.
- Use Geist when: Design repeatedly fails, requirements are unclear, or competing forces create tension

### With Architecture (03-clean-architecture/)
**Moderately useful.** Good for complex architectural decisions.
- Use Geist when: Choosing between architectures, investigating systemic issues, or planning major refactoring

### With Testing (04-quality-through-testing/)
**Rarely needed.** Most testing issues are straightforward.
- Use Geist only when: Coverage is high but bugs persist, or edge cases keep surprising you

### With Refactoring (05-refactoring-and-improvement/)
**Occasionally useful.** Apply when refactoring keeps failing.
- Use Geist when: Technical debt is hidden, refactoring introduces new problems, or impact is unclear

### With Collaboration (06-collaborative-construction/)
**Rarely needed.** Most collaboration issues are communication problems.
- Use Geist only when: Team processes repeatedly fail or knowledge gaps are systemic

## Practical Application

### The Three Questions Debug Protocol

When stuck on any problem, ask:
1. **Ghost**: What parallel reality am I not seeing?
2. **Geyser**: What forces am I not accounting for?
3. **Gist**: Am I solving the essential problem?

### Feature Gap Resolution Workflow

Use Geist for iterative feature completion:
1. **Ghost**: Identify unknown requirements and dependencies
2. **Geyser**: Understand forces preventing completion
3. **Gist**: Confirm essential features vs. nice-to-haves
4. **Iterate**: Continue until Gist confirms feature complete

### Architectural Decision Framework

Before major decisions:
1. **Ghost Analysis**: Document known unknowns and assumptions
2. **Geyser Analysis**: Map forces that will drive change
3. **Gist Analysis**: Define essential vs. incidental concerns
4. **Decision**: Choose approach that addresses all three dimensions

## Quick Start Checklist

When analyzing any problem:
- [ ] Ghost: List assumptions and unknowns explicitly
- [ ] Geyser: Identify forces and pressures
- [ ] Gist: Define the essential problem to solve
- [ ] Validate: Does solution address all three dimensions?

During design investigation:
- [ ] Ghost: What context is missing?
- [ ] Geyser: What will change or grow?
- [ ] Gist: What is the simplest solution to the core problem?
- [ ] Document: Record findings for future reference

When debugging:
- [ ] Ghost: What aren't we seeing about this failure?
- [ ] Geyser: What forces caused this problem?
- [ ] Gist: What is the root cause vs. symptoms?
- [ ] Fix: Address the essential issue, not just symptoms

## Related Resources

- **01-foundations/** through **06-collaborative-construction/**: Foundation practices (use these first)
- **08-project-management/**: Planning and organization (primary tools for most work)
- **CLAUDE.md**: Advanced usage for AI-assisted development
- **GENERALIZATION_CHECKLIST.md**: Systematic approach to assumptions

## Remember: Use Foundation Practices First

**The Geist Framework is powerful but specialized.** For most development work:

1. **Start with the basics**: Code Complete 2, Clean Code, Clean Architecture
2. **Use standard patterns**: SOLID principles, refactoring catalog, testing pyramids
3. **Follow team practices**: Code reviews, pair programming, integration workflows
4. **Only invoke Geist when**: Standard approaches aren't working or gaps persist

**Signs you need Geist:**
- Feature keeps getting "90% complete" but never finished
- Requirements seem clear but implementation keeps failing
- Multiple refactorings haven't solved the core problem
- Team is stuck despite following best practices
- Post-mortems don't reveal actionable insights

**Signs you DON'T need Geist:**
- Writing straightforward business logic
- Naming variables or functions
- Following established patterns
- Routine refactoring or bug fixes
- Standard architectural decisions

## Contributing

The Geist Framework guides should:
- Emphasize specialized, non-routine application
- Connect philosophical concepts to practical investigation
- Provide concrete questions for gap analysis
- Show examples of when standard approaches failed
- Keep philosophical grounding explicit but accessible
- Always reference simpler alternatives first
