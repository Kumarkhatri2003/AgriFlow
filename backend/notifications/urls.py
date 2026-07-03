# notifications/urls.py

from django.urls import path
from .views import (
    NotificationListView,
    NotificationDetailView,
    MarkAllReadView,
    UnreadCountView,
    GetFarmAlertsView,
    MarkNotificationCompletedView,
    MarkNotificationUncompletedView,
)

urlpatterns = [
    # Main endpoints
    path('', NotificationListView.as_view(), name='notifications'),
    path('unread-count/', UnreadCountView.as_view(), name='unread-count'),
    path('mark-all-read/', MarkAllReadView.as_view(), name='mark-all-read'),
    
    # Individual notification
    path('<int:notification_id>/', NotificationDetailView.as_view(), name='notification-detail'),
    
    # Farm alerts endpoint
    path('farm-alerts/', GetFarmAlertsView.as_view(), name='farm-alerts'),
    
    # Complete/Uncomplete endpoints
    path('<int:notification_id>/complete/', MarkNotificationCompletedView.as_view(), name='notification-complete'),
    path('<int:notification_id>/uncomplete/', MarkNotificationUncompletedView.as_view(), name='notification-uncomplete'),
]