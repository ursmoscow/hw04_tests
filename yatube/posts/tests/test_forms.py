from faker import Faker
from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from posts.models import Group, Post

fake = Faker()
User = get_user_model()


class PostCreateFormTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.group = Group.objects.create(
            title='Текстовый заголовок',
            slug='test_slug',
            description='Тестовое описание'
        )
        cls.test_user = User.objects.create_user(username='test_user')

        cls.post = Post.objects.create(
            text=fake.text(),
            author=cls.test_user,
            group=cls.group,
        )

    def setUp(self):
        self.authorized_client = Client()
        self.guest_client = Client()
        self.authorized_client.force_login(self.test_user)

    def test_create_post(self):
        """Тестирование создания Post"""
        post_count = Post.objects.count()
        form_data = {
            'text': fake.text(),
            'group': self.group.id,
        }
        response = self.authorized_client.post(
            reverse('posts:post_create'),
            data=form_data,
            follow=True
        )
        new_post = Post.objects.first()
        self.assertRedirects(response, reverse(
            'posts:profile', kwargs={'username': new_post.author}))
        self.assertEqual(Post.objects.count(), post_count + 1)
        self.assertEqual(form_data['text'], new_post.text)
        self.assertEqual(self.test_user, new_post.author)
        self.assertEqual(self.group, new_post.group)

    def test_not_create_post_no_authorized_client(self):
        """Неавторизованный клиент, не может создать
        пост и переадресовывается на страницу логина"""
        form_data = {
            'text': fake.text(),
            'group': self.group.id,
        }
        post_count = Post.objects.count()
        response = self.client.post(
            reverse('posts:post_create'),
            data=form_data,
            follow=True
        )
        login_url = reverse('users:login')
        create_url = reverse('posts:post_create')
        self.assertRedirects(response, f'{login_url}?next={create_url}')
        self.assertEqual(post_count, Post.objects.count())

    def test_post_edit_authorized_user(self):
        """Авторизованный пользователь. Редактирование поста."""
        post = self.post
        form_data = {
            'text': fake.text(),
            'group': self.group.id,
        }
        posts_count = Post.objects.count()
        response = self.authorized_client.post(
            reverse('posts:post_edit', kwargs={'post_id': post.id}),
            data=form_data,
            follow=True
        )
        redirect = reverse(
            'posts:post_detail',
            kwargs={'post_id': post.id})
        self.assertRedirects(response, redirect)
        self.assertEqual(Post.objects.count(), posts_count)
        self.assertTrue(
            Post.objects.filter(
                text=form_data['text'],
                group=self.group.id,
                author=self.test_user
            ).exists()
        )
