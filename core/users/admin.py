from django.contrib import admin
from django.contrib.auth import get_user_model
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

from .models import DriverDocuments, DriverProfile, PassengerProfile, Profile

User = get_user_model()
@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = (
        "id","email","phone_number","role","date_joined","updated_at"
    )
    readonly_fields = ("date_joined","updated_at")

    fieldsets = (
        (None, {"fields": ("email","phone_number","role","password")}),
        ("Permissions", {
            "fields": (
                "is_active", "is_staff", "is_superuser",
                "groups", "user_permissions",
            )
        }),
        ("Important dates", {"fields": ("last_login", "date_joined", "updated_at")}),
    )

    add_fieldsets = (
        (None, {
            "classes": ("wide",),
            "fields": (
                "email","phone_number","role","password1", "password2","is_staff","is_superuser"
            ),
        }),
    )

    search_fields = ("email", "phone_no")
    ordering = ("-date_joined",)

    def get_readonly_fields(self,request,obj=None):
        if obj:
            return self.readonly_fields + ("role",)
        return self.readonly_fields

@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ["id","user","first_name","last_name","date_of_birth","gender"]

@admin.register(DriverProfile)
class DriverProfileAdmin(admin.ModelAdmin):
    list_display = ["id","profile","is_driver_verified","total_rides_as_a_driver","rating"]

@admin.register(PassengerProfile)
class PassengerProfileAdmin(admin.ModelAdmin):
    list_display = ["id","profile","total_rides_as_a_passenger"]

@admin.register(DriverDocuments)
class DriverDocumentsAdmin(admin.ModelAdmin):
    list_display = ["id","driver_profile","file","uploaded_at"]


