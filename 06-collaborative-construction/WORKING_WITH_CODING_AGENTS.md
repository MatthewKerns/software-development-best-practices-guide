# Working with Coding Agents: Best Practices for Agent-Driven Development

## Overview

When working with AI coding agents in iterative development cycles, knowledge accumulation and drift become critical issues. This guide provides best practices for managing agent-driven development, with special emphasis on periodic consolidation and cleanup of both documentation and code—while preserving crucial historical knowledge.

The challenge: As agents create code and documentation iteratively, they accumulate incremental knowledge improvements while simultaneously developing knowledge gaps and inconsistencies. Without periodic consolidation, projects become bloated with outdated docs, competing implementations, and contradictory patterns. However, aggressive consolidation risks losing valuable historical context.

## The Knowledge Drift Problem

### How Knowledge Drift Occurs

**During Agent-Driven Development:**
1. **Iteration 1**: Agent creates initial implementation with docs
2. **Iteration 2-5**: Gradual improvements, each with partial context
3. **Iteration 6+**: Multiple versions of truth exist
4. **Result**: Competing patterns, outdated docs, knowledge gaps

### Signs You Need Consolidation

- Multiple implementation patterns for the same problem
- Documentation conflicts with actual implementation
- "Plan v1", "Plan v2", "Plan-FINAL-FINAL" proliferation
- Test files scattered across directories
- Competing architectural decisions
- Agent confusion about which pattern to follow
- Declining agent performance due to context pollution

## Critical: Historical Knowledge Preservation

### The Risk of Knowledge Loss

**What We Risk Losing During Consolidation:**
- Why certain approaches failed (preventing re-attempts)
- Security vulnerabilities discovered and fixed
- Performance bottlenecks identified and resolved
- Integration gotchas and workarounds
- Customer-reported issues and their solutions
- Architectural decisions and their rationale
- Failed experiments that inform current design
- Edge cases discovered through debugging
- Dependencies on external systems
- Migration paths and rollback procedures

### Knowledge Preservation Framework

#### Three-Tier Knowledge Architecture

```markdown
┌─────────────────────────────────────┐
│   Tier 1: Current State Docs        │
│   (Active, Frequently Updated)      │
├─────────────────────────────────────┤
│   Tier 2: Decision History          │
│   (Append-Only, Never Deleted)      │
├─────────────────────────────────────┤
│   Tier 3: Archive                   │
│   (Historical Snapshots, Searchable)│
└─────────────────────────────────────┘
```

#### Tier 1: Current State Documentation
**What Goes Here:** Active implementation guides, current API docs, setup instructions
**Update Frequency:** Every consolidation cycle
**Retention:** Replace with each consolidation

#### Tier 2: Decision History (NEVER DELETE)
**What Goes Here:**
- Architectural Decision Records (ADRs)
- Failed approach documentation
- Security incident reports
- Performance optimization history
- Breaking change rationales
- Migration experiences
- Bug root cause analyses

**Format:**
```markdown
docs/
├── current/           # Tier 1: Current state
├── decision-history/  # Tier 2: Permanent record
│   ├── ADR-001-why-we-chose-postgres.md
│   ├── ADR-002-authentication-strategy.md
│   ├── FAILED-001-redis-clustering-attempt.md
│   ├── SECURITY-001-sql-injection-fix.md
│   ├── PERF-001-query-optimization.md
│   └── MIGRATION-001-v1-to-v2-lessons.md
└── archive/          # Tier 3: Historical snapshots
```

#### Tier 3: Archive
**What Goes Here:** Snapshots of documentation before major consolidations
**Format:** Timestamped folders or git tags
**Searchable:** Yes, but clearly marked as historical

### Knowledge Extraction Before Consolidation

#### Pre-Consolidation Mining Protocol

```markdown
## Before Consolidating, Extract:

### 1. Failed Approaches
- What was tried that didn't work?
- Why did it fail?
- What constraints prevented success?
- What would need to change to make it work?

### 2. Security Discoveries
- What vulnerabilities were found?
- How were they exploited?
- What was the fix?
- What patterns prevent recurrence?

### 3. Performance Learnings
- What caused slowdowns?
- Which optimizations worked?
- Which optimizations failed?
- What are the performance boundaries?

### 4. Integration Gotchas
- What external system quirks were discovered?
- What undocumented behaviors exist?
- What workarounds are in place?
- What are the failure modes?

### 5. Debugging Insights
- What were the hard-to-find bugs?
- What were the symptoms vs root causes?
- What debugging techniques worked?
- What red herrings wasted time?

### 6. Customer/User Feedback
- What issues did users report?
- What features were requested but not implemented?
- What UX problems were identified?
- What usage patterns emerged?
```

### Enhanced Consolidation Process With Knowledge Preservation

#### Phase 1: Knowledge Mining

```markdown
Please analyze all documentation and code history for [feature/module]:

1. **Extract Historical Knowledge:**
   - Failed approaches and why they failed
   - Security issues discovered and resolved
   - Performance problems and solutions
   - Integration challenges and workarounds
   - Bug patterns and root causes
   - Architectural decisions and rationale

2. **Create Permanent Records:**
   - Write ADRs for major decisions
   - Document failed approaches in FAILED-* files
   - Record security fixes in SECURITY-* files
   - Capture performance learnings in PERF-* files
   - Save migration experiences in MIGRATION-* files

3. **Identify Reusable Patterns:**
   - What solutions can be templates?
   - What mistakes keep recurring?
   - What warnings should future developers see?
```

#### Phase 2: Consolidation With Context

```markdown
Now consolidate the current implementation while preserving history:

1. **Update Current State Docs (Tier 1):**
   - Current implementation guide
   - Active configurations
   - Setup instructions
   - API documentation

2. **Reference Historical Context:**
   - Link to relevant ADRs
   - Note "Don't do X, see FAILED-001"
   - Include "For history, see MIGRATION-001"
   - Add warnings from security incidents

3. **Archive Previous Version:**
   - Tag current docs with timestamp
   - Move to archive/ directory
   - Maintain searchability
   - Add deprecation notice
```

### Knowledge Preservation Templates

#### Architectural Decision Record (ADR) Template

```markdown
# ADR-[number]: [Title]

## Status
[Accepted/Deprecated/Superseded by ADR-XXX]

## Context
What problem were we solving? What constraints existed?

## Decision
What did we decide to do?

## Consequences
What happened as a result? Both good and bad.

## Alternatives Considered
What else did we try or consider?

## Lessons Learned
What would we do differently knowing what we know now?

## Related Documents
- Links to implementation
- Related ADRs
- Failed attempts documentation
```

#### Failed Approach Documentation Template

```markdown
# FAILED-[number]: [What We Tried]

## Date Attempted
[YYYY-MM-DD]

## What We Tried
Detailed description of the approach

## Why It Failed
- Root cause of failure
- Constraints that prevented success
- Performance/security/compatibility issues

## What We Learned
Key insights gained from the failure

## Future Considerations
Under what conditions might this approach work?

## Alternative Solution
What we did instead (link to current implementation)

## Warning for Future Developers
Specific things to watch out for
```

### Consolidation Prompt with Knowledge Preservation

```markdown
Please perform a knowledge-preserving consolidation of [feature]:

1. **Mine Historical Knowledge** (DO NOT DELETE):
   - Extract all failed approaches → Create FAILED-* docs
   - Extract security incidents → Create SECURITY-* docs
   - Extract performance insights → Create PERF-* docs
   - Extract architectural decisions → Create/Update ADRs
   - Extract debugging insights → Create DEBUG-* docs

2. **Consolidate Current State**:
   - Merge all current documentation into single authoritative guide
   - Include "Historical Context" section with links to decision history
   - Add "Lessons Learned" callouts from historical knowledge
   - Reference ADRs for major design decisions
   - Include warnings from failed approaches

3. **Archive Responsibly**:
   - Tag current version before consolidation
   - Move old docs to archive/ with timestamp
   - Add README to archive explaining the consolidation
   - Maintain search index for archived content

4. **Create Knowledge Index**:
   ```markdown
   # Knowledge Index for [Feature]

   ## Current Documentation
   - [Link to consolidated guide]

   ## Historical Context
   - ADR-001: Why we chose approach X
   - FAILED-001: Why approach Y didn't work
   - SECURITY-001: XSS vulnerability fix
   - PERF-001: Query optimization journey

   ## Key Warnings
   - Never do X (see FAILED-002)
   - Always check Y (see SECURITY-003)
   - Performance limit Z (see PERF-002)
   ```

5. **Validate Nothing Lost**:
   - All security fixes documented
   - All failed approaches captured
   - All performance learnings preserved
   - All architectural decisions recorded
   - All debugging insights saved
```

### Knowledge Preservation Checklist

```markdown
# Pre-Consolidation Knowledge Preservation Checklist

## Failed Approaches
- [ ] Identified all approaches that didn't work
- [ ] Documented why each approach failed
- [ ] Created FAILED-* documents for significant failures
- [ ] Added warnings to prevent re-attempts

## Security History
- [ ] Identified all security issues found and fixed
- [ ] Created SECURITY-* documents for each incident
- [ ] Documented prevention patterns
- [ ] Added security warnings to current docs

## Performance Journey
- [ ] Captured all performance problems encountered
- [ ] Documented successful optimizations
- [ ] Recorded performance boundaries discovered
- [ ] Created PERF-* documents for significant findings

## Architectural Decisions
- [ ] Created/updated ADRs for major decisions
- [ ] Documented alternatives considered
- [ ] Captured consequences (good and bad)
- [ ] Linked ADRs from current documentation

## Integration Experiences
- [ ] Documented external system quirks
- [ ] Captured workarounds and their reasons
- [ ] Created INTEGRATION-* docs for complex integrations
- [ ] Added integration warnings to current docs

## Debugging Insights
- [ ] Documented hard-to-find bugs
- [ ] Captured symptom vs root cause distinctions
- [ ] Created DEBUG-* docs for complex issues
- [ ] Added debugging tips to current docs

## Migration History
- [ ] Documented migration challenges
- [ ] Captured rollback procedures that worked
- [ ] Created MIGRATION-* docs for each migration
- [ ] Added migration warnings to current docs
```

### Anti-Patterns in Knowledge Preservation

#### ❌ Don't Do This

1. **Blind Deletion**
   - Deleting old docs without extracting insights
   - Removing "failed attempt" documentation
   - Discarding debugging notes

2. **Over-Consolidation**
   - Combining different types of knowledge
   - Losing detail in the name of brevity
   - Removing "why" in favor of only "what"

3. **Poor Organization**
   - Mixing historical and current docs
   - No clear marking of deprecated content
   - Unsearchable archives

#### ✅ Do This Instead

1. **Thoughtful Extraction**
   - Mine insights before consolidating
   - Preserve failure documentation
   - Keep debugging journey records

2. **Structured Preservation**
   - Separate tiers for different knowledge types
   - Maintain appropriate detail levels
   - Always preserve the "why"

3. **Clear Organization**
   - Distinct folders for current/history/archive
   - Clear deprecation notices
   - Searchable, indexed archives

## Automated Knowledge Preservation

### Git Hooks for Knowledge Capture

```bash
#!/bin/bash
# pre-consolidation hook

echo "Knowledge Preservation Check:"
echo "Have you created FAILED-* docs for failed approaches? [y/n]"
read -r response
if [[ "$response" != "y" ]]; then
    echo "Please document failed approaches before consolidating"
    exit 1
fi

echo "Have you updated/created relevant ADRs? [y/n]"
read -r response
if [[ "$response" != "y" ]]; then
    echo "Please update ADRs before consolidating"
    exit 1
fi
```

### Knowledge Extraction Script

```python
# extract_knowledge.py
import os
import re
from datetime import datetime

def extract_historical_knowledge(directory):
    """Extract important historical knowledge before consolidation"""

    knowledge = {
        'failed_approaches': [],
        'security_fixes': [],
        'performance_insights': [],
        'architectural_decisions': [],
        'debugging_insights': []
    }

    # Scan for patterns indicating historical knowledge
    patterns = {
        'failed': r'(didn\'t work|failed|unsuccessful|abandoned)',
        'security': r'(vulnerability|security|injection|XSS|CSRF)',
        'performance': r'(slow|optimization|performance|bottleneck)',
        'decision': r'(decided|chose|selected|went with)',
        'debug': r'(root cause|actual problem|real issue)'
    }

    # Extract and categorize knowledge
    for root, dirs, files in os.walk(directory):
        for file in files:
            if file.endswith('.md'):
                with open(os.path.join(root, file), 'r') as f:
                    content = f.read()

                    for category, pattern in patterns.items():
                        if re.search(pattern, content, re.IGNORECASE):
                            knowledge[f'{category}_insights'].append({
                                'file': file,
                                'matches': re.findall(pattern, content, re.IGNORECASE)
                            })

    # Generate preservation report
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    report_path = f'docs/knowledge-extraction-{timestamp}.md'

    with open(report_path, 'w') as report:
        report.write('# Knowledge Extraction Report\n\n')
        report.write(f'Generated: {datetime.now()}\n\n')

        for category, items in knowledge.items():
            report.write(f'## {category.replace("_", " ").title()}\n\n')
            for item in items:
                report.write(f'- **{item["file"]}**: {len(item["matches"])} relevant passages\n')

        report.write('\n## Action Required\n\n')
        report.write('Review these files and create appropriate decision history documents:\n')
        report.write('- [ ] Create FAILED-* docs for failed approaches\n')
        report.write('- [ ] Create SECURITY-* docs for security fixes\n')
        report.write('- [ ] Create PERF-* docs for performance insights\n')
        report.write('- [ ] Update ADRs for architectural decisions\n')
        report.write('- [ ] Create DEBUG-* docs for debugging insights\n')

    return report_path

# Run extraction
if __name__ == '__main__':
    report = extract_historical_knowledge('./docs')
    print(f'Knowledge extraction report generated: {report}')
    print('Please review and create decision history documents before consolidating.')
```

## Metrics for Knowledge Preservation

### Success Metrics

```markdown
# Knowledge Preservation Metrics

## Quantitative Metrics
- Decision history docs created: [count]
- Failed approaches documented: [count]
- Security incidents captured: [count]
- Performance insights recorded: [count]
- ADRs written/updated: [count]

## Qualitative Metrics
- Can new developers understand why decisions were made? [yes/no]
- Are past failures preventing re-attempts? [yes/no]
- Is security history informing current practices? [yes/no]
- Are performance boundaries well documented? [yes/no]
- Can we trace current design to original requirements? [yes/no]

## Knowledge Accessibility
- Time to find historical context: [target: <2 minutes]
- Searchability of archived content: [searchable/not searchable]
- Clarity of deprecation notices: [clear/unclear]
- Linking between current and historical docs: [complete/partial/none]
```

## Sample Workflow: Complete Knowledge-Preserving Consolidation

### Example: Email Integration Consolidation

**Step 1: Pre-Consolidation Audit**
```markdown
Found:
- 5 versions of email integration plans
- 2 failed OAuth attempts
- 1 security incident (token exposure)
- 3 performance optimization iterations
- Multiple debugging sessions for async issues
```

**Step 2: Knowledge Extraction**
```markdown
Created:
- FAILED-001-oauth-with-service-x.md (why OAuth failed)
- FAILED-002-websocket-email-sync.md (real-time sync issues)
- SECURITY-001-token-exposure-fix.md (how tokens were exposed)
- PERF-001-batch-email-processing.md (why batching was needed)
- DEBUG-001-async-race-condition.md (the async bug that took 2 days)
- ADR-003-email-service-selection.md (why we chose service Y)
```

**Step 3: Consolidate Current State**
```markdown
Created: docs/current/email-integration-guide.md
- Current implementation (using service Y)
- Configuration and setup
- API reference
- Testing procedures
- "Historical Context" section linking to decision history
- "Known Issues" with references to DEBUG-* docs
- "Security Considerations" referencing SECURITY-001
- "Performance Guidelines" referencing PERF-001
```

**Step 4: Archive Previous Versions**
```markdown
Moved to: docs/archive/2024-01-15-pre-consolidation/
- All 5 previous plan versions
- Old implementation attempts
- Original debugging notes
- Added README explaining the consolidation
```

**Step 5: Validation**
```markdown
✓ No historical knowledge lost
✓ Failed approaches documented and linked
✓ Security incident preserved with lessons
✓ Performance journey captured
✓ Current docs reference historical context
✓ Archive searchable and organized
```

## Conclusion

Knowledge preservation during consolidation is not just about preventing repeated mistakes—it's about building institutional memory that makes your codebase antifragile. Every failure, every security incident, every performance bottleneck teaches valuable lessons that should be preserved and made accessible.

The three-tier architecture (Current/Decision History/Archive) ensures that consolidation improves clarity without sacrificing wisdom. By systematically extracting and preserving historical knowledge before consolidating, we maintain the benefits of clean documentation while retaining hard-won insights.

Remember: **Delete the redundant, preserve the wisdom.**

## Quick Reference

### Essential Commands
```bash
# Before consolidating
./extract_knowledge.py  # Run knowledge extraction

# Create decision history
mkdir -p docs/decision-history
touch docs/decision-history/ADR-001-title.md

# Archive with timestamp
timestamp=$(date +%Y%m%d_%H%M%S)
mkdir -p docs/archive/$timestamp
mv docs/old-docs/* docs/archive/$timestamp/

# Search archives
grep -r "search term" docs/archive/

# Tag before major consolidation
git tag -a "pre-consolidation-$(date +%Y%m%d)" -m "Snapshot before consolidation"
```

## Related Documentation

- [Project Organization Guidelines](../08-project-management/PROJECT_ORGANIZATION.md)
- [Continuous Improvement](../05-refactoring-and-improvement/CONTINUOUS_IMPROVEMENT.md)
- [Code Reviews](./CODE_REVIEWS.md)
- [CLAUDE.md Agent Architecture](../CLAUDE.md)