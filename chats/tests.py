import uuid

from django.contrib.auth import get_user_model
from django.test import TestCase
from rest_framework import status
from rest_framework.test import APITestCase, APIClient

from chats.models import Chat

User = get_user_model()
API_BASE = 'http://127.0.0.1:8000/api/v1/chats/'


def get_chat_url(chat_id):
    return f'{API_BASE}{chat_id}/'


def assert_permission_denied(test_case, url, user, request_method, request_body=None):
    request_method = request_method.lower()
    if user:
        test_case.login(user=user)

    match request_method:
        case 'get':
            response = test_case.client.get(url)
        case 'post':
            response = test_case.client.post(url, data=request_body)
        case 'delete':
            response = test_case.client.delete(url)
        case _:
            raise ValueError(f'Expected request method: {request_method}')

    test_case.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)


class BaseChatTest(APITestCase):
    def setUp(self):
        self.client = APIClient()
        self.participant_1 = User.objects.create_user(username='test1', password='test1')
        self.participant_2 = User.objects.create_user(username='test2', password='test2')
        self.not_participant = User.objects.create_user(username='test3', password='test3')
        self.chat1 = Chat.objects.create()
        self.chat1.participants.set([self.participant_1, self.participant_2])

    def login(self, user):
        self.client.login(username=user.username, password=user.username)


class TestChatInfoAPIView(BaseChatTest):
    def setUp(self):
        super().setUp()
        self.url = get_chat_url(self.chat1.id)

    def test_permissions(self):
        assert_permission_denied(self, self.url, self.not_participant, 'GET')
        assert_permission_denied(self, self.url, self.not_participant, 'DELETE')

    def test_chat_info(self):
        self.login(user=self.participant_1)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['participants']), 2)
        self.assertEqual(response.data['participants'][1]['username'], self.participant_1.username)
        self.assertEqual(response.data['participants'][0]['username'], self.participant_2.username)

    def test_chat_delete(self):
        self.login(user=self.participant_1)
        response = self.client.delete(self.url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)


class TestChatsListCreateAPIView(BaseChatTest):
    def setUp(self):
        super().setUp()
        self.url = API_BASE

    def test_permissions(self):
        self.login(user=self.not_participant)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 0)

    def test_chats_list_get(self):
        self.login(user=self.participant_1)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    def test_chats_create(self):
        self.login(user=self.participant_1)
        self.random_participant = User.objects.create_user(username=f'test_{uuid.uuid4()}', password='test')
        response = self.client.post(self.url, data={'participant_id': self.random_participant.id})
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(
            response.data['name'],
            f'{self.participant_1.username} - {self.random_participant.username} chat.'
        )


class TestChatMessagesAPIView(BaseChatTest):
    def setUp(self):
        super().setUp()
        self.url = f'{API_BASE}{self.chat1.id}/messages/'
        