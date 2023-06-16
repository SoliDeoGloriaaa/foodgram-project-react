from django.shortcuts import render


def page_not_found(request, exception):
    """Вьюха 404 ошибки."""
    return render(request, 'core/404.html', {'path': request.path}, status=404)


def server_error(request):
    """Вьюха 500 ошибки."""
    return render(request, 'core/500.html', status=500)
