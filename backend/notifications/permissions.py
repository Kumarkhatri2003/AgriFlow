# notifications/permissions.py

from rest_framework import permissions


class IsFarmerUser(permissions.BasePermission):
    """
    Custom permission to only allow farmer users to access the view.
    """
    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated and request.user.is_farmer