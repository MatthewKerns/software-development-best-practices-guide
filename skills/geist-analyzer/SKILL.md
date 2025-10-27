---
name: geist-analyzer
description: Applies Ghost-Geyser-Gist framework for investigating complex software problems, understanding incomplete implementations, and analyzing gaps in features or requirements. Use when standard approaches fail or dealing with mysterious bugs, incomplete features, or architectural unknowns. Not for routine coding tasks.
allowed-tools: [Read, Grep, Glob]
---

# Geist Analyzer (Ghost-Geyser-Gist Framework)

## Purpose

A specialized philosophical investigation technique for complex software problems that standard debugging, requirements analysis, or design approaches cannot solve.

## When to Use This Skill

**✅ USE Geist for:**
- Implementation gap analysis (features stuck at "90% complete")
- Complex feature planning with many unknowns
- Mysterious debugging (obvious causes don't explain the problem)
- Architectural investigations (forces affecting system design)
- Post-mortem analysis (understanding what went wrong)
- Requirements that keep changing or feel incomplete

**❌ DO NOT use Geist for:**
- Basic variable naming (use Clean Code principles)
- Simple function design (use SOLID principles)
- Routine refactoring (use standard refactoring patterns)
- Everyday code review (use established checklists)
- Straightforward bug fixes

**Signs You Need Geist:**
- Feature keeps getting "90% complete" but never finished
- Requirements seem clear but implementation keeps failing
- Multiple refactorings haven't solved the core problem
- Team is stuck despite following best practices
- Post-mortems don't reveal actionable insights

**Signs You DON'T Need Geist:**
- Writing straightforward business logic
- Naming variables or functions
- Following established patterns
- Routine refactoring or bug fixes
- Standard architectural decisions

## The Three Dimensions

### Ghost: Parallel Reality (Unknown Unknowns)

**What it reveals:**
- Hidden assumptions in requirements
- Unstated dependencies
- Context that isn't visible in code
- Future needs not yet articulated
- Knowledge in people's heads but not documentation

**Key Questions:**
- What parallel reality am I not seeing?
- What assumptions am I making unconsciously?
- What context is missing from this picture?
- What do users need but haven't told us?
- What will we discover only after shipping?

**When to Apply:**
- Requirements gathering (uncover hidden assumptions)
- Design feels incomplete (missing context)
- Before architectural decisions (document unknowns)
- Mysterious bugs (what aren't we seeing?)
- Post-mortems (what context was missing?)

**Example Investigation:**
```
GHOST ANALYSIS: Authentication Feature Stuck at 90%

Visible Requirements:
- Users can log in with email/password
- Password reset via email
- Session management

Hidden Assumptions (Ghost):
- Users expect OAuth (Google, GitHub) - not documented
- Mobile app needs token refresh - not in requirements
- Password policies unclear - compliance requirement?
- Session timeout expectations - user assumption
- Multi-device login - implied but not stated

Action: Document unknowns, validate with stakeholders
```

### Geyser: Dynamic Forces (Explosive Change)

**What it reveals:**
- Pressures building under the surface
- Forces that will drive evolution
- Tensions between competing needs
- Scalability constraints
- External factors affecting the system

**Key Questions:**
- What forces am I not accounting for?
- What pressures are building beneath the surface?
- What will cause this design to break?
- What growth will we need to accommodate?
- What external changes will impact us?

**When to Apply:**
- Architecture design (anticipate forces)
- Planning for scale (growth pressures)
- Performance optimization (bottleneck forces)
- Evaluating technical debt (pressure to change)
- Capacity planning (resource forces)

**Example Investigation:**
```
GEYSER ANALYSIS: API Performance Degradation

Current State:
- API handles 100 req/sec comfortably
- Response times ~200ms average
- Single database instance

Forces Building (Geyser):
- User growth: 3x in 6 months
- Mobile app launching next quarter (5x traffic spike)
- Third-party integrations (unpredictable load)
- Real-time features planned (WebSocket pressure)
- Compliance audit (logging overhead)

Pressure Points:
- Database will hit CPU limit at 2x traffic
- Network bandwidth near capacity
- Cache invalidation becoming complex
- Session storage approaching memory limits

Action: Plan architecture evolution before forces erupt
```

### Gist: Essential Core (Irreducible Essence)

**What it reveals:**
- Core problem vs. incidental complexity
- Essential features vs. nice-to-haves
- What truly needs to be solved
- Where effort should focus
- What can be eliminated or simplified

**Key Questions:**
- Am I solving the essential problem?
- What is the irreducible core of this feature?
- What complexity is accidental vs. essential?
- What can be removed without losing value?
- What truly matters to users?

**When to Apply:**
- Requirements seem bloated (strip to essentials)
- Feature prioritization (focus on core)
- Code feels overly complex (find essence)
- Before starting implementation (validate core)
- Deciding what to refactor (essential vs. accidental)

**Example Investigation:**
```
GIST ANALYSIS: Document Collaboration Feature

Requested Features (28 items):
- Real-time editing
- Comment threads
- Version history
- Access control
- Export to PDF/Word
- Track changes
- Spell check
- Templates
- ...22 more features

Essential Core (Gist):
- Users need to work on same document simultaneously
- Users need to see who changed what
- Users need to control who can edit

Irreducible Feature Set:
1. Real-time collaborative editing (ESSENTIAL)
2. Basic version history (ESSENTIAL)
3. Simple access control (ESSENTIAL)
4. Export to PDF (NICE-TO-HAVE)
5. Everything else (DEFER)

Action: Ship minimal viable feature, validate before adding complexity
```

## Analysis Protocol

### The Three Questions Debug Workflow

When stuck on any problem:

1. **Ghost Analysis** (10 minutes):
   - List all assumptions explicitly
   - What context might be missing?
   - What unknowns exist?
   - Document in `GHOST_ASSUMPTIONS.md`

2. **Geyser Analysis** (10 minutes):
   - What forces are at play?
   - What pressures are building?
   - What will drive change?
   - Document in `GEYSER_FORCES.md`

3. **Gist Analysis** (10 minutes):
   - What's the essential problem?
   - What can be removed?
   - What truly matters?
   - Document in `GIST_ESSENCE.md`

4. **Synthesis** (10 minutes):
   - Do Ghost findings change requirements?
   - Do Geyser forces affect design?
   - Does Gist simplify the solution?
   - Update implementation plan

**Total Time**: 40 minutes for complete analysis

### Feature Gap Resolution Workflow

Use Geist for iterative feature completion:

1. **Ghost**: Identify unknown requirements and dependencies
   - Interview stakeholders
   - Review related features
   - Document assumptions

2. **Geyser**: Understand forces preventing completion
   - Analyze technical constraints
   - Identify competing priorities
   - Map external dependencies

3. **Gist**: Confirm essential features vs. nice-to-haves
   - Strip to minimal viable
   - Validate with users
   - Defer non-essential

4. **Iterate**: Continue until Gist confirms feature complete
   - Re-run Ghost (any new unknowns?)
   - Re-run Geyser (any new forces?)
   - Re-run Gist (still essential?)

### Architectural Decision Framework

Before major decisions:

1. **Ghost Analysis**: Document known unknowns and assumptions
   ```
   UNKNOWNS:
   - Will we need multi-tenancy? (ASK stakeholders)
   - What's the expected data volume? (ESTIMATE with team)
   - Are there compliance requirements? (RESEARCH)
   ```

2. **Geyser Analysis**: Map forces that will drive change
   ```
   FORCES:
   - User growth: 10x in 12 months (pressure on database)
   - Mobile app: Launching Q2 (need offline sync)
   - Acquisitions: Possible integrations (API flexibility)
   ```

3. **Gist Analysis**: Define essential vs. incidental concerns
   ```
   ESSENTIAL:
   - Fast reads (user-facing queries)
   - Reliable writes (data integrity)
   - Simple deployment (small team)

   DEFER:
   - Perfect schema (can evolve)
   - Every optimization (YAGNI)
   - Advanced features (not needed now)
   ```

4. **Decision**: Choose approach addressing all three dimensions

## Output Format

When conducting Geist analysis, provide:

### 1. Ghost Analysis
```
GHOST: Unknown Unknowns & Assumptions

Hidden Assumptions:
- [Assumption 1]: [Evidence or lack thereof]
- [Assumption 2]: [Where this came from]

Missing Context:
- [Context gap 1]: [What's not visible]
- [Context gap 2]: [Where to find it]

Unknown Requirements:
- [Unknown 1]: [How to validate]
- [Unknown 2]: [Who to ask]

Actions:
- [ ] Validate assumption X with stakeholder Y
- [ ] Research context gap A
- [ ] Document unknown B
```

### 2. Geyser Analysis
```
GEYSER: Dynamic Forces & Pressures

Building Pressures:
- [Pressure 1]: [Current state → Projected state]
- [Pressure 2]: [Timeline to breaking point]

Competing Forces:
- [Force 1 vs Force 2]: [Tension point]
- [Resolution strategy]

External Factors:
- [Factor 1]: [Impact on system]
- [Mitigation approach]

Pressure Points:
- [System limit 1]: [When it breaks]
- [System limit 2]: [How to prevent]

Actions:
- [ ] Plan for pressure point X
- [ ] Mitigate force Y
- [ ] Monitor factor Z
```

### 3. Gist Analysis
```
GIST: Essential Core & Simplification

Requested Features (N total):
- [Feature 1]
- [Feature 2]
- ...[N features]

Essential Core (Irreducible):
1. [Essential 1]: [Why essential]
2. [Essential 2]: [User value]
3. [Essential 3]: [Cannot remove without losing value]

Nice-to-Have (Defer):
- [Feature X]: [Can add later]
- [Feature Y]: [Not validated need]

Accidental Complexity (Remove):
- [Complexity A]: [Not needed]
- [Complexity B]: [Over-engineering]

Actions:
- [ ] Ship minimal viable with essentials 1-3
- [ ] Defer features X, Y until validated
- [ ] Remove complexities A, B
```

### 4. Synthesis & Recommendations
```
SYNTHESIS: Integrated Analysis

Ghost Impact on Requirements:
- [Unknown X] changes [Requirement Y]
- Document [Assumption Z] before proceeding

Geyser Impact on Design:
- [Force A] requires [Architectural change B]
- Plan for [Pressure C] in [Timeline D]

Gist Impact on Implementation:
- Focus on [Essential 1, 2, 3]
- Defer [Feature set X]
- Remove [Complexity Y]

Recommended Approach:
1. [Action based on Ghost findings]
2. [Action based on Geyser findings]
3. [Action based on Gist findings]

Next Steps:
- [ ] Validate Ghost assumptions
- [ ] Monitor Geyser pressures
- [ ] Implement Gist essentials
- [ ] Re-run analysis when stuck
```

## Real-World Example

### Scenario: E-commerce Checkout "90% Complete" for 3 Months

**Standard Debugging Failed**: Code works, tests pass, but product team says "not shippable"

**GEIST ANALYSIS:**

**Ghost: What aren't we seeing?**
```
Hidden Requirements:
- Tax calculation for international orders (not in specs)
- Payment gateway failover (assumed but not implemented)
- Abandoned cart recovery (marketing expects this)
- Gift card support (mentioned in sales deck)

Missing Context:
- Legal requirement for EU VAT handling
- PCI compliance constraints not documented
- Mobile app needs offline cart sync
- Customer service needs order modification flow

Actions Taken:
- ✅ Validated with legal (EU VAT required)
- ✅ Confirmed with security (PCI audit pending)
- ✅ Mobile team needs sync API (not in original requirements)
- ✅ Customer service workflow documented
```

**Geyser: What forces are building?**
```
Pressures:
- Black Friday coming (4x traffic spike in 6 weeks)
- International expansion delayed until checkout ready
- Payment processor migration scheduled (technical debt)
- Mobile app blocked on checkout API

Forces:
- Performance: Current design handles 100 orders/min, need 400
- Reliability: 99% uptime not sufficient for e-commerce (need 99.9%)
- Scalability: Single payment gateway is bottleneck

Actions Taken:
- ✅ Load testing revealed database bottleneck at 200 orders/min
- ✅ Payment gateway failover required for 99.9% target
- ✅ Caching strategy designed for Black Friday load
```

**Gist: What's truly essential?**
```
Current Implementation (47 features):
- Core checkout flow
- Payment processing
- Order confirmation
- Shipping calculation
- Tax calculation
- Discount codes
- Gift cards
- Abandoned cart
- ...39 more features

Essential Core (Must Ship):
1. Payment processing (ESSENTIAL - can't sell without this)
2. Order confirmation (ESSENTIAL - user needs receipt)
3. Shipping calculation (ESSENTIAL - fulfillment depends on it)
4. Tax calculation (ESSENTIAL - legal requirement)

Nice-to-Have (Ship Later):
5. Discount codes (DEFER - manual process exists)
6. Gift cards (DEFER - can add post-launch)
7. Abandoned cart (DEFER - optimize after data)

Complexity to Remove:
- Multi-step wizard (REMOVE - one-page checkout is simpler)
- Guest checkout + account creation hybrid (REMOVE - pick one)
- 15 payment methods (REMOVE - start with credit card + PayPal)

Actions Taken:
- ✅ Stripped to 4 essential features for v1
- ✅ Simplified to one-page checkout
- ✅ Reduced to 2 payment methods initially
- ✅ Shipped in 2 weeks, iterated based on real data
```

**RESULT**: Shipped in 2 weeks vs. 3 months of being "90% complete"

## References

- **[GEIST_DESIGN_INVESTIGATION_FRAMEWORK.md](../../10-geist-gap-analysis-framework/GEIST_DESIGN_INVESTIGATION_FRAMEWORK.md)** - Complete framework
- **[CONTINUOUS_GAP_ANALYSIS.md](../../10-geist-gap-analysis-framework/CONTINUOUS_GAP_ANALYSIS.md)** - Gap analysis workflow
- **[GEIST_COPILOT_INSTRUCTIONS.md](../../10-geist-gap-analysis-framework/GEIST_COPILOT_INSTRUCTIONS.md)** - AI assistant usage

## Success Metrics

**Problem Resolution:**
- Unstuck "90% complete" features
- Mysterious bugs explained
- Incomplete requirements clarified
- Architectural unknowns documented

**Efficiency:**
- 40 minutes for complete analysis
- 2-3 iterations to reach clarity
- Shipping weeks/months faster by focusing on essentials
