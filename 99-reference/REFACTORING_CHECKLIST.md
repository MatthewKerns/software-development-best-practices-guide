# Refactoring Checklist

**Quick reference for safe, systematic code refactoring.**

Based on: Refactoring by Martin Fowler, Clean Code (Ch. 17)

## Before You Refactor

### Prerequisites
- [ ] Tests exist and pass
- [ ] You understand current behavior
- [ ] You have a specific smell to address
- [ ] Changes can be made incrementally
- [ ] Code is under version control
- [ ] Build is green

### Safety Checks
- [ ] No pending changes to commit
- [ ] Working on dedicated branch
- [ ] Can roll back easily
- [ ] Team aware of significant refactorings

## The Refactoring Process

### 1. Red → Green → Refactor (TDD Cycle)
```
Red: Write failing test
  ↓
Green: Make it pass (simplest way)
  ↓
Refactor: Improve code while keeping tests green
  ↓
Commit
```

### 2. Systematic Steps
1. Identify the smell
2. Choose refactoring technique
3. Make one small change
4. Run tests
5. Commit if green
6. Repeat

### 3. Keep Steps Small
- [ ] One refactoring at a time
- [ ] Run tests after each change
- [ ] Commit frequently (working states)
- [ ] Each commit < 30 minutes of work

## Common Refactoring Patterns

### Extract Method
**When:** Function too long, code needs comment to explain

**Before:**
```python
def print_owing(invoice):
    print_banner()

    # Print details
    print(f"name: {invoice.customer}")
    print(f"amount: {invoice.get_outstanding()}")
```

**After:**
```python
def print_owing(invoice):
    print_banner()
    print_details(invoice)

def print_details(invoice):
    print(f"name: {invoice.customer}")
    print(f"amount: {invoice.get_outstanding()}")
```

**Steps:**
1. Create new method with descriptive name
2. Copy extracted code to new method
3. Replace original code with method call
4. Run tests

### Rename Variable/Method/Class
**When:** Name doesn't reveal intent

**Steps:**
1. Find all references (IDE search)
2. Rename all at once (use IDE refactor tool)
3. Run tests
4. Commit

**Tip:** Use automated refactoring tools when available

### Inline Method
**When:** Method body is as clear as name, indirection adds no value

**Before:**
```python
def get_rating(self):
    return self.more_than_five_late_deliveries() and "Poor" or "Good"

def more_than_five_late_deliveries(self):
    return self.number_of_late_deliveries > 5
```

**After:**
```python
def get_rating(self):
    return self.number_of_late_deliveries > 5 and "Poor" or "Good"
```

### Introduce Parameter Object
**When:** Group of parameters that travel together

**Before:**
```python
def create_user(first_name, last_name, email, phone, address_line1,
                address_line2, city, state, zip_code):
    pass
```

**After:**
```python
class UserData:
    def __init__(self, personal_info, contact_info, address):
        self.personal = personal_info
        self.contact = contact_info
        self.address = address

def create_user(user_data: UserData):
    pass
```

### Replace Conditional with Polymorphism
**When:** Switch/if-else on type codes

**Before:**
```python
def get_speed(bird):
    if bird.type == "european":
        return bird.base_speed
    elif bird.type == "african":
        return bird.base_speed - bird.load_factor
    elif bird.type == "norwegian_blue":
        return 0 if bird.is_nailed else bird.base_speed * bird.voltage
```

**After:**
```python
class Bird(ABC):
    @abstractmethod
    def get_speed(self): pass

class European(Bird):
    def get_speed(self):
        return self.base_speed

class African(Bird):
    def get_speed(self):
        return self.base_speed - self.load_factor

class NorwegianBlue(Bird):
    def get_speed(self):
        return 0 if self.is_nailed else self.base_speed * self.voltage
```

### Move Method
**When:** Method uses data from another class more than its own (Feature Envy)

**Before:**
```python
class Account:
    def __init__(self):
        self.type = AccountType()

class AccountType:
    def overdraft_charge(self, account):
        if account.type.is_premium():
            return 10
        return 20
```

**After:**
```python
class Account:
    def overdraft_charge(self):
        return self.type.overdraft_charge()

class AccountType:
    def overdraft_charge(self):
        return 10 if self.is_premium() else 20
```

### Replace Magic Number with Named Constant
**When:** Unexplained numeric literal

**Before:**
```python
potential_energy = mass * 9.81 * height
```

**After:**
```python
GRAVITATIONAL_ACCELERATION = 9.81

potential_energy = mass * GRAVITATIONAL_ACCELERATION * height
```

### Decompose Conditional
**When:** Complex conditional logic

**Before:**
```python
if date.before(SUMMER_START) or date.after(SUMMER_END):
    charge = quantity * winter_rate + winter_service_charge
else:
    charge = quantity * summer_rate
```

**After:**
```python
def is_summer(date):
    return not (date.before(SUMMER_START) or date.after(SUMMER_END))

def summer_charge(quantity):
    return quantity * summer_rate

def winter_charge(quantity):
    return quantity * winter_rate + winter_service_charge

# Usage
charge = summer_charge(quantity) if is_summer(date) else winter_charge(quantity)
```

### Extract Class
**When:** Class doing work of two, SRP violation

**Before:**
```python
class Person:
    def __init__(self):
        self.name = ""
        self.office_area_code = ""
        self.office_number = ""

    def get_telephone_number(self):
        return f"({self.office_area_code}) {self.office_number}"
```

**After:**
```python
class Person:
    def __init__(self):
        self.name = ""
        self.office_phone = TelephoneNumber()

    def get_telephone_number(self):
        return self.office_phone.get_number()

class TelephoneNumber:
    def __init__(self):
        self.area_code = ""
        self.number = ""

    def get_number(self):
        return f"({self.area_code}) {self.number}"
```

## Refactoring Strategies

### Boy Scout Rule
**"Leave code cleaner than you found it"**

- [ ] Fix small issues while working on code
- [ ] Improve names when you touch them
- [ ] Extract methods as you understand code
- [ ] Remove dead code when you find it

**Guideline:** 15-minute improvements per file

### Rule of Three
**DRY (Don't Repeat Yourself)**

1. **First time:** Write the code
2. **Second time:** Wince at duplication but duplicate anyway
3. **Third time:** Refactor to remove duplication

### Preparatory Refactoring
**"Make the change easy, then make the easy change"**

1. Identify where change will be made
2. Refactor to make change easy
3. Make the actual change
4. Test
5. Commit

### Comprehension Refactoring
**"Understand by refactoring"**

- [ ] Rename for clarity as you understand
- [ ] Extract methods to document structure
- [ ] Add comments temporarily, then refactor to eliminate them

### Litter-Pickup Refactoring
**"Fix what you pass"**

- [ ] Delete unused code
- [ ] Fix obvious smells
- [ ] Improve names
- [ ] Small, opportunistic improvements

## Safety Practices

### Testing Safety Net
- [ ] **Before refactoring:** Ensure 85%+ test coverage
- [ ] **After each step:** Run relevant tests
- [ ] **Before commit:** Run full test suite
- [ ] **Add tests:** If coverage insufficient

### Version Control Discipline
```bash
# Good refactoring workflow
git checkout -b refactor/extract-user-validation
# Make small change
git add -p  # Review changes
git commit -m "refactor: extract validate_email method"
# Run tests
# Repeat
git push -u origin refactor/extract-user-validation
```

### Commit Messages for Refactoring
```
refactor: extract calculate_discount to separate method

- Improves testability
- Reduces function length from 45 to 15 lines
- No behavior change
```

### Large Refactorings
- [ ] Break into small incremental changes
- [ ] Merge intermediate states frequently
- [ ] Keep main branch working at all times
- [ ] Feature flags for gradual rollout
- [ ] Team communication about large changes

## When NOT to Refactor

### Skip Refactoring When:
- [ ] Code works and doesn't need changes
- [ ] Rewrite would be faster
- [ ] Close to deadline (plan for after)
- [ ] No tests exist (add tests first)
- [ ] Code is being deleted soon

### Rewrite Instead of Refactor When:
- [ ] Code is beyond salvageable
- [ ] Complete redesign needed
- [ ] Technology stack change required
- [ ] Performance rewrite necessary

## Refactoring Checklist

### Before Starting
- [ ] Identified specific code smell
- [ ] Tests exist and pass
- [ ] Chosen appropriate refactoring technique
- [ ] Working on clean branch
- [ ] Team informed of significant changes

### During Refactoring
- [ ] Making small, incremental changes
- [ ] Running tests after each change
- [ ] Committing frequently
- [ ] Preserving behavior (no feature changes)
- [ ] Using IDE refactoring tools when possible

### After Refactoring
- [ ] All tests still pass
- [ ] Code is clearer/simpler
- [ ] No new code smells introduced
- [ ] Behavior unchanged (verified by tests)
- [ ] Changes committed with clear message

### Code Review Checklist
- [ ] Intent is clear from code structure
- [ ] Tests verify behavior unchanged
- [ ] Complexity decreased
- [ ] No over-engineering
- [ ] Follows SOLID principles

## Common Refactoring Mistakes

| Mistake | Problem | Solution |
|---------|---------|----------|
| **Big Bang** | Refactoring everything at once | Small, incremental steps |
| **No Tests** | Breaking things unknowingly | Add tests first |
| **Mixed Changes** | Refactoring + features together | Separate commits |
| **Scope Creep** | Refactoring unrelated code | Stay focused on original smell |
| **Perfectionism** | Trying to fix everything | Fix what you're working on |
| **No Commits** | Losing work, hard to rollback | Commit after each step |

## Refactoring Metrics

### Before/After Comparison
- [ ] **Lines of code:** Reduced?
- [ ] **Cyclomatic complexity:** Lower?
- [ ] **Test coverage:** Maintained or improved?
- [ ] **Duplication:** Removed?
- [ ] **Function length:** Shorter?
- [ ] **Parameter count:** Fewer?

### Code Quality Indicators
```python
# Measure complexity before/after
# Cyclomatic Complexity: 1-10 (good), 11-20 (medium), 21+ (high)

# Before: CC = 15 (medium)
def process_order(order):
    if order.type == "standard":
        if order.priority == "high":
            # ...
        else:
            # ...
    elif order.type == "express":
        # ...

# After: CC = 3 (good per function)
def process_order(order):
    return process_express(order) if order.is_express() else process_standard(order)

def process_standard(order):
    return process_high_priority(order) if order.is_high_priority() else process_normal(order)
```

## Tools and Automation

### IDE Refactoring Tools
- **Rename:** Safe rename across files
- **Extract Method:** Automated extraction
- **Move Method:** Safe method relocation
- **Inline:** Automated inlining

### Static Analysis
- **Linters:** Find code smells automatically
- **Complexity:** Measure cyclomatic complexity
- **Duplication:** Detect copy-paste code
- **Coverage:** Track test coverage

### Automation Commands
```bash
# Python
black .              # Auto-format
pylint src/          # Find issues
radon cc src/ -a     # Complexity
coverage run -m pytest && coverage report

# TypeScript
npm run lint         # ESLint
npm run format       # Prettier
npm test -- --coverage
```

## Emergency Rollback

### If Tests Fail
```bash
git diff             # Review changes
git checkout .       # Discard all changes
# OR
git reset --hard HEAD  # Reset to last commit
```

### If Pushed to Remote
```bash
git revert <commit>   # Create revert commit
# OR (if no one pulled)
git reset --hard <previous-commit>
git push --force-with-lease
```

## References

- **Full Guide**: [05-refactoring-and-improvement/](../05-refactoring-and-improvement/)
- **Source**: Refactoring by Martin Fowler, Clean Code (Ch. 17)
- **Catalog**: https://refactoring.com/catalog/

---

**Remember**: Refactoring is not a project phase - it's continuous improvement.
