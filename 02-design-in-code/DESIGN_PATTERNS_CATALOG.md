# Design Patterns Catalog: Solutions to Recurring Design Problems

## Overview

Design patterns are reusable solutions to common software design problems. They represent best practices evolved over time by experienced developers and provide a shared vocabulary for discussing design solutions. Understanding design patterns enables you to recognize recurring problems and apply proven solutions that enhance maintainability, flexibility, and comprehensibility.

**"Each pattern describes a problem which occurs over and over again in our environment, and then describes the core of the solution to that problem, in such a way that you can use this solution a million times over, without ever doing it the same way twice."** — Christopher Alexander, A Pattern Language

Design patterns are not finished designs that can be directly transformed into code. They are templates for how to solve a problem in various situations. Patterns show relationships and interactions between classes or objects without specifying the final application classes or objects involved.

## Why Design Patterns Matter

### The Cost of Ignorance

Systems built without knowledge of design patterns suffer:

**Reinventing the Wheel**: Developers create solutions from scratch for problems that have proven solutions, wasting time and introducing bugs.

**Poor Communication**: Without a shared vocabulary, design discussions become lengthy explanations instead of concise pattern references.

**Fragile Designs**: Ad-hoc solutions are often brittle and resist change because they lack the flexibility of tested patterns.

**Hard to Understand**: Code using unfamiliar patterns or reinvented solutions is harder for new team members to comprehend.

### The Benefits of Pattern Knowledge

Design patterns provide:
- **Proven Solutions**: Patterns are battle-tested solutions that have evolved over decades
- **Shared Vocabulary**: "We need a Factory here" communicates design intent clearly
- **Design Reusability**: Apply pattern knowledge across different projects and domains
- **Flexibility**: Patterns build changeability into designs from the start
- **Comprehension**: Recognizable patterns make code easier to understand
- **Best Practice Transfer**: Patterns capture expert knowledge for all developers

## Source Materials

This guide synthesizes patterns from:

- **Design Patterns: Elements of Reusable Object-Oriented Software** by Gang of Four (Gamma, Helm, Johnson, Vlissides)
  - Original catalog of 23 classic design patterns
  - Intent, motivation, applicability, structure, and consequences
  - The definitive reference for object-oriented design patterns

- **Head First Design Patterns** by Freeman, Robson, Bates, and Sierra
  - Accessible explanations with visual learning
  - Real-world scenarios and examples
  - Emphasis on pattern relationships and principles

- **Code Complete 2** by Steve McConnell (Chapter 5: Design in Construction)
  - Patterns in the context of construction-level design
  - Integration with broader design heuristics

## How to Use This Guide

### For Learning Patterns

1. **Start with Intent**: Understand what problem each pattern solves
2. **Study Structure**: Learn the key participants and their relationships
3. **See Examples**: Study code in multiple languages to grasp implementation
4. **Recognize When to Use**: Practice identifying situations where patterns apply
5. **Practice Implementation**: Apply patterns in small projects before production

### For Reference

Use this guide as a catalog:
- Look up patterns by problem type (creational, structural, behavioral)
- Reference implementation examples in your language
- Check "When to Use" and "When NOT to Use" sections
- Cross-reference related patterns

### For Code Reviews

- Identify opportunities to apply patterns
- Suggest appropriate patterns for design problems
- Check for pattern misuse or over-engineering
- Verify pattern implementations follow proper structure

## Pattern Categories Overview

The Gang of Four organized patterns into three categories based on their purpose:

### Creational Patterns (5 patterns)

**Purpose**: Deal with object creation mechanisms, trying to create objects in a manner suitable to the situation.

**Key Insight**: Abstract the instantiation process to make systems independent of how objects are created, composed, and represented.

**Patterns**:
1. **Singleton** - Ensure a class has only one instance and provide global access
2. **Factory Method** - Define interface for creating objects, let subclasses decide which class to instantiate
3. **Abstract Factory** - Provide interface for creating families of related objects
4. **Builder** - Separate construction of complex object from its representation
5. **Prototype** - Specify kinds of objects to create using prototypical instance

### Structural Patterns (7 patterns)

**Purpose**: Deal with object composition, creating relationships between entities.

**Key Insight**: Compose classes and objects to form larger structures while keeping structures flexible and efficient.

**Patterns**:
1. **Adapter** - Convert interface of a class into another interface clients expect
2. **Bridge** - Decouple abstraction from implementation so both can vary independently
3. **Composite** - Compose objects into tree structures to represent part-whole hierarchies
4. **Decorator** - Attach additional responsibilities to objects dynamically
5. **Facade** - Provide unified interface to a set of interfaces in a subsystem
6. **Flyweight** - Use sharing to support large numbers of fine-grained objects efficiently
7. **Proxy** - Provide surrogate or placeholder for another object to control access

### Behavioral Patterns (11 patterns)

**Purpose**: Deal with communication between objects, how they interact and distribute responsibility.

**Key Insight**: Characterize complex control flow that's difficult to follow at runtime, focusing on communication patterns.

**Patterns**:
1. **Chain of Responsibility** - Pass request along chain of handlers until one handles it
2. **Command** - Encapsulate request as object to parameterize clients with different requests
3. **Iterator** - Provide way to access elements of aggregate sequentially without exposing representation
4. **Mediator** - Define object that encapsulates how set of objects interact
5. **Memento** - Capture and externalize object's internal state without violating encapsulation
6. **Observer** - Define one-to-many dependency so when one object changes state, dependents are notified
7. **State** - Allow object to alter behavior when internal state changes
8. **Strategy** - Define family of algorithms, encapsulate each one, make them interchangeable
9. **Template Method** - Define skeleton of algorithm, defer some steps to subclasses
10. **Visitor** - Represent operation to be performed on elements of object structure
11. **Interpreter** - Given language, define representation for grammar along with interpreter

---

# Creational Patterns

Creational patterns abstract the instantiation process. They help make a system independent of how its objects are created, composed, and represented.

## 1. Singleton Pattern

### Intent

Ensure a class has only one instance and provide a global point of access to it.

### Problem

Sometimes you need exactly one instance of a class to coordinate actions across a system. For example:
- **Configuration Manager**: One source of truth for application settings
- **Database Connection Pool**: Single pool managing connections
- **Logger**: Centralized logging facility
- **Hardware Interface Manager**: Single controller for hardware access

Creating multiple instances would be wasteful or cause conflicts. But how do you ensure only one instance exists while still allowing convenient access?

### Solution

Make the class responsible for keeping track of its sole instance. The class can ensure that no other instance can be created (by intercepting requests to create new objects) and can provide a way to access the instance.

### Structure

**Key Participants**:
- **Singleton**: Defines Instance() operation that lets clients access unique instance; responsible for creating and maintaining its own unique instance

### Implementation

#### Python Implementation

```python
# Thread-safe Singleton with lazy initialization

from threading import Lock
from typing import Optional

class Singleton:
    """Singleton class ensuring only one instance exists."""

    _instance: Optional['Singleton'] = None
    _lock: Lock = Lock()

    def __new__(cls):
        if cls._instance is None:
            with cls._lock:
                # Double-check locking pattern
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        # Only initialize once
        if not hasattr(self, 'initialized'):
            self.initialized = True
            # Initialization code here
            self.value = 0

    def some_business_logic(self):
        """Example business logic."""
        return f"Singleton instance value: {self.value}"

# Practical Example: Configuration Manager
class ConfigurationManager:
    """Singleton configuration manager."""

    _instance: Optional['ConfigurationManager'] = None
    _lock: Lock = Lock()

    def __new__(cls):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        if not hasattr(self, 'initialized'):
            self.initialized = True
            self._config: dict = {}
            self._load_configuration()

    def _load_configuration(self):
        """Load configuration from file/environment."""
        self._config = {
            'database_url': 'postgres://localhost/mydb',
            'api_key': 'secret-key',
            'max_connections': 100
        }

    def get(self, key: str, default=None):
        """Get configuration value."""
        return self._config.get(key, default)

    def set(self, key: str, value):
        """Set configuration value."""
        self._config[key] = value

# Usage
config1 = ConfigurationManager()
config2 = ConfigurationManager()

assert config1 is config2  # Same instance

config1.set('api_timeout', 30)
print(config2.get('api_timeout'))  # Output: 30 (same instance)
```

#### TypeScript Implementation

```typescript
// Thread-safe Singleton with lazy initialization

class Singleton {
    private static instance: Singleton;
    private static lock: boolean = false;

    private constructor() {
        // Private constructor prevents instantiation
        this.value = 0;
    }

    public static getInstance(): Singleton {
        if (!Singleton.instance) {
            // Simulate locking for thread safety
            if (!Singleton.lock) {
                Singleton.lock = true;

                if (!Singleton.instance) {
                    Singleton.instance = new Singleton();
                }

                Singleton.lock = false;
            }
        }

        return Singleton.instance;
    }

    private value: number;

    public someBusinessLogic(): string {
        return `Singleton instance value: ${this.value}`;
    }

    public setValue(value: number): void {
        this.value = value;
    }
}

// Practical Example: Logger
class Logger {
    private static instance: Logger;
    private logLevel: string = "INFO";

    private constructor() {
        // Private constructor
    }

    public static getInstance(): Logger {
        if (!Logger.instance) {
            Logger.instance = new Logger();
        }
        return Logger.instance;
    }

    public setLogLevel(level: string): void {
        this.logLevel = level;
    }

    public log(message: string, level: string = "INFO"): void {
        const timestamp = new Date().toISOString();
        console.log(`[${timestamp}] [${level}] ${message}`);
    }

    public info(message: string): void {
        this.log(message, "INFO");
    }

    public error(message: string): void {
        this.log(message, "ERROR");
    }

    public warn(message: string): void {
        this.log(message, "WARN");
    }
}

// Usage
const logger1 = Logger.getInstance();
const logger2 = Logger.getInstance();

console.log(logger1 === logger2);  // true - same instance

logger1.info("Application started");
logger2.error("An error occurred");  // Uses same logger instance
```

#### Java Implementation

```java
// Thread-safe Singleton with double-check locking

public class Singleton {
    // Volatile ensures visibility across threads
    private static volatile Singleton instance;
    private int value;

    // Private constructor prevents instantiation
    private Singleton() {
        this.value = 0;
    }

    // Double-check locking for thread-safe lazy initialization
    public static Singleton getInstance() {
        if (instance == null) {
            synchronized (Singleton.class) {
                if (instance == null) {
                    instance = new Singleton();
                }
            }
        }
        return instance;
    }

    public String someBusinessLogic() {
        return "Singleton instance value: " + value;
    }

    public void setValue(int value) {
        this.value = value;
    }
}

// Practical Example: Database Connection Pool
public class DatabaseConnectionPool {
    private static volatile DatabaseConnectionPool instance;
    private final int maxConnections;
    private int activeConnections;

    private DatabaseConnectionPool() {
        this.maxConnections = 100;
        this.activeConnections = 0;
    }

    public static DatabaseConnectionPool getInstance() {
        if (instance == null) {
            synchronized (DatabaseConnectionPool.class) {
                if (instance == null) {
                    instance = new DatabaseConnectionPool();
                }
            }
        }
        return instance;
    }

    public synchronized Connection getConnection() {
        if (activeConnections < maxConnections) {
            activeConnections++;
            return new Connection();
        }
        throw new RuntimeException("No available connections");
    }

    public synchronized void releaseConnection(Connection conn) {
        activeConnections--;
        // Return connection to pool
    }

    public int getActiveConnections() {
        return activeConnections;
    }
}

// Enum Singleton (preferred in Java - thread-safe by default)
public enum ConfigurationManager {
    INSTANCE;

    private Map<String, String> config = new HashMap<>();

    ConfigurationManager() {
        loadConfiguration();
    }

    private void loadConfiguration() {
        config.put("database_url", "postgres://localhost/mydb");
        config.put("api_key", "secret-key");
    }

    public String get(String key) {
        return config.get(key);
    }

    public void set(String key, String value) {
        config.put(key, value);
    }
}

// Usage
DatabaseConnectionPool pool1 = DatabaseConnectionPool.getInstance();
DatabaseConnectionPool pool2 = DatabaseConnectionPool.getInstance();

System.out.println(pool1 == pool2);  // true - same instance

// Enum usage
ConfigurationManager config = ConfigurationManager.INSTANCE;
String dbUrl = config.get("database_url");
```

### When to Use

Use Singleton when:
- There must be exactly one instance of a class
- Instance must be accessible from well-known access point
- Sole instance should be extensible by subclassing
- You need strict control over global variables

**Common Use Cases**:
- Configuration managers
- Logging facilities
- Thread pools
- Cache managers
- Device drivers
- Database connection pools

### When NOT to Use

Avoid Singleton when:
- You need multiple instances (obviously)
- Testing requires isolation (Singletons make testing difficult)
- You might need different instances in different contexts
- State management becomes too complex
- Dependency injection would be clearer

**Problems with Singleton**:
- **Global State**: Can lead to hidden dependencies
- **Testing Difficulty**: Hard to mock or replace
- **Concurrency Issues**: Requires careful thread-safety
- **Tight Coupling**: Clients depend on concrete Singleton class

### Real-World Examples

**Application Configuration**:
```python
# Single source of truth for app settings
config = ConfigurationManager()
db_url = config.get('database_url')
api_key = config.get('api_key')
```

**Centralized Logging**:
```typescript
// All components use same logger
const logger = Logger.getInstance();
logger.info("User logged in");
logger.error("Database connection failed");
```

**Connection Pooling**:
```java
// Single pool manages all database connections
DatabaseConnectionPool pool = DatabaseConnectionPool.getInstance();
Connection conn = pool.getConnection();
// Use connection
pool.releaseConnection(conn);
```

### Related Patterns

- **Abstract Factory**: Often implemented as Singleton
- **Builder**: Often implemented as Singleton
- **Prototype**: Often implemented as Singleton

---

## 2. Factory Method Pattern

### Intent

Define an interface for creating an object, but let subclasses decide which class to instantiate. Factory Method lets a class defer instantiation to subclasses.

### Problem

A framework needs to standardize the architectural model for a range of applications, but allow for individual applications to define their own domain objects and provide for their instantiation.

How do you create objects when the exact type isn't known until runtime? How do you allow subclasses to specify which objects to create?

### Solution

Define a method for creating objects (the factory method) in a base class. Subclasses override this method to create specific types of objects.

### Structure

**Key Participants**:
- **Creator**: Declares factory method that returns Product objects
- **ConcreteCreator**: Overrides factory method to return ConcreteProduct instance
- **Product**: Defines interface of objects factory method creates
- **ConcreteProduct**: Implements Product interface

### Implementation

#### Python Implementation

```python
# Factory Method Pattern

from abc import ABC, abstractmethod

# Product Interface
class Document(ABC):
    """Abstract document interface."""

    @abstractmethod
    def open(self) -> str:
        pass

    @abstractmethod
    def save(self) -> str:
        pass

# Concrete Products
class PDFDocument(Document):
    """PDF document implementation."""

    def open(self) -> str:
        return "Opening PDF document"

    def save(self) -> str:
        return "Saving PDF document"

class WordDocument(Document):
    """Word document implementation."""

    def open(self) -> str:
        return "Opening Word document"

    def save(self) -> str:
        return "Saving Word document"

class ExcelDocument(Document):
    """Excel document implementation."""

    def open(self) -> str:
        return "Opening Excel spreadsheet"

    def save(self) -> str:
        return "Saving Excel spreadsheet"

# Creator
class Application(ABC):
    """Application base class with factory method."""

    @abstractmethod
    def create_document(self) -> Document:
        """Factory method - subclasses implement."""
        pass

    def new_document(self) -> str:
        """Template method using factory method."""
        # Use factory method to create document
        document = self.create_document()
        result = document.open()
        return result

# Concrete Creators
class PDFApplication(Application):
    """PDF application."""

    def create_document(self) -> Document:
        return PDFDocument()

class WordApplication(Application):
    """Word processing application."""

    def create_document(self) -> Document:
        return WordDocument()

class ExcelApplication(Application):
    """Spreadsheet application."""

    def create_document(self) -> Document:
        return ExcelDocument()

# Usage
def client_code(app: Application):
    """Client code works with any Application subclass."""
    result = app.new_document()
    print(result)

# Create different applications
pdf_app = PDFApplication()
word_app = WordApplication()
excel_app = ExcelApplication()

client_code(pdf_app)    # Output: Opening PDF document
client_code(word_app)   # Output: Opening Word document
client_code(excel_app)  # Output: Opening Excel spreadsheet
```

#### TypeScript Implementation

```typescript
// Factory Method Pattern

// Product Interface
interface Transport {
    deliver(): string;
    getType(): string;
}

// Concrete Products
class Truck implements Transport {
    deliver(): string {
        return "Delivering by land in a truck";
    }

    getType(): string {
        return "Truck";
    }
}

class Ship implements Transport {
    deliver(): string {
        return "Delivering by sea in a ship";
    }

    getType(): string {
        return "Ship";
    }
}

class Airplane implements Transport {
    deliver(): string {
        return "Delivering by air in an airplane";
    }

    getType(): string {
        return "Airplane";
    }
}

// Creator
abstract class Logistics {
    // Factory Method - subclasses override
    abstract createTransport(): Transport;

    // Template method using factory method
    planDelivery(): string {
        const transport = this.createTransport();
        return `Logistics: Planning delivery using ${transport.getType()}\n` +
               `Transport: ${transport.deliver()}`;
    }
}

// Concrete Creators
class RoadLogistics extends Logistics {
    createTransport(): Transport {
        return new Truck();
    }
}

class SeaLogistics extends Logistics {
    createTransport(): Transport {
        return new Ship();
    }
}

class AirLogistics extends Logistics {
    createTransport(): Transport {
        return new Airplane();
    }
}

// Client code
function clientCode(logistics: Logistics): void {
    console.log(logistics.planDelivery());
}

// Usage
const roadLogistics = new RoadLogistics();
const seaLogistics = new SeaLogistics();
const airLogistics = new AirLogistics();

clientCode(roadLogistics);
// Output: Logistics: Planning delivery using Truck
//         Transport: Delivering by land in a truck

clientCode(seaLogistics);
// Output: Logistics: Planning delivery using Ship
//         Transport: Delivering by sea in a ship

clientCode(airLogistics);
// Output: Logistics: Planning delivery using Airplane
//         Transport: Delivering by air in an airplane
```

#### Java Implementation

```java
// Factory Method Pattern

// Product Interface
public interface Button {
    void render();
    void onClick();
}

// Concrete Products
public class WindowsButton implements Button {
    @Override
    public void render() {
        System.out.println("Rendering Windows button");
    }

    @Override
    public void onClick() {
        System.out.println("Windows button clicked");
    }
}

public class MacButton implements Button {
    @Override
    public void render() {
        System.out.println("Rendering Mac button");
    }

    @Override
    public void onClick() {
        System.out.println("Mac button clicked");
    }
}

public class LinuxButton implements Button {
    @Override
    public void render() {
        System.out.println("Rendering Linux button");
    }

    @Override
    public void onClick() {
        System.out.println("Linux button clicked");
    }
}

// Creator
public abstract class Dialog {
    // Factory Method
    public abstract Button createButton();

    // Template method using factory method
    public void renderDialog() {
        Button button = createButton();
        button.render();
        // Additional dialog rendering logic
    }
}

// Concrete Creators
public class WindowsDialog extends Dialog {
    @Override
    public Button createButton() {
        return new WindowsButton();
    }
}

public class MacDialog extends Dialog {
    @Override
    public Button createButton() {
        return new MacButton();
    }
}

public class LinuxDialog extends Dialog {
    @Override
    public Button createButton() {
        return new LinuxButton();
    }
}

// Client code
public class Application {
    private Dialog dialog;

    public void initialize(String os) {
        if (os.equals("Windows")) {
            dialog = new WindowsDialog();
        } else if (os.equals("Mac")) {
            dialog = new MacDialog();
        } else if (os.equals("Linux")) {
            dialog = new LinuxDialog();
        } else {
            throw new IllegalArgumentException("Unknown OS: " + os);
        }
    }

    public void run() {
        dialog.renderDialog();
    }

    public static void main(String[] args) {
        Application app = new Application();

        // Configure for specific OS
        String os = System.getProperty("os.name").contains("Windows") ? "Windows" : "Mac";
        app.initialize(os);
        app.run();
    }
}
```

### When to Use

Use Factory Method when:
- Class can't anticipate the class of objects it must create
- Class wants subclasses to specify objects it creates
- Classes delegate responsibility to one of several helper subclasses
- You need to localize knowledge of which subclass to create

**Common Use Cases**:
- Creating UI components for different platforms
- Database connections for different database types
- Document readers for different file formats
- Protocol handlers for different network protocols

### When NOT to Use

Avoid Factory Method when:
- Creating objects is simple and doesn't vary
- You don't need subclass variations
- Simple instantiation with `new` suffices
- Dependency injection would be clearer

### Real-World Examples

**Cross-Platform UI**:
```typescript
// Same code creates appropriate UI for each platform
const dialog = createDialogForPlatform();
dialog.renderDialog();  // Renders platform-specific UI
```

**Database Connections**:
```python
# Factory method creates appropriate connection
class DatabaseConnector:
    def create_connection(self):  # Factory method
        pass

class MySQLConnector(DatabaseConnector):
    def create_connection(self):
        return MySQLConnection()

class PostgreSQLConnector(DatabaseConnector):
    def create_connection(self):
        return PostgreSQLConnection()
```

### Related Patterns

- **Abstract Factory**: Often implemented using Factory Methods
- **Template Method**: Factory Method is often called by Template Methods
- **Prototype**: Doesn't require subclassing but needs Initialize operation

---

## 3. Abstract Factory Pattern

### Intent

Provide an interface for creating families of related or dependent objects without specifying their concrete classes.

### Problem

How do you create families of related objects without hard-coding specific classes? For example, a UI toolkit needs to create buttons, checkboxes, and text fields that all match the same look-and-feel (Windows, Mac, Linux).

### Solution

Declare interfaces for creating each type of product. Concrete factory classes implement these interfaces to create concrete products. Clients work with factories and products through abstract interfaces.

### Structure

**Key Participants**:
- **AbstractFactory**: Declares interfaces for creating abstract products
- **ConcreteFactory**: Implements operations to create concrete products
- **AbstractProduct**: Declares interface for a type of product
- **ConcreteProduct**: Defines product to be created by corresponding concrete factory
- **Client**: Uses only interfaces declared by AbstractFactory and AbstractProduct

### Implementation

#### Python Implementation

```python
# Abstract Factory Pattern

from abc import ABC, abstractmethod

# Abstract Products
class Button(ABC):
    @abstractmethod
    def paint(self) -> str:
        pass

class Checkbox(ABC):
    @abstractmethod
    def paint(self) -> str:
        pass

class TextField(ABC):
    @abstractmethod
    def paint(self) -> str:
        pass

# Concrete Products - Windows Family
class WindowsButton(Button):
    def paint(self) -> str:
        return "Rendering Windows button"

class WindowsCheckbox(Checkbox):
    def paint(self) -> str:
        return "Rendering Windows checkbox"

class WindowsTextField(TextField):
    def paint(self) -> str:
        return "Rendering Windows text field"

# Concrete Products - Mac Family
class MacButton(Button):
    def paint(self) -> str:
        return "Rendering Mac button"

class MacCheckbox(Checkbox):
    def paint(self) -> str:
        return "Rendering Mac checkbox"

class MacTextField(TextField):
    def paint(self) -> str:
        return "Rendering Mac text field"

# Concrete Products - Linux Family
class LinuxButton(Button):
    def paint(self) -> str:
        return "Rendering Linux button"

class LinuxCheckbox(Checkbox):
    def paint(self) -> str:
        return "Rendering Linux checkbox"

class LinuxTextField(TextField):
    def paint(self) -> str:
        return "Rendering Linux text field"

# Abstract Factory
class GUIFactory(ABC):
    @abstractmethod
    def create_button(self) -> Button:
        pass

    @abstractmethod
    def create_checkbox(self) -> Checkbox:
        pass

    @abstractmethod
    def create_text_field(self) -> TextField:
        pass

# Concrete Factories
class WindowsFactory(GUIFactory):
    def create_button(self) -> Button:
        return WindowsButton()

    def create_checkbox(self) -> Checkbox:
        return WindowsCheckbox()

    def create_text_field(self) -> TextField:
        return WindowsTextField()

class MacFactory(GUIFactory):
    def create_button(self) -> Button:
        return MacButton()

    def create_checkbox(self) -> Checkbox:
        return MacCheckbox()

    def create_text_field(self) -> TextField:
        return MacTextField()

class LinuxFactory(GUIFactory):
    def create_button(self) -> Button:
        return LinuxButton()

    def create_checkbox(self) -> Checkbox:
        return LinuxCheckbox()

    def create_text_field(self) -> TextField:
        return LinuxTextField()

# Client code
class Application:
    def __init__(self, factory: GUIFactory):
        self.factory = factory

    def create_ui(self) -> str:
        """Create UI using factory - doesn't know concrete types."""
        button = self.factory.create_button()
        checkbox = self.factory.create_checkbox()
        text_field = self.factory.create_text_field()

        return (f"{button.paint()}\n"
                f"{checkbox.paint()}\n"
                f"{text_field.paint()}")

# Usage
def main():
    import sys

    # Determine factory based on OS
    if sys.platform == "win32":
        factory = WindowsFactory()
    elif sys.platform == "darwin":
        factory = MacFactory()
    else:
        factory = LinuxFactory()

    app = Application(factory)
    print(app.create_ui())

# All components from same family
windows_app = Application(WindowsFactory())
print(windows_app.create_ui())
# Output:
# Rendering Windows button
# Rendering Windows checkbox
# Rendering Windows text field
```

#### TypeScript Implementation

```typescript
// Abstract Factory Pattern

// Abstract Products
interface Chair {
    sit(): string;
    hasLegs(): boolean;
}

interface Sofa {
    lieOn(): string;
    hasArmrests(): boolean;
}

interface CoffeeTable {
    placeItems(): string;
    getShape(): string;
}

// Concrete Products - Modern Family
class ModernChair implements Chair {
    sit(): string {
        return "Sitting on modern chair";
    }

    hasLegs(): boolean {
        return false;  // Modern chair - suspended design
    }
}

class ModernSofa implements Sofa {
    lieOn(): string {
        return "Lying on modern sofa";
    }

    hasArmrests(): boolean {
        return false;  // Minimalist design
    }
}

class ModernCoffeeTable implements CoffeeTable {
    placeItems(): string {
        return "Placing items on modern coffee table";
    }

    getShape(): string {
        return "rectangular";
    }
}

// Concrete Products - Victorian Family
class VictorianChair implements Chair {
    sit(): string {
        return "Sitting on Victorian chair";
    }

    hasLegs(): boolean {
        return true;  // Classic four legs
    }
}

class VictorianSofa implements Sofa {
    lieOn(): string {
        return "Lying on Victorian sofa";
    }

    hasArmrests(): boolean {
        return true;  // Ornate armrests
    }
}

class VictorianCoffeeTable implements CoffeeTable {
    placeItems(): string {
        return "Placing items on Victorian coffee table";
    }

    getShape(): string {
        return "oval";
    }
}

// Abstract Factory
interface FurnitureFactory {
    createChair(): Chair;
    createSofa(): Sofa;
    createCoffeeTable(): CoffeeTable;
}

// Concrete Factories
class ModernFurnitureFactory implements FurnitureFactory {
    createChair(): Chair {
        return new ModernChair();
    }

    createSofa(): Sofa {
        return new ModernSofa();
    }

    createCoffeeTable(): CoffeeTable {
        return new ModernCoffeeTable();
    }
}

class VictorianFurnitureFactory implements FurnitureFactory {
    createChair(): Chair {
        return new VictorianChair();
    }

    createSofa(): Sofa {
        return new VictorianSofa();
    }

    createCoffeeTable(): CoffeeTable {
        return new VictorianCoffeeTable();
    }
}

// Client code
class LivingRoom {
    private chair: Chair;
    private sofa: Sofa;
    private table: CoffeeTable;

    constructor(factory: FurnitureFactory) {
        this.chair = factory.createChair();
        this.sofa = factory.createSofa();
        this.table = factory.createCoffeeTable();
    }

    describe(): string {
        return `Living Room:\n` +
               `${this.chair.sit()}\n` +
               `${this.sofa.lieOn()}\n` +
               `${this.table.placeItems()}\n` +
               `Table shape: ${this.table.getShape()}`;
    }
}

// Usage
const modernFactory = new ModernFurnitureFactory();
const modernRoom = new LivingRoom(modernFactory);
console.log(modernRoom.describe());
// Output: All modern furniture working together

const victorianFactory = new VictorianFurnitureFactory();
const victorianRoom = new LivingRoom(victorianFactory);
console.log(victorianRoom.describe());
// Output: All Victorian furniture working together
```

#### Java Implementation

```java
// Abstract Factory Pattern

// Abstract Products
public interface Database {
    void connect();
    void disconnect();
}

public interface Query {
    void execute(String sql);
}

public interface Transaction {
    void begin();
    void commit();
    void rollback();
}

// Concrete Products - MySQL Family
public class MySQLDatabase implements Database {
    @Override
    public void connect() {
        System.out.println("Connecting to MySQL database");
    }

    @Override
    public void disconnect() {
        System.out.println("Disconnecting from MySQL database");
    }
}

public class MySQLQuery implements Query {
    @Override
    public void execute(String sql) {
        System.out.println("Executing MySQL query: " + sql);
    }
}

public class MySQLTransaction implements Transaction {
    @Override
    public void begin() {
        System.out.println("Beginning MySQL transaction");
    }

    @Override
    public void commit() {
        System.out.println("Committing MySQL transaction");
    }

    @Override
    public void rollback() {
        System.out.println("Rolling back MySQL transaction");
    }
}

// Concrete Products - PostgreSQL Family
public class PostgreSQLDatabase implements Database {
    @Override
    public void connect() {
        System.out.println("Connecting to PostgreSQL database");
    }

    @Override
    public void disconnect() {
        System.out.println("Disconnecting from PostgreSQL database");
    }
}

public class PostgreSQLQuery implements Query {
    @Override
    public void execute(String sql) {
        System.out.println("Executing PostgreSQL query: " + sql);
    }
}

public class PostgreSQLTransaction implements Transaction {
    @Override
    public void begin() {
        System.out.println("Beginning PostgreSQL transaction");
    }

    @Override
    public void commit() {
        System.out.println("Committing PostgreSQL transaction");
    }

    @Override
    public void rollback() {
        System.out.println("Rolling back PostgreSQL transaction");
    }
}

// Abstract Factory
public interface DatabaseFactory {
    Database createDatabase();
    Query createQuery();
    Transaction createTransaction();
}

// Concrete Factories
public class MySQLFactory implements DatabaseFactory {
    @Override
    public Database createDatabase() {
        return new MySQLDatabase();
    }

    @Override
    public Query createQuery() {
        return new MySQLQuery();
    }

    @Override
    public Transaction createTransaction() {
        return new MySQLTransaction();
    }
}

public class PostgreSQLFactory implements DatabaseFactory {
    @Override
    public Database createDatabase() {
        return new PostgreSQLDatabase();
    }

    @Override
    public Query createQuery() {
        return new PostgreSQLQuery();
    }

    @Override
    public Transaction createTransaction() {
        return new PostgreSQLTransaction();
    }
}

// Client code
public class DataAccessLayer {
    private Database database;
    private Query query;
    private Transaction transaction;

    public DataAccessLayer(DatabaseFactory factory) {
        this.database = factory.createDatabase();
        this.query = factory.createQuery();
        this.transaction = factory.createTransaction();
    }

    public void executeInTransaction(String sql) {
        database.connect();
        transaction.begin();

        try {
            query.execute(sql);
            transaction.commit();
        } catch (Exception e) {
            transaction.rollback();
            throw e;
        } finally {
            database.disconnect();
        }
    }
}

// Usage
public class Application {
    public static void main(String[] args) {
        // Configure for specific database
        DatabaseFactory factory;
        String dbType = System.getenv("DB_TYPE");

        if ("mysql".equals(dbType)) {
            factory = new MySQLFactory();
        } else {
            factory = new PostgreSQLFactory();
        }

        DataAccessLayer dal = new DataAccessLayer(factory);
        dal.executeInTransaction("INSERT INTO users VALUES (1, 'John')");

        // All components from same database family work together
    }
}
```

### When to Use

Use Abstract Factory when:
- System should be independent of how products are created
- System should be configured with one of multiple families of products
- Family of related products is designed to be used together
- You want to enforce this constraint (use together, not mix)
- You want to reveal only interfaces, not implementations

**Common Use Cases**:
- Cross-platform UI toolkits (Windows, Mac, Linux components)
- Database access layers (MySQL, PostgreSQL, Oracle components)
- Theme systems (Light, Dark, High Contrast components)
- Document formats (PDF, Word, Excel components)

### When NOT to Use

Avoid Abstract Factory when:
- Product families don't need to be used together consistently
- You only have one product family
- Adding new products is more common than adding new families
- Simple Factory or Factory Method would suffice

### Real-World Examples

**UI Theming**:
```python
# All UI components match selected theme
theme_factory = DarkThemeFactory()
app = Application(theme_factory)
# All UI elements use dark theme consistently
```

**Database Abstraction**:
```typescript
// Switch databases without changing business logic
const factory = new PostgreSQLFactory();
const dal = new DataAccessLayer(factory);
// All database operations use PostgreSQL components
```

### Related Patterns

- **Factory Method**: Abstract Factory often implemented using Factory Methods
- **Singleton**: Concrete factories are often Singletons
- **Prototype**: Concrete factories can use Prototype for creating products

## 4. Builder Pattern

### Intent

Separate the construction of a complex object from its representation so that the same construction process can create different representations.

### Problem

How do you construct complex objects with many optional parameters or configurations? Constructor telescoping (multiple constructors with different parameter combinations) becomes unwieldy and error-prone.

Consider constructing a complex object like:
- **HTTP Request**: URL, headers, body, method, timeout, retries
- **SQL Query**: SELECT, FROM, WHERE, JOIN, ORDER BY, LIMIT
- **Document**: Title, author, sections, formatting, metadata
- **House**: Foundation, walls, roof, windows, doors, interior

### Solution

Extract object construction code into separate builder objects. The builder provides methods to set each part of the object. A director class can orchestrate the building process for common configurations.

### Structure

**Key Participants**:
- **Builder**: Specifies abstract interface for creating product parts
- **ConcreteBuilder**: Constructs and assembles product parts; defines and keeps track of representation
- **Director**: Constructs object using Builder interface
- **Product**: Complex object under construction

### Implementation

#### Python Implementation

```python
# Builder Pattern

from typing import Optional
from dataclasses import dataclass, field

# Product
@dataclass
class House:
    """Complex object being built."""
    foundation: str = ""
    walls: str = ""
    roof: str = ""
    windows: int = 0
    doors: int = 0
    garage: bool = False
    swimming_pool: bool = False
    garden: bool = False

    def __str__(self) -> str:
        features = [
            f"Foundation: {self.foundation}",
            f"Walls: {self.walls}",
            f"Roof: {self.roof}",
            f"Windows: {self.windows}",
            f"Doors: {self.doors}"
        ]
        if self.garage:
            features.append("Garage: Yes")
        if self.swimming_pool:
            features.append("Swimming Pool: Yes")
        if self.garden:
            features.append("Garden: Yes")
        return "\n".join(features)

# Builder Interface
class HouseBuilder:
    """Abstract builder interface."""

    def __init__(self):
        self.reset()

    def reset(self) -> None:
        """Reset builder to build new house."""
        self._house = House()

    def build_foundation(self) -> 'HouseBuilder':
        """Build foundation."""
        pass

    def build_walls(self) -> 'HouseBuilder':
        """Build walls."""
        pass

    def build_roof(self) -> 'HouseBuilder':
        """Build roof."""
        pass

    def build_windows(self) -> 'HouseBuilder':
        """Build windows."""
        pass

    def build_doors(self) -> 'HouseBuilder':
        """Build doors."""
        pass

    def build_garage(self) -> 'HouseBuilder':
        """Build garage."""
        pass

    def build_swimming_pool(self) -> 'HouseBuilder':
        """Build swimming pool."""
        pass

    def build_garden(self) -> 'HouseBuilder':
        """Build garden."""
        pass

    def get_result(self) -> House:
        """Return finished house."""
        house = self._house
        self.reset()  # Reset for next build
        return house

# Concrete Builders
class ModernHouseBuilder(HouseBuilder):
    """Builder for modern houses."""

    def build_foundation(self) -> 'HouseBuilder':
        self._house.foundation = "Concrete slab"
        return self

    def build_walls(self) -> 'HouseBuilder':
        self._house.walls = "Glass and steel"
        return self

    def build_roof(self) -> 'HouseBuilder':
        self._house.roof = "Flat roof with solar panels"
        return self

    def build_windows(self) -> 'HouseBuilder':
        self._house.windows = 20  # Many windows
        return self

    def build_doors(self) -> 'HouseBuilder':
        self._house.doors = 4
        return self

    def build_garage(self) -> 'HouseBuilder':
        self._house.garage = True
        return self

    def build_swimming_pool(self) -> 'HouseBuilder':
        self._house.swimming_pool = True
        return self

    def build_garden(self) -> 'HouseBuilder':
        self._house.garden = True
        return self

class TraditionalHouseBuilder(HouseBuilder):
    """Builder for traditional houses."""

    def build_foundation(self) -> 'HouseBuilder':
        self._house.foundation = "Brick foundation"
        return self

    def build_walls(self) -> 'HouseBuilder':
        self._house.walls = "Brick and wood"
        return self

    def build_roof(self) -> 'HouseBuilder':
        self._house.roof = "Pitched roof with tiles"
        return self

    def build_windows(self) -> 'HouseBuilder':
        self._house.windows = 8
        return self

    def build_doors(self) -> 'HouseBuilder':
        self._house.doors = 2
        return self

    def build_garage(self) -> 'HouseBuilder':
        self._house.garage = False
        return self

    def build_swimming_pool(self) -> 'HouseBuilder':
        self._house.swimming_pool = False
        return self

    def build_garden(self) -> 'HouseBuilder':
        self._house.garden = True
        return self

# Director
class HouseDirector:
    """Orchestrates building process."""

    def __init__(self, builder: HouseBuilder):
        self.builder = builder

    def construct_minimal_house(self) -> House:
        """Build minimal viable house."""
        return (self.builder
                .build_foundation()
                .build_walls()
                .build_roof()
                .build_windows()
                .build_doors()
                .get_result())

    def construct_full_featured_house(self) -> House:
        """Build house with all features."""
        return (self.builder
                .build_foundation()
                .build_walls()
                .build_roof()
                .build_windows()
                .build_doors()
                .build_garage()
                .build_swimming_pool()
                .build_garden()
                .get_result())

# Usage
# Without director - custom construction
builder = ModernHouseBuilder()
custom_house = (builder
                .build_foundation()
                .build_walls()
                .build_roof()
                .build_windows()
                .build_doors()
                .build_garage()
                # Skip pool and garden
                .get_result())

print("Custom Modern House:")
print(custom_house)

# With director - standard configurations
director = HouseDirector(TraditionalHouseBuilder())
traditional_house = director.construct_full_featured_house()

print("\nTraditional Full Featured House:")
print(traditional_house)

# Practical Example: HTTP Request Builder
@dataclass
class HTTPRequest:
    """HTTP request product."""
    url: str = ""
    method: str = "GET"
    headers: dict = field(default_factory=dict)
    body: Optional[str] = None
    timeout: int = 30
    retries: int = 0

class HTTPRequestBuilder:
    """Builder for HTTP requests."""

    def __init__(self):
        self._request = HTTPRequest()

    def with_url(self, url: str) -> 'HTTPRequestBuilder':
        self._request.url = url
        return self

    def with_method(self, method: str) -> 'HTTPRequestBuilder':
        self._request.method = method
        return self

    def with_header(self, key: str, value: str) -> 'HTTPRequestBuilder':
        self._request.headers[key] = value
        return self

    def with_body(self, body: str) -> 'HTTPRequestBuilder':
        self._request.body = body
        return self

    def with_timeout(self, timeout: int) -> 'HTTPRequestBuilder':
        self._request.timeout = timeout
        return self

    def with_retries(self, retries: int) -> 'HTTPRequestBuilder':
        self._request.retries = retries
        return self

    def build(self) -> HTTPRequest:
        """Return finished request."""
        request = self._request
        self._request = HTTPRequest()  # Reset
        return request

# Usage
request = (HTTPRequestBuilder()
           .with_url("https://api.example.com/users")
           .with_method("POST")
           .with_header("Content-Type", "application/json")
           .with_header("Authorization", "Bearer token123")
           .with_body('{"name": "John Doe"}')
           .with_timeout(60)
           .with_retries(3)
           .build())
```

#### TypeScript Implementation

```typescript
// Builder Pattern

// Product
class Car {
    public seats: number = 2;
    public engine: string = "Basic";
    public tripComputer: boolean = false;
    public gps: boolean = false;
    public sunroof: boolean = false;

    public getDescription(): string {
        const features = [
            `Seats: ${this.seats}`,
            `Engine: ${this.engine}`
        ];

        if (this.tripComputer) features.push("Trip Computer: Yes");
        if (this.gps) features.push("GPS: Yes");
        if (this.sunroof) features.push("Sunroof: Yes");

        return features.join("\n");
    }
}

// Builder Interface
interface CarBuilder {
    reset(): void;
    setSeats(seats: number): this;
    setEngine(engine: string): this;
    setTripComputer(): this;
    setGPS(): this;
    setSunroof(): this;
    getResult(): Car;
}

// Concrete Builder
class SportsCarBuilder implements CarBuilder {
    private car: Car;

    constructor() {
        this.car = new Car();
    }

    reset(): void {
        this.car = new Car();
    }

    setSeats(seats: number): this {
        this.car.seats = seats;
        return this;
    }

    setEngine(engine: string): this {
        this.car.engine = engine;
        return this;
    }

    setTripComputer(): this {
        this.car.tripComputer = true;
        return this;
    }

    setGPS(): this {
        this.car.gps = true;
        return this;
    }

    setSunroof(): this {
        this.car.sunroof = true;
        return this;
    }

    getResult(): Car {
        const result = this.car;
        this.reset();
        return result;
    }
}

// Director
class CarDirector {
    private builder: CarBuilder;

    constructor(builder: CarBuilder) {
        this.builder = builder;
    }

    constructSportsCar(): Car {
        return this.builder
            .setSeats(2)
            .setEngine("V8 Turbo")
            .setTripComputer()
            .setGPS()
            .setSunroof()
            .getResult();
    }

    constructFamilyCar(): Car {
        return this.builder
            .setSeats(5)
            .setEngine("V6")
            .setTripComputer()
            .setGPS()
            .getResult();
    }
}

// Usage
const builder = new SportsCarBuilder();
const director = new CarDirector(builder);

const sportsCar = director.constructSportsCar();
console.log("Sports Car:");
console.log(sportsCar.getDescription());

// Custom configuration without director
const customCar = builder
    .setSeats(4)
    .setEngine("Electric")
    .setGPS()
    .setSunroof()
    .getResult();

console.log("\nCustom Car:");
console.log(customCar.getDescription());

// Practical Example: Query Builder
class SQLQuery {
    private selectClause: string = "";
    private fromClause: string = "";
    private whereConditions: string[] = [];
    private orderByClause: string = "";
    private limitClause: string = "";

    public getSQL(): string {
        let sql = this.selectClause + " " + this.fromClause;

        if (this.whereConditions.length > 0) {
            sql += " WHERE " + this.whereConditions.join(" AND ");
        }

        if (this.orderByClause) {
            sql += " " + this.orderByClause;
        }

        if (this.limitClause) {
            sql += " " + this.limitClause;
        }

        return sql;
    }
}

class SQLQueryBuilder {
    private query: SQLQuery;

    constructor() {
        this.query = new SQLQuery();
    }

    select(...columns: string[]): this {
        this.query["selectClause"] = `SELECT ${columns.join(", ")}`;
        return this;
    }

    from(table: string): this {
        this.query["fromClause"] = `FROM ${table}`;
        return this;
    }

    where(condition: string): this {
        this.query["whereConditions"].push(condition);
        return this;
    }

    orderBy(column: string, direction: "ASC" | "DESC" = "ASC"): this {
        this.query["orderByClause"] = `ORDER BY ${column} ${direction}`;
        return this;
    }

    limit(count: number): this {
        this.query["limitClause"] = `LIMIT ${count}`;
        return this;
    }

    build(): SQLQuery {
        const result = this.query;
        this.query = new SQLQuery();
        return result;
    }
}

// Usage
const queryBuilder = new SQLQueryBuilder();
const query = queryBuilder
    .select("id", "name", "email")
    .from("users")
    .where("age > 18")
    .where("status = 'active'")
    .orderBy("name", "ASC")
    .limit(10)
    .build();

console.log(query.getSQL());
// Output: SELECT id, name, email FROM users WHERE age > 18 AND status = 'active' ORDER BY name ASC LIMIT 10
```

#### Java Implementation

```java
// Builder Pattern

// Product
public class Pizza {
    private final String dough;
    private final String sauce;
    private final String cheese;
    private final boolean pepperoni;
    private final boolean mushrooms;
    private final boolean olives;
    private final boolean bacon;

    // Private constructor - only builder can create
    private Pizza(Builder builder) {
        this.dough = builder.dough;
        this.sauce = builder.sauce;
        this.cheese = builder.cheese;
        this.pepperoni = builder.pepperoni;
        this.mushrooms = builder.mushrooms;
        this.olives = builder.olives;
        this.bacon = builder.bacon;
    }

    @Override
    public String toString() {
        StringBuilder sb = new StringBuilder();
        sb.append("Pizza:\n");
        sb.append("  Dough: ").append(dough).append("\n");
        sb.append("  Sauce: ").append(sauce).append("\n");
        sb.append("  Cheese: ").append(cheese).append("\n");

        List<String> toppings = new ArrayList<>();
        if (pepperoni) toppings.add("Pepperoni");
        if (mushrooms) toppings.add("Mushrooms");
        if (olives) toppings.add("Olives");
        if (bacon) toppings.add("Bacon");

        if (!toppings.isEmpty()) {
            sb.append("  Toppings: ").append(String.join(", ", toppings));
        }

        return sb.toString();
    }

    // Static inner Builder class (common Java pattern)
    public static class Builder {
        // Required parameters
        private final String dough;
        private final String sauce;

        // Optional parameters with defaults
        private String cheese = "Mozzarella";
        private boolean pepperoni = false;
        private boolean mushrooms = false;
        private boolean olives = false;
        private boolean bacon = false;

        // Constructor requires mandatory fields
        public Builder(String dough, String sauce) {
            this.dough = dough;
            this.sauce = sauce;
        }

        public Builder cheese(String cheese) {
            this.cheese = cheese;
            return this;
        }

        public Builder pepperoni() {
            this.pepperoni = true;
            return this;
        }

        public Builder mushrooms() {
            this.mushrooms = true;
            return this;
        }

        public Builder olives() {
            this.olives = true;
            return this;
        }

        public Builder bacon() {
            this.bacon = true;
            return this;
        }

        public Pizza build() {
            return new Pizza(this);
        }
    }
}

// Usage
public class BuilderExample {
    public static void main(String[] args) {
        // Build custom pizza
        Pizza customPizza = new Pizza.Builder("Thin crust", "Tomato")
            .cheese("Parmesan")
            .pepperoni()
            .mushrooms()
            .olives()
            .build();

        System.out.println(customPizza);

        // Build simple pizza
        Pizza simplePizza = new Pizza.Builder("Thick crust", "BBQ")
            .bacon()
            .build();

        System.out.println(simplePizza);
    }
}

// Practical Example: User Builder with Validation
public class User {
    private final String username;      // Required
    private final String email;         // Required
    private final String firstName;     // Optional
    private final String lastName;      // Optional
    private final int age;              // Optional
    private final String phone;         // Optional

    private User(Builder builder) {
        this.username = builder.username;
        this.email = builder.email;
        this.firstName = builder.firstName;
        this.lastName = builder.lastName;
        this.age = builder.age;
        this.phone = builder.phone;
    }

    public static class Builder {
        // Required
        private final String username;
        private final String email;

        // Optional
        private String firstName = "";
        private String lastName = "";
        private int age = 0;
        private String phone = "";

        public Builder(String username, String email) {
            if (username == null || username.isEmpty()) {
                throw new IllegalArgumentException("Username required");
            }
            if (email == null || !email.contains("@")) {
                throw new IllegalArgumentException("Valid email required");
            }
            this.username = username;
            this.email = email;
        }

        public Builder firstName(String firstName) {
            this.firstName = firstName;
            return this;
        }

        public Builder lastName(String lastName) {
            this.lastName = lastName;
            return this;
        }

        public Builder age(int age) {
            if (age < 0 || age > 150) {
                throw new IllegalArgumentException("Invalid age");
            }
            this.age = age;
            return this;
        }

        public Builder phone(String phone) {
            this.phone = phone;
            return this;
        }

        public User build() {
            // Additional validation before building
            if (age > 0 && age < 13) {
                throw new IllegalStateException("Users must be 13 or older");
            }
            return new User(this);
        }
    }
}

// Usage
User user = new User.Builder("johndoe", "john@example.com")
    .firstName("John")
    .lastName("Doe")
    .age(30)
    .phone("555-1234")
    .build();
```

### When to Use

Use Builder when:
- Object construction requires many steps or configurations
- You want to avoid constructor telescoping (many constructors)
- Different representations of same construction process are needed
- Construction process must allow different representations
- You need immutable objects with many optional parameters

**Common Use Cases**:
- Complex configuration objects
- HTTP request/response builders
- SQL query builders
- Document/report generators
- Test data builders
- UI component builders

### When NOT to Use

Avoid Builder when:
- Object is simple with few parameters
- Object doesn't have optional parameters
- Simple constructor or factory method suffices
- All parameters are required (no optional combinations)

### Real-World Examples

**Fluent API Configuration**:
```python
# Build complex configurations fluently
config = (ConfigBuilder()
          .with_database("postgres://localhost/db")
          .with_cache("redis://localhost")
          .with_timeout(30)
          .with_retries(3)
          .build())
```

**Query Building**:
```typescript
// Build SQL queries programmatically
const query = queryBuilder
    .select("id", "name")
    .from("users")
    .where("age > 18")
    .orderBy("name")
    .limit(10)
    .build();
```

**Test Data Creation**:
```java
// Build test objects with defaults and overrides
User testUser = new User.Builder("testuser", "test@example.com")
    .firstName("Test")
    .lastName("User")
    .age(25)
    .build();
```

### Related Patterns

- **Abstract Factory**: Can use Builder to create complex products
- **Composite**: Often built using Builder pattern
- **Singleton**: Builder can be implemented as Singleton

---

## 5. Prototype Pattern

### Intent

Specify the kinds of objects to create using a prototypical instance, and create new objects by copying this prototype.

### Problem

How do you create new objects when:
- Creating an object is expensive (database queries, network calls, complex initialization)
- Object creation requires many configuration steps
- You need copies of existing objects with slight modifications
- The exact class to instantiate isn't known until runtime

### Solution

Clone existing objects (prototypes) instead of creating new instances from scratch. Implement a cloning method that creates a copy of the current object.

### Structure

**Key Participants**:
- **Prototype**: Declares interface for cloning itself
- **ConcretePrototype**: Implements cloning operation
- **Client**: Creates new objects by asking prototype to clone itself

### Implementation

#### Python Implementation

```python
# Prototype Pattern

import copy
from abc import ABC, abstractmethod
from typing import List

# Prototype Interface
class Prototype(ABC):
    """Abstract prototype interface."""

    @abstractmethod
    def clone(self) -> 'Prototype':
        """Clone the object."""
        pass

# Concrete Prototypes
class Document(Prototype):
    """Document prototype."""

    def __init__(self, title: str, content: str, author: str):
        self.title = title
        self.content = content
        self.author = author
        self.sections: List[str] = []
        self.metadata: dict = {}

    def clone(self) -> 'Document':
        """Create deep copy of document."""
        return copy.deepcopy(self)

    def __str__(self) -> str:
        return (f"Document: {self.title}\n"
                f"Author: {self.author}\n"
                f"Sections: {len(self.sections)}\n"
                f"Content length: {len(self.content)}")

class Shape(Prototype):
    """Shape prototype."""

    def __init__(self, x: int, y: int, color: str):
        self.x = x
        self.y = y
        self.color = color

    def clone(self) -> 'Shape':
        """Clone shape."""
        return copy.copy(self)  # Shallow copy sufficient

    def __str__(self) -> str:
        return f"{self.__class__.__name__} at ({self.x}, {self.y}) color: {self.color}"

class Circle(Shape):
    """Circle shape."""

    def __init__(self, x: int, y: int, color: str, radius: int):
        super().__init__(x, y, color)
        self.radius = radius

    def __str__(self) -> str:
        return f"Circle at ({self.x}, {self.y}) radius: {self.radius} color: {self.color}"

class Rectangle(Shape):
    """Rectangle shape."""

    def __init__(self, x: int, y: int, color: str, width: int, height: int):
        super().__init__(x, y, color)
        self.width = width
        self.height = height

    def __str__(self) -> str:
        return f"Rectangle at ({self.x}, {self.y}) size: {self.width}x{self.height} color: {self.color}"

# Prototype Registry
class ShapeRegistry:
    """Registry for managing prototypes."""

    def __init__(self):
        self._prototypes: dict[str, Shape] = {}

    def register(self, key: str, prototype: Shape) -> None:
        """Register a prototype."""
        self._prototypes[key] = prototype

    def unregister(self, key: str) -> None:
        """Unregister a prototype."""
        del self._prototypes[key]

    def clone(self, key: str) -> Shape:
        """Clone a registered prototype."""
        prototype = self._prototypes.get(key)
        if prototype is None:
            raise ValueError(f"Prototype '{key}' not found")
        return prototype.clone()

# Usage
# Create original objects
red_circle = Circle(10, 10, "red", 5)
blue_rectangle = Rectangle(20, 20, "blue", 10, 5)

print("Original shapes:")
print(red_circle)
print(blue_rectangle)

# Clone and modify
red_circle_copy = red_circle.clone()
red_circle_copy.x = 50
red_circle_copy.y = 50

print("\nCloned and modified:")
print(red_circle)      # Original unchanged
print(red_circle_copy) # Modified copy

# Use registry
registry = ShapeRegistry()
registry.register("default-circle", Circle(0, 0, "black", 10))
registry.register("default-rectangle", Rectangle(0, 0, "black", 20, 10))

# Create instances from registry
circle1 = registry.clone("default-circle")
circle1.x = 100
circle1.y = 100
circle1.color = "green"

circle2 = registry.clone("default-circle")
circle2.x = 200
circle2.y = 200
circle2.color = "yellow"

print("\nClones from registry:")
print(circle1)
print(circle2)

# Practical Example: Database Connection Configuration
class DatabaseConfig(Prototype):
    """Database configuration prototype."""

    def __init__(self, host: str, port: int, database: str):
        self.host = host
        self.port = port
        self.database = database
        self.username = ""
        self.password = ""
        self.pool_size = 10
        self.timeout = 30
        self.ssl_enabled = False

    def clone(self) -> 'DatabaseConfig':
        """Clone configuration."""
        return copy.deepcopy(self)

    def __str__(self) -> str:
        return (f"Database: {self.database}@{self.host}:{self.port}\n"
                f"Pool size: {self.pool_size}, Timeout: {self.timeout}s")

# Create base configuration
production_config = DatabaseConfig("prod.example.com", 5432, "production_db")
production_config.username = "prod_user"
production_config.password = "secure_password"
production_config.pool_size = 50
production_config.ssl_enabled = True

# Clone for different environments
staging_config = production_config.clone()
staging_config.host = "staging.example.com"
staging_config.database = "staging_db"
staging_config.username = "staging_user"

dev_config = production_config.clone()
dev_config.host = "localhost"
dev_config.database = "dev_db"
dev_config.username = "dev_user"
dev_config.pool_size = 5
dev_config.ssl_enabled = False

print("\nDatabase Configurations:")
print("Production:", production_config)
print("Staging:", staging_config)
print("Development:", dev_config)
```

#### TypeScript Implementation

```typescript
// Prototype Pattern

// Prototype Interface
interface Cloneable<T> {
    clone(): T;
}

// Concrete Prototype
class Person implements Cloneable<Person> {
    public firstName: string;
    public lastName: string;
    public age: number;
    public address: Address;
    public hobbies: string[];

    constructor(firstName: string, lastName: string, age: number, address: Address) {
        this.firstName = firstName;
        this.lastName = lastName;
        this.age = age;
        this.address = address;
        this.hobbies = [];
    }

    // Deep clone
    clone(): Person {
        const cloned = new Person(
            this.firstName,
            this.lastName,
            this.age,
            this.address.clone() // Deep clone nested object
        );
        cloned.hobbies = [...this.hobbies]; // Clone array
        return cloned;
    }

    getDescription(): string {
        return `${this.firstName} ${this.lastName}, ${this.age} years old\n` +
               `Address: ${this.address.getFullAddress()}\n` +
               `Hobbies: ${this.hobbies.join(", ")}`;
    }
}

class Address implements Cloneable<Address> {
    constructor(
        public street: string,
        public city: string,
        public country: string,
        public zipCode: string
    ) {}

    clone(): Address {
        return new Address(this.street, this.city, this.country, this.zipCode);
    }

    getFullAddress(): string {
        return `${this.street}, ${this.city}, ${this.country} ${this.zipCode}`;
    }
}

// Usage
const originalPerson = new Person(
    "John",
    "Doe",
    30,
    new Address("123 Main St", "New York", "USA", "10001")
);
originalPerson.hobbies = ["reading", "coding", "hiking"];

console.log("Original Person:");
console.log(originalPerson.getDescription());

// Clone and modify
const clonedPerson = originalPerson.clone();
clonedPerson.firstName = "Jane";
clonedPerson.age = 28;
clonedPerson.address.city = "Boston";
clonedPerson.hobbies.push("painting");

console.log("\nCloned Person:");
console.log(clonedPerson.getDescription());

console.log("\nOriginal Person (unchanged):");
console.log(originalPerson.getDescription());

// Prototype Registry
class PrototypeRegistry<T extends Cloneable<T>> {
    private prototypes: Map<string, T> = new Map();

    register(key: string, prototype: T): void {
        this.prototypes.set(key, prototype);
    }

    unregister(key: string): void {
        this.prototypes.delete(key);
    }

    clone(key: string): T {
        const prototype = this.prototypes.get(key);
        if (!prototype) {
            throw new Error(`Prototype '${key}' not found`);
        }
        return prototype.clone();
    }

    listPrototypes(): string[] {
        return Array.from(this.prototypes.keys());
    }
}

// Practical Example: UI Component Templates
abstract class UIComponent implements Cloneable<UIComponent> {
    constructor(
        public x: number,
        public y: number,
        public width: number,
        public height: number
    ) {}

    abstract clone(): UIComponent;
    abstract render(): string;
}

class Button extends UIComponent {
    constructor(
        x: number,
        y: number,
        width: number,
        height: number,
        public text: string,
        public color: string
    ) {
        super(x, y, width, height);
    }

    clone(): Button {
        return new Button(this.x, this.y, this.width, this.height, this.text, this.color);
    }

    render(): string {
        return `Button "${this.text}" at (${this.x}, ${this.y}) size ${this.width}x${this.height} color ${this.color}`;
    }
}

class TextField extends UIComponent {
    constructor(
        x: number,
        y: number,
        width: number,
        height: number,
        public placeholder: string,
        public maxLength: number
    ) {
        super(x, y, width, height);
    }

    clone(): TextField {
        return new TextField(this.x, this.y, this.width, this.height, this.placeholder, this.maxLength);
    }

    render(): string {
        return `TextField at (${this.x}, ${this.y}) size ${this.width}x${this.height} placeholder "${this.placeholder}"`;
    }
}

// Create component registry with templates
const componentRegistry = new PrototypeRegistry<UIComponent>();

// Register standard component templates
componentRegistry.register("primary-button", new Button(0, 0, 100, 30, "Click me", "blue"));
componentRegistry.register("secondary-button", new Button(0, 0, 100, 30, "Cancel", "gray"));
componentRegistry.register("text-input", new TextField(0, 0, 200, 30, "Enter text...", 100));

// Create UI using templates
const submitButton = componentRegistry.clone("primary-button") as Button;
submitButton.x = 10;
submitButton.y = 50;
submitButton.text = "Submit";

const cancelButton = componentRegistry.clone("secondary-button") as Button;
cancelButton.x = 120;
cancelButton.y = 50;

const nameField = componentRegistry.clone("text-input") as TextField;
nameField.x = 10;
nameField.y = 10;
nameField.placeholder = "Enter your name";

console.log("\nUI Components from templates:");
console.log(submitButton.render());
console.log(cancelButton.render());
console.log(nameField.render());
```

#### Java Implementation

```java
// Prototype Pattern

// Prototype Interface
public interface Cloneable {
    Object clone();
}

// Concrete Prototype
public class Employee implements Cloneable {
    private String name;
    private String department;
    private double salary;
    private Address address;
    private List<String> skills;

    public Employee(String name, String department, double salary, Address address) {
        this.name = name;
        this.department = department;
        this.salary = salary;
        this.address = address;
        this.skills = new ArrayList<>();
    }

    // Deep clone
    @Override
    public Employee clone() {
        Employee cloned = new Employee(
            this.name,
            this.department,
            this.salary,
            this.address.clone() // Deep clone nested object
        );
        cloned.skills = new ArrayList<>(this.skills); // Clone list
        return cloned;
    }

    public void addSkill(String skill) {
        this.skills.add(skill);
    }

    public void setName(String name) {
        this.name = name;
    }

    public void setDepartment(String department) {
        this.department = department;
    }

    public void setSalary(double salary) {
        this.salary = salary;
    }

    @Override
    public String toString() {
        return String.format("Employee: %s\nDepartment: %s\nSalary: $%.2f\nAddress: %s\nSkills: %s",
            name, department, salary, address, String.join(", ", skills));
    }
}

public class Address implements Cloneable {
    private String street;
    private String city;
    private String state;
    private String zipCode;

    public Address(String street, String city, String state, String zipCode) {
        this.street = street;
        this.city = city;
        this.state = state;
        this.zipCode = zipCode;
    }

    @Override
    public Address clone() {
        return new Address(this.street, this.city, this.state, this.zipCode);
    }

    @Override
    public String toString() {
        return String.format("%s, %s, %s %s", street, city, state, zipCode);
    }
}

// Prototype Registry
public class EmployeeRegistry {
    private Map<String, Employee> prototypes = new HashMap<>();

    public void register(String key, Employee prototype) {
        prototypes.put(key, prototype);
    }

    public void unregister(String key) {
        prototypes.remove(key);
    }

    public Employee clone(String key) {
        Employee prototype = prototypes.get(key);
        if (prototype == null) {
            throw new IllegalArgumentException("Prototype '" + key + "' not found");
        }
        return prototype.clone();
    }

    public Set<String> listPrototypes() {
        return prototypes.keySet();
    }
}

// Usage
public class PrototypeExample {
    public static void main(String[] args) {
        // Create registry with templates
        EmployeeRegistry registry = new EmployeeRegistry();

        // Create template employees
        Address techAddress = new Address("100 Tech St", "San Francisco", "CA", "94105");
        Employee seniorDev = new Employee("Template Senior Dev", "Engineering", 120000, techAddress);
        seniorDev.addSkill("Java");
        seniorDev.addSkill("Python");
        seniorDev.addSkill("Leadership");

        Employee juniorDev = new Employee("Template Junior Dev", "Engineering", 80000, techAddress);
        juniorDev.addSkill("Java");
        juniorDev.addSkill("Git");

        // Register templates
        registry.register("senior-dev", seniorDev);
        registry.register("junior-dev", juniorDev);

        // Create actual employees from templates
        Employee john = registry.clone("senior-dev");
        john.setName("John Smith");
        john.addSkill("Microservices");

        Employee jane = registry.clone("junior-dev");
        jane.setName("Jane Doe");
        jane.addSkill("Spring Boot");

        System.out.println("Employee 1:");
        System.out.println(john);
        System.out.println("\nEmployee 2:");
        System.out.println(jane);

        // Template unchanged
        System.out.println("\nTemplate (unchanged):");
        System.out.println(seniorDev);
    }
}

// Practical Example: Game Character Prototypes
public abstract class GameCharacter implements Cloneable {
    protected String name;
    protected int health;
    protected int strength;
    protected int defense;
    protected List<String> abilities;
    protected Equipment equipment;

    public GameCharacter(String name, int health, int strength, int defense) {
        this.name = name;
        this.health = health;
        this.strength = strength;
        this.defense = defense;
        this.abilities = new ArrayList<>();
        this.equipment = new Equipment();
    }

    @Override
    public abstract GameCharacter clone();

    public void setName(String name) {
        this.name = name;
    }

    public void addAbility(String ability) {
        this.abilities.add(ability);
    }

    @Override
    public String toString() {
        return String.format("%s - HP: %d, STR: %d, DEF: %d\nAbilities: %s\nEquipment: %s",
            name, health, strength, defense,
            String.join(", ", abilities),
            equipment);
    }
}

public class Warrior extends GameCharacter {
    public Warrior(String name) {
        super(name, 150, 80, 60);
        addAbility("Slash");
        addAbility("Shield Bash");
    }

    @Override
    public Warrior clone() {
        Warrior cloned = new Warrior(this.name);
        cloned.health = this.health;
        cloned.strength = this.strength;
        cloned.defense = this.defense;
        cloned.abilities = new ArrayList<>(this.abilities);
        cloned.equipment = this.equipment.clone();
        return cloned;
    }
}

public class Mage extends GameCharacter {
    public Mage(String name) {
        super(name, 80, 120, 30);
        addAbility("Fireball");
        addAbility("Ice Blast");
    }

    @Override
    public Mage clone() {
        Mage cloned = new Mage(this.name);
        cloned.health = this.health;
        cloned.strength = this.strength;
        cloned.defense = this.defense;
        cloned.abilities = new ArrayList<>(this.abilities);
        cloned.equipment = this.equipment.clone();
        return cloned;
    }
}

public class Equipment implements Cloneable {
    private String weapon = "None";
    private String armor = "None";

    @Override
    public Equipment clone() {
        Equipment cloned = new Equipment();
        cloned.weapon = this.weapon;
        cloned.armor = this.armor;
        return cloned;
    }

    @Override
    public String toString() {
        return String.format("Weapon: %s, Armor: %s", weapon, armor);
    }
}

// Create character templates and spawn game characters
Warrior warriorTemplate = new Warrior("Warrior Template");
Mage mageTemplate = new Mage("Mage Template");

// Spawn player characters
Warrior player1 = warriorTemplate.clone();
player1.setName("Aragorn");
player1.addAbility("Heroic Strike");

Mage player2 = mageTemplate.clone();
player2.setName("Gandalf");
player2.addAbility("Lightning Bolt");
```

### When to Use

Use Prototype when:
- Object creation is expensive (complex initialization, database queries)
- You need many similar objects with slight variations
- Classes to instantiate are specified at runtime
- You want to avoid building class hierarchies of factories
- Instances have few combinations of state

**Common Use Cases**:
- Cloning database records
- Creating game objects from templates
- Copying configuration objects
- UI component templates
- Document templates

### When NOT to Use

Avoid Prototype when:
- Objects are simple and cheap to create
- Object has no varying state worth cloning
- Deep vs shallow copy creates complexity
- Circular references make cloning difficult

**Challenges**:
- **Deep vs Shallow Copy**: Must decide which members to deep copy
- **Circular References**: Can cause infinite recursion
- **Immutable Objects**: Cloning may be unnecessary

### Real-World Examples

**Game Development**:
```java
// Create enemies from templates
Enemy goblin = enemyRegistry.clone("goblin-template");
goblin.setPosition(100, 200);
goblin.setName("Goblin #47");
```

**Configuration Management**:
```typescript
// Clone base config for different environments
const devConfig = productionConfig.clone();
devConfig.host = "localhost";
devConfig.debug = true;
```

**UI Components**:
```python
# Create UI from component templates
button = component_registry.clone("primary-button")
button.x = 50
button.y = 100
button.text = "Submit"
```

### Related Patterns

- **Abstract Factory**: Can be alternative to Prototype
- **Composite**: Often benefits from Prototype for cloning structures
- **Decorator**: Often used with Prototype

---

# Structural Patterns

Structural patterns explain how to assemble objects and classes into larger structures while keeping these structures flexible and efficient.

## 6. Adapter Pattern

### Intent

Convert the interface of a class into another interface clients expect. Adapter lets classes work together that couldn't otherwise because of incompatible interfaces.

### Problem

You want to use an existing class, but its interface doesn't match the one you need. You can't or don't want to modify the existing class. How do you make incompatible interfaces work together?

### Solution

Create an adapter class that wraps the existing class and translates between the interfaces. The adapter implements the target interface and delegates calls to the existing class (adaptee).

### Structure

**Key Participants**:
- **Target**: Defines domain-specific interface client uses
- **Adapter**: Adapts Adaptee interface to Target interface
- **Adaptee**: Existing interface that needs adapting
- **Client**: Collaborates with objects conforming to Target interface

### Implementation

#### Python Implementation

```python
# Adapter Pattern

from abc import ABC, abstractmethod

# Target Interface
class MediaPlayer(ABC):
    """Target interface that client expects."""

    @abstractmethod
    def play(self, audio_type: str, filename: str) -> str:
        pass

# Adaptee - Existing incompatible interfaces
class AdvancedMP3Player:
    """Existing class with incompatible interface."""

    def play_mp3(self, filename: str) -> str:
        return f"Playing MP3 file: {filename}"

class AdvancedMP4Player:
    """Another existing class with different interface."""

    def play_mp4(self, filename: str) -> str:
        return f"Playing MP4 file: {filename}"

class AdvancedVLCPlayer:
    """Third existing class with yet another interface."""

    def play_vlc(self, filename: str) -> str:
        return f"Playing VLC file: {filename}"

# Adapter
class MediaAdapter(MediaPlayer):
    """Adapter that makes advanced players compatible with MediaPlayer interface."""

    def __init__(self, audio_type: str):
        self.audio_type = audio_type.lower()
        if self.audio_type == "mp3":
            self.player = AdvancedMP3Player()
        elif self.audio_type == "mp4":
            self.player = AdvancedMP4Player()
        elif self.audio_type == "vlc":
            self.player = AdvancedVLCPlayer()
        else:
            raise ValueError(f"Unsupported audio type: {audio_type}")

    def play(self, audio_type: str, filename: str) -> str:
        """Adapt the play method to call appropriate player."""
        audio_type = audio_type.lower()
        if audio_type == "mp3":
            return self.player.play_mp3(filename)
        elif audio_type == "mp4":
            return self.player.play_mp4(filename)
        elif audio_type == "vlc":
            return self.player.play_vlc(filename)
        else:
            raise ValueError(f"Unsupported format: {audio_type}")

# Concrete Target
class AudioPlayer(MediaPlayer):
    """Client-facing class that uses adapters."""

    def play(self, audio_type: str, filename: str) -> str:
        audio_type = audio_type.lower()

        # Built-in support for basic formats
        if audio_type == "mp3":
            return f"Playing MP3 file: {filename}"

        # Use adapter for advanced formats
        elif audio_type in ["mp4", "vlc"]:
            adapter = MediaAdapter(audio_type)
            return adapter.play(audio_type, filename)

        else:
            return f"Invalid media type: {audio_type}"

# Usage
player = AudioPlayer()

print(player.play("mp3", "song.mp3"))
print(player.play("mp4", "video.mp4"))
print(player.play("vlc", "movie.vlc"))

# Practical Example: Payment Gateway Adapter
class PaymentProcessor(ABC):
    """Target interface for payment processing."""

    @abstractmethod
    def process_payment(self, amount: float) -> str:
        pass

class StripeAPI:
    """Stripe's incompatible interface."""

    def charge(self, amount_in_cents: int, currency: str) -> dict:
        return {
            "status": "success",
            "amount": amount_in_cents,
            "currency": currency
        }

class PayPalAPI:
    """PayPal's incompatible interface."""

    def make_payment(self, amount: float, description: str) -> dict:
        return {
            "success": True,
            "total": amount,
            "memo": description
        }

# Adapters
class StripeAdapter(PaymentProcessor):
    """Adapter for Stripe API."""

    def __init__(self):
        self.stripe = StripeAPI()

    def process_payment(self, amount: float) -> str:
        # Convert dollars to cents
        amount_in_cents = int(amount * 100)
        result = self.stripe.charge(amount_in_cents, "USD")
        return f"Stripe payment: ${amount:.2f} - Status: {result['status']}"

class PayPalAdapter(PaymentProcessor):
    """Adapter for PayPal API."""

    def __init__(self):
        self.paypal = PayPalAPI()

    def process_payment(self, amount: float) -> str:
        result = self.paypal.make_payment(amount, "Online purchase")
        status = "success" if result['success'] else "failed"
        return f"PayPal payment: ${amount:.2f} - Status: {status}"

# Client code
def process_order(payment_method: PaymentProcessor, amount: float):
    """Client code works with any payment processor."""
    return payment_method.process_payment(amount)

# Usage
stripe = StripeAdapter()
paypal = PayPalAdapter()

print(process_order(stripe, 99.99))
print(process_order(paypal, 149.50))
```

#### TypeScript Implementation

```typescript
// Adapter Pattern

// Target Interface
interface DataStorage {
    save(data: string): string;
    load(): string;
}

// Adaptee - Cloud storage with incompatible interface
class CloudStorageAPI {
    uploadToCloud(content: string, key: string): boolean {
        console.log(`Uploading to cloud with key ${key}: ${content}`);
        return true;
    }

    downloadFromCloud(key: string): string {
        console.log(`Downloading from cloud: ${key}`);
        return `Cloud data for ${key}`;
    }
}

// Adaptee - Local storage with different interface
class LocalFileSystem {
    writeFile(filepath: string, content: string): void {
        console.log(`Writing to file ${filepath}: ${content}`);
    }

    readFile(filepath: string): string {
        console.log(`Reading file: ${filepath}`);
        return `File content from ${filepath}`;
    }
}

// Adapters
class CloudStorageAdapter implements DataStorage {
    private cloudStorage: CloudStorageAPI;
    private storageKey: string;

    constructor(key: string) {
        this.cloudStorage = new CloudStorageAPI();
        this.storageKey = key;
    }

    save(data: string): string {
        const success = this.cloudStorage.uploadToCloud(data, this.storageKey);
        return success ? "Data saved to cloud" : "Failed to save";
    }

    load(): string {
        return this.cloudStorage.downloadFromCloud(this.storageKey);
    }
}

class LocalStorageAdapter implements DataStorage {
    private fileSystem: LocalFileSystem;
    private filepath: string;

    constructor(filepath: string) {
        this.fileSystem = new LocalFileSystem();
        this.filepath = filepath;
    }

    save(data: string): string {
        this.fileSystem.writeFile(this.filepath, data);
        return "Data saved locally";
    }

    load(): string {
        return this.fileSystem.readFile(this.filepath);
    }
}

// Client code
class DataManager {
    private storage: DataStorage;

    constructor(storage: DataStorage) {
        this.storage = storage;
    }

    saveData(data: string): void {
        const result = this.storage.save(data);
        console.log(result);
    }

    loadData(): string {
        return this.storage.load();
    }
}

// Usage
const cloudStorage = new CloudStorageAdapter("user-data-123");
const localStorage = new LocalStorageAdapter("/data/user-data.json");

const cloudManager = new DataManager(cloudStorage);
cloudManager.saveData("Important user data");
console.log(cloudManager.loadData());

const localManager = new DataManager(localStorage);
localManager.saveData("User preferences");
console.log(localManager.loadData());
```

#### Java Implementation

```java
// Adapter Pattern

// Target Interface
public interface Temperature {
    double getTemperature();
}

// Adaptee - Existing Fahrenheit sensor
public class FahrenheitSensor {
    public double getFahrenheitTemp() {
        // Simulate sensor reading
        return 98.6;
    }
}

// Adapter
public class FahrenheitToCelsiusAdapter implements Temperature {
    private FahrenheitSensor sensor;

    public FahrenheitToCelsiusAdapter(FahrenheitSensor sensor) {
        this.sensor = sensor;
    }

    @Override
    public double getTemperature() {
        // Convert Fahrenheit to Celsius
        double fahrenheit = sensor.getFahrenheitTemp();
        return (fahrenheit - 32) * 5.0 / 9.0;
    }
}

// Client code
public class WeatherStation {
    private Temperature temperatureSensor;

    public WeatherStation(Temperature sensor) {
        this.temperatureSensor = sensor;
    }

    public void displayTemperature() {
        double temp = temperatureSensor.getTemperature();
        System.out.printf("Current temperature: %.1f°C%n", temp);
    }
}

// Usage
public class AdapterExample {
    public static void main(String[] args) {
        FahrenheitSensor fahrenheitSensor = new FahrenheitSensor();
        Temperature celsiusAdapter = new FahrenheitToCelsiusAdapter(fahrenheitSensor);

        WeatherStation station = new WeatherStation(celsiusAdapter);
        station.displayTemperature();
        // Output: Current temperature: 37.0°C
    }
}

// Practical Example: Legacy Database Adapter
public interface ModernDatabase {
    void connect(String connectionString);
    void executeQuery(String sql);
    void disconnect();
}

public class LegacyDatabaseSystem {
    public void openConnection(String host, int port, String database) {
        System.out.println("Legacy: Opening connection to " + database);
    }

    public void runCommand(String command) {
        System.out.println("Legacy: Executing command: " + command);
    }

    public void closeConnection() {
        System.out.println("Legacy: Closing connection");
    }
}

public class LegacyDatabaseAdapter implements ModernDatabase {
    private LegacyDatabaseSystem legacyDb;
    private String host;
    private int port;
    private String database;

    public LegacyDatabaseAdapter(LegacyDatabaseSystem legacyDb) {
        this.legacyDb = legacyDb;
    }

    @Override
    public void connect(String connectionString) {
        // Parse connection string: "host:port/database"
        String[] parts = connectionString.split("[:/]");
        this.host = parts[0];
        this.port = Integer.parseInt(parts[1]);
        this.database = parts[2];

        legacyDb.openConnection(host, port, database);
    }

    @Override
    public void executeQuery(String sql) {
        legacyDb.runCommand(sql);
    }

    @Override
    public void disconnect() {
        legacyDb.closeConnection();
    }
}

// Client code
ModernDatabase db = new LegacyDatabaseAdapter(new LegacyDatabaseSystem());
db.connect("localhost:5432/mydb");
db.executeQuery("SELECT * FROM users");
db.disconnect();
```

### When to Use

Use Adapter when:
- You want to use existing class with incompatible interface
- You want to create reusable class that cooperates with unrelated classes
- You need to use several existing subclasses but can't adapt their interface by subclassing
- Third-party library interface doesn't match your needs

**Common Use Cases**:
- Integrating third-party libraries
- Legacy system integration
- API version compatibility
- Cross-platform compatibility
- Unit testing with mocks

### When NOT to Use

Avoid Adapter when:
- You can modify the source code of incompatible class
- The adaptation logic is trivial
- Creating new interface from scratch is simpler
- Wrapper adds unnecessary complexity

### Real-World Examples

**Payment Processing**:
```python
# Adapt different payment gateway APIs
stripe_processor = StripeAdapter()
paypal_processor = PayPalAdapter()
# Both use same interface
```

**Data Storage**:
```typescript
// Adapt different storage backends
const cloudStorage = new CloudStorageAdapter("key");
const localStorage = new LocalStorageAdapter("path");
// Same interface for all storage types
```

**Legacy Integration**:
```java
// Adapt legacy system to modern interface
ModernDatabase db = new LegacyDatabaseAdapter(legacySystem);
db.connect("localhost:5432/db");
```

### Related Patterns

- **Bridge**: Similar structure but different intent (separates abstraction from implementation)
- **Decorator**: Enhances interface without changing it
- **Proxy**: Provides same interface, not different one

---

## 7. Bridge Pattern

### Intent

Decouple an abstraction from its implementation so that the two can vary independently.

### Problem

When an abstraction can have multiple implementations, how do you avoid a proliferation of classes? For example, shapes (circle, rectangle) with rendering methods (vector, raster) would create many combinations (VectorCircle, RasterCircle, VectorRectangle, RasterRectangle).

### Solution

Separate the abstraction hierarchy from the implementation hierarchy. The abstraction contains a reference to the implementation and delegates work to it.

### Structure

**Key Participants**:
- **Abstraction**: Defines abstraction's interface; maintains reference to Implementor
- **RefinedAbstraction**: Extends Abstraction
- **Implementor**: Defines interface for implementation classes
- **ConcreteImplementor**: Implements Implementor interface

### Implementation

#### Python Implementation

```python
# Bridge Pattern

from abc import ABC, abstractmethod

# Implementor Interface
class Renderer(ABC):
    """Implementation interface for rendering."""

    @abstractmethod
    def render_circle(self, radius: int) -> str:
        pass

    @abstractmethod
    def render_rectangle(self, width: int, height: int) -> str:
        pass

# Concrete Implementors
class VectorRenderer(Renderer):
    """Vector rendering implementation."""

    def render_circle(self, radius: int) -> str:
        return f"Drawing circle with radius {radius} using vector graphics"

    def render_rectangle(self, width: int, height: int) -> str:
        return f"Drawing rectangle {width}x{height} using vector graphics"

class RasterRenderer(Renderer):
    """Raster rendering implementation."""

    def render_circle(self, radius: int) -> str:
        return f"Drawing circle with radius {radius} using raster graphics (pixels)"

    def render_rectangle(self, width: int, height: int) -> str:
        return f"Drawing rectangle {width}x{height} using raster graphics (pixels)"

# Abstraction
class Shape(ABC):
    """Abstraction for shapes."""

    def __init__(self, renderer: Renderer):
        self.renderer = renderer

    @abstractmethod
    def draw(self) -> str:
        pass

    @abstractmethod
    def resize(self, factor: float) -> None:
        pass

# Refined Abstractions
class Circle(Shape):
    """Circle abstraction."""

    def __init__(self, renderer: Renderer, radius: int):
        super().__init__(renderer)
        self.radius = radius

    def draw(self) -> str:
        return self.renderer.render_circle(self.radius)

    def resize(self, factor: float) -> None:
        self.radius = int(self.radius * factor)

class Rectangle(Shape):
    """Rectangle abstraction."""

    def __init__(self, renderer: Renderer, width: int, height: int):
        super().__init__(renderer)
        self.width = width
        self.height = height

    def draw(self) -> str:
        return self.renderer.render_rectangle(self.width, self.height)

    def resize(self, factor: float) -> None:
        self.width = int(self.width * factor)
        self.height = int(self.height * factor)

# Usage
# Vector rendering
vector = VectorRenderer()
circle = Circle(vector, 5)
rectangle = Rectangle(vector, 10, 20)

print(circle.draw())
print(rectangle.draw())

# Raster rendering
raster = RasterRenderer()
circle2 = Circle(raster, 5)
rectangle2 = Rectangle(raster, 10, 20)

print(circle2.draw())
print(rectangle2.draw())

# Resize and redraw
circle.resize(2)
print(circle.draw())

# Practical Example: Remote Control and Devices
class Device(ABC):
    """Implementation interface for devices."""

    @abstractmethod
    def power_on(self) -> str:
        pass

    @abstractmethod
    def power_off(self) -> str:
        pass

    @abstractmethod
    def set_volume(self, volume: int) -> str:
        pass

class TV(Device):
    """Concrete TV implementation."""

    def __init__(self):
        self.volume = 50
        self.on = False

    def power_on(self) -> str:
        self.on = True
        return "TV: Powering on"

    def power_off(self) -> str:
        self.on = False
        return "TV: Powering off"

    def set_volume(self, volume: int) -> str:
        self.volume = volume
        return f"TV: Setting volume to {volume}"

class Radio(Device):
    """Concrete Radio implementation."""

    def __init__(self):
        self.volume = 30
        self.on = False

    def power_on(self) -> str:
        self.on = True
        return "Radio: Turning on"

    def power_off(self) -> str:
        self.on = False
        return "Radio: Turning off"

    def set_volume(self, volume: int) -> str:
        self.volume = volume
        return f"Radio: Volume set to {volume}"

class RemoteControl:
    """Abstraction for remote controls."""

    def __init__(self, device: Device):
        self.device = device

    def toggle_power(self) -> str:
        return self.device.power_on()

    def volume_up(self) -> str:
        return self.device.set_volume(60)

class AdvancedRemoteControl(RemoteControl):
    """Refined abstraction with additional features."""

    def mute(self) -> str:
        return self.device.set_volume(0)

# Usage
tv = TV()
remote = RemoteControl(tv)
print(remote.toggle_power())
print(remote.volume_up())

radio = Radio()
advanced_remote = AdvancedRemoteControl(radio)
print(advanced_remote.toggle_power())
print(advanced_remote.mute())
```

#### TypeScript Implementation

```typescript
// Bridge Pattern

// Implementor Interface
interface MessageSender {
    sendMessage(message: string, recipient: string): string;
}

// Concrete Implementors
class EmailSender implements MessageSender {
    sendMessage(message: string, recipient: string): string {
        return `Sending email to ${recipient}: ${message}`;
    }
}

class SMSSender implements MessageSender {
    sendMessage(message: string, recipient: string): string {
        return `Sending SMS to ${recipient}: ${message}`;
    }
}

class PushNotificationSender implements MessageSender {
    sendMessage(message: string, recipient: string): string {
        return `Sending push notification to ${recipient}: ${message}`;
    }
}

// Abstraction
abstract class Message {
    protected sender: MessageSender;

    constructor(sender: MessageSender) {
        this.sender = sender;
    }

    abstract send(recipient: string): string;
}

// Refined Abstractions
class TextMessage extends Message {
    private content: string;

    constructor(sender: MessageSender, content: string) {
        super(sender);
        this.content = content;
    }

    send(recipient: string): string {
        return this.sender.sendMessage(this.content, recipient);
    }
}

class UrgentMessage extends Message {
    private content: string;

    constructor(sender: MessageSender, content: string) {
        super(sender);
        this.content = `URGENT: ${content}`;
    }

    send(recipient: string): string {
        // Send multiple times for urgency
        const result1 = this.sender.sendMessage(this.content, recipient);
        const result2 = this.sender.sendMessage(this.content, recipient);
        return `${result1}\n${result2}`;
    }
}

// Usage
const emailSender = new EmailSender();
const smsSender = new SMSSender();
const pushSender = new PushNotificationSender();

const emailMessage = new TextMessage(emailSender, "Hello via email");
console.log(emailMessage.send("user@example.com"));

const smsMessage = new TextMessage(smsSender, "Hello via SMS");
console.log(smsMessage.send("+1234567890"));

const urgentPush = new UrgentMessage(pushSender, "System down!");
console.log(urgentPush.send("admin-device-id"));
```

#### Java Implementation

```java
// Bridge Pattern

// Implementor Interface
public interface DataSource {
    void writeData(String data);
    String readData();
}

// Concrete Implementors
public class DatabaseSource implements DataSource {
    @Override
    public void writeData(String data) {
        System.out.println("Writing to database: " + data);
    }

    @Override
    public String readData() {
        return "Data from database";
    }
}

public class FileSource implements DataSource {
    @Override
    public void writeData(String data) {
        System.out.println("Writing to file: " + data);
    }

    @Override
    public String readData() {
        return "Data from file";
    }
}

// Abstraction
public abstract class DataService {
    protected DataSource dataSource;

    public DataService(DataSource dataSource) {
        this.dataSource = dataSource;
    }

    public abstract void save(String data);
    public abstract String load();
}

// Refined Abstractions
public class UserService extends DataService {
    public UserService(DataSource dataSource) {
        super(dataSource);
    }

    @Override
    public void save(String data) {
        String formattedData = "User: " + data;
        dataSource.writeData(formattedData);
    }

    @Override
    public String load() {
        String rawData = dataSource.readData();
        return "Parsed user from: " + rawData;
    }
}

public class ProductService extends DataService {
    public ProductService(DataSource dataSource) {
        super(dataSource);
    }

    @Override
    public void save(String data) {
        String formattedData = "Product: " + data;
        dataSource.writeData(formattedData);
    }

    @Override
    public String load() {
        String rawData = dataSource.readData();
        return "Parsed product from: " + rawData;
    }
}

// Usage
public class BridgeExample {
    public static void main(String[] args) {
        // User service with database
        DataSource database = new DatabaseSource();
        DataService userService = new UserService(database);
        userService.save("John Doe");
        System.out.println(userService.load());

        // Product service with file
        DataSource file = new FileSource();
        DataService productService = new ProductService(file);
        productService.save("Widget");
        System.out.println(productService.load());
    }
}
```

### When to Use

Use Bridge when:
- You want to avoid permanent binding between abstraction and implementation
- Both abstractions and implementations should be extensible by subclassing
- Changes in implementation shouldn't impact clients
- You want to share implementation among multiple objects
- You have proliferation of classes from coupled interface and implementations

**Common Use Cases**:
- UI frameworks (platform-independent abstractions)
- Device drivers (abstract devices with platform-specific implementations)
- Database drivers (abstract queries with database-specific implementations)
- Graphics rendering (shapes with rendering-method implementations)

### When NOT to Use

Avoid Bridge when:
- Single implementation exists and is unlikely to vary
- Abstraction and implementation are closely tied
- Simpler inheritance hierarchy suffices
- Added complexity isn't justified

### Real-World Examples

**Cross-Platform UI**:
```python
# Shape abstraction can work with any renderer
vector_circle = Circle(VectorRenderer(), 5)
raster_circle = Circle(RasterRenderer(), 5)
```

**Message Sending**:
```typescript
// Message types work with any sender
const emailMessage = new TextMessage(emailSender, "Hello");
const smsMessage = new TextMessage(smsSender, "Hello");
```

**Data Services**:
```java
// Services can use any data source
UserService userService = new UserService(new DatabaseSource());
ProductService productService = new ProductService(new FileSource());
```

### Related Patterns

- **Adapter**: Makes incompatible interfaces work together; Bridge separates abstraction from implementation
- **Abstract Factory**: Can create and configure particular Bridge
- **Strategy**: Similar structure but different intent (algorithms vs implementations)

---

## 8. Composite Pattern

### Intent

Compose objects into tree structures to represent part-whole hierarchies. Composite lets clients treat individual objects and compositions of objects uniformly.

### Problem

How do you represent hierarchical structures where individual objects and groups of objects should be treated the same way? For example:
- **File systems**: Files and folders (folders contain files or other folders)
- **Organization charts**: Employees and departments
- **UI components**: Widgets and containers (containers hold widgets or other containers)
- **Graphics**: Shapes and shape groups

Without a pattern, client code must distinguish between simple and complex objects, leading to conditional logic throughout.

### Solution

Define a unified interface for both simple (leaf) and complex (composite) objects. Composite objects store child components and delegate operations to them. Clients interact with all objects through the common interface, treating individuals and composites uniformly.

### Structure

**Key Participants**:
- **Component**: Declares interface for objects in composition; implements default behavior
- **Leaf**: Represents leaf objects (no children); defines behavior for primitive objects
- **Composite**: Defines behavior for components with children; stores child components; implements child-related operations
- **Client**: Manipulates objects through Component interface

### Implementation

#### Python Implementation

```python
# Composite Pattern

from abc import ABC, abstractmethod
from typing import List

# Component
class FileSystemComponent(ABC):
    """Abstract component for file system elements."""

    def __init__(self, name: str):
        self.name = name

    @abstractmethod
    def get_size(self) -> int:
        """Get size in bytes."""
        pass

    @abstractmethod
    def display(self, indent: int = 0) -> str:
        """Display structure with indentation."""
        pass

    def add(self, component: 'FileSystemComponent') -> None:
        """Add child component (only for composites)."""
        raise NotImplementedError("Cannot add to leaf")

    def remove(self, component: 'FileSystemComponent') -> None:
        """Remove child component (only for composites)."""
        raise NotImplementedError("Cannot remove from leaf")

    def get_children(self) -> List['FileSystemComponent']:
        """Get child components (only for composites)."""
        return []

# Leaf
class File(FileSystemComponent):
    """Leaf component representing a file."""

    def __init__(self, name: str, size: int):
        super().__init__(name)
        self.size = size

    def get_size(self) -> int:
        return self.size

    def display(self, indent: int = 0) -> str:
        return " " * indent + f"📄 {self.name} ({self.size} bytes)"

# Composite
class Directory(FileSystemComponent):
    """Composite component representing a directory."""

    def __init__(self, name: str):
        super().__init__(name)
        self._children: List[FileSystemComponent] = []

    def add(self, component: FileSystemComponent) -> None:
        """Add file or subdirectory."""
        self._children.append(component)

    def remove(self, component: FileSystemComponent) -> None:
        """Remove file or subdirectory."""
        self._children.remove(component)

    def get_children(self) -> List[FileSystemComponent]:
        return self._children

    def get_size(self) -> int:
        """Total size is sum of all children."""
        return sum(child.get_size() for child in self._children)

    def display(self, indent: int = 0) -> str:
        """Display directory tree."""
        result = " " * indent + f"📁 {self.name}/ ({self.get_size()} bytes total)\n"
        for child in self._children:
            result += child.display(indent + 2) + "\n"
        return result.rstrip()

# Usage
# Build file system structure
root = Directory("root")

documents = Directory("documents")
documents.add(File("resume.pdf", 50000))
documents.add(File("cover_letter.docx", 25000))

photos = Directory("photos")
photos.add(File("vacation.jpg", 2000000))
photos.add(File("family.png", 1500000))

root.add(documents)
root.add(photos)
root.add(File("readme.txt", 1000))

# Treat all components uniformly
print(root.display())
print(f"\nTotal size: {root.get_size()} bytes")

# Practical Example: Organization Hierarchy
class OrganizationComponent(ABC):
    """Component for organization structure."""

    def __init__(self, name: str):
        self.name = name

    @abstractmethod
    def get_salary_total(self) -> float:
        pass

    @abstractmethod
    def get_employee_count(self) -> int:
        pass

    @abstractmethod
    def display(self, indent: int = 0) -> str:
        pass

class Employee(OrganizationComponent):
    """Leaf: Individual employee."""

    def __init__(self, name: str, position: str, salary: float):
        super().__init__(name)
        self.position = position
        self.salary = salary

    def get_salary_total(self) -> float:
        return self.salary

    def get_employee_count(self) -> int:
        return 1

    def display(self, indent: int = 0) -> str:
        return " " * indent + f"👤 {self.name} - {self.position} (${self.salary:,.2f})"

class Department(OrganizationComponent):
    """Composite: Department containing employees/subdepartments."""

    def __init__(self, name: str):
        super().__init__(name)
        self._members: List[OrganizationComponent] = []

    def add(self, component: OrganizationComponent) -> None:
        self._members.append(component)

    def remove(self, component: OrganizationComponent) -> None:
        self._members.remove(component)

    def get_salary_total(self) -> float:
        return sum(member.get_salary_total() for member in self._members)

    def get_employee_count(self) -> int:
        return sum(member.get_employee_count() for member in self._members)

    def display(self, indent: int = 0) -> str:
        result = " " * indent + f"🏢 {self.name} Department ({self.get_employee_count()} employees, ${self.get_salary_total():,.2f} total)\n"
        for member in self._members:
            result += member.display(indent + 2) + "\n"
        return result.rstrip()

# Build organization structure
company = Department("Company")

engineering = Department("Engineering")
engineering.add(Employee("Alice", "Senior Engineer", 120000))
engineering.add(Employee("Bob", "Junior Engineer", 80000))

sales = Department("Sales")
sales.add(Employee("Charlie", "Sales Manager", 90000))
sales.add(Employee("Diana", "Sales Rep", 60000))

company.add(engineering)
company.add(sales)
company.add(Employee("Eve", "CEO", 200000))

print(company.display())
print(f"\nTotal payroll: ${company.get_salary_total():,.2f}")
```

#### TypeScript Implementation

```typescript
// Composite Pattern

// Component
abstract class UIComponent {
    constructor(public name: string) {}

    abstract render(): string;
    abstract getComponentCount(): number;

    // Default implementations for composite operations
    add(component: UIComponent): void {
        throw new Error("Cannot add to leaf component");
    }

    remove(component: UIComponent): void {
        throw new Error("Cannot remove from leaf component");
    }

    getChildren(): UIComponent[] {
        return [];
    }
}

// Leaf Components
class Button extends UIComponent {
    constructor(name: string, private label: string) {
        super(name);
    }

    render(): string {
        return `<button>${this.label}</button>`;
    }

    getComponentCount(): number {
        return 1;
    }
}

class TextInput extends UIComponent {
    constructor(name: string, private placeholder: string) {
        super(name);
    }

    render(): string {
        return `<input type="text" placeholder="${this.placeholder}" />`;
    }

    getComponentCount(): number {
        return 1;
    }
}

class Label extends UIComponent {
    constructor(name: string, private text: string) {
        super(name);
    }

    render(): string {
        return `<label>${this.text}</label>`;
    }

    getComponentCount(): number {
        return 1;
    }
}

// Composite Components
class Panel extends UIComponent {
    private children: UIComponent[] = [];

    constructor(name: string, private cssClass: string = "") {
        super(name);
    }

    add(component: UIComponent): void {
        this.children.push(component);
    }

    remove(component: UIComponent): void {
        const index = this.children.indexOf(component);
        if (index !== -1) {
            this.children.splice(index, 1);
        }
    }

    getChildren(): UIComponent[] {
        return this.children;
    }

    render(): string {
        const childrenHtml = this.children.map(child => child.render()).join("\n  ");
        const classAttr = this.cssClass ? ` class="${this.cssClass}"` : "";
        return `<div${classAttr}>\n  ${childrenHtml}\n</div>`;
    }

    getComponentCount(): number {
        return 1 + this.children.reduce((sum, child) => sum + child.getComponentCount(), 0);
    }
}

class Form extends UIComponent {
    private children: UIComponent[] = [];

    constructor(name: string, private action: string) {
        super(name);
    }

    add(component: UIComponent): void {
        this.children.push(component);
    }

    remove(component: UIComponent): void {
        const index = this.children.indexOf(component);
        if (index !== -1) {
            this.children.splice(index, 1);
        }
    }

    getChildren(): UIComponent[] {
        return this.children;
    }

    render(): string {
        const childrenHtml = this.children.map(child => child.render()).join("\n  ");
        return `<form action="${this.action}">\n  ${childrenHtml}\n</form>`;
    }

    getComponentCount(): number {
        return 1 + this.children.reduce((sum, child) => sum + child.getComponentCount(), 0);
    }
}

// Usage: Build UI component tree
const loginForm = new Form("loginForm", "/login");

const usernamePanel = new Panel("usernamePanel", "form-group");
usernamePanel.add(new Label("usernameLabel", "Username:"));
usernamePanel.add(new TextInput("usernameInput", "Enter username"));

const passwordPanel = new Panel("passwordPanel", "form-group");
passwordPanel.add(new Label("passwordLabel", "Password:"));
passwordPanel.add(new TextInput("passwordInput", "Enter password"));

const buttonPanel = new Panel("buttonPanel", "form-actions");
buttonPanel.add(new Button("submitBtn", "Login"));
buttonPanel.add(new Button("cancelBtn", "Cancel"));

loginForm.add(usernamePanel);
loginForm.add(passwordPanel);
loginForm.add(buttonPanel);

// Render entire component tree
console.log(loginForm.render());
console.log(`\nTotal components: ${loginForm.getComponentCount()}`);
```

#### Java Implementation

```java
// Composite Pattern

import java.util.ArrayList;
import java.util.List;

// Component
public abstract class GraphicElement {
    protected String name;

    public GraphicElement(String name) {
        this.name = name;
    }

    public abstract void draw(int indent);
    public abstract double getArea();

    // Default implementations for composite operations
    public void add(GraphicElement element) {
        throw new UnsupportedOperationException("Cannot add to leaf");
    }

    public void remove(GraphicElement element) {
        throw new UnsupportedOperationException("Cannot remove from leaf");
    }

    public List<GraphicElement> getChildren() {
        return new ArrayList<>();
    }

    protected String getIndent(int indent) {
        return "  ".repeat(indent);
    }
}

// Leaf: Circle
public class Circle extends GraphicElement {
    private double radius;

    public Circle(String name, double radius) {
        super(name);
        this.radius = radius;
    }

    @Override
    public void draw(int indent) {
        System.out.println(getIndent(indent) + "○ Circle: " + name +
                          " (radius: " + radius + ")");
    }

    @Override
    public double getArea() {
        return Math.PI * radius * radius;
    }
}

// Leaf: Rectangle
public class Rectangle extends GraphicElement {
    private double width;
    private double height;

    public Rectangle(String name, double width, double height) {
        super(name);
        this.width = width;
        this.height = height;
    }

    @Override
    public void draw(int indent) {
        System.out.println(getIndent(indent) + "□ Rectangle: " + name +
                          " (" + width + "x" + height + ")");
    }

    @Override
    public double getArea() {
        return width * height;
    }
}

// Composite: Group
public class GraphicGroup extends GraphicElement {
    private List<GraphicElement> children = new ArrayList<>();

    public GraphicGroup(String name) {
        super(name);
    }

    @Override
    public void add(GraphicElement element) {
        children.add(element);
    }

    @Override
    public void remove(GraphicElement element) {
        children.remove(element);
    }

    @Override
    public List<GraphicElement> getChildren() {
        return new ArrayList<>(children);
    }

    @Override
    public void draw(int indent) {
        System.out.println(getIndent(indent) + "📦 Group: " + name +
                          " (total area: " + String.format("%.2f", getArea()) + ")");
        for (GraphicElement child : children) {
            child.draw(indent + 1);
        }
    }

    @Override
    public double getArea() {
        return children.stream()
                       .mapToDouble(GraphicElement::getArea)
                       .sum();
    }
}

// Usage
public class CompositeExample {
    public static void main(String[] args) {
        // Create individual shapes
        Circle smallCircle = new Circle("Small Circle", 5);
        Circle largeCircle = new Circle("Large Circle", 10);
        Rectangle rect1 = new Rectangle("Rect1", 10, 20);
        Rectangle rect2 = new Rectangle("Rect2", 5, 15);

        // Create composite groups
        GraphicGroup group1 = new GraphicGroup("Group 1");
        group1.add(smallCircle);
        group1.add(rect1);

        GraphicGroup group2 = new GraphicGroup("Group 2");
        group2.add(largeCircle);
        group2.add(rect2);

        // Create top-level composite
        GraphicGroup drawing = new GraphicGroup("Complete Drawing");
        drawing.add(group1);
        drawing.add(group2);

        // Treat all elements uniformly
        drawing.draw(0);
        System.out.printf("\nTotal area of drawing: %.2f%n", drawing.getArea());
    }
}
```

### When to Use

Use Composite when:
- You want to represent part-whole hierarchies of objects
- You want clients to ignore difference between compositions of objects and individual objects
- Structure can be represented as a tree
- Operations should work uniformly on both leaf and composite objects

**Common Use Cases**:
- File systems (files and directories)
- GUI component hierarchies (widgets and containers)
- Organization structures (employees and departments)
- Graphics systems (shapes and groups)
- Document structures (paragraphs, sections, chapters)
- Menu systems (menu items and submenus)

### When NOT to Use

Avoid Composite when:
- Your hierarchy is flat (no nesting needed)
- Operations differ significantly between leaf and composite objects
- Type safety requires distinguishing between simple and composite objects
- Overhead of uniform interface isn't justified

### Real-World Examples

**File System**:
```python
# Files and directories treated uniformly
root = Directory("root")
root.add(File("readme.txt", 1000))
root.add(Directory("subdirectory"))
print(f"Total size: {root.get_size()}")
```

**UI Components**:
```typescript
// Widgets and containers use same interface
form.add(new Panel("panel1"));
form.add(new Button("submitBtn", "Submit"));
console.log(form.render());
```

**Graphics**:
```java
// Individual shapes and groups share common interface
drawing.add(new Circle("circle1", 5));
drawing.add(new GraphicGroup("group1"));
drawing.draw(0);
```

### Related Patterns

- **Iterator**: Often used to traverse Composite structures
- **Visitor**: Can apply operations to Composite structures
- **Decorator**: Often combined with Composite (decorators wrap composites)
- **Chain of Responsibility**: Can use Composite structure to pass requests

### SOLID Principles

**Open-Closed Principle**: New component types can be added without modifying existing code

**Liskov Substitution Principle**: Leaf and Composite objects are substitutable through Component interface

**Single Responsibility Principle**: Each component type has one reason to change

---

## 9. Decorator Pattern

### Intent

Attach additional responsibilities to an object dynamically. Decorators provide a flexible alternative to subclassing for extending functionality.

### Problem

How do you add responsibilities to objects dynamically without affecting other objects of the same class? Subclassing creates static inheritance and can lead to class explosion. For example:
- **Stream processing**: Add compression, encryption, buffering to streams
- **UI components**: Add borders, scrollbars, shadows to windows
- **Text formatting**: Add bold, italic, underline to text

Subclassing every combination (BoldItalicUnderlineText, EncryptedCompressedBufferedStream) is unwieldy.

### Solution

Create decorator classes that wrap the original object. Decorators implement the same interface as the component they decorate and add their own behavior before/after delegating to the wrapped object. Multiple decorators can be stacked.

### Structure

**Key Participants**:
- **Component**: Defines interface for objects that can have responsibilities added
- **ConcreteComponent**: Defines object to which responsibilities can be attached
- **Decorator**: Maintains reference to Component and defines interface conforming to Component
- **ConcreteDecorator**: Adds responsibilities to the component

### Implementation

#### Python Implementation

```python
# Decorator Pattern

from abc import ABC, abstractmethod

# Component Interface
class DataSource(ABC):
    """Interface for reading and writing data."""

    @abstractmethod
    def write_data(self, data: str) -> None:
        pass

    @abstractmethod
    def read_data(self) -> str:
        pass

# Concrete Component
class FileDataSource(DataSource):
    """Concrete component: basic file operations."""

    def __init__(self, filename: str):
        self.filename = filename
        self._data = ""

    def write_data(self, data: str) -> None:
        """Write data to file."""
        self._data = data
        print(f"Writing to file {self.filename}: {data}")

    def read_data(self) -> str:
        """Read data from file."""
        print(f"Reading from file {self.filename}")
        return self._data

# Base Decorator
class DataSourceDecorator(DataSource):
    """Base decorator wrapping a data source."""

    def __init__(self, source: DataSource):
        self._wrapped = source

    def write_data(self, data: str) -> None:
        self._wrapped.write_data(data)

    def read_data(self) -> str:
        return self._wrapped.read_data()

# Concrete Decorators
class EncryptionDecorator(DataSourceDecorator):
    """Decorator adding encryption."""

    def write_data(self, data: str) -> None:
        """Encrypt before writing."""
        encrypted = self._encrypt(data)
        print(f"[Encryption] Encrypting data: {data} → {encrypted}")
        super().write_data(encrypted)

    def read_data(self) -> str:
        """Decrypt after reading."""
        encrypted = super().read_data()
        decrypted = self._decrypt(encrypted)
        print(f"[Encryption] Decrypting data: {encrypted} → {decrypted}")
        return decrypted

    def _encrypt(self, data: str) -> str:
        """Simple encryption (reverse string)."""
        return data[::-1]

    def _decrypt(self, data: str) -> str:
        """Simple decryption (reverse string)."""
        return data[::-1]

class CompressionDecorator(DataSourceDecorator):
    """Decorator adding compression."""

    def write_data(self, data: str) -> None:
        """Compress before writing."""
        compressed = self._compress(data)
        print(f"[Compression] Compressing data: {len(data)} → {len(compressed)} bytes")
        super().write_data(compressed)

    def read_data(self) -> str:
        """Decompress after reading."""
        compressed = super().read_data()
        decompressed = self._decompress(compressed)
        print(f"[Compression] Decompressing data: {len(compressed)} → {len(decompressed)} bytes")
        return decompressed

    def _compress(self, data: str) -> str:
        """Simple compression (remove spaces)."""
        return data.replace(" ", "")

    def _decompress(self, data: str) -> str:
        """Simple decompression (add spaces back - simplified)."""
        return data  # Simplified for demo

class LoggingDecorator(DataSourceDecorator):
    """Decorator adding logging."""

    def write_data(self, data: str) -> None:
        """Log write operation."""
        print(f"[Logging] Writing data at timestamp: 2024-01-01 12:00:00")
        super().write_data(data)
        print(f"[Logging] Write completed successfully")

    def read_data(self) -> str:
        """Log read operation."""
        print(f"[Logging] Reading data at timestamp: 2024-01-01 12:00:01")
        result = super().read_data()
        print(f"[Logging] Read completed successfully")
        return result

# Usage: Stack multiple decorators
print("=== Simple File Write ===")
simple_source = FileDataSource("data.txt")
simple_source.write_data("Hello World")

print("\n=== Encrypted File Write ===")
encrypted_source = EncryptionDecorator(FileDataSource("encrypted.txt"))
encrypted_source.write_data("Hello World")

print("\n=== Compressed + Encrypted + Logged File Write ===")
# Stack decorators: Logging → Compression → Encryption → File
stacked_source = LoggingDecorator(
    CompressionDecorator(
        EncryptionDecorator(
            FileDataSource("secure.txt")
        )
    )
)
stacked_source.write_data("Hello World")
print("\n=== Reading Back ===")
data = stacked_source.read_data()
print(f"Final data: {data}")

# Practical Example: Coffee Shop
class Beverage(ABC):
    """Component: Beverage interface."""

    @abstractmethod
    def get_description(self) -> str:
        pass

    @abstractmethod
    def cost(self) -> float:
        pass

class Coffee(Beverage):
    """Concrete component: Basic coffee."""

    def get_description(self) -> str:
        return "Coffee"

    def cost(self) -> float:
        return 2.00

class Tea(Beverage):
    """Concrete component: Basic tea."""

    def get_description(self) -> str:
        return "Tea"

    def cost(self) -> float:
        return 1.50

# Base decorator
class BeverageDecorator(Beverage):
    """Base decorator for beverages."""

    def __init__(self, beverage: Beverage):
        self._beverage = beverage

    def get_description(self) -> str:
        return self._beverage.get_description()

    def cost(self) -> float:
        return self._beverage.cost()

# Concrete decorators
class Milk(BeverageDecorator):
    """Add milk."""

    def get_description(self) -> str:
        return self._beverage.get_description() + ", Milk"

    def cost(self) -> float:
        return self._beverage.cost() + 0.50

class Sugar(BeverageDecorator):
    """Add sugar."""

    def get_description(self) -> str:
        return self._beverage.get_description() + ", Sugar"

    def cost(self) -> float:
        return self._beverage.cost() + 0.25

class WhippedCream(BeverageDecorator):
    """Add whipped cream."""

    def get_description(self) -> str:
        return self._beverage.get_description() + ", Whipped Cream"

    def cost(self) -> float:
        return self._beverage.cost() + 0.75

# Order coffee with add-ons
print("\n=== Coffee Shop Orders ===")
order1 = Coffee()
print(f"{order1.get_description()}: ${order1.cost():.2f}")

order2 = Milk(Sugar(Coffee()))
print(f"{order2.get_description()}: ${order2.cost():.2f}")

order3 = WhippedCream(Milk(Sugar(Coffee())))
print(f"{order3.get_description()}: ${order3.cost():.2f}")
```

#### TypeScript Implementation

```typescript
// Decorator Pattern

// Component Interface
interface TextFormatter {
    format(text: string): string;
}

// Concrete Component
class PlainText implements TextFormatter {
    format(text: string): string {
        return text;
    }
}

// Base Decorator
abstract class TextDecorator implements TextFormatter {
    constructor(protected wrapped: TextFormatter) {}

    format(text: string): string {
        return this.wrapped.format(text);
    }
}

// Concrete Decorators
class BoldDecorator extends TextDecorator {
    format(text: string): string {
        const wrapped = super.format(text);
        return `<b>${wrapped}</b>`;
    }
}

class ItalicDecorator extends TextDecorator {
    format(text: string): string {
        const wrapped = super.format(text);
        return `<i>${wrapped}</i>`;
    }
}

class UnderlineDecorator extends TextDecorator {
    format(text: string): string {
        const wrapped = super.format(text);
        return `<u>${wrapped}</u>`;
    }
}

class ColorDecorator extends TextDecorator {
    constructor(wrapped: TextFormatter, private color: string) {
        super(wrapped);
    }

    format(text: string): string {
        const wrapped = super.format(text);
        return `<span style="color:${this.color}">${wrapped}</span>`;
    }
}

// Usage: Stack text formatters
const plainText = new PlainText();
console.log(plainText.format("Hello"));
// Output: Hello

const boldText = new BoldDecorator(plainText);
console.log(boldText.format("Hello"));
// Output: <b>Hello</b>

const boldItalicText = new ItalicDecorator(new BoldDecorator(plainText));
console.log(boldItalicText.format("Hello"));
// Output: <i><b>Hello</b></i>

const fancyText = new ColorDecorator(
    new UnderlineDecorator(
        new ItalicDecorator(
            new BoldDecorator(plainText)
        )
    ),
    "red"
);
console.log(fancyText.format("Hello"));
// Output: <span style="color:red"><u><i><b>Hello</b></i></u></span>

// Practical Example: Notification System
interface Notifier {
    send(message: string): void;
}

class EmailNotifier implements Notifier {
    constructor(private email: string) {}

    send(message: string): void {
        console.log(`Sending email to ${this.email}: ${message}`);
    }
}

abstract class NotifierDecorator implements Notifier {
    constructor(protected notifier: Notifier) {}

    send(message: string): void {
        this.notifier.send(message);
    }
}

class SMSDecorator extends NotifierDecorator {
    constructor(notifier: Notifier, private phone: string) {
        super(notifier);
    }

    send(message: string): void {
        super.send(message);
        console.log(`Sending SMS to ${this.phone}: ${message}`);
    }
}

class SlackDecorator extends NotifierDecorator {
    constructor(notifier: Notifier, private channel: string) {
        super(notifier);
    }

    send(message: string): void {
        super.send(message);
        console.log(`Posting to Slack channel ${this.channel}: ${message}`);
    }
}

// Send notification through multiple channels
const baseNotifier = new EmailNotifier("user@example.com");
const multiChannelNotifier = new SlackDecorator(
    new SMSDecorator(baseNotifier, "+1234567890"),
    "#alerts"
);

multiChannelNotifier.send("Server is down!");
// Output:
// Sending email to user@example.com: Server is down!
// Sending SMS to +1234567890: Server is down!
// Posting to Slack channel #alerts: Server is down!
```

#### Java Implementation

```java
// Decorator Pattern

// Component Interface
public interface InputStream {
    int read();
    void close();
}

// Concrete Component
public class FileInputStream implements InputStream {
    private String filename;

    public FileInputStream(String filename) {
        this.filename = filename;
        System.out.println("Opening file: " + filename);
    }

    @Override
    public int read() {
        System.out.println("Reading from file: " + filename);
        return 65; // Return 'A' for demo
    }

    @Override
    public void close() {
        System.out.println("Closing file: " + filename);
    }
}

// Base Decorator
public abstract class InputStreamDecorator implements InputStream {
    protected InputStream wrapped;

    public InputStreamDecorator(InputStream stream) {
        this.wrapped = stream;
    }

    @Override
    public int read() {
        return wrapped.read();
    }

    @Override
    public void close() {
        wrapped.close();
    }
}

// Concrete Decorators
public class BufferedInputStream extends InputStreamDecorator {
    private static final int BUFFER_SIZE = 1024;

    public BufferedInputStream(InputStream stream) {
        super(stream);
        System.out.println("Adding buffering capability");
    }

    @Override
    public int read() {
        System.out.println("[Buffer] Reading with buffer (size: " + BUFFER_SIZE + ")");
        return super.read();
    }
}

public class GZIPInputStream extends InputStreamDecorator {
    public GZIPInputStream(InputStream stream) {
        super(stream);
        System.out.println("Adding GZIP decompression");
    }

    @Override
    public int read() {
        int compressed = super.read();
        System.out.println("[GZIP] Decompressing data");
        return compressed; // Decompressed data
    }
}

public class DataInputStream extends InputStreamDecorator {
    public DataInputStream(InputStream stream) {
        super(stream);
        System.out.println("Adding data conversion capability");
    }

    @Override
    public int read() {
        int data = super.read();
        System.out.println("[Data] Converting byte to readable format");
        return data;
    }

    public String readString() {
        int data = read();
        return Character.toString((char) data);
    }
}

// Usage
public class DecoratorExample {
    public static void main(String[] args) {
        System.out.println("=== Simple File Read ===");
        InputStream simpleStream = new FileInputStream("data.txt");
        System.out.println("Data: " + simpleStream.read());
        simpleStream.close();

        System.out.println("\n=== Buffered File Read ===");
        InputStream bufferedStream = new BufferedInputStream(
            new FileInputStream("data.txt")
        );
        System.out.println("Data: " + bufferedStream.read());
        bufferedStream.close();

        System.out.println("\n=== Buffered + Compressed File Read ===");
        InputStream compressedStream = new BufferedInputStream(
            new GZIPInputStream(
                new FileInputStream("data.gz")
            )
        );
        System.out.println("Data: " + compressedStream.read());
        compressedStream.close();

        System.out.println("\n=== Full Stack: Data + Buffer + GZIP ===");
        DataInputStream fullStream = new DataInputStream(
            new BufferedInputStream(
                new GZIPInputStream(
                    new FileInputStream("data.gz")
                )
            )
        );
        System.out.println("String data: " + fullStream.readString());
        fullStream.close();
    }
}
```

### When to Use

Use Decorator when:
- You want to add responsibilities to objects dynamically and transparently
- Responsibilities can be withdrawn
- Extension by subclassing is impractical (would create too many subclasses)
- You need flexible combination of features
- You want to keep class hierarchies small

**Common Use Cases**:
- Stream/IO wrappers (buffering, compression, encryption)
- UI component enhancement (borders, scrollbars, shadows)
- Text/HTML formatting (bold, italic, color)
- Notification systems (multiple channels)
- Authentication/authorization layers
- Caching layers

### When NOT to Use

Avoid Decorator when:
- Simple subclassing suffices
- Object identity is important (decorators create different objects)
- Performance overhead of delegation is unacceptable
- Interface has many methods (decorators must implement all)

### Real-World Examples

**Stream Processing**:
```python
# Stack decorators for stream processing
stream = LoggingDecorator(CompressionDecorator(EncryptionDecorator(FileDataSource("file.txt"))))
stream.write_data("data")
```

**Text Formatting**:
```typescript
// Stack formatters for text styling
const formatted = new ColorDecorator(new ItalicDecorator(new BoldDecorator(plainText)), "red");
console.log(formatted.format("Hello"));
```

**Java I/O Streams**:
```java
// Real Java streams use Decorator pattern
InputStream stream = new DataInputStream(new BufferedInputStream(new GZIPInputStream(new FileInputStream("file.gz"))));
```

### Related Patterns

- **Adapter**: Changes interface; Decorator enhances responsibilities
- **Composite**: Decorator can be viewed as degenerate composite with one child
- **Strategy**: Changes object's guts; Decorator changes skin
- **Proxy**: Provides same interface with access control; Decorator adds responsibilities

### SOLID Principles

**Single Responsibility Principle**: Each decorator adds one specific responsibility

**Open-Closed Principle**: New decorators can be added without modifying existing code

**Dependency Inversion Principle**: Decorators depend on component abstraction, not concrete classes

---

## 10. Facade Pattern

### Intent

Provide a unified interface to a set of interfaces in a subsystem. Facade defines a higher-level interface that makes the subsystem easier to use.

### Problem

How do you simplify access to a complex subsystem with many interdependent classes? Direct interaction requires:
- Understanding many classes and their relationships
- Correct initialization and sequencing
- Handling complexity in every client

For example, a home theater system has DVD player, projector, amplifier, lights, screen, and popcorn maker—each with their own interface.

### Solution

Create a facade class that provides simple methods for common tasks, hiding the complexity of the subsystem behind a clean interface. Clients interact with the facade rather than subsystem classes directly.

### Structure

**Key Participants**:
- **Facade**: Knows which subsystem classes handle requests; delegates client requests to appropriate subsystem objects
- **Subsystem Classes**: Implement subsystem functionality; handle work assigned by Facade; have no knowledge of Facade

### Implementation

#### Python Implementation

```python
# Facade Pattern

# Complex subsystem classes
class DVDPlayer:
    """Subsystem component: DVD Player."""

    def on(self) -> str:
        return "DVD Player: Turning on"

    def play(self, movie: str) -> str:
        return f"DVD Player: Playing '{movie}'"

    def stop(self) -> str:
        return "DVD Player: Stopping"

    def off(self) -> str:
        return "DVD Player: Turning off"

class Projector:
    """Subsystem component: Projector."""

    def on(self) -> str:
        return "Projector: Turning on"

    def set_input(self, source: str) -> str:
        return f"Projector: Setting input to {source}"

    def wide_screen_mode(self) -> str:
        return "Projector: Setting wide screen mode"

    def off(self) -> str:
        return "Projector: Turning off"

class Amplifier:
    """Subsystem component: Amplifier."""

    def on(self) -> str:
        return "Amplifier: Turning on"

    def set_dvd(self, dvd: DVDPlayer) -> str:
        return "Amplifier: Setting DVD player as source"

    def set_volume(self, level: int) -> str:
        return f"Amplifier: Setting volume to {level}"

    def off(self) -> str:
        return "Amplifier: Turning off"

class Lights:
    """Subsystem component: Theater Lights."""

    def dim(self, level: int) -> str:
        return f"Lights: Dimming to {level}%"

    def on(self) -> str:
        return "Lights: Turning on full brightness"

class Screen:
    """Subsystem component: Projector Screen."""

    def down(self) -> str:
        return "Screen: Lowering screen"

    def up(self) -> str:
        return "Screen: Raising screen"

class PopcornMaker:
    """Subsystem component: Popcorn Maker."""

    def on(self) -> str:
        return "Popcorn Maker: Turning on"

    def pop(self) -> str:
        return "Popcorn Maker: Popping popcorn"

    def off(self) -> str:
        return "Popcorn Maker: Turning off"

# Facade
class HomeTheaterFacade:
    """Facade providing simple interface to complex home theater system."""

    def __init__(
        self,
        dvd: DVDPlayer,
        projector: Projector,
        amp: Amplifier,
        lights: Lights,
        screen: Screen,
        popcorn: PopcornMaker
    ):
        self.dvd = dvd
        self.projector = projector
        self.amp = amp
        self.lights = lights
        self.screen = screen
        self.popcorn = popcorn

    def watch_movie(self, movie: str) -> None:
        """Simple method orchestrating complex subsystem."""
        print("Get ready to watch a movie...")
        print(self.popcorn.on())
        print(self.popcorn.pop())
        print(self.lights.dim(10))
        print(self.screen.down())
        print(self.projector.on())
        print(self.projector.set_input("DVD"))
        print(self.projector.wide_screen_mode())
        print(self.amp.on())
        print(self.amp.set_dvd(self.dvd))
        print(self.amp.set_volume(5))
        print(self.dvd.on())
        print(self.dvd.play(movie))

    def end_movie(self) -> None:
        """Simple method to shut down system."""
        print("\nShutting down movie theater...")
        print(self.popcorn.off())
        print(self.dvd.stop())
        print(self.dvd.off())
        print(self.amp.off())
        print(self.projector.off())
        print(self.screen.up())
        print(self.lights.on())

# Usage: Simple facade interface vs complex subsystem
# Without facade (complex):
# dvd = DVDPlayer()
# projector = Projector()
# ...
# popcorn.on()
# popcorn.pop()
# lights.dim(10)
# ...

# With facade (simple):
dvd = DVDPlayer()
projector = Projector()
amp = Amplifier()
lights = Lights()
screen = Screen()
popcorn = PopcornMaker()

home_theater = HomeTheaterFacade(dvd, projector, amp, lights, screen, popcorn)
home_theater.watch_movie("The Matrix")
home_theater.end_movie()

# Practical Example: Computer Startup Facade
class CPU:
    """Subsystem: CPU."""

    def freeze(self) -> str:
        return "CPU: Freezing"

    def jump(self, position: int) -> str:
        return f"CPU: Jumping to position {position}"

    def execute(self) -> str:
        return "CPU: Executing instructions"

class Memory:
    """Subsystem: Memory."""

    def load(self, position: int, data: str) -> str:
        return f"Memory: Loading '{data}' at position {position}"

class HardDrive:
    """Subsystem: Hard Drive."""

    def read(self, sector: int, size: int) -> str:
        return f"HardDrive: Reading {size} bytes from sector {sector}"

class ComputerFacade:
    """Facade for computer startup process."""

    def __init__(self):
        self.cpu = CPU()
        self.memory = Memory()
        self.hard_drive = HardDrive()

    def start(self) -> None:
        """Simplified startup sequence."""
        print("Starting computer...")
        print(self.cpu.freeze())
        print(self.memory.load(0, "boot_loader"))
        print(self.hard_drive.read(0, 1024))
        print(self.cpu.jump(0))
        print(self.cpu.execute())
        print("Computer started successfully!")

# Simple usage
print("\n=== Computer Startup ===")
computer = ComputerFacade()
computer.start()
```

#### TypeScript Implementation

```typescript
// Facade Pattern

// Subsystem: Payment Gateway
class PaymentGateway {
    processPayment(amount: number, cardNumber: string): string {
        return `Payment Gateway: Processing $${amount} payment with card ${cardNumber}`;
    }

    refund(transactionId: string, amount: number): string {
        return `Payment Gateway: Refunding $${amount} for transaction ${transactionId}`;
    }
}

// Subsystem: Inventory System
class InventorySystem {
    checkStock(productId: string): boolean {
        console.log(`Inventory: Checking stock for product ${productId}`);
        return true; // In stock
    }

    reserveProduct(productId: string): string {
        return `Inventory: Reserved product ${productId}`;
    }

    releaseProduct(productId: string): string {
        return `Inventory: Released product ${productId}`;
    }
}

// Subsystem: Shipping Service
class ShippingService {
    calculateShipping(address: string): number {
        console.log(`Shipping: Calculating cost for ${address}`);
        return 10.00;
    }

    shipProduct(productId: string, address: string): string {
        return `Shipping: Shipping product ${productId} to ${address}`;
    }

    trackShipment(trackingNumber: string): string {
        return `Shipping: Tracking ${trackingNumber}`;
    }
}

// Subsystem: Notification Service
class NotificationService {
    sendEmail(email: string, message: string): string {
        return `Notification: Sent email to ${email}`;
    }

    sendSMS(phone: string, message: string): string {
        return `Notification: Sent SMS to ${phone}`;
    }
}

// Facade
class OrderFacade {
    private paymentGateway: PaymentGateway;
    private inventory: InventorySystem;
    private shipping: ShippingService;
    private notification: NotificationService;

    constructor() {
        this.paymentGateway = new PaymentGateway();
        this.inventory = new InventorySystem();
        this.shipping = new ShippingService();
        this.notification = new NotificationService();
    }

    placeOrder(
        productId: string,
        cardNumber: string,
        shippingAddress: string,
        customerEmail: string
    ): void {
        console.log("=== Processing Order ===");

        // Check inventory
        if (!this.inventory.checkStock(productId)) {
            console.log("Order failed: Product out of stock");
            return;
        }

        // Reserve product
        console.log(this.inventory.reserveProduct(productId));

        // Calculate shipping
        const shippingCost = this.shipping.calculateShipping(shippingAddress);
        const productPrice = 99.99;
        const totalCost = productPrice + shippingCost;

        // Process payment
        console.log(this.paymentGateway.processPayment(totalCost, cardNumber));

        // Ship product
        console.log(this.shipping.shipProduct(productId, shippingAddress));

        // Send confirmation
        console.log(this.notification.sendEmail(
            customerEmail,
            `Order confirmed! Total: $${totalCost}`
        ));

        console.log("Order placed successfully!");
    }

    cancelOrder(productId: string, transactionId: string, customerEmail: string): void {
        console.log("\n=== Canceling Order ===");

        // Release inventory
        console.log(this.inventory.releaseProduct(productId));

        // Refund payment
        console.log(this.paymentGateway.refund(transactionId, 109.99));

        // Notify customer
        console.log(this.notification.sendEmail(
            customerEmail,
            "Order canceled and refunded"
        ));

        console.log("Order canceled successfully!");
    }
}

// Usage: Simple facade interface hides complex subsystem
const orderSystem = new OrderFacade();

orderSystem.placeOrder(
    "PROD-123",
    "4111-1111-1111-1111",
    "123 Main St, City, State",
    "customer@example.com"
);

orderSystem.cancelOrder(
    "PROD-123",
    "TXN-456",
    "customer@example.com"
);
```

#### Java Implementation

```java
// Facade Pattern

// Subsystem: Database
class Database {
    public void connect() {
        System.out.println("Database: Connecting to database");
    }

    public void disconnect() {
        System.out.println("Database: Disconnecting from database");
    }

    public String query(String sql) {
        return "Database: Executing query: " + sql;
    }
}

// Subsystem: Cache
class Cache {
    public void connect() {
        System.out.println("Cache: Connecting to Redis");
    }

    public void disconnect() {
        System.out.println("Cache: Disconnecting from Redis");
    }

    public String get(String key) {
        return "Cache: Retrieved value for key: " + key;
    }

    public void set(String key, String value) {
        System.out.println("Cache: Cached " + key + " = " + value);
    }
}

// Subsystem: Logger
class Logger {
    public void log(String message) {
        System.out.println("Logger: " + message);
    }

    public void error(String message) {
        System.err.println("Logger ERROR: " + message);
    }
}

// Subsystem: Validator
class Validator {
    public boolean validateEmail(String email) {
        System.out.println("Validator: Validating email: " + email);
        return email.contains("@");
    }

    public boolean validatePassword(String password) {
        System.out.println("Validator: Validating password");
        return password.length() >= 8;
    }
}

// Facade
public class UserServiceFacade {
    private Database database;
    private Cache cache;
    private Logger logger;
    private Validator validator;

    public UserServiceFacade() {
        this.database = new Database();
        this.cache = new Cache();
        this.logger = new Logger();
        this.validator = new Validator();
    }

    public boolean registerUser(String email, String password, String name) {
        logger.log("Starting user registration for: " + email);

        // Validate inputs
        if (!validator.validateEmail(email)) {
            logger.error("Invalid email format");
            return false;
        }

        if (!validator.validatePassword(password)) {
            logger.error("Password too weak");
            return false;
        }

        // Connect to database
        database.connect();

        // Save user
        String sql = String.format(
            "INSERT INTO users (email, password, name) VALUES ('%s', '%s', '%s')",
            email, password, name
        );
        System.out.println(database.query(sql));

        database.disconnect();

        // Cache user data
        cache.connect();
        cache.set("user:" + email, name);
        cache.disconnect();

        logger.log("User registered successfully: " + email);
        return true;
    }

    public String getUser(String email) {
        logger.log("Fetching user: " + email);

        // Try cache first
        cache.connect();
        String cachedUser = cache.get("user:" + email);
        cache.disconnect();

        if (cachedUser != null && !cachedUser.equals("null")) {
            logger.log("User found in cache");
            return cachedUser;
        }

        // Fetch from database
        logger.log("Cache miss, querying database");
        database.connect();
        String result = database.query("SELECT * FROM users WHERE email = '" + email + "'");
        database.disconnect();

        // Update cache
        cache.connect();
        cache.set("user:" + email, result);
        cache.disconnect();

        logger.log("User fetched successfully");
        return result;
    }
}

// Usage
public class FacadeExample {
    public static void main(String[] args) {
        UserServiceFacade userService = new UserServiceFacade();

        System.out.println("=== Register User ===");
        boolean success = userService.registerUser(
            "user@example.com",
            "SecurePass123",
            "John Doe"
        );
        System.out.println("Registration success: " + success);

        System.out.println("\n=== Get User ===");
        String user = userService.getUser("user@example.com");
        System.out.println("User data: " + user);
    }
}
```

### When to Use

Use Facade when:
- You want to provide simple interface to complex subsystem
- There are many dependencies between clients and implementation classes
- You want to layer subsystems (each layer has a facade as entry point)
- You want to decouple subsystem from clients and other subsystems

**Common Use Cases**:
- API wrappers (simplify complex APIs)
- Library interfaces (hide internal complexity)
- Database access layers
- Order processing systems
- Computer startup sequences
- Home automation systems

### When NOT to Use

Avoid Facade when:
- Subsystem is already simple
- Clients need access to low-level subsystem features
- Facade would become complex coordinator
- One-to-one mapping between facade and subsystem methods

### Real-World Examples

**Home Theater**:
```python
# Simple facade hides complex subsystem orchestration
home_theater = HomeTheaterFacade(dvd, projector, amp, lights, screen, popcorn)
home_theater.watch_movie("The Matrix")
```

**E-commerce Order**:
```typescript
// Facade coordinates payment, inventory, shipping, notifications
const orderSystem = new OrderFacade();
orderSystem.placeOrder("PROD-123", "card", "address", "email");
```

**User Service**:
```java
// Facade manages database, cache, logging, validation
UserServiceFacade service = new UserServiceFacade();
service.registerUser("email", "password", "name");
```

### Related Patterns

- **Adapter**: Changes interface; Facade simplifies interface
- **Mediator**: Abstracts communication between colleagues; Facade abstracts subsystem interface
- **Abstract Factory**: Can be alternative to Facade to hide platform-specific classes
- **Singleton**: Facade objects are often Singletons

### SOLID Principles

**Single Responsibility Principle**: Facade has one reason to change—simplifying subsystem access

**Dependency Inversion Principle**: Clients depend on facade abstraction, not concrete subsystem classes

**Interface Segregation Principle**: Facade provides focused interface, hiding unnecessary subsystem complexity

---

## 11. Flyweight Pattern

### Intent

Use sharing to support large numbers of fine-grained objects efficiently. Flyweight minimizes memory use by sharing data among similar objects.

### Problem

How do you support large numbers of objects without excessive memory consumption? For example:
- **Text editor**: Millions of character objects
- **Game**: Thousands of particle objects (bullets, explosions)
- **Graphics**: Many similar icons or sprites

Creating individual objects for each instance wastes memory when many objects share common data.

### Solution

Separate object state into intrinsic (shared) and extrinsic (context-specific) state. Store intrinsic state in flyweight objects that can be shared. Pass extrinsic state to flyweight methods when needed. Use a factory to manage flyweight instances and ensure sharing.

### Structure

**Key Participants**:
- **Flyweight**: Declares interface through which flyweights receive and act on extrinsic state
- **ConcreteFlyweight**: Implements Flyweight interface and stores intrinsic state (shared)
- **FlyweightFactory**: Creates and manages flyweight objects; ensures flyweights are shared
- **Client**: Maintains references to flyweights; computes or stores extrinsic state

### Implementation

#### Python Implementation

```python
# Flyweight Pattern

from typing import Dict, Tuple

# Flyweight
class CharacterStyle:
    """Flyweight storing intrinsic character formatting state."""

    def __init__(self, font: str, size: int, color: str):
        # Intrinsic state (shared)
        self.font = font
        self.size = size
        self.color = color
        print(f"Creating CharacterStyle: {font}, {size}pt, {color}")

    def display(self, character: str, position: int) -> str:
        """Display character with extrinsic state (character, position)."""
        return f"[{character}] at position {position} - {self.font}, {self.size}pt, {self.color}"

# Flyweight Factory
class StyleFactory:
    """Factory managing flyweight instances."""

    def __init__(self):
        self._styles: Dict[Tuple[str, int, str], CharacterStyle] = {}

    def get_style(self, font: str, size: int, color: str) -> CharacterStyle:
        """Get or create flyweight for given style."""
        key = (font, size, color)

        if key not in self._styles:
            self._styles[key] = CharacterStyle(font, size, color)
        else:
            print(f"Reusing existing CharacterStyle: {font}, {size}pt, {color}")

        return self._styles[key]

    def get_style_count(self) -> int:
        """Get number of flyweight instances."""
        return len(self._styles)

# Client: Character in document
class Character:
    """Client that uses flyweight."""

    def __init__(self, char: str, position: int, style: CharacterStyle):
        # Extrinsic state (unique per character)
        self.char = char
        self.position = position
        # Intrinsic state (shared via flyweight)
        self.style = style

    def display(self) -> str:
        return self.style.display(self.char, self.position)

# Document using flyweights
class Document:
    """Document containing many characters sharing styles."""

    def __init__(self):
        self.characters = []
        self.style_factory = StyleFactory()

    def add_character(self, char: str, position: int, font: str, size: int, color: str):
        """Add character with style (reuses flyweights)."""
        style = self.style_factory.get_style(font, size, color)
        self.characters.append(Character(char, position, style))

    def display(self):
        """Display all characters."""
        for char in self.characters:
            print(char.display())

        print(f"\nTotal characters: {len(self.characters)}")
        print(f"Unique styles (flyweights): {self.style_factory.get_style_count()}")
        print(f"Memory savings: {len(self.characters) - self.style_factory.get_style_count()} style objects")

# Usage
print("=== Creating Document ===")
doc = Document()

# Add many characters with few unique styles
doc.add_character('H', 0, 'Arial', 12, 'black')
doc.add_character('e', 1, 'Arial', 12, 'black')
doc.add_character('l', 2, 'Arial', 12, 'black')
doc.add_character('l', 3, 'Arial', 12, 'black')
doc.add_character('o', 4, 'Arial', 12, 'black')
doc.add_character(' ', 5, 'Arial', 12, 'black')
doc.add_character('W', 6, 'Arial', 14, 'red')
doc.add_character('o', 7, 'Arial', 14, 'red')
doc.add_character('r', 8, 'Arial', 14, 'red')
doc.add_character('l', 9, 'Arial', 14, 'red')
doc.add_character('d', 10, 'Arial', 14, 'red')

print("\n=== Displaying Document ===")
doc.display()

# Practical Example: Game Particle System
class ParticleType:
    """Flyweight for particle intrinsic state."""

    def __init__(self, sprite: str, color: str, size: int):
        # Intrinsic state (shared among many particles)
        self.sprite = sprite
        self.color = color
        self.size = size
        print(f"Loading particle type: {sprite}, {color}, {size}px")

    def render(self, x: int, y: int, velocity_x: int, velocity_y: int) -> str:
        """Render particle with extrinsic state."""
        return f"{self.sprite} at ({x},{y}) moving ({velocity_x},{velocity_y}) - {self.color}, {self.size}px"

class ParticleFactory:
    """Factory managing particle type flyweights."""

    def __init__(self):
        self._particle_types: Dict[Tuple[str, str, int], ParticleType] = {}

    def get_particle_type(self, sprite: str, color: str, size: int) -> ParticleType:
        key = (sprite, color, size)

        if key not in self._particle_types:
            self._particle_types[key] = ParticleType(sprite, color, size)

        return self._particle_types[key]

    def get_type_count(self) -> int:
        return len(self._particle_types)

class Particle:
    """Individual particle with extrinsic state."""

    def __init__(self, x: int, y: int, velocity_x: int, velocity_y: int, particle_type: ParticleType):
        # Extrinsic state (unique per particle)
        self.x = x
        self.y = y
        self.velocity_x = velocity_x
        self.velocity_y = velocity_y
        # Intrinsic state (shared)
        self.type = particle_type

    def render(self) -> str:
        return self.type.render(self.x, self.y, self.velocity_x, self.velocity_y)

class ParticleSystem:
    """System managing thousands of particles."""

    def __init__(self):
        self.particles = []
        self.factory = ParticleFactory()

    def create_explosion(self, x: int, y: int):
        """Create explosion with many particles."""
        print(f"\nCreating explosion at ({x},{y})")

        # Create 100 fire particles
        fire_type = self.factory.get_particle_type("fire.png", "orange", 8)
        for i in range(100):
            self.particles.append(Particle(x, y, i % 10, i % 5, fire_type))

        # Create 50 smoke particles
        smoke_type = self.factory.get_particle_type("smoke.png", "gray", 12)
        for i in range(50):
            self.particles.append(Particle(x, y, i % 5, i % 3, smoke_type))

    def render(self):
        """Render all particles."""
        print(f"\nRendering {len(self.particles)} particles...")
        for i, particle in enumerate(self.particles[:3]):  # Show first 3
            print(particle.render())
        print("...")

        print(f"\nTotal particles: {len(self.particles)}")
        print(f"Unique particle types (flyweights): {self.factory.get_type_count()}")
        print(f"Memory savings: Without flyweight would need {len(self.particles)} type objects")
        print(f"With flyweight only need {self.factory.get_type_count()} type objects")

# Usage
print("\n=== Particle System ===")
particle_system = ParticleSystem()
particle_system.create_explosion(100, 200)
particle_system.create_explosion(300, 400)
particle_system.render()
```

#### TypeScript Implementation

```typescript
// Flyweight Pattern

// Flyweight: Icon Type
class IconType {
    constructor(
        public readonly name: string,
        public readonly imagePath: string,
        public readonly width: number,
        public readonly height: number
    ) {
        console.log(`Loading icon: ${name} from ${imagePath}`);
    }

    render(x: number, y: number): string {
        return `Rendering ${this.name} at (${x},${y}) - ${this.width}x${this.height}px`;
    }
}

// Flyweight Factory
class IconFactory {
    private iconTypes: Map<string, IconType> = new Map();

    getIconType(name: string, imagePath: string, width: number, height: number): IconType {
        const key = `${name}_${imagePath}_${width}_${height}`;

        if (!this.iconTypes.has(key)) {
            this.iconTypes.set(key, new IconType(name, imagePath, width, height));
        } else {
            console.log(`Reusing icon type: ${name}`);
        }

        return this.iconTypes.get(key)!;
    }

    getTypeCount(): number {
        return this.iconTypes.size;
    }
}

// Client: Icon Instance
class Icon {
    constructor(
        private x: number,
        private y: number,
        private type: IconType
    ) {}

    move(x: number, y: number): void {
        this.x = x;
        this.y = y;
    }

    render(): string {
        return this.type.render(this.x, this.y);
    }
}

// Desktop with many icons
class Desktop {
    private icons: Icon[] = [];
    private factory: IconFactory = new IconFactory();

    addIcon(name: string, imagePath: string, x: number, y: number): void {
        const iconType = this.factory.getIconType(name, imagePath, 64, 64);
        this.icons.push(new Icon(x, y, iconType));
    }

    renderAll(): void {
        console.log("\n=== Rendering Desktop ===");
        this.icons.forEach(icon => console.log(icon.render()));

        console.log(`\nTotal icons: ${this.icons.length}`);
        console.log(`Unique icon types (flyweights): ${this.factory.getTypeCount()}`);
        console.log(`Memory saved: ${this.icons.length - this.factory.getTypeCount()} icon type objects`);
    }
}

// Usage
const desktop = new Desktop();

// Add many icons of same types
desktop.addIcon("Folder", "/icons/folder.png", 10, 10);
desktop.addIcon("Folder", "/icons/folder.png", 100, 10);
desktop.addIcon("Folder", "/icons/folder.png", 190, 10);
desktop.addIcon("File", "/icons/file.png", 10, 100);
desktop.addIcon("File", "/icons/file.png", 100, 100);
desktop.addIcon("File", "/icons/file.png", 190, 100);
desktop.addIcon("App", "/icons/app.png", 10, 190);

desktop.renderAll();

// Practical Example: Tree Forest
interface TreeType {
    name: string;
    color: string;
    texture: string;
}

class TreeFactory {
    private static treeTypes: Map<string, TreeType> = new Map();

    static getTreeType(name: string, color: string, texture: string): TreeType {
        const key = `${name}_${color}_${texture}`;

        if (!this.treeTypes.has(key)) {
            const treeType = { name, color, texture };
            this.treeTypes.set(key, treeType);
            console.log(`Creating tree type: ${name}`);
        }

        return this.treeTypes.get(key)!;
    }

    static getTypeCount(): number {
        return this.treeTypes.size;
    }
}

class Tree {
    constructor(
        private x: number,
        private y: number,
        private type: TreeType
    ) {}

    draw(): string {
        return `${this.type.name} tree at (${this.x},${this.y}) - ${this.type.color}, ${this.type.texture}`;
    }
}

class Forest {
    private trees: Tree[] = [];

    plantTree(x: number, y: number, name: string, color: string, texture: string): void {
        const type = TreeFactory.getTreeType(name, color, texture);
        this.trees.push(new Tree(x, y, type));
    }

    draw(): void {
        console.log("\n=== Drawing Forest ===");
        this.trees.forEach(tree => console.log(tree.draw()));

        console.log(`\nTotal trees: ${this.trees.length}`);
        console.log(`Unique tree types: ${TreeFactory.getTypeCount()}`);
    }
}

// Plant forest with few tree types but many instances
const forest = new Forest();
for (let i = 0; i < 100; i++) {
    const x = Math.floor(Math.random() * 1000);
    const y = Math.floor(Math.random() * 1000);

    if (i % 3 === 0) {
        forest.plantTree(x, y, "Oak", "green", "rough");
    } else if (i % 3 === 1) {
        forest.plantTree(x, y, "Pine", "dark-green", "needles");
    } else {
        forest.plantTree(x, y, "Birch", "light-green", "smooth");
    }
}

console.log(`\n100 trees planted with only 3 tree type objects!`);
```

#### Java Implementation

```java
// Flyweight Pattern

import java.util.HashMap;
import java.util.Map;

// Flyweight: Character Glyph
public class CharacterGlyph {
    private final char character;
    private final String fontFamily;
    private final int fontSize;

    public CharacterGlyph(char character, String fontFamily, int fontSize) {
        this.character = character;
        this.fontFamily = fontFamily;
        this.fontSize = fontSize;
        System.out.println("Creating glyph: '" + character + "' " + fontFamily + " " + fontSize + "pt");
    }

    public void render(int x, int y, String color) {
        System.out.println("Rendering '" + character + "' at (" + x + "," + y + ") - " +
                         fontFamily + " " + fontSize + "pt " + color);
    }
}

// Flyweight Factory
public class GlyphFactory {
    private Map<String, CharacterGlyph> glyphs = new HashMap<>();

    public CharacterGlyph getGlyph(char character, String fontFamily, int fontSize) {
        String key = character + "_" + fontFamily + "_" + fontSize;

        if (!glyphs.containsKey(key)) {
            glyphs.put(key, new CharacterGlyph(character, fontFamily, fontSize));
        }

        return glyphs.get(key);
    }

    public int getGlyphCount() {
        return glyphs.size();
    }
}

// Client: Text Element
public class TextElement {
    private char character;
    private int x;
    private int y;
    private String color;
    private CharacterGlyph glyph;

    public TextElement(char character, int x, int y, String color, CharacterGlyph glyph) {
        this.character = character;
        this.x = x;
        this.y = y;
        this.color = color;
        this.glyph = glyph;
    }

    public void render() {
        glyph.render(x, y, color);
    }
}

// Text Document
public class TextDocument {
    private java.util.List<TextElement> elements = new java.util.ArrayList<>();
    private GlyphFactory glyphFactory = new GlyphFactory();

    public void addCharacter(char character, int x, int y, String color, String fontFamily, int fontSize) {
        CharacterGlyph glyph = glyphFactory.getGlyph(character, fontFamily, fontSize);
        elements.add(new TextElement(character, x, y, color, glyph));
    }

    public void render() {
        System.out.println("\n=== Rendering Document ===");
        elements.forEach(TextElement::render);

        System.out.println("\nTotal characters: " + elements.size());
        System.out.println("Unique glyphs (flyweights): " + glyphFactory.getGlyphCount());
        System.out.println("Memory savings: " + (elements.size() - glyphFactory.getGlyphCount()) + " glyph objects");
    }
}

// Usage
public class FlyweightExample {
    public static void main(String[] args) {
        TextDocument document = new TextDocument();

        // Add text with repeated characters and styles
        String text = "Hello World";
        int x = 0;

        for (char c : text.toCharArray()) {
            document.addCharacter(c, x, 10, "black", "Arial", 12);
            x += 10;
        }

        // Add more text with same style
        text = "Hello Again";
        x = 0;

        for (char c : text.toCharArray()) {
            document.addCharacter(c, x, 30, "black", "Arial", 12);
            x += 10;
        }

        document.render();
    }
}
```

### When to Use

Use Flyweight when:
- Application uses large number of objects
- Storage costs are high due to sheer quantity of objects
- Most object state can be made extrinsic
- Many groups of objects can be replaced by relatively few shared objects
- Application doesn't depend on object identity (can use shared objects)

**Common Use Cases**:
- Text editors (character glyphs)
- Games (particles, sprites, tiles)
- Graphics systems (icons, shapes)
- Caching systems
- String interning

### When NOT to Use

Avoid Flyweight when:
- Few objects exist
- Object state cannot be separated into intrinsic/extrinsic
- Extrinsic state storage cost exceeds savings
- Object identity is important

### Real-World Examples

**Text Editor**:
```python
# Share character styles among millions of characters
style = style_factory.get_style('Arial', 12, 'black')
# Reused for many characters
```

**Game Particles**:
```typescript
// Share particle types among thousands of instances
const fireType = factory.getParticleType("fire.png", "orange", 8);
// Used for 100 fire particles in explosion
```

**String Interning**:
```java
// Java automatically uses Flyweight for String literals
String s1 = "hello";
String s2 = "hello";
// s1 and s2 reference same object
```

### Related Patterns

- **Composite**: Often combined with Flyweight to implement shared leaf nodes
- **State/Strategy**: Strategy objects often make good flyweights
- **Factory Method**: Often used to enforce sharing (FlyweightFactory)
- **Singleton**: Factory is often a Singleton

### SOLID Principles

**Single Responsibility Principle**: Flyweight has one job—storing shared intrinsic state

**Dependency Inversion Principle**: Clients depend on flyweight abstraction, not concrete implementations

---

## 12. Proxy Pattern

### Intent

Provide a surrogate or placeholder for another object to control access to it.

### Problem

How do you control access to an object? You may need to:
- **Delay expensive object creation** until actually needed (lazy loading)
- **Control access** to sensitive objects (protection)
- **Add functionality** when accessing remote objects (remote proxy)
- **Cache results** of expensive operations (caching proxy)
- **Log access** to objects (logging proxy)

Direct access doesn't allow these controls.

### Solution

Create a proxy class with the same interface as the real object. The proxy controls access to the real object, creating it on demand, checking permissions, caching results, or adding logging. Clients interact with the proxy as if it were the real object.

### Structure

**Key Participants**:
- **Subject**: Defines common interface for RealSubject and Proxy
- **RealSubject**: Defines real object that proxy represents
- **Proxy**: Maintains reference to RealSubject; controls access to it; may create and delete it

**Proxy Types**:
- **Virtual Proxy**: Lazy initialization, defers creation until needed
- **Protection Proxy**: Controls access based on permissions
- **Remote Proxy**: Represents object in different address space
- **Caching Proxy**: Caches results to avoid repeated computation
- **Logging Proxy**: Logs requests before delegating

### Implementation

#### Python Implementation

```python
# Proxy Pattern

from abc import ABC, abstractmethod
from typing import Optional
import time

# Subject Interface
class Image(ABC):
    """Interface for both real image and proxy."""

    @abstractmethod
    def display(self) -> str:
        pass

    @abstractmethod
    def get_size(self) -> int:
        pass

# Real Subject
class RealImage(Image):
    """Real image that is expensive to load."""

    def __init__(self, filename: str):
        self.filename = filename
        self._size = 0
        self._load_from_disk()

    def _load_from_disk(self) -> None:
        """Simulate expensive loading operation."""
        print(f"Loading image from disk: {self.filename}")
        time.sleep(1)  # Simulate delay
        self._size = 1024000  # 1MB
        print(f"Image loaded: {self.filename}")

    def display(self) -> str:
        return f"Displaying image: {self.filename}"

    def get_size(self) -> int:
        return self._size

# Virtual Proxy (Lazy Loading)
class ImageProxy(Image):
    """Proxy that delays loading until needed."""

    def __init__(self, filename: str):
        self.filename = filename
        self._real_image: Optional[RealImage] = None

    def display(self) -> str:
        """Load on first access."""
        if self._real_image is None:
            print("Proxy: Creating real image on first access")
            self._real_image = RealImage(self.filename)
        return self._real_image.display()

    def get_size(self) -> int:
        """Load on first access."""
        if self._real_image is None:
            print("Proxy: Creating real image on first access")
            self._real_image = RealImage(self.filename)
        return self._real_image.get_size()

# Usage: Virtual Proxy
print("=== Virtual Proxy (Lazy Loading) ===")
print("Creating image proxies (no loading yet)...")
image1 = ImageProxy("photo1.jpg")
image2 = ImageProxy("photo2.jpg")
image3 = ImageProxy("photo3.jpg")
print("Proxies created instantly!\n")

print("Now accessing image1...")
print(image1.display())

print("\nAccessing image1 again (already loaded)...")
print(image1.display())

print("\nNever accessing image2 or image3 (never loaded!)")

# Protection Proxy
class BankAccount(ABC):
    """Subject: Bank account interface."""

    @abstractmethod
    def deposit(self, amount: float) -> str:
        pass

    @abstractmethod
    def withdraw(self, amount: float) -> str:
        pass

    @abstractmethod
    def get_balance(self) -> float:
        pass

class RealBankAccount(BankAccount):
    """Real bank account."""

    def __init__(self, initial_balance: float):
        self._balance = initial_balance

    def deposit(self, amount: float) -> str:
        self._balance += amount
        return f"Deposited ${amount:.2f}. New balance: ${self._balance:.2f}"

    def withdraw(self, amount: float) -> str:
        if amount > self._balance:
            return f"Insufficient funds. Balance: ${self._balance:.2f}"
        self._balance -= amount
        return f"Withdrew ${amount:.2f}. New balance: ${self._balance:.2f}"

    def get_balance(self) -> float:
        return self._balance

class ProtectedBankAccount(BankAccount):
    """Protection proxy with access control."""

    def __init__(self, real_account: RealBankAccount, password: str):
        self._real_account = real_account
        self._password = password
        self._is_authenticated = False

    def authenticate(self, password: str) -> bool:
        """Authenticate user."""
        if password == self._password:
            self._is_authenticated = True
            print("Authentication successful")
            return True
        else:
            print("Authentication failed")
            return False

    def deposit(self, amount: float) -> str:
        if not self._is_authenticated:
            return "Access denied: Authentication required"
        return self._real_account.deposit(amount)

    def withdraw(self, amount: float) -> str:
        if not self._is_authenticated:
            return "Access denied: Authentication required"
        return self._real_account.withdraw(amount)

    def get_balance(self) -> float:
        if not self._is_authenticated:
            raise PermissionError("Access denied: Authentication required")
        return self._real_account.get_balance()

# Usage: Protection Proxy
print("\n=== Protection Proxy ===")
real_account = RealBankAccount(1000.00)
protected_account = ProtectedBankAccount(real_account, "secret123")

print(protected_account.deposit(100))  # Denied
print(protected_account.withdraw(50))  # Denied

protected_account.authenticate("secret123")
print(protected_account.deposit(100))  # Allowed
print(protected_account.withdraw(50))  # Allowed
print(f"Balance: ${protected_account.get_balance():.2f}")

# Caching Proxy
class DataService(ABC):
    """Subject: Data service interface."""

    @abstractmethod
    def fetch_data(self, query: str) -> str:
        pass

class RealDataService(DataService):
    """Real service with expensive operations."""

    def fetch_data(self, query: str) -> str:
        """Simulate expensive database query."""
        print(f"Executing expensive query: {query}")
        time.sleep(2)  # Simulate delay
        return f"Result for: {query}"

class CachingDataService(DataService):
    """Caching proxy to avoid repeated queries."""

    def __init__(self, real_service: DataService):
        self._real_service = real_service
        self._cache = {}

    def fetch_data(self, query: str) -> str:
        """Return cached result if available."""
        if query in self._cache:
            print(f"Returning cached result for: {query}")
            return self._cache[query]

        print(f"Cache miss for: {query}")
        result = self._real_service.fetch_data(query)
        self._cache[query] = result
        return result

# Usage: Caching Proxy
print("\n=== Caching Proxy ===")
real_service = RealDataService()
caching_service = CachingDataService(real_service)

print("First query (cache miss):")
print(caching_service.fetch_data("SELECT * FROM users"))

print("\nSame query again (cache hit):")
print(caching_service.fetch_data("SELECT * FROM users"))

print("\nDifferent query (cache miss):")
print(caching_service.fetch_data("SELECT * FROM products"))
```

#### TypeScript Implementation

```typescript
// Proxy Pattern

// Subject Interface
interface Database {
    query(sql: string): string;
}

// Real Subject
class RealDatabase implements Database {
    private connection: string;

    constructor() {
        console.log("Database: Establishing connection (expensive)...");
        this.connection = "Connected to PostgreSQL";
        this.simulateDelay(1000);
        console.log("Database: Connection established");
    }

    query(sql: string): string {
        console.log(`Database: Executing query: ${sql}`);
        this.simulateDelay(500);
        return `Results for: ${sql}`;
    }

    private simulateDelay(ms: number): void {
        const start = Date.now();
        while (Date.now() - start < ms) {}
    }
}

// Virtual Proxy (Lazy Initialization)
class DatabaseProxy implements Database {
    private realDatabase: RealDatabase | null = null;

    query(sql: string): string {
        if (this.realDatabase === null) {
            console.log("Proxy: Creating database connection on first query");
            this.realDatabase = new RealDatabase();
        }
        return this.realDatabase.query(sql);
    }
}

// Usage: Virtual Proxy
console.log("=== Virtual Proxy (Lazy Initialization) ===");
console.log("Creating database proxy (no connection yet)...");
const db = new DatabaseProxy();
console.log("Proxy created instantly!\n");

console.log("First query (connection created):");
console.log(db.query("SELECT * FROM users"));

console.log("\nSecond query (connection already exists):");
console.log(db.query("SELECT * FROM products"));

// Protection Proxy with Role-Based Access
interface Document {
    read(): string;
    write(content: string): void;
}

class SecureDocument implements Document {
    private content: string = "Confidential data";

    read(): string {
        return this.content;
    }

    write(content: string): void {
        this.content = content;
        console.log("Document updated");
    }
}

class DocumentProxy implements Document {
    private document: SecureDocument;
    private userRole: string;

    constructor(document: SecureDocument, userRole: string) {
        this.document = document;
        this.userRole = userRole;
    }

    read(): string {
        console.log(`Proxy: Checking read permission for role: ${this.userRole}`);
        if (this.userRole === "admin" || this.userRole === "user") {
            return this.document.read();
        }
        throw new Error("Access denied: Insufficient permissions to read");
    }

    write(content: string): void {
        console.log(`Proxy: Checking write permission for role: ${this.userRole}`);
        if (this.userRole === "admin") {
            this.document.write(content);
        } else {
            throw new Error("Access denied: Only admins can write");
        }
    }
}

// Usage: Protection Proxy
console.log("\n=== Protection Proxy ===");
const secureDoc = new SecureDocument();

const adminProxy = new DocumentProxy(secureDoc, "admin");
console.log("Admin reading:", adminProxy.read());
adminProxy.write("Updated by admin");

const userProxy = new DocumentProxy(secureDoc, "user");
console.log("User reading:", userProxy.read());
try {
    userProxy.write("Attempting to update");
} catch (e) {
    console.log("Error:", (e as Error).message);
}

// Logging Proxy
interface API {
    request(endpoint: string): string;
}

class RealAPI implements API {
    request(endpoint: string): string {
        return `Response from ${endpoint}`;
    }
}

class LoggingAPIProxy implements API {
    private api: RealAPI;
    private requestCount: number = 0;

    constructor(api: RealAPI) {
        this.api = api;
    }

    request(endpoint: string): string {
        this.requestCount++;
        const timestamp = new Date().toISOString();

        console.log(`[${timestamp}] Request #${this.requestCount} to ${endpoint}`);

        const startTime = Date.now();
        const response = this.api.request(endpoint);
        const duration = Date.now() - startTime;

        console.log(`[${timestamp}] Response received in ${duration}ms`);

        return response;
    }

    getRequestCount(): number {
        return this.requestCount;
    }
}

// Usage: Logging Proxy
console.log("\n=== Logging Proxy ===");
const api = new RealAPI();
const loggingApi = new LoggingAPIProxy(api);

loggingApi.request("/users");
loggingApi.request("/products");
loggingApi.request("/orders");

console.log(`\nTotal requests: ${loggingApi.getRequestCount()}`);
```

#### Java Implementation

```java
// Proxy Pattern

// Subject Interface
public interface Internet {
    void connect(String host);
}

// Real Subject
public class RealInternet implements Internet {
    @Override
    public void connect(String host) {
        System.out.println("Connecting to " + host);
    }
}

// Protection Proxy with Access Control
public class ProxyInternet implements Internet {
    private RealInternet realInternet = new RealInternet();
    private java.util.List<String> bannedSites;

    public ProxyInternet() {
        bannedSites = new java.util.ArrayList<>();
        bannedSites.add("facebook.com");
        bannedSites.add("twitter.com");
        bannedSites.add("instagram.com");
    }

    @Override
    public void connect(String host) {
        if (bannedSites.contains(host.toLowerCase())) {
            System.out.println("Access denied: " + host + " is blocked");
        } else {
            realInternet.connect(host);
        }
    }
}

// Virtual Proxy for Expensive Object
interface VideoFile {
    void play();
}

class RealVideoFile implements VideoFile {
    private String filename;

    public RealVideoFile(String filename) {
        this.filename = filename;
        loadFromDisk();
    }

    private void loadFromDisk() {
        System.out.println("Loading large video file: " + filename);
        try {
            Thread.sleep(2000); // Simulate loading delay
        } catch (InterruptedException e) {
            e.printStackTrace();
        }
        System.out.println("Video loaded: " + filename);
    }

    @Override
    public void play() {
        System.out.println("Playing video: " + filename);
    }
}

class VideoProxy implements VideoFile {
    private String filename;
    private RealVideoFile realVideo;

    public VideoProxy(String filename) {
        this.filename = filename;
    }

    @Override
    public void play() {
        if (realVideo == null) {
            System.out.println("Proxy: Loading video on first play");
            realVideo = new RealVideoFile(filename);
        }
        realVideo.play();
    }
}

// Usage
public class ProxyExample {
    public static void main(String[] args) {
        System.out.println("=== Protection Proxy ===");
        Internet internet = new ProxyInternet();
        internet.connect("google.com");
        internet.connect("facebook.com");
        internet.connect("github.com");

        System.out.println("\n=== Virtual Proxy ===");
        System.out.println("Creating video proxies (instant)...");
        VideoFile video1 = new VideoProxy("movie1.mp4");
        VideoFile video2 = new VideoProxy("movie2.mp4");
        System.out.println("Proxies created!\n");

        System.out.println("Playing video1 (loads now):");
        video1.play();

        System.out.println("\nPlaying video1 again (already loaded):");
        video1.play();

        System.out.println("\nVideo2 never played (never loaded!)");
    }
}
```

### When to Use

Use Proxy when you need:

**Virtual Proxy (Lazy Initialization)**:
- Defer expensive object creation until needed
- Load large resources on demand

**Protection Proxy (Access Control)**:
- Control access based on permissions
- Implement role-based access control

**Remote Proxy**:
- Represent object in different address space
- Handle network communication

**Caching Proxy**:
- Cache expensive operation results
- Avoid repeated computations

**Logging Proxy**:
- Log access to objects
- Monitor usage patterns

**Common Use Cases**:
- Lazy loading images/videos
- Access control for sensitive resources
- Remote service calls (web services, RPC)
- Caching database queries
- Request logging and monitoring

### When NOT to Use

Avoid Proxy when:
- Direct access is sufficient
- Overhead of proxy layer isn't justified
- Real-time performance is critical
- Object creation isn't expensive

### Real-World Examples

**Virtual Proxy**:
```python
# Delay loading until display() called
image_proxy = ImageProxy("large_image.jpg")  # Instant
image_proxy.display()  # Loads now
```

**Protection Proxy**:
```typescript
// Control access based on user role
const userProxy = new DocumentProxy(document, "user");
userProxy.read();  // Allowed
userProxy.write("data");  // Denied
```

**Caching Proxy**:
```java
// Cache expensive database queries
CachingDataService cache = new CachingDataService(realService);
cache.fetch("query");  // Executes query
cache.fetch("query");  // Returns cached result
```

### Related Patterns

- **Adapter**: Changes interface; Proxy keeps same interface
- **Decorator**: Adds responsibilities; Proxy controls access
- **Facade**: Simplifies interface; Proxy provides same interface with control

### SOLID Principles

**Single Responsibility Principle**: Proxy has one job—controlling access to real object

**Open-Closed Principle**: New proxy types can be added without modifying real subject

**Dependency Inversion Principle**: Both proxy and real subject depend on subject interface

---

*[End of Structural Patterns section]*

# Behavioral Patterns

Behavioral patterns deal with algorithms and the assignment of responsibilities between objects. They describe not just patterns of objects or classes but also the patterns of communication between them. These patterns characterize complex control flow that's difficult to follow at runtime and shift focus away from control flow to let you concentrate on the way objects are interconnected.

## 13. Chain of Responsibility Pattern

### Intent

Avoid coupling the sender of a request to its receiver by giving more than one object a chance to handle the request. Chain the receiving objects and pass the request along the chain until an object handles it.

### Problem

You need to process a request but don't know which handler should process it. Multiple objects might be able to handle the request, but you don't want to couple the sender to specific handlers. How do you decouple request senders from receivers while giving multiple objects a chance to handle the request?

### Solution

Create a chain of handler objects. Each handler decides whether to process the request or pass it to the next handler in the chain. The request travels along the chain until a handler processes it or the chain ends.

### Structure

**Key Participants**:
- **Handler**: Defines interface for handling requests and optional link to successor
- **ConcreteHandler**: Handles requests it's responsible for; forwards others to successor
- **Client**: Initiates request to a handler in the chain

### Implementation

#### Python Implementation

```python
# Chain of Responsibility Pattern

from abc import ABC, abstractmethod
from typing import Optional

# Handler Interface
class SupportHandler(ABC):
    """Abstract handler for support tickets."""

    def __init__(self, successor: Optional['SupportHandler'] = None):
        self._successor = successor

    def handle_request(self, request: str, priority: int) -> str:
        """Handle request or pass to successor."""
        if self.can_handle(priority):
            return self.process_request(request, priority)
        elif self._successor:
            return self._successor.handle_request(request, priority)
        else:
            return f"Request with priority {priority} could not be handled"

    @abstractmethod
    def can_handle(self, priority: int) -> bool:
        """Determine if this handler can process the request."""
        pass

    @abstractmethod
    def process_request(self, request: str, priority: int) -> str:
        """Process the request."""
        pass

# Concrete Handlers
class Level1Support(SupportHandler):
    """Handles basic support requests."""

    def can_handle(self, priority: int) -> bool:
        return priority <= 1

    def process_request(self, request: str, priority: int) -> str:
        return f"Level 1 Support: Handling basic request - {request}"

class Level2Support(SupportHandler):
    """Handles intermediate support requests."""

    def can_handle(self, priority: int) -> bool:
        return priority <= 2

    def process_request(self, request: str, priority: int) -> str:
        return f"Level 2 Support: Handling intermediate request - {request}"

class Level3Support(SupportHandler):
    """Handles critical support requests."""

    def can_handle(self, priority: int) -> bool:
        return priority <= 3

    def process_request(self, request: str, priority: int) -> str:
        return f"Level 3 Support: Handling critical request - {request}"

# Build the chain
level3 = Level3Support()
level2 = Level2Support(level3)
level1 = Level1Support(level2)

# Usage
print(level1.handle_request("Password reset", 1))
print(level1.handle_request("Database connection issue", 2))
print(level1.handle_request("System outage", 3))

# Practical Example: Expense Approval Chain
class ExpenseApprover(ABC):
    """Abstract handler for expense approvals."""

    def __init__(self, limit: float, successor: Optional['ExpenseApprover'] = None):
        self._limit = limit
        self._successor = successor

    def approve(self, expense: dict) -> str:
        """Approve expense or pass to higher authority."""
        amount = expense['amount']
        description = expense['description']

        if amount <= self._limit:
            return self.process_approval(expense)
        elif self._successor:
            return self._successor.approve(expense)
        else:
            return f"Expense ${amount:.2f} exceeds all approval limits"

    @abstractmethod
    def process_approval(self, expense: dict) -> str:
        """Process the approval."""
        pass

class TeamLead(ExpenseApprover):
    """Approves expenses up to $1,000."""

    def __init__(self, successor: Optional['ExpenseApprover'] = None):
        super().__init__(limit=1000, successor=successor)

    def process_approval(self, expense: dict) -> str:
        return f"Team Lead approved: ${expense['amount']:.2f} for {expense['description']}"

class Manager(ExpenseApprover):
    """Approves expenses up to $5,000."""

    def __init__(self, successor: Optional['ExpenseApprover'] = None):
        super().__init__(limit=5000, successor=successor)

    def process_approval(self, expense: dict) -> str:
        return f"Manager approved: ${expense['amount']:.2f} for {expense['description']}"

class Director(ExpenseApprover):
    """Approves expenses up to $10,000."""

    def __init__(self, successor: Optional['ExpenseApprover'] = None):
        super().__init__(limit=10000, successor=successor)

    def process_approval(self, expense: dict) -> str:
        return f"Director approved: ${expense['amount']:.2f} for {expense['description']}"

# Build approval chain
director = Director()
manager = Manager(director)
team_lead = TeamLead(manager)

# Usage
expenses = [
    {"amount": 500, "description": "Software license"},
    {"amount": 3500, "description": "Conference attendance"},
    {"amount": 8000, "description": "New equipment"},
]

for expense in expenses:
    print(team_lead.approve(expense))
```

#### TypeScript Implementation

```typescript
// Chain of Responsibility Pattern

// Handler Interface
abstract class Logger {
    protected nextLogger: Logger | null = null;
    protected level: number;

    constructor(level: number) {
        this.level = level;
    }

    setNext(nextLogger: Logger): Logger {
        this.nextLogger = nextLogger;
        return nextLogger;
    }

    log(level: number, message: string): void {
        if (level >= this.level) {
            this.write(message);
        }
        if (this.nextLogger !== null) {
            this.nextLogger.log(level, message);
        }
    }

    protected abstract write(message: string): void;
}

// Concrete Handlers
class ConsoleLogger extends Logger {
    constructor(level: number) {
        super(level);
    }

    protected write(message: string): void {
        console.log(`Console: ${message}`);
    }
}

class FileLogger extends Logger {
    constructor(level: number) {
        super(level);
    }

    protected write(message: string): void {
        console.log(`File: ${message}`);
    }
}

class ErrorLogger extends Logger {
    constructor(level: number) {
        super(level);
    }

    protected write(message: string): void {
        console.error(`ERROR LOG: ${message}`);
    }
}

// Log levels
enum LogLevel {
    DEBUG = 1,
    INFO = 2,
    WARNING = 3,
    ERROR = 4
}

// Build the chain
const consoleLogger = new ConsoleLogger(LogLevel.DEBUG);
const fileLogger = new FileLogger(LogLevel.INFO);
const errorLogger = new ErrorLogger(LogLevel.ERROR);

consoleLogger.setNext(fileLogger).setNext(errorLogger);

// Usage
consoleLogger.log(LogLevel.DEBUG, "Debug message - appears in console only");
consoleLogger.log(LogLevel.INFO, "Info message - appears in console and file");
consoleLogger.log(LogLevel.ERROR, "Error message - appears in all logs");

// Practical Example: Authentication Chain
abstract class AuthenticationHandler {
    protected nextHandler: AuthenticationHandler | null = null;

    setNext(handler: AuthenticationHandler): AuthenticationHandler {
        this.nextHandler = handler;
        return handler;
    }

    handle(username: string, password: string): boolean {
        const canHandle = this.authenticate(username, password);

        if (!canHandle && this.nextHandler !== null) {
            return this.nextHandler.handle(username, password);
        }

        return canHandle;
    }

    protected abstract authenticate(username: string, password: string): boolean;
}

class LocalAuthHandler extends AuthenticationHandler {
    private localUsers: Map<string, string>;

    constructor() {
        super();
        this.localUsers = new Map([
            ["admin", "admin123"],
            ["user", "user123"]
        ]);
    }

    protected authenticate(username: string, password: string): boolean {
        const storedPassword = this.localUsers.get(username);
        if (storedPassword && storedPassword === password) {
            console.log(`✓ Authenticated via Local Database: ${username}`);
            return true;
        }
        return false;
    }
}

class LDAPAuthHandler extends AuthenticationHandler {
    protected authenticate(username: string, password: string): boolean {
        // Simulate LDAP authentication
        if (username.endsWith("@company.com")) {
            console.log(`✓ Authenticated via LDAP: ${username}`);
            return true;
        }
        return false;
    }
}

class OAuth2AuthHandler extends AuthenticationHandler {
    protected authenticate(username: string, password: string): boolean {
        // Simulate OAuth2 authentication
        if (password.startsWith("oauth_")) {
            console.log(`✓ Authenticated via OAuth2: ${username}`);
            return true;
        }
        return false;
    }
}

// Build authentication chain
const localAuth = new LocalAuthHandler();
const ldapAuth = new LDAPAuthHandler();
const oauthAuth = new OAuth2AuthHandler();

localAuth.setNext(ldapAuth).setNext(oauthAuth);

// Usage
console.log("\nAuthentication attempts:");
localAuth.handle("admin", "admin123");                    // Local
localAuth.handle("john@company.com", "password");        // LDAP
localAuth.handle("user@gmail.com", "oauth_token_123");   // OAuth2
```

#### Java Implementation

```java
// Chain of Responsibility Pattern

// Handler Interface
public abstract class PurchaseApprover {
    protected PurchaseApprover successor;
    protected String role;

    public void setSuccessor(PurchaseApprover successor) {
        this.successor = successor;
    }

    public abstract void approvePurchase(Purchase purchase);
}

// Purchase Request
public class Purchase {
    private double amount;
    private String purpose;

    public Purchase(double amount, String purpose) {
        this.amount = amount;
        this.purpose = purpose;
    }

    public double getAmount() {
        return amount;
    }

    public String getPurpose() {
        return purpose;
    }
}

// Concrete Handlers
public class Supervisor extends PurchaseApprover {
    private static final double APPROVAL_LIMIT = 1000;

    public Supervisor() {
        this.role = "Supervisor";
    }

    @Override
    public void approvePurchase(Purchase purchase) {
        if (purchase.getAmount() <= APPROVAL_LIMIT) {
            System.out.printf("%s approved $%.2f for %s%n",
                role, purchase.getAmount(), purchase.getPurpose());
        } else if (successor != null) {
            successor.approvePurchase(purchase);
        } else {
            System.out.printf("Purchase of $%.2f exceeds all approval limits%n",
                purchase.getAmount());
        }
    }
}

public class DepartmentHead extends PurchaseApprover {
    private static final double APPROVAL_LIMIT = 5000;

    public DepartmentHead() {
        this.role = "Department Head";
    }

    @Override
    public void approvePurchase(Purchase purchase) {
        if (purchase.getAmount() <= APPROVAL_LIMIT) {
            System.out.printf("%s approved $%.2f for %s%n",
                role, purchase.getAmount(), purchase.getPurpose());
        } else if (successor != null) {
            successor.approvePurchase(purchase);
        } else {
            System.out.printf("Purchase of $%.2f exceeds all approval limits%n",
                purchase.getAmount());
        }
    }
}

public class CEO extends PurchaseApprover {
    private static final double APPROVAL_LIMIT = 50000;

    public CEO() {
        this.role = "CEO";
    }

    @Override
    public void approvePurchase(Purchase purchase) {
        if (purchase.getAmount() <= APPROVAL_LIMIT) {
            System.out.printf("%s approved $%.2f for %s%n",
                role, purchase.getAmount(), purchase.getPurpose());
        } else {
            System.out.printf("Purchase of $%.2f requires Board approval%n",
                purchase.getAmount());
        }
    }
}

// Usage
public class ChainOfResponsibilityExample {
    public static void main(String[] args) {
        // Build the chain
        PurchaseApprover supervisor = new Supervisor();
        PurchaseApprover departmentHead = new DepartmentHead();
        PurchaseApprover ceo = new CEO();

        supervisor.setSuccessor(departmentHead);
        departmentHead.setSuccessor(ceo);

        // Process purchase requests
        Purchase[] purchases = {
            new Purchase(800, "Office supplies"),
            new Purchase(3500, "New computers"),
            new Purchase(25000, "Server infrastructure"),
            new Purchase(75000, "Building renovation")
        };

        for (Purchase purchase : purchases) {
            supervisor.approvePurchase(purchase);
        }
    }
}
```

### When to Use

Use Chain of Responsibility when:
- More than one object can handle a request, and handler isn't known a priori
- You want to issue request to one of several objects without specifying receiver explicitly
- Set of objects that can handle request should be specified dynamically
- You want to decouple request sender from receiver

**Common Use Cases**:
- Event handling systems (UI event bubbling)
- Logging frameworks (different log levels)
- Approval workflows (expense approval, purchase requests)
- Authentication/authorization chains
- Error handling and exception propagation
- Help systems (context-sensitive help)

### When NOT to Use

Avoid Chain of Responsibility when:
- Every request must be handled (chain might end without handling)
- Performance is critical (traversing chain adds overhead)
- Handler order is complex or frequently changes
- Only one handler exists (use direct call instead)
- Request handling logic is simple enough for single handler

### Real-World Examples

**Support Ticket Escalation**:
```python
# Escalate tickets through support levels
level1_support = Level1Support(level2_support)
level1_support.handle_request("Password reset", priority=1)
```

**Logging Chain**:
```typescript
// Log to console, file, and error logs based on severity
consoleLogger.log(LogLevel.ERROR, "Critical error occurred");
// Propagates through all appropriate loggers
```

**Purchase Approval**:
```java
// Route purchase through approval hierarchy
supervisor.approvePurchase(new Purchase(3500, "Equipment"));
// Automatically escalates to appropriate authority
```

### Related Patterns

- **Command**: Chain of Responsibility can use Command to represent requests as objects
- **Composite**: Chain of Responsibility often used with Composite for parent-child chains
- **Decorator**: Similar structure but different intent (adds responsibilities vs. handles requests)

### SOLID Principles

**Single Responsibility Principle**: Each handler has one reason to change—its handling logic

**Open-Closed Principle**: New handlers can be added without modifying existing chain

**Dependency Inversion Principle**: Handlers depend on handler abstraction, not concrete handlers

---

## 14. Command Pattern

### Intent

Encapsulate a request as an object, thereby letting you parameterize clients with different requests, queue or log requests, and support undoable operations.

### Problem

You want to issue requests to objects without knowing anything about the operation being requested or the receiver of the request. You need to support undo/redo, queue operations, or log requests. How do you decouple the sender of a request from the object that handles it?

### Solution

Encapsulate a request as an object with all information needed to execute it. This lets you parameterize methods with different requests, delay or queue request execution, and support undoable operations.

### Structure

**Key Participants**:
- **Command**: Declares interface for executing an operation
- **ConcreteCommand**: Implements execute() by invoking operations on Receiver
- **Receiver**: Knows how to perform the operations
- **Invoker**: Asks command to carry out request
- **Client**: Creates ConcreteCommand and sets its receiver

### Implementation

#### Python Implementation

```python
# Command Pattern

from abc import ABC, abstractmethod
from typing import List

# Command Interface
class Command(ABC):
    """Abstract command interface."""

    @abstractmethod
    def execute(self) -> None:
        """Execute the command."""
        pass

    @abstractmethod
    def undo(self) -> None:
        """Undo the command."""
        pass

# Receiver
class TextEditor:
    """Receiver that performs actual operations."""

    def __init__(self):
        self._text: str = ""

    def insert(self, text: str, position: int = None) -> None:
        """Insert text at position."""
        if position is None:
            position = len(self._text)
        self._text = self._text[:position] + text + self._text[position:]
        print(f"Text after insert: '{self._text}'")

    def delete(self, start: int, end: int) -> str:
        """Delete text from start to end position."""
        deleted = self._text[start:end]
        self._text = self._text[:start] + self._text[end:]
        print(f"Text after delete: '{self._text}'")
        return deleted

    def get_text(self) -> str:
        """Get current text."""
        return self._text

# Concrete Commands
class InsertCommand(Command):
    """Command to insert text."""

    def __init__(self, editor: TextEditor, text: str, position: int = None):
        self._editor = editor
        self._text = text
        self._position = position if position is not None else len(editor.get_text())

    def execute(self) -> None:
        """Execute insert."""
        self._editor.insert(self._text, self._position)

    def undo(self) -> None:
        """Undo insert by deleting inserted text."""
        end_position = self._position + len(self._text)
        self._editor.delete(self._position, end_position)

class DeleteCommand(Command):
    """Command to delete text."""

    def __init__(self, editor: TextEditor, start: int, end: int):
        self._editor = editor
        self._start = start
        self._end = end
        self._deleted_text: str = ""

    def execute(self) -> None:
        """Execute delete."""
        self._deleted_text = self._editor.delete(self._start, self._end)

    def undo(self) -> None:
        """Undo delete by inserting deleted text."""
        self._editor.insert(self._deleted_text, self._start)

# Invoker
class CommandManager:
    """Manages command execution and undo/redo."""

    def __init__(self):
        self._history: List[Command] = []
        self._current_index: int = -1

    def execute_command(self, command: Command) -> None:
        """Execute command and add to history."""
        # Remove any commands after current index (can't redo after new command)
        self._history = self._history[:self._current_index + 1]

        command.execute()
        self._history.append(command)
        self._current_index += 1

    def undo(self) -> None:
        """Undo last command."""
        if self._current_index >= 0:
            command = self._history[self._current_index]
            command.undo()
            self._current_index -= 1
            print("Undo completed")
        else:
            print("Nothing to undo")

    def redo(self) -> None:
        """Redo previously undone command."""
        if self._current_index < len(self._history) - 1:
            self._current_index += 1
            command = self._history[self._current_index]
            command.execute()
            print("Redo completed")
        else:
            print("Nothing to redo")

# Usage
editor = TextEditor()
manager = CommandManager()

# Execute commands
manager.execute_command(InsertCommand(editor, "Hello"))
manager.execute_command(InsertCommand(editor, " World"))
manager.execute_command(InsertCommand(editor, "!", 11))

# Undo operations
manager.undo()  # Remove "!"
manager.undo()  # Remove " World"

# Redo operations
manager.redo()  # Add " World" back

# Practical Example: Transaction System
class Account:
    """Bank account receiver."""

    def __init__(self, balance: float = 0):
        self._balance = balance

    def deposit(self, amount: float) -> None:
        """Deposit money."""
        self._balance += amount
        print(f"Deposited ${amount:.2f}. Balance: ${self._balance:.2f}")

    def withdraw(self, amount: float) -> bool:
        """Withdraw money if sufficient balance."""
        if self._balance >= amount:
            self._balance -= amount
            print(f"Withdrew ${amount:.2f}. Balance: ${self._balance:.2f}")
            return True
        print(f"Insufficient funds. Balance: ${self._balance:.2f}")
        return False

    def get_balance(self) -> float:
        return self._balance

class DepositCommand(Command):
    """Command to deposit money."""

    def __init__(self, account: Account, amount: float):
        self._account = account
        self._amount = amount

    def execute(self) -> None:
        self._account.deposit(self._amount)

    def undo(self) -> None:
        self._account.withdraw(self._amount)

class WithdrawCommand(Command):
    """Command to withdraw money."""

    def __init__(self, account: Account, amount: float):
        self._account = account
        self._amount = amount
        self._succeeded = False

    def execute(self) -> None:
        self._succeeded = self._account.withdraw(self._amount)

    def undo(self) -> None:
        if self._succeeded:
            self._account.deposit(self._amount)

# Usage
account = Account(1000)
transaction_manager = CommandManager()

transaction_manager.execute_command(DepositCommand(account, 500))
transaction_manager.execute_command(WithdrawCommand(account, 300))
transaction_manager.undo()  # Cancel withdrawal
```

#### TypeScript Implementation

```typescript
// Command Pattern

// Command Interface
interface Command {
    execute(): void;
    undo(): void;
}

// Receiver: Smart Home Device
class Light {
    private isOn: boolean = false;
    private brightness: number = 0;

    turnOn(): void {
        this.isOn = true;
        this.brightness = 100;
        console.log("Light is ON at 100% brightness");
    }

    turnOff(): void {
        this.isOn = false;
        this.brightness = 0;
        console.log("Light is OFF");
    }

    setBrightness(level: number): void {
        this.brightness = level;
        console.log(`Brightness set to ${level}%`);
    }

    getBrightness(): number {
        return this.brightness;
    }
}

class Thermostat {
    private temperature: number = 20;

    setTemperature(temp: number): void {
        this.temperature = temp;
        console.log(`Temperature set to ${temp}°C`);
    }

    getTemperature(): number {
        return this.temperature;
    }
}

// Concrete Commands
class LightOnCommand implements Command {
    private light: Light;

    constructor(light: Light) {
        this.light = light;
    }

    execute(): void {
        this.light.turnOn();
    }

    undo(): void {
        this.light.turnOff();
    }
}

class LightOffCommand implements Command {
    private light: Light;

    constructor(light: Light) {
        this.light = light;
    }

    execute(): void {
        this.light.turnOff();
    }

    undo(): void {
        this.light.turnOn();
    }
}

class SetBrightnessCommand implements Command {
    private light: Light;
    private newBrightness: number;
    private previousBrightness: number;

    constructor(light: Light, brightness: number) {
        this.light = light;
        this.newBrightness = brightness;
        this.previousBrightness = light.getBrightness();
    }

    execute(): void {
        this.previousBrightness = this.light.getBrightness();
        this.light.setBrightness(this.newBrightness);
    }

    undo(): void {
        this.light.setBrightness(this.previousBrightness);
    }
}

class SetTemperatureCommand implements Command {
    private thermostat: Thermostat;
    private newTemperature: number;
    private previousTemperature: number;

    constructor(thermostat: Thermostat, temperature: number) {
        this.thermostat = thermostat;
        this.newTemperature = temperature;
        this.previousTemperature = thermostat.getTemperature();
    }

    execute(): void {
        this.previousTemperature = this.thermostat.getTemperature();
        this.thermostat.setTemperature(this.newTemperature);
    }

    undo(): void {
        this.thermostat.setTemperature(this.previousTemperature);
    }
}

// Macro Command - executes multiple commands
class MacroCommand implements Command {
    private commands: Command[];

    constructor(commands: Command[]) {
        this.commands = commands;
    }

    execute(): void {
        console.log("Executing macro command...");
        for (const command of this.commands) {
            command.execute();
        }
    }

    undo(): void {
        console.log("Undoing macro command...");
        // Undo in reverse order
        for (let i = this.commands.length - 1; i >= 0; i--) {
            this.commands[i].undo();
        }
    }
}

// Invoker: Remote Control
class RemoteControl {
    private history: Command[] = [];
    private currentIndex: number = -1;

    pressButton(command: Command): void {
        // Remove any commands after current index
        this.history = this.history.slice(0, this.currentIndex + 1);

        command.execute();
        this.history.push(command);
        this.currentIndex++;
    }

    pressUndo(): void {
        if (this.currentIndex >= 0) {
            const command = this.history[this.currentIndex];
            command.undo();
            this.currentIndex--;
        } else {
            console.log("Nothing to undo");
        }
    }

    pressRedo(): void {
        if (this.currentIndex < this.history.length - 1) {
            this.currentIndex++;
            const command = this.history[this.currentIndex];
            command.execute();
        } else {
            console.log("Nothing to redo");
        }
    }
}

// Usage
const livingRoomLight = new Light();
const thermostat = new Thermostat();

const remote = new RemoteControl();

// Execute individual commands
remote.pressButton(new LightOnCommand(livingRoomLight));
remote.pressButton(new SetBrightnessCommand(livingRoomLight, 50));
remote.pressButton(new SetTemperatureCommand(thermostat, 22));

// Undo last command
remote.pressUndo();

// Create and execute macro command (scene)
const movieNightScene = new MacroCommand([
    new SetBrightnessCommand(livingRoomLight, 30),
    new SetTemperatureCommand(thermostat, 21)
]);

remote.pressButton(movieNightScene);
remote.pressUndo(); // Undo entire scene
```

#### Java Implementation

```java
// Command Pattern

// Command Interface
public interface Command {
    void execute();
    void undo();
}

// Receiver: Document
public class Document {
    private StringBuilder content;

    public Document() {
        this.content = new StringBuilder();
    }

    public void write(String text) {
        content.append(text);
        System.out.println("Document: " + content);
    }

    public void erase(int length) {
        if (length <= content.length()) {
            content.delete(content.length() - length, content.length());
            System.out.println("Document: " + content);
        }
    }

    public String getContent() {
        return content.toString();
    }
}

// Concrete Commands
public class WriteCommand implements Command {
    private Document document;
    private String text;

    public WriteCommand(Document document, String text) {
        this.document = document;
        this.text = text;
    }

    @Override
    public void execute() {
        document.write(text);
    }

    @Override
    public void undo() {
        document.erase(text.length());
    }
}

public class EraseCommand implements Command {
    private Document document;
    private int length;
    private String erasedText;

    public EraseCommand(Document document, int length) {
        this.document = document;
        this.length = length;
    }

    @Override
    public void execute() {
        String content = document.getContent();
        if (length <= content.length()) {
            erasedText = content.substring(content.length() - length);
            document.erase(length);
        }
    }

    @Override
    public void undo() {
        if (erasedText != null) {
            document.write(erasedText);
        }
    }
}

// Invoker: Command History
public class CommandHistory {
    private List<Command> history = new ArrayList<>();
    private int currentIndex = -1;

    public void executeCommand(Command command) {
        // Remove commands after current index
        while (history.size() > currentIndex + 1) {
            history.remove(history.size() - 1);
        }

        command.execute();
        history.add(command);
        currentIndex++;
    }

    public void undo() {
        if (currentIndex >= 0) {
            Command command = history.get(currentIndex);
            command.undo();
            currentIndex--;
            System.out.println("Undo completed");
        } else {
            System.out.println("Nothing to undo");
        }
    }

    public void redo() {
        if (currentIndex < history.size() - 1) {
            currentIndex++;
            Command command = history.get(currentIndex);
            command.execute();
            System.out.println("Redo completed");
        } else {
            System.out.println("Nothing to redo");
        }
    }
}

// Usage
public class CommandPatternExample {
    public static void main(String[] args) {
        Document document = new Document();
        CommandHistory history = new CommandHistory();

        // Execute commands
        history.executeCommand(new WriteCommand(document, "Hello "));
        history.executeCommand(new WriteCommand(document, "World"));
        history.executeCommand(new WriteCommand(document, "!"));

        // Undo operations
        history.undo(); // Remove "!"
        history.undo(); // Remove "World"

        // Redo operations
        history.redo(); // Add "World" back

        // Erase command
        history.executeCommand(new EraseCommand(document, 5));
    }
}
```

### When to Use

Use Command when:
- You want to parameterize objects with operations
- You want to queue operations, schedule their execution, or execute remotely
- You want to support undo/redo operations
- You want to log changes to replay them later
- You want to structure system around high-level operations built on primitive operations

**Common Use Cases**:
- Undo/redo functionality (text editors, graphics programs)
- Transaction systems (database transactions, financial systems)
- Task queues and job schedulers
- GUI button actions and menu items
- Macro recording and playback
- Remote command execution
- Wizard/multi-step processes

### When NOT to Use

Avoid Command when:
- Operations are simple enough to call directly
- You don't need undo/redo, queuing, or logging
- Creating command objects for every operation adds excessive complexity
- Performance overhead of command objects is unacceptable
- Operations don't have clear parameters to encapsulate

### Real-World Examples

**Text Editor Undo/Redo**:
```python
# Execute text editing commands with full undo/redo support
manager.execute_command(InsertCommand(editor, "Hello"))
manager.undo()  # Remove "Hello"
manager.redo()  # Add "Hello" back
```

**Smart Home Control**:
```typescript
// Control devices with macro commands for scenes
const movieNight = new MacroCommand([
    new SetBrightnessCommand(light, 30),
    new SetTemperatureCommand(thermostat, 21)
]);
remote.pressButton(movieNight);
```

**Transaction System**:
```java
// Execute financial transactions with rollback capability
history.executeCommand(new WriteCommand(document, "Transaction log entry"));
history.undo();  // Rollback transaction
```

### Related Patterns

- **Memento**: Can store state for Command to implement undo
- **Composite**: Macro commands are Composite of commands
- **Prototype**: Commands can be prototyped and cloned
- **Chain of Responsibility**: Commands can be passed along chain

### SOLID Principles

**Single Responsibility Principle**: Each command encapsulates one operation

**Open-Closed Principle**: New commands can be added without modifying existing code

**Dependency Inversion Principle**: Invoker depends on command abstraction, not concrete commands

---

## 15. Iterator Pattern

### Intent

Provide a way to access the elements of an aggregate object sequentially without exposing its underlying representation.

### Problem

You want to access and traverse elements of a collection without exposing its internal structure (list, tree, graph, etc.). Different collections require different traversal algorithms. How do you provide uniform access to different collection types?

### Solution

Create an iterator object that encapsulates the traversal logic. The iterator knows how to traverse the specific collection and provides a uniform interface for accessing elements regardless of the collection's structure.

### Structure

**Key Participants**:
- **Iterator**: Defines interface for accessing and traversing elements
- **ConcreteIterator**: Implements Iterator interface; tracks current position
- **Aggregate**: Defines interface for creating iterator
- **ConcreteAggregate**: Implements iterator creation to return appropriate ConcreteIterator

### Implementation

#### Python Implementation

```python
# Iterator Pattern

from abc import ABC, abstractmethod
from typing import Any, List, Iterator as TypingIterator

# Iterator Interface
class Iterator(ABC):
    """Abstract iterator interface."""

    @abstractmethod
    def has_next(self) -> bool:
        """Check if more elements exist."""
        pass

    @abstractmethod
    def next(self) -> Any:
        """Return next element."""
        pass

    @abstractmethod
    def current(self) -> Any:
        """Return current element without advancing."""
        pass

# Aggregate Interface
class Collection(ABC):
    """Abstract collection interface."""

    @abstractmethod
    def create_iterator(self) -> Iterator:
        """Create iterator for this collection."""
        pass

# Concrete Iterator
class BookShelfIterator(Iterator):
    """Iterator for book collection."""

    def __init__(self, books: List[str]):
        self._books = books
        self._index = 0

    def has_next(self) -> bool:
        return self._index < len(self._books)

    def next(self) -> str:
        if not self.has_next():
            raise StopIteration("No more books")
        book = self._books[self._index]
        self._index += 1
        return book

    def current(self) -> str:
        if self._index == 0:
            raise ValueError("No current book")
        return self._books[self._index - 1]

# Concrete Aggregate
class BookShelf(Collection):
    """Collection of books."""

    def __init__(self):
        self._books: List[str] = []

    def add_book(self, book: str) -> None:
        self._books.append(book)

    def create_iterator(self) -> Iterator:
        return BookShelfIterator(self._books)

    def get_book_count(self) -> int:
        return len(self._books)

# Usage
shelf = BookShelf()
shelf.add_book("Design Patterns")
shelf.add_book("Clean Code")
shelf.add_book("Refactoring")

iterator = shelf.create_iterator()
while iterator.has_next():
    print(iterator.next())

# Practical Example: Tree Iterator (Depth-First)
class TreeNode:
    """Binary tree node."""

    def __init__(self, value: Any, left: 'TreeNode' = None, right: 'TreeNode' = None):
        self.value = value
        self.left = left
        self.right = right

class DepthFirstIterator(Iterator):
    """Depth-first tree iterator using stack."""

    def __init__(self, root: TreeNode):
        self._stack: List[TreeNode] = []
        if root:
            self._stack.append(root)

    def has_next(self) -> bool:
        return len(self._stack) > 0

    def next(self) -> Any:
        if not self.has_next():
            raise StopIteration("No more nodes")

        node = self._stack.pop()

        # Add children (right first so left is processed first)
        if node.right:
            self._stack.append(node.right)
        if node.left:
            self._stack.append(node.left)

        return node.value

    def current(self) -> Any:
        if not self._stack:
            raise ValueError("No current node")
        return self._stack[-1].value

class BreadthFirstIterator(Iterator):
    """Breadth-first tree iterator using queue."""

    def __init__(self, root: TreeNode):
        from collections import deque
        self._queue = deque()
        if root:
            self._queue.append(root)

    def has_next(self) -> bool:
        return len(self._queue) > 0

    def next(self) -> Any:
        if not self.has_next():
            raise StopIteration("No more nodes")

        node = self._queue.popleft()

        # Add children
        if node.left:
            self._queue.append(node.left)
        if node.right:
            self._queue.append(node.right)

        return node.value

    def current(self) -> Any:
        if not self._queue:
            raise ValueError("No current node")
        return self._queue[0].value

class BinaryTree(Collection):
    """Binary tree collection with multiple iterator strategies."""

    def __init__(self, root: TreeNode = None):
        self._root = root

    def create_iterator(self, strategy: str = "depth") -> Iterator:
        """Create iterator with specified strategy."""
        if strategy == "depth":
            return DepthFirstIterator(self._root)
        elif strategy == "breadth":
            return BreadthFirstIterator(self._root)
        else:
            raise ValueError(f"Unknown strategy: {strategy}")

# Build tree:     1
#               /   \
#              2     3
#             / \   /
#            4   5 6

root = TreeNode(1,
    TreeNode(2, TreeNode(4), TreeNode(5)),
    TreeNode(3, TreeNode(6))
)

tree = BinaryTree(root)

print("\nDepth-First Traversal:")
depth_iter = tree.create_iterator("depth")
while depth_iter.has_next():
    print(depth_iter.next())

print("\nBreadth-First Traversal:")
breadth_iter = tree.create_iterator("breadth")
while breadth_iter.has_next():
    print(breadth_iter.next())

# Python's built-in iterator protocol
class PythonicBookShelf:
    """Pythonic collection using __iter__ protocol."""

    def __init__(self):
        self._books: List[str] = []

    def add_book(self, book: str) -> None:
        self._books.append(book)

    def __iter__(self) -> TypingIterator[str]:
        """Return iterator using Python's protocol."""
        return iter(self._books)

    def reverse_iterator(self) -> TypingIterator[str]:
        """Custom iterator for reverse traversal."""
        return reversed(self._books)

# Pythonic usage
pythonic_shelf = PythonicBookShelf()
pythonic_shelf.add_book("Design Patterns")
pythonic_shelf.add_book("Clean Code")

for book in pythonic_shelf:
    print(book)

for book in pythonic_shelf.reverse_iterator():
    print(book)
```

#### TypeScript Implementation

```typescript
// Iterator Pattern

// Iterator Interface
interface Iterator<T> {
    hasNext(): boolean;
    next(): T;
    current(): T;
}

// Aggregate Interface
interface Iterable<T> {
    createIterator(): Iterator<T>;
}

// Concrete Aggregate: Social Network
interface Profile {
    id: string;
    email: string;
    name: string;
    friends: string[];
}

class ProfileIterator implements Iterator<Profile> {
    private profiles: Profile[];
    private currentPosition: number = 0;

    constructor(profiles: Profile[]) {
        this.profiles = profiles;
    }

    hasNext(): boolean {
        return this.currentPosition < this.profiles.length;
    }

    next(): Profile {
        if (!this.hasNext()) {
            throw new Error("No more profiles");
        }
        const profile = this.profiles[this.currentPosition];
        this.currentPosition++;
        return profile;
    }

    current(): Profile {
        if (this.currentPosition === 0) {
            throw new Error("No current profile");
        }
        return this.profiles[this.currentPosition - 1];
    }
}

class SocialNetwork implements Iterable<Profile> {
    private profiles: Map<string, Profile> = new Map();

    addProfile(profile: Profile): void {
        this.profiles.set(profile.id, profile);
    }

    getProfile(id: string): Profile | undefined {
        return this.profiles.get(id);
    }

    createIterator(): Iterator<Profile> {
        return new ProfileIterator(Array.from(this.profiles.values()));
    }

    createFriendsIterator(profileId: string): Iterator<Profile> {
        const profile = this.profiles.get(profileId);
        if (!profile) {
            return new ProfileIterator([]);
        }

        const friends = profile.friends
            .map(friendId => this.profiles.get(friendId))
            .filter((p): p is Profile => p !== undefined);

        return new ProfileIterator(friends);
    }

    createFriendsOfFriendsIterator(profileId: string): Iterator<Profile> {
        const profile = this.profiles.get(profileId);
        if (!profile) {
            return new ProfileIterator([]);
        }

        const friendsOfFriends = new Set<Profile>();

        // Get friends
        const friends = profile.friends
            .map(friendId => this.profiles.get(friendId))
            .filter((p): p is Profile => p !== undefined);

        // Get friends of friends
        for (const friend of friends) {
            for (const friendOfFriendId of friend.friends) {
                const friendOfFriend = this.profiles.get(friendOfFriendId);
                if (friendOfFriend &&
                    friendOfFriend.id !== profileId &&
                    !profile.friends.includes(friendOfFriend.id)) {
                    friendsOfFriends.add(friendOfFriend);
                }
            }
        }

        return new ProfileIterator(Array.from(friendsOfFriends));
    }
}

// Usage
const network = new SocialNetwork();

network.addProfile({
    id: "1",
    email: "alice@example.com",
    name: "Alice",
    friends: ["2", "3"]
});

network.addProfile({
    id: "2",
    email: "bob@example.com",
    name: "Bob",
    friends: ["1", "4"]
});

network.addProfile({
    id: "3",
    email: "charlie@example.com",
    name: "Charlie",
    friends: ["1"]
});

network.addProfile({
    id: "4",
    email: "diana@example.com",
    name: "Diana",
    friends: ["2"]
});

// Iterate through all profiles
console.log("All profiles:");
const allProfilesIterator = network.createIterator();
while (allProfilesIterator.hasNext()) {
    const profile = allProfilesIterator.next();
    console.log(`${profile.name} (${profile.email})`);
}

// Iterate through friends
console.log("\nAlice's friends:");
const friendsIterator = network.createFriendsIterator("1");
while (friendsIterator.hasNext()) {
    const friend = friendsIterator.next();
    console.log(`${friend.name} (${friend.email})`);
}

// Iterate through friends of friends
console.log("\nAlice's friends of friends:");
const friendsOfFriendsIterator = network.createFriendsOfFriendsIterator("1");
while (friendsOfFriendsIterator.hasNext()) {
    const friendOfFriend = friendsOfFriendsIterator.next();
    console.log(`${friendOfFriend.name} (${friendOfFriend.email})`);
}

// TypeScript Generator Function (Modern Approach)
class ModernCollection<T> {
    private items: T[] = [];

    add(item: T): void {
        this.items.push(item);
    }

    // Generator for forward iteration
    *[Symbol.iterator](): Generator<T> {
        for (const item of this.items) {
            yield item;
        }
    }

    // Generator for reverse iteration
    *reverseIterator(): Generator<T> {
        for (let i = this.items.length - 1; i >= 0; i--) {
            yield this.items[i];
        }
    }

    // Generator for filtered iteration
    *filter(predicate: (item: T) => boolean): Generator<T> {
        for (const item of this.items) {
            if (predicate(item)) {
                yield item;
            }
        }
    }
}

// Modern usage with generators
const collection = new ModernCollection<number>();
collection.add(1);
collection.add(2);
collection.add(3);
collection.add(4);
collection.add(5);

console.log("\nForward iteration:");
for (const item of collection) {
    console.log(item);
}

console.log("\nReverse iteration:");
for (const item of collection.reverseIterator()) {
    console.log(item);
}

console.log("\nFiltered iteration (even numbers):");
for (const item of collection.filter(n => n % 2 === 0)) {
    console.log(item);
}
```

#### Java Implementation

```java
// Iterator Pattern

// Iterator Interface
public interface Iterator<T> {
    boolean hasNext();
    T next();
}

// Aggregate Interface
public interface Container<T> {
    Iterator<T> createIterator();
}

// Concrete Aggregate
public class NameRepository implements Container<String> {
    private String[] names = {"Alice", "Bob", "Charlie", "Diana"};

    @Override
    public Iterator<String> createIterator() {
        return new NameIterator();
    }

    // Concrete Iterator (inner class)
    private class NameIterator implements Iterator<String> {
        private int index = 0;

        @Override
        public boolean hasNext() {
            return index < names.length;
        }

        @Override
        public String next() {
            if (!hasNext()) {
                throw new NoSuchElementException("No more names");
            }
            return names[index++];
        }
    }
}

// Usage
public class IteratorPatternExample {
    public static void main(String[] args) {
        NameRepository namesRepository = new NameRepository();

        Iterator<String> iterator = namesRepository.createIterator();
        while (iterator.hasNext()) {
            System.out.println(iterator.next());
        }
    }
}

// Practical Example: Channel Iterator for TV
public class Channel {
    private String name;
    private int channelNumber;

    public Channel(String name, int channelNumber) {
        this.name = name;
        this.channelNumber = channelNumber;
    }

    public String getName() {
        return name;
    }

    public int getChannelNumber() {
        return channelNumber;
    }

    @Override
    public String toString() {
        return channelNumber + ": " + name;
    }
}

public class ChannelCollection implements Container<Channel> {
    private List<Channel> channels = new ArrayList<>();

    public void addChannel(Channel channel) {
        channels.add(channel);
    }

    @Override
    public Iterator<Channel> createIterator() {
        return new ChannelIterator();
    }

    // Iterator that skips channels based on criteria
    public Iterator<Channel> createFilteredIterator(int minChannel, int maxChannel) {
        return new FilteredChannelIterator(minChannel, maxChannel);
    }

    private class ChannelIterator implements Iterator<Channel> {
        private int position = 0;

        @Override
        public boolean hasNext() {
            return position < channels.size();
        }

        @Override
        public Channel next() {
            if (!hasNext()) {
                throw new NoSuchElementException("No more channels");
            }
            return channels.get(position++);
        }
    }

    private class FilteredChannelIterator implements Iterator<Channel> {
        private int position = 0;
        private int minChannel;
        private int maxChannel;

        public FilteredChannelIterator(int minChannel, int maxChannel) {
            this.minChannel = minChannel;
            this.maxChannel = maxChannel;
        }

        @Override
        public boolean hasNext() {
            while (position < channels.size()) {
                Channel channel = channels.get(position);
                if (channel.getChannelNumber() >= minChannel &&
                    channel.getChannelNumber() <= maxChannel) {
                    return true;
                }
                position++;
            }
            return false;
        }

        @Override
        public Channel next() {
            if (!hasNext()) {
                throw new NoSuchElementException("No more channels in range");
            }
            return channels.get(position++);
        }
    }
}

// Usage
ChannelCollection channels = new ChannelCollection();
channels.addChannel(new Channel("BBC", 1));
channels.addChannel(new Channel("CNN", 5));
channels.addChannel(new Channel("ESPN", 10));
channels.addChannel(new Channel("HBO", 15));

System.out.println("All channels:");
Iterator<Channel> allChannels = channels.createIterator();
while (allChannels.hasNext()) {
    System.out.println(allChannels.next());
}

System.out.println("\nChannels 1-10:");
Iterator<Channel> filteredChannels = channels.createFilteredIterator(1, 10);
while (filteredChannels.hasNext()) {
    System.out.println(filteredChannels.next());
}
```

### When to Use

Use Iterator when:
- You want to access collection's contents without exposing internal structure
- You want to support multiple traversals of aggregate objects
- You want to provide uniform interface for traversing different aggregate structures
- Collection structure is complex (tree, graph, etc.) and traversal logic should be separate

**Common Use Cases**:
- Collection traversal (lists, sets, maps)
- Tree/graph traversal (depth-first, breadth-first)
- Database result sets
- File system traversal
- Menu navigation
- Social network friend lists
- Pagination of large datasets

### When NOT to Use

Avoid Iterator when:
- Collection structure is simple and direct access is sufficient
- You only need one type of iteration
- Creating iterator adds unnecessary overhead
- Language provides built-in iteration (for-each loops)
- Collection is modified during iteration (concurrent modification)

### Real-World Examples

**Book Collection**:
```python
# Iterate through books without exposing internal list
shelf = BookShelf()
iterator = shelf.create_iterator()
while iterator.has_next():
    print(iterator.next())
```

**Tree Traversal**:
```python
# Use different traversal strategies without changing tree
tree = BinaryTree(root)
depth_iter = tree.create_iterator("depth")  # DFS
breadth_iter = tree.create_iterator("breadth")  # BFS
```

**Social Network**:
```typescript
// Iterate through friends without exposing profile data structure
const friendsIterator = network.createFriendsIterator("1");
while (friendsIterator.hasNext()) {
    console.log(friendsIterator.next().name);
}
```

### Related Patterns

- **Composite**: Iterators often used to traverse Composite structures
- **Factory Method**: Polymorphic iterators can use Factory Method
- **Memento**: Can use Memento to capture iteration state
- **Visitor**: Can collaborate with Iterator to traverse structure

### SOLID Principles

**Single Responsibility Principle**: Iterator handles traversal; collection handles storage

**Open-Closed Principle**: New iterator types can be added without modifying collection

**Dependency Inversion Principle**: Client depends on iterator interface, not concrete iterators

---

## 16. Mediator Pattern

### Intent

Define an object that encapsulates how a set of objects interact. Mediator promotes loose coupling by keeping objects from referring to each other explicitly, and it lets you vary their interaction independently.

### Problem

Objects that communicate directly become tightly coupled and hard to reuse independently. As the number of objects increases, the communication complexity grows exponentially. How do you reduce coupling between communicating objects?

### Solution

Create a mediator object that encapsulates all communication logic. Objects communicate only with the mediator instead of directly with each other. The mediator coordinates interactions and controls the workflow.

### Structure

**Key Participants**:
- **Mediator**: Defines interface for communicating with Colleague objects
- **ConcreteMediator**: Implements cooperative behavior by coordinating Colleague objects
- **Colleague**: Objects that communicate via Mediator
- **ConcreteColleague**: Communicates with other Colleagues through its Mediator

### Implementation

#### Python Implementation

```python
# Mediator Pattern

from abc import ABC, abstractmethod
from typing import List, Optional
from datetime import datetime

# Mediator Interface
class ChatRoomMediator(ABC):
    """Abstract mediator for chat room."""

    @abstractmethod
    def send_message(self, message: str, user: 'User') -> None:
        """Send message from user."""
        pass

    @abstractmethod
    def add_user(self, user: 'User') -> None:
        """Add user to chat room."""
        pass

# Concrete Mediator
class ChatRoom(ChatRoomMediator):
    """Concrete chat room mediator."""

    def __init__(self, name: str):
        self._name = name
        self._users: List['User'] = []

    def add_user(self, user: 'User') -> None:
        """Add user and notify others."""
        self._users.append(user)
        user.set_chat_room(self)
        self._broadcast(f"{user.get_name()} joined the chat", user)

    def send_message(self, message: str, sender: 'User') -> None:
        """Send message to all users except sender."""
        timestamp = datetime.now().strftime("%H:%M:%S")
        formatted_message = f"[{timestamp}] {sender.get_name()}: {message}"

        for user in self._users:
            if user != sender:
                user.receive(formatted_message)

    def send_private_message(self, message: str, sender: 'User',
                            recipient_name: str) -> None:
        """Send private message to specific user."""
        timestamp = datetime.now().strftime("%H:%M:%S")

        recipient = self._find_user(recipient_name)
        if recipient:
            formatted_message = f"[{timestamp}] {sender.get_name()} (private): {message}"
            recipient.receive(formatted_message)
            sender.receive(f"[{timestamp}] You to {recipient_name} (private): {message}")
        else:
            sender.receive(f"User {recipient_name} not found")

    def _broadcast(self, message: str, exclude_user: Optional['User'] = None) -> None:
        """Broadcast system message."""
        for user in self._users:
            if user != exclude_user:
                user.receive(f"[SYSTEM] {message}")

    def _find_user(self, name: str) -> Optional['User']:
        """Find user by name."""
        for user in self._users:
            if user.get_name() == name:
                return user
        return None

# Colleague
class User:
    """User in chat room."""

    def __init__(self, name: str):
        self._name = name
        self._chat_room: Optional[ChatRoomMediator] = None

    def set_chat_room(self, chat_room: ChatRoomMediator) -> None:
        """Set chat room mediator."""
        self._chat_room = chat_room

    def send(self, message: str) -> None:
        """Send message via mediator."""
        if self._chat_room:
            print(f"{self._name} sends: {message}")
            self._chat_room.send_message(message, self)

    def send_private(self, message: str, recipient: str) -> None:
        """Send private message via mediator."""
        if self._chat_room and isinstance(self._chat_room, ChatRoom):
            self._chat_room.send_private_message(message, self, recipient)

    def receive(self, message: str) -> None:
        """Receive message."""
        print(f"{self._name} receives: {message}")

    def get_name(self) -> str:
        return self._name

# Usage
chat_room = ChatRoom("Developer Chat")

alice = User("Alice")
bob = User("Bob")
charlie = User("Charlie")

chat_room.add_user(alice)
chat_room.add_user(bob)
chat_room.add_user(charlie)

alice.send("Hello everyone!")
bob.send("Hi Alice!")
charlie.send_private("Can we talk?", "Alice")

# Practical Example: Form Mediator
class FormMediator(ABC):
    """Abstract mediator for form validation."""

    @abstractmethod
    def notify(self, component: 'FormComponent', event: str) -> None:
        """Handle component notifications."""
        pass

class RegistrationForm(FormMediator):
    """Concrete form mediator handling complex validation."""

    def __init__(self):
        self._email_field: Optional['TextField'] = None
        self._password_field: Optional['TextField'] = None
        self._confirm_password_field: Optional['TextField'] = None
        self._submit_button: Optional['Button'] = None
        self._terms_checkbox: Optional['Checkbox'] = None

    def register_components(self, email: 'TextField', password: 'TextField',
                          confirm_password: 'TextField', terms: 'Checkbox',
                          submit: 'Button') -> None:
        """Register all form components."""
        self._email_field = email
        self._password_field = password
        self._confirm_password_field = confirm_password
        self._terms_checkbox = terms
        self._submit_button = submit

        # Set mediator for all components
        email.set_mediator(self)
        password.set_mediator(self)
        confirm_password.set_mediator(self)
        terms.set_mediator(self)
        submit.set_mediator(self)

    def notify(self, component: 'FormComponent', event: str) -> None:
        """Coordinate component interactions."""
        if event == "change":
            self._validate_form()
        elif event == "submit":
            if self._is_form_valid():
                print("Form submitted successfully!")
            else:
                print("Please fix validation errors")

    def _validate_form(self) -> None:
        """Validate entire form and update submit button."""
        if self._is_form_valid():
            self._submit_button.enable()
        else:
            self._submit_button.disable()

    def _is_form_valid(self) -> bool:
        """Check if form is valid."""
        # Email validation
        email_valid = "@" in self._email_field.get_value()

        # Password validation
        password = self._password_field.get_value()
        password_valid = len(password) >= 8

        # Password confirmation
        passwords_match = (password ==
                          self._confirm_password_field.get_value())

        # Terms accepted
        terms_accepted = self._terms_checkbox.is_checked()

        # Update component states
        self._email_field.set_valid(email_valid)
        self._password_field.set_valid(password_valid)
        self._confirm_password_field.set_valid(passwords_match)

        return (email_valid and password_valid and
                passwords_match and terms_accepted)

# Form Components (Colleagues)
class FormComponent(ABC):
    """Abstract form component."""

    def __init__(self):
        self._mediator: Optional[FormMediator] = None

    def set_mediator(self, mediator: FormMediator) -> None:
        self._mediator = mediator

class TextField(FormComponent):
    """Text input field."""

    def __init__(self, label: str):
        super().__init__()
        self._label = label
        self._value = ""
        self._is_valid = True

    def set_value(self, value: str) -> None:
        self._value = value
        if self._mediator:
            self._mediator.notify(self, "change")

    def get_value(self) -> str:
        return self._value

    def set_valid(self, valid: bool) -> None:
        self._is_valid = valid
        status = "valid" if valid else "invalid"
        print(f"{self._label}: {status}")

class Checkbox(FormComponent):
    """Checkbox component."""

    def __init__(self, label: str):
        super().__init__()
        self._label = label
        self._checked = False

    def toggle(self) -> None:
        self._checked = not self._checked
        if self._mediator:
            self._mediator.notify(self, "change")

    def is_checked(self) -> bool:
        return self._checked

class Button(FormComponent):
    """Button component."""

    def __init__(self, label: str):
        super().__init__()
        self._label = label
        self._enabled = False

    def click(self) -> None:
        if self._enabled and self._mediator:
            self._mediator.notify(self, "submit")

    def enable(self) -> None:
        self._enabled = True
        print(f"{self._label} button: enabled")

    def disable(self) -> None:
        self._enabled = False
        print(f"{self._label} button: disabled")

# Usage
form = RegistrationForm()

email_field = TextField("Email")
password_field = TextField("Password")
confirm_password_field = TextField("Confirm Password")
terms_checkbox = Checkbox("Terms and Conditions")
submit_button = Button("Submit")

form.register_components(email_field, password_field,
                        confirm_password_field, terms_checkbox, submit_button)

# Simulate user input
email_field.set_value("user@example.com")
password_field.set_value("securepass123")
confirm_password_field.set_value("securepass123")
terms_checkbox.toggle()

# Try to submit
submit_button.click()
```

#### TypeScript Implementation

```typescript
// Mediator Pattern

// Mediator Interface
interface AirTrafficControl {
    registerAircraft(aircraft: Aircraft): void;
    requestLanding(aircraft: Aircraft): boolean;
    requestTakeoff(aircraft: Aircraft): boolean;
    notifyLanded(aircraft: Aircraft): void;
    notifyTookOff(aircraft: Aircraft): void;
}

// Concrete Mediator
class ControlTower implements AirTrafficControl {
    private aircrafts: Set<Aircraft> = new Set();
    private runwayOccupied: boolean = false;
    private landingQueue: Aircraft[] = [];
    private takeoffQueue: Aircraft[] = [];

    registerAircraft(aircraft: Aircraft): void {
        this.aircrafts.add(aircraft);
        aircraft.setControlTower(this);
        console.log(`${aircraft.getCallSign()} registered with control tower`);
    }

    requestLanding(aircraft: Aircraft): boolean {
        if (!this.runwayOccupied) {
            this.runwayOccupied = true;
            console.log(`✓ ${aircraft.getCallSign()} cleared for landing`);
            return true;
        } else {
            this.landingQueue.push(aircraft);
            console.log(`✗ ${aircraft.getCallSign()} holding - runway occupied`);
            return false;
        }
    }

    requestTakeoff(aircraft: Aircraft): boolean {
        if (!this.runwayOccupied && this.landingQueue.length === 0) {
            this.runwayOccupied = true;
            console.log(`✓ ${aircraft.getCallSign()} cleared for takeoff`);
            return true;
        } else {
            this.takeoffQueue.push(aircraft);
            console.log(`✗ ${aircraft.getCallSign()} holding - waiting for clearance`);
            return false;
        }
    }

    notifyLanded(aircraft: Aircraft): void {
        console.log(`${aircraft.getCallSign()} landed successfully`);
        this.runwayOccupied = false;
        this.processNextAircraft();
    }

    notifyTookOff(aircraft: Aircraft): void {
        console.log(`${aircraft.getCallSign()} took off successfully`);
        this.runwayOccupied = false;
        this.processNextAircraft();
    }

    private processNextAircraft(): void {
        // Priority: landing over takeoff
        if (this.landingQueue.length > 0) {
            const nextAircraft = this.landingQueue.shift()!;
            if (this.requestLanding(nextAircraft)) {
                nextAircraft.land();
            }
        } else if (this.takeoffQueue.length > 0) {
            const nextAircraft = this.takeoffQueue.shift()!;
            if (this.requestTakeoff(nextAircraft)) {
                nextAircraft.takeoff();
            }
        }
    }
}

// Colleague
abstract class Aircraft {
    protected controlTower: AirTrafficControl | null = null;
    protected callSign: string;

    constructor(callSign: string) {
        this.callSign = callSign;
    }

    setControlTower(tower: AirTrafficControl): void {
        this.controlTower = tower;
    }

    getCallSign(): string {
        return this.callSign;
    }

    abstract land(): void;
    abstract takeoff(): void;
}

// Concrete Colleagues
class PassengerJet extends Aircraft {
    land(): void {
        if (this.controlTower) {
            const cleared = this.controlTower.requestLanding(this);
            if (cleared) {
                console.log(`${this.callSign} landing...`);
                setTimeout(() => {
                    this.controlTower!.notifyLanded(this);
                }, 2000);
            }
        }
    }

    takeoff(): void {
        if (this.controlTower) {
            const cleared = this.controlTower.requestTakeoff(this);
            if (cleared) {
                console.log(`${this.callSign} taking off...`);
                setTimeout(() => {
                    this.controlTower!.notifyTookOff(this);
                }, 1500);
            }
        }
    }
}

class CargoPlane extends Aircraft {
    land(): void {
        if (this.controlTower) {
            const cleared = this.controlTower.requestLanding(this);
            if (cleared) {
                console.log(`${this.callSign} landing...`);
                setTimeout(() => {
                    this.controlTower!.notifyLanded(this);
                }, 3000);
            }
        }
    }

    takeoff(): void {
        if (this.controlTower) {
            const cleared = this.controlTower.requestTakeoff(this);
            if (cleared) {
                console.log(`${this.callSign} taking off...`);
                setTimeout(() => {
                    this.controlTower!.notifyTookOff(this);
                }, 2500);
            }
        }
    }
}

// Usage
const tower = new ControlTower();

const flight123 = new PassengerJet("Flight 123");
const flight456 = new PassengerJet("Flight 456");
const cargo789 = new CargoPlane("Cargo 789");

tower.registerAircraft(flight123);
tower.registerAircraft(flight456);
tower.registerAircraft(cargo789);

// Multiple aircraft requesting operations
flight123.land();       // Cleared
flight456.land();       // Must wait
cargo789.takeoff();     // Must wait
```

#### Java Implementation

```java
// Mediator Pattern

// Mediator Interface
public interface ChatMediator {
    void sendMessage(String message, User user);
    void addUser(User user);
}

// Concrete Mediator
public class ChatRoomImpl implements ChatMediator {
    private List<User> users;
    private String roomName;

    public ChatRoomImpl(String roomName) {
        this.users = new ArrayList<>();
        this.roomName = roomName;
    }

    @Override
    public void addUser(User user) {
        users.add(user);
        System.out.printf("%s joined %s%n", user.getName(), roomName);
    }

    @Override
    public void sendMessage(String message, User sender) {
        for (User user : users) {
            // Don't send message to sender
            if (user != sender) {
                user.receive(message, sender);
            }
        }
    }
}

// Colleague
public abstract class User {
    protected ChatMediator mediator;
    protected String name;

    public User(ChatMediator mediator, String name) {
        this.mediator = mediator;
        this.name = name;
    }

    public abstract void send(String message);
    public abstract void receive(String message, User sender);

    public String getName() {
        return name;
    }
}

// Concrete Colleague
public class ChatUser extends User {
    public ChatUser(ChatMediator mediator, String name) {
        super(mediator, name);
    }

    @Override
    public void send(String message) {
        System.out.printf("%s sends: %s%n", name, message);
        mediator.sendMessage(message, this);
    }

    @Override
    public void receive(String message, User sender) {
        System.out.printf("%s received from %s: %s%n",
            name, sender.getName(), message);
    }
}

// Usage
public class MediatorPatternExample {
    public static void main(String[] args) {
        ChatMediator chatRoom = new ChatRoomImpl("General Chat");

        User alice = new ChatUser(chatRoom, "Alice");
        User bob = new ChatUser(chatRoom, "Bob");
        User charlie = new ChatUser(chatRoom, "Charlie");

        chatRoom.addUser(alice);
        chatRoom.addUser(bob);
        chatRoom.addUser(charlie);

        alice.send("Hello everyone!");
        bob.send("Hi Alice!");
    }
}
```

### When to Use

Use Mediator when:
- Set of objects communicate in well-defined but complex ways
- Reusing object is difficult because it refers to and communicates with many other objects
- Behavior distributed between several classes should be customizable without lots of subclassing
- You want to reduce coupling between communicating objects

**Common Use Cases**:
- Chat rooms and messaging systems
- UI dialog boxes with interdependent widgets
- Air traffic control systems
- Game event systems
- Form validation with complex field dependencies
- Workflow orchestration
- Component coordination in complex systems

### When NOT to Use

Avoid Mediator when:
- Simple two-object communication is sufficient
- Mediator becomes monolithic "god object" doing too much
- Performance overhead of routing through mediator is unacceptable
- Objects rarely interact and coupling is minimal
- Direct communication is clearer and simpler

### Real-World Examples

**Chat Room**:
```python
# Users communicate through chat room mediator
alice.send("Hello!")  # Mediator routes to all other users
charlie.send_private("Hi", "Alice")  # Mediator routes to specific user
```

**Form Validation**:
```python
# Form mediator coordinates field validation
email_field.set_value("user@example.com")
# Mediator validates email and enables/disables submit button
```

**Air Traffic Control**:
```typescript
// Aircraft communicate through control tower
flight123.land()  // Tower manages runway access
flight456.land()  // Tower queues request
```

### Related Patterns

- **Observer**: Mediator differs by encapsulating communication vs. distributing it
- **Facade**: Simplifies interface; Mediator adds functionality and coordination
- **Command**: Mediator can use Command to represent requests between colleagues

### SOLID Principles

**Single Responsibility Principle**: Mediator has one job—coordinate colleague communication

**Open-Closed Principle**: New colleagues can be added without modifying mediator interface

**Dependency Inversion Principle**: Colleagues depend on mediator abstraction, not concrete mediator

---

## 17. Memento Pattern

### Intent

Without violating encapsulation, capture and externalize an object's internal state so that the object can be restored to this state later.

### Problem

You need to save and restore an object's state for undo/redo functionality, checkpoints, or rollback operations. However, exposing the object's internal state violates encapsulation. How do you save and restore state without exposing implementation details?

### Solution

Create a memento object that stores a snapshot of the originator's state. Only the originator can create and restore from mementos. A caretaker stores mementos but never examines or operates on their contents.

### Structure

**Key Participants**:
- **Memento**: Stores internal state of Originator; protects against access by objects other than Originator
- **Originator**: Creates memento containing snapshot of current state; uses memento to restore state
- **Caretaker**: Responsible for memento's safekeeping; never operates on or examines memento contents

### Implementation

#### Python Implementation

```python
# Memento Pattern

from typing import List, Optional
from dataclasses import dataclass, field
from copy import deepcopy

# Memento
@dataclass(frozen=True)
class EditorMemento:
    """Memento storing editor state."""

    content: str
    cursor_position: int
    selection_start: Optional[int] = None
    selection_end: Optional[int] = None

    def __repr__(self) -> str:
        return f"Snapshot(cursor={self.cursor_position}, length={len(self.content)})"

# Originator
class TextEditor:
    """Text editor that can save and restore state."""

    def __init__(self):
        self._content: str = ""
        self._cursor_position: int = 0
        self._selection_start: Optional[int] = None
        self._selection_end: Optional[int] = None

    def write(self, text: str) -> None:
        """Write text at cursor position."""
        self._content = (self._content[:self._cursor_position] +
                        text +
                        self._content[self._cursor_position:])
        self._cursor_position += len(text)
        print(f"Content: '{self._content}'")

    def delete(self, length: int) -> None:
        """Delete text before cursor."""
        start = max(0, self._cursor_position - length)
        self._content = (self._content[:start] +
                        self._content[self._cursor_position:])
        self._cursor_position = start
        print(f"Content: '{self._content}'")

    def set_cursor(self, position: int) -> None:
        """Set cursor position."""
        self._cursor_position = max(0, min(position, len(self._content)))

    def save(self) -> EditorMemento:
        """Create memento of current state."""
        return EditorMemento(
            content=self._content,
            cursor_position=self._cursor_position,
            selection_start=self._selection_start,
            selection_end=self._selection_end
        )

    def restore(self, memento: EditorMemento) -> None:
        """Restore state from memento."""
        self._content = memento.content
        self._cursor_position = memento.cursor_position
        self._selection_start = memento.selection_start
        self._selection_end = memento.selection_end
        print(f"Restored to: '{self._content}'")

    def get_content(self) -> str:
        return self._content

# Caretaker
class EditorHistory:
    """Manages editor undo/redo history."""

    def __init__(self, editor: TextEditor):
        self._editor = editor
        self._history: List[EditorMemento] = []
        self._current_index: int = -1

    def backup(self) -> None:
        """Save current state to history."""
        # Remove any states after current index
        self._history = self._history[:self._current_index + 1]

        memento = self._editor.save()
        self._history.append(memento)
        self._current_index += 1
        print(f"Saved state: {memento}")

    def undo(self) -> None:
        """Restore previous state."""
        if self._current_index > 0:
            self._current_index -= 1
            memento = self._history[self._current_index]
            self._editor.restore(memento)
        else:
            print("Nothing to undo")

    def redo(self) -> None:
        """Restore next state."""
        if self._current_index < len(self._history) - 1:
            self._current_index += 1
            memento = self._history[self._current_index]
            self._editor.restore(memento)
        else:
            print("Nothing to redo")

    def show_history(self) -> None:
        """Display history."""
        print("\nHistory:")
        for i, memento in enumerate(self._history):
            marker = " <--" if i == self._current_index else ""
            print(f"  {i}: {memento}{marker}")

# Usage
editor = TextEditor()
history = EditorHistory(editor)

# Make changes with backups
history.backup()
editor.write("Hello")

history.backup()
editor.write(" World")

history.backup()
editor.write("!")

# Undo changes
history.undo()
history.undo()

# Redo changes
history.redo()

history.show_history()

# Practical Example: Game Checkpoint System
@dataclass(frozen=True)
class GameMemento:
    """Memento for game state."""

    level: int
    health: int
    score: int
    position_x: int
    position_y: int
    inventory: List[str] = field(default_factory=list)

class Game:
    """Game with checkpoint system."""

    def __init__(self):
        self._level = 1
        self._health = 100
        self._score = 0
        self._position_x = 0
        self._position_y = 0
        self._inventory: List[str] = []

    def play(self, actions: str) -> None:
        """Simulate gameplay."""
        print(f"Playing: {actions}")
        # Simulate changes
        self._score += 100
        self._position_x += 10
        self._health -= 20

    def collect_item(self, item: str) -> None:
        """Add item to inventory."""
        self._inventory.append(item)
        print(f"Collected: {item}")

    def complete_level(self) -> None:
        """Advance to next level."""
        self._level += 1
        self._health = 100  # Restore health
        print(f"Level {self._level} unlocked!")

    def save_checkpoint(self) -> GameMemento:
        """Create checkpoint."""
        return GameMemento(
            level=self._level,
            health=self._health,
            score=self._score,
            position_x=self._position_x,
            position_y=self._position_y,
            inventory=deepcopy(self._inventory)
        )

    def load_checkpoint(self, memento: GameMemento) -> None:
        """Load from checkpoint."""
        self._level = memento.level
        self._health = memento.health
        self._score = memento.score
        self._position_x = memento.position_x
        self._position_y = memento.position_y
        self._inventory = deepcopy(memento.inventory)
        print(f"Checkpoint loaded: Level {self._level}, Health {self._health}")

    def display_status(self) -> None:
        """Show current game state."""
        print(f"\nGame Status:")
        print(f"  Level: {self._level}")
        print(f"  Health: {self._health}")
        print(f"  Score: {self._score}")
        print(f"  Position: ({self._position_x}, {self._position_y})")
        print(f"  Inventory: {self._inventory}")

class CheckpointManager:
    """Manages game checkpoints."""

    def __init__(self):
        self._checkpoints: dict[str, GameMemento] = {}

    def save_checkpoint(self, game: Game, name: str) -> None:
        """Save named checkpoint."""
        checkpoint = game.save_checkpoint()
        self._checkpoints[name] = checkpoint
        print(f"Checkpoint '{name}' saved")

    def load_checkpoint(self, game: Game, name: str) -> None:
        """Load named checkpoint."""
        if name in self._checkpoints:
            game.load_checkpoint(self._checkpoints[name])
        else:
            print(f"Checkpoint '{name}' not found")

    def list_checkpoints(self) -> None:
        """List all checkpoints."""
        print("\nSaved Checkpoints:")
        for name, checkpoint in self._checkpoints.items():
            print(f"  {name}: Level {checkpoint.level}, Score {checkpoint.score}")

# Usage
game = Game()
checkpoint_manager = CheckpointManager()

# Play and save checkpoints
game.display_status()

game.collect_item("Sword")
game.play("Fight monster")
checkpoint_manager.save_checkpoint(game, "before_boss")

game.play("Boss fight")
game.collect_item("Shield")
game.complete_level()
checkpoint_manager.save_checkpoint(game, "after_level_1")

game.display_status()

# Load previous checkpoint (player died)
checkpoint_manager.load_checkpoint(game, "before_boss")
game.display_status()

checkpoint_manager.list_checkpoints()
```

#### TypeScript Implementation

```typescript
// Memento Pattern

// Memento
class DocumentMemento {
    private readonly content: string;
    private readonly title: string;
    private readonly timestamp: Date;

    constructor(content: string, title: string) {
        this.content = content;
        this.title = title;
        this.timestamp = new Date();
    }

    getContent(): string {
        return this.content;
    }

    getTitle(): string {
        return this.title;
    }

    getTimestamp(): Date {
        return this.timestamp;
    }

    toString(): string {
        const time = this.timestamp.toLocaleTimeString();
        return `"${this.title}" at ${time}`;
    }
}

// Originator
class Document {
    private content: string = "";
    private title: string = "Untitled";

    setContent(content: string): void {
        this.content = content;
        console.log(`Content updated: "${content.substring(0, 20)}..."`);
    }

    setTitle(title: string): void {
        this.title = title;
        console.log(`Title updated: "${title}"`);
    }

    getContent(): string {
        return this.content;
    }

    getTitle(): string {
        return this.title;
    }

    save(): DocumentMemento {
        console.log("Creating document snapshot");
        return new DocumentMemento(this.content, this.title);
    }

    restore(memento: DocumentMemento): void {
        this.content = memento.getContent();
        this.title = memento.getTitle();
        console.log(`Restored: ${memento.toString()}`);
    }

    display(): void {
        console.log(`\nDocument: ${this.title}`);
        console.log(`Content: ${this.content}`);
    }
}

// Caretaker
class DocumentHistory {
    private history: DocumentMemento[] = [];
    private currentIndex: number = -1;

    save(document: Document): void {
        // Remove any snapshots after current index
        this.history = this.history.slice(0, this.currentIndex + 1);

        const memento = document.save();
        this.history.push(memento);
        this.currentIndex++;
    }

    undo(document: Document): void {
        if (this.currentIndex > 0) {
            this.currentIndex--;
            const memento = this.history[this.currentIndex];
            document.restore(memento);
        } else {
            console.log("Nothing to undo");
        }
    }

    redo(document: Document): void {
        if (this.currentIndex < this.history.length - 1) {
            this.currentIndex++;
            const memento = this.history[this.currentIndex];
            document.restore(memento);
        } else {
            console.log("Nothing to redo");
        }
    }

    showHistory(): void {
        console.log("\nDocument History:");
        this.history.forEach((memento, index) => {
            const marker = index === this.currentIndex ? " <--" : "";
            console.log(`  ${index}: ${memento}${marker}`);
        });
    }
}

// Usage
const document = new Document();
const history = new DocumentHistory();

// Make changes with saves
history.save(document);

document.setTitle("My Document");
document.setContent("Hello World");
history.save(document);

document.setContent("Hello World! This is a test.");
history.save(document);

document.setContent("Final version of the document.");
history.save(document);

document.display();

// Undo changes
history.undo(document);
history.undo(document);

document.display();

// Redo change
history.redo(document);

history.showHistory();

// Practical Example: Form State Management
interface FormData {
    username: string;
    email: string;
    age: number;
}

class FormMemento {
    private readonly state: FormData;
    private readonly timestamp: Date;

    constructor(state: FormData) {
        // Deep copy to prevent external modification
        this.state = { ...state };
        this.timestamp = new Date();
    }

    getState(): FormData {
        return { ...this.state };
    }

    getTimestamp(): Date {
        return this.timestamp;
    }
}

class Form {
    private formData: FormData = {
        username: "",
        email: "",
        age: 0
    };

    setUsername(username: string): void {
        this.formData.username = username;
    }

    setEmail(email: string): void {
        this.formData.email = email;
    }

    setAge(age: number): void {
        this.formData.age = age;
    }

    getFormData(): FormData {
        return { ...this.formData };
    }

    createMemento(): FormMemento {
        return new FormMemento(this.formData);
    }

    restoreFromMemento(memento: FormMemento): void {
        this.formData = memento.getState();
        console.log("Form state restored");
    }

    display(): void {
        console.log("\nCurrent Form:");
        console.log(`  Username: ${this.formData.username}`);
        console.log(`  Email: ${this.formData.email}`);
        console.log(`  Age: ${this.formData.age}`);
    }
}

class FormHistory {
    private snapshots: Map<string, FormMemento> = new Map();

    saveSnapshot(form: Form, name: string): void {
        const memento = form.createMemento();
        this.snapshots.set(name, memento);
        console.log(`Snapshot "${name}" saved`);
    }

    loadSnapshot(form: Form, name: string): void {
        const memento = this.snapshots.get(name);
        if (memento) {
            form.restoreFromMemento(memento);
        } else {
            console.log(`Snapshot "${name}" not found`);
        }
    }

    listSnapshots(): void {
        console.log("\nSaved Snapshots:");
        this.snapshots.forEach((memento, name) => {
            const time = memento.getTimestamp().toLocaleTimeString();
            console.log(`  ${name} (saved at ${time})`);
        });
    }
}

// Usage
const form = new Form();
const formHistory = new FormHistory();

// Fill form and save snapshot
form.setUsername("john_doe");
form.setEmail("john@example.com");
form.setAge(25);
formHistory.saveSnapshot(form, "initial_data");

// Modify form
form.setEmail("john.doe@example.com");
form.setAge(26);
formHistory.saveSnapshot(form, "updated_data");

form.display();

// Restore previous snapshot
formHistory.loadSnapshot(form, "initial_data");
form.display();

formHistory.listSnapshots();
```

#### Java Implementation

```java
// Memento Pattern

// Memento
public class Memento {
    private final String state;
    private final long timestamp;

    public Memento(String state) {
        this.state = state;
        this.timestamp = System.currentTimeMillis();
    }

    public String getState() {
        return state;
    }

    public long getTimestamp() {
        return timestamp;
    }

    @Override
    public String toString() {
        return String.format("State at %d: %s", timestamp, state);
    }
}

// Originator
public class TextArea {
    private String text;

    public void setText(String text) {
        this.text = text;
        System.out.println("Text set to: " + text);
    }

    public String getText() {
        return text;
    }

    public Memento save() {
        System.out.println("Saving state...");
        return new Memento(text);
    }

    public void restore(Memento memento) {
        text = memento.getState();
        System.out.println("State restored to: " + text);
    }
}

// Caretaker
public class TextEditor {
    private Stack<Memento> history = new Stack<>();
    private Stack<Memento> redoStack = new Stack<>();

    public void save(TextArea textArea) {
        Memento memento = textArea.save();
        history.push(memento);
        redoStack.clear(); // Clear redo stack on new save
    }

    public void undo(TextArea textArea) {
        if (!history.isEmpty()) {
            Memento currentState = textArea.save();
            redoStack.push(currentState);

            Memento previousState = history.pop();
            textArea.restore(previousState);
        } else {
            System.out.println("Nothing to undo");
        }
    }

    public void redo(TextArea textArea) {
        if (!redoStack.isEmpty()) {
            Memento nextState = redoStack.pop();
            history.push(textArea.save());
            textArea.restore(nextState);
        } else {
            System.out.println("Nothing to redo");
        }
    }

    public void showHistory() {
        System.out.println("\nHistory:");
        for (int i = 0; i < history.size(); i++) {
            System.out.println("  " + i + ": " + history.get(i));
        }
    }
}

// Usage
public class MementoPatternExample {
    public static void main(String[] args) {
        TextArea textArea = new TextArea();
        TextEditor editor = new TextEditor();

        // Make changes with saves
        textArea.setText("Version 1");
        editor.save(textArea);

        textArea.setText("Version 2");
        editor.save(textArea);

        textArea.setText("Version 3");
        editor.save(textArea);

        // Undo
        editor.undo(textArea);
        editor.undo(textArea);

        // Redo
        editor.redo(textArea);

        editor.showHistory();
    }
}
```

### When to Use

Use Memento when:
- You need to save and restore object state for undo/redo
- Direct access to state would expose implementation details and break encapsulation
- You need checkpoints or rollback capability
- State must be saved at specific points in time

**Common Use Cases**:
- Undo/redo functionality (text editors, graphics programs)
- Checkpoints in games
- Transaction rollback
- Version control systems
- Snapshot and restore features
- Form autosave
- Database transaction savepoints

### When NOT to Use

Avoid Memento when:
- State is simple and exposing it doesn't violate encapsulation
- Saving/restoring state is expensive (memory or performance)
- State is too large to copy frequently
- Full serialization is more appropriate
- State changes are too frequent for snapshots

### Real-World Examples

**Text Editor Undo**:
```python
# Save editor state for undo/redo
history.backup()  # Save current state
editor.write("Hello")
history.undo()  # Restore previous state
```

**Game Checkpoint**:
```python
# Save game progress at checkpoints
checkpoint_manager.save_checkpoint(game, "before_boss")
# ... player dies ...
checkpoint_manager.load_checkpoint(game, "before_boss")
```

**Form Autosave**:
```typescript
// Save form state to restore after refresh
formHistory.saveSnapshot(form, "autosave");
// ... page refresh ...
formHistory.loadSnapshot(form, "autosave");
```

### Related Patterns

- **Command**: Can use Memento to implement undo by storing state before execution
- **Iterator**: Memento can store iteration state
- **Prototype**: Memento can use cloning instead of explicit state storage

### SOLID Principles

**Single Responsibility Principle**: Memento stores state; Originator manages business logic; Caretaker manages history

**Open-Closed Principle**: New memento types can be added without modifying originator

**Dependency Inversion Principle**: Caretaker depends on memento abstraction, not concrete implementation

---

## 18. Observer Pattern

### Intent

Define a one-to-many dependency between objects so that when one object changes state, all its dependents are notified and updated automatically.

### Problem

You have an object (subject) whose state changes, and multiple other objects (observers) need to be notified when those changes occur. Hard-coding these notifications creates tight coupling and makes the system difficult to maintain and extend. How do you allow objects to be notified of state changes without creating dependencies?

### Solution

Define a subscription mechanism where observers can register/unregister to receive notifications from a subject. When the subject's state changes, it automatically notifies all registered observers by calling their update methods.

### Structure

**Key Participants**:
- **Subject**: Knows its observers; provides interface to attach/detach observers; sends notifications to observers
- **Observer**: Defines updating interface for objects that should be notified of changes
- **ConcreteSubject**: Stores state of interest; sends notification when state changes
- **ConcreteObserver**: Implements Observer interface; maintains reference to ConcreteSubject; keeps state consistent with subject

### Implementation

#### Python Implementation

```python
# Observer Pattern

from abc import ABC, abstractmethod
from typing import List, Protocol

# Observer Interface
class Observer(ABC):
    """Abstract observer interface."""

    @abstractmethod
    def update(self, subject: 'Subject') -> None:
        """Receive update from subject."""
        pass

# Subject Interface
class Subject(ABC):
    """Abstract subject interface."""

    def __init__(self):
        self._observers: List[Observer] = []

    def attach(self, observer: Observer) -> None:
        """Attach an observer."""
        if observer not in self._observers:
            self._observers.append(observer)
            print(f"Observer {observer.__class__.__name__} attached")

    def detach(self, observer: Observer) -> None:
        """Detach an observer."""
        if observer in self._observers:
            self._observers.remove(observer)
            print(f"Observer {observer.__class__.__name__} detached")

    def notify(self) -> None:
        """Notify all observers."""
        print(f"Notifying {len(self._observers)} observers...")
        for observer in self._observers:
            observer.update(self)

# Concrete Subject: Weather Station
class WeatherStation(Subject):
    """Weather station that notifies observers of weather changes."""

    def __init__(self):
        super().__init__()
        self._temperature: float = 0.0
        self._humidity: float = 0.0
        self._pressure: float = 0.0

    def set_measurements(self, temperature: float, humidity: float, pressure: float) -> None:
        """Update weather measurements and notify observers."""
        self._temperature = temperature
        self._humidity = humidity
        self._pressure = pressure
        print(f"\nWeather updated: {temperature}°C, {humidity}% humidity, {pressure} hPa")
        self.notify()

    def get_temperature(self) -> float:
        return self._temperature

    def get_humidity(self) -> float:
        return self._humidity

    def get_pressure(self) -> float:
        return self._pressure

# Concrete Observers
class CurrentConditionsDisplay(Observer):
    """Display showing current conditions."""

    def update(self, subject: Subject) -> None:
        """Update display with current conditions."""
        if isinstance(subject, WeatherStation):
            print(f"Current Conditions: {subject.get_temperature()}°C, "
                  f"{subject.get_humidity()}% humidity")

class StatisticsDisplay(Observer):
    """Display showing weather statistics."""

    def __init__(self):
        self._temperatures: List[float] = []

    def update(self, subject: Subject) -> None:
        """Update statistics with new temperature."""
        if isinstance(subject, WeatherStation):
            temp = subject.get_temperature()
            self._temperatures.append(temp)
            avg_temp = sum(self._temperatures) / len(self._temperatures)
            print(f"Statistics: Avg temp = {avg_temp:.1f}°C, "
                  f"Min = {min(self._temperatures):.1f}°C, "
                  f"Max = {max(self._temperatures):.1f}°C")

class ForecastDisplay(Observer):
    """Display showing weather forecast."""

    def __init__(self):
        self._last_pressure: float = 0.0

    def update(self, subject: Subject) -> None:
        """Update forecast based on pressure changes."""
        if isinstance(subject, WeatherStation):
            current_pressure = subject.get_pressure()
            if current_pressure > self._last_pressure:
                print("Forecast: Improving weather on the way!")
            elif current_pressure < self._last_pressure:
                print("Forecast: Watch out for cooler, rainy weather")
            else:
                print("Forecast: More of the same")
            self._last_pressure = current_pressure

# Usage
weather_station = WeatherStation()

current_display = CurrentConditionsDisplay()
statistics_display = StatisticsDisplay()
forecast_display = ForecastDisplay()

# Register observers
weather_station.attach(current_display)
weather_station.attach(statistics_display)
weather_station.attach(forecast_display)

# Update weather (all observers notified)
weather_station.set_measurements(25.0, 65.0, 1013.0)
weather_station.set_measurements(27.0, 70.0, 1015.0)

# Unregister an observer
weather_station.detach(forecast_display)

weather_station.set_measurements(23.0, 60.0, 1012.0)

# Practical Example: Stock Ticker
class Stock(Subject):
    """Stock that notifies observers of price changes."""

    def __init__(self, symbol: str, price: float):
        super().__init__()
        self._symbol = symbol
        self._price = price

    def set_price(self, price: float) -> None:
        """Update stock price and notify observers."""
        old_price = self._price
        self._price = price
        print(f"\n{self._symbol} price changed: ${old_price:.2f} → ${price:.2f}")
        self.notify()

    @property
    def symbol(self) -> str:
        return self._symbol

    @property
    def price(self) -> float:
        return self._price

class StockTrader(Observer):
    """Trader that reacts to stock price changes."""

    def __init__(self, name: str):
        self._name = name

    def update(self, subject: Subject) -> None:
        """React to stock price changes."""
        if isinstance(subject, Stock):
            print(f"[Trader {self._name}] {subject.symbol} is now ${subject.price:.2f}")
            if subject.price > 150:
                print(f"[Trader {self._name}] Selling {subject.symbol}!")
            elif subject.price < 100:
                print(f"[Trader {self._name}] Buying {subject.symbol}!")

class StockAlert(Observer):
    """Alert system for stock price thresholds."""

    def __init__(self, threshold: float):
        self._threshold = threshold

    def update(self, subject: Subject) -> None:
        """Send alert if price crosses threshold."""
        if isinstance(subject, Stock):
            if subject.price >= self._threshold:
                print(f"[ALERT] {subject.symbol} reached threshold: ${subject.price:.2f}")

# Usage
apple_stock = Stock("AAPL", 120.0)

trader1 = StockTrader("Alice")
trader2 = StockTrader("Bob")
alert = StockAlert(150.0)

apple_stock.attach(trader1)
apple_stock.attach(trader2)
apple_stock.attach(alert)

apple_stock.set_price(155.0)  # Triggers alert and sell actions
apple_stock.set_price(95.0)   # Triggers buy actions
```

#### TypeScript Implementation

```typescript
// Observer Pattern

// Observer Interface
interface Observer {
    update(subject: Subject): void;
}

// Subject Interface
abstract class Subject {
    private observers: Observer[] = [];

    attach(observer: Observer): void {
        const index = this.observers.indexOf(observer);
        if (index === -1) {
            this.observers.push(observer);
            console.log(`Observer ${observer.constructor.name} attached`);
        }
    }

    detach(observer: Observer): void {
        const index = this.observers.indexOf(observer);
        if (index !== -1) {
            this.observers.splice(index, 1);
            console.log(`Observer ${observer.constructor.name} detached`);
        }
    }

    notify(): void {
        console.log(`Notifying ${this.observers.length} observers...`);
        for (const observer of this.observers) {
            observer.update(this);
        }
    }
}

// Concrete Subject: Event System
class EventPublisher extends Subject {
    private eventName: string = "";
    private eventData: any = null;

    publishEvent(name: string, data: any): void {
        this.eventName = name;
        this.eventData = data;
        console.log(`\nEvent published: ${name}`);
        this.notify();
    }

    getEventName(): string {
        return this.eventName;
    }

    getEventData(): any {
        return this.eventData;
    }
}

// Concrete Observers
class EmailNotifier implements Observer {
    private email: string;

    constructor(email: string) {
        this.email = email;
    }

    update(subject: Subject): void {
        if (subject instanceof EventPublisher) {
            console.log(`[Email to ${this.email}] ${subject.getEventName()}: ` +
                       JSON.stringify(subject.getEventData()));
        }
    }
}

class Logger implements Observer {
    update(subject: Subject): void {
        if (subject instanceof EventPublisher) {
            const timestamp = new Date().toISOString();
            console.log(`[Log ${timestamp}] ${subject.getEventName()}: ` +
                       JSON.stringify(subject.getEventData()));
        }
    }
}

class AnalyticsTracker implements Observer {
    update(subject: Subject): void {
        if (subject instanceof EventPublisher) {
            console.log(`[Analytics] Tracked event: ${subject.getEventName()}`);
        }
    }
}

// Usage
const publisher = new EventPublisher();

const emailer = new EmailNotifier("admin@example.com");
const logger = new Logger();
const analytics = new AnalyticsTracker();

publisher.attach(emailer);
publisher.attach(logger);
publisher.attach(analytics);

// Publish events
publisher.publishEvent("user.signup", { userId: 123, email: "user@example.com" });
publisher.publishEvent("order.placed", { orderId: 456, total: 99.99 });

// Detach observer
publisher.detach(emailer);

publisher.publishEvent("product.viewed", { productId: 789 });

// Practical Example: UI Component Updates
interface DataObserver {
    onDataChange(data: any): void;
}

class DataModel {
    private observers: DataObserver[] = [];
    private data: any;

    subscribe(observer: DataObserver): void {
        this.observers.push(observer);
    }

    unsubscribe(observer: DataObserver): void {
        const index = this.observers.indexOf(observer);
        if (index !== -1) {
            this.observers.splice(index, 1);
        }
    }

    setData(data: any): void {
        this.data = data;
        this.notifyObservers();
    }

    getData(): any {
        return this.data;
    }

    private notifyObservers(): void {
        for (const observer of this.observers) {
            observer.onDataChange(this.data);
        }
    }
}

class TableView implements DataObserver {
    onDataChange(data: any): void {
        console.log("[Table View] Rendering table with data:", data);
    }
}

class ChartView implements DataObserver {
    onDataChange(data: any): void {
        console.log("[Chart View] Updating chart with data:", data);
    }
}

// Usage
const model = new DataModel();
const table = new TableView();
const chart = new ChartView();

model.subscribe(table);
model.subscribe(chart);

model.setData({ sales: [100, 200, 150] });  // Both views update
```

#### Java Implementation

```java
// Observer Pattern

import java.util.ArrayList;
import java.util.List;

// Observer Interface
interface Observer {
    void update(Subject subject);
}

// Subject Interface
abstract class Subject {
    private List<Observer> observers = new ArrayList<>();

    public void attach(Observer observer) {
        if (!observers.contains(observer)) {
            observers.add(observer);
            System.out.println("Observer " + observer.getClass().getSimpleName() + " attached");
        }
    }

    public void detach(Observer observer) {
        if (observers.remove(observer)) {
            System.out.println("Observer " + observer.getClass().getSimpleName() + " detached");
        }
    }

    protected void notifyObservers() {
        System.out.println("Notifying " + observers.size() + " observers...");
        for (Observer observer : observers) {
            observer.update(this);
        }
    }
}

// Concrete Subject: News Agency
public class NewsAgency extends Subject {
    private String news;
    private String category;

    public void setNews(String news, String category) {
        this.news = news;
        this.category = category;
        System.out.println("\nNews published: [" + category + "] " + news);
        notifyObservers();
    }

    public String getNews() {
        return news;
    }

    public String getCategory() {
        return category;
    }
}

// Concrete Observers
public class NewsChannel implements Observer {
    private String channelName;

    public NewsChannel(String channelName) {
        this.channelName = channelName;
    }

    @Override
    public void update(Subject subject) {
        if (subject instanceof NewsAgency) {
            NewsAgency agency = (NewsAgency) subject;
            System.out.println("[" + channelName + "] Breaking news: " + agency.getNews());
        }
    }
}

public class MobileApp implements Observer {
    private String appName;

    public MobileApp(String appName) {
        this.appName = appName;
    }

    @Override
    public void update(Subject subject) {
        if (subject instanceof NewsAgency) {
            NewsAgency agency = (NewsAgency) subject;
            System.out.println("[" + appName + " App] Push notification: " +
                             agency.getCategory() + " - " + agency.getNews());
        }
    }
}

public class EmailSubscriber implements Observer {
    private String email;
    private String interestedCategory;

    public EmailSubscriber(String email, String interestedCategory) {
        this.email = email;
        this.interestedCategory = interestedCategory;
    }

    @Override
    public void update(Subject subject) {
        if (subject instanceof NewsAgency) {
            NewsAgency agency = (NewsAgency) subject;
            // Only notify if category matches interest
            if (agency.getCategory().equals(interestedCategory)) {
                System.out.println("[Email to " + email + "] " + agency.getNews());
            }
        }
    }
}

// Usage
public class ObserverPatternExample {
    public static void main(String[] args) {
        NewsAgency agency = new NewsAgency();

        NewsChannel cnn = new NewsChannel("CNN");
        MobileApp newsApp = new MobileApp("NewsHub");
        EmailSubscriber sportsSubscriber = new EmailSubscriber("fan@example.com", "Sports");
        EmailSubscriber techSubscriber = new EmailSubscriber("geek@example.com", "Technology");

        agency.attach(cnn);
        agency.attach(newsApp);
        agency.attach(sportsSubscriber);
        agency.attach(techSubscriber);

        // Publish news (all observers notified)
        agency.setNews("Team wins championship!", "Sports");
        agency.setNews("New AI breakthrough announced", "Technology");

        // Detach an observer
        agency.detach(newsApp);

        agency.setNews("Stock market hits record high", "Finance");
    }
}
```

### When to Use

Use Observer when:
- A change to one object requires changing others, and you don't know how many objects need to change
- An object should notify other objects without making assumptions about who those objects are
- You need loose coupling between objects (subject doesn't know concrete observers)
- You want to establish one-to-many dependencies dynamically

**Common Use Cases**:
- Event handling systems (GUI frameworks, DOM events)
- Model-View-Controller (MVC) architecture
- Publish-subscribe messaging systems
- Real-time data feeds (stock tickers, sports scores)
- Social media notifications
- Logging and monitoring systems
- Reactive programming frameworks

### When NOT to Use

Avoid Observer when:
- Observers need to know the order of notification
- Updates are too frequent and cause performance issues
- Dependencies between observers create complex chains
- Simple callbacks or direct method calls suffice
- Memory leaks from forgotten observer registrations are a concern

### Real-World Examples

**Weather Station**:
```python
# Multiple displays update automatically when weather changes
weather_station.set_measurements(25.0, 65.0, 1013.0)
# CurrentConditionsDisplay, StatisticsDisplay, and ForecastDisplay all update
```

**Stock Trading**:
```typescript
// Traders and alert systems react to stock price changes
apple_stock.set_price(155.0);
// Triggers alerts and trading decisions automatically
```

**News Agency**:
```java
// News channels, apps, and email subscribers receive updates
agency.setNews("Breaking news!", "Sports");
// All registered observers notified immediately
```

### Related Patterns

- **Mediator**: Mediator uses centralized control; Observer uses distributed notification
- **Singleton**: Subject is often implemented as Singleton
- **Command**: Can use Observer to notify of command execution
- **Memento**: Observer can trigger creation of Memento snapshots

### SOLID Principles

**Single Responsibility Principle**: Subject manages notifications; observers manage their own update logic

**Open-Closed Principle**: New observer types can be added without modifying subject

**Dependency Inversion Principle**: Subject depends on Observer abstraction, not concrete observers

---

## 19. State Pattern

### Intent

Allow an object to alter its behavior when its internal state changes. The object will appear to change its class.

### Problem

An object needs to change its behavior based on its internal state, and it must change its behavior at runtime depending on that state. Using conditional statements (if/else or switch) for state-dependent behavior becomes unmaintainable as states multiply. How do you organize state-specific behavior and make state transitions explicit?

### Solution

Encapsulate state-specific behavior into separate state classes. The context object delegates state-dependent requests to the current state object, which implements the behavior for that state. State transitions are handled by state objects themselves or by the context.

### Structure

**Key Participants**:
- **Context**: Maintains instance of ConcreteState subclass that defines current state; delegates state-specific requests to current state
- **State**: Defines interface for encapsulating behavior associated with particular state of Context
- **ConcreteState**: Each subclass implements behavior associated with a state of Context

### Implementation

#### Python Implementation

```python
# State Pattern

from abc import ABC, abstractmethod

# State Interface
class ConnectionState(ABC):
    """Abstract state interface."""

    @abstractmethod
    def open(self, connection: 'TCPConnection') -> None:
        """Handle open request."""
        pass

    @abstractmethod
    def close(self, connection: 'TCPConnection') -> None:
        """Handle close request."""
        pass

    @abstractmethod
    def send(self, connection: 'TCPConnection', data: str) -> None:
        """Handle send request."""
        pass

# Concrete States
class ClosedState(ConnectionState):
    """State when connection is closed."""

    def open(self, connection: 'TCPConnection') -> None:
        print("Opening connection...")
        connection.set_state(EstablishedState())

    def close(self, connection: 'TCPConnection') -> None:
        print("Connection already closed")

    def send(self, connection: 'TCPConnection', data: str) -> None:
        print("Error: Cannot send data on closed connection")

class ListeningState(ConnectionState):
    """State when connection is listening."""

    def open(self, connection: 'TCPConnection') -> None:
        print("Connection request received")
        connection.set_state(EstablishedState())

    def close(self, connection: 'TCPConnection') -> None:
        print("Closing listening connection...")
        connection.set_state(ClosedState())

    def send(self, connection: 'TCPConnection', data: str) -> None:
        print("Error: Cannot send data while listening")

class EstablishedState(ConnectionState):
    """State when connection is established."""

    def open(self, connection: 'TCPConnection') -> None:
        print("Connection already established")

    def close(self, connection: 'TCPConnection') -> None:
        print("Closing connection...")
        connection.set_state(ClosedState())

    def send(self, connection: 'TCPConnection', data: str) -> None:
        print(f"Sending data: {data}")

# Context
class TCPConnection:
    """TCP connection with state-dependent behavior."""

    def __init__(self):
        self._state: ConnectionState = ClosedState()

    def set_state(self, state: ConnectionState) -> None:
        """Change current state."""
        print(f"State changed to: {state.__class__.__name__}")
        self._state = state

    def open(self) -> None:
        """Delegate to current state."""
        self._state.open(self)

    def close(self) -> None:
        """Delegate to current state."""
        self._state.close(self)

    def send(self, data: str) -> None:
        """Delegate to current state."""
        self._state.send(self, data)

# Usage
connection = TCPConnection()

# State transitions
connection.send("Hello")  # Error: closed connection
connection.open()         # Closed → Established
connection.send("Hello")  # Success
connection.open()         # Already established
connection.close()        # Established → Closed
connection.send("World")  # Error: closed connection

# Practical Example: Document Workflow
class DocumentState(ABC):
    """Abstract document state."""

    @abstractmethod
    def publish(self, document: 'Document') -> None:
        pass

    @abstractmethod
    def review(self, document: 'Document') -> None:
        pass

class DraftState(DocumentState):
    """Document in draft state."""

    def publish(self, document: 'Document') -> None:
        print("Cannot publish draft directly. Submit for review first.")

    def review(self, document: 'Document') -> None:
        print("Submitting draft for review...")
        document.set_state(ModerationState())

class ModerationState(DocumentState):
    """Document under review."""

    def publish(self, document: 'Document') -> None:
        print("Publishing reviewed document...")
        document.set_state(PublishedState())

    def review(self, document: 'Document') -> None:
        print("Document already under review")

class PublishedState(DocumentState):
    """Document published."""

    def publish(self, document: 'Document') -> None:
        print("Document already published")

    def review(self, document: 'Document') -> None:
        print("Creating new draft for changes...")
        document.set_state(DraftState())

class Document:
    """Document with workflow states."""

    def __init__(self, content: str):
        self._content = content
        self._state: DocumentState = DraftState()

    def set_state(self, state: DocumentState) -> None:
        print(f"Document state: {state.__class__.__name__}")
        self._state = state

    def publish(self) -> None:
        self._state.publish(self)

    def review(self) -> None:
        self._state.review(self)

# Usage
doc = Document("Important content")

doc.publish()  # Error: cannot publish draft
doc.review()   # Draft → Moderation
doc.publish()  # Moderation → Published
doc.review()   # Published → Draft (new version)
```

#### TypeScript Implementation

```typescript
// State Pattern

// State Interface
interface VendingMachineState {
    insertCoin(machine: VendingMachine): void;
    ejectCoin(machine: VendingMachine): void;
    selectProduct(machine: VendingMachine): void;
    dispense(machine: VendingMachine): void;
}

// Concrete States
class NoCoinState implements VendingMachineState {
    insertCoin(machine: VendingMachine): void {
        console.log("Coin inserted");
        machine.setState(new HasCoinState());
    }

    ejectCoin(machine: VendingMachine): void {
        console.log("No coin to eject");
    }

    selectProduct(machine: VendingMachine): void {
        console.log("Please insert coin first");
    }

    dispense(machine: VendingMachine): void {
        console.log("Please insert coin first");
    }
}

class HasCoinState implements VendingMachineState {
    insertCoin(machine: VendingMachine): void {
        console.log("Coin already inserted");
    }

    ejectCoin(machine: VendingMachine): void {
        console.log("Coin ejected");
        machine.setState(new NoCoinState());
    }

    selectProduct(machine: VendingMachine): void {
        console.log("Product selected");
        machine.setState(new DispensingState());
    }

    dispense(machine: VendingMachine): void {
        console.log("Select product first");
    }
}

class DispensingState implements VendingMachineState {
    insertCoin(machine: VendingMachine): void {
        console.log("Please wait, dispensing product");
    }

    ejectCoin(machine: VendingMachine): void {
        console.log("Cannot eject, product being dispensed");
    }

    selectProduct(machine: VendingMachine): void {
        console.log("Product already selected");
    }

    dispense(machine: VendingMachine): void {
        console.log("Dispensing product...");
        if (machine.getInventory() > 0) {
            machine.decrementInventory();
            console.log("Product dispensed. Enjoy!");
            machine.setState(new NoCoinState());
        } else {
            console.log("Out of stock!");
            machine.setState(new OutOfStockState());
        }
    }
}

class OutOfStockState implements VendingMachineState {
    insertCoin(machine: VendingMachine): void {
        console.log("Out of stock. Coin ejected.");
    }

    ejectCoin(machine: VendingMachine): void {
        console.log("No coin inserted");
    }

    selectProduct(machine: VendingMachine): void {
        console.log("Out of stock");
    }

    dispense(machine: VendingMachine): void {
        console.log("Out of stock");
    }
}

// Context
class VendingMachine {
    private state: VendingMachineState;
    private inventory: number;

    constructor(inventory: number) {
        this.state = new NoCoinState();
        this.inventory = inventory;
    }

    setState(state: VendingMachineState): void {
        console.log(`State: ${state.constructor.name}`);
        this.state = state;
    }

    insertCoin(): void {
        this.state.insertCoin(this);
    }

    ejectCoin(): void {
        this.state.ejectCoin(this);
    }

    selectProduct(): void {
        this.state.selectProduct(this);
    }

    dispense(): void {
        this.state.dispense(this);
    }

    getInventory(): number {
        return this.inventory;
    }

    decrementInventory(): void {
        this.inventory--;
    }
}

// Usage
const machine = new VendingMachine(2);

machine.selectProduct();    // Error: no coin
machine.insertCoin();       // NoCoin → HasCoin
machine.insertCoin();       // Already inserted
machine.selectProduct();    // HasCoin → Dispensing
machine.dispense();         // Dispenses product, Dispensing → NoCoin

machine.insertCoin();
machine.selectProduct();
machine.dispense();         // Last item dispensed, → OutOfStock

machine.insertCoin();       // Rejected (out of stock)
```

#### Java Implementation

```java
// State Pattern

// State Interface
interface State {
    void handleRequest(Context context);
}

// Concrete States
class ConcreteStateA implements State {
    @Override
    public void handleRequest(Context context) {
        System.out.println("State A: Handling request and transitioning to State B");
        context.setState(new ConcreteStateB());
    }
}

class ConcreteStateB implements State {
    @Override
    public void handleRequest(Context context) {
        System.out.println("State B: Handling request and transitioning to State A");
        context.setState(new ConcreteStateA());
    }
}

// Context
public class Context {
    private State state;

    public Context() {
        this.state = new ConcreteStateA();
    }

    public void setState(State state) {
        System.out.println("Context: State changed to " + state.getClass().getSimpleName());
        this.state = state;
    }

    public void request() {
        state.handleRequest(this);
    }
}

// Practical Example: Traffic Light
interface TrafficLightState {
    void handle(TrafficLight light);
    String getColor();
}

class RedLightState implements TrafficLightState {
    @Override
    public void handle(TrafficLight light) {
        System.out.println("Red light: STOP");
        System.out.println("Transitioning to Green...");
        light.setState(new GreenLightState());
    }

    @Override
    public String getColor() {
        return "RED";
    }
}

class YellowLightState implements TrafficLightState {
    @Override
    public void handle(TrafficLight light) {
        System.out.println("Yellow light: CAUTION");
        System.out.println("Transitioning to Red...");
        light.setState(new RedLightState());
    }

    @Override
    public String getColor() {
        return "YELLOW";
    }
}

class GreenLightState implements TrafficLightState {
    @Override
    public void handle(TrafficLight light) {
        System.out.println("Green light: GO");
        System.out.println("Transitioning to Yellow...");
        light.setState(new YellowLightState());
    }

    @Override
    public String getColor() {
        return "GREEN";
    }
}

public class TrafficLight {
    private TrafficLightState state;

    public TrafficLight() {
        this.state = new RedLightState();
    }

    public void setState(TrafficLightState state) {
        this.state = state;
    }

    public void change() {
        System.out.println("\nCurrent: " + state.getColor());
        state.handle(this);
    }

    public String getCurrentColor() {
        return state.getColor();
    }
}

// Usage
public class StatePatternExample {
    public static void main(String[] args) {
        TrafficLight light = new TrafficLight();

        // Cycle through states
        light.change();  // Red → Green
        light.change();  // Green → Yellow
        light.change();  // Yellow → Red
        light.change();  // Red → Green
    }
}
```

### When to Use

Use State when:
- An object's behavior depends on its state and must change at runtime
- Operations have large conditional statements that depend on object state
- State transitions need to be explicit and controlled
- State-specific behavior should be localized and separated

**Common Use Cases**:
- TCP/network connection states (closed, listening, established)
- Document workflow (draft, review, published)
- Vending machines and ATMs
- Game character states (idle, running, jumping, attacking)
- Order processing (pending, confirmed, shipped, delivered)
- Media player states (playing, paused, stopped)
- Traffic light controllers

### When NOT to Use

Avoid State when:
- State transitions are simple and don't justify separate classes
- There are only a few states with simple logic
- State-specific behavior is minimal
- Performance overhead of state objects is unacceptable
- States don't have different behavior, only different data

### Real-World Examples

**TCP Connection**:
```python
# Connection behavior changes based on state
connection.send("data")  # Behavior differs in Closed vs Established state
connection.open()        # State transition: Closed → Established
```

**Vending Machine**:
```typescript
// Machine behavior depends on current state
machine.insertCoin();    // NoCoin → HasCoin
machine.selectProduct(); // HasCoin → Dispensing
machine.dispense();      // Dispensing → NoCoin (or OutOfStock)
```

**Traffic Light**:
```java
// Light cycles through states
light.change();  // Red → Green → Yellow → Red
```

### Related Patterns

- **Strategy**: State encapsulates behavior like Strategy, but State allows object to change behavior by changing state
- **Singleton**: State objects are often Singletons
- **Flyweight**: State objects can be shared using Flyweight
- **Observer**: State changes can notify observers

### SOLID Principles

**Single Responsibility Principle**: Each state class handles behavior for one state

**Open-Closed Principle**: New states can be added without modifying context or existing states

**Liskov Substitution Principle**: All state objects are interchangeable through State interface

---

## 20. Strategy Pattern

### Intent

Define a family of algorithms, encapsulate each one, and make them interchangeable. Strategy lets the algorithm vary independently from clients that use it.

### Problem

You have multiple algorithms for a specific task (e.g., sorting, compression, routing) and need to select one at runtime. Hard-coding algorithms into classes creates tight coupling and makes it difficult to add new algorithms or change existing ones. How do you make algorithms interchangeable and independent from their clients?

### Solution

Define a family of algorithms as separate strategy classes, each implementing a common interface. The context object holds a reference to a strategy object and delegates the algorithm execution to it. Clients can switch strategies at runtime.

### Structure

**Key Participants**:
- **Strategy**: Declares interface common to all supported algorithms; Context uses this interface to call algorithm
- **ConcreteStrategy**: Implements algorithm using Strategy interface
- **Context**: Maintains reference to Strategy object; may define interface for Strategy to access its data

### Implementation

#### Python Implementation

```python
# Strategy Pattern

from abc import ABC, abstractmethod
from typing import List

# Strategy Interface
class SortStrategy(ABC):
    """Abstract sorting strategy."""

    @abstractmethod
    def sort(self, data: List[int]) -> List[int]:
        """Sort the data."""
        pass

# Concrete Strategies
class QuickSortStrategy(SortStrategy):
    """Quick sort implementation."""

    def sort(self, data: List[int]) -> List[int]:
        print("Using QuickSort")
        if len(data) <= 1:
            return data
        pivot = data[len(data) // 2]
        left = [x for x in data if x < pivot]
        middle = [x for x in data if x == pivot]
        right = [x for x in data if x > pivot]
        return self.sort(left) + middle + self.sort(right)

class BubbleSortStrategy(SortStrategy):
    """Bubble sort implementation."""

    def sort(self, data: List[int]) -> List[int]:
        print("Using BubbleSort")
        result = data.copy()
        n = len(result)
        for i in range(n):
            for j in range(0, n - i - 1):
                if result[j] > result[j + 1]:
                    result[j], result[j + 1] = result[j + 1], result[j]
        return result

class MergeSortStrategy(SortStrategy):
    """Merge sort implementation."""

    def sort(self, data: List[int]) -> List[int]:
        print("Using MergeSort")
        if len(data) <= 1:
            return data

        mid = len(data) // 2
        left = self.sort(data[:mid])
        right = self.sort(data[mid:])

        return self._merge(left, right)

    def _merge(self, left: List[int], right: List[int]) -> List[int]:
        result = []
        i = j = 0

        while i < len(left) and j < len(right):
            if left[i] <= right[j]:
                result.append(left[i])
                i += 1
            else:
                result.append(right[j])
                j += 1

        result.extend(left[i:])
        result.extend(right[j:])
        return result

# Context
class DataProcessor:
    """Context that uses sorting strategy."""

    def __init__(self, strategy: SortStrategy):
        self._strategy = strategy

    def set_strategy(self, strategy: SortStrategy) -> None:
        """Change sorting strategy at runtime."""
        self._strategy = strategy

    def process_data(self, data: List[int]) -> List[int]:
        """Process data using current strategy."""
        print(f"Processing {len(data)} elements...")
        return self._strategy.sort(data)

# Usage
data = [64, 34, 25, 12, 22, 11, 90]

processor = DataProcessor(QuickSortStrategy())
result = processor.process_data(data)
print(f"Result: {result}\n")

# Switch strategy at runtime
processor.set_strategy(BubbleSortStrategy())
result = processor.process_data(data)
print(f"Result: {result}\n")

processor.set_strategy(MergeSortStrategy())
result = processor.process_data(data)
print(f"Result: {result}\n")

# Practical Example: Payment Processing
class PaymentStrategy(ABC):
    """Abstract payment strategy."""

    @abstractmethod
    def pay(self, amount: float) -> bool:
        """Process payment."""
        pass

class CreditCardPayment(PaymentStrategy):
    """Credit card payment."""

    def __init__(self, card_number: str, cvv: str):
        self._card_number = card_number
        self._cvv = cvv

    def pay(self, amount: float) -> bool:
        print(f"Processing credit card payment of ${amount:.2f}")
        print(f"Card: **** **** **** {self._card_number[-4:]}")
        return True

class PayPalPayment(PaymentStrategy):
    """PayPal payment."""

    def __init__(self, email: str):
        self._email = email

    def pay(self, amount: float) -> bool:
        print(f"Processing PayPal payment of ${amount:.2f}")
        print(f"Account: {self._email}")
        return True

class CryptoPayment(PaymentStrategy):
    """Cryptocurrency payment."""

    def __init__(self, wallet_address: str):
        self._wallet_address = wallet_address

    def pay(self, amount: float) -> bool:
        print(f"Processing crypto payment of ${amount:.2f}")
        print(f"Wallet: {self._wallet_address[:8]}...")
        return True

class ShoppingCart:
    """Shopping cart with payment strategy."""

    def __init__(self):
        self._items: List[tuple[str, float]] = []
        self._payment_strategy: PaymentStrategy = None

    def add_item(self, item: str, price: float) -> None:
        self._items.append((item, price))
        print(f"Added: {item} - ${price:.2f}")

    def set_payment_method(self, strategy: PaymentStrategy) -> None:
        self._payment_strategy = strategy

    def checkout(self) -> bool:
        if not self._payment_strategy:
            print("Please select payment method")
            return False

        total = sum(price for _, price in self._items)
        print(f"\nTotal amount: ${total:.2f}")
        return self._payment_strategy.pay(total)

# Usage
cart = ShoppingCart()
cart.add_item("Laptop", 999.99)
cart.add_item("Mouse", 29.99)

# Pay with credit card
cart.set_payment_method(CreditCardPayment("1234567890123456", "123"))
cart.checkout()

# Pay with PayPal
cart2 = ShoppingCart()
cart2.add_item("Keyboard", 79.99)
cart2.set_payment_method(PayPalPayment("user@example.com"))
cart2.checkout()

# Pay with crypto
cart3 = ShoppingCart()
cart3.add_item("Monitor", 299.99)
cart3.set_payment_method(CryptoPayment("0x742d35Cc6634C0532925a3b844Bc9e7595f0bEb"))
cart3.checkout()
```

#### TypeScript Implementation

```typescript
// Strategy Pattern

// Strategy Interface
interface RouteStrategy {
    calculateRoute(from: string, to: string): string;
}

// Concrete Strategies
class CarRouteStrategy implements RouteStrategy {
    calculateRoute(from: string, to: string): string {
        return `Car route from ${from} to ${to}: Take highway (fastest, 30 min)`;
    }
}

class BikeRouteStrategy implements RouteStrategy {
    calculateRoute(from: string, to: string): string {
        return `Bike route from ${from} to ${to}: Use bike lanes (scenic, 45 min)`;
    }
}

class PublicTransitRouteStrategy implements RouteStrategy {
    calculateRoute(from: string, to: string): string {
        return `Transit route from ${from} to ${to}: Bus #42 then Metro (cheapest, 50 min)`;
    }
}

class WalkingRouteStrategy implements RouteStrategy {
    calculateRoute(from: string, to: string): string {
        return `Walking route from ${from} to ${to}: Through park (healthy, 60 min)`;
    }
}

// Context
class Navigator {
    private strategy: RouteStrategy;

    constructor(strategy: RouteStrategy) {
        this.strategy = strategy;
    }

    setStrategy(strategy: RouteStrategy): void {
        this.strategy = strategy;
        console.log(`Route strategy changed to ${strategy.constructor.name}`);
    }

    navigate(from: string, to: string): void {
        const route = this.strategy.calculateRoute(from, to);
        console.log(route);
    }
}

// Usage
const navigator = new Navigator(new CarRouteStrategy());

navigator.navigate("Home", "Office");

// Switch strategy based on user preference
navigator.setStrategy(new BikeRouteStrategy());
navigator.navigate("Home", "Office");

navigator.setStrategy(new PublicTransitRouteStrategy());
navigator.navigate("Home", "Office");

navigator.setStrategy(new WalkingRouteStrategy());
navigator.navigate("Home", "Office");

// Practical Example: Compression Strategy
interface CompressionStrategy {
    compress(file: string): string;
}

class ZipCompression implements CompressionStrategy {
    compress(file: string): string {
        return `Compressing ${file} using ZIP (fast, medium compression)`;
    }
}

class RarCompression implements CompressionStrategy {
    compress(file: string): string {
        return `Compressing ${file} using RAR (slow, high compression)`;
    }
}

class GzipCompression implements CompressionStrategy {
    compress(file: string): string {
        return `Compressing ${file} using GZIP (very fast, low compression)`;
    }
}

class FileCompressor {
    private strategy: CompressionStrategy;

    constructor(strategy: CompressionStrategy) {
        this.strategy = strategy;
    }

    setCompressionStrategy(strategy: CompressionStrategy): void {
        this.strategy = strategy;
    }

    compressFile(file: string): void {
        console.log(this.strategy.compress(file));
    }
}

// Usage: Select compression based on file size
const compressor = new FileCompressor(new ZipCompression());

const smallFile = "document.txt";
const largeFile = "video.mp4";

compressor.compressFile(smallFile);  // Use ZIP

// For large files, use better compression
compressor.setCompressionStrategy(new RarCompression());
compressor.compressFile(largeFile);  // Use RAR
```

#### Java Implementation

```java
// Strategy Pattern

// Strategy Interface
interface ValidationStrategy {
    boolean validate(String input);
}

// Concrete Strategies
class EmailValidationStrategy implements ValidationStrategy {
    @Override
    public boolean validate(String input) {
        System.out.println("Validating email: " + input);
        return input.contains("@") && input.contains(".");
    }
}

class PhoneValidationStrategy implements ValidationStrategy {
    @Override
    public boolean validate(String input) {
        System.out.println("Validating phone: " + input);
        return input.matches("\\d{3}-\\d{3}-\\d{4}");
    }
}

class PasswordValidationStrategy implements ValidationStrategy {
    @Override
    public boolean validate(String input) {
        System.out.println("Validating password: " + input);
        return input.length() >= 8 &&
               input.matches(".*[A-Z].*") &&
               input.matches(".*[0-9].*");
    }
}

// Context
public class InputValidator {
    private ValidationStrategy strategy;

    public InputValidator(ValidationStrategy strategy) {
        this.strategy = strategy;
    }

    public void setStrategy(ValidationStrategy strategy) {
        this.strategy = strategy;
    }

    public boolean validate(String input) {
        return strategy.validate(input);
    }
}

// Usage
public class StrategyPatternExample {
    public static void main(String[] args) {
        InputValidator validator = new InputValidator(new EmailValidationStrategy());

        System.out.println("Valid: " + validator.validate("user@example.com"));  // true
        System.out.println("Valid: " + validator.validate("invalid-email"));     // false

        // Switch to phone validation
        validator.setStrategy(new PhoneValidationStrategy());
        System.out.println("Valid: " + validator.validate("123-456-7890"));      // true
        System.out.println("Valid: " + validator.validate("12345"));             // false

        // Switch to password validation
        validator.setStrategy(new PasswordValidationStrategy());
        System.out.println("Valid: " + validator.validate("SecurePass123"));     // true
        System.out.println("Valid: " + validator.validate("weak"));              // false
    }
}
```

### When to Use

Use Strategy when:
- Many related classes differ only in their behavior
- You need different variants of an algorithm
- An algorithm uses data that clients shouldn't know about
- A class defines many behaviors as conditional statements
- You want to avoid exposing complex, algorithm-specific data structures

**Common Use Cases**:
- Sorting algorithms (quick, merge, bubble, insertion)
- Payment methods (credit card, PayPal, crypto, bank transfer)
- Route calculation (car, bike, walking, public transit)
- Compression algorithms (ZIP, RAR, GZIP, 7z)
- Validation strategies (email, phone, password, credit card)
- Pricing strategies (regular, discount, seasonal, member)
- Rendering strategies (canvas, WebGL, SVG)

### When NOT to Use

Avoid Strategy when:
- You have only one algorithm and no variations expected
- Algorithm changes are rare and don't justify separate classes
- Simple if/else statements are clearer and sufficient
- Clients don't need to be aware of different strategies
- Performance overhead of strategy objects is unacceptable

### Real-World Examples

**Sorting Algorithms**:
```python
# Choose sorting algorithm based on data size
processor.set_strategy(QuickSortStrategy())
result = processor.process_data(large_dataset)
```

**Payment Processing**:
```python
# User selects payment method at checkout
cart.set_payment_method(CreditCardPayment("1234...", "123"))
cart.checkout()
```

**Route Calculation**:
```typescript
// Navigate using different transportation modes
navigator.setStrategy(new BikeRouteStrategy());
navigator.navigate("Home", "Office");
```

**Input Validation**:
```java
// Validate different input types with same interface
validator.setStrategy(new EmailValidationStrategy());
boolean valid = validator.validate("user@example.com");
```

### Related Patterns

- **State**: Strategy and State both use composition and delegation, but Strategy makes algorithms interchangeable while State allows behavior to change with state
- **Template Method**: Strategy uses composition (has-a); Template Method uses inheritance (is-a)
- **Factory Method**: Can be used to create Strategy objects
- **Flyweight**: Strategy objects can be shared using Flyweight if they have no state

### SOLID Principles

**Single Responsibility Principle**: Each strategy class encapsulates one algorithm

**Open-Closed Principle**: New strategies can be added without modifying context or existing strategies

**Dependency Inversion Principle**: Context depends on Strategy abstraction, not concrete strategies

---

*[End of Behavioral Patterns section - Complete with Observer, State, and Strategy]*

# Pattern Selection Guide

## Decision Tree

**Need to create objects?**
- **Single instance globally?** → Singleton
- **Defer instantiation to subclasses?** → Factory Method
- **Create families of related objects?** → Abstract Factory
- **Construct complex object step-by-step?** → Builder
- **Clone existing instance?** → Prototype

**Need to adapt or compose objects?**
- **Make incompatible interfaces work?** → Adapter
- **Separate abstraction from implementation?** → Bridge
- **Compose objects into tree structures?** → Composite
- **Add responsibilities dynamically?** → Decorator
- **Simplify complex subsystem?** → Facade
- **Share objects efficiently?** → Flyweight
- **Control access to object?** → Proxy

**Need to manage object behavior/communication?**
- **Pass request along chain?** → Chain of Responsibility
- **Encapsulate request as object?** → Command
- **Access elements sequentially?** → Iterator
- **Centralize complex communications?** → Mediator
- **Capture and restore state?** → Memento
- **Notify dependents of state changes?** → Observer
- **Change behavior with state?** → State
- **Make algorithms interchangeable?** → Strategy
- **Define algorithm skeleton?** → Template Method
- **Add operations to object structure?** → Visitor
- **Interpret language grammar?** → Interpreter

## Common Pattern Combinations

**Patterns often work together**:

**Adapter + Facade**:
- Adapter makes two interfaces work together
- Facade simplifies multiple interfaces

**Composite + Iterator**:
- Composite creates tree structures
- Iterator traverses tree structures

**Observer + Mediator**:
- Observer for broadcast communication
- Mediator for centralized communication

**Strategy + Factory Method**:
- Strategy makes algorithms interchangeable
- Factory Method creates strategy objects

**Decorator + Composite**:
- Both use recursive composition
- Decorator adds responsibilities, Composite adds children

## Integration with SOLID Principles

Design patterns naturally support SOLID:

**Single Responsibility Principle**:
- Strategy, Command, Observer: Separate responsibilities
- Each pattern class has focused purpose

**Open-Closed Principle**:
- Factory Method, Abstract Factory, Strategy: Open for extension
- New variations added without modifying existing code

**Liskov Substitution Principle**:
- All patterns rely on proper substitutability
- Concrete implementations must honor abstract contracts

**Interface Segregation Principle**:
- Patterns use focused interfaces
- Clients depend only on what they use

**Dependency Inversion Principle**:
- Patterns depend on abstractions, not concretions
- Factory patterns, Strategy, Observer all invert dependencies

---

## Summary

Design patterns are proven solutions to recurring design problems. They provide:
- **Shared vocabulary** for communicating design intent
- **Reusable solutions** tested across many contexts
- **Flexible designs** that accommodate change
- **Best practices** from experienced developers

**Key Takeaways**:

1. **Learn patterns, don't force them**: Recognize when patterns apply naturally
2. **Understand trade-offs**: Every pattern has costs and benefits
3. **Start simple**: Don't over-engineer; add patterns when needed
4. **Combine wisely**: Patterns often work together effectively
5. **Refactor to patterns**: Discover pattern needs during development

**Mastering patterns requires**:
- Study: Learn intent, structure, and consequences
- Practice: Apply patterns in real projects
- Recognition: Identify pattern opportunities
- Judgment: Know when to use (and when not to use) patterns

Design patterns are tools, not goals. Use them to create better software, not to demonstrate pattern knowledge. The best use of patterns is invisible—code that's clear, flexible, and maintainable without calling attention to the patterns used.

## Further Reading

### Related Guides
- **DESIGN_IN_CONSTRUCTION.md**: Design heuristics and principles
- **CLASS_DESIGN.md**: Class-level design practices
- **../03-clean-architecture/SOLID_PRINCIPLES.md**: SOLID principles that patterns support
- **../05-refactoring-and-improvement/REFACTORING_CATALOG.md**: Refactoring to/from patterns

### Books
- **Design Patterns: Elements of Reusable Object-Oriented Software** by Gang of Four
- **Head First Design Patterns** by Freeman, Robson, Bates, and Sierra
- **Patterns of Enterprise Application Architecture** by Martin Fowler
- **Clean Code** by Robert C. Martin (Chapter 12: Emergence)

---

**Remember**: Patterns are discovered, not invented. They codify solutions that have evolved through experience. Learn them, recognize them, apply them judiciously, and let them guide your design thinking without constraining your creativity.
