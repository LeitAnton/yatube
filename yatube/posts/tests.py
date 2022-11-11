from urllib.parse import urljoin

from django.core.cache import cache
from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse

from .models import Post


class TestProfile(TestCase):
    def setUp(self):
        self.username = 'testuser'
        self.password = 'password1234'
        self.email = 'test_user02@gmail.com'
        self.first_text = 'Text for first post'
        self.second_text = 'Text for second post'

        self.user = User.objects.create_user(self.username, self.email, self.password)
        self.post = Post.objects.create(text=self.first_text, author=self.user)

        self.urls = (
            reverse('index'),
            reverse('profile', kwargs={'username': self.username}),
            reverse('post', kwargs={'username': self.username, 'post_id': self.post.id})
        )
        self.non_auth_client = Client()
        self.auth_client = Client()
        self.auth_client.force_login(self.user)

    def test_profile_page(self):
        response = self.auth_client.get(reverse('profile', kwargs={'username': self.username}))
        self.assertEqual(response.status_code, 200)
        self.assertIsInstance(response.context['author'], User)
        self.assertEqual(response.context['author'].username, self.user.username)

    def test_auth_client_create_post(self):
        self.auth_client.post(reverse('new_post'), data={'text': self.second_text})
        response = self.auth_client.get(reverse('profile', kwargs={'username': self.username}))
        self.assertEqual(len(response.context['page']), 2)

        for url in self.urls:
            response = self.auth_client.get(url)
            self.assertContains(response, self.post.text)

    def test_non_auth_client_create_post(self):
        response = self.non_auth_client.post(reverse('new_post'), data={'text': self.first_text})
        url = urljoin(reverse('login'), "?login=/new/")
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, url)

    def test_auth_client_edit_post(self):
        self.auth_client.post(
            reverse('post_edit', kwargs={'username': self.username, 'post_id': self.post.id}),
            data={'text': self.second_text+self.first_text},
            follow=True
        )
        post_edit = Post.objects.get(id=self.post.id)
        self.assertEqual(post_edit.text, self.second_text+self.first_text)

        for url in self.urls:
            response = self.auth_client.get(url)
            self.assertContains(response, post_edit.text)

    def test_image_load(self):
        cache.clear()
        with open('media/posts/test.jpg', 'rb') as img:
            self.auth_client.post(
                reverse('new_post'),
                data={'text': 'Post with image', 'author': self.user, 'image': img},
                follow=True
            )
            for url in self.urls[:2]:
                response = self.auth_client.get(url)
                self.assertContains(response, '<img')
