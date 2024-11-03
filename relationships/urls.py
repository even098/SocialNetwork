from django.urls import path
from . import views

urlpatterns = [
    path('follow/<int:user_id>/', views.FollowUserAPIView.as_view(), name='follow_user'),
    path('unfollow/<int:user_id>/', views.UnfollowUserAPIView.as_view(), name='unfollow_user'),
    path('followers/<int:user_id>/', views.FollowersListAPIView.as_view(), name='followers_list'),
    path('following/<int:user_id>/', views.FollowingListAPIView.as_view(), name='following_list'),
]
