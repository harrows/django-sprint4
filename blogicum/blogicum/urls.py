from django.contrib import admin
from django.urls import path
from .views import EditProfileView
from django.conf import settings
from django.conf.urls.static import static


handler404 = 'pages.views.page_not_found'
handler500 = 'pages.views.server_error'
handler403 = 'pages.views.csrf_failure'

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('blog.urls')),
    path('', include(('blog.urls', 'blog'), namespace='blog')),
    # path('', include(('users.urls', 'users'), namespace='users')),
    path('auth/', include(('users.urls', 'users'), namespace='users')),
    path('auth/', include('django.contrib.auth.urls')),
    path('pages/', include('pages.urls')),
    path('profile/edit/', EditProfileView.as_view(), name='edit_profile'),
    path('posts/<int:pk>/', PostDetailView.as_view(), name='post_detail'),
    path('posts/create/', PostCreateView.as_view(), name='post_create'),
    path('profile/<str:username>/', ProfileView.as_view(), name='profile'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

if settings.DEBUG:
    import debug_toolbar
    urlpatterns = [path('__debug__/', include(debug_toolbar.urls))] + urlpatterns