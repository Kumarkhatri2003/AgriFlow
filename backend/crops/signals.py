# crops/signals.py

from django.db.models.signals import post_save, post_delete, pre_save
from django.dispatch import receiver
from .models import Crop, CropActivityRule, CropTypeConfig
from notifications import utils as notification_utils


def _snapshot_crop(instance):
    """Capture pre-save field values for change detection in post_save."""
    if not instance.pk:
        instance._pre_save_crop = None
        return
    try:
        old = Crop.objects.get(pk=instance.pk)
        instance._pre_save_crop = {
            'planting_date': old.planting_date,
            'expected_harvest_date': old.expected_harvest_date,
            'growth_stage': old.growth_stage,
            'status': old.status,
            'variety': old.variety,
            'name': old.name,
        }
    except Crop.DoesNotExist:
        instance._pre_save_crop = None


@receiver(pre_save, sender=Crop)
def crop_pre_save_handler(sender, instance, **kwargs):
    _snapshot_crop(instance)


@receiver(post_save, sender=Crop)
def crop_created_or_updated(sender, instance, created, **kwargs):
    """
    Auto-generate reminders when crop is created or when alert-relevant fields change.
    """
    from crops.services.reminder_service import CropReminderService

    if created:
        CropReminderService.generate_reminders_for_crop(instance)
        notification_utils.refresh_notification_priorities(farmer=instance.farmer)
        return

    old = getattr(instance, '_pre_save_crop', None)
    if not old:
        return

    timeline_changed = old['planting_date'] != instance.planting_date
    needs_regen = (
        timeline_changed
        or old['expected_harvest_date'] != instance.expected_harvest_date
        or old['growth_stage'] != instance.growth_stage
        or (old['status'] != instance.status and instance.status == 'active')
        or old['variety'] != instance.variety
        or old['name'] != instance.name
    )

    if timeline_changed:
        notification_utils.archive_pending_notifications(
            farmer=instance.farmer,
            source_id=str(instance.id),
            source_type='crop',
        )

    if needs_regen:
        CropReminderService.generate_reminders_for_crop(instance)
        notification_utils.refresh_notification_priorities(farmer=instance.farmer)


@receiver(pre_save, sender=Crop)
def crop_status_change_handler(sender, instance, **kwargs):
    """Send notification and archive pending alerts when crop status changes."""
    if not instance.id:
        return

    try:
        old_instance = Crop.objects.get(id=instance.id)
    except Crop.DoesNotExist:
        return

    if old_instance.status == instance.status:
        return

    from crops.services.reminder_service import CropReminderService

    status_messages = {
        'active': {
            'title': f'🌱 Crop Activated: {instance.name}',
            'message': (
                f'Your crop "{instance.name}" has been marked as ACTIVE.\n\n'
                'You will now receive activity reminders.'
            ),
            'priority': 'medium',
        },
        'harvested': {
            'title': f'✂️ Crop Harvested: {instance.name}',
            'message': (
                f'🎉 Congratulations! Your crop "{instance.name}" has been marked as HARVESTED.\n\n'
                f'📊 Quick Stats:\n• Total Income: NPR {instance.total_income or 0}\n'
                f'• Total Expenses: NPR {instance.total_expense or 0}\n'
                f'• Net Profit: NPR {instance.net_profit or 0}'
            ),
            'priority': 'high',
        },
        'done': {
            'title': f'✅ Crop Completed: {instance.name}',
            'message': (
                f'Your crop "{instance.name}" has been marked as COMPLETED.\n\n'
                'Thank you for using AgriFlow.'
            ),
            'priority': 'low',
        },
    }

    msg = status_messages.get(instance.status)
    if msg:
        notification_utils.send_notification(
            farmer=instance.farmer,
            title=msg['title'],
            message=msg['message'],
            notification_type='crop',
            priority=msg['priority'],
            source_id=str(instance.id),
            source_type='crop',
            action_url=f"/crops/{instance.id}",
            action_label="View Crop",
        )

    if instance.status == 'harvested':
        CropReminderService.generate_reminders_for_crop(instance)

    if instance.status == 'done':
        notification_utils.archive_pending_notifications(
            farmer=instance.farmer,
            source_id=str(instance.id),
            source_type='crop',
        )


@receiver(post_delete, sender=Crop)
def crop_deleted_handler(sender, instance, **kwargs):
    """Archive pending notifications when a crop is deleted."""
    notification_utils.archive_pending_notifications(
        farmer=instance.farmer,
        source_id=str(instance.id),
        source_type='crop',
    )


@receiver(post_save, sender=CropActivityRule)
def activity_rule_updated(sender, instance, created, **kwargs):
    """Regenerate reminders when activity rules are created or updated."""
    from crops.models import Crop
    from crops.services.reminder_service import CropReminderService

    crops = Crop.objects.filter(
        name=instance.crop_config.crop_name,
        status='active',
    )
    for crop in crops:
        CropReminderService.generate_reminders_for_crop(crop)
        notification_utils.refresh_notification_priorities(farmer=crop.farmer)


@receiver(post_save, sender=CropTypeConfig)
def crop_config_updated(sender, instance, created, **kwargs):
    """Regenerate reminders when crop type configs change."""
    from crops.models import Crop
    from crops.services.reminder_service import CropReminderService

    crops = Crop.objects.filter(name=instance.crop_name, status='active')
    for crop in crops:
        crop.update_growth_stage(save=True)
        CropReminderService.generate_reminders_for_crop(crop)
        notification_utils.refresh_notification_priorities(farmer=crop.farmer)
