from django.views.generic import TemplateView
from django.shortcuts import render


class AboutView(TemplateView):
    template_name = 'pages/about.html'


class RulesView(TemplateView):
    template_name = 'pages/rules.html'


def page_not_found(request, exception=None):
    return render(
        request,
        'pages/404.html',
        status=404
    )


def permission_denied(request, exception=None):
    return render(
        'pages/403.html',
        request,
        status=403
    )


def bad_request(request, exception=None):
    return render(
        request,
        'pages/400.html',
        status=400
    )


def server_error(request):
    return render(
        request,
        'pages/500.html',
        status=500
    )


def csrf_failure(request, reason=''):
    return render(
        request,
        'pages/403csrf.html',
        status=403
    )