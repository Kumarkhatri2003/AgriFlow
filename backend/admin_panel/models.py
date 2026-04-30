from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone

User = get_user_model()


class Notification(models.Model):
    """System notifications sent to farmers"""
    
    NOTIFICATION_TYPES = [
        ('broadcast', 'Broadcast (All Farmers)'),
        ('targeted', 'Targeted (Specific Farmers)'),
        ('weather_alert', 'Weather Alert'),
        ('crop_reminder', 'Crop Care Reminder'),
        ('marketing', 'Marketing/Promotion'),
    ]
    
    PRIORITY_CHOICES = [
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
        ('urgent', 'Urgent'),
    ]
    
    title = models.CharField(max_length=255)
    message = models.TextField()
    notification_type = models.CharField(max_length=50, choices=NOTIFICATION_TYPES)
    priority = models.CharField(max_length=20, choices=PRIORITY_CHOICES, default='medium')
    
    # For targeted notifications
    target_farmers = models.ManyToManyField(User, blank=True, related_name='notifications')
    
    # Metadata
    sent_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='sent_notifications')
    sent_at = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)
    read_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        ordering = ['-sent_at']
    
    def __str__(self):
        return f"{self.title} - {self.sent_at.strftime('%Y-%m-%d')}"
    
    def mark_as_read(self):
        self.is_read = True
        self.read_at = timezone.now()
        self.save()


class SystemSetting(models.Model):
    """System-wide settings"""
    
    SETTING_TYPES = [
        ('crop_category', 'Crop Category'),
        ('livestock_type', 'Livestock Type'),
        ('expense_category', 'Expense Category'),
        ('notification_template', 'Notification Template'),
        ('system_config', 'System Configuration'),
    ]
    
    setting_type = models.CharField(max_length=50, choices=SETTING_TYPES)
    key = models.CharField(max_length=100)
    value = models.TextField()
    display_name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    order = models.IntegerField(default=0)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ['setting_type', 'key']
        ordering = ['order', 'display_name']
    
    def __str__(self):
        return f"{self.display_name} ({self.setting_type})"


class AdminLog(models.Model):
    """Track all admin actions for audit trail"""
    
    ACTION_CHOICES = [
        ('CREATE', 'Create'),
        ('UPDATE', 'Update'),
        ('DELETE', 'Delete'),
        ('ACTIVATE', 'Activate'),
        ('DEACTIVATE', 'Deactivate'),
        ('APPROVE', 'Approve'),
        ('REJECT', 'Reject'),
        ('EXPORT', 'Export'),
        ('BULK_ACTION', 'Bulk Action'),
        ('SEND_NOTIFICATION', 'Send Notification'),
    ]
    
    admin_user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='admin_logs')
    action = models.CharField(max_length=50, choices=ACTION_CHOICES)
    model_name = models.CharField(max_length=100)
    object_id = models.CharField(max_length=100, blank=True)
    object_repr = models.CharField(max_length=200, blank=True)
    changes = models.JSONField(default=dict)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.admin_user.username} - {self.action} - {self.model_name} at {self.created_at}"


class Report(models.Model):
    """Stored reports for download"""
    
    REPORT_TYPES = [
        ('farmer', 'Farmer Report'),
        ('financial', 'Financial Report'),
        ('crop', 'Crop Report'),
        ('livestock', 'Livestock Report'),
        ('custom', 'Custom Report'),
    ]
    
    FORMAT_CHOICES = [
        ('pdf', 'PDF'),
        ('excel', 'Excel'),
        ('csv', 'CSV'),
    ]
    
    report_type = models.CharField(max_length=50, choices=REPORT_TYPES)
    format = models.CharField(max_length=10, choices=FORMAT_CHOICES)
    title = models.CharField(max_length=255)
    filters = models.JSONField(default=dict)
    file = models.FileField(upload_to='reports/', null=True, blank=True)
    generated_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    generated_at = models.DateTimeField(auto_now_add=True)
    download_count = models.IntegerField(default=0)
    
    class Meta:
        ordering = ['-generated_at']
    
    def __str__(self):
        return f"{self.title} - {self.generated_at.strftime('%Y-%m-%d')}"