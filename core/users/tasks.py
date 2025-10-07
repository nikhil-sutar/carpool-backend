from celery import shared_task
from django.conf import settings
from django.core.mail import send_mail


@shared_task
def send_welcome_email(user_email):
    print("sending email...")
    
    send_mail(
        subject = "Welcome to carpool...",
        message = "Thanks for signing up..",
        from_email = settings.DEFAULT_FROM_EMAIL,
        recipient_list = [user_email] 
    )
    print("Mail sent...")