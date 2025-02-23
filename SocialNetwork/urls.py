from django.conf.urls.static import static
from django.contrib import admin
from django.contrib.gis import feeds
from django.urls import path, include

from SocialNetwork import settings

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/v1/users/', include('users.urls')),
    path('api/v1/posts/', include('posts.urls')),
    path('api/v1/feed/', include('feed.urls')),
    path('api/v1/comments/', include('comments.urls')),
    path('api/v1/relationships/', include('relationships.urls')),
    path('api/v1/notifications/', include('notifications.urls')),
    path('api/v1/chats/', include("chats.urls")),
    path('api/v1/search/', include("search.urls"))
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
