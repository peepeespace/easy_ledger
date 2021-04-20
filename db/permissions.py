from rest_framework import permissions

from user.models import User


class IsOwner(permissions.BasePermission):
    """
    Custom permission to only allow owners of an object to edit it.
    """
    def has_permission(self, request, view):
        user = User.objects.filter(email=request.user).first()
        return user and user.is_authenticated

    def has_object_permission(self, request, view, obj):
        return obj.user == request.user