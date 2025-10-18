# TDD Quick Reference

**Quick reference for Test-Driven Development workflow and best practices.**

Based on: Clean Code (Ch. 9), Code Complete 2 (Ch. 22)

## TDD Cycle: Red-Green-Refactor

```
1. RED    → Write a failing test
    ↓
2. GREEN  → Make it pass (simplest way)
    ↓
3. REFACTOR → Improve code while keeping tests green
    ↓
COMMIT and repeat
```

**Duration:** 5-10 minutes per cycle

## The Three Laws of TDD

1. **Don't write production code** until you have a failing test
2. **Don't write more test** than is sufficient to fail
3. **Don't write more production code** than is sufficient to pass

## TDD Workflow

### Step 1: RED - Write Failing Test

**Before writing code, write a test that:**
- [ ] Describes one specific behavior
- [ ] Fails for the right reason (not compile error)
- [ ] Has clear assertion
- [ ] Is focused and small

```python
# Step 1: RED - Write failing test
def test_calculate_discount_for_premium_customer():
    customer = Customer(type="premium")
    order = Order(total=100)

    discount = calculate_discount(customer, order)

    assert discount == 20  # 20% for premium
    # Test FAILS - function doesn't exist yet
```

### Step 2: GREEN - Make It Pass

**Write minimal code to pass the test:**
- [ ] Simplest implementation first
- [ ] Don't worry about elegance yet
- [ ] Hard-code if needed (refactor next)
- [ ] Make test pass quickly

```python
# Step 2: GREEN - Simplest code to pass
def calculate_discount(customer, order):
    return 20  # Hard-coded! But test passes
```

### Step 3: REFACTOR - Improve Code

**Improve without changing behavior:**
- [ ] Remove duplication
- [ ] Improve names
- [ ] Extract methods
- [ ] Simplify logic
- [ ] Tests stay green throughout

```python
# Step 3: REFACTOR - Proper implementation
def calculate_discount(customer, order):
    if customer.type == "premium":
        return order.total * 0.20
    return 0

# Add more tests, refactor more
def calculate_discount(customer, order):
    discount_rate = customer.get_discount_rate()
    return order.total * discount_rate
```

### Step 4: COMMIT

```bash
git add .
git commit -m "feat: add discount calculation for premium customers

- Implements 20% discount for premium customer type
- Tests verify discount calculation
- Coverage: 100% of calculate_discount function"
```

## Test Structure: Arrange-Act-Assert

```python
def test_user_login_with_valid_credentials():
    # ARRANGE: Set up test data
    user = User(username="john", password="secret123")
    auth_service = AuthenticationService()

    # ACT: Execute the behavior being tested
    result = auth_service.login(user.username, user.password)

    # ASSERT: Verify expected outcome
    assert result.is_authenticated == True
    assert result.user_id == user.id
```

**Alternative: Given-When-Then (BDD style)**
```python
def test_shopping_cart_total():
    # GIVEN a shopping cart with items
    cart = ShoppingCart()
    cart.add_item(Item("Widget", price=10), quantity=2)
    cart.add_item(Item("Gadget", price=15), quantity=1)

    # WHEN calculating the total
    total = cart.calculate_total()

    # THEN total should be sum of all items
    assert total == 35  # (10*2) + (15*1)
```

## FIRST Principles

| Principle | Meaning | Example |
|-----------|---------|---------|
| **Fast** | Tests run in milliseconds | Unit test: < 100ms |
| **Independent** | No dependencies between tests | Each test sets up own data |
| **Repeatable** | Same result every time | No random data, time dependencies |
| **Self-validating** | Boolean output (pass/fail) | Clear assertions, no manual checks |
| **Timely** | Written at right time | Before production code (TDD) |

### Fast
```python
# ✓ Fast - uses in-memory mock
def test_user_save():
    repo = InMemoryUserRepository()
    user = User(name="John")

    repo.save(user)

    assert repo.find_by_name("John") == user

# ✗ Slow - hits real database
def test_user_save():
    db = ProductionDatabase()  # Slow!
    user = User(name="John")
    db.save(user)
    assert db.query("SELECT * FROM users") == user
```

### Independent
```python
# ✓ Independent - each test isolated
def test_add_item():
    cart = ShoppingCart()  # Fresh cart
    cart.add_item(item)
    assert len(cart.items) == 1

def test_remove_item():
    cart = ShoppingCart()  # Fresh cart
    cart.add_item(item)
    cart.remove_item(item)
    assert len(cart.items) == 0

# ✗ Dependent - tests rely on order
shared_cart = ShoppingCart()

def test_add_item():
    shared_cart.add_item(item)
    assert len(shared_cart.items) == 1

def test_remove_item():  # Fails if run alone!
    shared_cart.remove_item(item)
    assert len(shared_cart.items) == 0
```

### Repeatable
```python
# ✓ Repeatable - deterministic
def test_calculate_age():
    birthdate = date(1990, 1, 1)
    reference_date = date(2020, 1, 1)

    age = calculate_age(birthdate, reference_date)

    assert age == 30  # Always 30

# ✗ Not repeatable - depends on current date
def test_calculate_age():
    birthdate = date(1990, 1, 1)

    age = calculate_age(birthdate)  # Uses datetime.now()

    assert age == 30  # Fails next year!
```

## Test Naming Conventions

### Pattern: test_method_scenario_expectedBehavior

```python
# Good test names
def test_login_with_valid_credentials_returns_success():
    pass

def test_login_with_invalid_password_raises_authentication_error():
    pass

def test_calculate_discount_for_premium_customer_returns_20_percent():
    pass

def test_add_item_to_empty_cart_increases_count_by_one():
    pass
```

### BDD Style: test_should_behavior_when_condition

```python
def test_should_authenticate_user_when_credentials_are_valid():
    pass

def test_should_raise_error_when_password_is_incorrect():
    pass

def test_should_apply_premium_discount_when_customer_is_premium():
    pass
```

## Test Coverage Standards

| Type | Coverage | Dependencies |
|------|----------|--------------|
| **Unit Tests** | 90%+ | Mocked dependencies |
| **Integration Tests** | 85%+ | Real dependencies |
| **Critical Paths** | 100% | User flows, money, security |

### What to Test

#### Always Test
- [ ] Business logic
- [ ] Edge cases
- [ ] Boundary conditions
- [ ] Error conditions
- [ ] Critical user flows

#### Sometimes Test
- [ ] Simple getters/setters (if logic involved)
- [ ] Configuration parsing
- [ ] Data transformations

#### Don't Test
- [ ] Framework code
- [ ] Third-party libraries
- [ ] Trivial getters/setters (no logic)
- [ ] Auto-generated code

## Common Test Patterns

### Test Doubles

| Type | Purpose | Example |
|------|---------|---------|
| **Stub** | Return canned response | Always return success |
| **Mock** | Verify interactions | Verify method called 3 times |
| **Fake** | Working implementation | In-memory database |
| **Spy** | Record interactions | Track method calls |

```python
# Stub - canned response
class StubUserRepository:
    def find_by_id(self, user_id):
        return User(id=user_id, name="Test User")

# Mock - verify interactions
def test_user_service_calls_repository():
    mock_repo = Mock()
    service = UserService(mock_repo)

    service.create_user("john@example.com")

    mock_repo.save.assert_called_once()

# Fake - working alternative
class FakeDatabase:
    def __init__(self):
        self.data = {}

    def save(self, key, value):
        self.data[key] = value

    def get(self, key):
        return self.data.get(key)
```

### Fixture Management

```python
# Setup/Teardown
class TestUserService:
    def setup_method(self):
        """Run before each test"""
        self.db = InMemoryDatabase()
        self.service = UserService(self.db)

    def teardown_method(self):
        """Run after each test"""
        self.db.clear()

    def test_create_user(self):
        self.service.create_user("john")
        assert self.db.count() == 1

# Pytest fixtures
@pytest.fixture
def user_service():
    db = InMemoryDatabase()
    service = UserService(db)
    yield service
    db.clear()

def test_create_user(user_service):
    user_service.create_user("john")
    assert user_service.count() == 1
```

## TDD Best Practices

### One Assertion Per Test (Guideline)
```python
# ✓ Focused test
def test_user_creation_sets_name():
    user = User(name="John")
    assert user.name == "John"

def test_user_creation_generates_id():
    user = User(name="John")
    assert user.id is not None

# ~ Acceptable - related assertions
def test_user_creation():
    user = User(name="John", email="john@example.com")
    assert user.name == "John"
    assert user.email == "john@example.com"

# ✗ Too many unrelated assertions
def test_user():
    user = User(name="John")
    assert user.name == "John"
    assert user.can_login() == True
    assert user.calculate_age() == 30
    # Testing multiple behaviors
```

### Test Behavior, Not Implementation
```python
# ✓ Tests behavior (survives refactoring)
def test_calculate_total_with_discount():
    order = Order()
    order.add_item(Item(price=100))

    total = order.calculate_total(discount=0.1)

    assert total == 90

# ✗ Tests implementation (breaks on refactoring)
def test_calculate_total_calls_apply_discount():
    order = Order()
    order.add_item(Item(price=100))

    with patch.object(order, '_apply_discount') as mock:
        order.calculate_total(discount=0.1)
        mock.assert_called_once()
    # Breaks if we refactor _apply_discount away
```

### Keep Tests Readable
```python
# ✓ Readable test
def test_order_total_includes_tax():
    # Given an order with $100 item in CA (10% tax)
    order = Order()
    order.add_item(Item(price=100))
    order.shipping_address = Address(state="CA")

    # When calculating total
    total = order.calculate_total_with_tax()

    # Then total should include 10% tax
    assert total == 110

# ✗ Hard to read
def test_order():
    o = Order()
    o.add_item(Item(price=100))
    o.shipping_address = Address(state="CA")
    assert o.calculate_total_with_tax() == 110  # Why 110?
```

## Common TDD Mistakes

| Mistake | Problem | Solution |
|---------|---------|----------|
| **Testing implementation** | Tests break on refactoring | Test behavior/outcomes |
| **Large tests** | Slow, hard to debug | Small, focused tests |
| **Dependent tests** | Fail in cascade | Make independent |
| **No assertions** | Test passes but doesn't verify | Always assert |
| **Testing framework** | Waste of time | Trust the framework |
| **Mocking everything** | Tests fragile | Mock only boundaries |
| **No refactor step** | Technical debt | Always refactor |

## TDD Anti-Patterns

### Anti-Pattern: Test After Code
```
✗ Write code → Write tests → Refactor
✓ Write test → Write code → Refactor
```

### Anti-Pattern: 100% Coverage Obsession
```
✗ Test every line (including getters)
✓ Test behavior and critical paths (90%+ coverage)
```

### Anti-Pattern: Testing Private Methods
```python
# ✗ Don't test private methods directly
def test_private_helper():
    obj = MyClass()
    result = obj._private_helper()  # Don't do this

# ✓ Test through public interface
def test_public_method():
    obj = MyClass()
    result = obj.public_method()  # This uses _private_helper
    assert result == expected
```

## TDD Workflow Checklist

### Starting New Feature
- [ ] Write first failing test
- [ ] Test fails for right reason
- [ ] Write minimal code to pass
- [ ] Test passes
- [ ] Refactor
- [ ] Commit

### Adding Test Case
- [ ] Identify new behavior/edge case
- [ ] Write failing test
- [ ] Extend code to handle it
- [ ] All tests pass
- [ ] Refactor if needed
- [ ] Commit

### Bug Fix
- [ ] Write test that reproduces bug
- [ ] Verify test fails
- [ ] Fix bug
- [ ] Test passes
- [ ] Verify no regression
- [ ] Commit

## TDD Metrics

### Test Quality Indicators
- **Test count:** Growing with features
- **Test speed:** All tests < 10 seconds
- **Test stability:** No flaky tests
- **Coverage:** 85-90%+
- **Defect detection:** Bugs found before production

### Red Flags
- [ ] Tests take > 10 minutes
- [ ] Tests fail randomly
- [ ] Coverage dropping
- [ ] Many tests skipped
- [ ] Tests modified to pass

## TDD Tools

### Test Runners
```bash
# Python
pytest -v                    # Verbose output
pytest -x                    # Stop on first failure
pytest --cov=src             # Coverage report
pytest -k test_user          # Run matching tests

# JavaScript
npm test                     # Run all tests
npm test -- --watch          # Watch mode
npm test -- --coverage       # Coverage
```

### Test Organization
```
project/
├── src/
│   └── calculator.py
└── tests/
    ├── unit/
    │   └── test_calculator.py
    └── integration/
        └── test_calculator_integration.py
```

## Quick Decision Tree

```
Starting new feature?
    ✓ Write failing test first (RED)

Test fails?
    ✓ Write minimal code (GREEN)
    ✗ Fix test (should fail for right reason)

Test passes?
    ✓ Refactor code
    ✗ Debug (why doesn't it pass?)

Code clean?
    ✓ Commit and move to next test
    ✗ Keep refactoring (tests stay green)

Feature complete?
    ✓ Done - all tests pass
    ✗ Write next failing test (RED)
```

## TDD Benefits

| Benefit | Explanation |
|---------|-------------|
| **Better design** | TDD forces testable, modular code |
| **Living documentation** | Tests document expected behavior |
| **Confidence** | Refactor without fear |
| **Fewer bugs** | Catch issues immediately |
| **Fast feedback** | Know within seconds if it works |
| **No regressions** | Tests prevent breaking old code |

## References

- **Full Guide**: [04-quality-through-testing/](../04-quality-through-testing/)
- **Source**: Clean Code (Ch. 9), Code Complete 2 (Ch. 22)

---

**Remember**: TDD is a design technique, not just testing. Let tests drive your design.
