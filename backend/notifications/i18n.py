"""Localized notification API payloads."""

PRIORITY_DISPLAY = {
    'en': {
        'critical': 'Critical - Overdue',
        'urgent': 'Urgent - Today',
        'high': 'High - 1-2 days',
        'medium': 'Medium - 3-4 days',
        'low': 'Low - 5+ days',
    },
    'np': {
        'critical': 'गम्भीर - म्याद नाघेको',
        'urgent': 'अत्यावश्यक - आज',
        'high': 'उच्च - १-२ दिन',
        'medium': 'मध्यम - ३-४ दिन',
        'low': 'न्यून - ५+ दिन',
    },
}

TYPE_DISPLAY = {
    'en': {
        'livestock': 'Livestock Alert',
        'crop': 'Crop Alert',
        'weather': 'Weather Alert',
        'admin': 'Admin Announcement',
    },
    'np': {
        'livestock': 'पशुपालन सतर्कता',
        'crop': 'बाली सतर्कता',
        'weather': 'मौसम सतर्कता',
        'admin': 'प्रशासक घोषणा',
    },
}

ACTION_LABELS = {
    'en': {
        'view_crop': 'View Crop',
        'view_animal': 'View Animal',
    },
    'np': {
        'view_crop': 'बाली हेर्नुहोस्',
        'view_animal': 'जनावर हेर्नुहोस्',
    },
}


def normalize_lang(lang):
    if not lang:
        return 'en'
    lang = str(lang).lower().strip()
    if lang in ('np', 'ne', 'nepali', 'ne-np'):
        return 'np'
    return 'en'


def get_request_language(request):
    if request is None:
        return 'en'
    return normalize_lang(
        request.query_params.get('lang')
        or request.headers.get('Accept-Language', '').split(',')[0].split('-')[0]
    )


def pick_localized(primary, secondary, lang):
    """Use Nepali when requested and available; otherwise English."""
    if lang == 'np' and secondary:
        return secondary
    return primary or secondary or ''


def notification_to_dict(notification, lang='en'):
    lang = normalize_lang(lang)
    title = pick_localized(notification.title, getattr(notification, 'title_np', None), lang)
    message = pick_localized(notification.message, getattr(notification, 'message_np', None), lang)
    action_label = pick_localized(
        notification.action_label,
        getattr(notification, 'action_label_np', None),
        lang,
    )
    priority = notification.priority
    ntype = notification.notification_type

    return {
        'id': notification.id,
        'title': title,
        'message': message,
        'priority': priority,
        'priority_display': PRIORITY_DISPLAY.get(lang, PRIORITY_DISPLAY['en']).get(
            priority, priority
        ),
        'type': ntype,
        'type_display': TYPE_DISPLAY.get(lang, TYPE_DISPLAY['en']).get(ntype, ntype),
        'is_read': notification.is_read,
        'is_completed': notification.is_completed,
        'completed_at': notification.completed_at.isoformat() if notification.completed_at else None,
        'created_at': notification.created_at.isoformat(),
        'action_url': notification.action_url,
        'action_label': action_label,
        'source_id': notification.source_id,
        'source_type': notification.source_type,
        'lang': lang,
    }
