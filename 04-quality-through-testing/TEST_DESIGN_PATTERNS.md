# Test Design Patterns: Advanced Testing Techniques

## Overview

Test design patterns are proven solutions to common testing challenges. While basic testing principles teach you to write individual tests, design patterns help you organize test suites, manage complexity, and maintain tests as systems evolve.

This comprehensive guide presents practical testing patterns that make test code more maintainable, readable, and effective. These patterns apply across languages and frameworks, providing a toolkit for building robust test suites.

## Why Test Design Patterns Matter

**"Tests are the Programmer's Stone, transmuting fear into boredom."** — Kent Beck

As codebases grow, test suites face specific challenges:

**Test Fragility**: Tests break when implementation details change, even when behavior is correct.

**Slow Feedback**: Large test suites take too long to run, reducing their usefulness.

**Test Duplication**: Similar setup code appears across many tests, violating DRY.

**Unclear Failures**: When tests fail, it's hard to understand what broke and why.

**Test Debt**: Poorly structured tests become a maintenance burden rather than a safety net.

### Benefits of Test Patterns

Well-designed test suites provide:
- **Maintainability**: Tests survive refactoring and remain readable
- **Fast Feedback**: Optimized test execution provides rapid results
- **Clear Intent**: Test structure clearly communicates expected behavior
- **Reusability**: Common patterns are abstracted and shared
- **Confidence**: Reliable tests enable aggressive refactoring

## Source Materials

This guide synthesizes patterns from:

- **xUnit Test Patterns** by Gerard Meszaros
  - Comprehensive test pattern catalog
  - Test smells and solutions
- **Clean Code** by Robert C. Martin (Chapter 9)
  - Clean test principles
- **Code Complete 2** by Steve McConnell (Chapters 22-23)
  - Testing strategies and techniques
- **Growing Object-Oriented Software, Guided by Tests**
  - Advanced TDD patterns

## Creation Patterns

### Test Data Builder Pattern

**Problem**: Creating complex test objects requires verbose, repetitive setup code.

**Solution**: Use the Builder pattern to create test data with fluent, readable syntax.

```java
// Java - Without Builder (verbose)
@Test
public void testOrderProcessing() {
    Address address = new Address();
    address.setStreet("123 Main St");
    address.setCity("Springfield");
    address.setState("IL");
    address.setZip("62701");
    address.setCountry("USA");

    Customer customer = new Customer();
    customer.setFirstName("John");
    customer.setLastName("Doe");
    customer.setEmail("john@example.com");
    customer.setPhone("555-1234");
    customer.setAddress(address);

    Order order = new Order();
    order.setCustomer(customer);
    order.setStatus(OrderStatus.PENDING);
    order.setCreatedDate(LocalDate.now());

    // Test logic buried in setup...
}

// Java - With Builder (clean)
@Test
public void testOrderProcessing() {
    Order order = anOrder()
        .forCustomer(aCustomer()
            .named("John Doe")
            .withEmail("john@example.com")
            .at(anAddress().inSpringfieldIL()))
        .withStatus(PENDING)
        .build();

    // Test logic is now clear and prominent
    processor.process(order);

    assertEquals(COMPLETED, order.getStatus());
}

// Builder implementation
public class OrderBuilder {
    private Customer customer = aCustomer().build();
    private OrderStatus status = PENDING;
    private LocalDate createdDate = LocalDate.now();
    private List<OrderItem> items = new ArrayList<>();

    public OrderBuilder forCustomer(CustomerBuilder customerBuilder) {
        this.customer = customerBuilder.build();
        return this;
    }

    public OrderBuilder withStatus(OrderStatus status) {
        this.status = status;
        return this;
    }

    public OrderBuilder createdOn(LocalDate date) {
        this.createdDate = date;
        return this;
    }

    public OrderBuilder withItem(Product product, int quantity) {
        items.add(new OrderItem(product, quantity));
        return this;
    }

    public Order build() {
        Order order = new Order();
        order.setCustomer(customer);
        order.setStatus(status);
        order.setCreatedDate(createdDate);
        items.forEach(order::addItem);
        return order;
    }

    // Factory method
    public static OrderBuilder anOrder() {
        return new OrderBuilder();
    }
}
```

**Benefits**:
- Tests are more readable (focus on what's being tested)
- Default values reduce boilerplate
- Changes to object structure require fewer test changes
- Builders can be reused across tests

```python
# Python - Builder pattern implementation
class UserBuilder:
    def __init__(self):
        self._email = "default@example.com"
        self._name = "Default User"
        self._age = 25
        self._is_active = True
        self._roles = []

    def with_email(self, email):
        self._email = email
        return self

    def named(self, name):
        self._name = name
        return self

    def aged(self, age):
        self._age = age
        return self

    def inactive(self):
        self._is_active = False
        return self

    def with_role(self, role):
        self._roles.append(role)
        return self

    def with_roles(self, *roles):
        self._roles.extend(roles)
        return self

    def build(self):
        return User(
            email=self._email,
            name=self._name,
            age=self._age,
            is_active=self._is_active,
            roles=self._roles
        )

# Usage in tests
def test_admin_can_delete_users():
    admin = (UserBuilder()
        .named("Admin User")
        .with_role("admin")
        .build())

    target_user = (UserBuilder()
        .named("Regular User")
        .build())

    result = admin.can_delete(target_user)
    assert result is True

def test_regular_user_cannot_delete_users():
    regular_user = UserBuilder().build()  # All defaults
    target_user = UserBuilder().build()

    result = regular_user.can_delete(target_user)
    assert result is False
```

### Object Mother Pattern

**Problem**: Need to create common test objects quickly without repeating construction logic.

**Solution**: Create factory methods that produce commonly used test objects.

```typescript
// TypeScript - Object Mother pattern
export class UserMother {
  static createAdmin(): User {
    return new User({
      id: 'admin-1',
      email: 'admin@example.com',
      name: 'Admin User',
      roles: ['admin', 'user'],
      isActive: true
    });
  }

  static createRegularUser(): User {
    return new User({
      id: 'user-1',
      email: 'user@example.com',
      name: 'Regular User',
      roles: ['user'],
      isActive: true
    });
  }

  static createInactiveUser(): User {
    return new User({
      id: 'inactive-1',
      email: 'inactive@example.com',
      name: 'Inactive User',
      roles: ['user'],
      isActive: false
    });
  }

  static createPremiumUser(): User {
    return new User({
      id: 'premium-1',
      email: 'premium@example.com',
      name: 'Premium User',
      roles: ['user', 'premium'],
      isActive: true
    });
  }
}

// Usage in tests
describe('UserService', () => {
  it('allows admins to delete users', () => {
    const admin = UserMother.createAdmin();
    const target = UserMother.createRegularUser();

    expect(admin.canDelete(target)).toBe(true);
  });

  it('prevents inactive users from posting', () => {
    const inactiveUser = UserMother.createInactiveUser();

    expect(() => inactiveUser.createPost('content')).toThrow();
  });

  it('gives premium users access to premium features', () => {
    const premiumUser = UserMother.createPremiumUser();

    expect(premiumUser.hasAccessTo('premium-feature')).toBe(true);
  });
});
```

**Benefits**:
- Centralized test data creation
- Consistent test objects across suite
- Easy to update when object structure changes
- Clear, semantic test setup

**Combine with Builder**:

```python
# Python - Object Mother + Builder
class UserMother:
    @staticmethod
    def admin():
        return UserBuilder().with_role('admin').build()

    @staticmethod
    def regular_user():
        return UserBuilder().build()

    @staticmethod
    def premium_user():
        return UserBuilder().with_role('premium').build()

# Usage - can still customize
def test_premium_admin():
    admin = UserMother.admin().with_role('premium')  # Combine!
```

## Organization Patterns

### Test Fixture Setup Pattern

**Problem**: Many tests need the same initial setup, leading to duplication.

**Solution**: Use setup/teardown hooks to share common initialization.

```python
# Python - Fixture pattern with pytest
import pytest

@pytest.fixture
def database():
    """Provide a clean database for each test."""
    db = InMemoryDatabase()
    db.initialize_schema()
    yield db  # Test runs here
    db.cleanup()

@pytest.fixture
def user_repository(database):
    """Provide a user repository with database."""
    return UserRepository(database)

@pytest.fixture
def sample_users(user_repository):
    """Provide pre-populated users."""
    users = [
        User(email="user1@example.com", name="User One"),
        User(email="user2@example.com", name="User Two"),
        User(email="user3@example.com", name="User Three")
    ]
    for user in users:
        user_repository.save(user)
    return users

# Tests use fixtures
def test_find_user_by_email(user_repository, sample_users):
    found = user_repository.find_by_email("user1@example.com")
    assert found.name == "User One"

def test_list_all_users(user_repository, sample_users):
    all_users = user_repository.find_all()
    assert len(all_users) == 3
```

```java
// Java - JUnit setup pattern
public class UserServiceTest {
    private UserService userService;
    private InMemoryUserRepository repository;
    private User testUser;

    @BeforeEach
    public void setUp() {
        // Runs before each test
        repository = new InMemoryUserRepository();
        userService = new UserService(repository);

        testUser = new User("test@example.com");
        repository.save(testUser);
    }

    @AfterEach
    public void tearDown() {
        // Runs after each test
        repository.clear();
    }

    @Test
    public void testFindUser() {
        User found = userService.findByEmail("test@example.com");
        assertEquals(testUser.getId(), found.getId());
    }

    @Test
    public void testDeleteUser() {
        userService.delete(testUser.getId());
        assertNull(userService.findByEmail("test@example.com"));
    }
}
```

**Key Principle**: Each test should be independent. Setup creates fresh state for each test.

### Parameterized Test Pattern

**Problem**: Testing similar scenarios with different inputs requires duplicate test code.

**Solution**: Use parameterized tests to run the same test with multiple inputs.

```python
# Python - Parameterized tests with pytest
import pytest

@pytest.mark.parametrize("input_email,expected_valid", [
    ("valid@example.com", True),
    ("another@test.org", True),
    ("user+tag@domain.co.uk", True),
    ("invalid@", False),
    ("@example.com", False),
    ("no-at-sign.com", False),
    ("", False),
    ("spaces in@email.com", False),
])
def test_email_validation(input_email, expected_valid):
    validator = EmailValidator()
    result = validator.is_valid(input_email)
    assert result == expected_valid
```

```java
// Java - JUnit parameterized tests
@ParameterizedTest
@CsvSource({
    "0, 0",
    "1, 1",
    "2, 2",
    "3, Fizz",
    "5, Buzz",
    "15, FizzBuzz",
    "30, FizzBuzz"
})
public void testFizzBuzz(int input, String expected) {
    String result = FizzBuzz.convert(input);
    assertEquals(expected, result);
}

@ParameterizedTest
@ValueSource(strings = {"", "   ", "\t", "\n"})
public void testBlankStrings(String input) {
    assertTrue(StringUtils.isBlank(input));
}

@ParameterizedTest
@MethodSource("provideUsersForValidation")
public void testUserValidation(User user, boolean expectedValid) {
    boolean result = validator.isValid(user);
    assertEquals(expectedValid, result);
}

private static Stream<Arguments> provideUsersForValidation() {
    return Stream.of(
        Arguments.of(new User("valid@example.com", 25), true),
        Arguments.of(new User("valid@example.com", 150), false),
        Arguments.of(new User("invalid", 25), false)
    );
}
```

```typescript
// TypeScript - Parameterized tests with Jest
describe('calculateDiscount', () => {
  const testCases = [
    { customerType: 'premium', amount: 100, expected: 80 },
    { customerType: 'premium', amount: 50, expected: 40 },
    { customerType: 'standard', amount: 100, expected: 90 },
    { customerType: 'standard', amount: 50, expected: 45 },
    { customerType: 'guest', amount: 100, expected: 100 },
  ];

  testCases.forEach(({ customerType, amount, expected }) => {
    it(`calculates ${expected} for ${customerType} customer with amount ${amount}`, () => {
      const result = calculateDiscount(amount, customerType);
      expect(result).toBe(expected);
    });
  });
});
```

**Benefits**:
- Reduces test duplication
- Makes it easy to add new test cases
- Clear documentation of expected behavior across inputs
- Identifies patterns in requirements

## Isolation Patterns

### Test Double Pattern

**Problem**: Tests depend on external systems (databases, APIs, file systems) that are slow or unavailable.

**Solution**: Replace dependencies with test doubles (stubs, mocks, fakes, spies).

#### Stub Pattern

**Use When**: You need to provide predetermined responses to queries.

```python
# Python - Stub for external API
class WeatherAPIStub:
    """Stub always returns sunny weather."""

    def get_weather(self, city):
        return {
            'temperature': 72,
            'condition': 'sunny',
            'humidity': 45
        }

def test_weather_display_formats_correctly():
    api = WeatherAPIStub()
    display = WeatherDisplay(api)

    output = display.get_forecast('San Francisco')

    assert output == "San Francisco: 72°F, sunny, 45% humidity"
```

#### Mock Pattern

**Use When**: You need to verify that specific methods were called with expected arguments.

```typescript
// TypeScript - Mock with verification
test('order processing sends confirmation email', async () => {
  const mockEmailService = {
    sendEmail: jest.fn().mockResolvedValue({ success: true })
  };

  const orderService = new OrderService(mockEmailService);
  await orderService.processOrder(order);

  // Verify interaction
  expect(mockEmailService.sendEmail).toHaveBeenCalledWith({
    to: 'customer@example.com',
    subject: 'Order Confirmation',
    body: expect.stringContaining('Order #12345')
  });
});
```

#### Fake Pattern

**Use When**: You need a working implementation with shortcuts (e.g., in-memory database).

```java
// Java - Fake in-memory repository
public class InMemoryUserRepository implements UserRepository {
    private final Map<Long, User> users = new ConcurrentHashMap<>();
    private final AtomicLong idGenerator = new AtomicLong(1);

    @Override
    public User save(User user) {
        if (user.getId() == null) {
            user.setId(idGenerator.getAndIncrement());
        }
        users.put(user.getId(), user.clone());
        return user;
    }

    @Override
    public Optional<User> findById(Long id) {
        return Optional.ofNullable(users.get(id)).map(User::clone);
    }

    @Override
    public List<User> findAll() {
        return new ArrayList<>(users.values());
    }

    @Override
    public void deleteById(Long id) {
        users.remove(id);
    }

    public void clear() {
        users.clear();
        idGenerator.set(1);
    }
}

@Test
public void testUserService() {
    UserRepository fakeRepo = new InMemoryUserRepository();
    UserService service = new UserService(fakeRepo);

    User created = service.createUser("test@example.com");
    User retrieved = service.getUserById(created.getId());

    assertEquals(created.getId(), retrieved.getId());
}
```

#### Spy Pattern

**Use When**: You need to record calls while using real implementation.

```python
# Python - Spy wrapper
class EmailServiceSpy:
    def __init__(self, real_service):
        self.real_service = real_service
        self.sent_emails = []

    def send_email(self, to, subject, body):
        self.sent_emails.append({
            'to': to,
            'subject': subject,
            'body': body,
            'timestamp': datetime.now()
        })
        return self.real_service.send_email(to, subject, body)

def test_notification_sends_to_all_recipients():
    real_service = EmailService()
    spy = EmailServiceSpy(real_service)
    notifier = NotificationService(spy)

    notifier.notify_team(['alice@example.com', 'bob@example.com'])

    assert len(spy.sent_emails) == 2
    assert spy.sent_emails[0]['to'] == 'alice@example.com'
    assert spy.sent_emails[1]['to'] == 'bob@example.com'
```

### Dependency Injection for Testability

**Problem**: Hard-coded dependencies make testing difficult.

**Solution**: Inject dependencies through constructors or setters.

```typescript
// TypeScript - Dependency injection

// BEFORE: Hard to test
class OrderService {
  processOrder(order: Order): void {
    const paymentGateway = new StripePaymentGateway();  // Hard-coded!
    const emailService = new SendGridEmailService();     // Hard-coded!

    paymentGateway.charge(order.total);
    emailService.sendConfirmation(order.customer.email);
  }
}

// AFTER: Easy to test
class OrderService {
  constructor(
    private paymentGateway: PaymentGateway,
    private emailService: EmailService
  ) {}

  processOrder(order: Order): void {
    this.paymentGateway.charge(order.total);
    this.emailService.sendConfirmation(order.customer.email);
  }
}

// Testing is now straightforward
test('processes order with injected dependencies', () => {
  const mockPayment = { charge: jest.fn() };
  const mockEmail = { sendConfirmation: jest.fn() };

  const service = new OrderService(mockPayment, mockEmail);
  service.processOrder(testOrder);

  expect(mockPayment.charge).toHaveBeenCalledWith(100);
  expect(mockEmail.sendConfirmation).toHaveBeenCalled();
});
```

## Assertion Patterns

### Custom Assertion Pattern

**Problem**: Complex assertions are verbose and hard to read.

**Solution**: Create custom assertion methods that read naturally.

```java
// Java - Custom assertions for readability

// BEFORE: Verbose assertions
@Test
public void testUserProfile() {
    UserProfile profile = service.getProfile(userId);

    assertEquals("John Doe", profile.getName());
    assertEquals("john@example.com", profile.getEmail());
    assertEquals(25, profile.getAge());
    assertTrue(profile.isPremium());
    assertFalse(profile.isSuspended());
    assertNotNull(profile.getLastLoginDate());
    assertTrue(profile.getLastLoginDate().isAfter(yesterday));
}

// AFTER: Custom assertion
@Test
public void testUserProfile() {
    UserProfile profile = service.getProfile(userId);

    assertThat(profile)
        .hasName("John Doe")
        .hasEmail("john@example.com")
        .hasAge(25)
        .isPremium()
        .isNotSuspended()
        .hasRecentLogin();
}

// Custom assertion builder
public class UserProfileAssert {
    private final UserProfile actual;

    private UserProfileAssert(UserProfile actual) {
        this.actual = actual;
    }

    public static UserProfileAssert assertThat(UserProfile actual) {
        return new UserProfileAssert(actual);
    }

    public UserProfileAssert hasName(String expected) {
        assertEquals(expected, actual.getName(),
            () -> "Expected name: " + expected + ", got: " + actual.getName());
        return this;
    }

    public UserProfileAssert hasEmail(String expected) {
        assertEquals(expected, actual.getEmail());
        return this;
    }

    public UserProfileAssert hasAge(int expected) {
        assertEquals(expected, actual.getAge());
        return this;
    }

    public UserProfileAssert isPremium() {
        assertTrue(actual.isPremium(), "User should be premium");
        return this;
    }

    public UserProfileAssert isNotSuspended() {
        assertFalse(actual.isSuspended(), "User should not be suspended");
        return this;
    }

    public UserProfileAssert hasRecentLogin() {
        assertNotNull(actual.getLastLoginDate());
        LocalDate yesterday = LocalDate.now().minusDays(1);
        assertTrue(actual.getLastLoginDate().isAfter(yesterday),
            "Last login should be recent");
        return this;
    }
}
```

```python
# Python - Custom assertion class
class OrderAssertions:
    def __init__(self, order):
        self.order = order

    def has_status(self, expected_status):
        assert self.order.status == expected_status, \
            f"Expected status {expected_status}, got {self.order.status}"
        return self

    def has_total(self, expected_total):
        assert self.order.total == expected_total, \
            f"Expected total {expected_total}, got {self.order.total}"
        return self

    def has_item_count(self, expected_count):
        actual_count = len(self.order.items)
        assert actual_count == expected_count, \
            f"Expected {expected_count} items, got {actual_count}"
        return self

    def is_paid(self):
        assert self.order.payment_status == 'paid', \
            "Order should be paid"
        return self

def assert_order(order):
    return OrderAssertions(order)

# Usage
def test_order_processing():
    order = process_order(items, payment)

    (assert_order(order)
        .has_status('completed')
        .has_total(150.00)
        .has_item_count(3)
        .is_paid())
```

### Delta Assertion Pattern

**Problem**: Floating-point comparisons fail due to precision issues.

**Solution**: Assert equality within a delta/tolerance.

```typescript
// TypeScript - Delta assertions
describe('financial calculations', () => {
  it('calculates interest correctly', () => {
    const principal = 1000;
    const rate = 0.05;
    const years = 10;

    const interest = calculateCompoundInterest(principal, rate, years);

    // Don't use exact equality for floats
    expect(interest).toBeCloseTo(628.89, 2);  // 2 decimal places
  });

  it('handles currency conversion', () => {
    const usd = 100;
    const rate = 0.85;

    const euros = convertUSDToEUR(usd, rate);

    expect(euros).toBeCloseTo(85.0, 2);
  });
});
```

```python
# Python - Approximate equality
import pytest

def test_physics_calculation():
    velocity = calculate_velocity(force=10, mass=2.5, time=3.0)

    # Use pytest.approx for floating point
    assert velocity == pytest.approx(12.0, abs=0.01)

def test_statistical_mean():
    data = [1.1, 2.2, 3.3, 4.4, 5.5]
    mean = calculate_mean(data)

    assert mean == pytest.approx(3.3, rel=0.01)  # Relative tolerance
```

## Performance Patterns

### Test Execution Speed Pattern

**Problem**: Slow tests discourage frequent execution.

**Solution**: Categorize tests by speed and run fast tests more frequently.

```python
# Python - Test categorization with markers
import pytest

@pytest.mark.fast
def test_calculation():
    """Fast unit test - runs in milliseconds."""
    assert add(2, 3) == 5

@pytest.mark.slow
def test_database_query():
    """Slower integration test."""
    db = connect_to_test_database()
    result = db.query("SELECT * FROM users")
    assert len(result) > 0

@pytest.mark.external
def test_api_integration():
    """Very slow - calls external API."""
    response = call_external_api()
    assert response.status_code == 200

# Run only fast tests during development
# $ pytest -m fast

# Run all tests before commit
# $ pytest
```

```java
// Java - Test categorization with tags
@Tag("fast")
@Test
public void testBusinessLogic() {
    // Fast unit test
}

@Tag("slow")
@Test
public void testDatabaseIntegration() {
    // Slower integration test
}

@Tag("external")
@Test
public void testExternalAPI() {
    // Very slow external dependency test
}

// In build configuration:
// ./gradlew test --tests "*fast*"
```

### Parallel Test Execution Pattern

**Problem**: Sequential test execution is slow for large suites.

**Solution**: Design tests to run independently in parallel.

```python
# Python - Parallel execution with pytest-xdist
# Tests must be independent (no shared state)

class TestUserOperations:
    def test_create_user(self):
        """Independent test - safe for parallel execution."""
        repo = InMemoryUserRepository()  # Each test gets own instance
        service = UserService(repo)

        user = service.create_user("test@example.com")
        assert user.email == "test@example.com"

    def test_delete_user(self):
        """Independent test - safe for parallel execution."""
        repo = InMemoryUserRepository()
        service = UserService(repo)

        user = service.create_user("test@example.com")
        service.delete_user(user.id)

        assert service.find_user(user.id) is None

# Run with parallelism:
# $ pytest -n auto  # Auto-detect CPU count
# $ pytest -n 4     # Use 4 workers
```

### Lazy Initialization Pattern

**Problem**: Expensive test setup runs even when not needed.

**Solution**: Initialize expensive resources only when first accessed.

```typescript
// TypeScript - Lazy initialization
class TestDataFactory {
  private _users: User[] | null = null;
  private _products: Product[] | null = null;

  get users(): User[] {
    if (!this._users) {
      this._users = this.createTestUsers();  // Expensive operation
    }
    return this._users;
  }

  get products(): Product[] {
    if (!this._products) {
      this._products = this.loadTestProducts();  // Expensive operation
    }
    return this._products;
  }

  private createTestUsers(): User[] {
    // Heavy computation or I/O
    return [/* ... */];
  }

  private loadTestProducts(): Product[] {
    // Heavy computation or I/O
    return [/* ... */];
  }
}

// Test only pays cost for what it uses
describe('ProductSearch', () => {
  const factory = new TestDataFactory();

  it('finds products by name', () => {
    // Only products are initialized, not users
    const results = search(factory.products, 'widget');
    expect(results.length).toBeGreaterThan(0);
  });
});
```

## Maintainability Patterns

### Page Object Pattern (UI Testing)

**Problem**: UI tests are fragile and duplicate element selectors.

**Solution**: Encapsulate page structure and interactions in Page Objects.

```python
# Python - Page Object for web testing
from selenium.webdriver.common.by import By

class LoginPage:
    """Page Object for login page."""

    def __init__(self, driver):
        self.driver = driver
        self.url = "http://example.com/login"

    # Locators
    EMAIL_INPUT = (By.ID, "email")
    PASSWORD_INPUT = (By.ID, "password")
    SUBMIT_BUTTON = (By.CSS_SELECTOR, "button[type='submit']")
    ERROR_MESSAGE = (By.CLASS_NAME, "error-message")

    def navigate(self):
        """Navigate to login page."""
        self.driver.get(self.url)
        return self

    def enter_email(self, email):
        """Enter email address."""
        element = self.driver.find_element(*self.EMAIL_INPUT)
        element.clear()
        element.send_keys(email)
        return self

    def enter_password(self, password):
        """Enter password."""
        element = self.driver.find_element(*self.PASSWORD_INPUT)
        element.clear()
        element.send_keys(password)
        return self

    def click_submit(self):
        """Click submit button."""
        self.driver.find_element(*self.SUBMIT_BUTTON).click()
        return DashboardPage(self.driver)  # Returns next page

    def get_error_message(self):
        """Get error message text."""
        return self.driver.find_element(*self.ERROR_MESSAGE).text

    def login(self, email, password):
        """Convenience method for complete login."""
        self.enter_email(email)
        self.enter_password(password)
        return self.click_submit()

# Usage in tests
def test_successful_login(driver):
    login_page = LoginPage(driver).navigate()
    dashboard = login_page.login("user@example.com", "password123")

    assert dashboard.is_displayed()

def test_failed_login_shows_error(driver):
    login_page = LoginPage(driver).navigate()
    login_page.login("user@example.com", "wrong-password")

    assert "Invalid credentials" in login_page.get_error_message()
```

**Benefits**:
- Tests are more readable (business language, not selectors)
- Changes to UI require updates in one place
- Page Objects can be reused across tests
- Compile-time checking of page methods (in typed languages)

### Test Smell Detection

Common test smells and their solutions:

#### Smell: Conditional Test Logic

```java
// BAD: Logic in tests
@Test
public void testUserStatus() {
    User user = getUser();
    if (user.isPremium()) {
        assertTrue(user.hasAccessTo("premium-feature"));
    } else {
        assertFalse(user.hasAccessTo("premium-feature"));
    }
}

// GOOD: Separate tests
@Test
public void premiumUserHasAccessToPremiumFeatures() {
    User user = createPremiumUser();
    assertTrue(user.hasAccessTo("premium-feature"));
}

@Test
public void regularUserDoesNotHaveAccessToPremiumFeatures() {
    User user = createRegularUser();
    assertFalse(user.hasAccessTo("premium-feature"));
}
```

#### Smell: Test Code Duplication

```typescript
// BAD: Duplicated setup
test('scenario 1', () => {
  const user = new User('test@example.com');
  user.setName('Test User');
  user.setAge(25);
  const service = new UserService(new InMemoryRepo());
  service.save(user);
  // Test logic...
});

test('scenario 2', () => {
  const user = new User('test@example.com');
  user.setName('Test User');
  user.setAge(25);
  const service = new UserService(new InMemoryRepo());
  service.save(user);
  // Different test logic...
});

// GOOD: Extract common setup
function createTestUser() {
  const user = new User('test@example.com');
  user.setName('Test User');
  user.setAge(25);
  return user;
}

function createUserService() {
  return new UserService(new InMemoryRepo());
}

test('scenario 1', () => {
  const user = createTestUser();
  const service = createUserService();
  service.save(user);
  // Test logic...
});

test('scenario 2', () => {
  const user = createTestUser();
  const service = createUserService();
  service.save(user);
  // Different test logic...
});
```

## Integration with Geist Framework

### Ghost: Unknown Test Scenarios

**Question**: What test patterns am I missing?

```python
# Visible: Testing happy path
def test_user_creation():
    user = create_user("test@example.com")
    assert user.email == "test@example.com"

# Ghost: What about edge cases requiring different patterns?

# Use Parameterized Test Pattern for boundary cases
@pytest.mark.parametrize("email", [
    "",
    " ",
    "not-an-email",
    "missing@",
    "@missing.com"
])
def test_invalid_email_formats(email):
    with pytest.raises(ValidationError):
        create_user(email)

# Use Object Mother Pattern for complex scenarios
def test_admin_permissions():
    admin = UserMother.create_admin()
    regular_user = UserMother.create_regular_user()

    assert admin.can_delete(regular_user)
    assert not regular_user.can_delete(admin)
```

### Geyser: Testing for Growth

**Question**: Will my tests survive system evolution?

Design patterns that accommodate change:
- Use Page Objects (UI changes don't break all tests)
- Use Test Data Builders (object structure changes require minimal test updates)
- Test interfaces, not implementations

### Gist: Essential Testing Patterns

**Question**: Which patterns solve my essential testing problems?

Focus on patterns that address your core challenges:
- Slow tests? → Use Test Double Pattern
- Duplicated setup? → Use Fixture or Object Mother Pattern
- Complex assertions? → Use Custom Assertion Pattern
- Many similar tests? → Use Parameterized Test Pattern

## Practical Pattern Selection Guide

### When to Use Each Pattern

| Pattern | Use When | Benefits |
|---------|----------|----------|
| **Test Data Builder** | Creating complex test objects | Readable, maintainable test setup |
| **Object Mother** | Need common test objects quickly | Centralized, consistent test data |
| **Fixture Setup** | Many tests share initialization | Reduces duplication, ensures clean state |
| **Parameterized Tests** | Same logic, different inputs | Compact, easy to extend |
| **Test Doubles** | Dependencies are slow/unavailable | Fast, isolated tests |
| **Custom Assertions** | Complex verifications | Readable, reusable assertions |
| **Page Objects** | UI testing | Maintainable UI tests |
| **Test Categorization** | Large test suite | Fast feedback loop |

## Further Reading

### Related Guides in This Repository
- **UNIT_TESTING_PRINCIPLES.md** - Clean test fundamentals
- **DEVELOPER_TESTING.md** - Testing strategies
- **TDD_WORKFLOW.md** - Test-driven development
- **01-foundations/FUNCTIONS_AND_ROUTINES.md** - Writing testable code

### External Resources
- **xUnit Test Patterns** by Gerard Meszaros - Comprehensive pattern catalog
- **Growing Object-Oriented Software, Guided by Tests** - Advanced TDD patterns
- **Clean Code** (Chapter 9) - Clean test principles
- **Test-Driven Development: By Example** by Kent Beck - TDD patterns

## Summary

Test design patterns provide proven solutions to common testing challenges. Key patterns:

1. **Creation Patterns**: Test Data Builder, Object Mother
2. **Organization Patterns**: Fixture Setup, Parameterized Tests
3. **Isolation Patterns**: Test Doubles (Stub, Mock, Fake, Spy)
4. **Assertion Patterns**: Custom Assertions, Delta Assertions
5. **Performance Patterns**: Test Categorization, Parallel Execution
6. **Maintainability Patterns**: Page Objects, Smell Detection

Well-designed test suites using these patterns provide:
- Faster feedback cycles
- Easier maintenance
- Clear intent and documentation
- Resilience to change
- Confidence in refactoring

**Remember**: Patterns are tools, not rules. Apply them where they solve real problems in your test suite. Start simple and introduce patterns as complexity demands.
