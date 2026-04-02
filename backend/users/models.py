from django.db import models
from django.contrib.auth.models import AbstractUser
import uuid

class User(AbstractUser):
    """Custom user model with email as primary identifier"""
    
    email = models.EmailField(unique=True)
    
    # User type
    is_farmer = models.BooleanField(default=True)
    is_admin = models.BooleanField(default=False)
    
    # ------- BASIC PROFILE FIELDS ----------
    
    # Personal Info
    first_name = models.CharField(max_length=150)
    last_name = models.CharField(max_length=150)
    phone = models.CharField(max_length=15, blank=True)
    
    # NEW FIELDS
    date_of_birth = models.DateField(null=True, blank=True)
    gender = models.CharField(max_length=50, choices=[
        ('male', 'Male'),
        ('female', 'Female'),
        ('other', 'Other'),
        ('prefer_not_to_say', 'Prefer not to say'),
    ], blank=True)
    
    #Geographical Location (Nepal specific)
    GEOGRAPHICAL_REGIONS = [
        ('himalayan', 'Himalayan (हिमाली)'),
        ('hilly', 'Hilly (पहाडी)'),
        ('terai', 'Terai (तराई)'),
    ]
    geographical_region = models.CharField(max_length=20, choices=GEOGRAPHICAL_REGIONS, blank=True)
    
    #Simple location
    location = models.CharField(max_length=100, blank=True)  # Village/City/Town
    district = models.CharField(max_length=100, blank=True)
    
    # Profile picture
    profile_picture = models.ImageField(upload_to='profiles/', null=True, blank=True)
    
    # Email verification
    is_email_verified = models.BooleanField(default=False)
    email_verification_token = models.CharField(max_length=255, blank=True, null=True)
    
    # Password reset
    reset_password_token = models.CharField(max_length=255, blank=True, null=True)
    reset_password_expires = models.DateTimeField(null=True, blank=True)
    
    # Terms and Privacy acceptance
    agreed_to_terms = models.BooleanField(default=False)
    agreed_to_privacy = models.BooleanField(default=False)
    terms_version = models.CharField(max_length=20, blank=True, default='1.0')
    privacy_version = models.CharField(max_length=20, blank=True, default='1.0')
    terms_accepted_at = models.DateTimeField(null=True, blank=True)
    privacy_accepted_at = models.DateTimeField(null=True, blank=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username','first_name', 'last_name']
    
    def __str__(self):
        return f"{self.get_full_name()} ({self.email})"
    
    def get_full_name(self):
        return f"{self.first_name} {self.last_name}".strip()
    
    class Meta:
        db_table = 'users'