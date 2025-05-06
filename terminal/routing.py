from django.urls import re_path, path
from . import consumers
from terminal.views import health_check_view

websocket_urlpatterns = [
    re_path(r"ws/terminal/$", consumers.TerminalConsumer.as_asgi()),
]

urlpatterns = [
    path("health-check/", health_check_view, name="health-check"),
]
