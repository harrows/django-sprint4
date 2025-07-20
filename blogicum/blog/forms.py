from django import forms
from django.contrib.auth import get_user_model

from .models import Comment, Post

User = get_user_model()


class PostForm(forms.ModelForm):
    """Форма создания / редактирования публикации."""

    class Meta:
        model = Post
        fields = ('title', 'text', 'category', 'location', 'pub_date', 'image')
        widgets = {
            'pub_date': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
        }


class CommentForm(forms.ModelForm):
    """Форма добавления / редактирования комментария."""

    class Meta:
        model = Comment
        fields = ('text',)
        widgets = {'text': forms.Textarea(attrs={'rows': 3})}


class EditProfileForm(forms.ModelForm):
    """Форма изменения профиля пользователя."""

    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'username', 'email')
