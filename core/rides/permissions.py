from django.contrib.auth import get_user_model
from rest_framework import permissions

from users.models import DriverProfile

User = get_user_model()

class IsDriver(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user.role == User.Roles.DRIVER
    
    def has_object_permission(self, request, view, obj):
        return obj.driver == request.user

class IsDriverVerified(permissions.BasePermission):
    def has_permission(self, request, view):
        print("Checking permission...")
        user = request.user
        if user.role == User.Roles.DRIVER:
            driver = DriverProfile.objects.get(profile = user.id)
            if driver.is_driver_verified:
                print("User has permission to access this endpoint..")
            else:
                print("Access denied...")
            return driver.is_driver_verified
        else:
            return False
    def has_object_permission(self, request, view, obj):
        print("Checking object level permission...")
        return obj.driver == request.user
