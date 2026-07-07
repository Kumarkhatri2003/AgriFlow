# notifications/serializers.py

from rest_framework import serializers
from .models import Notification


class NotificationSerializer(serializers.ModelSerializer):
    """Serializer for notifications.models.Notification (crop/livestock/weather/admin alerts)."""

    priority_display = serializers.CharField(source='get_priority_display', read_only=True)
    type_display = serializers.CharField(source='get_notification_type_display', read_only=True)
    due_date_str = serializers.SerializerMethodField()

    class Meta:
        model = Notification
        fields = [
            'id',
            'title',
            'message',
            'title_np',
            'message_np',
            'notification_type',
            'type_display',
            'priority',
            'priority_display',
            'source_id',
            'source_type',
            'action_url',
            'action_label',
            'action_label_np',
            'due_date',
            'due_date_str',
            'is_read',
            'read_at',
            'is_completed',
            'completed_at',
            'created_at',
        ]
        read_only_fields = ['id', 'created_at', 'read_at', 'completed_at']

    def get_due_date_str(self, obj):
        if obj.due_date:
            return obj.due_date.isoformat()
        return None