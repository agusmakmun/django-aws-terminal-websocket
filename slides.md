# Effortless Django Logging: OpenTelemetry Will Blow Your Mind!

---

## The Problem

- Django apps are powerful, but:
  - Debugging across HTTP, WebSocket, Celery, and Redis is hard.
  - Traditional logging is fragmented and hard to correlate.
  - Distributed systems need distributed tracing.

---

## The Solution

**OpenTelemetry**
- Open standard for distributed tracing and metrics.
- Works with Django, Celery, Redis, and more.
- Visualize traces in Jaeger, Tempo, Honeycomb, etc.

---

## The Demo App

- Real-time browser terminal for EC2 (Django + Channels + xterm.js)
- Streams SSH sessions to the browser
- Full OpenTelemetry tracing for:
  - HTTP requests
  - WebSocket events
  - Celery tasks
  - Redis/cache operations

---

## How Easy Is It?

### 1. Install a few packages

```bash
pip install django opentelemetry-api opentelemetry-sdk \
  opentelemetry-instrumentation-django opentelemetry-instrumentation-redis \
  opentelemetry-instrumentation-celery django-redis
```

---

### 2. Add a few lines to settings.py

```python
if os.getenv("ENABLE_OTEL", "0") == "1":
    # ... OpenTelemetry setup ...
    from terminal.otel_redis import setup_redis_otel
    setup_redis_otel(provider)
```

---

### 3. Run the OpenTelemetry Collector

```bash
docker run --rm -p 4318:4318 otel/opentelemetry-collector:latest
```

---

## What Do You Get?

- **Automatic tracing** for all HTTP, WebSocket, Celery, and Redis operations.
- **Rich context**: function, file, line, arguments, and even business context.
- **No manual context management** for cache or Redis.
- **Error handling**: Tracing never breaks your app.

---

## Example Trace

- See every request, WebSocket event, Celery task, and Redis command in a single trace.
- Drill down to see:
  - Which view or task triggered a Redis call
  - Arguments, return values, and errors
  - End-to-end latency and bottlenecks

![image](https://github.com/user-attachments/assets/bb825cc3-f992-4d79-a29e-a96390ca32e1)

---

## Advanced: Custom Enrichment

- Add your own attributes/events to spans (e.g., user ID, business context)
- Monkey-patch cache methods for global enrichment
- All logic in one place: `terminal/otel_redis.py`

---

## Zero Effort, Maximum Insight

- No more scattered logs
- No more guessing where the bottleneck is
- One trace, full story

---

## Try It Yourself!

- Clone the repo
- Run `./run-local.sh` and the collector
- Open your browser, interact, and watch the traces flow

---

## Q&A

- Ask me anything about Django, OpenTelemetry, or real-world observability!

---

<!--
notes: |
  - Emphasize how little code is needed for deep insight.
  - Demo the live trace view if possible.
  - Highlight the unified, automatic enrichment for Redis and cache.
  - Mention that this approach works for any Django app, not just terminals.
--> 