# SOLID Principles Quick Reference

**Quick reference for applying SOLID principles during design and code review.**

Based on: Clean Architecture (Chapters 7-11)

## The Five Principles

| Principle | Summary | Goal |
|-----------|---------|------|
| **SRP** | Single Responsibility | One reason to change |
| **OCP** | Open-Closed | Open for extension, closed for modification |
| **LSP** | Liskov Substitution | Subtypes must be substitutable |
| **ISP** | Interface Segregation | Client-specific interfaces |
| **DIP** | Dependency Inversion | Depend on abstractions |

## Single Responsibility Principle (SRP)

**"A class should have one, and only one, reason to change."**

### The Real Meaning
- Different **actors** should not cause the same class to change
- Actor = group of stakeholders who want a specific change
- One responsibility = serves one actor

### Violation Example
```python
# ✗ Three actors cause this class to change
class Employee:
    def calculate_pay(self):        # CFO's responsibility
        # Calculate employee pay

    def report_hours(self):         # COO's responsibility
        # Report hours worked

    def save(self):                 # CTO's responsibility
        # Save to database
```

### Solution: Separate by Actor
```python
# ✓ Each class serves one actor
class PayCalculator:              # CFO's domain
    def calculate_pay(employee):
        pass

class HourReporter:               # COO's domain
    def report_hours(employee):
        pass

class EmployeeRepository:         # CTO's domain
    def save(employee):
        pass

class EmployeeFacade:             # Coordinates for convenience
    def __init__(self):
        self.pay_calc = PayCalculator()
        self.reporter = HourReporter()
        self.repo = EmployeeRepository()
```

### SRP Checklist
- [ ] Can you identify the primary actor for this class?
- [ ] Would changes from different stakeholders affect this class?
- [ ] Does the class have multiple reasons to change?
- [ ] Are responsibilities from different business domains mixed?

## Open-Closed Principle (OCP)

**"Software entities should be open for extension, closed for modification."**

### Core Idea
- Add new features without changing existing code
- Achieve through abstractions and polymorphism
- Protect high-level policy from low-level details

### Violation Example
```python
# ✗ Must modify to add new types
def calculate_area(shapes):
    total = 0
    for shape in shapes:
        if isinstance(shape, Circle):
            total += math.pi * shape.radius ** 2
        elif isinstance(shape, Rectangle):
            total += shape.width * shape.height
        # Must modify this function for each new shape!
    return total
```

### Solution: Polymorphism
```python
# ✓ Open for extension, closed for modification
class Shape(ABC):
    @abstractmethod
    def area(self):
        pass

class Circle(Shape):
    def area(self):
        return math.pi * self.radius ** 2

class Rectangle(Shape):
    def area(self):
        return self.width * self.height

def calculate_area(shapes):
    return sum(shape.area() for shape in shapes)
    # No modification needed for new shapes!

# Extend by adding new class
class Triangle(Shape):
    def area(self):
        return 0.5 * self.base * self.height
```

### OCP Checklist
- [ ] Can you add new behavior without modifying existing code?
- [ ] Are you using if/switch on type codes?
- [ ] Are high-level policies protected from low-level details?
- [ ] Can the system be extended through new classes?

## Liskov Substitution Principle (LSP)

**"Subtypes must be substitutable for their base types."**

### Core Idea
- Derived classes must honor base class contracts
- Inheritance should mean "is-a" relationship
- Subclass shouldn't surprise users of base class

### Violation Example
```python
# ✗ Square violates Rectangle's contract
class Rectangle:
    def set_width(self, w):
        self.width = w

    def set_height(self, h):
        self.height = h

class Square(Rectangle):
    def set_width(self, w):
        self.width = w
        self.height = w  # Side effect!

    def set_height(self, h):
        self.width = h
        self.height = h  # Side effect!

# Breaks substitutability
def test_rectangle(rect):
    rect.set_width(5)
    rect.set_height(4)
    assert rect.width * rect.height == 20  # Fails for Square!
```

### Solution: Proper Abstraction
```python
# ✓ LSP compliant hierarchy
class Shape(ABC):
    @abstractmethod
    def area(self):
        pass

class Rectangle(Shape):
    def __init__(self, width, height):
        self.width = width
        self.height = height

    def area(self):
        return self.width * self.height

class Square(Shape):
    def __init__(self, side):
        self.side = side

    def area(self):
        return self.side * self.side
```

### LSP Checklist
- [ ] Can derived class be used wherever base class is expected?
- [ ] Does derived class strengthen preconditions? (BAD)
- [ ] Does derived class weaken postconditions? (BAD)
- [ ] Does derived class throw new exceptions? (BAD)
- [ ] Does inheritance represent true "is-a" relationship?

### Common LSP Violations
| Violation | Example | Fix |
|-----------|---------|-----|
| **Stronger preconditions** | Derived requires more inputs | Relax requirements |
| **Weaker postconditions** | Derived provides less | Strengthen guarantees |
| **New exceptions** | Derived throws unexpected errors | Handle in derived |
| **Type checking** | `if isinstance(x, Derived)` | Polymorphism |

## Interface Segregation Principle (ISP)

**"No client should depend on methods it doesn't use."**

### Core Idea
- Split large interfaces into client-specific ones
- Clients shouldn't depend on unused methods
- Many small interfaces > one large interface

### Violation Example
```python
# ✗ Fat interface forces unnecessary dependencies
class Worker(ABC):
    @abstractmethod
    def work(self): pass

    @abstractmethod
    def eat(self): pass

    @abstractmethod
    def sleep(self): pass

class HumanWorker(Worker):
    def work(self): print("Working")
    def eat(self): print("Eating")
    def sleep(self): print("Sleeping")

class RobotWorker(Worker):
    def work(self): print("Working")
    def eat(self): pass  # Robots don't eat!
    def sleep(self): pass  # Robots don't sleep!
```

### Solution: Segregated Interfaces
```python
# ✓ Client-specific interfaces
class Workable(ABC):
    @abstractmethod
    def work(self): pass

class Eatable(ABC):
    @abstractmethod
    def eat(self): pass

class Sleepable(ABC):
    @abstractmethod
    def sleep(self): pass

class HumanWorker(Workable, Eatable, Sleepable):
    def work(self): print("Working")
    def eat(self): print("Eating")
    def sleep(self): print("Sleeping")

class RobotWorker(Workable):
    def work(self): print("Working")
    # Only implements what it needs!
```

### ISP Checklist
- [ ] Do clients depend on methods they don't use?
- [ ] Are there empty/stub method implementations?
- [ ] Does interface serve multiple client types?
- [ ] Can interface be split into smaller, focused interfaces?

## Dependency Inversion Principle (DIP)

**"Depend on abstractions, not concretions."**

### Core Idea
- High-level modules shouldn't depend on low-level modules
- Both should depend on abstractions
- Abstractions shouldn't depend on details
- Details should depend on abstractions

### Violation Example
```python
# ✗ High-level depends on low-level concrete class
class MySQLDatabase:
    def save(self, data):
        # MySQL-specific code
        pass

class UserService:
    def __init__(self):
        self.db = MySQLDatabase()  # Concrete dependency!

    def create_user(self, user):
        self.db.save(user)
        # Tightly coupled to MySQL
```

### Solution: Depend on Abstraction
```python
# ✓ Both depend on abstraction
class Database(ABC):
    @abstractmethod
    def save(self, data): pass

class MySQLDatabase(Database):
    def save(self, data):
        # MySQL implementation
        pass

class PostgreSQLDatabase(Database):
    def save(self, data):
        # PostgreSQL implementation
        pass

class UserService:
    def __init__(self, db: Database):  # Depend on abstraction
        self.db = db

    def create_user(self, user):
        self.db.save(user)
        # Works with any Database implementation

# Dependency injection
db = MySQLDatabase()  # or PostgreSQLDatabase()
service = UserService(db)
```

### DIP Checklist
- [ ] Are high-level classes importing low-level concrete classes?
- [ ] Can you swap implementations without changing high-level code?
- [ ] Do dependencies point toward abstractions?
- [ ] Are you using dependency injection?

### Dependency Flow
```
✗ Traditional (Bad):
High-Level → Low-Level Concrete Classes

✓ DIP (Good):
High-Level → ←Interface← Low-Level
(Both depend on abstraction in high-level module)
```

## SOLID Quick Decision Tree

### Is this a SOLID violation?

**SRP Question:**
```
Does this class change for multiple different stakeholders/actors?
    ✓ SRP VIOLATION → Split by actor/responsibility
```

**OCP Question:**
```
Do you modify existing code to add new features?
    ✓ OCP VIOLATION → Use abstractions/polymorphism
```

**LSP Question:**
```
Can derived class replace base without breaking assumptions?
    ✗ LSP VIOLATION → Fix contract or remove inheritance
```

**ISP Question:**
```
Do clients depend on methods they don't use?
    ✓ ISP VIOLATION → Split into client-specific interfaces
```

**DIP Question:**
```
Does high-level code import low-level concrete classes?
    ✓ DIP VIOLATION → Depend on abstractions, inject dependencies
```

## Common Code Smells by Principle

| Principle | Code Smell | Indicator |
|-----------|------------|-----------|
| **SRP** | God Class | Class > 500 lines, many methods |
| **SRP** | Divergent Change | Multiple reasons to change |
| **OCP** | Switch on Type | `if isinstance()` or type codes |
| **OCP** | Shotgun Surgery | One change affects many classes |
| **LSP** | Type Checking | `if isinstance(x, DerivedClass)` |
| **LSP** | Refused Bequest | Empty/stub method implementations |
| **ISP** | Fat Interface | Interface with >10 methods |
| **ISP** | Empty Methods | `def method(): pass` |
| **DIP** | Import Concrete | High-level imports low-level class |
| **DIP** | Hard-coded Dependencies | `self.db = MySQLDB()` |

## Benefits of SOLID

| Principle | Primary Benefit |
|-----------|----------------|
| **SRP** | Easier to understand and change |
| **OCP** | Safe extension without modification |
| **LSP** | Reliable polymorphism |
| **ISP** | Reduced coupling, cleaner dependencies |
| **DIP** | Flexibility, testability, independence |

## When to Apply SOLID

### Design Phase
- [ ] Planning class responsibilities
- [ ] Designing inheritance hierarchies
- [ ] Creating interfaces
- [ ] Establishing dependencies

### Code Review
- [ ] Checking for SRP violations (god classes)
- [ ] Identifying OCP violations (type switches)
- [ ] Verifying LSP compliance
- [ ] Spotting fat interfaces (ISP)
- [ ] Reviewing dependency directions (DIP)

### Refactoring
- [ ] Breaking up large classes (SRP)
- [ ] Replacing type codes with polymorphism (OCP)
- [ ] Fixing broken inheritance (LSP)
- [ ] Splitting interfaces (ISP)
- [ ] Inverting dependencies (DIP)

## SOLID in Practice

### Testing Benefits
```python
# DIP enables easy testing
class UserService:
    def __init__(self, db: Database):
        self.db = db

# Test with mock
def test_create_user():
    mock_db = MockDatabase()
    service = UserService(mock_db)
    service.create_user(user)
    assert mock_db.save_called
```

### Maintenance Benefits
```python
# OCP allows safe extension
# Add new payment method without changing existing code
class StripePayment(PaymentMethod):
    def process(self, amount):
        # Stripe-specific implementation
        pass
```

## References

- **Full Guide**: [03-clean-architecture/](../03-clean-architecture/)
- **Source**: Clean Architecture by Robert C. Martin (Chapters 7-11)

---

**Remember**: SOLID principles make code flexible, maintainable, and testable.
