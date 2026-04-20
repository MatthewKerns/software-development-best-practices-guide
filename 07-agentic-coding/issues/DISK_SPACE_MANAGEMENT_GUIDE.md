# Disk Space Management Guide for Development Environments

**Last Updated:** November 20, 2025
**Context:** Based on real-world investigation of 147GB disk space recovery after macOS restart

## Executive Summary

Development environments accumulate massive amounts of temporary files, caches, and artifacts that can fill disks to 100% capacity. This guide documents:
- **What causes disk space exhaustion** (with evidence from 147GB recovery case study)
- **Why macOS restarts free so much space** (automatic cleanup mechanisms)
- **How to prevent disk space issues** (proactive monitoring and cleanup)
- **What data to collect** for future troubleshooting

## Table of Contents

1. [Case Study: 147GB Recovery](#case-study-147gb-recovery)
2. [Primary Disk Space Culprits](#primary-disk-space-culprits)
3. [Why macOS Restart Frees Space](#why-macos-restart-frees-space)
4. [Monitoring and Detection](#monitoring-and-detection)
5. [Preventive Maintenance](#preventive-maintenance)
6. [Emergency Cleanup Procedures](#emergency-cleanup-procedures)
7. [Claude Code Specific Issues](#claude-code-specific-issues)
8. [Docker Best Practices](#docker-best-practices)
9. [Automation Scripts](#automation-scripts)

---

## Case Study: 147GB Recovery

### The Incident

**Timeline:**
- **Before Restart:** 408GB used / 460GB total (968MB free, 100% full)
- **After Restart:** 261GB used / 460GB total (181GB free, 60% capacity)
- **Total Recovered:** 147GB in disk space

### What Was Cleaned

Based on forensic analysis and macOS behavior patterns:

| Source | Estimated Size | Mechanism |
|--------|---------------|-----------|
| Time Machine Local Snapshots | 80-100GB | Auto-purged when <10GB free |
| Docker.raw Sparse File Compaction | 20-30GB | Clean shutdown compacts file |
| Chrome Testing Artifacts (Claude Code bug) | 10-20GB | `/var/folders/` cleanup on restart |
| VM Swap Files | 5-10GB | Multiple swap files deleted |
| System Caches (`/var/folders/`) | 5-10GB | Temp files purged |
| Application Temp Files | 2-5GB | Various app caches cleared |

### Evidence

**Before Restart:**
```bash
Filesystem      Size    Used   Avail Capacity
/dev/disk3s5   460Gi   408Gi   968Mi   100%
```

**After Restart + Docker Cleanup:**
```bash
Filesystem      Size    Used   Avail Capacity
/dev/disk3s5   460Gi   261Gi   181Gi    60%
```

**Current State (Post-Cleanup Baseline):**
- Docker.raw: 64GB (capacity), 566MB actual usage
- `/var/folders/`: 4.2GB (mostly temp caches)
- Time Machine snapshots: 0 (purged)
- VM swap: 1GB sleepimage
- Application caches: 4.8GB total

---

## Primary Disk Space Culprits

### 1. Time Machine Local Snapshots (Highest Impact: 50-150GB)

**What:** macOS creates local snapshots of your files for Time Machine backups, even without an external drive connected.

**Why It Grows:**
- Snapshots created hourly during active work
- Can accumulate 100GB+ if backups aren't happening
- Hidden from Finder and standard `du` commands

**Detection:**
```bash
tmutil listlocalsnapshots /
```

**Cleanup:**
```bash
# macOS automatically purges when disk space critical (<10GB free)
# Manual deletion (not recommended - let macOS handle it):
tmutil deletelocalsnapshots [snapshot-date]
```

**Automatic Cleanup Trigger:**
- macOS purges ALL snapshots when available space < 10GB
- Happens automatically during restart when disk critically low
- **This is likely the biggest contributor to the 147GB recovery**

### 2. Docker.raw Sparse File (High Impact: 10-50GB)

**What:** Docker Desktop on macOS uses a sparse disk image (`Docker.raw`) that grows but doesn't shrink automatically.

**Current Setup:**
- **Location:** `~/Library/Containers/com.docker.docker/Data/vms/0/data/Docker.raw`
- **Capacity:** 64GB (maximum size)
- **Actual Usage:** Varies based on images/containers/volumes
- **Problem:** File grows with usage but rarely shrinks

**Why It Grows:**
- Every Docker image layer adds data
- Deleted containers/volumes leave "holes" in the file
- Build caches accumulate over time
- **Sparse file shows large size but actual disk usage hidden**

**Detection:**
```bash
# Check Docker disk usage
docker system df

# Check Docker.raw file
ls -lh ~/Library/Containers/com.docker.docker/Data/vms/0/data/Docker.raw
du -sh ~/Library/Containers/com.docker.docker/Data
```

**Cleanup:**
```bash
# Remove all unused Docker data (RECOMMENDED)
docker system prune -af --volumes

# Or clean selectively
docker system prune -a        # Remove unused images/containers
docker volume prune           # Remove unused volumes
docker builder prune          # Remove build cache
```

**Automatic Cleanup on Restart:**
- Docker daemon shuts down cleanly
- Sparse file gets compacted (removes empty "holes")
- Can recover 10-30GB depending on usage patterns
- **Estimated 20-30GB recovery in the 147GB case**

### 3. Chrome Testing Artifacts - Claude Code Bug (High Impact: 5-200GB!)

**What:** Claude Code has a known memory leak bug ([Issue #10107](https://github.com/anthropics/claude-code/issues/10107)) where browser testing creates Chrome copies in `/var/folders/` that are never deleted.

**Severity:** CRITICAL - Can consume up to 300GB if left unchecked

**Location:**
- `/private/var/folders/[random]/com.google.Chrome.code_sign_clone/`
- `/private/var/folders/[random]/T/.com.google.Chrome.*`
- `/private/var/folders/[random]/C/com.google.Chrome.*`

**Detection:**
```bash
# Find Chrome artifacts in temp folders
find /private/var/folders -name "*Chrome*" 2>/dev/null | xargs du -sh 2>/dev/null

# Check total /var/folders size
du -sh /private/var/folders/*
```

**Current State (After Restart):**
```
102M  /private/var/folders/.../C/com.google.Chrome.helper
248K  /private/var/folders/.../C/com.google.Chrome
```

**Cleanup:**
- Restart macOS (clears /var/folders)
- Or manually: `rm -rf /private/var/folders/*/com.google.Chrome*` (risky, requires sudo)

**Estimated Recovery:** 10-20GB in the 147GB case (could be much higher with prolonged usage)

### 4. VM Swap Files (Medium Impact: 5-20GB)

**What:** macOS creates swap files in `/private/var/vm/` when RAM is full.

**Location:** `/private/var/vm/swapfile[0-9]` and `sleepimage`

**Current State:**
```bash
$ ls -lh /private/var/vm/
-rw------T  1 root  wheel   1.0G sleepimage
```

**Why It Grows:**
- Multiple swap files can accumulate during heavy usage
- Each can be 1-2GB
- `sleepimage` = hibernation file (size of installed RAM)

**Cleanup:**
- Restart clears all swap files except sleepimage
- sleepimage persists but gets recreated
- **No manual cleanup recommended**

**Estimated Recovery:** 5-10GB in the 147GB case

### 5. System Caches in /var/folders (Medium Impact: 2-10GB)

**What:** macOS temp directory for per-user application caches.

**Structure:**
- `/private/var/folders/[random]/C/` - Cache files
- `/private/var/folders/[random]/T/` - Temporary files
- `/private/var/folders/[random]/0/` - User data

**Current State:** 4.2GB total after restart

**Cleanup:**
- Restart triggers automatic cleanup
- Safe Mode triggers aggressive cleanup
- Manual: Not recommended (risk breaking apps)

**Estimated Recovery:** 5-10GB in the 147GB case

### 6. Application Caches (Medium Impact: 2-10GB)

**Location:** `~/Library/Caches/`

**Top Offenders:**
```
2.5GB  ~/Library/Caches/Google (Chrome)
1.1GB  ~/Library/Caches/aws (AWS CLI)
640MB  ~/Library/Caches/com.microsoft.VSCode.ShipIt
566MB  ~/Library/Caches/ms-playwright
```

**Cleanup:**
```bash
# Safe - apps will rebuild caches
rm -rf ~/Library/Caches/Google/Chrome
rm -rf ~/Library/Caches/aws
rm -rf ~/Library/Caches/com.microsoft.VSCode.ShipIt
```

**Estimated Recovery:** 2-5GB in the 147GB case

### 7. Project Build Artifacts (Low-Medium Impact: 1-5GB)

**AWS SAM Build Cache:**
- **Location:** `aws-infrastructure/backend/.aws-sam/`
- **Current Size:** 1.2GB
- **Safe to Delete:** Yes (rebuilds on next `sam build`)

**Frontend node_modules:**
- **Location:** `frontend/invoice-review/node_modules/`
- **Current Size:** 590MB
- **Safe to Delete:** Yes (run `npm install` to rebuild)

**Python Cache:**
- `__pycache__/` directories
- `.pytest_cache/` directories
- `*.pyc` files

**Cleanup:**
```bash
# AWS SAM cache
rm -rf aws-infrastructure/backend/.aws-sam/

# Python caches
find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null
find . -type d -name ".pytest_cache" -exec rm -rf {} + 2>/dev/null
find . -name "*.pyc" -delete 2>/dev/null

# node_modules (only if needed)
rm -rf frontend/invoice-review/node_modules/
cd frontend/invoice-review && npm install
```

---

## Why macOS Restart Frees Space

### Automatic Cleanup Mechanisms

When macOS restarts, several cleanup processes run automatically:

#### 1. **Time Machine Snapshot Purge (Biggest Impact)**
**When:** During boot if available space < 10GB
**What:** Deletes ALL local Time Machine snapshots
**Recovery:** 50-150GB typical

**Evidence:**
```bash
# Before restart: Unknown (not captured)
# After restart:
$ tmutil listlocalsnapshots /
Snapshots for disk /:
(empty)
```

#### 2. **`/var/folders/` Cleanup**
**When:** Every restart
**What:** Deletes temp files older than 3 days or if disk critically low
**Recovery:** 5-20GB typical

**How It Works:**
- macOS runs `periodic daily` scripts on boot
- Cleans `/private/var/folders/*/T/` temp files
- Removes Chrome artifacts, app temp files, etc.

#### 3. **Docker.raw Sparse File Compaction**
**When:** Docker daemon clean shutdown/restart
**What:** Compacts sparse file by removing empty space
**Recovery:** 10-30GB typical

**How It Works:**
- Docker Desktop shuts down cleanly
- QEMU compacts the sparse disk image
- Empty blocks removed from file system

#### 4. **VM Swap File Cleanup**
**When:** Every restart
**What:** Deletes all `swapfile[0-9]` files
**Recovery:** 5-20GB typical

**How It Works:**
- Swap files in `/private/var/vm/` deleted on shutdown
- Fresh swap files created on next boot
- Only `sleepimage` persists

#### 5. **Application Cache Pruning**
**When:** Apps restart after reboot
**What:** Apps clear stale caches, logs, temp files
**Recovery:** 2-5GB typical

### Why Restart is So Effective

**Cascading Cleanup:**
1. Low disk space triggers aggressive cleanup
2. Time Machine purges all snapshots (50-150GB)
3. `/var/folders/` cleanup runs (5-20GB)
4. Docker compacts on clean shutdown (10-30GB)
5. VM swap files deleted (5-20GB)
6. Apps clear caches on restart (2-5GB)

**Total Possible Recovery:** 72-225GB (our case: 147GB)

---

## Monitoring and Detection

### Real-Time Monitoring

#### 1. **Disk Space Snapshot Tool**

Use the snapshot tool to capture state BEFORE and AFTER incidents:

```bash
# Create snapshot tool
cat > ~/bin/disk-snapshot << 'EOF'
#!/bin/bash
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
OUTPUT="$HOME/disk_snapshot_${TIMESTAMP}.txt"

echo "=== DISK SNAPSHOT - $TIMESTAMP ===" | tee "$OUTPUT"
df -h / | tee -a "$OUTPUT"
docker system df 2>/dev/null | tee -a "$OUTPUT"
tmutil listlocalsnapshots / | wc -l | tee -a "$OUTPUT"
du -sh /private/var/folders/* 2>/dev/null | sort -h | tail -5 | tee -a "$OUTPUT"
du -sh ~/Library/Caches/* 2>/dev/null | sort -h | tail -10 | tee -a "$OUTPUT"
echo "Saved to: $OUTPUT"
EOF

chmod +x ~/bin/disk-snapshot
```

**Usage:**
```bash
# When disk space is low:
~/bin/disk-snapshot

# Restart your Mac

# After restart:
~/bin/disk-snapshot

# Compare the two files to see what was cleaned
diff ~/disk_snapshot_[before].txt ~/disk_snapshot_[after].txt
```

#### 2. **Daily Space Check Alias**

Add to `~/.zshrc`:

```bash
# Quick disk space check
alias disk-check='df -h / && echo "---" && docker system df && echo "---" && tmutil listlocalsnapshots / | wc -l && echo "TM snapshots"'
```

#### 3. **Automated Monitoring Script**

```bash
# Add to crontab for daily checks at 9 AM:
# crontab -e
# 0 9 * * * /Users/[you]/bin/disk-monitor.sh

cat > ~/bin/disk-monitor.sh << 'EOF'
#!/bin/bash
THRESHOLD=20  # Alert if less than 20GB free

AVAIL=$(df -h / | tail -1 | awk '{print $4}' | sed 's/Gi//')

if [ "$AVAIL" -lt "$THRESHOLD" ]; then
    echo "⚠️ Low disk space: ${AVAIL}GB available"
    # Add notification or alert here
fi
EOF

chmod +x ~/bin/disk-monitor.sh
```

### What Data to Collect Next Time

When disk space gets critically low, capture this data BEFORE restarting:

```bash
# Full snapshot (run this immediately when disk is low)
~/bin/disk-snapshot

# Key data points:
df -h /                              # Overall disk usage
docker system df                     # Docker breakdown
tmutil listlocalsnapshots /          # TM snapshots (likely culprit)
ls -lh /private/var/vm/              # Swap files
du -sh /private/var/folders/*        # Temp files
find /private/var/folders -name "*Chrome*" | xargs du -sh  # Chrome artifacts
du -sh ~/Library/Caches/*            # App caches
```

**Save output to file for analysis after restart!**

---

## Preventive Maintenance

### Daily (30 seconds)

**After Docker Development Sessions:**

```bash
# Clean Docker immediately after work
docker system prune -af --volumes
```

**Why:** Prevents Docker.raw from growing uncontrollably. Running this daily can prevent 10-20GB accumulation.

### Weekly (2 minutes)

**Full Development Environment Cleanup:**

```bash
# Create weekly cleanup alias
cat >> ~/.zshrc << 'EOF'
alias dev-clean='echo "🧹 Cleaning dev environment..." && \
  docker system prune -af --volumes && \
  rm -rf ~/workspace/*/aws-infrastructure/backend/.aws-sam/ 2>/dev/null && \
  find ~/workspace -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null && \
  find ~/workspace -type d -name ".pytest_cache" -exec rm -rf {} + 2>/dev/null && \
  echo "✅ Dev environment cleaned!"'
EOF
```

**Usage:** Run `dev-clean` every Friday

**Expected Recovery:** 2-5GB per week

### Monthly (5 minutes)

**Deep Clean Application Caches:**

```bash
cat >> ~/.zshrc << 'EOF'
alias deep-clean='echo "🧹 Deep cleaning caches..." && \
  docker system prune -af --volumes && \
  rm -rf ~/Library/Caches/Google/Chrome && \
  rm -rf ~/Library/Caches/aws && \
  rm -rf ~/Library/Caches/ms-playwright && \
  rm -rf ~/Library/Caches/com.microsoft.VSCode.ShipIt && \
  find ~/workspace -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null && \
  find ~/workspace -type d -name "node_modules" -type d -mtime +30 -exec rm -rf {} + 2>/dev/null && \
  echo "✅ Deep clean complete!"'
EOF
```

**Usage:** Run `deep-clean` monthly

**Expected Recovery:** 5-10GB

### When to Restart vs Clean

**Run Cleanup Scripts When:**
- Available space drops below 50GB
- After heavy Docker development (multiple builds/tests)
- Weekly as preventive maintenance
- Before major deployments

**Restart Mac When:**
- Available space below 10GB despite cleanup
- Claude Code becomes sluggish (memory leak symptoms)
- After 1-2 weeks of continuous development
- When `/var/folders/` exceeds 10GB
- When Time Machine snapshots accumulate (check with `tmutil listlocalsnapshots /`)

**Safe Mode Restart When:**
- Normal restart doesn't free enough space
- Suspecting corrupted caches
- Need aggressive cleanup

**How to Boot Safe Mode:**
1. Shut down Mac
2. Press power button
3. Hold Shift immediately until login window
4. macOS performs aggressive cache cleanup
5. Reboot normally after

---

## Emergency Cleanup Procedures

### When Disk is 100% Full

**Priority Order (Highest Impact First):**

#### 1. Delete Time Machine Snapshots (50-150GB)
```bash
# List snapshots
tmutil listlocalsnapshots /

# Delete all (macOS will recreate as needed)
for snapshot in $(tmutil listlocalsnapshots / | grep "com.apple" | cut -d. -f4-); do
    sudo tmutil deletelocalsnapshots "$snapshot"
done
```

#### 2. Clean Docker (10-50GB)
```bash
docker system prune -af --volumes
```

#### 3. Clear Chrome Cache (2-5GB)
```bash
rm -rf ~/Library/Caches/Google/Chrome
```

#### 4. Delete AWS SAM Cache (1-2GB)
```bash
rm -rf ~/workspace/*/aws-infrastructure/backend/.aws-sam/
```

#### 5. Clear Application Caches (2-5GB)
```bash
rm -rf ~/Library/Caches/aws
rm -rf ~/Library/Caches/com.microsoft.VSCode.ShipIt
rm -rf ~/Library/Caches/ms-playwright
```

#### 6. Python Cache Cleanup (100-500MB)
```bash
find ~/workspace -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null
find ~/workspace -type d -name ".pytest_cache" -exec rm -rf {} + 2>/dev/null
find ~/workspace -name "*.pyc" -delete 2>/dev/null
```

#### 7. Last Resort - Restart Mac
If still critically low, restart to trigger all automatic cleanup mechanisms.

---

## Claude Code Specific Issues

### Known Bugs Affecting Disk Space

#### 1. Chrome Testing Memory Leak ([Issue #10107](https://github.com/anthropics/claude-code/issues/10107))

**Severity:** CRITICAL
**Impact:** Can consume 300GB over time
**Status:** Known issue, no fix yet

**What Happens:**
- Claude Code tests UI in Chrome browser
- Creates Chrome copies in `/var/folders/`
- Never deletes them
- Accumulates indefinitely

**Detection:**
```bash
find /private/var/folders -name "*Chrome*" -type d 2>/dev/null | xargs du -sh
```

**Workaround:**
- Restart Mac weekly when doing heavy UI development
- Monitor `/var/folders/` size
- Report large Chrome directories immediately

#### 2. Working Directory Tracking Files ([Issue #8856](https://github.com/anthropics/claude-code/issues/8856))

**Severity:** MEDIUM
**Impact:** 174 files per day reported
**Status:** One-line fix available, pending release

**What Happens:**
- Creates `/tmp/claude-*-cwd` files for Bash working directory tracking
- Never deletes them
- Accumulates over time

**Detection:**
```bash
find /tmp -name "claude-*-cwd" -type f | wc -l
```

**Workaround:**
```bash
# Clean up manually
find /tmp -name "claude-*-cwd" -type f -delete
```

**Current Status:** 0 files (after restart) - this issue wasn't contributing to the 147GB

#### 3. Memory Leak ([Issue #4953](https://github.com/anthropics/claude-code/issues/4953))

**Severity:** HIGH
**Impact:** Process grows to 120GB+ RAM
**Status:** Ongoing issue since July 2024

**Symptoms:**
- Claude Code process consumes increasing memory
- Mac becomes sluggish
- Eventually triggers swap usage (contributes to disk space)

**Workaround:**
- Use `/clear` command every 40 messages
- Restart Claude Code daily
- Keep CLAUDE.md files under 5KB (yours is 48KB - acceptable)

#### 4. Ripgrep Cache Accumulation ([Issue #6092](https://github.com/anthropics/claude-code/issues/6092))

**Severity:** LOW
**Impact:** ~150MB per Claude Code update
**Status:** Known issue

**What Happens:**
- Every Claude Code update packages ripgrep (~150MB)
- Cached in Bun's global cache per version
- Multiple versions accumulate

**Detection:**
```bash
du -sh ~/.bun/install/cache/
```

**Workaround:**
```bash
# Clear Bun cache periodically
rm -rf ~/.bun/install/cache/
```

### Best Practices for Claude Code

**To Minimize Disk Impact:**

1. **Use `/clear` every 40 messages** (prevents memory leak)
2. **Restart Claude Code daily** during heavy development
3. **Monitor `/var/folders/` weekly** for Chrome artifacts
4. **Keep CLAUDE.md under 5KB** (current: 48KB is OK)
5. **Restart Mac weekly** if doing UI testing (Chrome bug)
6. **Report anomalies** to Claude Code GitHub issues

---

## Docker Best Practices

### Disk Space Management

#### 1. Clean After Every Build Session

```bash
# Immediately after docker-compose down or testing
docker system prune -af --volumes
```

**Why:** Prevents Docker.raw from accumulating deleted containers/layers

#### 2. Monitor Docker Disk Usage

```bash
# Check regularly
docker system df

# Output:
TYPE            TOTAL     ACTIVE    SIZE      RECLAIMABLE
Images          5         2         15.39GB   12.56GB (81%)
Containers      2         0         98.3kB    98.3kB (100%)
Local Volumes   13        1         2.364GB   2.363GB (99%)
Build Cache     41        0         2.383GB   2.383GB
```

**Red Flags:**
- Reclaimable > 50% of SIZE
- Build Cache > 2GB
- Inactive containers exist

#### 3. Selective Cleanup (When Needed)

```bash
# Remove only stopped containers
docker container prune

# Remove unused images
docker image prune -a

# Remove unused volumes
docker volume prune

# Remove build cache
docker builder prune
```

#### 4. Docker Desktop Settings

**Recommended Configuration:**

1. Open Docker Desktop → Settings → Resources
2. Set Disk Image Size: **64GB** (current setting)
3. Consider **32GB** if not running many containers
4. Enable **VirtioFS** for better performance

### Docker.raw File Management

**Understanding Sparse Files:**

```bash
# File size (maximum capacity)
ls -lh ~/Library/Containers/com.docker.docker/Data/vms/0/data/Docker.raw
# Output: 64GB

# Actual disk usage (real space consumed)
du -sh ~/Library/Containers/com.docker.docker/Data/
# Output: 566MB (after cleanup)
```

**When Docker.raw Grows:**
- Building images (each layer adds data)
- Pulling images from registries
- Creating containers/volumes
- Build cache accumulation

**When Docker.raw Should Shrink (But Doesn't):**
- Deleting containers/images/volumes
- **Problem:** Sparse file has "holes" but doesn't automatically compact

**Forcing Compaction:**
1. Clean Docker data: `docker system prune -af --volumes`
2. Restart Docker Desktop (Docker → Quit Docker Desktop → Start)
3. OR restart Mac (triggers clean shutdown/compaction)

### Docker Compose Best Practices

**Project Setup:**

```yaml
# docker-compose.yml
version: '3.8'

services:
  backend:
    build: ./backend
    volumes:
      - ./backend:/app  # Bind mount for development
      # DON'T create unnecessary volumes

  # At the end of file
volumes:
  # Only named volumes you actually need
  postgres_data:
```

**Cleanup Commands:**

```bash
# Stop and remove containers/networks
./scripts/dev.sh down

# Remove volumes too (careful - deletes data!)
docker-compose down -v

# Rebuild from scratch
docker-compose build --no-cache
```

---

## Automation Scripts

### Complete Disk Management Script

```bash
# Create comprehensive disk management tool
cat > ~/bin/disk-manager << 'EOF'
#!/bin/bash

# Disk Space Management Tool
# Combines monitoring, cleanup, and reporting

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Configuration
CRITICAL_THRESHOLD=10  # GB
WARNING_THRESHOLD=50   # GB
SNAPSHOT_DIR="$HOME/disk_snapshots"

# Create snapshot directory
mkdir -p "$SNAPSHOT_DIR"

# Functions
check_disk_space() {
    echo -e "${YELLOW}=== Disk Space Check ===${NC}"
    df -h / | tail -1

    AVAIL=$(df -h / | tail -1 | awk '{print $4}' | sed 's/Gi//')

    if [ "$AVAIL" -lt "$CRITICAL_THRESHOLD" ]; then
        echo -e "${RED}⚠️  CRITICAL: Only ${AVAIL}GB available!${NC}"
        return 2
    elif [ "$AVAIL" -lt "$WARNING_THRESHOLD" ]; then
        echo -e "${YELLOW}⚠️  WARNING: Only ${AVAIL}GB available${NC}"
        return 1
    else
        echo -e "${GREEN}✓ OK: ${AVAIL}GB available${NC}"
        return 0
    fi
}

take_snapshot() {
    TIMESTAMP=$(date +%Y%m%d_%H%M%S)
    OUTPUT="${SNAPSHOT_DIR}/snapshot_${TIMESTAMP}.txt"

    echo "Taking disk snapshot..." | tee "$OUTPUT"

    echo "=== Overall Disk Usage ===" | tee -a "$OUTPUT"
    df -h / | tee -a "$OUTPUT"
    echo "" | tee -a "$OUTPUT"

    echo "=== Docker Usage ===" | tee -a "$OUTPUT"
    docker system df 2>/dev/null | tee -a "$OUTPUT" || echo "Docker not running" | tee -a "$OUTPUT"
    echo "" | tee -a "$OUTPUT"

    echo "=== Time Machine Snapshots ===" | tee -a "$OUTPUT"
    echo "Count: $(tmutil listlocalsnapshots / 2>/dev/null | wc -l)" | tee -a "$OUTPUT"
    echo "" | tee -a "$OUTPUT"

    echo "=== /var/folders Size ===" | tee -a "$OUTPUT"
    du -sh /private/var/folders/* 2>/dev/null | sort -h | tail -5 | tee -a "$OUTPUT"
    echo "" | tee -a "$OUTPUT"

    echo "=== Application Caches (Top 5) ===" | tee -a "$OUTPUT"
    du -sh ~/Library/Caches/* 2>/dev/null | sort -h | tail -5 | tee -a "$OUTPUT"
    echo "" | tee -a "$OUTPUT"

    echo -e "${GREEN}Snapshot saved: $OUTPUT${NC}"
}

quick_clean() {
    echo -e "${YELLOW}=== Quick Cleanup ===${NC}"

    echo "Cleaning Docker..."
    docker system prune -af --volumes 2>/dev/null || echo "Docker not running"

    echo "Cleaning Python caches..."
    find ~/workspace -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null
    find ~/workspace -type d -name ".pytest_cache" -exec rm -rf {} + 2>/dev/null

    echo "Cleaning AWS SAM cache..."
    rm -rf ~/workspace/*/aws-infrastructure/backend/.aws-sam/ 2>/dev/null

    echo -e "${GREEN}✓ Quick cleanup complete${NC}"
}

deep_clean() {
    echo -e "${YELLOW}=== Deep Cleanup ===${NC}"

    quick_clean

    echo "Cleaning Chrome cache..."
    rm -rf ~/Library/Caches/Google/Chrome 2>/dev/null

    echo "Cleaning AWS CLI cache..."
    rm -rf ~/Library/Caches/aws 2>/dev/null

    echo "Cleaning VSCode cache..."
    rm -rf ~/Library/Caches/com.microsoft.VSCode.ShipIt 2>/dev/null

    echo "Cleaning Playwright cache..."
    rm -rf ~/Library/Caches/ms-playwright 2>/dev/null

    echo -e "${GREEN}✓ Deep cleanup complete${NC}"
}

emergency_clean() {
    echo -e "${RED}=== EMERGENCY CLEANUP ===${NC}"

    # Take snapshot first
    take_snapshot

    deep_clean

    echo "Checking Time Machine snapshots..."
    SNAPSHOT_COUNT=$(tmutil listlocalsnapshots / 2>/dev/null | wc -l)
    if [ "$SNAPSHOT_COUNT" -gt 0 ]; then
        echo "Found $SNAPSHOT_COUNT Time Machine snapshots"
        echo "Deleting snapshots (requires sudo)..."
        for snapshot in $(tmutil listlocalsnapshots / | grep "com.apple" | cut -d. -f4-); do
            sudo tmutil deletelocalsnapshots "$snapshot" 2>/dev/null
        done
    fi

    echo -e "${GREEN}✓ Emergency cleanup complete${NC}"
    echo -e "${YELLOW}Consider restarting your Mac for maximum recovery${NC}"
}

# Main menu
case "${1:-check}" in
    check)
        check_disk_space
        ;;
    snapshot)
        take_snapshot
        ;;
    quick)
        check_disk_space
        quick_clean
        check_disk_space
        ;;
    deep)
        check_disk_space
        deep_clean
        check_disk_space
        ;;
    emergency)
        check_disk_space
        emergency_clean
        check_disk_space
        ;;
    *)
        echo "Usage: $0 {check|snapshot|quick|deep|emergency}"
        echo ""
        echo "Commands:"
        echo "  check     - Check current disk space"
        echo "  snapshot  - Take detailed snapshot for comparison"
        echo "  quick     - Quick cleanup (Docker, Python caches, AWS SAM)"
        echo "  deep      - Deep cleanup (includes application caches)"
        echo "  emergency - Emergency cleanup (includes Time Machine snapshots)"
        exit 1
        ;;
esac
EOF

chmod +x ~/bin/disk-manager
```

**Usage:**

```bash
# Check disk space
disk-manager check

# Take snapshot before restart
disk-manager snapshot

# Quick cleanup (daily/weekly)
disk-manager quick

# Deep cleanup (monthly)
disk-manager deep

# Emergency (when disk is critically low)
disk-manager emergency
```

### Automated Monitoring with Notifications

```bash
# Add to crontab: crontab -e
# Check disk space every hour and alert if low
0 * * * * ~/bin/disk-alert.sh

# Create alert script
cat > ~/bin/disk-alert.sh << 'EOF'
#!/bin/bash
THRESHOLD=20  # Alert if less than 20GB

AVAIL=$(df -h / | tail -1 | awk '{print $4}' | sed 's/Gi//')

if [ "$AVAIL" -lt "$THRESHOLD" ]; then
    # macOS notification
    osascript -e "display notification \"Only ${AVAIL}GB available\" with title \"Low Disk Space Warning\""

    # Optional: Send email or Slack notification
    # curl -X POST -H 'Content-type: application/json' \
    #   --data "{\"text\":\"Low disk space: ${AVAIL}GB available\"}" \
    #   YOUR_SLACK_WEBHOOK_URL
fi
EOF

chmod +x ~/bin/disk-alert.sh
```

---

## Summary of Best Practices

### Daily
- ✅ Run `docker system prune -af --volumes` after Docker work
- ✅ Use `/clear` in Claude Code every 40 messages
- ✅ Check disk space: `df -h /`

### Weekly
- ✅ Run `disk-manager quick` cleanup
- ✅ Check `/var/folders/` size for Chrome artifacts
- ✅ Restart Mac if doing heavy UI development (Claude Code Chrome bug)

### Monthly
- ✅ Run `disk-manager deep` cleanup
- ✅ Check Time Machine snapshots: `tmutil listlocalsnapshots /`
- ✅ Review project build artifacts (node_modules, .aws-sam, etc.)

### When Disk Space Low
1. Run `disk-manager snapshot` to capture state
2. Run `disk-manager emergency` for aggressive cleanup
3. If still low: Restart Mac to trigger all automatic cleanup
4. After restart: Run `disk-manager snapshot` to compare

### Next Time This Happens
1. **BEFORE restarting:** Run `disk-manager snapshot`
2. **Restart Mac**
3. **AFTER restarting:** Run `disk-manager snapshot`
4. **Compare snapshots:** `diff ~/disk_snapshots/snapshot_*.txt`
5. **Document findings:** Update this guide with new data

---

## References

### Claude Code Issues
- [Issue #10107](https://github.com/anthropics/claude-code/issues/10107) - Chrome testing memory leak (300GB!)
- [Issue #8856](https://github.com/anthropics/claude-code/issues/8856) - Working directory tracking files
- [Issue #4953](https://github.com/anthropics/claude-code/issues/4953) - Memory leak (120GB RAM)
- [Issue #6092](https://github.com/anthropics/claude-code/issues/6092) - Ripgrep cache accumulation

### Docker Resources
- [Docker Disk Space Docs](https://docs.docker.com/desktop/faqs/macfaqs/#where-does-docker-desktop-store-docker-images)
- [Reclaim Docker Space](https://medium.com/@alexeysamoshkin/reclaim-disk-space-by-removing-stale-and-unused-docker-data-a4c3bd1e4001)

### macOS Resources
- [Time Machine Local Snapshots](https://support.apple.com/guide/mac-help/what-are-local-snapshots-mh35873/mac)
- [/var/folders Explanation](https://magnusviri.com/what-is-var-folders.html)

---

## Changelog

**2025-11-20:** Initial guide created based on 147GB recovery case study
- Documented primary disk space culprits
- Explained why restart frees so much space
- Created monitoring and automation scripts
- Documented Claude Code specific issues
- Added preventive maintenance schedule

**Future Updates:**
- Add data from next disk space incident
- Update Claude Code issue status as bugs are fixed
- Add more automation scripts based on usage patterns
