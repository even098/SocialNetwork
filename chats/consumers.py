import json
from urllib.parse import parse_qs

from channels.db import database_sync_to_async
from channels.generic.websocket import AsyncWebsocketConsumer
from django.shortcuts import get_object_or_404
from rest_framework_simplejwt.tokens import AccessToken

from chats.models import Chat, Message
from chats.serializers import MessageSerializer
from search.serializers import MessageSearchSerializer


class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.chat_id = self.scope["url_route"]["kwargs"]["chat_id"]
        # chat = await database_sync_to_async(get_object_or_404)(Chat, id=self.chat_id)
        # user = self.scope['user']

        query_params = parse_qs(self.scope["query_string"].decode("utf-8"))
        message_id = query_params.get("message_id", [None])[0]

        # if not user.is_authenticated or user not in chat.participants.all():
        #     await self.close()

        await self.channel_layer.group_add(
            self.chat_id,
            self.channel_name
        )
        await self.accept()

        if message_id:
            await self.channel_layer.group_send(
                self.chat_id,
                {
                    "type": "navigate_to_message",
                    "message_id": message_id,
                }
            )

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(
            self.chat_id,
            self.channel_name
        )

    async def receive(self, text_data):
        text_data_json = json.loads(text_data)

        if "type" not in text_data_json:
            await self.close()
            return

    async def send_message(self, event):
        message = event["message"]
        username = event["username"]

        await self.send(text_data=json.dumps({"type": "send_message", "message": message, "username": username}))

    async def read_messages(self, event):
        try:
            message_ids = event["message_ids"]
            user_id = self.scope["user"].id

            await self.send(text_data=json.dumps({
                "type": "read_confirmation",
                "reader_id": user_id,
                "read_messages": message_ids,
            }))
        except Chat.DoesNotExist:
            await self.send(text_data=json.dumps({
                "type": "error",
                "message": "Chat not found."
            }))
        except Exception as e:
            await self.send(text_data=json.dumps({
                "type": "error",
                "message": f"An error occurred: {str(e)}"
            }))

    async def navigate_to_message(self, event):
        message_id = event["message_id"]
        message = await database_sync_to_async(Message.objects.filter(id=str(message_id)).first)()

        if message:
            await self.send(text_data=json.dumps(
                {
                    'type': event['type'],
                    'chat_id': str(message.chat_id),
                    'message_id': str(message_id),
                    'text': message.text,
                    'created_at': message.created_at.isoformat(),
                    'sender_id': message.sender_id,
                    'highlight': True
                }
            ))
        else:
            await self.send(text_data=json.dumps({'type': 'error', 'message': f'Message not found.'}))
