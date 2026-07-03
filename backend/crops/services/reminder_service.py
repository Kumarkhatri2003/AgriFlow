# crops/services/reminder_service.py

from datetime import date, timedelta
from crops.models import Crop, CropActivityRule
from crops.services.config_matcher import CropConfigMatcher
from notifications.action_priority import should_send_crop_reminder_today, PRE_ALERT_DAYS
from notifications import utils as notification_utils
from notifications.i18n import ACTION_LABELS


class CropReminderService:
    """
    Generate crop activity reminders with priority escalation
    """
    
    @staticmethod
    def generate_reminders_for_crop(crop):
        """Generate reminders for a single crop"""
        
        if not crop.planting_date or crop.status != 'active':
            return []
        
        # Get farmer's region
        farmer_region = crop.farmer.geographical_region if hasattr(crop.farmer, 'geographical_region') else None
        
        # Find matching config
        config, match_strategy = CropConfigMatcher.find_best_match(
            crop_name=crop.name,
            variety=crop.variety if crop.variety else None,
            region=farmer_region,
            planting_date=crop.planting_date
        )
        
        if not config:
            return []
            
        days_since = (date.today() - crop.planting_date).days
        
        # Check if crop is still growing
        if days_since < 0 or days_since > config.total_growing_days:
            return []
        
        # Get current stage
        current_stage = config.get_stage_name(days_since)
        
        if current_stage == 'completed':
            return []
        
        # Calculate days into current stage
        stage_start = config.get_stage_start_day(current_stage)
        days_into_stage = days_since - stage_start
        
        # Get rules for this stage
        rules = CropActivityRule.objects.filter(
            crop_config=config,
            growth_stage=current_stage,
            is_active=True
        )
        
        from notifications.models import Notification
        reminders = []
        
        for rule in rules:
            if rule.day_offset is None:
                continue
            
            # Calculate days until the activity
            days_until = rule.day_offset - days_into_stage
            
            # Get pre_reminder_days (default: 7 days — first alert at 6–7 days before)
            pre_days = getattr(rule, 'pre_reminder_days', PRE_ALERT_DAYS)
            
            # Check if there is an existing uncompleted notification to escalate/update
            existing_notif = Notification.objects.filter(
                farmer=crop.farmer,
                notification_type='crop',
                source_id=str(crop.id),
                title__icontains=rule.title,
                is_completed=False
            ).first()
            
            priority = should_send_crop_reminder_today(days_until, pre_days)
            if not priority:
                continue
                
            if existing_notif:
                # Update existing notification's priority and title
                priority_map = {
                    'low': 'low',
                    'medium': 'medium',
                    'high': 'high',
                    'urgent': 'urgent',
                    'critical': 'critical'
                }
                new_priority = priority_map.get(priority, 'medium')
                
                # Get escalated title format matching tests expectations
                priority_titles = {
                    'low': f"📋 {crop.name}: {rule.title} (In {days_until} Days)",
                    'medium': f"🟡 {crop.name}: {rule.title} (In {days_until} Days)",
                    'high': f"🟠 {crop.name}: {rule.title} (In {days_until} Days)",
                    'urgent': f"🌾 {crop.name}: {rule.title} (Scheduled Today)",
                    'critical': f"🚨 {crop.name}: {rule.title} (Overdue)"
                }
                new_title = priority_titles.get(priority, priority_titles['low'])
                
                existing_notif.priority = new_priority
                existing_notif.title = new_title
                existing_notif.save(update_fields=['priority', 'title'])
                reminders.append(existing_notif)
                continue

            # Only skip if COMPLETED (not uncompleted)
            completed_exists = Notification.objects.filter(
                farmer=crop.farmer,
                notification_type='crop',
                source_id=str(crop.id),
                title__icontains=rule.title,
                is_completed=True
            ).exists()
            
            if completed_exists:
                continue
            
            # Only skip if sent TODAY (not all time)
            sent_today = Notification.objects.filter(
                farmer=crop.farmer,
                notification_type='crop',
                source_id=str(crop.id),
                title__icontains=rule.title,
                created_at__date=date.today()
            ).exists()
            
            if sent_today:
                continue
            
            # Create reminder
            reminder = CropReminderService._create_priority_reminder(
                crop, rule, days_since, current_stage, config, days_until, priority
            )
            if reminder:
                reminders.append(reminder)
        
        return reminders
    
    @staticmethod
    def generate_reminders_for_user(user):
        """Generate reminders for all active crops of a specific user"""
        active_crops = Crop.objects.filter(farmer=user, status='active')
        reminders = []
        for crop in active_crops:
            crop_reminders = CropReminderService.generate_reminders_for_crop(crop)
            reminders.extend(crop_reminders)
        return reminders

    @staticmethod
    def generate_reminders_for_all_crops():
        """Generate reminders for all active crops - call this daily"""
        
        active_crops = Crop.objects.filter(status='active')
        
        results = {
            'total_crops': active_crops.count(),
            'total_reminders': 0,
            'details': []
        }
        
        for crop in active_crops:
            reminders = CropReminderService.generate_reminders_for_crop(crop)
            if reminders:
                results['total_reminders'] += len(reminders)
                results['details'].append({
                    'crop_id': str(crop.id),
                    'crop_name': crop.name,
                    'farmer': crop.farmer.username,
                    'reminders': len(reminders)
                })
        
        return results
    
    @staticmethod
    def _create_priority_reminder(crop, rule, days, stage, config, days_until, priority):
        """
        Create reminder with appropriate priority level
        ✅ FINAL duplicate check before creating
        """
        
        from notifications.models import Notification
        
        # ✅ FINAL CHECK: Only skip if sent TODAY
        sent_today = Notification.objects.filter(
            farmer=crop.farmer,
            notification_type='crop',
            source_id=str(crop.id),
            title__icontains=rule.title,
            created_at__date=date.today()
        ).exists()
        
        if sent_today:
            try:
                print(f"[SKIP] Already sent today for {crop.name} - {rule.title}")
            except UnicodeEncodeError:
                pass
            return None
        
        stage_display = config.get_stage_display_name(days)
        
        # Build message based on priority
        priority_messages = {
            'low': {
                'title': f"📋 {crop.name}: {rule.title} (In {days_until} Days)",
                'header': f"📋 UPCOMING ACTIVITY - {days_until} days to prepare",
                'footer': "✅ Start preparing materials and planning."
            },
            'medium': {
                'title': f"🟡 {crop.name}: {rule.title} (In {days_until} Days)",
                'header': f"🟡 ACTIVITY APPROACHING - {days_until} days left",
                'footer': "⚠️ Please start preparing and arranging resources."
            },
            'high': {
                'title': f"🟠 {crop.name}: {rule.title} (In {days_until} Days)",
                'header': f"🟠 ACTIVITY IN {days_until} DAYS - Prepare Now!",
                'footer': "🔔 This activity is coming soon. Please prepare."
            },
            'urgent': {
                'title': f"🌾 {crop.name}: {rule.title} (Scheduled Today)",
                'header': f"🔴 ACTION REQUIRED - TODAY!",
                'footer': "❗ Please complete this activity today!"
            },
            'critical': {
                'title': f"🚨 {crop.name}: {rule.title} (Overdue)",
                'header': f"🚨 ACTIVITY OVERDUE by {abs(days_until)} days!",
                'footer': "🔥 Please complete this activity immediately!"
            }
        }
        
        msg = priority_messages.get(priority, priority_messages['low'])
        
        message = f"""{msg['header']}

🌾 **Crop:** {crop.name}
📌 **Activity:** {rule.title}
📅 **Day:** {days} - {stage_display}

📋 **Details:** {rule.description}"""

        if rule.measurements:
            message += f"\n\n📊 **Required:**\n{rule.measurements}"
        
        if rule.target_pest:
            message += f"\n\n⚠️ **Watch for:**\n{rule.target_pest}"
        
        if rule.recommendations:
            message += f"\n\n💡 **Recommendations:**\n{rule.recommendations}"
        
        message += f"\n\n{msg['footer']}"

        # Map priority to notification priority
        priority_map = {
            'low': 'low',
            'medium': 'medium',
            'high': 'high',
            'urgent': 'urgent',
            'critical': 'critical'
        }
        
        # Create notification
        activity_due = date.today() + timedelta(days=days_until)
        notification = notification_utils.send_notification(
            farmer=crop.farmer,
            title=msg['title'],
            message=message,
            notification_type='crop',
            priority=priority_map.get(priority, 'medium'),
            source_id=str(crop.id),
            source_type='crop',
            action_url=f"/crops/{crop.id}",
            action_label=ACTION_LABELS['en']['view_crop'],
            due_date=activity_due,
        )
        
        try:
            print(f"[SUCCESS] Created: {msg['title']}")
        except UnicodeEncodeError:
            pass
        return notification