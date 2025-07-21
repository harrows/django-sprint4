# blog/urls.py
from django.urls import path

from . import views

app_name = "blog"

urlpatterns = [
    # Главная
    path("", views.index, name="index"),

    # Профиль
    path("profile/<str:username>/", views.profile, name="profile"),
    path("profile/<str:username>/edit/", views.edit_profile, name="edit_profile"),
    path(
        "profile/<str:username>/change_password/",
        views.change_password,
        name="change_password",
    ),

    # Публикации
    path("posts/create/", views.post_create, name="post_create"),
    path("posts/<int:post_id>/", views.post_detail, name="post_detail"),
    path("posts/<int:post_id>/edit/", views.post_edit, name="post_edit"),
    path("posts/<int:post_id>/delete/", views.delete_post, name="post_delete"),

    # Комментарии
    path("posts/<int:post_id>/comment/", views.add_comment, name="add_comment"),
    path(
        "posts/<int:post_id>/edit_comment/<int:comment_id>/",
        views.edit_comment,
        name="edit_comment",
    ),
    path(
        "posts/<int:post_id>/delete_comment/<int:comment_id>/",
        views.delete_comment,
        name="delete_comment",
    ),

    # Категории
    path("category/<slug:slug>/", views.category_posts, name="category_posts"),
]
