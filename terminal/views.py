from django.shortcuts import render
from django.http import JsonResponse
from terminal.otel_tracing import traced_function
from django.core.cache import cache


@traced_function()
def terminal_view(request):
    return render(request, "terminal/terminal.html")


@traced_function()
def health_check_view(request):
    key = "health_check_key"
    value = "pong"
    # Set cache
    cache.set(key, value, timeout=30)
    # Get cache
    cached_value = cache.get(key)
    # Delete cache
    cache.delete(key)
    return JsonResponse({"status": "ok", "cache_value": cached_value})
