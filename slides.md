# Effortless Django Observability: OpenTelemetry, Jaeger, and Grafana

---

## The Problem

&nbsp;

- Django apps are powerful, but:
  - Debugging across HTTP, WebSocket, Celery, and Redis is hard.
  - Traditional logging is fragmented and hard to correlate.
  - Distributed systems need distributed tracing and service performance monitoring.

<!--
notes: |
  - Introduce the pain points of debugging and monitoring in modern Django apps.
  - Emphasize the complexity of distributed systems and the need for unified observability.
-->

---

## The Solution

&nbsp;

**OpenTelemetry + Jaeger + Grafana**
- Open standard for distributed tracing and metrics.
- Works with Django, Celery, Redis, and more.
- Visualize traces in Jaeger, build dashboards in Grafana.

<!--
notes: |
  - Explain what OpenTelemetry is and why it's the new standard.
  - Mention that Jaeger and Grafana are popular open-source tools for tracing and dashboards.
-->

---

## OpenTelemetry in Django _(Tracing)_

&nbsp;

### Before using wrapper

```python
from django.http import JsonResponse
from opentelemetry import trace

tracer = trace.get_tracer(__name__)

def hello_view(request):
    with tracer.start_as_current_span("hello_view") as span:
        span.set_attribute("custom.greeting", "Hello, world!")
        return JsonResponse({"message": "Hello, world!"})
```

&nbsp;

### After using wrapper

```python
from django.http import JsonResponse
from terminal.otel_tracing import traced_function

@traced_function()
def hello_view(request):
    return JsonResponse({"message": "Hello, world!"})
```

<!--
notes: |
  - Show a real example from the project using @traced_function for tracing.
  - Explain that cache operations are also enriched with caller info and custom attributes.
  - Mention that all requests to these views are automatically traced and visible in Jaeger/Grafana.
-->

---

## The Demo App

&nbsp;

- Real-time browser terminal for EC2 (Django + Channels + xterm.js)
- Streams SSH sessions to the browser
- Full OpenTelemetry tracing for:
  - HTTP requests
  - WebSocket events
  - Celery tasks
  - Redis/cache operations
- Service Performance Monitoring with Grafana dashboards

<!--
notes: |
  - Briefly describe the demo app and its real-world use case.
  - Highlight the breadth of tracing: HTTP, WebSocket, Celery, Redis.
-->

---

![otel collector](https://github.com/user-attachments/assets/bb825cc3-f992-4d79-a29e-a96390ca32e1)

---

## How Easy Is It?

&nbsp;

### 1. Clone and Run with Docker Compose

```bash
git clone git@github.com:agusmakmun/django-aws-terminal-websocket.git
cd django-vm-websocket
docker-compose up --build
```

_or visit this for more_ https://github.com/agusmakmun/django-aws-terminal-websocket

<!--
notes: |
  - Emphasize the simplicity: one command to run the full stack.
  - Mention that Docker Compose handles all dependencies and services.
-->

---

### 2. Access the Stack

&nbsp;

- Django app: [http://localhost:8000/](http://localhost:8000/)
- Jaeger UI: [http://localhost:16686/](http://localhost:16686/)
- Grafana UI: [http://localhost:3000/](http://localhost:3000/) (admin/admin)

<!--
notes: |
  - Show how easy it is to access each part of the stack.
  - Mention default credentials for Grafana.
-->

---

### 3. Add Jaeger as a Data Source in Grafana

&nbsp;

1. Go to **Settings** → **Data Sources** → **Add data source**
2. Search for **Jaeger** and select it
3. Set the **URL** to `http://jaeger:16686`
4. Click **Save & Test**

<!--
notes: |
  - Walk through the steps to connect Jaeger to Grafana.
  - Explain that this enables trace visualization in dashboards.
-->

---

## What Do You Get?

- **Automatic tracing** for all HTTP, WebSocket, Celery, and Redis operations.
- **Rich context**: function, file, line, arguments, and even business context.
- **No manual context management** for cache or Redis.
- **Error handling**: Tracing never breaks your app.
- **Dashboards**: Visualize trace counts, durations, and error rates in Grafana.

<!--
notes: |
  - Summarize the benefits of automatic tracing and context enrichment.
  - Mention that error handling is built-in and dashboards are easy to build.
-->

---

## Example Trace in Jaeger

- See every request, WebSocket event, Celery task, and Redis command in a single trace.
- Drill down to see:
  - Which view or task triggered a Redis call
  - Arguments, return values, and errors
  - End-to-end latency and bottlenecks

![jaeger UI](https://github.com/user-attachments/assets/6cb44bb9-88e6-44e9-bf8b-c3afa4ccfe96)

<!--
notes: |
  - Show a real trace in Jaeger and explain how to interpret it.
  - Point out the critical path, errors, and context-rich spans.
-->

---

## Example Dashboard in Grafana

- Build dashboards and panels to visualize trace counts, durations, and error rates.
- For full SPM, consider adding Prometheus and OpenTelemetry metrics.

![grafana monitoring](https://github.com/user-attachments/assets/f4bd9c02-588e-407e-96dc-d1784f6ccc5b)

<!--
notes: |
  - Show a Grafana dashboard and explain what metrics are visualized.
  - Mention that you can combine traces and metrics for full SPM.
-->

---

## Advanced: Custom Enrichment

- Add your own attributes/events to spans (e.g., user ID, business context)
- Monkey-patch cache methods for global enrichment
- All Redis enrichment logic in: `terminal/otel_redis.py`
- General function/class tracing in: `terminal/otel_tracing.py`
- HTTP and WebSocket context propagation in: `terminal/otel_http_middleware.py` and `terminal/otel_websocket_middleware.py`
- Custom attributes and events appear in Jaeger trace details and can be used for filtering, search, and Grafana dashboards.

<!--
notes: |
  - Explain how custom enrichment works and why it's powerful.
  - Mention that all enrichment logic is centralized and easy to extend.
  - Show how custom attributes appear in Jaeger and Grafana.
-->

---

## Zero Effort, Maximum Insight

- No more scattered logs
- No more guessing where the bottleneck is
- One trace, full story
- One dashboard, full performance view

<!--
notes: |
  - Emphasize the value of unified observability.
  - Highlight the reduction in manual debugging effort.
-->

---

## Try It Yourself!

- Clone the repo (https://github.com/agusmakmun/django-aws-terminal-websocket)
- Run `docker-compose up --build`
- Open your browser, interact, and watch the traces flow in Jaeger and Grafana

<!--
notes: |
  - Encourage the audience to try the demo themselves.
  - Mention that everything is automated with Docker Compose.
-->

---

## Q&A

- Ask me anything about Django, OpenTelemetry, Jaeger, Grafana, or real-world observability!

<!--
notes: |
  - Invite questions and discussion.
  - Be ready to demo or dive deeper into any part of the stack.
-->

---

<!--
notes: |
  - Emphasize how little code is needed for deep insight.
  - Demo the live trace view if possible.
  - Highlight the unified, automatic enrichment for Redis and cache.
  - Mention that this approach works for any Django app, not just terminals.
--> 