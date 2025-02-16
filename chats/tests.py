import uuid

import aiounittest
from asgiref.sync import sync_to_async
from channels.db import database_sync_to_async
from channels.routing import URLRouter
from channels.testing import WebsocketCommunicator
from django.contrib.auth import get_user_model
from django.test import TestCase, override_settings, AsyncClient
from django.urls import path, re_path
from pip._vendor.urllib3.util.url import get_host
from rest_framework import status
from rest_framework.test import APITestCase, APIClient

from chats.consumers import ChatConsumer
from chats.models import Chat, Message

User = get_user_model()
API_BASE = 'http://127.0.0.1:8000/api/v1/chats'


def get_chat_url(chat_id):
    return f'{API_BASE}/{chat_id}/'


def assert_permission_denied(test_case, url, user, request_method, request_body=None, status_code=None):
    request_method = request_method.lower()
    status_code = status_code if status_code else status.HTTP_401_UNAUTHORIZED

    if user:
        test_case.login(user=user)
        status_code = status.HTTP_403_FORBIDDEN

    match request_method:
        case 'get':
            response = test_case.client.get(url)
        case 'post':
            response = test_case.client.post(url, data=request_body)
        case 'delete':
            response = test_case.client.delete(url)
        case _:
            raise ValueError(f'Expected request method: {request_method}')

    test_case.assertEqual(response.status_code, status_code)


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
        self.url = API_BASE + '/'

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
        self.url = f'{API_BASE}/{self.chat1.id}/messages/'
        self.message = Message.objects.create(chat=self.chat1, text='test message', sender=self.participant_1)

    def test_permissions(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.login(user=self.not_participant)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        response = self.client.post(self.url, data={'text': 'test message'})
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_get_messages(self):
        self.login(user=self.participant_1)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
        self.assertEqual(response.data['count'], 1)
        self.assertEqual(response.data['results'][0]['text'], 'test message')

    def test_create_message(self):
        self.login(user=self.participant_1)
        response = self.client.post(self.url, data={'text': 'test message'})
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['text'], 'test message')
        self.assertEqual(response.data['sender']['id'], self.participant_1.id)
        self.assertEqual(response.data['sender']['username'], self.participant_1.username)


async def async_login(client, user):
    await sync_to_async(client.login)(username=user.username, password=user.username)


class TestAsyncEndpoints(aiounittest.AsyncTestCase):
    async def prepare_test_data(self):
        username, username2 = str(uuid.uuid4()), str(uuid.uuid4())
        self.participant_1 = await database_sync_to_async(User.objects.create_user)(
            username=username, password=username
        )
        self.participant_2 = await database_sync_to_async(User.objects.create_user)(
            username=username2, password=username2
        )
        self.chat = await database_sync_to_async(Chat.objects.create)()
        self.client = AsyncClient()
        await database_sync_to_async(self.chat.participants.set)([self.participant_1, self.participant_2])

        self.application = URLRouter([
            re_path(r'ws/chat/(?P<chat_id>[a-f0-9-]+)/$', ChatConsumer.as_asgi()),
        ])

        await async_login(self.client, self.participant_1)

    async def test_chat_message_sends_to_channel_layer(self):
        await self.prepare_test_data()
        url = f'{API_BASE}/{self.chat.id}/messages/'
        communicator = WebsocketCommunicator(self.application, f'ws/chat/{self.chat.id}/')

        await async_login(self.client, self.participant_1)

        connected, subprotocol = await communicator.connect()
        assert connected
        await self.client.post(url, data={'text': 'test message'})

        response = await communicator.receive_json_from()
        assert response['type'] == 'send_message'
        assert response['message'] == 'test message'
        assert response['username'] == self.participant_1.username

        await communicator.disconnect()

    async def test_marked_as_read_message_sends_to_channel_layer(self):
        await self.prepare_test_data()
        url = f'{API_BASE}/{self.chat.id}/mark_as_read/'
        communicator = WebsocketCommunicator(self.application, f'ws/chat/{self.chat.id}/')
        communicator.scope['user'] = self.participant_1
        self.message = await database_sync_to_async(Message.objects.create)(
            text='test message',
            is_read=False,
            chat=self.chat,
            sender=self.participant_2
        )

        connected, subprotocol = await communicator.connect()
        assert connected
        await self.client.patch(url, data={'message_ids': [self.message.id]}, content_type='application/json')

        response = await communicator.receive_json_from()
        assert response['type'] == 'read_confirmation'
        assert response['reader_id'] == self.participant_1.id
        assert response['read_messages'] == [str(self.message.id)]

        await communicator.disconnect()


class TestUnreadMessagesCountAPIView(BaseChatTest):
    def setUp(self):
        super().setUp()
        self.url = f'{API_BASE}/unread/'
        self.message_1 = Message.objects.create(text='test_message', sender=self.participant_2, chat=self.chat1)
        self.message_2 = Message.objects.create(text='test_message', sender=self.participant_1, chat=self.chat1)
        self.message_3 = Message.objects.create(text='test_message', sender=self.participant_1, chat=self.chat1)

    def test_unread_messages(self):
        self.login(self.not_participant)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['unread_messages_count'], 0)

        self.login(self.participant_1)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['unread_messages_count'], 1)


class TestChatConnectURLAPIView(BaseChatTest):
    def setUp(self):
        super().setUp()
        self.url = f'{API_BASE}/{self.chat1.id}/connect/'

    def test_permissions(self):
        assert_permission_denied(test_case=self, url=self.url, user=None, request_method='GET')
        assert_permission_denied(test_case=self, url=self.url, user=self.not_participant, request_method='GET')

    def test_get_connection_url(self):
        self.login(self.participant_1)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['websocket_url'], f'ws://testserver/ws/chat/{self.chat1.id}/')
