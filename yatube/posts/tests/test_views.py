import shutil
import tempfile

from django.test import TestCase, Client, override_settings
from django.core.files.uploadedfile import SimpleUploadedFile
from django.conf import settings
from django.contrib.auth import get_user_model
from django.urls import reverse
from django import forms
from django.core.cache import cache


from ..models import Post, Group, Comment, Follow

User = get_user_model()
POSTS_PER_PAGE = 11
INDEX_URL = reverse('posts:index')
GROUP_LIST_URL = reverse('posts:group_list', kwargs={'slug': 'test-slug'})
PROFILE_URL = reverse('posts:profile', kwargs={'username': 'auth'})
POST_CREATE_URL = reverse('posts:post_create')
POST_DETAIL_URL = reverse('posts:post_detail', kwargs={'post_id': '1'})
POST_EDIT_URL = reverse('posts:post_edit', kwargs={'post_id': '1'})
PROFILE_FOLLOW = reverse('posts:profile_follow',
                         kwargs={'username': 'auth-follow'})
PROFILE_UNFOLLOW = reverse('posts:profile_unfollow',
                           kwargs={'username': 'auth-follow'})
RDR_GUEST = '/auth/login/?next=/profile/auth-follow/follow/'
TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)


class PostPaginatorTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.author = User.objects.create_user(username='auth')
        cls.author_client = Client()
        cls.author_client.force_login(cls.author)
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test-slug',
            description='Тестовое описание',)
        cls.posts_amount = POSTS_PER_PAGE + 1
        bulk_posts = [
            Post(
                text=f'Тестовая запись {num}',
                author=cls.author,
                group=cls.group
            )
            for num in range(cls.posts_amount)
        ]
        Post.objects.bulk_create(bulk_posts)

    def setUp(self) -> None:
        self.guest_client = Client()
        self.user = User.objects.create_user(username='NoName')
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_paginator(self):
        """Тестирование пагинатора"""
        templates = [INDEX_URL, GROUP_LIST_URL, PROFILE_URL]
        for template in templates:
            with self.subTest(template=template):
                response = self.authorized_client.get(template)
                self.assertEqual(len(response.context['page_obj']), 10)
                response_two = self.authorized_client.get(template + '?page=2')
                self.assertEqual(len(response_two.context['page_obj']), 2)


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class PageTests(TestCase):

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.author = User.objects.create_user(username='auth')
        cls.author_client = Client()
        cls.author_client.force_login(cls.author)
        cls.author_test = User.objects.create_user(username='auth-test')
        cls.author_test_client = Client()
        cls.author_test_client.force_login(cls.author_test)
        cls.author_follow = User.objects.create_user(username='auth-follow')
        cls.author_follow_client = Client()
        cls.author_follow_client.force_login(cls.author_follow)
        cls.small_gif = (b'\x47\x49\x46\x38\x39\x61\x02\x00'
                         b'\x01\x00\x80\x00\x00\x00\x00\x00'
                         b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
                         b'\x00\x00\x00\x2C\x00\x00\x00\x00'
                         b'\x02\x00\x01\x00\x00\x02\x02\x0C'
                         b'\x0A\x00\x3B')
        cls.uploaded = SimpleUploadedFile(
            name='small.gif',
            content=cls.small_gif,
            content_type='image/gif')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test-slug',
            description='Тестовое описание',)
        cls.group_test = Group.objects.create(title='Ошибочная группа',
                                              slug='test-slug-test',
                                              description='Неверная группа',)
        cls.post = Post.objects.create(text='Тестовая запись',
                                       author=cls.author,
                                       group=cls.group,
                                       image=cls.uploaded)
        cls.comment = Comment.objects.create(text='Комментарий',
                                             author=cls.author,
                                             post=cls.post)
        cls.follow = Follow.objects.create(author=cls.author,
                                           user=cls.author_test)

    def setUp(self) -> None:
        self.guest_client = Client()
        self.user = User.objects.create_user(username='NoName')
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_pages_uses_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""
        templates_pages_names = {
            POST_DETAIL_URL: 'posts/post_detail.html',
            POST_EDIT_URL: 'posts/post_create.html',
            INDEX_URL: 'posts/index.html',
            POST_CREATE_URL: 'posts/post_create.html',
            PROFILE_URL: 'posts/profile.html',
            GROUP_LIST_URL: 'posts/group_list.html'}
        for reverse_name, template in templates_pages_names.items():
            with self.subTest(reverse_name=reverse_name):
                response = self.author_client.get(reverse_name)
                self.assertTemplateUsed(response, template)

    def correct_fields(self, adress):
        """Функция для проверки полей."""
        response = self.author_client.get(adress)
        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.fields.ChoiceField,
            'image': forms.fields.ImageField, }
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context['form'].fields[value]
                self.assertIsInstance(form_field, expected)

    def correct_context(self, adress):
        """Функция для проверки контекста."""
        response = self.author_client.get(adress)
        first_object = response.context['page_obj'][0]
        self.assertEqual(first_object.text, 'Тестовая запись')
        self.assertEqual(first_object.group.title, 'Тестовая группа')
        self.assertEqual(first_object.author.username, 'auth')
        self.assertEqual(first_object.image, PageTests.post.image)

    def test_post_create_show_correct_context(self):
        """Шаблон post_create сформирован с правильным полями."""
        self.correct_fields(POST_CREATE_URL)

    def test_post_edit_show_correct_context(self):
        """Шаблон post_edit сформирован с правильным полями."""
        response = self.author_client.get(POST_EDIT_URL)
        self.assertEqual(response.context['post'].text, 'Тестовая запись')
        self.assertEqual(response.context['post'].group.title,
                         'Тестовая группа')
        self.assertEqual(response.context['post'].author.username, 'auth')
        self.correct_fields(POST_EDIT_URL)

    def test_index_page_show_correct_context(self):
        """Шаблон index сформирован с правильным контекстом."""
        self.correct_context(INDEX_URL)

    def test_group_list_page_show_correct_context(self):
        """Шаблон group_list сформирован с правильным контекстом."""
        response = self.authorized_client.get(GROUP_LIST_URL)
        self.assertEqual(response.context['group'].description,
                         'Тестовое описание')
        self.assertEqual(response.context['group'].slug, 'test-slug')
        self.correct_context(GROUP_LIST_URL)

    def test_post_detail_page_show_correct_context(self):
        """Шаблон post_detail сформирован с правильным контекстом."""
        response = self.author_client.get(POST_DETAIL_URL)
        posts = response.context['post_page']
        self.assertEqual(posts.pk, self.post.id)
        self.assertEqual(posts.text, 'Тестовая запись')
        self.assertEqual(posts.image, PageTests.post.image)

    def test_profile_page_show_correct_context(self):
        """Шаблон profile сформирован с правильным контекстом."""
        response = self.author_client.get(PROFILE_URL)
        self.assertEqual(response.context['post_count'], 1)
        self.correct_context(PROFILE_URL)

    def test_group_page_show_incorrect_context(self):
        """Проверка, что пост не попал в группу,
        для которой не был предназначен."""
        response = (self.authorized_client.
                    get(reverse('posts:group_list',
                                kwargs={'slug': 'test-slug-test'})))
        self.assertEqual(response.context['group'].title, 'Ошибочная группа')
        self.assertEqual(response.context['group'].slug, 'test-slug-test')
        self.assertEqual(len(response.context['page_obj']), 0)

    def test_cache_index(self):
        """Проверка работы кэширования."""
        response = self.authorized_client.get(INDEX_URL).content
        form_data = {
            'group': self.group.pk,
            'text': 'Страницы нет', }
        self.authorized_client.post(
            reverse('posts:post_create'),
            data=form_data,
            follow=True)
        response_two = self.authorized_client.get(INDEX_URL).content
        self.assertEqual(response_two, response)
        cache.clear()
        response_cache = self.authorized_client.get(INDEX_URL).content
        self.assertNotEqual(response_cache, response)

    def test_follow(self):
        """Проверка работы функций отписки и подписки на авторов."""
        follows_before = Follow.objects.count()
        self.author_test_client.get(PROFILE_FOLLOW)
        self.assertEqual(Follow.objects.count(), follows_before + 1)
        self.assertTrue(Follow.objects.filter(
            author=PageTests.follow.author).exists())
        follows_after = Follow.objects.count()
        self.author_test_client.get(PROFILE_UNFOLLOW)
        self.assertEqual(Follow.objects.count(), follows_after - 1)
        self.assertFalse(Follow.objects.filter(
            author=self.author_follow).exists())

    def test_follow_redirect_for_unauth(self):
        """Проверка редиректа неавторизированного пользователя
        для функции подписки."""
        response = self.guest_client.get(PROFILE_FOLLOW)
        self.assertRedirects(response, RDR_GUEST)

    def test_follow_context(self):
        """Проверка появления записей в ленте у подписчиков,
        и отсутствие поста в избранном у неподписанного пользователя"""
        self.author_test_client.get(reverse('posts:profile_follow',
                                            kwargs={'username': 'auth'}))
        response = self.author_test_client.get('/follow/')
        first_object = response.context['page_obj'][0]
        self.assertEqual(first_object.text, 'Тестовая запись')
        self.assertEqual(first_object.group.title, 'Тестовая группа')
        form_data = {
            'group': PageTests.group.pk,
            'text': 'А ты не подписан', }
        self.author_follow_client.post(POST_CREATE_URL,
                                       data=form_data,
                                       follow=True)
        post = Post.objects.get(text='А ты не подписан')
        response_unfollow = self.author_test_client.get('/follow/')
        self.assertNotContains(response_unfollow, post)
