# Functions and Routines: Building the Core Components

## Overview

Functions and routines are the fundamental building blocks of all software. They are the primary mechanism for organizing code, managing complexity, and enabling reuse. The quality of your functions directly determines the maintainability, testability, and comprehensibility of your entire codebase.

This guide synthesizes proven principles from industry-leading sources to provide comprehensive, actionable guidance for designing and implementing high-quality functions.

**"The first rule of functions is that they should be small. The second rule of functions is that they should be smaller than that."** — Robert C. Martin, Clean Code

## Why Function Design Matters

### The Cost of Poor Function Design

Poor function design creates measurable costs:

**Comprehension Time**: Large, complex functions with multiple responsibilities force developers to hold more context in working memory, dramatically slowing comprehension and increasing errors.

**Debugging Difficulty**: Functions that do multiple things create ambiguous failure points. When a 200-line function fails, identifying the exact problem becomes a time-consuming investigation.

**Modification Risk**: Making changes to large, poorly organized functions risks breaking unrelated functionality. Fear of side effects leads to "programming by coincidence" where developers avoid necessary refactoring.

**Testing Challenges**: Functions with multiple responsibilities require exponentially more test cases. A function with three independent behaviors needs tests for each behavior plus their interactions.

**Reusability Failure**: Specific, poorly abstracted functions can't be reused. This leads to code duplication and inconsistent implementations across the codebase.

### The Benefits of Well-Designed Functions

Well-designed functions provide:
- **Mental Manageability**: Small functions with clear purposes reduce cognitive load
- **Self-Documentation**: Well-named, single-purpose functions explain themselves
- **Easy Testing**: Small functions with clear inputs/outputs are trivially testable
- **Safe Refactoring**: Small, focused functions can be modified with confidence
- **Natural Reuse**: General, well-abstracted functions enable code reuse
- **Clear Architecture**: Good function organization reveals system structure

## Source Materials

This guide synthesizes principles from:

- **Code Complete 2** by Steve McConnell (Chapter 7: "High-Quality Routines")
  - Valid reasons to create routines
  - Routine cohesion levels
  - Parameter design principles
  - Function vs procedure distinction

- **Clean Code** by Robert C. Martin (Chapter 3: "Functions")
  - Function size and organization
  - Single responsibility principle
  - Levels of abstraction
  - Error handling in functions

## Valid Reasons to Create a Function (Code Complete 2)

Understanding *why* to create a function is as important as understanding *how*.

### 1. Reduce Complexity

**Purpose**: Hide complex operations behind simple interfaces.

**Before:**
```python
# Complex calculation embedded in larger function
def process_order(order):
    # Calculate shipping cost with complex logic
    if order.weight <= 5 and order.destination.zone == "domestic":
        base_rate = 5.99
    elif order.weight <= 5 and order.destination.zone == "international":
        base_rate = 15.99
    elif order.weight <= 20 and order.destination.zone == "domestic":
        base_rate = 12.99
    elif order.weight <= 20 and order.destination.zone == "international":
        base_rate = 29.99
    else:
        base_rate = order.weight * 2.50

    if order.customer.is_premium:
        base_rate *= 0.8

    shipping_cost = base_rate * (1 + order.destination.tax_rate)

    # ... rest of order processing
```

**After:**
```python
def calculate_shipping_cost(order):
    """Calculate shipping cost based on weight, destination, and customer status."""
    base_rate = _get_base_shipping_rate(order.weight, order.destination.zone)
    adjusted_rate = _apply_customer_discount(base_rate, order.customer)
    return _apply_destination_tax(adjusted_rate, order.destination)

def process_order(order):
    shipping_cost = calculate_shipping_cost(order)
    # ... rest of order processing with clear intent
```

**Benefit**: The complex shipping calculation is hidden. `process_order` remains readable and focused on high-level order processing logic.

### 2. Introduce Intermediate Abstraction

**Purpose**: Create meaningful abstractions that match mental models.

**Before:**
```typescript
// Low-level database operations exposed
async function generateMonthlyReport(): Promise<Report> {
    const connection = await database.connect();
    const query = `
        SELECT u.id, u.name, COUNT(o.id) as order_count, SUM(o.total) as revenue
        FROM users u
        LEFT JOIN orders o ON u.id = o.user_id
        WHERE o.created_at >= ? AND o.created_at < ?
        GROUP BY u.id, u.name
    `;
    const startDate = new Date(Date.now() - 30 * 24 * 60 * 60 * 1000);
    const endDate = new Date();
    const results = await connection.execute(query, [startDate, endDate]);
    // ... 50 more lines of data processing
}
```

**After:**
```typescript
// Meaningful abstractions
async function getUserOrderStatistics(startDate: Date, endDate: Date): Promise<UserStats[]> {
    const connection = await database.connect();
    return await connection.query(
        `SELECT u.id, u.name, COUNT(o.id) as order_count, SUM(o.total) as revenue
         FROM users u LEFT JOIN orders o ON u.id = o.user_id
         WHERE o.created_at >= ? AND o.created_at < ?
         GROUP BY u.id, u.name`,
        [startDate, endDate]
    );
}

async function generateMonthlyReport(): Promise<Report> {
    const dateRange = getLastThirtyDays();
    const userStats = await getUserOrderStatistics(dateRange.start, dateRange.end);
    return formatAsReport(userStats);
}
```

**Benefit**: Abstractions match business concepts. The code reads like a description of what it does, not how it does it.

### 3. Avoid Duplicate Code (DRY Principle)

**Purpose**: Eliminate redundancy to reduce maintenance burden.

**Before:**
```java
// Duplicate validation logic
public class UserService {
    public void createUser(String email, String password) {
        if (email == null || email.trim().isEmpty()) {
            throw new IllegalArgumentException("Email required");
        }
        if (!email.contains("@") || !email.contains(".")) {
            throw new IllegalArgumentException("Invalid email format");
        }
        if (password == null || password.length() < 8) {
            throw new IllegalArgumentException("Password must be at least 8 characters");
        }
        // ... create user
    }

    public void updateUser(String userId, String email, String password) {
        // Exact same validation duplicated
        if (email == null || email.trim().isEmpty()) {
            throw new IllegalArgumentException("Email required");
        }
        if (!email.contains("@") || !email.contains(".")) {
            throw new IllegalArgumentException("Invalid email format");
        }
        if (password == null || password.length() < 8) {
            throw new IllegalArgumentException("Password must be at least 8 characters");
        }
        // ... update user
    }
}
```

**After:**
```java
// Extracted validation
public class UserService {
    private void validateEmail(String email) {
        if (email == null || email.trim().isEmpty()) {
            throw new IllegalArgumentException("Email required");
        }
        if (!email.contains("@") || !email.contains(".")) {
            throw new IllegalArgumentException("Invalid email format");
        }
    }

    private void validatePassword(String password) {
        if (password == null || password.length() < 8) {
            throw new IllegalArgumentException("Password must be at least 8 characters");
        }
    }

    public void createUser(String email, String password) {
        validateEmail(email);
        validatePassword(password);
        // ... create user
    }

    public void updateUser(String userId, String email, String password) {
        validateEmail(email);
        validatePassword(password);
        // ... update user
    }
}
```

**Benefit**: Single source of truth. Bugs are fixed once. Validation logic changes in one place.

### 4. Support Subclassing (Inheritance)

**Purpose**: Enable polymorphism and specialization through inheritance.

```python
# Base class with overridable methods
class PaymentProcessor:
    def process_payment(self, amount, payment_method):
        """Template method defining payment processing steps."""
        self.validate_amount(amount)
        self.authenticate_payment_method(payment_method)
        transaction_id = self.execute_transaction(amount, payment_method)
        self.record_transaction(transaction_id)
        return transaction_id

    def validate_amount(self, amount):
        """Can be overridden for different validation rules."""
        if amount <= 0:
            raise ValueError("Amount must be positive")

    def execute_transaction(self, amount, payment_method):
        """Must be overridden by subclasses."""
        raise NotImplementedError("Subclasses must implement execute_transaction")

# Specialized implementations
class CreditCardProcessor(PaymentProcessor):
    def execute_transaction(self, amount, payment_method):
        # Credit card specific logic
        return self.gateway.charge_card(payment_method.card_token, amount)

class PayPalProcessor(PaymentProcessor):
    def validate_amount(self, amount):
        # PayPal has different minimum
        if amount < 1.00:
            raise ValueError("PayPal requires minimum $1.00")
        super().validate_amount(amount)

    def execute_transaction(self, amount, payment_method):
        # PayPal specific logic
        return self.paypal_api.create_payment(payment_method.email, amount)
```

**Benefit**: Shared behavior in base class, specialized behavior in subclasses. Changes to common steps propagate automatically.

### 5. Hide Sequences (Encapsulate Order Dependencies)

**Purpose**: Ensure operations execute in the correct order by hiding the sequence.

**Before:**
```typescript
// Exposed sequence - easy to get wrong
async function setupUserAccount(userId: string, role: string) {
    // These MUST happen in this order, but nothing enforces it
    await createUserRecord(userId);
    await assignUserRole(userId, role);
    await initializeUserPreferences(userId);
    await sendWelcomeEmail(userId);
}

// Caller might accidentally do this:
await assignUserRole(userId, role);  // ERROR: User doesn't exist yet!
await createUserRecord(userId);
```

**After:**
```typescript
// Hidden sequence - can't get it wrong
class UserAccountSetup {
    private userId: string;
    private role: string;

    constructor(userId: string, role: string) {
        this.userId = userId;
        this.role = role;
    }

    async execute(): Promise<void> {
        await this.createUserRecord();
        await this.assignRole();
        await this.initializePreferences();
        await this.sendWelcome();
    }

    private async createUserRecord(): Promise<void> {
        // Implementation
    }

    private async assignRole(): Promise<void> {
        // Implementation
    }

    private async initializePreferences(): Promise<void> {
        // Implementation
    }

    private async sendWelcome(): Promise<void> {
        // Implementation
    }
}

// Usage - sequence is encapsulated and guaranteed correct
const setup = new UserAccountSetup(userId, role);
await setup.execute();
```

**Benefit**: Impossible to execute steps out of order. The sequence is enforced by the implementation.

### 6. Hide Pointer Operations (Encapsulate Data Structures)

**Purpose**: Protect data structure integrity by hiding internal representations.

**Before:**
```python
# Direct manipulation of internal structure
class TaskQueue:
    def __init__(self):
        self.tasks = []  # Public access to internal list

# Dangerous usage
queue = TaskQueue()
queue.tasks.append(task1)
queue.tasks.insert(0, task2)  # Breaks FIFO semantics!
del queue.tasks[3]  # Can break queue invariants
```

**After:**
```python
# Encapsulated data structure
class TaskQueue:
    def __init__(self):
        self._tasks = []  # Private internal structure

    def enqueue(self, task):
        """Add task to end of queue."""
        self._tasks.append(task)

    def dequeue(self):
        """Remove and return task from front of queue."""
        if not self._tasks:
            raise IndexError("Queue is empty")
        return self._tasks.pop(0)

    def peek(self):
        """View front task without removing."""
        if not self._tasks:
            raise IndexError("Queue is empty")
        return self._tasks[0]

    def __len__(self):
        return len(self._tasks)

# Safe usage
queue = TaskQueue()
queue.enqueue(task1)
queue.enqueue(task2)
next_task = queue.dequeue()  # Guaranteed FIFO
```

**Benefit**: Queue semantics are preserved. Internal representation can change without affecting clients.

### 7. Improve Portability

**Purpose**: Isolate platform-specific code behind portable interfaces.

```java
// Platform abstraction
public interface FileSystemOperations {
    String getUserHomeDirectory();
    String getPathSeparator();
    boolean createDirectory(String path);
}

// Windows implementation
public class WindowsFileSystem implements FileSystemOperations {
    @Override
    public String getUserHomeDirectory() {
        return System.getenv("USERPROFILE");
    }

    @Override
    public String getPathSeparator() {
        return "\\";
    }

    @Override
    public boolean createDirectory(String path) {
        // Windows-specific directory creation
        return new File(path).mkdirs();
    }
}

// Unix implementation
public class UnixFileSystem implements FileSystemOperations {
    @Override
    public String getUserHomeDirectory() {
        return System.getenv("HOME");
    }

    @Override
    public String getPathSeparator() {
        return "/";
    }

    @Override
    public boolean createDirectory(String path) {
        // Unix-specific directory creation with permissions
        File dir = new File(path);
        boolean created = dir.mkdirs();
        if (created) {
            dir.setReadable(true, false);
            dir.setWritable(true, true);
        }
        return created;
    }
}

// Client code is portable
public class Application {
    private final FileSystemOperations fileSystem;

    public Application(FileSystemOperations fileSystem) {
        this.fileSystem = fileSystem;
    }

    public void initializeUserDirectory() {
        String homeDir = fileSystem.getUserHomeDirectory();
        String appDir = homeDir + fileSystem.getPathSeparator() + "myapp";
        fileSystem.createDirectory(appDir);
    }
}
```

**Benefit**: Platform differences isolated. Easy to port to new platforms by implementing the interface.

### 8. Simplify Complex Boolean Tests

**Purpose**: Replace complex conditionals with well-named functions.

**Before:**
```python
# Complex, hard-to-understand boolean expression
def process_transaction(transaction, user):
    if (transaction.amount > 1000 and
        (user.account_type == "premium" or user.years_member > 5) and
        user.fraud_score < 0.3 and
        transaction.destination_country in ["US", "CA", "UK"] and
        not user.account_locked and
        user.daily_transaction_count < 10):
        # Process transaction
        pass
```

**After:**
```python
# Clear, self-documenting functions
def is_high_value_transaction(transaction):
    return transaction.amount > 1000

def is_trusted_user(user):
    return user.account_type == "premium" or user.years_member > 5

def has_low_fraud_risk(user):
    return user.fraud_score < 0.3

def is_allowed_destination(transaction):
    return transaction.destination_country in ["US", "CA", "UK"]

def can_transact(user):
    return not user.account_locked and user.daily_transaction_count < 10

def requires_additional_verification(transaction, user):
    return (is_high_value_transaction(transaction) and
            is_trusted_user(user) and
            has_low_fraud_risk(user) and
            is_allowed_destination(transaction) and
            can_transact(user))

def process_transaction(transaction, user):
    if requires_additional_verification(transaction, user):
        # Process transaction
        pass
```

**Benefit**: Each condition is named and testable. The business rules are explicit and maintainable.

## Function Cohesion (Code Complete 2)

Cohesion measures how closely the operations within a function are related. High cohesion is desirable—it indicates that a function does one thing well.

### Levels of Cohesion (Best to Worst)

#### 1. Functional Cohesion (Best)

**Definition**: A function performs one and only one operation.

**Characteristics**:
- Single, well-defined purpose
- All code contributes to that purpose
- Can be described in a simple sentence without "and" or "or"

```python
# Functionally cohesive - does ONE thing
def calculate_compound_interest(principal, annual_rate, years):
    """Calculate compound interest for given principal, rate, and time."""
    return principal * (1 + annual_rate) ** years

def validate_email_format(email):
    """Validate email has correct format."""
    email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(email_pattern, email) is not None

def send_password_reset_email(user_email, reset_token):
    """Send password reset email to user with reset token."""
    subject = "Password Reset Request"
    body = f"Click here to reset your password: {reset_token}"
    return email_service.send(user_email, subject, body)
```

**Why it's best**: Easy to understand, test, reuse, and maintain. The function name describes exactly what it does.

#### 2. Sequential Cohesion (Good)

**Definition**: Operations are related because output from one is input to the next.

**Characteristics**:
- Steps must be performed in order
- Data flows through the function
- Each step depends on the previous step's result

```typescript
// Sequentially cohesive - data flows through steps
function processImageUpload(rawImageData: Buffer): ProcessedImage {
    // Each step uses output of previous step
    const validatedImage = validateImageFormat(rawImageData);
    const resizedImage = resizeToStandardDimensions(validatedImage);
    const optimizedImage = compressImage(resizedImage);
    const savedImage = saveToStorage(optimizedImage);
    return savedImage;
}

function calculateOrderTotal(items: CartItem[]): OrderTotal {
    const subtotal = calculateSubtotal(items);
    const taxAmount = calculateTax(subtotal);
    const shippingCost = calculateShipping(items);
    const totalAmount = subtotal + taxAmount + shippingCost;
    return {
        subtotal,
        tax: taxAmount,
        shipping: shippingCost,
        total: totalAmount
    };
}
```

**Why it's good**: Clear data flow. Natural pipeline of operations. Easy to follow and debug.

#### 3. Communicational Cohesion (Acceptable)

**Definition**: Operations work on the same data or contribute to the same output.

**Characteristics**:
- Operations use the same data structure
- Operations could be done in any order
- Related by data, not by flow

```java
// Communicational cohesion - operations on same data structure
public class UserProfile {
    // All operations work on User object
    public void updateUserProfile(User user, ProfileUpdate updates) {
        updateUserName(user, updates.getName());
        updateUserEmail(user, updates.getEmail());
        updateUserPhone(user, updates.getPhone());
        updateLastModified(user);
    }

    private void updateUserName(User user, String name) {
        if (name != null) user.setName(name);
    }

    private void updateUserEmail(User user, String email) {
        if (email != null) user.setEmail(email);
    }

    private void updateUserPhone(User user, String phone) {
        if (phone != null) user.setPhone(phone);
    }

    private void updateLastModified(User user) {
        user.setLastModified(new Date());
    }
}
```

**Why it's acceptable**: Operations are related by data. Makes sense to group them, though they could be separated.

#### 4. Temporal Cohesion (Questionable)

**Definition**: Operations are related because they happen at the same time.

**Characteristics**:
- Operations grouped because they occur together
- Not necessarily related functionally
- Often initialization or cleanup functions

```python
# Temporal cohesion - operations happen at same time
def initialize_application():
    """Initialize application - TEMPORAL COHESION WARNING"""
    load_configuration_files()
    connect_to_database()
    start_logging_system()
    initialize_cache()
    load_user_preferences()
    # These are related by WHEN they happen, not by WHAT they do

# Better: Break into functionally cohesive pieces
def initialize_data_layer():
    """Initialize data layer components."""
    connect_to_database()
    initialize_cache()

def initialize_configuration():
    """Initialize configuration system."""
    load_configuration_files()
    load_user_preferences()

def initialize_observability():
    """Initialize logging and monitoring."""
    start_logging_system()

def initialize_application():
    """Initialize all application systems."""
    initialize_configuration()
    initialize_data_layer()
    initialize_observability()
```

**Why it's questionable**: Operations aren't truly related. Harder to test and reuse individual operations.

#### 5. Procedural Cohesion (Weak)

**Definition**: Operations are grouped because they follow a certain sequence, even though they're not related.

**Characteristics**:
- Steps in an algorithm, but serve different purposes
- Order matters, but operations are unrelated
- Often indicates missing abstractions

```typescript
// Procedural cohesion - weak relationship
function processNewUserSignup(userData: UserData): void {
    // These operations are only related by procedure, not by purpose
    const userId = generateUniqueId();
    const hashedPassword = hashPassword(userData.password);
    insertUserIntoDatabase(userId, userData.email, hashedPassword);
    sendWelcomeEmail(userData.email);
    logSignupEvent(userId);
    incrementSignupCounter();
    checkForReferralBonus(userData.referralCode);
    initializeUserAnalytics(userId);
}

// Better: Group by purpose
class UserSignupService {
    async createUser(userData: UserData): Promise<User> {
        const userId = this.generateUniqueId();
        const credentials = this.createCredentials(userData);
        return await this.userRepository.create(userId, credentials);
    }

    async notifyUser(user: User): Promise<void> {
        await this.emailService.sendWelcome(user.email);
    }

    async recordSignup(user: User, referralCode?: string): Promise<void> {
        await this.analytics.logSignup(user.id);
        await this.metrics.incrementSignupCounter();
        if (referralCode) {
            await this.referralService.processBonus(referralCode);
        }
    }
}
```

**Why it's weak**: Operations serve different purposes. Hard to understand, test, and reuse.

#### 6. Logical Cohesion (Poor)

**Definition**: Operations are grouped because they're in the same category, but do different things.

**Characteristics**:
- Switch or if/else determines which operation
- Operations are categorically similar but functionally different
- Often indicates missing polymorphism

```python
# Logical cohesion - POOR DESIGN
def perform_operation(operation_type, data):
    """Perform different operations based on type - LOGICAL COHESION ANTI-PATTERN"""
    if operation_type == "validate":
        # Validation logic
        return validate_data(data)
    elif operation_type == "transform":
        # Transformation logic
        return transform_data(data)
    elif operation_type == "save":
        # Saving logic
        return save_data(data)
    elif operation_type == "send":
        # Sending logic
        return send_data(data)
    # These are completely different operations!

# Better: Separate functions or polymorphism
def validate_data(data):
    """Validate data format and content."""
    # Validation logic

def transform_data(data):
    """Transform data to required format."""
    # Transformation logic

def save_data(data):
    """Save data to storage."""
    # Saving logic

def send_data(data):
    """Send data to external service."""
    # Sending logic

# Or use polymorphism
class DataOperation(ABC):
    @abstractmethod
    def execute(self, data):
        pass

class ValidateOperation(DataOperation):
    def execute(self, data):
        return validate_data(data)

class TransformOperation(DataOperation):
    def execute(self, data):
        return transform_data(data)
```

**Why it's poor**: Function does different things based on parameters. Difficult to test and maintain.

#### 7. Coincidental Cohesion (Worst)

**Definition**: Operations are grouped arbitrarily with no meaningful relationship.

**Characteristics**:
- No logical connection between operations
- Often utility or miscellaneous functions
- Named things like "utils" or "helpers"

```java
// Coincidental cohesion - WORST DESIGN
public class Utilities {
    // These operations have NO relationship
    public static String formatDate(Date date) {
        // Date formatting
    }

    public static void sendEmail(String recipient, String body) {
        // Email sending
    }

    public static double calculateTax(double amount) {
        // Tax calculation
    }

    public static boolean validateCreditCard(String cardNumber) {
        // Credit card validation
    }

    public static void logToFile(String message) {
        // File logging
    }
    // These belong in completely different classes!
}

// Better: Organize by domain
public class DateFormatter {
    public static String format(Date date) { /* ... */ }
}

public class EmailService {
    public void send(String recipient, String body) { /* ... */ }
}

public class TaxCalculator {
    public double calculate(double amount) { /* ... */ }
}

public class CreditCardValidator {
    public boolean validate(String cardNumber) { /* ... */ }
}

public class Logger {
    public void logToFile(String message) { /* ... */ }
}
```

**Why it's worst**: No cohesion at all. Impossible to understand the purpose of the class/module.

### Cohesion Summary

**Target**: Aim for functional or sequential cohesion.
**Acceptable**: Communicational cohesion for operations on shared data.
**Warning Signs**: Temporal, procedural, logical, or coincidental cohesion indicates design problems.

**Rule of Thumb**: If you can't describe a function's purpose in a single sentence without "and" or "or", it lacks cohesion.

## Function Size: How Small Is Small Enough? (Clean Code)

### The Size Rule

**Clean Code Guideline**: Functions should be small. Very small. Typically:
- **Target**: 4-5 lines
- **Acceptable**: Up to 20 lines
- **Maximum**: 30 lines (rarely)

**Code Complete Guideline**: Functions should fit on one screen (typically 50-150 lines maximum).

### Modern Consensus: Smaller Than You Think

Research and practice suggest that **smaller is almost always better**:

```python
# Too large - hard to understand
def process_user_registration(email, password, name, phone):
    """Register new user - TOO LARGE"""
    # Validation (10 lines)
    if not email or "@" not in email:
        raise ValueError("Invalid email")
    if not password or len(password) < 8:
        raise ValueError("Password too short")
    if not name or len(name) < 2:
        raise ValueError("Name too short")
    if phone and not re.match(r'^\d{10}$', phone):
        raise ValueError("Invalid phone")

    # Check existing user (5 lines)
    existing_user = db.query("SELECT * FROM users WHERE email = ?", email)
    if existing_user:
        raise ValueError("User already exists")

    # Create user (8 lines)
    user_id = generate_id()
    hashed_password = hash_password(password)
    db.execute(
        "INSERT INTO users (id, email, password, name, phone) VALUES (?, ?, ?, ?, ?)",
        user_id, email, hashed_password, name, phone
    )

    # Send welcome email (10 lines)
    email_body = f"""
    Welcome {name}!
    Your account has been created.
    Please verify your email by clicking: {verification_link}
    """
    send_email(email, "Welcome!", email_body)

    # Log registration (3 lines)
    log_event("user_registration", {"user_id": user_id, "email": email})

    return user_id

# Better - small, focused functions
def validate_registration_data(email, password, name, phone):
    """Validate all registration data."""
    validate_email(email)
    validate_password(password)
    validate_name(name)
    validate_phone(phone)

def ensure_user_not_exists(email):
    """Check that user doesn't already exist."""
    if user_repository.find_by_email(email):
        raise ValueError("User already exists")

def create_user_account(email, password, name, phone):
    """Create user account in database."""
    user_id = generate_id()
    hashed_password = hash_password(password)
    user_repository.create(user_id, email, hashed_password, name, phone)
    return user_id

def send_welcome_notification(email, name):
    """Send welcome email to new user."""
    email_service.send_welcome_email(email, name)

def log_registration(user_id, email):
    """Log user registration event."""
    event_logger.log("user_registration", {"user_id": user_id, "email": email})

def process_user_registration(email, password, name, phone):
    """Register new user with validation and notifications."""
    validate_registration_data(email, password, name, phone)
    ensure_user_not_exists(email)
    user_id = create_user_account(email, password, name, phone)
    send_welcome_notification(email, name)
    log_registration(user_id, email)
    return user_id
```

### Why Small Functions Win

**Reason 1: Reduced Complexity**
- Small functions have fewer decision points
- Lower cyclomatic complexity
- Easier to reason about

**Reason 2: Better Names**
- Small functions can have more descriptive names
- Names document intent
- Function calls read like documentation

**Reason 3: Easier Testing**
- Each small function tests one thing
- Fewer edge cases per function
- Clear input/output contracts

**Reason 4: Simple Debugging**
- Stack traces with meaningful function names
- Easier to isolate failures
- Smaller search space for bugs

**Reason 5: Safe Refactoring**
- Small functions easier to modify
- Changes have limited scope
- Less risk of breaking unrelated functionality

### The "One Thing" Rule (Clean Code)

**Principle**: Functions should do one thing. They should do it well. They should do it only.

**How to determine "one thing"**:
1. Can you extract another function with a name that isn't a restatement of the implementation?
2. Does the function do more than one level of abstraction?
3. Can you describe the function without using "and" or "or"?

```typescript
// Does MORE than one thing
function saveUserAndSendEmail(user: User): void {
    database.save(user);  // Thing 1: persistence
    emailService.send(user.email, "Welcome!");  // Thing 2: notification
}

// Better: Each function does ONE thing
function saveUser(user: User): void {
    database.save(user);
}

function sendWelcomeEmail(email: string): void {
    emailService.send(email, "Welcome!");
}

function registerUser(user: User): void {
    saveUser(user);
    sendWelcomeEmail(user.email);
}
```

## Levels of Abstraction (Clean Code)

### The Single Level of Abstraction Principle

**Rule**: All statements in a function should be at the same level of abstraction.

**Why**: Mixing abstraction levels confuses readers about what's essential vs. detail.

**Poor Example - Mixed Abstraction Levels:**
```python
def generate_report(user_id):
    """Generate user report - MIXED ABSTRACTIONS"""
    user = fetch_user(user_id)  # High-level abstraction

    # Low-level string manipulation mixed with high-level concepts
    html = "<html><body>"
    html += "<h1>User Report</h1>"
    html += f"<p>Name: {user.name}</p>"

    orders = fetch_orders(user_id)  # High-level abstraction

    # Low-level loop and string concatenation
    html += "<ul>"
    for order in orders:
        html += f"<li>Order #{order.id}: ${order.total}</li>"
    html += "</ul>"
    html += "</body></html>"

    # Low-level file I/O
    with open(f"report_{user_id}.html", "w") as f:
        f.write(html)
```

**Good Example - Consistent Abstraction Level:**
```python
def generate_report(user_id):
    """Generate user report at consistent high level."""
    user = fetch_user(user_id)
    orders = fetch_orders(user_id)
    report_html = render_report_html(user, orders)
    save_report(user_id, report_html)

def render_report_html(user, orders):
    """Render report HTML at consistent medium level."""
    header = render_report_header(user)
    order_list = render_order_list(orders)
    return wrap_in_html_page(header, order_list)

def render_report_header(user):
    """Render report header section."""
    return f"<h1>User Report</h1><p>Name: {user.name}</p>"

def render_order_list(orders):
    """Render list of orders."""
    order_items = [render_order_item(order) for order in orders]
    return f"<ul>{''.join(order_items)}</ul>"

def render_order_item(order):
    """Render single order item."""
    return f"<li>Order #{order.id}: ${order.total}</li>"

def wrap_in_html_page(header, body):
    """Wrap content in HTML page structure."""
    return f"<html><body>{header}{body}</body></html>"

def save_report(user_id, html_content):
    """Save report to file."""
    filename = f"report_{user_id}.html"
    with open(filename, "w") as f:
        f.write(html_content)
```

### The Stepdown Rule (Clean Code)

**Rule**: Code should read like a top-down narrative. Each function should be followed by those at the next level of abstraction.

**Pattern**: TO [high-level], we [next level details], which [lower level details]

```java
// Stepdown example - read top to bottom
public class OrderProcessor {
    // Highest level - orchestration
    public void processOrder(Order order) {
        validateOrder(order);
        calculateTotals(order);
        applyDiscounts(order);
        chargePayment(order);
        fulfillOrder(order);
    }

    // Next level - validation details
    private void validateOrder(Order order) {
        validateCustomer(order.getCustomer());
        validateItems(order.getItems());
        validateShippingAddress(order.getShippingAddress());
    }

    // Next level - customer validation details
    private void validateCustomer(Customer customer) {
        if (customer.isBlocked()) {
            throw new ValidationException("Customer is blocked");
        }
        if (!customer.hasValidPaymentMethod()) {
            throw new ValidationException("No valid payment method");
        }
    }

    // Next level - items validation details
    private void validateItems(List<OrderItem> items) {
        if (items.isEmpty()) {
            throw new ValidationException("Order has no items");
        }
        for (OrderItem item : items) {
            validateItemAvailability(item);
        }
    }

    // Continuing stepdown...
}
```

**Reading Flow**:
1. TO process an order, we validate, calculate, discount, charge, and fulfill
2. TO validate an order, we validate customer, items, and address
3. TO validate customer, we check if blocked and has payment method
4. (Each level naturally flows to the next)

## Function Parameters (Code Complete 2 & Clean Code)

### The Ideal Number of Parameters

**Research-Based Guidelines**:
- **Ideal**: 0 parameters (niladic functions)
- **Good**: 1 parameter (monadic functions)
- **Acceptable**: 2 parameters (dyadic functions)
- **Questionable**: 3 parameters (triadic functions)
- **Avoid**: 4+ parameters (polyadic functions)

**Why fewer is better**:
- Easier to understand
- Simpler to test (fewer combinations)
- Less coupling between caller and callee
- Harder to make mistakes

### Zero Parameters (Best)

```python
# Niladic functions - easiest to use
def get_current_timestamp():
    """Get current Unix timestamp."""
    return time.time()

def generate_unique_id():
    """Generate globally unique identifier."""
    return str(uuid.uuid4())

def is_production_environment():
    """Check if running in production."""
    return os.getenv("ENV") == "production"
```

**Benefit**: No state to pass in. No opportunity for error. Trivial to call.

### One Parameter (Good)

```python
# Monadic functions - still very clear
def calculate_square(number):
    """Calculate square of a number."""
    return number * number

def validate_email(email_address):
    """Validate email format."""
    return re.match(r'^[\w\.-]+@[\w\.-]+\.\w+$', email_address) is not None

def send_notification(user_id):
    """Send notification to user."""
    user = fetch_user(user_id)
    notification_service.send(user.email, "You have a new message")
```

**Common Forms of Monadic Functions**:

1. **Asking a question about the argument**:
```typescript
function fileExists(path: string): boolean { /* ... */ }
function isValidUser(userId: string): boolean { /* ... */ }
```

2. **Transforming the argument**:
```typescript
function parseJson(jsonString: string): object { /* ... */ }
function toLowerCase(text: string): string { /* ... */ }
```

3. **Event handling** (input, no output):
```typescript
function logError(error: Error): void { /* ... */ }
function trackPageView(url: string): void { /* ... */ }
```

### Two Parameters (Acceptable)

```java
// Dyadic functions - still reasonable
public Point createPoint(int x, int y) {
    return new Point(x, y);
}

public boolean authenticate(String username, String password) {
    return authService.verify(username, password);
}

public void copyFile(String sourcePath, String destinationPath) {
    Files.copy(Paths.get(sourcePath), Paths.get(destinationPath));
}
```

**Warning**: Two parameters require more mental effort:
- Which order?
- What's the relationship?
- Are both equally important?

**Natural Pairs**: Some concepts naturally come in pairs:
- Coordinates: `(x, y)`
- Range: `(start, end)`
- Key-value: `(key, value)`

### Three Parameters (Questionable)

```python
# Triadic functions - start to get complex
def create_user_account(username, email, password):
    """Create user account with credentials."""
    # Implementation

def calculate_loan_payment(principal, interest_rate, term_months):
    """Calculate monthly loan payment."""
    # Implementation

def send_email(recipient, subject, body):
    """Send email to recipient."""
    # Implementation
```

**Problems with Three Parameters**:
- Parameter order becomes unclear
- Testing requires 3-dimensional test cases
- Cognitive load increases significantly
- Often indicates missing abstraction

**Solution**: Consider parameter objects

```python
# Before: Three parameters
def create_user_account(username, email, password):
    pass

# After: Parameter object
class UserCredentials:
    def __init__(self, username, email, password):
        self.username = username
        self.email = email
        self.password = password

def create_user_account(credentials):
    """Create user account from credentials."""
    pass

# Usage
credentials = UserCredentials("john_doe", "john@example.com", "secret123")
create_user_account(credentials)
```

### Four or More Parameters (Avoid)

```typescript
// AVOID: Too many parameters
function createInvoice(
    customerId: string,
    amount: number,
    taxRate: number,
    currency: string,
    dueDate: Date,
    description: string
): Invoice {
    // Very hard to call correctly!
}

// Better: Use parameter object
interface InvoiceData {
    customerId: string;
    amount: number;
    taxRate: number;
    currency: string;
    dueDate: Date;
    description: string;
}

function createInvoice(data: InvoiceData): Invoice {
    // Much clearer!
}

// Usage
createInvoice({
    customerId: "CUST-123",
    amount: 1000.00,
    taxRate: 0.08,
    currency: "USD",
    dueDate: new Date("2024-12-31"),
    description: "Professional services"
});
```

### Parameter Object Pattern

When you have multiple parameters that naturally belong together, create a parameter object:

```java
// Before: Multiple related parameters
public void drawRectangle(int x, int y, int width, int height, String color, int borderWidth) {
    // Implementation
}

// After: Parameter object
public class Rectangle {
    private final Point position;
    private final Dimension size;
    private final Style style;

    public Rectangle(Point position, Dimension size, Style style) {
        this.position = position;
        this.size = size;
        this.style = style;
    }
}

public class Point {
    private final int x;
    private final int y;

    public Point(int x, int y) {
        this.x = x;
        this.y = y;
    }
}

public class Dimension {
    private final int width;
    private final int height;

    public Dimension(int width, int height) {
        this.width = width;
        this.height = height;
    }
}

public class Style {
    private final String color;
    private final int borderWidth;

    public Style(String color, int borderWidth) {
        this.color = color;
        this.borderWidth = borderWidth;
    }
}

// Usage - much clearer structure
public void drawRectangle(Rectangle rectangle) {
    // Implementation
}

drawRectangle(new Rectangle(
    new Point(10, 20),
    new Dimension(100, 50),
    new Style("blue", 2)
));
```

**Benefits of Parameter Objects**:
- Related parameters grouped logically
- Reduced parameter count
- Named fields make calls self-documenting
- Easier to extend (add fields without changing signature)
- Parameter objects can have validation methods

### Flag Arguments Are Ugly (Clean Code)

**Rule**: Boolean flags as parameters are a sign that your function does more than one thing.

**Anti-Pattern:**
```python
# BAD: Flag argument
def save_user(user, send_email):
    """Save user and optionally send email."""
    database.save(user)
    if send_email:
        email_service.send_welcome(user.email)
    # This function does TWO things!

# Usage is unclear
save_user(user, True)  # What does True mean?
```

**Better:**
```python
# GOOD: Separate functions
def save_user(user):
    """Save user to database."""
    database.save(user)

def save_user_and_send_welcome(user):
    """Save user and send welcome email."""
    save_user(user)
    send_welcome_email(user)

# Usage is crystal clear
save_user(user)
save_user_and_send_welcome(user)
```

**If you must use flags, make them explicit:**
```typescript
// Enum instead of boolean
enum NotificationPreference {
    SEND_EMAIL,
    NO_EMAIL
}

function saveUser(user: User, notification: NotificationPreference): void {
    database.save(user);
    if (notification === NotificationPreference.SEND_EMAIL) {
        emailService.sendWelcome(user.email);
    }
}

// Usage is self-documenting
saveUser(user, NotificationPreference.SEND_EMAIL);
saveUser(user, NotificationPreference.NO_EMAIL);
```

### Parameter Ordering (Code Complete 2)

When you must have multiple parameters, use consistent ordering:

**1. Most Important First:**
```python
def copy_file(source, destination):  # Source is primary
    pass

def send_email(recipient, subject, body):  # Recipient is primary
    pass
```

**2. Input, Output, Status:**
```java
public void readFile(String inputPath, StringBuilder outputBuffer, Status status) {
    // Input first, then output, then status
}
```

**3. Consistency:**
```python
# Be consistent across similar functions
def write_to_file(filename, data):
    pass

def append_to_file(filename, data):  # Same order
    pass

def read_from_file(filename):  # Same filename position
    pass
```

### Output Parameters (Code Complete 2)

**Prefer Return Values Over Output Parameters:**

**Anti-Pattern:**
```java
// Output parameter - confusing
public void calculateTotals(Order order, TotalResult result) {
    result.setSubtotal(calculateSubtotal(order));
    result.setTax(calculateTax(order));
    result.setTotal(result.getSubtotal() + result.getTax());
}

// Usage - what's getting modified?
TotalResult result = new TotalResult();
calculateTotals(order, result);
```

**Better:**
```java
// Return value - clear and functional
public TotalResult calculateTotals(Order order) {
    double subtotal = calculateSubtotal(order);
    double tax = calculateTax(order);
    double total = subtotal + tax;
    return new TotalResult(subtotal, tax, total);
}

// Usage - clear that we're getting a new result
TotalResult result = calculateTotals(order);
```

**Exception**: Output parameters are acceptable when returning multiple related values in languages without tuples:

```python
# Python: Use tuples to return multiple values
def calculate_statistics(numbers):
    """Calculate mean, median, and std dev."""
    mean = sum(numbers) / len(numbers)
    median = sorted(numbers)[len(numbers) // 2]
    std_dev = calculate_std_dev(numbers, mean)
    return mean, median, std_dev  # Return tuple

# Usage
mean, median, std_dev = calculate_statistics([1, 2, 3, 4, 5])
```

## Function vs Procedure (Code Complete 2)

### The Distinction

**Function**: Returns a value and typically doesn't modify state.
**Procedure**: Performs an action and typically doesn't return a meaningful value (void).

```python
# Function - returns value, no side effects
def calculate_total(items):
    """Calculate total of items - FUNCTION"""
    return sum(item.price for item in items)

# Procedure - performs action, modifies state
def save_to_database(user):
    """Save user to database - PROCEDURE"""
    database.execute("INSERT INTO users VALUES (?)", user)
    # No return value, modifies database state
```

### Naming Convention

**Functions** (return values): Use nouns or noun phrases
```typescript
// Functions - what they return
function getUsername(userId: string): string { /* ... */ }
function calculateTotal(items: Item[]): number { /* ... */ }
function parseJson(text: string): object { /* ... */ }
```

**Procedures** (perform actions): Use verbs
```typescript
// Procedures - what they do
function saveUser(user: User): void { /* ... */ }
function sendEmail(recipient: string, body: string): void { /* ... */ }
function logError(error: Error): void { /* ... */ }
```

### Command-Query Separation (Clean Code)

**Principle**: Functions should either answer a question (query) or perform an action (command), but not both.

**Anti-Pattern:**
```java
// VIOLATION: Both command and query
public boolean setUsername(User user, String username) {
    if (isValidUsername(username)) {
        user.setUsername(username);  // Command: modify state
        return true;  // Query: return status
    }
    return false;
}

// Confusing usage:
if (setUsername(user, "john_doe")) {
    // Did this just set the username? Or check if it was already set?
}
```

**Better:**
```java
// Separate command and query
public void setUsername(User user, String username) {
    if (!isValidUsername(username)) {
        throw new IllegalArgumentException("Invalid username");
    }
    user.setUsername(username);
}

public String getUsername(User user) {
    return user.getUsername();
}

// Clear usage:
setUsername(user, "john_doe");  // Clearly an action
String name = getUsername(user);  // Clearly a query
```

**Acceptable Exception**: Mutation methods that return the mutated object for chaining:

```java
// Builder pattern - acceptable to return modified object
public class UserBuilder {
    public UserBuilder setName(String name) {
        this.name = name;
        return this;  // Allow chaining
    }

    public UserBuilder setEmail(String email) {
        this.email = email;
        return this;  // Allow chaining
    }

    public User build() {
        return new User(name, email);
    }
}

// Usage:
User user = new UserBuilder()
    .setName("John Doe")
    .setEmail("john@example.com")
    .build();
```

## Have No Side Effects (Clean Code)

**Principle**: Functions should not have hidden side effects. If a function says it does X, it shouldn't secretly also do Y.

**Anti-Pattern - Hidden Side Effect:**
```python
# BAD: checkPassword has a hidden side effect
def check_password(username, password):
    """Check if password is valid for username."""
    user = database.get_user(username)
    if user.password_hash == hash_password(password):
        # HIDDEN SIDE EFFECT: Creates user session!
        session_manager.create_session(user)
        return True
    return False

# Caller doesn't expect session creation:
if check_password(username, password):
    # Session was created as a side effect!
    pass
```

**Better - Explicit Actions:**
```python
# GOOD: Separate authentication from session creation
def authenticate_user(username, password):
    """Authenticate user credentials."""
    user = database.get_user(username)
    return user.password_hash == hash_password(password)

def create_user_session(username):
    """Create new user session."""
    user = database.get_user(username)
    return session_manager.create_session(user)

# Explicit and clear:
if authenticate_user(username, password):
    create_user_session(username)
```

### Temporal Coupling

**Problem**: Hidden side effects create temporal coupling—operations must be called in a specific order.

**Anti-Pattern:**
```typescript
// Hidden temporal coupling
class PasswordManager {
    private user: User | null = null;

    // Secretly sets this.user
    checkPassword(username: string, password: string): boolean {
        this.user = database.getUser(username);  // SIDE EFFECT
        return this.user.passwordHash === hashPassword(password);
    }

    // Requires checkPassword called first!
    resetPassword(newPassword: string): void {
        // Depends on this.user being set!
        if (this.user) {
            this.user.passwordHash = hashPassword(newPassword);
            database.save(this.user);
        }
    }
}

// Usage - temporal coupling not obvious
manager.checkPassword("john", "secret");
manager.resetPassword("newsecret");  // Only works because checkPassword called first!
```

**Better - Explicit Dependencies:**
```typescript
// Explicit parameters, no hidden state
class PasswordManager {
    checkPassword(username: string, password: string): boolean {
        const user = database.getUser(username);
        return user.passwordHash === hashPassword(password);
    }

    resetPassword(username: string, newPassword: string): void {
        const user = database.getUser(username);
        user.passwordHash = hashPassword(newPassword);
        database.save(user);
    }
}

// Usage - no hidden dependencies
manager.checkPassword("john", "secret");
manager.resetPassword("john", "newsecret");  // Explicit username
```

## Don't Repeat Yourself (DRY) (Clean Code)

**Principle**: Duplication is the root of all evil in software. Every piece of knowledge should have a single, unambiguous representation.

**Anti-Pattern - Duplication:**
```java
// Duplicated validation logic
public class OrderService {
    public void createOrder(Order order) {
        if (order.getItems().isEmpty()) {
            throw new IllegalArgumentException("Order must have items");
        }
        if (order.getTotal() <= 0) {
            throw new IllegalArgumentException("Order total must be positive");
        }
        if (order.getCustomer() == null) {
            throw new IllegalArgumentException("Order must have customer");
        }
        // Create order
    }

    public void updateOrder(Order order) {
        // EXACT SAME VALIDATION DUPLICATED
        if (order.getItems().isEmpty()) {
            throw new IllegalArgumentException("Order must have items");
        }
        if (order.getTotal() <= 0) {
            throw new IllegalArgumentException("Order total must be positive");
        }
        if (order.getCustomer() == null) {
            throw new IllegalArgumentException("Order must have customer");
        }
        // Update order
    }
}
```

**Better - Extract Common Logic:**
```java
// Single source of truth
public class OrderService {
    private void validateOrder(Order order) {
        if (order.getItems().isEmpty()) {
            throw new IllegalArgumentException("Order must have items");
        }
        if (order.getTotal() <= 0) {
            throw new IllegalArgumentException("Order total must be positive");
        }
        if (order.getCustomer() == null) {
            throw new IllegalArgumentException("Order must have customer");
        }
    }

    public void createOrder(Order order) {
        validateOrder(order);
        // Create order
    }

    public void updateOrder(Order order) {
        validateOrder(order);
        // Update order
    }
}
```

### Types of Duplication

**1. Copy-Paste Duplication (Obvious)**
```python
# BAD: Copied code blocks
def calculate_employee_salary(employee):
    base_salary = employee.base_salary
    bonus = base_salary * 0.1
    tax = (base_salary + bonus) * 0.25
    return base_salary + bonus - tax

def calculate_contractor_payment(contractor):
    base_payment = contractor.base_payment
    bonus = base_payment * 0.1  # Same calculation
    tax = (base_payment + bonus) * 0.25  # Same calculation
    return base_payment + bonus - tax  # Same formula
```

**2. Algorithmic Duplication (Subtle)**
```python
# BAD: Same algorithm, different code
def find_max_number(numbers):
    max_val = numbers[0]
    for num in numbers:
        if num > max_val:
            max_val = num
    return max_val

def find_oldest_user(users):
    oldest = users[0]
    for user in users:  # Same algorithm!
        if user.age > oldest.age:
            oldest = user
    return oldest

# GOOD: Extract common algorithm
def find_maximum(items, key_function=None):
    if key_function is None:
        key_function = lambda x: x

    max_item = items[0]
    max_value = key_function(max_item)

    for item in items:
        value = key_function(item)
        if value > max_value:
            max_value = value
            max_item = item

    return max_item

# Usage
max_number = find_maximum([1, 5, 3, 9, 2])
oldest_user = find_maximum(users, key_function=lambda u: u.age)
```

**3. Representational Duplication (Knowledge)**
```typescript
// BAD: Business rule duplicated in validation and calculation
function validateDiscount(orderTotal: number, discount: number): boolean {
    // Rule: Discount can't exceed 20% of total
    return discount <= orderTotal * 0.20;
}

function calculateMaxDiscount(orderTotal: number): number {
    // SAME RULE duplicated
    return orderTotal * 0.20;
}

// GOOD: Single representation of business rule
class DiscountPolicy {
    private static readonly MAX_DISCOUNT_PERCENTAGE = 0.20;

    static getMaxDiscountPercentage(): number {
        return this.MAX_DISCOUNT_PERCENTAGE;
    }

    static calculateMaxDiscount(orderTotal: number): number {
        return orderTotal * this.MAX_DISCOUNT_PERCENTAGE;
    }

    static isValidDiscount(orderTotal: number, discount: number): boolean {
        return discount <= this.calculateMaxDiscount(orderTotal);
    }
}
```

## Practical Function Design Checklist

Use this checklist when creating or reviewing functions:

### Design Phase
- [ ] Function has a single, clear purpose (one thing)
- [ ] Function name accurately describes what it does
- [ ] Function has high cohesion (preferably functional)
- [ ] Function is at one level of abstraction
- [ ] Function has 0-2 parameters (3 maximum)
- [ ] No flag/boolean parameters
- [ ] No output parameters (prefer return values)

### Implementation Phase
- [ ] Function is small (preferably < 20 lines)
- [ ] Function body matches abstraction level of name
- [ ] No duplicate code within or across functions
- [ ] No hidden side effects
- [ ] No temporal coupling
- [ ] Command-query separation maintained
- [ ] Function follows team naming conventions

### Error Handling Phase
- [ ] Errors handled appropriately (covered in detail in ERROR_HANDLING.md)
- [ ] No swallowed exceptions
- [ ] Clear error messages
- [ ] Input validation at boundaries

### Testing Phase
- [ ] Function is testable (clear inputs/outputs)
- [ ] Function has comprehensive unit tests
- [ ] Edge cases identified and tested
- [ ] Function behavior documented in tests

### Review Phase
- [ ] Function reads like well-written prose
- [ ] Function would be clear to a new team member
- [ ] Function name makes code self-documenting
- [ ] Function could be reused in other contexts
- [ ] Function improves overall code organization

## Common Function Anti-Patterns

### 1. The God Function

**Problem**: Function does everything.

```python
# ANTI-PATTERN: 200-line function
def process_everything(data):
    """Process all data - GOD FUNCTION"""
    # Validation (30 lines)
    # Transformation (40 lines)
    # Database operations (50 lines)
    # API calls (30 lines)
    # Email sending (20 lines)
    # Logging (10 lines)
    # Error handling (20 lines)
    pass
```

**Solution**: Break into single-purpose functions following the principles in this guide.

### 2. The Flag Function

**Problem**: Boolean parameter controls behavior.

```typescript
// ANTI-PATTERN: Flag argument
function processUser(user: User, isAdmin: boolean): void {
    if (isAdmin) {
        // Admin processing
    } else {
        // Regular user processing
    }
}
```

**Solution**: Separate functions or polymorphism.

### 3. The Swiss Army Function

**Problem**: Function does different things based on type parameter.

```java
// ANTI-PATTERN: Type-based behavior
public void handle(String type, Object data) {
    switch (type) {
        case "user": handleUser((User) data); break;
        case "order": handleOrder((Order) data); break;
        case "product": handleProduct((Product) data); break;
    }
}
```

**Solution**: Polymorphism or separate functions.

### 4. The Mystery Function

**Problem**: Function name doesn't reveal what it does.

```python
# ANTI-PATTERN: Unclear name
def process():  # Process what?
    pass

def handle_data():  # Handle how? What data?
    pass

def do_stuff(x, y):  # What stuff?
    pass
```

**Solution**: Descriptive names that reveal intent.

### 5. The Side Effect Function

**Problem**: Function has hidden side effects.

```typescript
// ANTI-PATTERN: Hidden side effect
function getUser(userId: string): User {
    const user = database.query(userId);
    analytics.trackUserAccess(userId);  // HIDDEN SIDE EFFECT
    return user;
}
```

**Solution**: Separate query from command or make side effect explicit in name.

### 6. The Output Parameter Function

**Problem**: Uses output parameters instead of return values.

```java
// ANTI-PATTERN: Output parameters
public void calculateTotals(Order order, Results results) {
    results.subtotal = calculateSubtotal(order);
    results.tax = calculateTax(order);
    results.total = results.subtotal + results.tax;
}
```

**Solution**: Return value or return multiple values.

### 7. The Deep Nesting Function

**Problem**: Multiple levels of indentation.

```python
# ANTI-PATTERN: Deep nesting
def process_order(order):
    if order is not None:
        if order.items:
            if order.customer:
                if order.customer.is_active:
                    if order.total > 0:
                        # Finally do the work 5 levels deep!
                        pass
```

**Solution**: Guard clauses and early returns.

```python
# GOOD: Guard clauses
def process_order(order):
    if order is None:
        raise ValueError("Order is required")
    if not order.items:
        raise ValueError("Order must have items")
    if not order.customer:
        raise ValueError("Order must have customer")
    if not order.customer.is_active:
        raise ValueError("Customer must be active")
    if order.total <= 0:
        raise ValueError("Order total must be positive")

    # Do the work at top level
```

### 8. The Temporal Coupling Function

**Problem**: Functions must be called in specific order.

```typescript
// ANTI-PATTERN: Temporal coupling
class ReportGenerator {
    private data: Data;

    loadData(): void {
        this.data = fetchData();
    }

    generateReport(): Report {
        // Only works if loadData was called first!
        return createReport(this.data);
    }
}
```

**Solution**: Make dependencies explicit.

```typescript
// GOOD: Explicit dependencies
class ReportGenerator {
    generateReport(data: Data): Report {
        return createReport(data);
    }
}

// Usage
const data = fetchData();
const report = generator.generateReport(data);
```

## Summary: The Golden Rules

1. **Small**: Functions should be 4-20 lines typically
2. **One Thing**: Do one thing, do it well, do it only
3. **One Abstraction Level**: All code at same abstraction level
4. **Stepdown**: Read code top-down, high to low abstraction
5. **Few Parameters**: 0-2 ideal, 3 maximum, avoid 4+
6. **No Flags**: Boolean parameters indicate multiple responsibilities
7. **Descriptive Names**: Name reveals intent completely
8. **No Side Effects**: Do what the name says, nothing more
9. **Command-Query Separation**: Either answer question or do action
10. **DRY**: Extract duplication ruthlessly

## Further Reading

- **Clean Code** (Chapter 3: Functions) - Robert C. Martin
- **Code Complete 2** (Chapter 7: High-Quality Routines) - Steve McConnell
- **Refactoring: Improving the Design of Existing Code** - Martin Fowler
- **Working Effectively with Legacy Code** - Michael Feathers

---

**Remember**: Functions are the first line of organization in any program. Well-designed functions are the foundation of maintainable, testable, and comprehensible code. Invest the time to get them right.
