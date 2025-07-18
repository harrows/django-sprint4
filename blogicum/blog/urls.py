from django.urls import path
from . import views

app_name = 'blog'

urlpatterns = [
    path('', views.IndexView.as_view(), name='index'),
    path('category/<slug:slug>/', views.CategoryPostsView.as_view(), name='category_posts'),
    path('posts/<int:post_id>/', views.post_detail, name='post_detail'),
    path('posts/<int:post_id>/edit/', views.PostEditView.as_view(), name='edit_post'),
    path('create/', views.PostCreateView.as_view(), name='create_post'),
    path('posts/<int:post_id>/edit_comment/<int:comment_id>/', views.CommentEditView.as_view(), name='edit_comment'),
    path('posts/<int:post_id>/delete_comment/<int:comment_id>/', views.CommentDeleteView.as_view(), name='delete_comment'),
]
