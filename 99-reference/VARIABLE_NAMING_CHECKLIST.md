# Variable Naming Checklist

**Quick reference for naming variables, functions, and classes during development and code review.**

Based on: [VARIABLE_NAMING.md](../01-foundations/VARIABLE_NAMING.md)

## Core Naming Principles

### Intention-Revealing Names
- [ ] Name reveals WHY it exists, WHAT it does, HOW it's used
- [ ] No comments needed to explain the name
- [ ] Clear to someone unfamiliar with the code

### Avoid Disinformation
- [ ] Name doesn't suggest wrong type (e.g., `accountList` for a dict)
- [ ] Name doesn't mislead about purpose
- [ ] No platform-specific abbreviations (e.g., `hp` could mean many things)

### Meaningful Distinctions
- [ ] No number series (e.g., `data1`, `data2`)
- [ ] No noise words (e.g., `userData` vs `userInfo`)
- [ ] Distinctions inform about differences

### Pronounceable & Searchable
- [ ] Can pronounce the name in conversation
- [ ] Can search for name in codebase (not single letter unless tiny scope)

## Optimal Name Length

| Scope | Length | Examples |
|-------|--------|----------|
| **Tiny (3-5 lines)** | 1-5 chars | `i`, `x`, `sum` |
| **Short (function locals)** | 8-12 chars | `user_count`, `total` |
| **Medium (parameters, class members)** | 10-16 chars | `account_balance`, `order_total` |
| **Long (global, module-level)** | 16+ chars | `DEFAULT_CONNECTION_TIMEOUT`, `MAX_RETRY_ATTEMPTS` |

**Sweet spot: 10-16 characters for most variables**

## Names by Variable Type

### Booleans
```
Pattern: is/has/can/should + predicate
✓ is_valid, has_permission, can_edit, should_retry
✗ status, flag, valid (not clearly boolean)
✗ not_valid (avoid negatives - confusing double negatives)
```

### Collections
```
Pattern: plural nouns or collective nouns
✓ users, active_accounts, pending_orders
✓ user_registry, account_pool, task_queue (collective)
✗ user (singular for collection)
✗ list1, array (generic)
```

### Counters/Accumulators
```
Pattern: descriptive + count/total/sum/average/max/min/index
✓ user_count, total_revenue, running_total
✓ current_index, start_index, salary_average
✗ count, total, avg (what are you counting?)
```

### Constants
```
Pattern: SCREAMING_SNAKE_CASE
✓ MAX_CONNECTIONS, DEFAULT_TIMEOUT_SECONDS
✓ API_BASE_URL, SECONDS_PER_DAY
✗ maxConnections, default_timeout (not constant style)
```

### Classes
```
Pattern: Nouns and noun phrases (PascalCase)
✓ UserAccount, OrderProcessor, PaymentGateway
✗ Manager, Data, Info (too generic)
✗ ProcessData, HandleUser (verbs - should be functions)
```

### Functions/Methods
```
Pattern: Verbs and verb phrases
✓ calculate_total_revenue(), validate_credentials()
✓ send_email(), is_valid_email() (boolean returns)
✗ data(), user(), total() (nouns - unclear action)
```

## Quick Checks

### Before Naming
- [ ] I understand what this represents
- [ ] I know the scope and lifetime
- [ ] I know domain context (technical or business)

### Quality Checks
- [ ] **Length**: Appropriate for scope (10-16 chars ideal)
- [ ] **Clarity**: Clear without needing comment
- [ ] **Accuracy**: Doesn't mislead about type/purpose
- [ ] **Consistency**: Follows team conventions
- [ ] **Searchability**: Not single letter (unless tiny scope)

### Anti-Patterns to Avoid
- [ ] ❌ Single letters (except `i`, `j`, `k` in tiny loops)
- [ ] ❌ Abbreviations (`usrAcct`, `tmp`, `ctx`)
- [ ] ❌ Type encodings (`str_name`, `int_count`, `lst_users`)
- [ ] ❌ Generic names (`data`, `info`, `temp`, `value`)
- [ ] ❌ Noise words without meaning (`userData` vs `userInfo`)
- [ ] ❌ Inconsistent opposites (`begin/stop` - should be `begin/end`)

## Language-Specific Conventions

### Python
```python
snake_case          # Variables, functions
PascalCase          # Classes
SCREAMING_SNAKE     # Constants
_private            # Internal (single underscore)
```

### TypeScript/JavaScript
```typescript
camelCase           // Variables, functions
PascalCase          // Classes
SCREAMING_SNAKE     // Constants
#private            // Private fields (TC39)
```

### Java
```java
camelCase           // Variables, methods
PascalCase          // Classes
SCREAMING_SNAKE     // Constants
```

## Common Naming Opposites

Use consistent pairs throughout codebase:

| ✓ Use | ✗ Avoid |
|-------|---------|
| begin / end | start / stop |
| first / last | top / bottom |
| min / max | minimum / maximum |
| source / destination | from / to |
| get / set | retrieve / assign |
| add / remove | insert / delete |
| create / destroy | new / kill |
| open / close | open / shut |
| show / hide | display / conceal |

## Context and Abstraction

### Add Context When Needed
```python
# Poor - no context
street = "123 Main St"
city = "Springfield"

# Better - context in names
address_street = "123 Main St"
address_city = "Springfield"

# Best - context through structure
class Address:
    street = "123 Main St"
    city = "Springfield"
```

### Don't Add Gratuitous Context
```python
# ✗ Too much context
class GasStationDeluxeAccountInfo: pass
class GasStationDeluxeAddress: pass

# ✓ Let namespaces provide context
# In gas_station_deluxe module:
class AccountInfo: pass
class Address: pass
```

## Domain-Specific Naming

### Solution Domain (Technical)
```python
# Use CS/engineering terms programmers know
job_queue = deque()
visitor_pattern = VisitorPattern()
account_repository = AccountRepository()
```

### Problem Domain (Business)
```python
# Use business language domain experts use
policy_holder = get_customer()
premium_amount = calculate_insurance()
underwriting_decision = evaluate_risk()
```

## The Naming Hierarchy

Priority order (most to least important):

1. **Clarity** - Must be understandable
2. **Accuracy** - Must be truthful
3. **Searchability** - Must be findable
4. **Consistency** - Must match conventions
5. **Conciseness** - As short as possible after meeting above

## Quick Decision Tree

```
Can you describe it in < 16 chars without abbreviating?
    ✓ Use full descriptive name
    ✗ Consider breaking into smaller concepts

Does it need a comment to explain it?
    ✓ Name doesn't reveal intent - rename
    ✗ Good name

Is this name used elsewhere with different meaning?
    ✓ Add distinguishing context
    ✗ Good name

Would this confuse a new team member?
    ✓ Add clarity or context
    ✗ Good name
```

## References

- **Full Guide**: [01-foundations/VARIABLE_NAMING.md](../01-foundations/VARIABLE_NAMING.md)
- **Source**: Code Complete 2 (Ch. 11), Clean Code (Ch. 2)

---

**Remember**: Code is read 10x more than written. Invest time in names.
