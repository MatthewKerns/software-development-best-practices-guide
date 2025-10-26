---
name: tdd-workflow-assistant
description: Guides Test-Driven Development (TDD) Red-Green-Refactor workflow. Use when implementing new features with TDD, ensuring proper test-first development. Helps write failing tests (RED), minimal implementation (GREEN), and clean refactoring (REFACTOR) while maintaining test coverage.
allowed-tools: [Read, Write, Edit, Bash, Grep, Glob]
---

# TDD Workflow Assistant

## Purpose

Guides developers through the Test-Driven Development (TDD) Red-Green-Refactor cycle, ensuring disciplined test-first development and maintaining high code quality.

## When to Use This Skill

**Use this skill when:**
- Implementing new features with TDD
- Adding functionality to existing code test-first
- Learning or practicing TDD methodology
- Ensuring proper test coverage from the start
- Need guidance on writing effective tests

**Examples:**
- "Help me implement this feature using TDD"
- "Guide me through RED-GREEN-REFACTOR for this function"
- "What test should I write first?"
- "Is my test properly failing (RED)?"
- "Help me refactor while keeping tests green"

## The RED-GREEN-REFACTOR Cycle

### 🔴 RED: Write a Failing Test

**Goal**: Write the smallest test that fails for the right reason

**Steps:**
1. Understand the requirement
2. Write a focused test for ONE behavior
3. Run the test and verify it fails
4. Confirm it fails for the expected reason (not syntax error)

**Good RED test characteristics:**
- Tests exactly ONE behavior
- Has clear, descriptive name
- Fails with expected message
- Uses AAA pattern (Arrange-Act-Assert)

**Example:**
```typescript
// RED: Write failing test first
describe('EmailValidator', () => {
  it('should return true for valid email address', () => {
    const validator = new EmailValidator();

    const result = validator.isValid('user@example.com');

    expect(result).toBe(true); // FAILS: EmailValidator is not defined
  });
});

// Run test: ❌ FAIL (Expected: EmailValidator doesn't exist yet)
```

### 🟢 GREEN: Make It Pass (Simplest Way)

**Goal**: Write the minimum code to make the test pass

**Steps:**
1. Write simplest implementation (even if naive)
2. Run the test and verify it passes
3. Don't add extra features
4. Don't optimize yet (that's REFACTOR)

**Good GREEN characteristics:**
- Minimum code to pass test
- May use hard-coded values (if simplest)
- Focused on making test pass, not elegance
- Runs quickly

**Example:**
```typescript
// GREEN: Simplest implementation to pass test
class EmailValidator {
  isValid(email: string): boolean {
    return email.includes('@'); // Simplest solution that passes
  }
}

// Run test: ✅ PASS
```

### 🔵 REFACTOR: Improve Design

**Goal**: Clean up code while keeping tests green

**Steps:**
1. Look for code smells
2. Extract duplicated code
3. Improve names and structure
4. Run tests after each change
5. Stop when clean and tests still pass

**Good REFACTOR characteristics:**
- Tests stay green throughout
- Improves readability
- Reduces duplication
- Enhances maintainability
- No new functionality

**Example:**
```typescript
// REFACTOR: Improve implementation (tests stay green)
class EmailValidator {
  private static readonly EMAIL_REGEX = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;

  isValid(email: string): boolean {
    if (!email || email.trim().length === 0) {
      return false;
    }

    return EmailValidator.EMAIL_REGEX.test(email);
  }
}

// Run tests: ✅ PASS (still green after refactoring)
```

## TDD Workflow Steps

### Step 1: Start with RED

**Checklist:**
- [ ] Read and understand the requirement
- [ ] Identify ONE specific behavior to test
- [ ] Write descriptive test name (behavior, not implementation)
- [ ] Use AAA pattern: Arrange, Act, Assert
- [ ] Run test and verify it FAILS
- [ ] Confirm failure reason is correct (not syntax error)

**Anti-Patterns to Avoid:**
- ❌ Writing test after code is written
- ❌ Testing multiple behaviors in one test
- ❌ Test passes immediately (wrote test wrong or code exists)
- ❌ Test fails for wrong reason (syntax error, import issue)

### Step 2: Move to GREEN

**Checklist:**
- [ ] Write simplest code to pass test
- [ ] Avoid premature optimization
- [ ] Don't add features not tested
- [ ] Run test and verify it PASSES
- [ ] Commit if test passes

**Anti-Patterns to Avoid:**
- ❌ Writing complex implementation immediately
- ❌ Adding features not covered by tests
- ❌ Optimizing before refactoring phase
- ❌ Skipping test run (assuming it works)

### Step 3: Enter REFACTOR

**Checklist:**
- [ ] Identify code smells
- [ ] Extract duplicated code
- [ ] Improve names (variables, functions, classes)
- [ ] Simplify complex logic
- [ ] Run tests after EACH refactoring
- [ ] Stop when code is clean and tests pass
- [ ] Commit when refactoring complete

**Anti-Patterns to Avoid:**
- ❌ Skipping refactor phase ("it works, move on")
- ❌ Adding new functionality during refactor
- ❌ Breaking tests during refactor
- ❌ Not running tests after each change
- ❌ Refactoring too much at once

### Step 4: Repeat Cycle

**When to add next test:**
- Current cycle complete (tests green, code clean)
- New behavior needs testing
- Edge case discovered
- Error scenario needs handling

**Cycle continues until:**
- All requirements implemented
- All edge cases covered
- Error handling complete
- Code clean and maintainable

## TDD Guidance by Scenario

### Scenario 1: New Function/Method

**RED:**
```python
def test_calculate_discount_returns_zero_for_no_discount():
    """RED: Test for base case - no discount"""
    calculator = DiscountCalculator()

    result = calculator.calculate_discount(price=100, discount_percent=0)

    assert result == 0  # FAILS: calculate_discount doesn't exist
```

**GREEN:**
```python
class DiscountCalculator:
    def calculate_discount(self, price: float, discount_percent: float) -> float:
        return 0  # Simplest code to pass test
```

**REFACTOR:**
```python
# Add more tests first, then refactor when patterns emerge
def test_calculate_discount_returns_correct_amount():
    """RED: Test for actual discount calculation"""
    calculator = DiscountCalculator()

    result = calculator.calculate_discount(price=100, discount_percent=10)

    assert result == 10  # FAILS: returns 0, not 10

# GREEN: Now implement real logic
class DiscountCalculator:
    def calculate_discount(self, price: float, discount_percent: float) -> float:
        return price * (discount_percent / 100)

# REFACTOR: Extract magic numbers, add validation
class DiscountCalculator:
    PERCENT_DIVISOR = 100

    def calculate_discount(self, price: float, discount_percent: float) -> float:
        if price < 0 or discount_percent < 0:
            raise ValueError("Price and discount must be non-negative")

        return price * (discount_percent / self.PERCENT_DIVISOR)
```

### Scenario 2: Error Handling

**RED:**
```typescript
it('should throw error for invalid email format', () => {
  const validator = new EmailValidator();

  expect(() => validator.validate('notanemail')).toThrow('Invalid email format');
  // FAILS: validate() doesn't throw, or doesn't exist
});
```

**GREEN:**
```typescript
class EmailValidator {
  validate(email: string): void {
    if (!email.includes('@')) {
      throw new Error('Invalid email format');
    }
    // Simplest code to pass
  }
}
```

**REFACTOR:**
```typescript
class EmailValidator {
  private static readonly EMAIL_REGEX = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;

  validate(email: string): void {
    if (!EmailValidator.EMAIL_REGEX.test(email)) {
      throw new ValidationError('Invalid email format');
    }
  }
}
```

### Scenario 3: Edge Cases

**Systematic approach:**
```python
# Test 1: Normal case (RED → GREEN → REFACTOR)
def test_divide_returns_correct_result():
    assert divide(10, 2) == 5

# Test 2: Edge case - division by zero (RED → GREEN → REFACTOR)
def test_divide_raises_error_for_zero_divisor():
    with pytest.raises(ValueError, match="Cannot divide by zero"):
        divide(10, 0)

# Test 3: Edge case - negative numbers (RED → GREEN → REFACTOR)
def test_divide_handles_negative_numbers():
    assert divide(-10, 2) == -5
    assert divide(10, -2) == -5

# Test 4: Edge case - floating point (RED → GREEN → REFACTOR)
def test_divide_returns_float_for_imprecise_division():
    result = divide(10, 3)
    assert abs(result - 3.333) < 0.001
```

## AAA Pattern (Arrange-Act-Assert)

Every test should follow this structure:

```typescript
it('should calculate total price with tax', () => {
  // ARRANGE: Set up test data and dependencies
  const calculator = new PriceCalculator();
  const basePrice = 100;
  const taxRate = 0.10;

  // ACT: Execute the behavior being tested
  const totalPrice = calculator.calculateTotal(basePrice, taxRate);

  // ASSERT: Verify the result
  expect(totalPrice).toBe(110);
});
```

**Benefits:**
- Clear test structure
- Easy to read and understand
- Identifies what's being tested
- Separates setup from verification

## TDD Best Practices

### Test Naming Conventions

**Good test names:**
- `test_calculate_discount_returns_zero_for_no_discount()`
- `should_throw_error_for_invalid_email()`
- `it should return empty array for no results`

**Poor test names:**
- `test1()`, `test_function()` (not descriptive)
- `test_everything()` (too broad)
- `test_edge_cases()` (vague)

### Test Independence

**Each test should:**
- Run independently (no shared state)
- Not depend on other tests' execution
- Clean up after itself
- Be repeatable (same result every time)

**Example:**
```python
class TestUserService:
    def setup_method(self):
        """Run before each test"""
        self.db = MockDatabase()
        self.service = UserService(self.db)

    def teardown_method(self):
        """Run after each test"""
        self.db.clear()

    def test_create_user_stores_in_database(self):
        # Test runs with fresh database each time
        user = self.service.create_user("test@example.com")
        assert self.db.count() == 1
```

### Coverage Targets

**Aim for:**
- Unit test coverage: ≥85%
- Critical paths: 100% coverage
- Edge cases: Fully tested
- Error paths: All tested

**Monitor:**
```bash
# Check coverage
pytest --cov=src --cov-report=html

# Set minimum coverage
pytest --cov=src --cov-fail-under=85
```

## Output Format

When guiding TDD workflow, provide:

### TDD Workflow Guide

```
TDD WORKFLOW: [Feature Name]

CURRENT PHASE: [RED | GREEN | REFACTOR]

═══════════════════════════════════════════
PHASE: 🔴 RED - Write Failing Test
═══════════════════════════════════════════

REQUIREMENT:
[Describe the specific behavior to test]

SUGGESTED TEST:
```[language]
[Complete test code with AAA pattern]
```

CHECKLIST:
- [ ] Test name describes behavior, not implementation
- [ ] Uses AAA pattern (Arrange, Act, Assert)
- [ ] Tests ONE specific behavior
- [ ] Will fail for the right reason

NEXT STEP:
Run test and verify it FAILS with: [expected error message]

═══════════════════════════════════════════
PHASE: 🟢 GREEN - Make It Pass
═══════════════════════════════════════════

IMPLEMENTATION:
```[language]
[Simplest code to make test pass]
```

CHECKLIST:
- [ ] Minimum code to pass test
- [ ] No premature optimization
- [ ] No untested features added
- [ ] Test now PASSES

NEXT STEP:
Run test and verify it PASSES, then commit

═══════════════════════════════════════════
PHASE: 🔵 REFACTOR - Improve Design
═══════════════════════════════════════════

CODE SMELLS DETECTED:
- [Smell 1]: [Description]
- [Smell 2]: [Description]

REFACTORING SUGGESTIONS:
1. [Refactoring 1]
   - Before: [code snippet]
   - After: [improved code]

2. [Refactoring 2]
   - Before: [code snippet]
   - After: [improved code]

CHECKLIST:
- [ ] Extract duplicated code
- [ ] Improve variable/function names
- [ ] Simplify complex logic
- [ ] Run tests after each change
- [ ] All tests still GREEN

NEXT STEP:
Apply refactorings one at a time, running tests after each
```

## Common TDD Mistakes

**Mistake 1: Writing tests after code**
- **Problem**: Not test-driven, just test-covered
- **Solution**: Force yourself to see RED before GREEN

**Mistake 2: Testing implementation details**
- **Problem**: Tests break when refactoring
- **Solution**: Test behavior, not implementation

**Mistake 3: Skipping REFACTOR phase**
- **Problem**: Technical debt accumulates
- **Solution**: Discipline to refactor every cycle

**Mistake 4: Tests too large**
- **Problem**: Hard to debug, unclear what failed
- **Solution**: One behavior per test

**Mistake 5: Not running tests frequently**
- **Problem**: Don't know what broke code
- **Solution**: Run tests after every small change

## References

- **[TDD_WORKFLOW.md](../04-quality-through-testing/TDD_WORKFLOW.md)** - Complete TDD guide
- **[UNIT_TESTING_PRINCIPLES.md](../04-quality-through-testing/UNIT_TESTING_PRINCIPLES.md)** - Unit testing best practices
- **[COVERAGE_STANDARDS.md](../04-quality-through-testing/COVERAGE_STANDARDS.md)** - Coverage requirements

## Success Metrics

**Process Adherence:**
- Tests written before code (100% of time)
- All tests pass before commit
- Coverage ≥85%
- Refactor phase completed every cycle

**Quality Outcomes:**
- Zero regression bugs from tested code
- High confidence in changes
- Fast debugging (precise test failures)
- Clean, maintainable code
