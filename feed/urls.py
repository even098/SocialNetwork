from django.urls import path

from feed import views

urlpatterns = [
    path('recommendations/', views.RecommendPostsView.as_view(), name='recommend_posts_for_user')
]
