# Function Design Checklist

**Quick reference for designing and reviewing functions during development.**

Based on: [FUNCTIONS_AND_ROUTINES.md](../01-foundations/FUNCTIONS_AND_ROUTINES.md)

## Function Size Rules

| Metric | Target | Maximum | Why |
|--------|--------|---------|-----|
| **Lines** | 4-10 | 20-30 | Easier to understand, test, debug |
| **Parameters** | 0-1 | 3 | Fewer combinations to test |
| **Indentation** | 1-2 levels | 3 | Avoid deep nesting |
| **Abstraction** | One level | One | Consistent mental model |

**Golden Rule: If it doesn't fit on one screen, it's too long.**

## The "One Thing" Rule

A function should do ONE thing, do it WELL, do it ONLY.

### Tests for "One Thing"
- [ ] Can describe function without "and" or "or"
- [ ] All code at same abstraction level
- [ ] Can't extract another function with non-trivial name

```python
# ✗ Does TWO things
def save_user_and_send_email(user):
    database.save(user)      # Thing 1: persistence
    email.send(user.email)   # Thing 2: notification

# ✓ Each does ONE thing
def save_user(user):
    database.save(user)

def send_welcome_email(user):
    email.send(user.email)

def register_user(user):
    save_user(user)
    send_welcome_email(user)
```

## Valid Reasons to Create a Function

- [ ] **Reduce complexity** - Hide complex logic behind simple interface
- [ ] **Introduce abstraction** - Create meaningful business concepts
- [ ] **Avoid duplication** - DRY principle (Rule of Three)
- [ ] **Support subclassing** - Template methods for inheritance
- [ ] **Hide sequences** - Encapsulate order dependencies
- [ ] **Hide data structures** - Protect internal representations
- [ ] **Improve portability** - Isolate platform-specific code
- [ ] **Simplify boolean tests** - Replace complex conditionals

## Function Cohesion Levels

| Level | Quality | Description | Example |
|-------|---------|-------------|---------|
| **Functional** | ✓✓ Best | Does one operation | `calculate_interest(principal, rate)` |
| **Sequential** | ✓ Good | Data flows through steps | `process_image(raw) → validate → resize → compress` |
| **Communicational** | ~ OK | Works on same data | `update_user_profile(user, updates)` |
| **Temporal** | ⚠ Weak | Happens at same time | `initialize_app()` - unrelated setup |
| **Procedural** | ✗ Poor | Steps in sequence | Mixed unrelated operations |
| **Logical** | ✗✗ Bad | Switch on type | `perform_operation(type, data)` |
| **Coincidental** | ✗✗✗ Worst | No relationship | `Utilities` class grab bag |

**Target: Functional or Sequential cohesion**

## Parameter Count Guidelines

| Count | Quality | Notes |
|-------|---------|-------|
| **0 (niladic)** | ✓ Ideal | Easiest to use and test |
| **1 (monadic)** | ✓ Good | Very clear |
| **2 (dyadic)** | ~ OK | Requires mental effort |
| **3 (triadic)** | ⚠ Questionable | Consider parameter object |
| **4+ (polyadic)** | ✗ Avoid | Use parameter object |

### Parameter Solutions

```python
# ✗ Too many parameters
def create_invoice(customer_id, amount, tax, currency, due_date, desc):
    pass

# ✓ Parameter object
class InvoiceData:
    customer_id: str
    amount: float
    tax_rate: float
    currency: str
    due_date: date
    description: str

def create_invoice(data: InvoiceData):
    pass
```

## Parameter Anti-Patterns

### Flag Arguments (Boolean Parameters)
```python
# ✗ Flag argument - function does TWO things
def save_user(user, send_email):
    database.save(user)
    if send_email:
        email.send(user.email)

# ✓ Separate functions
def save_user(user):
    database.save(user)

def save_user_and_send_welcome(user):
    save_user(user)
    send_welcome_email(user)
```

### Output Parameters
```python
# ✗ Output parameter - confusing
def calculate_totals(order, result):
    result.subtotal = calc_subtotal(order)
    result.tax = calc_tax(order)

# ✓ Return value - clear
def calculate_totals(order):
    subtotal = calc_subtotal(order)
    tax = calc_tax(order)
    return TotalResult(subtotal, tax)
```

## Abstraction Levels

**Rule: All statements in a function at same abstraction level.**

```python
# ✗ Mixed abstraction levels
def generate_report(user_id):
    user = fetch_user(user_id)        # High level
    html = "<html><body>"              # Low level - string manipulation
    html += f"<h1>{user.name}</h1>"    # Mixed!
    orders = fetch_orders(user_id)     # High level
    for order in orders:               # Low level loop
        html += f"<li>{order.id}</li>"
    save_file(html)                    # High level

# ✓ Consistent abstraction level
def generate_report(user_id):
    user = fetch_user(user_id)         # High level
    orders = fetch_orders(user_id)     # High level
    html = render_report(user, orders) # High level
    save_report(user_id, html)         # High level

def render_report(user, orders):
    header = render_header(user)       # Medium level
    order_list = render_orders(orders) # Medium level
    return wrap_html(header, order_list)
```

## Function Naming Patterns

### Function Names (Verbs)
```python
✓ calculate_total_revenue()
✓ validate_user_credentials()
✓ send_email_notification()
✓ is_valid_email()  # Boolean returns

✗ revenue()  # Noun - unclear
✗ user()     # What about user?
```

### Command-Query Separation
```python
# Commands: Perform action, return nothing
def save_user(user): ...
def send_email(recipient, body): ...

# Queries: Return value, no side effects
def get_user(user_id): ...
def calculate_total(items): ...

# ✗ Violation: Both command and query
def set_and_return_username(user, name):
    user.name = name  # Command
    return name       # Query - confusing!
```

## Function Design Checklist

### Design Phase
- [ ] Function has single, clear purpose
- [ ] Name accurately describes what it does
- [ ] Function has high cohesion (functional/sequential)
- [ ] All code at one abstraction level
- [ ] 0-2 parameters (3 maximum)
- [ ] No flag/boolean parameters
- [ ] No output parameters (use return values)

### Implementation Phase
- [ ] Function is small (< 20 lines preferred)
- [ ] No duplicate code
- [ ] No hidden side effects
- [ ] No temporal coupling (order dependencies)
- [ ] Command-query separation maintained
- [ ] Follows team naming conventions

### Error Handling
- [ ] Errors handled appropriately
- [ ] No swallowed exceptions
- [ ] Clear error messages
- [ ] Input validation at boundaries

### Testing
- [ ] Function is testable (clear inputs/outputs)
- [ ] Has comprehensive unit tests
- [ ] Edge cases tested
- [ ] Behavior documented in tests

## Common Anti-Patterns

| Anti-Pattern | Problem | Solution |
|--------------|---------|----------|
| **God Function** | Does everything (200+ lines) | Extract smaller functions |
| **Flag Function** | Boolean controls behavior | Separate functions |
| **Swiss Army** | Type parameter controls logic | Polymorphism |
| **Mystery Function** | Unclear name | Descriptive name |
| **Side Effect** | Hidden state changes | Explicit or separate |
| **Deep Nesting** | 5+ levels of indentation | Guard clauses, extract |
| **Output Parameters** | Modifies parameters | Return values |

## Guard Clauses Pattern

```python
# ✗ Deep nesting
def process_order(order):
    if order is not None:
        if order.items:
            if order.customer:
                if order.customer.is_active:
                    # Finally do work 5 levels deep!
                    pass

# ✓ Guard clauses
def process_order(order):
    if order is None:
        raise ValueError("Order required")
    if not order.items:
        raise ValueError("Order must have items")
    if not order.customer:
        raise ValueError("Order must have customer")
    if not order.customer.is_active:
        raise ValueError("Customer must be active")

    # Do work at top level
```

## DRY (Don't Repeat Yourself)

**Rule of Three**: Third time you write similar code, refactor it.

```python
# ✗ Duplication
def create_user(email, password):
    if not email or "@" not in email:
        raise ValueError("Invalid email")
    if not password or len(password) < 8:
        raise ValueError("Password too short")
    # create user

def update_user(user_id, email, password):
    if not email or "@" not in email:  # Duplicated!
        raise ValueError("Invalid email")
    if not password or len(password) < 8:  # Duplicated!
        raise ValueError("Password too short")
    # update user

# ✓ Extracted common logic
def validate_email(email):
    if not email or "@" not in email:
        raise ValueError("Invalid email")

def validate_password(password):
    if not password or len(password) < 8:
        raise ValueError("Password too short")

def create_user(email, password):
    validate_email(email)
    validate_password(password)
    # create user

def update_user(user_id, email, password):
    validate_email(email)
    validate_password(password)
    # update user
```

## Quick Decision Tree

```
Is the function > 20 lines?
    ✓ Extract smaller functions

Can you describe it without "and"/"or"?
    ✗ Function does multiple things - split it

Are there > 3 parameters?
    ✓ Create parameter object

Is there a boolean parameter?
    ✓ Split into separate functions

Is code duplicated elsewhere?
    ✓ Extract to shared function

Is nesting > 3 levels deep?
    ✓ Use guard clauses or extract

Does it have side effects?
    ✓ Separate command from query OR make explicit
```

## Stepdown Rule

**Code should read top-down like prose:**
- High-level orchestration at top
- Next level of detail below
- Lowest level at bottom

```python
# Read top to bottom, high to low abstraction
def process_order(order):           # Highest level
    validate_order(order)
    calculate_totals(order)
    charge_payment(order)
    fulfill_order(order)

def validate_order(order):          # Next level
    validate_customer(order.customer)
    validate_items(order.items)
    validate_shipping(order.address)

def validate_customer(customer):    # Lowest level details
    if customer.is_blocked():
        raise ValidationError("Customer blocked")
```

## References

- **Full Guide**: [01-foundations/FUNCTIONS_AND_ROUTINES.md](../01-foundations/FUNCTIONS_AND_ROUTINES.md)
- **Source**: Clean Code (Ch. 3), Code Complete 2 (Ch. 7)

---

**Remember**: Small functions with clear names are the foundation of maintainable code.
