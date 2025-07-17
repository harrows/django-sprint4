from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone

User = get_user_model()


class Category(models.Model):
    title = models.CharField(max_length=255)
    slug = models.SlugField(unique=True)
    description = models.TextField(blank=True)

    def __str__(self):
        return self.title


class Location(models.Model):
    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name


class Post(models.Model):
    title = models.CharField(max_length=255, verbose_name="Заголовок")
    text = models.TextField(verbose_name="Текст")
    pub_date = models.DateTimeField(verbose_name="Дата публикации", default=timezone.now)
    author = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='posts', verbose_name="Автор"
    )
    category = models.ForeignKey(
        Category, on_delete=models.SET_NULL, related_name='posts',
        blank=True, null=True, verbose_name="Категория"
    )
    location = models.ForeignKey(
        Location, on_delete=models.SET_NULL, related_name='posts',
        blank=True, null=True, verbose_name="Местоположение"
    )
    image = models.ImageField(
        upload_to='posts/', blank=True, null=True, verbose_name="Изображение"
    )

    class Meta:
        ordering = ['-pub_date']

    def __str__(self):
        return self.title


class Comment(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='comments')
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='comments')
    text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
