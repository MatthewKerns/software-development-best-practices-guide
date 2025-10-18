# Refactoring Catalog: Techniques for Code Improvement

## Overview

Refactoring is the process of changing a software system in such a way that it does not alter the external behavior of the code yet improves its internal structure. It is a disciplined way to clean up code that minimizes the chances of introducing bugs.

This comprehensive catalog provides concrete techniques for improving code structure. Each refactoring is a small, behavior-preserving transformation. By composing these small changes, you can make significant improvements to code quality without the risk of large-scale rewrites.

Think of these refactorings as your toolbox - when you identify a code smell, you select the appropriate tool to fix it. Just as a carpenter doesn't rebuild an entire house to fix a squeaky door, you don't rewrite entire systems to improve structure.

## Why a Refactoring Catalog Matters

### The Power of Named Refactorings

Having a catalog of named refactorings provides:

**Shared Vocabulary**: Instead of "make that code better," you can say "extract that into a method" or "replace those conditionals with polymorphism." Precision improves communication.

**Proven Techniques**: These refactorings have been tested by thousands of developers. You're not inventing solutions - you're applying established patterns.

**Composite Transformations**: Complex improvements decompose into sequences of simple, safe refactorings. Each step is small and verifiable.

**Risk Reduction**: Small, named transformations are less error-prone than ad-hoc restructuring.

**Tool Support**: IDEs implement automated refactorings. Knowing the names helps you find and use these tools.

### The Refactoring Process

Every refactoring follows this pattern:

1. **Identify the smell**: Recognize what's wrong
2. **Select the refactoring**: Choose the appropriate technique
3. **Ensure tests exist**: Have safety net in place
4. **Apply transformation**: Make the small change
5. **Run tests**: Verify behavior preserved
6. **Commit**: Save the working state
7. **Repeat**: Apply next refactoring if needed

## Source Materials

This catalog synthesizes techniques from:

- **Refactoring** by Martin Fowler
  - Comprehensive refactoring catalog
  - Mechanics for each refactoring
  - Code smell to refactoring mappings

- **Clean Code** by Robert C. Martin
  - Refactoring principles
  - Before/after examples
  - Integration with clean code practices

- **Code Complete 2** by Steve McConnell
  - Safe refactoring strategies
  - When to refactor vs. rewrite
  - Refactoring in practice

## Composing Methods

These refactorings help you improve method structure and decomposition.

### Extract Method

**Problem**: You have a code fragment that can be grouped together.

**Solution**: Turn the fragment into a method whose name explains the purpose.

**Motivation**: Short, well-named methods are easier to understand, test, and reuse. They reduce duplication and improve abstraction.

**Before:**
```python
def print_invoice(invoice):
    print_header()

    # Print line items
    print("Line Items:")
    total = 0
    for item in invoice.items:
        amount = item.quantity * item.price
        total += amount
        print(f"  {item.name}: {item.quantity} x ${item.price} = ${amount}")

    # Print footer with total
    print("-" * 40)
    print(f"Total: ${total}")
```

**After:**
```python
def print_invoice(invoice):
    print_header()
    print_line_items(invoice.items)
    print_total(invoice.items)

def print_line_items(items):
    print("Line Items:")
    for item in items:
        amount = calculate_line_item_amount(item)
        print(f"  {item.name}: {item.quantity} x ${item.price} = ${amount}")

def print_total(items):
    total = calculate_total_amount(items)
    print("-" * 40)
    print(f"Total: ${total}")

def calculate_line_item_amount(item):
    return item.quantity * item.price

def calculate_total_amount(items):
    return sum(calculate_line_item_amount(item) for item in items)
```

**Mechanics:**
1. Create new method with intention-revealing name
2. Copy extracted code to new method
3. Look for local variables and parameters needed
4. Replace extracted code with call to new method
5. Test

**When to Use**:
- Method is too long (>20-30 lines)
- Code needs a comment to explain what it does
- Same logic appears in multiple places

### Inline Method

**Problem**: Method body is as clear as its name.

**Solution**: Replace calls to method with method body and remove method.

**Motivation**: Sometimes indirection doesn't add value. When method body is as obvious as the name, eliminate the needless indirection.

**Before:**
```typescript
class ProductRating {
  getRating(): number {
    return this.moreThanFiveReviews() ? 2 : 1;
  }

  private moreThanFiveReviews(): boolean {
    return this.numberOfReviews > 5;
  }
}
```

**After:**
```typescript
class ProductRating {
  getRating(): number {
    return this.numberOfReviews > 5 ? 2 : 1;
  }
}
```

**Mechanics:**
1. Check method isn't polymorphic
2. Find all calls to method
3. Replace each call with method body
4. Remove method definition
5. Test

**When to Use**:
- Method body is as clear as the name
- Group of methods are badly factored
- Too much indirection making code hard to read

### Replace Temp with Query

**Problem**: Temporary variable holds the result of an expression.

**Solution**: Extract expression into method and replace all references to temp with method call.

**Motivation**: Temporary variables are often problematic - they're local and encourage long methods. Replacing with query methods enables sharing and improves testability.

**Before:**
```java
public double calculateTotal() {
    double basePrice = quantity * itemPrice;
    if (basePrice > 1000) {
        return basePrice * 0.95;
    } else {
        return basePrice * 0.98;
    }
}
```

**After:**
```java
public double calculateTotal() {
    if (getBasePrice() > 1000) {
        return getBasePrice() * 0.95;
    } else {
        return getBasePrice() * 0.98;
    }
}

private double getBasePrice() {
    return quantity * itemPrice;
}
```

**Mechanics:**
1. Find temp that's assigned once
2. Extract right-hand side into method
3. Replace all temp references with method call
4. Remove temp declaration
5. Test

**When to Use**:
- Temp is assigned once and expression is simple
- Want to extract part of a longer method
- Need to share calculation logic

### Split Temporary Variable

**Problem**: Temporary variable is assigned to more than once (and it's not a loop variable).

**Solution**: Make a separate temporary variable for each assignment.

**Motivation**: Variables should have one responsibility. Multiple assignments indicate the variable is doing multiple jobs.

**Before:**
```python
def calculate_distance(scenario):
    temp = 2 * (height + width)
    print(f"Perimeter: {temp}")
    temp = height * width
    print(f"Area: {temp}")
```

**After:**
```python
def calculate_distance(scenario):
    perimeter = 2 * (height + width)
    print(f"Perimeter: {perimeter}")

    area = height * width
    print(f"Area: {area}")
```

**Mechanics:**
1. Change name of temp at first assignment
2. Change all references up to next assignment
3. Repeat for each assignment
4. Test after each rename

**When to Use**:
- Variable is assigned multiple times
- Each assignment represents different purpose
- Variable name doesn't describe all uses

### Remove Assignments to Parameters

**Problem**: Code assigns a value to a parameter.

**Solution**: Use a temporary variable instead.

**Motivation**: Assigning to parameters reduces clarity and can cause confusion with pass-by-value vs. pass-by-reference semantics.

**Before:**
```typescript
function discount(inputValue: number, quantity: number): number {
  if (inputValue > 50) {
    inputValue = inputValue * 0.95;
  }
  if (quantity > 100) {
    inputValue = inputValue * 0.90;
  }
  return inputValue;
}
```

**After:**
```typescript
function discount(inputValue: number, quantity: number): number {
  let result = inputValue;

  if (inputValue > 50) {
    result = result * 0.95;
  }
  if (quantity > 100) {
    result = result * 0.90;
  }

  return result;
}
```

**Mechanics:**
1. Create temp variable for parameter
2. Replace parameter assignments with temp assignments
3. Change parameter references to temp references
4. Test

**When to Use**:
- Parameters are being modified
- Want to clarify that parameters are input-only
- Language uses pass-by-reference

## Moving Features Between Objects

These refactorings help you move functionality to the right place.

### Move Method

**Problem**: Method is used more by another class than the class it's defined in.

**Solution**: Create a new method in the class that uses it most, and move code there.

**Motivation**: Methods should be in the class that has the data they primarily work with. Moving methods reduces coupling and improves cohesion.

**Before:**
```java
class Account {
    private AccountType type;
    private int daysOverdrawn;

    public double overdraftCharge() {
        if (type.isPremium()) {
            double result = 10;
            if (daysOverdrawn > 7) {
                result += (daysOverdrawn - 7) * 0.85;
            }
            return result;
        } else {
            return daysOverdrawn * 1.75;
        }
    }
}

class AccountType {
    public boolean isPremium() {
        // ...
    }
}
```

**After:**
```java
class Account {
    private AccountType type;
    private int daysOverdrawn;

    public double overdraftCharge() {
        return type.overdraftCharge(daysOverdrawn);
    }
}

class AccountType {
    public boolean isPremium() {
        // ...
    }

    public double overdraftCharge(int daysOverdrawn) {
        if (isPremium()) {
            double result = 10;
            if (daysOverdrawn > 7) {
                result += (daysOverdrawn - 7) * 0.85;
            }
            return result;
        } else {
            return daysOverdrawn * 1.75;
        }
    }
}
```

**Mechanics:**
1. Examine features used by method in source class
2. Check for polymorphic calls to method
3. Create method in target class
4. Copy code and adjust to fit target
5. Replace source method with delegation
6. Test
7. Optionally remove source method if only delegating

**When to Use**:
- Method uses features of another class more than its own
- Future changes will be easier with method in different class
- Want to reduce coupling

### Extract Class

**Problem**: One class is doing work that should be done by two.

**Solution**: Create new class and move relevant fields and methods into it.

**Motivation**: Classes grow over time. When a class has too many responsibilities, extract some into a new class.

**Before:**
```python
class Person:
    def __init__(self):
        self.name = ""
        self.office_area_code = ""
        self.office_number = ""

    def get_telephone_number(self):
        return f"({self.office_area_code}) {self.office_number}"
```

**After:**
```python
class Person:
    def __init__(self):
        self.name = ""
        self.office_telephone = TelephoneNumber()

    def get_telephone_number(self):
        return self.office_telephone.get_telephone_number()

class TelephoneNumber:
    def __init__(self):
        self.area_code = ""
        self.number = ""

    def get_telephone_number(self):
        return f"({self.area_code}) {self.number}"
```

**Mechanics:**
1. Decide how to split responsibilities
2. Create new class for split-off responsibility
3. Link old to new class
4. Move fields from old to new
5. Move methods from old to new
6. Review interfaces of both classes
7. Test

**When to Use**:
- Class has subset of features that belong together
- Subset of data goes together
- Subset of methods go together
- Class is too large

### Inline Class

**Problem**: Class isn't doing very much.

**Solution**: Move all its features into another class and delete it.

**Motivation**: Sometimes after refactoring, a class is left with little responsibility. Merge it into another class.

**Before:**
```typescript
class Person {
  constructor(
    public name: string,
    private telephone: TelephoneNumber
  ) {}

  getTelephoneNumber(): string {
    return this.telephone.getTelephoneNumber();
  }
}

class TelephoneNumber {
  constructor(
    private areaCode: string,
    private number: string
  ) {}

  getTelephoneNumber(): string {
    return `(${this.areaCode}) ${this.number}`;
  }
}
```

**After:**
```typescript
class Person {
  constructor(
    public name: string,
    private areaCode: string,
    private number: string
  ) {}

  getTelephoneNumber(): string {
    return `(${this.areaCode}) ${this.number}`;
  }
}
```

**Mechanics:**
1. For each public method in class to inline, create same method in absorbing class
2. Change references to use absorbing class
3. Move fields and methods to absorbing class
4. Delete original class
5. Test

**When to Use**:
- Class has very few responsibilities
- Changes have reduced class to near nothing
- Abstraction isn't pulling its weight

### Hide Delegate

**Problem**: Client is calling a delegate class of an object.

**Solution**: Create methods on server to hide the delegate.

**Motivation**: Encapsulation means objects should know less about other parts of the system. When a client calls methods on a delegate, it creates coupling.

**Before:**
```java
// Client code
Person manager = john.getDepartment().getManager();
```

```java
class Person {
    private Department department;

    public Department getDepartment() {
        return department;
    }
}

class Department {
    private Person manager;

    public Person getManager() {
        return manager;
    }
}
```

**After:**
```java
// Client code
Person manager = john.getManager();
```

```java
class Person {
    private Department department;

    public Person getManager() {
        return department.getManager();
    }
}

class Department {
    private Person manager;

    public Person getManager() {
        return manager;
    }
}
```

**Mechanics:**
1. For each method on delegate, create delegating method on server
2. Adjust client to call server
3. Test after each method
4. Remove delegate accessor if no longer needed

**When to Use**:
- Want to reduce coupling to delegate
- Many clients calling delegate
- Delegate interface may change

## Organizing Data

These refactorings help you better organize data and improve encapsulation.

### Replace Magic Number with Symbolic Constant

**Problem**: You have a literal number with a particular meaning.

**Solution**: Create a constant, name it after the meaning, and replace the number with it.

**Motivation**: Magic numbers scattered through code are hard to understand and dangerous to change.

**Before:**
```python
def potential_energy(mass, height):
    return mass * 9.81 * height

def convert_to_fahrenheit(celsius):
    return celsius * 1.8 + 32
```

**After:**
```python
GRAVITATIONAL_ACCELERATION = 9.81
FAHRENHEIT_CONVERSION_FACTOR = 1.8
FAHRENHEIT_FREEZING_POINT = 32

def potential_energy(mass, height):
    return mass * GRAVITATIONAL_ACCELERATION * height

def convert_to_fahrenheit(celsius):
    return celsius * FAHRENHEIT_CONVERSION_FACTOR + FAHRENHEIT_FREEZING_POINT
```

**Mechanics:**
1. Declare constant and set to value of magic number
2. Find all occurrences of magic number
3. Check each occurrence represents same concept
4. Replace magic number with constant
5. Test

**When to Use**:
- Literal values appear multiple times
- Value has semantic meaning beyond its numeric value
- Value might need to change

### Encapsulate Field

**Problem**: Public field is exposed.

**Solution**: Make it private and provide accessors.

**Motivation**: Public data is bad because it allows uncontrolled access. Accessors allow you to change implementation later.

**Before:**
```typescript
class Person {
  public name: string;
}

// Client code
person.name = "John";
```

**After:**
```typescript
class Person {
  private _name: string;

  get name(): string {
    return this._name;
  }

  set name(value: string) {
    this._name = value;
  }
}

// Client code
person.name = "John";  // Still works but now controlled
```

**Mechanics:**
1. Create getter and setter for field
2. Find all references to field outside class
3. Replace references with getter/setter calls
4. Make field private
5. Test

**When to Use**:
- Field is public
- Want to add validation or logging later
- Want to change internal representation

### Replace Data Value with Object

**Problem**: Data item needs additional data or behavior.

**Solution**: Turn data item into an object.

**Motivation**: Simple data items start simple but often grow complexity. When you need to add validation, formatting, or derivation, create a proper object.

**Before:**
```java
class Order {
    private String customer;

    public Order(String customer) {
        this.customer = customer;
    }

    public String getCustomer() {
        return customer;
    }
}
```

**After:**
```java
class Order {
    private Customer customer;

    public Order(String customerName) {
        this.customer = new Customer(customerName);
    }

    public Customer getCustomer() {
        return customer;
    }
}

class Customer {
    private final String name;

    public Customer(String name) {
        this.name = name;
    }

    public String getName() {
        return name;
    }
}
```

**Mechanics:**
1. Create class for value
2. Add field to new class
3. Add getter to new class
4. Change type of field in source
5. Change getter in source
6. Change constructor in source
7. Test

**When to Use**:
- Data item is being used in several places
- Need to add behavior to data item
- Need validation or formatting
- Data item appears with associated data

### Replace Array with Object

**Problem**: Array elements represent different things.

**Solution**: Replace array with object that has fields for each element.

**Motivation**: Arrays should hold collections of similar objects. When positions mean different things, use an object with named fields.

**Before:**
```python
def process_performance(performance):
    # performance[0] is name
    # performance[1] is wins
    # performance[2] is losses
    name = performance[0]
    wins = performance[1]
    losses = performance[2]
    win_percentage = wins / (wins + losses)
```

**After:**
```python
class Performance:
    def __init__(self, name, wins, losses):
        self.name = name
        self.wins = wins
        self.losses = losses

    def get_win_percentage(self):
        return self.wins / (self.wins + self.losses)

def process_performance(performance):
    name = performance.name
    win_percentage = performance.get_win_percentage()
```

**Mechanics:**
1. Create class to represent array data
2. Add field for each array element
3. Change array references to object references
4. Test

**When to Use**:
- Array positions represent different types of data
- Need to add behavior to data structure
- Array indices are hard to remember

## Simplifying Conditional Expressions

These refactorings make conditional logic clearer and easier to understand.

### Decompose Conditional

**Problem**: Complex conditional (if-then-else) statement.

**Solution**: Extract methods from condition, then part, and else part.

**Motivation**: Complex conditionals are hard to read. Extracting into named methods makes the logic clearer.

**Before:**
```typescript
function calculateCharge(quantity: number, date: Date): number {
  let charge: number;

  if (date < SUMMER_START || date > SUMMER_END) {
    charge = quantity * winterRate + winterServiceCharge;
  } else {
    charge = quantity * summerRate;
  }

  return charge;
}
```

**After:**
```typescript
function calculateCharge(quantity: number, date: Date): number {
  if (isWinter(date)) {
    return winterCharge(quantity);
  } else {
    return summerCharge(quantity);
  }
}

function isWinter(date: Date): boolean {
  return date < SUMMER_START || date > SUMMER_END;
}

function winterCharge(quantity: number): number {
  return quantity * winterRate + winterServiceCharge;
}

function summerCharge(quantity: number): number {
  return quantity * summerRate;
}
```

**Mechanics:**
1. Extract condition into method
2. Extract then part into method
3. Extract else part into method
4. Test

**When to Use**:
- Complex if condition
- Long then or else blocks
- Logic needs clarification

### Consolidate Conditional Expression

**Problem**: Sequence of conditionals with same result.

**Solution**: Combine into single conditional and extract it.

**Motivation**: Multiple conditionals doing the same thing should be combined to show they're fundamentally one check.

**Before:**
```java
public double disabilityAmount(Employee employee) {
    if (employee.seniority < 2) return 0;
    if (employee.monthsDisabled > 12) return 0;
    if (employee.isPartTime) return 0;

    // Calculate disability amount
    return calculateDisabilityAmount(employee);
}
```

**After:**
```java
public double disabilityAmount(Employee employee) {
    if (isNotEligibleForDisability(employee)) {
        return 0;
    }

    return calculateDisabilityAmount(employee);
}

private boolean isNotEligibleForDisability(Employee employee) {
    return employee.seniority < 2
        || employee.monthsDisabled > 12
        || employee.isPartTime;
}
```

**Mechanics:**
1. Check all conditionals have same result
2. Combine with logical operators (AND/OR)
3. Extract combined condition to method
4. Test

**When to Use**:
- Multiple conditionals return same value
- Multiple conditionals execute same code
- Want to show checks are really one concept

### Consolidate Duplicate Conditional Fragments

**Problem**: Same fragment of code in all branches of conditional.

**Solution**: Move it outside the conditional.

**Motivation**: Code that executes regardless of condition should be outside the conditional.

**Before:**
```python
def calculate_total(is_special_deal):
    if is_special_deal:
        total = price * 0.95
        send_notification()
    else:
        total = price * 0.98
        send_notification()
```

**After:**
```python
def calculate_total(is_special_deal):
    if is_special_deal:
        total = price * 0.95
    else:
        total = price * 0.98

    send_notification()
```

**Mechanics:**
1. Identify duplicated code in branches
2. Move duplicated code outside conditional
3. Test

**When to Use**:
- Same code appears in all branches
- Code doesn't depend on which branch executes

### Replace Nested Conditional with Guard Clauses

**Problem**: Conditionals are nested and obscure normal path.

**Solution**: Use guard clauses for special cases.

**Motivation**: Conditionals come in two forms: both paths are normal (if-else), or one path is exceptional (guard clause). Make the distinction clear.

**Before:**
```typescript
function getPayAmount(employee: Employee): number {
  let result: number;

  if (employee.isDead) {
    result = deadAmount();
  } else {
    if (employee.isSeparated) {
      result = separatedAmount();
    } else {
      if (employee.isRetired) {
        result = retiredAmount();
      } else {
        result = normalPayAmount();
      }
    }
  }

  return result;
}
```

**After:**
```typescript
function getPayAmount(employee: Employee): number {
  if (employee.isDead) return deadAmount();
  if (employee.isSeparated) return separatedAmount();
  if (employee.isRetired) return retiredAmount();

  return normalPayAmount();
}
```

**Mechanics:**
1. For each special case, add guard clause
2. Return or throw from guard clause
3. Remove remaining nested conditionals
4. Test

**When to Use**:
- Nested conditionals obscure normal flow
- Special cases can be checked first
- Want to emphasize the normal path

### Replace Conditional with Polymorphism

**Problem**: Conditional behavior varies by object type.

**Solution**: Move each leg of conditional to overriding method in subclass.

**Motivation**: When behavior varies by type, polymorphism is clearer than conditionals. Adding new types becomes easier.

**Before:**
```java
class Bird {
    private BirdType type;

    public double getSpeed() {
        switch (type) {
            case EUROPEAN:
                return getBaseSpeed();
            case AFRICAN:
                return getBaseSpeed() - getLoadFactor() * numberOfCoconuts;
            case NORWEGIAN_BLUE:
                return (isNailed) ? 0 : getBaseSpeed();
            default:
                throw new RuntimeException("Unknown bird type");
        }
    }
}
```

**After:**
```java
abstract class Bird {
    public abstract double getSpeed();

    protected double getBaseSpeed() {
        // Common implementation
    }
}

class European extends Bird {
    @Override
    public double getSpeed() {
        return getBaseSpeed();
    }
}

class African extends Bird {
    @Override
    public double getSpeed() {
        return getBaseSpeed() - getLoadFactor() * numberOfCoconuts;
    }
}

class NorwegianBlue extends Bird {
    @Override
    public double getSpeed() {
        return isNailed ? 0 : getBaseSpeed();
    }
}
```

**Mechanics:**
1. Create subclass for each conditional leg
2. Move conditional method to superclass
3. Create overriding method in subclass
4. Copy code from conditional leg
5. Repeat for each leg
6. Remove conditional method from superclass
7. Test

**When to Use**:
- Conditional switches on type code
- Multiple methods have same type-based conditional
- Need to add new types frequently

## Dealing with Generalization

These refactorings help you work with inheritance hierarchies.

### Pull Up Method

**Problem**: Methods in subclasses do the same thing.

**Solution**: Move them to superclass.

**Motivation**: Eliminate duplication in inheritance hierarchies by moving common behavior up.

**Before:**
```python
class Employee:
    pass

class Salesman(Employee):
    def get_name(self):
        return self.name

class Engineer(Employee):
    def get_name(self):
        return self.name
```

**After:**
```python
class Employee:
    def get_name(self):
        return self.name

class Salesman(Employee):
    pass

class Engineer(Employee):
    pass
```

**Mechanics:**
1. Examine methods to ensure they're identical
2. Check method signatures are same
3. Create method in superclass
4. Remove from one subclass, test
5. Remove from other subclasses, test each time

**When to Use**:
- Identical methods in multiple subclasses
- Similar methods that can be parameterized

### Pull Up Field

**Problem**: Subclasses have same field.

**Solution**: Move field to superclass.

**Motivation**: Duplicate fields indicate that behavior belongs in superclass.

**Before:**
```java
class Salesman extends Employee {
    private String name;
}

class Engineer extends Employee {
    private String name;
}
```

**After:**
```java
class Employee {
    protected String name;
}

class Salesman extends Employee {
}

class Engineer extends Employee {
}
```

**Mechanics:**
1. Examine uses of field in all subclasses
2. Check field names and types are same
3. Create field in superclass
4. Remove from subclasses
5. Test

**When to Use**:
- Same field in multiple subclasses
- Field used similarly across subclasses

### Extract Subclass

**Problem**: Class has features used only in some instances.

**Solution**: Create subclass for that subset of features.

**Motivation**: When a class has behavior relevant only for some instances, extract a subclass.

**Before:**
```typescript
class Employee {
  constructor(
    private name: string,
    private salary: number,
    private engineeringGrade?: string  // Only for engineers
  ) {}

  getSalary(): number {
    if (this.engineeringGrade) {
      // Special engineer salary calculation
      return this.salary * this.getEngineerBonus();
    }
    return this.salary;
  }

  private getEngineerBonus(): number {
    // Grade-based bonus
    return 1.2;
  }
}
```

**After:**
```typescript
class Employee {
  constructor(
    protected name: string,
    protected salary: number
  ) {}

  getSalary(): number {
    return this.salary;
  }
}

class Engineer extends Employee {
  constructor(
    name: string,
    salary: number,
    private engineeringGrade: string
  ) {
    super(name, salary);
  }

  getSalary(): number {
    return this.salary * this.getEngineerBonus();
  }

  private getEngineerBonus(): number {
    return 1.2;
  }
}
```

**Mechanics:**
1. Create new subclass
2. Provide constructors for new subclass
3. Find calls to constructor and change to subclass where appropriate
4. Move subclass-specific features to subclass
5. Test

**When to Use**:
- Class behavior varies for different instances
- Type codes determine behavior
- Optional fields only used sometimes

### Extract Superclass

**Problem**: Two classes have similar features.

**Solution**: Create superclass and move common features there.

**Motivation**: When you see similar code in multiple classes, extract the commonality into a superclass.

**Before:**
```python
class Department:
    def __init__(self, name, staff):
        self.name = name
        self.staff = staff

    def get_total_annual_cost(self):
        return sum(s.annual_cost for s in self.staff)

class Employee:
    def __init__(self, name, id, annual_cost):
        self.name = name
        self.id = id
        self.annual_cost = annual_cost

    def get_id(self):
        return self.id
```

**After:**
```python
class Party:
    def __init__(self, name):
        self.name = name

    def get_name(self):
        return self.name

    def get_annual_cost(self):
        raise NotImplementedError()

class Department(Party):
    def __init__(self, name, staff):
        super().__init__(name)
        self.staff = staff

    def get_annual_cost(self):
        return sum(s.get_annual_cost() for s in self.staff)

class Employee(Party):
    def __init__(self, name, id, annual_cost):
        super().__init__(name)
        self.id = id
        self.annual_cost = annual_cost

    def get_id(self):
        return self.id

    def get_annual_cost(self):
        return self.annual_cost
```

**Mechanics:**
1. Create superclass
2. Make existing classes subclasses
3. Pull up common methods one at a time
4. Pull up common fields
5. Examine remaining methods for common code
6. Test after each pull up

**When to Use**:
- Two or more classes share common behavior
- Want to eliminate duplication in unrelated classes

## Big Refactorings

Some refactorings are large-scale transformations. These should be broken into small steps.

### Extract Hierarchy

**Problem**: Class is doing too much work, partly through conditional statements.

**Solution**: Create hierarchy of classes, each representing a special case.

**Before:**
```java
class ProductService {
    public double calculatePrice(Product product, Customer customer) {
        double price = product.getBasePrice();

        // Physical product logic
        if (product.isPhysical()) {
            price += calculateShipping(product);
            price += calculatePackaging(product);
        }

        // Digital product logic
        if (product.isDigital()) {
            price += calculateDownloadFee(product);
            if (customer.isPremium()) {
                price -= product.getBasePrice() * 0.1;  // Premium discount
            }
        }

        // Subscription logic
        if (product.isSubscription()) {
            price = calculateMonthlyRate(product);
            if (customer.hasAnnualPlan()) {
                price = price * 12 * 0.9;  // Annual discount
            }
        }

        return price;
    }
}
```

**After:**
```java
abstract class Product {
    protected double basePrice;

    public abstract double calculatePrice(Customer customer);

    protected double getBasePrice() {
        return basePrice;
    }
}

class PhysicalProduct extends Product {
    @Override
    public double calculatePrice(Customer customer) {
        return getBasePrice()
            + calculateShipping()
            + calculatePackaging();
    }

    private double calculateShipping() { /* ... */ }
    private double calculatePackaging() { /* ... */ }
}

class DigitalProduct extends Product {
    @Override
    public double calculatePrice(Customer customer) {
        double price = getBasePrice() + calculateDownloadFee();

        if (customer.isPremium()) {
            price -= getBasePrice() * 0.1;
        }

        return price;
    }

    private double calculateDownloadFee() { /* ... */ }
}

class SubscriptionProduct extends Product {
    @Override
    public double calculatePrice(Customer customer) {
        double monthlyRate = calculateMonthlyRate();

        if (customer.hasAnnualPlan()) {
            return monthlyRate * 12 * 0.9;
        }

        return monthlyRate;
    }

    private double calculateMonthlyRate() { /* ... */ }
}
```

**When to Use**:
- Large class with many conditionals based on type
- Different behavior for different variants
- Need to add new variants frequently

## Code Smell to Refactoring Mapping

This table helps you select the right refactoring for each smell:

| Code Smell | Primary Refactoring |
|------------|-------------------|
| Long Method | Extract Method |
| Large Class | Extract Class, Extract Subclass |
| Long Parameter List | Introduce Parameter Object, Preserve Whole Object |
| Divergent Change | Extract Class |
| Shotgun Surgery | Move Method, Move Field, Inline Class |
| Feature Envy | Move Method |
| Data Clumps | Extract Class, Introduce Parameter Object |
| Primitive Obsession | Replace Data Value with Object, Replace Array with Object |
| Switch Statements | Replace Conditional with Polymorphism |
| Parallel Inheritance | Move Method, Move Field |
| Lazy Class | Inline Class, Collapse Hierarchy |
| Speculative Generality | Collapse Hierarchy, Inline Class, Remove Parameter |
| Temporary Field | Extract Class |
| Message Chains | Hide Delegate |
| Middle Man | Remove Middle Man, Inline Method |
| Inappropriate Intimacy | Move Method, Extract Class, Hide Delegate |
| Duplicate Code | Extract Method, Pull Up Method, Extract Class |
| Dead Code | Delete it |
| Comments (compensating for bad code) | Extract Method, Rename Method |

## Safe Refactoring Checklist

Before any refactoring:
- [ ] Tests exist and pass
- [ ] Understand current behavior
- [ ] Have specific refactoring in mind
- [ ] Can break into small steps

During refactoring:
- [ ] Make one change at a time
- [ ] Run tests after each change
- [ ] Commit working states
- [ ] Use IDE refactoring tools where possible

After refactoring:
- [ ] All tests still pass
- [ ] Code is clearer
- [ ] No new smells introduced
- [ ] Behavior unchanged

## Related Guides

- **CODE_SMELLS.md**: Identify problems that need these refactorings
- **REFACTORING_WORKFLOW.md**: Process for safely applying refactorings
- **CONTINUOUS_IMPROVEMENT.md**: Building refactoring into daily work
- **04-quality-through-testing/**: Creating test safety net for refactoring
- **03-clean-architecture/SOLID_PRINCIPLES.md**: Principles guiding refactoring decisions

## Summary

This catalog provides a toolkit for improving code structure. Key principles:

**Small Steps**: Each refactoring is a small, behavior-preserving change. Complex improvements are sequences of simple refactorings.

**Test Support**: Always have passing tests before refactoring. Run them after each small change.

**Named Techniques**: Use the catalog names when discussing refactorings. "Extract Method" is clearer than "make it better."

**Composable**: Chain refactorings together. Extract Method, then Move Method, then Rename Method creates larger improvements.

**Tool Supported**: Modern IDEs implement many of these refactorings. Learn keyboard shortcuts for your most-used refactorings.

Start with the simplest refactorings (Extract Method, Rename Variable) and build up to complex transformations (Replace Conditional with Polymorphism, Extract Hierarchy). With practice, applying these refactorings becomes second nature, and your code quality improves continuously.
