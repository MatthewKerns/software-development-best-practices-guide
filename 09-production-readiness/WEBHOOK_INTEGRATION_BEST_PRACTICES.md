# Webhook Integration Best Practices - Production-Ready Push Notifications

**Category:** Production Readiness > External Integrations
**Audience:** Developers implementing webhook receivers (push notifications)
**Last Updated:** 2025-11-09

---

## Table of Contents

1. [Overview](#overview)
2. [Core Principles](#core-principles)
3. [Gmail Push Notifications (Case Study)](#gmail-push-notifications-case-study)
4. [Google Cloud Pub/Sub Patterns](#google-cloud-pubsub-patterns)
5. [Idempotency & Deduplication](#idempotency--deduplication)
6. [History API vs Search API](#history-api-vs-search-api)
7. [Error Handling & Retry Logic](#error-handling--retry-logic)
8. [Performance & Scalability](#performance--scalability)
9. [Monitoring & Debugging](#monitoring--debugging)
10. [Anti-Patterns to Avoid](#anti-patterns-to-avoid)

---

## Overview

### What Are Webhooks?

**Webhooks** are HTTP callbacks that enable real-time, event-driven communication between services using a **push model** (server-to-server).

**Key Characteristics:**
- **Push (not pull):** External service calls your endpoint when events occur
- **At-least-once delivery:** Messages may be delivered multiple times
- **Time-sensitive:** Must acknowledge receipt within seconds (typically <10s)
- **No request context:** Webhook handler doesn't know why event occurred

### When to Use Webhooks

✅ **Good Use Cases:**
- Real-time email/SMS notifications (Gmail, Twilio)
- Payment processing callbacks (Stripe, PayPal)
- CI/CD pipeline events (GitHub, GitLab)
- IoT device state changes
- Chat/messaging integrations (Slack, Discord)

❌ **Poor Use Cases:**
- Bulk data synchronization (use scheduled jobs)
- User-initiated requests (use REST APIs)
- High-frequency updates (>100/sec per endpoint)
- Critical transactions requiring immediate response

### Webhook vs API Comparison

| Aspect | REST API (Pull) | Webhook (Push) |
|--------|----------------|----------------|
| **Initiation** | Client initiates | Server initiates |
| **Latency** | Polling delay | Real-time (<5s) |
| **Control** | Client controls timing | Server controls timing |
| **Reliability** | Synchronous (immediate) | Asynchronous (retries) |
| **Complexity** | Simple (request/response) | Complex (idempotency required) |
| **Debugging** | Easy (you control calls) | Hard (external timing) |

---

## Core Principles

### Principle 1: Webhooks Are Notifications, Not Commands

**Anti-Pattern:**
```python
# ❌ WRONG: Webhook handler does all processing
@app.post("/webhook")
async def webhook(data):
    # 30 seconds of processing...
    process_invoice(data)
    send_emails(data)
    update_database(data)
    return {"status": "done"}  # ← Too late! (timeout)
```

**Best Practice:**
```python
# ✅ CORRECT: Webhook acknowledges immediately
@app.post("/webhook")
async def webhook(data):
    # Fast validation (<200ms)
    if not is_valid(data):
        return {"status": "acknowledged"}  # Still ACK invalid data!

    # Queue for async processing
    await queue.enqueue("process_invoice", data)

    # Acknowledge within <10 seconds
    return {"status": "acknowledged", "queued": True}

# Processing happens AFTER acknowledgment
async def process_invoice_worker(data):
    # Can take minutes - webhook already acknowledged
    process_invoice(data)
    send_emails(data)
```

**Why This Matters:**
- Webhook providers expect HTTP 200 within 10 seconds
- Timeout → Provider assumes failure → Retries
- Retries → Duplicate processing (if not idempotent)

---

### Principle 2: All Webhooks Must Be Idempotent

**Idempotent** means an operation produces the same result no matter how many times it's executed. For webhooks, this means processing the same event 100 times has the same effect as processing it once—no duplicate charges, emails, or side effects.

**The Problem:**

Webhook providers guarantee **at-least-once delivery**, NOT exactly-once:
- Network failures → Retry
- Timeout (no ACK received) → Retry
- Provider infrastructure issues → Retry
- **Result:** Same event delivered 2-100 times

**Anti-Pattern:**
```python
# ❌ WRONG: Non-idempotent processing
@app.post("/webhook/payment")
async def payment_webhook(payment_id):
    # Charge user (NOT idempotent!)
    charge_credit_card(payment_id, amount=100)

    # Send email (NOT idempotent!)
    send_receipt_email(user_email)

    return {"status": "ok"}

# Result: User charged 5 times if webhook retries 5x!
```

**Best Practice:**
```python
# ✅ CORRECT: Idempotent with database deduplication
@app.post("/webhook/payment")
async def payment_webhook(event_id, payment_id):
    # Check if already processed (database, not cache!)
    if await db.is_event_processed(event_id):
        logger.info("duplicate_event_ignored", event_id=event_id)
        return {"status": "acknowledged", "duplicate": True}

    # Mark as processed BEFORE processing (atomic)
    await db.mark_event_processed(event_id)

    # Now safe to process (idempotent)
    if not await db.is_payment_charged(payment_id):
        charge_credit_card(payment_id, amount=100)
        await db.mark_payment_charged(payment_id)

    if not await db.is_receipt_sent(payment_id):
        send_receipt_email(user_email)
        await db.mark_receipt_sent(payment_id)

    return {"status": "acknowledged"}

# Result: User charged exactly once, even if webhook retries 100x ✅
```

**Idempotency Checklist:**
- [ ] Database-backed deduplication (NOT in-memory cache)
- [ ] Check for duplicates BEFORE processing
- [ ] Mark as processed BEFORE side effects
- [ ] All operations can run multiple times safely

---

### Principle 3: Never Use In-Memory Caches for Deduplication

**Anti-Pattern:**
```python
# ❌ WRONG: TTL cache (60 seconds)
from cachetools import TTLCache

class WebhookService:
    def __init__(self):
        self.cache = TTLCache(maxsize=10000, ttl=60)

    def is_duplicate(self, event_id):
        return event_id in self.cache

# Problems:
# 1. Cache expires after 60s
# 2. Webhook retries can continue for HOURS
# 3. Server restart → Cache lost
# 4. Multiple instances → Separate caches
```

**Why This Fails:**

| Retry Timing | Cache Status | Result |
|--------------|--------------|--------|
| T+0s: First webhook | Cached (60s TTL) | ✅ Processed |
| T+30s: Retry #1 | Still cached | ✅ Blocked |
| T+65s: Retry #2 | **Cache expired!** | ❌ Reprocessed |
| T+120s: Retry #3 | Cache expired | ❌ Reprocessed |
| Server restart | **Cache lost!** | ❌ All retries processed |

**Best Practice:**
```python
# ✅ CORRECT: Database-backed deduplication
class WebhookService:
    def __init__(self, database):
        self.db = database

    async def is_duplicate(self, event_id):
        # Database query (persists across restarts)
        result = await self.db.query(
            "webhookEvents:isProcessed",
            {"eventId": event_id}
        )
        return result.get("processed", False)

    async def mark_processed(self, event_id):
        # Database write (atomic, persistent)
        await self.db.mutation(
            "webhookEvents:markProcessed",
            {
                "eventId": event_id,
                "processedAt": datetime.utcnow().isoformat(),
                "expiresAt": (datetime.utcnow() + timedelta(days=7)).isoformat()
            }
        )

# Benefits:
# ✅ Survives server restarts
# ✅ Shared across multiple instances
# ✅ Persists for days (matches retry window)
# ✅ Atomic operations (no race conditions)
```

**Database Schema:**
```javascript
// Convex schema example
webhookEvents: defineTable({
  eventId: v.string(),        // Unique webhook event ID
  processedAt: v.string(),    // ISO timestamp
  expiresAt: v.string(),      // Auto-cleanup after 7 days
  metadata: v.optional(v.object({
    source: v.string(),
    retryCount: v.number()
  }))
}).index("by_event_id", ["eventId"])
```

---

## Gmail Push Notifications (Case Study)

### The Challenge

Gmail uses Google Cloud Pub/Sub to deliver push notifications when emails arrive. This case study demonstrates production-ready webhook implementation.

**Gmail Notification Flow:**
```
Email arrives → Gmail applies filter → Pub/Sub notification → Your webhook → Process email
```

**Challenges:**
1. Pub/Sub retries for up to **7 days** (not seconds!)
2. Multiple notifications for same email (labels applied after webhook)
3. historyId-based incremental sync required (not full search)
4. Race conditions (multiple webhooks reading same state)

### Solution Architecture

```python
# 1. Webhook endpoint (Fast acknowledgment)
@router.post("/api/gmail/webhook/user-inbox")
async def user_inbox_webhook(envelope: PubSubEnvelope):
    """Acknowledge within <10 seconds, queue processing."""

    message_id = envelope.message.messageId

    # Database deduplication (7-day persistence)
    if await webhook_service.check_duplicate(message_id):
        return {"status": "acknowledged", "duplicate": True}

    # Mark processed IMMEDIATELY (prevents race conditions)
    await webhook_service.mark_processed(message_id)

    # Decode notification
    notification_data = await webhook_service.decode_pubsub_message(
        envelope.message.data
    )

    # Queue background processing (fast!)
    background_tasks.add_task(
        run_invoice_workflow,
        gmail_history_id=notification_data.get("historyId"),
        user_email=notification_data.get("emailAddress")
    )

    # Acknowledge within 200ms ✅
    return {"status": "acknowledged", "queued": True}


# 2. Background worker (Can take minutes)
async def run_invoice_workflow(gmail_history_id, user_email):
    """Process emails using History API (incremental sync)."""

    # Get stored historyId (START point for incremental sync)
    stored_history_id = await db.get_stored_history_id(user_id)

    if not stored_history_id:
        # First-time setup: Use notification ID
        stored_history_id = gmail_history_id

    # Fetch ONLY NEW emails using History API
    gmail_service = GmailMessageService(gmail_client)
    messages = await gmail_service.fetch_history_messages(
        start_history_id=stored_history_id,  # ← START (old state)
        inbox_type="user"
    )

    # Process each email (with Gmail message deduplication)
    for message_info in messages:
        gmail_message_id = message_info['message']['id']

        # Second-level deduplication (Gmail message ID)
        if await db.is_gmail_message_processed(gmail_message_id):
            continue

        await db.mark_gmail_message_processed(gmail_message_id)

        # Process email (guaranteed exactly-once)
        await process_invoice(gmail_message_id)

    # Update stored historyId (becomes next START point)
    await db.update_history_id(user_id, gmail_history_id)
```

**Key Insights:**

1. **Two-level deduplication:**
   - Level 1: Pub/Sub message ID (webhook retries)
   - Level 2: Gmail message ID (same email in multiple history calls)

2. **History API (not search):**
   - Incremental sync: `history.list(startHistoryId=stored_id)`
   - Only fetches NEW emails (efficient)
   - Deterministic (same query always returns same results)

3. **State tracking:**
   - Store historyId after each successful batch
   - Next webhook uses stored ID as START point
   - Prevents reprocessing old emails

---

## Google Cloud Pub/Sub Patterns

### Retry Behavior

**Default Configuration:**
- **Acknowledgment deadline:** 10 seconds
- **Retry policy:** Immediate retry (default) or exponential backoff
- **Maximum backoff:** 600 seconds (10 minutes)
- **Total retry window:** Up to **7 days**

**Retry Timeline:**

| Time | Event | Notes |
|------|-------|-------|
| T+0s | Initial delivery | |
| T+10s | No ACK received | Pub/Sub assumes failure |
| T+10s | Retry #1 | Immediate retry |
| T+20s | Retry #2 | With exponential backoff |
| T+40s | Retry #3 | Backoff increases |
| ... | ... | Continues for up to 7 days |

**Implications:**
- 60-second cache → Fails after 1 minute
- Server restart → Loses in-memory state
- **Must use database deduplication!**

### Best Practices for Pub/Sub

```python
# ✅ Production-ready Pub/Sub webhook
@app.post("/webhook/pubsub")
async def pubsub_webhook(envelope):
    start_time = time.time()

    try:
        # 1. Extract message ID
        message_id = envelope.message.messageId

        # 2. Database deduplication (persistent!)
        if await db.is_event_processed(message_id):
            elapsed = time.time() - start_time
            logger.info("duplicate_blocked",
                message_id=message_id,
                elapsed_ms=elapsed * 1000
            )
            return {"status": "acknowledged", "duplicate": True}

        # 3. Mark processed IMMEDIATELY (atomic)
        await db.mark_event_processed(message_id)

        # 4. Decode & validate
        data = base64.b64decode(envelope.message.data).decode('utf-8')
        payload = json.loads(data)

        # 5. Queue async processing
        await queue.enqueue("process_event", payload)

        # 6. Monitor response time
        elapsed = time.time() - start_time
        if elapsed > 5:
            logger.warning("slow_webhook_response",
                elapsed_seconds=elapsed
            )

        # 7. Always acknowledge (even on errors!)
        return {"status": "acknowledged", "elapsed_ms": elapsed * 1000}

    except Exception as e:
        # CRITICAL: Still acknowledge to prevent retries
        logger.error("webhook_error_still_acked",
            error=str(e),
            exc_info=True
        )
        return {"status": "acknowledged", "error": "logged"}
```

**Critical Patterns:**

1. **Always acknowledge:** Even on errors (prevent infinite retries)
2. **Fast ACK:** <10 seconds (Pub/Sub requirement)
3. **Database dedup:** Not cache (7-day persistence)
4. **Monitor timing:** Alert if >5 seconds (approaching limit)

---

## Idempotency & Deduplication

### Three-Layer Defense

**Layer 1: Event ID Deduplication (Webhook Level)**
```python
# Check if Pub/Sub message already processed
if await db.is_event_processed(pubsub_message_id):
    return early_ack()
```
**Coverage:** Webhook retries (same Pub/Sub message)

**Layer 2: Entity ID Deduplication (Business Level)**
```python
# Check if specific entity already processed
if await db.is_entity_processed(gmail_message_id):
    continue  # Skip this email
```
**Coverage:** Same entity in multiple webhook calls

**Layer 3: Operation Deduplication (Action Level)**
```python
# Check if specific action already performed
if not await db.was_email_sent(invoice_id):
    send_analysis_email(invoice_id)
    await db.mark_email_sent(invoice_id)
```
**Coverage:** Prevent duplicate side effects

### Database Schema Design

```javascript
// Table 1: Webhook event deduplication
webhookEvents: defineTable({
  messageId: v.string(),       // Pub/Sub message ID
  source: v.string(),          // "gmail", "stripe", etc.
  processedAt: v.string(),
  expiresAt: v.string()        // 7-day retention
}).index("by_message_id", ["messageId"])

// Table 2: Entity deduplication
processedEntities: defineTable({
  entityType: v.string(),      // "gmail_message", "payment", etc.
  entityId: v.string(),        // Unique entity ID
  processedAt: v.string(),
  expiresAt: v.string()        // 30-day retention
}).index("by_entity", ["entityType", "entityId"])

// Table 3: Action deduplication
performedActions: defineTable({
  entityId: v.string(),
  actionType: v.string(),      // "email_sent", "charge_processed"
  performedAt: v.string(),
  expiresAt: v.string()
}).index("by_entity_action", ["entityId", "actionType"])
```

---

## History API vs Search API

### The Fundamental Problem with Search

**Search API (Gmail example):**
```python
# ❌ ANTI-PATTERN: Search all matching emails
emails = gmail.search("has:attachment label:woodbury")

# Problems:
# 1. Returns ALL emails in inbox (not just new)
# 2. Non-deterministic (inbox contents change)
# 3. Reprocesses old emails on every webhook retry
# 4. No concept of "what's new since last check"
```

**Result with Pub/Sub retries:**
```
Webhook #1: Search → 50 emails → Process 50 → Send 50 analysis emails
Retry #1 (T+65s): Search → 50 emails → Process 50 → Send 50 MORE emails
Retry #2 (T+120s): Search → 50 emails → Process 50 → Send 50 MORE emails
Total: 150 duplicate emails sent! ❌
```

### The Correct Approach: History API

**History API (Gmail example):**
```python
# ✅ CORRECT: Fetch only changes since last sync
stored_history_id = await db.get_stored_history_id(user_id)

# Fetch incremental changes
history = gmail.history.list(
    startHistoryId=stored_history_id,  # ← START point (old state)
    historyTypes=['messageAdded']
)

# Returns ONLY new emails since stored_history_id
messages = extract_messages_from_history(history)

# Process ONLY new emails
for message in messages:
    process_email(message)

# Update stored history ID
await db.update_history_id(user_id, current_history_id)
```

**Result with Pub/Sub retries:**
```
Webhook #1: History (100→150) → 3 new emails → Process 3 → Send 3 emails
Retry #1 (T+65s): Blocked by database deduplication → 0 emails
Retry #2 (T+120s): Blocked by database deduplication → 0 emails
Total: 3 emails sent ✅
```

### Why History API is Superior

| Aspect | Search API | History API |
|--------|-----------|-------------|
| **Query** | `search("label:inbox")` | `history.list(startHistoryId=12000)` |
| **Returns** | ALL matching items | ONLY changes since 12000 |
| **Deterministic** | ❌ No (inbox changes) | ✅ Yes (history immutable) |
| **Efficiency** | Searches entire dataset | Fetches only delta |
| **Idempotent** | ❌ No | ✅ Yes (same query = same result) |
| **Webhook-friendly** | ❌ No | ✅ Yes (designed for webhooks) |

**Implementation Pattern:**

```python
class IncrementalSyncService:
    """Generic incremental sync using checkpoint-based history."""

    async def sync(self, user_id, notification_checkpoint):
        # 1. Get last known checkpoint (START)
        stored_checkpoint = await db.get_checkpoint(user_id)

        if not stored_checkpoint:
            # First-time: Full sync
            items = await api.full_sync()
            await db.set_checkpoint(user_id, notification_checkpoint)
            return items

        # 2. Fetch incremental changes (START → END)
        changes = await api.fetch_changes(
            start=stored_checkpoint,
            end=notification_checkpoint
        )

        # 3. Process only NEW items
        for item in changes:
            if not await db.is_processed(item.id):
                await process_item(item)
                await db.mark_processed(item.id)

        # 4. Update checkpoint (becomes next START)
        await db.set_checkpoint(user_id, notification_checkpoint)

        return changes
```

---

## Error Handling & Retry Logic

### Webhook Error Categories

| Error Type | Acknowledge? | Retry? | Example |
|------------|--------------|--------|---------|
| **Client error (4xx)** | ✅ Yes | ❌ No | Invalid payload, auth failure |
| **Server error (5xx)** | ❌ No | ✅ Yes | Database down, timeout |
| **Transient error** | ❌ No | ✅ Yes | Network timeout, rate limit |
| **Validation error** | ✅ Yes | ❌ No | Missing required field |

**Decision Tree:**
```python
try:
    # Process webhook
    result = await process_webhook(data)
    return {"status": "acknowledged"}  # ✅ Always ACK success

except ValidationError as e:
    # Client error: Don't retry
    logger.warning("invalid_webhook_data", error=str(e))
    return {"status": "acknowledged"}  # ✅ ACK to prevent retries

except DatabaseError as e:
    # Server error: Retry might help
    logger.error("database_error", error=str(e))
    raise  # ❌ Don't ACK → Pub/Sub will retry

except RateLimitError as e:
    # Transient: Retry after backoff
    logger.warning("rate_limit_hit", retry_after=e.retry_after)
    raise  # ❌ Don't ACK → Retry with backoff
```

### Dead Letter Queues

**When to Use:**
- Webhooks failing after N retries (e.g., 5 attempts)
- Prevents infinite retry loops
- Allows manual investigation

**Configuration (Pub/Sub example):**
```yaml
subscription:
  name: "user-inbox-push"
  topic: "gmail-notifications"
  deadLetterPolicy:
    deadLetterTopic: "projects/my-project/topics/webhook-dlq"
    maxDeliveryAttempts: 5  # After 5 failures → DLQ
```

**Monitoring DLQ:**
```python
# Alert when messages arrive in DLQ
@scheduled("*/5 * * * *")  # Every 5 minutes
async def monitor_dlq():
    messages = await pubsub.pull("webhook-dlq", max_messages=10)

    if messages:
        logger.error("webhooks_in_dlq", count=len(messages))
        alert_ops_team(
            title="Webhook DLQ has messages",
            count=len(messages),
            sample=messages[0]
        )
```

---

## Performance & Scalability

### Latency Requirements

| Component | Target | Critical |
|-----------|--------|----------|
| Webhook ACK | <200ms | <10s |
| Database query | <100ms | <500ms |
| Queue write | <50ms | <200ms |

### Optimization Patterns

**1. Parallel Database Operations**
```python
# ❌ SLOW: Sequential database calls (600ms total)
is_dup = await db.is_duplicate(message_id)  # 100ms
user = await db.get_user(email)             # 200ms
stored_id = await db.get_history_id(user_id) # 300ms

# ✅ FAST: Parallel database calls (300ms total)
is_dup, user, stored_id = await asyncio.gather(
    db.is_duplicate(message_id),
    db.get_user(email),
    db.get_history_id_lazy(user_id)
)
```

**2. Connection Pooling**
```python
# ✅ Reuse database connections
class WebhookService:
    def __init__(self):
        self.db_pool = await create_pool(
            min_size=5,
            max_size=20
        )

    async def process_webhook(self):
        async with self.db_pool.acquire() as conn:
            # Reuse connection from pool
            await conn.execute(...)
```

**3. Batch Processing**
```python
# Process multiple messages from DLQ in batch
messages = await pubsub.pull(max_messages=100)

# Batch database operations
await db.mark_many_processed([m.id for m in messages])
```

---

## Monitoring & Debugging

### Key Metrics

```python
# 1. Webhook throughput
metrics.increment("webhook.received", tags={"source": "gmail"})

# 2. Response time
with metrics.timer("webhook.response_time"):
    result = await process_webhook(data)

# 3. Duplicate rate
if is_duplicate:
    metrics.increment("webhook.duplicate")
else:
    metrics.increment("webhook.processed")

# 4. Error rate
try:
    await process_webhook(data)
except Exception:
    metrics.increment("webhook.error")
    raise
```

### Alerting Thresholds

| Metric | Warning | Critical |
|--------|---------|----------|
| Response time | >1s | >5s |
| Error rate | >5% | >10% |
| Duplicate rate | >50% | >80% |
| No webhooks received | 10 min | 30 min |

### Debugging Checklist

```bash
# 1. Check webhook is receiving calls
curl http://localhost:8000/webhook/health

# 2. Verify database deduplication
grep "duplicate_blocked" logs/*.log | tail -20

# 3. Check for errors
grep "ERROR\|failed" logs/*.log | tail -50

# 4. Monitor response times
grep "webhook_acknowledged" logs/*.log | \
  grep -o "elapsed_ms=[0-9]*" | \
  sort -rn | head -20

# 5. Verify database state
db.query("webhookEvents:count") # Should grow over time
```

---

## Anti-Patterns to Avoid

### ❌ Anti-Pattern 1: Synchronous Processing in Webhook

```python
# ❌ WRONG
@app.post("/webhook")
async def webhook(data):
    # 30 seconds of processing...
    result = await process_invoice(data)
    await send_emails(result)
    await update_analytics(result)
    return {"status": "done"}  # ← Timeout! (>10s)
```

**Problem:** Pub/Sub times out → Retries → Duplicates

**Fix:** Queue async processing

---

### ❌ Anti-Pattern 2: In-Memory Deduplication

```python
# ❌ WRONG
processed_events = set()  # In-memory cache

@app.post("/webhook")
async def webhook(event_id):
    if event_id in processed_events:
        return
    processed_events.add(event_id)
    await process(event_id)
```

**Problems:**
- Server restart → Cache lost
- Multiple instances → Separate caches
- No TTL → Memory leak

**Fix:** Database-backed deduplication

---

### ❌ Anti-Pattern 3: Using Notification Data as State

```python
# ❌ WRONG
@app.post("/webhook/gmail")
async def gmail_webhook(notification_history_id):
    # Using notification historyId as START point
    emails = gmail.history.list(
        startHistoryId=notification_history_id  # ← WRONG!
    )
    # Returns empty (notification ID is LATEST state)
```

**Problem:** Notification historyId is END point, not START point

**Fix:** Store and use previous historyId

---

### ❌ Anti-Pattern 4: Search Instead of Incremental Sync

```python
# ❌ WRONG
@app.post("/webhook/gmail")
async def gmail_webhook():
    # Search ALL emails every time
    emails = gmail.search("has:attachment")
    for email in emails:
        process_email(email)  # Reprocesses old emails!
```

**Problem:** Reprocesses all matching items on every webhook

**Fix:** Use History API for incremental sync

---

### ❌ Anti-Pattern 5: Not Acknowledging Errors

```python
# ❌ WRONG
@app.post("/webhook")
async def webhook(data):
    if not is_valid(data):
        raise ValidationError("Invalid data")  # ← Triggers retries!
    await process(data)
```

**Problem:** Client errors (4xx) shouldn't retry

**Fix:** Acknowledge invalid data (prevent retries)

---

## Summary: Production Checklist

### Before Deploying Webhooks

- [ ] **Database-backed deduplication** (7-day persistence minimum)
- [ ] **Fast acknowledgment** (<10 seconds, ideally <200ms)
- [ ] **Idempotent processing** (safe to retry 100x)
- [ ] **Async processing** (queue background tasks)
- [ ] **Error handling** (acknowledge 4xx, retry 5xx)
- [ ] **Monitoring** (response time, error rate, duplicate rate)
- [ ] **Dead letter queue** (for failed webhooks)
- [ ] **Incremental sync** (History API, not search)
- [ ] **State tracking** (store checkpoints in database)
- [ ] **Multi-layer deduplication** (event, entity, action levels)

### Key Takeaways

1. **Webhooks = Notifications** (not commands)
2. **Always acknowledge fast** (<10s)
3. **Always be idempotent** (database dedup)
4. **Never use in-memory cache** (use database)
5. **Use History API** (not search)
6. **Track state** (store checkpoints)
7. **Monitor everything** (timing, errors, duplicates)

---

**References:**
- [Gmail Push Notifications](https://developers.google.com/workspace/gmail/api/guides/push)
- [Pub/Sub Reliability](https://cloud.google.com/pubsub/docs/reliability-intro)
- [Webhook Best Practices (Stripe)](https://stripe.com/docs/webhooks/best-practices)

**Related Documents:**
- `../06-collaborative-construction/INTEGRATION_PLAYBOOK_GUIDE.md` - External service integration
- `MONITORING_AND_OBSERVABILITY.md` - Production monitoring patterns
- `SECURITY_HARDENING.md` - Webhook security validation
