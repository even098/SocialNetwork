from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.test import APITestCase, APIClient

from posts.models import Post

User = get_user_model()
API_BASE = 'http://127.0.0.1:8000/api/v1/posts'


def login(test_case, user):
    test_case.client.login(username=user.username, password=user.username)


class TestPostCreateAPIView(APITestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(username='test1', password='test1')
        self.url = f'{API_BASE}/create/'

    def test_post_create_authorized(self):
        login(self, self.user)
        response = self.client.post(self.url, {'content': 'test'})
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['content'], 'test')
        self.assertEqual(response.data['photo'], None)
        self.assertEqual(len(response.data['tags']), 0)

    def test_post_create_unauthorized(self):
        response = self.client.post(self.url, {'content': 'test'})
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class TestPostEditAPIView(APITestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(username='test1', password='test1')
        self.other_user = User.objects.create_user(username='test2', password='test2')
        self.post = Post.objects.create(author=self.user, content='test', photo=None)
        self.url = f'{API_BASE}/edit/{self.post.id}/'

    def test_post_edit_authorized(self):
        login(self, self.user)
        response = self.client.patch(self.url, {'content': 'edited'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['content'], 'edited')
        self.assertEqual(response.data['photo'], None)
        self.assertEqual(len(response.data['tags']), 0)

    def test_post_edit_not_author(self):
        login(self, self.other_user)
        response = self.client.patch(self.url, {'content': 'edited'})
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_post_edit_unauthorized(self):
        response = self.client.patch(self.url, {'content': 'edited'})
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class TestPostDeleteAPIView(APITestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(username='test1', password='test1')
        self.other_user = User.objects.create_user(username='test2', password='test2')
        self.post = Post.objects.create(author=self.user, content='test', photo=None)
        self.url = f'{API_BASE}/delete/{self.post.id}/'

    def test_post_delete_authorized(self):
        login(self, self.user)
        response = self.client.delete(self.url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Post.objects.all().count(), 0)

    def test_post_delete_other_user(self):
        login(self, self.other_user)
        response = self.client.delete(self.url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(Post.objects.all().count(), 1)

    def test_post_delete_unauthorized(self):
        response = self.client.delete(self.url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(Post.objects.all().count(), 1)

    def test_post_delete_not_exists(self):
        self.url = f'{API_BASE}/delete/-1/'
        response = self.client.delete(self.url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)


class TestLikePostAPIView(APITestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(username='test1', password='test1')
        self.post = Post.objects.create(author=self.user, content='test', photo=None)
        self.url = f'{API_BASE}/like/{self.post.id}/'

    def test_post_like_authorized(self):
        login(self, self.user)
        response = self.client.post(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['likes_count'], 1)

        response = self.client.post(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['likes_count'], 0)

    def test_post_like_unauthorized(self):
        response = self.client.post(self.url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_not_exists_post_like(self):
        self.url = f'{API_BASE}/like/-1/'
        login(self, self.user)
        response = self.client.post(self.url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)


class TestPostCommentsListAPIView(APITestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(username='test1', password='test1')
        self.post = Post.objects.create(author=self.user, content='test', photo=None)
        self.url = f'{API_BASE}/{self.post.id}/comments/'

    def test_post_comments_authorized(self):
        login(self, self.user)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['post']['id'], self.post.id)
        self.assertEqual(response.data['post']['content'], self.post.content)
        self.assertEqual(response.data['post']['views'], 1)
        self.assertEqual(len(response.data['comments']), 0)

    def test_post_comments_unauthorized(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['post']['views'], 0)
