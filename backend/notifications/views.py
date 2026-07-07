# notifications/views.py

from rest_framework import generics, viewsets, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.decorators import action
from django.utils import timezone
from django.shortcuts import get_object_or_404
from .models import Notification
from .serializers import NotificationSerializer
from .permissions import IsFarmerUser
from admin_panel.models import Notification as AdminNotification
from admin_panel.serializers import NotificationSerializer as AdminNotificationSerializer
from .utils import (
    get_farm_alerts_unread_count,
    get_unread_count, 
    get_all_notifications, 
    get_notifications_by_type,
    mark_all_as_read,
    generate_user_alerts_and_reminders_if_needed,
    refresh_notification_priorities,
)
from .i18n import get_request_language, notification_to_dict


class NotificationViewSet(viewsets.ModelViewSet):
    """
    ViewSet for handling notifications with actions:
    - list: Get all notifications
    - retrieve: Get single notification
    - update: Update notification
    - partial_update: Partially update notification
    - destroy: Delete notification
    - mark_read: Mark as read
    - mark_all_read: Mark all as read
    - unread_count: Get unread count
    """
    permission_classes = [IsAuthenticated, IsFarmerUser]
    serializer_class = NotificationSerializer
    
    def get_queryset(self):
        """Filter notifications for the current user"""
        return Notification.objects.filter(farmer=self.request.user)
    
    def list(self, request, *args, **kwargs):
        """
        GET /api/notifications/ - List all notifications with filters
        """
        generate_user_alerts_and_reminders_if_needed(request.user)
        refresh_notification_priorities(farmer=request.user)
        
        # Get filter parameters
        notification_type = request.query_params.get('type')
        limit = int(request.query_params.get('limit', 50))
        is_read = request.query_params.get('is_read')
        is_completed = request.query_params.get('is_completed')
        
        queryset = self.get_queryset()
        
        # Apply filters
        if notification_type:
            queryset = queryset.filter(notification_type=notification_type)
        if is_read is not None:
            queryset = queryset.filter(is_read=is_read.lower() == 'true')
        if is_completed is not None:
            queryset = queryset.filter(is_completed=is_completed.lower() == 'true')
        
        # ✅ For admin/weather notifications only (exclude crop/livestock)
        # This is for the notification bell
        is_feed = request.query_params.get('feed', 'false').lower() == 'true'
        if is_feed:
            queryset = queryset.exclude(notification_type__in=['crop', 'livestock'])
        
        # Order by created_at descending
        queryset = queryset.order_by('-created_at')[:limit]
        
        lang = get_request_language(request)
        
        # ✅ Get unread count excluding farm alerts
        unread_count = get_unread_count(request.user, include_farm_alerts=False)
        
        return Response({
            'success': True,
            'lang': lang,
            'unread_count': unread_count,
            'count': queryset.count(),
            'notifications': [notification_to_dict(n, lang) for n in queryset],
        })
    
    def retrieve(self, request, *args, **kwargs):
        """
        GET /api/notifications/{id}/ - Get single notification details
        """
        instance = self.get_object()
        lang = get_request_language(request)
        
        return Response({
            'success': True,
            'notification': notification_to_dict(instance, lang),
        })
    
    def partial_update(self, request, *args, **kwargs):
        """
        PATCH /api/notifications/{id}/ - Mark notification as read/unread or completed/uncompleted
        """
        instance = self.get_object()
        
        # Handle is_read toggle
        if 'is_read' in request.data:
            if request.data['is_read']:
                instance.mark_as_read()
            else:
                instance.mark_as_unread()
        
        # Handle is_completed toggle
        if 'is_completed' in request.data:
            if request.data['is_completed']:
                instance.mark_as_completed()
            else:
                instance.mark_as_uncompleted()
        
        # If neither is_read nor is_completed provided, default to mark as read
        if 'is_read' not in request.data and 'is_completed' not in request.data:
            instance.mark_as_read()
        
        return Response({
            'success': True,
            'is_read': instance.is_read,
            'is_completed': instance.is_completed,
            'read_at': instance.read_at.isoformat() if instance.read_at else None,
            'completed_at': instance.completed_at.isoformat() if instance.completed_at else None
        })
    
    def destroy(self, request, *args, **kwargs):
        """
        DELETE /api/notifications/{id}/ - Delete a notification
        """
        instance = self.get_object()
        instance.delete()
        return Response({
            'success': True,
            'message': 'Notification deleted successfully'
        }, status=status.HTTP_200_OK)
    
    @action(detail=True, methods=['post'], url_path='mark-read')
    def mark_read(self, request, pk=None):
        """
        POST /api/notifications/{id}/mark_read/ - Mark notification as read
        """
        instance = self.get_object()
        instance.mark_as_read()
        
        return Response({
            'success': True,
            'message': 'Notification marked as read',
            'is_read': instance.is_read,
            'read_at': instance.read_at.isoformat() if instance.read_at else None,
            'unread_count': get_unread_count(request.user, include_farm_alerts=False)
        })
    
    @action(detail=True, methods=['post'], url_path='mark-unread')
    def mark_unread(self, request, pk=None):
        """
        POST /api/notifications/{id}/mark_unread/ - Mark notification as unread
        """
        instance = self.get_object()
        instance.mark_as_unread()
        
        return Response({
            'success': True,
            'message': 'Notification marked as unread',
            'is_read': instance.is_read,
            'unread_count': get_unread_count(request.user, include_farm_alerts=False)
        })
    
    @action(detail=True, methods=['post'], url_path='complete')
    def complete(self, request, pk=None):
        """
        POST /api/notifications/{id}/complete/ - Mark notification as completed
        """
        instance = self.get_object()
        instance.mark_as_completed()
        
        return Response({
            'success': True,
            'message': 'Notification marked as completed',
            'is_completed': instance.is_completed,
            'completed_at': instance.completed_at.isoformat() if instance.completed_at else None,
            'unread_count': get_unread_count(request.user, include_farm_alerts=False)
        })
    
    @action(detail=True, methods=['post'], url_path='uncomplete')
    def uncomplete(self, request, pk=None):
        """
        POST /api/notifications/{id}/uncomplete/ - Mark notification as uncompleted
        """
        instance = self.get_object()
        instance.mark_as_uncompleted()
        
        return Response({
            'success': True,
            'message': 'Notification marked as uncompleted',
            'is_completed': instance.is_completed,
            'unread_count': get_unread_count(request.user, include_farm_alerts=False)
        })
    
    @action(detail=False, methods=['post'], url_path='mark-all-read')
    def mark_all_read(self, request):
        """
        POST /api/notifications/mark_all_read/ - Mark all notifications as read
        """
        # ✅ Only mark admin/weather as read (not farm alerts)
        count = mark_all_as_read(request.user, include_farm_alerts=False)
        
        return Response({
            'success': True,
            'message': f'{count} notifications marked as read',
            'marked_count': count,
            'unread_count': get_unread_count(request.user, include_farm_alerts=False)
        })
    
    @action(detail=False, methods=['get'], url_path='unread-count')
    def unread_count(self, request):
        """
        GET /api/notifications/unread_count/ - Get unread notification count
        """
        # ✅ Only count admin/weather notifications
        return Response({
            'success': True,
            'unread_count': get_unread_count(request.user, include_farm_alerts=False)
        })
    
    @action(detail=False, methods=['get'], url_path='farm-alerts')
    def farm_alerts(self, request):
        """
        GET /api/notifications/farm_alerts/ - Get farm alerts (crop + livestock)
        """
        status_filter = request.query_params.get('status', 'active')
        
        generate_user_alerts_and_reminders_if_needed(request.user)
        refresh_notification_priorities(farmer=request.user)
        
        queryset = self.get_queryset()
        
        # Filter by status
        if status_filter == 'active':
            queryset = queryset.filter(is_completed=False)
        elif status_filter == 'completed':
            queryset = queryset.filter(is_completed=True)
        
        lang = get_request_language(request)
        
        crop_alerts = [
            notification_to_dict(n, lang)
            for n in queryset.filter(notification_type='crop')
        ]
        livestock_alerts = [
            notification_to_dict(n, lang)
            for n in queryset.filter(notification_type='livestock')
        ]
        
        # ✅ Also return unread count for farm alerts (for dashboard badge)
        farm_alerts_unread = get_farm_alerts_unread_count(request.user)
        
        return Response({
            'success': True,
            'lang': lang,
            'crop': crop_alerts,
            'livestock': livestock_alerts,
            'farm_alerts_unread': farm_alerts_unread,  # ✅ For dashboard badge
        })

class NotificationListCreateView(generics.ListCreateAPIView):
    """
    GET /api/admin/notifications/ - List all notifications (admin)
    POST /api/admin/notifications/ - Create a new notification (admin)
    """
    permission_classes = [IsAuthenticated, IsFarmerUser]
    serializer_class = AdminNotificationSerializer
    
    def get_queryset(self):
        """Return all notifications (admin view)"""
        return AdminNotification.objects.all().order_by('-sent_at')
    
    def list(self, request, *args, **kwargs):
        """
        GET /api/admin/notifications/ - List all notifications with pagination
        """
        queryset = self.get_queryset()
        
        # Apply filters
        notification_type = request.query_params.get('type')
        if notification_type:
            queryset = queryset.filter(notification_type=notification_type)
        
        # Pagination
        page = int(request.query_params.get('page', 1))
        page_size = int(request.query_params.get('page_size', 20))
        start = (page - 1) * page_size
        end = start + page_size
        
        total = queryset.count()
        notifications_page = queryset[start:end]
        
        serializer = self.get_serializer(notifications_page, many=True)
        
        return Response({
            'notifications': serializer.data,
            'pagination': {
                'total': total,
                'page': page,
                'page_size': page_size,
                'total_pages': (total + page_size - 1) // page_size
            }
        })


class AdminNotificationDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    GET /api/admin/notifications/{id}/ - Get notification details (admin)
    PUT /api/admin/notifications/{id}/ - Update notification (admin)
    DELETE /api/admin/notifications/{id}/ - Delete notification (admin)
    """
    permission_classes = [IsAuthenticated, IsFarmerUser]
    serializer_class = AdminNotificationSerializer
    queryset = AdminNotification.objects.all()
    lookup_field = 'id'
    
    def retrieve(self, request, *args, **kwargs):
        """Get single notification details (read-only for sent notifications)"""
        instance = self.get_object()
        
        # Check if notification is already sent
        if instance.sent_at:
            return Response({
                'warning': 'This notification has already been sent and is read-only',
                'notification': self.get_serializer(instance).data
            })
        
        return Response(self.get_serializer(instance).data)
    
    def update(self, request, *args, **kwargs):
        """Prevent editing of sent notifications"""
        instance = self.get_object()
        
        if instance.sent_at:
            return Response({
                'error': 'Cannot edit a notification that has already been sent'
            }, status=status.HTTP_403_FORBIDDEN)
        
        return super().update(request, *args, **kwargs)
    
    def partial_update(self, request, *args, **kwargs):
        """Prevent partial editing of sent notifications"""
        instance = self.get_object()
        
        if instance.sent_at:
            return Response({
                'error': 'Cannot edit a notification that has already been sent'
            }, status=status.HTTP_403_FORBIDDEN)
        
        return super().partial_update(request, *args, **kwargs)


class AdminMarkAllReadView(generics.GenericAPIView):
    """
    POST /api/admin/notifications/mark-all-read/ - Mark all notifications as read for all farmers (admin)
    """
    permission_classes = [IsAuthenticated, IsFarmerUser]
    
    def post(self, request):
        now = timezone.now()
        notifications = Notification.objects.filter(is_read=False)
        count = notifications.count()
        notifications.update(is_read=True, read_at=now)
        
        return Response({
            'success': True,
            'message': f'Marked {count} notifications as read for all farmers',
            'count': count
        })