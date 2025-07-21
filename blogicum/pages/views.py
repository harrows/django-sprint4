from django.views.generic import TemplateView
from django.shortcuts import render


class AboutView(TemplateView):
    template_name = 'pages/about.html'


class RulesView(TemplateView):
    template_name = 'pages/rules.html'


def bad_request(request, exception, template_name='pages/400.html'):
    """HTTP 400 — неверный запрос."""
    return render(request, template_name, status=400)


def page_not_found(request, exception, template_name='pages/404.html'):
    """HTTP 404 — страница не найдена."""
    return render(request, template_name, status=404)


def permission_denied(request, exception, template_name='pages/403csrf.html'):
    """HTTP 403 — запрещено (отказ в доступе)."""
    return render(request, template_name, status=403)


def csrf_failure(request, reason='', template_name='pages/403csrf.html'):
    """Стандартный обработчик CSRF-ошибок."""
    return render(request, template_name, status=403)


def server_error(request, template_name='pages/500.html'):
    """HTTP 500 — внутренняя ошибка сервера."""
    return render(request, template_name, status=500)