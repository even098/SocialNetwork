from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
from rest_framework import serializers

from chats.models import Chat


User = get_user_model()


class ChatSerializer(serializers.ModelSerializer):
    id = serializers.UUIDField(read_only=True)
    name = serializers.CharField(max_length=255, read_only=True)
    participant_id = serializers.IntegerField(write_only=True)
    last_message = serializers.CharField(read_only=True)

    class Meta:
        model = Chat
        fields = ['id', 'name', 'participant_id', 'last_message']

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
