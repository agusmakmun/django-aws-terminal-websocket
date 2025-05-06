"""
OpenTelemetry tracing decorators for Django/Channels functions, methods, and
classes.

Provides:
- traced_function and traced_async_function for automatic span creation, status
  code setting, and error recording for sync and async functions/methods.
- traced_class and traced_async_class for automatic tracing of all sync or async
  methods in a class, respectively.
"""

from typing import Type
import inspect

from functools import wraps
from opentelemetry import trace, context as otel_context
from opentelemetry.trace.status import Status, StatusCode

tracer = trace.get_tracer(__name__)


def _get_span_name(func, args, span_name):
    """
    Determine the span name for a function or method.
    If span_name is provided, use it. Otherwise, use ClassName.method or
    function name.

    Args:
        func: The function or method being decorated.
        args: The positional arguments passed to the function.
        span_name: Optional custom span name.

    Returns:
        str: The span name to use.
    """
    if span_name:
        return span_name
    # If it's a method, args[0] is usually 'self' or 'cls'
    if args and hasattr(args[0], "__class__"):
        class_name = args[0].__class__.__name__
        return f"{class_name}.{func.__name__}"
    return func.__name__


def traced_function(span_name=None):
    """
    Decorator to trace a synchronous function with OpenTelemetry.
    Creates a span, sets code attributes, status, and records exceptions.

    Args:
        span_name (str, optional): Custom span name. Defaults to None.

    Returns:
        function: The decorated function with tracing.
    """

    def decorator(func):
        """
        Decorator function that wraps the original function with tracing logic.
        """

        @wraps(func)
        def wrapper(*args, **kwargs):
            """
            Wrapper function that creates a span, sets attributes, and handles
            status and exceptions for the wrapped function.

            Args:
                *args: Positional arguments for the wrapped function.
                **kwargs: Keyword arguments for the wrapped function.

            Returns:
                Any: The result of the wrapped function.
            """
            name = _get_span_name(func, args, span_name)
            module = func.__module__
            # Allow manual context override
            ctx = kwargs.pop("context", None)
            if ctx is None:
                ctx = otel_context.get_current()
            with tracer.start_as_current_span(name, context=ctx) as span:
                span.set_attribute("code.filepath", func.__code__.co_filename)
                span.set_attribute("code.lineno", func.__code__.co_firstlineno)
                span.set_attribute("code.function", name)
                span.set_attribute("code.namespace", module)
                span.set_attribute("args", str(args))
                span.set_attribute("kwargs", str(kwargs))
                try:
                    result = func(*args, **kwargs)
                    span.set_attribute("return_type", str(type(result)))
                    span.set_status(Status(StatusCode.OK))
                    return result
                except Exception as e:
                    span.record_exception(e)
                    span.set_status(Status(StatusCode.ERROR))
                    span.set_attribute("otel.error_message", str(e))
                    raise

        return wrapper

    return decorator


def traced_class(cls: Type) -> Type:
    """
    Class decorator to automatically apply traced_function to all synchronous
    (non-async) methods.

    - Excludes dunder methods and static/class methods.
    - Each sync method will be traced with a span named after the class and
      method.
    - Exceptions are recorded and span status is set to ERROR if any occur.
    - Span attributes include file, line, function, args, kwargs, and return
      type.

    Usage:
        @traced_class
        class MyClass:
            def foo(self):
                ...
    """
    for name, attr in cls.__dict__.items():
        if (
            inspect.isfunction(attr)
            and not inspect.iscoroutinefunction(attr)
            and not name.startswith("__")
        ):
            setattr(cls, name, traced_function()(attr))
    return cls


def traced_async_class(cls: Type) -> Type:
    """
    Class decorator to automatically apply traced_async_function to all async methods.
    """
    for name, attr in cls.__dict__.items():
        if inspect.iscoroutinefunction(attr) and not name.startswith("__"):
            setattr(cls, name, traced_async_function()(attr))
    return cls


def traced_async_function(span_name=None):
    """
    Decorator to trace an async function with OpenTelemetry.
    Creates a span, sets code attributes, status, and records exceptions.

    Args:
        span_name (str, optional): Custom span name. Defaults to None.

    Returns:
        function: The decorated async function with tracing.
    """

    def decorator(func):
        """
        Decorator function that wraps the original async function with tracing
        logic.
        """

        @wraps(func)
        async def wrapper(*args, **kwargs):
            """
            Wrapper function that creates a span, sets attributes, and handles
            status and exceptions for the wrapped async function.

            Args:
                *args: Positional arguments for the wrapped function.
                **kwargs: Keyword arguments for the wrapped function.

            Returns:
                Any: The result of the wrapped async function.
            """
            name = _get_span_name(func, args, span_name)
            module = func.__module__
            ctx = kwargs.pop("context", None)
            if ctx is None:
                ctx = otel_context.get_current()
            with tracer.start_as_current_span(name, context=ctx) as span:
                span.set_attribute("code.filepath", func.__code__.co_filename)
                span.set_attribute("code.lineno", func.__code__.co_firstlineno)
                span.set_attribute("code.function", name)
                span.set_attribute("code.namespace", module)
                span.set_attribute("args", str(args))
                span.set_attribute("kwargs", str(kwargs))
                try:
                    result = await func(*args, **kwargs)
                    span.set_attribute("return_type", str(type(result)))
                    span.set_status(Status(StatusCode.OK))
                    return result
                except Exception as e:
                    span.record_exception(e)
                    span.set_status(Status(StatusCode.ERROR))
                    span.set_attribute("otel.error_message", str(e))
                    raise

        return wrapper

    return decorator
