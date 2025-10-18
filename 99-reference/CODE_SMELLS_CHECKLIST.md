# Code Smells Checklist

**Quick reference for identifying code smells during development and code review.**

Based on: Clean Code (Chapter 17), Refactoring by Martin Fowler

## How to Use This Checklist

1. Review code section by section
2. Check for each smell category
3. Note smells for refactoring
4. Prioritize by impact and effort

## Function-Level Smells

### Long Function
- [ ] Function > 20-30 lines
- [ ] Can't understand function at a glance
- [ ] Multiple levels of abstraction
- [ ] Lots of variables and parameters

**Fix:** Extract Method, Replace Temp with Query

### Too Many Parameters
- [ ] More than 3-4 parameters
- [ ] Parameters are tightly related
- [ ] Same parameters passed together often

**Fix:** Introduce Parameter Object, Preserve Whole Object

### Flag Arguments
- [ ] Boolean parameter controls behavior
- [ ] Function does different things based on flag
- [ ] Name doesn't reveal flag meaning

**Fix:** Split into separate functions

```python
# ✗ Smell
def save_user(user, send_email): ...

# ✓ Fixed
def save_user(user): ...
def save_user_and_notify(user): ...
```

### Output Arguments
- [ ] Function modifies parameter instead of returning
- [ ] Caller expects modified parameter
- [ ] Confusing data flow

**Fix:** Return value instead

### Dead Code
- [ ] Unreachable code paths
- [ ] Unused functions
- [ ] Commented-out code blocks

**Fix:** Delete it (version control remembers)

### Duplicate Code
- [ ] Same code in multiple places
- [ ] Similar code with minor variations
- [ ] Copy-paste programming

**Fix:** Extract Method, Pull Up Method, Form Template Method

## Class-Level Smells

### Large Class
- [ ] Class > 200-300 lines
- [ ] Too many instance variables (>7-10)
- [ ] Too many methods (>20)
- [ ] Multiple responsibilities

**Fix:** Extract Class, Extract Subclass

### Feature Envy
- [ ] Method uses data from another class more than its own
- [ ] Method seems to belong in another class
- [ ] Excessive getter calls

**Fix:** Move Method, Extract Method

```python
# ✗ Smell - Feature Envy
class OrderProcessor:
    def calculate_total(self, order):
        total = 0
        for item in order.get_items():
            total += item.get_price() * item.get_quantity()
        return total - order.get_discount()

# ✓ Fixed - Move to Order
class Order:
    def calculate_total(self):
        total = sum(item.price * item.quantity for item in self.items)
        return total - self.discount
```

### Inappropriate Intimacy
- [ ] Classes access each other's private data
- [ ] Too much coupling between classes
- [ ] One class depends heavily on implementation of another

**Fix:** Move Method, Extract Class, Hide Delegate

### Divergent Change
- [ ] One class changes for many different reasons
- [ ] Different actors cause changes
- [ ] SRP violation

**Fix:** Extract Class (split by responsibility)

### Shotgun Surgery
- [ ] One change requires modifications in many classes
- [ ] Logic scattered across system
- [ ] Hard to make consistent changes

**Fix:** Move Method, Inline Class

### Data Class
- [ ] Class with only fields and getters/setters
- [ ] No behavior, just data container
- [ ] Other classes manipulate its data

**Fix:** Move Method (move behavior to data class)

## Naming Smells

### Unclear Names
- [ ] Name doesn't reveal intent
- [ ] Generic names (`data`, `info`, `temp`, `value`)
- [ ] Single letter names (except loop counters)
- [ ] Abbreviations (`usrAcct`, `tmp`)

**Fix:** Rename Variable/Method/Class

### Inconsistent Names
- [ ] Same concept named differently
- [ ] Different concepts named similarly
- [ ] Inconsistent verb pairs (`get`/`retrieve`)

**Fix:** Rename to consistent vocabulary

### Type Encodings
- [ ] Hungarian notation (`str_name`, `int_count`)
- [ ] Type in name when type system handles it
- [ ] Prefixes like `m_` for members

**Fix:** Remove encoding, rely on type system

## Comment Smells

### Redundant Comments
- [ ] Comment restates code
- [ ] Comment doesn't add information
- [ ] Code could be self-explanatory

**Fix:** Delete comment, improve code clarity

```python
# ✗ Redundant
i = i + 1  # Increment i

# ✓ Self-explanatory (no comment needed)
current_index += 1
```

### Misleading Comments
- [ ] Comment contradicts code
- [ ] Comment is outdated
- [ ] Comment describes old implementation

**Fix:** Update or delete comment

### Commented-Out Code
- [ ] Blocks of code commented out
- [ ] Old implementations left for reference
- [ ] Debugging code not removed

**Fix:** Delete (version control remembers)

### Required Comments
- [ ] Public API lacks documentation
- [ ] Complex algorithm not explained
- [ ] Business rules not documented

**Fix:** Add meaningful documentation

## Structure Smells

### Deep Nesting
- [ ] More than 3 levels of indentation
- [ ] Nested if statements
- [ ] Nested loops

**Fix:** Guard Clauses, Extract Method

```python
# ✗ Deep nesting
def process(order):
    if order:
        if order.items:
            if order.customer:
                if order.customer.is_active:
                    # Finally do work

# ✓ Guard clauses
def process(order):
    if not order:
        raise ValueError("Order required")
    if not order.items:
        raise ValueError("Items required")
    if not order.customer or not order.customer.is_active:
        raise ValueError("Active customer required")
    # Do work at top level
```

### Long Parameter List
- [ ] 4+ parameters
- [ ] Parameters often passed together
- [ ] Hard to remember order

**Fix:** Introduce Parameter Object

### Primitive Obsession
- [ ] Using primitives instead of small objects
- [ ] Data that travels together as primitives
- [ ] No encapsulation of related data

**Fix:** Replace Data Value with Object

```python
# ✗ Primitive obsession
def create_address(street, city, state, zip):
    pass

# ✓ Value object
class Address:
    def __init__(self, street, city, state, zip_code):
        self.street = street
        self.city = city
        self.state = state
        self.zip_code = zip_code

def create_address(address: Address):
    pass
```

### Data Clumps
- [ ] Same group of data items together
- [ ] Parameters that travel in groups
- [ ] Fields that belong together

**Fix:** Extract Class, Introduce Parameter Object

### Switch Statements
- [ ] Switch/if-else on type codes
- [ ] Same switch logic in multiple places
- [ ] Adding new types requires changing switches

**Fix:** Replace Conditional with Polymorphism

```python
# ✗ Switch on type
def calculate_area(shape):
    if shape.type == "circle":
        return math.pi * shape.radius ** 2
    elif shape.type == "rectangle":
        return shape.width * shape.height

# ✓ Polymorphism
class Shape(ABC):
    @abstractmethod
    def area(self): pass

class Circle(Shape):
    def area(self):
        return math.pi * self.radius ** 2
```

### Temporary Field
- [ ] Field only set in certain circumstances
- [ ] Field often null/empty
- [ ] Confusing object state

**Fix:** Extract Class, Introduce Null Object

### Speculative Generality
- [ ] Abstract classes with single implementation
- [ ] Parameters never used
- [ ] Future features that aren't needed

**Fix:** Collapse Hierarchy, Inline Class, Remove Parameter

## General Smells

### Middle Man
- [ ] Class delegates most work to another class
- [ ] Excessive delegation
- [ ] Wrapper adds no value

**Fix:** Remove Middle Man, Inline Method

### Inappropriate Static
- [ ] Function should be instance method
- [ ] Static hides polymorphic behavior
- [ ] Can't override or test easily

**Fix:** Convert to instance method

### Inconsistent Abstraction Levels
- [ ] High and low-level operations mixed
- [ ] Implementation details in high-level code
- [ ] Can't tell what's essential vs detail

**Fix:** Extract Method to separate levels

### Magic Numbers
- [ ] Unexplained numeric literals
- [ ] Constants without names
- [ ] Repeated numbers

**Fix:** Replace Magic Number with Named Constant

```python
# ✗ Magic number
if age > 18: ...

# ✓ Named constant
LEGAL_ADULT_AGE = 18
if age > LEGAL_ADULT_AGE: ...
```

### Vertical Separation
- [ ] Related code far apart
- [ ] Have to scroll to understand
- [ ] Variables declared far from use

**Fix:** Move code closer together

### Hidden Temporal Coupling
- [ ] Operations must occur in order
- [ ] Order not enforced by structure
- [ ] Easy to call in wrong sequence

**Fix:** Pass results, use method chaining

## Error Handling Smells

### Swallowed Exceptions
- [ ] Empty catch blocks
- [ ] Exceptions caught and ignored
- [ ] No logging or recovery

**Fix:** Handle, log, or let it propagate

### Returning Null
- [ ] Functions return null for "not found"
- [ ] Requires null checks everywhere
- [ ] Null checks easily forgotten

**Fix:** Return empty collection, throw exception, use Optional

### Passing Null
- [ ] Functions accept null parameters
- [ ] Null means different things
- [ ] Defensive null checks throughout

**Fix:** Validate and reject null, use Null Object

## Testing Smells

### Insufficient Tests
- [ ] Coverage < 85-90%
- [ ] Edge cases not tested
- [ ] Only happy path tested

**Fix:** Add missing test cases

### Ignored Tests
- [ ] Tests skipped/commented out
- [ ] Failing tests marked to skip
- [ ] "TODO: Fix this test"

**Fix:** Fix or delete tests

### Test Code Duplication
- [ ] Setup code duplicated
- [ ] Same assertions in multiple tests
- [ ] Copy-paste test code

**Fix:** Extract test helpers, use fixtures

## Smell Priority Matrix

| Severity | Smell | Impact | Fix Effort |
|----------|-------|--------|------------|
| **CRITICAL** | Divergent Change | High | Medium |
| **CRITICAL** | Shotgun Surgery | High | High |
| **CRITICAL** | Swallowed Exceptions | High | Low |
| **HIGH** | Long Function | Medium | Low |
| **HIGH** | Large Class | Medium | Medium |
| **HIGH** | Feature Envy | Medium | Medium |
| **HIGH** | Duplicate Code | Medium | Low |
| **MEDIUM** | Long Parameter List | Low | Low |
| **MEDIUM** | Switch Statements | Medium | Medium |
| **MEDIUM** | Primitive Obsession | Low | Low |
| **LOW** | Unclear Names | Low | Low |
| **LOW** | Magic Numbers | Low | Low |
| **LOW** | Redundant Comments | Low | Low |

## Quick Review Checklist

### File Level (30 seconds)
- [ ] File length reasonable (< 500 lines)
- [ ] Class count appropriate (1-3 per file)
- [ ] No massive blocks of commented code
- [ ] Consistent formatting

### Class Level (1 minute)
- [ ] Single responsibility
- [ ] Reasonable size (< 300 lines)
- [ ] Clear purpose from name
- [ ] No god classes

### Function Level (30 seconds each)
- [ ] Small (< 20 lines)
- [ ] Does one thing
- [ ] Few parameters (< 4)
- [ ] Clear name
- [ ] One abstraction level

### Code Block Level (quick scan)
- [ ] No deep nesting (< 3 levels)
- [ ] No duplication
- [ ] No magic numbers
- [ ] Clear variable names

## When to Refactor

**Rule of Three:**
- First time: Just do it
- Second time: Wince but duplicate
- Third time: Refactor

**Boy Scout Rule:**
- Always leave code cleaner than you found it

**Before Adding Features:**
- Refactor to make feature addition easy
- Then add the feature

**During Code Review:**
- Identify smells before merging
- Small refactorings during review
- Plan larger refactorings as stories

## References

- **Full Guide**: [05-refactoring-and-improvement/](../05-refactoring-and-improvement/)
- **Source**: Clean Code (Ch. 17), Refactoring by Martin Fowler

---

**Remember**: Code smells indicate problems, not disasters. Refactor incrementally.
