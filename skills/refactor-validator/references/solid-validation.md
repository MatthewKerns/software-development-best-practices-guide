# SOLID Validation Criteria

Based on: Clean Architecture by Robert C. Martin (Chapters 7-11)

## Single Responsibility Principle (SRP)

**"A module should have one, and only one, reason to change."**

### Validation Checklist
- [ ] Can you name the module's single responsibility in one phrase?
- [ ] Would changes from different stakeholders affect this module?
- [ ] Does the module name accurately describe its responsibility?
- [ ] Are there methods that serve different "actors" (e.g., CFO vs CTO)?

### SRP Violation Indicators
| Indicator | Example | Severity |
|-----------|---------|----------|
| Multiple unrelated public methods | `saveToDb()` + `sendEmail()` + `formatReport()` | HIGH |
| Module name contains "and" or "Manager" | `UserAndOrderManager` | MEDIUM |
| >3 distinct import domains | Imports DB + email + auth + logging + formatting | HIGH |
| Different change frequencies | Some methods change weekly, others yearly | MEDIUM |

### Decision
- PASS: One clear actor, one reason to change
- VIOLATION: Multiple actors would independently cause changes

## Open/Closed Principle (OCP)

**"Open for extension, closed for modification."**

### Validation Checklist
- [ ] Can new behavior be added without modifying existing code?
- [ ] Are there type-switch patterns (if/else on type codes)?
- [ ] Is polymorphism used where types vary?
- [ ] Are configuration points available for customization?

### OCP Violation Indicators
| Indicator | Example | Severity |
|-----------|---------|----------|
| Switch on type string/enum | `if (type === 'a') ... else if (type === 'b')` | HIGH |
| Same switch in multiple places | Type check duplicated across files | CRITICAL |
| Adding feature requires modifying existing function | New payment type = edit processPayment() | HIGH |

### Decision
- PASS: New variants can be added via new classes/modules
- VIOLATION: Adding new behavior requires editing existing code

## Liskov Substitution Principle (LSP)

**"Subtypes must be substitutable for their base types."**

### Validation Checklist
- [ ] Can derived class replace base class without breaking callers?
- [ ] Does derived class strengthen preconditions? (BAD)
- [ ] Does derived class weaken postconditions? (BAD)
- [ ] Does derived class throw unexpected exceptions?
- [ ] Are there `instanceof` checks for specific subtypes?

### LSP Violation Indicators
| Indicator | Example | Severity |
|-----------|---------|----------|
| `instanceof` check for subtypes | `if (x instanceof SpecificType)` | HIGH |
| Empty/stub method overrides | `eat() { /* robots don't eat */ }` | MEDIUM |
| Overridden method changes side effects | `setWidth()` also changes height | HIGH |
| Derived class throws new exception types | Base never throws, derived does | MEDIUM |

### Decision
- PASS: All implementations honor the interface contract
- N/A: No inheritance hierarchy in this module
- VIOLATION: Substitution would break caller assumptions

## Interface Segregation Principle (ISP)

**"No client should depend on methods it doesn't use."**

### Validation Checklist
- [ ] Do any interface implementations have empty/stub methods?
- [ ] Does any consumer use <50% of the interface's methods?
- [ ] Are there "fat" interfaces with >10 methods?
- [ ] Would splitting benefit any consumer?

### ISP Violation Indicators
| Indicator | Example | Severity |
|-----------|---------|----------|
| Interface >10 methods | `IChatService` with 15 methods | MEDIUM |
| Consumer uses <3 of 10 methods | Component only calls `send()` from 10-method interface | HIGH |
| Empty method implementations | `sleep() { }` on a Robot class | MEDIUM |
| "God interface" | One interface for all service operations | HIGH |

### Decision
- PASS: Interfaces are focused, clients use all methods
- VIOLATION: Clients forced to depend on unused methods

## Dependency Inversion Principle (DIP)

**"Depend on abstractions, not concretions."**

### Validation Checklist
- [ ] Do high-level modules import low-level concrete classes?
- [ ] Are dependencies injected (constructor, props, parameters)?
- [ ] Can implementations be swapped without changing high-level code?
- [ ] Do dependency arrows point toward abstractions?

### DIP Violation Indicators
| Indicator | Example | Severity |
|-----------|---------|----------|
| `new ConcreteClass()` in high-level module | `this.db = new MySQLDatabase()` | HIGH |
| Import concrete service directly | `import { SupabaseFoo } from './SupabaseFoo'` in component | MEDIUM |
| Can't test without real dependency | Must have DB connection to test business logic | HIGH |
| Circular dependency | A imports B imports A | CRITICAL |

### Decision
- PASS: Dependencies point toward abstractions, implementations injected
- VIOLATION: High-level code hardcodes low-level concrete dependencies

## Common Patterns in Refactored Code

After refactoring, verify these patterns are present:

### Service Layer
- Interface defined: `src/services/interfaces/IFooService.ts`
- Implementation: `src/services/FooService.ts` implements interface
- Orchestrator depends on interface, not implementation
- Can test orchestrator with mock service

### Hook Layer
- Hook manages state and side effects
- Component receives state via hook return value
- Hook doesn't know about UI (no JSX)
- Component doesn't know about data fetching (no API calls)

### Component Layer
- Component renders UI from props/hook state
- Event handlers delegate to hook or callback props
- No business logic in JSX
- No direct service calls

## Scoring Guide

| Score | Criteria |
|-------|----------|
| 5/5 PASS | All 5 principles validated, no violations |
| 4/5 | One principle N/A or minor note |
| 3/5 | One violation, acceptable with justification |
| 2/5 | Two violations, needs attention |
| 1/5 | Three+ violations, refactoring didn't achieve its goals |
