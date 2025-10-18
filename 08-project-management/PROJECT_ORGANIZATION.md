# Project Organization Guidelines

## 📁 Directory Structure Philosophy

This project follows a clear separation between **production codebase** and **development utilities**:

### 🏗️ **Production Codebase** (Core Project)

```
src/                    # Main application code
tests/                  # Formal test suite
requirements.txt        # Production dependencies
pyproject.toml         # Project configuration
README.md              # Project documentation
```

### 🛠️ **Development Infrastructure** (Clearly Separated)

```
dev-tools/             # Development scripts & utilities
├── scripts/           # One-off testing & debugging scripts
└── test-results/      # Historical test outputs

cicd/                  # CI/CD infrastructure
├── scripts/           # Build & deployment automation
└── infrastructure/    # Cloud infrastructure templates

testing_scripts/       # Specialized testing utilities
logs/                  # Application & debug logs
test-results/          # Current test artifacts
```

## 📋 File Organization Rules

### ✅ **Development Files Should Be:**

1. **Clearly separated** from production code
2. **Well documented** with purpose and usage
3. **Organized by category** (scripts, results, logs, etc.)
4. **Periodically cleaned up** to remove obsolete files

### ❌ **Avoid in Root Directory:**

- Test scripts (`test_*.py` unless part of formal test suite)
- Development utilities (`update_*.py`, `run_*.py`)
- Log files (`*.log`, `debug_*.txt`)
- Test results (`*_results.txt`, `coverage.txt`)
- Build artifacts and temporary files

### 🧹 **Cleanup Guidelines:**

- **Before commits**: Move development files to appropriate directories
- **After features**: Remove obsolete scripts and test files
- **Periodically**: Archive old logs and test results
- **Documentation**: Update README files when adding new utility categories

## 🔍 **Quick Reference**

| File Type            | Location                  | Purpose               |
| -------------------- | ------------------------- | --------------------- |
| `test_*.py` (ad-hoc) | `dev-tools/scripts/`      | Development testing   |
| `run_*.py`           | `dev-tools/scripts/`      | Development utilities |
| `update_*.py`        | `dev-tools/scripts/`      | Maintenance scripts   |
| `*.log`              | `logs/`                   | Application logs      |
| `*_results.txt`      | `dev-tools/test-results/` | Test outputs          |
| CI/CD scripts        | `cicd/scripts/`           | Build automation      |
| Formal tests         | `tests/`                  | Production test suite |

This organization ensures a clean, maintainable project structure that clearly separates development tooling from the core application.
