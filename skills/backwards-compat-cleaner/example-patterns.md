# Example Patterns This Skill Will Find

## Common Backwards Compatibility Anti-Patterns in Greenfield Projects

### 1. Renamed Functions/Classes Keeping Old Names
```python
# ❌ Found in many files
ProcessOrderV2 = ProcessOrder  # Backwards compat
create_user_account = create_account  # Old name preserved
LegacyAuthHandler = ModernAuthHandler  # Temporary alias
```

### 2. Dual Implementation Switches
```python
# ❌ Conditional logic for old vs new
def handle_request(data, use_legacy=False):
    if use_legacy or settings.ENABLE_LEGACY_MODE:
        return old_handler(data)
    return new_handler(data)
```

### 3. Unused Migration Code
```python
# ❌ Migration code that never needs to run
if database_version < "2.0":
    migrate_old_schema()
    update_legacy_records()
```

### 4. Multiple API Versions
```
# ❌ Maintaining multiple versions unnecessarily
/api/v1/users  (marked deprecated but still there)
/api/v2/users  (current but also being replaced)
/api/v3/users  (latest)
```

### 5. Test-Only Legacy Code
```python
# ❌ Tests for backwards compat that don't apply
class TestLegacyBehavior:
    def test_old_format_still_works(self):
        # Testing something that will never be used
```

### 6. Environment Flags Never Used
```python
# ❌ Feature flags that are always False
if os.getenv('USE_OLD_PROCESSOR', 'false') == 'true':
    # This code path is never taken
```

### 7. Database Columns "Just in Case"
```sql
-- ❌ Columns added for compatibility but never used
ALTER TABLE orders ADD COLUMN legacy_status VARCHAR(50);  -- Never populated
ALTER TABLE users ADD COLUMN old_user_id INT;  -- Migration placeholder
```

## What This Skill Does

1. **Finds** all these patterns systematically
2. **Checks** git history to understand why they exist
3. **Analyzes** if they're actually used anywhere
4. **Documents** the impact of removing them
5. **Helps** you clean them up safely

## Expected Results for Your Project

Based on typical greenfield projects:
- **15-25%** of backwards compat code is completely unused
- **30-40%** is only used in tests
- **20-30%** could be removed with minor updates
- **10-15%** might need careful review

## Benefits of Cleanup

- 🚀 **Performance**: Remove unnecessary conditionals
- 📦 **Size**: Reduce bundle/deployment size
- 🧹 **Maintainability**: Less code to maintain
- 🎯 **Clarity**: Single implementation path
- ⚡ **Speed**: Faster test execution
- 📚 **Documentation**: Cleaner, focused docs