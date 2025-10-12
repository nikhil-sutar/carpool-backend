from django.db import transaction
from django.db.models import F
from django.utils.timezone import localtime
from rest_framework import serializers

from rides.models import Ride

from .models import Booking, Payment

class BookingSerializer(serializers.ModelSerializer):
    passenger_display = serializers.SerializerMethodField(read_only=True)
    ride_display = serializers.SerializerMethodField(read_only=True)
    date = serializers.SerializerMethodField(read_only=True)
    time = serializers.SerializerMethodField(read_only=True)

    def get_passenger_display(self,obj):
        return f"{obj.passenger.profile.first_name} {obj.passenger.profile.last_name}"
    
    def get_ride_display(self,obj):
        return f"Trip from {obj.ride.source} to {obj.ride.destination}"
    
    def get_date(self,obj):
        return localtime(obj.ride.start_time).date()
    
    def get_time(self,obj):
        return localtime(obj.ride.start_time).time().strftime("%I:%M %p")
    
    class Meta:
        model = Booking
        fields = ['id','passenger','passenger_display','ride','ride_display','date','time','boarding_point','dropping_point','seats_booked','status']
        read_only_fields = ['id','passenger','status']

    def validate_seats_booked(self,value):
        if value <= 0:
            raise serializers.ValidationError("You must book at least 1 seat.")
        return value
    def validate(self, attrs):
        boarding_point = attrs.get('boarding_point')
        dropping_point = attrs.get('dropping_point')
        ride = attrs.get('ride')
        if boarding_point not in ride.boarding_points:
            raise serializers.ValidationError("Please give correct boarding point.")
        if dropping_point not in ride.dropping_points:
            raise serializers.ValidationError("Please give correct dropping point.")
        return attrs
    
    def create(self, validated_data):
        ride_id = validated_data.get('ride').id
        booked_seats = validated_data.get('seats_booked')
        with transaction.atomic():
            # Locks ride row to avoid race condition
            ride = Ride.objects.select_for_update().get(id=ride_id)
            if ride.seats_available < booked_seats:
                raise serializers.ValidationError("Not enough seats available.")
            
            booking = Booking.objects.create(**validated_data)

            # Create pending payment linked to this booking
            payment = Payment.objects.create(
                booking = booking,
                amount = ride.fare,
                status = Payment.PaymentStatus.PENDING
            )

            # Simulate payment success
            # Later replace this with real gateway logic
            payment.status = Payment.PaymentStatus.SUCCESS
            payment.save()

            # Confirm booking only after payment success
            if payment.status == Payment.PaymentStatus.SUCCESS:
                booking.status = Booking.BookingStatus.CONFIRMED
                booking.save()
                ride.seats_booked = F('seats_booked') + booked_seats
                ride.save()
            else:
                booking.status = Booking.BookingStatus.CANCELLED
                booking.save()
        return booking
    
class PaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Payment
        fields = ['id','booking','amount','status','transaction_id','payment_method','created_at','updated_at'] 
        read_only_fields = ['created_at','updated_at']
