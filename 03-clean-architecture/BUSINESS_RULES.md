# Business Rules: Entities and Use Cases

## Overview

Business Rules are the core of any software system—the critical rules and policies that would exist even if the system were entirely manual. They are divided into two categories: **Entities** (enterprise-wide business rules) and **Use Cases** (application-specific business rules). Understanding this distinction and protecting these rules from contamination by technical details is fundamental to clean architecture.

**"Business rules are the reason a software system exists. They are the core functionality. They carry the code that makes, or saves, money."** — Robert C. Martin, Clean Architecture

These rules should be the most independent, reusable, and stable parts of the system. They should have no dependencies on databases, frameworks, UI, or any other technical concerns. They should be pure, testable business logic.

## Why Business Rules Matter

### The Cost of Contaminated Business Rules

Systems where business rules are mixed with technical details exhibit:

**Untestable Logic**: Cannot test business rules without database connections, web servers, or external APIs. Simple calculations require complex integration test setups.

**Duplicated Rules**: Same business logic scattered across controllers, database triggers, UI validation, and API endpoints. Changing a rule requires hunting down all copies.

**Framework Coupling**: Business rules written using framework-specific APIs. Upgrading or replacing frameworks requires rewriting business logic.

**Rigid Systems**: Cannot reuse business rules in different contexts (web, mobile, CLI, batch jobs). Each delivery mechanism requires duplicating the logic.

**Slow Development**: Adding features requires understanding and modifying tangled web of UI, database, and business logic instead of just changing business rules.

### The Benefits of Pure Business Rules

Clean business rules provide:
- **Testability**: Test rules with simple unit tests, no infrastructure required
- **Reusability**: Same rules used across multiple delivery mechanisms
- **Clarity**: Business logic clearly separated from technical implementation
- **Stability**: Core rules change only when business requirements change
- **Independence**: Rules have zero dependencies on technical details
- **Comprehensibility**: Domain experts can read and verify business rules

## Source Materials

This guide is based on:

- **Clean Architecture** by Robert C. Martin (Chapter 20: "Business Rules")
  - Entities: Enterprise business rules
  - Use Cases: Application business rules
  - Clear separation between the two

## The Two Types of Business Rules

### Entities: Enterprise Business Rules

**Definition**: Critical business rules that would exist even if the system were not automated. The fundamental rules that define core business concepts.

**Characteristics**:
- Represent critical business data + critical business rules that operate on that data
- Would exist even if implemented with paper, filing cabinets, and manual processes
- Least likely to change when external factors change
- Most general and highest-level rules
- No dependencies on anything—completely independent

**Example**: An Order entity knows how to calculate its total, apply discounts, and validate that it meets business constraints. These rules exist whether orders are managed in software, spreadsheets, or paper forms.

### Use Cases: Application Business Rules

**Definition**: Application-specific rules that describe how the system is used to satisfy user goals. They orchestrate entities to accomplish specific business operations.

**Characteristics**:
- Define interactions between user and system
- Orchestrate entities to accomplish business goals
- Specific to the application, not universal business rules
- Change when application requirements change
- Depend on entities, but not on technical details

**Example**: A "Place Order" use case orchestrates Cart and Order entities, validates payment methods, processes payments, and sends confirmations. This is how *this application* handles ordering, not a universal business rule.

## Entities: Enterprise Business Rules

### What Entities Are

Entities encapsulate the most general, high-level rules. They contain critical business data and the methods that operate on that data.

**Not Database Entities**: Entities in clean architecture are NOT database tables or ORM models. They are pure business objects with no knowledge of persistence.

**Critical Business Objects**: Entities represent the core business concepts that the organization deals with: customers, products, orders, accounts, patients, appointments.

### Entity Characteristics

**Pure Business Logic**: No framework code, no database code, no UI code. Just business rules.

**Highly Reusable**: Can be used in different applications across the enterprise.

**Stable**: Change only when fundamental business rules change, not when UI or database changes.

**Self-Contained**: Validate their own data, enforce their own invariants, contain business methods that operate on their data.

### Entity Examples

**Example 1: Order Entity**

```python
# domain/entities/order.py
from dataclasses import dataclass
from typing import List
from datetime import datetime
from decimal import Decimal

@dataclass
class Money:
    """Value object representing money."""
    amount: Decimal
    currency: str = "USD"

    def __add__(self, other: 'Money') -> 'Money':
        if self.currency != other.currency:
            raise ValueError("Cannot add money with different currencies")
        return Money(self.amount + other.amount, self.currency)

    def __mul__(self, factor: int) -> 'Money':
        return Money(self.amount * Decimal(factor), self.currency)

    def __gt__(self, other: 'Money') -> bool:
        if self.currency != other.currency:
            raise ValueError("Cannot compare money with different currencies")
        return self.amount > other.amount


class Order:
    """
    Entity: Order

    Critical Business Rules:
    1. Orders must have at least one item
    2. Order total is sum of (item price * quantity) for all items
    3. Orders can have discounts applied
    4. Orders have status that follows specific lifecycle
    """

    # Business constants
    MAX_ORDER_TOTAL = Money(Decimal("100000.00"))
    MIN_ORDER_TOTAL = Money(Decimal("0.01"))

    def __init__(self, customer_id: str, order_id: str = None):
        self.id = order_id or self._generate_id()
        self.customer_id = customer_id
        self.items: List[OrderItem] = []
        self.status = OrderStatus.PENDING
        self.discount: Optional[Discount] = None
        self.created_at = datetime.now()
        self.updated_at = datetime.now()

    def add_item(self, product_id: str, quantity: int, unit_price: Money) -> None:
        """Business Rule: Add item to order."""
        if quantity <= 0:
            raise InvalidQuantityError("Quantity must be positive")

        item = OrderItem(product_id, quantity, unit_price)
        self.items.append(item)
        self.updated_at = datetime.now()

    def remove_item(self, product_id: str) -> None:
        """Business Rule: Remove item from order."""
        self.items = [item for item in self.items if item.product_id != product_id]
        self.updated_at = datetime.now()

    def calculate_subtotal(self) -> Money:
        """Business Rule: Subtotal is sum of all items."""
        if not self.items:
            return Money(Decimal("0.00"))

        subtotal = Money(Decimal("0.00"))
        for item in self.items:
            subtotal = subtotal + (item.unit_price * item.quantity)
        return subtotal

    def calculate_total(self) -> Money:
        """Business Rule: Total is subtotal minus discount."""
        subtotal = self.calculate_subtotal()

        if self.discount:
            discount_amount = self.discount.calculate(subtotal)
            return Money(subtotal.amount - discount_amount.amount, subtotal.currency)

        return subtotal

    def apply_discount(self, discount: 'Discount') -> None:
        """Business Rule: Apply discount to order."""
        if not discount.is_valid_for_order(self):
            raise InvalidDiscountError("Discount not valid for this order")

        self.discount = discount
        self.updated_at = datetime.now()

    def validate(self) -> None:
        """Business Rule: Validate order meets all constraints."""
        if not self.items:
            raise EmptyOrderError("Order must have at least one item")

        total = self.calculate_total()

        if total < self.MIN_ORDER_TOTAL:
            raise OrderTooSmallError(f"Order total {total.amount} is below minimum {self.MIN_ORDER_TOTAL.amount}")

        if total > self.MAX_ORDER_TOTAL:
            raise OrderTooLargeError(f"Order total {total.amount} exceeds maximum {self.MAX_ORDER_TOTAL.amount}")

    def mark_as_confirmed(self) -> None:
        """Business Rule: Order can only be confirmed if pending."""
        if self.status != OrderStatus.PENDING:
            raise InvalidOrderStateError(f"Cannot confirm order in {self.status} state")

        self.status = OrderStatus.CONFIRMED
        self.updated_at = datetime.now()

    def mark_as_shipped(self, tracking_number: str) -> None:
        """Business Rule: Order can only be shipped if confirmed."""
        if self.status != OrderStatus.CONFIRMED:
            raise InvalidOrderStateError(f"Cannot ship order in {self.status} state")

        self.status = OrderStatus.SHIPPED
        self.tracking_number = tracking_number
        self.updated_at = datetime.now()

    def cancel(self, reason: str) -> None:
        """Business Rule: Order can only be cancelled if not shipped."""
        if self.status == OrderStatus.SHIPPED:
            raise InvalidOrderStateError("Cannot cancel shipped order")

        self.status = OrderStatus.CANCELLED
        self.cancellation_reason = reason
        self.updated_at = datetime.now()

    @staticmethod
    def _generate_id() -> str:
        """Generate unique order ID."""
        return f"ORD-{uuid.uuid4().hex[:8].upper()}"


@dataclass
class OrderItem:
    """Value object representing an order line item."""
    product_id: str
    quantity: int
    unit_price: Money


class OrderStatus(Enum):
    """Order lifecycle states."""
    PENDING = "pending"
    CONFIRMED = "confirmed"
    SHIPPED = "shipped"
    DELIVERED = "delivered"
    CANCELLED = "cancelled"
```

**Key Points**:
- Pure business logic with no external dependencies
- Self-validating (enforces invariants)
- Contains business rules that would exist without computers
- Testable with simple unit tests
- No knowledge of databases, web frameworks, or UI

**Example 2: Loan Entity (Banking Domain)**

```python
# domain/entities/loan.py
from decimal import Decimal
from datetime import datetime, timedelta

class Loan:
    """
    Entity: Loan

    Critical Business Rules:
    1. Interest accrues daily based on annual percentage rate
    2. Payments are applied to interest first, then principal
    3. Loan has minimum and maximum terms
    4. Loan cannot be paid beyond principal + accrued interest
    """

    MIN_TERM_MONTHS = 6
    MAX_TERM_MONTHS = 360  # 30 years

    def __init__(
        self,
        loan_id: str,
        principal: Decimal,
        annual_rate: Decimal,
        term_months: int,
        origination_date: datetime
    ):
        self.id = loan_id
        self.principal = principal
        self.annual_rate = annual_rate
        self.term_months = term_months
        self.origination_date = origination_date
        self.remaining_principal = principal
        self.payments: List[Payment] = []

        self._validate()

    def calculate_daily_interest_rate(self) -> Decimal:
        """Business Rule: Daily rate is annual rate divided by 365."""
        return self.annual_rate / Decimal("365")

    def calculate_accrued_interest(self, as_of_date: datetime) -> Decimal:
        """Business Rule: Interest accrues daily on remaining principal."""
        days_elapsed = (as_of_date - self.origination_date).days
        daily_rate = self.calculate_daily_interest_rate()
        return self.remaining_principal * daily_rate * Decimal(days_elapsed)

    def calculate_monthly_payment(self) -> Decimal:
        """Business Rule: Calculate monthly payment using amortization formula."""
        monthly_rate = self.annual_rate / Decimal("12")
        numerator = self.principal * monthly_rate
        denominator = 1 - (1 + monthly_rate) ** (-self.term_months)
        return numerator / denominator

    def apply_payment(self, amount: Decimal, payment_date: datetime) -> PaymentResult:
        """
        Business Rule: Apply payment to accrued interest first, then principal.

        Returns details about how payment was applied.
        """
        if amount <= 0:
            raise InvalidPaymentError("Payment amount must be positive")

        accrued_interest = self.calculate_accrued_interest(payment_date)
        total_owed = self.remaining_principal + accrued_interest

        if amount > total_owed:
            raise OverpaymentError(f"Payment {amount} exceeds amount owed {total_owed}")

        # Apply to interest first
        interest_portion = min(amount, accrued_interest)
        principal_portion = amount - interest_portion

        self.remaining_principal -= principal_portion

        payment = Payment(
            amount=amount,
            date=payment_date,
            interest_portion=interest_portion,
            principal_portion=principal_portion
        )
        self.payments.append(payment)

        return PaymentResult(
            payment=payment,
            remaining_principal=self.remaining_principal,
            remaining_interest=accrued_interest - interest_portion
        )

    def is_paid_off(self) -> bool:
        """Business Rule: Loan is paid off when principal reaches zero."""
        return self.remaining_principal == Decimal("0")

    def calculate_payoff_amount(self, as_of_date: datetime) -> Decimal:
        """Business Rule: Payoff is remaining principal plus accrued interest."""
        accrued_interest = self.calculate_accrued_interest(as_of_date)
        return self.remaining_principal + accrued_interest

    def _validate(self) -> None:
        """Validate loan parameters against business rules."""
        if self.principal <= 0:
            raise InvalidLoanError("Principal must be positive")

        if self.annual_rate <= 0:
            raise InvalidLoanError("Interest rate must be positive")

        if not self.MIN_TERM_MONTHS <= self.term_months <= self.MAX_TERM_MONTHS:
            raise InvalidLoanError(
                f"Term must be between {self.MIN_TERM_MONTHS} and {self.MAX_TERM_MONTHS} months"
            )
```

## Use Cases: Application Business Rules

### What Use Cases Are

Use Cases orchestrate entities to accomplish specific goals. They define the interactions between actors (users) and the system to achieve business objectives.

**Not Controllers**: Use Cases are not web controllers or API handlers. They are application business logic, independent of delivery mechanism.

**Orchestration Logic**: Use Cases coordinate entities, repositories, and gateways to accomplish business goals.

### Use Case Characteristics

**Application-Specific**: Specific to how *this application* works, not universal business rules.

**Orchestrate Entities**: Call methods on entities, coordinate multiple entities, enforce application workflows.

**Define Interfaces**: Specify what they need from infrastructure (repositories, gateways) through abstract interfaces.

**Technology-Independent**: No knowledge of web frameworks, databases, or UI. Just business logic.

### Use Case Structure

A well-structured use case has:

1. **Clear Name**: Named after business operation (PlaceOrder, ApproveLoadApplication, ScheduleAppointment)
2. **Request Object**: Input data needed for the operation
3. **Response Object**: Result of the operation
4. **Business Logic**: Orchestration of entities and validation of business rules
5. **Interface Dependencies**: Abstract interfaces for infrastructure needs

### Use Case Examples

**Example 1: Place Order Use Case**

```python
# application/use_cases/place_order.py
from dataclasses import dataclass
from typing import Optional
from domain.entities.order import Order, OrderStatus
from domain.entities.cart import Cart
from domain.repositories import ICartRepository, IOrderRepository
from domain.gateways import IPaymentGateway, INotificationService

@dataclass
class PlaceOrderRequest:
    """Input data for placing an order."""
    customer_id: str
    payment_method_id: str
    shipping_address: Address
    billing_address: Address


@dataclass
class PlaceOrderResponse:
    """Result of placing an order."""
    success: bool
    order_id: Optional[str] = None
    error_message: Optional[str] = None


class PlaceOrderUseCase:
    """
    Use Case: Place Order

    Actor: Customer
    Goal: Convert shopping cart into confirmed order

    Success Scenario:
    1. Customer has items in cart
    2. Customer provides valid payment method
    3. System validates order
    4. System processes payment
    5. System creates order
    6. System clears cart
    7. System sends confirmation

    This is application-specific business logic that orchestrates
    entities (Cart, Order) and infrastructure (payment, notifications).
    """

    def __init__(
        self,
        cart_repository: ICartRepository,
        order_repository: IOrderRepository,
        payment_gateway: IPaymentGateway,
        notification_service: INotificationService
    ):
        # Dependencies on abstract interfaces, not concrete implementations
        self._carts = cart_repository
        self._orders = order_repository
        self._payment = payment_gateway
        self._notifications = notification_service

    async def execute(self, request: PlaceOrderRequest) -> PlaceOrderResponse:
        """Execute the place order use case."""

        # Step 1: Retrieve customer's cart
        cart = await self._carts.find_by_customer(request.customer_id)
        if not cart or not cart.items:
            return PlaceOrderResponse(
                success=False,
                error_message="Cart is empty"
            )

        # Step 2: Create order from cart (Entity creation)
        order = Order(customer_id=request.customer_id)
        for item in cart.items:
            order.add_item(item.product_id, item.quantity, item.unit_price)

        # Step 3: Apply any available discounts (Entity business logic)
        if cart.discount_code:
            discount = await self._get_discount(cart.discount_code)
            if discount and discount.is_valid_for_order(order):
                order.apply_discount(discount)

        # Step 4: Validate order (Entity validation)
        try:
            order.validate()
        except OrderValidationError as e:
            return PlaceOrderResponse(
                success=False,
                error_message=str(e)
            )

        # Step 5: Process payment (Infrastructure interaction)
        total = order.calculate_total()
        payment_result = await self._payment.charge(
            amount=total,
            payment_method_id=request.payment_method_id
        )

        if not payment_result.success:
            return PlaceOrderResponse(
                success=False,
                error_message=f"Payment failed: {payment_result.error_message}"
            )

        # Step 6: Mark order as confirmed (Entity state change)
        order.mark_as_confirmed()
        order.payment_transaction_id = payment_result.transaction_id

        # Step 7: Save order (Persistence)
        await self._orders.save(order)

        # Step 8: Clear cart (Application workflow)
        await self._carts.clear(request.customer_id)

        # Step 9: Send confirmation (Infrastructure interaction)
        await self._notifications.send_order_confirmation(
            customer_id=request.customer_id,
            order_id=order.id,
            total=total
        )

        return PlaceOrderResponse(
            success=True,
            order_id=order.id
        )
```

**Example 2: Approve Loan Application Use Case**

```python
# application/use_cases/approve_loan_application.py

@dataclass
class ApproveLoanRequest:
    """Input for loan approval."""
    application_id: str
    approved_by: str
    approval_notes: Optional[str] = None


@dataclass
class ApproveLoanResponse:
    """Result of loan approval."""
    success: bool
    loan_id: Optional[str] = None
    error_message: Optional[str] = None


class ApproveLoanApplicationUseCase:
    """
    Use Case: Approve Loan Application

    Actor: Loan Officer
    Goal: Approve a loan application and create loan

    Business Rules:
    1. Application must be in "under review" status
    2. Applicant must meet credit requirements
    3. Loan terms must be within policy limits
    4. Officer must have approval authority for amount
    """

    def __init__(
        self,
        application_repository: ILoanApplicationRepository,
        loan_repository: ILoanRepository,
        credit_checker: ICreditCheckService,
        policy_validator: ILoanPolicyValidator,
        notification_service: INotificationService
    ):
        self._applications = application_repository
        self._loans = loan_repository
        self._credit = credit_checker
        self._policy = policy_validator
        self._notifications = notification_service

    async def execute(self, request: ApproveLoanRequest) -> ApproveLoanResponse:
        """Execute loan approval use case."""

        # Step 1: Retrieve application
        application = await self._applications.find_by_id(request.application_id)
        if not application:
            return ApproveLoanResponse(
                success=False,
                error_message="Application not found"
            )

        # Step 2: Validate application status (Application workflow rule)
        if application.status != ApplicationStatus.UNDER_REVIEW:
            return ApproveLoanResponse(
                success=False,
                error_message=f"Cannot approve application in {application.status} status"
            )

        # Step 3: Verify credit requirements (Business rule validation)
        credit_check = await self._credit.check_credit(application.applicant_id)
        if not credit_check.meets_requirements:
            return ApproveLoanResponse(
                success=False,
                error_message=f"Applicant does not meet credit requirements: {credit_check.reason}"
            )

        # Step 4: Validate against loan policies (Business rule validation)
        policy_result = await self._policy.validate(
            principal=application.requested_amount,
            term=application.requested_term,
            rate=application.offered_rate
        )
        if not policy_result.valid:
            return ApproveLoanResponse(
                success=False,
                error_message=f"Loan does not meet policy: {policy_result.violations}"
            )

        # Step 5: Verify approval authority (Business rule)
        if not self._has_approval_authority(request.approved_by, application.requested_amount):
            return ApproveLoanResponse(
                success=False,
                error_message="Approver does not have authority for this loan amount"
            )

        # Step 6: Create loan entity (Entity creation)
        loan = Loan(
            loan_id=self._generate_loan_id(),
            principal=application.requested_amount,
            annual_rate=application.offered_rate,
            term_months=application.requested_term,
            origination_date=datetime.now()
        )

        # Step 7: Update application status (Entity state change)
        application.approve(
            approved_by=request.approved_by,
            notes=request.approval_notes
        )

        # Step 8: Persist changes
        await self._loans.save(loan)
        await self._applications.save(application)

        # Step 9: Notify applicant (Infrastructure interaction)
        await self._notifications.send_approval_notification(
            applicant_id=application.applicant_id,
            loan_id=loan.id
        )

        return ApproveLoanResponse(
            success=True,
            loan_id=loan.id
        )

    def _has_approval_authority(self, officer_id: str, amount: Decimal) -> bool:
        """Business rule: Verify officer has authority to approve this amount."""
        # Would query officer authority levels
        pass
```

## Entities vs Use Cases: Key Differences

| Aspect | Entities | Use Cases |
|--------|----------|-----------|
| **Level** | Enterprise-wide, most general | Application-specific |
| **Stability** | Most stable, rarely change | Change when application changes |
| **Dependencies** | Zero dependencies | Depend on entities and interfaces |
| **Reusability** | Reusable across applications | Specific to this application |
| **Examples** | Order, Loan, Patient, Product | PlaceOrder, ApproveLoan, ScheduleAppointment |
| **Purpose** | Define core business concepts | Define application workflows |
| **Testing** | Pure unit tests | Unit tests with mocked infrastructure |

## Testing Business Rules

### Testing Entities (Pure Unit Tests)

Entities have no dependencies, so testing is trivial:

```python
# tests/unit/test_order_entity.py
import pytest
from domain.entities.order import Order, Money
from decimal import Decimal

def test_order_calculates_total_correctly():
    """Test entity business rule: total calculation."""
    # Arrange
    order = Order(customer_id="cust_123")
    order.add_item("prod_1", quantity=2, unit_price=Money(Decimal("10.00")))
    order.add_item("prod_2", quantity=1, unit_price=Money(Decimal("15.00")))

    # Act
    total = order.calculate_total()

    # Assert
    assert total.amount == Decimal("35.00")


def test_order_validates_minimum_items():
    """Test entity business rule: validation."""
    # Arrange
    order = Order(customer_id="cust_123")

    # Act & Assert
    with pytest.raises(EmptyOrderError):
        order.validate()


def test_order_applies_discount_correctly():
    """Test entity business rule: discount application."""
    # Arrange
    order = Order(customer_id="cust_123")
    order.add_item("prod_1", quantity=1, unit_price=Money(Decimal("100.00")))
    discount = PercentageDiscount(percent=10)

    # Act
    order.apply_discount(discount)
    total = order.calculate_total()

    # Assert
    assert total.amount == Decimal("90.00")
```

### Testing Use Cases (Unit Tests with Mocks)

Use cases depend on infrastructure through interfaces, so we mock dependencies:

```python
# tests/unit/test_place_order_use_case.py
import pytest
from unittest.mock import AsyncMock, Mock
from application.use_cases.place_order import PlaceOrderUseCase, PlaceOrderRequest

@pytest.mark.asyncio
async def test_place_order_success():
    """Test use case business logic with mocked infrastructure."""
    # Arrange: Create mocks for all dependencies
    mock_cart_repo = Mock()
    mock_cart_repo.find_by_customer = AsyncMock(return_value=create_test_cart())
    mock_cart_repo.clear = AsyncMock()

    mock_order_repo = Mock()
    mock_order_repo.save = AsyncMock()

    mock_payment = Mock()
    mock_payment.charge = AsyncMock(return_value=PaymentResult(
        success=True,
        transaction_id="txn_123"
    ))

    mock_notifications = Mock()
    mock_notifications.send_order_confirmation = AsyncMock()

    # Create use case with mocked dependencies
    use_case = PlaceOrderUseCase(
        cart_repository=mock_cart_repo,
        order_repository=mock_order_repo,
        payment_gateway=mock_payment,
        notification_service=mock_notifications
    )

    request = PlaceOrderRequest(
        customer_id="cust_123",
        payment_method_id="pm_123",
        shipping_address=create_test_address(),
        billing_address=create_test_address()
    )

    # Act
    response = await use_case.execute(request)

    # Assert: Verify business logic executed correctly
    assert response.success
    assert response.order_id is not None

    # Verify workflow steps were executed
    mock_cart_repo.find_by_customer.assert_called_once_with("cust_123")
    mock_payment.charge.assert_called_once()
    mock_order_repo.save.assert_called_once()
    mock_cart_repo.clear.assert_called_once_with("cust_123")
    mock_notifications.send_order_confirmation.assert_called_once()


@pytest.mark.asyncio
async def test_place_order_fails_with_empty_cart():
    """Test use case handles business rule violation."""
    # Arrange: Cart is empty
    mock_cart_repo = Mock()
    mock_cart_repo.find_by_customer = AsyncMock(return_value=Cart(customer_id="cust_123", items=[]))

    use_case = PlaceOrderUseCase(
        cart_repository=mock_cart_repo,
        order_repository=Mock(),
        payment_gateway=Mock(),
        notification_service=Mock()
    )

    request = PlaceOrderRequest(
        customer_id="cust_123",
        payment_method_id="pm_123",
        shipping_address=create_test_address(),
        billing_address=create_test_address()
    )

    # Act
    response = await use_case.execute(request)

    # Assert: Business rule enforced
    assert not response.success
    assert "empty" in response.error_message.lower()


@pytest.mark.asyncio
async def test_place_order_fails_when_payment_declined():
    """Test use case handles payment failure."""
    # Arrange: Payment will fail
    mock_cart_repo = Mock()
    mock_cart_repo.find_by_customer = AsyncMock(return_value=create_test_cart())

    mock_payment = Mock()
    mock_payment.charge = AsyncMock(return_value=PaymentResult(
        success=False,
        error_message="Card declined"
    ))

    use_case = PlaceOrderUseCase(
        cart_repository=mock_cart_repo,
        order_repository=Mock(),
        payment_gateway=mock_payment,
        notification_service=Mock()
    )

    request = PlaceOrderRequest(
        customer_id="cust_123",
        payment_method_id="pm_123",
        shipping_address=create_test_address(),
        billing_address=create_test_address()
    )

    # Act
    response = await use_case.execute(request)

    # Assert: Payment failure handled correctly
    assert not response.success
    assert "payment failed" in response.error_message.lower()
    assert "card declined" in response.error_message.lower()
```

## Common Mistakes

### Mistake 1: Entities with Infrastructure Dependencies

**Problem**: Entity depends on database or framework code.

```python
# BAD: Entity depends on ORM
from sqlalchemy import Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class Order(Base):  # Entity inheriting from ORM base class
    __tablename__ = 'orders'

    id = Column(Integer, primary_key=True)
    customer_id = Column(String)

    def save(self):
        session.add(self)  # Entity knows about persistence
        session.commit()
```

**Fix**: Pure entity with no infrastructure knowledge.

```python
# GOOD: Pure entity
class Order:
    """Pure business entity with no external dependencies."""

    def __init__(self, customer_id: str, order_id: str = None):
        self.id = order_id or str(uuid.uuid4())
        self.customer_id = customer_id
        self.items: List[OrderItem] = []

    def calculate_total(self) -> Money:
        """Business logic only."""
        return sum(item.price * item.quantity for item in self.items)
```

### Mistake 2: Use Cases in Controllers

**Problem**: Business logic embedded in web controllers.

```python
# BAD: Business logic in controller
class OrderController:
    @app.post("/orders")
    async def create_order(self, request: Request):
        # Business logic mixed with HTTP handling
        cart = await db.fetch_cart(request.json['customer_id'])
        if not cart.items:
            return Response(status=400, body="Cart empty")

        total = sum(item.price * item.quantity for item in cart.items)

        payment_result = stripe.charge(total, request.json['payment_method'])
        if not payment_result['success']:
            return Response(status=402, body="Payment failed")

        order_id = await db.insert_order({...})
        await db.clear_cart(request.json['customer_id'])

        return Response(status=201, body={'order_id': order_id})
```

**Fix**: Business logic in use case, controller just adapts.

```python
# GOOD: Business logic in use case
class OrderController:
    def __init__(self, place_order_use_case: PlaceOrderUseCase):
        self._place_order = place_order_use_case

    @app.post("/orders")
    async def create_order(self, request: Request):
        # Adapt HTTP to domain
        use_case_request = PlaceOrderRequest(
            customer_id=request.json['customer_id'],
            payment_method_id=request.json['payment_method']
        )

        # Execute business logic
        result = await self._place_order.execute(use_case_request)

        # Adapt domain to HTTP
        if result.success:
            return Response(status=201, body={'order_id': result.order_id})
        else:
            return Response(status=400, body={'error': result.error_message})
```

### Mistake 3: Anemic Entities

**Problem**: Entities are just data bags with no behavior.

```python
# BAD: Anemic entity (just data)
class Order:
    def __init__(self):
        self.id = None
        self.customer_id = None
        self.items = []
        self.total = 0

# Business logic scattered in services
class OrderService:
    def calculate_total(self, order):
        return sum(item.price * item.quantity for item in order.items)

    def validate_order(self, order):
        if not order.items:
            raise ValueError("Empty order")
```

**Fix**: Rich entities with business behavior.

```python
# GOOD: Rich entity with business logic
class Order:
    def __init__(self, customer_id: str):
        self.id = str(uuid.uuid4())
        self.customer_id = customer_id
        self.items: List[OrderItem] = []

    def calculate_total(self) -> Money:
        """Entity contains its own business logic."""
        return sum(item.price * item.quantity for item in self.items)

    def validate(self) -> None:
        """Entity validates itself."""
        if not self.items:
            raise EmptyOrderError("Order must have items")
```

## Key Takeaways

### Essential Principles

1. **Entities are enterprise rules**: Core business concepts that would exist without software
2. **Use cases are application rules**: How this application uses entities to accomplish goals
3. **Zero technical dependencies**: Business rules know nothing about databases, frameworks, UI
4. **Entities are stable**: Change only when fundamental business changes
5. **Use cases orchestrate**: Coordinate entities, repositories, and gateways

### Business Rules Checklist

- [ ] Entities have no dependencies on frameworks or infrastructure
- [ ] Entities contain critical business methods and validations
- [ ] Use cases orchestrate entities to accomplish business goals
- [ ] Use cases define interfaces for infrastructure needs
- [ ] Business rules testable with simple unit tests
- [ ] Can understand business logic without knowing technical implementation
- [ ] Entities reusable across different applications

### Implementation Checklist

- [ ] Create entity classes for core business concepts
- [ ] Move business methods into entities (calculate, validate, transition)
- [ ] Extract use cases for each business operation
- [ ] Use cases depend on abstract interfaces, not implementations
- [ ] Write pure unit tests for entities
- [ ] Write unit tests with mocks for use cases
- [ ] Isolate framework code from business rules

## Related Resources

- **DEPENDENCY_RULE.md**: How business rules relate to architecture layers
- **PLUGIN_ARCHITECTURE.md**: Isolating infrastructure from business rules
- **SOLID_PRINCIPLES.md**: Single Responsibility and Dependency Inversion apply here
- **SCREAMING_ARCHITECTURE.md**: Making business rules visible in architecture

## Summary

Business rules are the heart of any software system. They come in two forms: **Entities** (enterprise-wide rules that would exist even without automation) and **Use Cases** (application-specific rules that orchestrate entities to accomplish user goals).

Entities should be pure business objects with zero dependencies—testable with simple unit tests. Use Cases should orchestrate entities and define interfaces for infrastructure needs—testable with mocked dependencies.

Keep business rules free from contamination by technical details. No database code in entities. No framework code in use cases. Pure business logic that clearly expresses the rules that make or save money.
