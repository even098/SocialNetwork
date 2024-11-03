from django.urls import path

from comments import views

urlpatterns = [
    path('post/<int:post_id>/', views.CommentListAPIView.as_view()),
    path('post/<int:post_id>/create/', views.CommentCreateAPIView.as_view()),
    path('<int:comment_id>/edit/', views.CommentUpdateAPIView.as_view()),
    path('<int:comment_id>/delete/', views.CommentDeleteAPIView.as_view()),
    path('<int:comment_id>/like/', views.LikeCommentAPIView.as_view())
]
