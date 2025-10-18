# Defensive Programming: Building Resilient Systems

## Overview

Defensive programming is the practice of writing code that protects itself against misuse, invalid input, and unexpected conditions. It's about anticipating what can go wrong and building safeguards that prevent failures, detect problems early, and provide clear diagnostics when issues occur.

This comprehensive guide synthesizes defensive programming wisdom from industry-leading sources and provides practical, actionable guidance for building robust, production-grade software.

**"Defensive programming saves you from your own mistakes and from the mistakes of others."** — Code Complete 2

## Why Defensive Programming Matters

### The Cost of Poor Defensive Programming

Poor defensive practices create measurable costs:

**Production Failures**: Unchecked inputs corrupt data. Missing validation allows SQL injection. Absent bounds checking causes buffer overflows. These failures lead to security breaches, data loss, and service outages.

**Debugging Nightmares**: Problems detected far from their source are exponentially harder to debug. A null pointer crash 1000 lines after the null was created requires hours of investigation.

**Security Vulnerabilities**: Every unchecked input is a potential attack vector. Missing input validation enables injection attacks. Absent authorization checks allow privilege escalation.

**Data Corruption**: Invalid data silently accepted corrupts databases. Calculations overflow without detection. Concurrent access without locking creates race conditions.

**User Trust Erosion**: Crashes lose user data. Cryptic errors frustrate users. Security breaches destroy reputation.

### The Benefits of Good Defensive Programming

Good defensive practices provide:
- **Early Error Detection**: Problems caught immediately at their source
- **Clear Diagnostics**: Rich error information speeds debugging
- **Security Hardening**: Attack surface minimized through validation
- **Data Integrity**: Invalid states prevented, not just detected
- **Graceful Degradation**: System continues operating despite errors
- **Developer Confidence**: Safe refactoring without fear of hidden failures

## Source Materials

This guide synthesizes principles from:

- **Code Complete 2** by Steve McConnell (Chapter 8: "Defensive Programming")
  - Protecting from invalid inputs
  - Assertions
  - Error handling techniques
  - Exceptions
  - Barricades
  - Debugging aids
  - Amount of defensiveness

- **Clean Code** by Robert C. Martin
  - Null handling
  - Boundaries
  - Error handling

Note: This guide focuses on defensive techniques and validation. For comprehensive error handling coverage, see ERROR_HANDLING.md.

## Protecting Your Program from Invalid Inputs

### The Three Sources of Bad Data

**1. External Data**: User input, file contents, network data, sensor readings
**2. Internal Data**: Results from other routines, data from database
**3. Routine Parameters**: Arguments passed to your functions

### Input Validation Strategies

#### 1. Check All External Data (Code Complete 2)

**Principle**: Never trust data from outside your program.

```python
# User input validation
def create_user_account(email: str, password: str, age: str) -> User:
    """Create user account with comprehensive input validation."""

    # Validate email
    if not email:
        raise ValueError("Email is required")
    if not isinstance(email, str):
        raise TypeError(f"Email must be string, got {type(email)}")
    if '@' not in email or '.' not in email:
        raise ValueError("Invalid email format")
    if len(email) > 255:
        raise ValueError("Email too long (max 255 characters)")

    # Validate password
    if not password:
        raise ValueError("Password is required")
    if len(password) < 8:
        raise ValueError("Password must be at least 8 characters")
    if len(password) > 128:
        raise ValueError("Password too long (max 128 characters)")

    # Validate age
    if not age:
        raise ValueError("Age is required")
    try:
        age_int = int(age)
    except ValueError:
        raise ValueError(f"Age must be numeric, got '{age}'")
    if age_int < 13:
        raise ValueError("Must be at least 13 years old")
    if age_int > 150:
        raise ValueError("Invalid age (must be under 150)")

    # All validations passed - safe to proceed
    return User(email=email.lower().strip(), password=hash_password(password), age=age_int)
```

#### 2. Check Values from External Sources

**File Input:**
```java
// File parsing with defensive validation
public List<Transaction> parseTransactionFile(String filePath) {
    List<Transaction> transactions = new ArrayList<>();

    try (BufferedReader reader = new BufferedReader(new FileReader(filePath))) {
        String line;
        int lineNumber = 0;

        while ((line = reader.readLine()) != null) {
            lineNumber++;

            // Defensive: Check for empty lines
            if (line.trim().isEmpty()) {
                logger.warn("Skipping empty line {}", lineNumber);
                continue;
            }

            // Defensive: Validate CSV structure
            String[] parts = line.split(",");
            if (parts.length != 3) {
                throw new ParseException(
                    String.format("Line %d: Expected 3 fields, got %d", lineNumber, parts.length)
                );
            }

            // Defensive: Validate each field
            String id = parts[0].trim();
            if (id.isEmpty()) {
                throw new ParseException(String.format("Line %d: Transaction ID cannot be empty", lineNumber));
            }

            String amountStr = parts[1].trim();
            BigDecimal amount;
            try {
                amount = new BigDecimal(amountStr);
            } catch (NumberFormatException e) {
                throw new ParseException(
                    String.format("Line %d: Invalid amount '%s'", lineNumber, amountStr)
                );
            }

            // Defensive: Business rule validation
            if (amount.compareTo(BigDecimal.ZERO) <= 0) {
                throw new ParseException(
                    String.format("Line %d: Amount must be positive, got %s", lineNumber, amount)
                );
            }
            if (amount.compareTo(new BigDecimal("1000000")) > 0) {
                logger.warn("Line {}: Unusually large amount {}", lineNumber, amount);
            }

            String date = parts[2].trim();
            // Additional date validation...

            transactions.add(new Transaction(id, amount, date));
        }

    } catch (IOException e) {
        throw new FileProcessingException("Failed to read transaction file", e);
    }

    return transactions;
}
```

**API Responses:**
```typescript
// API response validation
interface UserResponse {
    id: string;
    email: string;
    name: string;
    age?: number;
}

async function fetchUser(userId: string): Promise<User> {
    const response = await fetch(`/api/users/${userId}`);

    // Defensive: Check HTTP status
    if (!response.ok) {
        throw new APIError(
            `HTTP ${response.status}: ${response.statusText}`,
            response.status
        );
    }

    let data: any;
    try {
        data = await response.json();
    } catch (error) {
        throw new APIError('Invalid JSON response', 0, error);
    }

    // Defensive: Validate response structure
    if (!data || typeof data !== 'object') {
        throw new APIError('Response must be an object');
    }

    // Defensive: Validate required fields
    if (!data.id || typeof data.id !== 'string') {
        throw new APIError('Missing or invalid user ID');
    }
    if (!data.email || typeof data.email !== 'string') {
        throw new APIError('Missing or invalid email');
    }
    if (!data.name || typeof data.name !== 'string') {
        throw new APIError('Missing or invalid name');
    }

    // Defensive: Validate optional fields
    if (data.age !== undefined && typeof data.age !== 'number') {
        throw new APIError('Age must be a number');
    }
    if (data.age !== undefined && (data.age < 0 || data.age > 150)) {
        throw new APIError('Age out of valid range');
    }

    // Response validated - safe to use
    return {
        id: data.id,
        email: data.email,
        name: data.name,
        age: data.age,
    };
}
```

#### 3. Check Parameters to Routines

**Precondition Validation:**
```python
def transfer_funds(from_account: Account, to_account: Account, amount: Decimal) -> None:
    """
    Transfer funds between accounts with defensive parameter validation.

    Preconditions (all validated):
    - from_account and to_account must not be None
    - from_account and to_account must be different accounts
    - amount must be positive
    - from_account must have sufficient balance
    """
    # Defensive: Validate not None
    if from_account is None:
        raise ValueError("Source account cannot be None")
    if to_account is None:
        raise ValueError("Destination account cannot be None")

    # Defensive: Validate not same account
    if from_account.id == to_account.id:
        raise ValueError("Cannot transfer to same account")

    # Defensive: Validate amount
    if amount is None:
        raise ValueError("Amount cannot be None")
    if amount <= 0:
        raise ValueError(f"Amount must be positive, got {amount}")

    # Defensive: Validate sufficient funds
    if from_account.balance < amount:
        raise InsufficientFundsError(
            f"Insufficient funds: balance={from_account.balance}, required={amount}"
        )

    # All preconditions satisfied - safe to proceed
    from_account.withdraw(amount)
    to_account.deposit(amount)

    logger.info(f"Transferred {amount} from {from_account.id} to {to_account.id}")
```

**Type Validation:**
```java
// Defensive type checking
public <T> List<T> filterList(List<T> items, Predicate<T> filter) {
    // Defensive: Validate parameters not null
    if (items == null) {
        throw new IllegalArgumentException("Items list cannot be null");
    }
    if (filter == null) {
        throw new IllegalArgumentException("Filter predicate cannot be null");
    }

    // Defensive: Check for null items in list
    List<T> result = new ArrayList<>();
    for (int i = 0; i < items.size(); i++) {
        T item = items.get(i);
        if (item == null) {
            logger.warn("Skipping null item at index {}", i);
            continue;
        }

        if (filter.test(item)) {
            result.add(item);
        }
    }

    return result;
}
```

### Decide How to Handle Bad Inputs

**Code Complete 2 provides several strategies:**

#### 1. Reject Invalid Data (Fail Fast)

```python
# Critical systems: Reject invalid input immediately
def calculate_medication_dosage(patient_weight_kg: float, drug_concentration: float) -> float:
    """Calculate medication dosage - fail fast on invalid input."""

    # Reject any invalid input immediately
    if patient_weight_kg <= 0 or patient_weight_kg > 500:
        raise ValueError(
            f"Invalid patient weight: {patient_weight_kg}kg (must be 0-500kg)"
        )

    if drug_concentration <= 0 or drug_concentration > 1.0:
        raise ValueError(
            f"Invalid drug concentration: {drug_concentration} (must be 0-1.0)"
        )

    dosage = patient_weight_kg * drug_concentration * 0.1

    # Defensive: Validate output before returning
    if dosage > 100:  # Maximum safe dosage
        raise ValueError(
            f"Calculated dosage {dosage}mg exceeds safe maximum 100mg"
        )

    return dosage
```

#### 2. Sanitize Invalid Data

```typescript
// Web applications: Clean and sanitize input
function sanitizeUsername(input: string): string {
    // Defensive: Handle null/undefined
    if (!input) {
        return '';
    }

    // Defensive: Convert to string
    const str = String(input);

    // Sanitize: Remove dangerous characters
    let sanitized = str
        .trim()
        .toLowerCase()
        .replace(/[^a-z0-9_-]/g, '')  // Only allow alphanumeric, underscore, hyphen
        .substring(0, 50);  // Limit length

    // Defensive: Ensure minimum length
    if (sanitized.length < 3) {
        throw new ValidationError('Username must be at least 3 characters');
    }

    return sanitized;
}
```

#### 3. Return Neutral Value

```java
// Non-critical: Return safe default
public String getUserPreference(String userId, String preferenceKey) {
    // Defensive: Validate inputs
    if (userId == null || userId.trim().isEmpty()) {
        logger.warn("Invalid userId, returning default preference");
        return DEFAULT_PREFERENCE;
    }

    if (preferenceKey == null || preferenceKey.trim().isEmpty()) {
        logger.warn("Invalid preferenceKey, returning default");
        return DEFAULT_PREFERENCE;
    }

    try {
        return database.getUserPreference(userId, preferenceKey);
    } catch (DatabaseException e) {
        // Defensive: Return neutral value on error
        logger.error("Failed to fetch preference for user {}", userId, e);
        return DEFAULT_PREFERENCE;
    }
}
```

## Assertions: Programming with Confidence

### What Are Assertions?

**Definition**: Statements that should always be true at a given point in code. They catch programming errors during development.

**Key Distinction**:
- **Assertions**: For programmer errors (bugs)
- **Exceptions**: For runtime errors (external conditions)

### When to Use Assertions (Code Complete 2)

#### 1. Preconditions

```python
def calculate_square_root(number: float) -> float:
    """Calculate square root with precondition assertion."""
    # Assertion: Caller must provide non-negative number
    assert number >= 0, f"Cannot calculate square root of negative number: {number}"

    return math.sqrt(number)
```

#### 2. Postconditions

```java
public int[] sortArray(int[] array) {
    // ... sorting logic ...

    // Assertion: Array must be sorted after this method
    assert isSorted(array) : "Array not sorted after sort operation";

    return array;
}

private boolean isSorted(int[] array) {
    for (int i = 1; i < array.length; i++) {
        if (array[i] < array[i-1]) {
            return false;
        }
    }
    return true;
}
```

#### 3. Invariants

```python
class BankAccount:
    """Bank account with invariant: balance never negative."""

    def __init__(self, initial_balance: Decimal):
        assert initial_balance >= 0, "Initial balance cannot be negative"
        self._balance = initial_balance
        self._check_invariant()

    def _check_invariant(self):
        """Verify class invariant: balance >= 0."""
        assert self._balance >= 0, f"Invariant violation: negative balance {self._balance}"

    def deposit(self, amount: Decimal) -> None:
        assert amount > 0, "Deposit amount must be positive"
        self._check_invariant()  # Check before operation

        self._balance += amount

        self._check_invariant()  # Check after operation

    def withdraw(self, amount: Decimal) -> None:
        assert amount > 0, "Withdrawal amount must be positive"
        self._check_invariant()  # Check before

        if self._balance < amount:
            raise InsufficientFundsError(f"Balance {self._balance} < amount {amount}")

        self._balance -= amount

        self._check_invariant()  # Check after
```

#### 4. Impossible Conditions

```typescript
// Assertions for impossible code paths
enum OrderStatus {
    PENDING = 'PENDING',
    PROCESSING = 'PROCESSING',
    COMPLETED = 'COMPLETED',
    CANCELLED = 'CANCELLED',
}

function handleOrderStatus(status: OrderStatus): void {
    switch (status) {
        case OrderStatus.PENDING:
            handlePending();
            break;
        case OrderStatus.PROCESSING:
            handleProcessing();
            break;
        case OrderStatus.COMPLETED:
            handleCompleted();
            break;
        case OrderStatus.CANCELLED:
            handleCancelled();
            break;
        default:
            // This should never happen
            console.assert(
                false,
                `Unexpected order status: ${status}`
            );
            throw new Error(`Unhandled order status: ${status}`);
    }
}
```

### Guidelines for Effective Assertions

**DO:**
- Use assertions liberally during development
- Assert preconditions and postconditions
- Assert invariants before and after operations
- Use assertions to document assumptions

**DON'T:**
- Don't use assertions for user input validation
- Don't put code with side effects in assertions
- Don't use assertions instead of error handling
- Don't rely on assertions in production (they may be disabled)

```python
# WRONG: Side effect in assertion
count = 0
assert (count := count + 1) > 0  # BAD: Modifies count

# RIGHT: No side effect
assert count > 0  # GOOD: Just checks

# WRONG: User input validation
def login(username: str, password: str):
    assert username, "Username required"  # WRONG: Use exception

# RIGHT: User input validation
def login(username: str, password: str):
    if not username:
        raise ValueError("Username required")  # CORRECT
```

## Barricades: Defending the Boundaries

### The Barricade Concept

**Definition**: A validation boundary where all external data is checked. Inside the barricade, data is trusted.

**Pattern**: Validate once at the boundary, trust internally.

```python
# Barricade pattern example
class OrderAPI:
    """External API boundary - BARRICADE."""

    def create_order(self, request_data: dict) -> Order:
        """
        Public API endpoint - validates all inputs at barricade.

        This is the BARRICADE. All external data is validated here.
        Internal methods can trust their inputs.
        """
        # BARRICADE: Validate external data
        validated = self._validate_and_sanitize_order_request(request_data)

        # Pass trusted data to internal service
        return OrderService.create_order_internal(validated)

    def _validate_and_sanitize_order_request(self, data: dict) -> ValidatedOrderRequest:
        """Comprehensive validation at the barricade."""
        if not isinstance(data, dict):
            raise ValidationError("Request must be JSON object")

        # Validate customer ID
        customer_id = data.get('customer_id')
        if not customer_id or not isinstance(customer_id, str):
            raise ValidationError("Valid customer_id required")
        if not re.match(r'^cust_[a-zA-Z0-9]+$', customer_id):
            raise ValidationError("Invalid customer_id format")

        # Validate items
        items = data.get('items')
        if not items or not isinstance(items, list):
            raise ValidationError("Items array required")
        if len(items) == 0:
            raise ValidationError("At least one item required")
        if len(items) > 100:
            raise ValidationError("Maximum 100 items per order")

        validated_items = []
        for i, item in enumerate(items):
            if not isinstance(item, dict):
                raise ValidationError(f"Item {i} must be object")

            product_id = item.get('product_id')
            if not product_id or not isinstance(product_id, str):
                raise ValidationError(f"Item {i}: product_id required")

            quantity = item.get('quantity')
            if not isinstance(quantity, int) or quantity < 1 or quantity > 1000:
                raise ValidationError(f"Item {i}: quantity must be 1-1000")

            validated_items.append({
                'product_id': product_id,
                'quantity': quantity
            })

        # Return validated, trusted data
        return ValidatedOrderRequest(
            customer_id=customer_id,
            items=validated_items
        )


class OrderService:
    """Internal service - INSIDE BARRICADE."""

    @staticmethod
    def create_order_internal(validated_request: ValidatedOrderRequest) -> Order:
        """
        Internal method - data already validated at barricade.

        NO defensive validation needed here. Data is trusted because
        it passed through the barricade.
        """
        # Trust the data - no validation needed
        order = Order(
            customer_id=validated_request.customer_id,
            items=validated_request.items,
            created_at=datetime.utcnow()
        )

        # Business logic without defensive checks
        database.save(order)
        return order
```

### Benefits of Barricades

1. **Single Point of Validation**: Validate once, trust thereafter
2. **Performance**: No redundant validation inside barricade
3. **Clarity**: Clear boundary between trusted and untrusted data
4. **Maintainability**: Validation logic centralized
5. **Security**: All attack vectors handled at boundary

## Handling Null/None Values

### The Billion-Dollar Mistake

**Tony Hoare (inventor of null)**: "I call it my billion-dollar mistake... the invention of the null reference."

### Strategies to Avoid Null Problems

#### 1. Don't Return Null (Clean Code)

```typescript
// BAD: Returning null
function getUser(userId: string): User | null {
    const user = database.findUser(userId);
    return user ? user : null;  // Caller must check for null
}

// Caller code cluttered with null checks
const user = getUser("123");
if (user !== null) {  // Easy to forget this check
    console.log(user.name);
}

// GOOD: Throw exception
function getUser(userId: string): User {
    const user = database.findUser(userId);
    if (!user) {
        throw new UserNotFoundError(`User not found: ${userId}`);
    }
    return user;  // Never null
}

// Caller: No null check needed
const user = getUser("123");
console.log(user.name);  // Safe - always a User object
```

#### 2. Use Optional/Maybe Types

```java
// Java: Optional type
public Optional<User> findUserByEmail(String email) {
    User user = database.queryByEmail(email);
    return Optional.ofNullable(user);
}

// Explicit handling of presence/absence
Optional<User> userOpt = findUserByEmail("john@example.com");

// Option 1: Provide default
User user = userOpt.orElse(new GuestUser());

// Option 2: Throw exception
User user = userOpt.orElseThrow(() ->
    new UserNotFoundException("No user with email")
);

// Option 3: Execute only if present
userOpt.ifPresent(user -> sendWelcomeEmail(user));

// Option 4: Transform if present
String userName = userOpt
    .map(User::getName)
    .orElse("Guest");
```

#### 3. Null Object Pattern

```python
# Null Object Pattern
class User:
    def __init__(self, name: str, email: str):
        self.name = name
        self.email = email

    def send_notification(self, message: str) -> None:
        email_service.send(self.email, message)

class NullUser(User):
    """Null object - safe default behavior."""
    def __init__(self):
        super().__init__("Guest", "noreply@example.com")

    def send_notification(self, message: str) -> None:
        # Safe no-op for null object
        logger.info(f"Attempted to notify null user: {message}")

# Return null object instead of None
def get_user(user_id: str) -> User:
    user = database.find_user(user_id)
    return user if user else NullUser()

# No null checks needed
user = get_user("123")
user.send_notification("Hello")  # Safe even if user not found
print(user.name)  # Always works: real name or "Guest"
```

#### 4. Don't Pass Null

```java
// Defensive: Reject null parameters immediately
public void processOrder(Order order) {
    // Fail fast on null
    Objects.requireNonNull(order, "Order cannot be null");

    // Safe to use order - guaranteed non-null
    calculateTotal(order);
    chargePayment(order);
}

// Better: Use type system to prevent null
public void processOrder(@NonNull Order order) {
    // Annotation enforces non-null at compile time
    calculateTotal(order);
    chargePayment(order);
}
```

## Bounds Checking and Resource Management

### Array/Collection Bounds

```python
def get_element_at(items: list, index: int):
    """Safe element access with bounds checking."""
    # Defensive: Check for None
    if items is None:
        raise ValueError("Items list cannot be None")

    # Defensive: Check bounds
    if index < 0 or index >= len(items):
        raise IndexError(
            f"Index {index} out of bounds for list of length {len(items)}"
        )

    return items[index]


def safe_slice(items: list, start: int, end: int) -> list:
    """Safe list slicing with bounds validation."""
    if items is None:
        raise ValueError("Items list cannot be None")

    # Defensive: Validate start and end
    if start < 0:
        raise ValueError(f"Start index {start} cannot be negative")
    if end > len(items):
        raise ValueError(
            f"End index {end} exceeds list length {len(items)}"
        )
    if start > end:
        raise ValueError(
            f"Start index {start} cannot exceed end index {end}"
        )

    return items[start:end]
```

### Resource Cleanup

```typescript
// Defensive resource management
class DatabaseConnection {
    private connection: Connection | null = null;

    async connect(): Promise<void> {
        // Defensive: Check not already connected
        if (this.connection !== null) {
            throw new Error('Already connected');
        }

        this.connection = await database.connect();
    }

    async query(sql: string): Promise<Result> {
        // Defensive: Check connection exists
        if (this.connection === null) {
            throw new Error('Not connected to database');
        }

        return this.connection.execute(sql);
    }

    async close(): Promise<void> {
        // Defensive: Safe to call multiple times
        if (this.connection !== null) {
            try {
                await this.connection.close();
            } finally {
                this.connection = null;
            }
        }
    }
}

// Usage with try-finally for guaranteed cleanup
async function performDatabaseWork(): Promise<void> {
    const conn = new DatabaseConnection();

    try {
        await conn.connect();
        const results = await conn.query('SELECT * FROM users');
        processResults(results);
    } finally {
        // Defensive: Always cleanup, even if exception thrown
        await conn.close();
    }
}
```

## Numeric Overflow and Precision

### Integer Overflow Protection

```java
// Defensive: Check for overflow
public int multiply(int a, int b) {
    // Defensive: Check for overflow before multiplying
    if (a > 0 && b > 0 && a > Integer.MAX_VALUE / b) {
        throw new ArithmeticException(
            String.format("Multiplication overflow: %d * %d", a, b)
        );
    }
    if (a < 0 && b < 0 && a < Integer.MAX_VALUE / b) {
        throw new ArithmeticException(
            String.format("Multiplication overflow: %d * %d", a, b)
        );
    }

    return a * b;
}

public int add(int a, int b) {
    // Defensive: Check for overflow
    if (b > 0 && a > Integer.MAX_VALUE - b) {
        throw new ArithmeticException(
            String.format("Addition overflow: %d + %d", a, b)
        );
    }
    if (b < 0 && a < Integer.MIN_VALUE - b) {
        throw new ArithmeticException(
            String.format("Addition underflow: %d + %d", a, b)
        );
    }

    return a + b;
}
```

### Floating Point Precision

```python
from decimal import Decimal

def calculate_price(base_price: str, tax_rate: str) -> Decimal:
    """
    Calculate price with tax using Decimal for precision.

    Defensive: Never use float for money calculations.
    Float has rounding errors that corrupt financial data.
    """
    # Defensive: Use Decimal for exact decimal arithmetic
    try:
        price = Decimal(base_price)
        rate = Decimal(tax_rate)
    except Exception as e:
        raise ValueError(f"Invalid decimal values: {e}")

    # Defensive: Validate ranges
    if price < 0:
        raise ValueError(f"Price cannot be negative: {price}")
    if rate < 0 or rate > 1:
        raise ValueError(f"Tax rate must be 0-1: {rate}")

    total = price * (1 + rate)

    # Defensive: Round to 2 decimal places for currency
    return total.quantize(Decimal('0.01'))
```

## Concurrency and Thread Safety

### Defensive Synchronization

```java
// Defensive thread safety
public class Counter {
    private int count = 0;
    private final Object lock = new Object();

    public void increment() {
        // Defensive: Synchronize all access to shared state
        synchronized (lock) {
            count++;
            // Defensive: Verify invariant
            assert count > 0 : "Count should never overflow to negative";
        }
    }

    public int getCount() {
        // Defensive: Even reads must be synchronized
        synchronized (lock) {
            return count;
        }
    }
}

// Defensive: Document thread safety
/**
 * Thread-safe user cache.
 *
 * All public methods are synchronized and can be called concurrently.
 * Internal methods are NOT thread-safe and must only be called while
 * holding the lock.
 */
public class UserCache {
    private final Map<String, User> cache = new HashMap<>();
    private final ReadWriteLock lock = new ReentrantReadWriteLock();

    public User get(String userId) {
        lock.readLock().lock();
        try {
            return cache.get(userId);
        } finally {
            // Defensive: Always unlock in finally
            lock.readLock().unlock();
        }
    }

    public void put(String userId, User user) {
        lock.writeLock().lock();
        try {
            // Defensive: Validate before modifying
            if (userId == null || user == null) {
                throw new IllegalArgumentException("userId and user cannot be null");
            }
            cache.put(userId, user);
        } finally {
            // Defensive: Always unlock in finally
            lock.writeLock().unlock();
        }
    }
}
```

## Debugging Aids (Code Complete 2)

### Version Control for Variables

```python
class TrackedValue:
    """Defensive: Track value changes for debugging."""

    def __init__(self, initial_value, name="value"):
        self._value = initial_value
        self._name = name
        self._history = [(datetime.now(), initial_value, traceback.format_stack())]

    def get(self):
        return self._value

    def set(self, new_value, reason=""):
        # Defensive: Track every change
        self._history.append((
            datetime.now(),
            new_value,
            traceback.format_stack(),
            reason
        ))
        self._value = new_value

    def get_history(self):
        """Get full history of value changes."""
        return self._history

    def print_history(self):
        """Print change history for debugging."""
        print(f"=== History for {self._name} ===")
        for timestamp, value, stack, *reason in self._history:
            print(f"{timestamp}: {value}")
            if reason:
                print(f"  Reason: {reason[0]}")
            print(f"  Stack: {stack[-3]}")  # Print relevant stack frame
```

### Offensive Programming During Development

```typescript
// Development mode: Fail loudly
function processPayment(payment: Payment): Transaction {
    // DEVELOPMENT: Aggressive validation
    if (process.env.NODE_ENV === 'development') {
        // Fail loudly on any suspicious condition
        if (payment.amount <= 0) {
            throw new Error(`DEVELOPMENT: Invalid amount ${payment.amount}`);
        }
        if (payment.amount > 1000000) {
            throw new Error(`DEVELOPMENT: Suspicious large amount ${payment.amount}`);
        }
        if (!payment.customerId) {
            throw new Error('DEVELOPMENT: Missing customer ID');
        }
    }

    // PRODUCTION: Essential validation only
    if (payment.amount <= 0) {
        throw new ValidationError('Payment amount must be positive');
    }

    return executePayment(payment);
}
```

## How Much Defensive Programming Is Enough?

### Critical vs Non-Critical Code

**Critical Code** (Financial, Medical, Safety):
- Extensive validation
- Redundant checks
- Comprehensive logging
- Graceful degradation

```java
// Critical: Financial transaction
public void transferFunds(Account from, Account to, BigDecimal amount) {
    // CRITICAL: Extensive defensive checks

    // Pre-transaction validation
    validateAccount(from, "source");
    validateAccount(to, "destination");
    validateAmount(amount);
    validateSufficientFunds(from, amount);

    // Capture pre-transaction state
    BigDecimal fromBalanceBefore = from.getBalance();
    BigDecimal toBalanceBefore = to.getBalance();
    BigDecimal totalBefore = fromBalanceBefore.add(toBalanceBefore);

    // Execute transaction
    from.withdraw(amount);
    to.deposit(amount);

    // Defensive: Verify invariants
    BigDecimal totalAfter = from.getBalance().add(to.getBalance());
    if (!totalBefore.equals(totalAfter)) {
        // Critical invariant violated - rollback
        rollback(from, to, fromBalanceBefore, toBalanceBefore);
        throw new InvariantViolationException(
            "Transfer violated conservation of money"
        );
    }

    // Defensive: Redundant verification
    if (!from.getBalance().equals(fromBalanceBefore.subtract(amount))) {
        rollback(from, to, fromBalanceBefore, toBalanceBefore);
        throw new InvariantViolationException("Source balance incorrect");
    }

    // Defensive: Comprehensive logging
    auditLog.info(
        "TRANSFER: {} -> {}, amount={}, from_before={}, from_after={}, to_before={}, to_after={}",
        from.getId(), to.getId(), amount,
        fromBalanceBefore, from.getBalance(),
        toBalanceBefore, to.getBalance()
    );
}
```

**Non-Critical Code** (UI, Analytics, Logging):
- Basic validation
- Fail gracefully
- Don't interrupt user experience

```python
# Non-critical: Analytics tracking
def track_page_view(page_name: str, user_id: str = None) -> None:
    """Track page view - non-critical, fail silently."""
    try:
        # Basic validation only
        if not page_name or not isinstance(page_name, str):
            logger.warning(f"Invalid page name: {page_name}")
            return  # Fail silently

        # Send to analytics (best effort)
        analytics_service.track('page_view', {
            'page': page_name,
            'user_id': user_id,
            'timestamp': datetime.utcnow()
        })

    except Exception as e:
        # Defensive: Analytics failure shouldn't affect user experience
        logger.error(f"Analytics tracking failed: {e}")
        # Swallow exception - non-critical
```

## Practical Defensive Programming Checklist

Use this checklist to ensure defensive programming:

### Input Validation
- [ ] All external data validated at entry point (barricade)
- [ ] User input sanitized and validated
- [ ] File contents validated
- [ ] API responses validated (structure and types)
- [ ] Function parameters validated (preconditions)
- [ ] Invalid input rejected or sanitized appropriately

### Null/None Handling
- [ ] Functions don't return null (use exceptions or Optional)
- [ ] Functions don't accept null parameters
- [ ] Collections never contain null elements
- [ ] Null checks present where null is possible
- [ ] Null object pattern used where appropriate

### Assertions
- [ ] Preconditions asserted
- [ ] Postconditions asserted
- [ ] Invariants asserted before and after operations
- [ ] Impossible conditions asserted
- [ ] No side effects in assertions
- [ ] Assertions used for programmer errors only

### Bounds and Limits
- [ ] Array/collection indices validated
- [ ] String lengths checked
- [ ] Numeric values checked for overflow/underflow
- [ ] Resource limits enforced (memory, connections, etc.)
- [ ] Loop termination guaranteed

### Resource Management
- [ ] Resources cleaned up in finally blocks
- [ ] Connections closed even on error
- [ ] Locks released even on exception
- [ ] Memory freed appropriately
- [ ] File handles closed

### Thread Safety
- [ ] Shared state access synchronized
- [ ] Lock ordering documented to prevent deadlock
- [ ] Thread safety documented in comments
- [ ] Atomic operations used where appropriate
- [ ] Immutable data preferred

### Error Handling
- [ ] Errors detected early (fail fast)
- [ ] Rich error context provided
- [ ] Errors logged with sufficient detail
- [ ] Graceful degradation for non-critical features
- [ ] Critical operations have rollback capability

## Summary: Defensive Programming Principles

1. **Validate Input**: Check all external data at boundaries (barricades)
2. **Assert Invariants**: Use assertions to catch programming errors
3. **Fail Fast**: Detect errors early, near their source
4. **Avoid Null**: Don't return null, don't pass null
5. **Check Bounds**: Validate array indices and numeric ranges
6. **Manage Resources**: Always cleanup in finally blocks
7. **Thread Safety**: Synchronize shared state access
8. **Provide Context**: Rich error messages aid debugging
9. **Defensive Depth**: Match defensive level to code criticality
10. **Trust but Verify**: Trust internal code, verify external data

## Further Reading

- **Code Complete 2** (Chapter 8: Defensive Programming) - Steve McConnell
- **Clean Code** (Chapters on Error Handling and Boundaries) - Robert C. Martin
- **The Pragmatic Programmer** (Pragmatic Paranoia) - Hunt & Thomas
- **Secure Coding Guidelines** - Language-specific security guides
- **ERROR_HANDLING.md** - Comprehensive error handling guide in this series

---

**Remember**: Defensive programming is about building robust systems that survive the real world. Validate inputs rigorously, assert assumptions explicitly, handle errors gracefully, and provide rich diagnostics. The time you invest in defensive programming pays dividends every time it prevents a bug, catches an error early, or provides the diagnostic information needed to fix a problem quickly.
