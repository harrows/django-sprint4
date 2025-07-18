from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
# from .views import EditProfileView

from pages import views as pages_views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('auth/', include('django.contrib.auth.urls')),
    path('auth/registration/', pages_views.register, name='registration'),
    path('profile/<str:username>/', pages_views.ProfileView.as_view(), name='profile'),
    path("", include("blog.urls")),
    path("", include("users.urls")), 
    # path("profile/edit/", EditProfileView.as_view(), name="edit_profile"),
]

handler400 = "users.views.bad_request"
handler403 = "users.views.permission_denied"
handler404 = "users.views.page_not_found"
handler500 = "users.views.server_error"

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
