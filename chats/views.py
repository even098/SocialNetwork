from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from django.db.models import Q, Count, Sum
from rest_framework import exceptions, status
from rest_framework.exceptions import ValidationError
from rest_framework.generics import ListAPIView, ListCreateAPIView, RetrieveAPIView, get_object_or_404, UpdateAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from chats.models import Chat, Message
from chats.paginators import MessagesPaginator
from chats.permissions import IsParticipant
from chats.serializers import ChatSerializer, MessageSerializer


class ChatInfoAPIView(RetrieveAPIView):
    serializer_class = ChatSerializer
    permission_classes = [IsAuthenticated, IsParticipant]

    def delete(self, request, *args, **kwargs):
        try:
            chat = self.get_object()
            Message.objects.filter(chat=chat).delete()
            chat.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        except exceptions.PermissionDenied as e:
            return Response(data={'error': f'Permission denied!'}, status=status.HTTP_403_FORBIDDEN)
        except Exception as e:
            return Response(data={'error': f'An error occurred: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def get_object(self):
        chat = get_object_or_404(Chat, id=self.kwargs['chat_id'])
        self.check_object_permissions(self.request, chat)

        return chat


class ChatsListCreateAPIView(ListCreateAPIView):
    serializer_class = ChatSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Chat.objects.filter(participants=self.request.user)


class ChatMessagesAPIView(ListCreateAPIView):
    serializer_class = MessageSerializer
    permission_classes = [IsAuthenticated, IsParticipant]
    pagination_class = MessagesPaginator

    def get_queryset(self):
        chat = get_object_or_404(Chat, id=self.kwargs['chat_id'])
        self.check_object_permissions(self.request, chat)

        return Message.objects.filter(chat=chat).order_by('created_at')


class UnreadMessagesAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        user = request.user
        unread_messages_count = (
            Chat.objects.filter(participants=user)
                .annotate(
                    unread_count=Count(
                        'messages',
                        filter=Q(messages__is_read=False) | ~Q(messages__sender=user)
                    )
                 )
                .aggregate(total_unread=Sum('unread_count'))['total_unread']
        )

        return Response(data={'unread_messages_count': unread_messages_count}, status=status.HTTP_200_OK)


class ChatMessagesMarkAsReadAPIView(UpdateAPIView):
    permission_classes = [IsAuthenticated, IsParticipant]

    def patch(self, request, *args, **kwargs):
        chat_id = self.kwargs['chat_id']
        message_ids = self.request.data.get('message_ids', [])
        chat = get_object_or_404(Chat, id=chat_id)
        self.check_object_permissions(self.request, chat)

        if len(message_ids) > 100:
            raise exceptions.ValidationError({'detail': 'Too many messages.'})

        updated_count = Message.objects.filter(id__in=message_ids, is_read=False).update(is_read=True)

        channel_layer = get_channel_layer()
        async_to_sync(channel_layer.group_send)(
            str(chat_id),
            {
                "type": "read_messages",
                "reader_id": request.user.id,
                "message_ids": message_ids,
                "updated_count": updated_count
            }
        )

        return Response(data={"detail": f"{updated_count} messages marked as read."}, status=status.HTTP_200_OK)


class ChatConnectURLAPIView(APIView):
    permission_classes = [IsAuthenticated, IsParticipant]

    def get(self, request, *args, **kwargs):
        chat_id = self.kwargs['chat_id']
        chat = get_object_or_404(Chat, id=chat_id)
        self.check_object_permissions(self.request, chat)

        return Response(data={'websocket_url': f'ws://{request.get_host()}/ws/chat/{chat_id}/'},
                        status=status.HTTP_200_OK)
