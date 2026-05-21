from django.db import models
from django.conf import settings

User = settings.AUTH_USER_MODEL


class Notification(models.Model):
    """Notification model for all alerts - Uses unique related_name to avoid conflicts"""
    
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
    # IMPORTANT: Uses unique related_name 'user_notifications' to avoid conflict with admin_panel
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
    
    # ========== LINK TO SOURCE (crop, livestock, etc.) ==========
    source_id = models.CharField(max_length=100, null=True, blank=True, help_text="ID of the related crop/animal (UUID)")
    source_type = models.CharField(max_length=50, blank=True, null=True, help_text="e.g., crop, livestock")
    
    # ========== ACTION BUTTON ==========
    action_url = models.CharField(max_length=500, blank=True, null=True)
    action_label = models.CharField(max_length=100, blank=True, null=True)
    action_label_np = models.CharField(max_length=100, blank=True, null=True)
    
    # ========== STATUS ==========
    is_read = models.BooleanField(default=False)
    read_at = models.DateTimeField(null=True, blank=True)
    is_completed = models.BooleanField(default=False)
    completed_at = models.DateTimeField(null=True, blank=True)
    
    # ========== TIMESTAMPS ==========
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
        db_table = 'notifications_notification'  # Explicit table name
        indexes = [
            models.Index(fields=['farmer', 'is_read']),
            models.Index(fields=['created_at']),
            models.Index(fields=['notification_type', 'priority']),
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
        """Mark action as completed"""
        from django.utils import timezone
        if not self.is_completed:
            self.is_completed = True
            self.completed_at = timezone.now()
            self.save(update_fields=['is_completed', 'completed_at'])
            
    def mark_as_uncompleted(self):
        """Mark action as uncompleted"""
        self.is_completed = False
        self.completed_at = None
        self.save(update_fields=['is_completed', 'completed_at'])