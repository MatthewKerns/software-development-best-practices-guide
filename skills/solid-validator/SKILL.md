---
name: solid-validator
description: Validates code against SOLID principles (Single Responsibility, Open/Closed, Liskov Substitution, Interface Segregation, Dependency Inversion). Use during design review, refactoring, or when architecture feels wrong. Returns principle violations and refactoring suggestions.
allowed-tools: [Read, Grep, Glob]
---

# SOLID Principles Validator

## Purpose

Validates code against SOLID design principles to ensure maintainable, extensible architecture.

## When to Use

**Use when:**
- Designing new classes/modules
- Reviewing architecture
- Code feels brittle or hard to change
- Planning refactoring
- Teaching SOLID principles

## SOLID Principles

### S - Single Responsibility Principle

**Principle**: A class should have one, and only one, reason to change.

**Violation Example:**
```typescript
// VIOLATION: Multiple responsibilities
class User {
  saveToDatabase() { }    // Data persistence
  sendEmail() { }         // Email notification
  validateInput() { }     // Validation
  formatJSON() { }        // Formatting
}
```

**Fix:**
```typescript
class User {
  // Domain logic only
}

class UserRepository {
  save(user: User) { }    // Data persistence
}

class UserNotifier {
  sendEmail(user: User) { } // Notifications
}

class UserValidator {
  validate(user: User) { } // Validation
}
```

### O - Open/Closed Principle

**Principle**: Open for extension, closed for modification.

**Violation:**
```python
class PaymentProcessor:
    def process(self, payment_type, amount):
        if payment_type == "credit_card":
            # Credit card logic
        elif payment_type == "paypal":
            # PayPal logic
        elif payment_type == "crypto":
            # Crypto logic (modified existing class!)
```

**Fix:**
```python
class PaymentProcessor(ABC):
    @abstractmethod
    def process(self, amount): pass

class CreditCardProcessor(PaymentProcessor):
    def process(self, amount): ...

class PayPalProcessor(PaymentProcessor):
    def process(self, amount): ...

class CryptoProcessor(PaymentProcessor):
    def process(self, amount): ...  # Extended, not modified!
```

### L - Liskov Substitution Principle

**Principle**: Subtypes must be substitutable for their base types.

**Violation:**
```java
class Rectangle {
    void setWidth(int w) { width = w; }
    void setHeight(int h) { height = h; }
}

class Square extends Rectangle {
    void setWidth(int w) {
        width = w;
        height = w;  // VIOLATION: Changes behavior
    }
}
```

**Fix:**
```java
interface Shape {
    int getArea();
}

class Rectangle implements Shape {
    int getArea() { return width * height; }
}

class Square implements Shape {
    int getArea() { return side * side; }
}
```

### I - Interface Segregation Principle

**Principle**: No client should depend on methods it doesn't use.

**Violation:**
```typescript
interface Worker {
  work(): void;
  eat(): void;
  sleep(): void;
}

class Robot implements Worker {
  work() { }
  eat() { }    // VIOLATION: Robots don't eat
  sleep() { }  // VIOLATION: Robots don't sleep
}
```

**Fix:**
```typescript
interface Workable {
  work(): void;
}

interface Eatable {
  eat(): void;
}

interface Sleepable {
  sleep(): void;
}

class Robot implements Workable {
  work() { }
}

class Human implements Workable, Eatable, Sleepable {
  work() { }
  eat() { }
  sleep() { }
}
```

### D - Dependency Inversion Principle

**Principle**: Depend on abstractions, not concretions.

**Violation:**
```python
class EmailService:
    def send(self, message): ...

class UserService:
    def __init__(self):
        self.email = EmailService()  # Depends on concrete class
```

**Fix:**
```python
class NotificationService(ABC):
    @abstractmethod
    def send(self, message): pass

class EmailService(NotificationService):
    def send(self, message): ...

class UserService:
    def __init__(self, notifier: NotificationService):
        self.notifier = notifier  # Depends on abstraction
```

## Validation Report

```
SOLID VALIDATION: [Module/Class Name]

SINGLE RESPONSIBILITY [STATUS: VIOLATION]
- Class User has 4 responsibilities
- Reasons to change: persistence, validation, notifications, formatting

Recommendation: Extract UserRepository, UserValidator, UserNotifier

OPEN/CLOSED [STATUS: PASS]
- Payment types use strategy pattern
- New payment methods can be added without modification

LISKOV SUBSTITUTION [STATUS: VIOLATION]
- Square.setWidth() changes height (unexpected behavior)

Recommendation: Redesign hierarchy

INTERFACE SEGREGATION [STATUS: PASS]
- Interfaces are focused and cohesive

DEPENDENCY INVERSION [STATUS: VIOLATION]
- UserService depends on concrete EmailService

Recommendation: Introduce NotificationService interface
```

## References

- **[SOLID_PRINCIPLES.md](../03-clean-architecture/SOLID_PRINCIPLES.md)** - Complete guide
