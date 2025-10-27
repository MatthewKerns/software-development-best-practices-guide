# Production Readiness Framework

## Overview

This comprehensive 8-area framework ensures your application meets production standards before deployment. Each area contains specific validation criteria with severity ratings (Critical, High, Medium, Low) to help prioritize remediation efforts.

**Framework Philosophy:**
- **Prevent over React:** Catch issues before production, not after
- **Evidence-Based:** Validate with tests, metrics, and documentation
- **Risk-Prioritized:** Focus on critical/high severity issues first
- **Continuously Improve:** Production readiness is ongoing, not one-time

## How to Use This Framework

### Assessment Process

1. **Initial Gap Analysis:** Review all 8 areas and identify gaps
2. **Severity Classification:** Classify each gap (Critical/High/Medium/Low)
3. **Remediation Planning:** Create prioritized task list with effort estimates
4. **Implementation:** Fix critical/high severity gaps before launch
5. **Validation:** Re-assess to confirm all gaps resolved
6. **Documentation:** Document evidence of production readiness

### Severity Definitions

**Critical:** Launch blocker - will cause major outage, data loss, or security breach
**High:** Serious issue - will cause frequent problems or degraded user experience
**Medium:** Important issue - should fix soon but not a launch blocker
**Low:** Nice-to-have - optimize over time, low immediate risk

### Integration with Repository Practices

- **TDD Validation:** Write tests to validate each criterion
- **Geist Analysis:** Apply Ghost/Geyser/Gist to each area
- **DRY Compliance:** Reuse configurations across environments
- **Sub-Agents:** Use specialized agents for domain validation

---

## 1. Infrastructure Resilience

**Goal:** Ensure your infrastructure can handle failures gracefully and recover from disasters.

### 1.1 Auto-Scaling Configuration

**Critical:**
- [ ] Auto-scaling policies defined for compute resources (CPU/memory triggers)
- [ ] Scaling limits configured (min/max instances prevent runaway costs)
- [ ] Scaling metrics validated under load (actually triggers when needed)
- [ ] Scale-out tested with real traffic patterns
- [ ] Scale-in tested without dropping connections

**High:**
- [ ] Predictive scaling configured for known traffic patterns
- [ ] Multi-zone distribution for high availability
- [ ] Health checks properly configured (route traffic only to healthy instances)

**Medium:**
- [ ] Scaling notifications configured (alerts on scale events)
- [ ] Cost impact of scaling events tracked

**Validation:**
```bash
# Load test that triggers auto-scaling
k6 run --vus 1000 --duration 10m load-test.js

# Verify new instances launched
kubectl get pods --watch
aws autoscaling describe-auto-scaling-groups

# Validate no dropped connections during scale-out
grep "connection refused" /var/log/app/*.log
```

### 1.2 Failover & High Availability

**Critical:**
- [ ] Multi-zone/multi-region deployment (no single points of failure)
- [ ] Database failover tested and working (automatic promotion)
- [ ] Load balancer health checks configured (detect and route around failures)
- [ ] Session persistence handled (sticky sessions or distributed sessions)

**High:**
- [ ] Circuit breakers implemented for external dependencies
- [ ] Retry logic with exponential backoff for transient failures
- [ ] Timeout configurations prevent hanging requests
- [ ] Dead letter queues for failed async jobs

**Medium:**
- [ ] Chaos engineering tests (intentional failure injection)
- [ ] Disaster recovery drills conducted quarterly

**Validation:**
```python
# Chaos engineering test - kill random instances
def test_instance_failure_resilience():
    """Verify application survives random instance failures."""
    # Launch load test
    start_load_test(users=100, duration=300)

    # Kill 30% of instances randomly
    for _ in range(3):
        kill_random_instance()
        time.sleep(60)

    # Verify: error rate <1%, p95 latency <2x normal
    metrics = get_metrics(duration=300)
    assert metrics['error_rate'] < 0.01
    assert metrics['p95_latency'] < 2 * baseline_p95
```

### 1.3 Backup & Disaster Recovery

**Critical:**
- [ ] Automated daily backups configured and running
- [ ] Backup retention policy defined (30 days minimum)
- [ ] Backup restoration tested successfully (RTO/RPO validated)
- [ ] Backups stored in separate region/zone (survive regional failure)
- [ ] Point-in-time recovery available for databases (PITR)

**High:**
- [ ] Backup monitoring and alerting (detect failed backups immediately)
- [ ] Incremental backups for large datasets (faster backup/restore)
- [ ] Backup encryption configured (protect data at rest)

**Medium:**
- [ ] Backup verification automated (test restores regularly)
- [ ] Disaster recovery runbook documented and tested

**Validation:**
```bash
# Test full database restore from backup
# 1. Create test backup
pg_dump production_db > test_backup.sql

# 2. Restore to isolated environment
psql test_db < test_backup.sql

# 3. Validate data integrity
psql test_db -c "SELECT COUNT(*) FROM critical_table;"
psql test_db -c "SELECT MAX(created_at) FROM critical_table;"

# 4. Measure RTO (time to restore)
# Target: <1 hour for critical systems
```

---

## 2. Security Posture

**Goal:** Protect application, data, and users from security threats.

### 2.1 Authentication & Authorization

**Critical:**
- [ ] Strong authentication enforced (MFA for admin accounts)
- [ ] Password policies enforced (complexity, length, rotation)
- [ ] Session management secure (HttpOnly, Secure, SameSite cookies)
- [ ] Authorization checks on all sensitive operations
- [ ] No hardcoded credentials in code or configs

**High:**
- [ ] Rate limiting on authentication endpoints (prevent brute force)
- [ ] Account lockout after N failed attempts
- [ ] Password reset flow secure (token-based, time-limited)
- [ ] OAuth/OIDC integration for third-party auth (if applicable)

**Medium:**
- [ ] Biometric authentication supported (for mobile apps)
- [ ] Single sign-on (SSO) integration (for enterprise)

**Validation:**
```python
# Security test suite
def test_authentication_security():
    """Validate authentication security controls."""
    # Test: Password complexity enforcement
    assert register_user(password="weak") == HTTP_400
    assert register_user(password="Strong@Pass123") == HTTP_201

    # Test: Rate limiting on login
    for _ in range(10):
        login(email="test@example.com", password="wrong")
    assert login(email="test@example.com", password="correct") == HTTP_429

    # Test: Session expiration
    token = login(email="test@example.com", password="correct")
    time.sleep(3601)  # Session timeout: 1 hour
    assert api_call(token=token) == HTTP_401
```

### 2.2 Secrets Management

**Critical:**
- [ ] No secrets in version control (scan with git-secrets or trufflehog)
- [ ] Secrets stored in dedicated vault (AWS Secrets Manager, HashiCorp Vault, etc.)
- [ ] Secrets rotated regularly (automated rotation where possible)
- [ ] Environment-specific secrets (dev/staging/prod isolated)
- [ ] API keys and tokens properly scoped (least privilege)

**High:**
- [ ] Secrets encrypted at rest and in transit
- [ ] Audit logging for secret access
- [ ] Automatic secret expiration and alerting

**Validation:**
```bash
# Scan codebase for leaked secrets
trufflehog git file://. --json | jq '.[] | select(.verified==true)'

# Verify no secrets in environment files
grep -r "password\|secret\|api_key" .env* config/* | grep -v "PLACEHOLDER"

# Validate secrets rotation
aws secretsmanager describe-secret --secret-id prod/db/password | jq '.RotationEnabled'
```

### 2.3 API & Network Security

**Critical:**
- [ ] HTTPS enforced everywhere (HSTS headers configured)
- [ ] API authentication required (no unauthenticated endpoints exposing data)
- [ ] Input validation on all endpoints (prevent injection attacks)
- [ ] CORS properly configured (restrictive allowed origins)
- [ ] SQL injection prevention (parameterized queries/ORMs)

**High:**
- [ ] XSS prevention (CSP headers, output encoding)
- [ ] CSRF protection enabled
- [ ] Rate limiting per user/IP (prevent abuse)
- [ ] DDoS protection configured (CloudFlare, AWS Shield)

**Medium:**
- [ ] API versioning strategy (backward compatibility)
- [ ] Webhook signature verification (validate external callbacks)

**Validation:**
```python
# API security test suite
def test_api_security():
    """Validate API security controls."""
    # Test: HTTPS enforcement
    response = requests.get("http://api.example.com/health")
    assert response.status_code == 301  # Redirect to HTTPS

    # Test: Authentication required
    response = requests.get("https://api.example.com/user/profile")
    assert response.status_code == 401

    # Test: SQL injection prevention
    response = requests.get("https://api.example.com/search?q=' OR '1'='1")
    assert "error" not in response.text or response.status_code == 400

    # Test: Rate limiting
    for _ in range(101):
        requests.get("https://api.example.com/search?q=test")
    response = requests.get("https://api.example.com/search?q=test")
    assert response.status_code == 429
```

### 2.4 Vulnerability Management

**Critical:**
- [ ] Dependency scanning enabled (Snyk, Dependabot, npm audit)
- [ ] Zero known critical/high vulnerabilities in dependencies
- [ ] Security patches applied within 7 days of release

**High:**
- [ ] Container image scanning (no critical vulnerabilities)
- [ ] Regular penetration testing scheduled
- [ ] Security headers configured (X-Frame-Options, X-Content-Type-Options)

**Medium:**
- [ ] Bug bounty program or responsible disclosure policy
- [ ] Security training for development team

**Validation:**
```bash
# Dependency vulnerability scan
npm audit --audit-level=high
pip-audit --strict

# Container image scan
trivy image myapp:latest --severity CRITICAL,HIGH

# Verify security headers
curl -I https://example.com | grep -E "X-Frame-Options|X-Content-Type-Options|Strict-Transport-Security"
```

---

## 3. Performance & Scalability

**Goal:** Ensure application performs well under expected and peak load.

### 3.1 Database Optimization

**Critical:**
- [ ] Indexes created on frequently queried columns
- [ ] Slow query log analyzed and optimized (queries <100ms target)
- [ ] Connection pooling configured (prevent connection exhaustion)
- [ ] N+1 queries eliminated (use eager loading)

**High:**
- [ ] Query execution plans reviewed (EXPLAIN ANALYZE)
- [ ] Database statistics updated regularly (VACUUM, ANALYZE)
- [ ] Read replicas configured for read-heavy workloads

**Medium:**
- [ ] Query caching enabled where appropriate
- [ ] Archival strategy for old data (prevent unbounded table growth)

**Validation:**
```sql
-- Identify missing indexes
SELECT
    schemaname, tablename,
    seq_scan, seq_tup_read,
    idx_scan, idx_tup_fetch
FROM pg_stat_user_tables
WHERE seq_scan > 1000 AND seq_tup_read > 10000
ORDER BY seq_tup_read DESC;

-- Find slow queries (PostgreSQL)
SELECT query, calls, total_time, mean_time
FROM pg_stat_statements
ORDER BY mean_time DESC
LIMIT 20;
```

### 3.2 Caching Strategy

**Critical:**
- [ ] Caching layer implemented for expensive operations
- [ ] Cache invalidation strategy defined (prevent stale data)
- [ ] Cache hit rate monitored (>80% target)

**High:**
- [ ] CDN configured for static assets
- [ ] Browser caching headers configured (Cache-Control, ETag)
- [ ] Redis/Memcached cluster configured for HA

**Medium:**
- [ ] Full-page caching for static content
- [ ] API response caching for read-heavy endpoints

**Validation:**
```python
# Cache effectiveness test
def test_cache_hit_rate():
    """Validate caching improves performance."""
    # Warm up cache
    for i in range(100):
        api_call(f"/product/{i}")

    # Measure cached requests
    start = time.time()
    for i in range(100):
        response = api_call(f"/product/{i}")
        assert "X-Cache-Hit" in response.headers
    cached_duration = time.time() - start

    # Compare to uncached (cache cleared)
    clear_cache()
    start = time.time()
    for i in range(100):
        api_call(f"/product/{i}")
    uncached_duration = time.time() - start

    # Cached requests should be >5x faster
    assert cached_duration < uncached_duration / 5
```

### 3.3 Load Testing & Capacity Planning

**Critical:**
- [ ] Load tests executed at expected peak capacity
- [ ] Load tests include realistic user behavior patterns
- [ ] System remains stable under 2x expected load
- [ ] Resource bottlenecks identified (CPU, memory, I/O, network)

**High:**
- [ ] Stress tests identify breaking point (know your limits)
- [ ] Soak tests validate stability over 24+ hours
- [ ] Capacity planning documented (when to scale)

**Medium:**
- [ ] Spike tests validate sudden traffic increases
- [ ] Load test automation in CI/CD pipeline

**Validation:**
```javascript
// K6 load test scenario
import http from 'k6/http';
import { check, sleep } from 'k6';

export let options = {
    stages: [
        { duration: '2m', target: 100 },   // Ramp up
        { duration: '5m', target: 100 },   // Steady state
        { duration: '2m', target: 200 },   // Spike
        { duration: '5m', target: 200 },   // Sustained spike
        { duration: '2m', target: 0 },     // Ramp down
    ],
    thresholds: {
        http_req_duration: ['p(95)<500', 'p(99)<1000'],
        http_req_failed: ['rate<0.01'],
    },
};

export default function () {
    let response = http.get('https://api.example.com/products');
    check(response, {
        'status is 200': (r) => r.status === 200,
        'response time < 500ms': (r) => r.timings.duration < 500,
    });
    sleep(1);
}
```

### 3.4 Asset Optimization

**Critical:**
- [ ] Images optimized and compressed (WebP, AVIF)
- [ ] JavaScript/CSS minified and bundled
- [ ] Gzip/Brotli compression enabled

**High:**
- [ ] Lazy loading for images and non-critical content
- [ ] Code splitting for large JavaScript bundles
- [ ] Critical CSS inlined (above-the-fold content)

**Medium:**
- [ ] Service worker for offline support and caching
- [ ] HTTP/2 or HTTP/3 enabled (multiplexing, server push)

**Validation:**
```bash
# Lighthouse audit (target score: 90+)
lighthouse https://example.com --output=json --output-path=./report.json
cat report.json | jq '.categories.performance.score * 100'

# Asset size check
curl -I https://example.com/bundle.js | grep "Content-Length"
curl -I https://example.com/bundle.js | grep "Content-Encoding"
```

---

## 4. Monitoring & Observability

**Goal:** Provide visibility into production behavior and enable rapid issue detection.

### 4.1 Logging Infrastructure

**Critical:**
- [ ] Centralized logging configured (ELK, Splunk, CloudWatch, Datadog)
- [ ] Structured logging format (JSON) with consistent fields
- [ ] Log levels properly used (ERROR, WARN, INFO, DEBUG)
- [ ] Critical errors logged with context (user ID, request ID, stack trace)
- [ ] Log retention policy defined (minimum 30 days)

**High:**
- [ ] Request tracing with correlation IDs (trace requests across services)
- [ ] Sensitive data excluded from logs (PII, passwords, tokens)
- [ ] Log volume monitored (prevent disk space exhaustion)

**Medium:**
- [ ] Log analysis and dashboard creation
- [ ] Automated log-based alerting

**Validation:**
```python
# Logging validation test
def test_logging_infrastructure():
    """Validate logging is comprehensive and structured."""
    # Trigger error condition
    response = api_call("/divide", data={"a": 10, "b": 0})
    assert response.status_code == 500

    # Verify error logged with context
    logs = query_logs(level="ERROR", last_minutes=1)
    assert len(logs) > 0
    assert "ZeroDivisionError" in logs[0]['message']
    assert 'request_id' in logs[0]
    assert 'user_id' in logs[0]
    assert 'stack_trace' in logs[0]
```

### 4.2 Metrics & Dashboards

**Critical:**
- [ ] Key performance indicators (KPIs) defined and tracked
- [ ] Application-level metrics instrumented (requests, errors, latency)
- [ ] Infrastructure metrics monitored (CPU, memory, disk, network)
- [ ] Database metrics monitored (connections, query performance)
- [ ] Real-time dashboards for operations team

**High:**
- [ ] Business metrics tracked (signups, conversions, revenue)
- [ ] Custom metrics for critical application logic
- [ ] Historical trending analysis (compare current vs past performance)

**Medium:**
- [ ] Anomaly detection configured (alert on unusual patterns)
- [ ] Forecasting for capacity planning

**Validation:**
```python
# Metrics validation
def test_metrics_instrumentation():
    """Validate key metrics are being collected."""
    # Generate test traffic
    for i in range(100):
        api_call("/products")

    # Query metrics system
    metrics = query_metrics(metric="http_requests_total", last_minutes=5)
    assert metrics['count'] >= 100
    assert 'status_code' in metrics['labels']
    assert 'endpoint' in metrics['labels']
    assert 'method' in metrics['labels']
```

### 4.3 Alerting Configuration

**Critical:**
- [ ] Alerts configured for critical failures (service down, database unreachable)
- [ ] Alerts configured for error rate thresholds (>1% errors)
- [ ] Alerts configured for performance degradation (p95 latency >2x baseline)
- [ ] On-call rotation defined (someone always responsible)
- [ ] Alert escalation policy (if not acknowledged in X minutes)

**High:**
- [ ] Alerts route to appropriate channels (PagerDuty, Slack, Email)
- [ ] Alert runbooks documented (what to do when alert fires)
- [ ] Alert fatigue prevented (meaningful alerts only, proper thresholds)

**Medium:**
- [ ] Predictive alerts (forecast resource exhaustion)
- [ ] Composite alerts (multiple conditions)

**Validation:**
```python
# Alert configuration test
def test_alert_firing():
    """Validate alerts fire when thresholds breached."""
    # Trigger high error rate
    for i in range(100):
        api_call("/fail")  # Intentionally failing endpoint

    # Verify alert fired
    time.sleep(60)  # Wait for alert evaluation
    alerts = query_alerting_system(status="firing")
    assert any(alert['name'] == "HighErrorRate" for alert in alerts)
```

### 4.4 Distributed Tracing

**Critical:**
- [ ] Distributed tracing implemented for microservices (Jaeger, Zipkin, X-Ray)
- [ ] Trace context propagated across service boundaries
- [ ] Critical paths instrumented with spans

**High:**
- [ ] Trace sampling configured (balance overhead vs visibility)
- [ ] Trace analysis dashboard for performance debugging

**Medium:**
- [ ] Service dependency mapping automated
- [ ] Trace-based alerting (alert on slow traces)

**Validation:**
```python
# Distributed tracing validation
def test_distributed_tracing():
    """Validate traces capture full request flow."""
    # Execute multi-service request
    response = api_call("/checkout", data=checkout_data)
    trace_id = response.headers['X-Trace-ID']

    # Query tracing system
    trace = query_traces(trace_id=trace_id)

    # Verify all expected services in trace
    services = [span['service'] for span in trace['spans']]
    assert 'api-gateway' in services
    assert 'checkout-service' in services
    assert 'payment-service' in services
    assert 'inventory-service' in services
    assert 'notification-service' in services
```

---

## 5. Deployment & Release

**Goal:** Enable safe, repeatable, and reversible deployments.

### 5.1 CI/CD Pipeline

**Critical:**
- [ ] Automated build on every commit
- [ ] Automated tests run in CI (unit, integration, E2E)
- [ ] Build artifacts versioned and stored (Docker registry, artifact repository)
- [ ] Deployment automation configured (no manual steps)

**High:**
- [ ] Environment parity (dev/staging/prod nearly identical)
- [ ] Infrastructure as Code (Terraform, CloudFormation, Pulumi)
- [ ] Deployment requires passing tests (quality gate)

**Medium:**
- [ ] Blue-green or canary deployment strategy
- [ ] Automated smoke tests post-deployment

**Validation:**
```yaml
# CI/CD validation checklist
- name: CI Pipeline Validation
  steps:
    - verify: Build triggers on commit
      command: git push origin feature-branch
      expect: Build starts within 30 seconds

    - verify: Tests run automatically
      command: Check CI logs
      expect: Unit tests (100%), Integration tests (50+), E2E tests (10+) executed

    - verify: Build artifacts created
      command: docker images | grep myapp
      expect: Image tagged with commit SHA and semantic version

    - verify: Deployment automation
      command: Deploy to staging
      expect: Zero manual steps, deployment completes <5 minutes
```

### 5.2 Rollback Procedures

**Critical:**
- [ ] Rollback procedure documented and tested
- [ ] Rollback can be executed in <5 minutes
- [ ] Database migrations are reversible (backward-compatible)
- [ ] Feature flags allow instant disable of new features

**High:**
- [ ] Automated rollback on failed health checks
- [ ] Rollback testing in staging before every production deployment

**Medium:**
- [ ] Progressive rollback (roll back incrementally if possible)
- [ ] Rollback runbook includes communication plan

**Validation:**
```python
# Rollback test
def test_rollback_procedure():
    """Validate rollback works under 5 minutes."""
    # Deploy new version
    deploy_version("v2.0.0")
    assert get_deployed_version() == "v2.0.0"

    # Trigger rollback
    start = time.time()
    rollback_to_version("v1.9.0")
    rollback_duration = time.time() - start

    # Verify rollback successful and fast
    assert get_deployed_version() == "v1.9.0"
    assert rollback_duration < 300  # <5 minutes
    assert get_health_check_status() == "healthy"
```

### 5.3 Feature Flags & Progressive Rollout

**Critical:**
- [ ] Feature flag system implemented (LaunchDarkly, Flagsmith, custom)
- [ ] Critical features can be toggled without deployment
- [ ] Feature flags have default safe state (off by default for risky features)

**High:**
- [ ] Percentage-based rollouts (canary releases at code level)
- [ ] User targeting (enable for specific users/segments)

**Medium:**
- [ ] A/B testing capabilities
- [ ] Automatic flag cleanup (remove obsolete flags)

**Validation:**
```python
# Feature flag validation
def test_feature_flags():
    """Validate feature flags control feature availability."""
    # Feature disabled by default
    response = api_call("/new-feature")
    assert response.status_code == 404

    # Enable feature for 10% of users
    set_feature_flag("new-feature", enabled=True, percentage=10)

    # Verify ~10% get feature
    enabled_count = 0
    for i in range(1000):
        response = api_call("/new-feature", user=f"user{i}")
        if response.status_code == 200:
            enabled_count += 1

    assert 50 < enabled_count < 150  # Roughly 10% ± 5%
```

### 5.4 Deployment Validation

**Critical:**
- [ ] Smoke tests run immediately post-deployment
- [ ] Health check endpoints return 200 OK
- [ ] Critical user flows validated post-deployment
- [ ] Rollback triggered automatically if smoke tests fail

**High:**
- [ ] Performance comparison pre/post deployment
- [ ] Error rate monitoring during deployment
- [ ] Deployment notifications to team (Slack, email)

**Medium:**
- [ ] Automated screenshot comparison (visual regression)
- [ ] User acceptance testing in staging before production

**Validation:**
```python
# Post-deployment smoke tests
def test_post_deployment_smoke_tests():
    """Critical smoke tests that run after every deployment."""
    # Health check
    response = requests.get("https://api.example.com/health")
    assert response.status_code == 200
    assert response.json()['status'] == 'healthy'

    # Critical path: user can login
    response = login(email="test@example.com", password="test123")
    assert response.status_code == 200
    assert 'access_token' in response.json()

    # Critical path: user can view data
    token = response.json()['access_token']
    response = api_call("/dashboard", token=token)
    assert response.status_code == 200

    # Critical path: user can perform write operation
    response = api_call("/data", method="POST", token=token, data={...})
    assert response.status_code == 201
```

---

## 6. Data Integrity

**Goal:** Protect critical business data from loss or corruption.

### 6.1 Backup Strategy

**Critical:**
- [ ] Automated daily backups running successfully
- [ ] Backup completeness verified (no corrupted backups)
- [ ] Restore procedure tested and working (RTO/RPO validated)
- [ ] Backups encrypted (protect sensitive data)

**High:**
- [ ] Incremental backups for large datasets (faster backup/restore)
- [ ] Geo-redundant backup storage (survive regional disasters)
- [ ] Backup retention policy automated (30 days minimum, configurable)

**Medium:**
- [ ] Backup monitoring dashboard
- [ ] Automated backup restore testing (weekly)

**Validation:**
```bash
# Backup validation script
#!/bin/bash

# Verify backup exists and is recent
LATEST_BACKUP=$(aws s3 ls s3://backups/db/ --recursive | sort | tail -n 1)
BACKUP_AGE_HOURS=$(( ($(date +%s) - $(date -d "$(echo $LATEST_BACKUP | awk '{print $1, $2}')" +%s)) / 3600 ))

if [ $BACKUP_AGE_HOURS -gt 24 ]; then
    echo "ERROR: Latest backup is $BACKUP_AGE_HOURS hours old"
    exit 1
fi

# Test restore to isolated environment
pg_restore -d test_restore_db $LATEST_BACKUP

# Validate data integrity
ROW_COUNT=$(psql test_restore_db -t -c "SELECT COUNT(*) FROM critical_table;")
if [ $ROW_COUNT -lt 1000 ]; then
    echo "ERROR: Restored database has only $ROW_COUNT rows"
    exit 1
fi

echo "SUCCESS: Backup validated, restore tested"
```

### 6.2 Database Migrations

**Critical:**
- [ ] Migration scripts version controlled
- [ ] Migrations tested in staging before production
- [ ] Migrations are backward-compatible (allow rollback)
- [ ] Migrations have rollback scripts
- [ ] Zero-downtime migration strategy for breaking changes

**High:**
- [ ] Migration dry-run mode (preview changes without applying)
- [ ] Migration locks prevent concurrent execution
- [ ] Migration monitoring (duration, row counts affected)

**Medium:**
- [ ] Migration automation in CI/CD
- [ ] Migration documentation (what changed, why, impact)

**Validation:**
```python
# Migration testing framework
def test_database_migration():
    """Validate migrations are safe and reversible."""
    # Capture pre-migration state
    pre_migration_rows = query_db("SELECT COUNT(*) FROM users")
    pre_migration_schema = query_db("SELECT column_name FROM information_schema.columns WHERE table_name='users'")

    # Run migration
    result = run_migration("002_add_email_verification.sql")
    assert result.success

    # Verify migration applied correctly
    post_migration_schema = query_db("SELECT column_name FROM information_schema.columns WHERE table_name='users'")
    assert 'email_verified' in post_migration_schema
    assert query_db("SELECT COUNT(*) FROM users") == pre_migration_rows

    # Test rollback
    result = rollback_migration("002_add_email_verification.sql")
    assert result.success

    # Verify rollback successful
    post_rollback_schema = query_db("SELECT column_name FROM information_schema.columns WHERE table_name='users'")
    assert 'email_verified' not in post_rollback_schema
```

### 6.3 Data Validation & Integrity Constraints

**Critical:**
- [ ] Foreign key constraints enforced (referential integrity)
- [ ] NOT NULL constraints on required fields
- [ ] Unique constraints on unique identifiers
- [ ] Check constraints for valid data ranges

**High:**
- [ ] Input validation at application layer (defense in depth)
- [ ] Data type enforcement (prevent type confusion)
- [ ] Cascade delete rules defined (prevent orphaned records)

**Medium:**
- [ ] Trigger-based validation for complex rules
- [ ] Periodic data integrity audits

**Validation:**
```sql
-- Data integrity validation queries
-- Check for orphaned records
SELECT COUNT(*) FROM orders o
LEFT JOIN users u ON o.user_id = u.id
WHERE u.id IS NULL;
-- Expected: 0

-- Check for invalid data
SELECT COUNT(*) FROM users WHERE email NOT LIKE '%@%.%';
-- Expected: 0

-- Check for data consistency
SELECT COUNT(*) FROM orders
WHERE total_amount < 0 OR total_amount IS NULL;
-- Expected: 0
```

### 6.4 Audit Logging

**Critical:**
- [ ] Audit logs for sensitive operations (data modification, access, deletion)
- [ ] Audit logs tamper-proof (write-once storage)
- [ ] Audit logs include who, what, when, where (user, action, timestamp, IP)

**High:**
- [ ] Audit log retention (minimum 1 year for compliance)
- [ ] Audit log analysis and anomaly detection

**Medium:**
- [ ] Automated audit reports for compliance
- [ ] Audit log replay capability (reconstruct state)

**Validation:**
```python
# Audit logging validation
def test_audit_logging():
    """Validate sensitive operations are audited."""
    # Perform sensitive operation
    user_id = create_test_user()
    update_user_role(user_id, role="admin")

    # Verify audit log entry
    audit_logs = query_audit_logs(user_id=user_id, action="role_change")
    assert len(audit_logs) == 1
    assert audit_logs[0]['old_value'] == "user"
    assert audit_logs[0]['new_value'] == "admin"
    assert audit_logs[0]['actor_id'] is not None
    assert audit_logs[0]['timestamp'] is not None
    assert audit_logs[0]['ip_address'] is not None
```

---

## 7. Cost Optimization

**Goal:** Ensure efficient resource utilization and prevent cost overruns.

### 7.1 Resource Right-Sizing

**Critical:**
- [ ] Resource utilization monitored (CPU, memory, disk, network)
- [ ] Over-provisioned resources identified (utilization <30%)
- [ ] Under-provisioned resources identified (utilization >80%)

**High:**
- [ ] Reserved instances or savings plans for predictable workloads
- [ ] Spot instances for fault-tolerant batch workloads
- [ ] Auto-scaling prevents idle resources

**Medium:**
- [ ] Regular cost optimization reviews (monthly or quarterly)
- [ ] Rightsizing recommendations acted upon

**Validation:**
```python
# Resource utilization analysis
def analyze_resource_utilization():
    """Identify over/under-provisioned resources."""
    resources = get_all_compute_resources()

    over_provisioned = []
    under_provisioned = []

    for resource in resources:
        metrics = get_resource_metrics(resource.id, days=30)
        avg_cpu = metrics['avg_cpu']
        avg_memory = metrics['avg_memory']

        if avg_cpu < 30 and avg_memory < 30:
            over_provisioned.append(resource)
        elif avg_cpu > 80 or avg_memory > 80:
            under_provisioned.append(resource)

    print(f"Over-provisioned: {len(over_provisioned)} resources")
    print(f"Under-provisioned: {len(under_provisioned)} resources")

    # Generate recommendations
    for resource in over_provisioned:
        print(f"Downsize {resource.id}: {resource.type} -> {recommend_smaller_size(resource)}")
```

### 7.2 Cost Monitoring & Alerts

**Critical:**
- [ ] Cost tracking dashboard configured
- [ ] Budget alerts configured (alert at 50%, 80%, 100% of budget)
- [ ] Cost attribution by service/team (tag all resources)

**High:**
- [ ] Anomaly detection for unexpected cost spikes
- [ ] Cost forecasting (predict monthly costs)

**Medium:**
- [ ] Cost per user or transaction metrics
- [ ] Showback/chargeback reporting for internal teams

**Validation:**
```bash
# Cost monitoring validation
aws budgets describe-budgets --account-id 123456789012
# Verify: Budget defined with alerts

# Check resource tagging
UNTAGGED_RESOURCES=$(aws resourcegroupstaggingapi get-resources \
  --region us-east-1 \
  --resource-type-filters "ec2" "rds" "s3" \
  | jq '[.ResourceTagMappingList[] | select(.Tags | length == 0)] | length')

if [ $UNTAGGED_RESOURCES -gt 0 ]; then
    echo "WARNING: $UNTAGGED_RESOURCES resources are untagged"
fi
```

### 7.3 Waste Elimination

**Critical:**
- [ ] Unused resources identified and terminated
- [ ] Orphaned resources cleaned up (EBS volumes, snapshots, IPs)
- [ ] Development/testing environments shut down after hours

**High:**
- [ ] Data transfer costs optimized (use CDN, optimize region placement)
- [ ] Storage tiering (move old data to cheaper storage classes)

**Medium:**
- [ ] Compression enabled for data transfer and storage
- [ ] Cost-effective alternatives evaluated (managed services vs self-hosted)

**Validation:**
```python
# Waste identification script
def identify_cost_waste():
    """Find resources costing money without providing value."""
    waste_items = []

    # Unused EBS volumes (not attached to instances)
    unattached_volumes = aws_client.describe_volumes(
        Filters=[{'Name': 'status', 'Values': ['available']}]
    )
    waste_items.extend([
        {'type': 'EBS Volume', 'id': v['VolumeId'], 'cost_per_month': calculate_cost(v)}
        for v in unattached_volumes['Volumes']
    ])

    # Stopped instances running for >30 days
    stopped_instances = aws_client.describe_instances(
        Filters=[{'Name': 'instance-state-name', 'Values': ['stopped']}]
    )
    for reservation in stopped_instances['Reservations']:
        for instance in reservation['Instances']:
            stopped_duration = (datetime.now() - instance['StateTransitionReason']['Time']).days
            if stopped_duration > 30:
                waste_items.append({
                    'type': 'Stopped Instance',
                    'id': instance['InstanceId'],
                    'stopped_days': stopped_duration,
                    'cost_per_month': calculate_cost(instance)
                })

    print(f"Total waste items: {len(waste_items)}")
    print(f"Potential savings: ${sum(item['cost_per_month'] for item in waste_items)}/month")
```

---

## 8. Compliance Readiness

**Goal:** Meet regulatory requirements and industry standards.

### 8.1 Data Privacy (GDPR, CCPA)

**Critical:**
- [ ] User consent mechanisms implemented (opt-in/opt-out)
- [ ] Data access request handling (users can request their data)
- [ ] Data deletion request handling ("right to be forgotten")
- [ ] Privacy policy published and accessible

**High:**
- [ ] Data processing agreements with third-party vendors
- [ ] Data breach notification procedures documented
- [ ] Data minimization (only collect necessary data)

**Medium:**
- [ ] Privacy by design principles applied
- [ ] Data protection impact assessments (DPIAs) conducted

**Validation:**
```python
# GDPR compliance validation
def test_gdpr_compliance():
    """Validate GDPR requirements are met."""
    # Test: User can request their data
    user_id = create_test_user()
    data_request = request_user_data(user_id)
    assert data_request['status'] == 'approved'
    assert len(data_request['data']) > 0

    # Test: User can delete their data
    deletion_request = request_data_deletion(user_id)
    assert deletion_request['status'] == 'completed'

    # Verify user data actually deleted
    user_data = query_db(f"SELECT * FROM users WHERE id = {user_id}")
    assert len(user_data) == 0
```

### 8.2 Security Compliance (SOC2, ISO 27001)

**Critical:**
- [ ] Access controls documented and enforced (least privilege)
- [ ] Security incident response plan documented
- [ ] Vulnerability management process defined
- [ ] Change management process documented

**High:**
- [ ] Security awareness training for employees
- [ ] Third-party security assessments completed
- [ ] Penetration testing conducted annually

**Medium:**
- [ ] Security metrics tracked and reported
- [ ] Security policy review and updates (annual)

**Validation:**
```bash
# SOC2 compliance checklist validation
# Access control audit
aws iam get-account-authorization-details > iam-audit.json
jq '.Users[] | select(.UserId) | {User: .UserName, MFA: .UserPolicyList}' iam-audit.json

# Verify MFA enabled for all users
USERS_WITHOUT_MFA=$(jq '[.Users[] | select(.MfaDevices | length == 0)] | length' iam-audit.json)
if [ $USERS_WITHOUT_MFA -gt 0 ]; then
    echo "COMPLIANCE VIOLATION: $USERS_WITHOUT_MFA users without MFA"
fi
```

### 8.3 Industry-Specific Compliance (HIPAA, PCI-DSS)

**Critical (if applicable):**
- [ ] Data encryption at rest and in transit
- [ ] Audit logging for all data access
- [ ] Access controls with role-based permissions
- [ ] Regular compliance audits and certifications

**High (if applicable):**
- [ ] Dedicated compliance officer or DPO assigned
- [ ] Compliance training for relevant personnel
- [ ] Business associate agreements (HIPAA)

**Validation:**
```python
# HIPAA compliance validation (if applicable)
def test_hipaa_compliance():
    """Validate HIPAA requirements for healthcare data."""
    # Test: PHI is encrypted at rest
    database_encryption = check_database_encryption()
    assert database_encryption['enabled'] == True

    # Test: Audit logs for PHI access
    phi_access_logs = query_audit_logs(data_type="PHI", days=1)
    assert all('user_id' in log and 'timestamp' in log for log in phi_access_logs)

    # Test: Access controls enforced
    unauthorized_response = api_call("/patient/123/records", token=regular_user_token)
    assert unauthorized_response.status_code == 403
```

### 8.4 Audit Trail & Reporting

**Critical:**
- [ ] Comprehensive audit logs maintained
- [ ] Audit logs retained per regulatory requirements
- [ ] Compliance reporting automated where possible

**High:**
- [ ] Regular compliance audits scheduled
- [ ] Audit findings tracked and remediated

**Medium:**
- [ ] Compliance dashboard for stakeholders
- [ ] Automated compliance checks in CI/CD

**Validation:**
```bash
# Audit trail validation
# Verify audit logs are being collected
LOG_COUNT=$(aws cloudwatch get-metric-statistics \
  --namespace AWS/Logs \
  --metric-name IncomingLogEvents \
  --start-time $(date -u -d '1 hour ago' +%Y-%m-%dT%H:%M:%S) \
  --end-time $(date -u +%Y-%m-%dT%H:%M:%S) \
  --period 3600 \
  --statistics Sum \
  | jq '.Datapoints[0].Sum')

if [ "$LOG_COUNT" -lt 100 ]; then
    echo "WARNING: Low log volume ($LOG_COUNT events/hour)"
fi
```

---

## Production Readiness Scoring

Calculate your overall production readiness score:

### Scoring Formula

- **Critical:** 10 points each
- **High:** 5 points each
- **Medium:** 2 points each
- **Low:** 1 point each

**Total Possible:** ~500 points (varies by applicability)

### Readiness Levels

- **90-100%:** Production Ready (excellent operational maturity)
- **75-89%:** Mostly Ready (address remaining high/critical items before launch)
- **60-74%:** Needs Work (significant gaps remain, not ready for production)
- **<60%:** Not Ready (substantial work required across multiple areas)

### Example Scoring

```python
# Production readiness scoring calculator
def calculate_readiness_score(assessment_results):
    """Calculate production readiness score."""
    score = 0
    max_score = 0

    for area in assessment_results:
        for item in area['items']:
            points = {
                'Critical': 10,
                'High': 5,
                'Medium': 2,
                'Low': 1
            }[item['severity']]

            max_score += points
            if item['status'] == 'pass':
                score += points

    percentage = (score / max_score) * 100
    return {
        'score': score,
        'max_score': max_score,
        'percentage': percentage,
        'readiness_level': get_readiness_level(percentage)
    }

def get_readiness_level(percentage):
    if percentage >= 90:
        return "Production Ready"
    elif percentage >= 75:
        return "Mostly Ready"
    elif percentage >= 60:
        return "Needs Work"
    else:
        return "Not Ready"
```

---

## Next Steps

After completing this framework assessment:

1. **Generate Report:** Document findings with severity classifications
2. **Prioritize Gaps:** Focus on Critical and High severity items first
3. **Create Remediation Plan:** Estimate effort, assign owners, set deadlines
4. **Execute Fixes:** Implement fixes following TDD and repository best practices
5. **Re-Validate:** Run assessments again to confirm gaps resolved
6. **Document Evidence:** Maintain proof of production readiness for stakeholders

**Related Guides:**
- [PRODUCTION_DEPLOYMENT_CHECKLIST.md](PRODUCTION_DEPLOYMENT_CHECKLIST.md) - Pre-deployment validation checklist
- [SECURITY_HARDENING.md](SECURITY_HARDENING.md) - Detailed security guidance
- [PERFORMANCE_BENCHMARKS.md](PERFORMANCE_BENCHMARKS.md) - Performance standards
- [MONITORING_AND_OBSERVABILITY.md](MONITORING_AND_OBSERVABILITY.md) - Monitoring setup

---

**Framework Version:** 1.0
**Last Updated:** 2025-10-27
**Maintainer:** Development Best Practices Repository
