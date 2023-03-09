from django import forms

from .models import Follow, Post, Comment


class PostForm(forms.ModelForm):
    """
    The PostForm class is used for creating new posts and has fields
    for the post text, the group the post belongs to, and an image.
    The form labels for these fields are defined in the labels dictionary.
    """
    class Meta:
        model = Post
        fields = ('text', 'group', 'image')
        labels = {'text': 'Текст',
                  'group': 'Группа',
                  'image': 'Картинка'}


class CommentForm(forms.ModelForm):
    """
    The CommentForm class is used for adding comments to existing posts
    and has a single field for the comment text.
    The form label for this field is defined in the labels dictionary.
    """
    class Meta:
        model = Comment
        fields = {'text'}
        labels = {'text': 'Текст'}


class FollowForm(forms.ModelForm):
    """
    The FollowForm class is used for subscribing to authors and
    has a single field for the user to subscribe to.
    The form label for this field is defined in the labels dictionary.
    """
    class Meta:
        model = Follow
        fields = {'user'}
        labels = {'Пользователь подписывается на:'}
