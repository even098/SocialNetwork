from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.test import APITestCase, APIClient

from notifications.models import Notification

User = get_user_model()
API_BASE = 'http://127.0.0.1:8000/api/v1/notifications'


class TestNotificationsListAPIView(APITestCase):
    def setUp(self):
        self.client = APIClient()
        self.url = API_BASE + '/'
        self.user = User.objects.create_user(username='test1', password='test1')

    def test_get_notifications_authorized(self):
        self.client.login(username=self.user.username, password=self.user.username)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 0)

        Notification.objects.create(user=self.user, text='test', content_type_id=1, target_object_id=1)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    def test_get_notifications_not_authorized(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class TestNotificationReadAPIView(APITestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(username='test1', password='test1')
        self.notification = Notification.objects.create(user=self.user, text='test', content_type_id=1, target_object_id=1)
        self.url = f'{API_BASE}/read/{self.notification.id}/'

    def test_read_notification_authorized(self):
        self.client.login(username=self.user.username, password=self.user.username)
        response = self.client.post(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['message'], 'Notification marked as read')

    def test_read_notification_unauthorized(self):
        response = self.client.post(self.url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class TestAllNotificationsReadAPIView(TestNotificationReadAPIView):
    def setUp(self):
        super().setUp()
        self.url = f'{API_BASE}/read/all/'

    def test_read_notification_authorized(self):
        self.client.login(username=self.user.username, password=self.user.username)
        response = self.client.post(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['message'], 'All notifications marked as read')

    def test_read_notification_unauthorized(self):
        response = self.client.post(self.url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
