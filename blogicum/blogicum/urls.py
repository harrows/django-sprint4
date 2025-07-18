from django.contrib import admin
from django.urls import path, include

handler400 = "blogicum.views.bad_request"
handler403 = "blogicum.views.permission_denied"
handler404 = "blogicum.views.page_not_found"
handler500 = "blogicum.views.server_error"

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", include("posts.urls", namespace="posts")),
    path("auth/", include("django.contrib.auth.urls")),
]