from django.contrib import admin
from django.contrib.gis import feeds
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/v1/users/', include('users.urls')),
    path('api/v1/posts/', include('posts.urls')),
    path('api/v1/feed/', include('feed.urls')),
    path('api/v1/comments/', include('comments.urls')),
    path('api/v1/relationships/', include('relationships.urls')),
    path('api/v1/notifications/', include('notifications.urls')),
    path('api/v1/chats/', include("chats.urls")),
]
