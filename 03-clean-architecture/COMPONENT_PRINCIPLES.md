# Component Principles: Building Cohesive, Loosely Coupled Systems

## Overview

Components are the units of deployment—the smallest entities that can be deployed as part of a system. They are the granular building blocks that combine to form applications. Understanding how to organize code into components and manage dependencies between them is fundamental to creating maintainable, scalable architectures.

**"Component principles are about how to partition the code into components, which components should be in which  component, and how components should depend on each other."** — Robert C. Martin, Clean Architecture

These principles operate at a higher level than SOLID (which focuses on classes and modules). Component principles guide the organization of classes into components and the dependencies between those components.

## Why Component Principles Matter

### The Cost of Poor Component Design

Systems with poorly designed components exhibit:

**Release Coupling**: Changes to one component force releases of many unrelated components, creating massive, risky deployments.

**Circular Dependencies**: Components depend on each other in cycles, making it impossible to test, build, or deploy them independently.

**Unnecessary Releases**: Components are forced to track releases of dependencies they don't actually use, increasing maintenance burden.

**Fragmentation**: Code that belongs together is scattered across multiple components, making understanding and modification difficult.

**The "Big Ball of Mud"**: Without component boundaries, the entire system becomes one tangled mess where everything depends on everything else.

### The Benefits of Well-Designed Components

Well-designed components provide:
- **Independent Development**: Teams can work on different components simultaneously without conflicts
- **Independent Deployment**: Components can be deployed separately, enabling incremental releases
- **Reusability**: Well-bounded components can be reused in different contexts
- **Testability**: Components can be tested in isolation with mocked dependencies
- **Comprehensibility**: Clear component boundaries make system architecture understandable
- **Parallel Development**: Multiple teams can develop different components concurrently

## Source Materials

This guide is based on:

- **Clean Architecture** by Robert C. Martin (Part IV: "Component Principles")
  - Chapters 12-14: Component cohesion principles (REP, CCP, CRP)
  - Chapters 15-16: Component coupling principles (ADP, SDP, SAP)
  - Real-world examples and architectural implications

## What is a Component?

A component is the smallest unit of deployment. In different ecosystems:

- **Java**: JAR files
- **Ruby**: Gem files
- **Node.js**: NPM packages
- **.NET**: DLL files
- **Python**: Wheels or installed packages
- **Go**: Modules

Components are independently deployable units that can be versioned, released, and installed separately from other components.

## The Six Component Principles

### Cohesion Principles (How to Group)

These three principles help decide which classes belong together in a component:

1. **REP - Reuse/Release Equivalence Principle**
2. **CCP - Common Closure Principle**
3. **CRP - Common Reuse Principle**

### Coupling Principles (How to Connect)

These three principles help decide how components should depend on each other:

4. **ADP - Acyclic Dependencies Principle**
5. **SDP - Stable Dependencies Principle**
6. **SAP - Stable Abstractions Principle**

---

## Component Cohesion Principles

### 1. Reuse/Release Equivalence Principle (REP)

**Definition**: The granule of reuse is the granule of release.

**Core Insight**: Classes and modules that are grouped together into a component should be releasable together. They should share a common purpose that makes them reusable as a group.

#### Understanding REP

If you want to reuse code, you must track releases. Components are the unit of release, so anything you want to reuse must be part of a released component with a version number, release notes, and compatibility guarantees.

**Implications**:
- Classes in a component should form a cohesive group
- Component should have a clear theme or purpose
- All classes in component should be releasable together
- Version numbers, release notes, and compatibility tracking apply to the entire component

**Example of Violation:**

```python
# BAD: Unrelated classes grouped into one component "utils"

# utils/component.py - A hodgepodge component
class StringHelper:
    """String manipulation utilities"""
    @staticmethod
    def capitalize_words(text: str) -> str:
        return text.title()

class DatabaseConnection:
    """Database connectivity"""
    def connect(self, host: str) -> None:
        print(f"Connecting to {host}")

class EmailValidator:
    """Email validation"""
    @staticmethod
    def is_valid_email(email: str) -> bool:
        return "@" in email

class HTTPClient:
    """HTTP request handling"""
    def get(self, url: str) -> str:
        return "response"

# Problem: No cohesive theme
# - Cannot reuse string utilities without pulling in database code
# - Cannot version email validation independently
# - Changes to HTTP client force new releases for string utilities users
```

**Problem**: This "utils" component has no cohesive purpose. Users who need string utilities are forced to depend on database, email, and HTTP code they don't need. When any part changes, everyone must deal with a new release.

**Corrected Design:**

```python
# GOOD: Cohesive components with clear purposes

# text-processing/component.py
class StringFormatter:
    """Text formatting utilities"""
    @staticmethod
    def capitalize_words(text: str) -> str:
        return text.title()

    @staticmethod
    def to_snake_case(text: str) -> str:
        return text.lower().replace(" ", "_")

class TextValidator:
    """Text validation utilities"""
    @staticmethod
    def is_non_empty(text: str) -> bool:
        return bool(text and text.strip())

# database-access/component.py
class DatabaseConnection:
    """Database connection management"""
    def connect(self, host: str) -> None:
        print(f"Connecting to {host}")

class ConnectionPool:
    """Database connection pooling"""
    def __init__(self, size: int):
        self.size = size

# email-services/component.py
class EmailValidator:
    """Email validation"""
    @staticmethod
    def is_valid_email(email: str) -> bool:
        return "@" in email and "." in email

class EmailSender:
    """Email sending"""
    def send(self, to: str, subject: str, body: str) -> None:
        print(f"Sending email to {to}")

# http-client/component.py
class HTTPClient:
    """HTTP request handling"""
    def get(self, url: str) -> str:
        return "response"

    def post(self, url: str, data: dict) -> str:
        return "response"
```

**Benefit**: Each component has a clear, cohesive purpose. Users can depend on only what they need. Each component can be versioned and released independently based on its own change frequency.

#### REP in TypeScript (NPM Packages)

```typescript
// BAD: One package with unrelated functionality
// package.json
{
  "name": "awesome-toolkit",
  "version": "1.0.0",
  "description": "Various utilities"
}

// src/index.ts - Everything exported from one package
export class Logger { ... }
export class DatabaseConnector { ... }
export class ImageResizer { ... }
export class CreditCardValidator { ... }
export class WeatherAPI { ... }

// Problem: Users need Logger but must install image processing,
// database connectivity, payment validation, and weather APIs

// GOOD: Focused packages
// @myorg/logging/package.json
{
  "name": "@myorg/logging",
  "version": "2.1.0",
  "description": "Structured logging utilities"
}

// @myorg/database/package.json
{
  "name": "@myorg/database",
  "version": "1.5.2",
  "description": "Database connection and query utilities"
}

// @myorg/image-processing/package.json
{
  "name": "@myorg/image-processing",
  "version": "3.0.1",
  "description": "Image manipulation and resizing"
}

// @myorg/payment-validation/package.json
{
  "name": "@myorg/payment-validation",
  "version": "1.2.0",
  "description": "Credit card and payment validation"
}

// Now users depend only on what they need
// package.json for client
{
  "dependencies": {
    "@myorg/logging": "^2.1.0",  // Only needs logging
    "@myorg/database": "^1.5.2"  // and database
  }
}
```

### 2. Common Closure Principle (CCP)

**Definition**: Gather into components those classes that change for the same reasons and at the same times. Separate into different components those classes that change for different reasons or at different times.

**Core Insight**: This is the Single Responsibility Principle (SRP) restated for components. A component should not have multiple reasons to change. Classes that change together should stay together.

#### Understanding CCP

CCP is about minimizing the number of components that must be changed when requirements change. If two classes always change together, they belong in the same component. If they change for different reasons, they belong in different components.

**CCP is the component-level equivalent of SRP.**

**Example of Violation:**

```java
// BAD: Mixing UI and business logic in one component

// sales-component/Product.java
public class Product {
    private String id;
    private String name;
    private BigDecimal price;

    // Business logic - changes when business rules change
    public BigDecimal calculateDiscount(CustomerType customerType) {
        return switch (customerType) {
            case PREMIUM -> price.multiply(new BigDecimal("0.2"));
            case STANDARD -> price.multiply(new BigDecimal("0.1"));
            default -> BigDecimal.ZERO;
        };
    }
}

// sales-component/ProductView.java
public class ProductView {
    // UI rendering - changes when UI design changes
    public String renderHTML(Product product) {
        return """
            <div class="product">
                <h2>%s</h2>
                <p>Price: $%s</p>
            </div>
            """.formatted(product.getName(), product.getPrice());
    }

    public String renderJSON(Product product) {
        return """
            {
                "name": "%s",
                "price": %s
            }
            """.formatted(product.getName(), product.getPrice());
    }
}

// Problem: Two reasons to change in one component
// 1. Business rule changes (discount calculation)
// 2. UI presentation changes (HTML/JSON rendering)
```

**Problem**: When UI design changes, the component must be rebuilt and redeployed even though business logic didn't change. When business rules change, UI developers must deal with a new release even though presentation didn't change.

**Corrected Design:**

```java
// GOOD: Separated by reason for change

// business-logic-component/Product.java
public class Product {
    private final String id;
    private final String name;
    private final BigDecimal price;

    public Product(String id, String name, BigDecimal price) {
        this.id = id;
        this.name = name;
        this.price = price;
    }

    // Getters
    public String getId() { return id; }
    public String getName() { return name; }
    public BigDecimal getPrice() { return price; }
}

// business-logic-component/DiscountCalculator.java
public class DiscountCalculator {
    // Changes when business rules change
    public BigDecimal calculateDiscount(Product product, CustomerType customerType) {
        return switch (customerType) {
            case PREMIUM -> product.getPrice().multiply(new BigDecimal("0.2"));
            case STANDARD -> product.getPrice().multiply(new BigDecimal("0.1"));
            default -> BigDecimal.ZERO;
        };
    }
}

// ui-rendering-component/ProductRenderer.java
public class ProductRenderer {
    // Changes when UI requirements change
    public String renderHTML(Product product) {
        return """
            <div class="product">
                <h2>%s</h2>
                <p>Price: $%s</p>
            </div>
            """.formatted(product.getName(), product.getPrice());
    }

    public String renderJSON(Product product) {
        return """
            {
                "name": "%s",
                "price": %s
            }
            """.formatted(product.getName(), product.getPrice());
    }
}
```

**Benefit**: Business logic changes don't affect UI component and vice versa. Each component changes for exactly one reason.

#### CCP in Python (Package Structure)

```python
# BAD: Mixed concerns in data_processing package

# data_processing/validators.py
class DataValidator:
    """Changes when validation rules change"""
    def validate_email(self, email: str) -> bool:
        return "@" in email

    def validate_age(self, age: int) -> bool:
        return 0 < age < 120

# data_processing/database.py
class DatabaseRepository:
    """Changes when database schema or queries change"""
    def save_user(self, user_data: dict) -> None:
        # Database save logic
        pass

# data_processing/api_client.py
class APIClient:
    """Changes when external API changes"""
    def fetch_user_data(self, user_id: str) -> dict:
        # API call logic
        return {}

# Problem: Three different reasons to change in one component
# 1. Validation rules evolve
# 2. Database schema changes
# 3. External API updates

# GOOD: Separate components by change reason

# validation/validators.py
"""Component: Changes only when validation rules change"""
class EmailValidator:
    def validate(self, email: str) -> bool:
        return "@" in email and "." in email

class AgeValidator:
    def validate(self, age: int) -> bool:
        return 0 < age < 120

# persistence/repositories.py
"""Component: Changes only when data storage changes"""
class UserRepository:
    def save(self, user_data: dict) -> None:
        # Database save logic
        pass

    def find_by_id(self, user_id: str) -> dict:
        # Database query logic
        return {}

# external_integration/clients.py
"""Component: Changes only when external services change"""
class UserAPIClient:
    def fetch(self, user_id: str) -> dict:
        # API call logic
        return {}
```

### 3. Common Reuse Principle (CRP)

**Definition**: Don't force users of a component to depend on things they don't need.

**Core Insight**: Classes that are used together should be grouped together. If you use one class from a component, you should expect to use many or all of the classes in that component. Don't make users depend on classes they don't use.

#### Understanding CRP

CRP tells us which classes shouldn't be together. If classes are not tightly bound, they shouldn't be in the same component. When a component changes, all components that depend on it must be revalidated and redeployed—even if they only use a small part of it.

**CRP is the component-level equivalent of ISP (Interface Segregation Principle).**

**Example of Violation:**

```typescript
// BAD: Unrelated classes forced together

// data-layer/index.ts
export class UserRepository {
    // Database access for users
    async findById(id: string): Promise<User> { ... }
    async save(user: User): Promise<void> { ... }
}

export class ProductRepository {
    // Database access for products
    async findById(id: string): Promise<Product> { ... }
    async save(product: Product): Promise<void> { ... }
}

export class ReportGenerator {
    // Complex reporting logic - rarely used
    async generateSalesReport(month: number): Promise<Report> { ... }
    async generateInventoryReport(): Promise<Report> { ... }
}

export class DataExporter {
    // Data export utilities - rarely used
    exportToCSV(data: any[]): string { ... }
    exportToJSON(data: any[]): string { ... }
}

// Problem: Applications using UserRepository must depend on
// ReportGenerator and DataExporter even if they never use them

// client-app/services/user-service.ts
import { UserRepository } from 'data-layer';
// Forces dependency on entire data-layer component
// including ReportGenerator and DataExporter
```

**Problem**: When `ReportGenerator` changes, all components depending on `data-layer` must be revalidated, even if they only use `UserRepository`. This creates unnecessary coupling and deployment overhead.

**Corrected Design:**

```typescript
// GOOD: Split into cohesively reused components

// repositories/index.ts - Commonly used together
export class UserRepository {
    async findById(id: string): Promise<User> { ... }
    async save(user: User): Promise<void> { ... }
}

export class ProductRepository {
    async findById(id: string): Promise<Product> { ... }
    async save(product: Product): Promise<void> { ... }
}

// reporting/index.ts - Used together for reporting features
export class ReportGenerator {
    async generateSalesReport(month: number): Promise<Report> { ... }
    async generateInventoryReport(): Promise<Report> { ... }
}

export class ReportFormatter {
    formatAsPDF(report: Report): Buffer { ... }
    formatAsExcel(report: Report): Buffer { ... }
}

// data-export/index.ts - Used together for export features
export class DataExporter {
    exportToCSV(data: any[]): string { ... }
    exportToJSON(data: any[]): string { ... }
    exportToXML(data: any[]): string { ... }
}

// Now clients depend only on what they use
import { UserRepository } from 'repositories';
// No dependency on reporting or data-export
```

#### CRP in Python

```python
# BAD: Kitchen sink component

# analytics/module.py
class DataProcessor:
    """Core functionality - used by everyone"""
    def process(self, data: list) -> list:
        return [item * 2 for item in data]

class ChartGenerator:
    """Visualization - only used by reporting features"""
    def generate_bar_chart(self, data: list) -> str:
        return "chart"

class MachineLearningModel:
    """ML features - only used by advanced analytics"""
    def train(self, data: list) -> None:
        pass

    def predict(self, input_data: list) -> list:
        return []

class EmailReporter:
    """Email notifications - only used by scheduled jobs"""
    def send_report(self, recipient: str, data: list) -> None:
        pass

# Problem: Apps using DataProcessor depend on ML, charts, and email
from analytics import DataProcessor
# Forces dependency on ML models they'll never use!

# GOOD: Separate by actual usage patterns

# analytics_core/processor.py
"""Core analytics - used by all analytics features"""
class DataProcessor:
    def process(self, data: list) -> list:
        return [item * 2 for item in data]

class DataAggregator:
    def aggregate(self, data: list) -> dict:
        return {"sum": sum(data), "count": len(data)}

# analytics_visualization/charts.py
"""Visualization - used together for reporting"""
class ChartGenerator:
    def generate_bar_chart(self, data: list) -> str:
        return "chart"

class GraphRenderer:
    def render_line_graph(self, data: list) -> str:
        return "graph"

# analytics_ml/models.py
"""Machine learning - used together for predictions"""
class MachineLearningModel:
    def train(self, data: list) -> None:
        pass

    def predict(self, input_data: list) -> list:
        return []

class ModelEvaluator:
    def evaluate(self, model, test_data: list) -> float:
        return 0.95

# analytics_notifications/email.py
"""Notifications - used together for scheduled reporting"""
class EmailReporter:
    def send_report(self, recipient: str, data: list) -> None:
        pass

class ScheduledReporter:
    def schedule(self, frequency: str) -> None:
        pass

# Now clients depend only on what they actually use
from analytics_core import DataProcessor
# No dependency on ML or visualization
```

### The Tension Diagram

The three cohesion principles pull in different directions:

```
                CCP
                 /\
                /  \
               /    \
              /      \
             /        \
            /          \
           /            \
          /              \
         /                \
        /                  \
       /                    \
      /                      \
     /________________________\
   REP                        CRP
```

- **REP**: Group for reusability - wants larger, feature-complete components
- **CCP**: Group for maintenance - wants changes concentrated in few components
- **CRP**: Split for independence - wants smaller, focused components

**You cannot simultaneously optimize for all three.** You must choose a position in this triangle based on your project's current needs:

- **Early development**: Favor CCP (group things that change together)
- **Mature, stable system**: Favor REP and CRP (reusability and independence)
- **Rapidly evolving**: Favor CCP over CRP (minimize change impact)

---

## Component Coupling Principles

### 4. Acyclic Dependencies Principle (ADP)

**Definition**: Allow no cycles in the component dependency graph.

**Core Insight**: Component dependencies must form a directed acyclic graph (DAG). Cycles make it impossible to determine build order, test components independently, or release incrementally.

#### Understanding ADP

When components have circular dependencies, you cannot build or test them independently. Changes ripple through the cycle unpredictably. The entire cycle becomes one large, inseparable component.

**Example of Violation:**

```python
# BAD: Circular dependency between components

# user_management/user.py
from order_processing.order import Order  # Depends on order_processing

class User:
    def __init__(self, user_id: str):
        self.user_id = user_id

    def get_order_history(self) -> list:
        # User component depends on Order component
        return Order.find_by_user(self.user_id)

# order_processing/order.py
from user_management.user import User  # Depends on user_management!

class Order:
    def __init__(self, order_id: str, user_id: str):
        self.order_id = order_id
        self.user_id = user_id

    def get_customer(self) -> User:
        # Order component depends on User component
        return User(self.user_id)

# Cycle: user_management -> order_processing -> user_management
```

**Problems**:
- Cannot build `user_management` without `order_processing`
- Cannot build `order_processing` without `user_management`
- Cannot test either component independently
- Cannot release one without the other
- Difficult to understand which depends on what

**Solution 1: Dependency Inversion**

```python
# GOOD: Break cycle with abstraction

# user_management/user.py
from abc import ABC, abstractmethod

class OrderRepository(ABC):
    """Abstract interface - no dependency on order_processing"""
    @abstractmethod
    def find_by_user(self, user_id: str) -> list:
        pass

class User:
    def __init__(self, user_id: str, order_repo: OrderRepository):
        self.user_id = user_id
        self.order_repo = order_repo

    def get_order_history(self) -> list:
        # Depends on abstraction, not concrete Order
        return self.order_repo.find_by_user(self.user_id)

# order_processing/order.py
# No dependency on user_management!

class Order:
    def __init__(self, order_id: str, user_id: str):
        self.order_id = order_id
        self.user_id = user_id

# order_processing/repository.py
from user_management.user import OrderRepository  # Depends on interface

class DatabaseOrderRepository(OrderRepository):
    def find_by_user(self, user_id: str) -> list:
        # Implementation details
        return []

# Now dependency flows one way: order_processing -> user_management
# No cycle!
```

**Solution 2: Create New Component**

```python
# GOOD: Extract shared interface to new component

# domain_entities/user_entity.py
class UserEntity:
    """Pure data object - no dependencies"""
    def __init__(self, user_id: str, name: str):
        self.user_id = user_id
        self.name = name

# domain_entities/order_entity.py
class OrderEntity:
    """Pure data object - no dependencies"""
    def __init__(self, order_id: str, user_id: str, total: float):
        self.order_id = order_id
        self.user_id = user_id
        self.total = total

# user_management/user_service.py
from domain_entities.user_entity import UserEntity
from domain_entities.order_entity import OrderEntity

class UserService:
    def get_user_with_orders(self, user_id: str) -> tuple[UserEntity, list[OrderEntity]]:
        user = UserEntity(user_id, "John")
        orders = []  # Fetch from repository
        return user, orders

# order_processing/order_service.py
from domain_entities.order_entity import OrderEntity

class OrderService:
    def create_order(self, user_id: str, total: float) -> OrderEntity:
        return OrderEntity("ord-123", user_id, total)

# Dependencies:
# user_management -> domain_entities
# order_processing -> domain_entities
# No cycle!
```

#### ADP in Java

```java
// BAD: Circular dependency

// payments/PaymentProcessor.java
package com.myapp.payments;

import com.myapp.orders.Order;  // Depends on orders package

public class PaymentProcessor {
    public void processPayment(Order order) {
        // Process payment for order
        order.markAsPaid();  // Calls back into orders package
    }
}

// orders/Order.java
package com.myapp.orders;

import com.myapp.payments.PaymentProcessor;  // Depends on payments package!

public class Order {
    private PaymentProcessor processor = new PaymentProcessor();

    public void checkout() {
        processor.processPayment(this);  // Circular dependency
    }

    public void markAsPaid() {
        // Mark order as paid
    }
}

// GOOD: Break cycle with interface

// orders/Order.java
package com.myapp.orders;

// No import of PaymentProcessor!

public class Order {
    private OrderStatus status;

    public void markAsPaid() {
        this.status = OrderStatus.PAID;
    }

    public OrderStatus getStatus() {
        return status;
    }
}

// orders/PaymentCallback.java
package com.myapp.orders;

public interface PaymentCallback {
    void onPaymentSuccess(String orderId);
    void onPaymentFailure(String orderId);
}

// payments/PaymentProcessor.java
package com.myapp.payments;

import com.myapp.orders.Order;
import com.myapp.orders.PaymentCallback;

public class PaymentProcessor {
    private final PaymentCallback callback;

    public PaymentProcessor(PaymentCallback callback) {
        this.callback = callback;
    }

    public void processPayment(Order order) {
        // Process payment
        boolean success = true;  // Actual payment logic

        if (success) {
            callback.onPaymentSuccess(order.getId());
        } else {
            callback.onPaymentFailure(order.getId());
        }
    }
}

// Dependency: payments -> orders (one-way, no cycle)
```

### 5. Stable Dependencies Principle (SDP)

**Definition**: Depend in the direction of stability. Components should depend on components that are more stable than themselves.

**Core Insight**: Stability is related to the amount of work required to make a change. A component with many dependents is stable because it requires great effort to change (you must reconcile all dependents). A component with many dependencies is unstable because changes in dependencies force changes in the component.

#### Measuring Stability

**Stability Metric (I)**: I = Fan-out / (Fan-in + Fan-out)

- **Fan-in**: Number of classes outside the component that depend on classes inside the component
- **Fan-out**: Number of classes inside the component that depend on classes outside the component
- **I = 0**: Maximally stable (many dependents, no dependencies)
- **I = 1**: Maximally unstable (no dependents, many dependencies)

#### Understanding SDP

Unstable components should depend on stable components, not vice versa. If a stable component depends on an unstable component, changes in the unstable component force changes in the stable component, which ripples to all its dependents.

**Example:**

```typescript
// VIOLATION: Stable component depends on unstable component

// domain-model/User.ts (STABLE - many dependents)
// Fan-in: 15 components use User
// Fan-out: 1 (depends on ExperimentalFeature)
// I = 1 / (15 + 1) = 0.0625 (stable)

import { ExperimentalFeature } from 'experimental-features';

export class User {
    constructor(
        public id: string,
        public name: string
    ) {}

    // Stable component depends on unstable experimental feature!
    getFeatureFlags(): string[] {
        return ExperimentalFeature.getFlags(this.id);
    }
}

// experimental-features/ExperimentalFeature.ts (UNSTABLE - changes frequently)
// Fan-in: 1 (only User depends on it)
// Fan-out: 5 (depends on many other components)
// I = 5 / (1 + 5) = 0.83 (unstable)

export class ExperimentalFeature {
    static getFlags(userId: string): string[] {
        // Experimental feature that changes frequently
        return [];
    }
}

// Problem: User is stable (I=0.06) but depends on
// ExperimentalFeature which is unstable (I=0.83)
// Changes to experimental features force changes to stable User model!
```

**Corrected Design:**

```typescript
// GOOD: Unstable component depends on stable component

// domain-model/User.ts (STABLE)
// Fan-in: 15 components use User
// Fan-out: 0
// I = 0 / (15 + 0) = 0 (maximally stable)

export class User {
    constructor(
        public id: string,
        public name: string
    ) {}

    // No dependencies on unstable components
}

// feature-management/FeatureFlagService.ts (UNSTABLE)
// Fan-in: 2
// Fan-out: 5 (including User)
// I = 5 / (2 + 5) = 0.71 (unstable)

import { User } from 'domain-model';

export class FeatureFlagService {
    // Unstable component depends on stable component
    getFlags(user: User): string[] {
        // Experimental logic that can change frequently
        return this.experimentalFlags.getForUser(user.id);
    }
}

// Now dependency flows correctly: unstable -> stable
```

#### SDP in Python

```python
# BAD: Stable core depends on unstable UI

# core/business_rules.py (STABLE - core domain logic)
from ui.widgets import FancyButton  # WRONG DIRECTION!

class PaymentProcessor:
    """Core business logic - should be very stable"""

    def process_payment(self, amount: float) -> bool:
        # Business logic shouldn't depend on UI components!
        button = FancyButton("Pay Now")
        return True

# ui/widgets.py (UNSTABLE - UI changes frequently)
class FancyButton:
    """UI widget - changes with design trends"""
    def __init__(self, label: str):
        self.label = label

# Problem: Core business rules depend on frequently changing UI
# UI changes force business logic to change!

# GOOD: Unstable UI depends on stable core

# core/business_rules.py (STABLE)
class PaymentProcessor:
    """Core business logic - no dependencies on UI"""

    def process_payment(self, amount: float) -> bool:
        # Pure business logic
        if amount <= 0:
            return False
        # Process payment
        return True

# core/interfaces.py (STABLE)
from abc import ABC, abstractmethod

class PaymentHandler(ABC):
    """Stable interface for payment handling"""

    @abstractmethod
    def process_payment(self, amount: float) -> bool:
        pass

# ui/payment_view.py (UNSTABLE)
from core.business_rules import PaymentProcessor
from core.interfaces import PaymentHandler

class PaymentButton:
    """UI component depends on stable business logic"""

    def __init__(self, processor: PaymentHandler):
        self.processor = processor

    def on_click(self, amount: float) -> None:
        success = self.processor.process_payment(amount)
        if success:
            self.show_success_message()

# Dependency flows correctly: unstable UI -> stable core
```

### 6. Stable Abstractions Principle (SAP)

**Definition**: A component should be as abstract as it is stable.

**Core Insight**: Stable components should consist of abstract classes and interfaces, making them flexible and extensible. Unstable components should be concrete, making them easy to change.

#### Measuring Abstractness

**Abstractness Metric (A)**: A = Number of abstract classes / Total number of classes

- **A = 0**: Completely concrete
- **A = 1**: Completely abstract

#### The Main Sequence

The relationship between stability (I) and abstractness (A) forms the "main sequence":

```
Abstractness (A)
1.0 |  Zone of        Main Sequence (ideal)    Zone of
    |  Uselessness   /                          Pain
    |               /
0.5 |              /
    |             /
    |            /
0.0 |___________/________________________________
    0.0        0.5                             1.0
                                    Instability (I)
```

**Main Sequence**: Components should fall along the diagonal from (0, 1) to (1, 0)
- **Stable and Abstract** (I=0, A=1): Interfaces and abstract base classes
- **Unstable and Concrete** (I=1, A=0): Implementation details that change frequently

**Zone of Pain** (I=0, A=0): Stable and concrete - rigid, hard to change
**Zone of Uselessness** (I=1, A=1): Unstable and abstract - no concrete implementations

#### Understanding SAP

If a component is stable (many dependents), it should be abstract so it can be extended without modification (Open-Closed Principle). If a component is unstable (few dependents), it can be concrete because it's easy to change.

**SAP is the Dependency Inversion Principle (DIP) applied to components.**

**Example:**

```java
// BAD: Stable but concrete (Zone of Pain)

// database-access component (STABLE)
// I = 0.1 (10 components depend on it, it depends on 1)
// A = 0.0 (all concrete classes)

package com.myapp.database;

// Concrete, stable class - hard to extend or change
public class MySQLUserRepository {
    // Hardcoded to MySQL
    private Connection connection;

    public MySQLUserRepository() {
        this.connection = DriverManager.getConnection("jdbc:mysql://localhost");
    }

    public User findById(String id) {
        // MySQL-specific query
        Statement stmt = connection.createStatement();
        ResultSet rs = stmt.executeQuery("SELECT * FROM users WHERE id = " + id);
        // ... parse result
        return user;
    }

    public void save(User user) {
        // MySQL-specific insert
    }
}

// Problem: 10 components depend on MySQLUserRepository
// Cannot switch to PostgreSQL without changing all 10 dependents
// Stable but inflexible (Zone of Pain: I=0.1, A=0.0)

// GOOD: Stable and abstract (Main Sequence)

// database-access component (STABLE)
// I = 0.1 (10 components depend on it, it depends on 1)
// A = 1.0 (all abstract interfaces)

package com.myapp.database;

// Abstract, stable interface - flexible and extensible
public interface UserRepository {
    User findById(String id);
    void save(User user);
    List<User> findAll();
}

// database-mysql component (UNSTABLE)
// I = 0.9 (1 component depends on it, it depends on 5)
// A = 0.0 (concrete implementation)

package com.myapp.database.mysql;

import com.myapp.database.UserRepository;

// Concrete but unstable - easy to change or replace
public class MySQLUserRepository implements UserRepository {
    private Connection connection;

    public MySQLUserRepository(String connectionString) {
        this.connection = DriverManager.getConnection(connectionString);
    }

    @Override
    public User findById(String id) {
        // MySQL-specific implementation
        return user;
    }

    @Override
    public void save(User user) {
        // MySQL-specific implementation
    }

    @Override
    public List<User> findAll() {
        // MySQL-specific implementation
        return users;
    }
}

// database-postgres component (UNSTABLE)
// Easy to add without changing stable interface

package com.myapp.database.postgres;

import com.myapp.database.UserRepository;

public class PostgreSQLUserRepository implements UserRepository {
    // Alternative implementation
}

// Now on Main Sequence:
// database-access: I=0.1, A=1.0 (stable and abstract)
// database-mysql: I=0.9, A=0.0 (unstable and concrete)
```

#### SAP in TypeScript

```typescript
// BAD: Unstable but abstract (Zone of Uselessness)

// experimental-ui component (UNSTABLE - changes frequently)
// I = 0.9 (few dependents, many dependencies)
// A = 1.0 (all abstract)

export interface ThemeProvider {
    getTheme(): Theme;
}

export interface ColorPalette {
    getPrimaryColor(): string;
}

export interface LayoutEngine {
    calculateLayout(): Layout;
}

// Problem: All abstract but unstable - changes frequently
// No concrete implementations in the component!
// Zone of Uselessness: I=0.9, A=1.0

// GOOD: Unstable and concrete (Main Sequence)

// experimental-ui component (UNSTABLE)
// I = 0.9
// A = 0.2 (mostly concrete with some abstractions)

export interface ThemeProvider {
    getTheme(): Theme;
}

// Concrete implementations that can change easily
export class ExperimentalTheme implements ThemeProvider {
    getTheme(): Theme {
        return {
            primaryColor: '#FF5733',
            fontSize: '16px'
        };
    }
}

export class ColorCalculator {
    calculateContrastRatio(color1: string, color2: string): number {
        // Concrete calculation that can change
        return 4.5;
    }
}

export class LayoutBuilder {
    buildFlexLayout(items: any[]): Layout {
        // Concrete layout logic that can evolve
        return new Layout();
    }
}

// Now on Main Sequence: I=0.9, A=0.2 (unstable and mostly concrete)
```

#### SAP in Python

```python
# GOOD: Following SAP across components

# domain_core (STABLE and ABSTRACT)
# I = 0.0 (many dependents, no dependencies)
# A = 1.0 (all abstract base classes)

from abc import ABC, abstractmethod

class OrderRepository(ABC):
    """Stable abstraction"""
    @abstractmethod
    def save(self, order: 'Order') -> None:
        pass

    @abstractmethod
    def find_by_id(self, order_id: str) -> 'Order':
        pass

class PaymentGateway(ABC):
    """Stable abstraction"""
    @abstractmethod
    def charge(self, amount: float) -> bool:
        pass

# Main Sequence: I=0.0, A=1.0 (stable and abstract)

# infrastructure (UNSTABLE and CONCRETE)
# I = 0.8 (few dependents, many dependencies)
# A = 0.0 (all concrete implementations)

from domain_core import OrderRepository, PaymentGateway

class SQLOrderRepository(OrderRepository):
    """Concrete implementation - easy to change"""
    def save(self, order: 'Order') -> None:
        # SQL-specific implementation
        pass

    def find_by_id(self, order_id: str) -> 'Order':
        # SQL-specific query
        pass

class StripePaymentGateway(PaymentGateway):
    """Concrete implementation - easy to change"""
    def charge(self, amount: float) -> bool:
        # Stripe API call
        return True

# Main Sequence: I=0.8, A=0.0 (unstable and concrete)

# application_services (MODERATE stability and abstractness)
# I = 0.4 (some dependents, some dependencies)
# A = 0.4 (mix of abstract and concrete)

from domain_core import OrderRepository, PaymentGateway

class OrderService:
    """Moderate stability - some abstraction"""
    def __init__(self, repo: OrderRepository, gateway: PaymentGateway):
        self.repo = repo
        self.gateway = gateway

    def place_order(self, order: 'Order') -> bool:
        if self.gateway.charge(order.total):
            self.repo.save(order)
            return True
        return False

# Main Sequence: I=0.4, A=0.4 (balanced)
```

## Integration with Geist Framework

Component principles align with three-dimensional Geist analysis:

### Ghost (Unknown Unknowns) + Component Principles

**ADP reveals hidden cycles**: Circular dependencies hide in complex systems. Drawing the dependency graph exposes them.

**CRP reveals hidden coupling**: When components force dependencies on unused classes, hidden coupling emerges.

### Geyser (Dynamic Forces) + Component Principles

**CCP groups by change**: Anticipate where change will occur and group accordingly.

**SDP enables graceful evolution**: Depending on stable components means changes in unstable areas don't ripple everywhere.

**SAP allows extension**: Stable abstractions can absorb new implementations without breaking dependents.

### Gist (Essential Core) + Component Principles

**REP identifies reusable essentials**: What is the essential, reusable unit?

**SAP separates essential policy from details**: Stable, abstract components contain essential business rules. Unstable, concrete components contain changeable details.

## Practical Checklist

### Component Cohesion
- [ ] Each component has a clear, cohesive purpose (REP)
- [ ] Component can be versioned and released independently (REP)
- [ ] Classes that change together are in the same component (CCP)
- [ ] Classes that change for different reasons are in different components (CCP)
- [ ] Clients using one class from component likely use most classes (CRP)
- [ ] No forced dependencies on unused classes (CRP)

### Component Coupling
- [ ] No circular dependencies between components (ADP)
- [ ] Can build and test components independently (ADP)
- [ ] Unstable components depend on stable components (SDP)
- [ ] Stable components do not depend on unstable components (SDP)
- [ ] Stable components are abstract (SAP)
- [ ] Unstable components are concrete (SAP)
- [ ] Components fall on or near the main sequence (SAP)

### Component Metrics
- [ ] Calculate I (instability) for each component
- [ ] Calculate A (abstractness) for each component
- [ ] Plot components on I/A graph
- [ ] Components not in Zone of Pain (I=0, A=0)
- [ ] Components not in Zone of Uselessness (I=1, A=1)
- [ ] Components close to main sequence line

## Common Pitfalls

**Creating Too Many Components**: Don't over-fragment. Components have overhead. Start with fewer, larger components and split as needed.

**Ignoring Component Boundaries**: In practice, developers often violate component boundaries. Enforce them with build tools and architecture tests.

**Premature Optimization**: Don't optimize component structure before you understand change patterns. Let the design emerge.

**Ignoring the Tension**: You cannot maximize REP, CCP, and CRP simultaneously. Choose based on current project phase.

**Zone of Pain**: Stable, concrete components are rigid. Add abstractions to stable components.

**Zone of Uselessness**: Abstract components with no concrete implementations provide no value. Add implementations or remove the abstractions.

## Further Reading

### Related Guides
- **SOLID_PRINCIPLES.md**: Class-level principles that inform component design
- **DEPENDENCY_RULE.md**: How component principles enable clean architecture
- **ARCHITECTURE_PATTERNS.md**: Architectural patterns built on component principles
- **BOUNDARIES_AND_LAYERS.md**: How components form architectural boundaries
- **../05-refactoring-and-improvement/REFACTORING_CATALOG.md**: Refactoring to improve component structure

### Key Concepts
- **Directed Acyclic Graph (DAG)**: Component dependencies must form a DAG
- **Stability**: Resistance to change due to dependents
- **Abstractness**: Ratio of abstract to concrete classes
- **Main Sequence**: Ideal relationship between stability and abstractness

### Books
- **Clean Architecture** by Robert C. Martin (Part IV: Chapters 12-16)
- **Large-Scale C++ Software Design** by John Lakos
- **Agile Software Development, Principles, Patterns, and Practices** by Robert C. Martin

---

**Remember**: Component principles are guidelines for managing complexity at scale. Apply them when component structure becomes problematic, not before. Let your architecture emerge from real needs.
