from django.urls import path, include

from posts import views

urlpatterns = [
    path('/<int:post_id>/', views.test_view),
    path('create/', views.PostCreateAPIView.as_view(), name='post-create'),
    path('edit/<int:post_id>/', views.PostEditAPIView.as_view(), name='post-edit'),
    path('<int:post_id>/like/', views.LikePostAPIView.as_view(), name='post-like'),
]
