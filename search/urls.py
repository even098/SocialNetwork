from django.urls import path

from search import views

urlpatterns = [
    path('chats/', views.ChatsSearchAPIView.as_view()),  # Search chats with given name/participants and returns it
    path('messages/', views.MessagesSearchAPIView.as_view()),  # Search message with given keyword
    path('posts/', views.PostsSearchAPIView.as_view()),  # Search posts with given keyword (full-text search)
    path('users/', views.UsersSearchAPIView.as_view()),  # Search users with given keyword (username/first/last names)
]
