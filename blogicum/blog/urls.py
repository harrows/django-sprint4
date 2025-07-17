from django.urls import path
from blogicum import views

urlpatterns = [
    path("", views.IndexView.as_view(), name="index"),
    path("category/<slug:slug>/", views.CategoryView.as_view(), name="category_posts"),
    path("profile/<str:username>/", views.ProfileView.as_view(), name="profile"),
    path("profile/<str:username>/edit/", views.EditProfileView.as_view(), name="profile_edit"),
    path("posts/<int:pk>/", views.PostDetailView.as_view(), name="post_detail"),
    path("posts/create/", views.PostCreateView.as_view(), name="post_create"),
    path("posts/<int:pk>/edit/", views.PostUpdateView.as_view(), name="post_edit"),
    path("posts/<int:post_id>/delete_comment/<int:comment_id>/", views.CommentDeleteView.as_view(),name="comment_delete"),
]
