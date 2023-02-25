import datetime as dt

from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db.models import Q

from users.models import User


class Genre(models.Model):
    """Жанры произведений."""
    name = models.CharField(max_length=64)
    slug = models.SlugField(unique=True, db_index=True)

    def __str__(self):
        return self.slug


class Categorie(models.Model):
    """Категории произведений."""
    name = models.CharField(max_length=256)
    slug = models.SlugField(unique=True, db_index=True)

    def __str__(self):
        return self.slug


class Title(models.Model):
    """Произведения, к которым пишут отзывы.
    (определённый фильм, книга или песенка).
    """
    name = models.CharField(
        verbose_name="название произведения",
        max_length=200,
    )
    category = models.ForeignKey(
        Categorie,
        verbose_name="Категория произведения",
        related_name='titles',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )
    genre = models.ManyToManyField(
        Genre,
        verbose_name="Жанр произведения",
        related_name='titles',
        through='TitleGenre',
    )
    year = models.IntegerField(
        verbose_name="год создания произведения",
    )
    description = models.TextField(
        verbose_name="описание произведения",
    )

    class Meta:
        constraints = models.CheckConstraint(
            check=Q(year__lte=dt.datetime.today().year),
            name='year__lte=now_year'
        ),
        verbose_name_plural = "Произведения"

    def __str__(self):
        return self.name


class TitleGenre(models.Model):
    """Модель для связи произведений и жанров."""
    title = models.ForeignKey(
        Title,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )
    genre = models.ForeignKey(
        Genre,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )

    def __str__(self):
        return f'{self.title} {self.genre}'


class Review(models.Model):
    """Модель для отзывов к произведениям."""
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='reviews',
        verbose_name='Автор'
    )
    text = models.TextField()
    pub_date = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Дата публикации'
    )
    title = models.ForeignKey(
        Title,
        on_delete=models.CASCADE,
        related_name='reviews',
        verbose_name='Произведение'
    )
    score = models.SmallIntegerField(
        validators=[
            MinValueValidator(1),
            MaxValueValidator(10)
        ],
        verbose_name='Оценка'
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['author', 'title'],
                name='unique review'),
        ]
        verbose_name = 'Отзыв'
        verbose_name_plural = 'Отзывы'

    def __str__(self):
        return self.text


class Comment(models.Model):
    """Модель для комментариев к отзывам."""
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='comments',
        verbose_name='Автор'
    )
    text = models.TextField(
        verbose_name='Текст'
    )
    pub_date = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Дата Публикации'
    )
    review = models.ForeignKey(
        Review,
        on_delete=models.CASCADE,
        related_name='comments',
        verbose_name='Отзыв',
    )

    class Meta:
        verbose_name = 'Комментарий'
        verbose_name_plural = 'Комментарии'

    def __str__(self):
        return self.text
