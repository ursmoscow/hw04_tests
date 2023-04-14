import random
from faker import Faker
from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse
from django import forms
from django.conf import settings

from posts.models import Group, Post

fake = Faker()
User = get_user_model()


class PostPagesTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='TestUser')
        cls.group = Group.objects.create(
            title='Тестовое название группы',
            slug='group-slug',
            description='Тестовое описание группы',
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text=fake.text(),
            group=cls.group,
        )

    def setUp(self):

        self.authorized_client = Client()
        self.guest_client = Client()
        self.authorized_client.force_login(self.user)

    def test_group_list_page_show_correct_context(self):
        """Шаблон group_list сформирован с правильным контекстом."""
        response = self.guest_client.get(reverse('posts:group_list',
                                                 kwargs={'slug':
                                                         self.group.slug}))
        first_object = response.context['page_obj'][0]
        second_object = response.context['group']
        self.assertIn('page_obj', response.context)
        self.assertIn('group', response.context)
        self.assertEqual(first_object, Post.objects.first())
        self.assertEqual(second_object, Group.objects.first())

    def test_post_detail_pages_show_correct_context(self):
        """Шаблон post_detail сформирован с правильным контекстом."""
        reverse_page = reverse('posts:post_detail',
                               kwargs={'post_id': self.post.id})
        response = (self.authorized_client.get(reverse_page))
        first_object = response.context['user_post']
        self.assertIn('user_post', response.context)
        self.assertEqual(first_object, Post.objects.first())

    def test_index_page_show_correct_context(self):
        """Шаблон index сформирован с правильным контекстом."""
        response = self.guest_client.get(reverse('posts:index'))
        test_post = response.context['page_obj'][0]
        self.assertEqual(test_post, self.post)
        self.assertEqual(test_post.author, self.post.author)
        self.assertEqual(test_post.text, self.post.text)
        self.assertEqual(test_post.group, self.post.group)

    def test_profile_page_show_correct_context(self):
        """Шаблон profile сформирован с правильным контекстом."""
        response = self.guest_client.get(reverse('posts:profile',
                                                 kwargs={'username':
                                                         self.user.username}))
        test_post = response.context['page_obj'][0]
        self.assertEqual(test_post, self.post)
        self.assertEqual(test_post.author, self.post.author)
        self.assertEqual(test_post.text, self.post.text)
        self.assertEqual(test_post.group, self.post.group)

    def test_create_post_page_show_correct_context(self):
        """Шаблон create_post сформирован с правильным контекстом."""
        response = self.authorized_client.get(reverse('posts:post_create'))
        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.models.ModelChoiceField,
        }
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context.get('form').fields.get(value)
                self.assertIsInstance(form_field, expected)

    def test_edit_post_page_show_correct_context(self):
        """Шаблон edit_post сформирован с правильным контекстом."""
        self.author_client = Client()
        self.author_client.force_login(self.user)
        response = self.author_client.get(reverse(
            'posts:post_edit', kwargs={'post_id': self.post.id}))
        form_field = response.context.get('form').fields.get('text')
        self.assertIsInstance(form_field, forms.fields.CharField)


class PaginatorViewsTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='Artem1993',
                                            email='test@mail.ru',
                                            password='test_pass',)
        cls.group = Group.objects.create(
            title='Заголовок для тестовой группы',
            slug='test_slug2',
            description='Тестовое описание')

        cls.post_test_count = random.randint(settings.POSTS_CHIK + 1,
                                             settings.POSTS_CHIK * 2)
        for i in range(cls.post_test_count):
            Post.objects.bulk_create([
                Post(text=fake,
                     author=cls.user,
                     group=cls.group)
            ])

    def setUp(self):
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_pagination(self):
        """Тестирование Paginatora"""
        count_post_one_page = settings.POSTS_CHIK
        all_count = PaginatorViewsTest.post_test_count
        count_post_two_page = all_count - count_post_one_page
        tested_urls_paginations = {
            reverse('posts:index'),
            reverse('posts:group_list',
                    kwargs={'slug': self.group.slug}),
            reverse('posts:profile',
                    kwargs={'username': self.user})
        }
        for url in tested_urls_paginations:
            with self.subTest(url=url):
                response_one_page = self.client.get(url)
                self.assertEqual(
                    len(response_one_page.context['page_obj']),
                    settings.POSTS_CHIK)
                response_two_page = self.client.get(url + '?page=2')
                self.assertEqual(
                    len(response_two_page.context['page_obj']),
                    count_post_two_page)
