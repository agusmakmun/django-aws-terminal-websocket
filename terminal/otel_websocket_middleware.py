"""
OpenTelemetry middleware for Django Channels WebSocket connections.
Handles context propagation, span creation, and error recording for WebSocket events.
"""

import json
from opentelemetry import trace, context as otel_context
from opentelemetry.trace.propagation.tracecontext import TraceContextTextMapPropagator
from opentelemetry.trace.status import Status, StatusCode

tracer = trace.get_tracer(__name__)


class OpenTelemetryWebSocketMiddleware:
    """
    ASGI middleware for WebSocket context propagation and tracing.

    - Extracts and injects trace context for distributed tracing.
    - Creates spans for websocket.connect, websocket.session, websocket.accept, websocket.disconnect, websocket.close.
    - Records errors and sets status codes for all major WebSocket lifecycle events.
    - Ensures all WebSocket events are properly linked in a single trace.

    Usage:
        Add this middleware to your ASGI application for Channels WebSocket support.
        Example:
            application = ProtocolTypeRouter({
                "http": get_asgi_application(),
                "websocket": OpenTelemetryWebSocketMiddleware(URLRouter(websocket_urlpatterns)),
            })
    """

    def __init__(self, app):
        """
        Initialize the middleware with the given ASGI app.
        :param app: The ASGI application to wrap.
        """
        self.app = app

    async def __call__(self, scope, receive, send):
        """
        ASGI entrypoint. Handles context extraction, span creation, and error recording
        for all WebSocket events in the connection lifecycle.
        :param scope: The ASGI scope dictionary.
        :param receive: The ASGI receive callable.
        :param send: The ASGI send callable.
        """
        # If this is a connect event, create a root span and store its context
        if scope["type"] == "websocket":
            if not scope.get("otel_context"):
                with tracer.start_as_current_span("websocket.connect") as span:
                    ctx = trace.set_span_in_context(span)
                    scope["otel_context"] = ctx
                    span.set_status(
                        Status(
                            StatusCode.OK, "WebSocket connect completed successfully"
                        )
                    )

        extracted_context = None
        first_message = None
        first_message_ready = False

        async def otel_receive():
            nonlocal extracted_context, first_message, first_message_ready
            if not first_message_ready:
                # Prime the first message
                first_message = await receive()
                first_message_ready = True
                # Extract context for text WebSocket messages
                if first_message.get(
                    "type"
                ) == "websocket.receive" and first_message.get("text"):
                    try:
                        msg = json.loads(first_message["text"])
                        if isinstance(msg, dict) and "traceparent" in msg:
                            carrier = {"traceparent": msg["traceparent"]}
                            extracted_context = TraceContextTextMapPropagator().extract(
                                carrier
                            )
                            scope["otel_context"] = extracted_context
                    except Exception:
                        pass
                # Trace websocket.accept, disconnect, close events
                ctx = scope.get("otel_context")
                if first_message.get("type") == "websocket.accept":
                    with tracer.start_as_current_span(
                        "websocket.accept", context=ctx
                    ) as span:
                        span.set_status(Status(StatusCode.OK))
                elif first_message.get("type") == "websocket.disconnect":
                    with tracer.start_as_current_span(
                        "websocket.disconnect", context=ctx
                    ) as span:
                        span.set_attribute("ws.code", first_message.get("code"))
                        span.set_status(Status(StatusCode.OK))
                elif first_message.get("type") == "websocket.close":
                    with tracer.start_as_current_span(
                        "websocket.close", context=ctx
                    ) as span:
                        span.set_status(Status(StatusCode.OK))
                return first_message
            else:
                message = await receive()
                # Trace websocket.accept, disconnect, close events
                ctx = scope.get("otel_context")
                if message.get("type") == "websocket.accept":
                    with tracer.start_as_current_span(
                        "websocket.accept", context=ctx
                    ) as span:
                        span.set_status(Status(StatusCode.OK))
                elif message.get("type") == "websocket.disconnect":
                    with tracer.start_as_current_span(
                        "websocket.disconnect", context=ctx
                    ) as span:
                        span.set_attribute("ws.code", message.get("code"))
                        span.set_status(Status(StatusCode.OK))
                elif message.get("type") == "websocket.close":
                    with tracer.start_as_current_span(
                        "websocket.close", context=ctx
                    ) as span:
                        span.set_status(Status(StatusCode.OK))
                return message

        async def otel_send(message):
            if message.get("type") == "websocket.send" and message.get("text"):
                try:
                    msg = json.loads(message["text"])
                    carrier = {}
                    TraceContextTextMapPropagator().inject(carrier)
                    if "traceparent" in carrier:
                        msg["traceparent"] = carrier["traceparent"]
                        message["text"] = json.dumps(msg)
                except Exception:
                    pass
            await send(message)

        # Prime the first message and extract context
        await otel_receive()
        # Use the context from the scope (set by connect or receive)
        ctx = scope.get("otel_context")
        token = None
        if ctx is not None:
            token = otel_context.attach(ctx)
        try:
            with tracer.start_as_current_span(
                "websocket.session", context=ctx
            ) as session_span:
                first = True

                async def receive_with_first():
                    nonlocal first, first_message, first_message_ready
                    if first and first_message_ready:
                        first = False
                        return first_message
                    return await receive()

                try:
                    await self.app(scope, receive_with_first, otel_send)
                    session_span.set_status(
                        Status(
                            StatusCode.OK,
                            "WebSocket session completed successfully",
                        )
                    )
                except Exception as e:
                    session_span.record_exception(e)
                    session_span.set_status(Status(StatusCode.ERROR, str(e)))
                    raise
        finally:
            if token is not None:
                otel_context.detach(token)
