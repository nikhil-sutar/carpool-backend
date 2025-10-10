from django.contrib.auth import get_user_model
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.utils import timezone

User = get_user_model()
# Create your models here.
class VehicleMake(models.Model):
    name = models.CharField(max_length=100, unique=True)
    def __str__(self):
        return self.name

class VehicleModel(models.Model):
    make = models.ForeignKey(VehicleMake, on_delete=models.PROTECT, related_name='models')
    name = models.CharField(max_length=100)

    class Meta:
        unique_together = ("make","name")  #prevent duplicates like Honda City twice

    def __str__(self):
        return f"{self.make.name} {self.name}"

class Vehicle(models.Model):
    owner = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="vehicles"
    )
    model = models.ForeignKey(VehicleModel,on_delete=models.PROTECT,related_name='vehicles')
    registration_number = models.CharField(
        max_length=15,
        unique=True,
        help_text="Official license plate, e.g. MH09GR9392"
    )
    seats = models.PositiveSmallIntegerField(default=4)

    color = models.CharField(max_length=50, blank=True, null=True)
    manufacture_year = models.PositiveSmallIntegerField(
        validators = [
            MinValueValidator(2005),
            MaxValueValidator(timezone.now().year)
        ],
        blank=True, null=True
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.owner.profile.first_name}'s {self.model.make.name} {self.model.name} ({self.registration_number})"

class Ride(models.Model):
    class RideStatus(models.TextChoices):
        OPEN = 'open','Open'
        FULL = 'full','Full'
        COMPLETED = 'completed','Completed'
        CANCELLED = 'cancelled','Cancelled'
    
    driver = models.ForeignKey(User,on_delete=models.PROTECT,related_name='rides')
    vehicle = models.ForeignKey(Vehicle,on_delete=models.PROTECT,related_name='rides')
    source = models.CharField(max_length=250)
    destination = models.CharField(max_length=250)
    boarding_points = models.JSONField(default=list)
    dropping_points = models.JSONField(default=list)
    fare = models.DecimalField(max_digits=8,decimal_places=2)
    seats_offered = models.PositiveSmallIntegerField()
    seats_booked = models.PositiveSmallIntegerField(default=0)
    seats_available = models.PositiveSmallIntegerField(null=True,blank=True)
    status = models.CharField(max_length=10,choices=RideStatus.choices,default=RideStatus.OPEN)
    start_time = models.DateTimeField()
    end_time = models.DateTimeField(blank=True,null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def save(self,*args, **kwargs):
        if not self.pk:
            self.seats_available = self.seats_offered
        else:
            self.seats_available = self.seats_offered - self.seats_booked
        return super().save(*args, **kwargs)
    def __str__(self):
        return f"{self.driver.profile.first_name}'s from {self.source} to {self.destination} on {self.start_time}"
