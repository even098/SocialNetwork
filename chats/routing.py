from django.urls import path, include, re_path
from chats.consumers import ChatConsumer

websocket_urlpatterns = [
    re_path(r'ws/chat/(?P<chat_id>[a-f0-9-]+)/$', ChatConsumer.as_asgi()),
]
