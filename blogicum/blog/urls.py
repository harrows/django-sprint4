from django.urls import path
from . import views
from users.views import ProfileEditView

app_name = 'blog'

urlpatterns = [
    # Главная
    path('', views.IndexView.as_view(), name='index'),
    # Категория
    path('category/<slug:slug>/', views.CategoryView.as_view(), name='category'),
    # Профиль
    path('profile/<str:username>/', views.ProfilePostsView.as_view(), name='profile'),

    # Пост
    path('posts/<int:pk>/', views.post_detail, name='post_detail'),
    path('posts/create/', views.PostCreateView.as_view(),  name='create_post'),
    path('posts/<int:pk>/edit/', views.PostUpdateView.as_view(), name='edit_post'),   # ← нужный тестам
    path('posts/<int:pk>/delete/', views.PostDeleteView.as_view(), name='delete_post'),

    # Комментарии
    path('posts/<int:post_id>/comment/', views.comment_create,  name='add_comment'),
    path('posts/<int:post_id>/edit_comment/<int:comment_id>/', views.comment_edit, name='edit_comment'),
    path('posts/<int:post_id>/delete_comment/<int:comment_id>/', views.comment_delete, name='delete_comment'),
]