from django.db import transaction
from django.db.models import F
from rest_framework import serializers

from rides.models import Ride

from .models import Booking


class BookingSerializer(serializers.ModelSerializer):
    passenger_display = serializers.SerializerMethodField()
    ride_display = serializers.SerializerMethodField()

    def get_passenger_display(self,obj):
        return f"{obj.passenger.profile.first_name} {obj.passenger.profile.last_name}"
    
    def get_ride_display(self,obj):
        return f"Trip from {obj.ride.source} to {obj.ride.destination}"
    
    class Meta:
        model = Booking
        fields = ['id','passenger','passenger_display','ride','ride_display','boarding_point','dropping_point','seats_booked','status']
        read_only_fields = ['id','passenger','passenger_display','ride_display','status']

    def validate_seats_booked(self,value):
        if value <= 0:
            raise serializers.ValidationError("You must book at least 1 seat.")
        return value
    
    def create(self, validated_data):
        ride_id = validated_data.get('ride').id
        booked_seats = validated_data.get('seats_booked')
        with transaction.atomic():
            # Locks ride row to avoid race condition
            ride = Ride.objects.select_for_update().get(id=ride_id)
            if ride.seats_available < booked_seats:
                raise serializers.ValidationError("Not enough seats available.")
            
            booking = Booking.objects.create(**validated_data)
            booking.save()

            ride.seats_booked = F('seats_booked') + booked_seats
            ride.save()
        return booking
    
    