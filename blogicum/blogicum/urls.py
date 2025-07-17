from django.contrib import admin
from django.urls import path, include
from blogicum import views
from .views import EditProfileView
from django.conf import settings
from django.conf.urls.static import static


urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.IndexView.as_view(), name='index'),
    path('category/<slug:slug>/', views.CategoryView.as_view(), name='category'),
    path('profile/<str:username>/', views.ProfileView.as_view(), name='profile'),
    path('profile/<str:username>/edit/', views.EditProfileView.as_view(), name='edit_profile'),
    path('posts/<int:pk>/', views.PostDetailView.as_view(), name='post_detail'),
    path('posts/create/', views.PostCreateView.as_view(), name='post_create'),
    path('posts/<int:pk>/edit/', views.PostUpdateView.as_view(), name='post_edit'),
    path('posts/<int:pk>/delete/', views.PostDeleteView.as_view(), name='post_delete'),
    path('comments/<int:pk>/edit/', views.CommentUpdateView.as_view(), name='comment_edit'),
    path('comments/<int:pk>/delete/', views.CommentDeleteView.as_view(), name='comment_delete'),
    path('about/', views.AboutPageView.as_view(), name='about'),
    path('rules/', views.RulesPageView.as_view(), name='rules'),
    path('auth/', include('django.contrib.auth.urls')),
]


handler403 = 'blogicum.views.permission_denied'
handler404 = 'blogicum.views.page_not_found'
handler500 = 'blogicum.views.server_error'
