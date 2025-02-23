from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.test import APITestCase, APIClient

User = get_user_model()
API_BASE = 'http://127.0.0.1:8000/api/v1/users'


class TestUserProfileAPIView(APITestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(username='test', password='test')

    def test_user_profile(self):
        self.url = f'{API_BASE}/profile/{self.user.id}/'
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['username'], self.user.username)
        self.assertEqual(response.data.get('email'), None)

    def test_user_profile_not_found(self):
        self.url = f'{API_BASE}/profile/-1/'
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)


class TestUserUpdateAPIView(APITestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(username='test', password='test', email='test@gmail.com')

    def test_user_update_authorized(self):
        self.client.login(username='test', password='test')
        self.url = f'{API_BASE}/profile/edit/'
        response = self.client.patch(self.url, {'username': 'edited', 'password': 'edited'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['username'], 'edited')
        self.assertEqual(response.data['email'], self.user.email)

    def test_user_update_unauthorized(self):
        self.url = f'{API_BASE}/profile/edit/'
        response = self.client.patch(self.url, {'username': 'edited', 'password': 'edited'})
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
