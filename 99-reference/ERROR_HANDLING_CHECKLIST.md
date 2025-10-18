# Error Handling Checklist

**Quick reference for implementing robust error handling during development and code review.**

Based on: [ERROR_HANDLING.md](../01-foundations/ERROR_HANDLING.md)

## Correctness vs Robustness

**Choose your strategy based on criticality:**

| System Type | Strategy | Approach |
|-------------|----------|----------|
| **Life-critical** (medical, aviation) | Correctness | Fail rather than give wrong answer |
| **Financial** (banking, trading) | Correctness | Exact results or exception |
| **Consumer apps** (web, mobile) | Robustness | Continue with degraded service |
| **Data pipelines** (ETL, batch) | Robustness | Process remaining items |
| **Hybrid** (e-commerce) | Both | Critical=correct, optional=robust |

## Error Handling Techniques

| Technique | When to Use | Example |
|-----------|-------------|---------|
| **Return neutral value** | Safe default is reasonable | Return 0 for failed balance fetch (with logging) |
| **Return next valid** | Approximation acceptable | Skip corrupted data point, read next |
| **Return previous valid** | Stale data better than none | Use cached price if API fails |
| **Log warning, continue** | Error noteworthy but not critical | Analytics failure shouldn't stop payment |
| **Throw exception** | Caller should handle | Invalid credentials throw `AuthenticationException` |
| **Return error code** | Legacy/C-style APIs | Status codes for backward compatibility |
| **Shut down** | Continuing would cause damage | Can't run without database - exit(1) |

## Use Exceptions (Not Error Codes)

### Why Exceptions Win
- **Separation**: Error handling separate from business logic
- **Cannot ignore**: Must handle or propagate
- **Rich context**: Stack trace, message, chaining

```python
# ✗ Error codes clutter logic
def process_order(order):
    code = validate_order(order)
    if code != 0:
        return code
    code = check_inventory(order)
    if code != 0:
        return code
    # Business logic buried in error checks

# ✓ Exceptions separate concerns
def process_order(order):
    validate_order(order)
    check_inventory(order)
    process_payment(order)
    # Clear business logic flow
```

## Exception Design Principles

### 1. Write Try-Catch-Finally First
```python
# Start with structure
def process_file(filename):
    try:
        with open(filename) as f:
            # TODO: processing logic
    except IOError as e:
        # TODO: error handling
    finally:
        # TODO: cleanup
```

### 2. Provide Rich Context
```python
# ✗ Generic exception
raise Exception("Error")

# ✓ Rich context
raise UserNotFoundError(
    f"User not found: {user_id}",
    context={
        "user_id": user_id,
        "timestamp": datetime.now(),
        "correlation_id": request_id
    }
)
```

### 3. Design for Caller's Needs
```python
# ✗ Exposing implementation details
class APIClient:
    def fetch():
        raise ConnectionTimeoutException()  # Too specific
        raise SSLCertificateException()     # Caller must handle many
        raise JSONParseException()

# ✓ Caller-focused hierarchy
class APIError(Exception): pass
class APIConnectionError(APIError): pass
class APIDataError(APIError): pass
class APIRateLimitError(APIError): pass

# Caller handles business-level exceptions
try:
    data = api.fetch()
except APIRateLimitError:
    time.sleep(60)
    data = api.fetch()
except APIError:
    data = get_cached_data()
```

## Don't Return Null

**Problem:** Null checks required everywhere, easy to forget.

### Solutions

| Solution | When to Use | Example |
|----------|-------------|---------|
| **Throw exception** | Absence is exceptional | `user = get_user(id)` throws if not found |
| **Null object pattern** | Safe default behavior exists | Return `NullUser` with no-op methods |
| **Optional type** | Explicit presence/absence | `Optional<User>` forces handling |
| **Empty collection** | Collections should never be null | Return `[]` not `None` |

```python
# ✗ Returning null
def get_user_orders(user_id):
    orders = db.query(user_id)
    return orders if orders else None  # BAD

# Caller must check
orders = get_user_orders(user_id)
if orders is not None:  # Easy to forget
    for order in orders:
        process(order)

# ✓ Return empty collection
def get_user_orders(user_id):
    orders = db.query(user_id)
    return orders if orders else []  # Always return list

# Clean caller code
orders = get_user_orders(user_id)
for order in orders:  # Works even if empty
    process(order)
```

## Don't Pass Null

```python
# ✗ Accepting null
def process_order(order):
    if order is None:
        return  # Silent failure? Exception? Default?
    # Process order

# ✓ Validate and reject
def process_order(order):
    if order is None:
        raise ValueError("Order cannot be None")
    # Guaranteed non-null from here

# ✓✓ Use type system
def process_order(order: Order):  # Type system enforces non-null
    # order is guaranteed Order instance
```

## Assertions vs Exceptions

| Use | For | Example |
|-----|-----|---------|
| **Assertions** | Programming errors (bugs) | `assert age >= 0, "Age can't be negative"` |
| **Exceptions** | Runtime errors (external) | User input validation, file not found |

```python
# ✗ Exception for programming error
def set_age(age):
    if age < 0:
        raise ValueError("Age negative")  # Should be assertion

# ✓ Assertion for programming error
def set_age(age):
    assert age >= 0, "Age cannot be negative (bug!)"
    self.age = age

# ✓ Exception for runtime/user error
def process_user_input(age_string):
    try:
        age = int(age_string)
    except ValueError:
        raise ValueError("Invalid age format")
    if age < 0 or age > 150:
        raise ValueError("Age out of valid range")
```

### Assertion Guidelines
- [ ] Assert liberally during development
- [ ] Assert preconditions and postconditions
- [ ] Assert invariants
- [ ] **Never** put side effects in assertions
- [ ] **Never** use for user input validation
- [ ] **Never** rely on assertions in production (may be disabled)

## Barricades: Validate at Boundaries

**Pattern:** Validate once at entry, trust internally.

```python
# External API - BARRICADE
class UserAPI:
    def create_user(self, request_data):
        # Validate all external input at boundary
        validated = self._validate_and_sanitize(request_data)

        # Pass trusted data to internal logic
        return UserService.create_user_internal(validated)

    def _validate_and_sanitize(self, data):
        if not data.get("email") or "@" not in data["email"]:
            raise ValidationError("Invalid email")
        if len(data.get("password", "")) < 8:
            raise ValidationError("Password too short")

        return {
            "email": data["email"].strip().lower(),
            "password": data["password"],
            "name": data.get("name", "").strip()[:100]
        }

# Internal service - INSIDE BARRICADE
class UserService:
    @staticmethod
    def create_user_internal(validated_data):
        # Data already validated - no defensive checks needed
        user = User(
            email=validated_data["email"],
            password_hash=hash(validated_data["password"]),
            name=validated_data["name"]
        )
        database.save(user)
        return user
```

## Error Handling Checklist

### Design Phase
- [ ] Identified all error conditions (input, resources, business rules)
- [ ] Chose correctness vs robustness strategy
- [ ] Designed exception hierarchy for caller needs
- [ ] Identified barricade boundaries
- [ ] Determined critical vs non-critical paths

### Implementation Phase
- [ ] Used exceptions (not error codes in modern code)
- [ ] Provided rich context in exceptions
- [ ] Wrapped low-level exceptions at boundaries
- [ ] Validated inputs at barricades
- [ ] Used assertions for programming errors
- [ ] No side effects in error handling
- [ ] Resources cleaned up (try-finally, context managers)

### Error Messages
- [ ] Describe what went wrong
- [ ] Include relevant context (IDs, values, timestamps)
- [ ] Don't expose sensitive data
- [ ] Help users/developers fix the problem
- [ ] Preserve stack traces (exception chaining)

### Error Recovery
- [ ] Appropriate strategy (retry, fallback, fail)
- [ ] Transient errors retried with backoff
- [ ] Permanent errors fail fast
- [ ] Partial failures handled gracefully
- [ ] Resources released on error paths

### Don't Return/Pass Null
- [ ] Functions don't return null
- [ ] Functions don't accept null parameters
- [ ] Null object pattern used where appropriate
- [ ] Optional/Maybe types used where appropriate
- [ ] Collections return empty, never null

### Testing
- [ ] Happy path tested
- [ ] All exception paths tested
- [ ] Boundary conditions tested
- [ ] Recovery logic tested
- [ ] Error messages verified

### Logging & Monitoring
- [ ] Errors logged with context
- [ ] Correlation IDs tracked
- [ ] Metrics for error rates
- [ ] Alerts for critical errors
- [ ] Appropriate log levels (ERROR vs WARN vs INFO)

## Defensive Programming Spectrum

| Level | When | Approach |
|-------|------|----------|
| **Minimal** | Non-critical code | Basic validation, fail gracefully |
| **Standard** | Most code | Validate boundaries, assert assumptions |
| **Aggressive** | Critical code | Redundant checks, invariant verification |
| **Paranoid** | Life/financial | Pre/post conditions, double-check everything |

## Quick Decision Tree

```
Is this a programming error (bug)?
    ✓ Use assertion
    ✗ Continue

Is this external/user input?
    ✓ Validate at barricade, throw exception if invalid
    ✗ Continue

Can we continue safely with default/cached value?
    ✓ Return safe value (with logging)
    ✗ Continue

Is this error recoverable?
    ✓ Throw exception for caller to handle
    ✗ Continue

Would continuing cause more damage?
    ✓ Shut down/fail fast
    ✗ Throw exception
```

## Common Patterns

### Try-Catch-Finally
```python
def transfer_funds(from_acct, to_acct, amount):
    transaction = db.begin()
    try:
        from_acct.withdraw(amount)
        to_acct.deposit(amount)
        transaction.commit()
    except Exception as e:
        transaction.rollback()
        raise TransferError("Transfer failed") from e
    finally:
        transaction.close()
```

### Circuit Breaker
```python
class CircuitBreaker:
    def __init__(self, threshold=5):
        self.failures = 0
        self.threshold = threshold

    def call(self, operation):
        if self.failures >= self.threshold:
            raise SystemExit("Too many failures")

        try:
            result = operation()
            self.failures = 0  # Reset on success
            return result
        except Exception:
            self.failures += 1
            raise
```

### Exception Chaining
```python
# Preserve context with exception chaining
try:
    result = low_level_operation()
except LowLevelError as e:
    raise BusinessError(
        "Business operation failed",
        context={"user_id": user_id}
    ) from e  # Chain preserves stack trace
```

## References

- **Full Guide**: [01-foundations/ERROR_HANDLING.md](../01-foundations/ERROR_HANDLING.md)
- **Source**: Clean Code (Ch. 7), Code Complete 2 (Ch. 8)

---

**Remember**: Error handling is not separate from design - it IS design.
