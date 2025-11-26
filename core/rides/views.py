import os
from django.shortcuts import render
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAdminUser, IsAuthenticated
from rest_framework.response import Response
from rest_framework.filters import SearchFilter

from .filters import RideFilter
from .models import Ride, Vehicle, VehicleMake, VehicleModel
from .permissions import IsDriver, IsDriverVerified
from .serializers import (RideSerializer, VehicleMakeSerializer,
                          VehicleModelSerializer, VehicleSerializer,
                          BookingsDetailsSerialzer)
from .tasks import send_ride_confirmation_email
from bookings.models import Booking

# Create your views here.

class RideViewset(viewsets.ModelViewSet):
    queryset = Ride.objects.all()
    serializer_class = RideSerializer
    filterset_class = RideFilter
    search_fields = ['source','destination']
    def get_queryset(self):
        qs = Ride.objects.select_related('driver__profile','vehicle__model__make')
        user = self.request.user
        if self.action in ['update','partial_update','create','destroy','bookings_details']:
            qs = qs.filter(driver=user)
            return qs
        return qs.filter(status=Ride.RideStatus.OPEN)
    
    def get_permissions(self):
        print("In get permission",self.action)
        if self.action in ['create','update','destroy','partial_update','bookings_details']:
            permissions = [IsAuthenticated,IsDriverVerified]
        else:
            permissions = [IsAuthenticated]
        return [permission() for permission in permissions]

    def perform_create(self, serializer):
        user = self.request.user
        ride = serializer.save(driver=user)
        print(f"Ride created with id {ride.id}. Starting email task in backgorund. ")
        send_ride_confirmation_email.delay(
            user_email = user.email,
            ride_id = ride.id
        )

    # Here POST is used to make API clearer by telling its just not a field update but an action or command to server
    @action(detail=True,methods=['POST'])
    def cancel(self,request,pk=None):
        ride = self.get_object()
        if ride.driver != request.user:
            return Response({"error":"Not your ride"},status=status.HTTP_403_FORBIDDEN)
        elif ride.status != Ride.RideStatus.OPEN:
            return Response({"error":"Ride is not active."}, status=status.HTTP_400_BAD_REQUEST)
        ride.status = Ride.RideStatus.CANCELLED
        ride.save()
        return Response({"status":"Ride cancelled"},status=status.HTTP_200_OK)


    @action(detail=False,methods=['GET'])
    def my_rides(self,request,pk=None):
        user = request.user
        rides = Ride.objects.filter(driver=user)
        serializer = self.get_serializer(rides,many=True)
        return Response({"my_rides":serializer.data},status=status.HTTP_200_OK)
    
    @action(detail=True,methods=['GET'])
    def bookings_details(self,request,pk=None):
        print("Before executing get_object")
        ride = self.get_object()
        print("After executing get_object")
        self.check_object_permissions(request,ride)
        print("Object level permission checked...")
        serializer = BookingsDetailsSerialzer(ride)
        return Response(serializer.data,status=status.HTTP_200_OK)
        
class VehicleMakeViewset(viewsets.ModelViewSet):
    queryset = VehicleMake.objects.all()
    serializer_class = VehicleMakeSerializer
    permission_classes = [IsAdminUser]

class VehicleModelViewset(viewsets.ModelViewSet):
    queryset = VehicleModel.objects.select_related('make')
    serializer_class = VehicleModelSerializer
    permission_classes = [IsAdminUser]

class VehicleViewset(viewsets.ModelViewSet):
    queryset = Vehicle.objects.select_related('owner','model')
    serializer_class = VehicleSerializer
    permission_classes = [IsAuthenticated,IsDriver]

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)
        return serializer.data
