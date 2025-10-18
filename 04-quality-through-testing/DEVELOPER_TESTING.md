# Developer Testing: Building Quality Into Code

## Overview

Developer testing is the practice of software developers testing their own code before it reaches formal quality assurance or production. Unlike traditional testing where a separate QA team validates completed features, developer testing integrates quality verification directly into the construction process.

This comprehensive guide provides practical, actionable techniques for developers to test their code effectively, catch defects early, and design more testable systems. Developer testing is not just about finding bugs—it's about preventing them from being written in the first place.

## Why Developer Testing Matters

**"Testing can show the presence of bugs, but never their absence."** — Edsger Dijkstra

The cost of fixing a defect grows exponentially with time:
- **During coding**: 1x cost (immediate fix)
- **During unit testing**: 2-5x cost (context switch)
- **During integration**: 10x cost (impacts multiple components)
- **During system testing**: 20x cost (broader impact analysis)
- **After release**: 100x cost (customer impact, reputation, emergency fixes)

### The Benefits of Developer Testing

**Early Defect Detection**: Catch bugs when they're easiest and cheapest to fix—while the code is still fresh in your mind.

**Better Design**: Writing tests forces you to think about interfaces, dependencies, and edge cases. Untestable code is often poorly designed code.

**Living Documentation**: Tests document how code should behave, providing examples that stay synchronized with the implementation.

**Confident Refactoring**: Comprehensive tests enable aggressive refactoring and performance optimization without fear of breaking existing functionality.

**Reduced Debugging Time**: Well-tested code fails less frequently, and when it does fail, tests isolate the problem quickly.

## Source Materials

This guide synthesizes principles from:

- **Code Complete 2** by Steve McConnell (Chapters 22-23)
  - Developer testing vs. other testing
  - Incomplete testing (coverage is insufficient)
  - Structured basis testing
  - Data-flow testing
  - Boundary analysis
  - Testing for errors
  - Test support tools

## Core Testing Principles

### 1. Test Your Own Code

**Principle**: Developers are responsible for testing their own work before declaring it complete.

**Why This Matters**:
- You understand the code's intent better than anyone else
- You can test as you build, not after
- You can design for testability from the start
- You reduce the burden on QA teams (they focus on integration and system testing)

**Poor Practice:**
```python
# Python - Write code and immediately commit
def calculate_discount(price, customer_type):
    if customer_type == "premium":
        return price * 0.8
    return price * 0.9
# Commit without testing
```

**Good Practice:**
```python
# Python - Write code with immediate verification
def calculate_discount(price: float, customer_type: str) -> float:
    """Calculate discount based on customer type.

    Args:
        price: Original price (must be non-negative)
        customer_type: Either 'premium' or 'standard'

    Returns:
        Discounted price

    Raises:
        ValueError: If price is negative or customer_type invalid
    """
    if price < 0:
        raise ValueError(f"Price cannot be negative: {price}")

    if customer_type == "premium":
        return price * 0.8
    elif customer_type == "standard":
        return price * 0.9
    else:
        raise ValueError(f"Unknown customer type: {customer_type}")

# Immediate test verification
def test_calculate_discount():
    # Normal cases
    assert calculate_discount(100, "premium") == 80
    assert calculate_discount(100, "standard") == 90

    # Edge cases
    assert calculate_discount(0, "premium") == 0

    # Error cases
    import pytest
    with pytest.raises(ValueError):
        calculate_discount(-100, "premium")
    with pytest.raises(ValueError):
        calculate_discount(100, "unknown")

# Run test before committing
test_calculate_discount()
```

```typescript
// TypeScript - Test while building
function calculateDiscount(price: number, customerType: string): number {
  if (price < 0) {
    throw new Error(`Price cannot be negative: ${price}`);
  }

  if (customerType === "premium") {
    return price * 0.8;
  } else if (customerType === "standard") {
    return price * 0.9;
  } else {
    throw new Error(`Unknown customer type: ${customerType}`);
  }
}

// Jest tests written immediately
describe('calculateDiscount', () => {
  it('applies 20% discount for premium customers', () => {
    expect(calculateDiscount(100, "premium")).toBe(80);
  });

  it('applies 10% discount for standard customers', () => {
    expect(calculateDiscount(100, "standard")).toBe(90);
  });

  it('handles zero price', () => {
    expect(calculateDiscount(0, "premium")).toBe(0);
  });

  it('throws error for negative price', () => {
    expect(() => calculateDiscount(-100, "premium")).toThrow();
  });

  it('throws error for unknown customer type', () => {
    expect(() => calculateDiscount(100, "unknown")).toThrow();
  });
});
```

### 2. Incomplete Testing: Coverage Is Not Enough

**Principle**: 100% code coverage does not mean 100% tested. You must test logic paths, not just lines of code.

**The Problem with Line Coverage**:

```java
// Java - 100% line coverage, inadequate testing
public class UserValidator {
    public boolean isValid(User user) {
        return user != null && user.getEmail() != null &&
               user.getEmail().contains("@");
    }
}

// Test that achieves 100% line coverage
@Test
public void testIsValid() {
    User user = new User("test@example.com");
    assertTrue(validator.isValid(user));  // All lines executed!
}
```

**The Problem**: This test doesn't check:
- What happens when user is null?
- What happens when email is null?
- What happens when email doesn't contain "@"?
- What about multiple "@" symbols?
- What about empty strings?

**Proper Testing**:

```java
// Java - Comprehensive test cases
@Test
public void testIsValid_NullUser_ReturnsFalse() {
    assertFalse(validator.isValid(null));
}

@Test
public void testIsValid_NullEmail_ReturnsFalse() {
    User user = new User(null);
    assertFalse(validator.isValid(user));
}

@Test
public void testIsValid_EmptyEmail_ReturnsFalse() {
    User user = new User("");
    assertFalse(validator.isValid(user));
}

@Test
public void testIsValid_EmailWithoutAt_ReturnsFalse() {
    User user = new User("testexample.com");
    assertFalse(validator.isValid(user));
}

@Test
public void testIsValid_ValidEmail_ReturnsTrue() {
    User user = new User("test@example.com");
    assertTrue(validator.isValid(user));
}

@Test
public void testIsValid_MultipleAtSymbols_ReturnsTrue() {
    // Current implementation allows this - is that correct?
    User user = new User("test@@example.com");
    assertTrue(validator.isValid(user));  // Documents current behavior
}
```

**Key Insight**: Test logic branches, edge cases, and error conditions—not just happy paths.

### 3. Structured Basis Testing

**Principle**: Test every independent path through the code at least once.

**Cyclomatic Complexity**: The number of independent paths through a function.
- Formula: `E - N + 2P` where E = edges, N = nodes, P = connected components
- Practical: Count decision points (if, while, for, case) + 1

**Example:**

```python
# Python - Function with cyclomatic complexity of 4
def process_payment(amount, payment_method, has_insurance):
    if amount <= 0:  # Decision 1
        raise ValueError("Amount must be positive")

    if payment_method == "credit":  # Decision 2
        fee = amount * 0.03
    else:
        fee = 0

    if has_insurance:  # Decision 3
        discount = amount * 0.05
    else:
        discount = 0

    return amount + fee - discount

# Minimum 4 test cases needed for full path coverage
def test_process_payment_paths():
    # Path 1: Invalid amount
    with pytest.raises(ValueError):
        process_payment(-100, "credit", True)

    # Path 2: Credit + insurance
    assert process_payment(100, "credit", True) == 98  # 100 + 3 - 5

    # Path 3: Credit + no insurance
    assert process_payment(100, "credit", False) == 103  # 100 + 3 - 0

    # Path 4: Non-credit + insurance
    assert process_payment(100, "cash", True) == 95  # 100 + 0 - 5

    # Path 5: Non-credit + no insurance
    assert process_payment(100, "cash", False) == 100  # 100 + 0 - 0
```

```typescript
// TypeScript - Full path coverage
function processPayment(
  amount: number,
  paymentMethod: string,
  hasInsurance: boolean
): number {
  if (amount <= 0) {
    throw new Error("Amount must be positive");
  }

  const fee = paymentMethod === "credit" ? amount * 0.03 : 0;
  const discount = hasInsurance ? amount * 0.05 : 0;

  return amount + fee - discount;
}

describe('processPayment - all paths', () => {
  it('throws error for negative amount', () => {
    expect(() => processPayment(-100, "credit", true)).toThrow();
  });

  it('calculates credit payment with insurance', () => {
    expect(processPayment(100, "credit", true)).toBe(98);
  });

  it('calculates credit payment without insurance', () => {
    expect(processPayment(100, "credit", false)).toBe(103);
  });

  it('calculates cash payment with insurance', () => {
    expect(processPayment(100, "cash", true)).toBe(95);
  });

  it('calculates cash payment without insurance', () => {
    expect(processPayment(100, "cash", false)).toBe(100);
  });
});
```

**Key Insight**: Cyclomatic complexity > 10 indicates code that's difficult to test and maintain. Refactor complex functions into smaller ones.

### 4. Boundary Analysis

**Principle**: Errors cluster at boundaries. Test the edges, not just the middle.

**Boundary Conditions to Test**:
- Minimum and maximum values
- Empty and full collections
- First and last elements
- Just inside and just outside boundaries
- Null and undefined values
- Beginning and end of time ranges

**Example:**

```python
# Python - Boundary testing for pagination
def get_page(items, page_number, page_size):
    """Get a page of items.

    Args:
        items: List of items to paginate
        page_number: Page number (1-indexed)
        page_size: Number of items per page

    Returns:
        List of items for the requested page
    """
    if page_number < 1:
        raise ValueError("Page number must be at least 1")
    if page_size < 1:
        raise ValueError("Page size must be at least 1")

    start_index = (page_number - 1) * page_size
    end_index = start_index + page_size
    return items[start_index:end_index]

# Comprehensive boundary tests
def test_get_page_boundaries():
    items = list(range(1, 11))  # [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]

    # First page
    assert get_page(items, 1, 3) == [1, 2, 3]

    # Last full page
    assert get_page(items, 3, 3) == [7, 8, 9]

    # Partial last page
    assert get_page(items, 4, 3) == [10]

    # Beyond last page (empty result)
    assert get_page(items, 5, 3) == []

    # Single item per page - first
    assert get_page(items, 1, 1) == [1]

    # Single item per page - last
    assert get_page(items, 10, 1) == [10]

    # All items in one page
    assert get_page(items, 1, 100) == items

    # Empty list
    assert get_page([], 1, 3) == []

    # Invalid page number
    with pytest.raises(ValueError):
        get_page(items, 0, 3)

    with pytest.raises(ValueError):
        get_page(items, -1, 3)

    # Invalid page size
    with pytest.raises(ValueError):
        get_page(items, 1, 0)
```

```java
// Java - Boundary testing for date ranges
public class DateRangeValidator {
    private static final LocalDate MIN_DATE = LocalDate.of(2000, 1, 1);
    private static final LocalDate MAX_DATE = LocalDate.of(2100, 12, 31);

    public boolean isValidRange(LocalDate start, LocalDate end) {
        if (start == null || end == null) {
            return false;
        }
        if (start.isBefore(MIN_DATE) || end.isAfter(MAX_DATE)) {
            return false;
        }
        return !start.isAfter(end);
    }
}

@Test
public void testDateRange_Boundaries() {
    DateRangeValidator validator = new DateRangeValidator();

    // Valid: At minimum boundary
    assertTrue(validator.isValidRange(
        LocalDate.of(2000, 1, 1),
        LocalDate.of(2000, 1, 2)
    ));

    // Invalid: Just before minimum
    assertFalse(validator.isValidRange(
        LocalDate.of(1999, 12, 31),
        LocalDate.of(2000, 1, 2)
    ));

    // Valid: At maximum boundary
    assertTrue(validator.isValidRange(
        LocalDate.of(2100, 12, 30),
        LocalDate.of(2100, 12, 31)
    ));

    // Invalid: Just after maximum
    assertFalse(validator.isValidRange(
        LocalDate.of(2100, 12, 30),
        LocalDate.of(2101, 1, 1)
    ));

    // Valid: Same day (boundary case)
    assertTrue(validator.isValidRange(
        LocalDate.of(2050, 6, 15),
        LocalDate.of(2050, 6, 15)
    ));

    // Invalid: End before start
    assertFalse(validator.isValidRange(
        LocalDate.of(2050, 6, 15),
        LocalDate.of(2050, 6, 14)
    ));

    // Invalid: Null start
    assertFalse(validator.isValidRange(null, LocalDate.of(2050, 6, 15)));

    // Invalid: Null end
    assertFalse(validator.isValidRange(LocalDate.of(2050, 6, 15), null));
}
```

**Key Insight**: Most bugs occur at boundaries. Test extensively at edges.

### 5. Data-Flow Testing

**Principle**: Test that variables are defined before use, used after definition, and properly released.

**Data States to Test**:
- **Defined**: Variable assigned a value
- **Used**: Variable value is read
- **Killed**: Variable goes out of scope or is reassigned

**Common Defects**:
- Using undefined variables
- Defining variables that are never used (dead code)
- Variables defined twice without being used

**Example:**

```python
# Python - Data flow testing
def calculate_order_total(items, tax_rate, shipping_cost):
    """Calculate order total with tax and shipping.

    Data flow:
    - items: defined by parameter, used in loop
    - tax_rate: defined by parameter, used in tax calculation
    - shipping_cost: defined by parameter, used in final calculation
    - subtotal: defined before loop, used in tax calculation
    - item: defined in loop, used in accumulation
    - total: defined after tax, used in return
    """
    subtotal = 0  # Define

    for item in items:  # Define item
        subtotal += item.price * item.quantity  # Use item, Use/Define subtotal

    tax = subtotal * tax_rate  # Use subtotal, Use tax_rate, Define tax
    total = subtotal + tax + shipping_cost  # Use all, Define total

    return total  # Use total

# Test data flows
def test_calculate_order_total_data_flows():
    Item = namedtuple('Item', ['price', 'quantity'])

    # Test: All variables used
    items = [Item(10, 2), Item(5, 3)]
    total = calculate_order_total(items, 0.1, 5)
    assert total == 40.5  # (20 + 15) + 3.5 + 5

    # Test: Empty items (subtotal defined but loop body not executed)
    total = calculate_order_total([], 0.1, 5)
    assert total == 5  # 0 + 0 + 5

    # Test: Zero tax rate (tax_rate defined but results in zero)
    items = [Item(10, 1)]
    total = calculate_order_total(items, 0, 5)
    assert total == 15  # 10 + 0 + 5

    # Test: Zero shipping (shipping_cost defined but is zero)
    items = [Item(10, 1)]
    total = calculate_order_total(items, 0.1, 0)
    assert total == 11  # 10 + 1 + 0
```

**Key Insight**: Trace how data flows through your code to identify logical errors.

### 6. Error Guessing

**Principle**: Use your experience and intuition to guess where errors are likely.

**Common Error Patterns**:
- Off-by-one errors in loops
- Null pointer/reference errors
- Division by zero
- Integer overflow
- String encoding issues
- Timezone problems
- Race conditions
- Resource leaks

**Example:**

```typescript
// TypeScript - Error guessing for common mistakes
class ShoppingCart {
  private items: CartItem[] = [];

  addItem(item: CartItem): void {
    this.items.push(item);
  }

  removeItem(index: number): void {
    // Potential error: What if index is out of bounds?
    this.items.splice(index, 1);
  }

  getTotal(): number {
    // Potential error: What if items array is empty?
    // Potential error: What if item.price is null/undefined?
    return this.items.reduce((sum, item) => sum + item.price * item.quantity, 0);
  }

  applyDiscount(percentage: number): number {
    // Potential error: What if percentage > 100?
    // Potential error: What if percentage is negative?
    const total = this.getTotal();
    return total * (1 - percentage / 100);
  }
}

// Test for guessed errors
describe('ShoppingCart - error cases', () => {
  let cart: ShoppingCart;

  beforeEach(() => {
    cart = new ShoppingCart();
  });

  describe('removeItem', () => {
    it('handles removing from empty cart', () => {
      expect(() => cart.removeItem(0)).not.toThrow();
    });

    it('handles negative index', () => {
      cart.addItem({ name: "Item", price: 10, quantity: 1 });
      expect(() => cart.removeItem(-1)).not.toThrow();
    });

    it('handles index beyond array length', () => {
      cart.addItem({ name: "Item", price: 10, quantity: 1 });
      expect(() => cart.removeItem(5)).not.toThrow();
    });
  });

  describe('getTotal', () => {
    it('handles empty cart', () => {
      expect(cart.getTotal()).toBe(0);
    });

    it('handles items with zero price', () => {
      cart.addItem({ name: "Free", price: 0, quantity: 5 });
      expect(cart.getTotal()).toBe(0);
    });

    it('handles items with zero quantity', () => {
      cart.addItem({ name: "Item", price: 10, quantity: 0 });
      expect(cart.getTotal()).toBe(0);
    });
  });

  describe('applyDiscount', () => {
    beforeEach(() => {
      cart.addItem({ name: "Item", price: 100, quantity: 1 });
    });

    it('handles 100% discount', () => {
      expect(cart.applyDiscount(100)).toBe(0);
    });

    it('handles discount > 100%', () => {
      const result = cart.applyDiscount(150);
      expect(result).toBeGreaterThanOrEqual(0); // Should we allow this?
    });

    it('handles negative discount', () => {
      const result = cart.applyDiscount(-10);
      expect(result).toBe(110); // Negative discount = surcharge
    });

    it('handles zero discount', () => {
      expect(cart.applyDiscount(0)).toBe(100);
    });
  });
});
```

**Key Insight**: Experience teaches you where bugs hide. Test those areas thoroughly.

## Testing Strategies

### Test-First vs. Test-Last

**Test-First (TDD)**:
```python
# Python - Write test first
def test_fibonacci():
    assert fibonacci(0) == 0
    assert fibonacci(1) == 1
    assert fibonacci(2) == 1
    assert fibonacci(5) == 5
    assert fibonacci(10) == 55

# Then implement
def fibonacci(n):
    if n <= 1:
        return n
    return fibonacci(n-1) + fibonacci(n-2)
```

**Benefits of Test-First**:
- Forces you to think about interface before implementation
- Ensures 100% coverage by definition
- Creates minimal code (only what's needed to pass tests)
- Tests are easier to write (no implementation bias)

**Test-Last**:
```java
// Java - Write implementation first
public class StringUtils {
    public static String reverse(String input) {
        if (input == null) return null;
        return new StringBuilder(input).reverse().toString();
    }
}

// Then write tests
@Test
public void testReverse() {
    assertEquals("olleh", StringUtils.reverse("hello"));
    assertEquals("", StringUtils.reverse(""));
    assertNull(StringUtils.reverse(null));
}
```

**Benefits of Test-Last**:
- Faster for simple, well-understood problems
- Allows exploration of implementation approaches
- Can be easier when design is unclear

**Recommendation**: Use test-first for complex logic and test-last for simple utilities. Mix both approaches based on context.

### Test Scaffolding

**Scaffolding**: Temporary code that supports testing but isn't part of the production system.

**Types of Test Scaffolding**:

**Stubs**: Provide predetermined responses to calls
```python
# Python - Stub for external API
class PaymentGatewayStub:
    def process_payment(self, amount, card_number):
        # Always returns success for testing
        return {"status": "success", "transaction_id": "test-123"}

def test_checkout_with_stub():
    gateway = PaymentGatewayStub()
    checkout = CheckoutService(gateway)

    result = checkout.process_order(100, "4111-1111-1111-1111")
    assert result["status"] == "success"
```

**Mocks**: Verify that specific calls were made
```typescript
// TypeScript - Mock with Jest
import { EmailService } from './emailService';
import { UserRegistration } from './userRegistration';

jest.mock('./emailService');

test('sends welcome email on registration', () => {
  const mockEmailService = new EmailService() as jest.Mocked<EmailService>;
  mockEmailService.sendWelcomeEmail = jest.fn();

  const registration = new UserRegistration(mockEmailService);
  registration.registerUser('test@example.com');

  expect(mockEmailService.sendWelcomeEmail).toHaveBeenCalledWith('test@example.com');
});
```

**Fakes**: Working implementations with shortcuts
```java
// Java - Fake database for testing
public class InMemoryUserRepository implements UserRepository {
    private Map<Long, User> users = new HashMap<>();
    private AtomicLong idGenerator = new AtomicLong();

    @Override
    public User save(User user) {
        if (user.getId() == null) {
            user.setId(idGenerator.incrementAndGet());
        }
        users.put(user.getId(), user);
        return user;
    }

    @Override
    public Optional<User> findById(Long id) {
        return Optional.ofNullable(users.get(id));
    }
}

@Test
public void testUserService() {
    UserRepository fakeRepo = new InMemoryUserRepository();
    UserService service = new UserService(fakeRepo);

    User user = service.createUser("test@example.com");
    assertNotNull(user.getId());

    User retrieved = service.getUser(user.getId());
    assertEquals("test@example.com", retrieved.getEmail());
}
```

**Drivers**: Call the code being tested
```python
# Python - Test driver for command-line tool
def test_cli_command():
    # Driver: Simulates command-line execution
    from click.testing import CliRunner
    from myapp.cli import process_file

    runner = CliRunner()
    with runner.isolated_filesystem():
        with open('input.txt', 'w') as f:
            f.write('test data')

        result = runner.invoke(process_file, ['input.txt'])

        assert result.exit_code == 0
        assert 'Processing complete' in result.output
```

**Key Insight**: Good scaffolding makes testing easier and faster. Invest in reusable test infrastructure.

## Testing for Specific Error Classes

### Testing for Null/None

```python
# Python - Comprehensive null testing
def format_user_name(first_name, last_name):
    """Format user's full name.

    Handles None values gracefully.
    """
    if first_name is None and last_name is None:
        return "Unknown"
    if first_name is None:
        return last_name
    if last_name is None:
        return first_name
    return f"{first_name} {last_name}"

def test_format_user_name_null_cases():
    # Both None
    assert format_user_name(None, None) == "Unknown"

    # First None
    assert format_user_name(None, "Doe") == "Doe"

    # Last None
    assert format_user_name("John", None) == "John"

    # Neither None
    assert format_user_name("John", "Doe") == "John Doe"

    # Empty strings (different from None!)
    assert format_user_name("", "") == " "  # Documents current behavior
    assert format_user_name("", "Doe") == " Doe"
```

### Testing for Off-By-One Errors

```java
// Java - Off-by-one boundary testing
public class ArrayProcessor {
    public static int findLargest(int[] numbers) {
        if (numbers == null || numbers.length == 0) {
            throw new IllegalArgumentException("Array cannot be empty");
        }

        int largest = numbers[0];
        for (int i = 1; i < numbers.length; i++) {  // i=1, not i=0
            if (numbers[i] > largest) {
                largest = numbers[i];
            }
        }
        return largest;
    }
}

@Test
public void testFindLargest_OffByOneEdgeCases() {
    // Single element (loop never executes)
    assertEquals(5, ArrayProcessor.findLargest(new int[]{5}));

    // Largest at beginning
    assertEquals(10, ArrayProcessor.findLargest(new int[]{10, 5, 3}));

    // Largest at end (last iteration)
    assertEquals(10, ArrayProcessor.findLargest(new int[]{3, 5, 10}));

    // Largest in middle
    assertEquals(10, ArrayProcessor.findLargest(new int[]{3, 10, 5}));

    // All same values
    assertEquals(5, ArrayProcessor.findLargest(new int[]{5, 5, 5}));
}
```

### Testing for Concurrency Issues

```python
# Python - Basic concurrency testing
import threading
import time

class Counter:
    def __init__(self):
        self.value = 0
        self.lock = threading.Lock()

    def increment(self):
        with self.lock:
            current = self.value
            time.sleep(0.001)  # Simulate work
            self.value = current + 1

def test_counter_thread_safety():
    counter = Counter()
    threads = []

    # Create 10 threads that each increment 100 times
    for _ in range(10):
        thread = threading.Thread(
            target=lambda: [counter.increment() for _ in range(100)]
        )
        threads.append(thread)
        thread.start()

    # Wait for all threads
    for thread in threads:
        thread.join()

    # If thread-safe, should be exactly 1000
    assert counter.value == 1000
```

## Test Organization Patterns

### Arrange-Act-Assert (AAA)

```typescript
// TypeScript - Clear AAA structure
describe('OrderService', () => {
  it('calculates total with tax and shipping', () => {
    // Arrange - Set up test data
    const items = [
      { name: 'Item 1', price: 10, quantity: 2 },
      { name: 'Item 2', price: 5, quantity: 3 }
    ];
    const taxRate = 0.1;
    const shippingCost = 5;
    const service = new OrderService();

    // Act - Execute the behavior
    const total = service.calculateTotal(items, taxRate, shippingCost);

    // Assert - Verify the result
    expect(total).toBe(40.5);  // (20 + 15) * 1.1 + 5
  });
});
```

### Given-When-Then (BDD Style)

```python
# Python - BDD-style test organization
def test_user_registration():
    # Given a registration service and valid user data
    service = RegistrationService()
    email = "newuser@example.com"
    password = "SecurePass123!"

    # When registering a new user
    user = service.register(email, password)

    # Then the user should be created with correct attributes
    assert user.email == email
    assert user.is_active is True
    assert user.created_at is not None
    # And password should be hashed, not stored in plaintext
    assert user.password != password
```

### Test Fixtures and Setup

```java
// Java - Shared test setup with JUnit
public class UserServiceTest {
    private UserService userService;
    private InMemoryUserRepository repository;

    @BeforeEach
    public void setUp() {
        // Common setup for all tests
        repository = new InMemoryUserRepository();
        userService = new UserService(repository);
    }

    @Test
    public void testCreateUser() {
        User user = userService.createUser("test@example.com");
        assertNotNull(user.getId());
    }

    @Test
    public void testDuplicateEmail() {
        userService.createUser("test@example.com");
        assertThrows(DuplicateEmailException.class, () -> {
            userService.createUser("test@example.com");
        });
    }

    @AfterEach
    public void tearDown() {
        // Cleanup if needed
        repository.clear();
    }
}
```

## Practical Testing Checklist

### Before Writing Code

- [ ] Understand the requirements completely
- [ ] Identify edge cases and error conditions
- [ ] Determine test strategy (test-first vs. test-last)
- [ ] Set up necessary test infrastructure

### While Writing Code

- [ ] Write tests for each new function/method
- [ ] Test normal cases first, then edge cases
- [ ] Test error conditions and exceptions
- [ ] Test boundary conditions explicitly
- [ ] Verify all independent paths are tested

### After Writing Code

- [ ] Check cyclomatic complexity (should be ≤ 10)
- [ ] Verify coverage meets standards (85-90%)
- [ ] Review tests for clarity and maintainability
- [ ] Remove redundant or duplicate tests
- [ ] Ensure tests are fast (< 1 second total)

### Test Quality Criteria

- [ ] Tests are independent (can run in any order)
- [ ] Tests are deterministic (same input = same result)
- [ ] Tests are fast (milliseconds, not seconds)
- [ ] Tests have clear, descriptive names
- [ ] Tests follow AAA or Given-When-Then structure
- [ ] Assertions are specific and meaningful
- [ ] Test failures provide helpful error messages

## Common Testing Pitfalls

### Pitfall 1: Testing Implementation, Not Behavior

**Poor:**
```python
# Tests internal implementation details
def test_user_service_calls_repository():
    mock_repo = Mock()
    service = UserService(mock_repo)
    service.create_user("test@example.com")

    # Testing how it works, not what it does
    mock_repo.save.assert_called_once()
```

**Good:**
```python
# Tests observable behavior
def test_user_service_creates_accessible_user():
    repo = InMemoryUserRepository()
    service = UserService(repo)

    # Create user
    created = service.create_user("test@example.com")

    # Verify behavior: can retrieve created user
    retrieved = service.get_user(created.id)
    assert retrieved.email == "test@example.com"
```

### Pitfall 2: Tests That Are Too Large

**Poor:**
```typescript
// One massive test for everything
it('handles complete user lifecycle', () => {
  const service = new UserService();

  // Registration
  const user = service.register('test@example.com', 'password');
  expect(user.isActive).toBe(false);

  // Email verification
  service.verifyEmail(user.id, user.verificationToken);
  expect(service.getUser(user.id).isActive).toBe(true);

  // Password change
  service.changePassword(user.id, 'password', 'newPassword');
  expect(service.login('test@example.com', 'newPassword')).toBeTruthy();

  // Account deletion
  service.deleteAccount(user.id);
  expect(service.getUser(user.id)).toBeNull();
});
```

**Good:**
```typescript
// Separate, focused tests
describe('UserService', () => {
  it('creates inactive users on registration', () => {
    const user = service.register('test@example.com', 'password');
    expect(user.isActive).toBe(false);
  });

  it('activates user after email verification', () => {
    const user = service.register('test@example.com', 'password');
    service.verifyEmail(user.id, user.verificationToken);

    const verified = service.getUser(user.id);
    expect(verified.isActive).toBe(true);
  });

  // ... separate tests for password change and deletion
});
```

### Pitfall 3: Non-Deterministic Tests

**Poor:**
```python
# Test depends on current time
def test_user_age():
    user = User(birthdate=datetime(1990, 1, 1))
    assert user.age == 34  # Fails in 2025!
```

**Good:**
```python
# Test uses fixed reference point
def test_user_age():
    user = User(birthdate=datetime(1990, 1, 1))
    reference_date = datetime(2024, 1, 1)
    assert user.calculate_age(reference_date) == 34
```

### Pitfall 4: Tests That Don't Fail

```java
// Test that can never fail
@Test
public void testCalculation() {
    Calculator calc = new Calculator();
    int result = calc.add(2, 2);
    assertTrue(result == 4 || result == 5);  // Too permissive!
}

// Proper test with specific assertion
@Test
public void testAddition() {
    Calculator calc = new Calculator();
    assertEquals(4, calc.add(2, 2));
}
```

## Integration with Geist Framework

### Ghost Analysis: Unknown Testing Requirements

**Question**: What edge cases am I not seeing?

Apply Ghost thinking:
- What assumptions am I making about inputs?
- What failure modes haven't I considered?
- What parallel realities exist where my code fails?

**Example:**
```python
# Visible requirement
def divide(a, b):
    return a / b

# Ghost analysis reveals hidden requirements
def divide(a, b):
    """Divide a by b with proper error handling.

    Ghost considerations:
    - What if b is zero?
    - What if a or b are not numbers?
    - What if result exceeds float precision?
    - What about negative zero?
    - What about infinity?
    """
    if not isinstance(a, (int, float)) or not isinstance(b, (int, float)):
        raise TypeError(f"Cannot divide {type(a)} by {type(b)}")
    if b == 0:
        raise ValueError("Cannot divide by zero")
    if math.isinf(a) or math.isinf(b):
        raise ValueError("Cannot divide infinity")

    return a / b
```

### Geyser Analysis: Testing for Change

**Question**: How will future changes affect my tests?

Design tests that accommodate growth:
- Test interfaces, not implementations
- Use test builders for complex objects
- Abstract test data creation
- Make tests resilient to refactoring

**Example:**
```typescript
// Brittle test (breaks with refactoring)
it('creates user with correct fields', () => {
  const user = new User('John', 'Doe', 'john@example.com');
  expect(user.firstName).toBe('John');
  expect(user.lastName).toBe('Doe');
  expect(user.email).toBe('john@example.com');
});

// Resilient test (survives refactoring)
it('creates user with correct full name and contact info', () => {
  const user = createTestUser({
    firstName: 'John',
    lastName: 'Doe',
    email: 'john@example.com'
  });

  expect(user.getFullName()).toBe('John Doe');
  expect(user.getContactEmail()).toBe('john@example.com');
});
```

### Gist Analysis: Essential Testing

**Question**: What's the essence of what I'm testing?

Focus on essential behavior, not accidental complexity:
- Test business rules, not framework code
- Test outcomes, not mechanisms
- Test value delivered, not implementation steps

**Example:**
```python
# Tests accidental complexity
def test_order_processing_steps():
    order = Order()
    assert order.state == "created"

    order.add_item(item1)
    assert order.state == "items_added"

    order.calculate_total()
    assert order.state == "calculated"

    order.process_payment()
    assert order.state == "paid"

# Tests essential behavior (Gist)
def test_order_processing_essential():
    order = create_order_with_items([item1, item2])

    result = order.complete_purchase(payment_method)

    # Essential outcomes
    assert result.is_successful
    assert customer_received_confirmation_email()
    assert inventory_was_updated()
    assert payment_was_captured()
```

## Further Reading

### Related Guides in This Repository
- **UNIT_TESTING_PRINCIPLES.md** - Clean Code testing principles
- **TDD_WORKFLOW.md** - Test-driven development workflow
- **TEST_DESIGN_PATTERNS.md** - Advanced testing patterns
- **01-foundations/ERROR_HANDLING.md** - Designing code that's easy to test
- **03-clean-architecture/TESTABLE_ARCHITECTURE.md** - Architectural patterns for testability

### External Resources
- **Code Complete 2** (Chapters 22-23) - Comprehensive developer testing coverage
- **Clean Code** (Chapter 9) - Writing clean tests
- **xUnit Test Patterns** by Gerard Meszaros - Comprehensive test pattern catalog
- **Growing Object-Oriented Software, Guided by Tests** - TDD in practice

## Summary

Developer testing is not an optional activity—it's a fundamental part of software construction. Key takeaways:

1. **Test your own code** before declaring it complete
2. **Coverage is necessary but insufficient**—test logic, not just lines
3. **Test boundary conditions** where errors cluster
4. **Use structured basis testing** to ensure all paths are tested
5. **Build test scaffolding** to make testing easier
6. **Test errors explicitly**—don't just test happy paths
7. **Apply Geist thinking** to find hidden test requirements

Effective developer testing results in:
- Fewer defects reaching production
- Higher confidence in changes
- Better software design
- Living documentation
- Faster debugging

**Remember**: The goal of testing is not to prove that code works—it's to discover where it doesn't work while you can still fix it cheaply.
