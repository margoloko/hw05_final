from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()


class Group(models.Model):
    """
    Represents a group in the application.

    Fields:
    - title: the title of the group (max length of 200 characters)
    - slug: a unique slug for the group URL(max length of 190 characters)
    - description: a text field describing the group.
    """
    title = models.CharField(max_length=200)
    slug = models.SlugField(unique=True,
                            max_length=190,)
    description = models.TextField()

    def __str__(self) -> str:
        """
        Returns the string representation of the group,
        which is the title.
        """
        return self.title


class Post(models.Model):
   """
    Represents a post in the application.

    Fields:
    - text: the text content of the post
    - pub_date: the date the post was published
    - author: the user who authored the post(ForeignKey to the User model)
    - group: the group the post belongs
    to(ForeignKey to the Group model, can be null)
    - image: an optional image to include in the post.
    """
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
        """
        Returns the string representation of the post,
        which is the first 15 characters of the text.
        """
        return self.text[:15]

    class Meta:
        """
        Specifies the metadata for the Post model.
        """
        ordering = ['-pub_date']
        verbose_name = 'Пост'
        verbose_name_plural = 'Посты'


class Comment(models.Model):
    """
    Represents a comment on a post.

    Fields:
    - post: the post the comment is on(ForeignKey to the Post model)
    - author: the user who authored 
    the comment (ForeignKey to the User model)
    - text: the text content of the comment
    - created: the date the comment was created.
    """
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
        """
        Specifies the metadata for the Comment model.
        """
        ordering = ['-created']


class Follow(models.Model):
    """
    Represents a follow relationship between two users.

    Fields:
    - user: the user who is following
    another user (ForeignKey to the User model)
    - author: the user who is being
    followed (ForeignKey to the User model).
    """
    user = models.ForeignKey(User,
                             on_delete=models.CASCADE,
                             related_name='follower',
                             help_text='Вы подписываетесь на:')
    author = models.ForeignKey(User,
                               on_delete=models.CASCADE,
                               related_name='following',
                               help_text='Автор поста')
