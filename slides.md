# Effortless Django Observability: OpenTelemetry, Jaeger, and Grafana

---

## The Problem

- Django apps are powerful, but:
  - Debugging across HTTP, WebSocket, Celery, and Redis is hard.
  - Traditional logging is fragmented and hard to correlate.
  - Distributed systems need distributed tracing and service performance monitoring.

---

## The Solution

**OpenTelemetry + Jaeger + Grafana**
- Open standard for distributed tracing and metrics.
- Works with Django, Celery, Redis, and more.
- Visualize traces in Jaeger, build dashboards in Grafana.

---

## The Demo App

- Real-time browser terminal for EC2 (Django + Channels + xterm.js)
- Streams SSH sessions to the browser
- Full OpenTelemetry tracing for:
  - HTTP requests
  - WebSocket events
  - Celery tasks
  - Redis/cache operations
- Service Performance Monitoring with Grafana dashboards

---

## How Easy Is It?

### 1. Clone and Run with Docker Compose

```bash
git clone <repo-url>
cd django-vm-websocket
docker-compose up --build
```

---

### 2. Access the Stack

- Django app: [http://localhost:8000/](http://localhost:8000/)
- Jaeger UI: [http://localhost:16686/](http://localhost:16686/)
- Grafana UI: [http://localhost:3000/](http://localhost:3000/) (admin/admin)

---

### 3. Add Jaeger as a Data Source in Grafana

1. Go to **Settings** → **Data Sources** → **Add data source**
2. Search for **Jaeger** and select it
3. Set the **URL** to `http://jaeger:16686`
4. Click **Save & Test**

---

## What Do You Get?

- **Automatic tracing** for all HTTP, WebSocket, Celery, and Redis operations.
- **Rich context**: function, file, line, arguments, and even business context.
- **No manual context management** for cache or Redis.
- **Error handling**: Tracing never breaks your app.
- **Dashboards**: Visualize trace counts, durations, and error rates in Grafana.

---

## Example Trace in Jaeger

- See every request, WebSocket event, Celery task, and Redis command in a single trace.
- Drill down to see:
  - Which view or task triggered a Redis call
  - Arguments, return values, and errors
  - End-to-end latency and bottlenecks

![jaeger UI](https://github.com/user-attachments/assets/6cb44bb9-88e6-44e9-bf8b-c3afa4ccfe96)

---

## Example Dashboard in Grafana

- Build dashboards and panels to visualize trace counts, durations, and error rates.
- For full SPM, consider adding Prometheus and OpenTelemetry metrics.

![grafana monitoring](https://github.com/user-attachments/assets/f4bd9c02-588e-407e-96dc-d1784f6ccc5b)

---

## Advanced: Custom Enrichment

- Add your own attributes/events to spans (e.g., user ID, business context)
- Monkey-patch cache methods for global enrichment
- All Redis enrichment logic in: `terminal/otel_redis.py`
- General function/class tracing in: `terminal/otel_tracing.py`
- HTTP and WebSocket context propagation in: `terminal/otel_http_middleware.py` and `terminal/otel_websocket_middleware.py`
- Custom attributes and events appear in Jaeger trace details and can be used for filtering, search, and Grafana dashboards.

---

## Zero Effort, Maximum Insight

- No more scattered logs
- No more guessing where the bottleneck is
- One trace, full story
- One dashboard, full performance view

---

## Try It Yourself!

- Clone the repo
- Run `docker-compose up --build`
- Open your browser, interact, and watch the traces flow in Jaeger and Grafana

---

## Q&A

- Ask me anything about Django, OpenTelemetry, Jaeger, Grafana, or real-world observability!

---

<!--
notes: |
  - Emphasize how little code is needed for deep insight.
  - Demo the live trace view if possible.
  - Highlight the unified, automatic enrichment for Redis and cache.
  - Mention that this approach works for any Django app, not just terminals.
--> 