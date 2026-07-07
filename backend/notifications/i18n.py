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
    """
    Get language from request.
    
    Args:
        request: Django request object
        
    Returns:
        str: 'en' or 'np'
    """
    lang = request.query_params.get('lang', 'en')
    if lang not in ['en', 'np']:
        lang = 'en'
    return lang


def get_localized_text(obj, field_name, lang='en'):
    """
    Get localized text from object.
    If lang is 'np', returns field_name_np if exists, else field_name.
    
    Args:
        obj: Model instance
        field_name: Base field name (e.g., 'title', 'message')
        lang: Language code ('en' or 'np')
        
    Returns:
        str: Localized text
    """
    np_field = f"{field_name}_np"
    if lang == 'np' and hasattr(obj, np_field):
        return getattr(obj, np_field) or getattr(obj, field_name)
    return getattr(obj, field_name)


def notification_to_dict(notification, lang='en'):
    """
    Convert notification to dictionary with localized content.
    
    Returns both the localized text (title, message) AND the raw Nepali fields
    so the frontend can display them properly.
    
    Args:
        notification: Notification model instance
        lang: Language code ('en' or 'np')
        
    Returns:
        dict: Notification data with localized content
    """
    # Get localized content based on language
    if lang == 'np':
        title = notification.title_np or notification.title
        message = notification.message_np or notification.message
        action_label = notification.action_label_np or notification.action_label
    else:
        title = notification.title
        message = notification.message
        action_label = notification.action_label

    # Handle due_date
    due_date = notification.due_date
    if due_date is None and notification.created_at:
        due_date = notification.created_at.date()
    
    return {
        # ===== ID =====
        'id': notification.id,
        
        # ===== LOCALIZED CONTENT (for display) =====
        'title': title,
        'message': message,
        
        # ===== RAW NEPALI FIELDS (for language switching) =====
        'title_np': notification.title_np or '',
        'message_np': notification.message_np or '',
        
        # ===== RAW ENGLISH FIELDS (for reference) =====
        'title_en': notification.title,
        'message_en': notification.message,
        
        # ===== PRIORITY =====
        'priority': notification.priority,
        'priority_display': notification.get_priority_display(),
        
        # ===== NOTIFICATION TYPE =====
        'notification_type': notification.notification_type,
        'type': notification.notification_type,
        'type_display': notification.get_notification_type_display(),
        
        # ===== STATUS =====
        'is_read': notification.is_read,
        'is_completed': notification.is_completed,
        
        # ===== DATES =====
        'created_at': notification.created_at,
        'due_date': due_date.isoformat() if due_date else None,
        
        # ===== ACTION BUTTON =====
        'action_url': notification.action_url,
        'action_label': action_label,
        'action_label_np': notification.action_label_np or '',
        
        # ===== SOURCE =====
        'source_id': notification.source_id,
        'source_type': notification.source_type,
        
        # ===== FARMER ===== (if needed)
        'farmer_id': notification.farmer.id if notification.farmer else None,
    }


def notification_list_to_dict(notifications, lang='en'):
    """
    Convert a list of notifications to dictionary with localized content.
    
    Args:
        notifications: QuerySet or list of Notification objects
        lang: Language code ('en' or 'np')
        
    Returns:
        list: List of notification dictionaries
    """
    return [notification_to_dict(n, lang) for n in notifications]