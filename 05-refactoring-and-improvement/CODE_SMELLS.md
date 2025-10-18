# Code Smells: Recognizing When Code Needs Improvement

## Overview

A code smell is a surface indication that usually corresponds to a deeper problem in the system. Code smells are not bugs - they are not technically incorrect and do not prevent the program from functioning. Instead, they indicate weaknesses in design that may slow down development or increase the risk of bugs or failures in the future.

The term "code smell" was popularized by Kent Beck and Martin Fowler. A smell doesn't always indicate a problem, but it suggests you should look closer. Like a medical symptom, a code smell is something that can be quickly spotted and might indicate a need for refactoring.

This comprehensive guide catalogs the most common code smells, helps you recognize them, and points you toward appropriate refactorings.

## Why Code Smells Matter

### The Cost of Ignoring Smells

Code smells compound over time. What starts as a slightly-too-long function becomes a 500-line monstrosity that nobody wants to touch. Unchecked smells lead to:

**Decreased Development Velocity**: Developers spend increasing time understanding existing code rather than adding features. Small changes require disproportionate effort.

**Increased Bug Rate**: Complex, smelly code hides bugs. Developers making changes can't fully understand the implications, leading to defects.

**Technical Debt Accumulation**: Each ignored smell makes the next change harder. Interest compounds on technical debt just like financial debt.

**Developer Frustration**: Good developers want to work in clean codebases. Persistent code smells drive away talent.

**Risky Changes**: When code is complex and unclear, even simple changes become risky. Fear of breaking things leads to paralysis.

### The Benefits of Smell Detection

Actively identifying and addressing code smells provides:
- **Early Warning System**: Catch design problems before they become architectural issues
- **Objective Code Review**: Concrete criteria for "this needs refactoring"
- **Shared Vocabulary**: Team can discuss "feature envy" instead of vague "bad code"
- **Incremental Improvement**: Address one smell at a time rather than massive rewrites
- **Better Design Sense**: Learning smells improves your ability to write clean code initially

## Source Materials

This guide synthesizes principles from:

- **Clean Code** by Robert C. Martin (Chapter 17)
  - Comprehensive catalog of smells
  - Comments, environment, functions, names
  - General and test smells

- **Refactoring** by Martin Fowler
  - Original code smell catalog
  - Relationship between smells and refactorings
  - When to refactor vs. tolerate smells

- **Code Complete 2** by Steve McConnell
  - Recognizing problematic code
  - Measurable quality indicators
  - When to refactor vs. rewrite

## Comment Smells

Comments are often a sign that code isn't clear enough. While some comments are valuable, many indicate deeper problems.

### C1: Inappropriate Information

**Smell**: Comments contain information better held elsewhere, such as change history, author, or approval signatures.

**Why It Smells**: Version control systems track this information better. Comments get out of date.

**Poor Example:**
```python
# Author: John Doe
# Created: 2020-01-15
# Modified: 2020-03-22 by Jane Smith
# Modified: 2020-07-10 by Bob Johnson
# Approved by: Alice Williams
# Ticket: JIRA-1234
def calculate_discount(price, customer_type):
    """Calculate customer discount"""
    if customer_type == "premium":
        return price * 0.15
    return price * 0.05
```

**Better Approach:**
```python
def calculate_discount(price: float, customer_type: str) -> float:
    """Calculate discount based on customer tier.

    Premium customers receive 15% discount.
    Standard customers receive 5% discount.
    """
    PREMIUM_DISCOUNT = 0.15
    STANDARD_DISCOUNT = 0.05

    if customer_type == "premium":
        return price * PREMIUM_DISCOUNT
    return price * STANDARD_DISCOUNT
```

**Refactoring**: Remove metadata comments. Let git track history. Add only domain-relevant comments.

### C2: Obsolete Comment

**Smell**: Comment describes code that no longer exists or has changed.

**Why It Smells**: Misleading comments are worse than no comments. Developers trust comments and make wrong assumptions.

**Poor Example:**
```typescript
// Calculate tax based on state sales tax rates
// CA: 7.25%, NY: 8.52%, TX: 6.25%
function calculateTax(amount: number, zipCode: string): number {
  // Now using external tax API instead of hardcoded rates
  return taxService.calculateForZipCode(amount, zipCode);
}
```

**Better Approach:**
```typescript
function calculateTax(amount: number, zipCode: string): number {
  return taxService.calculateForZipCode(amount, zipCode);
}
```

**Refactoring**: Delete obsolete comments. Update or remove when code changes.

### C3: Redundant Comment

**Smell**: Comment says exactly what the code already clearly expresses.

**Why It Smells**: Adds noise without value. Can get out of sync with code.

**Poor Example:**
```java
// Get the user name
String userName = user.getName();

// Check if the user is active
if (user.isActive()) {
    // Send welcome email
    emailService.sendWelcomeEmail(user);
}
```

**Better Approach:**
```java
String userName = user.getName();

if (user.isActive()) {
    emailService.sendWelcomeEmail(user);
}
```

**Refactoring**: Remove comments that add no information beyond what code clearly states.

### C4: Poorly Written Comment

**Smell**: Comment is unclear, uses poor grammar, or is hard to understand.

**Why It Smells**: If a comment is worth writing, it's worth writing well. Unclear comments create confusion.

**Poor Example:**
```python
# this func does the thing with the stuff when the other thing happens
# dont use if your not sure what your doing!!!
def process_transaction(txn):
    # lots of complex logic here...
    pass
```

**Better Approach:**
```python
def process_transaction(transaction: Transaction) -> TransactionResult:
    """Process a financial transaction with idempotency guarantee.

    This function must be idempotent - calling it multiple times with
    the same transaction ID should not result in duplicate charges.

    Raises:
        InsufficientFundsError: Account balance too low
        InvalidTransactionError: Transaction failed validation
    """
    # Implementation...
    pass
```

**Refactoring**: Write comments as carefully as code. Use proper grammar and structure.

### C5: Commented-Out Code

**Smell**: Large blocks of commented-out code left in the codebase.

**Why It Smells**: Creates confusion about whether code is needed. Rots quickly as context is lost.

**Poor Example:**
```typescript
function processOrder(order: Order): void {
  validateOrder(order);
  // calculateShipping(order);
  // applyDiscount(order);
  calculateTotal(order);
  // sendConfirmationEmail(order);
  saveOrder(order);

  // Old implementation - keep for reference
  // const total = order.items.reduce((sum, item) => {
  //   return sum + (item.price * item.quantity);
  // }, 0);
  // order.total = total;
}
```

**Better Approach:**
```typescript
function processOrder(order: Order): void {
  validateOrder(order);
  calculateTotal(order);
  saveOrder(order);
}
```

**Refactoring**: Delete commented-out code. Trust version control to preserve history.

## Environment Smells

These smells relate to the broader development environment and build process.

### E1: Build Requires More Than One Step

**Smell**: Building the project requires multiple manual steps or complex commands.

**Why It Smells**: Increases friction, reduces automation, creates errors.

**Poor Example:**
```bash
# To build the project, developers must:
cd backend && npm install
cd ../frontend && npm install
cd ../shared && npm run build
cd ../backend && npm run build
cd ../frontend && npm run build
```

**Better Approach:**
```bash
# Single command build from project root
npm run build
```

```json
// package.json
{
  "scripts": {
    "build": "npm run build:shared && npm run build:backend && npm run build:frontend",
    "build:shared": "cd shared && npm run build",
    "build:backend": "cd backend && npm run build",
    "build:frontend": "cd frontend && npm run build"
  }
}
```

**Refactoring**: Create single-command build. Automate all setup steps.

### E2: Tests Require More Than One Step

**Smell**: Running tests requires multiple commands or manual setup.

**Why It Smells**: Developers skip testing if it's difficult. Reduces test execution frequency.

**Poor Example:**
```bash
# To run tests:
docker-compose up -d postgres
npm run migrate:test
npm run seed:test
npm test -- --config=test-config.json
docker-compose down
```

**Better Approach:**
```bash
# Single command that handles setup and teardown
npm test
```

**Refactoring**: Create test scripts that handle all setup/teardown. Use test containers.

## Function Smells

Function-level smells are some of the most common and easiest to spot.

### F1: Too Many Arguments

**Smell**: Function takes more than 3-4 arguments.

**Why It Smells**: Difficult to understand, test, and call. Often indicates function is doing too much.

**Poor Example:**
```python
def create_user(first_name, last_name, email, phone, address, city,
                state, zip_code, country, date_of_birth, ssn):
    """Too many parameters - hard to use and test"""
    user = User()
    user.first_name = first_name
    user.last_name = last_name
    # ... many more assignments
    return user
```

**Better Approach:**
```python
@dataclass
class UserRegistration:
    """Value object for user registration data"""
    first_name: str
    last_name: str
    email: str
    phone: str
    address: Address
    date_of_birth: date
    ssn: str

def create_user(registration: UserRegistration) -> User:
    """Single parameter object encapsulates related data"""
    user = User()
    user.first_name = registration.first_name
    user.last_name = registration.last_name
    user.email = registration.email
    # ... assign from structured object
    return user
```

**Refactoring**: Introduce Parameter Object. Group related parameters into a class.

### F2: Output Arguments

**Smell**: Function modifies arguments instead of returning values.

**Why It Smells**: Violates command-query separation. Confusing and error-prone.

**Poor Example:**
```java
// Modifies user object passed in - confusing!
public void appendFooter(StringBuilder report) {
    report.append("\n--- End of Report ---");
}

// Usage - unclear that report is modified
StringBuilder report = new StringBuilder();
generateReport(report);
appendFooter(report);  // Wait, this modifies report?
```

**Better Approach:**
```java
public String appendFooter(String report) {
    return report + "\n--- End of Report ---";
}

// Usage - clear that new value is returned
String report = generateReport();
report = appendFooter(report);
```

**Refactoring**: Return new values instead of modifying parameters. Use immutable objects.

### F3: Flag Arguments

**Smell**: Boolean arguments that control function behavior.

**Why It Smells**: Function does multiple things. Caller must know implementation details.

**Poor Example:**
```typescript
function bookConcert(customer: Customer, isPremium: boolean): Booking {
  if (isPremium) {
    // Premium booking logic with VIP access, better seats, etc.
    return createPremiumBooking(customer);
  } else {
    // Standard booking logic
    return createStandardBooking(customer);
  }
}

// Unclear at call site what 'true' means
const booking = bookConcert(customer, true);
```

**Better Approach:**
```typescript
function bookPremiumConcert(customer: Customer): Booking {
  return createPremiumBooking(customer);
}

function bookStandardConcert(customer: Customer): Booking {
  return createStandardBooking(customer);
}

// Clear intent
const booking = bookPremiumConcert(customer);
```

**Refactoring**: Split into multiple functions. Each does one thing clearly.

### F4: Dead Function

**Smell**: Function is never called.

**Why It Smells**: Adds confusion and maintenance burden. May represent incomplete refactoring.

**Poor Example:**
```python
def calculate_shipping_old(weight, distance):
    """Old shipping calculation - replaced by calculate_shipping_v2"""
    return weight * distance * 0.5

def calculate_shipping_v2(weight, distance, zone):
    """Current shipping calculation"""
    return weight * distance * zone.rate

# Only v2 is ever called, but old version remains
```

**Better Approach:**
```python
def calculate_shipping(weight: float, distance: float, zone: Zone) -> float:
    """Calculate shipping cost based on weight, distance, and zone"""
    return weight * distance * zone.rate
```

**Refactoring**: Delete unused functions. Trust version control for history.

### F5: Function Too Long

**Smell**: Function exceeds 20-30 lines or requires scrolling to see.

**Why It Smells**: Hard to understand, test, and maintain. Likely doing too many things.

**Poor Example:**
```java
public void processOrder(Order order) {
    // Validation (lines 1-15)
    if (order == null) throw new IllegalArgumentException("Order cannot be null");
    if (order.getItems().isEmpty()) throw new IllegalArgumentException("Order must have items");
    if (order.getCustomer() == null) throw new IllegalArgumentException("Customer required");
    // ... more validation

    // Calculate totals (lines 16-35)
    double subtotal = 0;
    for (Item item : order.getItems()) {
        subtotal += item.getPrice() * item.getQuantity();
    }
    double tax = subtotal * TAX_RATE;
    double shipping = calculateShipping(order);
    double total = subtotal + tax + shipping;
    // ... more calculations

    // Apply discounts (lines 36-55)
    if (order.getCustomer().isPremium()) {
        total *= 0.9;
    }
    // ... more discount logic

    // Save to database (lines 56-70)
    connection = dataSource.getConnection();
    statement = connection.prepareStatement("INSERT INTO orders...");
    // ... database code

    // Send notifications (lines 71-85)
    emailService.send(order.getCustomer().getEmail(), "Order confirmed");
    // ... notification code
}
```

**Better Approach:**
```java
public void processOrder(Order order) {
    validateOrder(order);
    OrderTotal total = calculateTotal(order);
    Order savedOrder = saveOrder(order, total);
    notifyCustomer(savedOrder);
}

private void validateOrder(Order order) {
    OrderValidator.validate(order);
}

private OrderTotal calculateTotal(Order order) {
    return orderCalculator.calculate(order);
}

private Order saveOrder(Order order, OrderTotal total) {
    return orderRepository.save(order.withTotal(total));
}

private void notifyCustomer(Order order) {
    notificationService.sendOrderConfirmation(order);
}
```

**Refactoring**: Extract Method repeatedly until each function is small and focused.

## General Smells

These are broader code quality issues that can appear anywhere.

### G1: Multiple Languages in One Source File

**Smell**: Mixing Java/Python with HTML, XML, SQL, etc. in the same file.

**Why It Smells**: Hard to syntax highlight, test, and maintain. Violates separation of concerns.

**Poor Example:**
```python
def generate_report(user_id):
    """Mixing SQL, HTML, and Python in one function"""

    # SQL embedded in Python
    query = """
        SELECT u.name, u.email, o.total, o.date
        FROM users u
        JOIN orders o ON u.id = o.user_id
        WHERE u.id = %s
        ORDER BY o.date DESC
    """
    results = db.execute(query, user_id)

    # HTML template embedded in Python
    html = """
    <html>
        <body>
            <h1>User Report</h1>
            <table>
    """

    for row in results:
        html += f"""
            <tr>
                <td>{row['name']}</td>
                <td>{row['email']}</td>
                <td>${row['total']}</td>
                <td>{row['date']}</td>
            </tr>
        """

    html += """
            </table>
        </body>
    </html>
    """
    return html
```

**Better Approach:**
```python
# data_access.py - SQL isolated
class UserRepository:
    def get_user_orders(self, user_id: int) -> List[OrderSummary]:
        return self.query(UserQueries.USER_ORDERS, user_id)

# templates/user_report.html - HTML isolated
{% extends "base.html" %}
{% block content %}
  <h1>User Report</h1>
  <table>
    {% for order in orders %}
      <tr>
        <td>{{ order.user_name }}</td>
        <td>{{ order.email }}</td>
        <td>${{ order.total }}</td>
        <td>{{ order.date }}</td>
      </tr>
    {% endfor %}
  </table>
{% endblock %}

# report_generator.py - Python orchestration
def generate_report(user_id: int) -> str:
    """Pure business logic - delegates to specialized components"""
    orders = user_repository.get_user_orders(user_id)
    return template_engine.render('user_report.html', orders=orders)
```

**Refactoring**: Separate languages into different files. Use templates, query builders, ORMs.

### G2: Obvious Behavior Is Unimplemented

**Smell**: Function doesn't do what you'd reasonably expect from its name.

**Why It Smells**: Violates Principle of Least Surprise. Causes bugs and confusion.

**Poor Example:**
```typescript
class DateRange {
  constructor(public start: Date, public end: Date) {}

  // Doesn't actually check if date is in range!
  includes(date: Date): boolean {
    return date >= this.start;  // Missing end date check
  }
}

// Bug waiting to happen
const q1 = new DateRange(new Date('2024-01-01'), new Date('2024-03-31'));
q1.includes(new Date('2024-12-31'));  // Returns true - wrong!
```

**Better Approach:**
```typescript
class DateRange {
  constructor(public start: Date, public end: Date) {}

  includes(date: Date): boolean {
    return date >= this.start && date <= this.end;
  }
}

// Works as expected
const q1 = new DateRange(new Date('2024-01-01'), new Date('2024-03-31'));
q1.includes(new Date('2024-12-31'));  // Returns false - correct!
```

**Refactoring**: Implement expected behavior. Test edge cases thoroughly.

### G3: Incorrect Behavior at Boundaries

**Smell**: Function fails on edge cases like null, empty, first/last, min/max.

**Why It Smells**: Boundary conditions are where bugs hide. Demonstrates incomplete thinking.

**Poor Example:**
```java
public int findMax(int[] numbers) {
    int max = numbers[0];  // Crashes on empty array!
    for (int i = 1; i < numbers.length; i++) {
        if (numbers[i] > max) {
            max = numbers[i];
        }
    }
    return max;
}
```

**Better Approach:**
```java
public OptionalInt findMax(int[] numbers) {
    if (numbers == null || numbers.length == 0) {
        return OptionalInt.empty();
    }

    int max = numbers[0];
    for (int i = 1; i < numbers.length; i++) {
        if (numbers[i] > max) {
            max = numbers[i];
        }
    }
    return OptionalInt.of(max);
}
```

**Refactoring**: Test boundaries explicitly. Handle null, empty, and extremes.

### G4: Duplication

**Smell**: Same code appears in multiple places.

**Why It Smells**: Violates DRY. Bug fixes require changes in multiple places. High maintenance cost.

**Poor Example:**
```python
def calculate_employee_bonus(employee):
    base_salary = employee.salary
    years_service = employee.years_of_service
    performance = employee.performance_rating

    if performance == "excellent":
        bonus = base_salary * 0.15 * (1 + years_service * 0.02)
    elif performance == "good":
        bonus = base_salary * 0.10 * (1 + years_service * 0.02)
    else:
        bonus = base_salary * 0.05 * (1 + years_service * 0.02)

    return bonus

def calculate_contractor_bonus(contractor):
    base_rate = contractor.hourly_rate * 2080  # Annual equivalent
    years_service = contractor.years_of_service
    performance = contractor.performance_rating

    # Duplicated calculation logic!
    if performance == "excellent":
        bonus = base_rate * 0.15 * (1 + years_service * 0.02)
    elif performance == "good":
        bonus = base_rate * 0.10 * (1 + years_service * 0.02)
    else:
        bonus = base_rate * 0.05 * (1 + years_service * 0.02)

    return bonus
```

**Better Approach:**
```python
def calculate_bonus(base_amount: float, years_service: int,
                   performance: str) -> float:
    """Calculate bonus using consistent formula across worker types"""
    performance_multipliers = {
        "excellent": 0.15,
        "good": 0.10,
        "satisfactory": 0.05
    }

    multiplier = performance_multipliers.get(performance, 0.05)
    seniority_factor = 1 + (years_service * 0.02)

    return base_amount * multiplier * seniority_factor

def calculate_employee_bonus(employee: Employee) -> float:
    return calculate_bonus(
        employee.salary,
        employee.years_of_service,
        employee.performance_rating
    )

def calculate_contractor_bonus(contractor: Contractor) -> float:
    annual_equivalent = contractor.hourly_rate * 2080
    return calculate_bonus(
        annual_equivalent,
        contractor.years_of_service,
        contractor.performance_rating
    )
```

**Refactoring**: Extract duplicated code into shared functions. Use template method pattern.

### G5: Code at Wrong Level of Abstraction

**Smell**: Implementation details mixed with high-level logic, or vice versa.

**Why It Smells**: Makes code hard to understand and change. Violates single level of abstraction.

**Poor Example:**
```typescript
class ReportGenerator {
  generateSalesReport(startDate: Date, endDate: Date): string {
    // HIGH LEVEL: Business logic
    const sales = this.getSalesBetween(startDate, endDate);

    // LOW LEVEL: File I/O details mixed in!
    const fs = require('fs');
    const path = '/tmp/report_' + Date.now() + '.txt';
    const stream = fs.createWriteStream(path);

    // HIGH LEVEL: Formatting
    let total = 0;
    for (const sale of sales) {
      total += sale.amount;
      // LOW LEVEL: Writing bytes
      stream.write(`${sale.id},${sale.amount}\n`);
    }

    stream.end();
    return path;
  }
}
```

**Better Approach:**
```typescript
class ReportGenerator {
  // HIGH LEVEL: Business orchestration
  generateSalesReport(startDate: Date, endDate: Date): Report {
    const sales = this.salesRepository.findBetween(startDate, endDate);
    return this.formatSalesReport(sales);
  }

  private formatSalesReport(sales: Sale[]): Report {
    const total = sales.reduce((sum, sale) => sum + sale.amount, 0);
    const lines = sales.map(sale => this.formatSaleLine(sale));
    return new Report(lines, total);
  }

  private formatSaleLine(sale: Sale): string {
    return `${sale.id},${sale.amount}`;
  }
}

// LOW LEVEL: File operations in separate class
class FileReportWriter {
  write(report: Report): string {
    const path = this.generatePath();
    const stream = fs.createWriteStream(path);

    for (const line of report.lines) {
      stream.write(line + '\n');
    }

    stream.end();
    return path;
  }

  private generatePath(): string {
    return `/tmp/report_${Date.now()}.txt`;
  }
}
```

**Refactoring**: Separate high-level business logic from low-level implementation details.

### G6: Too Much Information

**Smell**: Class or module exposes too many details that should be hidden.

**Why It Smells**: Tight coupling. Hard to change. Violates encapsulation.

**Poor Example:**
```java
// Exposes too much internal state
public class BankAccount {
    public double balance;
    public double interestRate;
    public int transactionCount;
    public List<Transaction> transactions;
    public Date lastModified;
    public String accountType;
    public boolean isLocked;

    // All fields public - anyone can modify anything!
}

// Consumers depend on internal structure
account.balance += 100;  // No validation, no audit trail
account.transactionCount++;  // Must remember to update manually
account.lastModified = new Date();  // Must remember this too
```

**Better Approach:**
```java
public class BankAccount {
    private double balance;
    private final List<Transaction> transactions;
    private Date lastModified;

    // Controlled interface - encapsulates rules
    public void deposit(double amount) {
        if (amount <= 0) {
            throw new IllegalArgumentException("Deposit must be positive");
        }

        this.balance += amount;
        this.transactions.add(new Transaction(DEPOSIT, amount));
        this.lastModified = new Date();
    }

    // Provide only what's needed
    public double getBalance() {
        return balance;
    }

    // No direct access to internal collections
    public List<Transaction> getTransactionHistory() {
        return Collections.unmodifiableList(transactions);
    }
}
```

**Refactoring**: Hide data. Expose minimal interface. Use methods to control access.

### G7: Dead Code

**Smell**: Code that is never executed - unreachable conditions, unused variables/methods.

**Why It Smells**: Confusing. Wastes maintenance effort. May indicate incomplete refactoring.

**Poor Example:**
```python
def process_payment(amount, method):
    if method == "credit_card":
        return process_credit_card(amount)
    elif method == "paypal":
        return process_paypal(amount)
    elif method == "bitcoin":
        # Bitcoin support was removed but code remains
        return process_bitcoin(amount)
    else:
        return process_credit_card(amount)

# This function is never called anymore
def process_bitcoin(amount):
    """Bitcoin payment processing - DEPRECATED"""
    # ... implementation
    pass

# Variable assigned but never used
def calculate_tax(amount):
    state_tax = amount * 0.05
    federal_tax = amount * 0.15
    total_tax = federal_tax  # state_tax is dead code
    return total_tax
```

**Better Approach:**
```python
def process_payment(amount: float, method: str) -> PaymentResult:
    processors = {
        "credit_card": process_credit_card,
        "paypal": process_paypal
    }

    processor = processors.get(method, process_credit_card)
    return processor(amount)

def calculate_tax(amount: float) -> float:
    """Calculate total tax (federal only, state tax deprecated)"""
    FEDERAL_TAX_RATE = 0.15
    return amount * FEDERAL_TAX_RATE
```

**Refactoring**: Delete dead code ruthlessly. Trust version control.

### G8: Vertical Separation

**Smell**: Variables and functions are declared far from where they are used.

**Why It Smells**: Forces reader to jump around. Breaks narrative flow.

**Poor Example:**
```java
public class OrderProcessor {
    private static final double TAX_RATE = 0.08;
    private static final double SHIPPING_RATE = 5.99;

    // 100 lines of other code...

    private EmailService emailService;
    private PaymentGateway paymentGateway;

    // 50 more lines...

    public void processOrder(Order order) {
        // Uses TAX_RATE declared 150 lines above
        double tax = order.getSubtotal() * TAX_RATE;
        // Uses SHIPPING_RATE declared 150 lines above
        double shipping = SHIPPING_RATE;
        // Uses fields declared 50 lines above
        paymentGateway.charge(order.getTotal());
        emailService.send(order.getCustomer());
    }
}
```

**Better Approach:**
```java
public class OrderProcessor {
    private final EmailService emailService;
    private final PaymentGateway paymentGateway;

    public void processOrder(Order order) {
        final double TAX_RATE = 0.08;
        final double SHIPPING_RATE = 5.99;

        double tax = order.getSubtotal() * TAX_RATE;
        double shipping = SHIPPING_RATE;

        paymentGateway.charge(order.getTotal());
        emailService.send(order.getCustomer());
    }
}
```

**Refactoring**: Declare variables close to usage. Keep related code together.

### G9: Inconsistency

**Smell**: Similar things done in different ways throughout codebase.

**Why It Smells**: Creates confusion. Readers can't build mental model.

**Poor Example:**
```python
# Three different patterns for the same concept!

def get_user_by_id(user_id):
    """Pattern 1: get_by_id"""
    return db.query(User).filter(id=user_id).first()

def find_product(product_id):
    """Pattern 2: find"""
    return db.query(Product).filter(id=product_id).first()

def retrieve_order_by_identifier(order_id):
    """Pattern 3: retrieve_by_identifier"""
    return db.query(Order).filter(id=order_id).first()
```

**Better Approach:**
```python
# Consistent pattern across all entities

def get_user_by_id(user_id: int) -> Optional[User]:
    return db.query(User).filter(id=user_id).first()

def get_product_by_id(product_id: int) -> Optional[Product]:
    return db.query(Product).filter(id=product_id).first()

def get_order_by_id(order_id: int) -> Optional[Order]:
    return db.query(Order).filter(id=order_id).first()
```

**Refactoring**: Establish conventions and follow them consistently.

### G10: Clutter

**Smell**: Code contains things that serve no purpose - empty constructors, unused variables, redundant comments.

**Why It Smells**: Obscures intent. Forces readers to determine what matters.

**Poor Example:**
```typescript
class UserService {
  // Default constructor - completely unnecessary
  constructor() {
    // Initialize nothing
  }

  /**
   * Gets a user
   * @param id - the user id
   * @returns the user
   */
  getUser(id: number): User {
    // Get the user from the database
    const user = this.userRepository.findById(id);
    // Return the user
    return user;
  }

  // Unused helper method
  private formatName(first: string, last: string): string {
    return `${first} ${last}`;
  }
}
```

**Better Approach:**
```typescript
class UserService {
  getUser(id: number): User {
    return this.userRepository.findById(id);
  }
}
```

**Refactoring**: Remove everything that doesn't serve a purpose.

## Name Smells

Names are critical for code comprehension. Bad names force readers to build mental mappings.

### N1: Choose Descriptive Names

**Smell**: Names don't describe what the variable/function does.

**Why It Smells**: Forces readers to discover meaning from context. Slows comprehension.

**Poor Example:**
```python
def proc(d):
    t = 0
    for i in d:
        t += i.a * i.q
    return t * 1.08
```

**Better Approach:**
```python
def calculate_order_total(line_items: List[LineItem]) -> float:
    """Calculate total including tax for all line items"""
    TAX_RATE = 1.08

    subtotal = sum(item.price * item.quantity for item in line_items)
    return subtotal * TAX_RATE
```

**Refactoring**: Use names that reveal intent completely.

### N2: Choose Names at Appropriate Level of Abstraction

**Smell**: Names reflect implementation instead of abstraction.

**Why It Smells**: Names couple to implementation, breaking abstraction.

**Poor Example:**
```java
// Name reveals MySQL implementation
public interface MySQLUserRepository {
    User findByPrimaryKey(int id);
}

// Caller is coupled to database choice
MySQLUserRepository repo = new MySQLUserRepositoryImpl();
```

**Better Approach:**
```java
// Name reflects abstraction
public interface UserRepository {
    User findById(int id);
}

// Caller is decoupled from implementation
UserRepository repo = new DatabaseUserRepository();
```

**Refactoring**: Name things for what they represent, not how they're implemented.

### N3: Use Standard Nomenclature Where Possible

**Smell**: Inventing new terms when standard ones exist.

**Why It Smells**: Forces learning of project-specific vocabulary. Reduces code portability.

**Poor Example:**
```typescript
// Non-standard pattern names
class ThingMaker {
  createThing(): Thing { return new Thing(); }
}

class StuffBuilder {
  makeStuff(): Stuff { return new Stuff(); }
}

class ItemGenerator {
  generateItem(): Item { return new Item(); }
}
```

**Better Approach:**
```typescript
// Standard Factory pattern
class ThingFactory {
  create(): Thing { return new Thing(); }
}

class StuffFactory {
  create(): Stuff { return new Stuff(); }
}

class ItemFactory {
  create(): Item { return new Item(); }
}
```

**Refactoring**: Use standard pattern names (Factory, Builder, Observer, etc.).

### N4: Unambiguous Names

**Smell**: Names can be interpreted multiple ways.

**Why It Smells**: Creates confusion and bugs from misunderstanding.

**Poor Example:**
```python
# Does this filter results or return a filter object?
def filter(self, criteria):
    pass

# Does this return clipped results or modify them?
def clip(values, max_value):
    pass

# Does this return last element or check if list has a last element?
def last(items):
    pass
```

**Better Approach:**
```python
def filter_by_criteria(self, criteria: Criteria) -> List[Result]:
    """Return results matching criteria"""
    pass

def clip_values_at_maximum(values: List[int], max_value: int) -> List[int]:
    """Return new list with values capped at max_value"""
    pass

def get_last_item(items: List[T]) -> T:
    """Return the last item in the list"""
    pass
```

**Refactoring**: Choose names with single, clear interpretation.

### N5: Use Long Names for Long Scopes

**Smell**: Short cryptic names used in large scopes; long names in tiny scopes.

**Why It Smells**: Violates optimal name length principle - short scope = short name, long scope = long name.

**Poor Example:**
```java
// Class field - large scope but cryptic name
private int x;

public void calculateInterest() {
    // Tiny scope but verbose name
    for (int accountIndexInListOfAccounts = 0;
         accountIndexInListOfAccounts < accounts.size();
         accountIndexInListOfAccounts++) {
        // Uses cryptic 'x' field from large scope
        accounts.get(accountIndexInListOfAccounts).addInterest(x);
    }
}
```

**Better Approach:**
```java
// Class field - large scope with descriptive name
private int annualInterestRatePercent;

public void calculateInterest() {
    // Tiny scope with short name
    for (int i = 0; i < accounts.size(); i++) {
        accounts.get(i).addInterest(annualInterestRatePercent);
    }
}
```

**Refactoring**: Long names for long scopes (fields, globals). Short names for short scopes (loop variables).

## Test Smells

Tests have their own set of smells that indicate problems.

### T1: Insufficient Tests

**Smell**: Test suite doesn't cover important cases or edge conditions.

**Why It Smells**: False confidence. Bugs in production that should have been caught.

**Poor Example:**
```python
def test_calculate_discount():
    """Only tests happy path"""
    price = 100
    discount_rate = 0.1
    result = calculate_discount(price, discount_rate)
    assert result == 90

# Missing tests:
# - Negative prices
# - Discount rate > 1
# - Zero values
# - Null/None inputs
# - Very large numbers
```

**Better Approach:**
```python
class TestCalculateDiscount:
    def test_normal_discount(self):
        assert calculate_discount(100, 0.1) == 90

    def test_no_discount(self):
        assert calculate_discount(100, 0) == 100

    def test_full_discount(self):
        assert calculate_discount(100, 1.0) == 0

    def test_negative_price_raises_error(self):
        with pytest.raises(ValueError):
            calculate_discount(-100, 0.1)

    def test_discount_rate_over_one_raises_error(self):
        with pytest.raises(ValueError):
            calculate_discount(100, 1.5)

    def test_zero_price(self):
        assert calculate_discount(0, 0.1) == 0
```

**Refactoring**: Test boundaries, edge cases, and error conditions systematically.

### T2: Use Coverage Tool

**Smell**: Don't know what percentage of code is tested.

**Why It Smells**: Can't identify untested code. No objective quality metric.

**Poor Example:**
```bash
# Just running tests without coverage
pytest tests/
```

**Better Approach:**
```bash
# Run with coverage reporting
pytest --cov=src --cov-report=html --cov-fail-under=90

# Review HTML report to find untested code
open htmlcov/index.html
```

**Refactoring**: Always run tests with coverage. Aim for >85% coverage.

### T3: Don't Skip Trivial Tests

**Smell**: Not testing simple functions because they're "too easy to break."

**Why It Smells**: Trivial code can break. Tests document expected behavior.

**Poor Example:**
```typescript
// No test because "it's obvious"
class Money {
  add(other: Money): Money {
    return new Money(this.amount + other.amount);
  }
}
```

**Better Approach:**
```typescript
describe('Money', () => {
  it('should add two money amounts', () => {
    const m1 = new Money(10);
    const m2 = new Money(20);
    expect(m1.add(m2).amount).toBe(30);
  });

  it('should handle adding zero', () => {
    const m1 = new Money(10);
    const m2 = new Money(0);
    expect(m1.add(m2).amount).toBe(10);
  });
});
```

**Refactoring**: Test everything that could possibly break.

### T4: Ignored Test

**Smell**: Tests marked as skipped or ignored.

**Why It Smells**: Technical debt. May indicate deeper problems.

**Poor Example:**
```java
@Test
@Ignore("Fails intermittently - fix later")
public void testConcurrentAccess() {
    // Test that sometimes fails due to race condition
}

@Test
@Ignore("Takes too long")
public void testLargeDataSet() {
    // Test skipped due to performance
}
```

**Better Approach:**
```java
@Test
public void testConcurrentAccess() {
    // Fixed race condition with proper synchronization
    CountDownLatch latch = new CountDownLatch(10);
    // ... proper concurrent test
}

@Test
@Category(PerformanceTests.class)
public void testLargeDataSet() {
    // Moved to separate performance test suite
    // Runs in CI but not on every dev commit
}
```

**Refactoring**: Fix ignored tests or move to appropriate test category. Never commit ignored tests.

### T5: Test Boundary Conditions

**Smell**: Tests only check typical values, not edge cases.

**Why It Smells**: Bugs hide at boundaries. Off-by-one errors are common.

**Poor Example:**
```python
def test_is_valid_age():
    """Only tests middle values"""
    assert is_valid_age(25) == True
    assert is_valid_age(50) == True
```

**Better Approach:**
```python
class TestIsValidAge:
    # Test boundaries explicitly
    def test_minimum_valid_age(self):
        assert is_valid_age(0) == True

    def test_below_minimum_age(self):
        assert is_valid_age(-1) == False

    def test_maximum_valid_age(self):
        assert is_valid_age(120) == True

    def test_above_maximum_age(self):
        assert is_valid_age(121) == False

    # Test typical values too
    def test_typical_age(self):
        assert is_valid_age(35) == True
```

**Refactoring**: Explicitly test min, max, just below min, just above max.

### T6: Tests Should Be Fast

**Smell**: Test suite takes minutes or hours to run.

**Why It Smells**: Developers skip running tests. Slow feedback loop.

**Poor Example:**
```java
@Test
public void testUserWorkflow() {
    // Slow integration test on every run
    startRealDatabase();
    Thread.sleep(5000);  // Wait for startup

    createUser();
    Thread.sleep(1000);

    loginUser();
    Thread.sleep(1000);

    // ... many more slow operations
}
```

**Better Approach:**
```java
// Fast unit test with mocks
@Test
public void testUserWorkflow() {
    UserService service = new UserService(mockDatabase);

    User user = service.createUser("test@example.com");
    LoginResult result = service.login(user.email, "password");

    assertTrue(result.isSuccess());
}

// Separate slow integration test
@Test
@Category(IntegrationTests.class)
public void testUserWorkflowIntegration() {
    // Full integration test runs in CI, not locally
}
```

**Refactoring**: Keep unit tests fast (<0.1s each). Move slow tests to integration suite.

## When to Refactor vs. When to Tolerate

Not every smell requires immediate refactoring. Consider:

### Refactor When:
- Smell is in code you're actively changing
- Smell is causing bugs or confusion
- Smell is in critical path code
- Team agrees it's a problem
- You have tests to verify behavior
- Change is low-risk

### Tolerate When:
- Code is stable and rarely changes
- Refactoring risk exceeds smell cost
- No tests exist and code is complex
- Code will be replaced soon
- Team lacks domain knowledge
- Time constraints are severe

### The Boy Scout Rule

**Always leave code cleaner than you found it.**

Even if you can't fix all smells, fix one small thing each time you touch code. This creates continuous improvement without dedicated refactoring time.

## Quick Reference Checklist

Use this checklist during code reviews:

### Comment Smells
- [ ] No change history or authorship in comments
- [ ] Comments are up-to-date with code
- [ ] No redundant comments that just restate code
- [ ] Comments explain WHY, not WHAT
- [ ] No commented-out code blocks

### Function Smells
- [ ] Functions have ≤3 parameters
- [ ] No boolean flag arguments
- [ ] Functions are <20-30 lines
- [ ] Each function does one thing
- [ ] No dead/unreachable code
- [ ] No output arguments

### General Smells
- [ ] No duplicated code
- [ ] Each file uses one primary language
- [ ] Variables declared close to usage
- [ ] Consistent naming and patterns
- [ ] No unnecessary clutter
- [ ] Proper abstraction levels

### Name Smells
- [ ] Names reveal intent clearly
- [ ] No ambiguous names
- [ ] Standard nomenclature used
- [ ] Scope-appropriate name length
- [ ] Names match abstraction level

### Test Smells
- [ ] Tests cover edge cases and boundaries
- [ ] No ignored or skipped tests
- [ ] Tests run quickly (<0.1s per unit test)
- [ ] Coverage tools used (>85% coverage)
- [ ] Even trivial functions tested

## Related Guides

- **REFACTORING_CATALOG.md**: Specific techniques to fix each smell
- **REFACTORING_WORKFLOW.md**: Safe process for applying refactorings
- **01-foundations/VARIABLE_NAMING.md**: Deep dive on naming
- **01-foundations/FUNCTIONS_AND_ROUTINES.md**: Function design principles
- **04-quality-through-testing/UNIT_TESTING_PRINCIPLES.md**: Test quality

## Summary

Code smells are your early warning system for design problems. Learn to recognize them quickly:

**Most Critical Smells to Fix:**
1. Duplication (violation of DRY)
2. Long functions (doing too much)
3. Too many parameters (poor abstraction)
4. Poor names (obscures intent)
5. Dead code (maintenance burden)

**Key Principles:**
- Smells indicate deeper problems
- Not all smells need immediate fixing
- Fix smells in code you're changing (Boy Scout Rule)
- Use smells as objective code review criteria
- Build smell recognition into development habits

Start with one smell category. Practice recognizing it in code reviews. Once it becomes automatic, add another. Over time, you'll develop an intuitive sense for code quality that guides you toward cleaner designs from the start.
