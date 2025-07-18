from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from .views import EditProfileView

from pages import views as pages_views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('auth/', include('django.contrib.auth.urls')),
    path('auth/registration/', pages_views.register, name='registration'),
    path('profile/<str:username>/', pages_views.ProfileView.as_view(), name='profile'),
    path('', include('pages.urls', namespace='pages')),
    path('', include('blog.urls', namespace='blog')),
    path("profile/edit/", EditProfileView.as_view(), name="edit_profile"),
]

handler403 = 'pages.views.permission_denied'
handler404 = 'pages.views.page_not_found'
handler500 = 'pages.views.server_error'


if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
