"""
Notification utilities - Functions to send and manage notifications
"""

from .models import Notification


def send_notification(
    farmer,
    title,
    message,
    notification_type='livestock',
    priority='medium',
    source_id=None,
    source_type=None,
    action_url=None,
    action_label=None,
    title_np=None,
    message_np=None,
    action_label_np=None,
):
    """
    Create a notification for a farmer.
    
    Parameters:
    - farmer: User object (the recipient)
    - title: Short title of the notification
    - message: Detailed message
    - notification_type: 'livestock', 'crop', 'weather', 'admin'
    - priority: 'critical', 'urgent', 'high', 'medium', 'low'
    - source_id: ID of related object (crop.id or animal.id)
    - source_type: Type of source ('crop', 'livestock')
    - action_url: URL to navigate when clicked
    - action_label: Text for action button
    
    Returns:
    - Notification object
    """
    return Notification.objects.create(
        farmer=farmer,
        title=title,
        message=message,
        title_np=title_np or '',
        message_np=message_np or '',
        notification_type=notification_type,
        priority=priority,
        source_id=source_id,
        source_type=source_type,
        action_url=action_url,
        action_label=action_label,
        action_label_np=action_label_np,
    )


def send_bulk_notification(farmers, title, message, notification_type='admin', priority='medium'):
    """
    Send same notification to multiple farmers.
    
    Parameters:
    - farmers: List/QuerySet of User objects
    - title, message: Notification content
    - notification_type, priority: Type and priority
    """
    notifications = []
    for farmer in farmers:
        notifications.append(
            Notification(
                farmer=farmer,
                title=title,
                message=message,
                notification_type=notification_type,
                priority=priority,
            )
        )
    Notification.objects.bulk_create(notifications)
    return len(notifications)


def get_unread_count(farmer):
    """Get number of unread notifications for a farmer"""
    return Notification.objects.filter(farmer=farmer, is_read=False).count()


def get_all_notifications(farmer, limit=50):
    """Get all notifications for a farmer (most recent first)"""
    return Notification.objects.filter(farmer=farmer)[:limit]


def get_recent_notifications(farmer, limit=20):
    """Get recent notifications for a farmer"""
    return Notification.objects.filter(farmer=farmer)[:limit]


def get_notifications_by_type(farmer, notification_type, limit=20):
    """Get notifications filtered by type"""
    return Notification.objects.filter(
        farmer=farmer, 
        notification_type=notification_type
    )[:limit]


def get_high_priority_notifications(farmer):
    """Get unread high priority notifications"""
    return Notification.objects.filter(
        farmer=farmer, 
        is_read=False,
        priority__in=['critical', 'urgent', 'high']
    )


def mark_all_as_read(farmer):
    """Mark all notifications as read for a farmer"""
    from django.utils import timezone
    count = Notification.objects.filter(farmer=farmer, is_read=False).update(
        is_read=True, 
        read_at=timezone.now()
    )
    return count


def delete_old_notifications(days=30):
    """Delete notifications older than specified days"""
    from django.utils import timezone
    from datetime import timedelta
    cutoff_date = timezone.now() - timedelta(days=days)
    count, _ = Notification.objects.filter(created_at__lt=cutoff_date, is_read=True).delete()
    return count


def generate_user_alerts_and_reminders_if_needed(user):
    """
    Checks if reminders and alerts have been generated for the user today.
    If not, generates them for both crops and livestock.
    """
    if not user or not user.is_authenticated or not hasattr(user, 'is_farmer') or not user.is_farmer:
        return
        
    from datetime import date
    
    if user.last_reminder_generation != date.today():
        # Prevent double-triggering by updating the timestamp immediately
        user.last_reminder_generation = date.today()
        user.save(update_fields=['last_reminder_generation'])
        
        # 1. Generate crop reminders
        try:
            from crops.services.reminder_service import CropReminderService
            CropReminderService.generate_reminders_for_user(user)
        except Exception as e:
            print(f"Error generating crop reminders for user {user.username}: {e}")
            
        # 2. Generate livestock alerts
        try:
            from livestock.alert_generator import LivestockAlertGenerator
            LivestockAlertGenerator.generate_all_alerts(farmer=user)
        except Exception as e:
            print(f"Error generating livestock alerts for user {user.username}: {e}")