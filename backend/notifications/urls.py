# notifications/urls.py

from django.urls import path
from rest_framework.routers import DefaultRouter
from . import views

# Router handles standard CRUD: list, retrieve, create, update, partial_update, destroy
# and the router-generated action URLs like mark_all_read, unread_count etc.
# config/urls.py mounts this at 'api/notifications/', so use empty prefix.
router = DefaultRouter()
router.register(r'', views.NotificationViewSet, basename='notification')

# Explicit hyphenated URL aliases matching what the frontend calls
# The DRF router generates underscore versions; these add hyphen aliases
hyphen_urlpatterns = [
    path('farm-alerts/', views.NotificationViewSet.as_view({'get': 'farm_alerts'}), name='notification-farm-alerts-hyphen'),
    path('unread-count/', views.NotificationViewSet.as_view({'get': 'unread_count'}), name='notification-unread-count-hyphen'),
    path('mark-all-read/', views.NotificationViewSet.as_view({'post': 'mark_all_read'}), name='notification-mark-all-read-hyphen'),
    path('<int:pk>/mark-read/', views.NotificationViewSet.as_view({'post': 'mark_read'}), name='notification-mark-read-hyphen'),
    path('<int:pk>/mark-unread/', views.NotificationViewSet.as_view({'post': 'mark_unread'}), name='notification-mark-unread-hyphen'),
    path('<int:pk>/complete/', views.NotificationViewSet.as_view({'post': 'complete'}), name='notification-complete-hyphen'),
    path('<int:pk>/uncomplete/', views.NotificationViewSet.as_view({'post': 'uncomplete'}), name='notification-uncomplete-hyphen'),
]

# Admin notification URLs
admin_urlpatterns = [
    path('admin/notifications/', views.NotificationListCreateView.as_view(), name='admin-notification-list'),
    path('admin/notifications/<int:id>/', views.AdminNotificationDetailView.as_view(), name='admin-notification-detail'),
    path('admin/notifications/mark-all-read/', views.AdminMarkAllReadView.as_view(), name='admin-mark-all-read'),
]

# hyphen_urlpatterns MUST come before router.urls so they take precedence
urlpatterns = hyphen_urlpatterns + router.urls + admin_urlpatterns