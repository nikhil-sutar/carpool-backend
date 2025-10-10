from django.contrib.auth import get_user_model
from django.db import transaction
from django.db.models import F
from django.shortcuts import render
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.filters import SearchFilter

from rides.models import Ride

from .filters import BookingsFilter
from .models import Booking, Payment
from .permissions import IsPassenger
from .serializers import BookingSerializer, PaymentSerializer
from .tasks import (send_booking_cancellation_email,
                    send_booking_confirmation_email)

# Create your views here.

User = get_user_model()

class BookingViewSet(viewsets.ModelViewSet):
    queryset = Booking.objects.select_related('ride','passenger__profile')
    serializer_class = BookingSerializer
    http_method_names = ['get','post']
    filterset_class = BookingsFilter
    search_fields = ['boarding_point','dropping_point']
    def get_queryset(self):
        qs = self.queryset
        user = self.request.user
        if user.role == User.Roles.PASSENGER:
            qs = qs.filter(passenger=user)
        elif user.role == User.Roles.ADMIN:
            qs = qs
        else:
            qs = qs.filter(ride__driver = self.request.user)
        
        print("Query params:", self.request.query_params)
        print("Final queryset:", qs.query)  # SQL generated

        return qs

    def get_permissions(self):
        if self.action in ['create','cancel_booking']:
            permissions = [IsAuthenticated,IsPassenger]
        else:
            permissions = [IsAuthenticated]
        return [permission() for permission in permissions]
    
    def perform_create(self, serializer):
        user = self.request.user
        booking = serializer.save(passenger=user)
        print("Sending booking confirmation email...")
        send_booking_confirmation_email.delay(user.email,booking.id)
        return serializer.data
    
    @action(detail=True,methods=['POST'])
    def cancel_booking(self,request,pk=None):
        booking = self.get_object()
        self.check_object_permissions(request,booking)
        user = request.user
        if booking.passenger != user:
            return Response({"error":"Not your trip"},status=status.HTTP_400_BAD_REQUEST)
        elif booking.ride.status != Ride.StatusChoices.OPEN:
            return Response({"error":"Trip is active you can't cancel it"},status=status.HTTP_400_BAD_REQUEST)
        elif booking.status == Booking.BookingStatus.CANCELLED:
            return Response({"error":"Booking already cancelled."},status=status.HTTP_400_BAD_REQUEST)
        
        with transaction.atomic():
            ride = Ride.objects.select_for_update().get(id=booking.ride.id)
            
            booking.status = Booking.BookingStatus.CANCELLED
            booking.save()

            ride.seats_booked = F('seats_booked') - booking.seats_booked
            ride.save() 
            send_booking_cancellation_email.delay(user.email,booking.id)
            ride.refresh_from_db()

        return Response({"message":"Booking cancelled successfully..!"})

    @action(detail=False)
    def my_bookings(self,request):
        bookings = Booking.objects.filter(passenger=request.user)
        serializer = self.get_serializer(bookings,many=True)
        return Response({"my-bookings":serializer.data},status=status.HTTP_200_OK)
    
class PaymentViewSet(viewsets.ModelViewSet):
    queryset = Payment.objects.all()
    serializer_class = PaymentSerializer
    permission_classes = [IsAuthenticated,IsPassenger]

    def get_queryset(self):
        qs = self.queryset
        user = self.request.user
        return qs.filter(booking__passenger = user)