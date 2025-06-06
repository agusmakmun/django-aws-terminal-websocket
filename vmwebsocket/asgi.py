"""
ASGI config for vmwebsocket project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.2/howto/deployment/asgi/
"""

import os

from channels.routing import ProtocolTypeRouter, URLRouter
from django.core.asgi import get_asgi_application
from terminal.routing import websocket_urlpatterns
from terminal.otel_websocket_middleware import OpenTelemetryWebSocketMiddleware

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "vmwebsocket.settings")

application = ProtocolTypeRouter(
    {
        "http": get_asgi_application(),
        "websocket": OpenTelemetryWebSocketMiddleware(URLRouter(websocket_urlpatterns)),
    }
)
