from django.contrib import admin

from .models import Booking, Payment


# Register your models here.
@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = ['id','passenger','ride__start_time','ride','boarding_point','dropping_point','seats_booked','status']

@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ['id','booking','amount','status','transaction_id','payment_method','created_at','updated_at']