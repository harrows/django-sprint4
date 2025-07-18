from django.db import models
from django.utils import timezone
from django.utils.text import slugify


def post_image_path(instance: "Post", filename: str) -> str:
    return f"posts/{instance.pk}/{filename}"


class Category(models.Model):
    title = models.CharField("Название", max_length=256, unique=True)
    description = models.TextField("Описание", blank=True)
    slug = models.SlugField("Слаг", max_length=256, unique=True)
    is_published = models.BooleanField("Опубликована", default=True, db_index=True)
    created_at = models.DateTimeField("Дата создания", default=timezone.now, editable=False)

    class Meta:
        ordering = ("title",)
        verbose_name = "Категория"
        verbose_name_plural = "Категории"

    def __str__(self) -> str:
        return self.title


class Location(models.Model):
    name = models.CharField("Название", max_length=256, unique=True)
    slug = models.SlugField("Слаг", max_length=256, unique=True, null=True, blank=True)
    is_published = models.BooleanField("Опубликовано", default=True, db_index=True)
    created_at = models.DateTimeField("Создано", default=timezone.now, editable=False)

    class Meta:
        ordering = ("name",)
        verbose_name = "Местоположение"
        verbose_name_plural = "Местоположения"

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)[:200]
        super().save(*args, **kwargs)

    def __str__(self) -> str:
        return self.name


class PublishedManager(models.Manager):
    def get_queryset(self):
        return (
            super()
            .get_queryset()
            .filter(is_published=True, pub_date__lte=timezone.now())
        )


class Post(models.Model):
    title = models.CharField("Заголовок", max_length=256)
    text = models.TextField("Текст")
    slug = models.SlugField("Слаг", max_length=256, unique=True, blank=True)
    pub_date = models.DateTimeField("Дата публикации", default=timezone.now, db_index=True)
    location = models.ForeignKey(
        Location,
        on_delete=models.SET_NULL,
        related_name="posts",
        verbose_name="Местоположение",
        null=True,
        blank=True,
    )
    category = models.ForeignKey(
        Category,
        on_delete=models.CASCADE,
        related_name="posts",
        verbose_name="Категория",
    )
    is_published = models.BooleanField("Опубликовано", default=True, db_index=True)
    image = models.ImageField("Картинка", upload_to=post_image_path, blank=True, null=True)
    created_at = models.DateTimeField("Создана", auto_now_add=True)


    objects = models.Manager()
    published = PublishedManager()

    class Meta:
        ordering = ("-pub_date",)
        verbose_name = "Пост"
        verbose_name_plural = "Посты"

    def __str__(self) -> str:
        return self.title


    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)[:250]
        super().save(*args, **kwargs)


class Comment(models.Model):
    post = models.ForeignKey(
        Post,
        on_delete=models.CASCADE,
        related_name="comments",
        verbose_name="Пост",
    )
    author = models.ForeignKey(
        "auth.User",
        on_delete=models.CASCADE,
        related_name="comments",
        verbose_name="Автор",
    )
    text = models.TextField("Текст комментария")
    created_at = models.DateTimeField("Создан", auto_now_add=True, db_index=True)

    class Meta:
        ordering = ("created_at",)
        verbose_name = "Комментарий"
        verbose_name_plural = "Комментарии"

    def __str__(self) -> str:
        return f"Комментарий {self.pk} к посту «{self.post}»"
