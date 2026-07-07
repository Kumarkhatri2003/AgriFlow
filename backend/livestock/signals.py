# livestock/signals.py

from django.db.models.signals import post_save, pre_save, post_delete
from django.dispatch import receiver
from .models import Animal, VaccinationRecord, HealthRecord, BreedingRecord, MilkRecord
from .alert_generator import LivestockAlertGenerator
from notifications.utils import archive_pending_notifications


# ==================== PRE-SAVE HANDLERS (Capture old values) ====================

def _snapshot_vaccination(instance):
    """Capture pre-save field values for change detection."""
    if not instance.pk:
        instance._pre_save_vax = None
        return
    try:
        old = VaccinationRecord.objects.get(pk=instance.pk)
        instance._pre_save_vax = {
            'next_due_date': old.next_due_date,
            'vaccine_name': old.vaccine_name,
            'animal_id': old.animal_id,
        }
    except VaccinationRecord.DoesNotExist:
        instance._pre_save_vax = None


def _snapshot_health(instance):
    """Capture pre-save field values for change detection."""
    if not instance.pk:
        instance._pre_save_health = None
        return
    try:
        old = HealthRecord.objects.get(pk=instance.pk)
        instance._pre_save_health = {
            'follow_up_date': old.follow_up_date,
            'diagnosis': old.diagnosis,
            'animal_id': old.animal_id,
        }
    except HealthRecord.DoesNotExist:
        instance._pre_save_health = None


def _snapshot_animal(instance):
    """Capture pre-save field values for change detection."""
    if not instance.pk:
        instance._pre_save_animal = None
        return
    try:
        old = Animal.objects.get(pk=instance.pk)
        instance._pre_save_animal = {
            'status': old.status,
            'is_pregnant': old.is_pregnant,
            'expected_birth_date': old.expected_birth_date,
        }
    except Animal.DoesNotExist:
        instance._pre_save_animal = None


def _snapshot_breeding(instance):
    """Capture pre-save field values for change detection."""
    if not instance.pk:
        instance._pre_save_breeding = None
        return
    try:
        old = BreedingRecord.objects.get(pk=instance.pk)
        instance._pre_save_breeding = {
            'breeding_date': old.breeding_date,
            'expected_birth_date': old.expected_birth_date,
            'animal_id': old.animal_id,
        }
    except BreedingRecord.DoesNotExist:
        instance._pre_save_breeding = None


@receiver(pre_save, sender=VaccinationRecord)
def vaccination_pre_save_handler(sender, instance, **kwargs):
    _snapshot_vaccination(instance)


@receiver(pre_save, sender=HealthRecord)
def health_pre_save_handler(sender, instance, **kwargs):
    _snapshot_health(instance)


@receiver(pre_save, sender=Animal)
def animal_pre_save_handler(sender, instance, **kwargs):
    _snapshot_animal(instance)


@receiver(pre_save, sender=BreedingRecord)
def breeding_pre_save_handler(sender, instance, **kwargs):
    _snapshot_breeding(instance)


# ==================== POST-SAVE HANDLERS ====================

@receiver(post_save, sender=Animal)
def animal_created_or_updated(sender, instance, created, **kwargs):
    """Auto-generate alerts when animal is created or updated"""
    if created:
        print(f"🐄 New animal: {instance.name}")
    else:
        print(f"🔄 Animal updated: {instance.name}")
        
        # Check if status changed to active or pregnancy related fields changed
        old = getattr(instance, '_pre_save_animal', None)
        if old:
            # If animal status changed to active
            if old.get('status') != instance.status and instance.status == 'active':
                print(f"   ✅ Animal activated - generating alerts")
            
            # If pregnancy status or expected birth date changed
            if (old.get('is_pregnant') != instance.is_pregnant or 
                old.get('expected_birth_date') != instance.expected_birth_date):
                print(f"   🔄 Pregnancy status/birth date changed")
                # Archive old pregnancy notifications
                if old.get('expected_birth_date'):
                    archive_pending_notifications(
                        farmer=instance.farmer,
                        source_id=str(instance.id),
                        source_type='livestock',
                        title_icontains='Birth Alert'
                    )
    
    # ✅ Force generation to bypass daily duplicate check
    LivestockAlertGenerator.generate_all_alerts(farmer=instance.farmer, force=True)


@receiver(post_save, sender=VaccinationRecord)
def vaccination_record_created_or_updated(sender, instance, created, **kwargs):
    """Auto-generate alerts when vaccination is added OR updated"""
    print(f"💉 Vaccination {'added' if created else 'updated'} for: {instance.animal.name}")
    print(f"   Vaccine: {instance.vaccine_name}, Next due: {instance.next_due_date}")
    
    # Check if this is an update (not created)
    if not created:
        old = getattr(instance, '_pre_save_vax', None)
        if old:
            # Check if next_due_date changed
            if old.get('next_due_date') != instance.next_due_date:
                print(f"   🔄 Date changed from {old.get('next_due_date')} to {instance.next_due_date}")
                
                # Archive old notifications for this vaccine
                archive_pending_notifications(
                    farmer=instance.animal.farmer,
                    source_id=str(instance.animal.id),
                    source_type='livestock',
                    title_icontains=instance.vaccine_name
                )
            
            # Check if vaccine name changed
            if old.get('vaccine_name') != instance.vaccine_name:
                print(f"   🔄 Vaccine name changed from {old.get('vaccine_name')} to {instance.vaccine_name}")
                
                # Archive old notifications with old name
                archive_pending_notifications(
                    farmer=instance.animal.farmer,
                    source_id=str(instance.animal.id),
                    source_type='livestock',
                    title_icontains=old.get('vaccine_name')
                )
    
    # ✅ Force generation to bypass daily duplicate check
    LivestockAlertGenerator.generate_all_alerts(farmer=instance.animal.farmer, force=True)


@receiver(post_save, sender=HealthRecord)
def health_record_created_or_updated(sender, instance, created, **kwargs):
    """Auto-generate alerts when health record is added OR updated"""
    print(f"🏥 Health record {'added' if created else 'updated'} for: {instance.animal.name}")
    print(f"   Diagnosis: {instance.diagnosis}, Follow-up: {instance.follow_up_date}")
    
    # Check if this is an update (not created)
    if not created:
        old = getattr(instance, '_pre_save_health', None)
        if old:
            # Check if follow_up_date changed
            if old.get('follow_up_date') != instance.follow_up_date:
                print(f"   🔄 Follow-up date changed from {old.get('follow_up_date')} to {instance.follow_up_date}")
                
                # Archive old notifications for this health record
                archive_pending_notifications(
                    farmer=instance.animal.farmer,
                    source_id=str(instance.animal.id),
                    source_type='livestock',
                    title_icontains=instance.diagnosis
                )
            
            # Check if diagnosis changed
            if old.get('diagnosis') != instance.diagnosis:
                print(f"   🔄 Diagnosis changed from {old.get('diagnosis')} to {instance.diagnosis}")
                
                # Archive old notifications with old diagnosis
                archive_pending_notifications(
                    farmer=instance.animal.farmer,
                    source_id=str(instance.animal.id),
                    source_type='livestock',
                    title_icontains=old.get('diagnosis')
                )
    
    # ✅ Force generation to bypass daily duplicate check
    LivestockAlertGenerator.generate_all_alerts(farmer=instance.animal.farmer, force=True)


@receiver(post_save, sender=BreedingRecord)
def breeding_record_created_or_updated(sender, instance, created, **kwargs):
    """Auto-generate alerts when breeding record is added OR updated"""
    print(f"❤️ Breeding record {'added' if created else 'updated'} for: {instance.animal.name}")
    
    # Check if this is an update (not created)
    if not created:
        old = getattr(instance, '_pre_save_breeding', None)
        if old:
            # Check if expected_birth_date changed
            if old.get('expected_birth_date') != instance.expected_birth_date:
                print(f"   🔄 Expected birth date changed from {old.get('expected_birth_date')} to {instance.expected_birth_date}")
                
                # Archive old pregnancy notifications
                archive_pending_notifications(
                    farmer=instance.animal.farmer,
                    source_id=str(instance.animal.id),
                    source_type='livestock',
                    title_icontains='Birth Alert'
                )
    
    # ✅ Force generation to bypass daily duplicate check
    LivestockAlertGenerator.generate_all_alerts(farmer=instance.animal.farmer, force=True)


@receiver(post_save, sender=MilkRecord)
def milk_record_created_or_updated(sender, instance, created, **kwargs):
    """Auto-generate alerts when milk record is added OR updated"""
    print(f"🥛 Milk record {'added' if created else 'updated'} for: {instance.animal.name}")
    
    # Milk records don't typically trigger alerts, but we keep for consistency
    # ✅ Force generation to bypass daily duplicate check
    LivestockAlertGenerator.generate_all_alerts(farmer=instance.animal.farmer, force=True)


# ==================== POST-DELETE HANDLERS ====================

@receiver(post_delete, sender=VaccinationRecord)
def vaccination_record_deleted(sender, instance, **kwargs):
    """Archive notifications when vaccination record is deleted"""
    if instance.animal:
        print(f"🗑️ Vaccination record deleted for: {instance.animal.name}")
        archive_pending_notifications(
            farmer=instance.animal.farmer,
            source_id=str(instance.animal.id),
            source_type='livestock',
            title_icontains=instance.vaccine_name
        )


@receiver(post_delete, sender=HealthRecord)
def health_record_deleted(sender, instance, **kwargs):
    """Archive notifications when health record is deleted"""
    if instance.animal:
        print(f"🗑️ Health record deleted for: {instance.animal.name}")
        archive_pending_notifications(
            farmer=instance.animal.farmer,
            source_id=str(instance.animal.id),
            source_type='livestock',
            title_icontains=instance.diagnosis
        )


@receiver(post_delete, sender=Animal)
def animal_deleted(sender, instance, **kwargs):
    """Archive notifications when animal is deleted"""
    if instance.farmer:
        print(f"🗑️ Animal deleted: {instance.name}")
        archive_pending_notifications(
            farmer=instance.farmer,
            source_id=str(instance.id),
            source_type='livestock'
        )