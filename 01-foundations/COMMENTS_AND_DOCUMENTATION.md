# Comments and Documentation: Making Code Understandable

## Overview

Comments and documentation are the bridge between what code does and why it exists. Poor comments add noise, become outdated lies, and waste readers' time. Good comments explain intent, document decisions, warn of consequences, and amplify understanding where code alone cannot.

This comprehensive guide synthesizes commenting wisdom from industry-leading sources and provides practical, actionable guidance for writing comments that actually help.

**"The proper use of comments is to compensate for our failure to express ourselves in code."** — Robert C. Martin, Clean Code

## Why Comments Matter

### The Cost of Poor Comments

Poor comments create measurable costs:

**Maintenance Burden**: Outdated comments mislead maintainers. When code changes but comments don't, developers must figure out which is correct—the code or the comment. This wastes time and introduces bugs.

**Noise and Clutter**: Redundant comments that restate what code obviously does create visual noise. Developers learn to ignore all comments, missing the few that actually matter.

**False Confidence**: Bad comments create false understanding. A misleading comment is worse than no comment—it actively deceives readers and causes incorrect modifications.

**Documentation Debt**: When comments are poor, developers write external documentation that duplicates information, creating multiple sources of truth that drift apart over time.

### The Benefits of Good Comments

Good comments provide:
- **Intent Clarification**: Explain WHY, not WHAT
- **Historical Context**: Document decisions and alternatives considered
- **Warning of Consequences**: Alert readers to non-obvious side effects
- **Legal Protection**: Provide copyright, license, and attribution
- **API Documentation**: Enable automated doc generation
- **Onboarding Acceleration**: Help new developers understand quickly

## Source Materials

This guide synthesizes principles from:

- **Code Complete 2** by Steve McConnell (Chapter 32: "Self-Documenting Code")
  - Kinds of comments
  - Commenting effectively
  - Commenting techniques
  - Self-documenting code

- **Clean Code** by Robert C. Martin (Chapter 4: "Comments")
  - Comments do not make up for bad code
  - Explain yourself in code
  - Good comments
  - Bad comments
  - Don't comment bad code—rewrite it

## The Fundamental Principle (Clean Code)

### Comments Don't Make Up for Bad Code

**Anti-Pattern**: Writing comments to explain confusing code

```python
# BAD: Comment tries to explain bad code
# Check to see if employee is eligible for full benefits
if (employee.flags & HOURLY_FLAG) and (employee.age > 65):
    # Complex flag checking logic
    pass

# GOOD: Clear code needs no explanation
if employee.is_eligible_for_full_benefits():
    pass
```

**Key Insight**: When you feel the need to write a comment, first try to refactor the code to make it self-explanatory.

### Explain Yourself in Code (Clean Code)

**Principle**: Prefer expressive code over explanatory comments.

**Poor Example:**
```java
// Check if user has permission to delete order
if (user.getRole() == Role.ADMIN ||
    (user.getRole() == Role.MANAGER && user.getDepartment().equals(order.getDepartment()))) {
    // Delete logic
}

// Better: Extract to method
if (userCanDeleteOrder(user, order)) {
    // Delete logic
}

private boolean userCanDeleteOrder(User user, Order order) {
    return user.getRole() == Role.ADMIN ||
           (user.getRole() == Role.MANAGER &&
            user.getDepartment().equals(order.getDepartment()));
}
```

**When to Comment**: Only when code cannot be made clearer through better naming or structure.

## Good Comments (Clean Code)

### 1. Legal Comments

**Purpose**: Copyright, license, authorship required for legal or contractual reasons.

```python
# Copyright (c) 2024 Example Corporation
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
```

**Best Practice**: Keep legal comments short, refer to external license file.

```java
/**
 * Copyright 2024 Example Corporation
 * SPDX-License-Identifier: Apache-2.0
 * See LICENSE file for full text.
 */
```

### 2. Informative Comments

**Purpose**: Provide basic information that cannot be expressed in code alone.

```python
# Good: Explain regex pattern
# Format: XXX-XXXX-XXXX (3 digit area code, 4 digit prefix, 4 digit line number)
phone_pattern = r'^\d{3}-\d{4}-\d{4}$'

# Good: Explain return value when not obvious
def get_user_status(user_id):
    """
    Returns:
        0: Active user
        1: Inactive user
        2: Suspended user
        3: Deleted user
    """
    return database.query_user_status(user_id)
```

**Better**: Use constants or enums instead

```typescript
// Better: Self-documenting with enum
enum UserStatus {
    ACTIVE = 0,
    INACTIVE = 1,
    SUSPENDED = 2,
    DELETED = 3,
}

function getUserStatus(userId: string): UserStatus {
    return database.queryUserStatus(userId);
}
```

### 3. Explanation of Intent

**Purpose**: Explain WHY a decision was made, not WHAT the code does.

```java
// Good: Explains intent behind seemingly odd code
public int compareTo(Object o) {
    if (o instanceof WikiPagePath) {
        WikiPagePath p = (WikiPagePath) o;
        // We want to sort by path depth first, then alphabetically
        // This ensures parent pages appear before child pages
        int depthDiff = this.depth() - p.depth();
        if (depthDiff != 0) {
            return depthDiff;
        }
        return this.name.compareTo(p.name);
    }
    return 1;
}
```

```python
# Good: Explains business logic reasoning
def calculate_discount(order):
    # We give 10% discount on orders over $100, but only if the customer
    # has no outstanding invoices. This prevents customers from placing
    # large orders to get discounts while owing us money.
    if order.total > 100 and customer.outstanding_balance == 0:
        return order.total * 0.10
    return 0
```

### 4. Clarification

**Purpose**: Clarify obscure code that cannot be improved (third-party libraries, legacy constraints).

```python
# Good: Clarify obscure library behavior
result = library.process(data)
# Library returns None for empty input, [] for invalid input,
# and processed data for valid input. This inconsistency is a known issue.
if result is None:
    handle_empty_input()
elif result == []:
    handle_invalid_input()
else:
    handle_valid_result(result)
```

**Warning**: Clarification comments are risky—they can become outdated. Prefer improving the code.

### 5. Warning of Consequences

**Purpose**: Warn other developers about important consequences.

```java
// Good: Warning about expensive operation
/**
 * WARNING: This method performs a full table scan.
 * Do NOT call in production code paths. Use only for admin tools
 * and diagnostics. Expected execution time: 30-60 seconds.
 */
public List<User> getAllUsersFullScan() {
    return database.query("SELECT * FROM users");
}
```

```python
# Good: Warning about side effects
def reset_user_password(user_id, new_password):
    """
    Reset user password.

    WARNING: This immediately invalidates all existing user sessions
    and sends a password change notification email. Cannot be undone.
    """
    invalidate_all_sessions(user_id)
    update_password(user_id, new_password)
    send_password_change_email(user_id)
```

```typescript
// Good: Warning about thread safety
/**
 * WARNING: Not thread-safe. Must be called within a synchronized block
 * or with external locking. Concurrent calls will corrupt internal state.
 */
function updateSharedCounter(increment: number): void {
    // Non-atomic operations
    const current = this.counter;
    this.counter = current + increment;
}
```

### 6. TODO Comments

**Purpose**: Note work that should be done but cannot be done now.

```python
# Good: TODO with context and owner
# TODO(johndoe): Refactor this to use async/await pattern when we upgrade to Python 3.8+
# Current implementation blocks on network I/O
def fetch_user_data(user_id):
    return requests.get(f"/api/users/{user_id}").json()

# TODO(JIRA-1234): Remove this workaround when upstream bug is fixed
# See https://github.com/library/issues/567
def workaround_library_bug(data):
    # Temporary fix for library parsing issue
    return data.replace('\\n', '\n')
```

**Best Practices for TODOs**:
- Include owner or ticket number
- Explain what needs to be done and why
- Link to issue tracker if applicable
- Scan and clean up TODOs regularly

```java
// Good: Structured TODO format
/**
 * TODO(ISSUE-456): Implement retry logic with exponential backoff
 * Currently fails permanently on transient network errors.
 * Target: Q2 2024
 * Owner: @jane-smith
 */
public void makeNetworkRequest() {
    // Current implementation
}
```

### 7. Amplification

**Purpose**: Amplify the importance of something that might seem inconsequential.

```python
# Good: Amplify importance
def trim_whitespace(text):
    # The trim is critical here. Whitespace in usernames causes authentication
    # failures because the LDAP server is case-sensitive AND whitespace-sensitive.
    # We spent 3 hours debugging this. DO NOT REMOVE.
    return text.strip()
```

```typescript
// Good: Amplify non-obvious importance
function setSessionTimeout(minutes: number): void {
    // This timeout MUST match the database session cleanup interval (configured
    // in db_cleanup.sql). Mismatches cause session leaks that exhaust database
    // connections. See incident report INC-2023-045.
    this.sessionTimeoutMs = minutes * 60 * 1000;
}
```

### 8. Documentation Comments (Javadoc/JSDoc/Docstrings)

**Purpose**: Generate API documentation from code comments.

**Python (Docstrings):**
```python
def calculate_compound_interest(
    principal: float,
    annual_rate: float,
    years: int,
    compounds_per_year: int = 12
) -> float:
    """
    Calculate compound interest.

    Uses the standard compound interest formula:
    A = P(1 + r/n)^(nt)

    Args:
        principal: Initial investment amount in dollars
        annual_rate: Annual interest rate as decimal (0.05 = 5%)
        years: Number of years to compound
        compounds_per_year: Compounding frequency (default: 12 for monthly)

    Returns:
        Final amount after compounding

    Raises:
        ValueError: If principal is negative or rate is invalid

    Example:
        >>> calculate_compound_interest(1000, 0.05, 10)
        1647.01

    Note:
        Results are rounded to 2 decimal places for currency.
    """
    if principal < 0:
        raise ValueError("Principal cannot be negative")
    if annual_rate < 0 or annual_rate > 1:
        raise ValueError("Rate must be between 0 and 1")

    rate_per_period = annual_rate / compounds_per_year
    total_periods = years * compounds_per_year
    amount = principal * (1 + rate_per_period) ** total_periods

    return round(amount, 2)
```

**TypeScript (JSDoc):**
```typescript
/**
 * Processes a payment transaction with full validation and error handling.
 *
 * This method performs the following steps:
 * 1. Validates payment details and customer account
 * 2. Authorizes the charge with payment gateway
 * 3. Captures the funds
 * 4. Records the transaction in database
 * 5. Sends confirmation notification
 *
 * @param payment - The payment details including amount and method
 * @param customerId - Unique identifier for the customer
 * @param options - Optional processing options
 * @returns A promise that resolves to the completed transaction
 *
 * @throws {ValidationError} If payment details are invalid
 * @throws {PaymentGatewayError} If gateway authorization fails
 * @throws {InsufficientFundsError} If customer has insufficient funds
 *
 * @example
 * ```typescript
 * const transaction = await processPayment(
 *   { amount: 99.99, method: 'credit_card' },
 *   'cust_123',
 *   { sendReceipt: true }
 * );
 * console.log(transaction.id);
 * ```
 *
 * @see {@link PaymentGateway} for gateway integration details
 * @see {@link Transaction} for transaction object structure
 *
 * @since 2.0.0
 */
async function processPayment(
    payment: Payment,
    customerId: string,
    options?: PaymentOptions
): Promise<Transaction> {
    // Implementation
}
```

**Java (Javadoc):**
```java
/**
 * Service for managing user authentication and session management.
 *
 * <p>This service handles all aspects of user authentication including
 * password validation, session creation, and token management. All methods
 * are thread-safe and can be called concurrently.
 *
 * <p><b>Security Considerations:</b>
 * <ul>
 *   <li>Passwords are hashed using bcrypt with 12 rounds</li>
 *   <li>Sessions expire after 24 hours of inactivity</li>
 *   <li>Failed login attempts are rate-limited</li>
 * </ul>
 *
 * @author Jane Smith
 * @version 2.1.0
 * @since 1.0.0
 */
public class AuthenticationService {

    /**
     * Authenticates a user with email and password.
     *
     * <p>This method verifies the credentials against stored user data
     * and creates a new session if authentication succeeds. Failed attempts
     * are logged and counted toward rate limiting.
     *
     * @param email the user's email address (must be valid format)
     * @param password the user's password (must be non-empty)
     * @return an authenticated session with access token
     * @throws AuthenticationException if credentials are invalid
     * @throws AccountLockedException if account is locked due to failed attempts
     * @throws IllegalArgumentException if email or password is null
     *
     * @see #createSession(User)
     * @see Session
     */
    public Session authenticate(String email, String password)
        throws AuthenticationException, AccountLockedException {
        // Implementation
    }
}
```

## Bad Comments (Clean Code)

### 1. Mumbling

**Problem**: Unclear comments that don't add value.

```python
# BAD: Mumbling - doesn't explain anything
def load_properties():
    # Load the properties
    properties = {}
    # ... code to load properties
    return properties

# GOOD: Either remove comment or explain WHY
def load_properties():
    """
    Load application properties from config file.
    Properties are cached for 5 minutes to reduce disk I/O.
    """
    properties = {}
    # ... code to load properties
    return properties
```

### 2. Redundant Comments

**Problem**: Comment restates what code obviously does.

```java
// BAD: Redundant - code is self-explanatory
// Get the user name
String userName = user.getName();

// Set the age to 30
user.setAge(30);

// Return the total
return total;

// GOOD: No comment needed - code is clear
String userName = user.getName();
user.setAge(30);
return total;
```

```typescript
// BAD: Redundant method documentation
/**
 * Gets the user by ID.
 * @param id The ID
 * @returns The user
 */
function getUserById(id: string): User {
    return database.findUser(id);
}

// GOOD: Only document if there's useful information
/**
 * Retrieves user from database with full profile including permissions.
 * Results are cached for 5 minutes. Returns null if user not found.
 */
function getUserById(id: string): User | null {
    return database.findUser(id);
}
```

### 3. Misleading Comments

**Problem**: Comment is incorrect or outdated.

```python
# BAD: Misleading - comment doesn't match code
def calculate_total(items):
    # Calculate total with 10% discount
    total = sum(item.price for item in items)
    # Code doesn't actually apply discount!
    return total

# GOOD: Remove misleading comment
def calculate_total(items):
    return sum(item.price for item in items)

# Or fix the code to match comment
def calculate_total_with_discount(items):
    subtotal = sum(item.price for item in items)
    return subtotal * 0.90  # Apply 10% discount
```

### 4. Mandated Comments

**Problem**: Required comments for every function create noise.

```java
// BAD: Mandated useless documentation
/**
 * Constructor.
 * @param name The name
 * @param age The age
 * @param email The email
 */
public User(String name, int age, String email) {
    this.name = name;
    this.age = age;
    this.email = email;
}

// GOOD: Only document when there's useful information
/**
 * Creates a new user with validation.
 * Email is normalized to lowercase. Age must be 18+.
 * @throws ValidationException if email invalid or age < 18
 */
public User(String name, int age, String email) {
    validateAge(age);
    this.name = name;
    this.age = age;
    this.email = email.toLowerCase();
}
```

### 5. Journal Comments

**Problem**: Change log in comments (version control does this better).

```python
# BAD: Journal comments
# Changes:
# 2024-01-15: Added email validation - John Doe
# 2024-01-20: Fixed bug in password hashing - Jane Smith
# 2024-01-25: Refactored to use async - Bob Johnson
# 2024-02-01: Added rate limiting - Alice Williams
def create_user(email, password):
    # Just use version control!
    pass

# GOOD: No journal - use git log instead
def create_user(email, password):
    # Implementation
    pass
```

### 6. Noise Comments

**Problem**: Comments that state the obvious or add no value.

```typescript
// BAD: Noise comments
class User {
    // The user's name
    private name: string;

    // The user's email
    private email: string;

    // Default constructor
    constructor() {
        // Set name to empty string
        this.name = "";
        // Set email to empty string
        this.email = "";
    }
}

// GOOD: Remove noise
class User {
    private name: string;
    private email: string;

    constructor() {
        this.name = "";
        this.email = "";
    }
}
```

### 7. Scary Noise

**Problem**: Copy-pasted doc comments with incorrect information.

```java
// BAD: Copy-paste error in docs
/**
 * Returns the day of the month.
 * @return the day of the month
 */
public int getMonth() {  // Method name doesn't match comment!
    return month;
}

/**
 * Returns the day of the month.  // Wrong! This is the year!
 * @return the day of the month
 */
public int getYear() {
    return year;
}
```

### 8. Commented-Out Code

**Problem**: Dead code left in comments clutters the codebase.

```python
# BAD: Commented-out code
def process_order(order):
    validate_order(order)
    # calculate_shipping(order)  # Old way - don't delete!
    # apply_discount(order)       # Might need this later
    # send_confirmation(order)    # Temporarily disabled
    process_payment(order)
    ship_order(order)

# GOOD: Delete it! Version control preserves history
def process_order(order):
    validate_order(order)
    process_payment(order)
    ship_order(order)
```

**Why it's bad**:
- Others don't know if it's important
- Clutters the code
- Becomes outdated
- Version control preserves history

### 9. HTML in Comments

**Problem**: HTML markup makes comments unreadable in source code.

```java
// BAD: HTML in source comments
/**
 * <p>This method processes a payment transaction.</p>
 * <ul>
 *   <li>Validates payment details</li>
 *   <li>Charges the payment method</li>
 *   <li>Records the transaction</li>
 * </ul>
 * <p><b>Note:</b> This is thread-safe.</p>
 */
public void processPayment(Payment payment) {
    // Unreadable in source code
}

// GOOD: Plain text that's readable everywhere
/**
 * Processes a payment transaction with these steps:
 * - Validates payment details
 * - Charges the payment method
 * - Records the transaction
 *
 * Note: This method is thread-safe.
 */
public void processPayment(Payment payment) {
    // Readable in source and generated docs
}
```

### 10. Nonlocal Information

**Problem**: Comment describes something far away from current context.

```python
# BAD: Comment describes distant code
def validate_user_input(user_input):
    # The default port is 8080 and can be changed in config.py
    # This has nothing to do with validating user input!
    if not user_input:
        raise ValueError("Input required")
    return True

# GOOD: Keep comments local
# In config.py:
DEFAULT_PORT = 8080  # Can be overridden via environment variable PORT

# In validation.py:
def validate_user_input(user_input):
    if not user_input:
        raise ValueError("Input required")
    return True
```

## Self-Documenting Code (Code Complete 2)

### Techniques for Self-Documenting Code

**1. Use Meaningful Names**

```typescript
// Poor: Needs comment to explain
let d: number;  // Days since creation

// Good: Self-explanatory
let daysSinceCreation: number;
```

**2. Extract Complex Expressions into Named Variables**

```python
# Poor: Needs comment
# Check if user is premium and eligible for discount
if user.tier == 'premium' and user.purchases > 10 and user.account_age > 365:
    apply_discount()

# Good: Self-documenting
is_premium_user = user.tier == 'premium'
has_frequent_purchases = user.purchases > 10
is_long_term_customer = user.account_age > 365

if is_premium_user and has_frequent_purchases and is_long_term_customer:
    apply_discount()
```

**3. Extract Functions**

```java
// Poor: Needs comments
public void processOrder(Order order) {
    // Validate order
    if (order.getItems().isEmpty()) {
        throw new ValidationException("No items");
    }
    if (order.getCustomer() == null) {
        throw new ValidationException("No customer");
    }

    // Calculate total
    double subtotal = 0;
    for (Item item : order.getItems()) {
        subtotal += item.getPrice() * item.getQuantity();
    }
    double tax = subtotal * TAX_RATE;
    double total = subtotal + tax;
    order.setTotal(total);
}

// Good: Functions are self-documenting
public void processOrder(Order order) {
    validateOrder(order);
    calculateOrderTotal(order);
}

private void validateOrder(Order order) {
    if (order.getItems().isEmpty()) {
        throw new ValidationException("Order must have items");
    }
    if (order.getCustomer() == null) {
        throw new ValidationException("Order must have customer");
    }
}

private void calculateOrderTotal(Order order) {
    double subtotal = calculateSubtotal(order.getItems());
    double tax = subtotal * TAX_RATE;
    order.setTotal(subtotal + tax);
}
```

**4. Use Named Constants Instead of Magic Numbers**

```python
# Poor: Magic numbers need comments
if age > 65:  # Retirement age
    apply_senior_discount()

if speed > 120:  # Speed limit in km/h
    issue_speeding_ticket()

# Good: Named constants are self-documenting
RETIREMENT_AGE = 65
SPEED_LIMIT_KMH = 120

if age > RETIREMENT_AGE:
    apply_senior_discount()

if speed > SPEED_LIMIT_KMH:
    issue_speeding_ticket()
```

**5. Use Enums Instead of Boolean Flags**

```typescript
// Poor: Boolean flag needs comment
function saveUser(user: User, sendEmail: boolean) {
    database.save(user);
    if (sendEmail) {  // What email? When? Why?
        emailService.send(user.email, "Welcome");
    }
}

// Good: Enum is self-documenting
enum NotificationPreference {
    SEND_WELCOME_EMAIL,
    NO_EMAIL,
}

function saveUser(
    user: User,
    notification: NotificationPreference
) {
    database.save(user);
    if (notification === NotificationPreference.SEND_WELCOME_EMAIL) {
        emailService.sendWelcome(user.email);
    }
}
```

### When Code Cannot Be Self-Documenting

**Complex Algorithms**: Explain the algorithm choice and its complexity

```python
def quicksort(arr):
    """
    Sort array using quicksort algorithm.

    Time complexity: O(n log n) average, O(n²) worst case
    Space complexity: O(log n) for recursion stack

    We use quicksort instead of mergesort because:
    - In-place sorting (lower memory usage)
    - Better cache locality
    - Faster for our typical input patterns (mostly sorted data)

    Note: For guaranteed O(n log n), consider using heapsort or mergesort.
    """
    if len(arr) <= 1:
        return arr

    pivot = arr[len(arr) // 2]
    left = [x for x in arr if x < pivot]
    middle = [x for x in arr if x == pivot]
    right = [x for x in arr if x > pivot]

    return quicksort(left) + middle + quicksort(right)
```

**Business Rules**: Document the business logic reasoning

```java
/**
 * Calculates the late fee for overdue invoices.
 *
 * Business Rules:
 * - First 7 days: No late fee (grace period)
 * - Days 8-30: 1.5% per month (18% annual)
 * - After 30 days: 2% per month (24% annual)
 * - Maximum late fee: 50% of original invoice amount
 *
 * These rates were negotiated with the finance team and approved
 * by legal. DO NOT CHANGE without finance approval.
 *
 * See: Financial Policy Document FP-2024-001
 */
public BigDecimal calculateLateFee(Invoice invoice, int daysOverdue) {
    // Implementation
}
```

**Workarounds**: Document why the workaround exists

```typescript
/**
 * WORKAROUND: Safari doesn't support lookbehind in regex
 *
 * The proper regex would be: /(?<=@)\w+/
 * But Safari < 16.4 doesn't support lookbehind assertions.
 *
 * This workaround uses a capturing group instead.
 * Remove this when Safari 16.4+ reaches 95% market share.
 *
 * Tracking: https://caniuse.com/js-regexp-lookbehind
 */
function extractDomain(email: string): string {
    const match = email.match(/@(\w+)/);
    return match ? match[1] : '';
}
```

## Kinds of Comments (Code Complete 2)

### 1. Repeat of the Code (BAD)

```python
# BAD: Repeats what code says
counter += 1  # Increment counter
if user is None:  # If user is None
    return  # Return
```

### 2. Explanation of the Code (ACCEPTABLE)

```python
# ACCEPTABLE: Explains what code does
# Parse ISO 8601 date format: YYYY-MM-DDTHH:MM:SS
date = datetime.strptime(date_string, "%Y-%m-%dT%H:%M:%S")
```

### 3. Marker in the Code (GOOD)

```java
// GOOD: Marks sections for navigation
public class OrderService {
    // ========== Public API Methods ==========

    public Order createOrder(OrderRequest request) { }
    public Order updateOrder(Long id, OrderRequest request) { }

    // ========== Validation Methods ==========

    private void validateOrder(OrderRequest request) { }
    private void validateItems(List<OrderItem> items) { }

    // ========== Calculation Methods ==========

    private BigDecimal calculateTotal(Order order) { }
    private BigDecimal calculateTax(BigDecimal subtotal) { }
}
```

### 4. Summary of the Code (GOOD)

```python
# GOOD: Summarizes what following code does
def process_batch_import(file_path):
    """Process batch import from CSV file."""

    # Read and validate CSV structure
    data = read_csv_file(file_path)
    validate_csv_headers(data)

    # Transform data to internal format
    transformed = transform_import_data(data)

    # Validate business rules
    validate_business_rules(transformed)

    # Save to database in transaction
    with database.transaction():
        save_imported_data(transformed)

    # Send completion notification
    notify_import_complete(file_path, len(transformed))
```

### 5. Description of the Code's Intent (BEST)

```java
// BEST: Describes intent, not implementation
/**
 * Ensures user has permission to access resource.
 *
 * Intent: Fail fast if user lacks permission before doing expensive work.
 * We check permissions here rather than in the database layer to avoid
 * loading the full resource unnecessarily.
 */
private void checkPermission(User user, Resource resource) {
    if (!user.hasPermission(resource.getRequiredPermission())) {
        throw new PermissionDeniedException();
    }
}
```

### 6. Information That Cannot Be Expressed in Code (BEST)

```python
# BEST: Information code cannot express
def retry_with_backoff(operation, max_attempts=3):
    """
    Retry operation with exponential backoff.

    Uses exponential backoff to avoid overwhelming the service:
    - Attempt 1: Immediate
    - Attempt 2: 1 second delay
    - Attempt 3: 2 second delay
    - Attempt 4: 4 second delay

    This pattern helps when the service is experiencing temporary overload.
    If all retries fail, the original exception is raised.

    Historical Note: Added after incident INC-2024-023 where our retry storm
    made a service outage worse. The backoff prevents thundering herd.
    """
    pass
```

## Commenting Techniques (Code Complete 2)

### 1. Comment the Why, Not the What

```typescript
// BAD: Comments the what
// Set timeout to 30 seconds
const timeout = 30000;

// GOOD: Comments the why
// 30 second timeout prevents indefinite hangs when external API is down
// This value was determined by measuring 99th percentile response time (12s)
// and adding 150% buffer for network variability
const TIMEOUT_MS = 30000;
```

### 2. Comment the Unexpected

```python
# GOOD: Explain unexpected behavior
def calculate_price(base_price, quantity):
    # We intentionally don't apply volume discounts here.
    # Volume discounts are calculated at checkout to prevent gaming the system
    # by splitting orders. See pricing policy document PP-2024-15.
    return base_price * quantity
```

### 3. Comment Preconditions and Postconditions

```java
/**
 * Transfer funds between accounts.
 *
 * Preconditions:
 * - Both accounts must exist and be active
 * - Source account must have sufficient balance
 * - Amount must be positive
 * - Both accounts must be in the same currency
 *
 * Postconditions:
 * - Source balance decreased by amount
 * - Destination balance increased by amount
 * - Transaction record created
 * - Notification sent to both parties
 * - Sum of all balances unchanged (conservation of money)
 */
public void transferFunds(
    Account source,
    Account destination,
    BigDecimal amount
) {
    // Implementation
}
```

### 4. Comment Edge Cases

```python
def divide(a, b):
    """
    Divide a by b.

    Edge cases:
    - Division by zero returns infinity (matches IEEE 754)
    - 0/0 returns NaN
    - Very small denominators may cause precision loss
    - Result rounded to 10 decimal places for currency safety
    """
    if b == 0:
        return float('inf') if a != 0 else float('nan')
    return round(a / b, 10)
```

### 5. Document Assumptions

```typescript
/**
 * Calculate shipping cost based on weight and destination.
 *
 * Assumptions:
 * - Weight is in kilograms (we don't handle pounds)
 * - Destination is a valid US ZIP code
 * - Shipping rates are updated weekly via cron job
 * - Rates table exists and is populated
 *
 * If any assumption is violated, method throws IllegalArgumentException.
 */
function calculateShippingCost(weightKg: number, zipCode: string): number {
    // Implementation
}
```

## Documentation Standards for Different Audiences

### 1. Developer Documentation (Code Level)

**Purpose**: Help developers understand and modify code

```python
class PaymentProcessor:
    """
    Process payment transactions through payment gateway.

    This class handles all payment operations including authorization,
    capture, refund, and void. It manages the lifecycle of payment
    transactions and ensures proper error handling and logging.

    Thread Safety: This class is thread-safe. All public methods can
    be called concurrently.

    Dependencies:
    - PaymentGateway: External gateway client
    - TransactionRepository: Database persistence
    - NotificationService: Customer notifications

    Configuration:
    - GATEWAY_API_KEY: Set via environment variable
    - TIMEOUT_MS: Default 30000, configurable
    - MAX_RETRIES: Default 3, configurable

    Example:
        processor = PaymentProcessor(gateway, repository)
        transaction = processor.authorize_payment(payment_details)
        processor.capture_payment(transaction.id)
    """

    def authorize_payment(self, payment: Payment) -> Transaction:
        """
        Authorize payment with gateway but don't capture funds.

        This places a hold on the customer's payment method without
        actually transferring funds. Useful for pre-authorization flows.

        Args:
            payment: Payment details including amount and method

        Returns:
            Authorized transaction with auth_code

        Raises:
            PaymentValidationError: If payment details invalid
            GatewayError: If gateway authorization fails
            InsufficientFundsError: If customer has insufficient funds

        Note:
            Authorizations expire after 7 days. Call capture_payment
            within this window or the authorization will be voided.
        """
        pass
```

### 2. API Documentation (Integration Level)

**Purpose**: Help API consumers integrate with your service

```typescript
/**
 * @api {post} /api/v1/orders Create Order
 * @apiName CreateOrder
 * @apiGroup Orders
 * @apiVersion 1.0.0
 *
 * @apiDescription
 * Creates a new order with the specified items and customer information.
 * This endpoint handles order validation, inventory checking, and payment
 * processing in a single atomic operation.
 *
 * @apiHeader {String} Authorization Bearer token for authentication
 * @apiHeader {String} Content-Type Must be application/json
 *
 * @apiParam {String} customerId Unique customer identifier
 * @apiParam {Object[]} items Array of order items
 * @apiParam {String} items.productId Product identifier
 * @apiParam {Number} items.quantity Quantity (must be positive integer)
 * @apiParam {Object} shipping Shipping information
 * @apiParam {String} shipping.address Street address
 * @apiParam {String} shipping.city City name
 * @apiParam {String} shipping.zipCode ZIP code
 *
 * @apiSuccess {String} orderId Unique order identifier
 * @apiSuccess {Number} total Total order amount in dollars
 * @apiSuccess {String} status Order status (always 'pending' on creation)
 * @apiSuccess {String} estimatedDelivery Estimated delivery date (ISO 8601)
 *
 * @apiError (400) ValidationError Invalid request parameters
 * @apiError (401) Unauthorized Missing or invalid authentication token
 * @apiError (409) InsufficientStock One or more items out of stock
 * @apiError (500) InternalError Unexpected server error
 *
 * @apiExample {curl} Example Request:
 *     curl -X POST https://api.example.com/api/v1/orders \
 *       -H "Authorization: Bearer YOUR_TOKEN" \
 *       -H "Content-Type: application/json" \
 *       -d '{
 *         "customerId": "cust_123",
 *         "items": [
 *           {"productId": "prod_456", "quantity": 2}
 *         ],
 *         "shipping": {
 *           "address": "123 Main St",
 *           "city": "Springfield",
 *           "zipCode": "12345"
 *         }
 *       }'
 *
 * @apiSuccessExample {json} Success Response:
 *     HTTP/1.1 201 Created
 *     {
 *       "orderId": "ord_789",
 *       "total": 99.98,
 *       "status": "pending",
 *       "estimatedDelivery": "2024-12-25"
 *     }
 */
async function createOrder(req: Request, res: Response): Promise<void> {
    // Implementation
}
```

### 3. User Documentation (End User Level)

**Purpose**: Help end users understand features

```markdown
# Order Management API

## Creating an Order

To create a new order, send a POST request to `/api/v1/orders`.

### Prerequisites
- You must have a valid API key
- Customer must exist in the system
- Products must be in stock

### Step-by-Step Guide

1. **Authenticate**: Include your API key in the Authorization header
2. **Prepare Order Data**: Format your order as JSON
3. **Submit Request**: POST to the orders endpoint
4. **Handle Response**: Check status code and process result

### Example

```bash
curl -X POST https://api.example.com/api/v1/orders \
  -H "Authorization: Bearer YOUR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "customerId": "cust_123",
    "items": [
      {"productId": "prod_456", "quantity": 2}
    ]
  }'
```

### Common Errors

**400 Bad Request**: Check that all required fields are present and properly formatted.

**401 Unauthorized**: Verify your API key is valid and hasn't expired.

**409 Conflict**: One or more items are out of stock. Check inventory before retrying.
```

## Practical Commenting Checklist

Use this checklist when writing comments:

### Before Writing a Comment
- [ ] Can I make the code self-explanatory instead?
- [ ] Can I extract this to a well-named function?
- [ ] Can I use better variable names?
- [ ] Is this comment necessary or just noise?

### When Writing Comments
- [ ] Comment explains WHY, not WHAT
- [ ] Comment adds information not in code
- [ ] Comment warns of non-obvious consequences
- [ ] Comment documents assumptions or constraints
- [ ] Comment is accurate and up-to-date
- [ ] Comment is well-written and clear
- [ ] Comment will survive code changes

### Documentation Comments
- [ ] All public APIs documented
- [ ] Parameters explained with types and constraints
- [ ] Return values described
- [ ] Exceptions/errors documented
- [ ] Examples provided for complex APIs
- [ ] Thread safety documented if relevant
- [ ] Performance characteristics noted if important

### Maintenance
- [ ] No commented-out code
- [ ] No obsolete comments
- [ ] No redundant comments
- [ ] TODOs have owner and context
- [ ] Comments reviewed along with code

## Summary: Commenting Principles

1. **Code First**: Make code self-documenting before adding comments
2. **Explain Why**: Comment intent and reasoning, not implementation
3. **Add Value**: Only comment what code cannot express
4. **Stay Current**: Update comments when code changes
5. **Be Accurate**: Wrong comments are worse than no comments
6. **Be Concise**: Respect readers' time
7. **Document APIs**: All public interfaces need documentation
8. **Warn of Danger**: Alert readers to non-obvious consequences
9. **Avoid Noise**: Don't comment the obvious
10. **Use Tools**: Leverage documentation generators

## Further Reading

- **Clean Code** (Chapter 4: Comments) - Robert C. Martin
- **Code Complete 2** (Chapter 32: Self-Documenting Code) - Steve McConnell
- **The Art of Readable Code** - Boswell & Foucher
- **Documentation Guidelines**:
  - Python: PEP 257 (Docstring Conventions)
  - Java: How to Write Doc Comments for Javadoc
  - TypeScript: TSDoc specification

---

**Remember**: Comments are a necessary evil. The best comment is the one you didn't need to write because the code was clear. When you must comment, make it count—explain the why, document the non-obvious, warn of consequences, and keep it accurate. Good comments amplify understanding; bad comments create confusion.
