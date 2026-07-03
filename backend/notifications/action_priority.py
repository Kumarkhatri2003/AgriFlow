# notifications/action_priority.py

"""Priority levels derived from days until an action is due."""

PRE_ALERT_DAYS = 7
EARLY_ALERT_DAYS = 6


def crop_priority_from_days_until(days_until: int, pre_days: int = PRE_ALERT_DAYS) -> str:
    """
    Map days until a crop activity is due to notification priority.
    First alert window: 6–7 days before (low).
    """
    if days_until < 0:
        return 'critical'
    if days_until == 0:
        return 'urgent'
    if days_until <= 2:
        return 'high'
    if days_until <= 5:
        return 'medium'
    if EARLY_ALERT_DAYS <= days_until <= pre_days:
        return 'low'
    return 'low'


def should_send_crop_reminder_today(days_until: int, pre_days: int = PRE_ALERT_DAYS):
    """
    Return priority string if a crop reminder should be sent today, else None.
    """
    if EARLY_ALERT_DAYS <= days_until <= pre_days:
        return 'low'
    if 3 <= days_until <= 5:
        return 'medium'
    if 1 <= days_until <= 2:
        return 'high'
    if days_until == 0:
        return 'urgent'
    if days_until < 0:
        days_overdue = abs(days_until)
        if days_overdue % 2 == 0 or days_overdue <= 3:
            return 'critical'
    return None


def priority_from_days_until(days_until: int) -> str:
    """
    Map days until action date to notification priority.

    critical → overdue (days_until < 0)
    urgent   → due today (days_until == 0)
    high     → 1–2 days
    medium   → 3–4 days
    low      → 5+ days away
    """
    if days_until < 0:
        return 'critical'
    if days_until == 0:
        return 'urgent'
    if days_until <= 2:
        return 'high'
    if days_until <= 4:
        return 'medium'
    return 'low'


def get_priority_level(days_until: int) -> dict:
    """
    Get priority level with display info.
    """
    priority = priority_from_days_until(days_until)
    
    display_info = {
        'critical': {
            'label': 'Critical',
            'color': 'red',
            'icon': '🚨',
            'message': 'Overdue - Action required immediately!'
        },
        'urgent': {
            'label': 'Urgent',
            'color': 'orange',
            'icon': '🔴',
            'message': 'Due today - Complete now!'
        },
        'high': {
            'label': 'High',
            'color': 'yellow',
            'icon': '🟠',
            'message': 'Due in 1-2 days - Prepare!'
        },
        'medium': {
            'label': 'Medium',
            'color': 'blue',
            'icon': '🟡',
            'message': 'Due in 3-4 days - Plan ahead'
        },
        'low': {
            'label': 'Low',
            'color': 'green',
            'icon': '🟢',
            'message': 'Due in 5+ days - Start preparing'
        }
    }
    
    return {
        'priority': priority,
        'display': display_info.get(priority, display_info['low'])
    }