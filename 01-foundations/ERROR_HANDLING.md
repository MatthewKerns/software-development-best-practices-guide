# Error Handling: Building Robust and Correct Software

## Overview

Error handling is not an afterthought—it is a fundamental aspect of software design that determines whether your system is robust, reliable, and maintainable. Poor error handling leads to silent failures, data corruption, security vulnerabilities, and production outages. Good error handling creates systems that fail gracefully, provide clear diagnostics, and recover intelligently.

This guide synthesizes proven principles from industry-leading sources to provide comprehensive, actionable guidance for designing and implementing production-grade error handling.

**"Clean code is code that handles errors gracefully."** — Robert C. Martin, Clean Code

## Why Error Handling Matters

### The Cost of Poor Error Handling

Poor error handling creates measurable costs:

**Production Failures**: Silent errors corrupt data. Swallowed exceptions cause cascading failures. Generic error messages hide root causes, extending outages.

**Security Vulnerabilities**: Exposing stack traces reveals system internals to attackers. Improper error handling creates denial-of-service vectors. Failed validations allow injection attacks.

**Debugging Nightmares**: Generic exceptions provide no context. Lost error information makes reproduction impossible. Missing stack traces force blind debugging.

**User Experience Degradation**: Cryptic error messages frustrate users. Application crashes lose user data. Unhandled errors cause unpredictable behavior.

**Maintenance Burden**: Error handling mixed with business logic creates spaghetti code. Inconsistent error strategies confuse maintainers. Technical debt from band-aid fixes compounds over time.

### The Benefits of Good Error Handling

Good error handling provides:
- **Robustness**: System continues operating despite errors
- **Diagnosability**: Clear information about what went wrong and why
- **Security**: Error information doesn't leak sensitive details
- **Maintainability**: Error handling separated from business logic
- **User Trust**: Graceful failures with helpful guidance
- **Developer Productivity**: Fast debugging with rich error context

## Source Materials

This guide synthesizes principles from:

- **Code Complete 2** by Steve McConnell (Chapter 8: "Defensive Programming")
  - Robustness vs correctness
  - Error handling techniques
  - Assertions and barricades
  - Amount of defensive programming

- **Clean Code** by Robert C. Martin (Chapter 7: "Error Handling")
  - Use exceptions rather than return codes
  - Write try-catch-finally first
  - Provide context with exceptions
  - Don't return null
  - Don't pass null

## Robustness vs Correctness (Code Complete 2)

### The Fundamental Tradeoff

**Correctness**: Never returning an inaccurate result. If the system can't compute a correct answer, it doesn't compute an answer at all.

**Robustness**: Always doing something reasonable to keep operating, even in the face of invalid inputs or unexpected conditions.

### When to Favor Correctness

**Life-Critical Systems**: Medical devices, aviation software, financial transaction systems.

```python
# Medical device - correctness is paramount
def calculate_medication_dosage(patient_weight_kg, medication_concentration):
    """Calculate medication dosage - must be exactly correct or fail."""
    if patient_weight_kg <= 0:
        raise ValueError("Invalid patient weight: must be positive")
    if patient_weight_kg > 500:
        # Suspiciously high - fail rather than risk overdose
        raise ValueError(f"Patient weight {patient_weight_kg}kg exceeds safe maximum")
    if medication_concentration <= 0:
        raise ValueError("Invalid medication concentration")

    dosage = patient_weight_kg * medication_concentration * 0.1

    if dosage > MAXIMUM_SAFE_DOSAGE:
        raise ValueError(f"Calculated dosage {dosage}mg exceeds safe maximum")

    return dosage
    # Better to fail than give wrong dosage
```

**Financial Systems**: Banking, trading, accounting.

```java
// Financial transaction - must be exact
public BigDecimal calculateInterest(BigDecimal principal, BigDecimal rate, int days) {
    if (principal.compareTo(BigDecimal.ZERO) < 0) {
        throw new IllegalArgumentException("Principal cannot be negative");
    }
    if (rate.compareTo(BigDecimal.ZERO) < 0 || rate.compareTo(new BigDecimal("1.0")) > 0) {
        throw new IllegalArgumentException("Rate must be between 0 and 1");
    }
    if (days < 0) {
        throw new IllegalArgumentException("Days cannot be negative");
    }

    // Use exact decimal arithmetic - no rounding errors
    BigDecimal dailyRate = rate.divide(new BigDecimal("365"), 10, RoundingMode.HALF_UP);
    BigDecimal interest = principal.multiply(dailyRate).multiply(new BigDecimal(days));

    return interest.setScale(2, RoundingMode.HALF_UP);
    // Exact calculation or exception - no approximations
}
```

### When to Favor Robustness

**Consumer Applications**: Web apps, mobile apps, games.

```typescript
// Web application - robustness preferred
function displayUserProfile(userId: string): JSX.Element {
    try {
        const user = fetchUser(userId);
        return <UserProfile user={user} />;
    } catch (error) {
        // Keep app working even if profile fetch fails
        logger.error("Failed to load user profile", { userId, error });
        return <ErrorMessage>Unable to load profile. Please try again.</ErrorMessage>;
    }
}

// Search feature - show partial results rather than fail completely
function searchProducts(query: string): Product[] {
    try {
        return searchEngine.search(query);
    } catch (error) {
        logger.error("Search failed", { query, error });
        // Return empty results rather than crash
        return [];
    }
}
```

**Data Processing Pipelines**: Continue processing remaining items when some fail.

```python
# ETL pipeline - robustness over correctness
def process_batch(records):
    """Process batch of records, continuing despite individual failures."""
    successful = []
    failed = []

    for record in records:
        try:
            processed = transform_record(record)
            validate_record(processed)
            successful.append(processed)
        except Exception as e:
            # Log failure but continue processing
            logger.error(f"Failed to process record {record.id}", exc_info=e)
            failed.append({"record": record, "error": str(e)})

    # Report summary
    logger.info(f"Processed {len(successful)} records, {len(failed)} failures")

    return {
        "successful": successful,
        "failed": failed
    }
```

### Hybrid Approach

Many systems need both:

```java
// Payment processor - correctness for money, robustness for notifications
public class PaymentProcessor {
    public PaymentResult processPayment(Payment payment) {
        // Correctness: Payment must be exact or fail
        try {
            validatePayment(payment);
            Transaction transaction = chargeCustomer(payment);
            recordTransaction(transaction);

            // Robustness: Notification failure shouldn't fail payment
            try {
                sendReceiptEmail(payment.getCustomerEmail(), transaction);
            } catch (EmailException e) {
                // Payment succeeded even though email failed
                logger.error("Failed to send receipt email", e);
            }

            return PaymentResult.success(transaction);

        } catch (PaymentValidationException | ChargeFailedException e) {
            // Payment failures are not recoverable
            throw e;
        }
    }
}
```

## Error Handling Techniques (Code Complete 2)

### 1. Return Neutral Value

**Use When**: Continuing with safe default is reasonable.

```python
# Return neutral value
def get_user_preference(user_id, preference_key):
    """Get user preference, returning default if not found."""
    try:
        preferences = database.get_user_preferences(user_id)
        return preferences.get(preference_key, DEFAULT_PREFERENCE)
    except DatabaseError:
        # Return neutral default if database unavailable
        logger.warning(f"Database error retrieving preference for {user_id}")
        return DEFAULT_PREFERENCE

# Temperature sensor reading
def read_temperature_sensor():
    """Read temperature, returning last known value if sensor fails."""
    try:
        return sensor.read_current_temperature()
    except SensorError:
        # Return neutral value: last known temperature
        return last_known_temperature
```

**Caution**: Don't hide important errors. Log them.

```typescript
// DON'T: Silently return neutral value
function getAccountBalance(accountId: string): number {
    try {
        return database.getBalance(accountId);
    } catch (error) {
        return 0;  // DANGEROUS: Hides error completely
    }
}

// DO: Log error before returning neutral value
function getAccountBalance(accountId: string): number {
    try {
        return database.getBalance(accountId);
    } catch (error) {
        logger.error("Failed to fetch account balance", { accountId, error });
        metrics.incrementCounter("balance_fetch_failures");
        return 0;  // Neutral value with full visibility
    }
}
```

### 2. Return Next Valid Data

**Use When**: Approximation is acceptable and useful.

```java
// Return next valid data
public class DataStreamReader {
    public int readNextValue() {
        try {
            return inputStream.readInt();
        } catch (CorruptedDataException e) {
            // Skip corrupted value, return next valid one
            logger.warn("Skipping corrupted data point", e);
            return readNextValue();  // Recursively try next value
        }
    }
}

// Configuration with fallbacks
public String getConfiguration(String key) {
    // Try environment-specific config
    String value = environmentConfig.get(key);
    if (value != null) return value;

    // Fall back to default config
    value = defaultConfig.get(key);
    if (value != null) return value;

    // Fall back to hardcoded default
    return HARDCODED_DEFAULTS.get(key);
}
```

### 3. Return Previous Valid Answer

**Use When**: Continuing with stale data is better than no data.

```python
# Cache previous result
class StockPriceService:
    def __init__(self):
        self._last_known_prices = {}

    def get_stock_price(self, symbol):
        """Get current stock price, returning cached price if fetch fails."""
        try:
            current_price = api.fetch_current_price(symbol)
            self._last_known_prices[symbol] = current_price
            return current_price
        except APIException:
            # Return previous answer if available
            if symbol in self._last_known_prices:
                logger.warning(f"Using cached price for {symbol}")
                return self._last_known_prices[symbol]
            else:
                raise ValueError(f"No price available for {symbol}")

# Sensor reading with staleness tracking
class SensorReader:
    def __init__(self):
        self.last_reading = None
        self.last_reading_time = None

    def get_reading(self):
        """Get sensor reading with staleness warning."""
        try:
            self.last_reading = sensor.read()
            self.last_reading_time = time.time()
            return self.last_reading
        except SensorError:
            if self.last_reading is not None:
                age = time.time() - self.last_reading_time
                logger.warning(f"Using stale reading (age: {age}s)")
                return self.last_reading
            else:
                raise ValueError("No sensor data available")
```

### 4. Log Warning and Continue

**Use When**: Error is noteworthy but not critical.

```typescript
// Log warning for non-critical errors
async function syncUserData(userId: string): Promise<void> {
    try {
        const userData = await fetchUserData(userId);

        // Try to sync to analytics (non-critical)
        try {
            await analyticsService.updateUserProfile(userData);
        } catch (error) {
            // Log but don't fail the operation
            logger.warn("Failed to sync user data to analytics", { userId, error });
        }

        // Try to update cache (non-critical)
        try {
            await cache.set(`user:${userId}`, userData);
        } catch (error) {
            logger.warn("Failed to update user cache", { userId, error });
        }

        // Critical: Save to primary database
        await database.saveUser(userData);

    } catch (error) {
        // Critical errors are thrown
        throw new Error(`Failed to sync user data: ${error.message}`);
    }
}
```

### 5. Return Error Code

**Use When**: Caller must handle error explicitly (legacy systems, C-style APIs).

```python
# Error codes (less preferred in modern code)
class StatusCode:
    SUCCESS = 0
    INVALID_INPUT = 1
    NOT_FOUND = 2
    PERMISSION_DENIED = 3
    INTERNAL_ERROR = 4

def legacy_api_call(request_data):
    """Legacy API using error codes."""
    if not validate_input(request_data):
        return StatusCode.INVALID_INPUT, None

    user = find_user(request_data.user_id)
    if not user:
        return StatusCode.NOT_FOUND, None

    if not user.has_permission(request_data.action):
        return StatusCode.PERMISSION_DENIED, None

    try:
        result = perform_action(request_data)
        return StatusCode.SUCCESS, result
    except Exception:
        return StatusCode.INTERNAL_ERROR, None

# Usage requires explicit checking
status, result = legacy_api_call(request)
if status == StatusCode.SUCCESS:
    process(result)
elif status == StatusCode.NOT_FOUND:
    handle_not_found()
# ... must check all codes
```

**Modern Alternative: Exceptions** (preferred in most languages)

### 6. Throw Exception

**Use When**: Error is exceptional and caller should handle it.

```java
// Throw exceptions (preferred in modern code)
public User authenticateUser(String username, String password) {
    if (username == null || username.trim().isEmpty()) {
        throw new IllegalArgumentException("Username is required");
    }

    User user = userRepository.findByUsername(username);
    if (user == null) {
        throw new AuthenticationException("Invalid credentials");
    }

    if (!passwordEncoder.matches(password, user.getPasswordHash())) {
        throw new AuthenticationException("Invalid credentials");
    }

    if (user.isLocked()) {
        throw new AccountLockedException("Account is locked");
    }

    return user;
}
```

### 7. Shut Down

**Use When**: Continuing would cause more damage than stopping.

```python
# Shutdown for unrecoverable errors
def initialize_application():
    """Initialize application or exit if critical components fail."""
    try:
        load_configuration()
    except ConfigurationError as e:
        logger.critical("Failed to load configuration", exc_info=e)
        sys.exit(1)  # Cannot run without configuration

    try:
        connect_to_database()
    except DatabaseConnectionError as e:
        logger.critical("Failed to connect to database", exc_info=e)
        sys.exit(1)  # Cannot run without database

    try:
        initialize_optional_features()
    except Exception as e:
        # Non-critical: log but continue
        logger.error("Failed to initialize optional features", exc_info=e)

    logger.info("Application initialized successfully")

# Circuit breaker shutdown
class CircuitBreaker:
    def __init__(self, failure_threshold=5):
        self.failure_count = 0
        self.failure_threshold = failure_threshold

    def call(self, operation):
        if self.failure_count >= self.failure_threshold:
            logger.critical("Circuit breaker threshold exceeded - shutting down")
            raise SystemExit("Too many failures - system is unhealthy")

        try:
            result = operation()
            self.failure_count = 0  # Reset on success
            return result
        except Exception as e:
            self.failure_count += 1
            logger.error(f"Operation failed ({self.failure_count}/{self.failure_threshold})")
            raise
```

## Use Exceptions Rather Than Return Codes (Clean Code)

### Why Exceptions Are Better

**1. Separation of Concerns**: Error handling doesn't clutter business logic.

```typescript
// POOR: Error codes clutter logic
function processOrder(order: Order): number {
    const validationCode = validateOrder(order);
    if (validationCode !== 0) {
        return validationCode;
    }

    const inventoryCode = checkInventory(order);
    if (inventoryCode !== 0) {
        return inventoryCode;
    }

    const paymentCode = processPayment(order);
    if (paymentCode !== 0) {
        return paymentCode;
    }

    const fulfillmentCode = fulfillOrder(order);
    if (fulfillmentCode !== 0) {
        return fulfillmentCode;
    }

    return 0;  // Success
}

// GOOD: Exceptions separate error handling
function processOrder(order: Order): void {
    // Clear business logic flow
    validateOrder(order);
    checkInventory(order);
    processPayment(order);
    fulfillOrder(order);
    // Errors handled separately by caller
}

// Caller handles errors cleanly
try {
    processOrder(order);
    showSuccessMessage();
} catch (ValidationError e) {
    showValidationError(e.message);
} catch (InventoryError e) {
    showInventoryError(e.message);
} catch (PaymentError e) {
    showPaymentError(e.message);
}
```

**2. Cannot Be Ignored**: Exceptions must be handled or propagated.

```java
// Error codes can be accidentally ignored
int result = riskyOperation();  // What if we forget to check result?
continueProcessing();  // Continues even if riskyOperation failed!

// Exceptions cannot be ignored
try {
    riskyOperation();  // If it throws, execution stops here
    continueProcessing();  // Won't run if exception thrown
} catch (Exception e) {
    // Must explicitly handle or let it propagate
}
```

**3. Rich Context**: Exceptions carry stack traces and context.

```python
# Error code: minimal information
def divide(a, b):
    if b == 0:
        return -1  # Error code - no context

# Exception: rich information
def divide(a, b):
    if b == 0:
        raise ValueError(f"Division by zero: {a} / {b}")
    # Exception includes message, stack trace, context
```

### When Error Codes Are Acceptable

**Low-level libraries**: C APIs, embedded systems, performance-critical paths.

```c
// C code - exceptions not available
int read_file(const char* filename, char* buffer, size_t size) {
    FILE* file = fopen(filename, "r");
    if (file == NULL) {
        return ERROR_FILE_NOT_FOUND;
    }

    size_t bytes_read = fread(buffer, 1, size, file);
    if (bytes_read < size && ferror(file)) {
        fclose(file);
        return ERROR_READ_FAILED;
    }

    fclose(file);
    return SUCCESS;
}
```

**Performance-critical paths**: Inner loops where exception overhead matters.

```python
# Hot path: use error codes for performance
def parse_number_fast(text):
    """Fast parsing returning (success, value) tuple."""
    try:
        return (True, int(text))
    except ValueError:
        return (False, 0)

# Called in tight loop
for line in huge_file:
    success, number = parse_number_fast(line)
    if success:
        process(number)
    # No exception overhead in failure case
```

## Write Try-Catch-Finally First (Clean Code)

### The TDD Approach to Error Handling

**Principle**: When writing code that can throw exceptions, start by writing the try-catch-finally structure. This forces you to think about error handling upfront.

```java
// Start with try-catch-finally structure
public void processFile(String filename) {
    BufferedReader reader = null;
    try {
        reader = new BufferedReader(new FileReader(filename));
        // TODO: Add processing logic
    } catch (IOException e) {
        // TODO: Handle errors
    } finally {
        if (reader != null) {
            try {
                reader.close();
            } catch (IOException e) {
                logger.error("Failed to close reader", e);
            }
        }
    }
}

// Then fill in the logic
public void processFile(String filename) {
    BufferedReader reader = null;
    try {
        reader = new BufferedReader(new FileReader(filename));
        String line;
        while ((line = reader.readLine()) != null) {
            processLine(line);
        }
    } catch (IOException e) {
        throw new FileProcessingException("Failed to process file: " + filename, e);
    } finally {
        if (reader != null) {
            try {
                reader.close();
            } catch (IOException e) {
                logger.error("Failed to close reader", e);
            }
        }
    }
}
```

### Try-Catch-Finally Semantics

**Try Block**: Code that might throw exceptions
**Catch Block**: Error recovery logic
**Finally Block**: Cleanup that must happen regardless of success or failure

```python
# Python: Context managers (preferred over try-finally)
def process_file(filename):
    """Process file using context manager."""
    try:
        with open(filename, 'r') as file:
            for line in file:
                process_line(line)
    except IOError as e:
        raise FileProcessingError(f"Failed to process {filename}") from e
    # File automatically closed by context manager

# When you need both cleanup and error handling
def transfer_funds(from_account, to_account, amount):
    """Transfer funds with transaction semantics."""
    transaction = database.begin_transaction()
    try:
        from_account.withdraw(amount)
        to_account.deposit(amount)
        transaction.commit()
    except Exception as e:
        transaction.rollback()
        raise TransferError("Fund transfer failed") from e
    finally:
        transaction.close()
```

### Test Exception Paths First

```typescript
// TDD: Write test for exception case first
describe("UserService", () => {
    it("should throw InvalidEmailError for invalid email", () => {
        const userService = new UserService();
        expect(() => {
            userService.createUser("invalid-email", "password123");
        }).toThrow(InvalidEmailError);
    });

    it("should throw DuplicateUserError for existing email", () => {
        const userService = new UserService();
        userService.createUser("john@example.com", "password123");

        expect(() => {
            userService.createUser("john@example.com", "password456");
        }).toThrow(DuplicateUserError);
    });

    it("should create user successfully with valid data", () => {
        const userService = new UserService();
        const user = userService.createUser("jane@example.com", "password123");
        expect(user.email).toBe("jane@example.com");
    });
});
```

## Provide Context With Exceptions (Clean Code)

### The Problem: Generic Exceptions

```python
# BAD: No context
def process_payment(payment_data):
    if not payment_data:
        raise ValueError("Invalid input")
    # What's invalid? What input?

# BAD: Generic exception
def fetch_user(user_id):
    try:
        return database.query("SELECT * FROM users WHERE id = ?", user_id)
    except Exception as e:
        raise Exception("Error")
    # What error? Which user? What database?
```

### The Solution: Rich Context

```python
# GOOD: Detailed context
def process_payment(payment_data):
    if payment_data is None:
        raise ValueError("Payment data cannot be None")

    if not payment_data.get("amount"):
        raise ValueError(
            f"Payment amount is required. Received payment data: {payment_data}"
        )

    if payment_data["amount"] <= 0:
        raise ValueError(
            f"Payment amount must be positive. "
            f"Received: {payment_data['amount']} for user {payment_data.get('user_id')}"
        )

# GOOD: Contextual exception
class UserNotFoundError(Exception):
    def __init__(self, user_id, additional_context=None):
        self.user_id = user_id
        self.additional_context = additional_context
        message = f"User not found: {user_id}"
        if additional_context:
            message += f" ({additional_context})"
        super().__init__(message)

def fetch_user(user_id):
    try:
        result = database.query("SELECT * FROM users WHERE id = ?", user_id)
        if not result:
            raise UserNotFoundError(user_id, "Database query returned no results")
        return result
    except DatabaseError as e:
        raise UserNotFoundError(
            user_id,
            f"Database error: {str(e)}"
        ) from e
```

### Exception Wrapping Pattern

```java
// Wrap low-level exceptions with business context
public class OrderService {
    public Order createOrder(OrderRequest request) {
        try {
            validateOrderRequest(request);
            return orderRepository.save(request);
        } catch (ValidationException e) {
            throw new OrderCreationException(
                "Order validation failed for customer: " + request.getCustomerId(),
                e
            );
        } catch (RepositoryException e) {
            throw new OrderCreationException(
                "Failed to persist order for customer: " + request.getCustomerId(),
                e
            );
        }
    }
}

// Exception hierarchy with context
public class OrderCreationException extends BusinessException {
    private final String customerId;
    private final OrderRequest request;

    public OrderCreationException(String message, Throwable cause) {
        super(message, cause);
        this.customerId = extractCustomerId(cause);
        this.request = extractRequest(cause);
    }

    public Map<String, Object> getContext() {
        Map<String, Object> context = new HashMap<>();
        context.put("customerId", customerId);
        context.put("orderAmount", request.getAmount());
        context.put("timestamp", System.currentTimeMillis());
        return context;
    }
}
```

### Logging Context

```typescript
// Add context to error logs
class PaymentProcessor {
    async processPayment(payment: Payment): Promise<Transaction> {
        const startTime = Date.now();
        const correlationId = generateCorrelationId();

        try {
            logger.info("Processing payment", {
                correlationId,
                customerId: payment.customerId,
                amount: payment.amount
            });

            const result = await this.chargeCard(payment);

            logger.info("Payment processed successfully", {
                correlationId,
                transactionId: result.id,
                duration: Date.now() - startTime
            });

            return result;

        } catch (error) {
            logger.error("Payment processing failed", {
                correlationId,
                customerId: payment.customerId,
                amount: payment.amount,
                duration: Date.now() - startTime,
                error: error.message,
                stack: error.stack
            });

            throw new PaymentProcessingError(
                `Payment failed for customer ${payment.customerId}`,
                { correlationId, originalError: error }
            );
        }
    }
}
```

## Define Exception Classes Based on Caller's Needs (Clean Code)

### The Problem: Too Many Exception Types

```python
# BAD: Exposing implementation details through exceptions
class ExternalAPIClient:
    def fetch_data(self, endpoint):
        # Caller must handle all these specific exceptions
        raise ConnectionTimeoutException()
        raise SSLCertificateException()
        raise HTTPErrorException()
        raise JSONParseException()
        raise RateLimitException()
        # Too many!

# Caller code is messy
try:
    data = api_client.fetch_data("/users")
except ConnectionTimeoutException:
    # Handle timeout
except SSLCertificateException:
    # Handle SSL
except HTTPErrorException:
    # Handle HTTP
except JSONParseException:
    # Handle JSON
except RateLimitException:
    # Handle rate limit
# Complex and brittle!
```

### The Solution: Define Exceptions for Caller's Context

```python
# GOOD: Wrap implementation details
class APIError(Exception):
    """Base exception for API operations."""
    pass

class APIConnectionError(APIError):
    """Raised when cannot connect to API."""
    pass

class APIDataError(APIError):
    """Raised when API returns invalid data."""
    pass

class APIRateLimitError(APIError):
    """Raised when API rate limit exceeded."""
    pass

class ExternalAPIClient:
    def fetch_data(self, endpoint):
        try:
            response = requests.get(endpoint, timeout=5)
            response.raise_for_status()
            return response.json()
        except (requests.Timeout, requests.ConnectionError) as e:
            raise APIConnectionError(f"Failed to connect to {endpoint}") from e
        except requests.HTTPError as e:
            if e.response.status_code == 429:
                raise APIRateLimitError("Rate limit exceeded") from e
            raise APIConnectionError(f"HTTP error: {e}") from e
        except ValueError as e:
            raise APIDataError("Invalid JSON response") from e

# Caller code is clean
try:
    data = api_client.fetch_data("/users")
except APIRateLimitError:
    # Wait and retry
    time.sleep(60)
    data = api_client.fetch_data("/users")
except APIError as e:
    # Handle all other API errors uniformly
    logger.error(f"API error: {e}")
    data = get_cached_data()
```

### Exception Hierarchy Design

```java
// Design exception hierarchy for caller's perspective
// Bad: Implementation-focused hierarchy
class DatabaseException extends Exception {}
class ConnectionPoolExhaustedException extends DatabaseException {}
class PreparedStatementException extends DatabaseException {}
class ResultSetProcessingException extends DatabaseException {}

// Good: Caller-focused hierarchy
class DataAccessException extends Exception {}
class DataNotFoundException extends DataAccessException {}
class DataIntegrityException extends DataAccessException {}
class DataAccessResourceException extends DataAccessException {}

// Implementation
public class UserRepository {
    public User findById(String userId) {
        try {
            return database.queryForObject("SELECT * FROM users WHERE id = ?", userId);
        } catch (SQLException e) {
            if (e.getErrorCode() == ErrorCodes.NO_DATA_FOUND) {
                throw new DataNotFoundException("User not found: " + userId, e);
            } else if (e.getErrorCode() == ErrorCodes.CONNECTION_FAILED) {
                throw new DataAccessResourceException("Database unavailable", e);
            } else {
                throw new DataAccessException("Database error", e);
            }
        }
    }
}

// Caller handles business-level exceptions
try {
    User user = userRepository.findById(userId);
    return user;
} catch (DataNotFoundException e) {
    return createDefaultUser();
} catch (DataAccessException e) {
    throw new ServiceUnavailableException("User service is unavailable", e);
}
```

## Don't Return Null (Clean Code)

### The Problem: Null Checks Everywhere

```typescript
// BAD: Returning null requires defensive checks everywhere
function getUser(userId: string): User | null {
    const user = database.findUser(userId);
    return user ? user : null;
}

// Caller must remember to check
const user = getUser("123");
if (user !== null) {  // Easy to forget
    console.log(user.name);
}

// Worse: Chained null checks
const user = getUser("123");
if (user !== null) {
    const address = user.getAddress();
    if (address !== null) {
        const city = address.getCity();
        if (city !== null) {
            console.log(city);
        }
    }
}
```

### Solution 1: Throw Exception

```typescript
// GOOD: Throw exception instead of returning null
function getUser(userId: string): User {
    const user = database.findUser(userId);
    if (!user) {
        throw new UserNotFoundError(`User not found: ${userId}`);
    }
    return user;
}

// Caller handles exceptional case explicitly
try {
    const user = getUser("123");
    console.log(user.name);  // No null check needed
} catch (UserNotFoundError e) {
    console.log("User not found");
}
```

### Solution 2: Null Object Pattern

```python
# Null Object Pattern
class User:
    def __init__(self, name, email):
        self.name = name
        self.email = email

    def send_email(self, message):
        email_service.send(self.email, message)

class NullUser(User):
    """Null object - safe default behavior"""
    def __init__(self):
        super().__init__("Guest", "noreply@example.com")

    def send_email(self, message):
        # Null object: safe no-op
        logger.info("Attempted to send email to null user")

# Return null object instead of None
def get_user(user_id):
    user = database.find_user(user_id)
    return user if user else NullUser()

# No null checks needed
user = get_user("123")
user.send_email("Hello")  # Safe even if user not found
print(user.name)  # Always works: real name or "Guest"
```

### Solution 3: Optional/Maybe Type

```java
// Java: Optional type
public Optional<User> findUser(String userId) {
    User user = database.query(userId);
    return Optional.ofNullable(user);
}

// Explicit handling of presence/absence
Optional<User> userOpt = findUser("123");

// Option 1: Provide default
User user = userOpt.orElse(new GuestUser());

// Option 2: Throw exception
User user = userOpt.orElseThrow(() ->
    new UserNotFoundException("User not found: 123")
);

// Option 3: Execute only if present
userOpt.ifPresent(user -> sendWelcomeEmail(user));

// Option 4: Transform if present
String userName = userOpt
    .map(User::getName)
    .orElse("Guest");
```

### Solution 4: Return Empty Collection

```python
# NEVER return None for collections
def get_user_orders(user_id):
    """Get user orders - WRONG"""
    orders = database.query_orders(user_id)
    return orders if orders else None  # BAD

# Caller must check for None
orders = get_user_orders(user_id)
if orders is not None:  # Annoying check
    for order in orders:
        process(order)

# ALWAYS return empty collection
def get_user_orders(user_id):
    """Get user orders - CORRECT"""
    orders = database.query_orders(user_id)
    return orders if orders else []  # Return empty list

# Caller code is clean
orders = get_user_orders(user_id)
for order in orders:  # Works even if empty
    process(order)
```

## Don't Pass Null (Clean Code)

### The Problem: Null Parameters

```java
// BAD: Accepting null parameters
public void processOrder(Order order) {
    if (order == null) {
        // What should we do here?
        return;  // Silent failure
        // or throw exception?
        // or use default?
    }
    // Process order
}

// Caller can pass null (accidentally or intentionally)
processOrder(null);  // Compiles but wrong
```

### Solution 1: Validate and Throw

```java
// GOOD: Reject null immediately
public void processOrder(Order order) {
    if (order == null) {
        throw new IllegalArgumentException("Order cannot be null");
    }
    // Process order - guaranteed non-null
}

// Better: Use Objects.requireNonNull (Java)
public void processOrder(Order order) {
    Objects.requireNonNull(order, "Order cannot be null");
    // Process order
}
```

### Solution 2: Use Type System

```typescript
// TypeScript: Non-null type
function processOrder(order: Order): void {  // No 'null' or 'undefined' in type
    // order is guaranteed to be Order instance
    console.log(order.id);  // Safe
}

// Caller must provide non-null
processOrder(order);  // OK
processOrder(null);  // Compile error!

// If null is valid, make it explicit
function processOrder(order: Order | null): void {
    if (order === null) {
        throw new Error("Order cannot be null");
    }
    // Type narrowing: order is Order here
    console.log(order.id);
}
```

### Solution 3: Multiple Overloads

```python
# Python: Use default parameters instead of allowing None
def send_email(recipient, subject, body="", attachments=None):
    """Send email with optional body and attachments."""
    if attachments is None:
        attachments = []  # Use empty list, not None

    # Safe to iterate - never None
    for attachment in attachments:
        add_attachment(attachment)

# Instead of:
def send_email_bad(recipient, subject, body, attachments):
    if body is None:
        body = ""
    if attachments is None:
        attachments = []
    # Defensive null checks required
```

## Assertions (Code Complete 2)

### What Are Assertions?

**Definition**: Statements that should always be true at a specific point in code. Used to catch programming errors during development.

**Key Principle**: Assertions are for development, not production error handling.

```python
# Assertion examples
def calculate_discount(price, discount_percentage):
    assert price >= 0, "Price cannot be negative"
    assert 0 <= discount_percentage <= 100, "Discount must be 0-100"

    discount = price * (discount_percentage / 100)

    assert discount <= price, "Discount cannot exceed price"
    return discount
```

### When to Use Assertions

**Use assertions for**:
- Preconditions: Conditions that must be true before function executes
- Postconditions: Conditions that must be true after function executes
- Invariants: Conditions that must always be true
- Impossible conditions: Code paths that should never execute

```java
// Preconditions
public void withdraw(double amount) {
    assert amount > 0 : "Amount must be positive";
    assert amount <= balance : "Insufficient funds";
    balance -= amount;
    assert balance >= 0 : "Balance cannot be negative (postcondition)";
}

// Invariants
public class BankAccount {
    private double balance;

    private void checkInvariant() {
        assert balance >= 0 : "Invariant violated: negative balance";
    }

    public void deposit(double amount) {
        checkInvariant();  // Check before
        balance += amount;
        checkInvariant();  // Check after
    }
}

// Impossible conditions
public void processCommand(Command cmd) {
    switch (cmd.getType()) {
        case ADD:    handleAdd(cmd); break;
        case UPDATE: handleUpdate(cmd); break;
        case DELETE: handleDelete(cmd); break;
        default:
            assert false : "Unknown command type: " + cmd.getType();
    }
}
```

### Assertions vs Exceptions

**Assertions**: For programming errors (bugs in your code)
**Exceptions**: For runtime errors (external conditions)

```python
# WRONG: Using exception for programming error
def set_age(age):
    if age < 0:
        raise ValueError("Age cannot be negative")
    # Should be assertion - negative age is programmer error

# RIGHT: Assertion for programming error
def set_age(age):
    assert age >= 0, "Age cannot be negative (programming error)"
    self.age = age

# RIGHT: Exception for runtime error
def process_user_input(age_string):
    try:
        age = int(age_string)
    except ValueError:
        raise ValueError("Invalid age format")  # User input error
    if age < 0 or age > 150:
        raise ValueError("Age out of valid range")  # Business rule validation
    return age
```

### Assertion Guidelines

**Do**:
- Assert liberally during development
- Assert preconditions and postconditions
- Assert invariants
- Use assertions to document assumptions

**Don't**:
- Use assertions for user input validation
- Put code with side effects in assertions
- Use assertions instead of error handling
- Rely on assertions in production (they may be disabled)

```typescript
// DON'T: Side effects in assertions
let count = 0;
assert(count++ === 0);  // BAD: Modifies count

// DO: No side effects
assert(count === 0);  // GOOD: Just checks

// DON'T: User input validation
function processInput(userAge: number) {
    assert(userAge > 0);  // WRONG: Use exception
}

// DO: Exception for user input
function processInput(userAge: number) {
    if (userAge <= 0) {
        throw new ValidationError("Age must be positive");
    }
}
```

## Barricades (Code Complete 2)

### The Concept

**Barricade**: A defensive boundary that validates all data entering from external sources. Inside the barricade, data is trusted.

**Pattern**: Validate once at the boundary, trust internally.

```python
# Barricade pattern
class UserAPI:
    """External API boundary - BARRICADE"""

    def create_user(self, request_data):
        """Public API endpoint - validate all inputs."""
        # BARRICADE: Validate external data
        validated_data = self._validate_and_sanitize(request_data)

        # Pass trusted data to internal logic
        return UserService.create_user_internal(validated_data)

    def _validate_and_sanitize(self, data):
        """Validate and sanitize all external input."""
        if not isinstance(data, dict):
            raise ValidationError("Request must be JSON object")

        email = data.get("email")
        if not email or not self._is_valid_email(email):
            raise ValidationError("Invalid email address")

        password = data.get("password")
        if not password or len(password) < 8:
            raise ValidationError("Password must be at least 8 characters")

        # Sanitize and return trusted data
        return {
            "email": email.strip().lower(),
            "password": password,
            "name": data.get("name", "").strip()[:100]  # Limit length
        }

class UserService:
    """Internal service - INSIDE BARRICADE"""

    @staticmethod
    def create_user_internal(validated_data):
        """Internal method - data already validated.
        No need for defensive checks here."""
        # Trust the data - it was validated at barricade
        user = User(
            email=validated_data["email"],
            password_hash=hash_password(validated_data["password"]),
            name=validated_data["name"]
        )
        database.save(user)
        return user
```

### Barricade Layers

```java
// Multi-layer barricade
public class OrderingSystem {
    // Layer 1: External API (HTTP)
    @RestController
    public class OrderController {
        @PostMapping("/orders")
        public ResponseEntity<Order> createOrder(@RequestBody OrderRequest request) {
            // BARRICADE LAYER 1: Validate HTTP input
            validateHttpRequest(request);

            OrderDTO dto = convertToDTO(request);
            return orderService.createOrder(dto);
        }

        private void validateHttpRequest(OrderRequest request) {
            if (request == null) throw new BadRequestException("Request body required");
            if (request.getCustomerId() == null) throw new BadRequestException("Customer ID required");
            // ... comprehensive HTTP-level validation
        }
    }

    // Layer 2: Service Layer
    @Service
    public class OrderService {
        public Order createOrder(OrderDTO dto) {
            // BARRICADE LAYER 2: Validate business rules
            validateBusinessRules(dto);

            Order order = orderRepository.create(dto);
            return order;
        }

        private void validateBusinessRules(OrderDTO dto) {
            Customer customer = customerRepository.findById(dto.getCustomerId());
            if (customer == null) {
                throw new BusinessException("Customer not found");
            }
            if (!customer.isActive()) {
                throw new BusinessException("Customer account is inactive");
            }
            // ... business rule validation
        }
    }

    // Layer 3: Repository (Database)
    @Repository
    public class OrderRepository {
        public Order create(OrderDTO dto) {
            // INSIDE ALL BARRICADES: No validation needed
            // Data has been validated at both HTTP and business layers
            return database.insert(new Order(dto));
        }
    }
}
```

### Benefits of Barricades

1. **Single Point of Validation**: Validate once, trust thereafter
2. **Clear Boundaries**: Obvious where validation happens
3. **Performance**: No redundant validation
4. **Maintainability**: Validation logic centralized
5. **Security**: All external data sanitized at boundary

## Defensive Programming: How Much Is Enough? (Code Complete 2)

### The Spectrum

**Too Little**: Production failures, security vulnerabilities, data corruption
**Too Much**: Code clutter, performance overhead, development slowdown
**Just Right**: Validated boundaries, checked assumptions, graceful failures

### Production Code vs Development Code

```python
# Development mode: Aggressive assertions
def calculate_loan_payment(principal, rate, months):
    # Development: Check everything
    assert principal > 0, f"Invalid principal: {principal}"
    assert 0 < rate < 1, f"Invalid rate: {rate}"
    assert months > 0, f"Invalid months: {months}"

    monthly_rate = rate / 12
    payment = principal * (monthly_rate * (1 + monthly_rate) ** months) / \
              ((1 + monthly_rate) ** months - 1)

    assert payment > 0, f"Invalid payment: {payment}"
    assert payment < principal * 10, f"Suspiciously high payment: {payment}"

    return payment

# Production mode: Essential validation only
def calculate_loan_payment(principal, rate, months):
    # Production: Validate inputs, handle errors
    if principal <= 0:
        raise ValueError("Principal must be positive")
    if not (0 < rate < 1):
        raise ValueError("Rate must be between 0 and 1")
    if months <= 0:
        raise ValueError("Loan term must be positive")

    monthly_rate = rate / 12
    payment = principal * (monthly_rate * (1 + monthly_rate) ** months) / \
              ((1 + monthly_rate) ** months - 1)

    return payment
```

### Critical vs Non-Critical Code

**Critical Code**: Financial, medical, safety-critical
- Extensive validation
- Redundant checks
- Graceful degradation
- Comprehensive logging

```java
// Critical: Financial transaction
public class MoneyTransfer {
    public void transfer(Account from, Account to, BigDecimal amount) {
        // Extensive validation for financial operations
        validateAccount(from, "source");
        validateAccount(to, "destination");
        validateAmount(amount);
        validateSufficientFunds(from, amount);

        // Pre-condition checks
        BigDecimal fromBalanceBefore = from.getBalance();
        BigDecimal toBalanceBefore = to.getBalance();
        BigDecimal totalBefore = fromBalanceBefore.add(toBalanceBefore);

        // Perform transfer
        from.withdraw(amount);
        to.deposit(amount);

        // Post-condition checks (invariant: total unchanged)
        BigDecimal totalAfter = from.getBalance().add(to.getBalance());
        if (!totalBefore.equals(totalAfter)) {
            // Critical invariant violated - roll back
            rollback(from, to, fromBalanceBefore, toBalanceBefore);
            throw new InvariantViolationException("Transfer violated balance invariant");
        }

        // Redundant verification
        if (!from.getBalance().equals(fromBalanceBefore.subtract(amount))) {
            rollback(from, to, fromBalanceBefore, toBalanceBefore);
            throw new InvariantViolationException("Source balance incorrect");
        }

        logger.info("Transfer completed", Map.of(
            "from", from.getId(),
            "to", to.getId(),
            "amount", amount,
            "fromBalanceBefore", fromBalanceBefore,
            "fromBalanceAfter", from.getBalance()
        ));
    }
}
```

**Non-Critical Code**: UI, logging, analytics
- Basic validation
- Fail gracefully
- Don't interrupt user experience

```typescript
// Non-critical: Analytics tracking
function trackUserAction(action: string, metadata?: Record<string, any>): void {
    try {
        // Basic validation only
        if (!action || action.trim() === "") {
            logger.warn("Empty action name for tracking");
            return;  // Fail silently - analytics not critical
        }

        // Send to analytics (fire and forget)
        analyticsService.track(action, metadata || {}).catch(error => {
            // Don't let analytics failure affect user experience
            logger.error("Analytics tracking failed", { action, error });
        });

    } catch (error) {
        // Swallow exception - analytics failure shouldn't crash app
        logger.error("Analytics error", error);
    }
}
```

## Practical Error Handling Checklist

Use this checklist when implementing error handling:

### Design Phase
- [ ] Identified all error conditions (input validation, resource failures, business rule violations)
- [ ] Decided correctness vs robustness strategy
- [ ] Designed exception hierarchy based on caller needs
- [ ] Identified barricade boundaries
- [ ] Determined critical vs non-critical code paths

### Implementation Phase
- [ ] Used exceptions instead of error codes (modern code)
- [ ] Provided rich context in all exceptions
- [ ] Wrapped low-level exceptions at boundaries
- [ ] Validated inputs at barricades
- [ ] Used assertions for programming errors
- [ ] No side effects in error handling
- [ ] Resources cleaned up properly (try-finally, context managers)

### Error Messages
- [ ] Messages describe what went wrong
- [ ] Messages include relevant context (IDs, values, timestamps)
- [ ] Messages don't expose sensitive data
- [ ] Messages help users/developers fix the problem
- [ ] Stack traces preserved (exception chaining)

### Error Recovery
- [ ] Appropriate recovery strategy chosen (retry, fallback, fail)
- [ ] Transient errors retried with backoff
- [ ] Permanent errors fail fast
- [ ] Partial failures handled gracefully
- [ ] Resources released on error paths

### Don't Return/Pass Null
- [ ] Functions don't return null (throw exception or return empty collection/Optional)
- [ ] Functions don't accept null parameters
- [ ] Null object pattern used where appropriate
- [ ] Optional/Maybe types used where appropriate

### Testing
- [ ] Happy path tested
- [ ] All exception paths tested
- [ ] Boundary conditions tested
- [ ] Recovery logic tested
- [ ] Error messages verified

### Logging & Monitoring
- [ ] Errors logged with context
- [ ] Correlation IDs tracked
- [ ] Metrics collected for error rates
- [ ] Alerts configured for critical errors
- [ ] Log levels appropriate (ERROR vs WARN vs INFO)

## Summary: Error Handling Principles

1. **Use Exceptions**: Exceptions are clearer than error codes in modern languages
2. **Provide Context**: Include what, why, where, and how to fix
3. **Separate Concerns**: Keep error handling separate from business logic
4. **Fail Fast**: Detect errors early, near their source
5. **Don't Return Null**: Use exceptions, empty collections, or Optional types
6. **Don't Pass Null**: Validate parameters, use type system
7. **Barricades**: Validate at boundaries, trust internally
8. **Assert Liberally**: Use assertions for programming errors during development
9. **Correctness vs Robustness**: Choose based on criticality
10. **Clean Resources**: Always clean up (try-finally, context managers)

## Further Reading

- **Clean Code** (Chapter 7: Error Handling) - Robert C. Martin
- **Code Complete 2** (Chapter 8: Defensive Programming) - Steve McConnell
- **Release It!** (Chapter 5: Stability Patterns) - Michael Nygard
- **The Pragmatic Programmer** (Chapter 4: Pragmatic Paranoia) - Hunt & Thomas

---

**Remember**: Error handling is not a separate activity—it is integral to software design. Systems that handle errors well are robust, maintainable, and trustworthy. Invest in error handling from the start.
