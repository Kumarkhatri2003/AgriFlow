from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils import timezone

# Create your models here.
class User(AbstractUser):

    email = models.EmailField(unique=True)

    #User types
    is_farmer = models.BooleanField(default=True)
    is_admin = models.BooleanField(default=False)

    # Profile info
    phone = models.CharField(max_length=15, blank=True)
    location = models.CharField(max_length=100, blank=True)
    profile_picture = models.ImageField(upload_to='profiles/', null=True, blank=True)

    #Email verification
    is_email_verified = models.BooleanField(default=False)
    email_verification_token = models.CharField(max_length=200, blank=True,null=True)


    # Password reset
    reset_password_token = models.CharField(max_length=255, blank=True, null=True)
    reset_password_expires = models.DateTimeField(null=True, blank=True)

    

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

    def __str__(self):
        return self.email
    
    class Meta:
        db_table = 'users'
