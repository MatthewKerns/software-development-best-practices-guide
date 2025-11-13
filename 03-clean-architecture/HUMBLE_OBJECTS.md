# Humble Objects: Separating Testable from Hard-to-Test

## Overview

The Humble Object pattern is a design technique that splits behaviors into two modules: one that is easy to test and one that is hard to test. The hard-to-test module is kept "humble"—stripped of all complex logic—while the easy-to-test module contains all the important behavior.

**"The Humble Object pattern is a way to separate the hard-to-test behaviors from the easy-to-test behaviors."** — Robert C. Martin, Clean Architecture

This pattern is essential when dealing with GUI frameworks, databases, external services, and other components that are difficult or slow to test. By extracting testable logic from these components, we can achieve high test coverage with fast, reliable unit tests rather than slow, brittle integration tests.

## Why Humble Objects Matter

### The Cost of Testing Everything with Integration Tests

Testing all logic through hard-to-test components creates:

**Slow Test Suites**: GUI tests take seconds or minutes. Database tests require setup and teardown. API tests depend on external services. Test suites take hours to run.

**Brittle Tests**: Tests fail due to timing issues, environment problems, or external service outages—not because business logic is broken.

**Low Coverage**: Integration tests are expensive to write and maintain, so teams write fewer of them, leaving logic untested.

**Difficult Debugging**: When integration tests fail, it's unclear whether the problem is business logic, infrastructure, test environment, or timing.

**Feedback Delay**: Developers wait minutes for test results instead of getting instant feedback from unit tests.

### The Benefits of Humble Objects

Separating humble objects from testable logic provides:
- **Fast Tests**: Unit tests run in milliseconds, not seconds
- **High Coverage**: Easy to test means more tests get written
- **Reliable Tests**: Pure logic tests don't fail due to infrastructure issues
- **Quick Feedback**: Developers get instant feedback during development
- **Simplified Debugging**: Test failures clearly indicate logic problems
- **Decoupled Design**: Separating concerns improves overall architecture

## Source Materials

This guide is based on:

- **Clean Architecture** by Robert C. Martin (Chapter 23: "Presenters and Humble Objects")
  - The Humble Object pattern
  - Presenters as humble objects
  - Testing boundaries

## The Humble Object Pattern

### Core Principle

Split behavior into two parts:
1. **Humble Component**: Contains hard-to-test code with minimal logic
2. **Testable Component**: Contains all important logic and is easy to test

The humble component depends on the testable component, not vice versa. The testable component has no knowledge of the humble component.

### Pattern Structure

```
┌─────────────────────────────────────┐
│  Humble Object                      │
│  (Hard to test: GUI, DB, External)  │
│                                     │
│  - Minimal logic                    │
│  - Calls testable component         │
│  - Handles infrastructure           │
└──────────────┬──────────────────────┘
               │
               │ depends on
               ↓
┌──────────────┴──────────────────────┐
│  Testable Component                 │
│  (Easy to test: Pure logic)         │
│                                     │
│  - All important logic              │
│  - No infrastructure dependencies   │
│  - Easily unit tested               │
└─────────────────────────────────────┘
```

## Common Applications

### 1. Presenters (View Models)

**Problem**: Views (UI) are hard to test. Testing requires rendering frameworks, browsers, or GUI toolkits.

**Solution**: Extract presentation logic into a testable Presenter. The View becomes humble—just data binding with no logic.

**Anti-Pattern (Fat View)**:
```python
# BAD: All logic in the view (hard to test)
class OrderView:
    def __init__(self, web_framework):
        self.framework = web_framework

    async def display_order(self, order_id: str):
        # Mix of data retrieval, business logic, and formatting
        order = await database.fetch_order(order_id)

        # Business logic in view
        if order.status == 'pending':
            status_color = 'yellow'
            status_text = 'Awaiting Payment'
        elif order.status == 'confirmed':
            status_color = 'green'
            status_text = 'Order Confirmed'
        else:
            status_color = 'red'
            status_text = 'Cancelled'

        # Formatting logic in view
        total = f"${order.total:.2f}"
        created_date = order.created_at.strftime("%B %d, %Y")

        # Display logic in view
        self.framework.render_template('order.html', {
            'order_id': order.id,
            'status_color': status_color,
            'status_text': status_text,
            'total': total,
            'created_date': created_date
        })
```

**Good Pattern (Humble View + Testable Presenter)**:
```python
# GOOD: Testable presenter with all logic
class OrderPresenter:
    """Testable presenter containing all presentation logic."""

    def __init__(self, order_repository: IOrderRepository):
        self._orders = order_repository

    async def present_order(self, order_id: str) -> OrderViewModel:
        """
        Prepare order data for display.
        Contains all formatting and presentation logic.
        Easily testable with unit tests.
        """
        order = await self._orders.find_by_id(order_id)

        if not order:
            return OrderViewModel(error="Order not found")

        # Presentation logic (testable)
        status_display = self._format_status(order.status)
        total_display = self._format_money(order.total)
        date_display = self._format_date(order.created_at)

        return OrderViewModel(
            order_id=order.id,
            status_text=status_display.text,
            status_color=status_display.color,
            total=total_display,
            created_date=date_display,
            items=[self._format_item(item) for item in order.items]
        )

    def _format_status(self, status: OrderStatus) -> StatusDisplay:
        """Business rule: How to display each status."""
        status_map = {
            OrderStatus.PENDING: StatusDisplay(text="Awaiting Payment", color="yellow"),
            OrderStatus.CONFIRMED: StatusDisplay(text="Order Confirmed", color="green"),
            OrderStatus.SHIPPED: StatusDisplay(text="Shipped", color="blue"),
            OrderStatus.CANCELLED: StatusDisplay(text="Cancelled", color="red")
        }
        return status_map.get(status, StatusDisplay(text="Unknown", color="gray"))

    def _format_money(self, amount: Money) -> str:
        """Formatting rule: Money display."""
        return f"${amount.amount:.2f}"

    def _format_date(self, date: datetime) -> str:
        """Formatting rule: Date display."""
        return date.strftime("%B %d, %Y")

    def _format_item(self, item: OrderItem) -> OrderItemViewModel:
        """Format individual order item."""
        return OrderItemViewModel(
            product_name=item.product_name,
            quantity=item.quantity,
            price=self._format_money(item.unit_price),
            total=self._format_money(item.unit_price * item.quantity)
        )


@dataclass
class OrderViewModel:
    """View model: Simple data structure for the view."""
    order_id: Optional[str] = None
    status_text: Optional[str] = None
    status_color: Optional[str] = None
    total: Optional[str] = None
    created_date: Optional[str] = None
    items: List[OrderItemViewModel] = None
    error: Optional[str] = None


# Humble view: Just data binding, no logic
class OrderView:
    """Humble view: Minimal logic, just renders data."""

    def __init__(self, web_framework, presenter: OrderPresenter):
        self.framework = web_framework
        self.presenter = presenter

    async def display_order(self, order_id: str):
        # Get formatted data from presenter
        view_model = await self.presenter.present_order(order_id)

        # Just render—no logic
        if view_model.error:
            self.framework.render_error(view_model.error)
        else:
            self.framework.render_template('order.html', view_model)
```

**Testing**:
```python
# tests/unit/test_order_presenter.py
import pytest
from presenters.order_presenter import OrderPresenter

@pytest.mark.asyncio
async def test_presenter_formats_pending_order_correctly():
    """Test presenter logic without touching the UI framework."""
    # Arrange: Mock repository
    mock_repo = Mock()
    mock_repo.find_by_id = AsyncMock(return_value=Order(
        id="order_123",
        status=OrderStatus.PENDING,
        total=Money(Decimal("99.99")),
        created_at=datetime(2024, 1, 15)
    ))

    presenter = OrderPresenter(mock_repo)

    # Act: Test presentation logic
    view_model = await presenter.present_order("order_123")

    # Assert: Verify formatting (no UI framework needed)
    assert view_model.status_text == "Awaiting Payment"
    assert view_model.status_color == "yellow"
    assert view_model.total == "$99.99"
    assert view_model.created_date == "January 15, 2024"
```

### 2. Database Boundaries

**Problem**: Database operations are slow and require setup. Testing through database is painful.

**Solution**: Extract business logic from database operations. Use repository interfaces with in-memory implementations for testing.

**Anti-Pattern (Business Logic in Repository)**:
```python
# BAD: Business logic mixed with database operations
class OrderRepository:
    async def save_order(self, order_data: dict):
        # Business logic in repository (hard to test)
        if order_data['total'] > 10000:
            order_data['requires_approval'] = True
            order_data['status'] = 'pending_approval'
        else:
            order_data['status'] = 'confirmed'

        # Calculate discount in repository
        if order_data['customer_tier'] == 'premium':
            order_data['discount'] = order_data['total'] * 0.1

        # Database operation
        await self.db.execute(
            "INSERT INTO orders (id, total, status, discount) VALUES ($1, $2, $3, $4)",
            order_data['id'], order_data['total'],
            order_data['status'], order_data['discount']
        )
```

**Good Pattern (Pure Entity + Humble Repository)**:
```python
# GOOD: Business logic in entity (testable)
class Order:
    """Testable entity with all business logic."""

    MAX_AUTO_APPROVE_AMOUNT = Money(Decimal("10000"))

    def __init__(self, customer_id: str, customer_tier: str):
        self.id = str(uuid.uuid4())
        self.customer_id = customer_id
        self.customer_tier = customer_tier
        self.items: List[OrderItem] = []
        self.status = OrderStatus.PENDING

    def calculate_total(self) -> Money:
        """Business logic: Calculate total."""
        return sum(item.price * item.quantity for item in self.items)

    def calculate_discount(self) -> Money:
        """Business logic: Calculate discount based on tier."""
        total = self.calculate_total()
        if self.customer_tier == 'premium':
            return Money(total.amount * Decimal("0.1"))
        return Money(Decimal("0"))

    def requires_approval(self) -> bool:
        """Business rule: Orders over $10k need approval."""
        return self.calculate_total() > self.MAX_AUTO_APPROVE_AMOUNT

    def determine_initial_status(self) -> OrderStatus:
        """Business rule: Determine initial order status."""
        if self.requires_approval():
            return OrderStatus.PENDING_APPROVAL
        return OrderStatus.CONFIRMED


# Humble repository: Just persistence, no logic
class PostgresOrderRepository(IOrderRepository):
    """Humble repository: Minimal logic, just persistence."""

    async def save(self, order: Order) -> None:
        """Save order to database—no business logic."""
        await self.db.execute(
            """
            INSERT INTO orders (id, customer_id, total, discount, status)
            VALUES ($1, $2, $3, $4, $5)
            """,
            order.id,
            order.customer_id,
            order.calculate_total().amount,
            order.calculate_discount().amount,
            order.determine_initial_status().value
        )
```

**Testing**:
```python
# tests/unit/test_order_entity.py
def test_order_requires_approval_for_large_orders():
    """Test business logic without database."""
    # Arrange
    order = Order(customer_id="cust_123", customer_tier="standard")
    order.add_item(OrderItem(price=Money(Decimal("15000")), quantity=1))

    # Act
    requires_approval = order.requires_approval()

    # Assert
    assert requires_approval == True


def test_premium_customer_gets_discount():
    """Test business logic without database."""
    # Arrange
    order = Order(customer_id="cust_123", customer_tier="premium")
    order.add_item(OrderItem(price=Money(Decimal("100")), quantity=1))

    # Act
    discount = order.calculate_discount()

    # Assert
    assert discount.amount == Decimal("10.00")
```

### 3. External Service Boundaries

**Problem**: External services (APIs, payment processors, email providers) are slow, unreliable, and require credentials.

**Solution**: Extract decision logic from service calls. The gateway is humble—just makes calls. Business logic is testable.

**Anti-Pattern (Logic in Gateway)**:
```python
# BAD: Business logic in gateway (hard to test)
class PaymentGateway:
    async def process_order_payment(self, order: Order):
        # Business logic in gateway
        if order.customer_type == 'new':
            # New customers: authorize for total + 10% hold
            amount_to_charge = order.total * 1.10
        elif order.customer_has_payment_issues():
            # Problem customers: require full payment upfront
            amount_to_charge = order.total
        else:
            # Regular customers: authorize for exact amount
            amount_to_charge = order.total

        # More business logic
        if amount_to_charge > 5000:
            # Large orders: use fraud check
            fraud_result = await self.stripe.fraud_check(order.customer_id)
            if fraud_result.suspicious:
                return PaymentResult(success=False, reason="Fraud detected")

        # External service call
        result = await self.stripe.charge(
            amount=amount_to_charge,
            customer=order.customer_id
        )
        return result
```

**Good Pattern (Logic in Use Case + Humble Gateway)**:
```python
# GOOD: Business logic in use case (testable)
class ProcessPaymentUseCase:
    """Testable use case with payment logic."""

    def __init__(self, payment_gateway: IPaymentGateway, fraud_checker: IFraudChecker):
        self._payment = payment_gateway
        self._fraud = fraud_checker

    async def execute(self, order: Order) -> PaymentResult:
        """Process payment with all business logic testable."""

        # Business logic: Determine amount to charge
        amount = self._calculate_charge_amount(order)

        # Business logic: Check if fraud screening needed
        if self._requires_fraud_screening(order, amount):
            fraud_result = await self._fraud.check(order.customer_id)
            if fraud_result.suspicious:
                return PaymentResult(
                    success=False,
                    reason="Payment flagged for fraud review"
                )

        # Call humble gateway (just makes the call)
        return await self._payment.charge(amount, order.customer_id)

    def _calculate_charge_amount(self, order: Order) -> Money:
        """Business rule: Calculate charge amount based on customer type."""
        if order.customer_type == CustomerType.NEW:
            # New customers: 10% authorization hold
            return Money(order.total.amount * Decimal("1.10"))
        elif order.has_payment_issues:
            # Problem customers: full amount upfront
            return order.total
        else:
            # Regular customers: exact amount
            return order.total

    def _requires_fraud_screening(self, order: Order, amount: Money) -> bool:
        """Business rule: When to require fraud screening."""
        return amount > Money(Decimal("5000"))


# Humble gateway: Just makes service calls
class StripePaymentGateway(IPaymentGateway):
    """Humble gateway: Minimal logic, just calls Stripe."""

    async def charge(self, amount: Money, customer_id: str) -> PaymentResult:
        """Make payment—no business logic."""
        try:
            result = await self.stripe.charge(
                amount=int(amount.amount * 100),  # Convert to cents
                currency="usd",
                customer=customer_id
            )
            return PaymentResult(
                success=True,
                transaction_id=result.id
            )
        except stripe.error.CardError as e:
            return PaymentResult(
                success=False,
                reason=str(e)
            )
```

**Testing**:
```python
# tests/unit/test_process_payment_use_case.py
@pytest.mark.asyncio
async def test_new_customers_charged_with_hold():
    """Test payment logic without calling Stripe."""
    # Arrange: Mock gateway and fraud checker
    mock_gateway = Mock()
    mock_gateway.charge = AsyncMock(return_value=PaymentResult(success=True))
    mock_fraud = Mock()

    use_case = ProcessPaymentUseCase(mock_gateway, mock_fraud)

    order = Order(customer_id="cust_123", customer_type=CustomerType.NEW)
    order.add_item(OrderItem(price=Money(Decimal("100")), quantity=1))

    # Act
    result = await use_case.execute(order)

    # Assert: Verify 10% hold was added (business logic tested without Stripe)
    mock_gateway.charge.assert_called_once()
    call_args = mock_gateway.charge.call_args
    assert call_args[0][0].amount == Decimal("110.00")  # 100 + 10% hold


@pytest.mark.asyncio
async def test_large_orders_require_fraud_screening():
    """Test fraud screening logic without external services."""
    # Arrange
    mock_gateway = Mock()
    mock_fraud = Mock()
    mock_fraud.check = AsyncMock(return_value=FraudResult(suspicious=True))

    use_case = ProcessPaymentUseCase(mock_gateway, mock_fraud)

    order = Order(customer_id="cust_123", customer_type=CustomerType.REGULAR)
    order.add_item(OrderItem(price=Money(Decimal("6000")), quantity=1))

    # Act
    result = await use_case.execute(order)

    # Assert: Verify fraud check was called and payment rejected
    mock_fraud.check.assert_called_once_with("cust_123")
    assert not result.success
    assert "fraud" in result.reason.lower()
```

### 4. Time and Randomness

**Problem**: Code that depends on current time or random values is hard to test reliably.

**Solution**: Extract time and randomness into injectable services. Business logic becomes testable.

**Anti-Pattern (Direct Time/Random Dependencies)**:
```python
# BAD: Direct dependencies on time and randomness
class DiscountService:
    def calculate_discount(self, order: Order) -> Money:
        # Direct dependency on current time
        current_hour = datetime.now().hour

        # Business logic mixed with hard-to-test dependencies
        if 2 <= current_hour <= 5:  # Late night discount
            discount_percent = 20
        elif current_hour >= 17:  # Evening discount
            discount_percent = 10
        else:
            discount_percent = 0

        # Direct dependency on random
        if random.random() < 0.1:  # 10% chance of extra discount
            discount_percent += 5

        return Money(order.total.amount * Decimal(discount_percent) / 100)
```

**Good Pattern (Inject Time and Random Services)**:
```python
# GOOD: Time and randomness as injectable dependencies
class ITimeProvider(ABC):
    """Interface for getting current time (testable)."""

    @abstractmethod
    def now(self) -> datetime:
        pass

    @abstractmethod
    def current_hour(self) -> int:
        pass


class SystemTimeProvider(ITimeProvider):
    """Humble implementation: Just returns system time."""

    def now(self) -> datetime:
        return datetime.now()

    def current_hour(self) -> int:
        return datetime.now().hour


class IRandomProvider(ABC):
    """Interface for random values (testable)."""

    @abstractmethod
    def random_float(self) -> float:
        pass


class SystemRandomProvider(IRandomProvider):
    """Humble implementation: Just returns random values."""

    def random_float(self) -> float:
        return random.random()


class DiscountService:
    """Testable service with injected dependencies."""

    def __init__(self, time_provider: ITimeProvider, random_provider: IRandomProvider):
        self._time = time_provider
        self._random = random_provider

    def calculate_discount(self, order: Order) -> Money:
        """Calculate discount—testable because time and random are injected."""
        current_hour = self._time.current_hour()

        # Business logic is now testable
        if 2 <= current_hour <= 5:
            discount_percent = 20
        elif current_hour >= 17:
            discount_percent = 10
        else:
            discount_percent = 0

        # Random behavior is now testable
        if self._random.random_float() < 0.1:
            discount_percent += 5

        return Money(order.total.amount * Decimal(discount_percent) / 100)
```

**Testing**:
```python
# tests/unit/test_discount_service.py
class FakeTimeProvider(ITimeProvider):
    """Fake time provider for testing."""

    def __init__(self, hour: int):
        self._hour = hour

    def now(self) -> datetime:
        return datetime(2024, 1, 1, self._hour, 0)

    def current_hour(self) -> int:
        return self._hour


class FakeRandomProvider(IRandomProvider):
    """Fake random provider for testing."""

    def __init__(self, value: float):
        self._value = value

    def random_float(self) -> float:
        return self._value


def test_late_night_discount():
    """Test late night discount logic with fake time."""
    # Arrange: Set time to 3 AM
    time_provider = FakeTimeProvider(hour=3)
    random_provider = FakeRandomProvider(value=0.5)  # No bonus
    service = DiscountService(time_provider, random_provider)

    order = Order(total=Money(Decimal("100")))

    # Act
    discount = service.calculate_discount(order)

    # Assert: 20% discount at 3 AM
    assert discount.amount == Decimal("20.00")


def test_bonus_discount_applied():
    """Test bonus discount logic with fake random."""
    # Arrange: Random will trigger bonus
    time_provider = FakeTimeProvider(hour=12)  # No time-based discount
    random_provider = FakeRandomProvider(value=0.05)  # Will trigger 10% chance
    service = DiscountService(time_provider, random_provider)

    order = Order(total=Money(Decimal("100")))

    # Act
    discount = service.calculate_discount(order)

    # Assert: 5% bonus discount
    assert discount.amount == Decimal("5.00")
```

## Testing Strategies

### Fast Unit Tests for Logic

Test the testable component with pure unit tests—no infrastructure needed:

```python
# tests/unit/test_order_presenter.py
def test_format_pending_status():
    presenter = OrderPresenter(mock_repository)
    status = presenter._format_status(OrderStatus.PENDING)
    assert status.text == "Awaiting Payment"
    assert status.color == "yellow"
```

### Minimal Integration Tests for Humble Objects

Write a few integration tests to verify humble objects work with real infrastructure:

```python
# tests/integration/test_order_view.py
@pytest.mark.integration
async def test_view_renders_with_real_framework():
    """Integration test: Verify view works with real web framework."""
    view = OrderView(real_web_framework, presenter)
    await view.display_order("order_123")
    # Minimal assertions—just verify it doesn't crash
    assert real_web_framework.rendered
```

### Contract Tests for Interfaces

Verify humble implementations satisfy interface contracts:

```python
# tests/contracts/test_time_provider_contract.py
class TimeProviderContractTests:
    """Contract tests for ITimeProvider implementations."""

    @pytest.fixture
    def provider(self) -> ITimeProvider:
        raise NotImplementedError

    def test_now_returns_datetime(self, provider: ITimeProvider):
        result = provider.now()
        assert isinstance(result, datetime)

    def test_current_hour_in_valid_range(self, provider: ITimeProvider):
        hour = provider.current_hour()
        assert 0 <= hour <= 23


class TestSystemTimeProvider(TimeProviderContractTests):
    @pytest.fixture
    def provider(self):
        return SystemTimeProvider()


class TestFakeTimeProvider(TimeProviderContractTests):
    @pytest.fixture
    def provider(self):
        return FakeTimeProvider(hour=12)
```

## When to Apply Humble Objects

### High-Value Scenarios

**GUI Logic**: Always separate presentation logic from view rendering. Views are very hard to test.

**Database Boundaries**: Always extract business logic from repository implementations.

**External Services**: Always separate decision logic from service calls. External services are slow and unreliable.

**Time-Dependent Logic**: Always inject time providers for logic that depends on current time.

**Random Behavior**: Always inject random providers for logic with randomness.

### Lower-Value Scenarios

**Simple Data Transformations**: If logic is trivial (e.g., uppercase a string), don't over-engineer.

**One-Line Operations**: Don't create humble objects for single operations with no logic.

**Already Fast**: If the component is already fast and reliable to test, humble objects may be overkill.

## Common Mistakes

### Mistake 1: Too Much Logic in Humble Object

**Problem**: Humble object contains complex business logic.

```python
# BAD: View contains formatting logic
class OrderView:
    def render(self, order: Order):
        # Complex formatting in view (should be in presenter)
        if order.total > 1000:
            total_color = "red"
            total_size = "large"
        else:
            total_color = "green"
            total_size = "normal"

        self.framework.render({
            'total': f"${order.total:.2f}",
            'total_color': total_color,
            'total_size': total_size
        })
```

**Fix**: Move all logic to presenter.

```python
# GOOD: All logic in presenter, view just renders
class OrderPresenter:
    def present(self, order: Order) -> OrderViewModel:
        total_display = self._format_total_with_emphasis(order.total)
        return OrderViewModel(
            total=total_display.text,
            total_color=total_display.color,
            total_size=total_display.size
        )

class OrderView:
    def render(self, view_model: OrderViewModel):
        # Just render—no logic
        self.framework.render(view_model)
```

### Mistake 2: Testing the Humble Object Extensively

**Problem**: Writing extensive tests for humble components instead of testable components.

```python
# BAD: Extensive testing of view rendering
def test_view_renders_order_id():
    # Testing humble object (the view)
    view.render(order)
    assert view.displayed_order_id == "order_123"

def test_view_renders_total():
    view.render(order)
    assert view.displayed_total == "$99.99"

def test_view_renders_status_color():
    view.render(order)
    assert view.status_color == "yellow"
```

**Fix**: Test presenter extensively, minimal tests for view.

```python
# GOOD: Extensive testing of presenter
def test_presenter_formats_order_id():
    view_model = presenter.present(order)
    assert view_model.order_id == "order_123"

def test_presenter_formats_total():
    view_model = presenter.present(order)
    assert view_model.total == "$99.99"

def test_presenter_formats_status_color():
    view_model = presenter.present(order)
    assert view_model.status_color == "yellow"

# Minimal integration test for view
@pytest.mark.integration
def test_view_renders_successfully():
    view.render(view_model)
    assert view.framework.rendered  # Just verify it works
```

### Mistake 3: No Clear Interface Between Components

**Problem**: Coupling between humble and testable components without clear interface.

```python
# BAD: View directly accesses presenter internal methods
class OrderView:
    def render(self, order_id: str):
        # View knows too much about presenter
        order = self.presenter._fetch_order(order_id)
        status = self.presenter._determine_status_color(order.status)
        total = self.presenter._format_currency(order.total)
        self.framework.render({'status': status, 'total': total})
```

**Fix**: Clear interface (view model) between components.

```python
# GOOD: Clear interface via view model
class OrderView:
    def render(self, order_id: str):
        # View just gets view model and renders
        view_model = self.presenter.present(order_id)
        self.framework.render(view_model)
```

## Key Takeaways

### Essential Principles

1. **Split behaviors**: Separate hard-to-test from easy-to-test
2. **Humble objects are simple**: Minimal logic, just infrastructure interaction
3. **Testable components have logic**: All important behavior goes here
4. **Test extensively where easy**: Focus tests on testable components
5. **Minimal tests for humble objects**: Just verify they work with real infrastructure

### Humble Object Checklist

- [ ] Presentation logic extracted to presenter, view is humble
- [ ] Business logic extracted from repositories
- [ ] Decision logic extracted from external service gateways
- [ ] Time and randomness injected as dependencies
- [ ] Testable components have comprehensive unit tests
- [ ] Humble components have minimal integration tests
- [ ] Clear interfaces between humble and testable components

### Implementation Checklist

- [ ] Identify hard-to-test components (GUI, database, external services)
- [ ] Extract all logic from these components into testable classes
- [ ] Create clear interfaces (view models, DTOs) between components
- [ ] Write comprehensive unit tests for testable components
- [ ] Write minimal integration tests for humble components
- [ ] Verify humble components are truly humble (minimal logic)

## Related Resources

- **BUSINESS_RULES.md**: Entities and use cases are testable components
- **PLUGIN_ARCHITECTURE.md**: Gateways and repositories as humble objects
- **DEPENDENCY_RULE.md**: Dependencies flow toward testable components
- **SOLID_PRINCIPLES.md**: Single Responsibility helps separate concerns

## Summary

The Humble Object pattern separates behaviors into hard-to-test and easy-to-test components. Hard-to-test components (GUIs, databases, external services) are kept "humble"—stripped of all logic. Easy-to-test components contain all important business logic and are thoroughly tested with fast unit tests.

Apply this pattern to:
- **Views**: Extract presentation logic to testable presenters
- **Repositories**: Extract business logic to entities
- **Gateways**: Extract decision logic to use cases
- **Time/Random**: Inject providers to make logic testable

The result: fast, reliable unit tests covering your important logic, with minimal slow integration tests just to verify infrastructure works. High test coverage with quick feedback during development.