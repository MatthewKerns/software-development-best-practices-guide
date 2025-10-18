# TDD Workflow: The Red-Green-Refactor Cycle

## Overview

Test-Driven Development (TDD) is a software development discipline where you write tests before writing the code that makes those tests pass. This inverts the traditional development flow and leads to better-designed, more thoroughly tested code.

This guide provides a practical, step-by-step workflow for practicing TDD effectively. You'll learn when to use TDD, how to execute the red-green-refactor cycle, and how to handle common challenges that arise during test-first development.

## Why TDD Matters

**"I'm not a great programmer; I'm just a good programmer with great habits."** — Kent Beck

TDD is not about testing—it's about design and discipline. The benefits extend far beyond test coverage:

**Design Pressure**: Writing tests first forces you to think about interfaces before implementations. Hard-to-test code is often poorly designed code.

**Minimal Code**: TDD naturally prevents over-engineering. You only write code that's needed to make a test pass.

**Living Documentation**: Tests written first document how the system should behave, with examples that stay synchronized with implementation.

**Fearless Refactoring**: Comprehensive test coverage from TDD enables aggressive refactoring without fear of breaking existing functionality.

**Debugging Time Reduction**: Bugs are caught immediately—within seconds of being introduced—when they're easiest to fix.

**Regression Prevention**: Once a bug is fixed with a test, it stays fixed. The test prevents future regressions.

## Source Materials

This guide synthesizes TDD practices from:

- **Clean Code** by Robert C. Martin (Chapter 9)
  - The Three Laws of TDD
  - Clean test principles
- **Test-Driven Development: By Example** by Kent Beck
  - Original TDD methodology
  - Practical TDD patterns
- **Code Complete 2** by Steve McConnell (Chapters 22-23)
  - Developer testing best practices
  - Test design strategies

## The TDD Cycle: Red-Green-Refactor

TDD follows a simple, repeatable three-phase cycle:

### The Three Phases

```
RED → GREEN → REFACTOR → RED → GREEN → REFACTOR → ...
 ↓      ↓        ↓
Write  Make it  Make it
test   pass     clean
```

**RED**: Write a failing test that defines desired behavior
- Write the smallest possible test
- Test should fail for the right reason
- Confirms test can detect the problem

**GREEN**: Write the minimal code to make the test pass
- Write the simplest code that works
- Don't optimize or beautify yet
- Get to green as quickly as possible

**REFACTOR**: Improve the code while keeping tests green
- Remove duplication
- Improve names and structure
- Optimize if needed
- Tests must stay green throughout

### Cycle Timing

Each cycle should be **short** (minutes, not hours):
- Red phase: < 1 minute (write one small test)
- Green phase: < 1 minute (minimal implementation)
- Refactor phase: < 2 minutes (quick cleanup)

**Total cycle time: 2-4 minutes**

If a cycle takes longer, the test is too large—break it into smaller steps.

## Detailed Workflow

### Phase 1: RED - Write a Failing Test

**Goal**: Write the smallest test that fails for the right reason.

#### Step 1.1: Identify Next Small Behavior

Think about the smallest piece of functionality you can test:

```python
# Python - Starting with the simplest possible behavior
# Goal: Implement a function to calculate string length

# Q: What's the simplest case?
# A: Empty string should have length 0

def test_empty_string_has_zero_length():
    result = string_length("")  # Function doesn't exist yet!
    assert result == 0
```

#### Step 1.2: Write Test That Fails

Run the test and verify it fails for the expected reason:

```bash
$ pytest test_string_length.py
ERROR: NameError: name 'string_length' is not defined
```

**Good failure**: Function doesn't exist yet.

```typescript
// TypeScript - Starting with Jest
describe('StringLength', () => {
  it('returns 0 for empty string', () => {
    const result = stringLength('');  // Function doesn't exist
    expect(result).toBe(0);
  });
});
```

```bash
$ npm test
FAIL: ReferenceError: stringLength is not defined
```

#### Step 1.3: Verify Test Can Fail

This step confirms your test can actually detect problems:

```python
# Python - Implement wrong version to confirm test fails
def string_length(s):
    return 99  # Obviously wrong

# Run test
$ pytest test_string_length.py
FAILED: assert 99 == 0
```

**Key Insight**: If a test can't fail, it doesn't test anything. Always see it fail first.

### Phase 2: GREEN - Make It Pass

**Goal**: Write the simplest code that makes the test pass.

#### Step 2.1: Write Minimal Implementation

**The Simplest Thing That Could Possibly Work:**

```python
# Python - Absolutely minimal implementation
def string_length(s):
    return 0  # Hardcoded! But it makes the test pass.

$ pytest test_string_length.py
PASSED
```

**Why hardcode?** It forces you to write more tests that will require a real implementation.

#### Step 2.2: Write Next Test

Now the hardcoded solution is insufficient:

```python
# Python - Second test forces real implementation
def test_single_character_has_length_one():
    result = string_length("a")
    assert result == 1

$ pytest test_string_length.py
FAILED: assert 0 == 1  # Our hardcoded 0 fails!
```

#### Step 2.3: Implement Real Solution

Now we need actual logic:

```python
# Python - Real implementation emerges
def string_length(s):
    if s == "":
        return 0
    return len(s)

$ pytest test_string_length.py
PASSED (2 tests)
```

#### Step 2.4: Write More Tests

Continue adding tests until behavior is complete:

```python
# Python - Complete test suite
def test_empty_string_has_zero_length():
    assert string_length("") == 0

def test_single_character_has_length_one():
    assert string_length("a") == 1

def test_multiple_characters_returns_correct_length():
    assert string_length("hello") == 5
    assert string_length("world") == 5

def test_special_characters_counted():
    assert string_length("hello!@#") == 8

def test_unicode_characters():
    assert string_length("hello世界") == 7

# All tests pass
$ pytest test_string_length.py
PASSED (5 tests)
```

**Key Insight**: Write just enough code to make the current test pass, then write the next test.

### Phase 3: REFACTOR - Make It Clean

**Goal**: Improve code quality while keeping all tests green.

#### Step 3.1: Remove Duplication

```java
// Java - Before refactoring (duplication)
public class Calculator {
    public int add(int a, int b) {
        if (a < 0 || b < 0) {
            throw new IllegalArgumentException("Negative numbers not allowed");
        }
        return a + b;
    }

    public int subtract(int a, int b) {
        if (a < 0 || b < 0) {
            throw new IllegalArgumentException("Negative numbers not allowed");
        }
        return a - b;
    }
}

// Java - After refactoring (DRY)
public class Calculator {
    private void validateNonNegative(int... numbers) {
        for (int n : numbers) {
            if (n < 0) {
                throw new IllegalArgumentException("Negative numbers not allowed");
            }
        }
    }

    public int add(int a, int b) {
        validateNonNegative(a, b);
        return a + b;
    }

    public int subtract(int a, int b) {
        validateNonNegative(a, b);
        return a - b;
    }
}

// Tests still pass after refactoring
$ mvn test
[INFO] Tests run: 6, Failures: 0
```

#### Step 3.2: Improve Names

```typescript
// TypeScript - Before: Unclear names
function calc(a: number, b: number): number {
  return a + b + (a * b * 0.1);
}

// After: Intention-revealing names
function calculateTotalWithSurcharge(
  baseAmount: number,
  additionalAmount: number
): number {
  const total = baseAmount + additionalAmount;
  const surcharge = total * 0.1;
  return total + surcharge;
}

// Tests remain green
```

#### Step 3.3: Extract Methods

```python
# Python - Before: Long method
def process_order(items, customer):
    total = 0
    for item in items:
        total += item.price * item.quantity

    if customer.is_premium:
        discount = total * 0.1
    else:
        discount = 0

    tax = (total - discount) * 0.08

    return {
        'subtotal': total,
        'discount': discount,
        'tax': tax,
        'total': total - discount + tax
    }

# Python - After: Extracted methods (more readable)
def process_order(items, customer):
    subtotal = calculate_subtotal(items)
    discount = calculate_discount(subtotal, customer)
    tax = calculate_tax(subtotal - discount)

    return {
        'subtotal': subtotal,
        'discount': discount,
        'tax': tax,
        'total': subtotal - discount + tax
    }

def calculate_subtotal(items):
    return sum(item.price * item.quantity for item in items)

def calculate_discount(subtotal, customer):
    if customer.is_premium:
        return subtotal * 0.1
    return 0

def calculate_tax(taxable_amount):
    return taxable_amount * 0.08

# All tests still pass after refactoring
```

#### Step 3.4: Run Tests Continuously

**Critical**: Run tests after every small refactoring:

```bash
# After each change, verify tests still pass
$ pytest
PASSED (12 tests)

# Make another refactoring
$ pytest
PASSED (12 tests)

# Continue until code is clean
```

**If tests fail during refactoring**: Undo immediately and try a smaller change.

**Key Insight**: Refactoring is safe only when tests stay green. Never refactor without tests.

## Complete TDD Example: FizzBuzz

Let's work through a complete example from scratch.

### Requirement

Write a function `fizzBuzz(n)` that:
- Returns "Fizz" for multiples of 3
- Returns "Buzz" for multiples of 5
- Returns "FizzBuzz" for multiples of both 3 and 5
- Returns the number as a string otherwise

### Cycle 1: Return the Number

```typescript
// TypeScript - Test 1: Simplest case
describe('fizzBuzz', () => {
  it('returns the number as string for 1', () => {
    expect(fizzBuzz(1)).toBe('1');
  });
});

// RED: Test fails (function doesn't exist)
// ReferenceError: fizzBuzz is not defined

// GREEN: Minimal implementation
function fizzBuzz(n: number): string {
  return '1';  // Hardcoded!
}

// REFACTOR: Nothing to refactor yet
```

### Cycle 2: Handle Different Numbers

```typescript
// Test 2: Another non-special number
it('returns the number as string for 2', () => {
  expect(fizzBuzz(2)).toBe('2');
});

// RED: Test fails
// Expected: '2', Received: '1'

// GREEN: Real implementation emerges
function fizzBuzz(n: number): string {
  return n.toString();
}

// REFACTOR: Clean and simple already
```

### Cycle 3: Multiples of 3

```typescript
// Test 3: Multiple of 3
it('returns Fizz for 3', () => {
  expect(fizzBuzz(3)).toBe('Fizz');
});

// RED: Test fails
// Expected: 'Fizz', Received: '3'

// GREEN: Add conditional
function fizzBuzz(n: number): string {
  if (n === 3) return 'Fizz';
  return n.toString();
}

// Test 4: Force generalization
it('returns Fizz for 6', () => {
  expect(fizzBuzz(6)).toBe('Fizz');
});

// RED: Fails for 6

// GREEN: Generalize
function fizzBuzz(n: number): string {
  if (n % 3 === 0) return 'Fizz';
  return n.toString();
}

// REFACTOR: Looks good
```

### Cycle 4: Multiples of 5

```typescript
// Test 5: Multiple of 5
it('returns Buzz for 5', () => {
  expect(fizzBuzz(5)).toBe('Buzz');
});

// RED: Fails

// GREEN: Add condition
function fizzBuzz(n: number): string {
  if (n % 3 === 0) return 'Fizz';
  if (n % 5 === 0) return 'Buzz';
  return n.toString();
}

// REFACTOR: Looks good
```

### Cycle 5: Multiples of Both

```typescript
// Test 6: Multiple of both 3 and 5
it('returns FizzBuzz for 15', () => {
  expect(fizzBuzz(15)).toBe('FizzBuzz');
});

// RED: Fails - returns 'Fizz' instead of 'FizzBuzz'

// GREEN: Fix order (check 15 first)
function fizzBuzz(n: number): string {
  if (n % 15 === 0) return 'FizzBuzz';  // Must be first!
  if (n % 3 === 0) return 'Fizz';
  if (n % 5 === 0) return 'Buzz';
  return n.toString();
}

// REFACTOR: Can we improve this?
function fizzBuzz(n: number): string {
  let result = '';
  if (n % 3 === 0) result += 'Fizz';
  if (n % 5 === 0) result += 'Buzz';
  return result || n.toString();
}

// All tests still pass after refactoring!
```

### Final Test Suite

```typescript
// Complete test suite
describe('fizzBuzz', () => {
  it('returns the number as string for 1', () => {
    expect(fizzBuzz(1)).toBe('1');
  });

  it('returns the number as string for 2', () => {
    expect(fizzBuzz(2)).toBe('2');
  });

  it('returns Fizz for 3', () => {
    expect(fizzBuzz(3)).toBe('Fizz');
  });

  it('returns Fizz for 6', () => {
    expect(fizzBuzz(6)).toBe('Fizz');
  });

  it('returns Buzz for 5', () => {
    expect(fizzBuzz(5)).toBe('Buzz');
  });

  it('returns Buzz for 10', () => {
    expect(fizzBuzz(10)).toBe('Buzz');
  });

  it('returns FizzBuzz for 15', () => {
    expect(fizzBuzz(15)).toBe('FizzBuzz');
  });

  it('returns FizzBuzz for 30', () => {
    expect(fizzBuzz(30)).toBe('FizzBuzz');
  });
});

// All 8 tests pass
```

## TDD for Real-World Scenarios

### Scenario 1: Building a Shopping Cart

```python
# Python - TDD for shopping cart feature

# Test 1: Empty cart has zero items
def test_empty_cart_has_zero_items():
    cart = ShoppingCart()
    assert cart.item_count() == 0

# GREEN: Minimal implementation
class ShoppingCart:
    def item_count(self):
        return 0

# Test 2: Adding item increases count
def test_add_item_increases_count():
    cart = ShoppingCart()
    cart.add_item(Item("Widget", 10.0))
    assert cart.item_count() == 1

# GREEN: Add storage
class ShoppingCart:
    def __init__(self):
        self.items = []

    def add_item(self, item):
        self.items.append(item)

    def item_count(self):
        return len(self.items)

# Test 3: Empty cart has zero total
def test_empty_cart_has_zero_total():
    cart = ShoppingCart()
    assert cart.get_total() == 0

# GREEN: Add method
class ShoppingCart:
    def __init__(self):
        self.items = []

    def add_item(self, item):
        self.items.append(item)

    def item_count(self):
        return len(self.items)

    def get_total(self):
        return sum(item.price for item in self.items)

# Test 4: Total calculates correctly
def test_cart_calculates_correct_total():
    cart = ShoppingCart()
    cart.add_item(Item("Widget", 10.0))
    cart.add_item(Item("Gadget", 20.0))
    assert cart.get_total() == 30.0

# Tests pass without changes - implementation already handles it!

# REFACTOR: Make names clearer
class ShoppingCart:
    def __init__(self):
        self._items = []

    def add_item(self, item):
        self._items.append(item)

    def item_count(self):
        return len(self._items)

    def calculate_total(self):  # Renamed for clarity
        return sum(item.price for item in self._items)
```

### Scenario 2: Email Validation

```java
// Java - TDD for email validation

// Test 1: Null email is invalid
@Test
public void testNullEmail_IsInvalid() {
    EmailValidator validator = new EmailValidator();
    assertFalse(validator.isValid(null));
}

// GREEN
public class EmailValidator {
    public boolean isValid(String email) {
        return false;  // null is invalid
    }
}

// Test 2: Empty string is invalid
@Test
public void testEmptyEmail_IsInvalid() {
    EmailValidator validator = new EmailValidator();
    assertFalse(validator.isValid(""));
}

// GREEN
public boolean isValid(String email) {
    if (email == null || email.isEmpty()) {
        return false;
    }
    return true;  // Temporary
}

// Test 3: Email without @ is invalid
@Test
public void testEmailWithoutAt_IsInvalid() {
    EmailValidator validator = new EmailValidator();
    assertFalse(validator.isValid("testexample.com"));
}

// GREEN
public boolean isValid(String email) {
    if (email == null || email.isEmpty()) {
        return false;
    }
    if (!email.contains("@")) {
        return false;
    }
    return true;
}

// Test 4: Valid email format
@Test
public void testValidEmail_IsValid() {
    EmailValidator validator = new EmailValidator();
    assertTrue(validator.isValid("test@example.com"));
}

// Tests pass! Continue with more edge cases...

// Test 5: Email with multiple @ is invalid
@Test
public void testMultipleAt_IsInvalid() {
    EmailValidator validator = new EmailValidator();
    assertFalse(validator.isValid("test@@example.com"));
}

// GREEN - Add validation
public boolean isValid(String email) {
    if (email == null || email.isEmpty()) return false;
    if (!email.contains("@")) return false;

    String[] parts = email.split("@");
    if (parts.length != 2) return false;

    return !parts[0].isEmpty() && !parts[1].isEmpty();
}

// REFACTOR - Extract methods
public boolean isValid(String email) {
    if (isNullOrEmpty(email)) return false;
    if (!hasValidAtSymbol(email)) return false;
    return hasValidParts(email);
}

private boolean isNullOrEmpty(String email) {
    return email == null || email.isEmpty();
}

private boolean hasValidAtSymbol(String email) {
    return email.contains("@") &&
           email.split("@").length == 2;
}

private boolean hasValidParts(String email) {
    String[] parts = email.split("@");
    return !parts[0].isEmpty() && !parts[1].isEmpty();
}
```

## TDD Strategies and Patterns

### Strategy 1: Fake It Till You Make It

Start with hardcoded values, then generalize:

```python
# Python - Fake it strategy

# Test 1
def test_sum_of_two_numbers():
    assert add(2, 3) == 5

# Fake it
def add(a, b):
    return 5  # Hardcoded!

# Test 2 forces generalization
def test_sum_of_different_numbers():
    assert add(4, 6) == 10

# Now implement for real
def add(a, b):
    return a + b
```

### Strategy 2: Triangulation

Write multiple examples to drive toward the general solution:

```typescript
// TypeScript - Triangulation

// Test 1
it('calculates average of two numbers', () => {
  expect(average([5, 10])).toBe(7.5);
});

// Test 2
it('calculates average of three numbers', () => {
  expect(average([5, 10, 15])).toBe(10);
});

// Test 3
it('calculates average of one number', () => {
  expect(average([5])).toBe(5);
});

// General solution emerges from triangulation
function average(numbers: number[]): number {
  const sum = numbers.reduce((acc, n) => acc + n, 0);
  return sum / numbers.length;
}
```

### Strategy 3: Obvious Implementation

If the solution is obvious and simple, just write it:

```java
// Java - Obvious implementation

@Test
public void testGetFullName_CombinesFirstAndLast() {
    Person person = new Person("John", "Doe");
    assertEquals("John Doe", person.getFullName());
}

// Obvious implementation - no need to fake it
public class Person {
    private String firstName;
    private String lastName;

    public Person(String firstName, String lastName) {
        this.firstName = firstName;
        this.lastName = lastName;
    }

    public String getFullName() {
        return firstName + " " + lastName;
    }
}
```

**When to use**: When the implementation is truly obvious and unlikely to change.

### Strategy 4: Test List

Maintain a list of tests to write:

```
Shopping Cart Test List:
✓ Empty cart has zero items
✓ Adding item increases count
✓ Empty cart has zero total
✓ Total calculates correctly
□ Removing item decreases count
□ Removing item updates total
□ Clearing cart removes all items
□ Cannot add null items
□ Quantity can be updated
□ Duplicate items are combined
```

Work through the list systematically, checking off tests as you complete them.

## Handling Complex Scenarios

### Testing Error Conditions

```python
# Python - TDD for error handling

# Test 1: Negative age raises error
def test_create_user_with_negative_age_raises_error():
    with pytest.raises(ValueError, match="Age cannot be negative"):
        create_user(name="John", age=-5)

# GREEN
def create_user(name, age):
    if age < 0:
        raise ValueError("Age cannot be negative")
    return User(name, age)

# Test 2: Age over 150 raises error
def test_create_user_with_unrealistic_age_raises_error():
    with pytest.raises(ValueError, match="Age must be realistic"):
        create_user(name="John", age=200)

# GREEN
def create_user(name, age):
    if age < 0:
        raise ValueError("Age cannot be negative")
    if age > 150:
        raise ValueError("Age must be realistic")
    return User(name, age)
```

### Testing with External Dependencies

```typescript
// TypeScript - TDD with mocked dependencies

// Test 1: Successful user creation sends welcome email
it('sends welcome email after user registration', async () => {
  const mockEmailService = {
    sendEmail: jest.fn().mockResolvedValue({ success: true })
  };

  const registrationService = new RegistrationService(mockEmailService);
  await registrationService.register('user@example.com', 'password');

  expect(mockEmailService.sendEmail).toHaveBeenCalledWith(
    'user@example.com',
    'Welcome!',
    expect.any(String)
  );
});

// GREEN - Implement
class RegistrationService {
  constructor(private emailService: EmailService) {}

  async register(email: string, password: string): Promise<User> {
    const user = await this.createUser(email, password);
    await this.emailService.sendEmail(
      email,
      'Welcome!',
      'Thanks for joining!'
    );
    return user;
  }

  private async createUser(email: string, password: string): Promise<User> {
    return new User(email, password);
  }
}
```

### Testing Asynchronous Code

```python
# Python - TDD for async code

# Test 1: Async function completes
@pytest.mark.asyncio
async def test_fetch_user_data_returns_user():
    service = UserService()
    user = await service.fetch_user_data(user_id=123)
    assert user.id == 123

# GREEN
class UserService:
    async def fetch_user_data(self, user_id):
        # Simulate async operation
        await asyncio.sleep(0)
        return User(id=user_id)

# Test 2: Handles errors gracefully
@pytest.mark.asyncio
async def test_fetch_user_data_handles_not_found():
    service = UserService()
    with pytest.raises(UserNotFoundError):
        await service.fetch_user_data(user_id=999)

# GREEN
class UserService:
    async def fetch_user_data(self, user_id):
        if user_id == 999:
            raise UserNotFoundError(f"User {user_id} not found")
        await asyncio.sleep(0)
        return User(id=user_id)
```

## Common TDD Challenges

### Challenge 1: Tests Are Too Large

**Problem**: Writing tests that try to verify too much at once.

**Solution**: Break into smaller, focused tests.

```java
// BAD: Too large
@Test
public void testCompleteUserWorkflow() {
    User user = createUser();
    user.activate();
    user.updateProfile("New Name");
    user.changePassword("newpass");
    user.deactivate();
    // Too much in one test!
}

// GOOD: Separate focused tests
@Test
public void testCreateUser() {
    User user = createUser();
    assertNotNull(user.getId());
}

@Test
public void testActivateUser() {
    User user = createInactiveUser();
    user.activate();
    assertTrue(user.isActive());
}
```

### Challenge 2: Getting Stuck on Green

**Problem**: Can't figure out how to make the test pass.

**Solution**: Write an even smaller test or use a fake-it implementation.

```python
# Stuck on this test?
def test_complex_calculation():
    result = calculate_interest(principal=1000, rate=0.05, years=10)
    assert result == 1628.89

# Break it down
def test_zero_years_returns_principal():
    result = calculate_interest(principal=1000, rate=0.05, years=0)
    assert result == 1000

def test_one_year_simple():
    result = calculate_interest(principal=1000, rate=0.05, years=1)
    assert result == 1050

# Build up gradually
```

### Challenge 3: Refactoring Breaks Tests

**Problem**: Tests fail when you refactor, even though behavior is correct.

**Solution**: Tests are coupled to implementation. Test behavior, not implementation.

```typescript
// BAD: Tests implementation
it('calls repository save method', () => {
  const spy = jest.spyOn(repository, 'save');
  service.createUser('test@example.com');
  expect(spy).toHaveBeenCalled();  // Breaks on refactoring!
});

// GOOD: Tests behavior
it('created user is retrievable', () => {
  const created = service.createUser('test@example.com');
  const retrieved = service.getUser(created.id);
  expect(retrieved.email).toBe('test@example.com');
});
```

### Challenge 4: Slow Tests

**Problem**: Test suite takes too long to run.

**Solution**: Use faster test doubles, avoid I/O, run tests in parallel.

```python
# SLOW: Real database
def test_user_creation():
    db = DatabaseConnection()
    user = create_user_in_db(db, "test@example.com")
    assert db.find_user(user.id).email == "test@example.com"

# FAST: In-memory fake
def test_user_creation():
    repo = InMemoryUserRepository()
    user = create_user(repo, "test@example.com")
    assert repo.find(user.id).email == "test@example.com"
```

## TDD Anti-Patterns to Avoid

### Anti-Pattern 1: Writing Tests After Code

**Problem**: Defeats the design benefits of TDD.

**Solution**: Commit to test-first discipline.

### Anti-Pattern 2: Testing Implementation Details

**Problem**: Tests break on every refactoring.

**Solution**: Test public interfaces and observable behavior.

### Anti-Pattern 3: Skipping Refactor Phase

**Problem**: Code becomes messy and hard to maintain.

**Solution**: Always refactor. It's one-third of the cycle.

### Anti-Pattern 4: Making Large Jumps

**Problem**: Trying to implement too much at once.

**Solution**: Take smaller steps. Write simpler tests.

### Anti-Pattern 5: Not Running Tests Frequently

**Problem**: Long feedback loops defeat TDD's purpose.

**Solution**: Run tests after every tiny change.

## Integration with Geist Framework

### Ghost: Unknown Test Cases

**Question**: What test cases am I not seeing?

```python
# Visible tests
def test_divide():
    assert divide(10, 2) == 5

# Ghost analysis reveals edge cases
def test_divide_by_zero():
    with pytest.raises(ZeroDivisionError):
        divide(10, 0)

def test_divide_negative_numbers():
    assert divide(-10, 2) == -5

def test_divide_floats():
    assert divide(10, 3) == pytest.approx(3.333)
```

### Geyser: Testing for Future Change

**Question**: Will my tests survive refactoring?

Test interfaces, not implementations, so tests withstand change.

### Gist: Essential Testing

**Question**: Am I testing the essence or accidental complexity?

Focus tests on business rules and essential behavior, not framework code or implementation details.

## Practical TDD Checklist

### Starting TDD
- [ ] Identify the smallest testable behavior
- [ ] Write a test that fails
- [ ] Verify the test fails for the right reason
- [ ] Write minimal code to pass
- [ ] Verify the test passes
- [ ] Refactor if needed
- [ ] Repeat

### During Red Phase
- [ ] Test is small and focused (one concept)
- [ ] Test has clear, descriptive name
- [ ] Test uses AAA or Given-When-Then structure
- [ ] Test fails for expected reason

### During Green Phase
- [ ] Code is minimal (just enough to pass)
- [ ] All tests pass
- [ ] No optimization yet (that's for refactor phase)

### During Refactor Phase
- [ ] Remove duplication
- [ ] Improve names and structure
- [ ] Extract methods when appropriate
- [ ] Run tests after each small change
- [ ] All tests remain green

## Further Reading

### Related Guides in This Repository
- **UNIT_TESTING_PRINCIPLES.md** - Clean Code testing principles
- **DEVELOPER_TESTING.md** - Comprehensive testing strategies
- **TEST_DESIGN_PATTERNS.md** - Advanced testing patterns
- **01-foundations/FUNCTIONS_AND_ROUTINES.md** - Writing testable functions

### External Resources
- **Test-Driven Development: By Example** by Kent Beck - Original TDD book
- **Clean Code** (Chapter 9) - TDD and clean tests
- **Growing Object-Oriented Software, Guided by Tests** - Advanced TDD practices
- **Working Effectively with Legacy Code** by Michael Feathers - TDD in existing codebases

## Summary

TDD is a discipline that produces better-designed, more thoroughly tested code. Key practices:

1. **Follow Red-Green-Refactor** religiously
2. **Write tests first** for design benefits
3. **Take small steps** (minutes, not hours)
4. **Fake it, then make it** to drive toward general solutions
5. **Refactor mercilessly** while tests stay green
6. **Run tests constantly** for rapid feedback
7. **Test behavior, not implementation** for refactoring safety

TDD results in:
- Better software design
- Comprehensive test coverage
- Living documentation
- Fearless refactoring
- Faster debugging
- Fewer defects

**Remember**: TDD is not about testing—it's about design and discipline. The tests are a beneficial side effect of a better development process.

**The TDD Mantra**: Red → Green → Refactor → Repeat
