from datetime import timezone
from django.utils import timezone
from rest_framework import serializers
from django.contrib.auth import authenticate
from django.contrib.auth.password_validation import validate_password
from django.core import exceptions
from rest_framework_simplejwt.tokens import RefreshToken
from .models import User
import uuid
import re


class UserSerializer(serializers.ModelSerializer):
    """Basic user info for frontend"""
    full_name = serializers.SerializerMethodField()
    
    class Meta:
        model = User
        fields = (
            'id', 'email', 'username', 'full_name', 
            'phone', 'location', 'profile_picture',
            'is_farmer', 'is_email_verified', 'created_at'
        )
        read_only_fields = ('id', 'is_email_verified', 'created_at')
    
    def get_full_name(self, obj):
        return f"{obj.first_name} {obj.last_name}".strip() or obj.username
    

class UserProfileSerializer(serializers.ModelSerializer):
    """Detailed user profile info for frontend"""
    full_name = serializers.SerializerMethodField()
    gender_display = serializers.CharField(source='get_gender_display', read_only=True)
    region_display = serializers.CharField(source='get_geographical_region_display', read_only=True)
    farm_location_display = serializers.CharField(source='get_farm_location_display', read_only=True)
    
    class Meta:
        model = User
        fields = (
            'id', 'email', 'username',
            'is_farmer', 'is_email_verified', 'created_at',
            
            # Updateable fields
            'full_name', 'gender_display', 'region_display',
            'farm_location_display',
            'first_name', 'last_name', 'phone', 'date_of_birth',
            'gender', 'geographical_region', 'location', 'district',
            'profile_picture',
            
            # Farm fields
            'farm_name', 'total_farm_area',
            'farm_village', 'farm_municipality', 'farm_district', 'farm_province', 'farm_ward_number',
            'farm_altitude', 'farm_soil_type', 'water_source', 
        )
        read_only_fields = ('id', 'email', 'username', 'is_email_verified', 'created_at')
        
    def get_full_name(self, obj):
        return f"{obj.first_name} {obj.last_name}".strip() or obj.username
    
    
class UpdateUserProfileSerializer(serializers.ModelSerializer):
    """Serializer for updating user profile"""
    
    class Meta:
        model = User
        fields = (
            'first_name', 'last_name', 'phone', 'date_of_birth',
            'gender', 'geographical_region', 'location', 'district',
            'profile_picture',
            
            # Farm location fields (updateable)
            'farm_name', 'total_farm_area',
            'farm_village', 'farm_municipality', 'farm_district',
            'farm_province', 'farm_ward_number',
            'farm_latitude', 'farm_longitude', 'farm_altitude',
            'farm_soil_type', 'water_source',
        )
    
    # ============ FIELD VALIDATIONS ============
    
    def validate_phone(self, value):
        """Validate Nepali phone number"""
        if value:
            # Remove any spaces or special characters
            cleaned = re.sub(r'[\s\-\(\)]', '', value)
            
            # Check if it's a valid Nepal phone number
            if not re.match(r'^98[0-9]{8}$|^97[0-9]{8}$', cleaned):
                raise serializers.ValidationError(
                    "Enter a valid Nepali phone number (e.g., 9841234567 or 9741234567)"
                )
            return cleaned
        return value
    
    def validate_date_of_birth(self, value):
        """Validate age (must be at least 13 years old)"""
        if value:
            today = timezone.now().date()
            age = today.year - value.year - ((today.month, today.day) < (value.month, value.day))
            
            if age < 13:
                raise serializers.ValidationError(
                    "You must be at least 13 years old to register"
                )
            if age > 120:
                raise serializers.ValidationError(
                    "Please enter a valid date of birth"
                )
        return value
    
    def validate_total_farm_area(self, value):
        """Validate farm area (positive and reasonable)"""
        if value is not None:
            if value <= 0:
                raise serializers.ValidationError(
                    "Farm area must be greater than 0 hectares"
                )
            if value > 10000:
                raise serializers.ValidationError(
                    "Farm area cannot exceed 10,000 hectares. Please contact support if this is correct."
                )
        return value
    
    def validate_farm_ward_number(self, value):
        """Validate ward number (1-32, typical for Nepal municipalities)"""
        if value:
            if value < 1 or value > 32:
                raise serializers.ValidationError(
                    "Ward number must be between 1 and 32"
                )
        return value
    
    def validate_farm_latitude(self, value):
        """Validate latitude range"""
        if value is not None:
            if not -90 <= value <= 90:
                raise serializers.ValidationError(
                    "Latitude must be between -90 and 90 degrees"
                )
        return value
    
    def validate_farm_longitude(self, value):
        """Validate longitude range"""
        if value is not None:
            if not -180 <= value <= 180:
                raise serializers.ValidationError(
                    "Longitude must be between -180 and 180 degrees"
                )
        return value
    
    def validate_farm_altitude(self, value):
        """Validate altitude (Nepal ranges from 59m to 8848m)"""
        if value is not None:
            if value < 0:
                raise serializers.ValidationError(
                    "Altitude cannot be negative"
                )
            if value > 9000:
                raise serializers.ValidationError(
                    "Altitude seems too high. Maximum is 8,848m (Mount Everest)"
                )
        return value
    
    def validate_farm_soil_type(self, value):
        """Validate soil type against common types"""
        if value:
            valid_soil_types = [
                'alluvial', 'clay', 'sandy', 'loamy', 'peaty', 
                'chalky', 'silt', 'laterite', 'mountain', 'terra rossa'
            ]
            if value.lower() not in valid_soil_types:
                raise serializers.ValidationError(
                    f"Invalid soil type. Choose from: {', '.join(valid_soil_types)}"
                )
        return value
    
    def validate_water_source(self, value):
        """Validate water source"""
        if value:
            valid_sources = [
                'irrigation', 'river', 'well', 'borewell', 
                'pond', 'rainwater', 'spring', 'canal'
            ]
            if value.lower() not in valid_sources:
                raise serializers.ValidationError(
                    f"Invalid water source. Choose from: {', '.join(valid_sources)}"
                )
        return value
    
    def validate_farm_name(self, value):
        """Validate farm name (basic sanitization)"""
        if value:
            if len(value) < 3:
                raise serializers.ValidationError(
                    "Farm name must be at least 3 characters long"
                )
            if len(value) > 100:
                raise serializers.ValidationError(
                    "Farm name cannot exceed 100 characters"
                )
            # Check for potentially harmful characters (basic)
            if re.search(r'[<>$%#@]', value):
                raise serializers.ValidationError(
                    "Farm name contains invalid characters"
                )
        return value
    
    # ============ CROSS-FIELD VALIDATION ============
    
    def validate(self, data):
        """Cross-field validations"""
        
        # If coordinates are provided, validate them together
        if 'farm_latitude' in data and 'farm_longitude' in data:
            lat = data['farm_latitude']
            lng = data['farm_longitude']
            
            if lat is not None and lng is not None:
                # Both coordinates should be provided together
                if (lat is None) != (lng is None):
                    raise serializers.ValidationError({
                        "farm_latitude": "Both latitude and longitude must be provided together",
                        "farm_longitude": "Both latitude and longitude must be provided together"
                    })
        
        # Validate district consistency
        if 'district' in data and 'farm_district' in data:
            if data['district'] != data['farm_district']:
                # This is allowed, but let's warn (or you can require consistency)
                # For now, just auto-sync in update method
                pass
        
        # Validate farm area with farm name (if farm name provided, area should be too)
        if 'farm_name' in data and data['farm_name']:
            if 'total_farm_area' not in data or not data.get('total_farm_area'):
                raise serializers.ValidationError({
                    "total_farm_area": "Farm area is required when providing a farm name"
                })
        
        return data
    
    def update(self, instance, validated_data):
        # Auto-sync district to farm_district if farm_district not provided
        if 'district' in validated_data and 'farm_district' not in validated_data:
            validated_data['farm_district'] = validated_data['district']
        
        return super().update(instance, validated_data)


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, validators=[validate_password])
    password2 = serializers.CharField(write_only=True)
    
    # Add terms fields
    agreed_to_terms = serializers.BooleanField(write_only=True, required=True)
    agreed_to_privacy = serializers.BooleanField(write_only=True, required=True)
    
    class Meta:
        model = User
        fields = [
            'username', 'email', 'password', 'password2',
            'first_name', 'last_name', 'phone',
            'date_of_birth', 'gender',
            'geographical_region', 'location', 'district',
            'agreed_to_terms', 'agreed_to_privacy'
        ]
    
    # ============ FIELD VALIDATIONS ============
    
    def validate_username(self, value):
        """Validate username format and uniqueness"""
        if len(value) < 3:
            raise serializers.ValidationError(
                "Username must be at least 3 characters long"
            )
        if len(value) > 30:
            raise serializers.ValidationError(
                "Username cannot exceed 30 characters"
            )
        if not re.match(r'^[a-zA-Z0-9_]+$', value):
            raise serializers.ValidationError(
                "Username can only contain letters, numbers, and underscores"
            )
        return value
    
    def validate_email(self, value):
        """Validate email format and uniqueness"""
        # Check format
        if not re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', value):
            raise serializers.ValidationError("Enter a valid email address")
        
        # Check uniqueness (case-insensitive)
        if User.objects.filter(email__iexact=value).exists():
            raise serializers.ValidationError("A user with this email already exists")
        
        return value.lower()  # Normalize to lowercase
    
    def validate_phone(self, value):
        """Validate Nepali phone number"""
        if value:
            # Remove spaces and special characters
            cleaned = re.sub(r'[\s\-\(\)]', '', value)
            
            if not re.match(r'^98[0-9]{8}$|^97[0-9]{8}$', cleaned):
                raise serializers.ValidationError(
                    "Enter a valid Nepali phone number (e.g., 9841234567)"
                )
            
            # Check uniqueness
            if User.objects.filter(phone=cleaned).exists():
                raise serializers.ValidationError("This phone number is already registered")
            
            return cleaned
        return value
    
    def validate_date_of_birth(self, value):
        """Validate age (must be at least 13)"""
        if value:
            today = timezone.now().date()
            age = today.year - value.year - ((today.month, today.day) < (value.month, value.day))
            
            if age < 13:
                raise serializers.ValidationError(
                    "You must be at least 13 years old to register"
                )
            if age > 120:
                raise serializers.ValidationError(
                    "Please enter a valid date of birth"
                )
        return value
    
    def validate_first_name(self, value):
        """Validate first name"""
        if value and len(value) < 2:
            raise serializers.ValidationError("First name must be at least 2 characters")
        if value and len(value) > 50:
            raise serializers.ValidationError("First name cannot exceed 50 characters")
        return value
    
    def validate_last_name(self, value):
        """Validate last name"""
        if value and len(value) < 2:
            raise serializers.ValidationError("Last name must be at least 2 characters")
        if value and len(value) > 50:
            raise serializers.ValidationError("Last name cannot exceed 50 characters")
        return value
    
    def validate_location(self, value):
        """Validate location string"""
        if value and len(value) > 200:
            raise serializers.ValidationError("Location cannot exceed 200 characters")
        return value
    
    # ============ MAIN VALIDATION ============
    
    def validate(self, attrs):
        # Check passwords match
        if attrs['password'] != attrs['password2']:
            raise serializers.ValidationError({
                "password": "Password fields didn't match."
            })
        
        # Check terms acceptance
        if not attrs.get('agreed_to_terms'):
            raise serializers.ValidationError({
                "agreed_to_terms": "You must agree to the Terms of Service."
            })
        
        if not attrs.get('agreed_to_privacy'):
            raise serializers.ValidationError({
                "agreed_to_privacy": "You must agree to the Privacy Policy."
            })
        
        # Validate gender choice
        gender = attrs.get('gender')
        if gender:
            valid_genders = ['M', 'F', 'O', '']  # Adjust based on your model choices
            if gender not in valid_genders:
                raise serializers.ValidationError({
                    "gender": "Invalid gender selection"
                })
        
        # Validate geographical region
        region = attrs.get('geographical_region')
        if region:
            valid_regions = ['terai', 'hilly', 'mountain', 'kathmandu_valley']
            if region.lower() not in valid_regions:
                raise serializers.ValidationError({
                    "geographical_region": f"Invalid region. Choose from: {', '.join(valid_regions)}"
                })
        
        return attrs
    
    def create(self, validated_data):
        agreed_to_terms = validated_data.pop('agreed_to_terms')
        agreed_to_privacy = validated_data.pop('agreed_to_privacy')
        password2 = validated_data.pop('password2')  # Remove password2
        
        district_value = validated_data.get('district', '')

        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data['email'],
            password=validated_data['password'],
            first_name=validated_data.get('first_name', ''),
            last_name=validated_data.get('last_name', ''),
            phone=validated_data.get('phone', ''),
            date_of_birth=validated_data.get('date_of_birth'),
            gender=validated_data.get('gender', ''),
            geographical_region=validated_data.get('geographical_region', ''),
            location=validated_data.get('location', ''),
            district=district_value,
            farm_district=district_value,
            is_active=True,
            is_farmer=True,
            agreed_to_terms=agreed_to_terms,
            agreed_to_privacy=agreed_to_privacy,
            terms_version='1.0',
            privacy_version='1.0',
            terms_accepted_at=timezone.now(),
            privacy_accepted_at=timezone.now()
        )
        
        # Generate email verification token
        user.email_verification_token = str(uuid.uuid4())
        user.save()
        
        return user


class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(
        write_only=True,
        style={'input_type': 'password'}
    )
    
    def validate_email(self, value):
        """Normalize email to lowercase"""
        return value.lower()
    
    def validate(self, data):
        email = data.get('email')
        password = data.get('password')
        
        if email and password:
            user = authenticate(email=email, password=password)
            
            if user:
                if not user.is_email_verified:
                    raise serializers.ValidationError(
                        "Please verify your email first. Check your inbox for the verification link."
                    )
                
                if not user.is_active:
                    raise serializers.ValidationError(
                        "Your account has been disabled. Please contact support."
                    )
                
                # Generate JWT tokens
                refresh = RefreshToken.for_user(user)
                
                return {
                    'user': UserSerializer(user).data,
                    'access': str(refresh.access_token),
                    'refresh': str(refresh)
                }
            else:
                raise serializers.ValidationError(
                    "Unable to log in with provided credentials. Please check your email and password."
                )
        else:
            raise serializers.ValidationError(
                "Must include both 'email' and 'password'."
            )


#---------------Change Password Serializer------------------#            
class ChangePasswordSerializer(serializers.Serializer):
    """Change password for logged in user"""
    old_password = serializers.CharField(
        write_only=True,
        style={'input_type': 'password'}
    )
    new_password = serializers.CharField(
        write_only=True,
        style={'input_type': 'password'},
        validators=[validate_password]
    )
    new_password2 = serializers.CharField(
        write_only=True,
        style={'input_type': 'password'},
        label="Confirm New Password"
    )
    
    def validate(self, attrs):
        if attrs['new_password'] != attrs['new_password2']:
            raise serializers.ValidationError({
                "new_password": "New password fields didn't match."
            })
        
        # Check old password != new password
        if attrs.get('old_password') == attrs.get('new_password'):
            raise serializers.ValidationError({
                "new_password": "New password must be different from old password."
            })
        
        return attrs


#---------------Password Reset Serializers------------------
class PasswordResetRequestSerializer(serializers.Serializer):
    """Request password reset email"""
    email = serializers.EmailField()
    
    def validate_email(self, value):
        """Normalize email and check existence"""
        value = value.lower()
        # Don't raise error if user doesn't exist (security)
        # Just return normalized email
        return value


class PasswordResetConfirmSerializer(serializers.Serializer):
    """Confirm password reset with token"""
    token = serializers.CharField()
    new_password = serializers.CharField(
        write_only=True,
        style={'input_type': 'password'},
        validators=[validate_password]
    )
    new_password2 = serializers.CharField(
        write_only=True,
        style={'input_type': 'password'},
        label="Confirm New Password"
    )
    
    def validate(self, attrs):
        if attrs['new_password'] != attrs['new_password2']:
            raise serializers.ValidationError({
                "new_password": "Password fields didn't match."
            })
        return attrs