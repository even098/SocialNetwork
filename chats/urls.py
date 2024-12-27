from django.contrib import admin
from django.urls import path, include

from chats import views

urlpatterns = [
    path('', views.ChatsAPIView.as_view()),  # Gets users chats list/Creates chat
    # path('<slug:chat_name>/messages/', views.ChatsAPIView.as_view()),
    # path('unread/', views.ChatsAPIView.as_view()),
    # path('<slug:chat_name>/mark_read/', views.ChatsAPIView.as_view()),
    # path('<slug:chat_name>/connect/', views.ChatsAPIView.as_view()),
]
