# models.py
from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.validators import (
    MinLengthValidator, 
    MaxLengthValidator, 
    RegexValidator,
    MinValueValidator,
    MaxValueValidator,
    ValidationError
)
from django.utils import timezone
import re

# ============ CUSTOM VALIDATORS ============

def validate_nepal_phone(value):
    """Validator for Nepali phone numbers"""
    if value:
        cleaned = re.sub(r'[\s\-\(\)]', '', value)
        if not re.match(r'^98[0-9]{8}$|^97[0-9]{8}$', cleaned):
            raise ValidationError(
                'Enter a valid Nepali phone number (e.g., 9841234567)'
            )
        return cleaned
    return value


def validate_min_age(value):
    """Ensure user is at least 13 years old"""
    if value:
        today = timezone.now().date()
        age = today.year - value.year - ((today.month, today.day) < (value.month, value.day))
        if age < 13:
            raise ValidationError('You must be at least 13 years old')
        if age > 120:
            raise ValidationError('Please enter a valid date of birth')


def validate_farm_area(value):
    """Validate farm area"""
    if value is not None:
        if value <= 0:
            raise ValidationError('Farm area must be greater than 0 ')
        


def validate_coordinates(lat, lng=None):
    """Validator for coordinates (can be used for single field too)"""
    def validate_latitude(value):
        if value is not None and not -90 <= value <= 90:
            raise ValidationError('Latitude must be between -90 and 90')
        return value
    
    def validate_longitude(value):
        if value is not None and not -180 <= value <= 180:
            raise ValidationError('Longitude must be between -180 and 180')
        return value
    
    return validate_latitude, validate_longitude


def validate_ward_number(value):
    """Validate Nepal ward number (1-32)"""
    if value and (value < 1 or value > 32):
        raise ValidationError('Ward number must be between 1 and 32')


def validate_altitude(value):
    """Validate altitude for Nepal"""
    if value is not None:
        if value < 0:
            raise ValidationError('Altitude cannot be negative')
        if value > 8848:  # Mount Everest height
            raise ValidationError('Altitude cannot exceed 8,848 meters (Mount Everest)')


# ============ USER MODEL ============

class User(AbstractUser):
    """Custom User Model with Nepal-specific fields"""
    
    # ============ GENDER CHOICES ============
    GENDER_CHOICES = [
        ('M', 'Male'),
        ('F', 'Female'),
        ('O', 'Other'),
    ]
    
    # ============ GEOGRAPHICAL REGIONS ============
    REGION_CHOICES = [
        ('terai', 'Terai Region'),
        ('hilly', 'Hilly Region'),
        ('mountain', 'Mountain Region'),
        ('kathmandu_valley', 'Kathmandu Valley'),
    ]
    
    # ============ SOIL TYPES ============
    SOIL_TYPE_CHOICES = [
        ('alluvial', 'Alluvial Soil'),
        ('clay', 'Clay Soil'),
        ('sandy', 'Sandy Soil'),
        ('loamy', 'Loamy Soil'),
        ('peaty', 'Peaty Soil'),
        ('chalky', 'Chalky Soil'),
        ('silt', 'Silt Soil'),
        ('laterite', 'Laterite Soil'),
        ('mountain', 'Mountain Soil'),
        ('terra_rossa', 'Terra Rossa'),
    ]
    
    # ============ WATER SOURCES ============
    WATER_SOURCE_CHOICES = [
        ('irrigation', 'Irrigation System'),
        ('river', 'River'),
        ('well', 'Well'),
        ('borewell', 'Borewell'),
        ('tube_well', 'Tube Well'),
        ('pond', 'Pond'),
        ('rainwater', 'Rainwater Harvesting'),
        ('spring', 'Natural Spring'),
        ('canal', 'Canal'),
    ]
    
    # ============ BASIC INFO FIELDS ============
    email = models.EmailField(
        unique=True,
        error_messages={
            'unique': 'A user with this email already exists',
            'invalid': 'Enter a valid email address',
        }
    )
    
    phone = models.CharField(
        max_length=10,
        unique=True,
        blank=True,
        null=True,
        validators=[validate_nepal_phone],
        error_messages={
            'unique': 'This phone number is already registered',
        }
    )
    
    date_of_birth = models.DateField(
        null=True, 
        blank=True,
        validators=[validate_min_age]
    )
    
    gender = models.CharField(
        max_length=1,
        choices=GENDER_CHOICES,
        blank=True,
        null=True
    )
    
    # ============ LOCATION FIELDS ============
    geographical_region = models.CharField(
        max_length=50,
        choices=REGION_CHOICES,
        blank=True,
        null=True
    )
    
    location = models.CharField(
        max_length=200,
        blank=True,
        null=True,
        validators=[MaxLengthValidator(200)]
    )
    
    district = models.CharField(
        max_length=100,
        blank=True,
        null=True
    )
    
    profile_picture = models.ImageField(
        upload_to='profile_pics/',
        blank=True,
        null=True
    )
    
    # ============ FARM FIELDS ============
    is_farmer = models.BooleanField(default=False)
    is_admin = models.BooleanField(default=False)
    
    farm_name = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        validators=[
            MinLengthValidator(3, message='Farm name must be at least 3 characters'),
            MaxLengthValidator(100, message='Farm name cannot exceed 100 characters'),
            RegexValidator(
                regex=r'^[a-zA-Z0-9\s\-_]+$',
                message='Farm name can only contain letters, numbers, spaces, hyphens, and underscores',
                code='invalid_farm_name'
            )
        ]
    )
    
    total_farm_area = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        blank=True,
        null=True,
        validators=[validate_farm_area]
    )
    
    # Farm location details
    farm_village = models.CharField(max_length=100, blank=True, null=True)
    farm_municipality = models.CharField(max_length=100, blank=True, null=True)
    farm_district = models.CharField(max_length=100, blank=True, null=True)
    farm_province = models.CharField(max_length=50, blank=True, null=True)
    
    farm_ward_number = models.IntegerField(
        blank=True,
        null=True,
        validators=[validate_ward_number]
    )
    
    # Farm coordinates
    farm_latitude = models.DecimalField(
        max_digits=10,
        decimal_places=7,
        blank=True,
        null=True,
        validators=[MaxValueValidator(90), MinValueValidator(-90)]
    )
    
    farm_longitude = models.DecimalField(
        max_digits=10,
        decimal_places=7,
        blank=True,
        null=True,
        validators=[MaxValueValidator(180), MinValueValidator(-180)]
    )
    
    farm_altitude = models.DecimalField(
        max_digits=8,
        decimal_places=2,
        blank=True,
        null=True,
        validators=[validate_altitude]
    )
    
    farm_soil_type = models.CharField(
        max_length=50,
        choices=SOIL_TYPE_CHOICES,
        blank=True,
        null=True
    )
    
    water_source = models.CharField(
        max_length=50,
        choices=WATER_SOURCE_CHOICES,
        blank=True,
        null=True
    )
    
    # ============ VERIFICATION & SECURITY FIELDS ============
    is_email_verified = models.BooleanField(default=False)
    email_verification_token = models.CharField(max_length=255, blank=True, null=True)
    
    reset_password_token = models.CharField(max_length=255, blank=True, null=True)
    reset_password_expires = models.DateTimeField(blank=True, null=True)
    
    # ============ TERMS FIELDS ============
    agreed_to_terms = models.BooleanField(default=False)
    agreed_to_privacy = models.BooleanField(default=False)
    terms_version = models.CharField(max_length=10, default='1.0')
    privacy_version = models.CharField(max_length=10, default='1.0')
    terms_accepted_at = models.DateTimeField(blank=True, null=True)
    privacy_accepted_at = models.DateTimeField(blank=True, null=True)
    
    # ============ TIMESTAMPS ============
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    # ============ REQUIRED FIELDS ============
    REQUIRED_FIELDS = ['email']
    
    class Meta:
        ordering = ['-date_joined']
        indexes = [
            models.Index(fields=['email']),
            models.Index(fields=['phone']),
            models.Index(fields=['is_farmer']),
            models.Index(fields=['district']),
            models.Index(fields=['farm_district']),
        ]
    
    def __str__(self):
        return f"{self.username} ({self.email})"
    
    # ============ MODEL-LEVEL VALIDATION ============
    
    def clean(self):
        """Model-level validation (called by forms and model.save())"""
        super().clean()
        
        # Ensure farm_latitude and farm_longitude are either both set or both null
        if (self.farm_latitude is None) != (self.farm_longitude is None):
            raise ValidationError(
                "Both latitude and longitude must be provided together"
            )
        
        # Ensure farm name and area consistency
        if self.farm_name and not self.total_farm_area:
            raise ValidationError({
                'total_farm_area': 'Farm area is required when providing a farm name'
            })
        
        # Validate coordinates if both are present
        if self.farm_latitude and self.farm_longitude:
            if not (-90 <= self.farm_latitude <= 90):
                raise ValidationError({
                    'farm_latitude': 'Latitude must be between -90 and 90'
                })
            if not (-180 <= self.farm_longitude <= 180):
                raise ValidationError({
                    'farm_longitude': 'Longitude must be between -180 and 180'
                })
        
        # Sync district to farm_district if farm_district not set
        if self.district and not self.farm_district:
            self.farm_district = self.district
    
    def save(self, *args, **kwargs):
        """Override save to run full validation"""
        self.full_clean()  # Runs clean() and field validators
        super().save(*args, **kwargs)
    
    # ============ HELPER METHODS ============
    
    def get_full_name(self):
        """Return the full name of the user"""
        if self.first_name or self.last_name:
            return f"{self.first_name} {self.last_name}".strip()
        return self.username
    
    def get_age(self):
        """Calculate user's age"""
        if self.date_of_birth:
            today = timezone.now().date()
            return today.year - self.date_of_birth.year - (
                (today.month, today.day) < (self.date_of_birth.month, self.date_of_birth.day)
            )
        return None
    
    def is_minor(self):
        """Check if user is under 18"""
        age = self.get_age()
        return age is not None and age < 18
    
    def has_complete_farm_profile(self):
        """Check if farmer has completed farm profile"""
        if not self.is_farmer:
            return False
        return all([
            self.farm_name,
            self.total_farm_area,
            self.farm_district,
        ])
    
    def get_location_display(self):
        """Return formatted location string"""
        parts = []
        if self.farm_village:
            parts.append(self.farm_village)
        if self.farm_municipality:
            parts.append(self.farm_municipality)
        if self.farm_district:
            parts.append(self.farm_district)
        if self.farm_province:
            parts.append(self.farm_province)
        return ", ".join(parts) if parts else None
    
    def verify_email(self):
        """Mark email as verified"""
        self.is_email_verified = True
        self.email_verification_token = None
        self.save(update_fields=['is_email_verified', 'email_verification_token'])
    
    def generate_verification_token(self):
        """Generate new verification token"""
        import uuid
        self.email_verification_token = str(uuid.uuid4())
        self.save(update_fields=['email_verification_token'])