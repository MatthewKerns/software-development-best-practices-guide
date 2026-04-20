# Disk Space Management - Quick Reference Card

**Last Updated:** November 2025
**Full Guide:** [DISK_SPACE_MANAGEMENT_GUIDE.md](./DISK_SPACE_MANAGEMENT_GUIDE.md)

---

## 🚨 Emergency Commands (Disk Full)

```bash
# 1. Quick check
df -h /

# 2. Take snapshot BEFORE cleanup
disk-snapshot

# 3. Emergency cleanup (run in order)
docker-clean                    # Frees 10-50GB
deep-clean                      # Frees 5-10GB more
sudo tmutil deletelocalsnapshots $(date +%Y-%m-%d)  # Frees 50-150GB

# 4. Last resort: Restart Mac (frees 50-200GB)
```

---

## ⚡ Quick Commands

### Daily
```bash
docker-clean     # Clean Docker after work (10-20GB)
disk-check       # Check disk + Docker status
```

### Weekly
```bash
dev-clean        # Clean dev environment (2-5GB)
tm-check         # Check Time Machine snapshots
```

### Monthly
```bash
deep-clean       # Full cache cleanup (5-10GB)
disk-snapshot    # Take snapshot for monitoring
```

---

## 📊 Monitoring

### Check What's Using Space
```bash
# Overall disk
df -h /

# Docker
docker system df

# Time Machine snapshots (MAJOR culprit: 50-150GB!)
tmutil listlocalsnapshots /

# /var/folders temp files
du -sh /private/var/folders/*

# Application caches
du -sh ~/Library/Caches/* | sort -h | tail -10

# Project artifacts
du -sh ~/workspace/langChainProjects/dataInputPipeline/* | sort -h | tail -5
```

---

## 🎯 Primary Culprits (From 147GB Recovery Case Study)

| Source | Typical Size | How to Fix |
|--------|-------------|------------|
| **Time Machine Snapshots** | 50-150GB | Restart Mac (auto-purges when <10GB free) |
| **Docker.raw Compaction** | 10-30GB | `docker-clean` + restart Docker |
| **Chrome Testing (Claude Code bug)** | 5-200GB | Restart Mac (clears `/var/folders/`) |
| **VM Swap Files** | 5-20GB | Restart Mac (deletes swap files) |
| **Application Caches** | 2-10GB | `deep-clean` |
| **Project Build Artifacts** | 1-5GB | `dev-clean` |

---

## 🛠️ Installed Tools

### Aliases (Available Now)
```bash
disk-check       # Quick disk + Docker status
docker-clean     # Clean Docker immediately
dev-clean        # Weekly dev environment cleanup
deep-clean       # Monthly deep cache cleanup
disk-snapshot    # Take detailed snapshot
tm-check         # Check Time Machine snapshots
```

### Scripts in ~/bin/
```bash
~/bin/disk-snapshot     # Detailed disk snapshot for comparison
```

---

## 🔄 Why Restart Frees So Much Space

**macOS automatically triggers these cleanups when you restart:**

1. **Time Machine Snapshot Purge** (50-150GB)
   - Happens when available space < 10GB
   - Deletes ALL local snapshots

2. **`/var/folders/` Cleanup** (5-20GB)
   - Removes temp files older than 3 days
   - Clears Chrome testing artifacts (Claude Code bug)

3. **Docker.raw Compaction** (10-30GB)
   - Docker shutdown compacts sparse file
   - Removes empty space from deleted containers

4. **VM Swap File Cleanup** (5-20GB)
   - Deletes all `swapfile[0-9]` files
   - Fresh swap files created on next boot

5. **Application Cache Pruning** (2-5GB)
   - Apps clear stale caches on restart

**Total Typical Recovery:** 72-225GB
**Our Case:** 147GB freed

---

## 📅 Maintenance Schedule

### Daily (30 seconds)
- [ ] Run `docker-clean` after Docker work

### Weekly (2 minutes)
- [ ] Run `dev-clean`
- [ ] Check disk space: `disk-check`
- [ ] If doing UI work: Restart Mac (Chrome bug)

### Monthly (5 minutes)
- [ ] Run `deep-clean`
- [ ] Take snapshot: `disk-snapshot`
- [ ] Review: `tm-check`

### When Space Low (<50GB)
1. Take snapshot: `disk-snapshot`
2. Run `deep-clean`
3. If still low: `tm-check` then delete snapshots
4. Last resort: Restart Mac

---

## 🐛 Claude Code Known Issues

### Chrome Testing Memory Leak ([Issue #10107](https://github.com/anthropics/claude-code/issues/10107))
**Impact:** 5-300GB in `/var/folders/`
**Fix:** Restart Mac weekly when doing UI development

### Working Directory Tracking ([Issue #8856](https://github.com/anthropics/claude-code/issues/8856))
**Impact:** 174 temp files/day
**Fix:** `find /tmp -name "claude-*-cwd" -delete`

### Memory Leak ([Issue #4953](https://github.com/anthropics/claude-code/issues/4953))
**Impact:** 120GB+ RAM usage → triggers swap
**Fix:** Use `/clear` every 40 messages, restart daily

---

## 💡 Pro Tips

**Before Restarting (For Next Time):**
```bash
# Capture state BEFORE restart
disk-snapshot

# Note the filename, e.g.: disk_snapshot_20251120_082103.txt
```

**After Restarting:**
```bash
# Capture state AFTER restart
disk-snapshot

# Compare to see what was freed
ls -lt ~/disk_snapshot_*.txt | head -2
```

**Docker Best Practice:**
```bash
# Add to your workflow
docker-compose down
docker-clean    # ← Add this!
```

**Weekly Habit:**
```bash
# Every Friday at 5 PM
dev-clean && disk-check
```

---

## 🚦 Disk Space Thresholds

- **>100GB free:** ✅ Healthy - Continue normal work
- **50-100GB free:** ⚠️ Monitor - Run `dev-clean` weekly
- **20-50GB free:** ⚠️ Warning - Run `deep-clean` + check TM snapshots
- **10-20GB free:** 🚨 Critical - Emergency cleanup + plan restart
- **<10GB free:** 🔴 EMERGENCY - Restart Mac immediately

---

## 📖 Full Documentation

For complete details, scripts, and troubleshooting:
👉 [DISK_SPACE_MANAGEMENT_GUIDE.md](./DISK_SPACE_MANAGEMENT_GUIDE.md)

For questions or to report new findings:
👉 Update the guide with your observations!
