from django import forms

from .models import Follow, Post, Comment


class PostForm(forms.ModelForm):
    """Форма для создания поста."""
    class Meta:
        model = Post
        fields = ('text', 'group', 'image')
        labels = {'text': 'Текст',
                  'group': 'Группа',
                  'image': 'Картинка'}


class CommentForm(forms.ModelForm):
    """Форма для добавления комментария."""
    class Meta:
        model = Comment
        fields = {'text'}
        labels = {'text': 'Текст'}


class FollowForm(forms.ModelForm):
    """Форма подписки на авторов."""
    class Meta:
        model = Follow
        fields = {'user'}
        labels = {'Пользователь подписывается на:'}
