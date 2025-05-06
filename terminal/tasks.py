import logging
import requests
from celery import shared_task
from django.conf import settings
from terminal.otel_tracing import traced_function

logger = logging.getLogger(__name__)


@shared_task
@traced_function()
def health_check_task():
    url = settings.HEALTH_CHECK_URL
    try:
        response = requests.get(url, timeout=10)
        logger.info(
            f"Health check status: {response.status_code}, body: {response.text}"
        )
    except Exception as e:
        logger.error(f"Health check failed: {e}")
