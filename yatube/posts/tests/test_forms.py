import shutil
import tempfile

from django.test import Client, TestCase, override_settings
from http import HTTPStatus
from django.core.files.uploadedfile import SimpleUploadedFile
from django.conf import settings
from django.urls import reverse
from django.contrib.auth import get_user_model

from ..models import Post, Group, Comment

User = get_user_model()
TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class PostFormTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.author = User.objects.create_user(username='auth')
        cls.author_client = Client()
        cls.author_client.force_login(cls.author)
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test-slug',
            description='Тестовое описание')
        cls.post = Post.objects.create(
            text='Тестовая запись',
            author=cls.author,
            group=cls.group)
        cls.comment = Comment.objects.create(text='Комментарий',
                                             author=cls.author,
                                             post=cls.post)

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def setUp(self):
        self.guest_client = Client()
        self.user = User.objects.create_user(username='NoName')
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_create_post(self):
        """Валидная форма добавляет новый пост."""
        small_gif = (b'\x47\x49\x46\x38\x39\x61\x02\x00'
                     b'\x01\x00\x80\x00\x00\x00\x00\x00'
                     b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
                     b'\x00\x00\x00\x2C\x00\x00\x00\x00'
                     b'\x02\x00\x01\x00\x00\x02\x02\x0C'
                     b'\x0A\x00\x3B')
        uploaded = SimpleUploadedFile(
            name='small.gif',
            content=small_gif,
            content_type='image/gif')
        form_data = {
            'group': PostFormTests.group.pk,
            'text': 'Тестовый текст',
            'image': uploaded, }
        # Подсчитаем количество постов в Post
        post_count = Post.objects.count()
        # Отправляем POST-запрос
        response = self.authorized_client.post(
            reverse('posts:post_create'),
            data=form_data,
            follow=True)
        self.assertEqual(response.status_code, HTTPStatus.OK)
        # Проверяем, сработал ли редирект
        self.assertRedirects(response, reverse('posts:profile', kwargs={
            'username': 'NoName'}))
        # Проверяем, увеличилось ли число постов
        self.assertEqual(Post.objects.count(), post_count + 1)
        self.assertTrue(Post.objects.filter(
                        text='Тестовый текст',
                        group=PostFormTests.group.pk,
                        author=self.user.pk,
                        image='posts/small.gif').exists())

    def test_edit_post(self):
        """Валидная форма изменяет пост."""
        # Подсчитаем количество постов в Post
        post_count = Post.objects.count()
        big_gif = (b'\x47\x49\x46\x38\x39\x61\x02\x00'
                   b'\x01\x00\x80\x00\x00\x00\x00\x00'
                   b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
                   b'\x00\x00\x00\x2C\x00\x00\x00\x00'
                   b'\x02\x00\x01\x00\x00\x02\x02\x0C'
                   b'\x0A\x00\x3B')
        uploaded = SimpleUploadedFile(
            name='big.gif',
            content=big_gif,
            content_type='image/gif')
        form_data = {'group': PostFormTests.group.pk,
                     'text': 'Измененный текст',
                     'image': uploaded}
        # Отправляем POST-запрос
        response = self.author_client.post(
            reverse('posts:post_edit', kwargs={
                    'post_id': PostFormTests.post.pk}),
            data=form_data,
            follow=True)
        self.assertEqual(response.status_code, HTTPStatus.OK)
        # Проверяем, что произошло изменение поста
        self.assertTrue(Post.objects.filter(
                        text='Измененный текст',
                        group=PostFormTests.group.pk,
                        image='posts/big.gif').exists())
        # Проверяем, сработал ли редирект
        self.assertRedirects(response, reverse('posts:post_detail',
                             kwargs={'post_id': PostFormTests.post.pk}))
        # Проверяем, число постов осталось прежним
        self.assertEqual(Post.objects.count(), post_count)

    def test_comment_acsess(self):
        """Kомментировать посты может авторизованный пользователь."""
        count_comment = Comment.objects.count()
        form_data = {'text': 'Новый комментарий'}
        response = self.authorized_client.post(reverse(
            'posts:add_comment', kwargs={'post_id': PostFormTests.post.pk}),
            data=form_data, follow=True)
        self.assertTrue(response, Comment.objects.filter(
            text='Новый комментарий').exists())
        self.assertTrue(Comment.objects.filter(post=self.post).exists())
        self.assertRedirects(response, reverse('posts:post_detail',
                             kwargs={'post_id': PostFormTests.post.pk}))
        self.assertEqual(Comment.objects.count(), count_comment + 1)

    def test_add_comment_for_guest_client(self):
        """У неавторизированного пользователя нет прав комментировать посты."""
        redirect = '/auth/login/?next=/posts/1/comment/'
        count_comment = Comment.objects.count()
        form_data = {'text': 'Новый комментарий'}
        response = self.guest_client.post(
            reverse('posts:add_comment', kwargs={'post_id': 1}),
            data=form_data,
            follow=True)
        self.assertEqual(Comment.objects.count(), count_comment)
        self.assertRedirects(response, redirect, status_code=302,
                             target_status_code=200)
