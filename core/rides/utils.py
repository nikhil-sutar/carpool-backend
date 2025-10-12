from .models import Location
from .tasks import verify_location_with_geopy

def get_or_create_location_async(name):
    print("Getting location...")
    location = Location.objects.filter(name=name).first()

    if location:
        return location
    
    location = Location.objects.create(name=name)

    print("Starting celery task to verify location with geopy...")
    verify_location_with_geopy.delay(location.id)
    
    return location