from django.urls import path, include
from chats.consumers import ChatConsumer

# Here, "" is routing to the URL ChatConsumer which
# will handle the chat functionality.
websocket_urlpatterns = [
    path("ws/chats/<slug:chat_name>", ChatConsumer.as_asgi()),
]
