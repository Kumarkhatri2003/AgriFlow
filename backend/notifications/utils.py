# notifications/utils.py

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
    due_date=None,
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
        due_date=due_date,
    )


def send_bulk_notification(farmers, title, message, notification_type='admin', priority='medium'):
    """
    Send same notification to multiple farmers.
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


def archive_pending_notifications(farmer, source_id=None, source_type=None, title_icontains=None):
    """
    Mark incomplete notifications as completed when source data changes
    or the related record is removed.
    """
    from django.utils import timezone

    qs = Notification.objects.filter(farmer=farmer, is_completed=False)
    if source_id is not None:
        qs = qs.filter(source_id=str(source_id))
    if source_type is not None:
        qs = qs.filter(source_type=source_type)
    if title_icontains:
        qs = qs.filter(title__icontains=title_icontains)
    return qs.update(is_completed=True, completed_at=timezone.now())


def refresh_notification_priorities(farmer=None):
    """
    Re-score incomplete notifications from due_date vs today.
    Called on every notification API fetch so criticality stays current.
    """
    from datetime import date
    from .action_priority import crop_priority_from_days_until, priority_from_days_until

    qs = Notification.objects.filter(is_completed=False, due_date__isnull=False)
    if farmer is not None:
        qs = qs.filter(farmer=farmer)

    today = date.today()
    updated = 0
    for notif in qs.iterator():
        days_until = (notif.due_date - today).days
        if notif.notification_type == 'crop':
            new_priority = crop_priority_from_days_until(days_until)
        else:
            new_priority = priority_from_days_until(days_until)
        if notif.priority != new_priority:
            Notification.objects.filter(pk=notif.pk).update(priority=new_priority)
            updated += 1
    return updated


def trigger_immediate_alerts_for_user(user):
    """
    Generate crop + livestock alerts immediately (CRUD-triggered).
    Does not touch last_reminder_generation so the daily batch still runs.
    """
    if not user or not user.is_authenticated:
        return
    if not getattr(user, 'is_farmer', False):
        return

    try:
        from crops.services.reminder_service import CropReminderService
        CropReminderService.generate_reminders_for_user(user)
    except Exception as e:
        print(f"Error generating crop reminders for {user.username}: {e}")

    try:
        from livestock.alert_generator import LivestockAlertGenerator
        LivestockAlertGenerator.generate_all_alerts(farmer=user)
    except Exception as e:
        print(f"Error generating livestock alerts for {user.username}: {e}")

    refresh_notification_priorities(farmer=user)


def generate_user_alerts_and_reminders_if_needed(user):
    """
    Checks if reminders and alerts have been generated for the user today.
    If not, generates them for both crops and livestock.
    
    Uses the last_reminder_generation field from the User model to track
    when reminders were last generated.
    """
    if not user or not user.is_authenticated:
        return
        
    # Only generate for farmers
    if not hasattr(user, 'is_farmer') or not user.is_farmer:
        return
        
    from datetime import date
    
    # Check if already generated today
    if user.last_reminder_generation == date.today():
        # Already generated today, skip
        return
    
    # Update timestamp
    user.last_reminder_generation = date.today()
    user.save(update_fields=['last_reminder_generation'])
    
    # 1. Generate crop reminders
    try:
        from crops.services.reminder_service import CropReminderService
        reminders = CropReminderService.generate_reminders_for_user(user)
        if reminders:
            try:
                print(f"[SUCCESS] Generated {len(reminders)} crop reminders for {user.username}")
            except UnicodeEncodeError:
                pass
    except Exception as e:
        try:
            print(f"[ERROR] Error generating crop reminders for {user.username}: {e}")
        except UnicodeEncodeError:
            pass
        
    # 2. Generate livestock alerts
    try:
        from livestock.alert_generator import LivestockAlertGenerator
        count = LivestockAlertGenerator.generate_all_alerts(farmer=user)
        if count:
            try:
                print(f"[SUCCESS] Generated {count} livestock alerts for {user.username}")
            except UnicodeEncodeError:
                pass
    except Exception as e:
        try:
            print(f"[ERROR] Error generating livestock alerts for {user.username}: {e}")
        except UnicodeEncodeError:
            pass

    refresh_notification_priorities(farmer=user)