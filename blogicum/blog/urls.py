from django.urls import path
from . import views

app_name = 'blog'

urlpatterns = [
    path('', views.index, name='index'),
    path('posts/create/', views.post_create, name='create_post'),
    path('posts/<int:post_id>/', views.post_detail, name='post_detail'),
    path('posts/<int:post_id>/edit/', views.post_edit, name='post_edit'),
    path('posts/<int:post_id>/delete/', views.post_delete, name='post_delete'),
    path('posts/<int:post_id>/comment/', views.comment_add, name='add_comment'),
    path('posts/<int:post_id>/edit_comment/<int:comment_id>/', views.comment_edit,name='edit_comment'),
    path('posts/<int:post_id>/delete_comment/<int:comment_id>/', views.comment_delete, name='delete_comment'),
    path('profile/<str:username>/', views.profile, name='profile'),
    path('profile/<str:username>/change_password/', views.change_password, name='change_password'),
    path('category/<slug:slug>/', views.category_posts, name='category_posts'),
]
