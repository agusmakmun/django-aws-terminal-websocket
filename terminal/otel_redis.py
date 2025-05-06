"""
OpenTelemetry enhancements for Redis in Django projects.

- CustomRedisSpanProcessor: Adds global attributes and events to all Redis spans,
  including caller info if available. Handles errors gracefully.
- Monkey-patches Django cache methods (get, set, delete) to automatically enrich
  the current span with caller function, file, and line number.
- setup_redis_otel(provider): Registers the span processor and applies the cache
  patch. Call this from your Django settings after setting up the OTEL provider.

Note: The span processor identifies Redis spans by checking for the standard
OpenTelemetry attribute 'db.system' == 'redis', which is set automatically by
opentelemetry-instrumentation-redis according to the OpenTelemetry semantic
conventions for databases.
"""

import inspect
from django.core.cache import cache
from opentelemetry import trace
from opentelemetry.sdk.trace import SpanProcessor


# --- Span Processor for all Redis spans ---
class CustomRedisSpanProcessor(SpanProcessor):
    """
    OpenTelemetry SpanProcessor that enriches all Redis spans with global
    attributes, caller info (if available), and custom events. Handles errors
    gracefully.

    Only processes spans where span.attributes['db.system'] == 'redis', as set
    by the OpenTelemetry Redis instrumentation according to the semantic
    conventions.
    """

    def on_start(self, span, parent_context):
        pass

    def on_end(self, span):
        """
        Enrich Redis spans with custom attributes and events. If an error occurs
        during enrichment, record it as a span attribute.
        """
        if span.attributes.get("db.system") == "redis":
            try:
                span.set_attribute("custom.global_redis_tag", "django-vm-websocket")
                statement = span.attributes.get("db.statement")
                args_length = span.attributes.get("db.redis.args_length")
                key = span.attributes.get("db.redis.key", "unknown")
                caller_func = span.attributes.get("custom.redis.caller_function")
                caller_file = span.attributes.get("custom.redis.caller_file")
                caller_line = span.attributes.get("custom.redis.caller_line")
                span.add_event(
                    "Global Redis operation",
                    {
                        "statement": statement,
                        "args_length": args_length,
                        "key": key,
                        "caller_function": caller_func,
                        "caller_file": caller_file,
                        "caller_line": caller_line,
                    },
                )
                if getattr(span.status, "status_code", None) != 1:  # 1 = OK
                    span.set_attribute("custom.redis_error", "Error in Redis operation")
            except Exception as e:
                span.set_attribute("custom.redis_spanprocessor_error", str(e))


# --- Monkey-patch for Django cache ---
def enrich_span_with_caller(span):
    """
    Enrich the current span with the caller's function, file, and line number.
    Used by the cache method monkey-patch.
    """
    frame = inspect.currentframe()
    if frame is not None:
        outer = frame.f_back.f_back
        if outer is not None:
            span.set_attribute("custom.redis.caller_function", outer.f_code.co_name)
            span.set_attribute("custom.redis.caller_file", outer.f_code.co_filename)
            span.set_attribute("custom.redis.caller_line", outer.f_lineno)


def patch_cache_method(method_name):
    """
    Monkey-patch a Django cache method to enrich the span with caller info.
    """
    orig = getattr(cache, method_name)

    def wrapper(*args, **kwargs):
        span = trace.get_current_span()
        if span and span.is_recording():
            enrich_span_with_caller(span)
        return orig(*args, **kwargs)

    setattr(cache, method_name, wrapper)


def patch_cache():
    """
    Apply monkey-patch to Django cache get, set, and delete methods.
    """
    for method in ["get", "set", "delete"]:
        patch_cache_method(method)


# --- Setup function to call from settings.py ---
def setup_redis_otel(provider):
    """
    Register the custom Redis span processor and patch Django cache methods.
    Call this from your Django settings after setting up the OTEL provider.

    The span processor identifies Redis spans by checking for the standard
    OpenTelemetry attribute 'db.system' == 'redis', which is set automatically
    by the opentelemetry-instrumentation-redis package.
    """
    provider.add_span_processor(CustomRedisSpanProcessor())
    patch_cache()
