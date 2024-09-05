from django.urls import path, include

from posts import views

urlpatterns = [
    path('posts/<int:post_id>/', views.test_view)
]
