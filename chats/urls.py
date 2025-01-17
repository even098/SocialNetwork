from django.contrib import admin
from django.urls import path, include

from chats import views

urlpatterns = [
    path('<uuid:chat_id>/', views.ChatInfoAPIView.as_view()),  # Gets chat info/Deletes chat
    path('', views.ChatsListCreateAPIView.as_view()),  # Gets user chats list/Creates chat
    path('<uuid:chat_id>/messages/', views.ChatMessagesAPIView.as_view()),  # Gets chat messages/Create message
    path('unread/', views.UnreadMessagesAPIView.as_view()),  # Returns unread messages count for current user
    path('<uuid:chat_id>/mark_as_read/', views.ChatMessagesMarkAsReadAPIView.as_view()),  # Mark messages as read
    path('<slug:chat_id>/connect/', views.ChatConnectURLAPIView.as_view()),  # Returns websocket-url to connect to
                                                                             # the chat
]
