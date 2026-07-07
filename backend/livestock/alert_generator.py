"""
Livestock Alert Generator - Based on due dates (NO DUPLICATES)
"""

from datetime import date, timedelta
from django.utils import timezone
from notifications.action_priority import priority_from_days_until, PRE_ALERT_DAYS
from notifications.utils import send_notification, archive_pending_notifications
from notifications.models import Notification
from notifications.i18n import ACTION_LABELS
from .models import Animal, VaccinationRecord, HealthRecord
import sys

def print(*args, **kwargs):
    try:
        sys.stdout.write(" ".join(map(str, args)) + kwargs.get("end", "\n"))
    except UnicodeEncodeError:
        clean_args = [str(arg).encode('ascii', errors='replace').decode('ascii') for arg in args]
        sys.stdout.write(" ".join(clean_args) + kwargs.get("end", "\n"))


class LivestockAlertGenerator:

    ALERT_WINDOWS = {
        'vaccination': (-PRE_ALERT_DAYS, PRE_ALERT_DAYS),
        'pregnancy': (-PRE_ALERT_DAYS, 14),
        'health_followup': (-PRE_ALERT_DAYS, PRE_ALERT_DAYS),
    }

    TITLE_KEYWORDS = {
        'vaccination': 'Vaccination',
        'pregnancy': 'Birth Alert',
        'health_followup': 'Health Follow-up',
    }
    
    @classmethod
    def get_priority(cls, days_until):
        """Determine priority based on days remaining until action date."""
        return priority_from_days_until(days_until)

    @classmethod
    def _in_alert_window(cls, alert_type, days_until):
        low, high = cls.ALERT_WINDOWS[alert_type]
        return low <= days_until <= high

    @classmethod
    def notification_already_sent(cls, farmer, animal_id, alert_type, due_date):
        """Check if an active notification already exists for this due date."""
        animal_id_str = str(animal_id)
        title_search = cls.TITLE_KEYWORDS.get(alert_type, '')

        query = Notification.objects.filter(
            farmer=farmer,
            source_id=animal_id_str,
            source_type='livestock',
            notification_type='livestock',
        )
        if title_search:
            query = query.filter(title__icontains=title_search)
        if due_date:
            query = query.filter(due_date=due_date)

        if query.filter(is_completed=True).exists():
            return True

        existing = query.filter(is_completed=False).exists()
        if existing:
            print(f"    ⏭️ SKIPPING - already notified for due date {due_date}")
        return existing

    @classmethod
    def _sent_today(cls, farmer, animal_id, alert_type):
        """Check if alert sent today for this animal and type."""
        title_search = cls.TITLE_KEYWORDS.get(alert_type, '')
        query = Notification.objects.filter(
            farmer=farmer,
            source_id=str(animal_id),
            source_type='livestock',
            notification_type='livestock',
            created_at__date=date.today(),
        )
        if title_search:
            query = query.filter(title__icontains=title_search)
        return query.exists()

    @classmethod
    def get_timing_message(cls, days_until, activity_name, animal_name):
        """Get formatted timing message (English)"""
        if days_until < 0:
            return f"⚠️ OVERDUE by {abs(days_until)} days: {activity_name} for {animal_name}"
        elif days_until == 0:
            return f"🔴 TODAY: {activity_name} for {animal_name}"
        elif days_until == 1:
            return f"🟠 TOMORROW: {activity_name} for {animal_name}"
        else:
            return f"🟡 In {days_until} days: {activity_name} for {animal_name}"

    @classmethod
    def get_timing_message_np(cls, days_until, activity_name, animal_name):
        """Get formatted timing message (Nepali)"""
        if days_until < 0:
            return f"⚠️ {abs(days_until)} दिन म्याद नाघ्यो: {animal_name} को लागि {activity_name}"
        elif days_until == 0:
            return f"🔴 आज: {animal_name} को लागि {activity_name}"
        elif days_until == 1:
            return f"🟠 भोलि: {animal_name} को लागि {activity_name}"
        else:
            return f"🟡 {days_until} दिनमा: {animal_name} को लागि {activity_name}"
    
    @classmethod
    def generate_vaccination_alert_for_record(cls, vax, force=False):
        """Generate alert for a single vaccination record (CRUD-triggered)."""
        if not vax.next_due_date or vax.animal.status != 'active':
            return 0
        
        today = date.today()
        days_until = (vax.next_due_date - today).days
        
        print(f"    🔍 Vaccination: {vax.vaccine_name}, days_until: {days_until}")
        
        if not cls._in_alert_window('vaccination', days_until):
            print(f"    ⏭️ SKIP: Outside alert window ({days_until})")
            return 0
        
        # ✅ Archive OLD notifications for this vaccine (regardless of due date)
        # This handles date changes - removes old notifications
        archived_count = archive_pending_notifications(
            farmer=vax.animal.farmer,
            source_id=str(vax.animal.id),
            source_type='livestock',
            title_icontains=vax.vaccine_name
        )
        if archived_count:
            print(f"    🗑️ Archived {archived_count} old vaccination notifications")
        
        # ✅ Check if notification already exists for THIS due date
        if cls.notification_already_sent(
            vax.animal.farmer, vax.animal.id, 'vaccination', vax.next_due_date
        ):
            return 0
        
        # ✅ Skip _sent_today check if force=True (for new records)
        if not force and cls._sent_today(vax.animal.farmer, vax.animal.id, 'vaccination'):
            print(f"    ⏭️ SKIP: Already sent today")
            return 0
        
        print(f"    ✅ Sending vaccination alert for: {vax.vaccine_name}")
        return cls._send_vaccination_alert(vax, days_until)

    @classmethod
    def generate_pregnancy_alert_for_animal(cls, animal, force=False):
        """Generate alert for a single pregnant animal (CRUD-triggered)."""
        if not animal.is_pregnant or not animal.expected_birth_date or animal.status != 'active':
            return 0
        
        today = date.today()
        days_until = (animal.expected_birth_date - today).days
        
        if not cls._in_alert_window('pregnancy', days_until):
            return 0
        
        # ✅ Archive OLD pregnancy notifications for this animal
        archived_count = archive_pending_notifications(
            farmer=animal.farmer,
            source_id=str(animal.id),
            source_type='livestock',
            title_icontains='Birth Alert'
        )
        if archived_count:
            print(f"    🗑️ Archived {archived_count} old pregnancy notifications")
        
        if cls.notification_already_sent(
            animal.farmer, animal.id, 'pregnancy', animal.expected_birth_date
        ):
            return 0
        
        # ✅ Skip _sent_today check if force=True
        if not force and cls._sent_today(animal.farmer, animal.id, 'pregnancy'):
            return 0
        
        return cls._send_pregnancy_alert(animal, days_until)

    @classmethod
    def generate_health_alert_for_record(cls, record, force=False):
        """Generate alert for a single health record (CRUD-triggered)."""
        if not record.follow_up_date or record.animal.status != 'active':
            return 0
        
        today = date.today()
        days_until = (record.follow_up_date - today).days
        
        if not cls._in_alert_window('health_followup', days_until):
            return 0
        
        # ✅ Archive OLD health notifications for this animal/diagnosis
        # Use a more specific filter to avoid archiving wrong notifications
        archived_count = archive_pending_notifications(
            farmer=record.animal.farmer,
            source_id=str(record.animal.id),
            source_type='livestock',
            title_icontains='Health Follow-up'
        )
        if archived_count:
            print(f"    🗑️ Archived {archived_count} old health notifications")
        
        if cls.notification_already_sent(
            record.animal.farmer, record.animal.id, 'health_followup', record.follow_up_date
        ):
            return 0
        
        # ✅ Skip _sent_today check if force=True
        if not force and cls._sent_today(record.animal.farmer, record.animal.id, 'health_followup'):
            return 0
        
        return cls._send_health_alert(record, days_until)

    @classmethod
    def _send_vaccination_alert(cls, vax, days_until):
        priority = cls.get_priority(days_until)
        activity_en = f"{vax.vaccine_name} vaccination"
        activity_np = f"{vax.vaccine_name} खोप"
        notification = send_notification(
            farmer=vax.animal.farmer,
            title=f"💉 {vax.vaccine_name} Vaccination - {vax.animal.name}",
            title_np=f"💉 {vax.vaccine_name} खोप - {vax.animal.name}",
            message=cls.get_timing_message(days_until, activity_en, vax.animal.name),
            message_np=cls.get_timing_message_np(days_until, activity_np, vax.animal.name),
            notification_type='livestock',
            priority=priority,
            source_id=str(vax.animal.id),
            source_type='livestock',
            action_url=f'/livestock/{vax.animal.id}/',
            action_label=ACTION_LABELS['en']['view_animal'],
            action_label_np=ACTION_LABELS['np']['view_animal'],
            due_date=vax.next_due_date,
        )
        print(f"    ✅ NEW notification sent (ID: {notification.id})")
        return 1

    @classmethod
    def _send_pregnancy_alert(cls, animal, days_until):
        priority = cls.get_priority(days_until)
        notification = send_notification(
            farmer=animal.farmer,
            title=f"🐄 Birth Alert - {animal.name}",
            title_np=f"🐄 प्रसव सतर्कता - {animal.name}",
            message=cls.get_timing_message(days_until, "expected birth", animal.name),
            message_np=cls.get_timing_message_np(days_until, "प्रसवको अपेक्षित मिति", animal.name),
            notification_type='livestock',
            priority=priority,
            source_id=str(animal.id),
            source_type='livestock',
            action_url=f'/livestock/{animal.id}/',
            action_label=ACTION_LABELS['en']['view_animal'],
            action_label_np=ACTION_LABELS['np']['view_animal'],
            due_date=animal.expected_birth_date,
        )
        print(f"    ✅ NEW notification sent (ID: {notification.id})")
        return 1

    @classmethod
    def _send_health_alert(cls, record, days_until):
        priority = cls.get_priority(days_until)
        notification = send_notification(
            farmer=record.animal.farmer,
            title=f"🏥 Health Follow-up - {record.animal.name}",
            title_np=f"🏥 स्वास्थ्य पुन: जाँच - {record.animal.name}",
            message=cls.get_timing_message(
                days_until, f"health follow-up ({record.diagnosis})", record.animal.name
            ),
            message_np=cls.get_timing_message_np(
                days_until,
                f"स्वास्थ्य पुन: जाँच ({record.diagnosis})",
                record.animal.name,
            ),
            notification_type='livestock',
            priority=priority,
            source_id=str(record.animal.id),
            source_type='livestock',
            action_url=f'/livestock/{record.animal.id}/',
            action_label=ACTION_LABELS['en']['view_animal'],
            action_label_np=ACTION_LABELS['np']['view_animal'],
            due_date=record.follow_up_date,
        )
        print(f"    ✅ NEW notification sent (ID: {notification.id})")
        return 1
    
    @classmethod
    def generate_vaccination_alerts(cls, farmer=None, force=False):
        """Generate alerts for upcoming/overdue vaccinations."""
        today = date.today()
        alerts_count = 0
        
        print("\n📋 Checking vaccination alerts...")
        
        query = VaccinationRecord.objects.filter(
            next_due_date__isnull=False
        )
        if farmer:
            query = query.filter(animal__farmer=farmer)
            
        vaccines = query.select_related('animal', 'animal__farmer')
        
        for vax in vaccines:
            days_until = (vax.next_due_date - today).days
            
            if cls._in_alert_window('vaccination', days_until):
                print(f"  🐄 {vax.animal.name}: {vax.vaccine_name} due in {days_until} days")
                count = cls.generate_vaccination_alert_for_record(vax, force=force)
                if count:
                    alerts_count += count
        
        return alerts_count
    
    @classmethod
    def generate_pregnancy_alerts(cls, farmer=None, force=False):
        """Generate alerts for upcoming/overdue births."""
        today = date.today()
        alerts_count = 0
        
        print("\n📋 Checking pregnancy alerts...")
        
        query = Animal.objects.filter(
            is_pregnant=True,
            expected_birth_date__isnull=False,
            status='active'
        )
        if farmer:
            query = query.filter(farmer=farmer)
            
        pregnant_animals = query
        
        for animal in pregnant_animals:
            days_until = (animal.expected_birth_date - today).days
            
            if cls._in_alert_window('pregnancy', days_until):
                print(f"  🐄 {animal.name}: birth due in {days_until} days")
                count = cls.generate_pregnancy_alert_for_animal(animal, force=force)
                if count:
                    alerts_count += count
        
        return alerts_count
    
    @classmethod
    def generate_health_followup_alerts(cls, farmer=None, force=False):
        """Generate alerts for health checkup follow-ups."""
        today = date.today()
        alerts_count = 0
        
        print("\n📋 Checking health follow-up alerts...")
        
        query = HealthRecord.objects.filter(
            follow_up_date__isnull=False
        )
        if farmer:
            query = query.filter(animal__farmer=farmer)
            
        health_records = query.select_related('animal', 'animal__farmer')
        
        for record in health_records:
            days_until = (record.follow_up_date - today).days
            
            if cls._in_alert_window('health_followup', days_until):
                print(f"  🐄 {record.animal.name}: health follow-up due in {days_until} days")
                count = cls.generate_health_alert_for_record(record, force=force)
                if count:
                    alerts_count += count
        
        return alerts_count
    
    @classmethod
    def generate_all_alerts(cls, farmer=None, force=False):
        """Generate all livestock alerts."""
        print("=" * 50)
        print("🐄 LIVESTOCK ALERT GENERATOR")
        print("=" * 50)
        
        if farmer:
            print(f"👤 Generating alerts for: {farmer.username}")
        if force:
            print("🔧 Force mode: Bypassing 'sent today' duplicate check")
        
        total = 0
        total += cls.generate_vaccination_alerts(farmer=farmer, force=force)
        total += cls.generate_pregnancy_alerts(farmer=farmer, force=force)
        total += cls.generate_health_followup_alerts(farmer=farmer, force=force)
        
        print("\n" + "=" * 50)
        print(f"✅ TOTAL ALERTS GENERATED: {total}")
        print("=" * 50)
        
        return total