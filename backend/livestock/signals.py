# livestock/signals.py

from django.db.models.signals import post_save, post_delete, pre_save
from django.dispatch import receiver
from notifications import utils as notification_utils
from .models import Animal, VaccinationRecord, HealthRecord, BreedingRecord


def _snapshot(instance, fields):
    if not instance.pk:
        instance._pre_save_state = None
        return
    try:
        old = instance.__class__.objects.get(pk=instance.pk)
        instance._pre_save_state = {f: getattr(old, f) for f in fields}
    except instance.__class__.DoesNotExist:
        instance._pre_save_state = None


@receiver(pre_save, sender=Animal)
def animal_pre_save(sender, instance, **kwargs):
    _snapshot(instance, [
        'is_pregnant', 'expected_birth_date', 'last_pregnancy_date', 'status',
    ])


@receiver(post_save, sender=Animal)
def animal_saved(sender, instance, created, **kwargs):
    from livestock.alert_generator import LivestockAlertGenerator

    if created:
        if instance.is_pregnant and instance.expected_birth_date:
            LivestockAlertGenerator.generate_pregnancy_alert_for_animal(instance)
        notification_utils.refresh_notification_priorities(farmer=instance.farmer)
        return

    old = getattr(instance, '_pre_save_state', None)
    if not old:
        return

    date_changed = (
        old['expected_birth_date'] != instance.expected_birth_date
        or old['last_pregnancy_date'] != instance.last_pregnancy_date
    )
    pregnancy_changed = old['is_pregnant'] != instance.is_pregnant
    status_changed = old['status'] != instance.status

    if date_changed and old['expected_birth_date']:
        notification_utils.archive_pending_notifications(
            farmer=instance.farmer,
            source_id=str(instance.id),
            source_type='livestock',
            title_icontains='Birth Alert',
        )

    if status_changed and instance.status in ('sold', 'dead', 'butchered'):
        notification_utils.archive_pending_notifications(
            farmer=instance.farmer,
            source_id=str(instance.id),
            source_type='livestock',
        )

    if pregnancy_changed and not instance.is_pregnant:
        notification_utils.archive_pending_notifications(
            farmer=instance.farmer,
            source_id=str(instance.id),
            source_type='livestock',
            title_icontains='Birth Alert',
        )

    if date_changed or pregnancy_changed or (status_changed and instance.status == 'active'):
        LivestockAlertGenerator.generate_pregnancy_alert_for_animal(instance)
        notification_utils.refresh_notification_priorities(farmer=instance.farmer)


@receiver(pre_save, sender=VaccinationRecord)
def vaccination_pre_save(sender, instance, **kwargs):
    _snapshot(instance, ['next_due_date', 'vaccine_name', 'animal_id'])


@receiver(post_save, sender=VaccinationRecord)
def vaccination_saved(sender, instance, created, **kwargs):
    from livestock.alert_generator import LivestockAlertGenerator

    old = getattr(instance, '_pre_save_state', None)
    if not created and old and old['next_due_date'] != instance.next_due_date:
        notification_utils.archive_pending_notifications(
            farmer=instance.animal.farmer,
            source_id=str(instance.animal.id),
            source_type='livestock',
            title_icontains='Vaccination',
        )

    LivestockAlertGenerator.generate_vaccination_alert_for_record(instance)
    notification_utils.refresh_notification_priorities(farmer=instance.animal.farmer)


@receiver(post_delete, sender=VaccinationRecord)
def vaccination_deleted(sender, instance, **kwargs):
    notification_utils.archive_pending_notifications(
        farmer=instance.animal.farmer,
        source_id=str(instance.animal.id),
        source_type='livestock',
        title_icontains='Vaccination',
    )


@receiver(pre_save, sender=HealthRecord)
def health_pre_save(sender, instance, **kwargs):
    _snapshot(instance, ['follow_up_date', 'diagnosis', 'animal_id'])


@receiver(post_save, sender=HealthRecord)
def health_saved(sender, instance, created, **kwargs):
    from livestock.alert_generator import LivestockAlertGenerator

    old = getattr(instance, '_pre_save_state', None)
    if not created and old and old['follow_up_date'] != instance.follow_up_date:
        notification_utils.archive_pending_notifications(
            farmer=instance.animal.farmer,
            source_id=str(instance.animal.id),
            source_type='livestock',
            title_icontains='Health Follow-up',
        )

    LivestockAlertGenerator.generate_health_alert_for_record(instance)
    notification_utils.refresh_notification_priorities(farmer=instance.animal.farmer)


@receiver(post_delete, sender=HealthRecord)
def health_deleted(sender, instance, **kwargs):
    notification_utils.archive_pending_notifications(
        farmer=instance.animal.farmer,
        source_id=str(instance.animal.id),
        source_type='livestock',
        title_icontains='Health Follow-up',
    )


@receiver(post_save, sender=BreedingRecord)
def breeding_saved(sender, instance, created, **kwargs):
    """Sync successful breeding to animal pregnancy fields and trigger alerts."""
    if not instance.successful or not instance.expected_birth_date:
        return

    animal = instance.animal
    animal.is_pregnant = True
    animal.last_pregnancy_date = instance.breeding_date
    animal.expected_birth_date = instance.expected_birth_date
    animal.save(update_fields=[
        'is_pregnant', 'last_pregnancy_date', 'expected_birth_date', 'updated_at',
    ])
