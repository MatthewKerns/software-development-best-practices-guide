# Design in Construction: Crafting Software Architecture During Coding

## Overview

Design in construction is the critical practice of making design decisions at the code level while building software. Unlike upfront architectural design that establishes system-wide structures, design in construction focuses on the daily design decisions developers make: choosing class structures, defining interfaces, organizing modules, managing dependencies, and creating abstractions.

This is where the theoretical meets the practical—where high-level architecture transforms into working code. The quality of these construction-level design decisions directly determines whether your codebase becomes maintainable and flexible, or devolves into an unmaintainable tangle of dependencies.

**"Design is not just what it looks like and feels like. Design is how it works."** — Steve Jobs

## Why Design During Construction Matters

### The Cost of Poor Construction Design

Construction-level design decisions compound over time:

**Complexity Explosion**: Each poorly designed class adds cognitive load. A system with 100 poorly designed classes is exponentially harder to understand than one with 100 well-designed classes.

**Change Amplification**: Small changes require modifications to many parts of the system. A one-line feature request becomes a week-long refactoring project.

**Fragility**: Changes in one area unexpectedly break unrelated functionality. Developers fear making changes, leading to workarounds and patches instead of proper fixes.

**Rigidity**: The system resists change. New requirements that should be simple require architectural gymnastics to implement.

**Immobility**: Code cannot be reused because it's too tangled with its current context. Duplication becomes the path of least resistance.

### The Benefits of Good Construction Design

Well-designed construction provides:
- **Conceptual Integrity**: The system has a coherent structure that makes sense
- **Changeability**: New requirements are accommodated with localized changes
- **Comprehensibility**: New developers understand the system quickly
- **Reusability**: Components can be used in multiple contexts
- **Testability**: Components can be tested in isolation
- **Maintainability**: Bugs are fixed in one place, not scattered throughout

## Source Materials

This guide synthesizes principles from:

- **Code Complete 2** by Steve McConnell (Chapter 5: "Design in Construction")
  - Design levels and heuristics
  - Managing complexity through abstraction
  - Information hiding and encapsulation
  - Design patterns at the construction level

- **Clean Code** by Robert C. Martin
  - Classes should be small and focused
  - Object-oriented design principles
  - Dependency management

## Levels of Design in Construction

Design happens at multiple levels, from the system architecture down to individual algorithms. Understanding these levels helps you make appropriate design decisions at each scale.

### 1. System Design Level

**Scope**: The entire software system.

**Concerns**: Major subsystems, system-wide data structures, database organization, high-level communication protocols.

**Construction Impact**: Usually decided before construction, but construction reveals flaws.

```python
# System-level design: Architecture pattern choice
# Example: Layered architecture decision

# Presentation Layer
class WebController:
    """Handles HTTP requests/responses."""
    def __init__(self, service_layer):
        self.service = service_layer

    def handle_request(self, request):
        result = self.service.process(request.data)
        return self.format_response(result)

# Business Logic Layer
class BusinessService:
    """Implements business rules."""
    def __init__(self, data_layer):
        self.repository = data_layer

    def process(self, data):
        validated = self.validate(data)
        result = self.apply_business_rules(validated)
        self.repository.save(result)
        return result

# Data Access Layer
class DataRepository:
    """Handles data persistence."""
    def save(self, entity):
        # Database operations
        pass

    def find(self, criteria):
        # Query operations
        pass

# System design: Layers depend downward only
# WebController -> BusinessService -> DataRepository
# Never: DataRepository -> BusinessService
```

### 2. Division into Subsystems

**Scope**: Breaking the system into major components.

**Concerns**: Subsystem responsibilities, subsystem interfaces, subsystem communication.

**Construction Decision**: How to organize related functionality into cohesive modules.

```typescript
// Subsystem-level design: Organizing related functionality

// Subsystem 1: Authentication
export namespace Authentication {
    export interface IAuthService {
        login(credentials: Credentials): Promise<Session>;
        logout(sessionId: string): Promise<void>;
        verifyToken(token: string): Promise<User>;
    }

    export class AuthService implements IAuthService {
        // Implementation
    }
}

// Subsystem 2: User Management
export namespace UserManagement {
    export interface IUserService {
        createUser(userData: UserData): Promise<User>;
        updateUser(userId: string, updates: Partial<UserData>): Promise<User>;
        deleteUser(userId: string): Promise<void>;
    }

    export class UserService implements IUserService {
        // Implementation
    }
}

// Subsystem 3: Notification
export namespace Notification {
    export interface INotificationService {
        sendEmail(recipient: string, message: EmailMessage): Promise<void>;
        sendSMS(phoneNumber: string, message: string): Promise<void>;
    }

    export class NotificationService implements INotificationService {
        // Implementation
    }
}

// Subsystems have well-defined boundaries and interfaces
// They can be developed, tested, and deployed independently
```

### 3. Class Design Level

**Scope**: Individual classes and their relationships.

**Concerns**: Class responsibilities, class interfaces, inheritance hierarchies, composition relationships.

**Construction Decision**: This is where most construction-level design happens.

```java
// Class-level design: Single Responsibility Principle

// Good: Each class has one reason to change
public class Invoice {
    private final String invoiceId;
    private final Customer customer;
    private final List<LineItem> items;
    private final Money total;

    // Invoice knows about invoice data and calculations
    public Invoice(String invoiceId, Customer customer, List<LineItem> items) {
        this.invoiceId = invoiceId;
        this.customer = customer;
        this.items = new ArrayList<>(items);
        this.total = calculateTotal();
    }

    private Money calculateTotal() {
        return items.stream()
            .map(LineItem::getPrice)
            .reduce(Money.ZERO, Money::add);
    }

    public Money getTotal() {
        return total;
    }

    // Other invoice-specific methods...
}

// Separate class for persistence concerns
public class InvoiceRepository {
    private final Database database;

    public InvoiceRepository(Database database) {
        this.database = database;
    }

    // Repository knows about saving and retrieving invoices
    public void save(Invoice invoice) {
        database.execute("INSERT INTO invoices...", invoice);
    }

    public Invoice findById(String invoiceId) {
        return database.query("SELECT * FROM invoices WHERE id = ?", invoiceId);
    }
}

// Separate class for formatting concerns
public class InvoiceFormatter {
    // Formatter knows about presentation
    public String formatAsPdf(Invoice invoice) {
        // PDF generation logic
        return "PDF content";
    }

    public String formatAsHtml(Invoice invoice) {
        // HTML generation logic
        return "<html>Invoice...</html>";
    }
}
```

### 4. Routine Design Level

**Scope**: Individual functions and methods.

**Concerns**: Function interfaces, parameters, algorithms, error handling.

**Construction Decision**: How to structure the logic within classes.

```python
# Routine-level design: Algorithm selection and implementation

class CustomerAnalytics:
    """Analyze customer behavior patterns."""

    def calculate_customer_lifetime_value(self, customer_id: str) -> float:
        """Calculate predicted lifetime value of customer.

        Design decision: Use average purchase value * purchase frequency * customer lifetime
        """
        purchases = self._get_customer_purchases(customer_id)
        avg_purchase_value = self._calculate_average_purchase_value(purchases)
        purchase_frequency = self._calculate_purchase_frequency(purchases)
        customer_lifetime = self._estimate_customer_lifetime(purchases)

        return avg_purchase_value * purchase_frequency * customer_lifetime

    def _get_customer_purchases(self, customer_id: str) -> list:
        """Retrieve all purchases for customer."""
        # Design decision: Return list of Purchase objects
        return self.repository.find_purchases_by_customer(customer_id)

    def _calculate_average_purchase_value(self, purchases: list) -> float:
        """Calculate average value of purchases."""
        # Design decision: Simple mean calculation
        if not purchases:
            return 0.0

        total = sum(purchase.total for purchase in purchases)
        return total / len(purchases)

    def _calculate_purchase_frequency(self, purchases: list) -> float:
        """Calculate purchases per year."""
        # Design decision: Use actual date range from purchases
        if len(purchases) < 2:
            return 1.0

        earliest = min(purchase.date for purchase in purchases)
        latest = max(purchase.date for purchase in purchases)
        days_span = (latest - earliest).days

        if days_span == 0:
            return len(purchases)

        years_span = days_span / 365.25
        return len(purchases) / years_span

    def _estimate_customer_lifetime(self, purchases: list) -> float:
        """Estimate years customer will remain active."""
        # Design decision: Industry standard 5-year lifetime
        # Could be enhanced with churn prediction model
        return 5.0
```

### 5. Internal Routine Design Level

**Scope**: The algorithm and logic inside a single routine.

**Concerns**: Code structure, variable names, control flow, data structures.

**Construction Decision**: Making the code clear and efficient.

```typescript
// Internal routine design: Clear structure and logic flow

function processOrderPayment(order: Order, paymentInfo: PaymentInfo): PaymentResult {
    // Design decision: Guard clauses for validation
    if (!order || !order.items || order.items.length === 0) {
        throw new ValidationError("Order must have items");
    }

    if (!paymentInfo || !paymentInfo.token) {
        throw new ValidationError("Payment information required");
    }

    // Design decision: Separate calculation from action
    const paymentAmount = calculateOrderTotal(order);

    // Design decision: Explicit error handling
    let paymentResponse: PaymentGatewayResponse;
    try {
        paymentResponse = await paymentGateway.charge(
            paymentInfo.token,
            paymentAmount
        );
    } catch (error) {
        return PaymentResult.failed(
            `Payment processing failed: ${error.message}`
        );
    }

    // Design decision: Check response explicitly
    if (!paymentResponse.success) {
        return PaymentResult.failed(
            paymentResponse.errorMessage || "Unknown payment error"
        );
    }

    // Design decision: Update order state only after successful payment
    order.markAsPaid(paymentResponse.transactionId);
    await orderRepository.save(order);

    return PaymentResult.successful(paymentResponse.transactionId);
}

function calculateOrderTotal(order: Order): Money {
    // Design decision: Use Money type for currency safety
    const subtotal = order.items.reduce(
        (sum, item) => sum.add(item.price.multiply(item.quantity)),
        Money.zero()
    );

    const tax = subtotal.multiply(order.taxRate);
    const shipping = calculateShipping(order);

    return subtotal.add(tax).add(shipping);
}
```

## Key Design Heuristics for Construction

### Heuristic 1: Manage Complexity Through Abstraction

**Principle**: The human mind can hold 7±2 items in working memory. Managing complexity means creating abstractions that reduce cognitive load.

**Anti-Pattern: Complexity Exposed**
```python
# BAD: Too much complexity exposed at once
def process_customer_order(customer_data, items_data, payment_data, shipping_data):
    """Process an order - TOO COMPLEX"""
    # Validate customer (20 lines)
    if not customer_data.get('email'):
        raise ValueError("Email required")
    if not '@' in customer_data.get('email', ''):
        raise ValueError("Invalid email")
    if not customer_data.get('name'):
        raise ValueError("Name required")
    # ... 15 more validation lines

    # Validate items (25 lines)
    if not items_data:
        raise ValueError("Must have items")
    for item in items_data:
        if not item.get('product_id'):
            raise ValueError("Product ID required")
        # ... more validation

    # Calculate totals (30 lines)
    subtotal = 0
    for item in items_data:
        quantity = item.get('quantity', 0)
        price = get_product_price(item['product_id'])
        item_total = quantity * price
        if item.get('discount_code'):
            # Complex discount calculation
            # ... 15 lines
        subtotal += item_total
    # ... more calculations

    # Process payment (40 lines)
    # ... complex payment logic

    # Create shipment (30 lines)
    # ... complex shipping logic

    # Total: 145 lines, impossible to understand
```

**Good Pattern: Complexity Hidden**
```python
# GOOD: Complexity managed through abstraction layers
def process_customer_order(order_request: OrderRequest) -> OrderResult:
    """Process customer order through well-defined steps."""
    # Each step hides complexity behind clear abstraction
    customer = validate_and_create_customer(order_request.customer_data)
    order = create_order(customer, order_request.items_data)
    payment = process_payment(order, order_request.payment_data)
    shipment = create_shipment(order, order_request.shipping_data)

    return OrderResult(order, payment, shipment)

# Each function manages one level of complexity
def validate_and_create_customer(customer_data: dict) -> Customer:
    """Validate customer data and create Customer object."""
    validator = CustomerValidator()
    validator.validate(customer_data)
    return Customer.from_dict(customer_data)

def create_order(customer: Customer, items_data: list) -> Order:
    """Create order from customer and items."""
    items = [OrderItem.from_dict(item_data) for item_data in items_data]
    order = Order(customer=customer, items=items)
    order.calculate_totals()
    return order

def process_payment(order: Order, payment_data: dict) -> Payment:
    """Process payment for order."""
    payment_processor = PaymentProcessor()
    return payment_processor.charge(order, payment_data)

def create_shipment(order: Order, shipping_data: dict) -> Shipment:
    """Create shipment for order."""
    shipping_service = ShippingService()
    return shipping_service.create_shipment(order, shipping_data)
```

**Benefit**: Each function is understandable in isolation. The complexity is distributed across layers of abstraction.

### Heuristic 2: Information Hiding (Encapsulation)

**Principle**: Hide design decisions that are likely to change. Expose only stable interfaces.

**Anti-Pattern: Implementation Exposed**
```java
// BAD: Implementation details exposed
public class UserPreferences {
    // Public fields - implementation exposed
    public Map<String, String> preferences;
    public String storageFilePath;
    public SimpleDateFormat dateFormat;

    public UserPreferences() {
        this.preferences = new HashMap<>();
        this.storageFilePath = "/data/users/prefs.json";
        this.dateFormat = new SimpleDateFormat("yyyy-MM-dd");
    }

    // Clients must know about storage format
    public void save() {
        // Write JSON to file
        try (FileWriter writer = new FileWriter(storageFilePath)) {
            JSONObject json = new JSONObject(preferences);
            writer.write(json.toString());
        } catch (IOException e) {
            e.printStackTrace();
        }
    }
}

// Client code tightly coupled to implementation
UserPreferences prefs = new UserPreferences();
prefs.preferences.put("theme", "dark");  // Direct map access
prefs.preferences.put("language", "en");
prefs.save();  // Must know to call save()

// Problems:
// 1. Changing storage format (JSON -> DB) breaks all clients
// 2. Can't validate preference values
// 3. Can't track changes
// 4. Thread safety issues
```

**Good Pattern: Implementation Hidden**
```java
// GOOD: Implementation hidden behind interface
public interface IUserPreferences {
    void setPreference(String key, String value);
    String getPreference(String key);
    void setTheme(Theme theme);
    Theme getTheme();
}

public class UserPreferences implements IUserPreferences {
    private final PreferenceStore store;
    private final Map<String, String> cache;
    private final Set<String> modifiedKeys;

    public UserPreferences(PreferenceStore store) {
        this.store = store;
        this.cache = new HashMap<>();
        this.modifiedKeys = new HashSet<>();
        loadPreferences();
    }

    @Override
    public void setPreference(String key, String value) {
        validateKey(key);
        validateValue(value);
        cache.put(key, value);
        modifiedKeys.add(key);
        autosaveIfNeeded();
    }

    @Override
    public String getPreference(String key) {
        return cache.getOrDefault(key, getDefaultValue(key));
    }

    @Override
    public void setTheme(Theme theme) {
        setPreference("theme", theme.toString());
    }

    @Override
    public Theme getTheme() {
        String value = getPreference("theme");
        return Theme.valueOf(value);
    }

    private void loadPreferences() {
        cache.putAll(store.load());
    }

    private void autosaveIfNeeded() {
        if (modifiedKeys.size() >= 5) {
            store.save(cache);
            modifiedKeys.clear();
        }
    }

    private void validateKey(String key) {
        if (key == null || key.isEmpty()) {
            throw new IllegalArgumentException("Key cannot be empty");
        }
    }

    private void validateValue(String value) {
        if (value == null) {
            throw new IllegalArgumentException("Value cannot be null");
        }
    }

    private String getDefaultValue(String key) {
        // Return sensible defaults
        return switch (key) {
            case "theme" -> "light";
            case "language" -> "en";
            default -> "";
        };
    }
}

// Storage implementation hidden in separate class
interface PreferenceStore {
    Map<String, String> load();
    void save(Map<String, String> preferences);
}

// Can switch implementations without affecting clients
class JsonFilePreferenceStore implements PreferenceStore {
    // JSON file implementation
}

class DatabasePreferenceStore implements PreferenceStore {
    // Database implementation
}

// Client code decoupled from implementation
IUserPreferences prefs = new UserPreferences(new JsonFilePreferenceStore());
prefs.setTheme(Theme.DARK);  // Type-safe, validated
prefs.setPreference("language", "en");
// Auto-saves, no client awareness needed
```

**Benefits of Information Hiding**:
1. **Changeability**: Storage can change from files to database without client changes
2. **Validation**: All preference changes are validated
3. **Optimization**: Auto-save logic can be optimized without client knowledge
4. **Testability**: Can inject mock `PreferenceStore` for testing
5. **Safety**: Type-safe methods prevent invalid theme values

### Heuristic 3: Identify Areas Likely to Change

**Principle**: Design flexibility where you need it, not everywhere. Focus on likely changes.

**Common Areas of Change**:
1. Business rules
2. Dependencies on external systems
3. Data formats and protocols
4. Hardware and platform dependencies
5. Input/output formats
6. User interface

**Example: Isolating Likely Changes**
```typescript
// Business Rule: Likely to change
// Isolate in separate strategy classes

interface DiscountStrategy {
    calculateDiscount(order: Order): Money;
    getDescription(): string;
}

// Easy to change: Just add new strategy class
class PercentageDiscountStrategy implements DiscountStrategy {
    constructor(private percentage: number) {}

    calculateDiscount(order: Order): Money {
        return order.subtotal.multiply(this.percentage);
    }

    getDescription(): string {
        return `${this.percentage * 100}% off`;
    }
}

class BuyOneGetOneStrategy implements DiscountStrategy {
    calculateDiscount(order: Order): Money {
        // BOGO logic
        let discount = Money.zero();
        // Implementation...
        return discount;
    }

    getDescription(): string {
        return "Buy One Get One Free";
    }
}

class VolumeDiscountStrategy implements DiscountStrategy {
    constructor(private thresholds: Map<number, number>) {}

    calculateDiscount(order: Order): Money {
        const itemCount = order.getTotalItemCount();
        const discountPercent = this.getDiscountForVolume(itemCount);
        return order.subtotal.multiply(discountPercent);
    }

    private getDiscountForVolume(itemCount: number): number {
        // Find applicable threshold
        let maxDiscount = 0;
        this.thresholds.forEach((discount, threshold) => {
            if (itemCount >= threshold && discount > maxDiscount) {
                maxDiscount = discount;
            }
        });
        return maxDiscount;
    }

    getDescription(): string {
        return "Volume Discount";
    }
}

// Order class doesn't change when discount rules change
class Order {
    private discountStrategy: DiscountStrategy;

    setDiscountStrategy(strategy: DiscountStrategy): void {
        this.discountStrategy = strategy;
    }

    calculateTotal(): Money {
        const discount = this.discountStrategy
            ? this.discountStrategy.calculateDiscount(this)
            : Money.zero();

        return this.subtotal.subtract(discount).add(this.tax);
    }
}

// New discount rules? Just create new strategy class
class SeasonalDiscountStrategy implements DiscountStrategy {
    calculateDiscount(order: Order): Money {
        const season = this.getCurrentSeason();
        const multiplier = this.getSeasonalMultiplier(season);
        return order.subtotal.multiply(multiplier);
    }

    getDescription(): string {
        return `${this.getCurrentSeason()} Sale`;
    }

    private getCurrentSeason(): string {
        // Determine current season
        return "Holiday";
    }

    private getSeasonalMultiplier(season: string): number {
        // Season-specific discounts
        const seasonalDiscounts = {
            "Holiday": 0.25,
            "Summer": 0.15,
            "Spring": 0.10,
            "Fall": 0.10
        };
        return seasonalDiscounts[season] || 0;
    }
}
```

### Heuristic 4: Keep Coupling Loose

**Principle**: Minimize dependencies between modules. Classes should know as little as possible about each other.

**Types of Coupling (Worst to Best)**:

#### Content Coupling (Worst)
One module directly modifies another module's internal data.

```python
# WORST: Content coupling
class BankAccount:
    def __init__(self):
        self.balance = 0  # Public, directly accessible

    def deposit(self, amount):
        self.balance += amount

# Another class directly manipulates internal state
class AccountManager:
    def transfer(self, from_account, to_account, amount):
        # Directly accessing and modifying internal state
        from_account.balance -= amount  # TERRIBLE
        to_account.balance += amount    # TERRIBLE
        # No validation, no transaction safety
```

#### Common Coupling (Very Bad)
Multiple modules share global data.

```java
// VERY BAD: Common coupling via global state
public class GlobalConfig {
    public static double TAX_RATE = 0.08;
    public static String CURRENCY = "USD";
    public static boolean DEBUG_MODE = false;
}

public class OrderCalculator {
    public double calculateTotal(double subtotal) {
        // Dependent on global state
        return subtotal * (1 + GlobalConfig.TAX_RATE);
    }
}

public class InvoiceFormatter {
    public String format(double amount) {
        // Dependent on same global state
        return GlobalConfig.CURRENCY + " " + amount;
    }
}

// Problems:
// 1. Hidden dependencies
// 2. Testing requires global state manipulation
// 3. Concurrent execution issues
// 4. No isolation
```

#### Control Coupling (Bad)
One module controls the flow of another by passing control flags.

```typescript
// BAD: Control coupling
function processUser(user: User, mode: string): void {
    if (mode === "create") {
        // Create logic
    } else if (mode === "update") {
        // Update logic
    } else if (mode === "delete") {
        // Delete logic
    }
    // Caller controls internal flow
}

// Better: Separate functions
function createUser(user: User): void {
    // Create logic
}

function updateUser(user: User): void {
    // Update logic
}

function deleteUser(user: User): void {
    // Delete logic
}
```

#### Data Coupling (Good)
Modules share only necessary data through parameters.

```python
# GOOD: Data coupling
class TaxCalculator:
    """Calculates taxes based on order data."""

    def calculate_sales_tax(self, subtotal: float, tax_rate: float) -> float:
        """Calculate sales tax.

        Args:
            subtotal: Order subtotal amount
            tax_rate: Applicable tax rate (0-1)

        Returns:
            Tax amount
        """
        return subtotal * tax_rate

    def calculate_item_tax(self, item_price: float, quantity: int, tax_rate: float) -> float:
        """Calculate tax for individual item.

        Args:
            item_price: Price per item
            quantity: Number of items
            tax_rate: Applicable tax rate (0-1)

        Returns:
            Tax amount for items
        """
        return item_price * quantity * tax_rate

class OrderProcessor:
    """Processes customer orders."""

    def __init__(self, tax_calculator: TaxCalculator):
        self.tax_calculator = tax_calculator

    def process_order(self, order: Order) -> OrderReceipt:
        """Process order and generate receipt."""
        subtotal = order.calculate_subtotal()
        tax = self.tax_calculator.calculate_sales_tax(
            subtotal,
            order.get_tax_rate()
        )
        total = subtotal + tax

        return OrderReceipt(
            order_id=order.id,
            subtotal=subtotal,
            tax=tax,
            total=total
        )

# Only necessary data passed between classes
# No shared state, no control flow coupling
# Easy to test in isolation
```

### Heuristic 5: Aim for Strong Cohesion

**Principle**: Elements within a module should belong together. A class should have one reason to exist.

**Example: Low Cohesion (Anti-Pattern)**
```java
// BAD: Low cohesion - unrelated responsibilities
public class UserUtilities {
    // User validation
    public boolean isValidEmail(String email) {
        return email.contains("@");
    }

    // Password hashing
    public String hashPassword(String password) {
        return BCrypt.hashpw(password, BCrypt.gensalt());
    }

    // Report generation
    public Report generateUserReport(User user) {
        // Report logic
    }

    // Email sending
    public void sendWelcomeEmail(String email) {
        // Email logic
    }

    // Database cleanup
    public void deleteInactiveUsers(int daysInactive) {
        // Cleanup logic
    }

    // These operations have nothing to do with each other!
}
```

**Example: High Cohesion (Good Pattern)**
```java
// GOOD: High cohesion - related responsibilities grouped

// Email validation cohesion
public class EmailValidator {
    private static final Pattern EMAIL_PATTERN =
        Pattern.compile("^[A-Z0-9._%+-]+@[A-Z0-9.-]+\\.[A-Z]{2,6}$",
                       Pattern.CASE_INSENSITIVE);

    public boolean isValid(String email) {
        if (email == null || email.isEmpty()) {
            return false;
        }
        return EMAIL_PATTERN.matcher(email).matches();
    }

    public EmailValidationResult validateWithDetails(String email) {
        if (email == null || email.isEmpty()) {
            return EmailValidationResult.invalid("Email is required");
        }
        if (!EMAIL_PATTERN.matcher(email).matches()) {
            return EmailValidationResult.invalid("Invalid email format");
        }
        return EmailValidationResult.valid();
    }
}

// Password operations cohesion
public class PasswordService {
    private final int BCRYPT_ROUNDS = 12;

    public String hashPassword(String plainPassword) {
        return BCrypt.hashpw(plainPassword, BCrypt.gensalt(BCRYPT_ROUNDS));
    }

    public boolean verifyPassword(String plainPassword, String hashedPassword) {
        return BCrypt.checkpw(plainPassword, hashedPassword);
    }

    public boolean isStrongPassword(String password) {
        return password.length() >= 8 &&
               password.matches(".*[A-Z].*") &&
               password.matches(".*[a-z].*") &&
               password.matches(".*[0-9].*");
    }
}

// Reporting cohesion
public class UserReportGenerator {
    private final UserRepository userRepository;
    private final ReportFormatter formatter;

    public Report generateActivityReport(String userId, DateRange range) {
        User user = userRepository.findById(userId);
        List<Activity> activities = userRepository.getActivities(userId, range);
        return formatter.formatActivityReport(user, activities);
    }

    public Report generateSummaryReport(List<String> userIds) {
        List<User> users = userRepository.findByIds(userIds);
        return formatter.formatSummaryReport(users);
    }
}

// Email operations cohesion
public class UserEmailService {
    private final EmailSender emailSender;
    private final TemplateEngine templateEngine;

    public void sendWelcomeEmail(User user) {
        String content = templateEngine.render("welcome", user);
        emailSender.send(user.getEmail(), "Welcome!", content);
    }

    public void sendPasswordResetEmail(User user, String resetToken) {
        Map<String, Object> data = Map.of(
            "user", user,
            "resetToken", resetToken
        );
        String content = templateEngine.render("password-reset", data);
        emailSender.send(user.getEmail(), "Password Reset", content);
    }
}

// User maintenance cohesion
public class UserMaintenanceService {
    private final UserRepository userRepository;
    private final Clock clock;

    public int deleteInactiveUsers(int daysInactive) {
        LocalDate threshold = LocalDate.now(clock).minusDays(daysInactive);
        List<User> inactiveUsers = userRepository.findInactiveSince(threshold);

        for (User user : inactiveUsers) {
            userRepository.delete(user.getId());
        }

        return inactiveUsers.size();
    }

    public void archiveOldAccounts(int yearsOld) {
        LocalDate threshold = LocalDate.now(clock).minusYears(yearsOld);
        List<User> oldUsers = userRepository.findCreatedBefore(threshold);

        for (User user : oldUsers) {
            userRepository.archive(user.getId());
        }
    }
}
```

### Heuristic 6: Build Hierarchies (Inheritance and Composition)

**Principle**: Use inheritance for "is-a" relationships, composition for "has-a" relationships.

**Inheritance: When to Use**
Use inheritance when:
- Subclass truly "is-a" specialized version of superclass
- Subclass will never violate superclass contract
- Changes to superclass should propagate to subclass

```python
# Good use of inheritance: "is-a" relationship

class PaymentMethod:
    """Base class for all payment methods."""

    def __init__(self, customer_id: str):
        self.customer_id = customer_id
        self.last_used = None

    def process_payment(self, amount: float) -> PaymentResult:
        """Process payment - must be implemented by subclasses."""
        raise NotImplementedError("Subclasses must implement process_payment")

    def validate(self) -> bool:
        """Validate payment method - must be implemented by subclasses."""
        raise NotImplementedError("Subclasses must implement validate")

    def update_last_used(self):
        """Update last used timestamp."""
        self.last_used = datetime.now()

# CreditCard "is-a" PaymentMethod
class CreditCard(PaymentMethod):
    """Credit card payment method."""

    def __init__(self, customer_id: str, card_number: str, expiry_date: str, cvv: str):
        super().__init__(customer_id)
        self.card_number = card_number
        self.expiry_date = expiry_date
        self.cvv = cvv

    def process_payment(self, amount: float) -> PaymentResult:
        """Process credit card payment."""
        if not self.validate():
            return PaymentResult.failed("Invalid card")

        # Process with payment gateway
        result = payment_gateway.charge_card(
            self.card_number,
            amount,
            self.cvv
        )

        if result.success:
            self.update_last_used()

        return result

    def validate(self) -> bool:
        """Validate credit card details."""
        return (
            self._is_valid_card_number() and
            self._is_not_expired() and
            self._is_valid_cvv()
        )

    def _is_valid_card_number(self) -> bool:
        # Luhn algorithm check
        return luhn_check(self.card_number)

    def _is_not_expired(self) -> bool:
        expiry = datetime.strptime(self.expiry_date, "%m/%Y")
        return expiry > datetime.now()

    def _is_valid_cvv(self) -> bool:
        return len(self.cvv) in [3, 4] and self.cvv.isdigit()

# BankAccount "is-a" PaymentMethod
class BankAccount(PaymentMethod):
    """Bank account payment method (ACH)."""

    def __init__(self, customer_id: str, routing_number: str, account_number: str):
        super().__init__(customer_id)
        self.routing_number = routing_number
        self.account_number = account_number

    def process_payment(self, amount: float) -> PaymentResult:
        """Process ACH payment."""
        if not self.validate():
            return PaymentResult.failed("Invalid bank account")

        result = payment_gateway.process_ach(
            self.routing_number,
            self.account_number,
            amount
        )

        if result.success:
            self.update_last_used()

        return result

    def validate(self) -> bool:
        """Validate bank account details."""
        return (
            self._is_valid_routing_number() and
            self._is_valid_account_number()
        )

    def _is_valid_routing_number(self) -> bool:
        return len(self.routing_number) == 9 and self.routing_number.isdigit()

    def _is_valid_account_number(self) -> bool:
        return len(self.account_number) >= 4 and self.account_number.isdigit()

# PayPal "is-a" PaymentMethod
class PayPal(PaymentMethod):
    """PayPal payment method."""

    def __init__(self, customer_id: str, email: str):
        super().__init__(customer_id)
        self.email = email

    def process_payment(self, amount: float) -> PaymentResult:
        """Process PayPal payment."""
        if not self.validate():
            return PaymentResult.failed("Invalid PayPal account")

        result = paypal_api.create_payment(self.email, amount)

        if result.success:
            self.update_last_used()

        return result

    def validate(self) -> bool:
        """Validate PayPal account."""
        return '@' in self.email and '.' in self.email

# Polymorphic usage
def charge_customer(payment_method: PaymentMethod, amount: float) -> PaymentResult:
    """Charge customer using any payment method."""
    # Works with any PaymentMethod subclass
    return payment_method.process_payment(amount)

# All payment methods work identically
credit_card = CreditCard("CUST-123", "4111111111111111", "12/2025", "123")
bank_account = BankAccount("CUST-123", "123456789", "987654321")
paypal = PayPal("CUST-123", "customer@email.com")

charge_customer(credit_card, 100.00)
charge_customer(bank_account, 100.00)
charge_customer(paypal, 100.00)
```

**Composition: When to Use**
Use composition when:
- Relationship is "has-a" not "is-a"
- You need flexibility to change components at runtime
- Multiple components work together to provide functionality

```typescript
// Good use of composition: "has-a" relationships

// Components that can be composed
class EmailNotifier {
    send(recipient: string, subject: string, body: string): void {
        // Email sending logic
        console.log(`Email sent to ${recipient}: ${subject}`);
    }
}

class SMSNotifier {
    send(phoneNumber: string, message: string): void {
        // SMS sending logic
        console.log(`SMS sent to ${phoneNumber}: ${message}`);
    }
}

class PushNotifier {
    send(deviceToken: string, message: string): void {
        // Push notification logic
        console.log(`Push sent to ${deviceToken}: ${message}`);
    }
}

class Logger {
    log(level: string, message: string): void {
        console.log(`[${level}] ${message}`);
    }
}

// Order "has-a" collection of notifiers (composition)
class Order {
    private emailNotifier: EmailNotifier;
    private smsNotifier: SMSNotifier;
    private pushNotifier: PushNotifier;
    private logger: Logger;

    constructor(
        emailNotifier: EmailNotifier,
        smsNotifier: SMSNotifier,
        pushNotifier: PushNotifier,
        logger: Logger
    ) {
        // Compose with multiple components
        this.emailNotifier = emailNotifier;
        this.smsNotifier = smsNotifier;
        this.pushNotifier = pushNotifier;
        this.logger = logger;
    }

    placeOrder(customer: Customer): void {
        // Use composed components
        this.logger.log("INFO", `Placing order for ${customer.email}`);

        // Can use different notification methods
        if (customer.preferences.emailNotifications) {
            this.emailNotifier.send(
                customer.email,
                "Order Confirmation",
                "Your order has been placed"
            );
        }

        if (customer.preferences.smsNotifications) {
            this.smsNotifier.send(
                customer.phoneNumber,
                "Order confirmed"
            );
        }

        if (customer.preferences.pushNotifications) {
            this.pushNotifier.send(
                customer.deviceToken,
                "Your order is confirmed"
            );
        }
    }
}

// Composition allows flexible configuration
const order = new Order(
    new EmailNotifier(),
    new SMSNotifier(),
    new PushNotifier(),
    new Logger()
);

// Could easily swap implementations
class MockEmailNotifier extends EmailNotifier {
    send(recipient: string, subject: string, body: string): void {
        // Mock implementation for testing
    }
}

const testOrder = new Order(
    new MockEmailNotifier(),  // Different implementation
    new SMSNotifier(),
    new PushNotifier(),
    new Logger()
);
```

**Favor Composition Over Inheritance**
```java
// Problem with inheritance: rigid hierarchy
class Animal {
    void eat() { }
    void sleep() { }
}

class Bird extends Animal {
    void fly() { }  // All birds fly?
}

class Penguin extends Bird {
    @Override
    void fly() {
        throw new UnsupportedOperationException("Penguins can't fly!");
    }

    void swim() { }
}

// Inheritance hierarchy breaks down

// Better: Composition with interfaces
interface Eater {
    void eat();
}

interface Sleeper {
    void sleep();
}

interface Flyer {
    void fly();
}

interface Swimmer {
    void swim();
}

// Compose behaviors
class Penguin implements Eater, Sleeper, Swimmer {
    private final EatingBehavior eatingBehavior;
    private final SleepingBehavior sleepingBehavior;
    private final SwimmingBehavior swimmingBehavior;

    public Penguin() {
        this.eatingBehavior = new FishEater();
        this.sleepingBehavior = new StandingSleeper();
        this.swimmingBehavior = new DivingSwimmer();
    }

    @Override
    public void eat() {
        eatingBehavior.eat();
    }

    @Override
    public void sleep() {
        sleepingBehavior.sleep();
    }

    @Override
    public void swim() {
        swimmingBehavior.swim();
    }

    // Penguin doesn't implement Flyer - no broken contract
}

class Sparrow implements Eater, Sleeper, Flyer {
    private final EatingBehavior eatingBehavior;
    private final SleepingBehavior sleepingBehavior;
    private final FlyingBehavior flyingBehavior;

    public Sparrow() {
        this.eatingBehavior = new SeedEater();
        this.sleepingBehavior = new NestSleeper();
        this.flyingBehavior = new WingFlyer();
    }

    @Override
    public void eat() {
        eatingBehavior.eat();
    }

    @Override
    public void sleep() {
        sleepingBehavior.sleep();
    }

    @Override
    public void fly() {
        flyingBehavior.fly();
    }
}
```

## Design Patterns at the Construction Level

### Factory Pattern: Encapsulate Object Creation

**When to Use**: When object creation is complex or when you want to decouple creation from usage.

```python
# Without Factory Pattern
class EmailService:
    def __init__(self):
        if os.getenv("ENV") == "production":
            self.sender = SMTPSender(
                host=os.getenv("SMTP_HOST"),
                port=int(os.getenv("SMTP_PORT")),
                username=os.getenv("SMTP_USER"),
                password=os.getenv("SMTP_PASS")
            )
        elif os.getenv("ENV") == "development":
            self.sender = ConsoleSender()
        else:
            self.sender = LogFileSender("/tmp/emails.log")

# Problem: Email service knows about all sender types and configuration
# Every class that needs email sender has this duplication

# With Factory Pattern
class EmailSenderFactory:
    """Factory for creating appropriate email sender based on environment."""

    @staticmethod
    def create_sender() -> EmailSender:
        """Create and configure email sender for current environment."""
        env = os.getenv("ENV", "development")

        if env == "production":
            return EmailSenderFactory._create_production_sender()
        elif env == "staging":
            return EmailSenderFactory._create_staging_sender()
        elif env == "test":
            return EmailSenderFactory._create_test_sender()
        else:
            return EmailSenderFactory._create_development_sender()

    @staticmethod
    def _create_production_sender() -> EmailSender:
        """Create production SMTP sender."""
        return SMTPSender(
            host=os.getenv("SMTP_HOST"),
            port=int(os.getenv("SMTP_PORT")),
            username=os.getenv("SMTP_USER"),
            password=os.getenv("SMTP_PASS"),
            use_tls=True
        )

    @staticmethod
    def _create_staging_sender() -> EmailSender:
        """Create staging sender (logs to file, doesn't send)."""
        return LogFileSender("/var/log/staging-emails.log")

    @staticmethod
    def _create_test_sender() -> EmailSender:
        """Create test sender (collects emails for assertion)."""
        return CollectingSender()

    @staticmethod
    def _create_development_sender() -> EmailSender:
        """Create development sender (prints to console)."""
        return ConsoleSender()

# Usage: Simple and clean
class EmailService:
    def __init__(self):
        self.sender = EmailSenderFactory.create_sender()

    def send_welcome_email(self, user_email: str):
        self.sender.send(
            to=user_email,
            subject="Welcome!",
            body="Thank you for signing up"
        )

# Benefits:
# 1. Centralized configuration
# 2. Easy to add new environments
# 3. Easy to test (inject CollectingSender)
# 4. Single responsibility (factory handles creation)
```

### Strategy Pattern: Encapsulate Algorithms

**When to Use**: When you have multiple algorithms for the same task and want to make them interchangeable.

```typescript
// Strategy Pattern: Different shipping calculation algorithms

interface ShippingStrategy {
    calculateCost(order: Order): Money;
    estimateDeliveryDays(): number;
    getServiceName(): string;
}

class StandardShippingStrategy implements ShippingStrategy {
    calculateCost(order: Order): Money {
        const baseRate = new Money(5.99);
        const weightCharge = order.getWeight() * 0.50;
        return baseRate.add(new Money(weightCharge));
    }

    estimateDeliveryDays(): number {
        return 5;  // 5-7 business days
    }

    getServiceName(): string {
        return "Standard Shipping";
    }
}

class ExpressShippingStrategy implements ShippingStrategy {
    calculateCost(order: Order): Money {
        const baseRate = new Money(15.99);
        const weightCharge = order.getWeight() * 1.00;
        return baseRate.add(new Money(weightCharge));
    }

    estimateDeliveryDays(): number {
        return 2;  // 2-3 business days
    }

    getServiceName(): string {
        return "Express Shipping";
    }
}

class OvernightShippingStrategy implements ShippingStrategy {
    calculateCost(order: Order): Money {
        const baseRate = new Money(29.99);
        const weightCharge = order.getWeight() * 2.00;
        const distance = order.getShippingDistance();
        const distanceCharge = distance > 500 ? 10.00 : 0;
        return baseRate
            .add(new Money(weightCharge))
            .add(new Money(distanceCharge));
    }

    estimateDeliveryDays(): number {
        return 1;  // Next day
    }

    getServiceName(): string {
        return "Overnight Shipping";
    }
}

class FreeShippingStrategy implements ShippingStrategy {
    private readonly threshold: Money;

    constructor(threshold: Money = new Money(50.00)) {
        this.threshold = threshold;
    }

    calculateCost(order: Order): Money {
        if (order.getSubtotal().isGreaterThan(this.threshold)) {
            return Money.zero();
        }
        return new StandardShippingStrategy().calculateCost(order);
    }

    estimateDeliveryDays(): number {
        return 5;
    }

    getServiceName(): string {
        return "Free Shipping";
    }
}

// Order uses strategy pattern
class Order {
    private shippingStrategy: ShippingStrategy;

    setShippingStrategy(strategy: ShippingStrategy): void {
        this.shippingStrategy = strategy;
    }

    calculateShippingCost(): Money {
        if (!this.shippingStrategy) {
            this.shippingStrategy = new StandardShippingStrategy();
        }
        return this.shippingStrategy.calculateCost(this);
    }

    getEstimatedDelivery(): string {
        const days = this.shippingStrategy.estimateDeliveryDays();
        const deliveryDate = new Date();
        deliveryDate.setDate(deliveryDate.getDate() + days);
        return deliveryDate.toLocaleDateString();
    }
}

// Usage: Easy to change shipping calculation
const order = new Order();

// Standard shipping
order.setShippingStrategy(new StandardShippingStrategy());
console.log(order.calculateShippingCost());  // $5.99 + weight

// Switch to express
order.setShippingStrategy(new ExpressShippingStrategy());
console.log(order.calculateShippingCost());  // $15.99 + weight

// Promotional free shipping
order.setShippingStrategy(new FreeShippingStrategy(new Money(30.00)));
console.log(order.calculateShippingCost());  // $0 if order > $30

// Benefits:
// 1. Easy to add new shipping methods
// 2. Shipping logic isolated and testable
// 3. Can change strategy at runtime
// 4. Open-closed principle: open to extension, closed to modification
```

### Template Method Pattern: Define Algorithm Skeleton

**When to Use**: When you have an algorithm with invariant steps but variable implementations.

```java
// Template Method Pattern: Order processing workflow

public abstract class OrderProcessor {
    // Template method - defines algorithm skeleton
    public final OrderResult processOrder(Order order) {
        try {
            validateOrder(order);

            Payment payment = processPayment(order);
            if (!payment.isSuccessful()) {
                return OrderResult.paymentFailed(payment.getErrorMessage());
            }

            reserveInventory(order);

            Shipment shipment = createShipment(order);

            sendConfirmation(order, payment, shipment);

            logOrderSuccess(order);

            return OrderResult.success(order, payment, shipment);

        } catch (ValidationException e) {
            logOrderFailure(order, e);
            return OrderResult.validationFailed(e.getMessage());
        } catch (Exception e) {
            logOrderFailure(order, e);
            rollbackOrder(order);
            return OrderResult.failed(e.getMessage());
        }
    }

    // Abstract methods - must be implemented by subclasses
    protected abstract void validateOrder(Order order) throws ValidationException;
    protected abstract Payment processPayment(Order order);
    protected abstract void reserveInventory(Order order);
    protected abstract Shipment createShipment(Order order);

    // Hook methods - can be overridden but have default implementation
    protected void sendConfirmation(Order order, Payment payment, Shipment shipment) {
        emailService.sendOrderConfirmation(order.getCustomer().getEmail(), order);
    }

    protected void logOrderSuccess(Order order) {
        logger.info("Order processed successfully: " + order.getId());
    }

    protected void logOrderFailure(Order order, Exception e) {
        logger.error("Order processing failed: " + order.getId(), e);
    }

    protected void rollbackOrder(Order order) {
        // Default rollback implementation
        try {
            inventoryService.releaseReservation(order.getId());
        } catch (Exception e) {
            logger.error("Rollback failed for order: " + order.getId(), e);
        }
    }
}

// Concrete implementation for retail orders
public class RetailOrderProcessor extends OrderProcessor {
    @Override
    protected void validateOrder(Order order) throws ValidationException {
        if (order.getItems().isEmpty()) {
            throw new ValidationException("Order must have items");
        }

        if (order.getShippingAddress() == null) {
            throw new ValidationException("Shipping address required");
        }

        for (OrderItem item : order.getItems()) {
            if (!productCatalog.isAvailable(item.getProductId())) {
                throw new ValidationException("Product not available: " + item.getProductId());
            }
        }
    }

    @Override
    protected Payment processPayment(Order order) {
        return paymentGateway.charge(
            order.getPaymentMethod(),
            order.getTotal()
        );
    }

    @Override
    protected void reserveInventory(Order order) {
        for (OrderItem item : order.getItems()) {
            inventoryService.reserve(
                item.getProductId(),
                item.getQuantity(),
                order.getId()
            );
        }
    }

    @Override
    protected Shipment createShipment(Order order) {
        return shippingService.createShipment(
            order.getItems(),
            order.getShippingAddress()
        );
    }
}

// Concrete implementation for wholesale orders (different rules)
public class WholesaleOrderProcessor extends OrderProcessor {
    @Override
    protected void validateOrder(Order order) throws ValidationException {
        if (order.getItems().isEmpty()) {
            throw new ValidationException("Order must have items");
        }

        // Wholesale-specific: Minimum order quantity
        int totalQuantity = order.getItems().stream()
            .mapToInt(OrderItem::getQuantity)
            .sum();

        if (totalQuantity < 100) {
            throw new ValidationException("Minimum wholesale order: 100 units");
        }

        // Wholesale-specific: Credit check
        if (!creditService.hasAvailableCredit(order.getCustomer(), order.getTotal())) {
            throw new ValidationException("Insufficient credit limit");
        }
    }

    @Override
    protected Payment processPayment(Order order) {
        // Wholesale uses net-30 terms instead of immediate payment
        return Payment.onAccount(order.getCustomer(), order.getTotal(), 30);
    }

    @Override
    protected void reserveInventory(Order order) {
        // Wholesale reservation from different warehouse
        for (OrderItem item : order.getItems()) {
            warehouseService.reserveWholesale(
                item.getProductId(),
                item.getQuantity(),
                order.getId()
            );
        }
    }

    @Override
    protected Shipment createShipment(Order order) {
        // Wholesale uses freight shipping
        return freightService.createFreightShipment(
            order.getItems(),
            order.getShippingAddress()
        );
    }

    @Override
    protected void sendConfirmation(Order order, Payment payment, Shipment shipment) {
        // Wholesale gets different confirmation format
        emailService.sendWholesaleConfirmation(
            order.getCustomer().getEmail(),
            order,
            payment.getTerms()
        );
    }
}

// Usage: Same interface, different implementations
OrderProcessor retailProcessor = new RetailOrderProcessor();
OrderResult result1 = retailProcessor.processOrder(retailOrder);

OrderProcessor wholesaleProcessor = new WholesaleOrderProcessor();
OrderResult result2 = wholesaleProcessor.processOrder(wholesaleOrder);

// Benefits:
// 1. Algorithm structure guaranteed consistent
// 2. Subclasses can't skip steps or change order
// 3. Common code in one place (DRY)
// 4. Easy to add new order types
// 5. Testable at multiple levels
```

## Integration with Geist Framework

### Ghost: Designing for Unknown Requirements

**Ghost Analysis Question**: What requirements might emerge that I don't know about yet?

**Design Response**: Build flexibility where uncertainty exists.

```python
# Ghost: We don't know all the validation rules that might be needed

# Inflexible design
class UserValidator:
    def validate(self, user_data):
        if not user_data.get('email'):
            raise ValueError("Email required")
        if not user_data.get('password'):
            raise ValueError("Password required")
        # What about future requirements? Change this class?

# Ghost-aware design: Open for extension
class ValidationRule(ABC):
    """Base class for all validation rules."""

    @abstractmethod
    def validate(self, data: dict) -> ValidationResult:
        """Validate data according to this rule."""
        pass

class EmailRequiredRule(ValidationRule):
    def validate(self, data: dict) -> ValidationResult:
        if not data.get('email'):
            return ValidationResult.invalid("Email required")
        return ValidationResult.valid()

class PasswordStrengthRule(ValidationRule):
    def __init__(self, min_length: int = 8):
        self.min_length = min_length

    def validate(self, data: dict) -> ValidationResult:
        password = data.get('password', '')
        if len(password) < self.min_length:
            return ValidationResult.invalid(
                f"Password must be at least {self.min_length} characters"
            )
        return ValidationResult.valid()

class UserValidator:
    """Validator that can accommodate unknown future rules."""

    def __init__(self):
        self.rules: list[ValidationRule] = []

    def add_rule(self, rule: ValidationRule):
        """Add validation rule - Ghost: Future rules we don't know about yet."""
        self.rules.append(rule)

    def validate(self, user_data: dict) -> ValidationResult:
        """Validate user data against all rules."""
        for rule in self.rules:
            result = rule.validate(user_data)
            if not result.is_valid:
                return result
        return ValidationResult.valid()

# Usage: Can add unknown future rules without changing validator
validator = UserValidator()
validator.add_rule(EmailRequiredRule())
validator.add_rule(PasswordStrengthRule(min_length=10))

# Future: New compliance requirement appears
class GDPRComplianceRule(ValidationRule):
    """New rule we didn't know about during initial design."""
    def validate(self, data: dict) -> ValidationResult:
        if not data.get('gdpr_consent'):
            return ValidationResult.invalid("GDPR consent required")
        return ValidationResult.valid()

# Just add it - no changes to existing code
validator.add_rule(GDPRComplianceRule())
```

### Geyser: Designing for Explosive Growth

**Geyser Analysis Question**: How will this system behave under pressure? What happens when it scales 10x? 100x?

**Design Response**: Design for performance and scalability from the start.

```typescript
// Geyser: System might need to handle millions of notifications

// Non-scalable design
class NotificationService {
    sendNotifications(userIds: string[], message: string): void {
        // Geyser problem: Loads all users into memory
        const users = this.userRepository.findByIds(userIds);

        for (const user of users) {
            // Geyser problem: Synchronous, blocks on each send
            this.emailSender.send(user.email, message);
        }
        // Geyser problem: No batching, no rate limiting
        // With 1M users, this will fail spectacularly
    }
}

// Geyser-aware design: Built for scale
interface NotificationBatch {
    users: User[];
    message: string;
}

class ScalableNotificationService {
    private readonly batchSize = 1000;
    private readonly maxConcurrentBatches = 10;

    async sendNotifications(userIds: string[], message: string): Promise<void> {
        // Geyser: Stream users instead of loading all
        const userStream = this.userRepository.streamByIds(userIds);

        // Geyser: Process in batches
        const batches = this.createBatches(userStream, this.batchSize);

        // Geyser: Parallel processing with concurrency limit
        const queue = new ConcurrencyLimitedQueue(this.maxConcurrentBatches);

        for await (const batch of batches) {
            queue.add(async () => {
                await this.processBatch(batch, message);
            });
        }

        await queue.waitForCompletion();
    }

    private async *createBatches(
        userStream: AsyncIterable<User>,
        batchSize: number
    ): AsyncGenerator<User[]> {
        let batch: User[] = [];

        for await (const user of userStream) {
            batch.push(user);

            if (batch.length >= batchSize) {
                yield batch;
                batch = [];
            }
        }

        if (batch.length > 0) {
            yield batch;
        }
    }

    private async processBatch(users: User[], message: string): Promise<void> {
        // Geyser: Bulk sending to reduce API calls
        const emailAddresses = users.map(u => u.email);

        try {
            await this.emailSender.sendBulk(emailAddresses, message);

            // Geyser: Track success for monitoring
            this.metrics.recordBatchSuccess(users.length);

        } catch (error) {
            // Geyser: Resilient error handling
            await this.handleBatchFailure(users, message, error);
        }

        // Geyser: Rate limiting to prevent overwhelming downstream systems
        await this.rateLimiter.waitForCapacity();
    }

    private async handleBatchFailure(
        users: User[],
        message: string,
        error: Error
    ): Promise<void> {
        // Geyser: Failed batches go to retry queue
        await this.retryQueue.enqueue({
            users,
            message,
            error: error.message,
            attemptCount: 0
        });

        this.metrics.recordBatchFailure(users.length);
    }
}

// Geyser: Monitoring and metrics built in
class NotificationMetrics {
    recordBatchSuccess(count: number): void {
        this.successCounter.increment(count);
        this.throughputGauge.set(count);
    }

    recordBatchFailure(count: number): void {
        this.failureCounter.increment(count);
    }

    getHealthStatus(): HealthStatus {
        const successRate = this.calculateSuccessRate();

        if (successRate < 0.95) {
            return HealthStatus.DEGRADED;
        }

        return HealthStatus.HEALTHY;
    }
}
```

### Gist: Designing for Essential Complexity

**Gist Analysis Question**: What is the irreducible essence of this problem? What complexity is essential vs accidental?

**Design Response**: Eliminate accidental complexity, embrace essential complexity with clear models.

```java
// Gist: What is the essence of an "Order"?

// Accidental complexity: Mixed concerns
public class Order {
    // Essential: Order data
    private String orderId;
    private Customer customer;
    private List<OrderItem> items;

    // Accidental: Formatting concerns mixed in
    public String toJson() {
        return new Gson().toJson(this);
    }

    public String toXml() {
        return new XmlMapper().writeValueAsString(this);
    }

    // Accidental: Persistence concerns mixed in
    public void saveToDatabase() {
        Connection conn = Database.getConnection();
        // SQL statements...
    }

    // Accidental: Email concerns mixed in
    public void sendConfirmationEmail() {
        EmailSender.send(customer.getEmail(), "Order confirmation...");
    }

    // Accidental: Validation mixed with business logic
    public void placeOrder() {
        if (items.isEmpty()) throw new RuntimeException("No items");
        if (customer == null) throw new RuntimeException("No customer");
        // ... place order logic mixed with validation
    }
}

// Gist-focused design: Essential complexity only
public class Order {
    // GIST: These are the essence of an order
    private final OrderId orderId;
    private final CustomerId customerId;
    private final List<OrderLine> lines;
    private final Money subtotal;
    private final Money tax;
    private final Money total;
    private final OrderStatus status;
    private final Instant createdAt;

    private Order(
        OrderId orderId,
        CustomerId customerId,
        List<OrderLine> lines,
        Instant createdAt
    ) {
        // GIST: Essential invariant - order must have items
        if (lines.isEmpty()) {
            throw new IllegalArgumentException("Order must have items");
        }

        this.orderId = orderId;
        this.customerId = customerId;
        this.lines = new ArrayList<>(lines);  // Defensive copy
        this.createdAt = createdAt;

        // GIST: Essential business rule - calculate totals
        this.subtotal = calculateSubtotal();
        this.tax = calculateTax();
        this.total = subtotal.add(tax);
        this.status = OrderStatus.PENDING;
    }

    // GIST: Essential behavior - calculate order totals
    private Money calculateSubtotal() {
        return lines.stream()
            .map(OrderLine::getLineTotal)
            .reduce(Money.zero(), Money::add);
    }

    private Money calculateTax() {
        return subtotal.multiply(TaxRate.STANDARD.getValue());
    }

    // GIST: Essential behavior - confirm order
    public Order confirm() {
        if (status != OrderStatus.PENDING) {
            throw new IllegalStateException("Can only confirm pending orders");
        }
        return new Order(orderId, customerId, lines, createdAt)
            .withStatus(OrderStatus.CONFIRMED);
    }

    // GIST: Essential behavior - cancel order
    public Order cancel() {
        if (status == OrderStatus.SHIPPED) {
            throw new IllegalStateException("Cannot cancel shipped order");
        }
        return new Order(orderId, customerId, lines, createdAt)
            .withStatus(OrderStatus.CANCELLED);
    }

    // GIST: Essential queries
    public OrderId getId() { return orderId; }
    public CustomerId getCustomerId() { return customerId; }
    public Money getTotal() { return total; }
    public OrderStatus getStatus() { return status; }
    public List<OrderLine> getLines() { return new ArrayList<>(lines); }

    // Factory method
    public static Order create(CustomerId customerId, List<OrderLine> lines) {
        return new Order(
            OrderId.generate(),
            customerId,
            lines,
            Instant.now()
        );
    }
}

// Accidental complexity separated into other classes
public class OrderRepository {
    public void save(Order order) {
        // Persistence logic separate from domain model
    }
}

public class OrderJsonFormatter {
    public String format(Order order) {
        // Formatting logic separate from domain model
    }
}

public class OrderConfirmationService {
    public void sendConfirmation(Order order) {
        // Email logic separate from domain model
    }
}

// GIST: Order class now contains only essential complexity
// - Order identity and data
// - Business rules for order totals
// - Business rules for order lifecycle
// Everything else is accidental complexity handled elsewhere
```

## Practical Design Checklist

Use this checklist when making construction-level design decisions:

### Complexity Management
- [ ] Each class has a single, clear purpose
- [ ] Classes are organized into cohesive subsystems
- [ ] Complexity is hidden behind abstractions
- [ ] Deep nesting (>3 levels) is eliminated
- [ ] Each level of abstraction is consistent

### Information Hiding
- [ ] Implementation details are private
- [ ] Public interfaces are minimal and stable
- [ ] Likely changes are isolated behind interfaces
- [ ] Dependencies are on abstractions, not concretions

### Coupling and Cohesion
- [ ] Classes have loose coupling (few dependencies)
- [ ] Classes have strong cohesion (related responsibilities)
- [ ] No circular dependencies
- [ ] Dependencies point in one direction

### Inheritance and Composition
- [ ] Inheritance used only for true "is-a" relationships
- [ ] Composition preferred for "has-a" relationships
- [ ] Liskov Substitution Principle is honored
- [ ] No more than 3-4 levels of inheritance

### Design Patterns
- [ ] Patterns used appropriately (not over-engineered)
- [ ] Patterns solve real problems, not hypothetical ones
- [ ] Pattern implementation is clear and documented
- [ ] Patterns don't add unnecessary complexity

### Geist Integration
- [ ] Ghost: Design accommodates unknown future requirements
- [ ] Geyser: Design handles growth and scaling pressures
- [ ] Gist: Essential complexity is clear, accidental complexity eliminated

## Common Design Anti-Patterns

### The God Class
**Problem**: One class does everything.

**Solution**: Apply Single Responsibility Principle, break into focused classes.

### The Blob
**Problem**: Large class with low cohesion - unrelated responsibilities grouped together.

**Solution**: Extract classes based on responsibility.

### Spaghetti Code
**Problem**: No clear structure, tangled dependencies, hard to follow flow.

**Solution**: Introduce layers, clarify dependencies, extract functions.

### Lava Flow
**Problem**: Dead code and obsolete features left in system.

**Solution**: Remove unused code aggressively, keep codebase clean.

### Golden Hammer
**Problem**: Using same solution for every problem ("When you have a hammer, everything looks like a nail").

**Solution**: Choose patterns based on actual problem, not familiarity.

### Premature Optimization
**Problem**: Optimizing before understanding actual performance bottlenecks.

**Solution**: Design for clarity first, measure performance, optimize as needed.

## Summary: Essential Principles

1. **Manage Complexity**: Hide complexity behind abstractions
2. **Information Hiding**: Expose minimal, stable interfaces
3. **Design for Change**: Isolate likely changes behind boundaries
4. **Loose Coupling**: Minimize dependencies between classes
5. **Strong Cohesion**: Keep related responsibilities together
6. **Favor Composition**: Prefer "has-a" over "is-a"
7. **Use Patterns Wisely**: Patterns solve problems, not theory
8. **Geist-Aware Design**: Consider Ghost (unknowns), Geyser (growth), Gist (essence)

## Further Reading

- **Code Complete 2** (Chapter 5: Design in Construction) - Steve McConnell
- **Clean Code** (Chapters 6, 10: Objects and Classes) - Robert C. Martin
- **Design Patterns: Elements of Reusable Object-Oriented Software** - Gang of Four
- **Refactoring: Improving the Design of Existing Code** - Martin Fowler
- **Domain-Driven Design** - Eric Evans

---

**Remember**: Design is not a separate phase that happens before coding. Design happens continuously during construction. Every class you write, every function you create, every abstraction you introduce is a design decision. Make these decisions deliberately, with clear principles guiding you.
