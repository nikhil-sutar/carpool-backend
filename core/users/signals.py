from django.contrib.auth import get_user_model
from django.db.models.signals import post_save
from django.dispatch import receiver

from .models import DriverProfile, PassengerProfile, Profile
from .tasks import send_welcome_email

User = get_user_model()

@receiver(post_save,sender=User)
def create_user_profile(sender,instance,created,**kwargs):
    if created:
        profile = Profile.objects.create(user=instance)
        if instance.role == 'driver':
            DriverProfile.objects.create(profile=profile)
        elif instance.role == 'passenger':
            PassengerProfile.objects.create(profile=profile)

        send_welcome_email.delay(instance.email)


