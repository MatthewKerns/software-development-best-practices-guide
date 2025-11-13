# Plugin Architecture: Building Flexible, Extensible Systems

## Overview

Plugin architecture is the architectural pattern that enables systems to remain open for extension while closed for modification. By treating external dependencies—databases, frameworks, UI, third-party services—as plugins to the core business logic rather than foundations it rests upon, we create systems that are flexible, testable, and independent of volatile details.

**"The history of software development technology is the story of how to conveniently create plugins to establish a scalable and maintainable system architecture."** — Robert C. Martin, Clean Architecture

Plugin architecture is the practical application of the Dependency Inversion Principle (DIP) at the system level. It inverts the typical dependency structure so that business logic defines interfaces that infrastructure implements, rather than business logic depending on infrastructure details.

## Why Plugin Architecture Matters

### The Cost of Framework-Centric Architecture

Traditional architectures build business logic on top of frameworks and infrastructure:

**Framework Lock-In**: Core business rules are written using framework-specific APIs. Upgrading or replacing the framework requires rewriting business logic.

**Untestable Code**: Business logic cannot be tested without starting web servers, connecting to databases, or invoking framework lifecycle methods.

**Coupled to Volatility**: Business rules depend on the most volatile parts of the system—UI frameworks, database schemas, third-party APIs—forcing constant changes to stable code.

**Difficult Migration**: Moving from monolith to microservices, from REST to GraphQL, from MySQL to PostgreSQL requires massive refactoring.

**Vendor Lock-In**: Cloud provider APIs, SaaS integrations, and proprietary tools become embedded in business logic, making switching prohibitively expensive.

### The Benefits of Plugin Architecture

Plugin-based systems provide:
- **Framework Independence**: Business logic has no knowledge of Spring, Django, React, or any framework
- **Testability**: Core rules tested with in-memory implementations, no infrastructure required
- **Deployment Flexibility**: Same business logic deployed as web app, CLI, batch job, or serverless function
- **Database Independence**: Switch from PostgreSQL to MongoDB to DynamoDB without touching business code
- **UI Independence**: Support web, mobile, desktop, voice interfaces with the same use cases
- **Easy Migration**: Replace infrastructure components without disrupting business logic

## Source Materials

This guide is based on:

- **Clean Architecture** by Robert C. Martin (Chapters 17-19)
  - Chapter 17: "Boundaries: Drawing Lines"
  - Chapter 18: "Boundary Anatomy"
  - Chapter 19: "Policy and Level"
  - The Plugin Argument
  - Architectural boundaries

## What is a Plugin?

A plugin is a component that implements an interface defined by another component but is not depended upon by that component. The component defining the interface doesn't know the plugin exists—the dependency points from the plugin toward the interface definition.

```
┌─────────────────┐         ┌──────────────────┐
│  Business Logic │         │   Database       │
│                 │         │   Plugin         │
│  defines:       │         │                  │
│  IRepository    │◄────────│  implements:     │
│                 │         │  IRepository     │
└─────────────────┘         └──────────────────┘
    (High-level)                 (Low-level)

    Dependency points toward interface definition ───→
```

### The Plugin Argument

In plugin architecture, the source code dependency opposes the flow of control at runtime:

**Runtime Flow**: Business Logic → calls → Database
**Source Code Dependency**: Database Plugin → implements interface defined by → Business Logic

This inversion is achieved through dependency inversion: the high-level component defines the interface it needs, and the low-level component implements that interface.

## Core Principles

### 1. Business Logic Defines Interfaces

The business logic layer defines the interfaces (ports) it needs to interact with external systems. These interfaces express needs in terms of the business domain, not technical implementation.

**Example: Repository Interface**

```python
# domain/repositories.py (Business Logic Layer)
from abc import ABC, abstractmethod
from typing import List, Optional
from domain.entities import Order

class IOrderRepository(ABC):
    """Interface defined by business logic for order persistence.

    This interface is expressed in domain terms, not database terms.
    Business logic defines what it needs without knowing how it will be implemented.
    """

    @abstractmethod
    async def find_by_id(self, order_id: str) -> Optional[Order]:
        """Retrieve an order by its unique identifier."""
        pass

    @abstractmethod
    async def find_by_customer(self, customer_id: str) -> List[Order]:
        """Find all orders for a specific customer."""
        pass

    @abstractmethod
    async def save(self, order: Order) -> None:
        """Persist an order."""
        pass

    @abstractmethod
    async def delete(self, order_id: str) -> None:
        """Remove an order from the system."""
        pass
```

### 2. Infrastructure Implements Interfaces

Infrastructure components (plugins) implement the interfaces defined by business logic. Multiple implementations can exist for different contexts: production databases, in-memory stores for testing, mock implementations for development.

**Example: PostgreSQL Plugin**

```python
# infrastructure/persistence/postgres_order_repository.py
import asyncpg
from typing import List, Optional
from domain.entities import Order
from domain.repositories import IOrderRepository

class PostgresOrderRepository(IOrderRepository):
    """PostgreSQL implementation of order repository.

    This plugin depends on the interface defined in the business logic layer.
    The business logic knows nothing about PostgreSQL.
    """

    def __init__(self, connection_pool: asyncpg.Pool):
        self._pool = connection_pool

    async def find_by_id(self, order_id: str) -> Optional[Order]:
        async with self._pool.acquire() as conn:
            row = await conn.fetchrow(
                "SELECT id, customer_id, total, status, created_at FROM orders WHERE id = $1",
                order_id
            )
            if not row:
                return None
            return self._row_to_order(row)

    async def find_by_customer(self, customer_id: str) -> List[Order]:
        async with self._pool.acquire() as conn:
            rows = await conn.fetch(
                "SELECT id, customer_id, total, status, created_at FROM orders WHERE customer_id = $1",
                customer_id
            )
            return [self._row_to_order(row) for row in rows]

    async def save(self, order: Order) -> None:
        async with self._pool.acquire() as conn:
            await conn.execute(
                """
                INSERT INTO orders (id, customer_id, total, status, created_at)
                VALUES ($1, $2, $3, $4, $5)
                ON CONFLICT (id) DO UPDATE SET
                    total = EXCLUDED.total,
                    status = EXCLUDED.status
                """,
                order.id, order.customer_id, order.total, order.status, order.created_at
            )

    async def delete(self, order_id: str) -> None:
        async with self._pool.acquire() as conn:
            await conn.execute("DELETE FROM orders WHERE id = $1", order_id)

    @staticmethod
    def _row_to_order(row) -> Order:
        """Convert database row to domain entity."""
        return Order(
            id=row['id'],
            customer_id=row['customer_id'],
            total=row['total'],
            status=row['status'],
            created_at=row['created_at']
        )
```

**Example: In-Memory Plugin for Testing**

```python
# infrastructure/persistence/in_memory_order_repository.py
from typing import Dict, List, Optional
from domain.entities import Order
from domain.repositories import IOrderRepository

class InMemoryOrderRepository(IOrderRepository):
    """In-memory implementation for testing.

    Same interface, different implementation. Business logic doesn't know or care.
    """

    def __init__(self):
        self._orders: Dict[str, Order] = {}

    async def find_by_id(self, order_id: str) -> Optional[Order]:
        return self._orders.get(order_id)

    async def find_by_customer(self, customer_id: str) -> List[Order]:
        return [
            order for order in self._orders.values()
            if order.customer_id == customer_id
        ]

    async def save(self, order: Order) -> None:
        self._orders[order.id] = order

    async def delete(self, order_id: str) -> None:
        self._orders.pop(order_id, None)
```

### 3. Dependency Injection Wires Plugins

The application's composition root (main function, dependency injection container) is responsible for creating plugins and injecting them into business logic components.

**Example: Dependency Injection**

```python
# infrastructure/di_container.py
import asyncpg
from domain.repositories import IOrderRepository
from domain.use_cases import ProcessOrderUseCase
from infrastructure.persistence.postgres_order_repository import PostgresOrderRepository
from infrastructure.persistence.in_memory_order_repository import InMemoryOrderRepository

class DIContainer:
    """Dependency injection container for wiring plugins."""

    def __init__(self, config: dict):
        self._config = config
        self._pool: Optional[asyncpg.Pool] = None

    async def initialize(self):
        """Initialize infrastructure components."""
        if self._config['environment'] == 'production':
            self._pool = await asyncpg.create_pool(
                self._config['database_url']
            )

    def get_order_repository(self) -> IOrderRepository:
        """Create and return appropriate repository implementation."""
        if self._config['environment'] == 'test':
            return InMemoryOrderRepository()
        elif self._config['environment'] == 'production':
            return PostgresOrderRepository(self._pool)
        else:
            raise ValueError(f"Unknown environment: {self._config['environment']}")

    def get_process_order_use_case(self) -> ProcessOrderUseCase:
        """Create use case with injected dependencies."""
        repository = self.get_order_repository()
        return ProcessOrderUseCase(repository)

# main.py
import asyncio
from infrastructure.di_container import DIContainer

async def main():
    # Composition root: where plugins are created and injected
    config = {
        'environment': 'production',
        'database_url': 'postgresql://...'
    }

    container = DIContainer(config)
    await container.initialize()

    # Use case receives plugin via dependency injection
    use_case = container.get_process_order_use_case()

    # Business logic executes without knowing which plugin is used
    await use_case.execute(order_data)

if __name__ == '__main__':
    asyncio.run(main())
```

## Plugin Architecture Patterns

### Pattern 1: Repository Plugin

**Use Case**: Decouple business logic from data persistence mechanisms.

**Structure**:
```
Domain Layer (Business Logic)
    ↓ defines
IRepository Interface
    ↑ implements
Persistence Layer (Plugins)
    - PostgresRepository
    - MongoRepository
    - InMemoryRepository
    - CacheDecoratorRepository
```

**Example**:

```python
# Domain defines what it needs
class IUserRepository(ABC):
    @abstractmethod
    async def find_by_email(self, email: str) -> Optional[User]:
        pass

# Plugin implements interface
class PostgresUserRepository(IUserRepository):
    async def find_by_email(self, email: str) -> Optional[User]:
        # PostgreSQL-specific implementation
        pass

# Another plugin for caching
class CachedUserRepository(IUserRepository):
    def __init__(self, repository: IUserRepository, cache: ICache):
        self._repository = repository
        self._cache = cache

    async def find_by_email(self, email: str) -> Optional[User]:
        cached = await self._cache.get(f"user:email:{email}")
        if cached:
            return cached
        user = await self._repository.find_by_email(email)
        if user:
            await self._cache.set(f"user:email:{email}", user)
        return user
```

### Pattern 2: Gateway Plugin

**Use Case**: Decouple business logic from external services and APIs.

**Structure**:
```
Domain Layer (Business Logic)
    ↓ defines
IPaymentGateway Interface
    ↑ implements
Infrastructure Layer (Plugins)
    - StripePaymentGateway
    - PayPalPaymentGateway
    - MockPaymentGateway
```

**Example**:

```python
# domain/gateways.py
from abc import ABC, abstractmethod
from domain.value_objects import Money, PaymentResult

class IPaymentGateway(ABC):
    """Interface for payment processing.

    Business logic defines this in domain terms, not in terms of
    Stripe API or PayPal SDK.
    """

    @abstractmethod
    async def charge(self, amount: Money, payment_method: str) -> PaymentResult:
        """Charge a payment method for the specified amount."""
        pass

    @abstractmethod
    async def refund(self, transaction_id: str, amount: Money) -> PaymentResult:
        """Refund a previous transaction."""
        pass

# infrastructure/gateways/stripe_payment_gateway.py
import stripe
from domain.gateways import IPaymentGateway
from domain.value_objects import Money, PaymentResult

class StripePaymentGateway(IPaymentGateway):
    """Stripe implementation of payment gateway."""

    def __init__(self, api_key: str):
        stripe.api_key = api_key

    async def charge(self, amount: Money, payment_method: str) -> PaymentResult:
        try:
            charge = stripe.Charge.create(
                amount=int(amount.cents),
                currency=amount.currency.lower(),
                source=payment_method
            )
            return PaymentResult(
                success=True,
                transaction_id=charge.id,
                amount=amount
            )
        except stripe.error.CardError as e:
            return PaymentResult(
                success=False,
                error_message=str(e)
            )

    async def refund(self, transaction_id: str, amount: Money) -> PaymentResult:
        try:
            refund = stripe.Refund.create(
                charge=transaction_id,
                amount=int(amount.cents)
            )
            return PaymentResult(
                success=True,
                transaction_id=refund.id,
                amount=amount
            )
        except stripe.error.StripeError as e:
            return PaymentResult(
                success=False,
                error_message=str(e)
            )

# infrastructure/gateways/mock_payment_gateway.py
class MockPaymentGateway(IPaymentGateway):
    """Mock implementation for testing and development."""

    async def charge(self, amount: Money, payment_method: str) -> PaymentResult:
        # Always succeeds in test environment
        return PaymentResult(
            success=True,
            transaction_id=f"mock_{uuid.uuid4()}",
            amount=amount
        )

    async def refund(self, transaction_id: str, amount: Money) -> PaymentResult:
        return PaymentResult(
            success=True,
            transaction_id=f"refund_{uuid.uuid4()}",
            amount=amount
        )
```

### Pattern 3: Presenter Plugin

**Use Case**: Decouple business logic from UI/presentation formats.

**Structure**:
```
Application Layer (Use Cases)
    ↓ defines
IPresenter Interface
    ↑ implements
Presentation Layer (Plugins)
    - JSONPresenter (REST API)
    - HTMLPresenter (Web UI)
    - CLIPresenter (Command Line)
    - GraphQLPresenter (GraphQL API)
```

**Example**:

```python
# application/presenters.py
from abc import ABC, abstractmethod
from domain.entities import Order

class IOrderPresenter(ABC):
    """Interface for presenting order data.

    Business logic produces domain entities. Presenters convert
    to format appropriate for the delivery mechanism.
    """

    @abstractmethod
    def present_order(self, order: Order) -> Any:
        """Convert order to presentation format."""
        pass

    @abstractmethod
    def present_order_list(self, orders: List[Order]) -> Any:
        """Convert list of orders to presentation format."""
        pass

# presentation/rest/json_order_presenter.py
from typing import Any, List
from domain.entities import Order
from application.presenters import IOrderPresenter

class JSONOrderPresenter(IOrderPresenter):
    """JSON presentation for REST API."""

    def present_order(self, order: Order) -> dict:
        return {
            'id': order.id,
            'customer_id': order.customer_id,
            'total': {
                'amount': order.total.amount,
                'currency': order.total.currency
            },
            'status': order.status.value,
            'created_at': order.created_at.isoformat()
        }

    def present_order_list(self, orders: List[Order]) -> dict:
        return {
            'orders': [self.present_order(order) for order in orders],
            'count': len(orders)
        }

# presentation/cli/cli_order_presenter.py
class CLIOrderPresenter(IOrderPresenter):
    """Command-line presentation."""

    def present_order(self, order: Order) -> str:
        return f"""
Order #{order.id}
Customer: {order.customer_id}
Total: {order.total.amount} {order.total.currency}
Status: {order.status.value}
Created: {order.created_at.strftime('%Y-%m-%d %H:%M')}
        """.strip()

    def present_order_list(self, orders: List[Order]) -> str:
        if not orders:
            return "No orders found."

        lines = [f"Found {len(orders)} orders:\n"]
        for order in orders:
            lines.append(f"  #{order.id} - {order.total.amount} {order.total.currency} - {order.status.value}")
        return "\n".join(lines)
```

### Pattern 4: Event Bus Plugin

**Use Case**: Decouple components through event-driven communication.

**Structure**:
```
Domain Layer
    ↓ defines
IDomainEventBus Interface
    ↑ implements
Infrastructure Layer (Plugins)
    - InMemoryEventBus
    - RedisEventBus
    - KafkaEventBus
    - RabbitMQEventBus
```

**Example**:

```python
# domain/events.py
from abc import ABC, abstractmethod
from typing import Callable, List
from dataclasses import dataclass
from datetime import datetime

@dataclass
class DomainEvent:
    """Base class for domain events."""
    occurred_at: datetime
    aggregate_id: str

@dataclass
class OrderPlaced(DomainEvent):
    """Event raised when an order is placed."""
    customer_id: str
    total_amount: float

class IDomainEventBus(ABC):
    """Interface for publishing and subscribing to domain events."""

    @abstractmethod
    def publish(self, event: DomainEvent) -> None:
        """Publish an event to all subscribers."""
        pass

    @abstractmethod
    def subscribe(self, event_type: type, handler: Callable[[DomainEvent], None]) -> None:
        """Subscribe to events of a specific type."""
        pass

# infrastructure/events/in_memory_event_bus.py
from collections import defaultdict
from typing import Callable, Dict, List
from domain.events import DomainEvent, IDomainEventBus

class InMemoryEventBus(IDomainEventBus):
    """In-memory event bus for testing and simple scenarios."""

    def __init__(self):
        self._subscribers: Dict[type, List[Callable]] = defaultdict(list)

    def publish(self, event: DomainEvent) -> None:
        event_type = type(event)
        for handler in self._subscribers[event_type]:
            handler(event)

    def subscribe(self, event_type: type, handler: Callable[[DomainEvent], None]) -> None:
        self._subscribers[event_type].append(handler)

# infrastructure/events/redis_event_bus.py
import redis
import json
from domain.events import DomainEvent, IDomainEventBus

class RedisEventBus(IDomainEventBus):
    """Redis pub/sub implementation for distributed systems."""

    def __init__(self, redis_client: redis.Redis):
        self._redis = redis_client
        self._pubsub = self._redis.pubsub()

    def publish(self, event: DomainEvent) -> None:
        channel = event.__class__.__name__
        payload = json.dumps({
            'occurred_at': event.occurred_at.isoformat(),
            'aggregate_id': event.aggregate_id,
            'data': event.__dict__
        })
        self._redis.publish(channel, payload)

    def subscribe(self, event_type: type, handler: Callable[[DomainEvent], None]) -> None:
        channel = event_type.__name__
        self._pubsub.subscribe(channel)

        for message in self._pubsub.listen():
            if message['type'] == 'message':
                event_data = json.loads(message['data'])
                event = event_type(**event_data['data'])
                handler(event)
```

## Testing with Plugin Architecture

Plugin architecture makes testing dramatically simpler because you can replace real plugins with test doubles.

### Unit Testing Use Cases

```python
# tests/unit/test_process_order_use_case.py
import pytest
from domain.use_cases import ProcessOrderUseCase
from infrastructure.persistence.in_memory_order_repository import InMemoryOrderRepository

@pytest.mark.asyncio
async def test_process_order_creates_order():
    # Arrange: Use in-memory plugin for testing
    repository = InMemoryOrderRepository()
    use_case = ProcessOrderUseCase(repository)

    order_data = {
        'customer_id': 'cust_123',
        'items': [{'product_id': 'prod_1', 'quantity': 2}]
    }

    # Act
    result = await use_case.execute(order_data)

    # Assert: Verify business logic without database
    assert result.success
    saved_order = await repository.find_by_id(result.order_id)
    assert saved_order is not None
    assert saved_order.customer_id == 'cust_123'
```

### Integration Testing with Real Plugins

```python
# tests/integration/test_postgres_order_repository.py
import pytest
import asyncpg
from infrastructure.persistence.postgres_order_repository import PostgresOrderRepository
from domain.entities import Order

@pytest.mark.integration
@pytest.mark.asyncio
async def test_postgres_repository_saves_and_retrieves_order(db_pool: asyncpg.Pool):
    # Arrange: Use real PostgreSQL plugin
    repository = PostgresOrderRepository(db_pool)

    order = Order(
        id='order_123',
        customer_id='cust_456',
        total=Money(amount=99.99, currency='USD'),
        status=OrderStatus.PENDING
    )

    # Act
    await repository.save(order)
    retrieved = await repository.find_by_id('order_123')

    # Assert: Verify actual persistence
    assert retrieved is not None
    assert retrieved.customer_id == 'cust_456'
    assert retrieved.total.amount == 99.99
```

### Testing with Multiple Plugin Implementations

```python
# tests/test_repository_contract.py
import pytest
from typing import Type
from domain.repositories import IOrderRepository

class RepositoryContractTests:
    """Contract tests that all repository implementations must pass."""

    @pytest.fixture
    def repository(self) -> IOrderRepository:
        """Override in subclass to provide specific implementation."""
        raise NotImplementedError

    @pytest.mark.asyncio
    async def test_save_and_retrieve(self, repository: IOrderRepository):
        order = create_test_order()
        await repository.save(order)
        retrieved = await repository.find_by_id(order.id)
        assert retrieved.id == order.id

    @pytest.mark.asyncio
    async def test_delete_removes_order(self, repository: IOrderRepository):
        order = create_test_order()
        await repository.save(order)
        await repository.delete(order.id)
        retrieved = await repository.find_by_id(order.id)
        assert retrieved is None

# Test in-memory implementation
class TestInMemoryRepository(RepositoryContractTests):
    @pytest.fixture
    def repository(self):
        return InMemoryOrderRepository()

# Test PostgreSQL implementation
class TestPostgresRepository(RepositoryContractTests):
    @pytest.fixture
    def repository(self, db_pool):
        return PostgresOrderRepository(db_pool)
```

## Common Plugin Scenarios

### Scenario 1: Database Migration

**Problem**: Migrating from PostgreSQL to MongoDB without disrupting business logic.

**Solution**:

```python
# Step 1: Business logic already uses IOrderRepository interface
# No changes needed to use cases or domain logic

# Step 2: Create MongoDB plugin
class MongoOrderRepository(IOrderRepository):
    def __init__(self, mongo_client: motor.AsyncIOMotorClient):
        self._db = mongo_client.orders_db
        self._collection = self._db.orders

    async def find_by_id(self, order_id: str) -> Optional[Order]:
        doc = await self._collection.find_one({'_id': order_id})
        if not doc:
            return None
        return self._doc_to_order(doc)

    # ... implement other interface methods

# Step 3: Update composition root to use MongoDB plugin
def get_order_repository() -> IOrderRepository:
    if config['database'] == 'postgres':
        return PostgresOrderRepository(pg_pool)
    elif config['database'] == 'mongodb':
        return MongoOrderRepository(mongo_client)
```

**Result**: Zero changes to business logic. Migration isolated to infrastructure layer.

### Scenario 2: Multi-Cloud Deployment

**Problem**: Support deployment to AWS, Google Cloud, and Azure with different storage mechanisms.

**Solution**:

```python
# domain/storage.py
class IFileStorage(ABC):
    @abstractmethod
    async def store(self, key: str, content: bytes) -> str:
        """Store file and return URL."""
        pass

    @abstractmethod
    async def retrieve(self, key: str) -> bytes:
        """Retrieve file content."""
        pass

# infrastructure/storage/s3_file_storage.py
import boto3
class S3FileStorage(IFileStorage):
    def __init__(self, bucket: str, region: str):
        self._s3 = boto3.client('s3', region_name=region)
        self._bucket = bucket

    async def store(self, key: str, content: bytes) -> str:
        self._s3.put_object(Bucket=self._bucket, Key=key, Body=content)
        return f"https://{self._bucket}.s3.amazonaws.com/{key}"

# infrastructure/storage/gcs_file_storage.py
from google.cloud import storage
class GCSFileStorage(IFileStorage):
    def __init__(self, bucket: str):
        self._client = storage.Client()
        self._bucket = self._client.bucket(bucket)

    async def store(self, key: str, content: bytes) -> str:
        blob = self._bucket.blob(key)
        blob.upload_from_string(content)
        return f"https://storage.googleapis.com/{self._bucket.name}/{key}"

# infrastructure/storage/azure_blob_storage.py
from azure.storage.blob import BlobServiceClient
class AzureBlobStorage(IFileStorage):
    def __init__(self, connection_string: str, container: str):
        self._blob_service = BlobServiceClient.from_connection_string(connection_string)
        self._container = container

    async def store(self, key: str, content: bytes) -> str:
        blob_client = self._blob_service.get_blob_client(self._container, key)
        blob_client.upload_blob(content)
        return blob_client.url

# Configuration-driven plugin selection
def create_file_storage(config: dict) -> IFileStorage:
    provider = config['cloud_provider']
    if provider == 'aws':
        return S3FileStorage(config['bucket'], config['region'])
    elif provider == 'gcp':
        return GCSFileStorage(config['bucket'])
    elif provider == 'azure':
        return AzureBlobStorage(config['connection_string'], config['container'])
```

### Scenario 3: A/B Testing Payment Providers

**Problem**: Test new payment provider while keeping existing one as fallback.

**Solution**:

```python
# infrastructure/gateways/split_payment_gateway.py
class SplitPaymentGateway(IPaymentGateway):
    """Route traffic between two payment gateways for A/B testing."""

    def __init__(
        self,
        primary: IPaymentGateway,
        secondary: IPaymentGateway,
        split_percentage: int = 10
    ):
        self._primary = primary
        self._secondary = secondary
        self._split_percentage = split_percentage

    async def charge(self, amount: Money, payment_method: str) -> PaymentResult:
        # Route split_percentage% of traffic to secondary gateway
        if random.randint(1, 100) <= self._split_percentage:
            logger.info("Routing to secondary payment gateway")
            result = await self._secondary.charge(amount, payment_method)
            if not result.success:
                # Fallback to primary if secondary fails
                logger.warning("Secondary gateway failed, falling back to primary")
                result = await self._primary.charge(amount, payment_method)
            return result
        else:
            return await self._primary.charge(amount, payment_method)

    async def refund(self, transaction_id: str, amount: Money) -> PaymentResult:
        # Determine which gateway processed the original transaction
        # and route refund accordingly
        pass

# Composition root
def create_payment_gateway(config: dict) -> IPaymentGateway:
    stripe = StripePaymentGateway(config['stripe_key'])

    if config.get('ab_test_payment_provider'):
        braintree = BraintreePaymentGateway(config['braintree_key'])
        return SplitPaymentGateway(
            primary=stripe,
            secondary=braintree,
            split_percentage=config['split_percentage']
        )

    return stripe
```

## Anti-Patterns to Avoid

### Anti-Pattern 1: Leaky Abstractions

**Problem**: Interface exposes implementation details.

```python
# BAD: Repository interface exposes SQL
class IOrderRepository(ABC):
    @abstractmethod
    def execute_query(self, sql: str, params: tuple) -> List[dict]:
        """Execute raw SQL query."""
        pass
```

**Fix**: Interface expressed in domain terms.

```python
# GOOD: Repository interface in domain language
class IOrderRepository(ABC):
    @abstractmethod
    def find_by_status(self, status: OrderStatus) -> List[Order]:
        """Find orders by status."""
        pass
```

### Anti-Pattern 2: Business Logic in Plugins

**Problem**: Plugin contains business rules.

```python
# BAD: Business logic in repository
class PostgresOrderRepository(IOrderRepository):
    async def save(self, order: Order) -> None:
        # Business rule: Don't allow orders over $10,000
        if order.total.amount > 10000:
            raise ValueError("Order exceeds maximum amount")

        await self._db.execute(...)
```

**Fix**: Business rules in domain layer.

```python
# GOOD: Business rules in domain entity
class Order:
    MAX_ORDER_AMOUNT = Money(10000, 'USD')

    def validate(self) -> None:
        if self.total > self.MAX_ORDER_AMOUNT:
            raise OrderExceedsMaximumError(self.total, self.MAX_ORDER_AMOUNT)

# Repository just persists
class PostgresOrderRepository(IOrderRepository):
    async def save(self, order: Order) -> None:
        # No business logic, just persistence
        await self._db.execute(...)
```

### Anti-Pattern 3: Anemic Interfaces

**Problem**: Interface has too few methods, forcing clients to do complex operations.

```python
# BAD: Too granular, forces clients to know implementation
class IOrderRepository(ABC):
    @abstractmethod
    def insert(self, table: str, values: dict) -> None:
        pass

    @abstractmethod
    def update(self, table: str, id: str, values: dict) -> None:
        pass
```

**Fix**: Interface at appropriate abstraction level.

```python
# GOOD: Rich interface at domain level
class IOrderRepository(ABC):
    @abstractmethod
    async def save(self, order: Order) -> None:
        """Save order (create or update)."""
        pass

    @abstractmethod
    async def find_pending_orders_for_customer(self, customer_id: str) -> List[Order]:
        """Find all pending orders for a customer."""
        pass
```

### Anti-Pattern 4: God Interfaces

**Problem**: Interface tries to serve too many clients with different needs.

```python
# BAD: One interface for all order operations
class IOrderRepository(ABC):
    # Used by order processing
    async def save(self, order: Order) -> None: pass
    async def find_by_id(self, order_id: str) -> Optional[Order]: pass

    # Used by analytics
    async def count_orders_by_date(self, start: date, end: date) -> int: pass
    async def calculate_revenue(self, period: str) -> float: pass

    # Used by reporting
    async def generate_sales_report(self, format: str) -> bytes: pass
    async def export_to_csv(self) -> str: pass
```

**Fix**: Segregate interfaces by client needs (Interface Segregation Principle).

```python
# GOOD: Separate interfaces for different clients
class IOrderRepository(ABC):
    """Core order persistence for order processing."""
    async def save(self, order: Order) -> None: pass
    async def find_by_id(self, order_id: str) -> Optional[Order]: pass

class IOrderAnalytics(ABC):
    """Order analytics for business intelligence."""
    async def count_orders_by_date(self, start: date, end: date) -> int: pass
    async def calculate_revenue(self, period: str) -> float: pass

class IOrderReporting(ABC):
    """Order reporting for management."""
    async def generate_sales_report(self, format: str) -> bytes: pass
    async def export_to_csv(self) -> str: pass
```

## Key Takeaways

### Essential Principles

1. **High-level policy defines interfaces**: Business logic dictates its needs through abstract interfaces
2. **Low-level details implement interfaces**: Infrastructure provides concrete implementations
3. **Dependencies point inward**: Plugins depend on business logic, never the reverse
4. **Multiple implementations**: Same interface, different contexts (production, testing, development)
5. **Dependency injection wires plugins**: Composition root creates and injects plugins

### Benefits Checklist

- [ ] Business logic has zero dependencies on frameworks
- [ ] Can test use cases without infrastructure
- [ ] Can swap databases without touching business code
- [ ] Can deploy same logic to different platforms
- [ ] Can replace external services easily
- [ ] UI changes don't affect business rules
- [ ] Framework upgrades are isolated to infrastructure layer

### Implementation Checklist

- [ ] Domain layer defines all external interfaces
- [ ] Infrastructure layer implements those interfaces
- [ ] Business logic only depends on interfaces, not implementations
- [ ] Dependency injection container wires plugins to business logic
- [ ] Each plugin has in-memory equivalent for testing
- [ ] Tests verify business logic without infrastructure
- [ ] Plugin implementations are in separate modules/packages

## Related Resources

- **SOLID_PRINCIPLES.md**: Foundation principles, especially DIP
- **DEPENDENCY_RULE.md**: Architectural manifestation of plugin pattern
- **ARCHITECTURAL_BOUNDARIES.md**: Where to draw lines between components
- **COMPONENT_PRINCIPLES.md**: How to organize plugins into components

## Summary

Plugin architecture inverts the traditional dependency structure: instead of building business logic on top of frameworks and databases, we build frameworks and databases as plugins to business logic. This inversion—achieved through dependency inversion and interface definition at the business logic layer—creates systems that are flexible, testable, and independent of volatile technical details.

Every external dependency—database, web framework, third-party API, UI library—should be a plugin to your core business logic, not a foundation it rests upon.
