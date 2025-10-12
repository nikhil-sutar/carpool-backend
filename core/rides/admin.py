from django.contrib import admin

from .models import Ride, Vehicle, VehicleMake, VehicleModel, Location

# Register your models here.

@admin.register(VehicleMake)
class VehicleMakeAdmin(admin.ModelAdmin):
    list_display = ['id','name']

@admin.register(VehicleModel)
class VehicleModelAdmin(admin.ModelAdmin):
    list_display = ['id','make','name']

@admin.register(Vehicle)
class VehicleAdmin(admin.ModelAdmin):
    list_display = ['id','owner','model','registration_number','seats','color','manufacture_year']

@admin.register(Ride)
class RideAdmin(admin.ModelAdmin):
    list_display = ['id','driver','vehicle','source','destination','fare','seats_offered','seats_booked','seats_available','status','start_time','end_time']

@admin.register(Location)
class LocationAdmin(admin.ModelAdmin):
    list_display = ['id','name','latitude','longitude','is_verified']


