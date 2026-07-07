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
    Send same notification to multiple farmers.
    """
    notifications = []
    for farmer in farmers:
        notifications.append(
            Notification(
                farmer=farmer,
                title=title,
                message=message,
                title_np=title_np or '',
                message_np=message_np or '',
                notification_type=notification_type,
                priority=priority,
            )
        )
    Notification.objects.bulk_create(notifications)
    return len(notifications)

def get_unread_count(farmer, include_farm_alerts=False):
    """
    Get number of unread notifications for a farmer.
    
    Args:
        farmer: User object
        include_farm_alerts: If True, include crop/livestock alerts in count.
                           Default False (only shows admin and weather).
    """
    queryset = Notification.objects.filter(farmer=farmer, is_read=False)
    
    # ✅ Exclude crop and livestock alerts by default
    if not include_farm_alerts:
        queryset = queryset.exclude(notification_type__in=['crop', 'livestock'])
    
    return queryset.count()


def get_farm_alerts_unread_count(farmer):
    """
    Get unread count specifically for farm alerts (crop + livestock).
    Used for the dashboard alert badges.
    """
    return Notification.objects.filter(
        farmer=farmer,
        is_read=False,
        notification_type__in=['crop', 'livestock']
    ).count()


def get_all_notifications(farmer, limit=50, include_farm_alerts=False):
    """
    Get all notifications for a farmer (most recent first).
    
    Args:
        farmer: User object
        limit: Max number of notifications
        include_farm_alerts: If True, include crop/livestock alerts.
    """
    queryset = Notification.objects.filter(farmer=farmer)
    
    if not include_farm_alerts:
        queryset = queryset.exclude(notification_type__in=['crop', 'livestock'])
    
    return queryset[:limit]


def get_recent_notifications(farmer, limit=20, include_farm_alerts=False):
    """Get recent notifications for a farmer"""
    return get_all_notifications(farmer, limit, include_farm_alerts)


def get_notifications_by_type(farmer, notification_type, limit=20):
    """Get notifications filtered by type"""
    return Notification.objects.filter(
        farmer=farmer, 
        notification_type=notification_type
    )[:limit]


def get_high_priority_notifications(farmer, include_farm_alerts=False):
    """Get unread high priority notifications"""
    queryset = Notification.objects.filter(
        farmer=farmer, 
        is_read=False,
        priority__in=['critical', 'urgent', 'high']
    )
    
    if not include_farm_alerts:
        queryset = queryset.exclude(notification_type__in=['crop', 'livestock'])
    
    return queryset


def mark_all_as_read(farmer, include_farm_alerts=False):
    """
    Mark all notifications as read for a farmer.
    
    Args:
        farmer: User object
        include_farm_alerts: If True, also mark crop/livestock alerts as read.
    """
    from django.utils import timezone
    
    queryset = Notification.objects.filter(farmer=farmer, is_read=False)
    
    if not include_farm_alerts:
        queryset = queryset.exclude(notification_type__in=['crop', 'livestock'])
    
    count = queryset.update(is_read=True, read_at=timezone.now())
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
    Mark incomplete notifications as completed AND delete completed ones 
    when source data changes or the related record is removed.
    This prevents duplicates when dates are changed.
    """
    from django.utils import timezone
    
    archived_count = 0
    deleted_count = 0
    
    # Step 1: Archive incomplete notifications (mark as completed)
    qs = Notification.objects.filter(farmer=farmer, is_completed=False)
    if source_id is not None:
        qs = qs.filter(source_id=str(source_id))
    if source_type is not None:
        qs = qs.filter(source_type=source_type)
    if title_icontains:
        qs = qs.filter(title__icontains=title_icontains)
    
    archived_count = qs.update(is_completed=True, completed_at=timezone.now())
    
    # Step 2: Delete completed notifications that match the criteria
    delete_qs = Notification.objects.filter(farmer=farmer, is_completed=True)
    if source_id is not None:
        delete_qs = delete_qs.filter(source_id=str(source_id))
    if source_type is not None:
        delete_qs = delete_qs.filter(source_type=source_type)
    if title_icontains:
        delete_qs = delete_qs.filter(title__icontains=title_icontains)
    
    deleted_count, _ = delete_qs.delete()
    
    if archived_count:
        print(f"    🗑️ Archived {archived_count} pending notifications")
    if deleted_count:
        print(f"    🗑️ Deleted {deleted_count} completed notifications")
    
    return archived_count + deleted_count


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