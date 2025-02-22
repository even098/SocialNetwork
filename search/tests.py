from django.contrib.auth import get_user_model
from django.contrib.postgres.search import SearchVector
from django.db import connection
from django.urls import resolve
from rest_framework import status
from rest_framework.test import APITestCase, APIClient

from chats.models import Chat, Message
from posts.models import Post

User = get_user_model()
API_BASE = 'http://127.0.0.1:8000/api/v1/search'


class TestSearchChatsAPIView(APITestCase):
    def login(self, user):
        self.client.login(username=user.username, password=user.username)

    def setUp(self):
        self.client = APIClient()
        self.participant1 = User.objects.create_user(username='test1', password='test1')
        self.participant2 = User.objects.create_user(username='test2', password='test2')
        self.not_participant = User.objects.create_user(username='test3', password='test3')
        self.chat = Chat.objects.create(name=f'{self.participant1} - {self.participant2} chat.')
        self.chat.participants.set([self.participant1, self.participant2])
        self.chat.save()

    def test_search_chat_by_name_authorized(self):
        self.login(self.participant1)
        self.url = f'{API_BASE}/chats?name=chat'
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data[0]['id'], str(self.chat.id))

    def test_search_chat_by_name_unauthorized(self):
        self.url = f'{API_BASE}/chats?name=chat'
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_search_chat_by_participants_authorized(self):
        self.login(self.participant1)
        self.url = f'{API_BASE}/chats?user={self.participant1.username}'
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data[0]['id'], str(self.chat.id))

    def test_search_chat_by_participants_unauthorized(self):
        self.url = f'{API_BASE}/chats?user={self.participant1.username}'
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_search_chat_by_name_not_participant(self):
        self.login(self.not_participant)
        self.url = f'{API_BASE}/chats?name=chat'
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 0)

    def test_search_chat_by_participants_not_participant(self):
        self.login(self.not_participant)
        self.url = f'{API_BASE}/chats?user={self.participant2.username}'
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 0)


class TestMessagesSearchAPIView(APITestCase):
    def login(self, user):
        self.client.login(username=user.username, password=user.username)

    def setUp(self):
        self.client = APIClient()
        self.participant1 = User.objects.create_user(username='test1', password='test1')
        self.participant2 = User.objects.create_user(username='test2', password='test2')
        self.not_participant = User.objects.create_user(username='test3', password='test3')
        self.chat = Chat.objects.create(name=f'{self.participant1} - {self.participant2} chat.')
        self.chat.participants.set([self.participant1, self.participant2])
        self.chat.save()
        self.message = Message.objects.create(chat=self.chat, sender=self.participant1, text='message')
        Message.objects.filter(id=self.message.id).update(search_vector=SearchVector('text'))
        # назначаем search vector вручную, потому что Сериализатор в данном случае не срабатывает

    def test_search_messages_authorized_participant(self):
        self.login(self.participant1)
        self.url = f'{API_BASE}/messages?keyword=message'
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data[0]['chat'], self.chat.id)
        self.assertEqual(response.data[0]['text'], self.message.text)
        self.assertEqual(response.data[0]['sender'], self.participant1.id)

    def test_search_messages_not_participant(self):
        self.login(self.not_participant)
        self.url = f'{API_BASE}/messages?keyword=message'
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 0)

    def test_search_messages_unauthorized(self):
        self.url = f'{API_BASE}/messages?keyword=message'
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class TestPostsSearchAPIView(APITestCase):
    def login(self, user):
        self.client.login(username=user.username, password=user.username)

    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(username='test1', password='test1')
        self.post = Post.objects.create(content='testing', author=self.user)
        Post.objects.filter(id=self.post.id).update(search_vector=SearchVector('content'))
        # назначаем search vector вручную, потому что Сериализатор в данном случае не срабатывает

    def test_posts_search_by_keyword_authorized(self):
        self.login(self.user)
        self.url = f'{API_BASE}/posts?keyword=testing'
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data[0]['id'], self.post.id)
        self.assertEqual(response.data[0]['content'], self.post.content)

    def test_posts_search_by_author_authorized(self):
        self.login(self.user)
        self.url = f'{API_BASE}/posts?author=test'
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data[0]['id'], self.post.id)
        self.assertEqual(response.data[0]['content'], self.post.content)

    def test_posts_search_unauthorized(self):
        self.url = f'{API_BASE}/posts?keyword=testing'
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class TestUsersSearchAPIView(APITestCase):
    def login(self, user):
        self.client.login(username=user.username, password=user.username)

    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(username='test1', password='test1')

    def test_search_user_authorized(self):
        self.login(self.user)
        self.url = f'{API_BASE}/users?keyword=test'
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data[0]['id'], self.user.id)

    def test_search_not_existing_user(self):
        self.login(self.user)
        self.url = f'{API_BASE}/users?keyword=-1'
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 0)

    def test_search_user_unauthorized(self):
        self.url = f'{API_BASE}/users?keyword=test'
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
