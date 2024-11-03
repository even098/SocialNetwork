from django.urls import path, include

from posts import views

urlpatterns = [
    path('create/', views.PostCreateAPIView.as_view(), name='post_create'),
    path('edit/<int:post_id>/', views.PostEditAPIView.as_view(), name='post_edit'),
    path('delete/<int:post_id>/', views.PostDeleteAPIView.as_view(), name='post_delete'),
    path('<int:post_id>/like/', views.LikePostAPIView.as_view(), name='post_like'),
]
