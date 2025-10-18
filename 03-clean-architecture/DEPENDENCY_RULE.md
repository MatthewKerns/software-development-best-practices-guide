# The Dependency Rule: Core Principle of Clean Architecture

## Overview

The Dependency Rule is the fundamental principle that makes clean architecture work. It states that source code dependencies must point only inward, toward higher-level policies. This simple rule creates systems where business logic is independent of frameworks, databases, UI, and external agencies.

**"Source code dependencies must point only inward, toward higher-level policies."** — Robert C. Martin, Clean Architecture

This principle is the architectural manifestation of the Dependency Inversion Principle (DIP) applied at the system level. It enables the separation of concerns that makes software testable, maintainable, and flexible.

## Why the Dependency Rule Matters

### The Cost of Violating the Dependency Rule

Systems that violate the dependency rule exhibit:

**Business Logic Coupled to Frameworks**: Core business rules depend on Spring, React, or Django. Changing frameworks requires rewriting business logic.

**Untestable Code**: Cannot test business rules without spinning up databases, web servers, or external APIs.

**Rigid Architecture**: Adding new delivery mechanisms (web, mobile, CLI) requires modifying core business logic.

**Vendor Lock-In**: Switching databases, cloud providers, or third-party services requires massive refactoring.

**Fragile Code**: UI changes break business rules. Database schema changes break use cases. Everything is tangled.

### The Benefits of Following the Dependency Rule

Well-architected systems provide:
- **Independent Business Logic**: Core rules have no external dependencies
- **Framework Independence**: Frameworks are plugins, not foundations
- **Testability**: Business logic tested without infrastructure
- **UI Independence**: Same business logic serves web, mobile, CLI
- **Database Independence**: Switch databases without touching business code
- **External Agency Independence**: External services are details, easily swapped

## Source Materials

This guide is based on:

- **Clean Architecture** by Robert C. Martin (Chapter 17: "Boundaries: Drawing Lines")
  - The Dependency Rule explained
  - Architectural boundaries
  - Plugin architecture

## The Clean Architecture Diagram

The iconic concentric circles diagram illustrates the dependency rule:

```
                    ┌─────────────────────────────────┐
                    │   Frameworks & Drivers          │  External
                    │  (Web, DB, UI, Devices)         │
                    │                                 │
                    │   ┌───────────────────────┐     │
                    │   │ Interface Adapters    │     │  Interface
                    │   │  (Controllers,        │     │  Adapters
                    │   │   Presenters,         │     │
                    │   │   Gateways)           │     │
                    │   │                       │     │
                    │   │  ┌────────────────┐   │     │
                    │   │  │ Application    │   │     │  Application
                    │   │  │  Business      │   │     │  Business
                    │   │  │  Rules         │   │     │  Rules
                    │   │  │  (Use Cases)   │   │     │
                    │   │  │                │   │     │
                    │   │  │  ┌──────────┐  │   │     │
                    │   │  │  │Enterprise│  │   │     │  Enterprise
                    │   │  │  │ Business │  │   │     │  Business
                    │   │  │  │  Rules   │  │   │     │  Rules
                    │   │  │  │(Entities)│  │   │     │
                    │   │  │  └──────────┘  │   │     │
                    │   │  └────────────────┘   │     │
                    │   └───────────────────────┘     │
                    └─────────────────────────────────┘

              Dependencies point INWARD only ───→
```

### The Four Layers

**Entities (Center)**: Enterprise-wide business rules. Most general, highest-level rules. Change least frequently.

**Use Cases (Application Business Rules)**: Application-specific business rules. Orchestrate data flow to and from entities. Direct entities to use their enterprise business rules.

**Interface Adapters**: Convert data between use case/entity format and external format. Controllers, presenters, gateways live here.

**Frameworks & Drivers (Outer)**: Frameworks, tools, databases, web frameworks. Most volatile. Change most frequently.

### The Dependency Rule in Practice

Code in inner circles:
- **Cannot** mention anything in outer circles
- **Cannot** import frameworks, databases, or UI code
- **Cannot** reference external libraries or tools
- **Can** define interfaces that outer circles implement

Code in outer circles:
- **Can** depend on inner circles
- **Must** depend on abstractions defined in inner circles
- **Cannot** force inner circles to depend on them
- **Must** implement interfaces defined by inner circles

## Understanding Each Layer

### Layer 1: Entities (Enterprise Business Rules)

**Purpose**: Encapsulate critical business rules that are true regardless of automation.

**Characteristics**:
- Pure business logic
- No dependencies on any outer layer
- No dependencies on frameworks
- Would exist even without the application

**Example:**

```python
# entities/account.py
from decimal import Decimal
from datetime import datetime
from typing import Optional

class Account:
    """
    Enterprise business rule: Account management
    These rules would exist even without computer systems
    """

    def __init__(
        self,
        account_id: str,
        balance: Decimal,
        overdraft_limit: Decimal = Decimal('0')
    ):
        self._account_id = account_id
        self._balance = balance
        self._overdraft_limit = overdraft_limit
        self._transactions: list[Transaction] = []

    def deposit(self, amount: Decimal) -> None:
        """Business rule: Can always deposit positive amounts"""
        if amount <= 0:
            raise ValueError("Deposit amount must be positive")

        self._balance += amount
        self._record_transaction("DEPOSIT", amount)

    def withdraw(self, amount: Decimal) -> None:
        """Business rule: Can withdraw up to balance + overdraft limit"""
        if amount <= 0:
            raise ValueError("Withdrawal amount must be positive")

        available = self._balance + self._overdraft_limit
        if amount > available:
            raise InsufficientFundsError(
                f"Insufficient funds. Available: {available}"
            )

        self._balance -= amount
        self._record_transaction("WITHDRAWAL", amount)

    def transfer_to(self, recipient: 'Account', amount: Decimal) -> None:
        """Business rule: Transfer is atomic - withdraw then deposit"""
        self.withdraw(amount)
        recipient.deposit(amount)

    def is_overdrawn(self) -> bool:
        """Business rule: Overdrawn when balance is negative"""
        return self._balance < 0

    def _record_transaction(self, type_: str, amount: Decimal) -> None:
        transaction = Transaction(
            timestamp=datetime.now(),
            type=type_,
            amount=amount,
            resulting_balance=self._balance
        )
        self._transactions.append(transaction)

    @property
    def balance(self) -> Decimal:
        return self._balance

    @property
    def account_id(self) -> str:
        return self._account_id

class Transaction:
    """Value object for transactions"""
    def __init__(
        self,
        timestamp: datetime,
        type: str,
        amount: Decimal,
        resulting_balance: Decimal
    ):
        self.timestamp = timestamp
        self.type = type
        self.amount = amount
        self.resulting_balance = resulting_balance

class InsufficientFundsError(Exception):
    """Domain exception - part of business rules"""
    pass

# Note: Zero dependencies on frameworks, databases, or UI
# Could be used in any application - web, mobile, CLI, batch
```

### Layer 2: Use Cases (Application Business Rules)

**Purpose**: Application-specific business rules. Orchestrate flow of data to and from entities.

**Characteristics**:
- Depend on entities (inner layer)
- Define interfaces for data access (implemented by outer layers)
- No knowledge of how data is delivered or stored
- No dependencies on frameworks or UI

**Example:**

```typescript
// use-cases/transfer-funds.ts

// Interfaces that use cases depend on (implemented by outer layers)
export interface AccountGateway {
    findById(accountId: string): Promise<Account | null>;
    save(account: Account): Promise<void>;
}

export interface TransactionLogger {
    logTransfer(
        fromAccount: string,
        toAccount: string,
        amount: number
    ): Promise<void>;
}

// Input data structure
export interface TransferFundsRequest {
    fromAccountId: string;
    toAccountId: string;
    amount: number;
}

// Output data structure
export interface TransferFundsResponse {
    success: boolean;
    message: string;
    newBalance?: number;
}

// Use case - application-specific business rule
export class TransferFundsUseCase {
    constructor(
        private accountGateway: AccountGateway,
        private transactionLogger: TransactionLogger
    ) {}

    async execute(request: TransferFundsRequest): Promise<TransferFundsResponse> {
        // Validate input
        if (request.amount <= 0) {
            return {
                success: false,
                message: "Transfer amount must be positive"
            };
        }

        // Retrieve entities
        const fromAccount = await this.accountGateway.findById(
            request.fromAccountId
        );
        const toAccount = await this.accountGateway.findById(
            request.toAccountId
        );

        if (!fromAccount) {
            return {
                success: false,
                message: "Source account not found"
            };
        }

        if (!toAccount) {
            return {
                success: false,
                message: "Destination account not found"
            };
        }

        // Execute business rule (entity method)
        try {
            fromAccount.transferTo(toAccount, request.amount);
        } catch (error) {
            return {
                success: false,
                message: error.message
            };
        }

        // Persist changes
        await this.accountGateway.save(fromAccount);
        await this.accountGateway.save(toAccount);

        // Log transaction
        await this.transactionLogger.logTransfer(
            request.fromAccountId,
            request.toAccountId,
            request.amount
        );

        return {
            success: true,
            message: "Transfer completed successfully",
            newBalance: fromAccount.balance
        };
    }
}

// Note: Use case depends on Account entity (inner layer)
// Use case defines interfaces (AccountGateway, TransactionLogger)
// No dependencies on databases, frameworks, or UI
```

### Layer 3: Interface Adapters

**Purpose**: Convert data between the format most convenient for use cases/entities and the format most convenient for external agencies.

**Characteristics**:
- Implement interfaces defined by use cases
- Convert between internal and external data formats
- Controllers, presenters, gateways live here
- Depend on use cases and entities (inner layers)

**Example:**

```java
// interface-adapters/controllers/TransferController.java
package com.mybank.adapters.controllers;

import com.mybank.usecases.TransferFundsUseCase;
import com.mybank.usecases.TransferFundsRequest;
import com.mybank.usecases.TransferFundsResponse;

// Web framework classes (outer layer)
import org.springframework.web.bind.annotation.*;
import org.springframework.http.ResponseEntity;

@RestController
@RequestMapping("/api/transfers")
public class TransferController {
    private final TransferFundsUseCase transferFunds;

    public TransferController(TransferFundsUseCase transferFunds) {
        this.transferFunds = transferFunds;
    }

    @PostMapping
    public ResponseEntity<TransferResponseDTO> transfer(
        @RequestBody TransferRequestDTO dto
    ) {
        // Convert web DTO to use case request (data format conversion)
        TransferFundsRequest request = new TransferFundsRequest(
            dto.getFromAccountId(),
            dto.getToAccountId(),
            dto.getAmount()
        );

        // Execute use case
        TransferFundsResponse response = transferFunds.execute(request);

        // Convert use case response to web DTO (data format conversion)
        TransferResponseDTO responseDto = new TransferResponseDTO(
            response.isSuccess(),
            response.getMessage(),
            response.getNewBalance()
        );

        // Return appropriate HTTP status
        if (response.isSuccess()) {
            return ResponseEntity.ok(responseDto);
        } else {
            return ResponseEntity.badRequest().body(responseDto);
        }
    }
}

// DTOs for web layer (outer layer concerns)
class TransferRequestDTO {
    private String fromAccountId;
    private String toAccountId;
    private BigDecimal amount;

    // Getters/setters
}

class TransferResponseDTO {
    private boolean success;
    private String message;
    private BigDecimal newBalance;

    // Constructor, getters/setters
}

// interface-adapters/gateways/DatabaseAccountGateway.java
package com.mybank.adapters.gateways;

import com.mybank.entities.Account;
import com.mybank.usecases.AccountGateway;  // Interface from use case layer

// Database framework (outer layer)
import javax.persistence.*;

public class DatabaseAccountGateway implements AccountGateway {
    private final EntityManager entityManager;

    public DatabaseAccountGateway(EntityManager entityManager) {
        this.entityManager = entityManager;
    }

    @Override
    public Account findById(String accountId) {
        // Convert from database entity to domain entity
        AccountJpaEntity jpaEntity = entityManager.find(
            AccountJpaEntity.class,
            accountId
        );

        if (jpaEntity == null) {
            return null;
        }

        // Map database format to domain format
        return new Account(
            jpaEntity.getId(),
            jpaEntity.getBalance(),
            jpaEntity.getOverdraftLimit()
        );
    }

    @Override
    public void save(Account account) {
        // Convert from domain entity to database entity
        AccountJpaEntity jpaEntity = new AccountJpaEntity();
        jpaEntity.setId(account.getAccountId());
        jpaEntity.setBalance(account.getBalance());

        entityManager.merge(jpaEntity);
    }
}

// Database entity (outer layer concern)
@Entity
@Table(name = "accounts")
class AccountJpaEntity {
    @Id
    private String id;
    private BigDecimal balance;
    private BigDecimal overdraftLimit;

    // Getters/setters
}
```

### Layer 4: Frameworks & Drivers

**Purpose**: Glue code that connects everything. Database schemas, web server configuration, external libraries.

**Characteristics**:
- Most volatile layer - changes frequently
- Frameworks, tools, databases
- Outermost layer - depends on everything inward
- Very little custom code here

**Example:**

```python
# frameworks-drivers/main.py - Application entry point
from fastapi import FastAPI
from frameworks.database import DatabaseConnection
from interface_adapters.controllers import TransferController
from interface_adapters.gateways import DatabaseAccountGateway
from use_cases.transfer_funds import TransferFundsUseCase

# Framework configuration (outer layer)
app = FastAPI()

# Dependency injection / wiring
db_connection = DatabaseConnection("postgresql://localhost/bank")
account_gateway = DatabaseAccountGateway(db_connection)
transfer_use_case = TransferFundsUseCase(account_gateway)
transfer_controller = TransferController(transfer_use_case)

# Register routes (framework-specific)
app.include_router(transfer_controller.router)

# frameworks-drivers/database/schema.sql
-- Database schema (outer layer detail)
CREATE TABLE accounts (
    id VARCHAR(50) PRIMARY KEY,
    balance DECIMAL(15, 2) NOT NULL,
    overdraft_limit DECIMAL(15, 2) DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_accounts_balance ON accounts(balance);

-- This is a detail - could change to MongoDB, DynamoDB, etc.
-- without affecting inner layers
```

## Crossing Boundaries: The Dependency Inversion Trick

**Problem**: Inner layers need functionality from outer layers (e.g., use cases need to save data, which requires database access in the outer layer).

**Solution**: Dependency Inversion. Inner layers define interfaces. Outer layers implement them.

### Example: Use Case Needs Data Access

```typescript
// WRONG: Use case depends on outer layer
// use-cases/create-user.ts
import { PostgreSQLDatabase } from '../frameworks/database';  // WRONG!

export class CreateUserUseCase {
    execute(userData: UserData): void {
        const db = new PostgreSQLDatabase();  // Direct dependency on outer layer!
        db.saveUser(userData);
    }
}

// RIGHT: Use case defines interface, outer layer implements
// use-cases/create-user.ts (Inner layer)
export interface UserRepository {
    save(user: User): Promise<void>;
}

export class CreateUserUseCase {
    constructor(private userRepository: UserRepository) {}

    async execute(userData: UserData): Promise<void> {
        const user = new User(userData);
        await this.userRepository.save(user);  // Depends on interface
    }
}

// interface-adapters/gateways/postgresql-user-repository.ts (Outer layer)
import { UserRepository } from '../../use-cases/create-user';
import { PostgreSQLDatabase } from '../../frameworks/database';

export class PostgreSQLUserRepository implements UserRepository {
    constructor(private db: PostgreSQLDatabase) {}

    async save(user: User): Promise<void> {
        // PostgreSQL-specific implementation
        await this.db.query(
            'INSERT INTO users (id, name, email) VALUES ($1, $2, $3)',
            [user.id, user.name, user.email]
        );
    }
}

// Dependency points inward: PostgreSQLUserRepository -> UserRepository
```

### The Control Flow vs. Dependency Flow

**Control Flow**: Controller → Use Case → Gateway → Database

**Dependency Flow**: Database → Gateway → Use Case ← Controller

```
Control Flow (runtime):
Controller ──→ Use Case ──→ Gateway ──→ Database

Dependency Flow (compile time):
Controller ──→ Use Case ←── Gateway ←── Database
                   ↑
                   │
            (defines interface)
```

The use case defines an interface. The gateway implements it. At runtime, control flows outward (use case calls gateway). At compile time, dependencies point inward (gateway depends on interface defined by use case).

## Practical Examples

### Example 1: E-Commerce Order Processing

```python
# entities/order.py (Innermost layer)
from decimal import Decimal
from typing import List

class Order:
    """Enterprise business rule: Order management"""

    def __init__(self, order_id: str, customer_id: str):
        self.order_id = order_id
        self.customer_id = customer_id
        self.items: List[OrderItem] = []
        self.status = OrderStatus.PENDING

    def add_item(self, product_id: str, quantity: int, price: Decimal) -> None:
        """Business rule: Can add items only to pending orders"""
        if self.status != OrderStatus.PENDING:
            raise InvalidOperationError("Cannot modify submitted order")

        item = OrderItem(product_id, quantity, price)
        self.items.append(item)

    def calculate_total(self) -> Decimal:
        """Business rule: Total is sum of item prices"""
        return sum(item.quantity * item.price for item in self.items)

    def submit(self) -> None:
        """Business rule: Order must have items to submit"""
        if not self.items:
            raise InvalidOperationError("Cannot submit empty order")

        self.status = OrderStatus.SUBMITTED

# use-cases/submit-order.py (Application business rules)
from entities.order import Order

class OrderRepository:
    """Interface defined by use case"""
    def find_by_id(self, order_id: str) -> Order:
        raise NotImplementedError

    def save(self, order: Order) -> None:
        raise NotImplementedError

class PaymentGateway:
    """Interface defined by use case"""
    def charge(self, customer_id: str, amount: Decimal) -> PaymentResult:
        raise NotImplementedError

class SubmitOrderUseCase:
    def __init__(
        self,
        order_repo: OrderRepository,
        payment_gateway: PaymentGateway
    ):
        self.order_repo = order_repo
        self.payment_gateway = payment_gateway

    def execute(self, order_id: str) -> SubmitOrderResponse:
        # Retrieve entity
        order = self.order_repo.find_by_id(order_id)

        # Execute business rule
        try:
            order.submit()
        except InvalidOperationError as e:
            return SubmitOrderResponse(success=False, message=str(e))

        # Process payment
        total = order.calculate_total()
        payment_result = self.payment_gateway.charge(
            order.customer_id,
            total
        )

        if not payment_result.success:
            return SubmitOrderResponse(
                success=False,
                message="Payment failed"
            )

        # Persist changes
        self.order_repo.save(order)

        return SubmitOrderResponse(
            success=True,
            message="Order submitted successfully",
            order_id=order.order_id
        )

# interface-adapters/controllers/order-controller.py (Web adapter)
from fastapi import APIRouter, HTTPException
from use_cases.submit_order import SubmitOrderUseCase

class OrderController:
    def __init__(self, submit_order_use_case: SubmitOrderUseCase):
        self.submit_order = submit_order_use_case
        self.router = APIRouter()

        @self.router.post("/orders/{order_id}/submit")
        async def submit_order(order_id: str):
            response = self.submit_order.execute(order_id)

            if not response.success:
                raise HTTPException(status_code=400, detail=response.message)

            return {"message": response.message, "orderId": response.order_id}

# interface-adapters/gateways/sql-order-repository.py (Database adapter)
from use_cases.submit_order import OrderRepository
from entities.order import Order

class SQLOrderRepository(OrderRepository):
    def __init__(self, db_connection):
        self.db = db_connection

    def find_by_id(self, order_id: str) -> Order:
        # SQL-specific data retrieval
        row = self.db.query(
            "SELECT * FROM orders WHERE id = ?",
            [order_id]
        )
        # Convert database format to entity
        return self._row_to_entity(row)

    def save(self, order: Order) -> None:
        # Convert entity to database format
        # SQL-specific data persistence
        self.db.execute(
            "UPDATE orders SET status = ? WHERE id = ?",
            [order.status, order.order_id]
        )

# Dependency flow: All outer layers depend inward
# Control flow: Controller → Use Case → Gateway → Database
```

### Example 2: Email Service with Multiple Providers

```java
// entities/Email.java (Entity)
package com.myapp.entities;

public class Email {
    private final String to;
    private final String subject;
    private final String body;

    public Email(String to, String subject, String body) {
        if (to == null || !to.contains("@")) {
            throw new InvalidEmailException("Invalid email address");
        }
        this.to = to;
        this.subject = subject;
        this.body = body;
    }

    // Getters
    public String getTo() { return to; }
    public String getSubject() { return subject; }
    public String getBody() { return body; }
}

// use-cases/SendEmail.java (Use case)
package com.myapp.usecases;

import com.myapp.entities.Email;

public interface EmailGateway {
    void send(Email email);
}

public class SendEmailUseCase {
    private final EmailGateway emailGateway;

    public SendEmailUseCase(EmailGateway emailGateway) {
        this.emailGateway = emailGateway;
    }

    public void execute(String to, String subject, String body) {
        Email email = new Email(to, subject, body);
        emailGateway.send(email);
    }
}

// interface-adapters/gateways/SendGridEmailGateway.java (Adapter)
package com.myapp.adapters.gateways;

import com.myapp.usecases.EmailGateway;
import com.myapp.entities.Email;
import com.sendgrid.*;  // External library

public class SendGridEmailGateway implements EmailGateway {
    private final SendGrid sendGridClient;

    public SendGridEmailGateway(String apiKey) {
        this.sendGridClient = new SendGrid(apiKey);
    }

    @Override
    public void send(Email email) {
        // Convert domain Email to SendGrid format
        com.sendgrid.Email from = new com.sendgrid.Email("noreply@myapp.com");
        com.sendgrid.Email to = new com.sendgrid.Email(email.getTo());
        Content content = new Content("text/plain", email.getBody());
        Mail mail = new Mail(from, email.getSubject(), to, content);

        // Send via SendGrid
        try {
            Request request = new Request();
            request.setMethod(Method.POST);
            request.setEndpoint("mail/send");
            request.setBody(mail.build());
            sendGridClient.api(request);
        } catch (IOException e) {
            throw new EmailSendException("Failed to send email", e);
        }
    }
}

// Easy to swap providers - just implement EmailGateway
// interface-adapters/gateways/MailgunEmailGateway.java
package com.myapp.adapters.gateways;

import com.myapp.usecases.EmailGateway;
import com.myapp.entities.Email;

public class MailgunEmailGateway implements EmailGateway {
    private final MailgunClient mailgunClient;

    public MailgunEmailGateway(String apiKey, String domain) {
        this.mailgunClient = new MailgunClient(apiKey, domain);
    }

    @Override
    public void send(Email email) {
        // Mailgun-specific implementation
        mailgunClient.sendEmail(
            email.getTo(),
            email.getSubject(),
            email.getBody()
        );
    }
}

// Dependency: SendGridEmailGateway -> EmailGateway (inner)
//             MailgunEmailGateway -> EmailGateway (inner)
// Use case doesn't know or care which implementation is used
```

## Testing with the Dependency Rule

The dependency rule makes testing trivial. Inner layers have no dependencies, so they're easy to test. Outer layers depend on interfaces, so you can inject test doubles.

### Testing Entities

```python
# test_account.py
from entities.account import Account
from decimal import Decimal
import pytest

def test_deposit_increases_balance():
    account = Account("ACC-001", Decimal("100"))

    account.deposit(Decimal("50"))

    assert account.balance == Decimal("150")

def test_withdraw_within_limit():
    account = Account("ACC-001", Decimal("100"))

    account.withdraw(Decimal("50"))

    assert account.balance == Decimal("50")

def test_withdraw_exceeding_limit_raises_error():
    account = Account("ACC-001", Decimal("100"))

    with pytest.raises(InsufficientFundsError):
        account.withdraw(Decimal("150"))

# No mocks needed - entity has no dependencies!
```

### Testing Use Cases

```typescript
// transfer-funds.test.ts
import { TransferFundsUseCase } from './transfer-funds';
import { Account } from '../entities/account';

// Test doubles implementing interfaces
class InMemoryAccountGateway implements AccountGateway {
    private accounts = new Map<string, Account>();

    async findById(accountId: string): Promise<Account | null> {
        return this.accounts.get(accountId) || null;
    }

    async save(account: Account): Promise<void> {
        this.accounts.set(account.accountId, account);
    }

    // Test helper
    addAccount(account: Account): void {
        this.accounts.set(account.accountId, account);
    }
}

class StubTransactionLogger implements TransactionLogger {
    public transfers: Array<{from: string, to: string, amount: number}> = [];

    async logTransfer(from: string, to: string, amount: number): Promise<void> {
        this.transfers.push({from, to, amount});
    }
}

describe('TransferFundsUseCase', () => {
    let gateway: InMemoryAccountGateway;
    let logger: StubTransactionLogger;
    let useCase: TransferFundsUseCase;

    beforeEach(() => {
        gateway = new InMemoryAccountGateway();
        logger = new StubTransactionLogger();
        useCase = new TransferFundsUseCase(gateway, logger);
    });

    it('transfers funds between accounts', async () => {
        const fromAccount = new Account('ACC-001', 1000);
        const toAccount = new Account('ACC-002', 500);
        gateway.addAccount(fromAccount);
        gateway.addAccount(toAccount);

        const response = await useCase.execute({
            fromAccountId: 'ACC-001',
            toAccountId: 'ACC-002',
            amount: 200
        });

        expect(response.success).toBe(true);
        expect(fromAccount.balance).toBe(800);
        expect(toAccount.balance).toBe(700);
        expect(logger.transfers).toHaveLength(1);
    });

    it('fails when source account has insufficient funds', async () => {
        const fromAccount = new Account('ACC-001', 100);
        const toAccount = new Account('ACC-002', 500);
        gateway.addAccount(fromAccount);
        gateway.addAccount(toAccount);

        const response = await useCase.execute({
            fromAccountId: 'ACC-001',
            toAccountId: 'ACC-002',
            amount: 200
        });

        expect(response.success).toBe(false);
        expect(response.message).toContain('Insufficient funds');
    });
});

// No real database, no web server - just fast, focused tests
```

## Integration with Geist Framework

The Dependency Rule aligns with three-dimensional Geist analysis:

### Ghost (Unknown Unknowns) + Dependency Rule

**Reveals Hidden Dependencies**: Violating the dependency rule creates hidden coupling. Following it exposes all dependencies as explicit interfaces.

**Example**: If your business logic directly uses a database library, you won't discover coupling issues until you try to test or swap databases.

### Geyser (Dynamic Forces) + Dependency Rule

**Prepares for Inevitable Change**: The dependency rule assumes change is inevitable. Frameworks, databases, and UI will change. Business rules are more stable.

**Example**: By isolating business logic from frameworks, you can upgrade frameworks or switch technologies without rewriting core logic.

### Gist (Essential Core) + Dependency Rule

**Identifies Essential vs. Accidental**: The inner circles contain essential business logic. The outer circles contain accidental complexity (how we deliver, store, or display).

**Example**: "Transfer money between accounts" is essential. "Save to PostgreSQL" or "Display in React" is accidental.

## Common Violations and How to Fix Them

### Violation 1: Entity Depends on Framework

```python
# BAD: Entity uses Django ORM
from django.db import models

class User(models.Model):  # Entity depends on Django!
    username = models.CharField(max_length=100)
    email = models.EmailField()

    def is_valid_email(self):
        return "@" in self.email

# GOOD: Pure entity, separate ORM model
class User:
    """Pure business logic - no framework dependency"""
    def __init__(self, username: str, email: str):
        self.username = username
        self.email = email

    def is_valid_email(self) -> bool:
        return "@" in self.email and "." in self.email

# Separate Django model in outer layer
from django.db import models

class UserModel(models.Model):
    username = models.CharField(max_length=100)
    email = models.EmailField()

    def to_entity(self) -> User:
        return User(self.username, self.email)

    @staticmethod
    def from_entity(user: User) -> 'UserModel':
        return UserModel(username=user.username, email=user.email)
```

### Violation 2: Use Case Depends on Web Framework

```java
// BAD: Use case depends on HTTP request
import javax.servlet.http.HttpServletRequest;

public class CreateUserUseCase {
    public void execute(HttpServletRequest request) {
        String username = request.getParameter("username");
        // Business logic mixed with web concerns
    }
}

// GOOD: Use case depends on plain data
public class CreateUserUseCase {
    public CreateUserResponse execute(CreateUserRequest request) {
        // Business logic with no web framework dependency
        User user = new User(request.getUsername(), request.getEmail());
        // ...
        return new CreateUserResponse(user.getId());
    }
}

// Controller adapts web request to use case request
import javax.servlet.http.HttpServletRequest;

public class UserController {
    private CreateUserUseCase createUser;

    public void handleCreateUser(HttpServletRequest httpRequest) {
        CreateUserRequest request = new CreateUserRequest(
            httpRequest.getParameter("username"),
            httpRequest.getParameter("email")
        );

        CreateUserResponse response = createUser.execute(request);
        // Adapt response to HTTP response
    }
}
```

### Violation 3: Business Logic in Controller

```typescript
// BAD: Business logic in controller
class OrderController {
    async createOrder(req: Request, res: Response) {
        // Business logic in controller!
        const order = new Order(req.body.customerId);

        for (const item of req.body.items) {
            order.addItem(item.productId, item.quantity, item.price);
        }

        const total = order.calculateTotal();

        // Payment processing logic in controller!
        const paymentGateway = new StripeGateway();
        const paymentResult = await paymentGateway.charge(total);

        if (paymentResult.success) {
            await database.saveOrder(order);
            res.json({success: true});
        } else {
            res.status(400).json({success: false});
        }
    }
}

// GOOD: Business logic in use case
class CreateOrderUseCase {
    constructor(
        private orderRepo: OrderRepository,
        private paymentGateway: PaymentGateway
    ) {}

    async execute(request: CreateOrderRequest): Promise<CreateOrderResponse> {
        const order = new Order(request.customerId);

        for (const item of request.items) {
            order.addItem(item.productId, item.quantity, item.price);
        }

        const total = order.calculateTotal();
        const paymentResult = await this.paymentGateway.charge(total);

        if (!paymentResult.success) {
            return {success: false, message: "Payment failed"};
        }

        await this.orderRepo.save(order);
        return {success: true, orderId: order.id};
    }
}

class OrderController {
    constructor(private createOrder: CreateOrderUseCase) {}

    async handleCreateOrder(req: Request, res: Response) {
        // Adapt web request to use case request
        const request = new CreateOrderRequest(
            req.body.customerId,
            req.body.items
        );

        const response = await this.createOrder.execute(request);

        // Adapt use case response to HTTP response
        if (response.success) {
            res.json(response);
        } else {
            res.status(400).json(response);
        }
    }
}
```

## Practical Checklist

### Entities Layer
- [ ] No dependencies on outer layers
- [ ] No framework imports
- [ ] No database libraries
- [ ] No UI code
- [ ] Pure business logic
- [ ] Could exist without automation

### Use Cases Layer
- [ ] Depend only on entities (inner layer)
- [ ] Define interfaces for data access
- [ ] No framework dependencies
- [ ] No knowledge of data storage mechanism
- [ ] No knowledge of data delivery mechanism
- [ ] Orchestrate entity operations

### Interface Adapters Layer
- [ ] Implement interfaces defined by use cases
- [ ] Convert data formats
- [ ] No business logic
- [ ] Controllers, presenters, gateways here
- [ ] Depend on use cases and entities

### Frameworks & Drivers Layer
- [ ] Framework configuration
- [ ] Database schemas
- [ ] External library setup
- [ ] Wiring/dependency injection
- [ ] Very little custom code

### General
- [ ] All dependencies point inward
- [ ] Inner layers define interfaces
- [ ] Outer layers implement interfaces
- [ ] Can test inner layers without outer layers
- [ ] Can swap outer layer implementations

## Further Reading

### Related Guides
- **SOLID_PRINCIPLES.md**: DIP is the class-level equivalent
- **BOUNDARIES_AND_LAYERS.md**: Detailed boundary-crossing techniques
- **BUSINESS_RULES.md**: Structuring entities and use cases
- **TESTABLE_ARCHITECTURE.md**: Testing with clean architecture
- **ARCHITECTURE_PATTERNS.md**: Patterns built on the dependency rule

### Key Concepts
- **Dependency Inversion**: Core technique for crossing boundaries
- **Plugin Architecture**: Outer layers are plugins to inner layers
- **Ports and Adapters**: Alternative name for this architecture
- **Hexagonal Architecture**: Similar architectural pattern

### Books
- **Clean Architecture** by Robert C. Martin (Chapters 17-22)
- **Implementing Domain-Driven Design** by Vaughn Vernon
- **Hexagonal Architecture** by Alistair Cockburn

---

**Remember**: The dependency rule is simple but strict. Source code dependencies must point only inward. This single rule creates independently deployable, testable, and maintainable systems.
