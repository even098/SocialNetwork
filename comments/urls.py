from django.urls import path

from comments import views

urlpatterns = [
    path('create/post/<int:post_id>/', views.CommentCreateAPIView.as_view()),
    path('edit/<int:comment_id>/', views.CommentUpdateAPIView.as_view()),
    path('delete/<int:comment_id>/', views.CommentDeleteAPIView.as_view()),
    path('like/<int:comment_id>/', views.LikeCommentAPIView.as_view())
]
