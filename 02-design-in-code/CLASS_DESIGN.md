# Class Design: Creating High-Quality Classes

## Overview

Classes are the fundamental building blocks of object-oriented systems. A well-designed class represents a coherent concept with a clear responsibility, clean interfaces, and appropriate encapsulation. Poor class design leads to rigid, fragile code that's difficult to understand, test, and maintain.

This guide provides comprehensive principles for designing classes that are small, focused, cohesive, loosely coupled, and adaptable to change. These principles apply whether you're working in Java, Python, TypeScript, or any other object-oriented language.

**"The first rule of classes is that they should be small. The second rule of classes is that they should be smaller than that."** — Robert C. Martin, Clean Code

## Why Class Design Matters

### The Cost of Poor Class Design

Poorly designed classes create cascading problems:

**Complexity Explosion**: Large classes with many responsibilities require developers to understand too much at once. Cognitive overload leads to errors.

**Fragility**: Changes to one responsibility break unrelated functionality. A bug fix in the billing logic accidentally breaks the reporting feature.

**Rigidity**: The class resists change because everything is tangled together. Simple feature requests require massive refactoring.

**Immobility**: The class can't be reused because it's coupled to too many other classes. Copy-paste becomes easier than reuse.

**Viscosity**: Doing things the right way is harder than doing them the wrong way. Developers add hacks rather than proper solutions.

### The Benefits of Well-Designed Classes

Well-designed classes provide:
- **Comprehensibility**: Each class has a clear, single purpose that's easy to understand
- **Testability**: Small, focused classes are trivial to test in isolation
- **Reusability**: Classes with minimal coupling can be used in multiple contexts
- **Maintainability**: Changes are localized to one class, not scattered across many
- **Flexibility**: New requirements are accommodated by adding classes, not modifying existing ones
- **Reliability**: Fewer responsibilities mean fewer bugs

## Source Materials

This guide synthesizes principles from:

- **Code Complete 2** by Steve McConnell (Chapter 6: "Working Classes")
  - Abstract Data Types (ADTs)
  - Good class interfaces
  - Reasons to create a class
  - Inheritance and composition

- **Clean Code** by Robert C. Martin (Chapter 10: "Classes")
  - Class organization
  - Class size and cohesion
  - Single Responsibility Principle
  - Open-Closed Principle

## Class Organization

### Standard Class Organization Pattern

Classes should follow a consistent organization that makes them easy to navigate:

```java
// Standard Java class organization
public class Order {
    // 1. Constants (public static final)
    public static final int MAX_ITEMS = 100;
    private static final double TAX_RATE = 0.08;

    // 2. Static variables
    private static int orderCounter = 0;

    // 3. Instance variables (private)
    private final String orderId;
    private final Customer customer;
    private final List<OrderItem> items;
    private OrderStatus status;
    private Money total;

    // 4. Constructors
    public Order(Customer customer) {
        this.orderId = generateOrderId();
        this.customer = customer;
        this.items = new ArrayList<>();
        this.status = OrderStatus.PENDING;
        this.total = Money.zero();
    }

    // 5. Public methods (most important first)
    public void addItem(OrderItem item) {
        validateCanModifyOrder();
        validateItemLimit();
        items.add(item);
        recalculateTotal();
    }

    public void removeItem(OrderItem item) {
        validateCanModifyOrder();
        items.remove(item);
        recalculateTotal();
    }

    public Money getTotal() {
        return total;
    }

    // 6. Private methods (called by public methods)
    private void validateCanModifyOrder() {
        if (status == OrderStatus.SHIPPED || status == OrderStatus.CANCELLED) {
            throw new IllegalStateException("Cannot modify " + status + " order");
        }
    }

    private void validateItemLimit() {
        if (items.size() >= MAX_ITEMS) {
            throw new IllegalStateException("Order cannot exceed " + MAX_ITEMS + " items");
        }
    }

    private void recalculateTotal() {
        Money subtotal = items.stream()
            .map(OrderItem::getPrice)
            .reduce(Money.zero(), Money::add);

        Money tax = subtotal.multiply(TAX_RATE);
        this.total = subtotal.add(tax);
    }

    private static String generateOrderId() {
        return "ORD-" + String.format("%06d", ++orderCounter);
    }

    // 7. Getters and setters (if needed)
    public String getOrderId() {
        return orderId;
    }

    public OrderStatus getStatus() {
        return status;
    }

    public List<OrderItem> getItems() {
        return new ArrayList<>(items);  // Defensive copy
    }
}
```

**Organization Principles**:
1. **Public before private**: Readers see the interface before implementation
2. **High-level before low-level**: Important abstractions come first
3. **Caller before callee**: Methods appear before the methods they call
4. **Stepdown rule**: Read code top to bottom like a narrative

### Python Class Organization

```python
class Order:
    """Represents a customer order."""

    # 1. Class constants
    MAX_ITEMS = 100
    _TAX_RATE = 0.08

    # 2. Class variables
    _order_counter = 0

    def __init__(self, customer: Customer):
        """Initialize new order for customer."""
        # 3. Instance variables
        self._order_id = self._generate_order_id()
        self._customer = customer
        self._items: List[OrderItem] = []
        self._status = OrderStatus.PENDING
        self._total = Money.zero()

    # 4. Public methods (most important first)
    def add_item(self, item: OrderItem) -> None:
        """Add item to order."""
        self._validate_can_modify_order()
        self._validate_item_limit()
        self._items.append(item)
        self._recalculate_total()

    def remove_item(self, item: OrderItem) -> None:
        """Remove item from order."""
        self._validate_can_modify_order()
        self._items.remove(item)
        self._recalculate_total()

    # 5. Properties (Python's answer to getters)
    @property
    def order_id(self) -> str:
        """Get order identifier."""
        return self._order_id

    @property
    def total(self) -> Money:
        """Get order total."""
        return self._total

    @property
    def items(self) -> List[OrderItem]:
        """Get copy of order items."""
        return self._items.copy()  # Defensive copy

    # 6. Private methods (underscore prefix)
    def _validate_can_modify_order(self) -> None:
        """Ensure order can be modified."""
        if self._status in (OrderStatus.SHIPPED, OrderStatus.CANCELLED):
            raise IllegalStateError(f"Cannot modify {self._status} order")

    def _validate_item_limit(self) -> None:
        """Ensure order hasn't exceeded item limit."""
        if len(self._items) >= self.MAX_ITEMS:
            raise IllegalStateError(f"Order cannot exceed {self.MAX_ITEMS} items")

    def _recalculate_total(self) -> None:
        """Recalculate order total with tax."""
        subtotal = sum(item.price for item in self._items, Money.zero())
        tax = subtotal * self._TAX_RATE
        self._total = subtotal + tax

    @classmethod
    def _generate_order_id(cls) -> str:
        """Generate unique order ID."""
        cls._order_counter += 1
        return f"ORD-{cls._order_counter:06d}"

    # 7. Special methods (dunder methods) at end
    def __repr__(self) -> str:
        return f"Order({self._order_id}, items={len(self._items)}, total={self._total})"

    def __eq__(self, other) -> bool:
        if not isinstance(other, Order):
            return False
        return self._order_id == other._order_id
```

### TypeScript Class Organization

```typescript
class Order {
    // 1. Constants
    public static readonly MAX_ITEMS = 100;
    private static readonly TAX_RATE = 0.08;

    // 2. Static variables
    private static orderCounter = 0;

    // 3. Instance variables (private by default)
    private readonly orderId: string;
    private readonly customer: Customer;
    private readonly items: OrderItem[];
    private status: OrderStatus;
    private total: Money;

    // 4. Constructor
    constructor(customer: Customer) {
        this.orderId = Order.generateOrderId();
        this.customer = customer;
        this.items = [];
        this.status = OrderStatus.PENDING;
        this.total = Money.zero();
    }

    // 5. Public methods (most important first)
    public addItem(item: OrderItem): void {
        this.validateCanModifyOrder();
        this.validateItemLimit();
        this.items.push(item);
        this.recalculateTotal();
    }

    public removeItem(item: OrderItem): void {
        this.validateCanModifyOrder();
        const index = this.items.indexOf(item);
        if (index !== -1) {
            this.items.splice(index, 1);
            this.recalculateTotal();
        }
    }

    // 6. Getters (TypeScript properties)
    public getOrderId(): string {
        return this.orderId;
    }

    public getTotal(): Money {
        return this.total;
    }

    public getItems(): OrderItem[] {
        return [...this.items];  // Defensive copy
    }

    // 7. Private methods
    private validateCanModifyOrder(): void {
        if (this.status === OrderStatus.SHIPPED || this.status === OrderStatus.CANCELLED) {
            throw new Error(`Cannot modify ${this.status} order`);
        }
    }

    private validateItemLimit(): void {
        if (this.items.length >= Order.MAX_ITEMS) {
            throw new Error(`Order cannot exceed ${Order.MAX_ITEMS} items`);
        }
    }

    private recalculateTotal(): void {
        const subtotal = this.items.reduce(
            (sum, item) => sum.add(item.getPrice()),
            Money.zero()
        );

        const tax = subtotal.multiply(Order.TAX_RATE);
        this.total = subtotal.add(tax);
    }

    private static generateOrderId(): string {
        return `ORD-${String(++Order.orderCounter).padStart(6, '0')}`;
    }
}
```

## Class Size: How Small Is Small Enough?

### The Size Rule

**Clean Code Guideline**: Classes should be small. Very small. But how do we measure class size?

**Wrong Metric: Lines of Code**
```python
# BAD: Using lines of code as size metric
# This class is "small" (50 lines) but has too many responsibilities

class UserManager:  # Only 50 lines, but does too much!
    def create_user(self, data): pass
    def validate_email(self, email): pass
    def hash_password(self, password): pass
    def send_welcome_email(self, user): pass
    def log_creation_event(self, user): pass
    def update_analytics(self, user): pass
    def create_home_directory(self, user): pass
    def setup_default_preferences(self, user): pass
```

**Right Metric: Responsibilities**
```python
# GOOD: Measure by responsibilities, not lines
# Each class has ONE responsibility

class UserCreator:
    """Responsible for creating user accounts."""
    def create_user(self, data: UserData) -> User:
        pass

class EmailValidator:
    """Responsible for validating email addresses."""
    def validate(self, email: str) -> bool:
        pass

class PasswordHasher:
    """Responsible for password hashing."""
    def hash_password(self, password: str) -> str:
        pass

class WelcomeEmailer:
    """Responsible for sending welcome emails."""
    def send(self, user: User) -> None:
        pass

class UserAnalytics:
    """Responsible for tracking user analytics."""
    def track_user_creation(self, user: User) -> None:
        pass
```

### The Single Responsibility Principle (SRP)

**Principle**: A class should have one, and only one, reason to change.

**"A class should have one, and only one, reason to change."** — Robert C. Martin

**Anti-Pattern: Multiple Responsibilities**
```java
// BAD: Employee class with multiple responsibilities
public class Employee {
    private String name;
    private String email;
    private double salary;

    // Responsibility 1: Employee data management
    public void setName(String name) {
        this.name = name;
    }

    public String getName() {
        return name;
    }

    // Responsibility 2: Salary calculation
    public double calculatePay() {
        // Complex payroll calculation logic
        double grossPay = salary;
        double taxes = calculateTaxes(grossPay);
        double deductions = calculateDeductions(grossPay);
        return grossPay - taxes - deductions;
    }

    // Responsibility 3: Tax calculation
    private double calculateTaxes(double grossPay) {
        // Tax calculation logic
        return grossPay * 0.25;
    }

    // Responsibility 4: Database persistence
    public void save() {
        Database.execute(
            "UPDATE employees SET name=?, salary=? WHERE id=?",
            name, salary, id
        );
    }

    // Responsibility 5: Reporting
    public String generatePayrollReport() {
        return String.format(
            "Employee: %s\nSalary: $%.2f\nTaxes: $%.2f",
            name, salary, calculateTaxes(salary)
        );
    }

    // This class has 5 reasons to change:
    // 1. Employee data structure changes
    // 2. Payroll calculation rules change
    // 3. Tax laws change
    // 4. Database schema changes
    // 5. Report format changes
}
```

**Good Pattern: Single Responsibility**
```java
// GOOD: Each class has one responsibility

// Responsibility 1: Employee data
public class Employee {
    private final String id;
    private String name;
    private String email;
    private Money salary;

    public Employee(String id, String name, String email, Money salary) {
        this.id = id;
        this.name = name;
        this.email = email;
        this.salary = salary;
    }

    // Only reason to change: Employee data structure
    public String getId() { return id; }
    public String getName() { return name; }
    public void setName(String name) { this.name = name; }
    public Money getSalary() { return salary; }
}

// Responsibility 2: Payroll calculation
public class PayrollCalculator {
    private final TaxCalculator taxCalculator;
    private final DeductionCalculator deductionCalculator;

    public PayrollCalculator(TaxCalculator taxCalculator, DeductionCalculator deductionCalculator) {
        this.taxCalculator = taxCalculator;
        this.deductionCalculator = deductionCalculator;
    }

    // Only reason to change: Payroll rules
    public Money calculateNetPay(Employee employee) {
        Money grossPay = employee.getSalary();
        Money taxes = taxCalculator.calculate(grossPay);
        Money deductions = deductionCalculator.calculate(grossPay);
        return grossPay.subtract(taxes).subtract(deductions);
    }
}

// Responsibility 3: Tax calculation
public class TaxCalculator {
    private final TaxRateProvider taxRateProvider;

    // Only reason to change: Tax laws
    public Money calculate(Money grossPay) {
        double taxRate = taxRateProvider.getCurrentTaxRate();
        return grossPay.multiply(taxRate);
    }
}

// Responsibility 4: Database persistence
public class EmployeeRepository {
    private final Database database;

    // Only reason to change: Database schema or technology
    public void save(Employee employee) {
        database.execute(
            "UPDATE employees SET name=?, salary=? WHERE id=?",
            employee.getName(),
            employee.getSalary().getAmount(),
            employee.getId()
        );
    }

    public Employee findById(String id) {
        // Database query logic
    }
}

// Responsibility 5: Report generation
public class PayrollReportGenerator {
    private final PayrollCalculator calculator;

    // Only reason to change: Report format
    public String generate(Employee employee) {
        Money netPay = calculator.calculateNetPay(employee);
        return String.format(
            "Employee: %s\nSalary: %s\nNet Pay: %s",
            employee.getName(),
            employee.getSalary(),
            netPay
        );
    }
}
```

### Identifying Class Responsibilities

**Test**: Can you describe the class purpose in 25 words or less without using "and," "or," or "but"?

```typescript
// BAD: Description requires "and" - multiple responsibilities
class UserManager {
    // "UserManager validates user input AND saves users to database
    // AND sends welcome emails AND tracks analytics"
    // Multiple "and" = multiple responsibilities
}

// GOOD: Description doesn't need "and" - single responsibility
class UserValidator {
    // "UserValidator validates user input for correctness"
    // One clear responsibility
}

class UserRepository {
    // "UserRepository saves and retrieves users from database"
    // One clear responsibility (persistence)
}

class WelcomeEmailSender {
    // "WelcomeEmailSender sends welcome emails to new users"
    // One clear responsibility
}
```

## Class Cohesion

### Measuring Cohesion

**Cohesion**: How closely the methods and data of a class are related.

**High Cohesion Indicator**: Most methods use most instance variables.

**Example: Low Cohesion (Bad)**
```python
# BAD: Low cohesion - methods use different instance variables
class ReportGenerator:
    def __init__(self):
        # Group 1 variables (used by database methods)
        self.db_connection = None
        self.query_timeout = 30

        # Group 2 variables (used by formatting methods)
        self.page_width = 80
        self.font_size = 12

        # Group 3 variables (used by email methods)
        self.smtp_server = "smtp.example.com"
        self.email_from = "reports@example.com"

    # Uses only Group 1 variables
    def fetch_data(self):
        # Uses: db_connection, query_timeout
        pass

    # Uses only Group 2 variables
    def format_report(self, data):
        # Uses: page_width, font_size
        pass

    # Uses only Group 3 variables
    def email_report(self, report):
        # Uses: smtp_server, email_from
        pass

    # Low cohesion: Each method uses different variables
    # This should be 3 separate classes!
```

**Example: High Cohesion (Good)**
```python
# GOOD: High cohesion - methods use most instance variables
class Stack:
    def __init__(self):
        self._elements = []
        self._max_size = 100
        self._current_size = 0

    def push(self, element):
        # Uses: _elements, _max_size, _current_size
        if self._current_size >= self._max_size:
            raise OverflowError("Stack is full")
        self._elements.append(element)
        self._current_size += 1

    def pop(self):
        # Uses: _elements, _current_size
        if self._current_size == 0:
            raise UnderflowError("Stack is empty")
        element = self._elements.pop()
        self._current_size -= 1
        return element

    def peek(self):
        # Uses: _elements, _current_size
        if self._current_size == 0:
            raise UnderflowError("Stack is empty")
        return self._elements[-1]

    def is_full(self):
        # Uses: _current_size, _max_size
        return self._current_size >= self._max_size

    def is_empty(self):
        # Uses: _current_size
        return self._current_size == 0

    def size(self):
        # Uses: _current_size
        return self._current_size

    # High cohesion: All methods use most instance variables
    # The class represents a coherent concept (Stack)
```

### Maintaining Cohesion Results in Many Small Classes

When you break classes to maintain cohesion, you end up with many small classes:

```java
// Low cohesion: One large class
public class OrderProcessor {
    // Too many unrelated instance variables
    private Database database;
    private EmailService emailService;
    private InventorySystem inventory;
    private PaymentGateway paymentGateway;
    private ShippingCalculator shipping;
    private TaxCalculator tax;
    private Logger logger;

    // Methods use different subsets of variables
}

// High cohesion: Many small, focused classes
public class OrderValidator {
    // Only variables related to validation
    private final ValidationRules rules;

    public ValidationResult validate(Order order) {
        // All methods use 'rules'
    }
}

public class OrderPersistence {
    // Only variables related to persistence
    private final Database database;

    public void save(Order order) {
        // All methods use 'database'
    }
}

public class OrderNotifier {
    // Only variables related to notifications
    private final EmailService emailService;

    public void sendConfirmation(Order order) {
        // All methods use 'emailService'
    }
}

public class InventoryReserver {
    // Only variables related to inventory
    private final InventorySystem inventory;

    public Reservation reserve(Order order) {
        // All methods use 'inventory'
    }
}

// Each class has high cohesion: methods use most instance variables
```

## Organizing for Change: The Open-Closed Principle

**Open-Closed Principle (OCP)**: Classes should be open for extension but closed for modification.

### Anti-Pattern: Switch Statements Indicate Potential OCP Violations

```typescript
// BAD: Must modify class to add new payment types
class PaymentProcessor {
    processPayment(payment: Payment, type: string): PaymentResult {
        // Switch statement = must modify this code for each new payment type
        switch (type) {
            case 'credit_card':
                return this.processCreditCard(payment);
            case 'bank_account':
                return this.processBankAccount(payment);
            case 'paypal':
                return this.processPayPal(payment);
            // Adding Bitcoin? Must modify this class!
            default:
                throw new Error('Unknown payment type');
        }
    }

    private processCreditCard(payment: Payment): PaymentResult {
        // Credit card logic
    }

    private processBankAccount(payment: Payment): PaymentResult {
        // Bank account logic
    }

    private processPayPal(payment: Payment): PaymentResult {
        // PayPal logic
    }

    // Problem: Closed for extension, open for modification
}
```

### Good Pattern: Polymorphism Instead of Switch

```typescript
// GOOD: Open for extension, closed for modification
interface PaymentMethod {
    process(amount: Money): PaymentResult;
}

class CreditCardPayment implements PaymentMethod {
    private readonly cardNumber: string;
    private readonly cvv: string;

    constructor(cardNumber: string, cvv: string) {
        this.cardNumber = cardNumber;
        this.cvv = cvv;
    }

    process(amount: Money): PaymentResult {
        // Credit card specific logic
        return paymentGateway.chargeCreditCard(this.cardNumber, this.cvv, amount);
    }
}

class BankAccountPayment implements PaymentMethod {
    private readonly routingNumber: string;
    private readonly accountNumber: string;

    constructor(routingNumber: string, accountNumber: string) {
        this.routingNumber = routingNumber;
        this.accountNumber = accountNumber;
    }

    process(amount: Money): PaymentResult {
        // Bank account specific logic
        return paymentGateway.processACH(this.routingNumber, this.accountNumber, amount);
    }
}

class PayPalPayment implements PaymentMethod {
    private readonly email: string;

    constructor(email: string) {
        this.email = email;
    }

    process(amount: Money): PaymentResult {
        // PayPal specific logic
        return paypalAPI.createPayment(this.email, amount);
    }
}

// Adding Bitcoin is easy - create new class, don't modify existing code
class BitcoinPayment implements PaymentMethod {
    private readonly walletAddress: string;

    constructor(walletAddress: string) {
        this.walletAddress = walletAddress;
    }

    process(amount: Money): PaymentResult {
        // Bitcoin specific logic
        return bitcoinAPI.sendPayment(this.walletAddress, amount);
    }
}

// PaymentProcessor is now closed for modification
class PaymentProcessor {
    processPayment(paymentMethod: PaymentMethod, amount: Money): PaymentResult {
        // No switch statement needed
        // Works with any PaymentMethod implementation
        return paymentMethod.process(amount);
    }
}

// Open for extension: Add new payment methods without modifying PaymentProcessor
// Closed for modification: PaymentProcessor never changes
```

## Valid Reasons to Create a Class

### 1. Model Real-World Objects

**When**: The class represents something from the problem domain.

```python
# Model domain concepts as classes
class Customer:
    """Represents a customer in the e-commerce system."""
    def __init__(self, customer_id: str, name: str, email: str):
        self.customer_id = customer_id
        self.name = name
        self.email = email
        self.orders: List[Order] = []

class Product:
    """Represents a product available for sale."""
    def __init__(self, product_id: str, name: str, price: Money):
        self.product_id = product_id
        self.name = name
        self.price = price

class Order:
    """Represents a customer's order."""
    def __init__(self, order_id: str, customer: Customer):
        self.order_id = order_id
        self.customer = customer
        self.items: List[OrderItem] = []

# Each class models a real concept from e-commerce domain
```

### 2. Model Abstract Objects

**When**: The class represents an abstraction that doesn't exist in reality but clarifies the design.

```java
// Abstract concept: Iterator (doesn't exist in reality)
public class OrderIterator implements Iterator<Order> {
    private final List<Order> orders;
    private int currentIndex;

    public OrderIterator(List<Order> orders) {
        this.orders = orders;
        this.currentIndex = 0;
    }

    @Override
    public boolean hasNext() {
        return currentIndex < orders.size();
    }

    @Override
    public Order next() {
        if (!hasNext()) {
            throw new NoSuchElementException();
        }
        return orders.get(currentIndex++);
    }
}

// Abstract concept: Command (encapsulates an action)
public interface Command {
    void execute();
    void undo();
}

public class PlaceOrderCommand implements Command {
    private final Order order;
    private final OrderRepository repository;

    @Override
    public void execute() {
        repository.save(order);
    }

    @Override
    public void undo() {
        repository.delete(order);
    }
}
```

### 3. Reduce Complexity

**When**: Hiding complexity behind a simpler interface.

```typescript
// Complex subsystem hidden behind facade
class OrderFulfillmentFacade {
    private inventoryService: InventoryService;
    private shippingService: ShippingService;
    private notificationService: NotificationService;

    // Simple interface hides complex interactions
    async fulfillOrder(order: Order): Promise<FulfillmentResult> {
        // Complex orchestration hidden from caller
        const reservation = await this.inventoryService.reserve(order.items);

        const shipment = await this.shippingService.createShipment(
            order.shippingAddress,
            reservation
        );

        await this.notificationService.sendShipmentNotification(
            order.customer,
            shipment
        );

        return FulfillmentResult.success(shipment.trackingNumber);
    }
}

// Caller sees simple interface, not complex orchestration
const facade = new OrderFulfillmentFacade();
const result = await facade.fulfillOrder(order);  // Simple!
```

### 4. Isolate Complexity

**When**: Complex logic is confined to one class and hidden from others.

```python
# Isolate complex tax calculation logic
class TaxCalculator:
    """Isolates complex tax calculation rules."""

    def __init__(self, tax_jurisdiction_provider: TaxJurisdictionProvider):
        self._jurisdiction_provider = tax_jurisdiction_provider

    def calculate_tax(self, order: Order) -> Money:
        """Calculate tax for order - complexity hidden here."""
        # Complex logic isolated in this class
        jurisdiction = self._jurisdiction_provider.get_jurisdiction(
            order.shipping_address
        )

        tax_rate = self._get_tax_rate_for_jurisdiction(jurisdiction)

        taxable_amount = self._calculate_taxable_amount(order)

        tax = taxable_amount * tax_rate

        # Handle tax exemptions
        if self._is_tax_exempt(order.customer):
            tax = Money.zero()

        return tax

    def _get_tax_rate_for_jurisdiction(self, jurisdiction: TaxJurisdiction) -> float:
        # Complex tax rate determination
        state_rate = jurisdiction.state_tax_rate
        county_rate = jurisdiction.county_tax_rate
        city_rate = jurisdiction.city_tax_rate
        special_district_rate = jurisdiction.special_district_tax_rate

        return state_rate + county_rate + city_rate + special_district_rate

    def _calculate_taxable_amount(self, order: Order) -> Money:
        # Complex logic for what's taxable
        taxable = Money.zero()

        for item in order.items:
            if not item.is_tax_exempt():
                taxable += item.price * item.quantity

        # Shipping is taxable in some jurisdictions
        if order.shipping_address.state in ['CA', 'NY', 'TX']:
            taxable += order.shipping_cost

        return taxable

    def _is_tax_exempt(self, customer: Customer) -> bool:
        # Complex exemption logic
        return (
            customer.has_tax_exempt_certificate() or
            customer.is_government_entity() or
            customer.is_non_profit()
        )

# Complex tax calculation isolated - other classes don't need to know details
```

### 5. Hide Implementation Details

**When**: You want to preserve the ability to change implementation without affecting clients.

```java
// Interface hides implementation details
public interface UserRepository {
    User findById(String userId);
    List<User> findByEmail(String email);
    void save(User user);
    void delete(String userId);
}

// Implementation 1: Database
public class DatabaseUserRepository implements UserRepository {
    private final Database database;

    @Override
    public User findById(String userId) {
        // Database-specific implementation
        return database.query("SELECT * FROM users WHERE id = ?", userId);
    }

    // Other methods...
}

// Implementation 2: In-memory (for testing)
public class InMemoryUserRepository implements UserRepository {
    private final Map<String, User> users = new HashMap<>();

    @Override
    public User findById(String userId) {
        // In-memory implementation
        return users.get(userId);
    }

    // Other methods...
}

// Clients depend on interface, not implementation
public class UserService {
    private final UserRepository repository;  // Interface, not concrete class

    public UserService(UserRepository repository) {
        this.repository = repository;
    }

    public User getUser(String userId) {
        return repository.findById(userId);  // Don't know or care about implementation
    }
}
```

### 6. Limit Effects of Changes

**When**: You expect changes in one area and want to prevent them from rippling through the system.

```typescript
// Isolate configuration changes
class EmailConfiguration {
    private smtpHost: string;
    private smtpPort: number;
    private username: string;
    private password: string;

    // Configuration can change without affecting EmailSender
    static fromEnvironment(): EmailConfiguration {
        return new EmailConfiguration(
            process.env.SMTP_HOST || 'localhost',
            parseInt(process.env.SMTP_PORT || '25'),
            process.env.SMTP_USER || '',
            process.env.SMTP_PASS || ''
        );
    }

    static fromFile(path: string): EmailConfiguration {
        const config = JSON.parse(fs.readFileSync(path, 'utf-8'));
        return new EmailConfiguration(
            config.host,
            config.port,
            config.username,
            config.password
        );
    }

    getSmtpHost(): string { return this.smtpHost; }
    getSmtpPort(): number { return this.smtpPort; }
    // ...
}

// EmailSender doesn't know where configuration comes from
class EmailSender {
    constructor(private config: EmailConfiguration) {}

    send(to: string, subject: string, body: string): void {
        // Use configuration without knowing its source
        const connection = smtp.connect(
            this.config.getSmtpHost(),
            this.config.getSmtpPort()
        );
        // ...
    }
}

// Configuration source can change without affecting EmailSender
const config = EmailConfiguration.fromEnvironment();  // or fromFile()
const sender = new EmailSender(config);
```

### 7. Hide Global Data

**When**: You need global access but want to control how it's used.

```python
# Hide global configuration behind class
class ApplicationConfig:
    """Singleton configuration manager - hides global state."""

    _instance = None
    _config = {}

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def set(self, key: str, value: Any) -> None:
        """Set configuration value."""
        self._config[key] = value

    def get(self, key: str, default: Any = None) -> Any:
        """Get configuration value."""
        return self._config.get(key, default)

    def get_database_url(self) -> str:
        """Get database URL with validation."""
        url = self.get('database_url')
        if not url:
            raise ConfigurationError("Database URL not configured")
        return url

    def get_max_connections(self) -> int:
        """Get max connections with default."""
        return self.get('max_connections', 10)

# Global access controlled through class methods
config = ApplicationConfig()
config.set('database_url', 'postgresql://localhost/mydb')

# Accessing global data is explicit
db_url = config.get_database_url()

# Better than: DATABASE_URL = 'postgresql://localhost/mydb' (raw global)
```

### 8. Group Related Operations

**When**: Related operations belong together and share data.

```java
// Group related string operations
public class StringFormatter {
    // Related operations that share common functionality
    public String toTitleCase(String text) {
        return Arrays.stream(text.split(" "))
            .map(word -> capitalize(word))
            .collect(Collectors.joining(" "));
    }

    public String toCamelCase(String text) {
        String[] words = text.split(" ");
        StringBuilder result = new StringBuilder(words[0].toLowerCase());
        for (int i = 1; i < words.length; i++) {
            result.append(capitalize(words[i]));
        }
        return result.toString();
    }

    public String toSnakeCase(String text) {
        return text.toLowerCase().replace(" ", "_");
    }

    public String toKebabCase(String text) {
        return text.toLowerCase().replace(" ", "-");
    }

    // Shared helper method
    private String capitalize(String word) {
        if (word.isEmpty()) return word;
        return word.substring(0, 1).toUpperCase() + word.substring(1).toLowerCase();
    }
}
```

## Encapsulation and Information Hiding

### Minimize Public Interface

**Principle**: Make everything private by default, expose only what's necessary.

```python
# BAD: Too much exposed
class BankAccount:
    def __init__(self, account_number):
        self.account_number = account_number
        self.balance = 0.0  # Public - can be modified directly!
        self.transactions = []  # Public - internal state exposed!

# Client can break invariants
account = BankAccount("12345")
account.balance = 1000000.0  # Fraud! No transaction record
account.transactions.clear()  # Erase transaction history!

# GOOD: Minimal public interface
class BankAccount:
    def __init__(self, account_number):
        self._account_number = account_number
        self._balance = 0.0  # Private
        self._transactions = []  # Private

    # Controlled access through methods
    def deposit(self, amount: float) -> None:
        """Deposit money into account."""
        if amount <= 0:
            raise ValueError("Deposit amount must be positive")

        self._balance += amount
        self._transactions.append(Transaction("DEPOSIT", amount))

    def withdraw(self, amount: float) -> None:
        """Withdraw money from account."""
        if amount <= 0:
            raise ValueError("Withdrawal amount must be positive")
        if amount > self._balance:
            raise InsufficientFundsError("Insufficient funds")

        self._balance -= amount
        self._transactions.append(Transaction("WITHDRAWAL", amount))

    def get_balance(self) -> float:
        """Get current balance."""
        return self._balance

    def get_transaction_history(self) -> List[Transaction]:
        """Get copy of transaction history."""
        return self._transactions.copy()  # Defensive copy

# Invariants are protected
account = BankAccount("12345")
account.deposit(100.0)  # Controlled access
# account._balance = 1000000.0  # Python convention: don't access private
```

### Defensive Copying

**Principle**: Don't return references to mutable internal state.

```java
// BAD: Returns reference to internal mutable state
public class Order {
    private List<OrderItem> items;

    public List<OrderItem> getItems() {
        return items;  // BAD: Returns reference to internal list
    }
}

// Client can modify internal state
Order order = new Order();
List<OrderItem> items = order.getItems();
items.clear();  // Just cleared the order's items!

// GOOD: Returns defensive copy
public class Order {
    private List<OrderItem> items;

    public List<OrderItem> getItems() {
        return new ArrayList<>(items);  // Defensive copy
    }

    // Even better: Return unmodifiable view
    public List<OrderItem> getItemsUnmodifiable() {
        return Collections.unmodifiableList(items);
    }
}

// Client can't modify internal state
Order order = new Order();
List<OrderItem> items = order.getItems();
items.clear();  // Only clears the copy, not the order's internal list
```

## Inheritance vs. Composition

### Favor Composition Over Inheritance

**When to Use Inheritance**: True "is-a" relationships that won't change.

```typescript
// GOOD: Legitimate inheritance (is-a relationship)
abstract class Shape {
    abstract calculateArea(): number;
    abstract calculatePerimeter(): number;
}

class Circle extends Shape {
    constructor(private radius: number) {
        super();
    }

    calculateArea(): number {
        return Math.PI * this.radius ** 2;
    }

    calculatePerimeter(): number {
        return 2 * Math.PI * this.radius;
    }
}

class Rectangle extends Shape {
    constructor(private width: number, private height: number) {
        super();
    }

    calculateArea(): number {
        return this.width * this.height;
    }

    calculatePerimeter(): number {
        return 2 * (this.width + this.height);
    }
}

// Circle "is-a" Shape ✓
// Rectangle "is-a" Shape ✓
```

**When to Use Composition**: "has-a" relationships or when behavior varies.

```typescript
// BAD: Inheritance for behavior reuse (has-a, not is-a)
class Logger {
    log(message: string): void {
        console.log(message);
    }
}

class UserService extends Logger {  // UserService "is-a" Logger? NO!
    createUser(data: UserData): User {
        this.log("Creating user");  // Using inherited method
        // ...
    }
}

// GOOD: Composition for behavior reuse
class Logger {
    log(message: string): void {
        console.log(message);
    }
}

class UserService {
    private logger: Logger;  // UserService "has-a" Logger ✓

    constructor(logger: Logger) {
        this.logger = logger;
    }

    createUser(data: UserData): User {
        this.logger.log("Creating user");  // Using composed object
        // ...
    }
}
```

### Problems with Inheritance

**Problem 1: Fragile Base Class**
```python
# Base class change breaks subclasses
class PaymentProcessor:
    def process(self, amount):
        self.validate(amount)  # Calls validate
        # Process payment

    def validate(self, amount):
        if amount <= 0:
            raise ValueError("Amount must be positive")

class PremiumPaymentProcessor(PaymentProcessor):
    def validate(self, amount):
        super().validate(amount)
        if amount > 10000:  # Premium accounts have limit
            raise ValueError("Amount too large")

# Later, base class changes
class PaymentProcessor:
    def process(self, amount):
        # Removed validate call - broke PremiumPaymentProcessor!
        # Process payment directly
```

**Problem 2: Unclear Intent**
```java
// What methods should subclasses override? Not clear from base class
public class Document {
    public void save() { }
    public void print() { }
    public void email() { }
    public void archive() { }

    // Which methods should subclasses override?
    // All? Some? None?
}
```

**Composition Solution**:
```java
// Clear, flexible, composable
public interface Saveable {
    void save();
}

public interface Printable {
    void print();
}

public interface Emailable {
    void email();
}

public class Document implements Saveable, Printable {
    private final SaveStrategy saveStrategy;
    private final PrintStrategy printStrategy;

    @Override
    public void save() {
        saveStrategy.save(this);
    }

    @Override
    public void print() {
        printStrategy.print(this);
    }

    // Clear what this document can do
    // Easy to add new capabilities by implementing more interfaces
    // Easy to change behavior by swapping strategies
}
```

## Summary: Class Design Principles

1. **Small Classes**: Measure by responsibilities, not lines of code
2. **Single Responsibility**: One reason to change
3. **High Cohesion**: Methods use most instance variables
4. **Open-Closed**: Open for extension, closed for modification
5. **Minimal Interface**: Make everything private by default
6. **Information Hiding**: Hide implementation details
7. **Defensive Copying**: Protect internal state
8. **Favor Composition**: Use composition over inheritance
9. **Organize for Change**: Expect change, design for it
10. **Meaningful Names**: Class names reveal purpose

## Further Reading

- **Code Complete 2** (Chapter 6: Working Classes) - Steve McConnell
- **Clean Code** (Chapter 10: Classes) - Robert C. Martin
- **Effective Java** (Items on Classes and Interfaces) - Joshua Bloch
- **Design Patterns** - Gang of Four
- **Refactoring** - Martin Fowler

---

**Remember**: Classes are the fundamental organizational unit of object-oriented design. Well-designed classes are small, focused, cohesive, and loosely coupled. They hide their implementation details, have clear responsibilities, and are organized for change. Every class you create should have a clear reason to exist and a single reason to change.
