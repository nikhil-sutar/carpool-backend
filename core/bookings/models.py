from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator
from django.db import models
from django.db.models import Q

from rides.models import Ride

User = get_user_model()
# Create your models here.
class Booking(models.Model):
    class BookingStatus(models.TextChoices):
        PENDING = 'pending', 'Pending'
        CONFIRMED = 'confirmed', 'Confirmed'
        CANCELLED = 'cancelled', 'Cancelled'

    passenger = models.ForeignKey(User,on_delete=models.CASCADE)
    ride = models.ForeignKey(Ride,on_delete=models.CASCADE)
    boarding_point = models.CharField(max_length=250)
    dropping_point = models.CharField(max_length=250)
    seats_booked = models.IntegerField(validators=[MinValueValidator(1)])
    status = models.CharField(choices=BookingStatus.choices,default=BookingStatus.PENDING)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields = ['passenger','ride'],
                condition = Q(status="confirmed"),
                name = "unique_active_booking_per_ride"
            )
        ]
    def __str__(self):
        return f"Trip to {self.ride.destination} of {self.passenger.profile.first_name}"
    
class Payment(models.Model):
    class PaymentStatus(models.TextChoices):
        PENDING = 'pending', 'Pending'
        SUCCESS = 'success', 'Success'
        FAILED = 'failed', 'Failed'
    booking = models.OneToOneField(Booking, on_delete=models.CASCADE,related_name="payment")
    amount = models.DecimalField(max_digits=8,decimal_places=2)
    status = models.CharField(choices=PaymentStatus.choices,default=PaymentStatus.PENDING)
    transaction_id = models.CharField(max_length=100,blank=True,null=True)
    payment_method = models.CharField(max_length=50,default='wallet')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)