from django.urls import path, re_path
from . import views

app_name = 'blog'

urlpatterns = [
    # Главная страница
    path('', views.index, name='index'),

    # Профиль пользователя
    path('profile/edit/', views.edit_profile_self, name='edit_profile'),
    path('profile/<str:username>/', views.profile, name='profile'),
    path('profile/<str:username>/edit/', views.edit_profile, name='edit_profile_username'),
    path('profile/<str:username>/change_password/', views.change_password, name='change_password_username'),

    # Публикации
    path('posts/create/', views.post_create, name='create_post'),
    path('posts/<int:post_id>/', views.post_detail, name='post_detail'),
    path('posts/<int:post_id>/edit/', views.post_edit, name='edit_post'),
    path('posts/<int:post_id>/delete/', views.delete_post, name='delete_post'),

    # Комментарии
    path('posts/<int:post_id>/comment/', views.add_comment, name='add_comment'),
    path(
        'posts/<int:post_id>/edit_comment/<int:comment_id>/',
        views.edit_comment,
        name='edit_comment',
    ),
    path(
        'posts/<int:post_id>/delete_comment/<int:comment_id>/',
        views.delete_comment,
        name='delete_comment',
    ),

    # Категории
    re_path(r'^category/(?P<slug>[-a-zA-Z0-9_]*)/$', views.category_posts, name='category_posts'),

    # Регистрация нового пользователя
    path('auth/registration/', views.registration, name='registration'),
]
