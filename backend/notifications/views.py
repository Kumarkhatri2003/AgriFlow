from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from django.utils import timezone
from .models import Notification
from .utils import (
    get_unread_count, 
    get_all_notifications, 
    get_notifications_by_type,
    mark_all_as_read,
    generate_user_alerts_and_reminders_if_needed
)
from .i18n import get_request_language, notification_to_dict


class NotificationListView(APIView):
    """GET /api/notifications/ - Get all notifications for logged-in farmer"""
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        # Automatically generate notifications for today if needed
        generate_user_alerts_and_reminders_if_needed(request.user)
        
        # Get filter parameters
        notification_type = request.query_params.get('type')
        limit = int(request.query_params.get('limit', 50))
        
        lang = get_request_language(request)

        if notification_type:
            notifications = get_notifications_by_type(request.user, notification_type, limit)
        else:
            notifications = get_all_notifications(request.user, limit)
        
        return Response({
            'success': True,
            'lang': lang,
            'unread_count': get_unread_count(request.user),
            'count': len(notifications),
            'notifications': [notification_to_dict(n, lang) for n in notifications],
        })
 
 
class NotificationDetailView(APIView):
    """GET, PATCH, DELETE /api/notifications/{id}/"""
    permission_classes = [IsAuthenticated]
    
    def get(self, request, notification_id):
        """Get single notification details"""
        try:
            notif = Notification.objects.get(id=notification_id, farmer=request.user)
            lang = get_request_language(request)
            return Response({
                'success': True,
                'notification': notification_to_dict(notif, lang),
            })
        except Notification.DoesNotExist:
            return Response({'success': False, 'error': 'Notification not found'}, status=404)
     
    def patch(self, request, notification_id):
        """Mark notification as read/unread or completed/uncompleted"""
        try:
            notif = Notification.objects.get(id=notification_id, farmer=request.user)
            
            # Toggle or set based on request
            if 'is_completed' in request.data:
                if request.data['is_completed']:
                    notif.mark_as_completed()
                else:
                    notif.mark_as_uncompleted()
            
            if 'is_read' in request.data:
                if request.data['is_read']:
                    notif.mark_as_read()
                else:
                    notif.mark_as_unread()
            elif 'is_completed' not in request.data:
                # Default: mark as read
                notif.mark_as_read()
            
            return Response({
                'success': True, 
                'is_read': notif.is_read,
                'is_completed': notif.is_completed,
                'completed_at': notif.completed_at.isoformat() if notif.completed_at else None
            })
        except Notification.DoesNotExist:
            return Response({'success': False, 'error': 'Notification not found'}, status=404)
    
    def delete(self, request, notification_id):
        """Delete a notification"""
        try:
            notif = Notification.objects.get(id=notification_id, farmer=request.user)
            notif.delete()
            return Response({'success': True, 'message': 'Notification deleted'})
        except Notification.DoesNotExist:
            return Response({'success': False, 'error': 'Notification not found'}, status=404)


class MarkAllReadView(APIView):
    """PATCH /api/notifications/mark-all-read/ - Mark all notifications as read"""
    permission_classes = [IsAuthenticated]
    
    def patch(self, request):
        count = mark_all_as_read(request.user)
        return Response({
            'success': True, 
            'message': f'{count} notifications marked as read',
            'marked_count': count
        })


class UnreadCountView(APIView):
    """GET /api/notifications/unread-count/ - Get unread notification count"""
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        return Response({
            'success': True,
            'unread_count': get_unread_count(request.user)
        })