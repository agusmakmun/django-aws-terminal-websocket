# Django EC2 WebSocket Terminal

This project is a Django-based web application that provides a browser-based terminal interface using WebSockets and [xterm.js](https://xtermjs.org/). It is designed to stream terminal sessions (e.g., from an EC2 instance) to the frontend in real time.

## Features
- **Django + Channels**: Uses Django Channels for WebSocket support.
- **EC2 Integration**: Ready for backend logic to stream terminal output from an AWS EC2 instance (via SSH, to be implemented in `TerminalConsumer`).
- **xterm.js Frontend**: Presents a fully interactive terminal in the browser using xterm.js.
- **Simple Django Template**: Uses a minimal HTML template for easy customization.
- **Health Check API**: `/health-check/` endpoint for monitoring and periodic Celery checks.
- **Distributed Tracing**: OpenTelemetry spans for HTTP, WebSocket, Celery, and Redis operations.
- **Automatic Local Setup**: `run-local.sh` starts Uvicorn, Celery worker, Celery beat, and Redis (via Docker) with logs saved to `.log` files.

### Preview

<img width="1054" alt="image" src="https://github.com/user-attachments/assets/91475790-be87-4f70-b87a-386d41d2829a" />

![image](https://github.com/user-attachments/assets/bb825cc3-f992-4d79-a29e-a96390ca32e1)


## Project Structure
```
django-vm-websocket/
├── manage.py
├── requirements.txt
├── run-local.sh
├── vmwebsocket/
│   ├── asgi.py
│   ├── celery.py  # Celery app definition
│   ├── settings.py
│   ├── urls.py
│   └── ...
├── terminal/
│   ├── consumers.py
│   ├── routing.py
│   ├── tasks.py
│   ├── views.py
│   ├── otel_tracing.py
│   └── templates/terminal/terminal.html
└── ...
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

### 3. Run Migrations
```bash
python manage.py migrate
```

### 4. Run Everything Locally (Recommended)

Open **two terminals**:

- **Terminal 1:**
  ```bash
  docker run --rm -p 4318:4318 otel/opentelemetry-collector:latest
  ```
  This starts the OpenTelemetry Collector to receive and forward traces.

- **Terminal 2:**
  ```bash
  ./run-local.sh
  ```
  This script starts Uvicorn (Django ASGI), Celery worker, Celery beat, and a Redis container (named `local-redis`) via Docker if not already running.
  Logs are saved to `uvicorn.log`, `celery-worker.log`, and `celery-beat.log` (all ignored by git).
  Press Ctrl+C to stop all services. The Redis container will remain running unless you stop it with `docker stop local-redis`.

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
- Python 3.8+
- Django 5.2+
- channels 4.0+
- celery>=5.0
- boto3 1.38+
- asyncssh>=2.14
- uvicorn[standard]>=0.20
- requests
- redis (for Celery broker and cache)
- opentelemetry-api, opentelemetry-sdk, opentelemetry-instrumentation-django, opentelemetry-instrumentation-celery, opentelemetry-instrumentation-redis, opentelemetry-exporter-otlp

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

This project supports distributed tracing with [OpenTelemetry](https://opentelemetry.io/) for Django, Celery, and Redis. To enable tracing:

1. Install the requirements:
   ```bash
   pip install -r requirements.txt
   ```
2. Set the following environment variables before starting your server:
   ```bash
   export ENABLE_OTEL=1
   export OTEL_SERVICE_NAME=django-vm-websocket  # or your preferred service name
   export OTEL_EXPORTER_OTLP_ENDPOINT=http://localhost:4318/v1/traces  # or your collector endpoint
   ```
3. Start the OpenTelemetry Collector locally using Docker:
   ```bash
   docker run --rm -p 4318:4318 otel/opentelemetry-collector:latest
   ```
   This will start the collector with a default configuration that accepts traces on port 4318.

4. Start your Django server as usual (e.g., with `./run-local.sh` or `uvicorn`).

Traces will be sent to the configured OTLP endpoint. You can use [OpenTelemetry Collector](https://opentelemetry.io/docs/collector/) or a compatible backend (like Jaeger, Tempo, or Honeycomb) to receive and visualize traces.

## Troubleshooting OpenTelemetry Collector Connection

If you have issues connecting to the OpenTelemetry Collector at `http://localhost:4318/v1/traces`, follow these steps:

1. **Collector is running, but curl GET fails:**
   - `curl -v http://localhost:4318/v1/traces` will result in `Recv failure: Connection reset by peer`. This is **expected** because the endpoint only accepts POST requests with a specific payload.

2. **Test with a POST request:**
   - Run: `curl -X POST http://localhost:4318/v1/traces -d '{}'`
   - If the collector is running and the OTLP HTTP receiver is enabled, you should get a response like `400 Bad Request` or `415 Unsupported Media Type`. If you still get `Recv failure: Connection reset by peer`, the collector is not accepting connections as expected.

3. **Check the collector config is loaded:**
   - Run: `docker run --rm -v $(pwd)/otel-collector-config.yaml:/etc/otelcol/config.yaml otel/opentelemetry-collector:latest cat /etc/otelcol/config.yaml`
   - You should see the contents of your config file. If not, the volume mount is not working.

4. **Try running the collector without your config:**
   - Run: `docker run --rm -p 4318:4318 otel/opentelemetry-collector:latest`
   - Then test with the POST request above. If you get a different error, the collector is working and the issue is with your config or volume mount.

5. **Check for port conflicts:**
   - Run: `lsof -i :4318` to make sure nothing else is using the port.

6. **Try a different collector image version:**
   - Run: `docker run --rm -p 4318:4318 -p 4317:4317 -v $(pwd)/otel-collector-config.yaml:/etc/otelcol/config.yaml otel/opentelemetry-collector:0.93.0`

If you follow these steps and still have issues, check the logs from both the collector and your Django app for errors, and ensure your environment variables are set in the same shell as your Django process.

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
