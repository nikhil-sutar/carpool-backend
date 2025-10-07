from django.contrib import admin

from .models import Booking


# Register your models here.
@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = ['id','passenger','ride','boarding_point','dropping_point','seats_booked','status']