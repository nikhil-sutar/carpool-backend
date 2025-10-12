from django.contrib.auth import get_user_model
from django.utils import timezone
from django.utils.dateparse import parse_datetime 
from django.utils.timezone import localtime
from rest_framework import serializers

from users.models import DriverProfile
from users.serializers import UserSerializer

from .models import Ride, Vehicle, VehicleMake, VehicleModel, Location
from .utils import get_or_create_location_async
from bookings.models import Booking

User = get_user_model()

class PublicDriverSerializer(serializers.ModelSerializer):
    name = serializers.SerializerMethodField()

    def get_name(self,obj):
        return f"{obj.profile.first_name} {obj.profile.last_name}"
    
    class Meta:
        model = DriverProfile
        fields = ['profile','name','is_driver_verified','total_rides_as_a_driver','rating','updated_at']

class PublicVehicleSerializer(serializers.ModelSerializer):
    model_name = serializers.SerializerMethodField()
    class Meta:
        model = Vehicle
        fields = ['model_name','color']

    def get_model_name(self,obj):
        return f"{obj.model.make.name} {obj.model.name}"

class RideSerializer(serializers.ModelSerializer):
    driver = PublicDriverSerializer(read_only=True)
    vehicle = PublicVehicleSerializer(read_only=True)
    vehicle_id = serializers.PrimaryKeyRelatedField(
        source='vehicle',
        queryset=Vehicle.objects.all(),
        write_only=True
    )
    source = serializers.CharField()
    destination = serializers.CharField()
    status_display = serializers.CharField(source='get_status_display',read_only=True)
    duration = serializers.SerializerMethodField()
    duration_display = serializers.SerializerMethodField()
    # available_seats = serializers.SerializerMethodField(read_only=True)
    def get_duration(self,obj):
        start_time = obj.start_time
        end_time = obj.end_time
        delta = abs(end_time - start_time)
        return delta.total_seconds()
    
    def get_duration_display(self,obj):
        delta = abs(obj.end_time - obj.start_time)
        hours,remainder = divmod(delta.total_seconds(),3600) #return delta//3600 & delta % 3600
        minutes, _ = divmod(remainder,60)
        if minutes == 0:
            return f"{int(hours)}h"
        return f"{int(hours)}h {int(minutes)}m"

    class Meta:
        model = Ride
        fields = ['id','driver','vehicle','vehicle_id','source','destination','boarding_points','dropping_points','fare','seats_offered','seats_booked','seats_available','status','status_display','start_time','end_time','duration','duration_display','created_at','updated_at']
        read_only_fields = ['driver','seats_booked','seats_available','status','created_at','updated_at','duration','duration_display']
    
    def validate_vehicle_id(self,value):
        vehicle = value
        # print("1)Vehicle:",vehicle)
        user = self.context['request'].user
        if user != vehicle.owner:
            raise serializers.ValidationError("Please specify the ID of your own vehicle.")
        return value
    
    def validate_fare(self,value):
        if value < 50:
            raise serializers.ValidationError("Fare must be at least 10 INR.")
        elif value > 10000:
            raise serializers.ValidationError("Fare seems unreasonably high.")
        return value

    def validate_start_time(self,value):
        request = self.context['request']
        user = request.user
        end_time = self.initial_data.get('end_time')
        if not end_time:
            raise serializers.ValidationError("End time is required to validate start time")
        if isinstance(end_time,str):
            end_time = parse_datetime(end_time)

        if value < localtime():
            raise serializers.ValidationError("Start time should be greater than current time")
        
        overlapping_ride = Ride.objects.filter(
            driver = user,
            start_time__lt = end_time,
            end_time__gt = value,
            status__in = [Ride.RideStatus.OPEN,Ride.RideStatus.FULL]
        ).exclude(id = self.instance.id if self.instance else None)

        if overlapping_ride.exists():
            raise serializers.ValidationError("You already have another ride scheduled during this time period.")
    
        return value
    
    def validate(self, attrs):
        vehicle = attrs.get('vehicle')
        seats_offered = attrs.get('seats_offered')
        start_time = attrs.get('start_time')
        end_time = attrs.get('end_time')
        if seats_offered == 0 or seats_offered > vehicle.seats-1:
            raise serializers.ValidationError(f"Offered seats should be in range 1-{vehicle.seats-1}")

        if end_time < start_time:
            raise serializers.ValidationError("End time should be after start time")

        return attrs
    
    def create(self, validated_data):
        source_name = validated_data.pop('source')
        destination_name = validated_data.pop('destination')

        source_obj = get_or_create_location_async(source_name)
        destination_obj = get_or_create_location_async(destination_name)
        validated_data['source'] = source_obj
        validated_data['destination'] = destination_obj
        ride = Ride.objects.create(**validated_data)
        return ride

    def update(self, instance, validated_data):
        if instance.status != Ride.RideStatus.OPEN:
            for field in ['vehicle','fare','seats_offered','start_time']:
                if field in validated_data:
                    raise serializers.ValidationError(f"{field} cannot be updated once ride is active.")
        return super().update(instance, validated_data)

class VehicleMakeSerializer(serializers.ModelSerializer):
    class Meta:
        model = VehicleMake
        fields = ['id','name']

class VehicleModelSerializer(serializers.ModelSerializer):
    make_display = serializers.SerializerMethodField(read_only=True)

    def get_make_display(self,obj):
        return f"{obj.make.name}"
    
    class Meta:
        model = VehicleModel
        fields = ['id','make','make_display','name']

class VehicleSerializer(serializers.ModelSerializer):
    owner_display = serializers.SerializerMethodField(read_only=True)
    model_display = serializers.SerializerMethodField(read_only=True)

    def get_owner_display(self,obj):
        return f"{obj.owner.email}"
    def get_model_display(self,obj):
        return f"{obj.model.make.name} {obj.model.name}"
    class Meta:
        model = Vehicle
        fields = ['owner','owner_display','model','model_display','registration_number','seats','color','manufacture_year']
        read_only_fields = ['owner','owner_display','model_display']
    
    def validate_seats(self,value):
        if value > 7:
            raise serializers.ValidationError("Passenger vehicle can't have more than 7 seats.")
        return value
    
    def validate_manufacture_year(self,value):
        print(type(value))
        if int(value) > timezone.now().year:
            raise serializers.ValidationError("Year can't be greater than current year.")
        return value

class BookingsDetailsSerialzer(serializers.Serializer):
    trip = serializers.SerializerMethodField(read_only=True)
    date = serializers.SerializerMethodField(read_only=True)
    time = serializers.SerializerMethodField(read_only=True)
    seats_booked = serializers.SerializerMethodField(read_only=True)
    passenger_details = serializers.SerializerMethodField(read_only=True)

    def get_trip(self,obj):
        return f"Trip from {obj.source} to {obj.destination}"
    
    def get_date(self,obj):
        return localtime(obj.start_time.date())

    def get_time(self,obj):
        return localtime(obj.start_time.time().strftime("%I:%M %p"))
    
    def get_seats_booked(self,obj):
        return obj.seats_booked
    
    def get_passenger_details(self,obj):
        bookings = Booking.objects.filter(ride=obj.id).select_related('passenger__profile')
        data = [{
            'passenger':booking.passenger.profile.first_name,
            'boarding_point': booking.boarding_point,
            'dropping_point': booking.dropping_point,
            'seats_booked':booking.seats_booked,
            'contact':booking.passenger.phone_number
        } for booking in bookings]

        return data