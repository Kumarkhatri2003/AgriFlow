# backend/notifications/services.py

from django.contrib.auth import get_user_model
from .models import Notification
from django.utils import timezone

User = get_user_model()


def send_bulk_notification(
    farmers,
    title,
    message,
    notification_type='admin',
    priority='medium',
    title_np=None,
    message_np=None,
):
    """
    Send notifications to multiple farmers
    """
    if not farmers or farmers.count() == 0:
        return 0
    
    created_count = 0
    notifications_to_create = []
    
    for farmer in farmers:
        notifications_to_create.append(
            Notification(
                farmer=farmer,
                title=title,
                message=message,
                title_np=title_np or '',
                message_np=message_np or '',
                notification_type=notification_type,
                priority=priority,
                is_read=False,
                is_completed=False
            )
        )
        
        if len(notifications_to_create) >= 100:
            Notification.objects.bulk_create(notifications_to_create)
            created_count += len(notifications_to_create)
            notifications_to_create = []
    
    if notifications_to_create:
        Notification.objects.bulk_create(notifications_to_create)
        created_count += len(notifications_to_create)
    
    return created_count