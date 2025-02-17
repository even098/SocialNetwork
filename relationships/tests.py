from django.contrib.auth import get_user_model
from django.test import TestCase
from rest_framework import status
from rest_framework.test import APITestCase, APIClient

from relationships.models import Follow

User = get_user_model()
API_BASE = 'http://127.0.0.1:8000/api/v1/relationships'


def login(test_case, user):
    test_case.client.login(username=user.username, password=user.username)


def create_following(follower, following):
    Follow.objects.create(follower=follower, following=following)
    following.followers_count = 1
    following.save()
    follower.following_count = 1
    follower.save()


class TestFollowUserAPIView(APITestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(username='test1', password='test1')
        self.other_user = User.objects.create_user(username='test2', password='test2')

    def test_follow_other_user(self):
        login(self, self.user)
        self.url = f'{API_BASE}/follow/{self.other_user.id}/'
        response = self.client.post(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_follow_yourself(self):
        login(self, self.user)
        self.url = f'{API_BASE}/follow/{self.user.id}/'
        response = self.client.post(self.url)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


    def test_already_following_user(self):
        login(self, self.user)
        self.url = f'{API_BASE}/follow/{self.other_user.id}/'
        Follow.objects.create(follower=self.user, following=self.other_user)
        response = self.client.post(self.url)
        self.assertEqual(response.status_code, status.HTTP_409_CONFLICT)

    def test_follow_not_existing_user(self):
        login(self, self.user)
        self.url = f'{API_BASE}/follow/-1/'
        response = self.client.post(self.url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_follow_unauthorized(self):
        self.url = f'{API_BASE}/follow/{self.user.id}/'
        response = self.client.post(self.url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class TestUnfollowUserAPIView(APITestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(username='test1', password='test1')
        self.other_user = User.objects.create_user(username='test2', password='test2')

    def test_unfollow_valid_user(self):
        login(self, self.user)
        create_following(follower=self.user, following=self.other_user)
        self.url = f'{API_BASE}/unfollow/{self.other_user.id}/'
        response = self.client.delete(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_unfollow_not_following_user(self):
        login(self, self.user)
        self.url = f'{API_BASE}/unfollow/{self.other_user.id}/'
        response = self.client.delete(self.url)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_unfollow_not_existing_user(self):
        login(self, self.user)
        self.url = f'{API_BASE}/unfollow/-1/'
        response = self.client.delete(self.url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_unfollow_unauthorized(self):
        self.url = f'{API_BASE}/unfollow/{self.other_user.id}/'
        response = self.client.delete(self.url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class TestFollowersFollowingListAPIView(APITestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(username='test1', password='test1')
        self.other_user = User.objects.create_user(username='test2', password='test2')
        create_following(follower=self.user, following=self.other_user)

    def test_followers_list(self):
        self.url = f'{API_BASE}/followers/{self.other_user.id}/'
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data[0]['username'], self.user.username)

    def test_following_list(self):
        self.url = f'{API_BASE}/following/{self.user.id}/'
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data[0]['username'], self.other_user.username)

    def test_followers_invalid_user(self):
        self.url = f'{API_BASE}/followers/-1/'
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_following_invalid_user(self):
        self.url = f'{API_BASE}/following/-1/'
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
