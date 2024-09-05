from django.urls import path, include

from users import views
from users.views import GoogleLoginApi, GoogleLoginRedirectApi

urlpatterns = [
    path('users/<int:pk>/', views.UserProfileAPIView.as_view()),
    path('users/<int:pk>/', views.UserUpdateAPIView.as_view()),
    path('auth/', include('djoser.urls')),
    path('auth/', include('djoser.urls.jwt')),
    path('users/google-oauth2/callback/', GoogleLoginApi.as_view(), name='callback-sdk'),
    path('users/google-oauth2/login/', GoogleLoginRedirectApi.as_view()),
]
