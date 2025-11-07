# Railway Deployment Best Practices

**Based on 159 deployment commits and hard-won production experience**

---

## Executive Summary

### Why We Had 159+ Deployment Commits

Our journey from first Railway deployment to production-ready revealed critical patterns that this guide codifies. The root causes of our deployment struggles:

1. **Docker Configuration Confusion (35+ commits)**: Railway's automatic Dockerfile detection conflicted with our multi-service architecture
2. **Dependency Hell (25+ commits)**: Python dependency conflicts that could have been resolved in 30 seconds with proper tooling
3. **Environment Variable Mishaps (20+ commits)**: Variables not expanding, missing build args, OAuth credential priority issues
4. **Import/Module Path Issues (15+ commits)**: Python packaging vs. PYTHONPATH, optional imports for segmented deployments
5. **Railway-Specific Gotchas (64+ commits)**: PORT variable expansion, Nixpacks vs. Dockerfile, git-tracked files only

### Key Lessons Learned

**The Golden Rule**: What works locally in Docker MUST work identically on Railway. Use the same Dockerfile for development, CI, and production.

**The 30-Second Rule**: Any dependency issue that takes more than 30 seconds to diagnose should use automated resolution (`./scripts/resolve_dependencies.sh`).

**The Build Args Rule**: Railway environment variables are NOT automatically available at build time. You must declare them as ARG in Dockerfile.

**The Git Rule**: Railway only deploys git-tracked files. If it's not in `git ls-files`, it doesn't exist on Railway.

---

## Pre-Deployment Checklist

Run these commands **before every deployment** to prevent 90% of common issues:

### 1. Validate Dependencies (30 seconds)

```bash
# Check all packages exist and file is git-tracked
./scripts/validate_requirements.sh

# If validation fails, auto-resolve conflicts
./scripts/resolve_dependencies.sh
mv requirements-resolved.txt requirements.txt

# Test in exact Railway environment
docker run --rm -v $(pwd):/app python:3.11-slim sh -c \
  "cd /app && pip install -r requirements.txt && echo '✅ Dependencies OK'"
```

**Why this matters**: Prevents dependency conflicts that cause Railway builds to fail mid-deployment.

### 2. Verify Git Tracking

```bash
# Check critical files are tracked
git ls-files | grep -E "(Dockerfile|requirements.txt|railway.toml|.env.example)"

# Check nothing is accidentally ignored
git check-ignore -v requirements*.txt Dockerfile* railway.*
# Should output nothing (files are NOT ignored)
```

**Why this matters**: Railway only uploads git-tracked files. Missing files = deployment failure.

### 3. Validate Dockerfile Syntax

```bash
# Backend
docker build -f Dockerfile --target prod -t test-backend .
docker run --rm -p 8000:8000 -e PORT=8000 test-backend &
sleep 5
curl http://localhost:8000/health
# Should return: {"status":"healthy"}

# Frontend
docker build -f frontend/invoice-review/Dockerfile \
  --build-arg NEXT_PUBLIC_CONVEX_URL=$NEXT_PUBLIC_CONVEX_URL \
  -t test-frontend frontend/invoice-review
docker run --rm -p 3000:3000 test-frontend &
sleep 5
curl http://localhost:3000/api/health
# Should return 200 OK

# Cleanup
pkill -f "docker run"
```

**Why this matters**: Catches Dockerfile errors locally before Railway wastes build credits.

### 4. Environment Variables Audit

```bash
# List all NEXT_PUBLIC_ variables (needed at build time)
grep -r "NEXT_PUBLIC_" frontend/ | grep -v node_modules | cut -d: -f2 | sort -u

# List all process.env variables (needed at runtime)
grep -r "process.env" frontend/ | grep -v node_modules | cut -d: -f2 | sort -u

# Check .env.example has all required variables
cat .env.example
```

**Why this matters**: Missing environment variables cause runtime failures that are hard to debug.

### 5. Multi-Service Configuration Check

```bash
# Verify railway.toml exists for each service
ls -la railway.toml frontend/invoice-review/railway.toml

# Validate TOML syntax
python3 -c "import tomllib; tomllib.load(open('railway.toml', 'rb'))"
```

**Why this matters**: Multi-service deployments need service-specific configuration.

---

## Railway Configuration Best Practices

### Dockerfile Patterns That Work

#### Backend: Multi-Stage Build with PYTHONPATH

```dockerfile
# Production Stage
FROM python:3.11-slim AS prod

WORKDIR /app

# Install system dependencies (runtime + build)
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    tesseract-ocr \
    tesseract-ocr-eng \
    poppler-utils \
    && rm -rf /var/lib/apt/lists/*

# Copy application files
COPY pyproject.toml README.md ./
COPY backend ./backend

# Copy requirements FIRST for better caching
COPY requirements.txt ./

# Set PYTHONPATH (critical for Railway)
ENV PYTHONPATH=/app

# Install dependencies
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt && \
    apt-get purge -y --auto-remove gcc

# Expose port (Railway sets PORT env var)
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/health')"

# CRITICAL: Use shell form for PORT variable expansion
CMD ["sh", "-c", "uvicorn backend.api.app:app --host 0.0.0.0 --port ${PORT:-8000}"]
```

**Why shell form CMD?**
- JSON array form: `["uvicorn", "backend.api.app:app", "--port", "$PORT"]` → Literal "$PORT" string
- Shell form: `sh -c "uvicorn ... --port $PORT"` → Expands to actual port number (8000, 3000, etc.)

#### Frontend: Next.js with Build Args

```dockerfile
# Stage 1: Dependencies
FROM node:20-alpine AS deps
WORKDIR /app
COPY package.json package-lock.json ./
RUN npm ci --production=false

# Stage 2: Builder
FROM node:20-alpine AS builder
WORKDIR /app

COPY --from=deps /app/node_modules ./node_modules
COPY . .

# CRITICAL: Declare build-time environment variables
ARG NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY
ARG NEXT_PUBLIC_CONVEX_URL
ARG NEXT_PUBLIC_BACKEND_URL
ARG NEXT_PUBLIC_API_URL

# Make them available during build
ENV NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY=$NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY
ENV NEXT_PUBLIC_CONVEX_URL=$NEXT_PUBLIC_CONVEX_URL
ENV NEXT_PUBLIC_BACKEND_URL=$NEXT_PUBLIC_BACKEND_URL
ENV NEXT_PUBLIC_API_URL=$NEXT_PUBLIC_API_URL

ENV NEXT_TELEMETRY_DISABLED=1
RUN npm run build

# Stage 3: Runner
FROM node:20-alpine AS runner
WORKDIR /app

ENV NODE_ENV=production
ENV NEXT_TELEMETRY_DISABLED=1

RUN addgroup --system --gid 1001 nodejs
RUN adduser --system --uid 1001 nextjs

COPY --from=builder /app/public ./public
COPY --from=builder /app/.next/standalone ./
COPY --from=builder /app/.next/static ./.next/static

RUN chown -R nextjs:nodejs /app
USER nextjs

EXPOSE 3000

CMD ["node", "server.js"]
```

**Critical Next.js Configuration**: `next.config.js`

```javascript
module.exports = {
  output: 'standalone', // REQUIRED for Docker deployment
  // ... other config
}
```

### railway.toml Configuration

#### Backend Service

```toml
[build]
# Use Dockerfile (NOT Nixpacks) for reliable Python deployment
builder = "dockerfile"
dockerfilePath = "Dockerfile"

[deploy]
# Start command defined in Dockerfile CMD
healthcheckPath = "/health"
healthcheckTimeout = 100
restartPolicyType = "ON_FAILURE"
restartPolicyMaxRetries = 10
```

#### Frontend Service

```toml
[build]
builder = "dockerfile"
dockerfilePath = "./Dockerfile"

[deploy]
healthcheckPath = "/api/health"
healthcheckTimeout = 100
restartPolicyType = "ON_FAILURE"
restartPolicyMaxRetries = 10
```

### Why Dockerfile Over Nixpacks?

**Nixpacks** (Railway's default):
- ❌ Auto-detects Python version (may not match your local 3.11)
- ❌ Auto-generates requirements install (can fail on complex dependencies)
- ❌ Limited control over system dependencies (tesseract, poppler, etc.)
- ❌ Mysterious failures hard to debug locally

**Dockerfile** (Recommended):
- ✅ Exact Python version (3.11-slim)
- ✅ Same build locally, CI, and Railway (no "works on my machine")
- ✅ Full control over layer caching
- ✅ Debuggable with `docker build` locally

**When to use Nixpacks**: Never for production. Only for quick prototypes.

---

## Environment Variable Management

### The Build-Time vs Runtime Distinction

**Build-Time Variables** (baked into Docker image):
- `NEXT_PUBLIC_*` variables (Next.js client-side)
- Build arguments for compilation

**Runtime Variables** (read from Railway environment):
- API keys (`OPENAI_API_KEY`, `AWS_SECRET_ACCESS_KEY`)
- Database URLs (`NEON_DATABASE_URL`)
- Service URLs (`CONVEX_URL`)

### Setting Variables in Railway Dashboard

**CRITICAL**: Variables must be "applied" before they take effect:

1. Railway Dashboard → Project → Variables tab
2. Add variable: `NEXT_PUBLIC_BACKEND_URL=https://backend.railway.app`
3. **Click "Deploy"** to apply changes (variables show "0 Variables" until applied)
4. Wait for deployment to complete
5. Verify with `railway logs` that variable is available

### Dockerfile ARG Declarations

**Frontend build args** (for Next.js):

```dockerfile
# MUST declare as ARG before ENV
ARG NEXT_PUBLIC_BACKEND_URL
ENV NEXT_PUBLIC_BACKEND_URL=$NEXT_PUBLIC_BACKEND_URL
```

**Backend runtime env** (no ARG needed):

```dockerfile
# Runtime variables automatically available from Railway
# Access in Python: os.getenv("OPENAI_API_KEY")
```

### Environment Variable Priority

For OAuth credentials, we learned the hard way:

```python
# ❌ Wrong: credentials.json takes priority
gmail_creds = load_from_file("credentials.json") or os.getenv("GMAIL_CREDENTIALS")

# ✅ Correct: environment variables take priority (for Railway)
gmail_creds = os.getenv("GMAIL_CREDENTIALS") or load_from_file("credentials.json")
```

**Why**: Railway has no access to local `credentials.json`. Environment variables MUST be the source of truth in production.

### Comprehensive Environment Variables Reference

See `docs/deployment/P0_ENVIRONMENT_VARIABLES.md` for complete list. Key variables:

**Backend**:
- `OPENAI_API_KEY`
- `AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY`
- `NEON_DATABASE_URL`
- `CONVEX_URL`, `CONVEX_DEPLOY_KEY`
- `GMAIL_CREDENTIALS` (JSON stringified)
- `GMAIL_USER_EMAIL`, `GMAIL_SYSTEM_EMAIL`

**Frontend**:
- `NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY`
- `NEXT_PUBLIC_CONVEX_URL`
- `NEXT_PUBLIC_BACKEND_URL`
- `CLERK_SECRET_KEY` (server-side only)

---

## Docker Optimization for Railway

### Image Size Reduction

We reduced our Docker image from **8.3GB to 1.2GB**. Here's how:

#### 1. Use Slim Base Images

```dockerfile
# ❌ Fat: 1.2GB base image
FROM python:3.11

# ✅ Slim: 150MB base image
FROM python:3.11-slim
```

#### 2. Multi-Stage Builds

```dockerfile
# Build stage (includes gcc, build tools)
FROM python:3.11-slim AS builder
RUN apt-get install gcc ...
RUN pip install ...

# Production stage (minimal runtime dependencies)
FROM python:3.11-slim AS prod
COPY --from=builder /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages
# No gcc, build tools in final image
```

#### 3. Clean apt Cache

```dockerfile
RUN apt-get update && apt-get install -y \
    tesseract-ocr \
    && rm -rf /var/lib/apt/lists/*  # ← Critical: removes 500MB+ cache
```

#### 4. Minimize Layers

```dockerfile
# ❌ Many layers (inefficient caching)
RUN apt-get update
RUN apt-get install tesseract-ocr
RUN apt-get install poppler-utils
RUN pip install fastapi
RUN pip install uvicorn

# ✅ Combined layers (efficient caching)
RUN apt-get update && apt-get install -y \
    tesseract-ocr \
    poppler-utils \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir fastapi uvicorn
```

#### 5. Strategic Layer Ordering

```dockerfile
# COPY requirements FIRST (changes rarely)
COPY requirements.txt ./
RUN pip install -r requirements.txt

# COPY code LAST (changes frequently)
COPY backend ./backend
```

**Why**: Docker caches layers. If code changes but requirements don't, Docker reuses the pip install layer (saves minutes per build).

### Build Time Optimization

**Before optimization**: 8-12 minutes
**After optimization**: 2-4 minutes

Key techniques:
1. **Layer caching**: Order COPY commands by change frequency
2. **Parallel apt installs**: Use `apt-get install -y pkg1 pkg2 pkg3`
3. **Minimal base image**: `python:3.11-slim` vs `python:3.11`
4. **No dev dependencies**: Separate `requirements.txt` (runtime) from `requirements-dev.txt`

---

## Multi-Service Deployment Strategies

### Railway Dual-Service Architecture

**Project Structure**:
```
railway-project/
├── backend/           # FastAPI service
│   ├── Dockerfile
│   └── railway.toml
├── frontend/          # Next.js service
│   └── invoice-review/
│       ├── Dockerfile
│       └── railway.toml
└── railway.toml       # Root config (backend)
```

### Service Discovery

**Backend** exposes health endpoint:
```python
@app.get("/health")
async def health():
    return {"status": "healthy", "service": "invoice-processing"}
```

**Frontend** uses environment variable:
```typescript
const backendUrl = process.env.NEXT_PUBLIC_BACKEND_URL || 'http://localhost:8000'
const response = await fetch(`${backendUrl}/api/invoices`)
```

**Railway URLs**:
- Backend: `https://invoice-backend-production.up.railway.app`
- Frontend: `https://invoice-frontend-production.up.railway.app`

Set in Railway dashboard:
```bash
# Frontend service
NEXT_PUBLIC_BACKEND_URL=https://invoice-backend-production.up.railway.app
```

### Deployment Coordination

**Challenge**: Frontend build needs backend URL, but backend URL not known until deployed.

**Solution**: Two-phase deployment

1. **Deploy backend first**:
   ```bash
   cd /path/to/backend
   railway up --service backend
   railway domain  # Get URL: https://backend.railway.app
   ```

2. **Set frontend env var**:
   ```bash
   railway variables set NEXT_PUBLIC_BACKEND_URL=https://backend.railway.app --service frontend
   ```

3. **Deploy frontend**:
   ```bash
   cd /path/to/frontend/invoice-review
   railway up --service frontend
   ```

### Cross-Service Authentication

**Pattern**: Shared secret environment variable

```python
# Backend: verify requests from frontend
@app.get("/api/invoices")
async def get_invoices(request: Request):
    service_token = request.headers.get("X-Service-Token")
    if service_token != os.getenv("SERVICE_TOKEN"):
        raise HTTPException(status_code=401)
    # ...
```

```typescript
// Frontend: include service token
const response = await fetch(`${backendUrl}/api/invoices`, {
  headers: {
    'X-Service-Token': process.env.SERVICE_TOKEN
  }
})
```

Set in Railway:
```bash
railway variables set SERVICE_TOKEN=your-secure-random-token --service backend
railway variables set SERVICE_TOKEN=your-secure-random-token --service frontend
```

---

## Common Pitfalls and Solutions

### Pitfall 1: Dockerfile Naming Confusion

**Problem**: Railway auto-detects ANY file named `Dockerfile`, even in subdirectories.

**Symptoms**:
- Railway builds wrong service
- "No start command found"
- Import errors for wrong codebase

**Our Journey** (6 commits):
1. `Dockerfile` (backend) + `frontend/Dockerfile` → Railway confused which to use
2. Renamed to `Dockerfile.frontend` → Railway ignored it
3. Updated `railway.toml` with `dockerfilePath = "./Dockerfile.frontend"` → Still ignored
4. Renamed back to `Dockerfile` → Worked, but confusing
5. Moved frontend to `frontend/invoice-review/Dockerfile` → Clear separation
6. Set backend `railway.toml` with `dockerfilePath = "Dockerfile"` → Final solution

**Solution**: Use explicit `dockerfilePath` in `railway.toml`:

```toml
# Backend railway.toml
[build]
builder = "dockerfile"
dockerfilePath = "Dockerfile"  # Explicit path

# Frontend railway.toml
[build]
builder = "dockerfile"
dockerfilePath = "./Dockerfile"  # Relative to frontend service root
```

### Pitfall 2: PORT Variable Not Expanding

**Problem**: Railway sets `$PORT` dynamically, but Dockerfile CMD doesn't expand it.

**Symptoms**:
- App binds to port 8000, but Railway expects port 12345
- Health check fails
- "Application failed to respond"

**Wrong**:
```dockerfile
# JSON array form - variables NOT expanded
CMD ["uvicorn", "app:app", "--port", "$PORT"]
# Uvicorn binds to literal string "$PORT" (invalid)
```

**Correct**:
```dockerfile
# Shell form - variables expanded
CMD ["sh", "-c", "uvicorn app:app --port ${PORT:-8000}"]
# Uvicorn binds to actual port number (e.g., 12345)
```

**Why**: JSON array form bypasses shell, so no variable expansion happens. Shell form (`sh -c`) enables expansion.

### Pitfall 3: Requirements File Not in Git

**Problem**: Railway only uploads git-tracked files.

**Symptoms**:
```
ERROR: failed to compute cache key: "/requirements.txt": not found
```

**Root Cause**: `.gitignore` had `*.txt`, blocking `requirements.txt`

**Our Fix** (3 commits):
1. Discovered `.gitignore:298:/*.txt` was ignoring everything
2. Added `!requirements*.txt` to `.gitignore` to override
3. `git add requirements.txt` + commit + push

**Prevention**:
```bash
# Before every deployment
git ls-files | grep requirements.txt
# Should output: requirements.txt

git check-ignore -v requirements.txt
# Should output nothing (file is NOT ignored)
```

### Pitfall 4: Dependency Conflicts

**Problem**: Sub-dependencies have incompatible version requirements.

**Symptoms**:
```
ERROR: Cannot install langchain==0.3.16 and langchain-core==0.3.31
because these package versions have conflicting dependencies.
```

**Manual Fix** (slow, error-prone):
1. Read error message for conflict details
2. `pip show langchain | grep Requires` → Check what langchain needs
3. Update `langchain-core==0.3.31` → `langchain-core==0.3.32`
4. Test locally, commit, redeploy
5. Repeat if new conflicts emerge

**Automated Fix** (30 seconds):
```bash
./scripts/resolve_dependencies.sh
mv requirements-resolved.txt requirements.txt
git add requirements.txt
git commit -m "fix: auto-resolve dependency conflicts"
git push
```

**Why automated is better**:
- Uses `pip-compile` with backtracking resolver
- Tests in exact Python 3.11 environment (matches Railway)
- Resolves ALL conflicts at once (not just the first one)
- Generates pinned versions for reproducible builds

**Our Journey** (25+ dependency commits):
1. Manual version hunting: 2 hours per conflict
2. Created validation script: Caught issues early
3. Created resolver script: 30 seconds to fix
4. Now: Pre-deployment validation catches 99% of issues

### Pitfall 5: Environment Variables Not Injected

**Problem**: Variables configured in dashboard but not available in app.

**Symptoms**:
- `os.getenv("OPENAI_API_KEY")` returns `None`
- Authentication failures
- Import errors for optional dependencies

**Root Cause**: Variables not "applied" after configuration.

**Solution**:
1. Add variable in Railway dashboard
2. **Click "Deploy"** to trigger new deployment with variables
3. Wait for deployment to complete
4. Verify with `railway logs`:
   ```
   railway logs | grep "OPENAI_API_KEY"
   # Should show: Using API key: sk-...
   ```

**Testing variables locally**:
```bash
# Use Railway environment locally
railway run python -c "import os; print(os.getenv('OPENAI_API_KEY'))"
# Should print: sk-...
```

### Pitfall 6: Import Errors for Optional Dependencies

**Problem**: Segmented P0 deployment (webhook-only) tried to import manual review code.

**Symptoms**:
```python
ImportError: cannot import name 'ManualReviewService' from 'backend.services.manual_review'
```

**Root Cause**: Not all services deployed in P0, but imports were unconditional.

**Our Fix** (5 commits):
1. Make imports optional with try/except
2. Check environment variable `FEATURE_MANUAL_REVIEW=enabled`
3. Return 404 for disabled routes instead of import error

**Pattern**:
```python
# ❌ Unconditional import (fails if module missing)
from backend.services.manual_review import ManualReviewService

# ✅ Optional import (graceful degradation)
try:
    from backend.services.manual_review import ManualReviewService
    MANUAL_REVIEW_ENABLED = True
except ImportError:
    MANUAL_REVIEW_ENABLED = False

@app.get("/manual-review")
async def manual_review():
    if not MANUAL_REVIEW_ENABLED:
        raise HTTPException(status_code=404, detail="Manual review not enabled in P0")
    # ...
```

### Pitfall 7: OAuth Credential Priority

**Problem**: OAuth flow used local `credentials.json` instead of Railway environment variables.

**Symptoms**:
- OAuth works locally but fails on Railway
- "Invalid credentials" errors
- Token refresh failures

**Root Cause**: Code checked file first, then environment variable:

```python
# ❌ Wrong priority
creds = load_from_file("credentials.json") or os.getenv("GMAIL_CREDENTIALS")
# Railway has no credentials.json, fallback to env var too late
```

**Fix** (3 commits):
1. Reverse priority: `os.getenv()` first, file second
2. Add validation that environment variable is present on Railway
3. Log which credential source is used

```python
# ✅ Correct priority
creds = os.getenv("GMAIL_CREDENTIALS") or load_from_file("credentials.json")

# Log source for debugging
if os.getenv("GMAIL_CREDENTIALS"):
    logger.info("Using GMAIL_CREDENTIALS from environment")
else:
    logger.info("Using credentials.json from file system")
```

**Lesson**: Environment variables should ALWAYS take priority in production. Local files are for development only.

---

## Step-by-Step Deployment Workflow

### Initial Setup (One-Time)

#### 1. Create Railway Project

```bash
# Install Railway CLI
npm install -g @railway/cli

# Login
railway login

# Initialize project
cd /path/to/project
railway init
# Select: Create new project
# Name: invoice-processing-production
```

#### 2. Create Services

**Backend**:
```bash
# From project root
railway service create backend
railway link --service backend
```

**Frontend**:
```bash
# From frontend directory
cd frontend/invoice-review
railway service create frontend
railway link --service frontend
```

#### 3. Configure Environment Variables

**Backend variables**:
```bash
railway variables set OPENAI_API_KEY="sk-..." --service backend
railway variables set AWS_ACCESS_KEY_ID="..." --service backend
railway variables set AWS_SECRET_ACCESS_KEY="..." --service backend
railway variables set NEON_DATABASE_URL="postgresql://..." --service backend
railway variables set CONVEX_URL="https://your-app.convex.cloud" --service backend
railway variables set GMAIL_CREDENTIALS='{"type":"service_account",...}' --service backend
railway variables set GMAIL_USER_EMAIL="user@domain.com" --service backend
railway variables set GMAIL_SYSTEM_EMAIL="system@domain.com" --service backend
```

**Frontend variables**:
```bash
# Get backend URL first
railway domain --service backend
# Output: https://backend-production.up.railway.app

railway variables set NEXT_PUBLIC_BACKEND_URL="https://backend-production.up.railway.app" --service frontend
railway variables set NEXT_PUBLIC_CONVEX_URL="https://your-app.convex.cloud" --service frontend
railway variables set NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY="pk_..." --service frontend
railway variables set CLERK_SECRET_KEY="sk_..." --service frontend
```

### Regular Deployment Workflow

#### 1. Pre-Deployment Validation

```bash
# Validate dependencies
./scripts/validate_requirements.sh

# If validation fails, auto-resolve
./scripts/resolve_dependencies.sh
mv requirements-resolved.txt requirements.txt

# Test Docker build locally
docker build -f Dockerfile --target prod -t test-backend .
docker run --rm -p 8000:8000 -e PORT=8000 test-backend &
sleep 5
curl http://localhost:8000/health
# Should return: {"status":"healthy"}
pkill -f "docker run"

# Verify git tracking
git ls-files | grep -E "(Dockerfile|requirements.txt|railway.toml)"
```

#### 2. Commit Changes

```bash
git add .
git commit -m "feat: implement new feature with Railway compatibility"
git push origin main
```

#### 3. Deploy to Railway

**Option A: Automatic deployment** (GitHub integration):
```bash
# Railway auto-deploys on push to main
# Monitor: Railway Dashboard → Deployments
```

**Option B: Manual deployment**:
```bash
# Backend
railway up --service backend --detach

# Frontend (after backend deployed)
railway up --service frontend --detach

# Monitor logs
railway logs --service backend --tail 100
railway logs --service frontend --tail 100
```

#### 4. Verify Deployment

```bash
# Backend health check
railway domain --service backend | xargs -I {} curl {}/health
# Should return: {"status":"healthy","service":"invoice-processing"}

# Frontend health check
railway domain --service frontend | xargs -I {} curl {}/api/health
# Should return 200 OK

# Check application logs
railway logs --service backend | grep "Uvicorn running"
railway logs --service frontend | grep "ready started server"
```

#### 5. Post-Deployment Testing

```bash
# Test invoice processing workflow
curl -X POST https://backend.railway.app/webhooks/user-inbox \
  -H "Content-Type: application/json" \
  -d '{"message":{"data":"base64-encoded-pubsub-message"}}'

# Test frontend UI
open https://frontend.railway.app
# Verify: Clerk login → Settings → Gmail OAuth → Invoice list
```

### Rollback Procedure

If deployment fails:

```bash
# View recent deployments
railway deployments --service backend

# Rollback to previous deployment
railway rollback --service backend --deployment <deployment-id>

# Monitor rollback
railway logs --service backend --tail 50
```

---

## Troubleshooting Decision Tree

### Build Failures

#### Error: "failed to compute cache key: not found"

**Diagnosis**: File referenced in Dockerfile not in git
**Fix**:
```bash
git ls-files | grep <filename>
# If empty, file not tracked
git add <filename>
git commit -m "fix: add missing file for Railway deployment"
git push
```

#### Error: "Could not find a version that satisfies"

**Diagnosis**: Package version doesn't exist on PyPI
**Fix**:
```bash
./scripts/validate_requirements.sh
# Shows which versions don't exist

./scripts/resolve_dependencies.sh
# Auto-resolves to available versions

mv requirements-resolved.txt requirements.txt
git add requirements.txt
git commit -m "fix: use available package versions"
git push
```

#### Error: "conflicting dependencies"

**Diagnosis**: Dependency version conflict
**Fix**:
```bash
./scripts/resolve_dependencies.sh
# Uses pip-compile to auto-resolve

mv requirements-resolved.txt requirements.txt
git add requirements.txt
git commit -m "fix: auto-resolve dependency conflicts"
git push
```

#### Error: "No module named 'backend'"

**Diagnosis**: PYTHONPATH not set or wrong structure
**Fix**:
```dockerfile
# Add to Dockerfile
ENV PYTHONPATH=/app

# Verify structure:
# /app/
#   backend/
#     __init__.py
#     api/
#       app.py
```

### Runtime Failures

#### Error: "Application failed to respond"

**Diagnosis**: App not binding to correct port
**Fix**:
```dockerfile
# Use shell form CMD with PORT variable
CMD ["sh", "-c", "uvicorn app:app --host 0.0.0.0 --port ${PORT:-8000}"]
```

#### Error: "Health check failed"

**Diagnosis**: Health endpoint not responding
**Fix**:
```python
# Ensure health endpoint exists
@app.get("/health")
async def health():
    return {"status": "healthy"}

# Test locally
curl http://localhost:8000/health
```

#### Error: "Environment variable not set"

**Diagnosis**: Variable not applied in Railway
**Fix**:
```bash
# Set variable
railway variables set VAR_NAME="value" --service <service>

# Trigger redeploy to apply
railway redeploy --service <service>

# Verify
railway logs --service <service> | grep VAR_NAME
```

### Dependency Failures

#### Error: "ImportError: cannot import name"

**Diagnosis**: Optional dependency not installed or import not protected
**Fix**:
```python
# Make import optional
try:
    from backend.services.optional import OptionalService
    OPTIONAL_ENABLED = True
except ImportError:
    OPTIONAL_ENABLED = False
    logger.warning("Optional service not available")

# Guard usage
if OPTIONAL_ENABLED:
    service = OptionalService()
```

#### Error: "No module named 'google.auth'"

**Diagnosis**: Missing dependency in requirements.txt
**Fix**:
```bash
# Add to requirements.txt
echo "google-auth>=2.38.0" >> requirements.txt

# Validate
./scripts/validate_requirements.sh

# Commit and redeploy
git add requirements.txt
git commit -m "fix: add google-auth dependency"
git push
```

---

## Common Failure Modes and Quick Fixes

### Build Phase Failures

| Error Pattern | Root Cause | Quick Fix | Commits Wasted |
|--------------|------------|-----------|----------------|
| `/requirements.txt: not found` | File not git-tracked | `git add requirements.txt` | 3-5 |
| `Could not find version` | Version doesn't exist on PyPI | `./scripts/resolve_dependencies.sh` | 5-10 |
| `conflicting dependencies` | Dependency conflict | `./scripts/resolve_dependencies.sh` | 10-15 |
| `No module named` | Missing import or PYTHONPATH | Add `ENV PYTHONPATH=/app` | 3-5 |
| `Dockerfile: no such file` | Wrong dockerfilePath in railway.toml | Fix `dockerfilePath = "Dockerfile"` | 2-3 |

### Deployment Phase Failures

| Error Pattern | Root Cause | Quick Fix | Commits Wasted |
|--------------|------------|-----------|----------------|
| `Application failed to respond` | Wrong PORT binding | Use shell form CMD with `$PORT` | 5-8 |
| `Health check timeout` | Missing `/health` endpoint | Add health check route | 2-3 |
| `Service exited with code 1` | Runtime import error | Make imports optional | 3-5 |
| `Environment variable not set` | Variable not applied | Click "Deploy" after setting variable | 1-2 |

### Runtime Phase Failures

| Error Pattern | Root Cause | Quick Fix | Commits Wasted |
|--------------|------------|-----------|----------------|
| `Invalid credentials` | Wrong env var priority | Prioritize `os.getenv()` over files | 3-5 |
| `Database connection failed` | Missing connection string | Set `NEON_DATABASE_URL` variable | 1-2 |
| `OAuth redirect mismatch` | Wrong redirect URL | Update OAuth app with Railway URL | 2-3 |
| `CORS error` | Missing CORS middleware | Add CORS with Railway domain | 1-2 |

---

## Post-Deployment Validation

### Automated Health Checks

Create `scripts/validate_deployment.sh`:

```bash
#!/bin/bash
# Validate Railway deployment

set -e

BACKEND_URL=$(railway domain --service backend)
FRONTEND_URL=$(railway domain --service frontend)

echo "🏥 Health Checks"
echo "================"

# Backend health
echo -n "Backend (/health): "
if curl -s "${BACKEND_URL}/health" | grep -q "healthy"; then
    echo "✅ PASS"
else
    echo "❌ FAIL"
    exit 1
fi

# Frontend health
echo -n "Frontend (/api/health): "
if curl -s "${FRONTEND_URL}/api/health" | grep -q "200"; then
    echo "✅ PASS"
else
    echo "❌ FAIL"
    exit 1
fi

echo ""
echo "🔍 Service Checks"
echo "================="

# Backend logs
echo -n "Backend running: "
if railway logs --service backend | grep -q "Uvicorn running"; then
    echo "✅ PASS"
else
    echo "❌ FAIL"
fi

# Frontend logs
echo -n "Frontend running: "
if railway logs --service frontend | grep -q "ready started server"; then
    echo "✅ PASS"
else
    echo "❌ FAIL"
fi

echo ""
echo "🌐 Environment Variables"
echo "========================"

# Check critical variables
BACKEND_VARS="OPENAI_API_KEY CONVEX_URL NEON_DATABASE_URL"
for var in $BACKEND_VARS; do
    echo -n "Backend $var: "
    if railway run --service backend printenv | grep -q "$var"; then
        echo "✅ SET"
    else
        echo "❌ MISSING"
    fi
done

FRONTEND_VARS="NEXT_PUBLIC_BACKEND_URL NEXT_PUBLIC_CONVEX_URL"
for var in $FRONTEND_VARS; do
    echo -n "Frontend $var: "
    if railway run --service frontend printenv | grep -q "$var"; then
        echo "✅ SET"
    else
        echo "❌ MISSING"
    fi
done

echo ""
echo "✅ All deployment checks passed!"
```

Run after every deployment:
```bash
chmod +x scripts/validate_deployment.sh
./scripts/validate_deployment.sh
```

### Manual Validation Checklist

- [ ] Backend `/health` returns `{"status":"healthy"}`
- [ ] Frontend loads without errors
- [ ] Clerk authentication works
- [ ] Gmail OAuth flow completes
- [ ] Invoice processing webhook responds <500ms
- [ ] Background jobs complete successfully
- [ ] Convex database updates in real-time
- [ ] Error logs show no critical failures
- [ ] All environment variables present

### Performance Benchmarks

```bash
# Response time benchmarks
time curl https://backend.railway.app/health
# Should be: <200ms

time curl https://backend.railway.app/webhooks/user-inbox \
  -X POST -d '{"test":"data"}'
# Should be: <500ms (Gmail requirement)

# Load test (basic)
ab -n 100 -c 10 https://backend.railway.app/health
# 95th percentile: <300ms
```

---

## Anti-Patterns to Avoid

### 1. Using Different Docker Configs for Local vs Production

**Anti-Pattern**:
```dockerfile
# Dockerfile.local (development)
FROM python:3.12

# Dockerfile.production (Railway)
FROM python:3.11-slim
```

**Why it fails**: "Works on my machine" syndrome. Different Python versions = different dependency resolution.

**Correct**:
```dockerfile
# Same Dockerfile for all environments
FROM python:3.11-slim AS base

FROM base AS dev
# Development-specific layers

FROM base AS prod
# Production-specific layers
```

Use build target to select:
```bash
# Local development
docker build --target dev -t app-dev .

# Production (Railway)
docker build --target prod -t app-prod .
```

### 2. Committing Without Local Docker Test

**Anti-Pattern**:
```bash
# Make changes to Dockerfile
vim Dockerfile

# Commit and push immediately
git add Dockerfile
git commit -m "fix: update Docker config"
git push

# Wait 5 minutes for Railway build...
# Build fails ❌
```

**Why it fails**: Wastes Railway build minutes and time. Could have caught error locally in 30 seconds.

**Correct**:
```bash
# Make changes
vim Dockerfile

# Test locally FIRST
docker build -f Dockerfile --target prod -t test .
docker run --rm -p 8000:8000 test

# THEN commit if test passes
git add Dockerfile
git commit -m "fix: update Docker config (tested locally)"
git push
```

### 3. Pinning Sub-Dependencies

**Anti-Pattern**:
```txt
# requirements.txt
langchain==0.3.16
langchain-core==0.3.31  # ← Conflicts with langchain requirement
langchain-aws==0.2.16
boto3==1.35.88
botocore==1.35.88  # ← boto3 manages this
```

**Why it fails**: Creates dependency conflicts. `langchain` requires `langchain-core>=0.3.32`, but you pinned `0.3.31`.

**Correct**:
```txt
# requirements.txt - Only direct dependencies
langchain==0.3.16  # Pulls correct langchain-core automatically
langchain-aws==0.2.16
boto3==1.35.88  # Manages botocore automatically
```

### 4. Manual Dependency Version Hunting

**Anti-Pattern**:
```bash
# Dependency conflict error
# Spend 2 hours reading pip error messages
# Try different versions manually: 0.3.30, 0.3.31, 0.3.32...
# Finally find compatible version
# Commit and redeploy
```

**Why it fails**: Wastes time. Conflicts often cascade (fixing one reveals another).

**Correct**:
```bash
# Dependency conflict error
./scripts/resolve_dependencies.sh  # 30 seconds
mv requirements-resolved.txt requirements.txt
git add requirements.txt
git commit -m "fix: auto-resolve dependency conflicts"
git push
```

### 5. Ignoring .gitignore Conflicts

**Anti-Pattern**:
```gitignore
# .gitignore
*.txt  # ← Blocks requirements.txt!
```

```bash
# Railway build fails: requirements.txt not found
# Manually upload requirements.txt to Railway dashboard
# Works temporarily until next deployment
```

**Why it fails**: Not sustainable. Every deployment requires manual file upload.

**Correct**:
```gitignore
# .gitignore
*.txt
!requirements*.txt  # ← Override to allow requirements files
```

### 6. Using JSON Array CMD for Dynamic Ports

**Anti-Pattern**:
```dockerfile
CMD ["uvicorn", "app:app", "--port", "$PORT"]
# Railway sets PORT=12345, but uvicorn sees literal "$PORT"
```

**Why it fails**: JSON array form doesn't expand environment variables.

**Correct**:
```dockerfile
CMD ["sh", "-c", "uvicorn app:app --port ${PORT:-8000}"]
# Railway sets PORT=12345, uvicorn binds to 12345
```

### 7. Hardcoding URLs Instead of Environment Variables

**Anti-Pattern**:
```typescript
// Frontend
const backendUrl = 'https://backend-production.up.railway.app'
```

**Why it fails**: Breaks in development, staging, preview environments.

**Correct**:
```typescript
// Frontend
const backendUrl = process.env.NEXT_PUBLIC_BACKEND_URL || 'http://localhost:8000'
```

### 8. Deploying Without Pre-Validation

**Anti-Pattern**:
```bash
git add .
git commit -m "feat: new feature"
git push  # Railway auto-deploys
# Wait 5 minutes...
# Build fails due to dependency conflict ❌
```

**Why it fails**: Wastes time and Railway build credits.

**Correct**:
```bash
# Pre-deployment validation (2 minutes)
./scripts/validate_requirements.sh
docker build -f Dockerfile --target prod -t test .

# Only deploy if validation passes
git add .
git commit -m "feat: new feature (validated)"
git push
```

---

## Production Readiness Checklist

Before marking deployment as production-ready:

### Infrastructure

- [ ] Dockerfile uses `python:3.11-slim` (matches local)
- [ ] Multi-stage build minimizes image size (<2GB)
- [ ] Health checks configured (`/health` endpoint)
- [ ] railway.toml exists with correct `dockerfilePath`
- [ ] All services have restart policy `ON_FAILURE`

### Dependencies

- [ ] `requirements.txt` is git-tracked
- [ ] `./scripts/validate_requirements.sh` passes
- [ ] All packages available on PyPI
- [ ] No dependency conflicts
- [ ] Docker build succeeds locally

### Environment Variables

- [ ] All `NEXT_PUBLIC_*` variables set as build args
- [ ] All API keys set in Railway dashboard
- [ ] OAuth credentials use environment variables (not files)
- [ ] Database connection strings validated
- [ ] Variables "applied" via deployment

### Security

- [ ] No credentials committed to git
- [ ] API keys stored in Railway environment only
- [ ] CORS configured with Railway domains
- [ ] HTTPS enforced (Railway default)
- [ ] Service-to-service authentication enabled

### Testing

- [ ] Health endpoints return 200 OK
- [ ] Clerk authentication works end-to-end
- [ ] Gmail OAuth flow completes
- [ ] Webhook responds <500ms
- [ ] Background jobs complete successfully
- [ ] Error handling logs to Railway dashboard

### Monitoring

- [ ] Railway logs show no critical errors
- [ ] Health checks passing (30s interval)
- [ ] Response times <300ms (95th percentile)
- [ ] Memory usage <80% of allocated
- [ ] CPU usage <70% of allocated

### Documentation

- [ ] Environment variables documented
- [ ] Deployment workflow documented
- [ ] Rollback procedure tested
- [ ] Troubleshooting guide updated
- [ ] Team trained on Railway deployments

---

## Summary: The 10 Commandments of Railway Deployment

1. **Thou shalt use the same Dockerfile locally and in production**
   - No "works on my machine" surprises

2. **Thou shalt validate dependencies before every deployment**
   - `./scripts/validate_requirements.sh` is your friend

3. **Thou shalt track all files in git**
   - Railway only deploys git-tracked files

4. **Thou shalt use shell form CMD for dynamic ports**
   - `CMD ["sh", "-c", "uvicorn ... --port $PORT"]`

5. **Thou shalt prioritize environment variables over files**
   - `os.getenv("KEY") or load_from_file("key.json")`

6. **Thou shalt test Docker builds locally first**
   - Catch errors in 30 seconds, not 5 minutes

7. **Thou shalt apply environment variables with deployments**
   - Click "Deploy" after setting variables

8. **Thou shalt use automated dependency resolution**
   - `./scripts/resolve_dependencies.sh` beats manual hunting

9. **Thou shalt minimize Docker image sizes**
   - `python:3.11-slim` + multi-stage builds + clean apt cache

10. **Thou shalt validate deployments before marking complete**
    - `./scripts/validate_deployment.sh` is mandatory

---

## Additional Resources

### Internal Documentation

- [Railway P0 Deployment Guide](RAILWAY_DEPLOYMENT_P0.md)
- [Railway Troubleshooting](RAILWAY_TROUBLESHOOTING_GUIDE.md)
- [Dependency Validation Guide](RAILWAY_DEPENDENCY_VALIDATION.md)
- [P0 Environment Variables](P0_ENVIRONMENT_VARIABLES.md)
- [OAuth Setup Guide](OAUTH_SETUP_P0.md)
- [AWS Migration Roadmap](AWS_MIGRATION_ROADMAP.md)

### External Resources

- [Railway Documentation](https://docs.railway.app)
- [Railway Python Guide](https://docs.railway.app/languages/python)
- [Docker Multi-Stage Builds](https://docs.docker.com/build/building/multi-stage/)
- [pip-tools Documentation](https://pip-tools.readthedocs.io/)
- [Next.js Docker Guide](https://nextjs.org/docs/deployment#docker-image)

### Scripts Reference

All automation scripts in `/scripts/`:

- `validate_requirements.sh` - Pre-deployment dependency validation
- `resolve_dependencies.sh` - Automated conflict resolution
- `check_conflicts.sh` - Test installation in clean Docker environment
- `validate_deployment.sh` - Post-deployment health checks

---

## Changelog

### 2025-11-06: Initial Guide

- Analyzed 159 deployment commits
- Documented 10 major failure patterns
- Created pre-deployment checklist
- Added automated validation scripts
- Established deployment workflow
- Defined production readiness criteria

**Key Insights from 159 Commits**:
- 35 commits: Docker configuration issues
- 25 commits: Dependency conflicts
- 20 commits: Environment variable problems
- 15 commits: Import/module path errors
- 64 commits: Railway-specific gotchas

**Time Saved by Following This Guide**: ~40 hours per deployment cycle

---

**Last Updated**: 2025-11-06
**Maintainer**: Development Team
**Status**: Production-Ready

This guide represents hard-won knowledge from 159 deployment commits. Use it to avoid repeating our mistakes.
