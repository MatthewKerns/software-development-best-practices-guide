---
name: dry-compliance-checker
description: Pre-emptively detects code duplication and DRY (Don't Repeat Yourself) violations before implementation. Use during planning and design phases to save implementation + refactoring work. Searches existing code for similar functionality, identifies patterns, and suggests reuse strategies.
allowed-tools: [Read, Grep, Glob]
---

# DRY Compliance Checker

## Purpose

Prevents code duplication by identifying existing functionality and patterns BEFORE implementation, saving costly implementation + refactoring cycles.

## When to Use This Skill

**Use this skill during:**
- Feature planning (before writing code)
- Design phase (identifying reuse opportunities)
- Before implementing "new" functionality
- Refactoring planning (finding duplication)
- Code review (catching duplication early)

**Examples:**
- "Check if authentication logic already exists before implementing"
- "Search for similar validation patterns in the codebase"
- "Is this utility function already implemented somewhere?"
- "Pre-emptive check: does email sending logic exist?"
- "Find all pagination implementations for reuse"

## Why Pre-Emptive Detection Matters

### The Cost of Reactive Duplication Discovery

**Traditional Approach (Expensive):**
```
1. Implement Feature A (5 hours)
2. Implement Feature B with duplicate logic (5 hours)
3. Code review discovers duplication
4. Refactor to extract common pattern (3 hours)
5. Update tests (2 hours)
6. Update documentation (1 hour)
Total: 16 hours
```

**Pre-Emptive Approach (Efficient):**
```
1. Plan Feature A (30 minutes)
2. Check for existing patterns (15 minutes)
3. Find similar Feature B logic
4. Reuse or extend existing code (2 hours)
5. Update tests (30 minutes)
Total: 3.25 hours (80% time savings!)
```

### Real-World Example: Duplication from "Backward Compatibility"

**What Happened:**
- Implemented tool response with both `exit_code` and `return_code`
- Both contained identical values (e.g., 0)
- Added `return_code` for "backward compatibility" with ZERO users
- Required refactoring cycle to remove duplication

**Cost:**
- Implementation: Added duplicate field
- Refactoring: Removed duplication
- Test updates: Changed assertions
- Documentation: Updated docs twice

**What Should Have Happened:**
- Planning: Check existing utility returns
- Discovery: Already returns `exit_code`
- Decision: Don't add `return_code`
- Implementation: Use only `exit_code`
- Result: Zero refactoring needed

## Pre-Emptive Detection Workflow

### Step 1: Define What You're Implementing (2 minutes)

**Checklist:**
- [ ] Clear description of functionality
- [ ] Key operations/methods needed
- [ ] Domain/module context
- [ ] Expected inputs/outputs

**Example:**
```
PLANNING: Email Sending Feature

Functionality:
- Send transactional emails
- Template support
- Attachment handling
- Error handling and retries

Key Operations:
- sendEmail(to, subject, body)
- sendTemplateEmail(to, template, data)
- addAttachment(email, file)
```

### Step 2: Search for Similar Functionality (10 minutes)

**Search Patterns:**
```bash
# Search for class/function names
grep -r "EmailService\|MailService\|EmailSender" --include="*.ts" --include="*.py"

# Search for key operations
grep -r "sendEmail\|send_email\|send.*mail" --include="*.ts" --include="*.py"

# Search for domain concepts
grep -r "email\|mail\|message" src/ --include="*.ts" | grep -i "class\|function\|def"

# Search for patterns (imports)
grep -r "nodemailer\|sendgrid\|ses" --include="*.ts" --include="*.json"
```

**What to Look For:**
- ✅ Existing classes/modules with similar names
- ✅ Functions performing similar operations
- ✅ Utilities in the same domain
- ✅ Third-party libraries already integrated
- ✅ Test files (reveal existing implementations)

### Step 3: Analyze Discovered Code (15 minutes)

**For Each Match:**
- Read implementation
- Check if it meets your needs
- Identify gaps (missing features)
- Assess quality (worth reusing?)
- Note extension points

**Decision Matrix:**
```
Match Quality:
├─ PERFECT MATCH (90-100% fits needs)
│  → Action: Reuse as-is
│
├─ GOOD MATCH (70-89% fits needs)
│  → Action: Extend or adapt existing code
│
├─ PARTIAL MATCH (40-69% fits needs)
│  → Action: Extract common pattern, implement differences
│
└─ POOR MATCH (<40% fits needs)
   → Action: Implement new, consider future generalization
```

### Step 4: Choose Reuse Strategy (5 minutes)

**Strategy Options:**

**A. Direct Reuse** (Match Quality: 90-100%)
```typescript
// Existing: EmailService already does everything
import { EmailService } from './services/EmailService';

// Just use it!
const emailService = new EmailService();
emailService.sendEmail(to, subject, body);
```

**B. Extend Existing** (Match Quality: 70-89%)
```typescript
// Existing: EmailService, but missing template support
import { EmailService } from './services/EmailService';

class TemplateEmailService extends EmailService {
  sendTemplateEmail(to: string, template: string, data: object) {
    const body = this.renderTemplate(template, data);
    return this.sendEmail(to, this.getTemplateSubject(template), body);
  }
}
```

**C. Extract Common Pattern** (Match Quality: 40-69%)
```typescript
// Existing: EmailService + SMSService have similar retry logic
// Extract common pattern

// BEFORE: Duplication in both services
class EmailService {
  async send(message) {
    for (let i = 0; i < 3; i++) {
      try { return await this.api.send(message); }
      catch (e) { await sleep(1000 * i); }
    }
  }
}

class SMSService {
  async send(message) {
    for (let i = 0; i < 3; i++) {
      try { return await this.api.send(message); }
      catch (e) { await sleep(1000 * i); }
    }
  }
}

// AFTER: Extract retry pattern
class RetryHelper {
  static async withRetry(fn, attempts = 3) {
    for (let i = 0; i < attempts; i++) {
      try { return await fn(); }
      catch (e) { if (i === attempts - 1) throw e; await sleep(1000 * i); }
    }
  }
}

class EmailService {
  async send(message) {
    return RetryHelper.withRetry(() => this.api.send(message));
  }
}
```

**D. Implement New, Plan for Generalization** (Match Quality: <40%)
```typescript
// No good match exists, implement fresh
// BUT: Design for future reuse

// Example: First notification service (email)
// Design with future SMS/Push in mind

interface NotificationService {
  send(message: Message): Promise<Result>;
}

class EmailNotificationService implements NotificationService {
  // Implementation
}

// Later: Easy to add SMS without duplication
class SMSNotificationService implements NotificationService {
  // Shares interface, different implementation
}
```

## Common Duplication Patterns

### Pattern 1: Validation Logic

**Search For:**
```bash
grep -r "validate\|isValid\|check" src/ --include="*.ts"
grep -r "email.*valid\|phone.*valid\|url.*valid" src/
```

**Common Duplications:**
- Email validation regex copied across files
- Phone number formatting in multiple places
- URL validation duplicated
- Input sanitization repeated

**Solution:**
```typescript
// BEFORE: Duplication
// file1.ts
const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;

// file2.ts
const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;

// AFTER: Centralize
// utils/validation.ts
export class Validators {
  private static readonly EMAIL_REGEX = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;

  static isValidEmail(email: string): boolean {
    return this.EMAIL_REGEX.test(email);
  }
}
```

### Pattern 2: Error Handling

**Search For:**
```bash
grep -r "try.*catch\|error handling" src/
grep -r "retry\|exponential.*backoff" src/
```

**Common Duplications:**
- Retry logic with exponential backoff
- Error logging format
- Error response structure
- Fallback mechanisms

**Solution:**
```typescript
// Extract common error handling
class ErrorHandler {
  static async withRetry<T>(
    fn: () => Promise<T>,
    maxAttempts: number = 3
  ): Promise<T> {
    // Reusable retry logic
  }

  static logError(error: Error, context: object): void {
    // Centralized error logging
  }
}
```

### Pattern 3: Data Transformation

**Search For:**
```bash
grep -r "transform\|convert\|format\|parse" src/
grep -r "toJSON\|fromJSON\|serialize" src/
```

**Common Duplications:**
- Date formatting repeated
- JSON serialization patterns
- Data mapping logic
- Type conversions

**Solution:**
```typescript
// Centralize transformations
class DataTransformers {
  static formatDate(date: Date, format: string): string { }
  static parseJSON<T>(json: string): T { }
  static mapToDTO<T, U>(entity: T, mapper: (t: T) => U): U { }
}
```

### Pattern 4: API Integration

**Search For:**
```bash
grep -r "axios\|fetch\|http" src/
grep -r "api.*call\|request\|endpoint" src/
```

**Common Duplications:**
- HTTP client configuration
- Authentication headers
- Request/response interceptors
- Error handling for API calls

**Solution:**
```typescript
// Create base API client
class BaseApiClient {
  protected async request<T>(config: RequestConfig): Promise<T> {
    // Common: auth, headers, error handling, retries
  }
}

class UserApiClient extends BaseApiClient {
  getUser(id: string) {
    return this.request({ method: 'GET', url: `/users/${id}` });
  }
}
```

### Pattern 5: Configuration Patterns

**Search For:**
```bash
grep -r "config\|configuration\|settings" src/
grep -r "process\.env\|getenv" src/
```

**Common Duplications:**
- Environment variable reading
- Configuration validation
- Default value handling
- Configuration merging

**Solution:**
```typescript
// Centralize configuration
class ConfigService {
  static get<T>(key: string, defaultValue?: T): T {
    // Unified config access
  }

  static getRequired<T>(key: string): T {
    const value = this.get<T>(key);
    if (!value) throw new Error(`Missing required config: ${key}`);
    return value;
  }
}
```

## Detection Report Format

```
DRY COMPLIANCE CHECK REPORT
Feature: [Feature Name]
Date: [Check Date]

SEARCH SUMMARY
--------------
Keywords Searched:
- [keyword 1]
- [keyword 2]

Files Scanned: [N]
Matches Found: [N]

FINDINGS
--------

1. EXISTING IMPLEMENTATION FOUND
   Location: src/services/EmailService.ts:45
   Match Quality: 85% (GOOD MATCH)
   Gaps: Missing template support, attachments

   Recommendation: EXTEND existing EmailService
   Effort Saved: ~5 hours (avoid reimplementation)

   Code Preview:
   ```typescript
   class EmailService {
     async sendEmail(to, subject, body) { ... }
   }
   ```

   Extension Strategy:
   ```typescript
   class TemplateEmailService extends EmailService {
     async sendTemplateEmail(to, template, data) {
       // Add template rendering
       const body = render(template, data);
       return this.sendEmail(to, subject, body);
     }
   }
   ```

2. SIMILAR PATTERN FOUND
   Location: src/services/SMSService.ts:30
   Pattern: Retry logic with exponential backoff
   Match Quality: 60% (PARTIAL MATCH)

   Recommendation: EXTRACT common retry pattern
   Effort Saved: ~2 hours (avoid duplication)

   Refactoring:
   - Extract RetryHelper utility
   - Apply to both EmailService and SMSService
   - Reuse for future integrations

3. UTILITY FUNCTION EXISTS
   Location: src/utils/validators.ts:12
   Function: isValidEmail(email: string)
   Match Quality: 100% (PERFECT MATCH)

   Recommendation: REUSE existing validator
   Effort Saved: ~1 hour (avoid duplication)

TIME SAVINGS ESTIMATE
---------------------
- Reimplementation avoided: 5 hours
- Duplication prevented: 2 hours
- Utility reuse: 1 hour
Total: 8 hours saved by pre-emptive check

RECOMMENDED ACTIONS
-------------------
1. ✅ Extend EmailService for template support (2h)
2. ✅ Extract RetryHelper from EmailService/SMSService (1.5h)
3. ✅ Import and reuse isValidEmail validator (5min)

Total Implementation Time: 3.5h (vs 11.5h from scratch)
Savings: 70% time reduction
```

## Pre-Emptive Checklist

**Before Implementing ANY Feature:**

- [ ] **Step 1**: Define what you're implementing (2min)
- [ ] **Step 2**: Search for similar functionality (10min)
  - [ ] Search by class/function names
  - [ ] Search by key operations
  - [ ] Search by domain concepts
  - [ ] Check third-party libraries
  - [ ] Review test files
- [ ] **Step 3**: Analyze matches (15min)
  - [ ] Read existing implementations
  - [ ] Assess match quality (%)
  - [ ] Identify gaps
  - [ ] Evaluate reusability
- [ ] **Step 4**: Choose strategy (5min)
  - [ ] Direct reuse (90-100% match)
  - [ ] Extend existing (70-89% match)
  - [ ] Extract pattern (40-69% match)
  - [ ] Implement new (< 40% match)
- [ ] **Step 5**: Document decision
  - [ ] Record what was found
  - [ ] Justify reuse or new implementation
  - [ ] Estimate time saved

**Total Time Investment**: ~30 minutes
**Typical Time Savings**: 2-8 hours (4x-16x ROI)

## References

- **[REFACTORING_CATALOG.md](../05-refactoring-and-improvement/REFACTORING_CATALOG.md)** - Refactoring patterns
- **[CODE_SMELLS.md](../05-refactoring-and-improvement/CODE_SMELLS.md)** - Identifying duplication
- **[DESIGN_IN_CONSTRUCTION.md](../02-design-in-code/DESIGN_IN_CONSTRUCTION.md)** - Reuse strategies

## Success Metrics

**Efficiency:**
- 70-90% time savings vs reactive refactoring
- 30-minute investment yields 2-8 hour savings
- Prevents duplication before it exists

**Quality:**
- Reduced code duplication
- Increased pattern reuse
- Better architecture
- Consistent implementations
