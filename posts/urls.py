from django.urls import path, include

from posts import views

urlpatterns = [
    path('<int:post_id>/comments/', views.PostCommentListAPIView.as_view(), name='post_comment_list'),
    path('create/', views.PostCreateAPIView.as_view(), name='post_create'),
    path('edit/<int:post_id>/', views.PostEditAPIView.as_view(), name='post_edit'),
    path('delete/<int:post_id>/', views.PostDeleteAPIView.as_view(), name='post_delete'),
    path('like/<int:post_id>/', views.LikePostAPIView.as_view(), name='post_like'),
]
