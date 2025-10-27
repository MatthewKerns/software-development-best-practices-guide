# Monitoring & Observability Guide

## Overview

Monitoring and observability provide visibility into production system behavior, enabling rapid issue detection and resolution. This guide covers comprehensive monitoring strategies from simple uptime checks to full observability stacks.

**Key Concepts:**

- **Monitoring:** Collecting and analyzing predefined metrics (known unknowns)
- **Observability:** Understanding system behavior from outputs (unknown unknowns)
- **Telemetry:** Data emitted by systems (logs, metrics, traces)
- **Alerting:** Notifications when conditions exceed thresholds

**Three Pillars of Observability:**

1. **Logs:** Discrete event records (what happened)
2. **Metrics:** Numerical measurements over time (how much)
3. **Traces:** Request flows across services (where bottlenecks are)

**Complexity Tiers:**

- **Small-Scale:** Uptime monitoring + simple analytics ($0-50/month)
- **Medium-Scale:** Centralized logging + metrics + error tracking ($200-500/month)
- **Large-Scale:** Full observability stack + distributed tracing ($1K-5K+/month)

---

## 1. Logging Infrastructure

### 1.1 Structured Logging (All Scales)

**Why:** Machine-readable logs enable powerful querying and analysis

**Implementation (Python):**
```python
# structured_logging.py
import logging
import json
from datetime import datetime
import traceback

class StructuredLogger:
    """Structured JSON logging for production."""

    def __init__(self, name, service_name, environment):
        self.logger = logging.getLogger(name)
        self.service_name = service_name
        self.environment = environment

        # Configure handler
        handler = logging.StreamHandler()
        handler.setFormatter(self.JsonFormatter())
        self.logger.addHandler(handler)
        self.logger.setLevel(logging.INFO)

    class JsonFormatter(logging.Formatter):
        """Format logs as JSON."""

        def format(self, record):
            log_data = {
                'timestamp': datetime.utcnow().isoformat() + 'Z',
                'level': record.levelname,
                'message': record.getMessage(),
                'logger': record.name,
                'module': record.module,
                'function': record.funcName,
                'line': record.lineno,
            }

            # Add context from record
            if hasattr(record, 'request_id'):
                log_data['request_id'] = record.request_id
            if hasattr(record, 'user_id'):
                log_data['user_id'] = record.user_id
            if hasattr(record, 'duration_ms'):
                log_data['duration_ms'] = record.duration_ms

            # Add exception info
            if record.exc_info:
                log_data['exception'] = {
                    'type': record.exc_info[0].__name__,
                    'message': str(record.exc_info[1]),
                    'stacktrace': traceback.format_exception(*record.exc_info)
                }

            return json.dumps(log_data)

    def info(self, message, **kwargs):
        self.logger.info(message, extra=kwargs)

    def error(self, message, **kwargs):
        self.logger.error(message, extra=kwargs, exc_info=True)

    def warning(self, message, **kwargs):
        self.logger.warning(message, extra=kwargs)

# Usage in application
logger = StructuredLogger(
    name='api',
    service_name='user-service',
    environment='production'
)

# Log with context
logger.info('User registered',
    user_id='12345',
    email='user@example.com',
    source='web'
)

# Log errors with automatic exception capture
try:
    process_payment(amount=100)
except Exception as e:
    logger.error('Payment processing failed',
        user_id='12345',
        amount=100,
        payment_method='credit_card'
    )
```

**Structured Logging Best Practices:**
```python
# Good: Rich context, structured fields
logger.info('Order created',
    order_id='ORD-12345',
    user_id='USR-67890',
    amount=99.99,
    currency='USD',
    items_count=3,
    shipping_method='express'
)

# Bad: Unstructured string, hard to query
logger.info('Order ORD-12345 created for user USR-67890 with amount $99.99')

# Good: Consistent field names across services
logger.info('Request completed',
    request_id='req-abc123',
    duration_ms=245,
    status_code=200
)

# Bad: Inconsistent naming
logger.info('Request done',
    reqId='req-abc123',
    time=245,
    status=200
)
```

**Checklist:**
- [ ] All logs JSON-formatted
- [ ] Request IDs included for tracing
- [ ] Sensitive data excluded (passwords, tokens, SSNs)
- [ ] Log levels used correctly (DEBUG, INFO, WARN, ERROR)
- [ ] Consistent field naming across services

### 1.2 Centralized Log Aggregation (Medium/Large Scale)

**Why:** Consolidate logs from multiple services/instances for unified search

**Architecture:**
```
Application Logs → Log Shipper → Aggregation → Storage → Query/Visualize
(stdout/files)     (Fluentd)     (Logstash)   (ES)      (Kibana)
```

**Implementation (ELK Stack):**
```yaml
# docker-compose.yml - ELK Stack
version: '3.8'
services:
  elasticsearch:
    image: docker.elastic.co/elasticsearch/elasticsearch:8.11.0
    environment:
      - discovery.type=single-node
      - "ES_JAVA_OPTS=-Xms512m -Xmx512m"
    ports:
      - "9200:9200"
    volumes:
      - elasticsearch-data:/usr/share/elasticsearch/data

  logstash:
    image: docker.elastic.co/logstash/logstash:8.11.0
    ports:
      - "5044:5044"  # Beats input
      - "9600:9600"  # Monitoring
    volumes:
      - ./logstash.conf:/usr/share/logstash/pipeline/logstash.conf
    depends_on:
      - elasticsearch

  kibana:
    image: docker.elastic.co/kibana/kibana:8.11.0
    ports:
      - "5601:5601"
    environment:
      ELASTICSEARCH_HOSTS: http://elasticsearch:9200
    depends_on:
      - elasticsearch

volumes:
  elasticsearch-data:
```

**Logstash Configuration:**
```ruby
# logstash.conf
input {
  beats {
    port => 5044
  }
}

filter {
  # Parse JSON logs
  json {
    source => "message"
  }

  # Extract timestamp
  date {
    match => [ "timestamp", "ISO8601" ]
    target => "@timestamp"
  }

  # Add geo-location from IP
  geoip {
    source => "client_ip"
    target => "geoip"
  }

  # Enrich with service metadata
  mutate {
    add_field => {
      "[@metadata][service]" => "%{service_name}"
      "[@metadata][environment]" => "%{environment}"
    }
  }
}

output {
  elasticsearch {
    hosts => ["elasticsearch:9200"]
    index => "logs-%{[@metadata][service]}-%{+YYYY.MM.dd}"
  }

  # Optional: Send errors to Slack
  if [level] == "ERROR" {
    slack {
      url => "${SLACK_WEBHOOK_URL}"
      format => "Error in %{service_name}: %{message}"
    }
  }
}
```

**Fluentd Configuration (Alternative):**
```xml
<!-- fluent.conf -->
<source>
  @type tail
  path /var/log/app/*.log
  pos_file /var/log/td-agent/app.log.pos
  tag app.logs
  <parse>
    @type json
    time_key timestamp
    time_format %Y-%m-%dT%H:%M:%S.%LZ
  </parse>
</source>

<filter app.logs>
  @type record_transformer
  <record>
    hostname "#{Socket.gethostname}"
    service_name ${SERVICE_NAME}
    environment ${ENVIRONMENT}
  </record>
</filter>

<match app.logs>
  @type elasticsearch
  host elasticsearch
  port 9200
  logstash_format true
  logstash_prefix logs-app
  <buffer>
    flush_interval 10s
    retry_max_times 5
  </buffer>
</match>
```

**Cloud-Based Alternatives:**
```markdown
# Managed Log Aggregation Services

## AWS CloudWatch Logs
- **Pros:** Native AWS integration, scalable
- **Cons:** Query syntax limited, can be expensive
- **Cost:** ~$0.50/GB ingested + $0.03/GB stored

## Datadog Logs
- **Pros:** Unified metrics + logs + traces, powerful queries
- **Cons:** Can be expensive at scale
- **Cost:** ~$0.10/GB ingested (volume discounts available)

## Splunk
- **Pros:** Enterprise features, powerful search
- **Cons:** Expensive, complex setup
- **Cost:** ~$150/GB/day indexed

## Self-Hosted ELK
- **Pros:** Full control, no per-GB fees
- **Cons:** Operational overhead, scaling complexity
- **Cost:** Infrastructure only (~$500-2K/month for medium scale)
```

**Checklist:**
- [ ] Centralized logging configured
- [ ] Logs retained 30+ days (compliance dependent)
- [ ] Log volume monitored (alert on spikes)
- [ ] Search performance acceptable (<5s for most queries)

### 1.3 Log Querying & Analysis

**Common Query Patterns:**

**Find all errors in last hour:**
```
# Elasticsearch Query DSL
GET /logs-*/_search
{
  "query": {
    "bool": {
      "must": [
        { "match": { "level": "ERROR" }},
        { "range": {
            "@timestamp": {
              "gte": "now-1h"
            }
          }
        }
      ]
    }
  },
  "sort": [ { "@timestamp": "desc" } ],
  "size": 100
}
```

**Find slow requests (>1s):**
```
# Kibana Query Language (KQL)
duration_ms > 1000 AND level: INFO
```

**Count errors by service:**
```
# Elasticsearch Aggregation
GET /logs-*/_search
{
  "size": 0,
  "query": {
    "bool": {
      "must": [
        { "match": { "level": "ERROR" }},
        { "range": { "@timestamp": { "gte": "now-24h" }}}
      ]
    }
  },
  "aggs": {
    "errors_by_service": {
      "terms": {
        "field": "service_name.keyword",
        "size": 10
      }
    }
  }
}
```

**Trace requests across services:**
```
# Search by request_id to follow request flow
request_id: "req-abc123" AND @timestamp > now-1h
```

---

## 2. Metrics & Monitoring

### 2.1 Application Metrics (All Scales)

**Key Metrics to Track:**

**Golden Signals (SRE Framework):**
1. **Latency:** Request duration (p50, p95, p99)
2. **Traffic:** Request rate (requests/second)
3. **Errors:** Error rate (% of failed requests)
4. **Saturation:** Resource utilization (CPU, memory, disk)

**Implementation (Prometheus):**
```python
# metrics.py - Prometheus instrumentation
from prometheus_client import Counter, Histogram, Gauge, Summary
import time
from functools import wraps

# Request metrics
http_requests_total = Counter(
    'http_requests_total',
    'Total HTTP requests',
    ['method', 'endpoint', 'status']
)

http_request_duration_seconds = Histogram(
    'http_request_duration_seconds',
    'HTTP request duration in seconds',
    ['method', 'endpoint'],
    buckets=[0.01, 0.05, 0.1, 0.5, 1.0, 2.0, 5.0]
)

# Business metrics
user_registrations_total = Counter(
    'user_registrations_total',
    'Total user registrations',
    ['source']
)

active_users = Gauge(
    'active_users',
    'Number of currently active users'
)

# Database metrics
db_connections_used = Gauge(
    'db_connections_used',
    'Number of database connections in use'
)

db_connections_max = Gauge(
    'db_connections_max',
    'Maximum database connections allowed'
)

db_query_duration_seconds = Histogram(
    'db_query_duration_seconds',
    'Database query duration',
    ['query_type'],
    buckets=[0.001, 0.01, 0.05, 0.1, 0.5, 1.0]
)

# Decorator for automatic instrumentation
def track_request_metrics(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        method = request.method
        endpoint = request.endpoint

        # Track request
        start_time = time.time()

        try:
            response = f(*args, **kwargs)
            status = response.status_code

            # Record metrics
            http_requests_total.labels(
                method=method,
                endpoint=endpoint,
                status=status
            ).inc()

            duration = time.time() - start_time
            http_request_duration_seconds.labels(
                method=method,
                endpoint=endpoint
            ).observe(duration)

            return response

        except Exception as e:
            # Record error
            http_requests_total.labels(
                method=method,
                endpoint=endpoint,
                status=500
            ).inc()
            raise

    return decorated_function

# Usage
@app.route('/api/register', methods=['POST'])
@track_request_metrics
def register_user():
    user = create_user(request.json)

    # Track business metric
    user_registrations_total.labels(
        source=request.json.get('source', 'direct')
    ).inc()

    return jsonify(user.to_dict()), 201

# Expose metrics endpoint
@app.route('/metrics')
def metrics():
    from prometheus_client import generate_latest
    return generate_latest(), 200, {'Content-Type': 'text/plain; charset=utf-8'}
```

**Prometheus Configuration:**
```yaml
# prometheus.yml
global:
  scrape_interval: 15s
  evaluation_interval: 15s

scrape_configs:
  # Scrape application metrics
  - job_name: 'api'
    static_configs:
      - targets: ['api-1:8080', 'api-2:8080', 'api-3:8080']
    metrics_path: '/metrics'

  # Scrape node metrics (system-level)
  - job_name: 'node-exporter'
    static_configs:
      - targets: ['node-exporter:9100']

  # Scrape database metrics
  - job_name: 'postgres'
    static_configs:
      - targets: ['postgres-exporter:9187']

# Alerting rules
rule_files:
  - 'alerts.yml'

# Alert manager configuration
alerting:
  alertmanagers:
    - static_configs:
        - targets: ['alertmanager:9093']
```

**Checklist:**
- [ ] Golden signals instrumented (latency, traffic, errors, saturation)
- [ ] Business metrics tracked (signups, conversions, revenue)
- [ ] Metrics retention 30+ days
- [ ] Dashboards created for key metrics

### 2.2 Infrastructure Metrics (All Scales)

**System Metrics to Monitor:**

**Compute:**
- CPU usage (%)
- Memory usage (%)
- Disk usage (%)
- Network I/O (bytes/s)

**Database:**
- Connection count
- Query rate (queries/s)
- Query duration (p95, p99)
- Cache hit rate (%)
- Replication lag (seconds)

**Application:**
- Request rate (req/s)
- Error rate (%)
- Response time (ms)
- Active connections

**Node Exporter (System Metrics):**
```bash
# Install node_exporter on each server
wget https://github.com/prometheus/node_exporter/releases/download/v1.6.1/node_exporter-1.6.1.linux-amd64.tar.gz
tar xvf node_exporter-1.6.1.linux-amd64.tar.gz
cd node_exporter-1.6.1.linux-amd64
./node_exporter &

# Metrics available at http://localhost:9100/metrics
```

**PostgreSQL Metrics:**
```bash
# Install postgres_exporter
docker run -d \
  --name postgres-exporter \
  -e DATA_SOURCE_NAME="postgresql://user:password@postgres:5432/database?sslmode=disable" \
  -p 9187:9187 \
  prometheuscommunity/postgres-exporter

# Metrics available at http://localhost:9187/metrics
```

**CloudWatch Metrics (AWS):**
```python
# Push custom metrics to CloudWatch
import boto3
from datetime import datetime

cloudwatch = boto3.client('cloudwatch')

def put_metric(metric_name, value, unit='Count'):
    """Push metric to CloudWatch."""
    cloudwatch.put_metric_data(
        Namespace='Production/API',
        MetricData=[{
            'MetricName': metric_name,
            'Value': value,
            'Unit': unit,
            'Timestamp': datetime.utcnow()
        }]
    )

# Usage
put_metric('ActiveUsers', 1543, unit='Count')
put_metric('ResponseTime', 0.245, unit='Seconds')
```

### 2.3 Dashboards (All Scales)

**Grafana Dashboard Example:**
```json
{
  "dashboard": {
    "title": "Production API Dashboard",
    "panels": [
      {
        "title": "Request Rate",
        "targets": [{
          "expr": "sum(rate(http_requests_total[5m])) by (endpoint)"
        }],
        "type": "graph"
      },
      {
        "title": "Error Rate",
        "targets": [{
          "expr": "sum(rate(http_requests_total{status=~\"5..\"}[5m])) / sum(rate(http_requests_total[5m]))"
        }],
        "type": "graph",
        "alert": {
          "conditions": [{
            "evaluator": { "params": [0.01], "type": "gt" },
            "query": { "params": ["A", "5m", "now"] }
          }]
        }
      },
      {
        "title": "Response Time (p95)",
        "targets": [{
          "expr": "histogram_quantile(0.95, rate(http_request_duration_seconds_bucket[5m]))"
        }],
        "type": "graph"
      },
      {
        "title": "Active Users",
        "targets": [{
          "expr": "active_users"
        }],
        "type": "stat"
      }
    ]
  }
}
```

**Dashboard Best Practices:**
```markdown
# Dashboard Organization

## Overview Dashboard (Executive/Manager View)
- System health status (red/yellow/green)
- Request rate trend
- Error rate trend
- Key business metrics (signups, revenue)

## Service Dashboard (Developer View)
- Request rate by endpoint
- Error rate by endpoint
- Response time (p50, p95, p99)
- Database query performance
- Cache hit rate

## Infrastructure Dashboard (SRE View)
- CPU, memory, disk usage per host
- Network I/O
- Database connections
- Queue depth (if applicable)

## Business Dashboard (Product/Leadership View)
- Daily active users
- Conversion rate
- Revenue metrics
- Feature adoption
```

**Checklist:**
- [ ] Overview dashboard created
- [ ] Service-specific dashboards for each microservice
- [ ] Infrastructure dashboard
- [ ] Business metrics dashboard
- [ ] Dashboards accessible to relevant teams

---

## 3. Alerting

### 3.1 Alert Rules (Medium/Large Scale)

**Alerting Principles:**

1. **Alert on Symptoms, Not Causes:** Alert when users are impacted
2. **Actionable Alerts:** Every alert should require human action
3. **Appropriate Severity:** Critical alerts wake people up, warnings can wait
4. **Include Context:** Alerts should have enough info to start troubleshooting

**Prometheus Alert Rules:**
```yaml
# alerts.yml
groups:
  - name: api_alerts
    interval: 30s
    rules:
      # Critical: High error rate
      - alert: HighErrorRate
        expr: |
          sum(rate(http_requests_total{status=~"5.."}[5m]))
          / sum(rate(http_requests_total[5m])) > 0.05
        for: 5m
        labels:
          severity: critical
          team: backend
        annotations:
          summary: "High error rate detected"
          description: "Error rate is {{ $value | humanizePercentage }} (threshold: 5%)"
          runbook: "https://wiki.example.com/runbooks/high-error-rate"

      # Critical: Service down
      - alert: ServiceDown
        expr: up{job="api"} == 0
        for: 1m
        labels:
          severity: critical
          team: sre
        annotations:
          summary: "Service {{ $labels.instance }} is down"
          description: "Service has been down for more than 1 minute"

      # Warning: High latency
      - alert: HighLatency
        expr: |
          histogram_quantile(0.95,
            rate(http_request_duration_seconds_bucket[5m])
          ) > 1
        for: 10m
        labels:
          severity: warning
          team: backend
        annotations:
          summary: "High response time detected"
          description: "P95 latency is {{ $value }}s (threshold: 1s)"

      # Warning: Database connection pool exhausted
      - alert: DatabaseConnectionPoolHigh
        expr: db_connections_used / db_connections_max > 0.9
        for: 5m
        labels:
          severity: warning
          team: database
        annotations:
          summary: "Database connection pool near capacity"
          description: "Connection pool is {{ $value | humanizePercentage }} full"

      # Warning: Disk space low
      - alert: DiskSpaceLow
        expr: |
          (node_filesystem_avail_bytes / node_filesystem_size_bytes) < 0.2
        for: 10m
        labels:
          severity: warning
          team: sre
        annotations:
          summary: "Disk space low on {{ $labels.instance }}"
          description: "Only {{ $value | humanizePercentage }} disk space remaining"
```

**AlertManager Configuration:**
```yaml
# alertmanager.yml
global:
  slack_api_url: 'https://hooks.slack.com/services/YOUR/WEBHOOK/URL'

route:
  # Default receiver
  receiver: 'team-slack'

  # Group alerts by cluster and alertname
  group_by: ['cluster', 'alertname']

  # Wait before sending initial notification
  group_wait: 30s

  # Wait before sending new alerts in same group
  group_interval: 5m

  # Wait before repeating alert
  repeat_interval: 4h

  # Route specific alerts to specific teams
  routes:
    - match:
        severity: critical
      receiver: 'pagerduty'
      continue: true  # Also send to Slack

    - match:
        team: database
      receiver: 'database-team'

receivers:
  - name: 'team-slack'
    slack_configs:
      - channel: '#alerts'
        title: '{{ .GroupLabels.alertname }}'
        text: '{{ range .Alerts }}{{ .Annotations.description }}{{ end }}'

  - name: 'pagerduty'
    pagerduty_configs:
      - service_key: 'YOUR_PAGERDUTY_KEY'
        description: '{{ .GroupLabels.alertname }}'

  - name: 'database-team'
    slack_configs:
      - channel: '#database-alerts'
```

**Checklist:**
- [ ] Critical alerts configured (error rate, service down)
- [ ] Warning alerts configured (latency, resource usage)
- [ ] Alerts include runbook links
- [ ] Alert fatigue prevented (meaningful alerts only)
- [ ] On-call rotation configured

### 3.2 On-Call Management

**On-Call Rotation (PagerDuty):**
```python
# setup_oncall.py - Configure on-call rotation
import pypd

pypd.api_key = os.getenv('PAGERDUTY_API_KEY')

# Create escalation policy
escalation_policy = pypd.EscalationPolicy.create(
    name='Production On-Call',
    escalation_rules=[
        {
            'escalation_delay_in_minutes': 5,
            'targets': [
                {'type': 'user_reference', 'id': 'PRIMARY_ONCALL_USER'}
            ]
        },
        {
            'escalation_delay_in_minutes': 15,
            'targets': [
                {'type': 'user_reference', 'id': 'SECONDARY_ONCALL_USER'}
            ]
        },
        {
            'escalation_delay_in_minutes': 30,
            'targets': [
                {'type': 'user_reference', 'id': 'MANAGER_USER'}
            ]
        }
    ]
)

# Create schedule (follow-the-sun rotation)
schedule = pypd.Schedule.create(
    name='Production On-Call Schedule',
    time_zone='America/New_York',
    schedule_layers=[
        {
            'name': 'Weekly Rotation',
            'start': '2025-01-01T00:00:00',
            'rotation_virtual_start': '2025-01-01T00:00:00',
            'rotation_turn_length_seconds': 604800,  # 1 week
            'users': [
                {'user': {'id': 'USER_1'}},
                {'user': {'id': 'USER_2'}},
                {'user': {'id': 'USER_3'}},
                {'user': {'id': 'USER_4'}}
            ]
        }
    ]
)
```

**On-Call Best Practices:**
```markdown
# On-Call Guidelines

## Response Time Expectations
- **SEV1 (Critical):** <5 minutes acknowledgment, <15 minutes response
- **SEV2 (High):** <15 minutes acknowledgment, <1 hour response
- **SEV3 (Medium):** <1 hour acknowledgment, <4 hours response

## On-Call Responsibilities
- Monitor PagerDuty for incidents
- Acknowledge alerts promptly
- Follow runbooks for common issues
- Escalate if unable to resolve in 30 minutes
- Document actions taken in incident report

## Alert Acknowledgment
- Click "Acknowledge" in PagerDuty immediately
- Post in #incidents Slack channel
- Begin investigation within response time

## Handoff Protocol
- Review open incidents with next on-call
- Share context on recent issues
- Update runbooks if new patterns emerge
```

---

## 4. Distributed Tracing (Large Scale)

### 4.1 OpenTelemetry Implementation

**Why:** Debug performance across microservices, identify bottlenecks

**Implementation:**
```python
# tracing.py - OpenTelemetry setup
from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.exporter.jaeger.thrift import JaegerExporter
from opentelemetry.instrumentation.flask import FlaskInstrumentor
from opentelemetry.instrumentation.requests import RequestsInstrumentor
from opentelemetry.instrumentation.sqlalchemy import SQLAlchemyInstrumentor

# Setup tracer provider
trace.set_tracer_provider(TracerProvider())
tracer = trace.get_tracer(__name__)

# Configure Jaeger exporter
jaeger_exporter = JaegerExporter(
    agent_host_name='jaeger-agent',
    agent_port=6831,
)

# Add batch span processor
trace.get_tracer_provider().add_span_processor(
    BatchSpanProcessor(jaeger_exporter)
)

# Auto-instrument frameworks
FlaskInstrumentor().instrument_app(app)
RequestsInstrumentor().instrument()
SQLAlchemyInstrumentor().instrument(engine=db.engine)

# Manual instrumentation for business logic
@app.route('/api/checkout', methods=['POST'])
def checkout():
    with tracer.start_as_current_span("checkout") as span:
        # Add attributes to span
        span.set_attribute("user.id", request.user_id)
        span.set_attribute("cart.total", request.json['total'])
        span.set_attribute("cart.items", len(request.json['items']))

        # Child span for cart validation
        with tracer.start_as_current_span("validate_cart"):
            cart = validate_cart(request.json['cart'])
            span.set_attribute("cart.valid", True)

        # Child span for payment processing
        with tracer.start_as_current_span("process_payment") as payment_span:
            payment_result = process_payment(cart.total)
            payment_span.set_attribute("payment.id", payment_result.id)
            payment_span.set_attribute("payment.status", payment_result.status)

        # Child span for order creation
        with tracer.start_as_current_span("create_order"):
            order = create_order(cart, payment_result)
            span.set_attribute("order.id", order.id)

        # Child span for notification
        with tracer.start_as_current_span("send_confirmation"):
            send_confirmation_email(order)

        return jsonify({'order_id': order.id}), 201
```

**Trace Context Propagation:**
```python
# Propagate trace context across HTTP requests
import requests
from opentelemetry.propagate import inject

def call_downstream_service(url, data):
    """Call downstream service with trace context."""
    headers = {}

    # Inject trace context into headers
    inject(headers)

    response = requests.post(url, json=data, headers=headers)
    return response.json()

# Usage
with tracer.start_as_current_span("call_inventory_service"):
    inventory_result = call_downstream_service(
        'http://inventory-service/api/reserve',
        {'items': cart.items}
    )
```

**Checklist:**
- [ ] All services instrumented with tracing
- [ ] Trace context propagated across service boundaries
- [ ] Critical paths have custom spans with attributes
- [ ] Trace sampling configured (balance overhead vs visibility)
- [ ] Jaeger or similar UI accessible

### 4.2 Trace Analysis

**Find Slow Traces:**
```sql
-- Query Jaeger for traces >1s
SELECT
    trace_id,
    operation_name,
    duration,
    start_time
FROM traces
WHERE duration > 1000000  -- 1 second in microseconds
  AND service = 'api-gateway'
  AND start_time > NOW() - INTERVAL '1 hour'
ORDER BY duration DESC
LIMIT 100;
```

**Identify Bottleneck Services:**
```sql
-- Find which service causes most latency
SELECT
    service,
    AVG(duration) as avg_duration_us,
    COUNT(*) as span_count
FROM spans
WHERE trace_id IN (SELECT trace_id FROM slow_traces)
GROUP BY service
ORDER BY avg_duration_us DESC;
```

---

## 5. Error Tracking (All Scales)

### 5.1 Sentry Integration

**Why:** Capture exceptions, stack traces, and context automatically

**Implementation:**
```python
# error_tracking.py
import sentry_sdk
from sentry_sdk.integrations.flask import FlaskIntegration
from sentry_sdk.integrations.sqlalchemy import SqlalchemyIntegration

sentry_sdk.init(
    dsn="https://your-dsn@sentry.io/project-id",
    integrations=[
        FlaskIntegration(),
        SqlalchemyIntegration(),
    ],
    environment="production",
    release=os.getenv('APP_VERSION', 'unknown'),

    # Performance monitoring (sample 10% of transactions)
    traces_sample_rate=0.1,

    # Filter sensitive data
    before_send=filter_sensitive_data
)

def filter_sensitive_data(event, hint):
    """Remove sensitive data from error reports."""
    # Remove authorization headers
    if 'request' in event and 'headers' in event['request']:
        event['request']['headers'].pop('Authorization', None)
        event['request']['headers'].pop('Cookie', None)

    # Remove sensitive form fields
    if 'request' in event and 'data' in event['request']:
        if isinstance(event['request']['data'], dict):
            event['request']['data'].pop('password', None)
            event['request']['data'].pop('credit_card', None)
            event['request']['data'].pop('ssn', None)

    return event

# Automatic error capture
@app.route('/api/user/<int:user_id>')
def get_user(user_id):
    try:
        user = User.query.get(user_id)
        return jsonify(user.to_dict())
    except Exception as e:
        # Automatically sent to Sentry with context
        sentry_sdk.capture_exception(e)
        return jsonify({'error': 'Internal error'}), 500

# Add custom context to errors
@app.before_request
def add_sentry_context():
    sentry_sdk.set_user({
        "id": getattr(request, 'user_id', None),
        "ip_address": request.remote_addr
    })

    sentry_sdk.set_tag("endpoint", request.endpoint)
    sentry_sdk.set_tag("method", request.method)
```

**Error Grouping & Alerts:**
```python
# Configure Sentry alerts
# (Done via Sentry UI or API)

# Alert when:
# - New error type appears
# - Error frequency exceeds threshold (>10/minute)
# - Error affects >100 users in 1 hour

# Send alerts to:
# - Slack (#errors channel)
# - PagerDuty (for critical errors)
# - Email (weekly digest)
```

**Checklist:**
- [ ] Error tracking configured (Sentry, Rollbar, Bugsnag)
- [ ] Sensitive data filtered from error reports
- [ ] User context included in errors
- [ ] Release tracking enabled (correlate errors with deployments)
- [ ] Alerts configured for new/frequent errors

---

## 6. Uptime Monitoring (All Scales)

### 6.1 External Health Checks

**Why:** Detect outages from user perspective (outside your infrastructure)

**Implementation:**
```python
# health_check.py - Comprehensive health check endpoint
from flask import jsonify
import psycopg2

@app.route('/health', methods=['GET'])
def health_check():
    """Comprehensive health check endpoint."""
    health = {
        'status': 'healthy',
        'timestamp': datetime.utcnow().isoformat(),
        'version': os.getenv('APP_VERSION', 'unknown'),
        'checks': {}
    }

    # Database check
    try:
        conn = psycopg2.connect(DATABASE_URL, connect_timeout=2)
        conn.close()
        health['checks']['database'] = 'healthy'
    except Exception as e:
        health['checks']['database'] = f'unhealthy: {str(e)}'
        health['status'] = 'unhealthy'

    # Cache check (Redis)
    try:
        redis_client.ping()
        health['checks']['cache'] = 'healthy'
    except Exception as e:
        health['checks']['cache'] = f'degraded: {str(e)}'
        health['status'] = 'degraded'

    # External API check (optional)
    try:
        response = requests.get('https://api.stripe.com/v1/account', timeout=2)
        health['checks']['payment_gateway'] = 'healthy' if response.status_code < 500 else 'degraded'
    except Exception:
        health['checks']['payment_gateway'] = 'degraded'

    status_code = 200 if health['status'] == 'healthy' else 503
    return jsonify(health), status_code
```

**UptimeRobot Configuration:**
```markdown
# External Monitoring Setup (UptimeRobot)

## Monitor Configuration
- **URL:** https://api.example.com/health
- **Type:** HTTP(s)
- **Interval:** 5 minutes (free tier) or 1 minute (paid)
- **Timeout:** 30 seconds
- **Success Criteria:** HTTP 200 status code

## Alert Contacts
1. **Email:** team@example.com (immediate)
2. **SMS:** +1-555-0100 (on-call phone)
3. **Slack:** #alerts webhook (immediate)
4. **PagerDuty:** Integration key (critical only)

## Alert Thresholds
- Down for >5 minutes: Trigger PagerDuty
- Down for >1 minute: Send Slack + email
- Recovering: Send all-clear notification
```

**Checklist:**
- [ ] Health check endpoint implemented
- [ ] External monitoring configured (UptimeRobot, Pingdom, etc.)
- [ ] Multi-region health checks (if multi-region deployment)
- [ ] Alerts configured for downtime
- [ ] Public status page (optional but recommended)

---

## 7. Observability Best Practices

### 7.1 Cardinality Management

**Problem:** High-cardinality labels (user IDs, request IDs) explode metric storage

**Good (Low Cardinality):**
```python
# Count requests by endpoint and status
http_requests_total = Counter(
    'http_requests_total',
    'Total HTTP requests',
    ['method', 'endpoint', 'status']
)
# Cardinality: methods (5) * endpoints (50) * statuses (10) = 2,500 time series
```

**Bad (High Cardinality):**
```python
# Count requests by user_id (BAD)
http_requests_total = Counter(
    'http_requests_total',
    'Total HTTP requests',
    ['method', 'endpoint', 'status', 'user_id']
)
# Cardinality: methods (5) * endpoints (50) * statuses (10) * users (1M) = 2.5B time series ❌
```

**Solution:** Use user_id in logs/traces, not metrics

### 7.2 Sampling Strategies

**Problem:** Full observability at scale is expensive

**Trace Sampling:**
```python
# Sample 10% of successful requests, 100% of errors
from opentelemetry.sdk.trace.sampling import TraceIdRatioBased, ParentBasedTraceIdRatio

def custom_sampler(parent_context, trace_id, name, attributes):
    """Sample all errors, 10% of successes."""
    # Always sample if error
    if attributes and attributes.get('http.status_code', 0) >= 400:
        return ALWAYS_ON

    # Sample 10% of successful requests
    return TraceIdRatioBased(0.1)
```

**Log Sampling:**
```python
# Sample verbose logs in production
import random

def should_log_debug():
    """Sample 1% of debug logs."""
    return random.random() < 0.01

if should_log_debug():
    logger.debug('Verbose debug information...')
```

---

## Summary: Monitoring & Observability Checklist

**Small-Scale (Minimum Viable Observability):**
- [ ] Uptime monitoring (UptimeRobot)
- [ ] Simple analytics (Plausible, Google Analytics)
- [ ] Error tracking (Sentry free tier)
- [ ] Server logs retained 7+ days

**Medium-Scale (Production-Grade Observability):**
- [ ] Structured logging with centralization (ELK, CloudWatch)
- [ ] Application metrics (Prometheus + Grafana)
- [ ] Infrastructure metrics (Node Exporter, CloudWatch)
- [ ] Alerting configured (critical + warning alerts)
- [ ] On-call rotation (PagerDuty)
- [ ] Logs/metrics retained 30+ days

**Large-Scale (Full Observability Stack):**
- [ ] Distributed tracing (Jaeger, X-Ray)
- [ ] SLI/SLO monitoring with error budgets
- [ ] Advanced alerting (multi-dimensional, ML-based anomaly detection)
- [ ] Capacity planning dashboards
- [ ] Cost monitoring dashboards
- [ ] Logs/metrics/traces retained 90+ days

**Universal Best Practices:**
- [ ] Golden signals monitored (latency, traffic, errors, saturation)
- [ ] Dashboards accessible to relevant teams
- [ ] Runbooks linked from alerts
- [ ] Alert fatigue prevented (meaningful alerts only)
- [ ] Monthly monitoring review (adjust thresholds, remove noise)

---

**Guide Version:** 1.0
**Last Updated:** 2025-10-27
**Related:** [MEDIUM_SCALE_READINESS.md](MEDIUM_SCALE_READINESS.md), [LARGE_SCALE_READINESS.md](LARGE_SCALE_READINESS.md), [PRODUCTION_READINESS_FRAMEWORK.md](PRODUCTION_READINESS_FRAMEWORK.md#4-monitoring--observability)
