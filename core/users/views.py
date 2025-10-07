from django.contrib.auth import get_user_model
from django.shortcuts import render
from rest_framework import generics, status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAdminUser, IsAuthenticated
from rest_framework.response import Response

from .models import (DriverDocuments, DriverProfile, DriverVerification,
                     PassengerProfile, Profile)
from .permissions import IsAdminOrDriverSelf, IsAdminOrPassengerSelf
from .serializers import (DriverDocumentSerializer, DriverProfileSerializer,
                          DriverVerificationSerializer,
                          PassengerProfileSerializer, ProfileSerializer,
                          UserSerializer)

User = get_user_model()

# Create your views here.
class UserListCreateAPIView(generics.ListCreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer

    def perform_create(self, serializer):
        user = serializer.save()
        print("User registered successfully..!")
        return serializer.data

class ProfileViewset(viewsets.ModelViewSet):
    queryset = Profile.objects.select_related('user')
    serializer_class = ProfileSerializer
    permission_classes = [IsAuthenticated]
    def get_queryset(self):
        qs = self.queryset
        user = self.request.user
        if user.role == User.Roles.ADMIN:
            return qs
        return qs.filter(user=user)

class DriverProfileViewset(viewsets.ReadOnlyModelViewSet):
    queryset = DriverProfile.objects.select_related('profile','profile__user')
    serializer_class = DriverProfileSerializer
    permission_classes = [IsAuthenticated,IsAdminOrDriverSelf]

    def get_queryset(self):
        qs = self.queryset
        user = self.request.user
        if user.role == User.Roles.ADMIN:
            return qs
        return qs.filter(profile = user.profile)
    
    @action(detail=True,methods=['POST'],permission_classes=[IsAdminUser])
    def verify(self,request,pk=None):
        driver_profile = self.get_object()
        driver_profile.is_driver_verified = True
        driver_profile.save()

        return Response({"message":f"{driver_profile.profile.user.email} verified successfully..!"},status=status.HTTP_200_OK)

class PassengerProfileViewset(viewsets.ReadOnlyModelViewSet):
    queryset = PassengerProfile.objects.select_related('profile','profile__user')
    serializer_class = PassengerProfileSerializer
    permission_classes = [IsAuthenticated,IsAdminOrPassengerSelf]

    def get_queryset(self):
        qs = self.queryset
        user = self.request.user
        if user.role == User.Roles.ADMIN:
            return qs
        return qs.filter(profile=user.profile)

class DriverDocumentViewset(viewsets.ModelViewSet):
    queryset = DriverDocuments.objects.select_related('driver_profile')
    serializer_class = DriverDocumentSerializer
    permission_classes = [IsAuthenticated,IsAdminOrDriverSelf]
    def get_queryset(self):
        qs = self.queryset
        user = self.request.user    
        if user.role == User.Roles.ADMIN:
            return qs
        return qs.filter(driver_profile=user.profile.driver_profile)
    
    def perform_create(self, serializer):
        driver_profile = self.request.user.profile.driver_profile
        serializer.save(driver_profile=driver_profile)
        return serializer.data

class DriverVerificationViewset(viewsets.ModelViewSet):
    queryset = DriverVerification.objects.select_related('driver_profile')
    serializer_class =  DriverVerificationSerializer
    permission_classes = [IsAuthenticated,IsAdminOrDriverSelf]
    http_method_names = ['get','post']
    def get_queryset(self):
        qs = self.queryset
        if self.request.user.role == User.Roles.ADMIN:
            return qs
        return qs.filter(driver_profile=self.request.user.profile.driver_profile)
    
    def perform_create(self, serializer):
        driver_profile = self.request.user.profile.driver_profile
        serializer.save(driver_profile=driver_profile)
        return serializer.data

class DriverVerificationAdminViewset(viewsets.ModelViewSet):
    queryset = DriverVerification.objects.select_related('driver_profile')
    serializer_class = DriverVerificationSerializer
    permission_classes = [IsAdminUser]

    @action(detail=True,methods=['POST'])
    def approve(self,request,pk=None):
        verification = self.get_object()
        verification.status = DriverVerification.StatusChoices.APPROVED
        verification.save()

        verification.driver_profile.is_driver_verified = True
        verification.driver_profile.save()

        return Response({"message":"Driver approved successfully..!"},status=status.HTTP_200_OK)
    
    @action(detail=True,methods=['POST'])
    def reject(self,request,pk=None):
        verification = self.get_object()
        verification.status = DriverVerification.StatusChoices.REJECTED
        verification.admin_feedback = self.request.data.get('admin_feedback','')
        verification.save()
        
        verification.driver_profile.is_driver_verified = False
        verification.driver_profile.save()

        return Response({"message":"Driver rejected successfully..!"},status=status.HTTP_200_OK)
    