# Architectural Boundaries: Drawing Lines That Matter

## Overview

Architectural boundaries are the lines we draw in our systems to separate components with different rates of change, different reasons to change, and different levels of policy. These boundaries protect high-level business logic from low-level implementation details, enable independent development and deployment, and create testable, maintainable architectures.

**"Software architecture is the art of drawing lines that I call boundaries. Those boundaries separate software elements from one another, and restrict those on one side from knowing about those on the other."** — Robert C. Martin, Clean Architecture

The decisions about where to draw these boundaries—and when to draw them—are among the most important architectural decisions we make. Good boundaries are drawn along the seams where change is most likely to occur, allowing us to defer decisions about details while protecting stable business policies.

## Why Boundaries Matter

### The Cost of No Boundaries

Systems without clear boundaries exhibit:

**The Big Ball of Mud**: Everything depends on everything else. A change anywhere requires understanding everywhere. Testing requires the entire system. Deployment is all-or-nothing.

**Cascading Changes**: Changing a database field requires modifying business logic, UI components, API contracts, and tests across the entire system. Simple changes become project-sized efforts.

**Coupled to Volatility**: Business rules change when the UI framework is upgraded. Core algorithms break when the database schema evolves. Stable policies are held hostage by volatile details.

**Cannot Defer Decisions**: Must choose database, web framework, and UI library before writing any business logic. Early decisions lock you in before requirements are understood.

**Untestable Components**: Cannot test business logic without starting web servers, connecting to databases, and mocking dozens of dependencies. Integration tests are the only option.

### The Benefits of Well-Drawn Boundaries

Clear boundaries provide:
- **Independent Development**: Teams work on different sides of boundaries without conflicts
- **Independent Deployment**: Components deploy separately, enabling incremental releases
- **Deferred Decisions**: Delay choosing frameworks, databases, and tools until you have more information
- **Testability**: Test business logic without infrastructure
- **Parallel Development**: Multiple teams develop simultaneously
- **Replaceability**: Swap implementations without touching business logic

## Source Materials

This guide is based on:

- **Clean Architecture** by Robert C. Martin (Part V: "Architecture")
  - Chapter 17: "Boundaries: Drawing Lines"
  - Chapter 18: "Boundary Anatomy"
  - Chapter 19: "Policy and Level"
  - When to draw boundaries, where to draw them, and what they cost

## What is a Boundary?

A boundary is a line that separates things that matter from things that don't matter. More precisely, it separates things at different levels of policy—different distances from the inputs and outputs of the system.

### Boundary Characteristics

**Unidirectional Dependencies**: Code on one side can depend on code on the other side, but not vice versa. Dependencies cross boundaries in one direction only—from lower-level details toward higher-level policies.

**Abstract Interfaces**: Boundaries are enforced through abstract interfaces (ports) that high-level components define and low-level components implement.

**Isolated Changes**: Changes on one side of a boundary don't ripple across to the other side. The interface remains stable while implementations vary.

**Different Rates of Change**: Code on different sides of boundaries changes at different rates and for different reasons. Boundaries protect stable code from volatile code.

### The Boundary Anatomy

```
┌────────────────────────────────────────────────────┐
│                                                    │
│  High-Level Component (Business Logic)            │
│                                                    │
│  defines interface:                                │
│  IRepository                                       │
│                                                    │
└────────────┬───────────────────────────────────────┘
             │
             │ Boundary (Interface)
             │
             ↑ implements
             │
┌────────────┴───────────────────────────────────────┐
│                                                    │
│  Low-Level Component (Implementation Detail)      │
│                                                    │
│  implements:                                       │
│  PostgresRepository                                │
│                                                    │
└────────────────────────────────────────────────────┘

    Dependency points UP (toward higher policy) ───→
    Control flow points DOWN (calls implementation)
```

At runtime, control flows from high-level to low-level (business logic calls repository). But at compile time, source code dependencies point from low-level to high-level (repository implements interface defined by business logic). This inversion is the essence of a boundary.

## Types of Boundaries

### 1. Layer Boundaries (Horizontal)

**Purpose**: Separate different levels of abstraction within the system.

**Example**: Domain → Application → Infrastructure

```
┌─────────────────────────────────────────────┐
│  Domain Layer (Entities & Business Rules)   │
│  - Pure business logic                      │
│  - No external dependencies                 │
└─────────────────┬───────────────────────────┘
                  │ boundary
┌─────────────────┴───────────────────────────┐
│  Application Layer (Use Cases)              │
│  - Orchestrates domain logic                │
│  - Defines interfaces for infrastructure    │
└─────────────────┬───────────────────────────┘
                  │ boundary
┌─────────────────┴───────────────────────────┐
│  Infrastructure Layer (Details)             │
│  - Databases, frameworks, external APIs     │
│  - Implements interfaces from above         │
└─────────────────────────────────────────────┘
```

**Crossing the Boundary**:

```python
# domain/entities.py (highest level)
class Order:
    """Pure business entity with no dependencies."""

    def __init__(self, customer_id: str, items: List[OrderItem]):
        self.customer_id = customer_id
        self.items = items
        self._validate()

    def calculate_total(self) -> Money:
        """Business rule: calculate order total."""
        return sum(item.price * item.quantity for item in self.items)

    def _validate(self) -> None:
        """Business rule: orders must have at least one item."""
        if not self.items:
            raise InvalidOrderError("Order must contain at least one item")

# application/use_cases.py (middle level)
from domain.entities import Order
from domain.repositories import IOrderRepository  # Abstract interface

class PlaceOrderUseCase:
    """Application logic that orchestrates domain entities."""

    def __init__(self, repository: IOrderRepository):
        self._repository = repository  # Depends on abstraction

    async def execute(self, request: PlaceOrderRequest) -> PlaceOrderResponse:
        # Create domain entity
        order = Order(request.customer_id, request.items)

        # Use business logic
        total = order.calculate_total()

        # Persist through interface (boundary)
        await self._repository.save(order)

        return PlaceOrderResponse(order_id=order.id, total=total)

# infrastructure/persistence/postgres_repository.py (lowest level)
from domain.repositories import IOrderRepository  # Implements interface from above

class PostgresOrderRepository(IOrderRepository):
    """Infrastructure detail that implements domain interface."""

    async def save(self, order: Order) -> None:
        # Implementation detail: how we store orders
        await self._db.execute(
            "INSERT INTO orders (id, customer_id, total) VALUES ($1, $2, $3)",
            order.id, order.customer_id, order.calculate_total().amount
        )
```

### 2. Vertical Boundaries (Feature Modules)

**Purpose**: Separate different business capabilities or features.

**Example**: Orders module ↔ Payments module ↔ Shipping module

```
┌─────────────┐   ┌─────────────┐   ┌─────────────┐
│   Orders    │   │  Payments   │   │  Shipping   │
│   Module    │   │   Module    │   │   Module    │
│             │   │             │   │             │
│  - Entities │   │  - Entities │   │  - Entities │
│  - Use Cases│   │  - Use Cases│   │  - Use Cases│
│  - Ports    │   │  - Ports    │   │  - Ports    │
└──────┬──────┘   └──────┬──────┘   └──────┬──────┘
       │                  │                  │
       └──────────────────┴──────────────────┘
                          │
              ┌───────────┴───────────┐
              │  Shared Infrastructure│
              │  (Database, etc.)     │
              └───────────────────────┘
```

**Crossing the Boundary** (Event-Driven):

```python
# orders/domain/events.py
@dataclass
class OrderPlaced(DomainEvent):
    """Event published when order is placed."""
    order_id: str
    customer_id: str
    total: Money

# orders/application/use_cases.py
class PlaceOrderUseCase:
    def __init__(self, repository: IOrderRepository, event_bus: IDomainEventBus):
        self._repository = repository
        self._event_bus = event_bus

    async def execute(self, request: PlaceOrderRequest) -> PlaceOrderResponse:
        order = Order(request.customer_id, request.items)
        await self._repository.save(order)

        # Publish event across boundary
        event = OrderPlaced(
            order_id=order.id,
            customer_id=order.customer_id,
            total=order.calculate_total()
        )
        self._event_bus.publish(event)

        return PlaceOrderResponse(order_id=order.id)

# payments/application/event_handlers.py
class OrderPlacedHandler:
    """Payment module reacts to order events without direct dependency."""

    def __init__(self, payment_gateway: IPaymentGateway):
        self._payment_gateway = payment_gateway

    async def handle(self, event: OrderPlaced) -> None:
        # Process payment when order is placed
        result = await self._payment_gateway.charge(
            amount=event.total,
            customer_id=event.customer_id
        )
        # ... handle result

# Configuration wires modules together
event_bus.subscribe(OrderPlaced, order_placed_handler.handle)
```

### 3. External Service Boundaries

**Purpose**: Isolate system from external dependencies (databases, APIs, frameworks).

**Example**: Application Core ↔ External Systems

```
┌────────────────────────────────────┐
│     Application Core               │
│                                    │
│  defines interfaces:               │
│  - IPaymentGateway                 │
│  - IEmailService                   │
│  - IOrderRepository                │
└────────────┬───────────────────────┘
             │
             │ boundary
             │
┌────────────┴───────────────────────┐
│    Adapters (Infrastructure)       │
│                                    │
│  implements interfaces:            │
│  - StripePaymentGateway           │
│  - SendGridEmailService           │
│  - PostgresOrderRepository         │
└────────────────────────────────────┘
```

**Crossing the Boundary**:

```python
# application/gateways.py (core defines interface)
class IPaymentGateway(ABC):
    """Interface defined by application core in domain terms."""

    @abstractmethod
    async def charge(self, amount: Money, method: PaymentMethod) -> PaymentResult:
        pass

# application/services.py (core uses interface)
class OrderService:
    def __init__(self, payment_gateway: IPaymentGateway):
        self._payment_gateway = payment_gateway

    async def process_order(self, order: Order) -> Result:
        # Core doesn't know about Stripe, just uses interface
        payment_result = await self._payment_gateway.charge(
            amount=order.total,
            method=order.payment_method
        )
        # ... handle result

# infrastructure/gateways/stripe_gateway.py (adapter implements)
import stripe

class StripePaymentGateway(IPaymentGateway):
    """Adapter that translates between core and Stripe API."""

    def __init__(self, api_key: str):
        stripe.api_key = api_key

    async def charge(self, amount: Money, method: PaymentMethod) -> PaymentResult:
        try:
            # Translate domain concepts to Stripe API
            charge = stripe.Charge.create(
                amount=int(amount.cents),
                currency=amount.currency.lower(),
                source=method.stripe_token
            )

            # Translate Stripe response to domain result
            return PaymentResult(
                success=True,
                transaction_id=charge.id,
                amount=amount
            )
        except stripe.error.CardError as e:
            return PaymentResult(success=False, error=str(e))
```

## When to Draw Boundaries

### Draw Boundaries Early

**At System Inception**: Draw major architectural boundaries (layers, modules) early. These boundaries guide system structure from the start.

- Separate business logic from infrastructure from the beginning
- Identify major business capabilities and create module boundaries
- Define core domain entities without coupling to frameworks

**When Requirements Are Clear**: Draw boundaries between stable, well-understood components and volatile, experimental components.

**Example**: Stable order processing logic vs. experimental recommendation engine

### Defer Boundary Drawing

**When Uncertainty Is High**: Don't create boundaries around things you don't understand yet. Wait until patterns emerge.

**For Small Systems**: Simple systems may not need elaborate boundaries initially. Start simple, refactor to boundaries when complexity increases.

**When Cost Exceeds Benefit**: Drawing boundaries has a cost (indirection, interfaces, complexity). Don't draw boundaries that don't pay for themselves.

### The Boundary Decision Matrix

| Factor | Draw Early | Can Defer |
|--------|------------|-----------|
| Core business logic vs. infrastructure | ✓ | |
| Stable policies vs. volatile details | ✓ | |
| Different teams working on components | ✓ | |
| Components with different deployment schedules | ✓ | |
| Third-party integrations | ✓ | |
| Well-understood domain separation | ✓ | |
| Experimental features | | ✓ |
| Small, simple systems | | ✓ |
| Unclear requirements | | ✓ |
| Internal implementation details of single component | | ✓ |

## How to Draw Boundaries

### Step 1: Identify Seams

Look for natural separation points in your system:

**Different Rates of Change**: Components that change frequently should be separated from components that change rarely.

```python
# Changes frequently: UI framework, CSS, layouts
# Should be separated from...
# Changes rarely: business calculation logic
```

**Different Reasons to Change**: Components that change for different stakeholders should be separated.

```python
# Changes for marketing team: email templates, notification content
# Should be separated from...
# Changes for engineering team: notification delivery mechanism
```

**Different Levels of Policy**: High-level policies (business rules) should be separated from low-level details (implementation).

```python
# High-level: "Orders must be validated before processing"
# Should be separated from...
# Low-level: "Store orders in PostgreSQL with this schema"
```

### Step 2: Define Interfaces at Boundaries

Create abstract interfaces that high-level components need, expressed in the language of the business domain.

**Anti-Pattern** (Leaky Abstraction):
```python
# BAD: Interface exposes implementation details
class IOrderStorage(ABC):
    @abstractmethod
    def execute_sql(self, query: str) -> List[dict]:
        """Execute SQL query."""
        pass
```

**Good Pattern** (Domain-Centric):
```python
# GOOD: Interface in domain language
class IOrderRepository(ABC):
    @abstractmethod
    async def find_pending_orders(self) -> List[Order]:
        """Retrieve all orders awaiting processing."""
        pass

    @abstractmethod
    async def mark_as_processed(self, order_id: str) -> None:
        """Mark an order as successfully processed."""
        pass
```

### Step 3: Enforce Dependency Direction

Ensure dependencies point from low-level details toward high-level policies.

**Enforcement Through Module Structure**:
```
src/
├── domain/           # No external dependencies
│   ├── entities.py
│   └── repositories.py  # Interfaces only
├── application/      # Depends only on domain
│   └── use_cases.py
└── infrastructure/   # Depends on domain and application
    └── persistence/
        └── postgres_repository.py  # Implements domain interfaces
```

**Enforcement Through Import Rules**:
```python
# domain/repositories.py - NO imports from infrastructure
from abc import ABC, abstractmethod
from domain.entities import Order

class IOrderRepository(ABC):
    pass

# infrastructure/persistence/postgres_repository.py - imports FROM domain
from domain.repositories import IOrderRepository  # ✓ Correct direction
from domain.entities import Order

class PostgresOrderRepository(IOrderRepository):
    pass
```

### Step 4: Use Dependency Injection

Wire implementations to interfaces at the composition root (main function or DI container).

```python
# main.py - Composition root
async def main():
    # Create infrastructure components (low-level details)
    db_pool = await asyncpg.create_pool(DATABASE_URL)
    repository = PostgresOrderRepository(db_pool)
    payment_gateway = StripePaymentGateway(STRIPE_API_KEY)

    # Inject into application components (high-level policy)
    use_case = ProcessOrderUseCase(
        repository=repository,
        payment_gateway=payment_gateway
    )

    # Run application
    await use_case.execute(order_request)
```

## Boundary Patterns

### Pattern 1: Hexagonal Architecture (Ports and Adapters)

**Structure**: Application core surrounded by adapters that connect to external systems.

```
                  ┌────────────────────┐
                  │                    │
       ┌──────────┤  Application Core  ├──────────┐
       │          │  (Business Logic)  │          │
       │          │                    │          │
       │          └────────────────────┘          │
       │                                          │
    Port (Interface)                         Port (Interface)
       │                                          │
       │                                          │
┌──────┴──────┐                          ┌───────┴──────┐
│  Adapter    │                          │   Adapter    │
│  (REST API) │                          │ (PostgreSQL) │
└─────────────┘                          └──────────────┘
```

**Example**:

```python
# Core defines ports (interfaces)
class IOrderService(ABC):
    """Port: How external world interacts with core."""
    @abstractmethod
    async def place_order(self, request: PlaceOrderRequest) -> PlaceOrderResponse:
        pass

class IOrderRepository(ABC):
    """Port: How core interacts with persistence."""
    @abstractmethod
    async def save(self, order: Order) -> None:
        pass

# Adapters implement ports
class RESTOrderController:
    """Adapter: Translates HTTP to domain operations."""

    def __init__(self, order_service: IOrderService):
        self._service = order_service

    async def handle_post_order(self, http_request: Request) -> Response:
        # Translate HTTP to domain
        domain_request = PlaceOrderRequest(
            customer_id=http_request.json['customer_id'],
            items=http_request.json['items']
        )

        # Call core
        result = await self._service.place_order(domain_request)

        # Translate domain to HTTP
        return Response(status=201, json={'order_id': result.order_id})

class PostgresOrderRepository(IOrderRepository):
    """Adapter: Translates domain to database operations."""

    async def save(self, order: Order) -> None:
        # Translate domain to SQL
        await self._db.execute(
            "INSERT INTO orders (id, customer_id) VALUES ($1, $2)",
            order.id, order.customer_id
        )
```

### Pattern 2: Onion Architecture

**Structure**: Concentric layers with dependencies pointing inward.

```
┌─────────────────────────────────────────┐
│  Infrastructure (outermost)             │
│  ┌───────────────────────────────────┐  │
│  │  Application Services             │  │
│  │  ┌─────────────────────────────┐  │  │
│  │  │  Domain Services            │  │  │
│  │  │  ┌───────────────────────┐  │  │  │
│  │  │  │  Domain Model (core)  │  │  │  │
│  │  │  └───────────────────────┘  │  │  │
│  │  └─────────────────────────────┘  │  │
│  └───────────────────────────────────┘  │
└─────────────────────────────────────────┘

    Dependencies point INWARD only ───→
```

**Example**:

```python
# Core: Domain Model (innermost)
class Order:
    """Pure domain logic, no dependencies."""

    def add_item(self, item: OrderItem) -> None:
        self.items.append(item)
        self._recalculate_total()

# Layer 2: Domain Services
class OrderValidator:
    """Domain service, depends only on domain model."""

    def validate(self, order: Order) -> ValidationResult:
        if not order.items:
            return ValidationResult(valid=False, errors=["Order has no items"])
        return ValidationResult(valid=True)

# Layer 3: Application Services
class OrderApplicationService:
    """Application logic, depends on domain."""

    def __init__(
        self,
        validator: OrderValidator,
        repository: IOrderRepository
    ):
        self._validator = validator
        self._repository = repository

    async def place_order(self, request: PlaceOrderRequest) -> Result:
        order = Order(request.customer_id)
        for item in request.items:
            order.add_item(item)

        validation = self._validator.validate(order)
        if not validation.valid:
            return Result(success=False, errors=validation.errors)

        await self._repository.save(order)
        return Result(success=True, order_id=order.id)

# Outermost: Infrastructure
class FastAPIController:
    """Infrastructure, depends on application services."""

    def __init__(self, order_service: OrderApplicationService):
        self._service = order_service

    @app.post("/orders")
    async def create_order(self, request: Request) -> Response:
        result = await self._service.place_order(request.json)
        return Response(status=201 if result.success else 400)
```

### Pattern 3: Clean Architecture Layers

**Structure**: Four-layer architecture with strict dependency rules.

```
Entities (innermost)
    ↑
Use Cases
    ↑
Interface Adapters
    ↑
Frameworks & Drivers (outermost)
```

**Example**: See DEPENDENCY_RULE.md for detailed explanation.

## Testing Across Boundaries

### Unit Testing Within Boundaries

Test components in isolation using test doubles for boundary interfaces.

```python
# tests/unit/test_order_service.py
import pytest
from unittest.mock import Mock
from application.services import OrderService
from domain.repositories import IOrderRepository

@pytest.mark.asyncio
async def test_order_service_places_order():
    # Arrange: Mock the boundary
    mock_repository = Mock(spec=IOrderRepository)
    mock_repository.save = AsyncMock()

    service = OrderService(repository=mock_repository)

    # Act: Test service without crossing boundary
    result = await service.place_order(order_request)

    # Assert
    assert result.success
    mock_repository.save.assert_called_once()
```

### Integration Testing Across Boundaries

Test that boundaries are properly crossed with real implementations.

```python
# tests/integration/test_order_repository.py
import pytest
import asyncpg
from infrastructure.persistence.postgres_repository import PostgresOrderRepository
from domain.entities import Order

@pytest.mark.integration
@pytest.mark.asyncio
async def test_repository_crosses_boundary_correctly(db_pool: asyncpg.Pool):
    # Arrange: Use real implementation
    repository = PostgresOrderRepository(db_pool)
    order = Order(customer_id="cust_123")

    # Act: Cross the boundary
    await repository.save(order)
    retrieved = await repository.find_by_id(order.id)

    # Assert: Verify boundary crossing works
    assert retrieved.id == order.id
    assert retrieved.customer_id == "cust_123"
```

### Contract Testing for Boundaries

Verify all implementations of a boundary satisfy the same contract.

```python
# tests/contracts/test_repository_contract.py
class RepositoryContractTests:
    """Contract tests that all repository implementations must pass."""

    @pytest.fixture
    def repository(self) -> IOrderRepository:
        """Override in subclass to provide implementation."""
        raise NotImplementedError

    @pytest.mark.asyncio
    async def test_save_and_retrieve(self, repository: IOrderRepository):
        """All repositories must support save and retrieve."""
        order = Order(customer_id="cust_123")
        await repository.save(order)
        retrieved = await repository.find_by_id(order.id)
        assert retrieved.id == order.id

# Test each implementation
class TestPostgresRepository(RepositoryContractTests):
    @pytest.fixture
    def repository(self, db_pool):
        return PostgresOrderRepository(db_pool)

class TestInMemoryRepository(RepositoryContractTests):
    @pytest.fixture
    def repository(self):
        return InMemoryOrderRepository()
```

## Common Boundary Mistakes

### Mistake 1: Bidirectional Dependencies

**Problem**: Components on both sides of boundary depend on each other.

```python
# BAD: Circular dependency across boundary
# domain/services.py
from infrastructure.database import Database  # Domain depends on infrastructure

class OrderService:
    def __init__(self):
        self.db = Database()  # Direct dependency

# infrastructure/database.py
from domain.entities import Order  # Infrastructure depends on domain

class Database:
    def save_order(self, order: Order):
        pass
```

**Fix**: Dependencies point one direction through interfaces.

```python
# GOOD: Unidirectional dependency
# domain/repositories.py
class IOrderRepository(ABC):
    @abstractmethod
    async def save(self, order: Order) -> None:
        pass

# domain/services.py
class OrderService:
    def __init__(self, repository: IOrderRepository):  # Depends on interface
        self._repository = repository

# infrastructure/database.py
from domain.repositories import IOrderRepository  # Implements interface

class PostgresOrderRepository(IOrderRepository):
    async def save(self, order: Order) -> None:
        pass
```

### Mistake 2: Business Logic in Infrastructure

**Problem**: Business rules leak across boundary into infrastructure layer.

```python
# BAD: Business rule in repository
class PostgresOrderRepository(IOrderRepository):
    async def save(self, order: Order) -> None:
        # Business rule: validate before saving
        if order.total > 10000:
            raise ValueError("Order too large")  # Business logic in infrastructure!

        await self._db.execute(...)
```

**Fix**: Business rules stay in domain layer.

```python
# GOOD: Business rule in domain
class Order:
    MAX_TOTAL = Money(10000, 'USD')

    def validate(self) -> None:
        if self.total > self.MAX_TOTAL:
            raise OrderTooLargeError(self.total)  # Business rule in domain

class PostgresOrderRepository(IOrderRepository):
    async def save(self, order: Order) -> None:
        # Just persistence, no business logic
        await self._db.execute(...)
```

### Mistake 3: Anemic Boundaries

**Problem**: Interfaces so generic they provide no boundary protection.

```python
# BAD: Generic CRUD interface provides no domain meaning
class IRepository(ABC):
    @abstractmethod
    def create(self, data: dict) -> str:
        pass

    @abstractmethod
    def read(self, id: str) -> dict:
        pass

    @abstractmethod
    def update(self, id: str, data: dict) -> None:
        pass

    @abstractmethod
    def delete(self, id: str) -> None:
        pass
```

**Fix**: Rich interfaces expressed in domain language.

```python
# GOOD: Domain-specific interface
class IOrderRepository(ABC):
    @abstractmethod
    async def find_orders_awaiting_shipment(self) -> List[Order]:
        """Domain-specific query."""
        pass

    @abstractmethod
    async def mark_as_shipped(self, order_id: str, tracking: TrackingInfo) -> None:
        """Domain operation."""
        pass
```

### Mistake 4: Premature Abstraction

**Problem**: Drawing boundaries before understanding the domain.

```python
# BAD: Over-abstracted before requirements are clear
class IDataAccessLayer(ABC):
    @abstractmethod
    def execute(self, operation: Operation) -> Result:
        pass

class IOperationFactory(ABC):
    @abstractmethod
    def create_operation(self, spec: OperationSpec) -> Operation:
        pass

# Too much abstraction for unclear requirements
```

**Fix**: Start simple, refactor to boundaries when patterns emerge.

```python
# GOOD: Start with direct implementation
class OrderRepository:
    """Simple, direct implementation."""

    async def save(self, order: Order) -> None:
        await self._db.execute(
            "INSERT INTO orders (id, customer_id) VALUES ($1, $2)",
            order.id, order.customer_id
        )

# Later, when you need flexibility, extract interface
class IOrderRepository(ABC):
    @abstractmethod
    async def save(self, order: Order) -> None:
        pass

class PostgresOrderRepository(IOrderRepository):
    # Move implementation here
    pass
```

## Key Takeaways

### Essential Principles

1. **Boundaries separate concerns**: Different rates of change, different reasons to change, different levels of policy
2. **Dependencies cross inward**: From low-level details toward high-level policies
3. **Interfaces at boundaries**: High-level components define interfaces, low-level implements
4. **Draw boundaries early for major separations**: Business logic from infrastructure, stable from volatile
5. **Defer boundaries when uncertain**: Don't draw lines you don't understand yet

### Boundary Checklist

- [ ] Business logic separated from infrastructure
- [ ] Dependencies point from details toward policies
- [ ] High-level components define interfaces they need
- [ ] Low-level components implement interfaces from above
- [ ] Can test high-level without low-level
- [ ] Can swap implementations without changing high-level
- [ ] Changes on one side don't force changes on other side

### When to Draw Boundaries

- [ ] Separating business logic from infrastructure: Always
- [ ] Isolating third-party dependencies: Early
- [ ] Between major business capabilities: When teams are separate
- [ ] Around experimental features: When experimenting
- [ ] Within small, simple components: Defer until complexity increases

## Related Resources

- **DEPENDENCY_RULE.md**: The fundamental rule that makes boundaries work
- **PLUGIN_ARCHITECTURE.md**: Practical patterns for crossing boundaries
- **SOLID_PRINCIPLES.md**: Especially Dependency Inversion Principle (DIP)
- **COMPONENT_PRINCIPLES.md**: Boundaries at component level

## Summary

Architectural boundaries are the lines that separate components with different reasons to change, different rates of change, and different levels of policy. Well-drawn boundaries protect high-level business logic from volatile implementation details, enable independent development and testing, and allow decisions about details to be deferred until you have better information.

The key insight: dependencies must cross boundaries in one direction only—from lower-level details toward higher-level policies. This is achieved through dependency inversion: high-level components define abstract interfaces (ports) that low-level components implement (adapters).

Draw boundaries between business logic and infrastructure early. Draw boundaries between components when teams need independence. Defer boundaries when requirements are unclear. Always ensure dependencies point toward stability.
