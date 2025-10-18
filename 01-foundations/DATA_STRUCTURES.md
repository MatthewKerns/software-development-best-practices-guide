# Data Structures: Organizing Information for Clarity and Performance

## Overview

Data structures are the backbone of every program. They determine how information is organized, accessed, and manipulated. Poor data structure choices lead to convoluted code, performance problems, and maintenance nightmares. Good data structure choices make code elegant, performant, and maintainable.

This comprehensive guide synthesizes data structure wisdom from industry-leading sources and provides practical, actionable guidance for choosing and using data structures effectively.

**"Bad programmers worry about the code. Good programmers worry about data structures and their relationships."** — Linus Torvalds

## Why Data Structures Matter

### The Cost of Poor Data Structure Choices

Poor data structures create measurable costs:

**Performance Problems**: Using a list when you need constant-time lookup forces O(n) searches. Using a tree when you need sequential access creates pointer-chasing overhead. These choices compound across millions of operations.

**Complexity Explosion**: Fighting against inappropriate data structures creates convoluted code. Simple operations require complex workarounds. Logic becomes tangled with data manipulation.

**Maintenance Burden**: Unclear data organization makes code hard to understand. Implicit relationships between data elements hide in code instead of being explicit in structure.

**Memory Waste**: Inappropriate structures waste memory. Sparse data in dense arrays. Tiny objects with massive overhead. Memory fragmentation from poor allocation patterns.

**Concurrency Issues**: Shared mutable state causes race conditions. Missing synchronization creates data corruption. Overly aggressive locking kills performance.

### The Benefits of Good Data Structures

Good data structures provide:
- **Natural Algorithms**: Operations flow naturally from structure
- **Performance**: Right structure gives right time complexity
- **Clarity**: Structure makes relationships explicit
- **Safety**: Type-safe structures prevent errors
- **Maintainability**: Clear organization aids understanding
- **Scalability**: Efficient structures handle growth

## Source Materials

This guide synthesizes principles from:

- **Code Complete 2** by Steve McConnell (Chapter 12: "Fundamental Data Types", Chapter 13: "Unusual Data Types")
  - Choosing data types
  - Creating custom types
  - Type safety
  - Data structure design

- **Clean Code** by Robert C. Martin (Chapter 6: "Objects and Data Structures")
  - Data/object anti-symmetry
  - Data abstraction
  - Law of Demeter
  - Data transfer objects

## Fundamental Data Types (Code Complete 2)

### Numbers: Integers and Floating Point

#### Integer Types: Choosing the Right Size

```python
# Python: Integers have unlimited precision (no overflow)
count = 0
large_number = 10 ** 100  # Works fine

# But be explicit about size in fixed-width contexts
import struct

# 8-bit unsigned (0-255)
byte_value = struct.pack('B', 200)

# 32-bit signed integer
int32_value = struct.pack('i', -2147483648)

# 64-bit unsigned integer
uint64_value = struct.pack('Q', 18446744073709551615)
```

```java
// Java: Choose appropriate integer type
byte smallCount = 127;        // -128 to 127
short pageNumber = 30000;     // -32,768 to 32,767
int userId = 2147483647;      // -2^31 to 2^31-1
long transactionId = 9223372036854775807L;  // -2^63 to 2^63-1

// Use smallest type that fits your range
// Saves memory in large arrays/collections
byte[] smallValues = new byte[1_000_000];  // 1 MB
int[] largeValues = new int[1_000_000];    // 4 MB
```

**Defensive: Check for Overflow**

```typescript
// TypeScript: Check for safe integer range
function addSafely(a: number, b: number): number {
    const result = a + b;

    // JavaScript numbers are IEEE 754 doubles
    // Safe integer range: -(2^53-1) to (2^53-1)
    if (!Number.isSafeInteger(result)) {
        throw new Error(
            `Integer overflow: ${a} + ${b} = ${result} exceeds safe range`
        );
    }

    return result;
}

// Use BigInt for large integers
const largeNumber = BigInt("9007199254740991");
const result = largeNumber + BigInt(1);  // Safe, no overflow
```

#### Floating Point: Precision and Rounding

```python
# WRONG: Float for money (has rounding errors)
price = 0.1 + 0.2  # 0.30000000000000004 (not 0.3!)

# RIGHT: Decimal for money (exact decimal arithmetic)
from decimal import Decimal

price = Decimal('0.1') + Decimal('0.2')  # Exactly 0.3
tax = Decimal('19.99') * Decimal('0.08')  # Exact calculation

# Always use Decimal for financial calculations
def calculate_order_total(item_prices: list[str], tax_rate: str) -> Decimal:
    """Calculate order total with exact decimal arithmetic."""
    subtotal = sum(Decimal(price) for price in item_prices)
    tax = subtotal * Decimal(tax_rate)
    total = subtotal + tax
    return total.quantize(Decimal('0.01'))  # Round to cents
```

```java
// Java: BigDecimal for financial calculations
public BigDecimal calculateCompoundInterest(
    BigDecimal principal,
    BigDecimal rate,
    int years
) {
    // NEVER use double for money calculations
    // Use BigDecimal for exact decimal arithmetic

    BigDecimal amount = principal;
    BigDecimal onePlusRate = BigDecimal.ONE.add(rate);

    for (int i = 0; i < years; i++) {
        amount = amount.multiply(onePlusRate);
    }

    // Round to 2 decimal places
    return amount.setScale(2, RoundingMode.HALF_UP);
}

// Example: Comparing doubles
public boolean isPriceEqual(double price1, double price2) {
    // WRONG: Direct comparison
    // return price1 == price2;  // Fails due to rounding errors

    // RIGHT: Compare with epsilon tolerance
    final double EPSILON = 0.001;
    return Math.abs(price1 - price2) < EPSILON;
}
```

### Characters and Strings

#### String Immutability and Performance

```python
# WRONG: String concatenation in loop (O(n²) time)
def build_csv_row_slow(values: list[str]) -> str:
    result = ""
    for value in values:
        result += value + ","  # Creates new string each time!
    return result.rstrip(",")

# RIGHT: Use join (O(n) time)
def build_csv_row_fast(values: list[str]) -> str:
    return ",".join(values)

# RIGHT: Use StringBuilder pattern for complex building
def build_report(data: list[dict]) -> str:
    lines = []  # List used as string builder
    lines.append("Report Header")
    lines.append("=" * 50)

    for row in data:
        lines.append(f"{row['name']}: {row['value']}")

    lines.append("=" * 50)
    lines.append(f"Total: {sum(r['value'] for r in data)}")

    return "\n".join(lines)
```

```java
// Java: StringBuilder for string building
public String generateHtmlTable(List<User> users) {
    // WRONG: String concatenation in loop
    // String html = "<table>";
    // for (User user : users) {
    //     html += "<tr><td>" + user.getName() + "</td></tr>";
    // }
    // html += "</table>";

    // RIGHT: StringBuilder for efficiency
    StringBuilder html = new StringBuilder();
    html.append("<table>\n");

    for (User user : users) {
        html.append("  <tr>\n");
        html.append("    <td>").append(user.getName()).append("</td>\n");
        html.append("    <td>").append(user.getEmail()).append("</td>\n");
        html.append("  </tr>\n");
    }

    html.append("</table>");
    return html.toString();
}
```

#### String Validation and Sanitization

```typescript
// Defensive string handling
function sanitizeUsername(input: string | null | undefined): string {
    // Defensive: Handle null/undefined
    if (input == null) {
        throw new ValidationError('Username cannot be null or undefined');
    }

    // Defensive: Ensure it's a string
    const str = String(input);

    // Sanitize: Trim whitespace
    const trimmed = str.trim();

    // Validate: Length
    if (trimmed.length < 3) {
        throw new ValidationError('Username must be at least 3 characters');
    }
    if (trimmed.length > 50) {
        throw new ValidationError('Username cannot exceed 50 characters');
    }

    // Validate: Characters
    if (!/^[a-zA-Z0-9_-]+$/.test(trimmed)) {
        throw new ValidationError(
            'Username can only contain letters, numbers, underscore, and hyphen'
        );
    }

    return trimmed.toLowerCase();
}
```

### Booleans: Clear Intent

```python
# POOR: Boolean variables with unclear names
flag = True
status = False
result = True

# GOOD: Boolean variables with clear predicate names
is_valid = True
has_permission = False
can_edit = True
should_retry = False
was_successful = True

# GOOD: Boolean functions with clear names
def is_eligible_for_discount(user: User, order: Order) -> bool:
    """Check if user is eligible for discount."""
    return (
        user.membership_level == 'premium'
        and order.total > 100
        and user.account_age_days > 30
    )

# Use the boolean expressively
if is_eligible_for_discount(user, order):
    apply_discount(order)
```

**Avoid Magic Boolean Parameters**

```java
// BAD: Boolean parameter obscures meaning
saveUser(user, true);  // What does 'true' mean?
processOrder(order, false);  // What does 'false' mean?

// GOOD: Enum makes intent clear
enum NotificationPreference {
    SEND_EMAIL,
    NO_EMAIL
}

enum ProcessingMode {
    ASYNC,
    SYNC
}

saveUser(user, NotificationPreference.SEND_EMAIL);  // Clear!
processOrder(order, ProcessingMode.SYNC);  // Clear!
```

## Collections and Arrays (Code Complete 2)

### Choosing the Right Collection

#### Arrays: Fixed Size, Index Access

```python
# Python lists (dynamic arrays)
# Use when: Need index access, order matters, size unknown
user_ids = []
user_ids.append(123)
user_ids.append(456)
first_user = user_ids[0]  # O(1) access by index

# Fixed-size array (using array module)
import array
# Use when: Need fixed-size, homogeneous data, memory efficiency
sensor_readings = array.array('f', [0.0] * 1000)  # 1000 floats
sensor_readings[500] = 72.5  # O(1) access
```

```java
// Java arrays: Fixed size
// Use when: Size known at creation, need fast index access
int[] numbers = new int[100];
numbers[0] = 42;  // O(1) access

String[] names = {"Alice", "Bob", "Charlie"};
String first = names[0];  // O(1) access

// Defensive: Check bounds
public int getElement(int[] array, int index) {
    if (index < 0 || index >= array.length) {
        throw new IndexOutOfBoundsException(
            String.format("Index %d out of bounds for array length %d",
                index, array.length)
        );
    }
    return array[index];
}
```

#### Lists: Dynamic Size, Sequential Access

```typescript
// TypeScript/JavaScript Array (dynamic list)
// Use when: Size changes, need push/pop, order matters
const users: User[] = [];
users.push(newUser);     // O(1) append
users.pop();             // O(1) remove last
users.unshift(first);    // O(n) prepend
users.shift();           // O(n) remove first

// Searching in list
const user = users.find(u => u.id === '123');  // O(n) search

// Defensive: Check for empty
function getFirst<T>(list: T[]): T {
    if (list.length === 0) {
        throw new Error('Cannot get first element of empty list');
    }
    return list[0];
}
```

#### Sets: Unique Elements, Fast Lookup

```python
# Python set: Unordered, unique elements
# Use when: Need uniqueness, fast membership testing
seen_ids = set()
seen_ids.add(123)  # O(1) add
seen_ids.add(123)  # Duplicate ignored

if 123 in seen_ids:  # O(1) membership test
    print("ID already seen")

# Common use: Remove duplicates
items = [1, 2, 2, 3, 3, 3, 4]
unique_items = list(set(items))  # [1, 2, 3, 4]

# Set operations
set_a = {1, 2, 3, 4}
set_b = {3, 4, 5, 6}

union = set_a | set_b          # {1, 2, 3, 4, 5, 6}
intersection = set_a & set_b   # {3, 4}
difference = set_a - set_b     # {1, 2}
```

```java
// Java Set: Unique elements
// Use when: Need uniqueness, fast contains check
Set<String> uniqueEmails = new HashSet<>();
uniqueEmails.add("alice@example.com");  // O(1) add
uniqueEmails.add("alice@example.com");  // Duplicate ignored

if (uniqueEmails.contains("alice@example.com")) {  // O(1) lookup
    System.out.println("Email exists");
}

// LinkedHashSet: Maintains insertion order
Set<String> orderedSet = new LinkedHashSet<>();

// TreeSet: Sorted set
Set<Integer> sortedNumbers = new TreeSet<>();
sortedNumbers.add(5);
sortedNumbers.add(2);
sortedNumbers.add(8);
// Automatically sorted: [2, 5, 8]
```

#### Maps/Dictionaries: Key-Value Pairs

```python
# Python dict: Key-value mapping
# Use when: Need fast lookup by key, one-to-one mapping
user_by_id = {}
user_by_id[123] = User("Alice", "alice@example.com")  # O(1) set
user = user_by_id[123]  # O(1) get

# Defensive: Check key existence
def get_user_safe(user_id: int) -> User:
    if user_id not in user_by_id:
        raise KeyError(f"User not found: {user_id}")
    return user_by_id[user_id]

# Or use get with default
user = user_by_id.get(456, DEFAULT_USER)

# Common pattern: Count occurrences
from collections import Counter
words = ["apple", "banana", "apple", "cherry", "banana", "apple"]
word_counts = Counter(words)
# Counter({'apple': 3, 'banana': 2, 'cherry': 1})

# Common pattern: Group by key
from collections import defaultdict
users_by_role = defaultdict(list)
for user in all_users:
    users_by_role[user.role].append(user)
```

```typescript
// TypeScript Map: Key-value with any key type
// Use when: Need non-string keys or key order matters
const userById = new Map<number, User>();
userById.set(123, alice);  // O(1) set
const user = userById.get(123);  // O(1) get

// Defensive: Check existence
function getUserById(id: number): User {
    if (!userById.has(id)) {
        throw new Error(`User not found: ${id}`);
    }
    return userById.get(id)!;
}

// Object as dictionary (string keys only)
interface UserDictionary {
    [email: string]: User;
}

const userByEmail: UserDictionary = {};
userByEmail['alice@example.com'] = alice;

// Defensive: Check property existence
if ('alice@example.com' in userByEmail) {
    const user = userByEmail['alice@example.com'];
}
```

### Collection Performance Characteristics

| Operation | Array | List | Set | Map |
|-----------|-------|------|-----|-----|
| Access by index | O(1) | O(1) | N/A | N/A |
| Search by value | O(n) | O(n) | O(1) | N/A |
| Search by key | N/A | N/A | N/A | O(1) |
| Insert at end | N/A | O(1) | O(1) | O(1) |
| Insert at beginning | N/A | O(n) | O(1) | O(1) |
| Delete | O(n) | O(n) | O(1) | O(1) |
| Memory overhead | Low | Medium | Medium | High |

## Custom Types and Classes (Code Complete 2)

### When to Create Custom Types

**1. Make the Abstraction Obvious**

```python
# POOR: Primitive obsession
def calculate_shipping(weight_kg, distance_km, is_express):
    # Weight and distance are just numbers - no type safety
    pass

# GOOD: Custom types make abstraction clear
from dataclasses import dataclass
from decimal import Decimal

@dataclass(frozen=True)  # Immutable
class Weight:
    """Weight with validation."""
    kilograms: Decimal

    def __post_init__(self):
        if self.kilograms <= 0:
            raise ValueError("Weight must be positive")

@dataclass(frozen=True)
class Distance:
    """Distance with validation."""
    kilometers: Decimal

    def __post_init__(self):
        if self.kilometers <= 0:
            raise ValueError("Distance must be positive")

@dataclass(frozen=True)
class ShippingSpeed:
    """Shipping speed enumeration."""
    value: str

    STANDARD = "standard"
    EXPRESS = "express"

def calculate_shipping(
    weight: Weight,
    distance: Distance,
    speed: ShippingSpeed
) -> Decimal:
    # Type-safe, clear intent, validated inputs
    pass
```

**2. Simplify Complex Data**

```java
// POOR: Complex data passed as primitives
public void createOrder(
    String customerId,
    String[] productIds,
    int[] quantities,
    String shippingStreet,
    String shippingCity,
    String shippingZip
) {
    // Too many parameters, unclear relationships
}

// GOOD: Custom types organize complex data
public class Address {
    private final String street;
    private final String city;
    private final String zipCode;

    public Address(String street, String city, String zipCode) {
        validateNotEmpty(street, "Street");
        validateNotEmpty(city, "City");
        validateZipCode(zipCode);

        this.street = street;
        this.city = city;
        this.zipCode = zipCode;
    }

    // Getters and validation methods...
}

public class OrderItem {
    private final String productId;
    private final int quantity;

    public OrderItem(String productId, int quantity) {
        validateNotEmpty(productId, "Product ID");
        if (quantity <= 0) {
            throw new IllegalArgumentException("Quantity must be positive");
        }

        this.productId = productId;
        this.quantity = quantity;
    }

    // Getters...
}

public void createOrder(
    String customerId,
    List<OrderItem> items,
    Address shippingAddress
) {
    // Clear, organized, validated
}
```

**3. Make Operations on Data Safer**

```typescript
// POOR: Raw email string with scattered validation
function sendEmail(email: string, message: string): void {
    // Email validation scattered everywhere
    if (!email.includes('@')) {
        throw new Error('Invalid email');
    }
    // Send email...
}

function addUserEmail(userId: string, email: string): void {
    // Duplicate validation
    if (!email.includes('@')) {
        throw new Error('Invalid email');
    }
    // Save email...
}

// GOOD: Email type encapsulates validation
class Email {
    private readonly value: string;

    constructor(email: string) {
        // Validation in one place
        if (!email || typeof email !== 'string') {
            throw new ValidationError('Email must be a string');
        }

        const trimmed = email.trim().toLowerCase();

        if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(trimmed)) {
            throw new ValidationError(`Invalid email format: ${email}`);
        }

        if (trimmed.length > 255) {
            throw new ValidationError('Email too long (max 255 characters)');
        }

        this.value = trimmed;
    }

    toString(): string {
        return this.value;
    }

    getDomain(): string {
        return this.value.split('@')[1];
    }

    equals(other: Email): boolean {
        return this.value === other.value;
    }
}

// Usage: Always valid
function sendEmail(email: Email, message: string): void {
    // No validation needed - Email type guarantees validity
    emailService.send(email.toString(), message);
}

function addUserEmail(userId: string, email: Email): void {
    // No validation needed
    database.saveEmail(userId, email.toString());
}

// Validation happens once at construction
const email = new Email('alice@example.com');  // Validates
sendEmail(email, 'Welcome');  // No validation needed
```

### Value Objects vs Entities

**Value Objects**: Defined by their attributes, immutable

```python
from dataclasses import dataclass
from decimal import Decimal

@dataclass(frozen=True)  # Immutable value object
class Money:
    """Value object for money amounts."""
    amount: Decimal
    currency: str

    def __post_init__(self):
        if self.amount < 0:
            raise ValueError("Amount cannot be negative")
        if self.currency not in ['USD', 'EUR', 'GBP']:
            raise ValueError(f"Unsupported currency: {self.currency}")

    def add(self, other: 'Money') -> 'Money':
        if self.currency != other.currency:
            raise ValueError("Cannot add different currencies")
        return Money(self.amount + other.amount, self.currency)

    def multiply(self, factor: Decimal) -> 'Money':
        return Money(self.amount * factor, self.currency)

# Value objects are interchangeable
money1 = Money(Decimal('10.00'), 'USD')
money2 = Money(Decimal('10.00'), 'USD')
assert money1 == money2  # Equal because values are equal
```

**Entities**: Defined by identity, mutable

```java
// Entity: Defined by ID, mutable
public class User {
    private final String id;  // Immutable identity
    private String name;      // Mutable attributes
    private String email;

    public User(String id, String name, String email) {
        this.id = Objects.requireNonNull(id, "User ID cannot be null");
        this.name = Objects.requireNonNull(name, "Name cannot be null");
        this.email = Objects.requireNonNull(email, "Email cannot be null");
    }

    public String getId() {
        return id;
    }

    public void setName(String name) {
        this.name = Objects.requireNonNull(name, "Name cannot be null");
    }

    public void setEmail(String email) {
        this.email = Objects.requireNonNull(email, "Email cannot be null");
    }

    @Override
    public boolean equals(Object obj) {
        if (this == obj) return true;
        if (!(obj instanceof User)) return false;
        User other = (User) obj;
        // Entities equal if IDs equal (not attributes)
        return id.equals(other.id);
    }

    @Override
    public int hashCode() {
        return id.hashCode();
    }
}

// Entities with same ID are equal even with different attributes
User user1 = new User("123", "Alice", "alice@example.com");
User user2 = new User("123", "Alice Updated", "newemail@example.com");
assert user1.equals(user2);  // Equal because same ID
```

## Data Abstraction (Clean Code)

### Objects vs Data Structures

**Data Structures**: Expose data, no behavior

```python
# Data structure: Exposes data
@dataclass
class Point:
    """Pure data structure."""
    x: float
    y: float

# Client code operates on the data
def calculate_distance(p1: Point, p2: Point) -> float:
    """Calculate distance between points."""
    dx = p1.x - p2.x
    dy = p1.y - p2.y
    return math.sqrt(dx * dx + dy * dy)

# Adding new operations is easy (just add new function)
def calculate_midpoint(p1: Point, p2: Point) -> Point:
    return Point((p1.x + p2.x) / 2, (p1.y + p2.y) / 2)

# But changing the data structure affects all operations
```

**Objects**: Hide data, expose behavior

```typescript
// Object: Hides data, exposes behavior
class Point {
    private x: number;
    private y: number;

    constructor(x: number, y: number) {
        this.x = x;
        this.y = y;
    }

    // Behavior encapsulated
    distanceTo(other: Point): number {
        const dx = this.x - other.x;
        const dy = this.y - other.y;
        return Math.sqrt(dx * dx + dy * dy);
    }

    midpointTo(other: Point): Point {
        return new Point(
            (this.x + other.x) / 2,
            (this.y + other.y) / 2
        );
    }
}

// Client code uses behavior, doesn't access data
const p1 = new Point(0, 0);
const p2 = new Point(3, 4);
const distance = p1.distanceTo(p2);  // Uses behavior

// Adding new operations requires modifying class
// But changing internal representation is easy
```

**The Anti-Symmetry**:
- Data structures make it easy to add new functions without changing existing data structures
- Objects make it easy to add new classes without changing existing functions

Choose based on what's more likely to change.

### Law of Demeter (Clean Code)

**Principle**: "Only talk to your immediate friends."

```java
// VIOLATION: Chain of calls (train wreck)
String city = user.getAddress().getCity().getName();
// Coupled to User, Address, City, and their relationships

// GOOD: Tell, don't ask
String city = user.getCityName();

// User class encapsulates the navigation
public class User {
    private Address address;

    public String getCityName() {
        // Encapsulate the chain
        return address != null ? address.getCityName() : "Unknown";
    }
}

public class Address {
    private City city;

    public String getCityName() {
        return city != null ? city.getName() : "Unknown";
    }
}
```

**Exception**: Data structures (DTOs) are okay to navigate

```typescript
// Data Transfer Object: Okay to access properties
interface UserDTO {
    name: string;
    address: {
        street: string;
        city: string;
        zip: string;
    };
}

// This is fine for DTOs
function formatAddress(dto: UserDTO): string {
    return `${dto.address.street}, ${dto.address.city} ${dto.address.zip}`;
}
```

## Specialized Data Structures

### Stacks: LIFO Operations

```python
# Stack: Last In, First Out
# Use when: Need to reverse order, track call stack, undo operations

class Stack:
    """Generic stack implementation."""

    def __init__(self):
        self._items = []

    def push(self, item):
        """Add item to top of stack."""
        self._items.append(item)

    def pop(self):
        """Remove and return top item."""
        if self.is_empty():
            raise IndexError("Cannot pop from empty stack")
        return self._items.pop()

    def peek(self):
        """View top item without removing."""
        if self.is_empty():
            raise IndexError("Cannot peek at empty stack")
        return self._items[-1]

    def is_empty(self) -> bool:
        return len(self._items) == 0

    def size(self) -> int:
        return len(self._items)

# Common use: Undo stack
class TextEditor:
    def __init__(self):
        self.text = ""
        self.undo_stack = Stack()

    def insert(self, content: str):
        self.undo_stack.push(self.text)  # Save current state
        self.text += content

    def undo(self):
        if not self.undo_stack.is_empty():
            self.text = self.undo_stack.pop()  # Restore previous state
```

### Queues: FIFO Operations

```java
// Queue: First In, First Out
// Use when: Need to process items in order, task scheduling, BFS

import java.util.LinkedList;
import java.util.Queue;

public class TaskProcessor {
    private Queue<Task> taskQueue = new LinkedList<>();

    public void enqueueTask(Task task) {
        taskQueue.offer(task);  // Add to back of queue
    }

    public void processNextTask() {
        if (taskQueue.isEmpty()) {
            throw new IllegalStateException("No tasks to process");
        }

        Task task = taskQueue.poll();  // Remove from front
        processTask(task);
    }

    public Task peekNextTask() {
        if (taskQueue.isEmpty()) {
            return null;
        }
        return taskQueue.peek();  // View without removing
    }

    public int getQueueSize() {
        return taskQueue.size();
    }
}

// Priority Queue: Items ordered by priority
import java.util.PriorityQueue;

public class PriorityTaskProcessor {
    private PriorityQueue<Task> priorityQueue = new PriorityQueue<>(
        (t1, t2) -> Integer.compare(t2.getPriority(), t1.getPriority())
    );

    public void enqueueTask(Task task) {
        priorityQueue.offer(task);
    }

    public Task getHighestPriorityTask() {
        return priorityQueue.poll();  // Gets highest priority item
    }
}
```

### Trees: Hierarchical Data

```typescript
// Binary Search Tree: Sorted hierarchical data
// Use when: Need sorted data, range queries, fast lookup

class TreeNode<T> {
    value: T;
    left: TreeNode<T> | null = null;
    right: TreeNode<T> | null = null;

    constructor(value: T) {
        this.value = value;
    }
}

class BinarySearchTree<T> {
    private root: TreeNode<T> | null = null;

    insert(value: T): void {
        this.root = this.insertNode(this.root, value);
    }

    private insertNode(node: TreeNode<T> | null, value: T): TreeNode<T> {
        if (node === null) {
            return new TreeNode(value);
        }

        if (value < node.value) {
            node.left = this.insertNode(node.left, value);
        } else if (value > node.value) {
            node.right = this.insertNode(node.right, value);
        }

        return node;
    }

    search(value: T): boolean {
        return this.searchNode(this.root, value);
    }

    private searchNode(node: TreeNode<T> | null, value: T): boolean {
        if (node === null) {
            return false;
        }

        if (value === node.value) {
            return true;
        }

        if (value < node.value) {
            return this.searchNode(node.left, value);
        } else {
            return this.searchNode(node.right, value);
        }
    }

    // In-order traversal: Returns sorted elements
    inOrder(): T[] {
        const result: T[] = [];
        this.inOrderTraversal(this.root, result);
        return result;
    }

    private inOrderTraversal(node: TreeNode<T> | null, result: T[]): void {
        if (node !== null) {
            this.inOrderTraversal(node.left, result);
            result.push(node.value);
            this.inOrderTraversal(node.right, result);
        }
    }
}
```

### Graphs: Network Relationships

```python
from typing import Dict, List, Set
from collections import deque

# Graph: Nodes and edges
# Use when: Modeling networks, social relationships, dependencies

class Graph:
    """Directed graph implementation."""

    def __init__(self):
        self._adjacency_list: Dict[str, List[str]] = {}

    def add_vertex(self, vertex: str) -> None:
        """Add a vertex to the graph."""
        if vertex not in self._adjacency_list:
            self._adjacency_list[vertex] = []

    def add_edge(self, from_vertex: str, to_vertex: str) -> None:
        """Add directed edge from one vertex to another."""
        # Defensive: Ensure vertices exist
        self.add_vertex(from_vertex)
        self.add_vertex(to_vertex)

        self._adjacency_list[from_vertex].append(to_vertex)

    def get_neighbors(self, vertex: str) -> List[str]:
        """Get all neighbors of a vertex."""
        if vertex not in self._adjacency_list:
            raise ValueError(f"Vertex not found: {vertex}")
        return self._adjacency_list[vertex].copy()

    def breadth_first_search(self, start: str) -> List[str]:
        """BFS traversal from start vertex."""
        if start not in self._adjacency_list:
            raise ValueError(f"Start vertex not found: {start}")

        visited: Set[str] = set()
        queue = deque([start])
        result = []

        while queue:
            vertex = queue.popleft()
            if vertex not in visited:
                visited.add(vertex)
                result.append(vertex)

                for neighbor in self._adjacency_list[vertex]:
                    if neighbor not in visited:
                        queue.append(neighbor)

        return result

    def has_path(self, from_vertex: str, to_vertex: str) -> bool:
        """Check if path exists from one vertex to another."""
        visited = set()
        queue = deque([from_vertex])

        while queue:
            vertex = queue.popleft()
            if vertex == to_vertex:
                return True

            if vertex not in visited:
                visited.add(vertex)
                for neighbor in self._adjacency_list.get(vertex, []):
                    queue.append(neighbor)

        return False

# Example: Dependency graph
dependencies = Graph()
dependencies.add_edge("auth", "database")
dependencies.add_edge("api", "auth")
dependencies.add_edge("api", "cache")
dependencies.add_edge("web", "api")

# Check if web depends on database (transitively)
has_dependency = dependencies.has_path("web", "database")  # True
```

## Immutability and Thread Safety

### Immutable Data Structures

```java
// Immutable class: Thread-safe by design
public final class Money {
    private final BigDecimal amount;
    private final String currency;

    public Money(BigDecimal amount, String currency) {
        this.amount = Objects.requireNonNull(amount);
        this.currency = Objects.requireNonNull(currency);
    }

    // No setters - immutable

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
        return new Money(
            this.amount.add(other.amount),
            this.currency
        );
    }

    public Money multiply(BigDecimal factor) {
        return new Money(
            this.amount.multiply(factor),
            this.currency
        );
    }

    @Override
    public boolean equals(Object obj) {
        if (this == obj) return true;
        if (!(obj instanceof Money)) return false;
        Money other = (Money) obj;
        return amount.equals(other.amount) &&
               currency.equals(other.currency);
    }

    @Override
    public int hashCode() {
        return Objects.hash(amount, currency);
    }
}
```

**Benefits of Immutability**:
- Thread-safe without synchronization
- Can be safely shared
- Can be used as map keys
- No defensive copying needed
- Easier to reason about

### Defensive Copying

```python
# Defensive copying for mutable data
class UserProfile:
    """User profile with defensive copying."""

    def __init__(self, name: str, roles: list[str]):
        self.name = name
        # Defensive copy: Don't store reference to mutable input
        self._roles = roles.copy()

    def get_roles(self) -> list[str]:
        # Defensive copy: Don't expose internal mutable state
        return self._roles.copy()

    def add_role(self, role: str) -> None:
        # Defensive: Validate
        if not role or not isinstance(role, str):
            raise ValueError("Role must be non-empty string")
        if role not in self._roles:
            self._roles.append(role)

# Safe usage
roles = ["user", "admin"]
profile = UserProfile("Alice", roles)

# Modifying original doesn't affect profile
roles.append("superadmin")  # profile not affected

# Modifying returned list doesn't affect profile
returned_roles = profile.get_roles()
returned_roles.append("hacker")  # profile not affected
```

## Practical Data Structure Checklist

### Choosing Data Structures
- [ ] Data structure matches access patterns (index, key, sequential)
- [ ] Time complexity acceptable for operations
- [ ] Memory overhead acceptable
- [ ] Mutability/immutability appropriate
- [ ] Thread safety considered

### Custom Types
- [ ] Complex data organized into types
- [ ] Validation encapsulated in type
- [ ] Type names reveal intent
- [ ] Value objects immutable
- [ ] Entities have clear identity

### Defensive Practices
- [ ] Bounds checking for arrays/collections
- [ ] Null/None handling explicit
- [ ] Defensive copying for mutable data
- [ ] Validation at construction
- [ ] Invariants enforced

### Performance
- [ ] No unnecessary copying
- [ ] Appropriate collection for size
- [ ] String building efficient
- [ ] Numeric types sized correctly
- [ ] Memory allocation patterns understood

## Summary: Data Structure Principles

1. **Choose Appropriately**: Match structure to access patterns and operations
2. **Encapsulate Complexity**: Hide data structure details behind clean interfaces
3. **Validate Early**: Validate data at construction/boundaries
4. **Be Immutable**: Prefer immutable data structures when possible
5. **Be Defensive**: Defensive copying for mutable data
6. **Custom Types**: Create types to make abstractions clear
7. **Law of Demeter**: Tell, don't ask; encapsulate navigation
8. **Right Tool**: Use specialized structures (stack, queue, tree) when appropriate
9. **Think Performance**: Understand time/space complexity
10. **Thread Safety**: Consider concurrent access patterns

## Further Reading

- **Code Complete 2** (Chapters 12-13: Data Types) - Steve McConnell
- **Clean Code** (Chapter 6: Objects and Data Structures) - Robert C. Martin
- **Domain-Driven Design** - Eric Evans (Value Objects and Entities)
- **Effective Java** - Joshua Bloch (Item 17: Minimize Mutability)
- **Data Structures and Algorithms** - Classic algorithms textbooks

---

**Remember**: Data structures are not just containers—they are the foundation of your program's organization and performance. Choose structures that match your access patterns, encapsulate complexity behind clear abstractions, validate data rigorously, and prefer immutability when possible. The right data structure makes algorithms obvious; the wrong data structure makes even simple operations painful.
