from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.test import APITestCase, APIClient

from comments.models import Comment
from posts.models import Post

User = get_user_model()
API_BASE = 'http://127.0.0.1:8000/api/v1/comments'


class TestCommentsAPIViews(APITestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(username='user1', password='user1')
        self.other_user = User.objects.create_user(username='user2', password='user2')
        self.post = Post.objects.create(content='test post', author=self.user)

    def get_update_comment_response(self, user=None):
        if user:
            self.login(user)

        self.comment = Comment.objects.create(user=self.user, text='test', post=self.post)
        self.url = f'{API_BASE}/edit/{self.comment.id}/'
        response = self.client.patch(self.url, data={'text': 'edited'})
        return response

    def get_delete_comment_response(self, user=None):
        if user:
            self.login(user)

        self.comment = Comment.objects.create(user=self.user, text='test', post=self.post)
        self.url = f'{API_BASE}/delete/{self.comment.id}/'
        response = self.client.delete(self.url)
        return response

    def test_create_comment_authorized(self):
        self.login(self.user)
        self.url = f'{API_BASE}/create/'
        response = self.client.post(self.url, data={'post_id': self.post.id, 'text': 'test'})
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['text'], 'test')
        self.assertEqual(response.data['user'], {'id': self.user.id, 'username': self.user.username})

    def test_create_comment_not_authorized(self):
        self.url = f'{API_BASE}/create/'
        response = self.client.post(self.url, data={'post_id': self.post.id, 'text': 'test'})
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_update_comment_authorized(self):
        response = self.get_update_comment_response(user=self.user)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['text'], 'edited')
        self.assertEqual(response.data['user'], {'id': self.user.id, 'username': self.user.username})

    def test_update_comment_not_authorized(self):
        response = self.get_update_comment_response()
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_update_comment_not_author(self):
        response = self.get_update_comment_response(user=self.other_user)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_delete_comment_authorized(self):
        response = self.get_delete_comment_response(user=self.user)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Comment.objects.count(), 0)

    def test_delete_comment_unauthorized(self):
        response = self.get_delete_comment_response()
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_delete_comment_not_author(self):
        response = self.get_delete_comment_response(user=self.other_user)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_like_comment(self):
        self.login(self.user)
        self.comment = Comment.objects.create(user=self.user, text='test', post=self.post)
        self.url = f'{API_BASE}/like/{self.comment.id}/'
        response = self.client.post(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['likes_count'], 1)

    def test_like_comment_unauthorized(self):
        self.comment = Comment.objects.create(user=self.user, text='test', post=self.post)
        self.url = f'{API_BASE}/like/{self.comment.id}/'
        response = self.client.post(self.url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def login(self, user):
        self.client.login(username=user.username, password=user.username)
