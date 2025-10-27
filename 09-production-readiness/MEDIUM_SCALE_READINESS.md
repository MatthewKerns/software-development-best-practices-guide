# Medium-Scale Production Readiness Guide

**Target Audience:** Dynamic web applications with user authentication, databases, APIs, and 10K-100K monthly active users

**Complexity Level:** Medium
**Time to Complete:** 2-3 weeks
**Team Size:** 3-10 developers

---

## Overview

This guide covers production readiness for medium-scale applications with dynamic features, user data, and moderate traffic. Focus is on operational maturity without enterprise-scale complexity.

**What Qualifies as Medium-Scale:**
- Dynamic content with user authentication
- Database-backed application (PostgreSQL, MySQL, MongoDB)
- REST or GraphQL APIs
- Moderate traffic (10K-100K monthly active users)
- Single monolith or 2-3 microservices
- Team of 3-10 developers
- Budget: $500-5,000/month infrastructure

**Key Differences from Small-Scale:**
- Database management and backups critical
- User data privacy and security paramount
- Performance monitoring required
- Incident response procedures necessary
- Automated testing essential

---

## Quick Checklist (Pre-Launch Validation)

Complete this checklist 1 week before launch:

**Infrastructure:**
- [ ] Auto-scaling configured and tested
- [ ] Database backups automated (daily, tested restoration)
- [ ] CDN configured for static assets
- [ ] Load balancer health checks working

**Security:**
- [ ] Authentication/authorization implemented and tested
- [ ] Secrets in vault (no hardcoded credentials)
- [ ] Input validation on all endpoints (prevent injection)
- [ ] Rate limiting configured (prevent abuse)
- [ ] Security audit completed (manual or automated scan)

**Performance:**
- [ ] Load testing completed (2x expected peak traffic)
- [ ] Database indexes optimized (slow query log analyzed)
- [ ] Caching layer implemented (Redis/Memcached)
- [ ] API response times <200ms (p95)

**Monitoring:**
- [ ] Application logs centralized (ELK, CloudWatch, Datadog)
- [ ] Error tracking configured (Sentry, Rollbar, Bugsnag)
- [ ] Uptime monitoring (PagerDuty, Pingdom, UptimeRobot)
- [ ] Alerts configured for critical metrics

**Data:**
- [ ] Database migrations tested (forward and rollback)
- [ ] Backup restoration tested successfully
- [ ] Data validation rules enforced
- [ ] Audit logging for sensitive operations

**Deployment:**
- [ ] CI/CD pipeline automated and tested
- [ ] Zero-downtime deployment strategy (blue-green or rolling)
- [ ] Rollback procedure documented and tested
- [ ] Feature flags for risky features

---

## 1. Infrastructure Resilience (3-5 days)

### 1.1 Auto-Scaling Configuration

**Why:** Handle traffic spikes gracefully, optimize costs

**Implementation (AWS Auto Scaling):**
```yaml
# Auto Scaling Group configuration
AutoScalingGroup:
  MinSize: 2              # Always at least 2 instances (HA)
  MaxSize: 10             # Cap to prevent cost runaway
  DesiredCapacity: 2      # Start with 2 instances
  HealthCheckGracePeriod: 300  # 5 minutes for instance warmup

  ScalingPolicies:
    - Name: ScaleUp
      MetricName: CPUUtilization
      Threshold: 70          # Scale up at 70% CPU
      ScalingAdjustment: 2   # Add 2 instances

    - Name: ScaleDown
      MetricName: CPUUtilization
      Threshold: 30          # Scale down at 30% CPU
      ScalingAdjustment: -1  # Remove 1 instance (gradual)
```

**Testing:**
```bash
# Load test to trigger auto-scaling
k6 run --vus 500 --duration 10m load-test.js

# Monitor scaling events
aws autoscaling describe-scaling-activities \
  --auto-scaling-group-name production-asg \
  --max-records 10

# Verify no dropped connections during scale-out
grep "connection refused\|connection reset" /var/log/app/*.log
```

**Reference:** [PRODUCTION_READINESS_FRAMEWORK.md#11-auto-scaling-configuration](PRODUCTION_READINESS_FRAMEWORK.md#11-auto-scaling-configuration)

### 1.2 Database High Availability

**Why:** Database is single point of failure, must be resilient

**Implementation (PostgreSQL RDS):**
```yaml
# RDS Multi-AZ configuration
Database:
  Engine: postgres
  EngineVersion: 14.7
  MultiAZ: true              # Automatic failover to standby
  BackupRetentionPeriod: 30  # 30 days of automated backups
  PreferredBackupWindow: "03:00-04:00"  # Low-traffic window
  AutoMinorVersionUpgrade: true          # Security patches

  # Read replicas for read-heavy workloads
  ReadReplicas:
    - Region: us-east-1a
    - Region: us-east-1b

  # Connection pooling (PgBouncer)
  ConnectionPool:
    MaxConnections: 100
    DefaultPoolSize: 20
    MinPoolSize: 5
```

**Monitoring:**
```sql
-- Monitor connection usage
SELECT count(*) FROM pg_stat_activity;
-- Alert if >80% of max_connections

-- Monitor replication lag (read replicas)
SELECT
    client_addr,
    state,
    pg_wal_lsn_diff(pg_current_wal_lsn(), replay_lsn) AS lag_bytes
FROM pg_stat_replication;
-- Alert if lag >1MB
```

**Reference:** [PRODUCTION_READINESS_FRAMEWORK.md#12-failover--high-availability](PRODUCTION_READINESS_FRAMEWORK.md#12-failover--high-availability)

### 1.3 Backup & Recovery

**Critical:** Automated backups with tested restoration

**Implementation:**
```bash
#!/bin/bash
# Daily automated database backup

TIMESTAMP=$(date +%Y%m%d_%H%M%S)
BACKUP_DIR=/backups/postgres
S3_BUCKET=s3://prod-backups/database

# Create backup
pg_dump -h $DB_HOST -U $DB_USER -F c -b -v \
  -f $BACKUP_DIR/backup_$TIMESTAMP.dump $DB_NAME

# Encrypt backup
gpg --encrypt --recipient prod-backup@example.com \
  $BACKUP_DIR/backup_$TIMESTAMP.dump

# Upload to S3 (geo-redundant)
aws s3 cp $BACKUP_DIR/backup_$TIMESTAMP.dump.gpg \
  $S3_BUCKET/ --storage-class STANDARD_IA

# Verify backup integrity
pg_restore --list $BACKUP_DIR/backup_$TIMESTAMP.dump | wc -l

# Cleanup old local backups (keep 7 days)
find $BACKUP_DIR -name "backup_*.dump*" -mtime +7 -delete

# Send notification
curl -X POST https://hooks.slack.com/services/YOUR/WEBHOOK/URL \
  -H 'Content-Type: application/json' \
  -d "{\"text\": \"Database backup completed: $TIMESTAMP\"}"
```

**Restoration Testing (Monthly):**
```bash
#!/bin/bash
# Test database restoration to isolated environment

# Download latest backup
LATEST_BACKUP=$(aws s3 ls $S3_BUCKET/ | sort | tail -n 1 | awk '{print $4}')
aws s3 cp $S3_BUCKET/$LATEST_BACKUP /tmp/

# Decrypt
gpg --decrypt /tmp/$LATEST_BACKUP > /tmp/backup.dump

# Restore to test database
createdb test_restore
pg_restore -d test_restore /tmp/backup.dump

# Validate data integrity
psql test_restore -c "SELECT COUNT(*) FROM users;" # Expect >0
psql test_restore -c "SELECT MAX(created_at) FROM users;" # Expect recent

# Cleanup
dropdb test_restore
rm /tmp/$LATEST_BACKUP /tmp/backup.dump

echo "Restore test passed: RTO < 30 minutes, RPO < 24 hours"
```

**Targets:**
- **RPO (Recovery Point Objective):** <24 hours (daily backups)
- **RTO (Recovery Time Objective):** <1 hour (automated restore)

**Reference:** [PRODUCTION_READINESS_FRAMEWORK.md#13-backup--disaster-recovery](PRODUCTION_READINESS_FRAMEWORK.md#13-backup--disaster-recovery)

---

## 2. Security Hardening (5-7 days)

### 2.1 Authentication & Authorization

**Why:** Protect user accounts and sensitive data

**Implementation (JWT + Refresh Tokens):**
```python
# Authentication middleware
from functools import wraps
from flask import request, jsonify
import jwt
from datetime import datetime, timedelta

SECRET_KEY = os.getenv('JWT_SECRET_KEY')  # From vault, not hardcoded

def require_auth(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        token = request.headers.get('Authorization', '').replace('Bearer ', '')

        if not token:
            return jsonify({'error': 'Missing token'}), 401

        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=['HS256'])
            request.user_id = payload['user_id']
            request.user_role = payload['role']
        except jwt.ExpiredSignatureError:
            return jsonify({'error': 'Token expired'}), 401
        except jwt.InvalidTokenError:
            return jsonify({'error': 'Invalid token'}), 401

        return f(*args, **kwargs)
    return decorated_function

def require_role(required_role):
    def decorator(f):
        @wraps(f)
        @require_auth
        def decorated_function(*args, **kwargs):
            if request.user_role != required_role:
                return jsonify({'error': 'Insufficient permissions'}), 403
            return f(*args, **kwargs)
        return decorated_function
    return decorator

# Usage
@app.route('/admin/users', methods=['GET'])
@require_role('admin')
def list_users():
    users = User.query.all()
    return jsonify([user.to_dict() for user in users])
```

**Security Checklist:**
- [ ] Passwords hashed with bcrypt/Argon2 (never plaintext)
- [ ] JWT tokens short-lived (<15 minutes)
- [ ] Refresh tokens for session management
- [ ] MFA enforced for admin accounts
- [ ] Session invalidation on logout
- [ ] Rate limiting on auth endpoints (5 attempts per 15 minutes)

**Testing:**
```python
# Authentication security test suite
def test_authentication_security():
    # Test: Expired token rejected
    expired_token = generate_token(expires_in=-3600)  # Expired 1 hour ago
    response = client.get('/api/profile', headers={'Authorization': f'Bearer {expired_token}'})
    assert response.status_code == 401

    # Test: Invalid token rejected
    response = client.get('/api/profile', headers={'Authorization': 'Bearer invalid_token'})
    assert response.status_code == 401

    # Test: Authorization enforced
    user_token = login_as('regular_user')
    response = client.get('/admin/users', headers={'Authorization': f'Bearer {user_token}'})
    assert response.status_code == 403  # Forbidden

    admin_token = login_as('admin_user')
    response = client.get('/admin/users', headers={'Authorization': f'Bearer {admin_token}'})
    assert response.status_code == 200  # Allowed
```

### 2.2 Secrets Management

**Why:** Prevent credential leaks, enable rotation

**Implementation (AWS Secrets Manager):**
```python
# Fetch secrets from vault (not environment variables)
import boto3
import json

def get_secret(secret_name):
    """Retrieve secret from AWS Secrets Manager."""
    client = boto3.client('secretsmanager', region_name='us-east-1')

    try:
        response = client.get_secret_value(SecretId=secret_name)
        return json.loads(response['SecretString'])
    except Exception as e:
        logger.error(f"Failed to retrieve secret {secret_name}: {e}")
        raise

# Application initialization
DATABASE_CREDENTIALS = get_secret('prod/database/credentials')
API_KEYS = get_secret('prod/api/keys')

db_connection = connect_database(
    host=DATABASE_CREDENTIALS['host'],
    username=DATABASE_CREDENTIALS['username'],
    password=DATABASE_CREDENTIALS['password']
)
```

**Secret Rotation (Automated):**
```python
# Lambda function for automatic secret rotation
import boto3
import psycopg2

def lambda_handler(event, context):
    """Rotate database credentials every 90 days."""
    secret_id = event['SecretId']
    token = event['ClientRequestToken']
    step = event['Step']

    if step == 'createSecret':
        # Generate new password
        new_password = generate_secure_password(32)

        # Store pending secret
        secrets_client.put_secret_value(
            SecretId=secret_id,
            ClientRequestToken=token,
            SecretString=json.dumps({'password': new_password}),
            VersionStages=['AWSPENDING']
        )

    elif step == 'setSecret':
        # Update database user password
        conn = psycopg2.connect(...)
        cursor = conn.cursor()
        cursor.execute(f"ALTER USER app_user WITH PASSWORD '{new_password}';")
        conn.commit()

    elif step == 'testSecret':
        # Verify new password works
        try:
            psycopg2.connect(host=host, user=user, password=new_password)
        except Exception as e:
            raise Exception(f"New password failed validation: {e}")

    elif step == 'finishSecret':
        # Mark new password as current
        secrets_client.update_secret_version_stage(
            SecretId=secret_id,
            VersionStage='AWSCURRENT',
            MoveToVersionId=token,
            RemoveFromVersionId='AWSPENDING'
        )

    return {'statusCode': 200}
```

**Checklist:**
- [ ] No secrets in version control (verified with trufflehog)
- [ ] Secrets stored in dedicated vault (AWS Secrets Manager, HashiCorp Vault)
- [ ] Secrets rotated every 90 days (automated)
- [ ] Separate secrets per environment (dev/staging/prod)
- [ ] Audit logging for secret access

### 2.3 API Security

**Why:** Protect against abuse, injection, and unauthorized access

**Implementation:**
```python
# Input validation with Marshmallow
from marshmallow import Schema, fields, ValidationError, validate

class UserRegistrationSchema(Schema):
    email = fields.Email(required=True)
    password = fields.Str(
        required=True,
        validate=validate.Length(min=12, max=128)
    )
    username = fields.Str(
        required=True,
        validate=validate.Regexp(r'^[a-zA-Z0-9_]{3,20}$')
    )

@app.route('/api/register', methods=['POST'])
@limiter.limit("5 per minute")  # Rate limiting
def register_user():
    schema = UserRegistrationSchema()
    try:
        data = schema.load(request.json)
    except ValidationError as err:
        return jsonify({'errors': err.messages}), 400

    # SQL injection prevention (parameterized queries)
    user = User(
        email=data['email'],
        password=bcrypt.hashpw(data['password'].encode(), bcrypt.gensalt())
    )
    db.session.add(user)
    db.session.commit()

    return jsonify({'message': 'User created'}), 201
```

**Rate Limiting (Per User + Per IP):**
```python
# Redis-backed rate limiting
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

limiter = Limiter(
    app,
    key_func=get_remote_address,
    storage_uri="redis://localhost:6379",
    default_limits=["200 per hour", "50 per minute"]
)

# Custom rate limit by user ID
def get_user_id():
    return request.user_id if hasattr(request, 'user_id') else get_remote_address()

@app.route('/api/expensive-operation', methods=['POST'])
@limiter.limit("10 per hour", key_func=get_user_id)
def expensive_operation():
    # Expensive operation here
    return jsonify({'status': 'processing'}), 202
```

**Security Headers:**
```python
# Security headers middleware
from flask_talisman import Talisman

Talisman(app,
    force_https=True,
    strict_transport_security=True,
    content_security_policy={
        'default-src': "'self'",
        'script-src': ["'self'", "'unsafe-inline'", "cdn.example.com"],
        'style-src': ["'self'", "'unsafe-inline'"],
        'img-src': ["'self'", "data:", "https:"],
    }
)
```

**Checklist:**
- [ ] Input validation on all endpoints
- [ ] Rate limiting (per IP and per user)
- [ ] SQL injection prevention (ORMs, parameterized queries)
- [ ] XSS prevention (output encoding, CSP headers)
- [ ] CSRF protection (tokens for state-changing operations)
- [ ] HTTPS enforced with HSTS

**Reference:** [PRODUCTION_READINESS_FRAMEWORK.md#23-api--network-security](PRODUCTION_READINESS_FRAMEWORK.md#23-api--network-security)

---

## 3. Performance & Scalability (4-6 days)

### 3.1 Database Optimization

**Why:** Database is often the bottleneck for medium-scale apps

**Query Optimization:**
```sql
-- Enable slow query log
SET log_min_duration_statement = 100;  -- Log queries >100ms

-- Analyze slow queries
SELECT
    calls,
    total_time,
    mean_time,
    query
FROM pg_stat_statements
ORDER BY mean_time DESC
LIMIT 20;

-- Add indexes for frequent queries
CREATE INDEX CONCURRENTLY idx_users_email ON users(email);
CREATE INDEX CONCURRENTLY idx_posts_user_id_created ON posts(user_id, created_at DESC);

-- Analyze query plans
EXPLAIN (ANALYZE, BUFFERS) SELECT * FROM posts WHERE user_id = 123 ORDER BY created_at DESC LIMIT 10;
```

**Connection Pooling:**
```python
# SQLAlchemy connection pooling
from sqlalchemy import create_engine
from sqlalchemy.pool import QueuePool

engine = create_engine(
    'postgresql://user:password@localhost/dbname',
    poolclass=QueuePool,
    pool_size=20,           # Maintain 20 connections
    max_overflow=10,        # Allow 10 extra connections under load
    pool_timeout=30,        # Wait 30s for connection before error
    pool_recycle=3600,      # Recycle connections every hour
    pool_pre_ping=True      # Verify connection health before use
)
```

**N+1 Query Prevention:**
```python
# Bad: N+1 queries
users = User.query.all()
for user in users:
    print(user.posts)  # Separate query for each user (N+1 problem)

# Good: Eager loading
users = User.query.options(joinedload(User.posts)).all()
for user in users:
    print(user.posts)  # Posts already loaded (1 query total)
```

**Checklist:**
- [ ] Slow query log analyzed, queries optimized
- [ ] Indexes on frequently queried columns
- [ ] Connection pooling configured
- [ ] N+1 queries eliminated
- [ ] Database vacuuming scheduled (PostgreSQL)

### 3.2 Caching Strategy

**Why:** Reduce database load, improve response times

**Implementation (Redis):**
```python
import redis
import json
from functools import wraps

redis_client = redis.Redis(host='localhost', port=6379, decode_responses=True)

def cache(expire=300):
    """Cache decorator with TTL."""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            # Generate cache key from function name and arguments
            cache_key = f"cache:{f.__name__}:{str(args)}:{str(kwargs)}"

            # Try cache first
            cached_value = redis_client.get(cache_key)
            if cached_value:
                return json.loads(cached_value)

            # Cache miss: compute and cache
            result = f(*args, **kwargs)
            redis_client.setex(cache_key, expire, json.dumps(result))
            return result
        return decorated_function
    return decorator

# Usage
@app.route('/api/popular-posts')
@cache(expire=600)  # Cache for 10 minutes
def get_popular_posts():
    posts = Post.query.order_by(Post.views.desc()).limit(10).all()
    return jsonify([post.to_dict() for post in posts])
```

**Cache Invalidation:**
```python
# Invalidate cache when data changes
@app.route('/api/posts/<int:post_id>', methods=['PUT'])
@require_auth
def update_post(post_id):
    post = Post.query.get_or_404(post_id)
    post.update(request.json)
    db.session.commit()

    # Invalidate related caches
    redis_client.delete(f"cache:get_post:{post_id}")
    redis_client.delete(f"cache:get_popular_posts")

    return jsonify(post.to_dict())
```

**Checklist:**
- [ ] Redis/Memcached deployed and configured
- [ ] Expensive queries cached (>100ms)
- [ ] Cache invalidation strategy implemented
- [ ] Cache hit rate monitored (target >80%)

**Reference:** [PRODUCTION_READINESS_FRAMEWORK.md#32-caching-strategy](PRODUCTION_READINESS_FRAMEWORK.md#32-caching-strategy)

### 3.3 Load Testing

**Why:** Validate system can handle expected (and unexpected) load

**Implementation (K6):**
```javascript
// load-test.js
import http from 'k6/http';
import { check, sleep } from 'k6';
import { Rate } from 'k6/metrics';

const errorRate = new Rate('errors');

export let options = {
    stages: [
        { duration: '2m', target: 50 },    // Ramp up to 50 users
        { duration: '5m', target: 50 },    // Stay at 50 users
        { duration: '2m', target: 200 },   // Spike to 200 users (2x expected)
        { duration: '5m', target: 200 },   // Sustain spike
        { duration: '2m', target: 0 },     // Ramp down
    ],
    thresholds: {
        http_req_duration: ['p(95)<500', 'p(99)<1000'],  // 95% < 500ms, 99% < 1s
        http_req_failed: ['rate<0.01'],                  // Error rate < 1%
        errors: ['rate<0.1'],
    },
};

const BASE_URL = 'https://api.example.com';

export default function () {
    // Simulate realistic user behavior
    let loginRes = http.post(`${BASE_URL}/auth/login`, JSON.stringify({
        email: 'test@example.com',
        password: 'test123'
    }), {
        headers: { 'Content-Type': 'application/json' },
    });

    check(loginRes, {
        'login successful': (r) => r.status === 200,
    }) || errorRate.add(1);

    let token = loginRes.json('access_token');
    sleep(1);

    // Fetch dashboard (expensive query)
    let dashboardRes = http.get(`${BASE_URL}/api/dashboard`, {
        headers: { 'Authorization': `Bearer ${token}` },
    });

    check(dashboardRes, {
        'dashboard loaded': (r) => r.status === 200,
        'response time OK': (r) => r.timings.duration < 500,
    }) || errorRate.add(1);

    sleep(2);

    // Create post (write operation)
    let postRes = http.post(`${BASE_URL}/api/posts`, JSON.stringify({
        title: 'Test Post',
        content: 'Test content for load testing'
    }), {
        headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${token}`
        },
    });

    check(postRes, {
        'post created': (r) => r.status === 201,
    }) || errorRate.add(1);

    sleep(3);
}
```

**Running Load Tests:**
```bash
# Run load test
k6 run load-test.js

# Expected output:
# ✓ http_req_duration.............avg=245ms  min=89ms  med=210ms  max=987ms  p(95)=456ms p(99)=789ms
# ✓ http_req_failed...............0.3%
# ✓ checks........................99.7%

# If thresholds fail, investigate:
# - Database slow queries
# - Missing cache
# - Insufficient auto-scaling
# - Connection pool exhaustion
```

**Targets:**
- **Throughput:** 100+ requests/second
- **Response Time:** p95 <500ms, p99 <1s
- **Error Rate:** <1%
- **Concurrent Users:** 2x expected peak

---

## 4. Monitoring & Observability (3-4 days)

### 4.1 Centralized Logging

**Why:** Troubleshoot production issues, audit user actions

**Implementation (CloudWatch + ELK):**
```python
# Structured logging with context
import logging
import json
from datetime import datetime

class JSONFormatter(logging.Formatter):
    def format(self, record):
        log_data = {
            'timestamp': datetime.utcnow().isoformat(),
            'level': record.levelname,
            'message': record.getMessage(),
            'logger': record.name,
            'module': record.module,
            'function': record.funcName,
            'line': record.lineno,
        }

        # Add request context if available
        if hasattr(record, 'request_id'):
            log_data['request_id'] = record.request_id
        if hasattr(record, 'user_id'):
            log_data['user_id'] = record.user_id

        # Add exception info if present
        if record.exc_info:
            log_data['exception'] = self.formatException(record.exc_info)

        return json.dumps(log_data)

# Configure logging
handler = logging.StreamHandler()
handler.setFormatter(JSONFormatter())
logger = logging.getLogger('app')
logger.addHandler(handler)
logger.setLevel(logging.INFO)

# Usage
@app.before_request
def log_request():
    request.request_id = str(uuid.uuid4())
    logger.info('Request started', extra={
        'request_id': request.request_id,
        'method': request.method,
        'path': request.path,
        'ip': request.remote_addr,
    })

@app.route('/api/resource', methods=['POST'])
@require_auth
def create_resource():
    try:
        resource = Resource.create(request.json)
        logger.info('Resource created', extra={
            'request_id': request.request_id,
            'user_id': request.user_id,
            'resource_id': resource.id,
        })
        return jsonify(resource.to_dict()), 201
    except Exception as e:
        logger.error('Resource creation failed', extra={
            'request_id': request.request_id,
            'user_id': request.user_id,
            'error': str(e),
        }, exc_info=True)
        return jsonify({'error': 'Internal error'}), 500
```

**Checklist:**
- [ ] Structured logging (JSON format)
- [ ] Request IDs for tracing
- [ ] Sensitive data excluded (passwords, tokens)
- [ ] Logs centralized (CloudWatch, ELK, Datadog)
- [ ] Log retention 30+ days

### 4.2 Error Tracking

**Why:** Detect and fix production errors quickly

**Implementation (Sentry):**
```python
import sentry_sdk
from sentry_sdk.integrations.flask import FlaskIntegration

sentry_sdk.init(
    dsn="https://your-dsn@sentry.io/project-id",
    integrations=[FlaskIntegration()],
    environment="production",
    traces_sample_rate=0.1,  # 10% of transactions traced
    before_send=filter_sensitive_data
)

def filter_sensitive_data(event, hint):
    """Remove sensitive data from error reports."""
    if 'request' in event:
        if 'headers' in event['request']:
            event['request']['headers'].pop('Authorization', None)
        if 'data' in event['request']:
            if isinstance(event['request']['data'], dict):
                event['request']['data'].pop('password', None)
                event['request']['data'].pop('token', None)
    return event

# Automatic error capture
@app.route('/api/risky-operation', methods=['POST'])
def risky_operation():
    try:
        result = perform_operation()
        return jsonify(result)
    except Exception as e:
        # Automatically sent to Sentry
        sentry_sdk.capture_exception(e)
        return jsonify({'error': 'Operation failed'}), 500
```

**Alerting Rules:**
```yaml
# Sentry alert rules
- name: High Error Rate
  conditions:
    - error_count > 10 in 5 minutes
  actions:
    - PagerDuty: critical
    - Slack: #alerts

- name: New Error Type
  conditions:
    - new_issue = true
    - environment = production
  actions:
    - Slack: #dev-team
```

### 4.3 Application Metrics

**Why:** Understand system health, detect degradation early

**Implementation (Prometheus + Grafana):**
```python
from prometheus_flask_exporter import PrometheusMetrics

metrics = PrometheusMetrics(app)

# Default metrics: request count, duration, etc.
# Custom business metrics
metrics.info('app_info', 'Application info', version='1.2.3')

user_registrations = metrics.counter(
    'user_registrations_total',
    'Total user registrations',
    labels={'source': lambda: request.args.get('source', 'direct')}
)

@app.route('/api/register', methods=['POST'])
def register():
    user = create_user(request.json)
    user_registrations.inc()  # Increment counter
    return jsonify(user.to_dict()), 201
```

**Key Metrics to Track:**
- **Application:** Request rate, error rate, response time (p50/p95/p99)
- **Business:** Signups, logins, conversions, revenue
- **Infrastructure:** CPU, memory, disk, network
- **Database:** Query rate, query duration, connection pool usage

**Grafana Dashboard:**
```yaml
# Grafana dashboard panels
- Request Rate (req/s)
- Error Rate (%)
- Response Time (p50, p95, p99)
- Active Users
- Database Connections
- Cache Hit Rate (%)
- CPU Usage (%)
- Memory Usage (%)
```

### 4.4 Alerting

**Why:** Get notified before users complain

**Alert Rules (Prometheus):**
```yaml
# prometheus-alerts.yml
groups:
  - name: application
    rules:
      - alert: HighErrorRate
        expr: rate(http_requests_total{status=~"5.."}[5m]) > 0.05
        for: 5m
        labels:
          severity: critical
        annotations:
          summary: "High error rate detected"
          description: "Error rate is {{ $value }}% over the last 5 minutes"

      - alert: SlowResponseTime
        expr: http_request_duration_seconds{quantile="0.95"} > 1
        for: 10m
        labels:
          severity: warning
        annotations:
          summary: "Slow response time detected"
          description: "P95 latency is {{ $value }}s"

      - alert: DatabaseConnectionPoolExhausted
        expr: db_connections_used / db_connections_max > 0.9
        for: 5m
        labels:
          severity: critical
        annotations:
          summary: "Database connection pool near capacity"
```

**On-Call Rotation:**
```python
# PagerDuty integration
import pypd

pypd.api_key = os.getenv('PAGERDUTY_API_KEY')

def trigger_incident(title, description, severity):
    """Trigger PagerDuty incident."""
    incident = pypd.Incident.create(
        title=title,
        service=pypd.Service.find_one(name='Production API'),
        urgency=severity,
        body={'type': 'incident_body', 'details': description}
    )
    return incident

# Usage in alerts
if error_rate > THRESHOLD:
    trigger_incident(
        title="High Error Rate Alert",
        description=f"Error rate: {error_rate}%",
        severity='high'
    )
```

---

## 5. Deployment & Release (3-4 days)

### 5.1 CI/CD Pipeline

**Why:** Automate testing and deployment, reduce human error

**Implementation (GitHub Actions):**
```yaml
# .github/workflows/deploy.yml
name: Deploy to Production

on:
  push:
    branches: [ main ]

jobs:
  test:
    runs-on: ubuntu-latest
    services:
      postgres:
        image: postgres:14
        env:
          POSTGRES_PASSWORD: postgres
        options: >-
          --health-cmd pg_isready
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5

    steps:
      - uses: actions/checkout@v3

      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'

      - name: Install dependencies
        run: |
          pip install -r requirements.txt
          pip install -r requirements-test.txt

      - name: Run tests
        env:
          DATABASE_URL: postgresql://postgres:postgres@localhost/test
        run: |
          pytest tests/ -v --cov=app --cov-report=term-missing
          # Fail if coverage <85%
          coverage report --fail-under=85

      - name: Security scan
        run: |
          pip install bandit safety
          bandit -r app/ -ll
          safety check --json

  deploy:
    needs: test
    runs-on: ubuntu-latest
    if: github.ref == 'refs/heads/main'

    steps:
      - uses: actions/checkout@v3

      - name: Configure AWS credentials
        uses: aws-actions/configure-aws-credentials@v1
        with:
          aws-access-key-id: ${{ secrets.AWS_ACCESS_KEY_ID }}
          aws-secret-access-key: ${{ secrets.AWS_SECRET_ACCESS_KEY }}
          aws-region: us-east-1

      - name: Build Docker image
        run: |
          docker build -t myapp:${{ github.sha }} .
          docker tag myapp:${{ github.sha }} myapp:latest

      - name: Push to ECR
        run: |
          aws ecr get-login-password | docker login --username AWS --password-stdin $ECR_REGISTRY
          docker push myapp:${{ github.sha }}
          docker push myapp:latest

      - name: Deploy to ECS (Blue-Green)
        run: |
          # Update ECS task definition with new image
          aws ecs update-service \
            --cluster production \
            --service api \
            --task-definition api:${{ github.sha }} \
            --deployment-configuration maximumPercent=200,minimumHealthyPercent=100

      - name: Wait for deployment
        run: |
          aws ecs wait services-stable \
            --cluster production \
            --services api

      - name: Run smoke tests
        run: |
          python scripts/smoke-tests.py --env production

      - name: Notify team
        if: always()
        uses: 8398a7/action-slack@v3
        with:
          status: ${{ job.status }}
          text: 'Deployment to production: ${{ job.status }}'
          webhook_url: ${{ secrets.SLACK_WEBHOOK }}
```

**Checklist:**
- [ ] Tests run automatically on every commit
- [ ] Deployment automated (no manual steps)
- [ ] Smoke tests run post-deployment
- [ ] Deployment notifications (Slack, email)

### 5.2 Zero-Downtime Deployment

**Why:** Deploy during business hours without user disruption

**Implementation (Blue-Green Deployment):**
```bash
# Blue-Green deployment script
#!/bin/bash

CLUSTER="production"
SERVICE="api"
NEW_TASK_DEF="api:${GIT_SHA}"

echo "Starting blue-green deployment..."

# Register new task definition
aws ecs register-task-definition --cli-input-json file://task-definition.json

# Update service with new task definition
# ECS will:
# 1. Start new tasks (green)
# 2. Wait for health checks to pass
# 3. Drain connections from old tasks (blue)
# 4. Stop old tasks
aws ecs update-service \
  --cluster $CLUSTER \
  --service $SERVICE \
  --task-definition $NEW_TASK_DEF \
  --deployment-configuration \
    "maximumPercent=200,minimumHealthyPercent=100,deploymentCircuitBreaker={enable=true,rollback=true}"

# Wait for deployment to stabilize
echo "Waiting for deployment to stabilize..."
aws ecs wait services-stable --cluster $CLUSTER --services $SERVICE

# Verify deployment
RUNNING_COUNT=$(aws ecs describe-services \
  --cluster $CLUSTER \
  --services $SERVICE \
  --query 'services[0].runningCount' \
  --output text)

if [ "$RUNNING_COUNT" -ge 2 ]; then
    echo "Deployment successful: $RUNNING_COUNT tasks running"
else
    echo "Deployment failed: only $RUNNING_COUNT tasks running"
    exit 1
fi
```

**Checklist:**
- [ ] Zero-downtime deployment strategy (blue-green or rolling)
- [ ] Health checks configured (route traffic only to healthy instances)
- [ ] Deployment circuit breaker (auto-rollback on failure)
- [ ] Connection draining (graceful shutdown)

### 5.3 Rollback Procedures

**Why:** Quickly revert bad deployments

**Implementation:**
```bash
# Rollback to previous version
#!/bin/bash

CLUSTER="production"
SERVICE="api"

# Get previous task definition
PREVIOUS_TASK_DEF=$(aws ecs describe-services \
  --cluster $CLUSTER \
  --services $SERVICE \
  --query 'services[0].deployments[1].taskDefinition' \
  --output text)

echo "Rolling back to $PREVIOUS_TASK_DEF..."

# Update service to previous task definition
aws ecs update-service \
  --cluster $CLUSTER \
  --service $SERVICE \
  --task-definition $PREVIOUS_TASK_DEF \
  --force-new-deployment

# Wait for rollback to complete
aws ecs wait services-stable --cluster $CLUSTER --services $SERVICE

echo "Rollback complete"

# Notify team
curl -X POST https://hooks.slack.com/services/YOUR/WEBHOOK/URL \
  -H 'Content-Type: application/json' \
  -d "{\"text\": \"⚠️  Rolled back production to $PREVIOUS_TASK_DEF\"}"
```

**Database Migration Rollback:**
```python
# Reversible migrations (Alembic)
"""Add email_verified column

Revision ID: 001
Create Date: 2025-10-27
"""

from alembic import op
import sqlalchemy as sa

# Upgrade
def upgrade():
    op.add_column('users', sa.Column('email_verified', sa.Boolean(), nullable=False, server_default='false'))

# Rollback
def downgrade():
    op.drop_column('users', 'email_verified')
```

**Checklist:**
- [ ] Rollback procedure documented and tested
- [ ] Database migrations reversible
- [ ] Rollback can be executed in <5 minutes
- [ ] Rollback triggers automatic alerts

**Reference:** [ROLLBACK_AND_RECOVERY.md](ROLLBACK_AND_RECOVERY.md) (to be created)

---

## 6. Data Integrity & Compliance (2-3 days)

### 6.1 Data Validation

**Why:** Prevent invalid data from corrupting database

**Implementation:**
```python
# Database-level constraints
from sqlalchemy import CheckConstraint

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(255), nullable=False, unique=True)
    age = db.Column(db.Integer, CheckConstraint('age >= 13 AND age <= 120'))
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    __table_args__ = (
        CheckConstraint('LENGTH(email) >= 5', name='email_min_length'),
    )

# Application-level validation
from marshmallow import Schema, fields, validates, ValidationError

class UserSchema(Schema):
    email = fields.Email(required=True)
    age = fields.Integer(required=True)

    @validates('age')
    def validate_age(self, value):
        if value < 13:
            raise ValidationError('User must be at least 13 years old')
        if value > 120:
            raise ValidationError('Invalid age')
```

### 6.2 Audit Logging

**Why:** Track sensitive operations for compliance and forensics

**Implementation:**
```python
# Audit log model
class AuditLog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    timestamp = db.Column(db.DateTime, nullable=False, default=datetime.utcnow, index=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    action = db.Column(db.String(50), nullable=False, index=True)  # CREATE, UPDATE, DELETE
    resource_type = db.Column(db.String(50), nullable=False)       # User, Post, Payment
    resource_id = db.Column(db.Integer, nullable=False)
    old_value = db.Column(db.JSON, nullable=True)                 # Before
    new_value = db.Column(db.JSON, nullable=True)                 # After
    ip_address = db.Column(db.String(45), nullable=False)
    user_agent = db.Column(db.String(255))

# Automatic audit logging with decorator
def audit_changes(resource_type):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            # Capture old state
            resource_id = kwargs.get('id')
            old_value = None
            if resource_id:
                old_resource = get_resource(resource_type, resource_id)
                old_value = old_resource.to_dict() if old_resource else None

            # Execute operation
            result = f(*args, **kwargs)

            # Capture new state
            new_resource = result if isinstance(result, db.Model) else None
            new_value = new_resource.to_dict() if new_resource else None

            # Log audit entry
            AuditLog.create(
                user_id=request.user_id,
                action=request.method,
                resource_type=resource_type,
                resource_id=resource_id or new_resource.id,
                old_value=old_value,
                new_value=new_value,
                ip_address=request.remote_addr,
                user_agent=request.headers.get('User-Agent')
            )

            return result
        return decorated_function
    return decorator

# Usage
@app.route('/api/users/<int:id>', methods=['PUT'])
@require_auth
@audit_changes('User')
def update_user(id):
    user = User.query.get_or_404(id)
    user.update(request.json)
    db.session.commit()
    return jsonify(user.to_dict())
```

### 6.3 GDPR Compliance (if applicable)

**Why:** Legal requirement for EU users, builds trust

**Data Access Request:**
```python
@app.route('/api/user/data-export', methods=['POST'])
@require_auth
def export_user_data():
    """User can request all their data (GDPR Article 15)."""
    user = User.query.get(request.user_id)

    # Collect all user data
    data = {
        'profile': user.to_dict(),
        'posts': [post.to_dict() for post in user.posts],
        'comments': [comment.to_dict() for comment in user.comments],
        'audit_logs': [log.to_dict() for log in AuditLog.query.filter_by(user_id=user.id).all()],
    }

    # Generate downloadable file
    filename = f"user_data_{user.id}_{datetime.utcnow().strftime('%Y%m%d')}.json"
    filepath = f"/tmp/{filename}"

    with open(filepath, 'w') as f:
        json.dump(data, f, indent=2, default=str)

    # Send email with download link (expires in 7 days)
    send_email(
        to=user.email,
        subject="Your Data Export is Ready",
        body=f"Download your data: https://example.com/downloads/{filename}"
    )

    return jsonify({'message': 'Export will be emailed to you within 24 hours'})
```

**Data Deletion Request:**
```python
@app.route('/api/user/delete', methods=['POST'])
@require_auth
def delete_user_account():
    """User can request account deletion (GDPR Article 17 - Right to be Forgotten)."""
    user = User.query.get(request.user_id)

    # Anonymize instead of hard delete (preserve referential integrity)
    user.email = f"deleted_{user.id}@example.com"
    user.username = f"deleted_user_{user.id}"
    user.first_name = None
    user.last_name = None
    user.phone = None
    user.deleted_at = datetime.utcnow()

    # Cascade delete user-generated content (or anonymize)
    for post in user.posts:
        post.author = None  # Anonymize authorship

    db.session.commit()

    return jsonify({'message': 'Account deleted successfully'})
```

**Checklist:**
- [ ] Data access request handler (users can export their data)
- [ ] Data deletion request handler (users can delete account)
- [ ] Privacy policy published and accessible
- [ ] Cookie consent banner (if using cookies)
- [ ] Data processing agreement with third-party vendors

---

## 7. Incident Response Plan (1 day)

### 7.1 Runbook

**Why:** Reduce response time during outages

**Example Runbook (High Error Rate):**
```markdown
# Runbook: High Error Rate Alert

## Symptoms
- Error rate >5% sustained for 5+ minutes
- PagerDuty incident triggered
- Users reporting 500 errors

## Triage Steps
1. **Check monitoring dashboard**
   - URL: https://grafana.example.com/d/production
   - Look for error rate spike, response time increase

2. **Check error tracking (Sentry)**
   - URL: https://sentry.io/projects/production
   - Identify most common error type

3. **Check recent deployments**
   ```bash
   aws ecs describe-services --cluster production --services api
   # Look for recent task definition changes
   ```

4. **Check database health**
   ```sql
   SELECT COUNT(*) FROM pg_stat_activity;  -- Connection count
   SELECT * FROM pg_stat_activity WHERE state = 'active' AND query_start < NOW() - INTERVAL '30 seconds';  -- Long queries
   ```

## Resolution Steps

### If error is in new deployment:
```bash
# Rollback immediately
./scripts/rollback.sh
```

### If database connection pool exhausted:
```bash
# Restart application (gracefully)
aws ecs update-service --cluster production --service api --force-new-deployment

# Or scale up database connections
# Update RDS parameter group: max_connections = 200
```

### If external API dependency down:
```python
# Enable circuit breaker (fail fast)
# Or switch to degraded mode (disable feature)
```

## Communication
- Update status page: https://status.example.com
- Post in Slack #incidents
- If >30 minute outage, email users

## Post-Incident
- Complete post-mortem within 48 hours
- Identify root cause and preventive measures
- Update runbook with learnings
```

### 7.2 Status Page

**Why:** Communicate outages transparently to users

**Implementation (StatusPage.io or self-hosted):**
```python
# Update status page programmatically
import requests

STATUS_PAGE_API_KEY = os.getenv('STATUSPAGE_API_KEY')
STATUS_PAGE_ID = 'your-page-id'

def update_status(component, status, message):
    """Update component status on status page.

    Args:
        component: Component ID (e.g., 'api', 'database')
        status: 'operational', 'degraded_performance', 'partial_outage', 'major_outage'
        message: Incident description
    """
    url = f"https://api.statuspage.io/v1/pages/{STATUS_PAGE_ID}/components/{component}"

    response = requests.patch(url, headers={
        'Authorization': f'OAuth {STATUS_PAGE_API_KEY}',
    }, json={
        'component': {
            'status': status,
            'description': message
        }
    })

    return response.json()

# Usage during incident
update_status(
    component='api',
    status='partial_outage',
    message='API experiencing elevated error rates. Investigating.'
)
```

---

## When to Upgrade to Large-Scale

Consider the [LARGE_SCALE_READINESS.md](LARGE_SCALE_READINESS.md) guide when:

- Monthly active users exceed 100K
- Multiple microservices (3+ repositories)
- Team exceeds 10 developers
- Multi-region deployment required
- Compliance requirements intensify (SOC2, HIPAA, PCI-DSS)
- Infrastructure costs exceed $5K/month

---

**Guide Version:** 1.0
**Last Updated:** 2025-10-27
**For:** Dynamic web applications with 10K-100K monthly active users
