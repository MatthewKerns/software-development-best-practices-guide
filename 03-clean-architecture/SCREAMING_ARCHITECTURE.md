# Screaming Architecture: Making Intent Obvious

## Overview

Screaming Architecture is the principle that the architecture of a software system should scream its purpose—its business intent—rather than the frameworks, tools, or delivery mechanisms it uses. When you look at the top-level directory structure and file organization, you should immediately understand what the system does, not what technologies it's built with.

**"Architectures should not be about frameworks. Architectures should be about use cases."** — Robert C. Martin, Clean Architecture

Good architecture reveals intent. It tells you what the system is for, what business problems it solves, and what capabilities it provides. The fact that it uses Rails, Spring, React, or PostgreSQL should be a minor implementation detail buried in infrastructure folders, not the first thing you see.

## Why Screaming Architecture Matters

### The Cost of Framework-First Architecture

Traditional framework-centric architectures organize code around technical concerns:

**Obscured Business Intent**: Looking at the codebase, you see "models", "views", "controllers", "services", "repositories"—but you have no idea what the application actually does.

```
src/
├── models/
├── views/
├── controllers/
├── services/
└── repositories/
```

*What does this application do? Is it a hospital system? An e-commerce platform? A social network? You cannot tell.*

**Framework Lock-In**: The entire application structure is dictated by framework conventions. Switching frameworks means restructuring the entire codebase.

**Difficult Onboarding**: New developers spend days understanding the technical structure before learning the business domain. They learn about MVC patterns before understanding what orders, patients, or accounts are.

**Mixed Abstraction Levels**: Business logic is scattered among technical layers. Finding the "place order" feature requires searching through controllers, services, models, and repositories.

### The Benefits of Intent-Revealing Architecture

Screaming architecture provides:
- **Immediate Comprehension**: New developers understand the business domain instantly
- **Business-Centric Navigation**: Find features by business capability, not technical layer
- **Framework Independence**: Technical details are isolated; business structure is preserved
- **Clear Communication**: Architecture communicates with stakeholders in business terms
- **Discoverable Use Cases**: Every use case is visible and findable

## Source Materials

This guide is based on:

- **Clean Architecture** by Robert C. Martin (Chapter 21: "Screaming Architecture")
  - Architecture reveals intent
  - Use case-driven design
  - Framework independence

## What Architecture Should Scream

### Screaming About Business

When you look at the architecture, it should scream about the business:

**Healthcare System**:
```
src/
├── patients/
│   ├── register_patient.py
│   ├── schedule_appointment.py
│   └── view_medical_history.py
├── appointments/
│   ├── book_appointment.py
│   ├── cancel_appointment.py
│   └── reschedule_appointment.py
├── prescriptions/
│   ├── write_prescription.py
│   ├── fill_prescription.py
│   └── check_interactions.py
└── billing/
    ├── generate_invoice.py
    ├── process_payment.py
    └── submit_insurance_claim.py
```

*This screams: "I'm a healthcare system that manages patients, appointments, prescriptions, and billing."*

**E-Commerce System**:
```
src/
├── catalog/
│   ├── browse_products.py
│   ├── search_products.py
│   └── view_product_details.py
├── shopping/
│   ├── add_to_cart.py
│   ├── update_cart.py
│   └── checkout.py
├── orders/
│   ├── place_order.py
│   ├── track_order.py
│   └── cancel_order.py
└── fulfillment/
    ├── pick_items.py
    ├── pack_order.py
    └── ship_order.py
```

*This screams: "I'm an e-commerce system that handles catalogs, shopping, orders, and fulfillment."*

### Not Screaming About Frameworks

When you look at the architecture, it should NOT scream about frameworks:

**Bad - Framework-Centric**:
```
src/
├── models/
│   ├── user.py
│   ├── order.py
│   └── product.py
├── views/
│   ├── user_views.py
│   ├── order_views.py
│   └── product_views.py
├── controllers/
│   ├── user_controller.py
│   ├── order_controller.py
│   └── product_controller.py
└── repositories/
    ├── user_repository.py
    ├── order_repository.py
    └── product_repository.py
```

*This screams: "I'm a Rails/Django/MVC application!" But what does it do? Unknown.*

## Principles of Screaming Architecture

### Principle 1: Organize by Business Capability

Structure your codebase around business features, not technical layers.

**Anti-Pattern - Technical Layers**:
```
ecommerce/
├── entities/
│   ├── user.py
│   ├── product.py
│   └── order.py
├── use_cases/
│   ├── create_user.py
│   ├── create_product.py
│   └── create_order.py
└── repositories/
    ├── user_repository.py
    ├── product_repository.py
    └── order_repository.py
```

*Technical organization: All entities together, all use cases together, all repositories together. Finding "place order" requires jumping between three directories.*

**Good Pattern - Business Capabilities**:
```
ecommerce/
├── catalog/                    # Product browsing capability
│   ├── entities/
│   │   ├── product.py
│   │   └── category.py
│   ├── use_cases/
│   │   ├── browse_catalog.py
│   │   ├── search_products.py
│   │   └── filter_by_category.py
│   └── repositories/
│       └── product_repository.py
├── shopping/                   # Shopping cart capability
│   ├── entities/
│   │   └── cart.py
│   ├── use_cases/
│   │   ├── add_to_cart.py
│   │   ├── update_quantity.py
│   │   └── calculate_total.py
│   └── repositories/
│       └── cart_repository.py
└── orders/                     # Order management capability
    ├── entities/
    │   └── order.py
    ├── use_cases/
    │   ├── place_order.py
    │   ├── track_order.py
    │   └── cancel_order.py
    └── repositories/
        └── order_repository.py
```

*Business organization: Everything related to orders is together. Finding "place order" is trivial—it's in `orders/use_cases/place_order.py`.*

### Principle 2: Make Use Cases First-Class Citizens

Use cases should be prominent, named after business operations, and easy to find.

**Anti-Pattern - Hidden Use Cases**:
```python
# services/order_service.py
class OrderService:
    def create(self, data):  # What business operation is this?
        pass

    def update(self, id, data):  # Update what? Why?
        pass

    def process(self, id):  # Process what? How?
        pass
```

*Generic technical names hide business intent.*

**Good Pattern - Explicit Use Cases**:
```python
# orders/use_cases/place_order.py
class PlaceOrderUseCase:
    """
    Use Case: Place Order

    Actor: Customer
    Goal: Purchase items in shopping cart

    Success Scenario:
    1. Customer reviews cart
    2. Customer provides shipping address
    3. Customer selects payment method
    4. System validates order
    5. System processes payment
    6. System creates order
    7. System sends confirmation
    """

    async def execute(self, request: PlaceOrderRequest) -> PlaceOrderResponse:
        # Business logic for placing an order
        pass

# orders/use_cases/cancel_order.py
class CancelOrderUseCase:
    """
    Use Case: Cancel Order

    Actor: Customer
    Goal: Cancel a previously placed order

    Success Scenario:
    1. Customer requests cancellation
    2. System validates order can be cancelled
    3. System initiates refund
    4. System marks order as cancelled
    5. System notifies customer
    """

    async def execute(self, request: CancelOrderRequest) -> CancelOrderResponse:
        # Business logic for canceling an order
        pass
```

*Business operations are explicit, self-documenting, and easy to find.*

### Principle 3: Defer Framework Details

Frameworks and technical details should be isolated in infrastructure folders, not dominating the architecture.

**Example Structure**:
```
healthcare_system/
├── patients/                   # Business capability (visible)
│   ├── entities/
│   ├── use_cases/
│   └── repositories/
├── appointments/               # Business capability (visible)
│   ├── entities/
│   ├── use_cases/
│   └── repositories/
└── infrastructure/             # Technical details (hidden)
    ├── web/                    # Web framework (FastAPI, Flask, Django)
    │   ├── api/
    │   └── controllers/
    ├── persistence/            # Database (PostgreSQL, MongoDB)
    │   └── sqlalchemy/
    └── external/               # External services
        ├── email/
        └── payment/
```

*Business capabilities are prominent. Framework is buried in infrastructure. You see "patients" and "appointments" before you see "FastAPI" or "PostgreSQL".*

### Principle 4: Name Things After Business Concepts

Use business terminology, not technical jargon.

**Anti-Pattern - Technical Names**:
```python
# BAD: Technical names obscure business meaning
class DataAccessObject:
    def insert(self, record): pass
    def select(self, id): pass
    def update(self, id, values): pass

class ServiceLayer:
    def process_transaction(self, data): pass

class Controller:
    def handle_post(self, request): pass
```

**Good Pattern - Business Names**:
```python
# GOOD: Business names reveal intent
class PatientRepository:
    def register_new_patient(self, patient: Patient) -> None: pass
    def find_patient_by_id(self, patient_id: str) -> Optional[Patient]: pass
    def update_contact_info(self, patient_id: str, contact: ContactInfo) -> None: pass

class AppointmentScheduler:
    def book_appointment(self, patient_id: str, doctor_id: str, time: datetime) -> Appointment: pass

class PatientRegistrationController:
    def register_patient(self, request: PatientRegistrationRequest) -> Response: pass
```

## Real-World Examples

### Example 1: Banking System

**Framework-Centric (Bad)**:
```
banking-app/
├── models/
│   ├── account.py
│   ├── transaction.py
│   └── user.py
├── views/
│   ├── account_views.py
│   └── transaction_views.py
├── controllers/
│   ├── account_controller.py
│   └── transaction_controller.py
└── services/
    ├── account_service.py
    └── transaction_service.py
```

**Business-Centric (Good)**:
```
banking-system/
├── accounts/
│   ├── open_account.py
│   ├── close_account.py
│   ├── check_balance.py
│   └── view_statement.py
├── transactions/
│   ├── deposit_funds.py
│   ├── withdraw_funds.py
│   ├── transfer_funds.py
│   └── reverse_transaction.py
├── loans/
│   ├── apply_for_loan.py
│   ├── approve_loan.py
│   ├── disburse_loan.py
│   └── make_payment.py
└── fraud_detection/
    ├── flag_suspicious_activity.py
    ├── verify_identity.py
    └── block_account.py
```

### Example 2: Rental Property Management

**Framework-Centric (Bad)**:
```
rental-app/
├── entities/
├── use_cases/
├── controllers/
├── repositories/
└── services/
```

**Business-Centric (Good)**:
```
property-management/
├── listings/
│   ├── create_listing.py
│   ├── update_listing.py
│   ├── search_listings.py
│   └── archive_listing.py
├── tenants/
│   ├── apply_for_rental.py
│   ├── screen_tenant.py
│   ├── sign_lease.py
│   └── move_in_tenant.py
├── maintenance/
│   ├── submit_request.py
│   ├── assign_to_vendor.py
│   ├── track_progress.py
│   └── complete_work_order.py
├── rent/
│   ├── collect_rent.py
│   ├── send_reminder.py
│   ├── apply_late_fee.py
│   └── process_refund.py
└── inspections/
    ├── schedule_inspection.py
    ├── perform_inspection.py
    ├── document_issues.py
    └── verify_repairs.py
```

### Example 3: Hospital Management System

**What Should Scream**: Patient care, appointments, medical records, billing

**Architecture**:
```
hospital-system/
├── patient_care/
│   ├── admit_patient/
│   │   ├── use_case.py           # Admit patient use case
│   │   ├── entities.py           # Admission entity
│   │   └── repositories.py       # Admission repository interface
│   ├── discharge_patient/
│   │   ├── use_case.py
│   │   ├── entities.py
│   │   └── repositories.py
│   └── transfer_patient/
│       ├── use_case.py
│       └── entities.py
├── appointments/
│   ├── schedule_appointment/
│   ├── cancel_appointment/
│   └── check_in_patient/
├── medical_records/
│   ├── create_record/
│   ├── update_vitals/
│   ├── add_diagnosis/
│   └── view_history/
├── prescriptions/
│   ├── write_prescription/
│   ├── fill_prescription/
│   └── check_drug_interactions/
└── billing/
    ├── generate_invoice/
    ├── process_insurance_claim/
    └── collect_payment/
```

**Infrastructure (Buried)**:
```
infrastructure/
├── web/
│   └── fastapi_app/
│       ├── routers/
│       └── middleware/
├── persistence/
│   └── postgres/
│       └── repositories/
└── external_services/
    ├── insurance_gateway/
    └── pharmacy_integration/
```

## Implementation Patterns

### Pattern 1: Use Case Per File

Each use case is a separate, discoverable file.

```
orders/
├── place_order.py              # One use case
├── cancel_order.py             # Another use case
├── modify_order.py             # Another use case
└── track_order.py              # Another use case
```

**Implementation**:
```python
# orders/place_order.py
class PlaceOrderUseCase:
    """
    Place Order Use Case

    Business Rule: Customer can place an order if they have items in cart
                  and provide valid payment method.
    """

    def __init__(
        self,
        cart_repository: ICartRepository,
        order_repository: IOrderRepository,
        payment_gateway: IPaymentGateway
    ):
        self._cart = cart_repository
        self._orders = order_repository
        self._payment = payment_gateway

    async def execute(self, request: PlaceOrderRequest) -> PlaceOrderResponse:
        # Retrieve cart
        cart = await self._cart.find_by_customer(request.customer_id)
        if not cart or not cart.items:
            raise EmptyCartError()

        # Validate payment method
        if not request.payment_method:
            raise MissingPaymentMethodError()

        # Process payment
        total = cart.calculate_total()
        payment_result = await self._payment.charge(total, request.payment_method)
        if not payment_result.success:
            raise PaymentFailedError(payment_result.error)

        # Create order
        order = Order.from_cart(cart, payment_result.transaction_id)
        await self._orders.save(order)

        # Clear cart
        await self._cart.clear(request.customer_id)

        return PlaceOrderResponse(order_id=order.id, total=total)
```

### Pattern 2: Feature Folders

Group everything related to a feature together.

```
catalog/
├── entities/
│   ├── product.py
│   ├── category.py
│   └── price.py
├── use_cases/
│   ├── browse_catalog.py
│   ├── search_products.py
│   ├── filter_by_category.py
│   └── apply_discounts.py
├── repositories/
│   └── product_repository.py
└── policies/
    └── pricing_policy.py
```

### Pattern 3: Screaming Entry Points

Top-level files reveal core operations.

```
src/
├── register_patient.py         # Core operation
├── schedule_appointment.py     # Core operation
├── prescribe_medication.py     # Core operation
├── generate_invoice.py         # Core operation
└── infrastructure/             # Technical details hidden
    ├── web/
    ├── database/
    └── external/
```

## How to Migrate to Screaming Architecture

### Step 1: Identify Business Capabilities

List the major business capabilities your system provides:

**Example - E-Commerce**:
- Product catalog management
- Shopping cart operations
- Order processing
- Payment handling
- Inventory management
- Shipping and fulfillment
- Customer account management

### Step 2: Create Capability Folders

Create top-level folders for each business capability:

```
src/
├── catalog/
├── shopping/
├── orders/
├── payments/
├── inventory/
├── fulfillment/
└── accounts/
```

### Step 3: Extract Use Cases

Identify and extract explicit use cases for each capability:

```
orders/
├── use_cases/
│   ├── place_order.py
│   ├── cancel_order.py
│   ├── modify_order.py
│   ├── track_order.py
│   └── return_order.py
```

### Step 4: Move Supporting Code

Move entities, repositories, and other supporting code into capability folders:

```
orders/
├── entities/
│   ├── order.py
│   ├── order_item.py
│   └── order_status.py
├── use_cases/
│   ├── place_order.py
│   └── cancel_order.py
├── repositories/
│   └── order_repository.py
└── policies/
    └── cancellation_policy.py
```

### Step 5: Isolate Framework

Move framework-specific code to infrastructure:

```
infrastructure/
├── web/
│   └── fastapi/
│       ├── routers/
│       │   ├── order_router.py
│       │   └── catalog_router.py
│       └── middleware/
├── persistence/
│   └── postgres/
│       └── repositories/
└── external/
    └── stripe/
        └── payment_gateway.py
```

## Common Mistakes

### Mistake 1: Technical Grouping at Top Level

**Problem**: Top-level folders are technical layers.

```
# BAD
src/
├── controllers/
├── services/
├── repositories/
└── models/
```

**Fix**: Top-level folders are business capabilities.

```
# GOOD
src/
├── orders/
├── catalog/
├── shipping/
└── payments/
```

### Mistake 2: Generic Use Case Names

**Problem**: Use cases named with generic technical terms.

```python
# BAD
class OrderService:
    def create(self, data): pass
    def update(self, id, data): pass
    def delete(self, id): pass
```

**Fix**: Use cases named with specific business operations.

```python
# GOOD
class PlaceOrderUseCase:
    def execute(self, request: PlaceOrderRequest) -> PlaceOrderResponse: pass

class CancelOrderUseCase:
    def execute(self, request: CancelOrderRequest) -> CancelOrderResponse: pass

class ModifyOrderUseCase:
    def execute(self, request: ModifyOrderRequest) -> ModifyOrderResponse: pass
```

### Mistake 3: Framework Dominance

**Problem**: Framework structure dictates business structure.

```
# BAD: Django app structure dominates
myapp/
├── models.py           # All models in one file
├── views.py            # All views in one file
├── urls.py             # All URLs in one file
└── admin.py            # All admin in one file
```

**Fix**: Business structure with framework isolated.

```
# GOOD: Business capabilities visible
healthcare/
├── patients/
│   ├── register_patient.py
│   └── view_medical_history.py
├── appointments/
│   ├── schedule_appointment.py
│   └── cancel_appointment.py
└── infrastructure/
    └── django/            # Framework isolated
        ├── models.py
        ├── views.py
        └── urls.py
```

### Mistake 4: Abstracting Too Early

**Problem**: Creating generic abstractions before understanding the domain.

```python
# BAD: Generic abstraction obscures business intent
class GenericProcessor:
    def process(self, entity: Entity, operation: Operation) -> Result:
        pass
```

**Fix**: Start with concrete, named business operations.

```python
# GOOD: Explicit business operations
class ProcessPaymentUseCase:
    def execute(self, payment: Payment) -> PaymentResult:
        pass

class RefundPaymentUseCase:
    def execute(self, refund: Refund) -> RefundResult:
        pass
```

## Key Takeaways

### Essential Principles

1. **Architecture reveals business intent**: Structure communicates what the system does
2. **Organize by capability**: Group by business features, not technical layers
3. **Use cases are first-class**: Business operations are explicit and prominent
4. **Frameworks are details**: Technical decisions buried in infrastructure
5. **Name with business terms**: Use domain language throughout

### Screaming Architecture Checklist

- [ ] Top-level folders named after business capabilities
- [ ] Use cases explicitly named and easily discoverable
- [ ] New developers understand domain before learning framework
- [ ] Business operations visible without digging through layers
- [ ] Framework code isolated in infrastructure folders
- [ ] Names use business terminology, not technical jargon
- [ ] Architecture communicates with stakeholders

### Migration Checklist

- [ ] Identify business capabilities
- [ ] Create capability folders at top level
- [ ] Extract and name use cases explicitly
- [ ] Move entities and repositories into capabilities
- [ ] Isolate framework code in infrastructure
- [ ] Rename technical terms to business concepts
- [ ] Update documentation to reflect business structure

## Related Resources

- **DEPENDENCY_RULE.md**: How dependencies flow in clean architecture
- **PLUGIN_ARCHITECTURE.md**: Isolating framework as implementation detail
- **ARCHITECTURAL_BOUNDARIES.md**: Where to draw lines between capabilities
- **BUSINESS_RULES.md**: Entities and use cases as core business concepts

## Summary

Screaming Architecture is about making your system's purpose obvious from its structure. When someone looks at your codebase, they should immediately see what business problems it solves—orders, appointments, prescriptions, payments—not what technical tools it uses—controllers, services, models, repositories.

Organize by business capability, make use cases first-class citizens, defer framework details to infrastructure folders, and name everything using business terminology. Your architecture should scream about the domain, not the technology.

A good architecture tells readers about the system, not about the frameworks. It allows frameworks to be details, plugins, and tools—not the substance of the system. It puts use cases front and center, making them scream from the architecture.
