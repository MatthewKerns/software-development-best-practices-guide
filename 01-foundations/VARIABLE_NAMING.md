# Variable Naming: The Foundation of Readable Code

## Overview

Variable naming is the most fundamental and frequently performed act in programming. Every variable, function, class, and constant you create requires a name. Good names make code self-documenting and easier to understand; poor names create confusion and technical debt that compounds over time.

This comprehensive guide synthesizes naming wisdom from industry-leading sources and provides practical, actionable guidance for creating clear, intention-revealing names.

## Why Naming Matters

**"There are only two hard things in Computer Science: cache invalidation and naming things."** — Phil Karlton

Variable naming is hard because it requires:
- Understanding the problem domain deeply
- Choosing the right level of abstraction
- Predicting how others will read the code
- Balancing clarity with conciseness

### The Cost of Poor Names

Poor variable names create measurable costs:

**Comprehension Time**: Studies show that developers spend 60-70% of their time reading code vs. writing it. Unclear names directly impact this majority activity.

**Debugging Difficulty**: When variable names don't reveal their purpose, developers must mentally map meaningless identifiers to concepts, increasing cognitive load and bug introduction rate.

**Maintenance Cost**: Code with poor names requires constant reference to documentation or mental context reconstruction. The same code reviewed months later becomes unreadable even to its author.

**Onboarding Friction**: New team members struggle to understand codebases with unclear naming, extending onboarding time and reducing productivity.

### The Benefits of Good Names

Good names provide:
- **Self-documentation**: Code explains itself without comments
- **Fast comprehension**: Readers understand intent immediately
- **Reduced bugs**: Clear names make incorrect usage obvious
- **Easier refactoring**: Good names survive structural changes
- **Better design**: Struggling to name something often reveals design problems

## Source Materials

This guide synthesizes principles from:

- **Code Complete 2** by Steve McConnell (Chapter 11)
  - Optimal name length and structure
  - Names to avoid
  - Naming conventions by scope and purpose

- **Clean Code** by Robert C. Martin (Chapter 2)
  - Intention-revealing names
  - Avoiding disinformation
  - Meaningful distinctions

## Core Naming Principles

### 1. Use Intention-Revealing Names (Clean Code)

**Principle**: The name should tell you why it exists, what it does, and how it's used.

**Poor Examples:**
```python
# Python - What is 'd'? Days? Distance? Data?
d = 14

# What list? Of what?
list1 = get_items()

# Temp? Temporary what?
temp = calculate()
```

**Good Examples:**
```python
# Python - Clear intent and meaning
elapsed_days_since_creation = 14
active_user_accounts = get_items()
monthly_revenue_total = calculate()
```

```typescript
// TypeScript - Intention-revealing names
const elapsedDaysSinceCreation: number = 14;
const activeUserAccounts: Account[] = getItems();
const monthlyRevenueTotal: number = calculate();
```

```java
// Java - Clear purpose and usage
int elapsedDaysSinceCreation = 14;
List<Account> activeUserAccounts = getItems();
BigDecimal monthlyRevenueTotal = calculate();
```

**Key Insight**: If a name requires a comment to explain it, the name does not reveal its intent.

### 2. Avoid Disinformation (Clean Code)

**Principle**: Don't leave false clues that obscure meaning. Avoid names that vary in small ways or mean something else in the programming context.

**Poor Examples:**
```python
# Calling something a 'list' when it's not
account_list = {}  # This is a dict, not a list!

# Similar names with different meanings
user_accounts_for_processing = get_active()
user_account_for_processing = get_single()  # Easy to confuse

# Platform-specific names
hp = 100  # Does 'hp' mean Hewlett-Packard? Hit Points? Horsepower?
```

**Good Examples:**
```python
# Accurate type description
account_registry = {}  # or active_accounts_dict
accounts_awaiting_verification = get_active()
single_account_for_review = get_single()
player_hit_points = 100
```

```typescript
// TypeScript - Type-accurate names
const accountRegistry: Record<string, Account> = {};
const accountsAwaitingVerification: Account[] = getActive();
const singleAccountForReview: Account = getSingle();
const playerHitPoints: number = 100;
```

**Key Insight**: Variable names create expectations. Violating those expectations creates bugs.

### 3. Make Meaningful Distinctions (Clean Code)

**Principle**: If names must differ, make sure they differ meaningfully. Avoid number series, noise words, and non-informative distinctions.

**Poor Examples:**
```python
# Number series tells nothing
data1 = fetch_from_api()
data2 = fetch_from_cache()

# Noise words don't distinguish
user_info = get_user()
user_data = get_details()
user_object = create_new()  # 'object' adds nothing
```

**Good Examples:**
```python
# Meaningful distinctions
api_response_data = fetch_from_api()
cached_user_data = fetch_from_cache()

# Clear differentiation
user_profile = get_user()
user_purchase_history = get_details()
newly_created_user = create_new()
```

```java
// Java - Meaningful distinctions
ApiResponse apiResponseData = fetchFromApi();
CachedData cachedUserData = fetchFromCache();

UserProfile userProfile = getUser();
PurchaseHistory userPurchaseHistory = getDetails();
User newlyCreatedUser = createNew();
```

**Key Insight**: Distinguish names in ways that inform the reader about meaningful differences.

### 4. Use Pronounceable Names (Clean Code)

**Principle**: Programming is a social activity. You will discuss code with others. Make names pronounceable to enable conversation.

**Poor Examples:**
```python
# Unpronounceable abbreviations
gen_ymdhms = datetime.now()  # "gen why em dee aitch em ess"
drc_fn = process_records      # "dee are see eff en"
```

**Good Examples:**
```python
# Easily pronounced
generation_timestamp = datetime.now()
directory_file_name = process_records
```

```typescript
// TypeScript - Pronounceable names
const generationTimestamp: Date = new Date();
const directoryFileName: string = processRecords();
```

**Why it matters**:
- "Hey, look at this generation timestamp anomaly..."
- vs. "Hey, look at this gen why em dee aitch em ess anomaly..."

### 5. Use Searchable Names (Clean Code)

**Principle**: Single-letter names and numeric constants are hard to locate across a codebase. Names should be easy to grep/search for.

**Poor Examples:**
```python
# Single letter - impossible to search meaningfully
for e in events:
    if e > 5:  # What is 5? What is e?
        process(e * 7)  # What is 7?
```

**Good Examples:**
```python
# Searchable names with clear meaning
MAX_RETRY_ATTEMPTS = 5
MILLISECONDS_PER_DAY = 86400000

for event_duration in event_durations:
    if event_duration > MAX_RETRY_ATTEMPTS:
        process(event_duration * MILLISECONDS_PER_DAY)
```

```java
// Java - Searchable constants and variables
private static final int MAX_RETRY_ATTEMPTS = 5;
private static final long MILLISECONDS_PER_DAY = 86400000L;

for (int eventDuration : eventDurations) {
    if (eventDuration > MAX_RETRY_ATTEMPTS) {
        process(eventDuration * MILLISECONDS_PER_DAY);
    }
}
```

**Key Insight**: The length of a name should correspond to the size of its scope (more on this below).

### 6. Avoid Encodings (Clean Code)

**Principle**: Modern IDEs provide type information. Don't encode type or scope in names (Hungarian notation, member prefixes).

**Poor Examples:**
```python
# Hungarian notation (type prefixes)
str_username = "john_doe"
int_count = 42
lst_accounts = []

# Member prefixes
class User:
    def __init__(self):
        self.m_name = ""  # 'm_' prefix is noise
        self._private_data = {}  # Exception: _ for private is conventional
```

**Good Examples:**
```python
# Clean names without type encoding
username = "john_doe"
count = 42
accounts = []

class User:
    def __init__(self):
        self.name = ""
        self._private_data = {}  # Conventional Python private indicator
```

```typescript
// TypeScript - Types handled by type system
const username: string = "john_doe";
const count: number = 42;
const accounts: Account[] = [];

class User {
    name: string;  // Type is explicit in declaration
    private privateData: Record<string, any>;
}
```

**Exception**: Some language conventions (like Python's `_private`) are acceptable because they're idiomatic.

### 7. Avoid Mental Mapping (Clean Code)

**Principle**: Readers shouldn't have to mentally translate your names into concepts they know. Clarity is king.

**Poor Examples:**
```python
# Single letter requires mental mapping
for i in range(len(accounts)):
    a = accounts[i]
    # Now 'a' must be mentally mapped to "account"
    process(a)

# Cryptic abbreviations
r = http_request()  # request? response? result?
```

**Good Examples:**
```python
# No translation required
for account in accounts:
    process(account)

# Clear, explicit names
http_response = make_http_request()
```

**Acceptable Exception**: Loop counters `i`, `j`, `k` are acceptable in very short loops (3-5 lines) when the scope is tiny and tradition makes them clear:

```python
# Acceptable: very short, traditional usage
for i in range(10):
    print(i)

# Better for longer loops
for user_index in range(len(users)):
    user = users[user_index]
    # ... many lines ...
```

## Optimal Name Length (Code Complete 2)

### Research-Based Guidelines

Studies on comprehension and debugging show optimal name lengths:

- **Sweet Spot: 10-16 characters** (highest comprehension, fewest bugs)
- **Acceptable: 8-20 characters**
- **Too Short: < 8 characters** (often ambiguous)
- **Too Long: > 20 characters** (hard to read and type)

### Name Length by Scope (Code Complete 2)

**Principle**: Name length should be proportional to scope.

**Short Scope → Short Names:**
```python
# Loop variables in tight scopes
for i in range(5):
    print(i)  # 3 lines total, 'i' is fine

# Small function locals
def calculate_total(items):
    sum = 0  # Short name, short scope
    for item in items:
        sum += item.price
    return sum
```

**Medium Scope → Medium Names:**
```python
# Function parameters
def process_user_account(account_id, user_role):
    # Medium scope, medium names
    pass

# Class members
class OrderProcessor:
    def __init__(self):
        self.pending_orders = []
        self.processed_count = 0
```

**Long Scope → Long Names:**
```python
# Module-level constants
DEFAULT_CONNECTION_TIMEOUT_SECONDS = 30
MAXIMUM_RETRY_ATTEMPTS_BEFORE_FAILURE = 3

# Global configuration
APPLICATION_WIDE_SECURITY_SETTINGS = {
    'encryption_enabled': True
}
```

### When to Use Longer Names (Code Complete 2)

Use longer, more descriptive names when:
- The variable is used across many lines
- Multiple similar variables exist
- The purpose isn't obvious from context
- The variable is global or module-level

Use shorter names when:
- The scope is 3-5 lines
- Context makes purpose obvious
- It's a well-known abbreviation (like `i` for loop index)

## Names to Avoid (Code Complete 2)

### Single-Letter Names

**Avoid except in tiny scopes:**
```python
# Too cryptic
def calculate(a, b, c):
    return a * b + c

# Clear intent
def calculate_compound_interest(principal, rate, time):
    return principal * rate + time
```

**Acceptable single letters:**
- `i`, `j`, `k` for loop counters (3-5 line scope)
- `x`, `y`, `z` for coordinates (mathematical context)
- `e` for exceptions in catch blocks (convention)

### Ambiguous Abbreviations

**Avoid:**
```python
# What do these mean?
temp_val = compute()  # Temperature? Temporary?
proc_rec = process()  # Process record? Procedure?
num = count()         # Number of what?
```

**Use full words:**
```python
temporary_calculation = compute()
processed_records = process()
user_count = count()
```

### Misleading Names

**Avoid names that suggest the wrong thing:**
```python
# 'List' suggests a list data type
account_list = {}  # Actually a dictionary!

# 'Manager' usually implies lifecycle management
data_manager = fetch_data()  # Actually just fetches, doesn't manage

# 'Controller' suggests MVC pattern
data_controller = {"key": "value"}  # Actually just a dict
```

**Use accurate names:**
```python
account_registry = {}
fetched_user_data = fetch_data()
configuration_map = {"key": "value"}
```

## Naming Conventions by Variable Type

### Boolean Variables

**Pattern**: Use predicate phrases (is, has, can, should)

```python
# Python - Boolean naming
is_valid = check_validity()
has_permission = verify_access()
can_edit = check_edit_rights()
should_retry = evaluate_retry_condition()

# Avoid negative booleans - they're confusing
not_valid = check()  # Avoid: if not not_valid is confusing
is_invalid = check()  # Better, but 'is_valid' is clearer
```

```typescript
// TypeScript - Boolean predicates
const isValid: boolean = checkValidity();
const hasPermission: boolean = verifyAccess();
const canEdit: boolean = checkEditRights();
const shouldRetry: boolean = evaluateRetryCondition();
```

```java
// Java - Boolean naming conventions
boolean isValid = checkValidity();
boolean hasPermission = verifyAccess();
boolean canEdit = checkEditRights();
boolean shouldRetry = evaluateRetryCondition();
```

**Anti-pattern:**
```python
# Avoid: Not clearly boolean
status = True  # status of what?
flag = False   # what flag?
```

### Collection Variables

**Pattern**: Use plural nouns or collective nouns

```python
# Python - Collection naming
users = fetch_all_users()
active_accounts = get_active()
pending_orders = query_pending()

# Use collective nouns when appropriate
user_registry = {}
account_pool = set()
task_queue = deque()
```

```typescript
// TypeScript - Strongly typed collections
const users: User[] = fetchAllUsers();
const activeAccounts: Account[] = getActive();
const pendingOrders: Order[] = queryPending();

// Maps and Sets with descriptive names
const userRegistry: Map<string, User> = new Map();
const accountPool: Set<Account> = new Set();
```

```java
// Java - Generic type collections
List<User> users = fetchAllUsers();
Set<Account> activeAccounts = getActive();
Queue<Order> pendingOrders = queryPending();

Map<String, User> userRegistry = new HashMap<>();
```

**Anti-pattern:**
```python
# Singular name for collection
user = fetch_all_users()  # Confusing: implies single user

# Generic names
list1 = get_data()  # What list?
array = fetch()     # Array of what?
```

### Counters and Accumulators

**Pattern**: Use meaningful names with `count`, `total`, `sum`, `index`, etc.

```python
# Python - Counter naming
user_count = len(users)
total_revenue = sum(sales)
running_total = 0
active_session_count = count_sessions()

# Index variables
current_index = 0
start_index = find_start()
end_index = find_end()
```

```typescript
// TypeScript - Counters and accumulators
let userCount: number = users.length;
let totalRevenue: number = sales.reduce((sum, sale) => sum + sale, 0);
let runningTotal: number = 0;
let activeSessionCount: number = countSessions();
```

**Common Qualifiers:**
- `count`: Number of items
- `total`: Sum of values
- `sum`: Mathematical sum
- `average` / `avg`: Mean value
- `max` / `min`: Maximum/minimum
- `index`: Position in collection

### Computed Values (Code Complete 2)

**Pattern**: Place qualifiers at the end for consistency

```python
# Python - Computed value qualifiers
revenue_total = calculate_revenue()  # Not total_revenue
salary_average = compute_average()   # Not average_salary
price_max = find_maximum()           # Not max_price
count_min = get_minimum()            # Not min_count

# Common patterns
current_index = 0
previous_value = None
next_element = get_next()
```

**Why qualifiers at the end?** It groups related variables:
```python
# Easy to see all revenue-related variables
revenue_total = 0
revenue_average = 0
revenue_max = 0
revenue_min = 0

# Harder to see the relationship
total_revenue = 0
average_revenue = 0
max_revenue = 0
min_revenue = 0
```

### Constants

**Pattern**: Use SCREAMING_SNAKE_CASE for true constants

```python
# Python - Constant naming
MAX_CONNECTIONS = 100
DEFAULT_TIMEOUT_SECONDS = 30
API_BASE_URL = "https://api.example.com"
SECONDS_PER_DAY = 86400

# Configuration "constants" (set once, never changed)
DATABASE_CONNECTION_STRING = os.getenv("DB_URL")
```

```typescript
// TypeScript - Constants
const MAX_CONNECTIONS: number = 100;
const DEFAULT_TIMEOUT_SECONDS: number = 30;
const API_BASE_URL: string = "https://api.example.com";
const SECONDS_PER_DAY: number = 86400;
```

```java
// Java - Final constants
public static final int MAX_CONNECTIONS = 100;
public static final int DEFAULT_TIMEOUT_SECONDS = 30;
public static final String API_BASE_URL = "https://api.example.com";
public static final long SECONDS_PER_DAY = 86400L;
```

### Temporary Variables

**Anti-pattern**: Using `temp`, `tmp`, `t`

```python
# Poor: Generic temp names
temp = calculate()
tmp = fetch_data()
t = transform()
```

**Better**: Describe what the temporary holds

```python
# Good: Descriptive temporary names
intermediate_calculation = compute_step_one()
cached_api_response = fetch_data()
transformed_user_data = transform()
```

**Acceptable exception**: Very short scopes where purpose is obvious:
```python
# Acceptable: 2-3 line swap
temp = a
a = b
b = temp
```

## Class and Function Naming

### Class Names (Clean Code)

**Pattern**: Nouns and noun phrases

```python
# Python - Class naming
class UserAccount:
    pass

class OrderProcessor:
    pass

class PaymentGateway:
    pass

class InvoiceLineItem:
    pass
```

```typescript
// TypeScript - Class naming
class UserAccount {
    // ...
}

class OrderProcessor {
    // ...
}

class PaymentGateway {
    // ...
}
```

```java
// Java - Class naming
public class UserAccount {
    // ...
}

public class OrderProcessor {
    // ...
}

public class PaymentGateway {
    // ...
}
```

**Avoid**: Manager, Data, Info, Processor (when too generic)
**Better**: Be specific about what the class manages or processes

```python
# Generic
class DataManager:  # Manages what data?
    pass

# Specific
class UserAccountManager:  # Clear responsibility
    pass

class CustomerDatabaseManager:  # Clear domain
    pass
```

### Method/Function Names (Clean Code)

**Pattern**: Verbs and verb phrases

```python
# Python - Function naming
def calculate_total_revenue():
    pass

def validate_user_credentials(username, password):
    pass

def send_email_notification(recipient, message):
    pass

def is_valid_email(email):  # Boolean-returning functions use 'is'
    pass
```

```typescript
// TypeScript - Method naming
function calculateTotalRevenue(): number {
    // ...
}

function validateUserCredentials(username: string, password: string): boolean {
    // ...
}

function sendEmailNotification(recipient: string, message: string): void {
    // ...
}

function isValidEmail(email: string): boolean {
    // ...
}
```

```java
// Java - Method naming
public BigDecimal calculateTotalRevenue() {
    // ...
}

public boolean validateUserCredentials(String username, String password) {
    // ...
}

public void sendEmailNotification(String recipient, String message) {
    // ...
}

public boolean isValidEmail(String email) {
    // ...
}
```

**Accessors, mutators, and predicates:**
```python
# Python - Property naming
class User:
    def __init__(self):
        self._email = ""

    @property
    def email(self):  # Accessor: noun
        return self._email

    @email.setter
    def email(self, value):  # Mutator: noun
        self._email = value

    def has_valid_subscription(self):  # Predicate: has/is/can
        return self._subscription_active
```

## Common Naming Opposites (Code Complete 2)

Use consistent opposites throughout your codebase:

| Use These Pairs | Not These |
|----------------|-----------|
| begin / end | start / stop |
| first / last | top / bottom |
| min / max | minimum / maximum |
| source / destination | from / to |
| up / down | increase / decrease |
| get / set | retrieve / assign |
| add / remove | insert / delete |
| create / destroy | new / kill |
| open / close | open / shut |
| show / hide | display / conceal |
| source / target | origin / destination |

**Example consistency:**
```python
# Consistent opposites
def get_user_name():
    pass

def set_user_name(name):
    pass

# Inconsistent - avoid
def get_user_name():
    pass

def assign_user_name(name):  # Should be 'set_user_name'
    pass
```

## Domain-Specific Naming

### Use Solution Domain Names (Clean Code)

When the concept is primarily technical, use CS/engineering terms:

```python
# Solution domain names (technical concepts)
job_queue = deque()
visitor_pattern = VisitorPattern()
factory_method = FactoryMethod()
account_repository = AccountRepository()
```

**Readers are programmers**: They know algorithms, patterns, math terms, and CS concepts. Using these terms is appropriate.

### Use Problem Domain Names (Clean Code)

When the concept is from the business domain, use domain language:

```python
# Problem domain names (business concepts)
policy_holder = get_customer()
premium_amount = calculate_insurance()
claim_adjuster = assign_adjuster()
underwriting_decision = evaluate_risk()
```

**When in doubt**: Ask a domain expert what they call it. Code should speak the language of the domain.

### Context Matters

```python
# Financial domain
principal = 100000  # Loan principal
interest_rate = 0.05
amortization_schedule = calculate()

# Physics simulation
mass = 10.0
acceleration = 9.8
velocity_vector = calculate()

# E-commerce
shopping_cart = []
checkout_total = 0.0
fulfillment_status = "pending"
```

## Adding Meaningful Context

### Context Through Naming

**Poor**: Names without context
```python
# What are these?
street = "123 Main St"
city = "Springfield"
state = "IL"
zipcode = "62701"
```

**Better**: Context in variable names
```python
# Clear: These are address components
address_street = "123 Main St"
address_city = "Springfield"
address_state = "IL"
address_zipcode = "62701"
```

**Best**: Context through structure
```python
class Address:
    def __init__(self):
        self.street = "123 Main St"
        self.city = "Springfield"
        self.state = "IL"
        self.zipcode = "62701"

# Usage
user_address = Address()
billing_address = Address()
```

### Don't Add Gratuitous Context

**Anti-pattern**: Prefixing everything with system/module name

```python
# Too much context
class GasStationDeluxeAccountInfo:  # "GasStationDeluxe" prefix everywhere
    pass

class GasStationDeluxeAddress:
    pass

# Better: Let namespaces provide context
# In gas_station_deluxe module:
class AccountInfo:  # Module provides context
    pass

class Address:
    pass
```

## Practical Naming Checklist

Use this checklist when creating or reviewing names:

### Before Naming
- [ ] I understand what this variable represents
- [ ] I understand the scope and lifetime
- [ ] I know the domain context (technical or business)

### Intention and Clarity
- [ ] Name reveals intent without needing a comment
- [ ] Name would be clear to someone unfamiliar with this code
- [ ] Name doesn't require mental translation
- [ ] Name is pronounceable

### Accuracy and Precision
- [ ] Name accurately describes the content/purpose
- [ ] Name doesn't mislead about type or structure
- [ ] Name makes meaningful distinctions from similar variables
- [ ] Name uses correct domain terminology

### Length and Scope
- [ ] Length is appropriate for scope (short scope → short name)
- [ ] Length is 10-16 characters for most variables (ideal range)
- [ ] Name isn't unnecessarily abbreviated
- [ ] Name isn't unnecessarily long

### Consistency
- [ ] Name follows team/project conventions
- [ ] Name uses consistent opposites (begin/end, not begin/stop)
- [ ] Name matches similar variables in style
- [ ] Name uses established patterns (is/has for booleans, etc.)

### Searchability and Maintainability
- [ ] Name is searchable (not a single letter unless tiny scope)
- [ ] Name doesn't use encodings (no Hungarian notation)
- [ ] Name will survive refactoring
- [ ] Name makes code more self-documenting

## Common Anti-Patterns and Fixes

### Anti-Pattern: Vague Nouns

```python
# Anti-pattern
data = fetch()
info = get_details()
manager = create_thing()
processor = make_processor()

# Fix: Be specific
user_profile_data = fetch()
account_billing_info = get_details()
database_connection_manager = create_thing()
payment_transaction_processor = make_processor()
```

### Anti-Pattern: Abbreviations

```python
# Anti-pattern
usrAcct = get_usr()
ctxt = fetch_ctx()
conn = get_db_conn()

# Fix: Spell it out
user_account = get_user()
context = fetch_context()
database_connection = get_database_connection()
```

### Anti-Pattern: Inconsistent Naming

```python
# Anti-pattern: Mixing styles
def getUserName():  # camelCase
    pass

def get_user_email():  # snake_case
    pass

def FetchUserAddress():  # PascalCase
    pass

# Fix: Choose one convention
def get_user_name():  # Consistent snake_case
    pass

def get_user_email():
    pass

def get_user_address():
    pass
```

### Anti-Pattern: Encoding Type

```python
# Anti-pattern: Hungarian notation
str_name = "John"
int_age = 30
list_accounts = []

# Fix: Let the type system handle it
name = "John"
age = 30
accounts = []
```

### Anti-Pattern: Redundant Context

```python
# Anti-pattern: Within User class
class User:
    def __init__(self):
        self.user_name = ""  # 'user_' prefix is redundant
        self.user_email = ""
        self.user_age = 0

# Fix: Context is clear from class
class User:
    def __init__(self):
        self.name = ""  # Clear from context
        self.email = ""
        self.age = 0
```

### Anti-Pattern: Misleading Names

```python
# Anti-pattern: Name implies wrong thing
def get_accounts():
    # Actually creates accounts, doesn't just fetch
    return create_new_accounts()

# Fix: Name matches behavior
def create_default_accounts():
    return create_new_accounts()
```

## Language-Specific Conventions

### Python
- **Variables/functions**: `snake_case`
- **Classes**: `PascalCase`
- **Constants**: `SCREAMING_SNAKE_CASE`
- **Private**: Prefix with `_` (single underscore)
- **Very private**: Prefix with `__` (double underscore, name mangling)

```python
# Python conventions
user_account = UserAccount()
MAX_CONNECTIONS = 100

class PaymentProcessor:
    def __init__(self):
        self.public_attribute = "visible"
        self._internal_cache = {}
        self.__very_private = "mangled"
```

### TypeScript/JavaScript
- **Variables/functions**: `camelCase`
- **Classes**: `PascalCase`
- **Constants**: `SCREAMING_SNAKE_CASE` or `camelCase`
- **Private**: Prefix with `#` (TC39 private fields) or `_` (convention)

```typescript
// TypeScript conventions
const userAccount = new UserAccount();
const MAX_CONNECTIONS = 100;

class PaymentProcessor {
    publicAttribute: string = "visible";
    #privateField: string = "truly private";
    _internalCache: Map<string, any> = new Map();
}
```

### Java
- **Variables/methods**: `camelCase`
- **Classes**: `PascalCase`
- **Constants**: `SCREAMING_SNAKE_CASE`
- **Packages**: `lowercase`

```java
// Java conventions
UserAccount userAccount = new UserAccount();
public static final int MAX_CONNECTIONS = 100;

public class PaymentProcessor {
    private String internalCache;
    public String publicAttribute;
}
```

## Summary: The Naming Hierarchy

From most important to least:

1. **Clarity**: Name must be understandable
2. **Accuracy**: Name must be truthful
3. **Searchability**: Name must be findable
4. **Consistency**: Name must match conventions
5. **Conciseness**: Name should be as short as possible *after* meeting above criteria

**Remember**: Code is read far more than it's written. Invest time in names.

## Further Reading

- **Code Complete 2**, Chapter 11: "The Power of Variable Names"
- **Clean Code**, Chapter 2: "Meaningful Names"
- **The Art of Readable Code** by Boswell & Foucher
- **Implementation Patterns** by Kent Beck

## Quick Reference

See [VARIABLE_NAMING_CHECKLIST.md](../99-reference/VARIABLE_NAMING_CHECKLIST.md) for a condensed, actionable checklist to use during development and code review.

---

**Remember**: Good naming is an investment that pays dividends every time the code is read. Take the extra minute to choose the right name—your future self and your teammates will thank you.
