# crops/services/reminder_service.py

from datetime import date
from crops.models import Crop, CropActivityRule
from crops.services.config_matcher import CropConfigMatcher
from notifications.action_priority import priority_from_days_until
from notifications.utils import send_notification
from notifications.i18n import ACTION_LABELS


class CropReminderService:
    """
    Generate crop activity reminders based on planting date and growth stages
    Uses the existing send_notification utility
    """
    
    @staticmethod
    def generate_reminders_for_crop(crop):
        """
        Generate reminders for a single crop
        crop: Your existing Crop model instance
        """
        
        if not crop.planting_date:
            return []
        
        # Update growth stage first to ensure consistency in the DB
        if crop.status == 'active':
            crop.update_growth_stage(save=True)
        
        # Get farmer's region from User model
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
            title_base = f"🌾 {crop.name}: {rule.title}"
            
            # Determine trigger day (7 days in advance)
            if rule.day_offset == 0:
                trigger_day = 0
            else:
                trigger_day = max(0, rule.day_offset - 7)
                
            # Case 1: Advance reminder day (7 days early, or day 0 if offset < 7)
            if days_into_stage == trigger_day:
                # Check if a notification already exists for this rule and crop
                exists = Notification.objects.filter(
                    farmer=crop.farmer,
                    notification_type='crop',
                    source_id=str(crop.id),
                    source_type='crop',
                    title__startswith=f"🌾 {crop.name}: {rule.title}"
                ).exists()
                
                if not exists:
                    days_left = rule.day_offset - days_into_stage if rule.day_offset > 0 else 0
                    reminder = CropReminderService._create_reminder(
                        crop, rule, days_since, current_stage, config,
                        is_advance=True, days_left=days_left
                    )
                    reminders.append(reminder)
                    
            # Case 2: Today is the scheduled day
            elif rule.day_offset > 0 and days_into_stage == rule.day_offset:
                # Look for an existing uncompleted notification
                existing = Notification.objects.filter(
                    farmer=crop.farmer,
                    notification_type='crop',
                    source_id=str(crop.id),
                    source_type='crop',
                    title__startswith=f"🌾 {crop.name}: {rule.title}",
                    is_completed=False
                ).first()
                
                if existing:
                    existing.priority = priority_from_days_until(0)
                    existing.title = f"🌾 {crop.name}: {rule.title} (Scheduled Today)"
                    existing.save(update_fields=['priority', 'title'])
                    reminders.append(existing)
                else:
                    # Check if a completed one exists. If not, create a new today reminder
                    completed_exists = Notification.objects.filter(
                        farmer=crop.farmer,
                        notification_type='crop',
                        source_id=str(crop.id),
                        source_type='crop',
                        title__startswith=f"🌾 {crop.name}: {rule.title}",
                        is_completed=True
                    ).exists()
                    
                    if not completed_exists:
                        reminder = CropReminderService._create_reminder(
                            crop, rule, days_since, current_stage, config,
                            is_today=True
                        )
                        reminders.append(reminder)
                        
            # Case 3: Overdue (past scheduled day)
            elif rule.day_offset > 0 and days_into_stage > rule.day_offset:
                # Check if there is an uncompleted notification
                existing = Notification.objects.filter(
                    farmer=crop.farmer,
                    notification_type='crop',
                    source_id=str(crop.id),
                    source_type='crop',
                    title__startswith=f"🌾 {crop.name}: {rule.title}",
                    is_completed=False
                ).first()
                
                if existing:
                    days_overdue = days_into_stage - rule.day_offset
                    existing.priority = priority_from_days_until(-days_overdue)
                    if "Overdue" not in existing.title:
                        existing.title = f"🚨 {crop.name}: {rule.title} (Overdue)"
                    existing.save(update_fields=['priority', 'title'])
                    reminders.append(existing)
                    
        return reminders
    
    @staticmethod
    def generate_reminders_for_user(user):
        """Generate reminders for all active crops of a specific user"""
        active_crops = Crop.objects.filter(farmer=user, status='active')
        reminders = []
        for crop in active_crops:
            reminders.extend(CropReminderService.generate_reminders_for_crop(crop))
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
    def _already_reminded_today(crop, rule):
        """Check if this reminder was already sent today"""
        from notifications.models import Notification
        
        title = f"🌾 {crop.name}: {rule.title}"
        return Notification.objects.filter(
            farmer=crop.farmer,
            notification_type='crop',
            source_id=str(crop.id),
            source_type='crop',
            title__startswith=title,
            created_at__date=date.today()
        ).exists()
    
    @staticmethod
    def _build_crop_message(crop, rule, days, stage_display, config, is_advance, days_left, is_today, lang='en'):
        rule_title = rule.title_np if lang == 'np' and getattr(rule, 'title_np', None) else rule.title
        crop_name = crop.name_np if lang == 'np' and getattr(crop, 'name_np', None) else crop.name
        rule_desc = rule.description_np if lang == 'np' and getattr(rule, 'description_np', None) else rule.description

        if lang == 'np':
            lines = [rule_title, "", f"🌾 बाली: {crop_name}"]
            if crop.variety:
                lines.append(f"📌 जात: {crop.variety}")
            if config.region:
                lines.append(f"📍 क्षेत्र: {config.get_region_display()}")
            if is_advance:
                lines.append(f"📅 तालिका: {days_left} दिनमा (रोपाइको {days + days_left} औं दिन)")
                lines.append("⚠️ [पूर्व सूचना] आवश्यक सामग्री तयार पार्नुहोस्।")
            elif is_today:
                lines.append(f"📅 तालिका: आज (रोपाइको {days} औं दिन)")
            else:
                lines.append(f"📅 दिन: {days} - {stage_display}")
        else:
            lines = [rule_title, "", f"🌾 Crop: {crop_name}"]
            if crop.variety:
                lines.append(f"📌 Variety: {crop.variety}")
            if config.region:
                lines.append(f"📍 Region: {config.get_region_display()}")
            if is_advance:
                lines.append(f"📅 Schedule: in {days_left} days (on Day {days + days_left} of planting)")
                lines.append("⚠️ [Advance Notice] Please prepare necessary inputs.")
            elif is_today:
                lines.append(f"📅 Schedule: TODAY (Day {days} of planting)")
            else:
                lines.append(f"📅 Day: {days} - {stage_display}")

        lines.extend(["", rule_desc or ""])

        if rule.measurements:
            lines.extend(["", "📊 आवश्यक:" if lang == 'np' else "📊 Required:", rule.measurements])
        if rule.target_pest:
            lines.extend(["", "⚠️ सतर्कता:" if lang == 'np' else "⚠️ Watch for:", rule.target_pest])
        if rule.recommendations:
            lines.extend(["", "💡 सिफारिस:" if lang == 'np' else "💡 Recommendations:", rule.recommendations])

        return "\n".join(lines)

    @staticmethod
    def _build_crop_title(crop, rule, is_advance, days_left, is_today, lang='en'):
        rule_title = rule.title_np if lang == 'np' and getattr(rule, 'title_np', None) else rule.title
        crop_name = crop.name_np if lang == 'np' and getattr(crop, 'name_np', None) else crop.name
        if is_advance:
            if lang == 'np':
                return f"🌾 {crop_name}: {rule_title} ({days_left} दिनमा)"
            return f"🌾 {crop.name}: {rule.title} (In {days_left} Days)"
        if is_today:
            if lang == 'np':
                return f"🌾 {crop_name}: {rule_title} (आज तालिका)"
            return f"🌾 {crop.name}: {rule.title} (Scheduled Today)"
        if lang == 'np':
            return f"🌾 {crop_name}: {rule_title}"
        return f"🌾 {crop.name}: {rule.title}"

    @staticmethod
    def _create_reminder(crop, rule, days, stage, config, is_advance=False, days_left=0, is_today=False):
        """Create notification using your send_notification utility"""
        
        stage_display = config.get_stage_display_name(days)
        message = CropReminderService._build_crop_message(
            crop, rule, days, stage_display, config, is_advance, days_left, is_today, 'en'
        )
        message_np = CropReminderService._build_crop_message(
            crop, rule, days, stage_display, config, is_advance, days_left, is_today, 'np'
        )

        if is_today:
            days_until = 0
        elif is_advance:
            days_until = days_left
        else:
            days_until = 0
        priority = priority_from_days_until(days_until)

        action_url = f"/crops/{crop.id}" if crop.id else None
        title = CropReminderService._build_crop_title(crop, rule, is_advance, days_left, is_today, 'en')
        title_np = CropReminderService._build_crop_title(crop, rule, is_advance, days_left, is_today, 'np')

        notification = send_notification(
            farmer=crop.farmer,
            title=title,
            title_np=title_np,
            message=message,
            message_np=message_np,
            notification_type='crop',
            priority=priority,
            source_id=str(crop.id),
            source_type='crop',
            action_url=action_url,
            action_label=ACTION_LABELS['en']['view_crop'],
            action_label_np=ACTION_LABELS['np']['view_crop'],
        )
        return notification