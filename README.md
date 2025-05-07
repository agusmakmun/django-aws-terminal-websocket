# Django EC2 WebSocket Terminal

This project is a Django + Channels web application that provides a real-time, browser-based terminal using WebSockets and [xterm.js](https://xtermjs.org/). It streams interactive shell sessions—such as SSH to an EC2 instance—directly to the frontend. The stack features full distributed tracing and service performance monitoring with OpenTelemetry, Jaeger, and Grafana, covering HTTP, WebSocket, Celery, and Redis operations.

## Features
- **Django + Channels**: Uses Django Channels for WebSocket support.
- **EC2 Integration**: Ready for backend logic to stream terminal output from an AWS EC2 instance (via SSH, to be implemented in `TerminalConsumer`).
- **xterm.js Frontend**: Presents a fully interactive terminal in the browser using xterm.js.
- **Simple Django Template**: Uses a minimal HTML template for easy customization.
- **Health Check API**: `/health-check/` endpoint for monitoring and periodic Celery checks.
- **Distributed Tracing**: OpenTelemetry spans for HTTP, WebSocket, Celery, and Redis operations.
- **Service Performance Monitoring**: Grafana as dashboard to showcase the Performance Monitoring from OpenTelemetry (Jaeger).
- **Automatic Local Setup**: `docker-compose up --build` starts Uvicorn, Celery worker, Celery beat, Redis, OpenTelemetry Collector, Jaeger, Grafana (via Docker) with logs saved to `.log` files.

### Preview

![temrninal websocket](https://github.com/user-attachments/assets/91475790-be87-4f70-b87a-386d41d2829a)

![otel collector](https://github.com/user-attachments/assets/bb825cc3-f992-4d79-a29e-a96390ca32e1)

![jaeger UI](https://github.com/user-attachments/assets/6cb44bb9-88e6-44e9-bf8b-c3afa4ccfe96)

![grafana monitoring](https://github.com/user-attachments/assets/f4bd9c02-588e-407e-96dc-d1784f6ccc5b)


## Project Structure
```
django-vm-websocket/
├── manage.py
├── requirements.txt
├── Dockerfile
├── docker-compose.yml
├── README.md
├── vmwebsocket/
│   ├── __init__.py
│   ├── asgi.py
│   ├── celery.py
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
├── terminal/
│   ├── __init__.py
│   ├── apps.py
│   ├── consumers.py
│   ├── otel_http_middleware.py
│   ├── otel_redis.py
│   ├── otel_tracing.py
│   ├── otel_websocket_middleware.py
│   ├── routing.py
│   ├── tasks.py
│   ├── views.py
│   └── templates/
│       └── terminal/
│           └── terminal.html
└── db.sqlite3

# Services run via Docker Compose:
#   - django (web, worker, beat)
#   - redis (cache & broker)
#   - jaeger (tracing backend & UI)
#   - grafana (service performance monitoring UI)
```

## Setup Instructions

### 1. Clone and Prepare Environment
```bash
# Clone the repository
# cd into the project directory
python3 -m venv ../env-vm-performance
source ../env-vm-performance/bin/activate
```

### 2. Install Requirements
```bash
pip install -r requirements.txt
```
_(*for local debug only, Docker Compose is recommended for full stack)_

### 3. Run Everything Locally with Docker (Recommended)

You can run the entire stack (Django, Celery worker, Celery beat, Redis, Jaeger and Grafana) with a single command using Docker Compose:

```bash
docker-compose up --build
```

- The Django app will be available at: [http://localhost:8000/](http://localhost:8000/)
- The Jaeger UI will be available at: [http://localhost:16686/](http://localhost:16686/)
- Grafana UI will be available at: [http://localhost:3000/](http://localhost:3000/)
- Redis will be available on port 6379 (internal networking)

To stop all services, press `Ctrl+C` in the terminal running Docker Compose.

If you make code changes, you may need to rebuild:
```bash
docker-compose up --build
```

You can also run individual services (e.g., just the worker):
```bash
docker-compose run --rm celery-worker
```

### 5. Access the Terminal
Open your browser and go to [http://localhost:8000/](http://localhost:8000/)

You should see a terminal interface powered by xterm.js. Typing in the terminal will echo your input (for now).

## WebSocket & EC2 Streaming
- The WebSocket endpoint is at `/ws/terminal/`.
- The backend logic for streaming an actual EC2 shell session is in `terminal/consumers.py` (`TerminalConsumer`).
- All async methods in `TerminalConsumer` are traced with `@traced_async_class` for full observability.
- You can use `boto3` and `asyncssh` (or similar) to connect to EC2 and stream the shell output.

## EC2 SSH Configuration

To enable the backend to connect to your AWS EC2 instance via SSH, set the following:

- **Environment Variables:**
  - `AWS_HOSTNAME`: The public DNS or IP of your EC2 instance.
  - `AWS_USERNAME`: The SSH username (e.g., `ec2-user`, `ubuntu`, or `root`).

  Example:
  ```bash
  export AWS_HOSTNAME=ec2-xx-xx-xx-xx.compute-1.amazonaws.com
  export AWS_USERNAME=ec2-user
  ```

- **SSH Private Key:**
  - Place your EC2 SSH private key file as `terminal/aws.pem`.
  - Ensure the file is not tracked by git (already in `.gitignore`).

  Example:
  ```bash
  cp /path/to/your-key.pem terminal/aws.pem
  chmod 600 terminal/aws.pem
  ```

- The backend will use these settings to establish an SSH connection to your EC2 instance for the WebSocket terminal.

## Health Check API and Periodic Task

- **Health Check API:**
  - Endpoint: `/health-check/`
  - Method: `GET`
  - Response: `{ "status": "ok" }`
  - Use this endpoint to verify the service is running (for load balancers, monitoring, etc).
  - Example:
    ```bash
    curl http://localhost:8000/health-check/
    ```

- **Celery Periodic Health Check:**
  - A Celery task (`health_check_task`) runs every minute (scheduled by Celery Beat).
  - The task calls the health check API and logs the result.
  - The task is traced with OpenTelemetry: you will see both a Celery task span and a nested span for the function logic (via `@traced_function`).
  - You can view logs in `celery-worker.log` and `celery-beat.log`.

## Customization
- **Frontend**: Edit `terminal/templates/terminal/terminal.html` to customize the look or add features.
- **Backend**: Extend `TerminalConsumer` to handle authentication, EC2 connection, and streaming.

## Requirements

The following Python packages are required for full functionality:

- django>=5.2
- celery>=5.0
- channels>=4.0
- boto3>=1.38
- asyncssh>=2.14
- uvicorn[standard]>=0.20
- opentelemetry-api>=1.24.0
- opentelemetry-sdk>=1.24.0
- opentelemetry-instrumentation-django>=0.44b0
- opentelemetry-exporter-otlp>=1.24.0
- opentelemetry-instrumentation-redis==0.53b1
- opentelemetry-instrumentation-celery==0.53b1
- requests==2.32.3
- redis==6.0.0
- django-redis==5.4.0

Install all dependencies with:
```bash
pip install -r requirements.txt
```

## License
MIT or your preferred license.

## Running with ASGI Servers

This project requires an ASGI server to support WebSockets. You can use either Daphne or Uvicorn:

### Using Uvicorn (for manual run)
```bash
uvicorn vmwebsocket.asgi:application --host 0.0.0.0 --port 8000
```
**Note:** Do not use `python manage.py runserver` for WebSocket support.

## OpenTelemetry Tracing

This project supports distributed tracing with [OpenTelemetry](https://opentelemetry.io/) for Django, Celery, and Redis. Traces are exported to Jaeger (all-in-one) for visualization and analysis. For advanced service performance monitoring, Grafana is included and can be connected to Jaeger as a data source. Dashboards and SPM can be built in Grafana using Jaeger as a data source.

1. Install the requirements (for local debug only):
   ```bash
   pip install -r requirements.txt
   ```
2. Set the following environment variables before starting your server (for local debug only):
   ```bash
   export ENABLE_OTEL=1
   export OTEL_SERVICE_NAME=django-vm-websocket  # or your preferred service name
   export OTEL_EXPORTER_OTLP_ENDPOINT=http://localhost:4318/v1/traces  # or your Jaeger endpoint
   ```
3. Run the stack with Docker Compose:
   ```bash
   docker-compose up --build
   ```
4. View traces in Jaeger UI ([http://localhost:16686/](http://localhost:16686/)) and analyze service performance in Grafana ([http://localhost:3000/](http://localhost:3000/)).

## Troubleshooting OpenTelemetry Collector Connection

_This section is only relevant if you are running a standalone OpenTelemetry Collector. For most users, Jaeger all-in-one via Docker Compose is sufficient and recommended._

## Class-Level Tracing with OpenTelemetry

This project provides decorators to automatically trace all methods in a class:

- `@traced_class`: Traces all synchronous (non-async) methods in a class.
- `@traced_async_class`: Traces all asynchronous (async) methods in a class.

These decorators automatically create OpenTelemetry spans for each method call,
record exceptions, and set span status. This reduces boilerplate and ensures
consistent tracing across your codebase.

**Usage Example (sync):**

```python
from terminal.otel_tracing import traced_class

@traced_class
class MySyncClass:
    def foo(self, x):
        return x * 2
```

**Usage Example (async):**

```python
from terminal.otel_tracing import traced_async_class

@traced_async_class
class MyAsyncClass:
    async def bar(self, y):
        return y + 1
```

- Use `@traced_class` for classes with regular (synchronous) methods.
- Use `@traced_async_class` for classes with async methods (e.g., Channels consumers).
- You can still use `@traced_function` or `@traced_async_function` on individual
  methods if you want more control or need to customize span names.

See `terminal/otel_tracing.py` for full details and docstrings.

## Redis OpenTelemetry Tracing (Advanced)

This project provides **comprehensive OpenTelemetry tracing for all Redis operations**, including both direct Redis usage and Django cache operations.

### Features

- **Global Redis Span Enrichment:**  
  All Redis spans (created by `opentelemetry-instrumentation-redis`) are automatically enriched with:
  - The Redis command, key, and argument length.
  - The caller's function, file, and line number (if the operation was triggered via Django's cache API).
  - Custom events and error attributes for enhanced traceability.

- **Automatic Django Cache Instrumentation:**  
  The Django cache backend (`cache.get`, `cache.set`, `cache.delete`) is monkey-patched at startup to automatically add caller context to the current OpenTelemetry span—no manual code changes needed in your views or tasks.

- **Unified Setup:**  
  All Redis OpenTelemetry enhancements are managed in `terminal/otel_redis.py`.  
  In your `settings.py`, you simply call:
  ```python
  from terminal.otel_redis import setup_redis_otel
  setup_redis_otel(provider)
  ```
  after setting up your OpenTelemetry provider.

- **Error Handling:**  
  All enrichment logic is wrapped in exception handling, so tracing is never broken by enrichment errors.

### Example Trace

A Redis span in your traces will include:
- `db.system: redis`
- `db.statement: SET ? ? ? ?`
- `custom.global_redis_tag: django-vm-websocket`
- `custom.redis.caller_function: health_check_view`
- `custom.redis.caller_file: /path/to/views.py`
- `custom.redis.caller_line: 15`
- Custom event: `"Global Redis operation"` with all the above details

### Requirements

- `opentelemetry-instrumentation-redis`
- `django-redis` (for Django cache backend)
- All other OpenTelemetry and Django dependencies (see requirements.txt)

### How it works

- **No manual context management is needed.**  
  All cache operations and direct Redis usage are automatically traced and enriched.
- **You can view these spans in your OpenTelemetry backend or the collector logs.**

## 📽️ Running the Slidev Presentation

This project includes a Slidev presentation (`slides.md`) to help you understand and demo the OpenTelemetry integration.

### 1. Install Slidev

**Locally (recommended):**

```bash
npm install --save-dev @slidev/cli
```

Or with yarn:

```bash
yarn add -D @slidev/cli
```

**Globally (optional):**

```bash
npm install -g @slidev/cli
```

### 2. Run the Presentation

If installed locally:

```bash
npx slidev
```

Or with yarn:

```bash
yarn slidev
```

If installed globally:

```bash
slidev
```

This will open an interactive presentation in your browser using the `slides.md` file.

## Service Performance Monitoring with Grafana

Grafana is included in the Docker Compose setup for advanced service performance monitoring and trace analysis.

- **Access Grafana:** [http://localhost:3000/](http://localhost:3000/) (default user: `admin`, password: `admin`)
- **Add Jaeger as a data source:**
  1. Go to **Settings** → **Data Sources** → **Add data source**
  2. Search for **Jaeger** and select it
  3. Set the **URL** to `http://jaeger:16686`
  4. Click **Save & Test**
- **Explore traces:**
  - Go to **Explore** in Grafana
  - Select the **Jaeger** data source
  - Search, filter, and analyze traces for your Django, WebSocket, Celery, and Redis operations

You can build dashboards and panels to visualize trace counts, durations, and error rates. For full SPM, consider adding Prometheus and OpenTelemetry metrics.
