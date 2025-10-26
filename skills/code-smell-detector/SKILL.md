---
name: code-smell-detector
description: Identifies code smells and suggests specific refactoring patterns. Use during code review, before refactoring, or when code feels wrong. Detects long methods, large classes, duplicated code, and other maintainability issues. Returns smell classification and refactoring recommendations.
allowed-tools: [Read, Grep, Glob]
---

# Code Smell Detector

## Purpose

Identifies code quality issues (smells) and suggests specific refactoring patterns to improve maintainability.

## When to Use This Skill

**Use when:**
- Code review (catch smells early)
- Before refactoring (identify targets)
- Code feels "wrong" but unclear why
- Technical debt assessment
- Learning to recognize quality issues

**Examples:**
- "Analyze this function for code smells"
- "Why does this class feel too complex?"
- "What refactorings would improve this code?"
- "Identify technical debt in this module"

## Common Code Smells & Refactorings

### 1. Long Method (>50 lines)

**Smell**: Method does too much, hard to understand

**Detection:**
- Method exceeds 50 lines
- Multiple levels of indentation (>3)
- Lots of comments explaining sections
- Hard to name precisely

**Refactoring**: Extract Method
```typescript
// BEFORE: Long method (code smell)
function processOrder(order) {
  // Validate order (10 lines)
  if (!order.items) throw new Error();
  if (order.items.length === 0) throw new Error();
  // ... more validation

  // Calculate total (15 lines)
  let total = 0;
  for (const item of order.items) {
    total += item.price * item.quantity;
  }
  // ... more calculation

  // Apply discounts (12 lines)
  if (order.coupon) {
    // ... discount logic
  }

  // Save to database (8 lines)
  // ... database logic
}

// AFTER: Extracted methods
function processOrder(order) {
  validateOrder(order);
  const total = calculateTotal(order);
  const discounted = applyDiscounts(total, order);
  return saveOrder(order, discounted);
}
```

### 2. Large Class (>300 lines)

**Smell**: Class has too many responsibilities

**Refactoring**: Extract Class
```python
# BEFORE: God class
class User:
    def __init__(self): ...
    def login(self): ...
    def logout(self): ...
    def update_profile(self): ...
    def change_password(self): ...
    def send_email(self): ...
    def validate_email(self): ...
    def format_address(self): ...
    # ... 20 more methods

# AFTER: Extracted classes
class User:
    def __init__(self): ...
    def login(self): ...
    def logout(self): ...

class UserProfile:
    def update(self): ...
    def change_password(self): ...

class UserNotifications:
    def send_email(self): ...
    def validate_email(self): ...
```

### 3. Duplicated Code

**Refactoring**: Extract Method/Class
```typescript
// BEFORE: Duplication
function sendWelcomeEmail(user) {
  const client = new EmailClient();
  client.send(user.email, "Welcome!", template);
}

function sendResetEmail(user) {
  const client = new EmailClient();
  client.send(user.email, "Reset Password", template);
}

// AFTER: Extract common pattern
class EmailService {
  private client = new EmailClient();

  send(to: string, subject: string, template: string) {
    this.client.send(to, subject, template);
  }
}
```

### 4. Long Parameter List (>3 params)

**Refactoring**: Introduce Parameter Object
```java
// BEFORE: Long parameter list
public Order createOrder(
    String customerId,
    String productId,
    int quantity,
    String shippingAddress,
    String billingAddress,
    String couponCode
) { }

// AFTER: Parameter object
public class OrderRequest {
    String customerId;
    String productId;
    int quantity;
    String shippingAddress;
    String billingAddress;
    String couponCode;
}

public Order createOrder(OrderRequest request) { }
```

### 5. Feature Envy

**Smell**: Method uses another class's data more than its own

**Refactoring**: Move Method
```python
# BEFORE: Feature envy
class Order:
    def get_customer_discount(self):
        return (
            self.customer.loyalty_points * 0.01 +
            self.customer.tier_discount +
            self.customer.referral_bonus
        )

# AFTER: Move to Customer
class Customer:
    def calculate_discount(self):
        return (
            self.loyalty_points * 0.01 +
            self.tier_discount +
            self.referral_bonus
        )

class Order:
    def get_customer_discount(self):
        return self.customer.calculate_discount()
```

## Detection Report Format

```
CODE SMELL ANALYSIS: [File/Module Name]

METRICS
-------
Lines of Code: [N]
Cyclomatic Complexity: [N]
Method Count: [N]
Class Count: [N]

DETECTED SMELLS
---------------

1. LONG METHOD [Severity: HIGH]
   Location: src/order.ts:45 (processOrder)
   Lines: 87 (threshold: 50)
   Complexity: 12 (threshold: 10)

   Problem:
   - Method handles validation, calculation, discounts, and persistence
   - Hard to test individual pieces
   - Difficult to reuse parts

   Refactoring: Extract Method
   Suggested Methods:
   - validateOrder(order): void
   - calculateTotal(order): number
   - applyDiscounts(total, order): number
   - saveOrder(order, total): Order

   Estimated Effort: 1-2 hours
   Benefit: Improved testability, reusability, clarity

2. DUPLICATED CODE [Severity: MEDIUM]
   Locations:
   - src/email-service.ts:30-45
   - src/sms-service.ts:25-40

   Duplication:
   ```typescript
   // Retry logic repeated in both files
   for (let i = 0; i < 3; i++) {
     try { return await this.send(); }
     catch (e) { await sleep(1000 * i); }
   }
   ```

   Refactoring: Extract Method
   Suggested Utility:
   ```typescript
   class RetryHelper {
     static async withRetry(fn, attempts = 3) { }
   }
   ```

   Estimated Effort: 30 minutes
   Benefit: DRY compliance, maintainability

3. FEATURE ENVY [Severity: LOW]
   Location: src/order.ts:120 (getCustomerDiscount)

   Problem:
   - Order class accessing Customer data extensively
   - Logic belongs in Customer class

   Refactoring: Move Method
   Move to: src/customer.ts (Customer class)

   Estimated Effort: 15 minutes
   Benefit: Better encapsulation

REFACTORING PRIORITIES
-----------------------
1. Extract methods from processOrder [HIGH]
2. Extract RetryHelper utility [MEDIUM]
3. Move discount calculation to Customer [LOW]

TOTAL ESTIMATED EFFORT: 2-3 hours
EXPECTED IMPROVEMENT: 40% complexity reduction
```

## References

- **[CODE_SMELLS.md](../05-refactoring-and-improvement/CODE_SMELLS.md)** - Complete catalog
- **[REFACTORING_CATALOG.md](../05-refactoring-and-improvement/REFACTORING_CATALOG.md)** - Refactoring patterns
