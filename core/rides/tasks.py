from celery import shared_task
from django.conf import settings
from django.core.mail import send_mail
from django.db import transaction
from django.db.models import F, Count
from django.utils import timezone
from geopy.geocoders import Nominatim
from geopy.exc import GeocoderServiceError

from .models import Ride, Location
from bookings.models import Booking
from users.models import DriverProfile, PassengerProfile
import logging

logger = logging.getLogger(__name__)

@shared_task
def send_ride_confirmation_email(user_email,ride_id):
    logger.info(f"Sending email for ride {ride_id} to {user_email}...")
    ride = Ride.objects.get(id=ride_id)
    send_mail(
        subject = "Ride creation mail",
        message = f"Ride from {ride.source} to {ride.destination} created successfully.",
        from_email = settings.DEFAULT_FROM_EMAIL,
        recipient_list = [user_email]
    )
    logger.info(f"Email sent for ride {ride_id}")

@shared_task
def mark_completed_rides():
    logger.info("Marking ride status completed...")
    now = timezone.now()
    rides_to_complete = Ride.objects.filter(status=Ride.RideStatus.OPEN, end_time__lt=now)

    if not rides_to_complete.exists():
        logger.info("No rides to mark as completed.")
        return
    ride_ids = list(rides_to_complete.values_list('id',flat=True))
    with transaction.atomic():
        updated = rides_to_complete.update(status=Ride.RideStatus.COMPLETED)
        logger.info(f"Marked {updated} rides as completed.")

        driver_counts = Ride.objects.filter(id__in=ride_ids).values(
            'driver__profile__driver_profile'
        ).annotate(
            count=Count('id')
        ).values_list('driver__profile__driver_profile','count')
        logger.info(f"Driver counts:{driver_counts}")
        for profile_id, count in driver_counts:
            logger.info(f"Updating Driver Profile_id:{profile_id} with count:{count}")
            DriverProfile.objects.filter(id=profile_id).update(
                total_rides_as_a_driver = F('total_rides_as_a_driver') + count
            )

        passenger_counts = Booking.objects.filter(
            ride__in = ride_ids
        ).values(
            'passenger__profile__passenger_profile'
        ).annotate(
            count = Count('id')
        ).values_list('passenger__profile__passenger_profile','count')
        logger.info(f"Passenger counts:{passenger_counts}")
        for profile_id, count in passenger_counts:
            logger.info(f"Updating Passenger Profile_id:{profile_id} with count:{count}")
            PassengerProfile.objects.filter(id=profile_id).update(
                total_rides_as_a_passenger = F('total_rides_as_a_passenger') + count
            )
    logger.info("Completed marking rides and updating profiles efficiently.")

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
        logger.info("Location does not exist...")
    except GeocoderServiceError as e:
        logger.info(e)