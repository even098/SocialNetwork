from django.urls import path, include

from users import views
from users.views import GoogleLoginApi, GoogleLoginRedirectApi

urlpatterns = [
    path('profile/<int:pk>/', views.UserProfileAPIView.as_view(), name='user-profile'),
    path('profile/edit/', views.UserUpdateAPIView.as_view(), name='user-edit'),
    path('google-oauth2/callback/', GoogleLoginApi.as_view(), name='callback-sdk'),
    path('google-oauth2/login/', GoogleLoginRedirectApi.as_view(), name='login-sdk'),
    path('auth/', include('djoser.urls')),
    path('auth/', include('djoser.urls.jwt')),
]
