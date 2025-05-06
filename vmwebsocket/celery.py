import os
from celery import Celery

# Set the default Django settings module for the 'celery' program.
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "vmwebsocket.settings")

app = Celery("vmwebsocket")

# Using a string here means the worker doesn't have to serialize
# the configuration object to child processes.
app.config_from_object("django.conf:settings", namespace="CELERY")

# Load task modules from all registered Django app configs.
app.autodiscover_tasks()

# OpenTelemetry instrumentation for Celery is handled in settings.py

if os.getenv("ENABLE_OTEL", "0") == "1":
    try:
        from opentelemetry.instrumentation.celery import CeleryInstrumentor

        CeleryInstrumentor().instrument()
    except ImportError:
        pass  # Celery instrumentation not available
