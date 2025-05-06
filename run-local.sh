#!/bin/bash

# OpenTelemetry environment variables
export ENABLE_OTEL=1
export OTEL_SERVICE_NAME="django-vm-websocket"  # or your preferred service name
export OTEL_EXPORTER_OTLP_ENDPOINT="http://localhost:4318/v1/traces"  # or your collector endpoint

# Start Redis with Docker if not already running
if [ "$(docker ps -q -f name=local-redis)" ]; then
  echo "Redis container 'local-redis' already running."
elif [ "$(docker ps -aq -f status=exited -f name=local-redis)" ]; then
  echo "Starting existing stopped Redis container 'local-redis' ..."
  docker start local-redis
else
  echo "Starting new Redis container 'local-redis' on port 6379 ..."
  docker run -d -p 6379:6379 --name local-redis redis
fi

# Run Django (Uvicorn), Celery worker, and Celery beat for local development

# Start Uvicorn (Django ASGI server)
echo "Starting Uvicorn (Django ASGI server) on http://localhost:8000 ..."
uvicorn vmwebsocket.asgi:application --host 0.0.0.0 --port 8000 2>&1 | tee uvicorn.log &
UVICORN_PID=$!

# Start Celery worker
echo "Starting Celery worker ..."
celery -A vmwebsocket worker --loglevel=info 2>&1 | tee celery-worker.log &
CELERY_WORKER_PID=$!

# Start Celery beat
echo "Starting Celery beat ..."
celery -A vmwebsocket beat --loglevel=info 2>&1 | tee celery-beat.log &
CELERY_BEAT_PID=$!

# Trap Ctrl+C and kill all background jobs
trap "echo 'Stopping...'; kill $UVICORN_PID $CELERY_WORKER_PID $CELERY_BEAT_PID; exit 0" SIGINT

echo "All services started. Press Ctrl+C to stop."
echo "Logs: uvicorn.log, celery-worker.log, celery-beat.log"

# Wait for background jobs
wait
