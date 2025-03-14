from django.db.models import Q, F
from rest_framework import status
from rest_framework.exceptions import ValidationError
from rest_framework.generics import RetrieveAPIView, ListAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from chats.models import Chat, Message
from posts.models import Post
from search.filters import get_filtered_chats, get_filtered_users, get_filtered_posts
from search.serializers import ChatSearchSerializer, MessageSearchSerializer, PostSearchSerializer, UserSearchSerializer

from django.contrib.postgres.search import SearchQuery, SearchRank, SearchVector


class ChatsSearchAPIView(ListAPIView):
    serializer_class = ChatSearchSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        name = self.request.GET.get('name')
        users = self.request.GET.get('users')

        if (name and len(name) > 100) or (users and len(users) > 50):
            raise ValidationError('Name or users field is too long!')

        return get_filtered_chats(self.request.user, name, users)


class MessagesSearchAPIView(ListAPIView):
    serializer_class = MessageSearchSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        keyword = self.request.GET.get('keyword')

        if keyword and len(keyword) > 100:
            raise ValidationError('Keyword is too long!')

        query = SearchQuery(keyword)

        results = Message.objects.annotate(
            rank=SearchRank(F('search_vector'), query)
        ).filter(search_vector=query, chat__participants=self.request.user).order_by('-rank')

        return results


class PostsSearchAPIView(ListAPIView):
    serializer_class = PostSearchSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        author = self.request.GET.get('author')
        keyword = self.request.GET.get('keyword')

        if (keyword and len(keyword) > 100) or (author and len(author) > 50):
            raise ValidationError('Keyword or author field is too long!')

        results = get_filtered_posts(author, keyword)

        return results


class UsersSearchAPIView(ListAPIView):
    serializer_class = UserSearchSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        keyword = self.request.GET.get('keyword')

        if keyword and len(keyword) > 100:
            raise ValidationError('Keyword is too long!')

        results = get_filtered_users(keyword)
        return results
