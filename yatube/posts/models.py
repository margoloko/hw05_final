from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()


class Group(models.Model):
    """ Класс Group для сообществ."""

    title = models.CharField(max_length=200)
    slug = models.SlugField(unique=True,
                            max_length=190,)
    description = models.TextField()

    def __str__(self) -> str:
        return self.title


class Post(models.Model):
    """ Класс Post описывает свойства постов."""

    text = models.TextField('Текст поста',
                            help_text='Введите текст поста')
    pub_date = models.DateTimeField('Дата публикации',
                                    auto_now_add=True)
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Автор',
        related_name='posts')
    group = models.ForeignKey(Group,
                              blank=True,
                              null=True,
                              on_delete=models.SET_NULL,
                              related_name='posts',
                              verbose_name='Группа',
                              help_text='Выберите группу')
    image = models.ImageField('Картинка',
                              upload_to='posts/',
                              blank=True,
                              help_text='Загрузите картинку')

    def __str__(self):
        return self.text[:15]

    class Meta:
        ordering = ['-pub_date']
        verbose_name = 'Пост'
        verbose_name_plural = 'Посты'


class Comment(models.Model):
    """ Comment ."""
    post = models.ForeignKey(Post,
                             on_delete=models.CASCADE,
                             related_name='comments')
    author = models.ForeignKey(User,
                               on_delete=models.CASCADE,
                               verbose_name='Автор',
                               related_name='comments')
    text = models.TextField('Текст комментария',
                            help_text='Введите текст комментария')
    created = models.DateTimeField('Дата публикации комментария',
                                   auto_now_add=True)

    class Meta:
        ordering = ['-created']


class Follow(models.Model):
    user = models.ForeignKey(User,
                             on_delete=models.CASCADE,
                             related_name='follower',
                             help_text='Вы подписываетесь на:')
    author = models.ForeignKey(User,
                               on_delete=models.CASCADE,
                               related_name='following',
                               help_text='Автор поста')
