from django.contrib.auth import get_user_model
from rest_framework import permissions

User = get_user_model()

class IsAdminOrDriverSelf(permissions.BasePermission):
    def has_permission(self, request, view):
        user = request.user
        if user.role in [User.Roles.ADMIN,User.Roles.DRIVER]:
            return True
        return False
    
    def has_object_permission(self, request, view, obj):
        user = request.user
        if user.role == User.Roles.ADMIN:
            return True
        return obj.profile.user == user
    
class IsAdminOrPassengerSelf(permissions.BasePermission):
    def has_permission(self, request, view):
        user = request.user
        if user.role in [User.Roles.ADMIN,User.Roles.PASSENGER]:
            return True
        return False
    
    def has_object_permission(self, request, view, obj):
        user = request.user
        if user.role == User.Roles.ADMIN:
            return True
        return obj.profile.user == user 
