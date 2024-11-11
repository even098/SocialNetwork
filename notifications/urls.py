from django.urls import path
from notifications import views

urlpatterns = [
    path('', views.NotificationListAPIView.as_view(), name='notification-list'),
    path('read/<int:notification_id>/', views.MarkNotificationReadAPIView.as_view(), name='notification-read'),
    path('read/all/', views.MarkAllNotificationsReadAPIView.as_view(), name='notification-read-all')
]
