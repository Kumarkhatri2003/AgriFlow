# notifications/i18n.py

ACTION_LABELS = {
    'en': {
        'view_crop': 'View Crop',
        'view_animal': 'View Animal',
        'view_notification': 'View Details',
        'mark_read': 'Mark as Read',
        'mark_complete': 'Mark as Complete',
        'dismiss': 'Dismiss',
    },
    'np': {
        'view_crop': 'बाली हेर्नुहोस्',
        'view_animal': 'पशु हेर्नुहोस्',
        'view_notification': 'विवरण हेर्नुहोस्',
        'mark_read': 'पढेको चिन्ह लगाउनुहोस्',
        'mark_complete': 'पूरा भएको चिन्ह लगाउनुहोस्',
        'dismiss': 'हटाउनुहोस्',
    }
}


def get_request_language(request):
    """Get language from request"""
    lang = request.query_params.get('lang', 'en')
    if lang not in ['en', 'np']:
        lang = 'en'
    return lang


def get_localized_text(obj, field_name, lang='en'):
    """
    Get localized text from object.
    If lang is 'np', returns field_name_np if exists, else field_name.
    """
    np_field = f"{field_name}_np"
    if lang == 'np' and hasattr(obj, np_field):
        return getattr(obj, np_field) or getattr(obj, field_name)
    return getattr(obj, field_name)


def notification_to_dict(notification, lang='en'):
    """
    Convert notification to dictionary with localized content.
    """
    if lang == 'np':
        title = notification.title_np or notification.title
        message = notification.message_np or notification.message
        action_label = notification.action_label_np or notification.action_label
    else:
        title = notification.title
        message = notification.message
        action_label = notification.action_label

    due_date = notification.due_date
    if due_date is None and notification.created_at:
        due_date = notification.created_at.date()
    
    return {
        'id': notification.id,
        'title': title,
        'message': message,
        'priority': notification.priority,
        'priority_display': notification.get_priority_display(),
        'notification_type': notification.notification_type,
        'type': notification.notification_type,
        'type_display': notification.get_notification_type_display(),
        'is_read': notification.is_read,
        'is_completed': notification.is_completed,
        'created_at': notification.created_at,
        'due_date': due_date.isoformat() if due_date else None,
        'action_url': notification.action_url,
        'action_label': action_label,
        'source_id': notification.source_id,
        'source_type': notification.source_type,
    }