from django.contrib import admin
from django.utils.html import format_html
from django.utils import timezone
from .models import Notification


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ['title', 'farmer', 'priority_badge', 'notification_type_badge', 'is_read_badge', 'created_at']
    list_filter = ['priority', 'notification_type', 'is_read', 'created_at']
    search_fields = ['title', 'message', 'farmer__username', 'farmer__email']
    readonly_fields = ['created_at', 'read_at']
    
    fieldsets = (
        ('Farmer & Type', {
            'fields': ('farmer', 'notification_type', 'priority')
        }),
        ('Content', {
            'fields': ('title', 'message')
        }),
        ('Action Button', {
            'fields': ('action_url', 'action_label'),
            'classes': ('collapse',)
        }),
        ('Source Reference', {
            'fields': ('source_type', 'source_id'),
            'classes': ('collapse',)
        }),
        ('Status', {
            'fields': ('is_read', 'read_at', 'created_at')
        }),
    )
    
    def priority_badge(self, obj):
        colors = {
            'critical': '#8B0000',
            'urgent': '#dc3545', 
            'high': '#fd7e14',
            'medium': '#ffc107',
            'low': '#28a745'
        }
        color = colors.get(obj.priority, '#6c757d')
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 10px; border-radius: 12px; font-size: 12px;">{}</span>',
            color, obj.get_priority_display()
        )
    priority_badge.short_description = 'Priority'
    
    def notification_type_badge(self, obj):
        icons = {
            'livestock': '🐄',
            'crop': '🌾',
            'weather': '🌤️',
            'admin': '📢'
        }
        icon = icons.get(obj.notification_type, '📋')
        return format_html('<span>{}</span>', f"{icon} {obj.get_notification_type_display()}")
    notification_type_badge.short_description = 'Type'
    
    def is_read_badge(self, obj):
        if obj.is_read:
            return format_html('<span style="color: green;">✓ Read</span>')
        return format_html('<span style="color: red;">● Unread</span>')
    is_read_badge.short_description = 'Status'
    
    actions = ['mark_as_read', 'mark_as_unread', 'delete_selected']
    
    def mark_as_read(self, request, queryset):
        from django.utils import timezone
        updated = queryset.update(is_read=True, read_at=timezone.now())
        self.message_user(request, f"{updated} notifications marked as read.")
    mark_as_read.short_description = "Mark selected as read"
    
    def mark_as_unread(self, request, queryset):
        updated = queryset.update(is_read=False, read_at=None)
        self.message_user(request, f"{updated} notifications marked as unread.")
    mark_as_unread.short_description = "Mark selected as unread"