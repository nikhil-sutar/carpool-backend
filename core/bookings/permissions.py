from django.contrib.auth import get_user_model
from rest_framework import permissions

from users.models import PassengerProfile

User = get_user_model()
class IsPassenger(permissions.BasePermission):
    def has_permission(self, request, view):
        print("Checking view level permission...")
        user = request.user
        if user.role == User.Roles.PASSENGER:
            return True
        return False
    
    def has_object_permission(self, request, view, obj):
        print(f"Checking object permissions... obj.passenger={obj.passenger}, user={request.user}")
        user = request.user
        if obj.passenger == user:
            return True
        return False