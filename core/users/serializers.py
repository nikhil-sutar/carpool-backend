from django.contrib.auth import get_user_model
from rest_framework import serializers

from .models import (DriverDocuments, DriverProfile, DriverVerification,
                     PassengerProfile, Profile)

User = get_user_model()

class UserSerializer(serializers.ModelSerializer):
    password2 = serializers.CharField(style={'input_type':'password'},write_only=True)
    class Meta:
        model = User
        fields = ['email','phone_number','role','password','password2','date_joined','updated_at','is_active','is_staff']
        extra_kwargs = {
            'password' : {'write_only':True}
        }
        read_only_fields = ['date_joined','updated_at','is_staff']
    
    def validate(self, attrs):
        if attrs['password'] != attrs['password2']:
            raise serializers.ValidationError("Passwords do not match.")
        return attrs
    
    def create(self, validated_data):
        password2 = validated_data.pop('password2')
        user = User.objects.create_user(**validated_data)
        return user

class ProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = Profile
        fields = ['user','first_name','last_name','profile_picture','date_of_birth','gender','updated_at']
        read_only_fields = ['user']
    
class DriverProfileSerializer(serializers.ModelSerializer):
    profile = ProfileSerializer(read_only=True)
    # profile_id = serializers.PrimaryKeyRelatedField(source='profile',queryset=Profile.objects.all(),write_only=True)
    class Meta:
        model = DriverProfile
        fields = ["id","profile","is_driver_verified","total_rides_as_a_driver","rating","updated_at"]
        read_only_fields = ['is_driver_verified','total_rides_as_a_driver','rating']

class PassengerProfileSerializer(serializers.ModelSerializer):
    profile = ProfileSerializer()
    class Meta:
        model = PassengerProfile
        fields = ["profile","total_rides_as_a_passenger"]   
        read_only_fields = ["profile","total_rides_as_a_passenger"]

class DriverDocumentSerializer(serializers.ModelSerializer):
    class Meta:
        model = DriverDocuments
        fields = ['id','driver_profile','file','uploaded_at']
        read_only_fields = ['driver_profile','uploaded_at']

class DriverVerificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = DriverVerification
        fields = ["id","driver_profile","status","admin_feedback","submitted_at","updated_at"] 
        read_only_fields = ['driver_profile','admin_feedback','submitted_at','updated_at']