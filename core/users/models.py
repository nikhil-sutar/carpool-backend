from django.contrib.auth.models import (AbstractBaseUser, BaseUserManager,
                                        PermissionsMixin)
from django.core.exceptions import ValidationError
from django.db import models
from django.db.models import Q

# Helper class to that tells django how to create a new user and superuser 

class UserManager(BaseUserManager):
    def create_user(self,email,password,phone_number=None,role='passenger',**extra_fields):
        if not email and not phone_number:
            raise ValueError("Either Email or Phone number is required")

        if email:
            email = self.normalize_email(email)
        user = self.model(email=email,phone_number=phone_number,role=role,**extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user
    
    def create_superuser(self,email,password,**extra_fields):
        extra_fields.setdefault("is_staff",True)
        extra_fields.setdefault("is_superuser",True)
        return self.create_user(email=email,password=password,role="admin",**extra_fields)
        
class User(AbstractBaseUser,PermissionsMixin):
    class Roles(models.TextChoices):
        DRIVER = 'driver', 'Driver'
        PASSENGER = 'passenger', 'Passenger'
        ADMIN = 'admin', 'Admin'

    email = models.EmailField(unique=True)
    phone_number = models.CharField(max_length=13,unique=True,blank=True,null=True)
    role = models.CharField(max_length=10,choices=Roles.choices,default=Roles.PASSENGER)

    date_joined = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    class Meta:
        constraints = [
            models.CheckConstraint(
                check=(
                    Q(role='admin') |
                    (Q(is_staff=False) & Q(is_superuser=False))
                ),
                name="admin_role_required_for_staff_or_superuser",
            )
        ]

    def clean(self):
        if (self.is_staff or self.is_superuser) and self.role != self.Roles.ADMIN:
            raise ValidationError("Only admin users can be staff or superuser.")
    # whenever anyone tries to interact with custom User model using object, use custom user manager instead of default
    objects = UserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    def __str__(self):
        return self.email

class Profile(models.Model):
    class GenderChoices(models.TextChoices):
        MALE = 'male'
        FEMALE = 'female'
    
    user = models.OneToOneField(User,on_delete=models.CASCADE,related_name='profile')
    first_name = models.CharField(max_length=50,blank=True,null=True)
    last_name = models.CharField(max_length=50,blank=True,null=True)
    profile_picture = models.ImageField(blank=True,null=True,upload_to='profile_pics/')
    date_of_birth = models.DateField(blank=True,null=True)
    gender = models.CharField(max_length=10,choices=GenderChoices.choices,blank=True, null=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.first_name or self.user.email}'s Profile"
    
class DriverProfile(models.Model):
    profile = models.OneToOneField(Profile,on_delete=models.CASCADE, related_name="driver_profile")
    is_driver_verified = models.BooleanField(default=False)
    total_rides_as_a_driver = models.IntegerField(default=0) 
    rating = models.DecimalField(max_digits=5, decimal_places=2, blank=True, null=True)
    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        if self.profile.user.role != User.Roles.DRIVER:
            raise ValidationError("Only users with role=driver can have a DriverProfile.")
        super().save(*args, **kwargs)

    def __str__(self):
        return f"DriverProfile({self.profile.first_name})"

class PassengerProfile(models.Model):
    profile = models.OneToOneField(Profile,on_delete=models.CASCADE, related_name="passenger_profile")
    total_rides_as_a_passenger = models.IntegerField(default=0)

    def save(self, *args, **kwargs):
        if self.profile.user.role != User.Roles.PASSENGER:
            raise ValidationError("Only users with role=passenger can have a PassengerProfile.")
        super().save(*args, **kwargs)

    def __str__(self):
        return f"PassengerProfile({self.profile.first_name})"

class DriverDocuments(models.Model):
    driver_profile = models.ForeignKey(DriverProfile,on_delete=models.CASCADE,related_name='documents')
    file = models.FileField(upload_to="driver_documents/")
    uploaded_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.driver_profile.profile.user.email}-{self.file.name}"
    
class DriverVerification(models.Model):
    class StatusChoices(models.TextChoices):
        PENDING = 'pending','Pending'
        APPROVED = 'approved', 'Approved'
        REJECTED = 'rejected', 'Rejected'
    
    driver_profile = models.OneToOneField(DriverProfile,on_delete=models.CASCADE, related_name='verification')
    status = models.CharField(choices=StatusChoices.choices,default=StatusChoices.PENDING)
    admin_feedback = models.TextField(blank=True,null=True)
    submitted_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.driver_profile.profile.user.email} driver verification {self.status}"
