from celery import shared_task
from django.conf import settings
from django.core.mail import send_mail

from .models import Booking


@shared_task
def send_booking_confirmation_email(passenger_email,booking_id):
    booking = Booking.objects.get(id=booking_id)
    send_mail(
        subject = "Booking confirmation mail",
        message = f"Your booking from {booking.boarding_point} to {booking.dropping_point} has been confirmed",
        from_email = settings.DEFAULT_FROM_EMAIL,
        recipient_list = [passenger_email]
    )
    print(f"Booking confirmation mail from {booking.boarding_point} to {booking.dropping_point} sent to {passenger_email} successfully!")

@shared_task
def send_booking_cancellation_email(passenger_email,booking_id):
    booking = Booking.objects.get(id=booking_id)
    send_mail(
        subject = "Booking cancellation mail",
        message = f"Your booking from {booking.boarding_point} to {booking.dropping_point} has been cancelled.",
        from_email = settings.DEFAULT_FROM_EMAIL,
        recipient_list = [passenger_email]
    )
    print(f"Booking cancelled mail for ride from {booking.boarding_point} to {booking.dropping_point} sent to {passenger_email} successfully!")