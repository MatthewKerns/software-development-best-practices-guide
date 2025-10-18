# Code Formatting: The Visual Foundation of Maintainable Code

## Overview

Code formatting is the first thing developers see when they open a file. Poor formatting creates immediate friction—code becomes harder to scan, comprehension slows, and patterns disappear into visual noise. Good formatting, by contrast, makes code structure obvious, reveals logical groupings, and enables rapid comprehension.

This comprehensive guide synthesizes formatting wisdom from industry-leading sources and provides practical, actionable guidance for creating visually clear and maintainable code.

**"Any fool can write code that a computer can understand. Good programmers write code that humans can understand."** — Martin Fowler

## Why Formatting Matters

### The Cost of Poor Formatting

Poor formatting creates measurable costs:

**Comprehension Time**: Studies show that developers spend 60-70% of their time reading code. Inconsistent formatting forces readers to constantly adjust their mental parsing, dramatically slowing comprehension.

**Bug Introduction**: Misleading indentation hides logical structure. Visual clutter obscures important details. These formatting problems directly contribute to bugs that could have been prevented by clearer presentation.

**Review Friction**: Code reviews devolve into style debates. Reviewers waste time discussing formatting instead of logic. Mixed styles create cognitive dissonance that distracts from substantive issues.

**Merge Conflicts**: Inconsistent formatting across team members creates unnecessary merge conflicts. Whitespace changes pollute diffs, making it harder to review actual logic changes.

**Onboarding Burden**: New team members struggle to read unfamiliar formatting styles. Time is wasted establishing local conventions instead of following established standards.

### The Benefits of Good Formatting

Good formatting provides:
- **Instant Comprehension**: Structure is obvious at a glance
- **Error Prevention**: Misleading indentation is impossible
- **Efficient Reviews**: Reviewers focus on logic, not style
- **Clean Diffs**: Only meaningful changes appear in version control
- **Team Velocity**: No time wasted on style debates
- **Professional Appearance**: Code looks intentional and crafted

## Source Materials

This guide synthesizes principles from:

- **Code Complete 2** by Steve McConnell (Chapter 31: "Layout and Style")
  - Fundamental theorem of formatting
  - Layout objectives
  - Formatting techniques
  - Layout styles

- **Clean Code** by Robert C. Martin (Chapter 5: "Formatting")
  - Vertical formatting principles
  - Horizontal formatting principles
  - Team rules
  - The purpose of formatting

## The Fundamental Theorem of Formatting (Code Complete 2)

### The Core Principle

**Theorem**: Good visual layout shows the logical structure of a program.

**Corollary**: If formatting doesn't enhance comprehension, it's wrong.

### Layout Objectives

**1. Accurately represent the logical structure of the code**
**2. Consistently represent the logical structure**
**3. Improve readability**
**4. Withstand modifications**

```python
# Poor: Formatting hides structure
def process_order(order):
    if order.valid:
        total=order.subtotal
        if order.has_discount:
            total=total-order.discount
        if order.has_tax: total=total+order.tax
        order.total=total
    return order

# Good: Formatting reveals structure
def process_order(order):
    if not order.valid:
        return order

    total = order.subtotal

    if order.has_discount:
        total -= order.discount

    if order.has_tax:
        total += order.tax

    order.total = total
    return order
```

## Vertical Formatting (Clean Code)

### The Newspaper Metaphor

**Principle**: Code should read like a well-written newspaper article.

**Top**: High-level concepts (headlines)
**Middle**: Details and implementation
**Bottom**: Low-level utilities

```typescript
// Newspaper structure: High to low level
class OrderProcessor {
    // High-level public API (headlines)
    public processOrder(order: Order): ProcessedOrder {
        this.validateOrder(order);
        const calculatedOrder = this.calculateTotals(order);
        const chargedOrder = this.chargePayment(calculatedOrder);
        return this.fulfillOrder(chargedOrder);
    }

    // Mid-level implementation (story details)
    private validateOrder(order: Order): void {
        this.validateCustomer(order.customer);
        this.validateItems(order.items);
        this.validateShippingAddress(order.shippingAddress);
    }

    private calculateTotals(order: Order): Order {
        const subtotal = this.calculateSubtotal(order.items);
        const tax = this.calculateTax(subtotal);
        const shipping = this.calculateShipping(order);
        return { ...order, subtotal, tax, shipping };
    }

    // Low-level utilities (fine print)
    private calculateSubtotal(items: Item[]): number {
        return items.reduce((sum, item) => sum + item.price * item.quantity, 0);
    }

    private calculateTax(subtotal: number): number {
        return subtotal * TAX_RATE;
    }
}
```

### Vertical Openness (Blank Lines)

**Principle**: Use blank lines to separate groups of related lines (visual paragraphs).

**Poor Example - No Visual Separation:**
```python
# Cramped: Everything runs together
def generate_report(user_id):
    user = fetch_user(user_id)
    orders = fetch_orders(user_id)
    total_spent = sum(order.total for order in orders)
    average_order = total_spent / len(orders) if orders else 0
    report = {
        'user': user,
        'order_count': len(orders),
        'total_spent': total_spent,
        'average_order': average_order
    }
    return report
```

**Good Example - Visual Paragraphs:**
```python
# Clear: Related lines grouped visually
def generate_report(user_id):
    # Data fetching
    user = fetch_user(user_id)
    orders = fetch_orders(user_id)

    # Calculations
    total_spent = sum(order.total for order in orders)
    average_order = total_spent / len(orders) if orders else 0

    # Report assembly
    report = {
        'user': user,
        'order_count': len(orders),
        'total_spent': total_spent,
        'average_order': average_order
    }

    return report
```

### Vertical Density (Related Code Close Together)

**Principle**: Lines of code that are tightly related should appear close together.

**Poor Example - Related Code Scattered:**
```java
public class User {
    private String name;

    public String getName() {
        return name;
    }

    private String email;

    public void setName(String name) {
        this.name = name;
    }

    private int age;

    public String getEmail() {
        return email;
    }

    public void setEmail(String email) {
        this.email = email;
    }
    // Fields and methods scattered randomly
}
```

**Good Example - Related Code Grouped:**
```java
public class User {
    // Fields grouped together
    private String name;
    private String email;
    private int age;

    // Name accessors grouped
    public String getName() {
        return name;
    }

    public void setName(String name) {
        this.name = name;
    }

    // Email accessors grouped
    public String getEmail() {
        return email;
    }

    public void setEmail(String email) {
        this.email = email;
    }

    // Age accessors grouped
    public int getAge() {
        return age;
    }

    public void setAge(int age) {
        this.age = age;
    }
}
```

### Vertical Distance

**Principle**: Concepts that are closely related should be kept vertically close to each other.

**1. Variable Declarations**: Close to their usage

```python
# Poor: Variable far from usage
def process_data():
    user_count = 0
    total_revenue = 0
    active_sessions = 0

    # ... 50 lines of code ...

    # user_count finally used here
    print(f"Users: {user_count}")

# Good: Variable near usage
def process_data():
    # ... code ...

    user_count = count_users()
    print(f"Users: {user_count}")
```

**2. Related Functions**: Close to each other

```typescript
// Poor: Helper function far from caller
class DataProcessor {
    public processData(data: Data[]): Result {
        const validated = this.validateData(data);
        return this.transformData(validated);
    }

    // ... 100 lines of unrelated code ...

    private validateData(data: Data[]): Data[] {
        // Validation logic
    }
}

// Good: Helper close to caller
class DataProcessor {
    public processData(data: Data[]): Result {
        const validated = this.validateData(data);
        return this.transformData(validated);
    }

    private validateData(data: Data[]): Data[] {
        // Validation logic - immediately after usage
    }

    private transformData(data: Data[]): Result {
        // Transform logic - follows validation
    }
}
```

**3. Caller Before Callee**: Functions should appear in order of calls

```python
# Good: Top-down ordering (caller before callee)
def main():
    data = load_data()
    processed = process_data(data)
    save_results(processed)

def load_data():
    """Load data - called first, appears first."""
    return fetch_from_database()

def process_data(data):
    """Process data - called second, appears second."""
    return transform(data)

def save_results(results):
    """Save results - called last, appears last."""
    write_to_file(results)

# Natural reading order: top to bottom matches execution order
```

### Vertical File Length

**Research-Based Guidelines**:
- **Typical**: 200-500 lines
- **Small**: Under 200 lines (preferred)
- **Large**: 500-1000 lines (acceptable)
- **Very Large**: Over 1000 lines (consider splitting)

**Why smaller files?**
- Easier to understand
- Easier to find things
- Easier to test
- Less merge conflicts

```python
# Too large: 2000-line file
# user_management.py (2000 lines)
class UserService:
    # 500 lines of user CRUD
    # 300 lines of authentication
    # 400 lines of permissions
    # 300 lines of notifications
    # 500 lines of analytics

# Better: Split into focused files
# user_service.py (200 lines)
class UserService:
    # Core user CRUD operations

# authentication_service.py (150 lines)
class AuthenticationService:
    # Authentication logic

# permission_service.py (180 lines)
class PermissionService:
    # Permission checking

# notification_service.py (120 lines)
class NotificationService:
    # User notifications

# user_analytics.py (100 lines)
class UserAnalytics:
    # Analytics tracking
```

## Horizontal Formatting (Clean Code)

### Line Length

**Research-Based Guideline**: 80-120 characters maximum

**Historical Context**: 80 characters comes from punch card era, but remains useful
**Modern Practice**: 100-120 characters accommodates modern screens
**Team Choice**: Pick one and enforce it

```python
# Too long: Requires horizontal scrolling
def calculate_monthly_payment(principal_amount, annual_interest_rate, loan_term_in_months, include_insurance, insurance_rate):
    return (principal_amount * (annual_interest_rate / 12)) / (1 - (1 + (annual_interest_rate / 12)) ** -loan_term_in_months) + (principal_amount * insurance_rate if include_insurance else 0)

# Good: Broken into readable lines (under 100 chars)
def calculate_monthly_payment(
    principal_amount,
    annual_interest_rate,
    loan_term_in_months,
    include_insurance,
    insurance_rate
):
    monthly_rate = annual_interest_rate / 12
    payment = (principal_amount * monthly_rate) / (
        1 - (1 + monthly_rate) ** -loan_term_in_months
    )

    if include_insurance:
        payment += principal_amount * insurance_rate

    return payment
```

### Horizontal Openness and Density

**Principle**: Use horizontal whitespace to associate strongly related things and disassociate weakly related things.

**Assignment Operators**: Space around = emphasizes both sides

```java
// Poor: No spacing
int x=5;
String name="John";
double price=19.99;

// Good: Space around assignment
int x = 5;
String name = "John";
double price = 19.99;
```

**Binary Operators**: Space around operators shows precedence

```typescript
// Poor: No spacing or consistent spacing
const total=subtotal+tax+shipping;
const area = width*height;
const result = a*b + c*d;

// Good: Space around all binary operators
const total = subtotal + tax + shipping;
const area = width * height;
const result = (a * b) + (c * d);
```

**Function Calls**: No space between function name and parenthesis

```python
# Poor: Space between function and parenthesis
calculate_total (items, tax_rate)
send_email ("user@example.com", "Subject", "Body")

# Good: No space (function and args are tightly related)
calculate_total(items, tax_rate)
send_email("user@example.com", "Subject", "Body")
```

**Function Parameters**: Space after commas

```java
// Poor: No spacing between parameters
public void createUser(String name,String email,int age,boolean active){

}

// Good: Space after commas for readability
public void createUser(String name, String email, int age, boolean active) {

}
```

### Horizontal Alignment

**Modern Consensus**: Don't artificially align declarations

**Anti-Pattern (Old Style):**
```python
# Don't do this: Artificial alignment
first_name          = "John"
last_name           = "Doe"
age                 = 30
email_address       = "john@example.com"
phone_number        = "555-1234"
# Looks nice but hard to maintain
```

**Better (Modern Style):**
```python
# Do this: Natural alignment
first_name = "John"
last_name = "Doe"
age = 30
email_address = "john@example.com"
phone_number = "555-1234"
# Easy to maintain, focus on content
```

**Why avoid artificial alignment?**
- Maintenance burden (adding long variable breaks alignment)
- Draws eye to whitespace, not content
- Hard to maintain in teams
- Creates noisy diffs

### Indentation (Code Complete 2)

**Purpose**: Show logical structure and nesting level

**Standard Indentation**: 2-4 spaces per level

```python
# 4-space indentation (Python standard)
def process_order(order):
    if order.is_valid():
        total = order.subtotal

        if order.has_discount:
            discount = calculate_discount(order)
            total -= discount

        if order.has_tax:
            tax = calculate_tax(total)
            total += tax

        order.total = total

    return order
```

```typescript
// 2-space indentation (TypeScript/JavaScript common)
function processOrder(order: Order): Order {
  if (order.isValid()) {
    let total = order.subtotal;

    if (order.hasDiscount) {
      const discount = calculateDiscount(order);
      total -= discount;
    }

    if (order.hasTax) {
      const tax = calculateTax(total);
      total += tax;
    }

    order.total = total;
  }

  return order;
}
```

**Tabs vs Spaces**: Use spaces (tabs display inconsistently across editors)

**Never mix tabs and spaces** (causes Python syntax errors, visual inconsistency)

### Breaking Long Lines (Code Complete 2)

**Techniques for breaking long lines:**

**1. Break after commas**

```java
// Good: Break after commas in parameter lists
public Order createOrder(
    String customerId,
    List<OrderItem> items,
    Address shippingAddress,
    PaymentMethod paymentMethod,
    ShippingOption shippingOption
) {
    // Implementation
}
```

**2. Break before operators**

```python
# Good: Break before operators
total_cost = (
    base_price
    + tax_amount
    + shipping_cost
    + handling_fee
    - discount_amount
)
```

**3. Indent continuation lines**

```typescript
// Good: Indent continuation lines
const userDisplayName = user.firstName
    + " "
    + user.middleName
    + " "
    + user.lastName;

// Or use template literals
const userDisplayName = `${user.firstName} ${user.middleName} ${user.lastName}`;
```

**4. Break at natural boundaries**

```python
# Good: Break at natural logical boundaries
if (
    user.is_authenticated
    and user.has_permission('admin')
    and user.account.is_active
    and not user.account.is_suspended
):
    grant_admin_access(user)
```

## Formatting Control Structures

### If Statements

**Basic Structure:**

```python
# Python: Clear indentation
if condition:
    do_something()
    do_something_else()
elif other_condition:
    do_other_thing()
else:
    do_default()
```

```java
// Java: Braces on same line (K&R style)
if (condition) {
    doSomething();
    doSomethingElse();
} else if (otherCondition) {
    doOtherThing();
} else {
    doDefault();
}
```

**Complex Conditions:** Break into multiple lines

```typescript
// Poor: Long condition on one line
if (user.isAuthenticated && user.hasPermission('admin') && user.accountStatus === 'active' && !user.isSuspended) {
    // Hard to read
}

// Good: Break complex conditions
if (
    user.isAuthenticated
    && user.hasPermission('admin')
    && user.accountStatus === 'active'
    && !user.isSuspended
) {
    // Clear and scannable
}

// Better: Extract to well-named function
if (userCanAccessAdminPanel(user)) {
    // Self-documenting
}
```

### Loops

**For Loops:**

```python
# Python: Clean iteration
for item in items:
    process_item(item)

# With index
for index, item in enumerate(items):
    print(f"{index}: {item}")

# Nested loops: Clear indentation
for user in users:
    for order in user.orders:
        process_order(order)
```

```java
// Java: Traditional for loop
for (int i = 0; i < items.size(); i++) {
    Item item = items.get(i);
    processItem(item);
}

// Enhanced for loop
for (Item item : items) {
    processItem(item);
}
```

**While Loops:**

```typescript
// TypeScript: While loop formatting
while (hasMoreData) {
    const data = fetchNextBatch();
    processData(data);

    if (isComplete(data)) {
        break;
    }
}
```

### Switch/Match Statements

```java
// Java: Switch formatting
switch (orderStatus) {
    case PENDING:
        processPendingOrder(order);
        break;

    case PROCESSING:
        continueProcessing(order);
        break;

    case SHIPPED:
        trackShipment(order);
        break;

    case DELIVERED:
        confirmDelivery(order);
        break;

    default:
        handleUnknownStatus(order);
        break;
}
```

```python
# Python 3.10+: Match statement
match order_status:
    case "PENDING":
        process_pending_order(order)

    case "PROCESSING":
        continue_processing(order)

    case "SHIPPED":
        track_shipment(order)

    case "DELIVERED":
        confirm_delivery(order)

    case _:
        handle_unknown_status(order)
```

### Try-Catch Blocks

```java
// Java: Try-catch formatting
try {
    processPayment(order);
    updateInventory(order);
    sendConfirmation(order);
} catch (PaymentException e) {
    logger.error("Payment failed", e);
    refundOrder(order);
} catch (InventoryException e) {
    logger.error("Inventory update failed", e);
    rollbackPayment(order);
} finally {
    releaseResources();
}
```

```python
# Python: Try-except formatting
try:
    process_payment(order)
    update_inventory(order)
    send_confirmation(order)
except PaymentException as e:
    logger.error(f"Payment failed: {e}")
    refund_order(order)
except InventoryException as e:
    logger.error(f"Inventory update failed: {e}")
    rollback_payment(order)
finally:
    release_resources()
```

## Formatting Classes and Functions

### Class Layout Order (Code Complete 2)

**Standard ordering (most languages):**

1. Class/Static variables (public → protected → private)
2. Instance variables (public → protected → private)
3. Constructors
4. Public methods
5. Protected methods
6. Private methods
7. Nested classes (if applicable)

```java
// Java: Standard class layout
public class UserService {
    // 1. Static constants
    private static final int MAX_LOGIN_ATTEMPTS = 3;
    private static final long SESSION_TIMEOUT = 3600;

    // 2. Instance variables
    private final UserRepository userRepository;
    private final PasswordEncoder passwordEncoder;
    private final Logger logger;

    // 3. Constructor
    public UserService(
        UserRepository userRepository,
        PasswordEncoder passwordEncoder
    ) {
        this.userRepository = userRepository;
        this.passwordEncoder = passwordEncoder;
        this.logger = LoggerFactory.getLogger(UserService.class);
    }

    // 4. Public methods
    public User createUser(String email, String password) {
        validateEmail(email);
        validatePassword(password);

        String hashedPassword = passwordEncoder.encode(password);
        return userRepository.save(new User(email, hashedPassword));
    }

    public User authenticateUser(String email, String password) {
        User user = userRepository.findByEmail(email);
        validateAuthentication(user, password);
        return user;
    }

    // 5. Private methods (helpers)
    private void validateEmail(String email) {
        if (!email.contains("@")) {
            throw new ValidationException("Invalid email format");
        }
    }

    private void validatePassword(String password) {
        if (password.length() < 8) {
            throw new ValidationException("Password too short");
        }
    }

    private void validateAuthentication(User user, String password) {
        if (user == null) {
            throw new AuthenticationException("Invalid credentials");
        }
        if (!passwordEncoder.matches(password, user.getPasswordHash())) {
            throw new AuthenticationException("Invalid credentials");
        }
    }
}
```

### Function Formatting

**Function Declaration:**

```python
# Python: Function formatting
def calculate_loan_payment(
    principal: float,
    annual_rate: float,
    term_months: int
) -> float:
    """
    Calculate monthly loan payment.

    Args:
        principal: Loan amount in dollars
        annual_rate: Annual interest rate (0.05 = 5%)
        term_months: Loan term in months

    Returns:
        Monthly payment amount
    """
    monthly_rate = annual_rate / 12
    payment = (principal * monthly_rate) / (
        1 - (1 + monthly_rate) ** -term_months
    )
    return payment
```

```typescript
// TypeScript: Function formatting
function calculateLoanPayment(
    principal: number,
    annualRate: number,
    termMonths: number
): number {
    const monthlyRate = annualRate / 12;
    const payment = (principal * monthlyRate) / (
        1 - Math.pow(1 + monthlyRate, -termMonths)
    );
    return payment;
}
```

### Method Chaining

```typescript
// Method chaining: One call per line
user
    .setFirstName("John")
    .setLastName("Doe")
    .setEmail("john@example.com")
    .setAge(30)
    .save();

// Query building: Clear structure
const users = database
    .select('users')
    .where('age', '>', 18)
    .where('status', '=', 'active')
    .orderBy('created_at', 'desc')
    .limit(10)
    .execute();
```

## Formatting Data Structures

### Arrays and Lists

```python
# Python: Array formatting
# Short array: One line
numbers = [1, 2, 3, 4, 5]

# Long array: One item per line
user_permissions = [
    'read_users',
    'create_users',
    'update_users',
    'delete_users',
    'read_orders',
    'create_orders',
]

# Nested arrays: Clear indentation
matrix = [
    [1, 2, 3],
    [4, 5, 6],
    [7, 8, 9],
]
```

### Dictionaries and Objects

```python
# Python: Dictionary formatting
# Short dict: One line
config = {'debug': True, 'port': 8080}

# Long dict: One key per line
user = {
    'id': 12345,
    'first_name': 'John',
    'last_name': 'Doe',
    'email': 'john@example.com',
    'age': 30,
    'is_active': True,
    'created_at': '2024-01-01',
}

# Nested dict: Clear nesting
database_config = {
    'host': 'localhost',
    'port': 5432,
    'credentials': {
        'username': 'admin',
        'password': 'secret',
    },
    'pool': {
        'min_size': 5,
        'max_size': 20,
    },
}
```

```typescript
// TypeScript: Object formatting
const user = {
    id: 12345,
    firstName: 'John',
    lastName: 'Doe',
    email: 'john@example.com',
    age: 30,
    isActive: true,
    createdAt: new Date(),
};

// Object with methods: Clear separation
const calculator = {
    add(a: number, b: number): number {
        return a + b;
    },

    subtract(a: number, b: number): number {
        return a - b;
    },

    multiply(a: number, b: number): number {
        return a * b;
    },
};
```

### Type Definitions

```typescript
// TypeScript: Type and interface formatting
interface User {
    id: number;
    firstName: string;
    lastName: string;
    email: string;
    age: number;
    isActive: boolean;
}

// Complex type: Readable structure
type OrderStatus =
    | 'pending'
    | 'processing'
    | 'shipped'
    | 'delivered'
    | 'cancelled';

// Generic types: Clear constraints
interface Repository<T extends BaseEntity> {
    findById(id: string): Promise<T | null>;
    findAll(): Promise<T[]>;
    save(entity: T): Promise<T>;
    delete(id: string): Promise<void>;
}
```

## Comments and Documentation Formatting

### Single-Line Comments

```python
# Python: Comment formatting
# Good: Comment explains WHY, not WHAT
tax_rate = 0.08  # California state sales tax

# Good: Comment before code block
# Calculate shipping cost based on weight and destination
# International shipments use different rate tables
shipping_cost = calculate_shipping(weight, destination)
```

### Multi-Line Comments

```java
// Java: Multi-line comment formatting
/**
 * Processes a payment transaction.
 *
 * This method handles the complete payment workflow including
 * validation, authorization, capture, and notification. All
 * operations are wrapped in a transaction for consistency.
 *
 * @param payment The payment details
 * @return The completed transaction
 * @throws PaymentException If payment processing fails
 */
public Transaction processPayment(Payment payment) {
    // Implementation
}
```

### Inline Comments

```typescript
// TypeScript: Inline comment placement
const total = (
    subtotal  // Base amount before adjustments
    + tax     // State and local taxes
    + shipping  // Delivery charges
    - discount  // Applied promotions
);

// Don't overdo it - prefer clear variable names
const total = subtotal + tax + shipping - discount;  // Self-explanatory
```

## Language-Specific Conventions

### Python (PEP 8)

```python
# Python: PEP 8 formatting standards
import os
import sys
from typing import List, Dict, Optional

# Constants: UPPER_SNAKE_CASE
MAX_RETRIES = 3
DEFAULT_TIMEOUT = 30

# Classes: PascalCase
class UserService:
    """Service for managing user operations."""

    # Methods and variables: snake_case
    def __init__(self, database_url: str):
        self.database_url = database_url
        self._connection = None

    def create_user(
        self,
        email: str,
        password: str,
        full_name: Optional[str] = None
    ) -> Dict[str, any]:
        """
        Create a new user account.

        Args:
            email: User's email address
            password: User's password (will be hashed)
            full_name: User's full name (optional)

        Returns:
            Dictionary containing user data

        Raises:
            ValidationError: If email or password invalid
        """
        # Validate inputs
        if not self._is_valid_email(email):
            raise ValidationError("Invalid email format")

        # Create user
        user_data = {
            'email': email,
            'password_hash': hash_password(password),
            'full_name': full_name,
        }

        return self._save_user(user_data)

    # Private methods: Leading underscore
    def _is_valid_email(self, email: str) -> bool:
        return '@' in email and '.' in email

    def _save_user(self, user_data: Dict[str, any]) -> Dict[str, any]:
        # Implementation
        pass
```

### TypeScript/JavaScript

```typescript
// TypeScript: Standard formatting conventions
import { Injectable } from '@nestjs/common';
import { InjectRepository } from '@nestjs/typeorm';
import { Repository } from 'typeorm';

// Interfaces: PascalCase with 'I' prefix (optional)
interface IUserService {
    createUser(email: string, password: string): Promise<User>;
    findUserById(id: string): Promise<User | null>;
}

// Classes: PascalCase
@Injectable()
export class UserService implements IUserService {
    // Constructor parameter properties
    constructor(
        @InjectRepository(User)
        private readonly userRepository: Repository<User>,
    ) {}

    // Methods: camelCase
    async createUser(email: string, password: string): Promise<User> {
        // Validate email
        if (!this.isValidEmail(email)) {
            throw new ValidationException('Invalid email format');
        }

        // Check for existing user
        const existingUser = await this.findUserByEmail(email);
        if (existingUser) {
            throw new ConflictException('User already exists');
        }

        // Create and save user
        const user = this.userRepository.create({
            email,
            passwordHash: await this.hashPassword(password),
        });

        return this.userRepository.save(user);
    }

    async findUserById(id: string): Promise<User | null> {
        return this.userRepository.findOne({ where: { id } });
    }

    // Private methods: camelCase
    private isValidEmail(email: string): boolean {
        return /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email);
    }

    private async hashPassword(password: string): Promise<string> {
        // Implementation
        return password;  // Placeholder
    }

    private async findUserByEmail(email: string): Promise<User | null> {
        return this.userRepository.findOne({ where: { email } });
    }
}

// Type aliases: PascalCase
type UserId = string;
type UserRole = 'admin' | 'user' | 'guest';

// Enums: PascalCase with UPPER_CASE values
enum OrderStatus {
    PENDING = 'PENDING',
    PROCESSING = 'PROCESSING',
    SHIPPED = 'SHIPPED',
    DELIVERED = 'DELIVERED',
}
```

### Java

```java
// Java: Standard formatting conventions
package com.example.userservice;

import java.util.List;
import java.util.Optional;
import javax.validation.constraints.Email;
import javax.validation.constraints.NotNull;

/**
 * Service for managing user operations.
 * Handles user creation, authentication, and retrieval.
 */
public class UserService {
    // Constants: UPPER_SNAKE_CASE
    private static final int MAX_LOGIN_ATTEMPTS = 3;
    private static final long SESSION_DURATION_MS = 3600000;

    // Instance variables: camelCase
    private final UserRepository userRepository;
    private final PasswordEncoder passwordEncoder;
    private final Logger logger;

    // Constructor
    public UserService(
        UserRepository userRepository,
        PasswordEncoder passwordEncoder
    ) {
        this.userRepository = userRepository;
        this.passwordEncoder = passwordEncoder;
        this.logger = LoggerFactory.getLogger(UserService.class);
    }

    // Public methods: camelCase
    public User createUser(
        @NotNull @Email String email,
        @NotNull String password
    ) {
        // Validate inputs
        validateEmail(email);
        validatePassword(password);

        // Check for existing user
        if (userRepository.existsByEmail(email)) {
            throw new UserAlreadyExistsException(
                "User with email " + email + " already exists"
            );
        }

        // Create user
        User user = User.builder()
            .email(email)
            .passwordHash(passwordEncoder.encode(password))
            .createdAt(Instant.now())
            .build();

        return userRepository.save(user);
    }

    public Optional<User> findUserById(Long id) {
        return userRepository.findById(id);
    }

    public List<User> findAllUsers() {
        return userRepository.findAll();
    }

    // Private methods: camelCase
    private void validateEmail(String email) {
        if (email == null || !email.contains("@")) {
            throw new ValidationException("Invalid email format");
        }
    }

    private void validatePassword(String password) {
        if (password == null || password.length() < 8) {
            throw new ValidationException("Password must be at least 8 characters");
        }
    }
}
```

## Team Rules (Clean Code)

### The Most Important Rule

**"Every programmer has his own favorite formatting rules, but if he works in a team, then the team rules."** — Robert C. Martin

### Establishing Team Standards

**1. Choose a Style Guide**: Pick an existing, well-established guide
   - Python: PEP 8
   - JavaScript/TypeScript: Airbnb, StandardJS, Google
   - Java: Google Java Style, Oracle conventions
   - C#: Microsoft C# Coding Conventions

**2. Document Deviations**: If you deviate from standard, document why

**3. Automate Enforcement**: Use formatters and linters
   - Python: `black`, `flake8`, `pylint`
   - JavaScript/TypeScript: `prettier`, `eslint`
   - Java: `google-java-format`, `checkstyle`
   - Multi-language: `editorconfig`

**4. Configure Pre-commit Hooks**: Enforce formatting before commits

```bash
# Example: Pre-commit hook for Python
#!/bin/sh
# .git/hooks/pre-commit

echo "Running black formatter..."
black src/ tests/

echo "Running flake8 linter..."
flake8 src/ tests/

echo "Running mypy type checker..."
mypy src/
```

### Configuration Files

**EditorConfig Example** (cross-language consistency):
```ini
# .editorconfig
root = true

[*]
charset = utf-8
end_of_line = lf
insert_final_newline = true
trim_trailing_whitespace = true

[*.py]
indent_style = space
indent_size = 4
max_line_length = 100

[*.{js,ts,jsx,tsx}]
indent_style = space
indent_size = 2
max_line_length = 100

[*.java]
indent_style = space
indent_size = 4
max_line_length = 120

[*.{yml,yaml}]
indent_style = space
indent_size = 2
```

**Prettier Configuration** (JavaScript/TypeScript):
```json
{
    "semi": true,
    "trailingComma": "es5",
    "singleQuote": true,
    "printWidth": 100,
    "tabWidth": 2,
    "useTabs": false,
    "arrowParens": "always"
}
```

**Black Configuration** (Python):
```toml
# pyproject.toml
[tool.black]
line-length = 100
target-version = ['py39', 'py310']
include = '\.pyi?$'
extend-exclude = '''
/(
  # directories
  \.eggs
  | \.git
  | \.mypy_cache
  | \.venv
  | build
  | dist
)/
'''
```

## Common Formatting Anti-Patterns

### Anti-Pattern 1: Inconsistent Indentation

```python
# BAD: Mixed indentation
def process_data():
    if condition:
      do_something()  # 2 spaces
        do_other()    # 4 spaces
    do_final()        # Inconsistent

# GOOD: Consistent indentation
def process_data():
    if condition:
        do_something()  # 4 spaces
        do_other()      # 4 spaces
    do_final()          # 4 spaces
```

### Anti-Pattern 2: Misleading Indentation

```java
// BAD: Misleading indentation
if (condition)
    doSomething();
    doOtherthing();  // Looks indented but always executes!

// GOOD: Clear structure with braces
if (condition) {
    doSomething();
    doOtherthing();
}
```

### Anti-Pattern 3: Long Lines That Require Scrolling

```typescript
// BAD: Requires horizontal scrolling
function processOrder(orderId: string, customerId: string, items: OrderItem[], shippingAddress: Address, billingAddress: Address, paymentMethod: PaymentMethod) {
    // Can't see the full function signature
}

// GOOD: Broken into readable lines
function processOrder(
    orderId: string,
    customerId: string,
    items: OrderItem[],
    shippingAddress: Address,
    billingAddress: Address,
    paymentMethod: PaymentMethod
) {
    // Clear and readable
}
```

### Anti-Pattern 4: No Visual Separation

```python
# BAD: Everything crammed together
def complex_function():
    data = fetch_data()
    processed = transform_data(data)
    validated = validate_data(processed)
    saved = save_data(validated)
    notified = send_notifications(saved)
    logged = log_results(notified)
    return logged

# GOOD: Visual paragraphs
def complex_function():
    # Fetch and transform
    data = fetch_data()
    processed = transform_data(data)

    # Validate
    validated = validate_data(processed)

    # Persist
    saved = save_data(validated)

    # Notify and log
    send_notifications(saved)
    log_results(saved)

    return saved
```

### Anti-Pattern 5: Deeply Nested Code

```java
// BAD: Deep nesting
public void processRequest(Request request) {
    if (request != null) {
        if (request.isValid()) {
            if (request.hasPermission()) {
                if (!request.isExpired()) {
                    if (rateLimiter.allowRequest()) {
                        // Finally do the work 5 levels deep!
                        processValidRequest(request);
                    }
                }
            }
        }
    }
}

// GOOD: Guard clauses (flat structure)
public void processRequest(Request request) {
    if (request == null) {
        return;
    }
    if (!request.isValid()) {
        throw new InvalidRequestException();
    }
    if (!request.hasPermission()) {
        throw new PermissionDeniedException();
    }
    if (request.isExpired()) {
        throw new ExpiredRequestException();
    }
    if (!rateLimiter.allowRequest()) {
        throw new RateLimitExceededException();
    }

    // Work at top level
    processValidRequest(request);
}
```

## Practical Formatting Checklist

Use this checklist when formatting code:

### File Level
- [ ] File is under 500 lines (consider splitting if larger)
- [ ] Imports/includes organized and grouped
- [ ] No trailing whitespace
- [ ] File ends with newline
- [ ] Consistent line endings (LF or CRLF, not mixed)

### Vertical Formatting
- [ ] Related code kept close together
- [ ] Blank lines separate logical sections
- [ ] Functions ordered caller-before-callee
- [ ] Public methods before private methods
- [ ] No more than 2-3 consecutive blank lines

### Horizontal Formatting
- [ ] Lines under 100-120 characters
- [ ] Consistent indentation (spaces, not tabs)
- [ ] Space around operators
- [ ] No space between function name and parenthesis
- [ ] Space after commas
- [ ] Long lines broken at natural boundaries

### Control Structures
- [ ] Consistent brace style (K&R, Allman, etc.)
- [ ] Complex conditions broken into multiple lines
- [ ] Guard clauses instead of deep nesting
- [ ] Consistent formatting for if/else chains

### Classes and Functions
- [ ] Consistent class member ordering
- [ ] One declaration per line
- [ ] Parameter lists broken for readability
- [ ] Method chaining readable (one call per line)

### Data Structures
- [ ] Short collections on one line
- [ ] Long collections one item per line
- [ ] Trailing commas in multi-line collections
- [ ] Nested structures clearly indented

### Team Consistency
- [ ] Follows team style guide
- [ ] Automated formatter configured
- [ ] Pre-commit hooks in place
- [ ] Style violations caught in CI

## Summary: Formatting Principles

1. **Visual Structure = Logical Structure**: Formatting should reveal program organization
2. **Consistency**: Pick a style and stick to it across the entire codebase
3. **Vertical Openness**: Use blank lines to separate logical sections
4. **Vertical Density**: Keep related code close together
5. **Horizontal Limits**: Keep lines under 100-120 characters
6. **Indentation**: Use consistent indentation to show nesting
7. **Team Rules**: Individual preferences yield to team standards
8. **Automate**: Use formatters and linters to enforce consistency
9. **Readability First**: Code is read far more than written
10. **Maintainability**: Good formatting survives modifications

## Further Reading

- **Clean Code** (Chapter 5: Formatting) - Robert C. Martin
- **Code Complete 2** (Chapter 31: Layout and Style) - Steve McConnell
- **PEP 8** - Python Style Guide
- **Google Style Guides** - Multi-language style guides
- **The Art of Readable Code** - Boswell & Foucher

---

**Remember**: Formatting is not about personal preference—it's about effective communication. Well-formatted code is easier to read, easier to understand, and easier to maintain. Invest in formatting from the start, automate enforcement, and let the team focus on solving problems instead of debating style.
