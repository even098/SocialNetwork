from django.contrib.auth import get_user_model
from rest_framework import serializers
from taggit.models import Tag

from chats.models import Chat, Message
from chats.serializers import UserSerializer
from posts.models import Post


class ChatSearchSerializer(serializers.ModelSerializer):
    participants = UserSerializer(many=True, read_only=True)

    class Meta:
        model = Chat
        fields = ['id', 'name', 'participants']
        read_only_fields = ['id', 'participants']


class MessageSearchSerializer(serializers.ModelSerializer):
    class Meta:
        model = Message
        fields = ['chat', 'id', 'text', 'sender', 'is_read', 'created_at']
        read_only_fields = fields


class PostSearchSerializer(serializers.ModelSerializer):
    tags = serializers.SlugRelatedField(
        many=True,
        read_only=False,
        slug_field='name',
        queryset=Tag.objects.all()
    )

    class Meta:
        model = Post
        fields = ['id', 'content', 'photo', 'tags', 'created_at']
        read_only_fields = fields


class UserSearchSerializer(serializers.ModelSerializer):
    class Meta:
        model = get_user_model()
        fields = ['id', 'username', 'first_name', 'last_name', 'avatar', 'location']
        read_only_fields = fields
