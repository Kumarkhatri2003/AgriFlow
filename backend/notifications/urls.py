from django.urls import path
from .views import (
    NotificationListView, 
    NotificationDetailView, 
    MarkAllReadView,
    UnreadCountView
)

urlpatterns = [
    # Main endpoints
    path('', NotificationListView.as_view(), name='notifications'),
    path('unread-count/', UnreadCountView.as_view(), name='unread-count'),
    path('mark-all-read/', MarkAllReadView.as_view(), name='mark-all-read'),
    
    # Individual notification
    path('<int:notification_id>/', NotificationDetailView.as_view(), name='notification-detail'),
]