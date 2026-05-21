"""
Livestock Alert Generator - Based on due dates (NO DUPLICATES)
"""

from datetime import date, timedelta
from django.utils import timezone
from notifications.action_priority import priority_from_days_until
from notifications.utils import send_notification
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
    
    @classmethod
    def get_priority(cls, days_until):
        """Determine priority based on days remaining until action date."""
        return priority_from_days_until(days_until)

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
    def notification_already_sent(cls, farmer, animal_id, alert_type, due_date):
        """Check if notification already sent for this animal/event in last 7 days"""
        seven_days_ago = timezone.now() - timedelta(days=7)
        
        # CRITICAL: Convert UUID to string for comparison
        animal_id_str = str(animal_id)
        
        # Map alert_type to a searchable substring in the title
        title_search = ''
        if alert_type == 'vaccination':
            title_search = 'Vaccination'
        elif alert_type == 'pregnancy':
            title_search = 'Birth Alert'
        elif alert_type == 'health_followup':
            title_search = 'Health Follow-up'
        
        query = Notification.objects.filter(
            farmer=farmer,
            source_id=animal_id_str,
            source_type='livestock',
            notification_type='livestock',
            created_at__gte=seven_days_ago,
        )

        if title_search:
            query = query.filter(title__icontains=title_search)

        # Completed task — do not send the same alert again
        if query.filter(is_completed=True).exists():
            return True

        existing = query.filter(is_completed=False).exists()
        
        if existing:
            print(f"    ⏭️ SKIPPING - already notified")
        
        return existing
    
    @classmethod
    def generate_vaccination_alerts(cls, farmer=None):
        """Generate alerts for upcoming/overdue vaccinations (NO DUPLICATES)"""
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
            
            if -7 <= days_until <= 7:
                print(f"  🐄 {vax.animal.name}: {vax.vaccine_name} due in {days_until} days")
                
                if cls.notification_already_sent(
                    vax.animal.farmer,
                    vax.animal.id,
                    'vaccination',
                    vax.next_due_date
                ):
                    continue
                
                priority = cls.get_priority(days_until)
                activity_en = f"{vax.vaccine_name} vaccination"
                activity_np = f"{vax.vaccine_name} खोप"
                message = cls.get_timing_message(days_until, activity_en, vax.animal.name)
                message_np = cls.get_timing_message_np(days_until, activity_np, vax.animal.name)

                send_notification(
                    farmer=vax.animal.farmer,
                    title=f"💉 {vax.vaccine_name} Vaccination - {vax.animal.name}",
                    title_np=f"💉 {vax.vaccine_name} खोप - {vax.animal.name}",
                    message=message,
                    message_np=message_np,
                    notification_type='livestock',
                    priority=priority,
                    source_id=str(vax.animal.id),
                    source_type='livestock',
                    action_url=f'/livestock/{vax.animal.id}/',
                    action_label=ACTION_LABELS['en']['view_animal'],
                    action_label_np=ACTION_LABELS['np']['view_animal'],
                )
                alerts_count += 1
                print(f"    ✅ NEW notification sent")
        
        return alerts_count
    
    @classmethod
    def generate_pregnancy_alerts(cls, farmer=None):
        """Generate alerts for upcoming/overdue births (NO DUPLICATES)"""
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
            
            if -7 <= days_until <= 14:
                print(f"  🐄 {animal.name}: birth due in {days_until} days")
                
                if cls.notification_already_sent(
                    animal.farmer,
                    animal.id,
                    'pregnancy',
                    animal.expected_birth_date
                ):
                    continue
                
                priority = cls.get_priority(days_until)
                message = cls.get_timing_message(days_until, "expected birth", animal.name)
                message_np = cls.get_timing_message_np(days_until, "प्रसवको अपेक्षित मिति", animal.name)

                send_notification(
                    farmer=animal.farmer,
                    title=f"🐄 Birth Alert - {animal.name}",
                    title_np=f"🐄 प्रसव सतर्कता - {animal.name}",
                    message=message,
                    message_np=message_np,
                    notification_type='livestock',
                    priority=priority,
                    source_id=str(animal.id),
                    source_type='livestock',
                    action_url=f'/livestock/{animal.id}/',
                    action_label=ACTION_LABELS['en']['view_animal'],
                    action_label_np=ACTION_LABELS['np']['view_animal'],
                )
                alerts_count += 1
                print(f"    ✅ NEW notification sent")
        
        return alerts_count
    
    @classmethod
    def generate_health_followup_alerts(cls, farmer=None):
        """Generate alerts for health checkup follow-ups (NO DUPLICATES)"""
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
            
            if -7 <= days_until <= 7:
                print(f"  🐄 {record.animal.name}: health follow-up due in {days_until} days")
                
                if cls.notification_already_sent(
                    record.animal.farmer,
                    record.animal.id,
                    'health_followup',
                    record.follow_up_date
                ):
                    continue
                
                priority = cls.get_priority(days_until)
                message = cls.get_timing_message(
                    days_until, f"health follow-up ({record.diagnosis})", record.animal.name
                )
                message_np = cls.get_timing_message_np(
                    days_until,
                    f"स्वास्थ्य पुन: जाँच ({record.diagnosis})",
                    record.animal.name,
                )

                send_notification(
                    farmer=record.animal.farmer,
                    title=f"🏥 Health Follow-up - {record.animal.name}",
                    title_np=f"🏥 स्वास्थ्य पुन: जाँच - {record.animal.name}",
                    message=message,
                    message_np=message_np,
                    notification_type='livestock',
                    priority=priority,
                    source_id=str(record.animal.id),
                    source_type='livestock',
                    action_url=f'/livestock/{record.animal.id}/',
                    action_label=ACTION_LABELS['en']['view_animal'],
                    action_label_np=ACTION_LABELS['np']['view_animal'],
                )
                alerts_count += 1
                print(f"    ✅ NEW notification sent")
        
        return alerts_count
    
    @classmethod
    def generate_all_alerts(cls, farmer=None):
        """Generate all livestock alerts (NO DUPLICATES)"""
        print("=" * 50)
        print("🐄 LIVESTOCK ALERT GENERATOR")
        print("=" * 50)
        
        total = 0
        total += cls.generate_vaccination_alerts(farmer=farmer)
        total += cls.generate_pregnancy_alerts(farmer=farmer)
        total += cls.generate_health_followup_alerts(farmer=farmer)
        
        print("\n" + "=" * 50)
        print(f"✅ TOTAL ALERTS GENERATED: {total}")
        print("=" * 50)
        
        return total