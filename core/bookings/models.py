from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator
from django.db import models
from django.db.models import Q

from rides.models import Ride

User = get_user_model()
# Create your models here.
class Booking(models.Model):
    class booking_status(models.TextChoices):
        PENDING = 'pending', 'Pending'
        CONFIRMED = 'confirmed', 'Confirmed'
        CANCELLED = 'cancelled', 'Cancelled'

    passenger = models.ForeignKey(User,on_delete=models.CASCADE)
    ride = models.ForeignKey(Ride,on_delete=models.CASCADE)
    boarding_point = models.CharField(max_length=250)
    dropping_point = models.CharField(max_length=250)
    seats_booked = models.IntegerField(validators=[MinValueValidator(1)])
    status = models.CharField(choices=booking_status.choices,default=booking_status.CONFIRMED)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields = ['passenger','ride'],
                condition = Q(status="confirmed"),
                name = "unique_active_booking_per_ride"
            )
        ]
    def __str__(self):
        return f"Trip to {self.ride.destination} of {self.passenger.username}"