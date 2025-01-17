from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from django.contrib.auth import get_user_model
from django.contrib.postgres.search import SearchVector
from django.shortcuts import get_object_or_404
from rest_framework import serializers

from chats.models import Chat, Message

User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username']


class ChatSerializer(serializers.ModelSerializer):
    id = serializers.UUIDField(read_only=True)
    name = serializers.CharField(max_length=255, read_only=True)
    participant_id = serializers.IntegerField(write_only=True)
    participants = UserSerializer(many=True, read_only=True)
    last_message = serializers.CharField(read_only=True)

    class Meta:
        model = Chat
        fields = ['id', 'name', 'participant_id', 'participants', 'last_message']

    def create(self, validated_data):
        user = self.context['request'].user

        participant_id = validated_data.pop('participant_id')
        participant = get_object_or_404(User, id=participant_id)

        chat = Chat.objects.filter(participants=user.id).filter(participants__id=participant.id).first()

        if chat:
            raise serializers.ValidationError({'detail': 'Chat already exists.', 'chat_id': chat.id})

        chat = Chat.objects.create(name=f'{user} - {participant} chat.')
        chat.participants.set([user, participant])
        return chat


class MessageSerializer(serializers.ModelSerializer):
    sender = serializers.SerializerMethodField()

    class Meta:
        model = Message
        fields = ['id', 'text', 'created_at', 'is_read', 'sender']
        read_only_fields = ['id', 'created_at', 'is_read', 'sender']

    def create(self, validated_data):
        text = validated_data.get('text', None)
        chat_id = self.context['view'].kwargs['chat_id']
        sender = self.context['request'].user
        chat = Chat.objects.filter(id=chat_id).first()

        if not chat:
            raise serializers.ValidationError({'detail': 'Chat does not exist.', 'chat_id': chat_id})

        message = Message.objects.create(text=text, sender=sender, chat=chat)
        message.search_vector = SearchVector('text')
        message.save()
        chat.last_message = message
        chat.save()

        channel_layer = get_channel_layer()
        async_to_sync(channel_layer.group_send)(
            str(chat_id),
            {
                "type": "send_message",
                "message": message.text,
                "username": message.sender.username,
            }
        )

        return message

    def get_sender(self, obj):
        return {
            'id': obj.sender.id,
            'username': obj.sender.username
        }
