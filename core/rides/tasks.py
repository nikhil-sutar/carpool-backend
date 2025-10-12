from celery import shared_task
from django.conf import settings
from django.core.mail import send_mail
from django.db.models import F
from django.utils import timezone
from geopy.geocoders import Nominatim
from geopy.exc import GeocoderServiceError

from .models import Ride, Location

@shared_task
def send_ride_confirmation_email(user_email,ride_id):
    print(f"Sending email for ride {ride_id} to {user_email}...")
    ride = Ride.objects.get(id=ride_id)
    send_mail(
        subject = "Ride creation mail",
        message = f"Ride from {ride.source} to {ride.destination} created successfully.",
        from_email = settings.DEFAULT_FROM_EMAIL,
        recipient_list = [user_email]
    )
    print(f"Email sent for ride {ride_id}")

@shared_task
def mark_completed_rides():
    print("Marking ride status completed...")
    now = timezone.now()
    rides_to_complete = Ride.objects.filter(status=Ride.RideStatus.OPEN, end_time__lt=now)

    if not rides_to_complete.exists():
        print("No rides to mark as completed.")
        return
    
    for ride in rides_to_complete.select_related('driver__profile__driver_profile'):
        print(f"Marking ride from {ride.source} to {ride.destination} as completed")
        ride.status = "completed"
        ride.save(update_fields=['status'])

        print(f"Updating total_rides_as_a_driver for driver {ride.driver.profile.first_name}")
        driver_profile = ride.driver.profile.driver_profile
        driver_profile.total_rides_as_a_driver = F('total_rides_as_a_driver') + 1
        driver_profile.save(update_fields=['total_rides_as_a_driver'])

@shared_task
def verify_location_with_geopy(location_id):
    try:
        location = Location.objects.get(id=location_id)
        geolocator = Nominatim(user_agent='carpool_app')
        geo_location = geolocator.geocode(location.name)
        if geo_location:
            location.latitude = geo_location.latitude
            location.longitude = geo_location.longitude
            location.is_verified = True
        location.save()
    except Location.DoesNotExist:
        print("Location does not exist...")
    except GeocoderServiceError as e:
        print(e)