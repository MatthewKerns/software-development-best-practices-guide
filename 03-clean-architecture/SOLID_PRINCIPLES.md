# SOLID Principles: Foundation of Clean Architecture

## Overview

The SOLID principles are five fundamental design principles that make software designs more understandable, flexible, and maintainable. Introduced by Robert C. Martin, these principles form the foundation of clean architecture and object-oriented design.

**"The goal of the principles is the creation of mid-level software structures that: tolerate change, are easy to understand, and are the basis of components that can be used in many software systems."** — Robert C. Martin, Clean Architecture

These principles apply at the class and module level—the mid-level of software architecture. They help developers create systems that remain flexible and maintainable as requirements evolve.

## Why SOLID Matters

### The Cost of Ignoring SOLID

Systems built without SOLID principles exhibit:

**Rigidity**: Changes ripple through the system unpredictably. A simple feature request requires modifying dozens of classes.

**Fragility**: Modifications break seemingly unrelated parts of the system. Fixing one bug creates two more.

**Immobility**: Useful code cannot be extracted and reused. Components are so entangled that separation is impossible.

**Viscosity**: Doing things right is harder than doing them wrong. Developers take shortcuts because proper implementation is too difficult.

**Needless Complexity**: Premature abstractions and unused features clutter the codebase, making it harder to understand.

### The Benefits of SOLID Design

SOLID principles provide:
- **Maintainability**: Changes are localized and predictable
- **Testability**: Components can be tested in isolation
- **Flexibility**: New features integrate smoothly without major refactoring
- **Comprehensibility**: Each component has a clear, single purpose
- **Reusability**: Well-abstracted components work in multiple contexts
- **Reduced Risk**: Changes have minimal unintended consequences

## Source Materials

This guide is based on:

- **Clean Architecture** by Robert C. Martin (Part III: "Design Principles")
  - Chapters 7-11: Detailed explanations of all five SOLID principles
  - Real-world examples and violations
  - Architectural implications of each principle

- **Agile Software Development, Principles, Patterns, and Practices** by Robert C. Martin
  - Original formulation of SOLID principles
  - Deep dive into design smells

## The Five SOLID Principles

### 1. Single Responsibility Principle (SRP)

**Definition**: A module should have one, and only one, reason to change.

**Core Insight**: "Reason to change" means "responsibility to a stakeholder or actor." A class should be responsible to only one actor.

#### Understanding SRP

The SRP is often misunderstood. It's not about "doing one thing"—it's about serving one actor or stakeholder. If different people might request changes to a class for different reasons, the class violates SRP.

**Example of Violation:**

```python
# VIOLATION: This class serves three different actors
class Employee:
    """Manages employee data and business rules."""

    def __init__(self, name: str, role: str, hourly_rate: float):
        self.name = name
        self.role = role
        self.hourly_rate = hourly_rate

    def calculate_pay(self) -> float:
        """Calculate employee pay - used by ACCOUNTING"""
        hours = self.get_hours_worked()
        return hours * self.hourly_rate

    def report_hours(self) -> str:
        """Generate hours report - used by HR"""
        hours = self.get_hours_worked()
        return f"{self.name} worked {hours} hours"

    def save(self) -> None:
        """Persist to database - used by IT/OPERATIONS"""
        database.save(self)

    def get_hours_worked(self) -> float:
        """Shared method used by multiple functions"""
        # Complex logic to calculate hours
        return 40.0  # Simplified
```

**Problem**: Three different departments (Accounting, HR, IT) might request changes:
- Accounting might want to change pay calculation
- HR might want to change reporting format
- IT might want to change database structure

If `get_hours_worked()` changes for Accounting's needs, it might break HR's reporting.

**Corrected Design:**

```python
# Each class serves a single actor

class EmployeeData:
    """Pure data container - used by all actors"""
    def __init__(self, name: str, role: str, hourly_rate: float):
        self.name = name
        self.role = role
        self.hourly_rate = hourly_rate

class PayrollCalculator:
    """Pay calculation - serves ACCOUNTING"""
    def calculate_pay(self, employee: EmployeeData) -> float:
        hours = self._get_accounting_hours(employee)
        return hours * employee.hourly_rate

    def _get_accounting_hours(self, employee: EmployeeData) -> float:
        # Accounting's specific hours calculation
        return 40.0

class HRReporter:
    """Hours reporting - serves HR"""
    def report_hours(self, employee: EmployeeData) -> str:
        hours = self._get_hr_hours(employee)
        return f"{employee.name} worked {hours} hours"

    def _get_hr_hours(self, employee: EmployeeData) -> float:
        # HR's specific hours calculation
        return 40.0

class EmployeeRepository:
    """Data persistence - serves IT/OPERATIONS"""
    def save(self, employee: EmployeeData) -> None:
        database.save(employee)

    def find_by_id(self, employee_id: str) -> EmployeeData:
        return database.find(employee_id)
```

**Benefit**: Changes requested by one department don't affect others. Each class can evolve independently.

#### SRP in TypeScript

```typescript
// VIOLATION: Mixed concerns
class UserAccount {
    constructor(private username: string, private email: string) {}

    // Authentication concern - Security team might request changes
    authenticate(password: string): boolean {
        const hashedPassword = this.hashPassword(password);
        return database.verifyCredentials(this.username, hashedPassword);
    }

    // Email notification concern - Marketing team might request changes
    sendWelcomeEmail(): void {
        const emailBody = this.formatWelcomeEmail();
        emailService.send(this.email, "Welcome!", emailBody);
    }

    // Data validation concern - Data quality team might request changes
    isValidEmail(): boolean {
        return /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(this.email);
    }

    private hashPassword(password: string): string {
        return crypto.createHash('sha256').update(password).digest('hex');
    }

    private formatWelcomeEmail(): string {
        return `Welcome ${this.username}! We're glad you joined.`;
    }
}

// CORRECTED: Separated concerns
interface User {
    username: string;
    email: string;
}

class UserAuthenticator {
    // Serves Security team
    authenticate(user: User, password: string): boolean {
        const hashedPassword = this.hashPassword(password);
        return database.verifyCredentials(user.username, hashedPassword);
    }

    private hashPassword(password: string): string {
        return crypto.createHash('sha256').update(password).digest('hex');
    }
}

class WelcomeEmailSender {
    // Serves Marketing team
    sendWelcomeEmail(user: User): void {
        const emailBody = this.formatWelcomeEmail(user);
        emailService.send(user.email, "Welcome!", emailBody);
    }

    private formatWelcomeEmail(user: User): string {
        return `Welcome ${user.username}! We're glad you joined.`;
    }
}

class EmailValidator {
    // Serves Data quality team
    isValid(email: string): boolean {
        return /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email);
    }
}
```

#### SRP in Java

```java
// VIOLATION: Report generation mixed with business logic
public class SalesReport {
    private List<Sale> sales;

    // Business calculation - serves Finance team
    public BigDecimal calculateTotalRevenue() {
        return sales.stream()
            .map(Sale::getAmount)
            .reduce(BigDecimal.ZERO, BigDecimal::add);
    }

    // HTML formatting - serves Web team
    public String generateHTML() {
        StringBuilder html = new StringBuilder("<html><body>");
        html.append("<h1>Sales Report</h1>");
        html.append("<p>Total Revenue: ").append(calculateTotalRevenue()).append("</p>");
        html.append("<table>");
        for (Sale sale : sales) {
            html.append("<tr><td>").append(sale.getProduct())
                .append("</td><td>").append(sale.getAmount())
                .append("</td></tr>");
        }
        html.append("</table></body></html>");
        return html.toString();
    }

    // PDF formatting - serves Print team
    public byte[] generatePDF() {
        PDFDocument doc = new PDFDocument();
        doc.addTitle("Sales Report");
        doc.addText("Total Revenue: " + calculateTotalRevenue());
        // ... more PDF generation
        return doc.toBytes();
    }
}

// CORRECTED: Separated responsibilities
public class SalesData {
    private final List<Sale> sales;

    public SalesData(List<Sale> sales) {
        this.sales = Collections.unmodifiableList(sales);
    }

    public List<Sale> getSales() {
        return sales;
    }
}

public class RevenueCalculator {
    // Serves Finance team
    public BigDecimal calculateTotal(SalesData data) {
        return data.getSales().stream()
            .map(Sale::getAmount)
            .reduce(BigDecimal.ZERO, BigDecimal::add);
    }
}

public class HTMLReportFormatter {
    // Serves Web team
    private final RevenueCalculator calculator;

    public HTMLReportFormatter(RevenueCalculator calculator) {
        this.calculator = calculator;
    }

    public String format(SalesData data) {
        StringBuilder html = new StringBuilder("<html><body>");
        html.append("<h1>Sales Report</h1>");
        html.append("<p>Total Revenue: ")
            .append(calculator.calculateTotal(data))
            .append("</p>");
        html.append(formatSalesTable(data.getSales()));
        html.append("</body></html>");
        return html.toString();
    }

    private String formatSalesTable(List<Sale> sales) {
        StringBuilder table = new StringBuilder("<table>");
        for (Sale sale : sales) {
            table.append("<tr><td>").append(sale.getProduct())
                 .append("</td><td>").append(sale.getAmount())
                 .append("</td></tr>");
        }
        table.append("</table>");
        return table.toString();
    }
}

public class PDFReportFormatter {
    // Serves Print team
    private final RevenueCalculator calculator;

    public PDFReportFormatter(RevenueCalculator calculator) {
        this.calculator = calculator;
    }

    public byte[] format(SalesData data) {
        PDFDocument doc = new PDFDocument();
        doc.addTitle("Sales Report");
        doc.addText("Total Revenue: " + calculator.calculateTotal(data));
        // ... more PDF generation
        return doc.toBytes();
    }
}
```

### 2. Open-Closed Principle (OCP)

**Definition**: Software entities should be open for extension but closed for modification.

**Core Insight**: Design systems so that new behaviors can be added without changing existing code. Achieve this through abstraction and polymorphism.

#### Understanding OCP

The goal is to make the system easy to extend without incurring high impact. You should be able to add new features by adding new code, not by changing old code that already works.

**Example of Violation:**

```python
# VIOLATION: Adding new shapes requires modifying existing code
class AreaCalculator:
    def calculate_area(self, shapes: list) -> float:
        total_area = 0.0

        for shape in shapes:
            if shape.type == "circle":
                total_area += 3.14159 * shape.radius ** 2
            elif shape.type == "rectangle":
                total_area += shape.width * shape.height
            elif shape.type == "triangle":
                total_area += 0.5 * shape.base * shape.height
            # Adding a new shape requires modifying this method!

        return total_area
```

**Problem**: Every time you add a new shape, you must modify `calculate_area()`. This violates OCP and creates risks:
- Existing, tested code must be changed
- Risk of breaking calculations for existing shapes
- Method grows indefinitely with each new shape type

**Corrected Design:**

```python
# CORRECTED: Open for extension, closed for modification
from abc import ABC, abstractmethod

class Shape(ABC):
    """Abstract base class for all shapes"""

    @abstractmethod
    def area(self) -> float:
        """Calculate the area of this shape"""
        pass

class Circle(Shape):
    def __init__(self, radius: float):
        self.radius = radius

    def area(self) -> float:
        return 3.14159 * self.radius ** 2

class Rectangle(Shape):
    def __init__(self, width: float, height: float):
        self.width = width
        self.height = height

    def area(self) -> float:
        return self.width * self.height

class Triangle(Shape):
    def __init__(self, base: float, height: float):
        self.base = base
        self.height = height

    def area(self) -> float:
        return 0.5 * self.base * self.height

# Adding new shapes is easy - no modification needed
class Pentagon(Shape):
    def __init__(self, side: float):
        self.side = side

    def area(self) -> float:
        return 1.72048 * self.side ** 2

class AreaCalculator:
    """Never needs to change when new shapes are added"""
    def calculate_total_area(self, shapes: list[Shape]) -> float:
        return sum(shape.area() for shape in shapes)
```

**Benefit**: Adding new shapes requires zero changes to `AreaCalculator`. The class is closed for modification but open for extension.

#### OCP in TypeScript

```typescript
// VIOLATION: Payment processing requires modification for new payment methods
class PaymentProcessor {
    processPayment(payment: Payment): void {
        if (payment.method === "credit_card") {
            this.processCreditCard(payment);
        } else if (payment.method === "paypal") {
            this.processPayPal(payment);
        } else if (payment.method === "bitcoin") {
            this.processBitcoin(payment);
        }
        // Adding new payment method requires modifying this method
    }

    private processCreditCard(payment: Payment): void {
        // Credit card processing logic
    }

    private processPayPal(payment: Payment): void {
        // PayPal processing logic
    }

    private processBitcoin(payment: Payment): void {
        // Bitcoin processing logic
    }
}

// CORRECTED: Strategy pattern enables extension without modification
interface PaymentMethod {
    process(amount: number): Promise<PaymentResult>;
}

class CreditCardPayment implements PaymentMethod {
    constructor(
        private cardNumber: string,
        private cvv: string,
        private expiryDate: string
    ) {}

    async process(amount: number): Promise<PaymentResult> {
        // Credit card processing logic
        const gateway = new CreditCardGateway();
        return await gateway.charge(this.cardNumber, amount, this.cvv);
    }
}

class PayPalPayment implements PaymentMethod {
    constructor(private email: string) {}

    async process(amount: number): Promise<PaymentResult> {
        // PayPal processing logic
        const api = new PayPalAPI();
        return await api.createPayment(this.email, amount);
    }
}

class BitcoinPayment implements PaymentMethod {
    constructor(private walletAddress: string) {}

    async process(amount: number): Promise<PaymentResult> {
        // Bitcoin processing logic
        const blockchain = new BitcoinBlockchain();
        return await blockchain.transfer(this.walletAddress, amount);
    }
}

// Adding new payment methods requires NO changes to this class
class PaymentProcessor {
    async processPayment(
        method: PaymentMethod,
        amount: number
    ): Promise<PaymentResult> {
        return await method.process(amount);
    }
}

// New payment method added with zero modifications to existing code
class ApplePayPayment implements PaymentMethod {
    constructor(private token: string) {}

    async process(amount: number): Promise<PaymentResult> {
        const applePay = new ApplePayService();
        return await applePay.authorize(this.token, amount);
    }
}
```

#### OCP in Java

```java
// VIOLATION: Discount calculation requires modification for new discount types
public class DiscountCalculator {
    public BigDecimal calculateDiscount(Order order, String discountType) {
        BigDecimal amount = order.getTotal();

        if (discountType.equals("PERCENTAGE")) {
            return amount.multiply(new BigDecimal("0.10"));
        } else if (discountType.equals("FIXED")) {
            return new BigDecimal("5.00");
        } else if (discountType.equals("BOGO")) {
            // Buy one get one logic
            return amount.divide(new BigDecimal("2"));
        }
        // Adding new discount type requires modifying this method

        return BigDecimal.ZERO;
    }
}

// CORRECTED: Polymorphism enables extension without modification
public interface DiscountStrategy {
    BigDecimal calculateDiscount(Order order);
}

public class PercentageDiscount implements DiscountStrategy {
    private final BigDecimal percentage;

    public PercentageDiscount(BigDecimal percentage) {
        this.percentage = percentage;
    }

    @Override
    public BigDecimal calculateDiscount(Order order) {
        return order.getTotal().multiply(percentage);
    }
}

public class FixedAmountDiscount implements DiscountStrategy {
    private final BigDecimal amount;

    public FixedAmountDiscount(BigDecimal amount) {
        this.amount = amount;
    }

    @Override
    public BigDecimal calculateDiscount(Order order) {
        BigDecimal discount = amount;
        // Don't discount more than order total
        return discount.min(order.getTotal());
    }
}

public class BuyOneGetOneDiscount implements DiscountStrategy {
    @Override
    public BigDecimal calculateDiscount(Order order) {
        // Discount equals price of cheapest item
        return order.getItems().stream()
            .map(Item::getPrice)
            .min(BigDecimal::compareTo)
            .orElse(BigDecimal.ZERO);
    }
}

// Never needs modification when new discount types are added
public class DiscountCalculator {
    public BigDecimal calculateDiscount(Order order, DiscountStrategy strategy) {
        return strategy.calculateDiscount(order);
    }
}

// New discount types added with zero changes to existing code
public class SeasonalDiscount implements DiscountStrategy {
    private final Season season;

    public SeasonalDiscount(Season season) {
        this.season = season;
    }

    @Override
    public BigDecimal calculateDiscount(Order order) {
        BigDecimal rate = switch (season) {
            case WINTER -> new BigDecimal("0.15");
            case SUMMER -> new BigDecimal("0.20");
            default -> new BigDecimal("0.05");
        };
        return order.getTotal().multiply(rate);
    }
}
```

### 3. Liskov Substitution Principle (LSP)

**Definition**: Subtypes must be substitutable for their base types without altering the correctness of the program.

**Core Insight**: If S is a subtype of T, then objects of type T may be replaced with objects of type S without breaking the program. This means derived classes must honor the contracts established by their base classes.

#### Understanding LSP

LSP ensures that inheritance hierarchies are designed correctly. A violation means that code working with a base class will break when given a derived class—a fundamental failure of polymorphism.

**Example of Violation:**

```python
# VIOLATION: Square violates LSP when used as Rectangle
class Rectangle:
    def __init__(self, width: float, height: float):
        self._width = width
        self._height = height

    def set_width(self, width: float) -> None:
        self._width = width

    def set_height(self, height: float) -> None:
        self._height = height

    def area(self) -> float:
        return self._width * self._height

class Square(Rectangle):
    """A square IS-A rectangle, right? WRONG for LSP!"""

    def set_width(self, width: float) -> None:
        # Square must maintain equal sides
        self._width = width
        self._height = width  # VIOLATES LSP!

    def set_height(self, height: float) -> None:
        # Square must maintain equal sides
        self._width = height  # VIOLATES LSP!
        self._height = height

# This function works correctly for Rectangle
def test_rectangle_area(rect: Rectangle) -> None:
    rect.set_width(5)
    rect.set_height(4)
    assert rect.area() == 20, "Expected area of 20"

# But breaks with Square!
rectangle = Rectangle(0, 0)
test_rectangle_area(rectangle)  # Passes

square = Square(0, 0)
test_rectangle_area(square)  # FAILS! Area is 16, not 20
```

**Problem**: `Square` cannot be substituted for `Rectangle` because it violates the behavioral contract. Code expecting independent width/height breaks.

**Corrected Design:**

```python
# CORRECTED: Proper abstraction honors LSP
from abc import ABC, abstractmethod

class Shape(ABC):
    """Abstract base that doesn't make assumptions about dimensions"""

    @abstractmethod
    def area(self) -> float:
        pass

class Rectangle(Shape):
    def __init__(self, width: float, height: float):
        self._width = width
        self._height = height

    def set_width(self, width: float) -> None:
        self._width = width

    def set_height(self, height: float) -> None:
        self._height = height

    def area(self) -> float:
        return self._width * self._height

class Square(Shape):
    """Square is NOT a subtype of Rectangle"""
    def __init__(self, side: float):
        self._side = side

    def set_side(self, side: float) -> None:
        self._side = side

    def area(self) -> float:
        return self._side ** 2

# Now functions work with the appropriate abstraction
def calculate_total_area(shapes: list[Shape]) -> float:
    return sum(shape.area() for shape in shapes)

# Both work correctly
shapes = [Rectangle(5, 4), Square(5)]
print(calculate_total_area(shapes))  # Correct: 45
```

#### LSP in TypeScript

```typescript
// VIOLATION: Bird hierarchy violates LSP
class Bird {
    fly(): void {
        console.log("Flying through the air");
    }
}

class Penguin extends Bird {
    fly(): void {
        // Penguins can't fly! This violates LSP
        throw new Error("Penguins cannot fly");
    }
}

// Code expecting any Bird to fly
function makeBirdFly(bird: Bird): void {
    bird.fly();  // Works for most birds, throws for Penguin!
}

const sparrow = new Bird();
makeBirdFly(sparrow);  // OK

const penguin = new Penguin();
makeBirdFly(penguin);  // THROWS ERROR - LSP violation!

// CORRECTED: Proper abstraction
interface Bird {
    eat(): void;
    makeSound(): void;
}

interface FlyingBird extends Bird {
    fly(): void;
}

class Sparrow implements FlyingBird {
    eat(): void {
        console.log("Eating seeds");
    }

    makeSound(): void {
        console.log("Chirp chirp");
    }

    fly(): void {
        console.log("Flying through the air");
    }
}

class Penguin implements Bird {
    eat(): void {
        console.log("Eating fish");
    }

    makeSound(): void {
        console.log("Squawk");
    }

    swim(): void {
        console.log("Swimming gracefully");
    }
}

// Functions now use appropriate abstraction
function feedBird(bird: Bird): void {
    bird.eat();  // Works for all birds
}

function makeFlyingBirdFly(bird: FlyingBird): void {
    bird.fly();  // Only called with birds that can fly
}

feedBird(new Sparrow());  // OK
feedBird(new Penguin());  // OK

makeFlyingBirdFly(new Sparrow());  // OK
// makeFlyingBirdFly(new Penguin());  // Compile error - prevents LSP violation
```

#### LSP in Java

```java
// VIOLATION: Stack violates LSP when extending ArrayList
public class Stack<T> extends ArrayList<T> {
    public void push(T item) {
        add(item);
    }

    public T pop() {
        if (isEmpty()) {
            throw new EmptyStackException();
        }
        return remove(size() - 1);
    }

    public T peek() {
        if (isEmpty()) {
            throw new EmptyStackException();
        }
        return get(size() - 1);
    }
}

// Code using ArrayList interface
public void processItems(ArrayList<String> items) {
    items.add(0, "First");  // Insert at beginning - valid for ArrayList
    // ... process items
}

// LSP violation
Stack<String> stack = new Stack<>();
processItems(stack);  // Breaks stack semantics - item not at top!

// CORRECTED: Composition over inheritance
public class Stack<T> {
    private final List<T> elements = new ArrayList<>();

    public void push(T item) {
        elements.add(item);
    }

    public T pop() {
        if (isEmpty()) {
            throw new EmptyStackException();
        }
        return elements.remove(elements.size() - 1);
    }

    public T peek() {
        if (isEmpty()) {
            throw new EmptyStackException();
        }
        return elements.get(elements.size() - 1);
    }

    public boolean isEmpty() {
        return elements.isEmpty();
    }

    public int size() {
        return elements.size();
    }
}

// Now Stack cannot be misused as ArrayList - LSP preserved
```

### 4. Interface Segregation Principle (ISP)

**Definition**: No client should be forced to depend on methods it does not use.

**Core Insight**: Large, "fat" interfaces should be split into smaller, more specific interfaces so that clients only need to know about the methods relevant to them.

#### Understanding ISP

ISP prevents interface pollution. When interfaces grow too large, implementing classes are forced to provide empty implementations for methods they don't need. This creates unnecessary coupling and violates LSP.

**Example of Violation:**

```python
# VIOLATION: Fat interface forces unnecessary implementations
from abc import ABC, abstractmethod

class Worker(ABC):
    """Bloated interface with methods not all workers need"""

    @abstractmethod
    def work(self) -> None:
        pass

    @abstractmethod
    def eat(self) -> None:
        pass

    @abstractmethod
    def sleep(self) -> None:
        pass

class HumanWorker(Worker):
    def work(self) -> None:
        print("Human working")

    def eat(self) -> None:
        print("Human eating lunch")

    def sleep(self) -> None:
        print("Human sleeping")

class RobotWorker(Worker):
    def work(self) -> None:
        print("Robot working")

    def eat(self) -> None:
        # Robots don't eat - forced to implement anyway!
        pass  # ISP violation

    def sleep(self) -> None:
        # Robots don't sleep - forced to implement anyway!
        pass  # ISP violation
```

**Problem**: `RobotWorker` is forced to implement methods it doesn't need. This creates confusing interfaces and potential bugs if these methods are accidentally called.

**Corrected Design:**

```python
# CORRECTED: Segregated interfaces
from abc import ABC, abstractmethod

class Workable(ABC):
    @abstractmethod
    def work(self) -> None:
        pass

class Eatable(ABC):
    @abstractmethod
    def eat(self) -> None:
        pass

class Sleepable(ABC):
    @abstractmethod
    def sleep(self) -> None:
        pass

class HumanWorker(Workable, Eatable, Sleepable):
    def work(self) -> None:
        print("Human working")

    def eat(self) -> None:
        print("Human eating lunch")

    def sleep(self) -> None:
        print("Human sleeping")

class RobotWorker(Workable):
    """Only implements what it needs"""
    def work(self) -> None:
        print("Robot working")

# Functions depend only on what they need
def manage_work(worker: Workable) -> None:
    worker.work()

def manage_break(worker: Eatable) -> None:
    worker.eat()

# Both work correctly
human = HumanWorker()
robot = RobotWorker()

manage_work(human)  # OK
manage_work(robot)  # OK

manage_break(human)  # OK
# manage_break(robot)  # Compile error - prevents bugs
```

#### ISP in TypeScript

```typescript
// VIOLATION: Monolithic interface
interface SmartDevice {
    turnOn(): void;
    turnOff(): void;
    connectWifi(ssid: string, password: string): void;
    playMusic(song: string): void;
    adjustTemperature(degrees: number): void;
    lockDoor(): void;
    unlockDoor(): void;
}

// Light bulb forced to implement irrelevant methods
class SmartLight implements SmartDevice {
    turnOn(): void {
        console.log("Light on");
    }

    turnOff(): void {
        console.log("Light off");
    }

    connectWifi(ssid: string, password: string): void {
        console.log("Connected to WiFi");
    }

    // Forced to implement - doesn't make sense for a light
    playMusic(song: string): void {
        throw new Error("Lights don't play music");
    }

    adjustTemperature(degrees: number): void {
        throw new Error("Lights don't control temperature");
    }

    lockDoor(): void {
        throw new Error("Lights don't lock doors");
    }

    unlockDoor(): void {
        throw new Error("Lights don't unlock doors");
    }
}

// CORRECTED: Segregated interfaces
interface Switchable {
    turnOn(): void;
    turnOff(): void;
}

interface WiFiConnectable {
    connectWifi(ssid: string, password: string): void;
    disconnectWifi(): void;
}

interface MusicPlayer {
    playMusic(song: string): void;
    pauseMusic(): void;
    stopMusic(): void;
}

interface Thermostat {
    adjustTemperature(degrees: number): void;
    getCurrentTemperature(): number;
}

interface DoorLock {
    lockDoor(): void;
    unlockDoor(): void;
}

// Each device implements only relevant interfaces
class SmartLight implements Switchable, WiFiConnectable {
    turnOn(): void {
        console.log("Light on");
    }

    turnOff(): void {
        console.log("Light off");
    }

    connectWifi(ssid: string, password: string): void {
        console.log("Light connected to WiFi");
    }

    disconnectWifi(): void {
        console.log("Light disconnected from WiFi");
    }
}

class SmartSpeaker implements Switchable, WiFiConnectable, MusicPlayer {
    turnOn(): void {
        console.log("Speaker on");
    }

    turnOff(): void {
        console.log("Speaker off");
    }

    connectWifi(ssid: string, password: string): void {
        console.log("Speaker connected to WiFi");
    }

    disconnectWifi(): void {
        console.log("Speaker disconnected");
    }

    playMusic(song: string): void {
        console.log(`Playing ${song}`);
    }

    pauseMusic(): void {
        console.log("Music paused");
    }

    stopMusic(): void {
        console.log("Music stopped");
    }
}

class SmartThermostat implements Switchable, WiFiConnectable, Thermostat {
    private currentTemp: number = 20;

    turnOn(): void {
        console.log("Thermostat on");
    }

    turnOff(): void {
        console.log("Thermostat off");
    }

    connectWifi(ssid: string, password: string): void {
        console.log("Thermostat connected to WiFi");
    }

    disconnectWifi(): void {
        console.log("Thermostat disconnected");
    }

    adjustTemperature(degrees: number): void {
        this.currentTemp = degrees;
        console.log(`Temperature set to ${degrees}`);
    }

    getCurrentTemperature(): number {
        return this.currentTemp;
    }
}

// Functions depend only on what they need
function powerControl(device: Switchable): void {
    device.turnOn();
}

function setupWifi(device: WiFiConnectable, ssid: string, password: string): void {
    device.connectWifi(ssid, password);
}

function playAudio(player: MusicPlayer, song: string): void {
    player.playMusic(song);
}
```

#### ISP in Java

```java
// VIOLATION: God interface
public interface Repository {
    void save(Object entity);
    Object findById(String id);
    List<Object> findAll();
    void delete(String id);
    void update(Object entity);
    List<Object> search(String query);
    void backup();
    void restore();
    void migrate();
    void vacuum();
}

// Read-only repository forced to implement write methods
public class ReadOnlyReportRepository implements Repository {
    @Override
    public void save(Object entity) {
        throw new UnsupportedOperationException("Read-only repository");
    }

    @Override
    public Object findById(String id) {
        return database.query("SELECT * FROM reports WHERE id = ?", id);
    }

    @Override
    public List<Object> findAll() {
        return database.query("SELECT * FROM reports");
    }

    @Override
    public void delete(String id) {
        throw new UnsupportedOperationException("Read-only repository");
    }

    @Override
    public void update(Object entity) {
        throw new UnsupportedOperationException("Read-only repository");
    }

    @Override
    public List<Object> search(String query) {
        return database.fullTextSearch(query);
    }

    // Maintenance operations don't make sense for read-only
    @Override
    public void backup() {
        throw new UnsupportedOperationException();
    }

    @Override
    public void restore() {
        throw new UnsupportedOperationException();
    }

    @Override
    public void migrate() {
        throw new UnsupportedOperationException();
    }

    @Override
    public void vacuum() {
        throw new UnsupportedOperationException();
    }
}

// CORRECTED: Segregated repository interfaces
public interface Readable<T> {
    T findById(String id);
    List<T> findAll();
}

public interface Searchable<T> {
    List<T> search(String query);
}

public interface Writable<T> {
    void save(T entity);
    void update(T entity);
    void delete(String id);
}

public interface Maintainable {
    void backup();
    void restore();
    void migrate();
    void vacuum();
}

// Read-only repository implements only what it needs
public class ReadOnlyReportRepository implements Readable<Report>, Searchable<Report> {
    @Override
    public Report findById(String id) {
        return database.query("SELECT * FROM reports WHERE id = ?", id);
    }

    @Override
    public List<Report> findAll() {
        return database.query("SELECT * FROM reports");
    }

    @Override
    public List<Report> search(String query) {
        return database.fullTextSearch(query);
    }
}

// Full CRUD repository
public class UserRepository
    implements Readable<User>, Writable<User>, Searchable<User> {

    @Override
    public User findById(String id) {
        return database.query("SELECT * FROM users WHERE id = ?", id);
    }

    @Override
    public List<User> findAll() {
        return database.query("SELECT * FROM users");
    }

    @Override
    public void save(User entity) {
        database.execute("INSERT INTO users VALUES (?, ?)", entity.getId(), entity.getName());
    }

    @Override
    public void update(User entity) {
        database.execute("UPDATE users SET name = ? WHERE id = ?",
            entity.getName(), entity.getId());
    }

    @Override
    public void delete(String id) {
        database.execute("DELETE FROM users WHERE id = ?", id);
    }

    @Override
    public List<User> search(String query) {
        return database.fullTextSearch(query);
    }
}

// Database maintenance service
public class DatabaseMaintenanceService implements Maintainable {
    @Override
    public void backup() {
        database.createBackup();
    }

    @Override
    public void restore() {
        database.restoreFromBackup();
    }

    @Override
    public void migrate() {
        migrationRunner.run();
    }

    @Override
    public void vacuum() {
        database.vacuum();
    }
}
```

### 5. Dependency Inversion Principle (DIP)

**Definition**: High-level modules should not depend on low-level modules. Both should depend on abstractions. Abstractions should not depend on details. Details should depend on abstractions.

**Core Insight**: The dependency relationship should be inverted from the natural flow. Instead of high-level business logic depending on low-level implementation details, both should depend on abstract interfaces.

#### Understanding DIP

DIP is the foundational principle of clean architecture. It enables testability, flexibility, and the ability to defer implementation decisions. By depending on abstractions, you can swap implementations without changing client code.

**Example of Violation:**

```python
# VIOLATION: High-level business logic depends on low-level implementation
class MySQLDatabase:
    """Low-level database implementation"""
    def connect(self) -> None:
        print("Connecting to MySQL")

    def execute_query(self, query: str) -> list:
        print(f"Executing MySQL query: {query}")
        return []

class UserService:
    """High-level business logic - DEPENDS ON CONCRETE DATABASE"""
    def __init__(self):
        self.database = MySQLDatabase()  # Direct dependency!

    def get_user(self, user_id: str) -> dict:
        self.database.connect()
        results = self.database.execute_query(
            f"SELECT * FROM users WHERE id = '{user_id}'"
        )
        return results[0] if results else {}
```

**Problems:**
- Cannot test `UserService` without MySQL
- Cannot switch to PostgreSQL without modifying `UserService`
- High-level business logic is coupled to low-level database details

**Corrected Design:**

```python
# CORRECTED: Both depend on abstraction
from abc import ABC, abstractmethod

class DatabaseInterface(ABC):
    """Abstraction that both high and low-level modules depend on"""

    @abstractmethod
    def connect(self) -> None:
        pass

    @abstractmethod
    def execute_query(self, query: str) -> list:
        pass

# Low-level module depends on abstraction
class MySQLDatabase(DatabaseInterface):
    def connect(self) -> None:
        print("Connecting to MySQL")

    def execute_query(self, query: str) -> list:
        print(f"Executing MySQL query: {query}")
        return []

# Alternative low-level implementation
class PostgreSQLDatabase(DatabaseInterface):
    def connect(self) -> None:
        print("Connecting to PostgreSQL")

    def execute_query(self, query: str) -> list:
        print(f"Executing PostgreSQL query: {query}")
        return []

# High-level module depends on abstraction
class UserService:
    def __init__(self, database: DatabaseInterface):
        self.database = database  # Depends on interface, not concrete class

    def get_user(self, user_id: str) -> dict:
        self.database.connect()
        results = self.database.execute_query(
            f"SELECT * FROM users WHERE id = '{user_id}'"
        )
        return results[0] if results else {}

# Easy to test with mock
class MockDatabase(DatabaseInterface):
    def connect(self) -> None:
        pass

    def execute_query(self, query: str) -> list:
        return [{"id": "123", "name": "Test User"}]

# Usage: dependency injection
mysql_db = MySQLDatabase()
user_service = UserService(mysql_db)

# Easy to switch implementations
postgres_db = PostgreSQLDatabase()
user_service = UserService(postgres_db)

# Easy to test
mock_db = MockDatabase()
test_service = UserService(mock_db)
```

#### DIP in TypeScript

```typescript
// VIOLATION: Email service depends on concrete SMTP implementation
class SMTPMailer {
    send(to: string, subject: string, body: string): void {
        console.log("Sending via SMTP");
        // SMTP-specific implementation
    }
}

class NotificationService {
    private mailer = new SMTPMailer();  // Direct dependency!

    notifyUser(email: string, message: string): void {
        this.mailer.send(email, "Notification", message);
    }
}

// CORRECTED: Both depend on abstraction
interface EmailSender {
    send(to: string, subject: string, body: string): Promise<void>;
}

// Low-level implementations
class SMTPMailer implements EmailSender {
    async send(to: string, subject: string, body: string): Promise<void> {
        console.log("Sending via SMTP");
        // SMTP-specific implementation
    }
}

class SendGridMailer implements EmailSender {
    constructor(private apiKey: string) {}

    async send(to: string, subject: string, body: string): Promise<void> {
        console.log("Sending via SendGrid");
        // SendGrid API implementation
    }
}

class MailgunMailer implements EmailSender {
    constructor(private domain: string, private apiKey: string) {}

    async send(to: string, subject: string, body: string): Promise<void> {
        console.log("Sending via Mailgun");
        // Mailgun API implementation
    }
}

// High-level business logic depends on abstraction
class NotificationService {
    constructor(private emailSender: EmailSender) {}

    async notifyUser(email: string, message: string): Promise<void> {
        await this.emailSender.send(email, "Notification", message);
    }
}

// Dependency injection - easy to configure and swap
const smtpMailer = new SMTPMailer();
const notificationService1 = new NotificationService(smtpMailer);

const sendGridMailer = new SendGridMailer("api-key");
const notificationService2 = new NotificationService(sendGridMailer);

// Easy to test with mock
class MockEmailSender implements EmailSender {
    public sentEmails: Array<{to: string, subject: string, body: string}> = [];

    async send(to: string, subject: string, body: string): Promise<void> {
        this.sentEmails.push({to, subject, body});
    }
}

const mockSender = new MockEmailSender();
const testService = new NotificationService(mockSender);
await testService.notifyUser("test@example.com", "Test message");
console.assert(mockSender.sentEmails.length === 1);
```

#### DIP in Java

```java
// VIOLATION: Payment processor depends on concrete payment gateway
public class StripePaymentGateway {
    public PaymentResult charge(BigDecimal amount, String cardToken) {
        System.out.println("Charging via Stripe");
        // Stripe-specific implementation
        return new PaymentResult(true, "txn_123");
    }
}

public class OrderProcessor {
    private final StripePaymentGateway gateway = new StripePaymentGateway();

    public void processOrder(Order order) {
        BigDecimal total = order.getTotal();
        PaymentResult result = gateway.charge(total, order.getPaymentToken());

        if (result.isSuccess()) {
            order.markAsPaid();
        }
    }
}

// CORRECTED: Dependency inversion with abstraction
public interface PaymentGateway {
    PaymentResult charge(BigDecimal amount, String paymentToken);
    PaymentResult refund(String transactionId, BigDecimal amount);
}

// Low-level implementations depend on interface
public class StripePaymentGateway implements PaymentGateway {
    private final String apiKey;

    public StripePaymentGateway(String apiKey) {
        this.apiKey = apiKey;
    }

    @Override
    public PaymentResult charge(BigDecimal amount, String paymentToken) {
        System.out.println("Charging via Stripe");
        // Stripe-specific implementation
        return new PaymentResult(true, "stripe_txn_123");
    }

    @Override
    public PaymentResult refund(String transactionId, BigDecimal amount) {
        System.out.println("Refunding via Stripe");
        return new PaymentResult(true, "stripe_refund_123");
    }
}

public class PayPalPaymentGateway implements PaymentGateway {
    private final String clientId;
    private final String secret;

    public PayPalPaymentGateway(String clientId, String secret) {
        this.clientId = clientId;
        this.secret = secret;
    }

    @Override
    public PaymentResult charge(BigDecimal amount, String paymentToken) {
        System.out.println("Charging via PayPal");
        // PayPal-specific implementation
        return new PaymentResult(true, "paypal_txn_456");
    }

    @Override
    public PaymentResult refund(String transactionId, BigDecimal amount) {
        System.out.println("Refunding via PayPal");
        return new PaymentResult(true, "paypal_refund_456");
    }
}

// High-level business logic depends on abstraction
public class OrderProcessor {
    private final PaymentGateway gateway;

    public OrderProcessor(PaymentGateway gateway) {
        this.gateway = gateway;  // Injected dependency
    }

    public void processOrder(Order order) {
        BigDecimal total = order.getTotal();
        PaymentResult result = gateway.charge(total, order.getPaymentToken());

        if (result.isSuccess()) {
            order.markAsPaid();
            order.setTransactionId(result.getTransactionId());
        } else {
            order.markAsFailed();
        }
    }

    public void refundOrder(Order order) {
        if (order.getTransactionId() == null) {
            throw new IllegalStateException("Cannot refund unpaid order");
        }

        PaymentResult result = gateway.refund(
            order.getTransactionId(),
            order.getTotal()
        );

        if (result.isSuccess()) {
            order.markAsRefunded();
        }
    }
}

// Dependency injection configuration
public class ApplicationConfig {
    public OrderProcessor createOrderProcessor(String environment) {
        PaymentGateway gateway;

        if (environment.equals("production")) {
            gateway = new StripePaymentGateway(System.getenv("STRIPE_API_KEY"));
        } else {
            gateway = new MockPaymentGateway();  // For testing
        }

        return new OrderProcessor(gateway);
    }
}

// Easy to test
public class MockPaymentGateway implements PaymentGateway {
    private boolean shouldSucceed = true;

    public void setShouldSucceed(boolean shouldSucceed) {
        this.shouldSucceed = shouldSucceed;
    }

    @Override
    public PaymentResult charge(BigDecimal amount, String paymentToken) {
        return new PaymentResult(shouldSucceed, "mock_txn_789");
    }

    @Override
    public PaymentResult refund(String transactionId, BigDecimal amount) {
        return new PaymentResult(shouldSucceed, "mock_refund_789");
    }
}
```

## How SOLID Principles Work Together

The five SOLID principles are not independent—they reinforce each other to create maintainable, flexible systems.

### Principle Interactions

**SRP + OCP**: When classes have single responsibilities, they're easier to extend without modification.

```python
# SRP ensures focused classes
class ReportGenerator:
    def generate(self, data: ReportData) -> Report:
        return Report(data)

class PDFFormatter:
    def format(self, report: Report) -> bytes:
        return self._convert_to_pdf(report)

# OCP makes extension easy
class ExcelFormatter:  # New formatter - no modifications needed
    def format(self, report: Report) -> bytes:
        return self._convert_to_excel(report)
```

**LSP + DIP**: Proper substitution requires depending on abstractions, not concrete classes.

```typescript
// DIP: Depend on abstraction
interface Logger {
    log(message: string): void;
}

// LSP: All implementations must be substitutable
class FileLogger implements Logger {
    log(message: string): void {
        fs.appendFileSync('app.log', message + '\n');
    }
}

class ConsoleLogger implements Logger {
    log(message: string): void {
        console.log(message);
    }
}

// Works with any Logger implementation
class Application {
    constructor(private logger: Logger) {}

    run(): void {
        this.logger.log("Application started");  // LSP ensures this works
    }
}
```

**ISP + SRP**: Segregated interfaces naturally arise from single responsibilities.

```java
// SRP: Each interface has one responsibility
public interface Readable {
    String read();
}

public interface Writable {
    void write(String data);
}

// ISP: Classes implement only what they need
public class FileManager implements Readable, Writable {
    @Override
    public String read() {
        return fileSystem.readFile();
    }

    @Override
    public void write(String data) {
        fileSystem.writeFile(data);
    }
}

public class ConfigReader implements Readable {
    // Only implements reading - doesn't need write
    @Override
    public String read() {
        return config.load();
    }
}
```

### Complete Example: Order Processing System

Here's how all five principles work together in a realistic system:

```python
from abc import ABC, abstractmethod
from typing import List
from decimal import Decimal

# DIP: Abstract interfaces that both high and low-level modules depend on
class PaymentProcessor(ABC):
    @abstractmethod
    def process_payment(self, amount: Decimal, token: str) -> bool:
        pass

class NotificationSender(ABC):
    @abstractmethod
    def send_notification(self, recipient: str, message: str) -> None:
        pass

class OrderRepository(ABC):
    @abstractmethod
    def save(self, order: 'Order') -> None:
        pass

# SRP: Single responsibility - domain entity
class Order:
    def __init__(self, order_id: str, items: List['OrderItem'], customer_email: str):
        self.order_id = order_id
        self.items = items
        self.customer_email = customer_email
        self.status = "pending"

    def total(self) -> Decimal:
        return sum(item.price * item.quantity for item in self.items)

    def mark_as_paid(self) -> None:
        self.status = "paid"

# SRP: Single responsibility - order item
class OrderItem:
    def __init__(self, product_name: str, price: Decimal, quantity: int):
        self.product_name = product_name
        self.price = price
        self.quantity = quantity

# SRP: Single responsibility - process orders
class OrderService:
    def __init__(
        self,
        payment_processor: PaymentProcessor,
        notification_sender: NotificationSender,
        order_repository: OrderRepository
    ):
        self.payment_processor = payment_processor
        self.notification_sender = notification_sender
        self.order_repository = order_repository

    def place_order(self, order: Order, payment_token: str) -> bool:
        # High-level business logic - doesn't know implementation details
        payment_successful = self.payment_processor.process_payment(
            order.total(),
            payment_token
        )

        if payment_successful:
            order.mark_as_paid()
            self.order_repository.save(order)
            self.notification_sender.send_notification(
                order.customer_email,
                f"Order {order.order_id} confirmed"
            )
            return True

        return False

# OCP: Can add new payment processors without modifying OrderService
class StripePaymentProcessor(PaymentProcessor):
    def process_payment(self, amount: Decimal, token: str) -> bool:
        print(f"Processing ${amount} via Stripe")
        return True

class PayPalPaymentProcessor(PaymentProcessor):
    def process_payment(self, amount: Decimal, token: str) -> bool:
        print(f"Processing ${amount} via PayPal")
        return True

# OCP: Can add new notification methods
class EmailNotificationSender(NotificationSender):
    def send_notification(self, recipient: str, message: str) -> None:
        print(f"Sending email to {recipient}: {message}")

class SMSNotificationSender(NotificationSender):
    def send_notification(self, recipient: str, message: str) -> None:
        print(f"Sending SMS to {recipient}: {message}")

# LSP: All implementations are substitutable
class InMemoryOrderRepository(OrderRepository):
    def __init__(self):
        self.orders = {}

    def save(self, order: Order) -> None:
        self.orders[order.order_id] = order

class DatabaseOrderRepository(OrderRepository):
    def save(self, order: Order) -> None:
        # Real database save
        print(f"Saving order {order.order_id} to database")

# ISP: Segregated test interface - only provides what tests need
class TestPaymentProcessor(PaymentProcessor):
    def __init__(self, should_succeed: bool = True):
        self.should_succeed = should_succeed
        self.processed_payments = []

    def process_payment(self, amount: Decimal, token: str) -> bool:
        self.processed_payments.append((amount, token))
        return self.should_succeed

# Usage demonstrates all principles working together
def main():
    # Easy to configure different implementations (DIP)
    payment_processor = StripePaymentProcessor()
    notification_sender = EmailNotificationSender()
    repository = InMemoryOrderRepository()

    order_service = OrderService(
        payment_processor,
        notification_sender,
        repository
    )

    # Create and process order
    items = [
        OrderItem("Widget", Decimal("19.99"), 2),
        OrderItem("Gadget", Decimal("29.99"), 1)
    ]
    order = Order("ORD-001", items, "customer@example.com")

    success = order_service.place_order(order, "payment_token_123")
    print(f"Order processed: {success}")

    # Easy to swap implementations (OCP, LSP, DIP)
    order_service.payment_processor = PayPalPaymentProcessor()
    order_service.notification_sender = SMSNotificationSender()

    # Easy to test (all principles)
    test_processor = TestPaymentProcessor()
    test_service = OrderService(
        test_processor,
        EmailNotificationSender(),
        InMemoryOrderRepository()
    )
```

## Integration with Geist Framework

The SOLID principles align with the three-dimensional Geist analysis:

### Ghost (Unknown Unknowns) + SOLID

**SRP helps reveal hidden assumptions**: When a class has multiple responsibilities, it often hides assumptions about how those responsibilities relate. Splitting them exposes these assumptions.

**Example:**
```python
# Hidden assumption: authentication and logging are coupled
class UserManager:
    def login(self, username: str, password: str) -> bool:
        if self.authenticate(username, password):
            self.log_login(username)  # Assumption: always log after auth
            return True
        return False

# SRP reveals the assumption as an explicit dependency
class Authenticator:
    def authenticate(self, username: str, password: str) -> bool:
        return validate_credentials(username, password)

class LoginService:
    def __init__(self, authenticator: Authenticator, logger: LoginLogger):
        self.authenticator = authenticator
        self.logger = logger

    def login(self, username: str, password: str) -> bool:
        if self.authenticator.authenticate(username, password):
            self.logger.log_login(username)  # Explicit, testable dependency
            return True
        return False
```

**ISP reveals hidden client needs**: When interfaces are too large, it's unclear what clients actually need. Segregation reveals true dependencies.

### Geyser (Dynamic Forces) + SOLID

**OCP prepares for inevitable change**: Systems evolve under pressure. OCP ensures you can extend without breaking existing code.

**DIP enables swapping implementations**: As external forces change (new vendors, technologies), DIP lets you adapt without major refactoring.

**Example:**
```typescript
// Geyser: Payment providers change frequently
interface PaymentGateway {
    charge(amount: number): Promise<boolean>;
}

class OrderProcessor {
    constructor(private gateway: PaymentGateway) {}  // DIP

    async process(order: Order): Promise<void> {
        await this.gateway.charge(order.total);
        // Business logic unchanged when gateway changes
    }
}

// New provider? No problem (OCP + DIP)
class NewProviderGateway implements PaymentGateway {
    async charge(amount: number): Promise<boolean> {
        // New implementation
        return true;
    }
}
```

### Gist (Essential Core) + SOLID

**SRP identifies what's essential**: Each responsibility represents a core concept. If a class has multiple responsibilities, it's mixing essential and accidental complexity.

**LSP preserves essential contracts**: Substitutability means preserving the essential behavior that clients depend on.

**Example:**
```java
// Gist: Essential behavior is "send message"
public interface MessageSender {
    void send(String recipient, String message);
}

// LSP: All implementations preserve essential contract
public class EmailSender implements MessageSender {
    public void send(String recipient, String message) {
        // Email details are accidental - essential behavior preserved
        emailAPI.send(recipient, message);
    }
}

public class SMSSender implements MessageSender {
    public void send(String recipient, String message) {
        // SMS details are accidental - essential behavior preserved
        smsAPI.send(recipient, message);
    }
}
```

## Common Violations and How to Fix Them

### Violation 1: God Class (SRP)

**Problem**: One class does everything.

```python
# BAD
class Application:
    def __init__(self):
        self.users = []
        self.orders = []

    def register_user(self, username, password): ...
    def login_user(self, username, password): ...
    def create_order(self, user_id, items): ...
    def process_payment(self, order_id, payment_info): ...
    def send_confirmation_email(self, email, order_id): ...
    def generate_invoice(self, order_id): ...
    def log_activity(self, message): ...
```

**Fix**: Extract responsibilities into focused classes.

```python
# GOOD
class UserRepository:
    def save(self, user): ...
    def find_by_username(self, username): ...

class AuthenticationService:
    def register(self, username, password): ...
    def login(self, username, password): ...

class OrderService:
    def create_order(self, user_id, items): ...

class PaymentProcessor:
    def process(self, order_id, payment_info): ...

class EmailService:
    def send_confirmation(self, email, order_id): ...

class InvoiceGenerator:
    def generate(self, order_id): ...

class Logger:
    def log(self, message): ...
```

### Violation 2: Type Switching (OCP)

**Problem**: Adding new types requires modifying existing code.

```typescript
// BAD
function calculateShipping(order: Order): number {
    if (order.shippingMethod === "standard") {
        return 5.99;
    } else if (order.shippingMethod === "express") {
        return 12.99;
    } else if (order.shippingMethod === "overnight") {
        return 24.99;
    }
    // Adding new method requires modifying this function
}

// GOOD
interface ShippingMethod {
    calculateCost(order: Order): number;
}

class StandardShipping implements ShippingMethod {
    calculateCost(order: Order): number {
        return 5.99;
    }
}

class ExpressShipping implements ShippingMethod {
    calculateCost(order: Order): number {
        return 12.99;
    }
}

class OvernightShipping implements ShippingMethod {
    calculateCost(order: Order): number {
        return 24.99;
    }
}

function calculateShipping(order: Order, method: ShippingMethod): number {
    return method.calculateCost(order);  // Never needs modification
}
```

### Violation 3: Refused Bequest (LSP)

**Problem**: Subclass doesn't support base class operations.

```java
// BAD
public class Bird {
    public void fly() {
        System.out.println("Flying");
    }
}

public class Penguin extends Bird {
    @Override
    public void fly() {
        throw new UnsupportedOperationException("Penguins can't fly");
    }
}

// GOOD
public interface Bird {
    void eat();
}

public interface FlyingBird extends Bird {
    void fly();
}

public class Sparrow implements FlyingBird {
    public void eat() { ... }
    public void fly() { ... }
}

public class Penguin implements Bird {
    public void eat() { ... }
    public void swim() { ... }  // Penguin-specific behavior
}
```

### Violation 4: Fat Interface (ISP)

**Problem**: Interface has methods most clients don't need.

```python
# BAD
class IWorker(ABC):
    @abstractmethod
    def work(self): pass

    @abstractmethod
    def eat(self): pass

    @abstractmethod
    def sleep(self): pass

    @abstractmethod
    def get_paid(self): pass

# Robot workers must implement irrelevant methods
class Robot(IWorker):
    def work(self): ...
    def eat(self): pass  # Unused
    def sleep(self): pass  # Unused
    def get_paid(self): pass  # Unused

# GOOD
class IWorkable(ABC):
    @abstractmethod
    def work(self): pass

class IFeedable(ABC):
    @abstractmethod
    def eat(self): pass

class IPayable(ABC):
    @abstractmethod
    def get_paid(self): pass

class Robot(IWorkable):
    def work(self): ...

class Human(IWorkable, IFeedable, IPayable):
    def work(self): ...
    def eat(self): ...
    def get_paid(self): ...
```

### Violation 5: Concrete Dependencies (DIP)

**Problem**: High-level code depends on low-level implementation details.

```typescript
// BAD
class MySQLDatabase {
    connect(): void { ... }
    query(sql: string): any[] { ... }
}

class UserService {
    private db = new MySQLDatabase();  // Concrete dependency

    getUser(id: string): User {
        this.db.connect();
        return this.db.query(`SELECT * FROM users WHERE id = ${id}`)[0];
    }
}

// GOOD
interface Database {
    connect(): void;
    query(sql: string): any[];
}

class MySQLDatabase implements Database {
    connect(): void { ... }
    query(sql: string): any[] { ... }
}

class UserService {
    constructor(private db: Database) {}  // Abstract dependency

    getUser(id: string): User {
        this.db.connect();
        return this.db.query(`SELECT * FROM users WHERE id = ${id}`)[0];
    }
}
```

## Practical Checklist

### Single Responsibility Principle
- [ ] Each class serves only one actor/stakeholder
- [ ] Class has only one reason to change
- [ ] Class name clearly describes its single responsibility
- [ ] Methods all relate to the same high-level responsibility
- [ ] No mixed concerns (business logic + persistence + presentation)

### Open-Closed Principle
- [ ] New features add code, not modify existing code
- [ ] Use abstraction and polymorphism for extension points
- [ ] Type checking (instanceof, typeof) is minimal or absent
- [ ] Strategy, Template Method, or other patterns enable extension
- [ ] Protected variation: identify and encapsulate variation points

### Liskov Substitution Principle
- [ ] Derived classes can replace base classes without breaking code
- [ ] Preconditions not strengthened in derived classes
- [ ] Postconditions not weakened in derived classes
- [ ] Invariants preserved in derived classes
- [ ] No throwing unexpected exceptions in derived classes
- [ ] Base class contracts fully honored by all derived classes

### Interface Segregation Principle
- [ ] Interfaces are small and focused
- [ ] No "fat" interfaces with many unrelated methods
- [ ] Clients depend only on methods they actually use
- [ ] No empty or throwing implementations of interface methods
- [ ] Related methods grouped into cohesive interfaces

### Dependency Inversion Principle
- [ ] High-level modules don't import low-level modules directly
- [ ] Both depend on abstractions (interfaces, abstract classes)
- [ ] Abstractions don't depend on implementation details
- [ ] Dependency injection used for wiring
- [ ] Easy to test with mocks/stubs
- [ ] Easy to swap implementations

## Common Pitfalls

**Premature Abstraction**: Don't add abstractions before you need them. Wait until you have two concrete examples before abstracting.

**Over-Engineering**: SOLID doesn't mean every class needs an interface. Use principles where they add value.

**Cargo Cult Programming**: Don't apply SOLID blindly. Understand the "why" behind each principle.

**Ignoring Context**: SOLID applies at the module/class level, not every line of code. Don't over-fragment your code.

**Analysis Paralysis**: Don't spend hours deciding if a class has one responsibility. Start coding, refactor when violations become painful.

## Further Reading

### Related Guides
- **COMPONENT_PRINCIPLES.md**: Higher-level application of SOLID at component boundaries
- **DEPENDENCY_RULE.md**: How DIP enables clean architecture
- **ARCHITECTURE_PATTERNS.md**: Architectural patterns built on SOLID
- **TESTABLE_ARCHITECTURE.md**: How SOLID enables comprehensive testing
- **../02-design-in-code/CLASS_DESIGN.md**: Detailed class-level design practices
- **../05-refactoring-and-improvement/CODE_SMELLS.md**: Identifying SOLID violations

### Key Concepts
- **Abstraction**: The foundation of OCP, LSP, and DIP
- **Polymorphism**: Enables OCP and LSP
- **Dependency Injection**: Practical implementation of DIP
- **Composition over Inheritance**: Helps achieve SRP and LSP
- **Interface-Based Design**: Central to ISP and DIP

### Books
- **Clean Architecture** by Robert C. Martin (Part III)
- **Agile Software Development, Principles, Patterns, and Practices** by Robert C. Martin
- **Design Patterns: Elements of Reusable Object-Oriented Software** by Gang of Four

---

**Remember**: SOLID principles are guidelines, not laws. Use them to create maintainable, flexible systems—but always prioritize simplicity and pragmatism over dogmatic adherence.
