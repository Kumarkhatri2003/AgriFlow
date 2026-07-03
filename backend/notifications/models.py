# notifications/models.py

from django.db import models
from django.conf import settings

User = settings.AUTH_USER_MODEL


class Notification(models.Model):
    """Notification model for all alerts"""
    
    PRIORITY_CHOICES = [
        ('critical', 'Critical - Overdue'),
        ('urgent', 'Urgent - Today'),
        ('high', 'High - 1-2 days'),
        ('medium', ' Medium - 3-4 days'),
        ('low', 'Low - 5+ days'),
    ]
    
    TYPE_CHOICES = [
        ('livestock', 'Livestock Alert'),
        ('crop', 'Crop Alert'),
        ('weather', 'Weather Alert'),
        ('admin', 'Admin Announcement'),
    ]
    
    # ========== RELATIONSHIPS ==========
    farmer = models.ForeignKey(
        User, 
        on_delete=models.CASCADE, 
        related_name='user_notifications'
    )
    
    # ========== CONTENT ==========
    title = models.CharField(max_length=200)
    message = models.TextField()
    title_np = models.CharField(max_length=200, blank=True, default='')
    message_np = models.TextField(blank=True, default='')
    priority = models.CharField(max_length=10, choices=PRIORITY_CHOICES, default='medium')
    notification_type = models.CharField(max_length=20, choices=TYPE_CHOICES, default='livestock')
    
    # ========== LINK TO SOURCE ==========
    source_id = models.CharField(max_length=100, null=True, blank=True)
    source_type = models.CharField(max_length=50, blank=True, null=True)
    
    # ========== ACTION BUTTON ==========
    action_url = models.CharField(max_length=500, blank=True, null=True)
    action_label = models.CharField(max_length=100, blank=True, null=True)
    action_label_np = models.CharField(max_length=100, blank=True, null=True)
    
    # ========== STATUS ==========
    is_read = models.BooleanField(default=False)
    read_at = models.DateTimeField(null=True, blank=True)
    is_completed = models.BooleanField(default=False)  # <-- ADD THIS FIELD
    completed_at = models.DateTimeField(null=True, blank=True)  # <-- ADD THIS FIELD
    
    due_date = models.DateField(null=True, blank=True, help_text='Scheduled activity date for calendar views')
    
    # ========== TIMESTAMPS ==========
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
        db_table = 'notifications_notification'
        indexes = [
            models.Index(fields=['farmer', 'is_read']),
            models.Index(fields=['created_at']),
            models.Index(fields=['notification_type', 'priority']),
            models.Index(fields=['is_completed']),  # <-- ADD THIS INDEX
        ]
    
    def __str__(self):
        return f"[{self.get_priority_display()}] {self.title}"
    
    def mark_as_read(self):
        """Mark notification as read"""
        from django.utils import timezone
        if not self.is_read:
            self.is_read = True
            self.read_at = timezone.now()
            self.save(update_fields=['is_read', 'read_at'])
    
    def mark_as_unread(self):
        """Mark notification as unread"""
        self.is_read = False
        self.read_at = None
        self.save(update_fields=['is_read', 'read_at'])
    
    def mark_as_completed(self):
        """Mark notification action as completed"""
        from django.utils import timezone
        if not self.is_completed:
            self.is_completed = True
            self.completed_at = timezone.now()
            self.save(update_fields=['is_completed', 'completed_at'])
    
    def mark_as_uncompleted(self):
        """Mark notification action as uncompleted (reopen)"""
        self.is_completed = False
        self.completed_at = None
        self.save(update_fields=['is_completed', 'completed_at'])