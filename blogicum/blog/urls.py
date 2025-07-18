from django.urls import path
from . import views
from blogicum import views as blog_views

app_name = 'blog'

urlpatterns = [
    path('', blog_views.IndexView.as_view(), name='index'),
    path('category/<slug:slug>/', blog_views.CategoryView.as_view(), name='category'),
    path('posts/<int:pk>/', blog_views.PostDetailView.as_view(), name='post_detail'),
    path('posts/create/', blog_views.PostCreateView.as_view(), name='create_post'),
    path('posts/<int:pk>/edit/', blog_views.PostUpdateView.as_view(), name='edit_post'),
    path('posts/<int:pk>/delete/', blog_views.PostDeleteView.as_view(), name='delete_post'),
    path('posts/<int:post_id>/edit_comment/<int:comment_id>/', blog_views.CommentUpdateView.as_view(pk_url_kwarg='comment_id'), name='edit_comment'),
    path('posts/<int:post_id>/delete_comment/<int:comment_id>/', blog_views.CommentDeleteView.as_view(), name='delete_comment'),
    path('profile/<str:username>/', blog_views.ProfileView.as_view(), name='profile'),
    path('profile/<str:username>/edit/', blog_views.EditProfileView.as_view(), name='edit_profile'),
]
