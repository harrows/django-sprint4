from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone

User = get_user_model()


class PublishedManager(models.Manager):
    def get_queryset(self):
        return (super()
                .get_queryset()
                .filter(is_published=True, pub_date__lte=timezone.now()))


class TimeStampedMixin(models.Model):
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата создания', blank=True, null=True)
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Дата изменения')

    class Meta:
        abstract = True


class Category(TimeStampedMixin):
    title = models.CharField('Название', max_length=256)
    description = models.TextField('Описание', blank=True)
    slug = models.SlugField(unique=True)
    is_published = models.BooleanField('Опубликована', default=True)

    objects = models.Manager()
    published = PublishedManager()

    class Meta:
        ordering = ('title',)
        verbose_name = 'Категория'
        verbose_name_plural = 'Категории'

    def __str__(self) -> str:
        return self.title


class Location(TimeStampedMixin):
    name = models.CharField('Название места', max_length=256)
    is_published = models.BooleanField('Опубликовано', default=True)
    slug = models.SlugField('Слаг', unique=True, max_length=200, blank=True, null=True)

    objects = models.Manager()
    published = PublishedManager()

    class Meta:
        ordering = ('name',)
        verbose_name = 'Локация'
        verbose_name_plural = 'Локации'

    def __str__(self) -> str:
        return self.name


def post_image_path(instance: "Post", filename: str) -> str:
    return f"posts/{instance.author_id}/{filename}"


class Post(TimeStampedMixin):
    title = models.CharField('Заголовок', max_length=256)
    text = models.TextField('Текст')
    image = models.ImageField('Картинка', upload_to=post_image_path, blank=True)
    pub_date = models.DateTimeField('Дата и время публикации')
    is_published = models.BooleanField('Опубликовано', default=False)
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='posts', verbose_name='Автор')
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, related_name='posts', null=True, blank=True, verbose_name='Категория')
    location = models.ForeignKey(Location, on_delete=models.SET_NULL, related_name='posts', null=True, blank=True, verbose_name='Локация')

    objects = models.Manager()
    published = PublishedManager()

    class Meta:
        ordering = ('-pub_date',)
        verbose_name = 'Пост'
        verbose_name_plural = 'Посты'

    def __str__(self) -> str:
        return self.title


class Comment(TimeStampedMixin):
    text = models.TextField('Текст')
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='comments')
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='comments')

    class Meta:
        ordering = ('created_at',)
        verbose_name = 'Комментарий'
        verbose_name_plural = 'Комментарии'

    def __str__(self) -> str:
        return self.text[:50]
