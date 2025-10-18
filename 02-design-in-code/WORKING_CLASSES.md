# Working Classes: Practical Class Construction Techniques

## Overview

Working classes are the practical implementation of class design principles. While class design theory provides the foundation, this guide focuses on the day-to-day techniques for constructing high-quality classes: choosing good interfaces, managing state, handling construction and destruction, designing for testability, and creating maintainable class hierarchies.

This guide is your practical handbook for writing production-quality classes that are robust, testable, and maintainable.

**"Make it work, make it right, make it fast—in that order."** — Kent Beck

## Why Practical Class Construction Matters

### The Reality of Production Code

Theoretical class design is necessary but not sufficient. Production code faces realities that theory doesn't address:

**Concurrency**: Multiple threads accessing the same object simultaneously.

**Resource Management**: Objects that own database connections, file handles, network sockets.

**Serialization**: Objects that must be persisted or transmitted over networks.

**Testability**: Objects that must be tested in isolation.

**Performance**: Objects created millions of times need efficient construction.

**Backward Compatibility**: Existing classes that can't be changed without breaking clients.

### The Cost of Poor Class Construction

Poorly constructed classes create problems:

**Fragility**: Objects in inconsistent states cause mysterious bugs.

**Resource Leaks**: Unreleased resources crash systems under load.

**Difficult Testing**: Tightly coupled classes can't be tested in isolation.

**Poor Performance**: Inefficient constructors slow down the entire system.

**Maintenance Nightmares**: Complex initialization makes changes risky.

## Source Materials

This guide synthesizes principles from:

- **Code Complete 2** by Steve McConnell (Chapter 6: "Working Classes")
  - Constructors and initialization
  - Deep vs shallow copy
  - Immutability
  - Persistent data
  - Abstract data types (ADTs)

## Constructors: Getting Objects Started Right

### The Ideal Constructor

A good constructor:
1. Initializes all instance variables
2. Establishes class invariants
3. Never fails (or fails fast with clear errors)
4. Does minimal work
5. Never calls overridable methods

### Initialize All Data Members

**Anti-Pattern: Partial Initialization**
```python
# BAD: Not all data initialized
class CreditCardProcessor:
    def __init__(self, merchant_id):
        self.merchant_id = merchant_id
        # Missing: gateway, logger, retry_policy

    def process_payment(self, card, amount):
        # NullReferenceError: gateway not initialized!
        return self.gateway.charge(card, amount)
```

**Good Pattern: Complete Initialization**
```python
# GOOD: All data initialized
class CreditCardProcessor:
    def __init__(
        self,
        merchant_id: str,
        gateway: PaymentGateway,
        logger: Logger,
        retry_policy: RetryPolicy = None
    ):
        # All required data initialized
        self.merchant_id = merchant_id
        self.gateway = gateway
        self.logger = logger

        # Optional data has sensible default
        self.retry_policy = retry_policy or DefaultRetryPolicy()

        # All instance variables initialized - object is in valid state

    def process_payment(self, card: CreditCard, amount: Money) -> PaymentResult:
        # Safe to use all instance variables
        return self.gateway.charge(card, amount)
```

### Establish Class Invariants

**Invariant**: Condition that must always be true for the object.

```java
// Establish invariants in constructor
public class DateRange {
    private final LocalDate startDate;
    private final LocalDate endDate;

    public DateRange(LocalDate startDate, LocalDate endDate) {
        // Invariant: Start must be before or equal to end
        if (startDate.isAfter(endDate)) {
            throw new IllegalArgumentException(
                "Start date must be before or equal to end date"
            );
        }

        this.startDate = startDate;
        this.endDate = endDate;

        // Invariant established - object is in valid state
    }

    public int getDayCount() {
        // Safe to assume startDate <= endDate
        return (int) ChronoUnit.DAYS.between(startDate, endDate) + 1;
    }

    public boolean contains(LocalDate date) {
        // Safe to assume startDate <= endDate
        return !date.isBefore(startDate) && !date.isAfter(endDate);
    }
}

// Client cannot create invalid DateRange
DateRange range = new DateRange(
    LocalDate.of(2024, 1, 1),
    LocalDate.of(2023, 12, 31)  // ERROR: Will throw exception
);
```

### Constructor Overloading

**Pattern**: Provide multiple ways to construct objects, delegate to most complete constructor.

```typescript
// Constructor overloading pattern
class EmailMessage {
    private to: string;
    private from: string;
    private subject: string;
    private body: string;
    private cc: string[];
    private bcc: string[];
    private attachments: Attachment[];

    // Most complete constructor - all parameters
    constructor(
        to: string,
        from: string,
        subject: string,
        body: string,
        cc: string[] = [],
        bcc: string[] = [],
        attachments: Attachment[] = []
    ) {
        this.to = to;
        this.from = from;
        this.subject = subject;
        this.body = body;
        this.cc = cc;
        this.bcc = bcc;
        this.attachments = attachments;
    }

    // Convenience: Simple email
    static createSimple(to: string, from: string, subject: string, body: string): EmailMessage {
        return new EmailMessage(to, from, subject, body);
    }

    // Convenience: Email with CC
    static createWithCC(
        to: string,
        from: string,
        subject: string,
        body: string,
        cc: string[]
    ): EmailMessage {
        return new EmailMessage(to, from, subject, body, cc);
    }

    // Convenience: Email with attachments
    static createWithAttachments(
        to: string,
        from: string,
        subject: string,
        body: string,
        attachments: Attachment[]
    ): EmailMessage {
        return new EmailMessage(to, from, subject, body, [], [], attachments);
    }
}

// Usage: Choose appropriate constructor
const simple = EmailMessage.createSimple(
    "user@example.com",
    "noreply@company.com",
    "Welcome",
    "Thank you for signing up"
);

const withCC = EmailMessage.createWithCC(
    "user@example.com",
    "sales@company.com",
    "Order Confirmation",
    "Your order has been placed",
    ["manager@company.com"]
);
```

### Prefer Static Factory Methods

**Advantages**:
1. Descriptive names (unlike constructors)
2. Can return existing instances (caching)
3. Can return subtype
4. Can do validation before construction

```python
# Static factory methods for clarity
class Money:
    def __init__(self, amount: Decimal, currency: str):
        self._amount = amount
        self._currency = currency

    @classmethod
    def dollars(cls, amount: float) -> 'Money':
        """Create Money in US dollars."""
        return cls(Decimal(str(amount)), 'USD')

    @classmethod
    def euros(cls, amount: float) -> 'Money':
        """Create Money in euros."""
        return cls(Decimal(str(amount)), 'EUR')

    @classmethod
    def zero(cls, currency: str = 'USD') -> 'Money':
        """Create zero money."""
        return cls(Decimal('0'), currency)

    @classmethod
    def from_string(cls, value: str) -> 'Money':
        """Create Money from string like '$100.00' or '€50.00'."""
        if value.startswith('$'):
            return cls.dollars(float(value[1:]))
        elif value.startswith('€'):
            return cls.euros(float(value[1:]))
        else:
            raise ValueError(f"Unknown currency in: {value}")

# Usage: Clear, descriptive creation
price = Money.dollars(99.99)
zero = Money.zero()
parsed = Money.from_string("$150.00")

# Much clearer than: Money(Decimal('99.99'), 'USD')
```

### Avoid Doing Real Work in Constructors

**Problem**: Constructors that do too much are hard to test and slow.

```java
// BAD: Constructor does too much work
public class CustomerReport {
    private List<Customer> customers;
    private Map<String, Statistics> statistics;

    public CustomerReport() {
        // BAD: Database query in constructor!
        this.customers = Database.query("SELECT * FROM customers");

        // BAD: Expensive calculation in constructor!
        this.statistics = new HashMap<>();
        for (Customer customer : customers) {
            statistics.put(
                customer.getId(),
                calculateCustomerStatistics(customer)  // Expensive!
            );
        }

        // Problems:
        // 1. Can't create CustomerReport without hitting database
        // 2. Can't create CustomerReport without expensive calculations
        // 3. Hard to test
        // 4. Slow
    }
}

// GOOD: Defer work until needed
public class CustomerReport {
    private final CustomerRepository repository;
    private List<Customer> customers;
    private Map<String, Statistics> statistics;

    public CustomerReport(CustomerRepository repository) {
        // Just store dependency - no work done
        this.repository = repository;
    }

    public List<Customer> getCustomers() {
        // Lazy loading - work done only when needed
        if (customers == null) {
            customers = repository.findAll();
        }
        return customers;
    }

    public Statistics getStatisticsForCustomer(String customerId) {
        // Lazy calculation - only when needed, only for requested customer
        if (!statistics.containsKey(customerId)) {
            Customer customer = repository.findById(customerId);
            statistics.put(customerId, calculateCustomerStatistics(customer));
        }
        return statistics.get(customerId);
    }

    // Benefits:
    // 1. Fast construction
    // 2. Can inject mock repository for testing
    // 3. Work done only when needed
    // 4. Can control when database is accessed
}
```

## Immutability: Objects That Never Change

### Benefits of Immutable Classes

Immutable objects:
1. **Thread-safe** by default (no synchronization needed)
2. **Simpler** to reason about (no state changes)
3. **Safe to share** (no defensive copying needed)
4. **Good hash keys** (hash code never changes)
5. **Prevent bugs** (can't be put in inconsistent state)

### Creating Immutable Classes

**Recipe for Immutability**:
1. Make all fields final
2. Don't provide setters
3. Make the class final (prevent subclassing)
4. Initialize all fields in constructor
5. Don't share references to mutable objects

```java
// Immutable class example
public final class Money {  // final = can't be subclassed
    private final BigDecimal amount;  // final = can't be reassigned
    private final String currency;    // final = can't be reassigned

    public Money(BigDecimal amount, String currency) {
        // Validate and initialize in constructor
        if (amount == null) {
            throw new IllegalArgumentException("Amount cannot be null");
        }
        if (currency == null || currency.isEmpty()) {
            throw new IllegalArgumentException("Currency cannot be null or empty");
        }

        this.amount = amount;
        this.currency = currency;
    }

    // Getters only - no setters
    public BigDecimal getAmount() {
        return amount;
    }

    public String getCurrency() {
        return currency;
    }

    // Operations return new instances
    public Money add(Money other) {
        if (!this.currency.equals(other.currency)) {
            throw new IllegalArgumentException("Cannot add different currencies");
        }
        return new Money(this.amount.add(other.amount), this.currency);
    }

    public Money multiply(double multiplier) {
        return new Money(
            this.amount.multiply(BigDecimal.valueOf(multiplier)),
            this.currency
        );
    }

    // Safe to use as hash key
    @Override
    public int hashCode() {
        return Objects.hash(amount, currency);
    }

    @Override
    public boolean equals(Object obj) {
        if (this == obj) return true;
        if (!(obj instanceof Money)) return false;
        Money other = (Money) obj;
        return amount.equals(other.amount) && currency.equals(other.currency);
    }

    // Immutable objects are thread-safe
    // No synchronization needed
}

// Usage
Money price = new Money(new BigDecimal("99.99"), "USD");
Money doubled = price.multiply(2);  // Creates new Money, doesn't modify original

// Safe to share across threads
Money shared = new Money(new BigDecimal("100.00"), "USD");
thread1.use(shared);  // Safe
thread2.use(shared);  // Safe - can't be modified
```

### Immutable Collections

```python
# Immutable collection wrapper
class ImmutableList:
    """Wrapper that prevents modification of list."""

    def __init__(self, items: List):
        # Store defensive copy
        self._items = tuple(items)  # Tuple is immutable

    def __getitem__(self, index):
        return self._items[index]

    def __len__(self):
        return len(self._items)

    def __iter__(self):
        return iter(self._items)

    # No methods that modify!
    # No append, remove, clear, etc.

    def __repr__(self):
        return f"ImmutableList({list(self._items)})"

# Usage
items = ImmutableList([1, 2, 3])
print(items[0])  # 1
print(len(items))  # 3
for item in items:  # Works
    print(item)

# items.append(4)  # AttributeError - no append method
# items[0] = 10     # TypeError - can't modify tuple
```

### When to Use Immutability

**Always Immutable**:
- Value objects (Money, Date, Coordinate)
- Configuration objects
- Dictionary keys
- Objects shared across threads

**Sometimes Mutable**:
- Builder objects (building immutable objects)
- Entities with identity (User, Order)
- Performance-critical objects (avoid excessive copying)

## Deep Copy vs. Shallow Copy

### Understanding Copy Depth

**Shallow Copy**: Copies references, not objects.
**Deep Copy**: Recursively copies all objects.

```typescript
// Shallow vs Deep copy
class Address {
    constructor(
        public street: string,
        public city: string,
        public zipCode: string
    ) {}

    clone(): Address {
        return new Address(this.street, this.city, this.zipCode);
    }
}

class Customer {
    constructor(
        public name: string,
        public address: Address
    ) {}

    // Shallow copy - shares address reference
    shallowCopy(): Customer {
        return new Customer(this.name, this.address);
    }

    // Deep copy - clones address
    deepCopy(): Customer {
        return new Customer(this.name, this.address.clone());
    }
}

// Demonstrate difference
const original = new Customer(
    "John Doe",
    new Address("123 Main St", "Springfield", "12345")
);

const shallow = original.shallowCopy();
const deep = original.deepCopy();

// Modify original address
original.address.street = "456 Oak Ave";

console.log(shallow.address.street);  // "456 Oak Ave" - shares reference!
console.log(deep.address.street);     // "123 Main St" - independent copy
```

### When to Use Each

**Shallow Copy**:
- Objects contain only primitive values
- References to shared immutable objects
- Performance is critical

**Deep Copy**:
- Objects contain mutable objects
- Need independent copy
- Serialization/deserialization

### Implementing Deep Copy

```python
# Deep copy implementation
class Order:
    def __init__(self, order_id: str, customer: Customer, items: List[OrderItem]):
        self.order_id = order_id
        self.customer = customer
        self.items = items

    def deep_copy(self) -> 'Order':
        """Create deep copy of order."""
        # Copy primitive
        new_id = self.order_id

        # Deep copy customer
        new_customer = self.customer.deep_copy()

        # Deep copy items list and each item
        new_items = [item.deep_copy() for item in self.items]

        return Order(new_id, new_customer, new_items)

class Customer:
    def __init__(self, name: str, email: str):
        self.name = name
        self.email = email

    def deep_copy(self) -> 'Customer':
        return Customer(self.name, self.email)  # Strings are immutable

class OrderItem:
    def __init__(self, product_id: str, quantity: int, price: Money):
        self.product_id = product_id
        self.quantity = quantity
        self.price = price

    def deep_copy(self) -> 'OrderItem':
        # Money is immutable, safe to share
        return OrderItem(self.product_id, self.quantity, self.price)

# Usage
original_order = Order(
    "ORD-001",
    Customer("John Doe", "john@example.com"),
    [OrderItem("PROD-1", 2, Money.dollars(50.00))]
)

copied_order = original_order.deep_copy()

# Modify original
original_order.customer.name = "Jane Doe"
original_order.items[0].quantity = 5

# Copy is unaffected
print(copied_order.customer.name)  # "John Doe"
print(copied_order.items[0].quantity)  # 2
```

## Abstract Data Types (ADTs)

### What is an ADT?

An Abstract Data Type is a collection of data and operations that work on that data, with implementation details hidden.

**Key Characteristics**:
1. **Interface**: Public operations that define what the ADT does
2. **Implementation**: Private data and algorithms that define how it does it
3. **Abstraction**: Clients use the ADT without knowing implementation

### Classic ADT Example: Stack

```java
// Stack ADT - interface defines what, implementation defines how
public interface Stack<T> {
    // Public interface - what a stack does
    void push(T item);
    T pop();
    T peek();
    boolean isEmpty();
    int size();
}

// Implementation 1: Array-based
public class ArrayStack<T> implements Stack<T> {
    private Object[] elements;
    private int size;
    private static final int DEFAULT_CAPACITY = 16;

    public ArrayStack() {
        elements = new Object[DEFAULT_CAPACITY];
        size = 0;
    }

    @Override
    public void push(T item) {
        ensureCapacity();
        elements[size++] = item;
    }

    @Override
    @SuppressWarnings("unchecked")
    public T pop() {
        if (isEmpty()) {
            throw new EmptyStackException();
        }
        T item = (T) elements[--size];
        elements[size] = null;  // Prevent memory leak
        return item;
    }

    @Override
    @SuppressWarnings("unchecked")
    public T peek() {
        if (isEmpty()) {
            throw new EmptyStackException();
        }
        return (T) elements[size - 1];
    }

    @Override
    public boolean isEmpty() {
        return size == 0;
    }

    @Override
    public int size() {
        return size;
    }

    private void ensureCapacity() {
        if (size == elements.length) {
            elements = Arrays.copyOf(elements, size * 2);
        }
    }
}

// Implementation 2: Linked-list-based
public class LinkedStack<T> implements Stack<T> {
    private static class Node<T> {
        T data;
        Node<T> next;

        Node(T data, Node<T> next) {
            this.data = data;
            this.next = next;
        }
    }

    private Node<T> top;
    private int size;

    public LinkedStack() {
        top = null;
        size = 0;
    }

    @Override
    public void push(T item) {
        top = new Node<>(item, top);
        size++;
    }

    @Override
    public T pop() {
        if (isEmpty()) {
            throw new EmptyStackException();
        }
        T item = top.data;
        top = top.next;
        size--;
        return item;
    }

    @Override
    public T peek() {
        if (isEmpty()) {
            throw new EmptyStackException();
        }
        return top.data;
    }

    @Override
    public boolean isEmpty() {
        return top == null;
    }

    @Override
    public int size() {
        return size;
    }
}

// Client code works with either implementation
public class StackUser {
    private Stack<String> stack;

    public StackUser(Stack<String> stack) {
        this.stack = stack;  // Don't know or care which implementation
    }

    public void process() {
        stack.push("First");
        stack.push("Second");
        String item = stack.pop();  // "Second"
        // Works identically with ArrayStack or LinkedStack
    }
}
```

### Custom ADT Example: Money

```python
# Money ADT - proper representation of monetary values
class Money:
    """Abstract Data Type for monetary values."""

    def __init__(self, amount: Decimal, currency: str):
        """Private constructor - use factory methods instead."""
        if not isinstance(amount, Decimal):
            raise TypeError("Amount must be Decimal")
        if currency not in ['USD', 'EUR', 'GBP', 'JPY']:
            raise ValueError(f"Unsupported currency: {currency}")

        self._amount = amount
        self._currency = currency

    # Public interface - what Money can do

    @classmethod
    def dollars(cls, amount: float) -> 'Money':
        """Create Money in US dollars."""
        return cls(Decimal(str(amount)), 'USD')

    @classmethod
    def euros(cls, amount: float) -> 'Money':
        """Create Money in euros."""
        return cls(Decimal(str(amount)), 'EUR')

    def add(self, other: 'Money') -> 'Money':
        """Add two Money values (must be same currency)."""
        if self._currency != other._currency:
            raise ValueError("Cannot add different currencies")
        return Money(self._amount + other._amount, self._currency)

    def subtract(self, other: 'Money') -> 'Money':
        """Subtract money values."""
        if self._currency != other._currency:
            raise ValueError("Cannot subtract different currencies")
        return Money(self._amount - other._amount, self._currency)

    def multiply(self, multiplier: float) -> 'Money':
        """Multiply money by scalar."""
        return Money(
            self._amount * Decimal(str(multiplier)),
            self._currency
        )

    def divide(self, divisor: float) -> 'Money':
        """Divide money by scalar."""
        return Money(
            self._amount / Decimal(str(divisor)),
            self._currency
        )

    def is_positive(self) -> bool:
        """Check if amount is positive."""
        return self._amount > 0

    def is_zero(self) -> bool:
        """Check if amount is zero."""
        return self._amount == 0

    def format(self) -> str:
        """Format for display."""
        symbols = {'USD': '$', 'EUR': '€', 'GBP': '£', 'JPY': '¥'}
        symbol = symbols[self._currency]
        return f"{symbol}{self._amount:.2f}"

    # Implementation details hidden from clients

    def __eq__(self, other) -> bool:
        if not isinstance(other, Money):
            return False
        return self._amount == other._amount and self._currency == other._currency

    def __lt__(self, other: 'Money') -> bool:
        if self._currency != other._currency:
            raise ValueError("Cannot compare different currencies")
        return self._amount < other._amount

    def __repr__(self) -> str:
        return f"Money({self._amount}, {self._currency})"

# Usage - clients don't know implementation
price = Money.dollars(99.99)
tax = Money.dollars(8.00)
total = price.add(tax)  # Money(107.99, USD)

discounted = total.multiply(0.9)  # 10% off
print(discounted.format())  # $97.19

# Implementation could change to store cents as integer
# Clients wouldn't need to change
```

## Designing for Testability

### Dependency Injection

**Problem**: Hard-coded dependencies make testing difficult.

```typescript
// BAD: Hard to test
class OrderService {
    // Hard-coded dependencies
    private repository = new DatabaseOrderRepository();
    private emailer = new SmtpEmailSender();
    private logger = new FileLogger('/var/log/orders.log');

    processOrder(order: Order): void {
        // Can't test without real database, email server, file system
        this.repository.save(order);
        this.emailer.sendConfirmation(order);
        this.logger.log(`Order processed: ${order.id}`);
    }
}

// GOOD: Dependencies injected, easy to test
class OrderService {
    constructor(
        private repository: OrderRepository,
        private emailer: EmailSender,
        private logger: Logger
    ) {
        // Dependencies injected - can use mocks for testing
    }

    processOrder(order: Order): void {
        this.repository.save(order);
        this.emailer.sendConfirmation(order);
        this.logger.log(`Order processed: ${order.id}`);
    }
}

// Testing with mocks
class MockOrderRepository implements OrderRepository {
    orders: Order[] = [];

    save(order: Order): void {
        this.orders.push(order);
    }
}

class MockEmailSender implements EmailSender {
    sentEmails: Order[] = [];

    sendConfirmation(order: Order): void {
        this.sentEmails.push(order);
    }
}

class MockLogger implements Logger {
    logs: string[] = [];

    log(message: string): void {
        this.logs.push(message);
    }
}

// Test is now easy
function testOrderService(): void {
    const mockRepo = new MockOrderRepository();
    const mockEmailer = new MockEmailSender();
    const mockLogger = new MockLogger();

    const service = new OrderService(mockRepo, mockEmailer, mockLogger);

    const order = new Order("ORD-123");
    service.processOrder(order);

    // Easy to verify behavior
    assert(mockRepo.orders.length === 1);
    assert(mockEmailer.sentEmails.length === 1);
    assert(mockLogger.logs[0].includes("ORD-123"));
}
```

### Avoid Static Dependencies

```java
// BAD: Static dependencies can't be mocked
public class UserService {
    public void createUser(User user) {
        // Static method - can't be mocked
        Database.save(user);

        // Static method - can't be mocked
        EmailSender.send(user.getEmail(), "Welcome!");

        // Hard to test
    }
}

// GOOD: Instance dependencies can be mocked
public class UserService {
    private final UserRepository repository;
    private final EmailService emailService;

    public UserService(UserRepository repository, EmailService emailService) {
        this.repository = repository;
        this.emailService = emailService;
    }

    public void createUser(User user) {
        repository.save(user);
        emailService.sendWelcome(user.getEmail());
        // Easy to test with mock repository and email service
    }
}
```

### Extract Interfaces for Testing

```python
# Extract interfaces to enable mocking
from abc import ABC, abstractmethod

class PaymentGateway(ABC):
    """Interface for payment processing."""

    @abstractmethod
    def charge(self, card: CreditCard, amount: Money) -> PaymentResult:
        """Charge credit card."""
        pass

class StripePaymentGateway(PaymentGateway):
    """Real Stripe implementation."""

    def charge(self, card: CreditCard, amount: Money) -> PaymentResult:
        # Real Stripe API call
        response = stripe.Charge.create(
            amount=int(amount.get_amount() * 100),
            currency=amount.get_currency().lower(),
            source=card.get_token()
        )
        return PaymentResult.success(response.id)

class MockPaymentGateway(PaymentGateway):
    """Mock for testing."""

    def __init__(self):
        self.charged_amounts = []

    def charge(self, card: CreditCard, amount: Money) -> PaymentResult:
        # Simulate successful charge
        self.charged_amounts.append(amount)
        return PaymentResult.success("mock-transaction-id")

class OrderService:
    def __init__(self, payment_gateway: PaymentGateway):
        self.payment_gateway = payment_gateway

    def process_order(self, order: Order) -> OrderResult:
        result = self.payment_gateway.charge(order.payment_method, order.total)
        # Rest of order processing
        return OrderResult.success()

# Testing
def test_order_service():
    mock_gateway = MockPaymentGateway()
    service = OrderService(mock_gateway)

    order = Order(total=Money.dollars(100.00))
    service.process_order(order)

    # Easy to verify
    assert len(mock_gateway.charged_amounts) == 1
    assert mock_gateway.charged_amounts[0] == Money.dollars(100.00)

# Production
production_gateway = StripePaymentGateway()
production_service = OrderService(production_gateway)
```

## Resource Management

### RAII Pattern (Resource Acquisition Is Initialization)

**Principle**: Acquire resources in constructor, release in destructor/finalizer.

```java
// RAII pattern for database connection
public class DatabaseConnection implements AutoCloseable {
    private final Connection connection;

    public DatabaseConnection(String url) throws SQLException {
        // Acquire resource in constructor
        this.connection = DriverManager.getConnection(url);
    }

    public ResultSet executeQuery(String sql) throws SQLException {
        return connection.createStatement().executeQuery(sql);
    }

    @Override
    public void close() {
        // Release resource in close method
        try {
            if (connection != null && !connection.isClosed()) {
                connection.close();
            }
        } catch (SQLException e) {
            // Log error but don't throw from close
            logger.error("Error closing connection", e);
        }
    }
}

// Usage with try-with-resources (automatic cleanup)
try (DatabaseConnection db = new DatabaseConnection("jdbc:...")) {
    ResultSet results = db.executeQuery("SELECT * FROM users");
    // Process results
} // Connection automatically closed here, even if exception thrown
```

### Python Context Managers

```python
# Context manager for resource management
class FileProcessor:
    """Process file with automatic cleanup."""

    def __init__(self, filename: str):
        self.filename = filename
        self.file = None

    def __enter__(self):
        """Acquire resource."""
        self.file = open(self.filename, 'r')
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Release resource."""
        if self.file:
            self.file.close()
        return False  # Don't suppress exceptions

    def process(self):
        """Process file contents."""
        return self.file.read()

# Usage with 'with' statement (automatic cleanup)
with FileProcessor('data.txt') as processor:
    data = processor.process()
    # Process data
# File automatically closed here, even if exception thrown
```

## Practical Class Checklist

Use this checklist when implementing classes:

### Construction Phase
- [ ] All instance variables initialized in constructor
- [ ] Class invariants established and validated
- [ ] Constructor does minimal work (no I/O, heavy computation)
- [ ] Static factory methods provided for complex construction
- [ ] Constructor never calls overridable methods

### Interface Design Phase
- [ ] Public interface is minimal and cohesive
- [ ] Methods have clear, single responsibilities
- [ ] No implementation details leak through interface
- [ ] Defensive copies protect mutable state
- [ ] Methods validate inputs at boundaries

### Immutability Phase
- [ ] Value objects are immutable (Money, Date, etc.)
- [ ] Immutable classes are final and have final fields
- [ ] Operations return new instances rather than modifying
- [ ] Mutable objects only when performance critical

### Testability Phase
- [ ] Dependencies injected, not hard-coded
- [ ] Interfaces extracted for all collaborators
- [ ] No static dependencies (or abstracted behind interfaces)
- [ ] Class can be tested in isolation with mocks
- [ ] Test fixtures are easy to create

### Resource Management Phase
- [ ] Resources acquired in constructor or method entry
- [ ] Resources released in close/cleanup method
- [ ] Implements AutoCloseable (Java) or context manager (Python)
- [ ] Cleanup happens even if exceptions thrown
- [ ] No resource leaks in error paths

## Common Class Anti-Patterns

### Anti-Pattern 1: God Object
**Problem**: One class does everything.

**Solution**: Apply Single Responsibility Principle, extract classes.

### Anti-Pattern 2: Anemic Domain Model
**Problem**: Classes with only getters/setters, no behavior.

**Solution**: Move behavior into domain classes where it belongs.

### Anti-Pattern 3: Feature Envy
**Problem**: Class uses methods of another class more than its own.

**Solution**: Move the method to the class it's envious of.

### Anti-Pattern 4: Inappropriate Intimacy
**Problem**: Classes know too much about each other's internals.

**Solution**: Reduce coupling, use interfaces, hide implementation.

### Anti-Pattern 5: Lazy Class
**Problem**: Class doesn't do enough to justify its existence.

**Solution**: Merge with another class or eliminate.

## Summary: Working Class Principles

1. **Complete Initialization**: Initialize all data in constructor
2. **Establish Invariants**: Ensure valid state from construction
3. **Immutable When Possible**: Default to immutable, mutable only when needed
4. **Hide Implementation**: Expose minimal interface
5. **Dependency Injection**: Dependencies passed in, not created
6. **Resource Management**: Acquire in constructor, release in cleanup
7. **Design for Testing**: Interfaces, injection, minimal static dependencies
8. **Defensive Copying**: Protect internal state
9. **Clear Abstractions**: ADTs hide implementation behind interface
10. **Fail Fast**: Detect errors early, report clearly

## Further Reading

- **Code Complete 2** (Chapter 6: Working Classes) - Steve McConnell
- **Effective Java** (Items on Classes and Constructors) - Joshua Bloch
- **Clean Code** (Chapter 10: Classes) - Robert C. Martin
- **Growing Object-Oriented Software, Guided by Tests** - Freeman & Pryce
- **Working Effectively with Legacy Code** - Michael Feathers

---

**Remember**: Working classes are the backbone of maintainable systems. Every class you write should be fully initialized, protect its invariants, hide its implementation, manage resources properly, and be easy to test. These practices transform theoretical class design into production-ready code that's robust, reliable, and maintainable.
