
# Python Dependency Cache & Duplicate Files Guidance

## Principles
- Treat virtual environments and compiled caches as **disposable**.
- Keep all environments and caches **out of version control**.
- Use a dependency manager with a **lockfile** for deterministic installs.
- Share **download caches**, not `site-packages` folders across projects.
- Periodically **prune** caches locally and in CI.

## Recommended Tools
- Dependency manager: **uv** (preferred) or **Poetry**.
- Linting/format: **Ruff** (with `pre-commit`).

## .gitignore (baseline)
```gitignore
# Python bytecode/caches
__pycache__/
*.py[cod]
*.so
*.pyd

# Packaging/metadata
*.egg-info/
.eggs/
build/
dist/

# Virtual environments
.venv/
venv/
.env/
.python-version
.__pypackages__/

# Tool caches
.mypy_cache/
.pytest_cache/
.ruff_cache/
.cache/
```

## Cleanup Commands (safe to run)
```bash
# pip
pip cache purge || true

# uv
uv cache prune || true

# poetry
poetry cache clear pypi --all -n || true

# remove Python bytecode
find . -name "__pycache__" -type d -prune -exec rm -rf {} +
```

## Pre-commit
```yaml
repos:
- repo: https://github.com/pre-commit/pre-commit-hooks
  rev: v4.6.0
  hooks:
    - id: check-merge-conflict
    - id: end-of-file-fixer
    - id: trailing-whitespace

- repo: https://github.com/astral-sh/ruff-pre-commit
  rev: v0.5.7
  hooks:
    - id: ruff
      args: [--fix]

- repo: local
  hooks:
    - id: clean-pyc
      name: Remove __pycache__ folders
      entry: bash -c "find . -name '__pycache__' -type d -prune -exec rm -rf {} +"
      language: system
      pass_filenames: false
```

## GitHub Actions: cache downloads, block cache dirs in git
```yaml
# .github/workflows/ci.yml
name: CI
on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: "3.11"

      # Fail if envs/caches are committed
      - name: Ensure no envs/caches are tracked
        run: |
          set -e
          disallowed='(\.venv|venv|__pycache__|\.pytest_cache|\.mypy_cache|\.ruff_cache|\.cache)(/|$)'
          if git ls-files -z | xargs -0 -n1 | grep -E "$disallowed"; then
            echo "Error: disallowed cache/env directories are tracked in git."
            exit 1
          fi

      # Cache pip (or uv/poetry caches) keyed on lockfiles
      - name: Cache pip wheels
        uses: actions/cache@v4
        with:
          path: ~/.cache/pip
          key: ${{ runner.os }}-pip-${{ hashFiles('**/requirements*.txt', '**/uv.lock', '**/poetry.lock') }}
          restore-keys: ${{ runner.os }}-pip-

      - name: Install deps
        run: |
          python -m pip install -U pip
          if [ -f uv.lock ]; then
            pip install uv && uv sync --frozen
          elif [ -f poetry.lock ]; then
            pip install poetry && poetry install --no-root --no-interaction --no-ansi
          elif ls requirements*.txt >/dev/null 2>&1; then
            pip install -r requirements.txt
          else
            echo "No lockfile or requirements* found"; exit 1
          fi

      - name: Run tests
        run: pytest -q
```

## AWS CodeBuild/CodePipeline (cache downloads, slim artifacts)
```yaml
# buildspec.yml
version: 0.2
phases:
  install:
    runtime-versions:
      python: 3.11
    commands:
      - pip install -U pip
      - |
        if [ -f uv.lock ]; then
          pip install uv
          uv sync --frozen
        elif [ -f poetry.lock ]; then
          pip install poetry
          poetry install --no-root --no-interaction --no-ansi
        elif ls requirements*.txt >/dev/null 2>&1; then
          pip install -r requirements.txt
        else
          echo "No lockfile or requirements* found"; exit 1
        fi
  pre_build:
    commands:
      - echo "Ensuring no envs/caches are checked in"
      - |
        disallowed='(\.venv|venv|__pycache__|\.pytest_cache|\.mypy_cache|\.ruff_cache|\.cache)(/|$)'
        if git ls-files -z | xargs -0 -n1 | grep -E "$disallowed"; then
          echo "Error: disallowed cache/env directories are tracked in git."
          exit 1
        fi
  build:
    commands:
      - pytest -q
cache:
  paths:
    - /root/.cache/pip/**/*
    - /root/.cache/uv/**/*
    - /root/.cache/pypoetry/**/*
artifacts:
  files:
    - "**/*"
  discard-paths: no
```

## Docker (final stage without wheel cache)
```dockerfile
# multi-stage build (example)
FROM python:3.11-slim AS builder
WORKDIR /app
COPY pyproject.toml poetry.lock* requirements*.txt uv.lock* ./
# Install deps and build wheels in builder only
RUN pip install -U pip && pip wheel --wheel-dir /wheels -r requirements.txt || true

FROM python:3.11-slim AS runtime
WORKDIR /app
COPY --from=builder /wheels /wheels
RUN pip install --no-cache-dir /wheels/* || true
COPY . .
CMD ["python", "-m", "your_app"]
```

## Monorepo Notes
- Prefer **one env per service/package**.
- Use a workspace (Poetry) or one lockfile per service.
- Standardize env location to `.venv` in each service root.

## Acceptance Criteria
- Fresh clone + single command produces deterministic environment.
- No `__pycache__`, envs, or tool caches tracked by git.
- CI uses a download cache keyed on lockfiles.
- Docker images contain no pip/uv/poetry cache in final layer.
```
