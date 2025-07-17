from django.urls import path
from .views import SignUpView, ProfileView, ProfileEditView

app_name = 'users'

urlpatterns = [
    path('auth/registration/', SignUpView.as_view(), name='signup'),
    path('profile/<str:username>/', ProfileView.as_view(), name='profile'),
    path('profile/<str:username>/edit/', ProfileEditView.as_view(), name='profile_edit'),
    path('registration/', SignUpView.as_view(), name='registration'),
]
