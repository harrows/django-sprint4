from django.conf import settings
from django.db import models
from django.db.models.functions import Now
from django.contrib.auth import get_user_model



User = get_user_model()

TITLE_MAX_LENGTH: int = 256
SLUG_MAX_LENGTH: int = 64


class PostQuerySet(models.QuerySet):

    def published(self):
        return self.filter(
            is_published=True,
            pub_date__lte=Now(),
            category__is_published=True,
        )

    def with_related(self):
        return self.select_related('author', 'category', 'location')


class Category(models.Model):
    title = models.CharField('Заголовок', max_length=TITLE_MAX_LENGTH)
    slug = models.SlugField(
        'Идентификатор',
        max_length=SLUG_MAX_LENGTH,
        unique=True,
        help_text=(
            'Идентификатор страницы для URL; '
            'разрешены символы латиницы, цифры, дефис и подчёркивание.'
        ),
    )
    description = models.TextField('Описание')
    is_published = models.BooleanField(
        'Опубликовано',
        default=True,
        help_text='Снимите галочку, чтобы скрыть публикацию.',
    )
    created_at = models.DateTimeField('Добавлено', auto_now_add=True)

    class Meta:
        ordering = ('title',)
        verbose_name = 'категория'
        verbose_name_plural = 'Категории'

    def __str__(self) -> str:
        return self.title


class Location(models.Model):
    name = models.CharField('Название места', max_length=TITLE_MAX_LENGTH)
    is_published = models.BooleanField(
        'Опубликовано',
        default=True,
        help_text='Снимите галочку, чтобы скрыть место.',
    )
    created_at = models.DateTimeField('Добавлено', auto_now_add=True)

    class Meta:
        ordering = ('name',)
        verbose_name = 'местоположение'
        verbose_name_plural = 'Местоположения'

    def __str__(self) -> str:
        return self.name


class Post(models.Model):
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='posts',
    )
    category = models.ForeignKey(
        Category,
        verbose_name='Категория',
        on_delete=models.SET_NULL,
        null=True,
        related_name='posts',
    )
    location = models.ForeignKey(
        Location,
        verbose_name='Местоположение',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )

    title = models.CharField('Заголовок', max_length=TITLE_MAX_LENGTH)
    text = models.TextField('Текст')
    pub_date = models.DateTimeField(
        'Дата и время публикации',
        help_text=(
            'Если установить дату и время в будущем — '
            'можно делать отложенные публикации.'
        ),
    )
    is_published = models.BooleanField(
        'Опубликовано',
        default=True,
        help_text='Снимите галочку, чтобы скрыть публикацию.',
    )
    created_at = models.DateTimeField('Добавлено', auto_now_add=True)

    objects: PostQuerySet = PostQuerySet.as_manager()

    class Meta:
        ordering = ('-pub_date',)
        verbose_name = 'публикация'
        verbose_name_plural = 'Публикации'

    def __str__(self) -> str:
        return self.title
    
    image = models.ImageField(
        'Картинка', upload_to='posts_images/', blank=True
    )


class Comment(models.Model):
    post      = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='comments')
    author    = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    text      = models.TextField()
    created   = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['created']