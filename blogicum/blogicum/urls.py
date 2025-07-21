# blogicum/blogicum/urls.py
from django.contrib import admin
from django.urls import include, path

from blog import views as blog_views

urlpatterns = [
    # Главный маршрутизатор приложения блога (namespace «blog:…»)
    path("", include("blog.urls", namespace="blog")),

    # ─────── auth ───────
    # 1. типовые представления Django (login, logout, password_change…)
    #    имена остаются «login», «logout», поэтому шаблон header.html будет работать
    path("auth/", include("django.contrib.auth.urls")),
    # 2. собственная регистрация (используется в шаблоне как {% url 'registration' %})
    path("auth/registration/", blog_views.registration, name="registration"),

    # статические страницы
    path("", include("pages.urls", namespace="pages")),

    path("admin/", admin.site.urls),
]

# Кастомные обработчики ошибок
handler400 = "pages.views.bad_request"
handler403 = "pages.views.permission_denied"
handler404 = "pages.views.page_not_found"
handler500 = "pages.views.server_error"
