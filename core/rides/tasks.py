from celery import shared_task
from django.conf import settings
from django.core.mail import send_mail
from django.db.models import Q
from django.utils import timezone

from .models import Ride


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
    rides = Ride.objects.filter(status='open', end_time__lt=now)
    for ride in rides:
        ride.status = "completed"
        ride.save()
        print(f"Trip from {ride.source} to {ride.destination} marked completed.")
       
    
    
    