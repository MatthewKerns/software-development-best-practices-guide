# Rollback & Disaster Recovery Guide

## Overview

Rollback and disaster recovery procedures are critical safety mechanisms for production systems. This guide covers strategies for reverting bad deployments, recovering from failures, and maintaining business continuity.

**Key Principles:**
- **Rollback First, Debug Later:** When production is broken, restore service immediately
- **Test Before You Need It:** Regularly test rollback and recovery procedures
- **Document Everything:** Runbooks should be executable by anyone on-call
- **Automate When Possible:** Manual rollback is error-prone under pressure
- **Measure and Improve:** Track MTTR (Mean Time To Recovery) and optimize

**Complexity Tiers:**
- **Small-Scale:** Manual rollback via Git revert + redeploy (5-15 minutes)
- **Medium-Scale:** Automated rollback + database migration rollback (5-30 minutes)
- **Large-Scale:** Blue-green/canary with automatic rollback + multi-region failover (<5 minutes)

---

## 1. Application Rollback Strategies

### 1.1 Git-Based Rollback (All Scales)

**When to Use:** Bad code deployment, broken features, configuration errors

**Quick Rollback (Manual):**
```bash
#!/bin/bash
# rollback.sh - Quick application rollback

set -e

echo "=== Application Rollback ==="

# 1. Get current deployed version
CURRENT_VERSION=$(git describe --tags --abbrev=0)
echo "Current version: $CURRENT_VERSION"

# 2. Get previous stable version
PREVIOUS_VERSION=$(git describe --tags --abbrev=0 $CURRENT_VERSION^)
echo "Rolling back to: $PREVIOUS_VERSION"

# 3. Confirm rollback
read -p "Rollback from $CURRENT_VERSION to $PREVIOUS_VERSION? (yes/no): " CONFIRM
if [ "$CONFIRM" != "yes" ]; then
    echo "Rollback cancelled"
    exit 1
fi

# 4. Checkout previous version
git checkout $PREVIOUS_VERSION

# 5. Deploy (adapt to your deployment method)
# Option A: Netlify/Vercel
netlify deploy --prod

# Option B: Docker
docker build -t myapp:rollback .
docker tag myapp:rollback myapp:latest
docker push myapp:latest

# Option C: Kubernetes
kubectl set image deployment/myapp myapp=myapp:$PREVIOUS_VERSION
kubectl rollout status deployment/myapp

# 6. Verify deployment
sleep 30
HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" https://api.example.com/health)
if [ "$HTTP_CODE" -eq 200 ]; then
    echo "✓ Rollback successful"
else
    echo "✗ Rollback failed - health check returned $HTTP_CODE"
    exit 1
fi

# 7. Notify team
curl -X POST https://hooks.slack.com/services/YOUR/WEBHOOK/URL \
  -H 'Content-Type: application/json' \
  -d "{\"text\": \"⚠️ Rolled back from $CURRENT_VERSION to $PREVIOUS_VERSION\"}"

echo "Rollback complete. Monitor closely for next 30 minutes."
```

**Automated Rollback (CI/CD):**
```yaml
# .github/workflows/rollback.yml
name: Rollback to Previous Version

on:
  workflow_dispatch:
    inputs:
      target_version:
        description: 'Target version to rollback to (leave empty for previous)'
        required: false

jobs:
  rollback:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
        with:
          fetch-depth: 0  # Full history for version lookup

      - name: Determine rollback target
        id: target
        run: |
          if [ -z "${{ github.event.inputs.target_version }}" ]; then
            CURRENT=$(git describe --tags --abbrev=0)
            TARGET=$(git describe --tags --abbrev=0 $CURRENT^)
          else
            TARGET="${{ github.event.inputs.target_version }}"
          fi
          echo "target=$TARGET" >> $GITHUB_OUTPUT
          echo "Rolling back to: $TARGET"

      - name: Checkout target version
        run: git checkout ${{ steps.target.outputs.target }}

      - name: Run smoke tests
        run: npm test

      - name: Deploy rollback
        run: |
          # Your deployment command
          ./deploy.sh

      - name: Verify deployment
        run: |
          sleep 30
          curl -f https://api.example.com/health || exit 1

      - name: Notify team
        uses: 8398a7/action-slack@v3
        with:
          status: custom
          custom_payload: |
            {
              text: "🔄 Rollback to ${{ steps.target.outputs.target }} completed",
              attachments: [{
                color: 'warning',
                fields: [{
                  title: 'Triggered By',
                  value: '${{ github.actor }}',
                  short: true
                }]
              }]
            }
```

**Checklist:**
- [ ] Rollback script tested in staging
- [ ] Team trained on rollback procedure
- [ ] Rollback time measured (<15 minutes target)
- [ ] Automatic health checks post-rollback

### 1.2 Feature Flag Rollback (Medium/Large Scale)

**When to Use:** Instant rollback without redeployment, A/B test issues, gradual rollout problems

**Implementation:**
```python
# Feature flag instant rollback
import requests

LAUNCHDARKLY_API_KEY = os.getenv('LAUNCHDARKLY_API_KEY')
PROJECT_KEY = 'production'
ENVIRONMENT_KEY = 'production'

def disable_feature_flag(flag_key, reason):
    """Instantly disable a feature flag (rollback)."""
    url = f"https://app.launchdarkly.com/api/v2/flags/{PROJECT_KEY}/{flag_key}"

    # Disable flag in production
    response = requests.patch(url, headers={
        'Authorization': LAUNCHDARKLY_API_KEY,
        'Content-Type': 'application/json'
    }, json={
        'comment': f"Emergency rollback: {reason}",
        'environmentKey': ENVIRONMENT_KEY,
        'instructions': [{
            'kind': 'turnFlagOff'
        }]
    })

    if response.status_code == 200:
        print(f"✓ Feature flag '{flag_key}' disabled")

        # Log rollback
        log_rollback_event({
            'type': 'feature_flag_rollback',
            'flag': flag_key,
            'reason': reason,
            'timestamp': datetime.utcnow().isoformat()
        })

        # Notify team
        send_slack_notification(
            f"🚨 Feature flag `{flag_key}` disabled: {reason}"
        )
    else:
        raise Exception(f"Failed to disable flag: {response.text}")

# Usage during incident
if error_rate > 0.10 and recent_deployment:
    disable_feature_flag(
        flag_key='new-checkout-flow',
        reason='High error rate (12%) detected after enabling new checkout'
    )
```

**Gradual Rollback (Percentage-Based):**
```python
def gradual_rollback(flag_key, current_percentage, target_percentage=0, step=10, interval=60):
    """Gradually reduce feature flag rollout percentage.

    Args:
        flag_key: Feature flag identifier
        current_percentage: Current rollout percentage (e.g., 100)
        target_percentage: Target percentage (default: 0 = full rollback)
        step: Percentage to decrease per interval (default: 10)
        interval: Seconds between steps (default: 60)
    """
    percentage = current_percentage

    while percentage > target_percentage:
        percentage = max(target_percentage, percentage - step)

        # Update flag rollout
        update_flag_rollout(flag_key, percentage)

        print(f"Rolled back to {percentage}% - monitoring for {interval}s...")

        # Monitor error rate
        time.sleep(interval)
        error_rate = get_error_rate()

        if error_rate < 0.01:  # <1% error rate = safe to continue
            print(f"Error rate normal ({error_rate:.2%}) at {percentage}%")
        else:
            print(f"⚠️ Error rate still high ({error_rate:.2%}) - continuing rollback")

    print(f"✓ Gradual rollback complete: {flag_key} at {target_percentage}%")

# Usage: Gradually roll back from 100% to 0%
gradual_rollback('new-payment-gateway', current_percentage=100)
```

**Checklist:**
- [ ] Critical features have feature flags
- [ ] Feature flags can be toggled without deployment
- [ ] Rollback scripts for instant flag disable
- [ ] Monitoring alerts on flag state changes

### 1.3 Container/Kubernetes Rollback (Medium/Large Scale)

**When to Use:** Containerized deployments, microservices

**Kubernetes Rollback:**
```bash
#!/bin/bash
# k8s-rollback.sh - Rollback Kubernetes deployment

DEPLOYMENT=$1
NAMESPACE=${2:-production}

if [ -z "$DEPLOYMENT" ]; then
    echo "Usage: $0 <deployment-name> [namespace]"
    exit 1
fi

echo "=== Kubernetes Rollback: $DEPLOYMENT ==="

# 1. Check rollout history
echo "Rollout history:"
kubectl rollout history deployment/$DEPLOYMENT -n $NAMESPACE

# 2. Get current revision
CURRENT_REVISION=$(kubectl rollout history deployment/$DEPLOYMENT -n $NAMESPACE --revision=0 | tail -n 1 | awk '{print $1}')
echo "Current revision: $CURRENT_REVISION"

# 3. Rollback to previous revision
echo "Rolling back to previous revision..."
kubectl rollout undo deployment/$DEPLOYMENT -n $NAMESPACE

# 4. Wait for rollback to complete
echo "Waiting for rollback to complete..."
kubectl rollout status deployment/$DEPLOYMENT -n $NAMESPACE --timeout=5m

# 5. Verify rollback
READY_REPLICAS=$(kubectl get deployment $DEPLOYMENT -n $NAMESPACE -o jsonpath='{.status.readyReplicas}')
DESIRED_REPLICAS=$(kubectl get deployment $DEPLOYMENT -n $NAMESPACE -o jsonpath='{.spec.replicas}')

if [ "$READY_REPLICAS" -eq "$DESIRED_REPLICAS" ]; then
    echo "✓ Rollback successful: $READY_REPLICAS/$DESIRED_REPLICAS replicas ready"
else
    echo "✗ Rollback failed: $READY_REPLICAS/$DESIRED_REPLICAS replicas ready"
    exit 1
fi

# 6. Run smoke tests
echo "Running smoke tests..."
kubectl run smoke-test --image=curlimages/curl --rm -i --restart=Never -- \
  curl -f http://$DEPLOYMENT.$NAMESPACE.svc.cluster.local/health

echo "Rollback complete. Monitor closely."
```

**Automated Rollback on Health Check Failure:**
```yaml
# deployment.yaml with automated rollback
apiVersion: apps/v1
kind: Deployment
metadata:
  name: api
spec:
  replicas: 3
  strategy:
    type: RollingUpdate
    rollingUpdate:
      maxSurge: 1
      maxUnavailable: 0  # Zero downtime

  # Automated rollback on failure
  progressDeadlineSeconds: 600  # 10 minutes timeout
  revisionHistoryLimit: 10      # Keep 10 previous versions

  template:
    spec:
      containers:
      - name: api
        image: myapp:latest

        # Readiness probe (traffic only to ready pods)
        readinessProbe:
          httpGet:
            path: /health
            port: 8080
          initialDelaySeconds: 10
          periodSeconds: 5
          failureThreshold: 3

        # Liveness probe (restart unhealthy pods)
        livenessProbe:
          httpGet:
            path: /health
            port: 8080
          initialDelaySeconds: 30
          periodSeconds: 10
          failureThreshold: 3
```

**Checklist:**
- [ ] Deployment history retained (10+ revisions)
- [ ] Health checks configured (readiness + liveness)
- [ ] Progressive delivery (rolling update, not recreate)
- [ ] Automated rollback on health check failure

---

## 2. Database Rollback Strategies

### 2.1 Forward-Compatible Migrations (MANDATORY)

**Principle:** Database migrations must be backward-compatible to allow safe rollback

**Safe Migration Pattern:**
```python
# GOOD: Backward-compatible migration (3-step process)

# Step 1: Add new column (nullable, with default)
"""Add email_verified column

Revision: 001
"""
def upgrade():
    op.add_column('users',
        sa.Column('email_verified', sa.Boolean(), nullable=True, server_default='false')
    )
    # Old code still works (ignores new column)

def downgrade():
    op.drop_column('users', 'email_verified')

# Deploy Step 1, wait 24 hours
# ✓ New column exists but unused
# ✓ Rollback safe (old code doesn't use new column)

# Step 2: Start using new column in code
# Deploy new application code that writes to email_verified
# Old code still works (ignores column, writes to old fields)

# Step 3: Backfill data, make column NOT NULL (optional)
"""Backfill email_verified column

Revision: 002
"""
def upgrade():
    # Backfill existing data
    op.execute("""
        UPDATE users
        SET email_verified = (email_confirmation_token IS NULL)
        WHERE email_verified IS NULL
    """)

    # Make non-nullable after backfill
    op.alter_column('users', 'email_verified', nullable=False)

def downgrade():
    op.alter_column('users', 'email_verified', nullable=True)

# Deploy Step 3 only after Step 2 is stable for 24+ hours
```

**Unsafe Migration (AVOID):**
```python
# BAD: Breaking migration (forces immediate code deployment)

def upgrade():
    # This breaks old code immediately
    op.drop_column('users', 'old_field')
    op.add_column('users', sa.Column('new_field', sa.String(), nullable=False))

# Problem: Old application code expects 'old_field', crashes immediately
# Rollback: Impossible without data loss
```

**Safe Column Removal (Expand-Contract Pattern):**
```python
# Phase 1: Stop writing to old column (deploy code change)
# Wait 24-48 hours, verify no usage

# Phase 2: Migration removes unused column
"""Remove deprecated old_field column

Revision: 003
Prerequisite: Application code must not reference old_field
"""
def upgrade():
    # Safe because nothing uses this column anymore
    op.drop_column('users', 'old_field')

def downgrade():
    # Recreate column (data lost, but acceptable)
    op.add_column('users', sa.Column('old_field', sa.String(), nullable=True))
```

**Checklist:**
- [ ] All migrations backward-compatible
- [ ] Expand-contract pattern for schema changes
- [ ] 24-48 hour waiting period between breaking changes
- [ ] Migration rollback tested in staging

### 2.2 Database Backup & Restore

**Automated Backup (All Scales):**
```bash
#!/bin/bash
# db-backup.sh - Automated database backup

set -e

DB_HOST=${DB_HOST:-localhost}
DB_NAME=${DB_NAME:-production}
DB_USER=${DB_USER:-postgres}
BACKUP_DIR=${BACKUP_DIR:-/backups/postgres}
S3_BUCKET=${S3_BUCKET:-s3://prod-backups/database}

TIMESTAMP=$(date +%Y%m%d_%H%M%S)
BACKUP_FILE="$BACKUP_DIR/${DB_NAME}_${TIMESTAMP}.dump"

echo "=== Database Backup: $DB_NAME ==="

# 1. Create backup directory
mkdir -p $BACKUP_DIR

# 2. Perform backup
echo "Creating backup..."
pg_dump -h $DB_HOST -U $DB_USER -F c -b -v -f $BACKUP_FILE $DB_NAME

# 3. Verify backup integrity
echo "Verifying backup..."
pg_restore --list $BACKUP_FILE > /dev/null
BACKUP_SIZE=$(du -h $BACKUP_FILE | cut -f1)
echo "Backup size: $BACKUP_SIZE"

# 4. Compress backup
echo "Compressing backup..."
gzip $BACKUP_FILE
BACKUP_FILE="${BACKUP_FILE}.gz"

# 5. Encrypt backup
echo "Encrypting backup..."
gpg --encrypt --recipient backup@example.com $BACKUP_FILE
ENCRYPTED_FILE="${BACKUP_FILE}.gpg"

# 6. Upload to S3 (geo-redundant storage)
echo "Uploading to S3..."
aws s3 cp $ENCRYPTED_FILE $S3_BUCKET/ \
  --storage-class GLACIER_IR \
  --metadata "timestamp=$TIMESTAMP,database=$DB_NAME,size=$BACKUP_SIZE"

# 7. Verify upload
aws s3 ls $S3_BUCKET/ | grep $(basename $ENCRYPTED_FILE)

# 8. Cleanup old local backups (keep 7 days)
find $BACKUP_DIR -name "*.dump.gz.gpg" -mtime +7 -delete

# 9. Log backup completion
echo "Backup complete: $ENCRYPTED_FILE"
echo "S3 location: $S3_BUCKET/$(basename $ENCRYPTED_FILE)"

# 10. Send notification
curl -X POST https://hooks.slack.com/services/YOUR/WEBHOOK/URL \
  -H 'Content-Type: application/json' \
  -d "{\"text\": \"✓ Database backup completed: $DB_NAME ($BACKUP_SIZE)\"}"
```

**Database Restore (Disaster Recovery):**
```bash
#!/bin/bash
# db-restore.sh - Restore database from backup

set -e

BACKUP_FILE=$1
DB_NAME=${2:-production_restore}
DB_HOST=${DB_HOST:-localhost}
DB_USER=${DB_USER:-postgres}

if [ -z "$BACKUP_FILE" ]; then
    echo "Usage: $0 <backup-file> [database-name]"
    echo "Available backups:"
    aws s3 ls s3://prod-backups/database/ | tail -10
    exit 1
fi

echo "=== Database Restore ==="
echo "WARNING: This will drop and recreate database '$DB_NAME'"
read -p "Continue? (yes/no): " CONFIRM

if [ "$CONFIRM" != "yes" ]; then
    echo "Restore cancelled"
    exit 1
fi

# 1. Download backup from S3
echo "Downloading backup..."
aws s3 cp s3://prod-backups/database/$BACKUP_FILE /tmp/

# 2. Decrypt backup
echo "Decrypting backup..."
gpg --decrypt /tmp/$BACKUP_FILE > /tmp/backup.dump.gz

# 3. Decompress backup
echo "Decompressing backup..."
gunzip /tmp/backup.dump.gz

# 4. Drop existing database (if exists)
echo "Dropping existing database..."
psql -h $DB_HOST -U $DB_USER -c "DROP DATABASE IF EXISTS $DB_NAME;"

# 5. Create new database
echo "Creating database..."
psql -h $DB_HOST -U $DB_USER -c "CREATE DATABASE $DB_NAME;"

# 6. Restore backup
echo "Restoring backup..."
pg_restore -h $DB_HOST -U $DB_USER -d $DB_NAME -v /tmp/backup.dump

# 7. Verify restoration
echo "Verifying restoration..."
RECORD_COUNT=$(psql -h $DB_HOST -U $DB_USER -d $DB_NAME -t -c "SELECT COUNT(*) FROM users;")
echo "User records: $RECORD_COUNT"

if [ "$RECORD_COUNT" -gt 0 ]; then
    echo "✓ Restore successful"
else
    echo "✗ Restore verification failed"
    exit 1
fi

# 8. Update sequences (if needed)
echo "Updating sequences..."
psql -h $DB_HOST -U $DB_USER -d $DB_NAME <<EOF
SELECT 'SELECT SETVAL(' ||
       quote_literal(quote_ident(PGT.schemaname) || '.' || quote_ident(S.relname)) ||
       ', COALESCE(MAX(' ||quote_ident(C.attname)|| '), 1) ) FROM ' ||
       quote_ident(PGT.schemaname)|| '.'||quote_ident(T.relname)|| ';'
FROM pg_class AS S,
     pg_depend AS D,
     pg_class AS T,
     pg_attribute AS C,
     pg_tables AS PGT
WHERE S.relkind = 'S'
    AND S.oid = D.objid
    AND D.refobjid = T.oid
    AND D.refobjid = C.attrelid
    AND D.refobjsubid = C.attnum
    AND T.relname = PGT.tablename
ORDER BY S.relname;
EOF

# 9. Cleanup
rm /tmp/backup.dump /tmp/$BACKUP_FILE

echo "Restore complete. Database: $DB_NAME"
```

**Restore Testing (Monthly):**
```bash
#!/bin/bash
# test-restore.sh - Monthly backup restoration test

LATEST_BACKUP=$(aws s3 ls s3://prod-backups/database/ | sort | tail -n 1 | awk '{print $4}')

echo "=== Testing Backup Restoration ==="
echo "Latest backup: $LATEST_BACKUP"

# Restore to test database
./db-restore.sh $LATEST_BACKUP test_restore_$(date +%Y%m%d)

# Run validation queries
psql -d test_restore -c "SELECT COUNT(*) FROM users;"
psql -d test_restore -c "SELECT MAX(created_at) FROM users;"

# Calculate RTO (Recovery Time Objective)
# Target: <1 hour for medium/large scale

# Cleanup test database
psql -c "DROP DATABASE test_restore_$(date +%Y%m%d);"

echo "✓ Backup restoration test passed"
```

**Checklist:**
- [ ] Automated daily backups
- [ ] Backups encrypted and geo-redundant
- [ ] Restore tested monthly (RTO validated)
- [ ] Point-in-time recovery available (if needed)
- [ ] Backup monitoring and alerting

---

## 3. Disaster Recovery Planning

### 3.1 Recovery Time Objective (RTO) & Recovery Point Objective (RPO)

**Define Targets:**
```markdown
# RTO/RPO Targets by Scale

## Small-Scale
- **RTO:** 4 hours (acceptable downtime)
- **RPO:** 24 hours (daily backups)
- **Cost:** Minimal (<$50/month)

## Medium-Scale
- **RTO:** 1 hour (restore from backup)
- **RPO:** 1 hour (hourly backups or WAL archiving)
- **Cost:** Moderate ($200-500/month)

## Large-Scale
- **RTO:** 15 minutes (multi-region failover)
- **RPO:** 5 minutes (continuous replication)
- **Cost:** Significant ($1K-5K/month)
```

**RTO/RPO Validation:**
```python
# Validate RTO/RPO targets with testing
def validate_rto_rpo():
    """Test disaster recovery within RTO/RPO targets."""

    # Record start time
    incident_start = datetime.now()

    # Simulate failure
    print("Simulating database failure...")
    stop_database()

    # Begin recovery
    recovery_start = datetime.now()
    print(f"Recovery started at {recovery_start}")

    # Restore from latest backup
    latest_backup = get_latest_backup()
    backup_timestamp = parse_backup_timestamp(latest_backup)

    restore_database(latest_backup)

    # Record recovery completion
    recovery_end = datetime.now()

    # Calculate metrics
    rto_actual = (recovery_end - recovery_start).total_seconds() / 60  # minutes
    rpo_actual = (incident_start - backup_timestamp).total_seconds() / 60  # minutes

    print(f"RTO Actual: {rto_actual:.1f} minutes")
    print(f"RPO Actual: {rpo_actual:.1f} minutes")

    # Validate against targets
    rto_target = 60  # 1 hour for medium-scale
    rpo_target = 60  # 1 hour for medium-scale

    if rto_actual <= rto_target and rpo_actual <= rpo_target:
        print("✓ DR targets met")
    else:
        print(f"✗ DR targets exceeded (RTO: {rto_target}m, RPO: {rpo_target}m)")

    return {
        'rto_actual': rto_actual,
        'rpo_actual': rpo_actual,
        'rto_target': rto_target,
        'rpo_target': rpo_target,
        'passed': rto_actual <= rto_target and rpo_actual <= rpo_target
    }
```

### 3.2 Multi-Region Failover (Large-Scale)

**Automated Failover:**
```python
# Multi-region disaster recovery failover
import boto3

def failover_to_secondary_region():
    """Failover from primary to secondary region."""

    PRIMARY_REGION = 'us-east-1'
    SECONDARY_REGION = 'eu-west-1'

    # 1. Verify primary region is unhealthy
    if is_region_healthy(PRIMARY_REGION):
        print("Primary region is healthy, no failover needed")
        return

    print(f"Primary region {PRIMARY_REGION} unhealthy, failing over to {SECONDARY_REGION}")

    # 2. Promote read replica to primary (Aurora Global Database)
    rds_client = boto3.client('rds', region_name=SECONDARY_REGION)

    response = rds_client.failover_global_cluster(
        GlobalClusterIdentifier='production-global',
        TargetDbClusterIdentifier='production-secondary'
    )

    print("Database failover initiated...")

    # 3. Wait for database promotion
    waiter = rds_client.get_waiter('db_cluster_available')
    waiter.wait(DBClusterIdentifier='production-secondary')

    print("✓ Database promoted to primary in secondary region")

    # 4. Update DNS to point to secondary region
    route53 = boto3.client('route53')

    response = route53.change_resource_record_sets(
        HostedZoneId='Z1234567890ABC',
        ChangeBatch={
            'Changes': [{
                'Action': 'UPSERT',
                'ResourceRecordSet': {
                    'Name': 'api.example.com',
                    'Type': 'A',
                    'AliasTarget': {
                        'HostedZoneId': 'Z1234567890DEF',
                        'DNSName': 'api-eu-west-1.example.com',
                        'EvaluateTargetHealth': True
                    }
                }
            }]
        }
    )

    print("✓ DNS updated to point to secondary region")

    # 5. Verify failover
    time.sleep(60)  # Wait for DNS propagation

    health_check = requests.get('https://api.example.com/health')
    if health_check.status_code == 200:
        print("✓ Failover successful")

        # Notify team
        send_alert(
            severity='critical',
            message=f'Failover to {SECONDARY_REGION} completed. Primary region {PRIMARY_REGION} offline.'
        )
    else:
        print("✗ Failover failed")
        raise Exception("Secondary region unhealthy after failover")
```

**Failover Testing (Quarterly):**
```bash
#!/bin/bash
# test-failover.sh - Test multi-region failover

echo "=== Multi-Region Failover Test ==="

# 1. Record baseline
PRIMARY_REGION="us-east-1"
SECONDARY_REGION="eu-west-1"

echo "Primary region: $PRIMARY_REGION"
echo "Secondary region: $SECONDARY_REGION"

# 2. Verify both regions healthy
curl -f https://api-us-east-1.example.com/health || exit 1
curl -f https://api-eu-west-1.example.com/health || exit 1

# 3. Simulate primary region failure (disable health check)
echo "Simulating primary region failure..."
aws route53 update-health-check \
  --health-check-id $PRIMARY_HEALTH_CHECK_ID \
  --disabled

# 4. Wait for automatic failover (should be <5 minutes)
echo "Waiting for automatic failover..."
START_TIME=$(date +%s)

for i in {1..60}; do
    RESOLVED_REGION=$(dig +short api.example.com | head -n 1)
    SECONDARY_IP=$(dig +short api-eu-west-1.example.com | head -n 1)

    if [ "$RESOLVED_REGION" == "$SECONDARY_IP" ]; then
        END_TIME=$(date +%s)
        FAILOVER_TIME=$((END_TIME - START_TIME))
        echo "✓ Failover completed in ${FAILOVER_TIME} seconds"
        break
    fi

    sleep 5
done

# 5. Verify application functionality in secondary region
curl -f https://api.example.com/health || exit 1

# 6. Re-enable primary region
aws route53 update-health-check \
  --health-check-id $PRIMARY_HEALTH_CHECK_ID \
  --no-disabled

echo "Failover test complete. RTO: ${FAILOVER_TIME}s (target: <300s)"
```

---

## 4. Rollback Testing & Drills

### 4.1 Monthly Rollback Drills

**Rollback Drill Schedule:**
```markdown
# Monthly Rollback Drill Calendar

## Week 1: Application Rollback
- Deploy new version to staging
- Introduce intentional bug
- Practice rollback procedure
- Measure time to rollback
- Update runbook based on learnings

## Week 2: Database Restore
- Restore latest backup to test environment
- Validate data integrity
- Measure RTO (recovery time)
- Test rollback of migration

## Week 3: Feature Flag Rollback
- Enable feature flag in staging
- Simulate high error rate
- Practice instant flag disable
- Verify gradual rollback script

## Week 4: Full DR Simulation
- Simulate multi-component failure
- Practice complete disaster recovery
- Measure end-to-end recovery time
- Document lessons learned
```

**Automated Rollback Testing:**
```python
# rollback_test.py - Automated rollback testing
import subprocess
import time
from datetime import datetime

class RollbackTester:
    """Test rollback procedures automatically."""

    def test_application_rollback(self):
        """Test application rollback time."""
        print("=== Testing Application Rollback ===")

        # Deploy test version
        print("Deploying test version...")
        subprocess.run(['./deploy.sh', 'test-v1.0.0'], check=True)
        time.sleep(30)

        # Trigger rollback
        print("Triggering rollback...")
        start_time = time.time()
        subprocess.run(['./rollback.sh'], check=True)
        rollback_time = time.time() - start_time

        # Verify application healthy
        response = requests.get('https://staging.example.com/health')
        assert response.status_code == 200

        print(f"✓ Rollback completed in {rollback_time:.1f}s")

        return {
            'test': 'application_rollback',
            'rollback_time_seconds': rollback_time,
            'target_seconds': 300,  # 5 minutes
            'passed': rollback_time < 300
        }

    def test_database_restore(self):
        """Test database backup restore."""
        print("=== Testing Database Restore ===")

        # Get latest backup
        latest_backup = self._get_latest_backup()
        print(f"Latest backup: {latest_backup}")

        # Restore to test database
        start_time = time.time()
        subprocess.run([
            './db-restore.sh',
            latest_backup,
            'rollback_test'
        ], check=True)
        restore_time = time.time() - start_time

        # Validate data
        result = subprocess.run([
            'psql', '-d', 'rollback_test',
            '-t', '-c', 'SELECT COUNT(*) FROM users;'
        ], capture_output=True, text=True)
        user_count = int(result.stdout.strip())

        assert user_count > 0

        print(f"✓ Restore completed in {restore_time:.1f}s")
        print(f"  User records: {user_count}")

        # Cleanup
        subprocess.run(['psql', '-c', 'DROP DATABASE rollback_test;'])

        return {
            'test': 'database_restore',
            'restore_time_seconds': restore_time,
            'target_seconds': 3600,  # 1 hour
            'passed': restore_time < 3600
        }

    def test_feature_flag_rollback(self):
        """Test feature flag instant rollback."""
        print("=== Testing Feature Flag Rollback ===")

        # Enable test flag
        enable_feature_flag('test-rollback-flag', percentage=100)
        time.sleep(5)

        # Trigger rollback
        start_time = time.time()
        disable_feature_flag('test-rollback-flag', reason='Rollback test')
        rollback_time = time.time() - start_time

        # Verify flag disabled
        flag_state = get_feature_flag_state('test-rollback-flag')
        assert flag_state['enabled'] == False

        print(f"✓ Feature flag rollback completed in {rollback_time:.1f}s")

        return {
            'test': 'feature_flag_rollback',
            'rollback_time_seconds': rollback_time,
            'target_seconds': 10,  # Instant (<10s)
            'passed': rollback_time < 10
        }

    def run_all_tests(self):
        """Run all rollback tests and generate report."""
        results = []

        results.append(self.test_application_rollback())
        results.append(self.test_database_restore())
        results.append(self.test_feature_flag_rollback())

        # Generate report
        print("\n=== Rollback Test Report ===")
        all_passed = True
        for result in results:
            status = "✓ PASS" if result['passed'] else "✗ FAIL"
            print(f"{result['test']}: {status} ({result['rollback_time_seconds']:.1f}s / {result['target_seconds']}s target)")
            all_passed = all_passed and result['passed']

        if all_passed:
            print("\n✓ All rollback tests passed")
        else:
            print("\n✗ Some rollback tests failed - review procedures")

        return results

# Run monthly
if __name__ == '__main__':
    tester = RollbackTester()
    results = tester.run_all_tests()
```

---

## 5. Communication During Rollback

### 5.1 Incident Communication Protocol

**Communication Checklist:**
```markdown
# Rollback Communication Protocol

## Immediate (Within 5 minutes)
- [ ] Update status page: "Investigating issue"
- [ ] Post in #incidents Slack channel
- [ ] Notify on-call team via PagerDuty

## During Rollback (Every 15 minutes)
- [ ] Status page updates with progress
- [ ] Slack updates in #incidents
- [ ] If >30 minutes, email stakeholders

## Post-Rollback (Within 1 hour)
- [ ] Status page: "Resolved"
- [ ] Slack: Summary of issue and resolution
- [ ] Email affected users (if necessary)

## Post-Mortem (Within 48 hours)
- [ ] Schedule post-mortem meeting
- [ ] Document timeline of events
- [ ] Identify root cause
- [ ] Define action items to prevent recurrence
```

**Status Page Updates:**
```python
# Update status page during rollback
import requests

STATUSPAGE_API_KEY = os.getenv('STATUSPAGE_API_KEY')
STATUSPAGE_PAGE_ID = 'your-page-id'

def update_incident_status(incident_id, status, message):
    """Update incident status on status page.

    Args:
        incident_id: Incident identifier
        status: 'investigating', 'identified', 'monitoring', 'resolved'
        message: Status update message
    """
    url = f"https://api.statuspage.io/v1/pages/{STATUSPAGE_PAGE_ID}/incidents/{incident_id}"

    response = requests.patch(url, headers={
        'Authorization': f'OAuth {STATUSPAGE_API_KEY}',
    }, json={
        'incident': {
            'status': status,
            'body': message
        }
    })

    return response.json()

# Example: Rollback communication flow
incident_id = create_incident(
    name='API Performance Degradation',
    status='investigating',
    impact='major',
    body='We are investigating reports of slow API response times.'
)

# During rollback
update_incident_status(
    incident_id,
    status='identified',
    message='Issue identified: recent deployment causing high error rate. Rolling back deployment.'
)

# After rollback
update_incident_status(
    incident_id,
    status='monitoring',
    message='Rollback completed. Monitoring system stability.'
)

# 1 hour later
update_incident_status(
    incident_id,
    status='resolved',
    message='System fully recovered. Error rates returned to normal. Post-mortem will be published within 48 hours.'
)
```

---

## Summary: Rollback & Recovery Best Practices

**Key Takeaways:**

1. **Rollback First, Debug Later:** Restore service immediately, investigate after
2. **Test Rollback Procedures:** Monthly drills ensure procedures work under pressure
3. **Automate When Possible:** Manual rollback is error-prone during incidents
4. **Backward-Compatible Migrations:** Database rollback requires forward-compatible changes
5. **Communicate Proactively:** Keep users and stakeholders informed throughout

**Rollback Time Targets:**

| Scale | RTO Target | Rollback Method |
|-------|-----------|-----------------|
| Small | 15 minutes | Git revert + redeploy |
| Medium | 5 minutes | Kubernetes rollout undo or feature flag disable |
| Large | <5 minutes | Blue-green swap or multi-region failover |

**Monthly Checklist:**
- [ ] Test application rollback in staging
- [ ] Test database backup restore
- [ ] Verify feature flag instant disable works
- [ ] Review and update runbooks
- [ ] Measure and track MTTR (Mean Time To Recovery)

---

**Guide Version:** 1.0
**Last Updated:** 2025-10-27
**Related:** [MEDIUM_SCALE_READINESS.md](MEDIUM_SCALE_READINESS.md), [LARGE_SCALE_READINESS.md](LARGE_SCALE_READINESS.md)
