from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()


class Group(models.Model):
    title = models.CharField(
        max_length=200,
    )
    slug = models.SlugField(
        unique=True,
    )
    description = models.TextField(
        blank=True,
        null=True,
    )

    def __str__(self):
        return f'{self.title}'


class Post(models.Model):
    RELATED_NAME = 'posts'
    text = models.TextField(
        'Текст поста',
        help_text='Введите текст поста'
    )
    pub_date = models.DateTimeField(
        auto_now_add=True
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name=RELATED_NAME,
    )
    group = models.ForeignKey(
        Group,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name=RELATED_NAME,
    )

    class Meta:
        ordering = ('-pub_date',)

    def __str__(self):
        return self.text[:15]
