from django.shortcuts import render


def terminal_view(request):
    return render(request, "terminal/terminal.html")
