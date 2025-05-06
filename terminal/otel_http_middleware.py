from opentelemetry.trace.propagation.tracecontext import TraceContextTextMapPropagator


class TraceparentHeaderMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        carrier = {}
        TraceContextTextMapPropagator().inject(carrier)
        if "traceparent" in carrier:
            response["Traceparent"] = carrier["traceparent"]
        return response
