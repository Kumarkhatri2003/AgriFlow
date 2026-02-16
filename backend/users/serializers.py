from rest_framework import serializers
from django.contrib.auth import authenticate
from django.contrib.auth.password_validation import validate_password
from django.core import exceptions
from rest_framework_simplejwt.tokens import RefreshToken
from .models import User
import uuid


class  UserSerializer(serializers.ModelSerializer):
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

class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(
        write_only = True,
        required = True,
        style ={'input_type':'password'},
        validators =[validate_password]
    )

    password2 = serializers.CharField(
        write_only = True,
        required = True,
        style ={'input_type':'password'},
        label = "Confirm Password"
    )

    class Meta:
        model = User
        fields = (
            'email','username','password','password2','first_name','last_name','phone','location'
            )

    def validate(self, attrs):
        if attrs['password'] != attrs['password2']:
            raise serializers.ValidationError({
                "password" : "Password fields doesn't match."
            })
        return attrs

    def create(self, validated_data):
        validated_data.pop('password2') 

        user = User.objects.create_user(
            **validated_data,
            is_active=True
        ) 

        #Generate email verification
        user.email_verification_token = str(uuid.uuid4())
        user.save()

        return user
    
class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(
        write_only = True,
        style ={'input_type': 'password'}
    )

    def validate(self, data):
        email = data.get('email')
        password = data.get('password')

        if email and password:
            user = authenticate(email=email , password=password)

            if user:
                if not user.is_email_verified:
                    raise serializers.ValidationError(
                        "Please verify your email first."
                    )
                
                if not user.is_active:
                    raise serializers.ValidationError(
                        "User account is disabled."
                    )
                
                #Generate JWT tokens

                refresh = RefreshToken.for_user(user)

                return{
                    'user':UserSerializer(user).data,
                    'access':str(refresh.access_token),
                    'refresh': str(refresh)
                }
            else:
                raise serializers.ValidationError(
                    "Unable to log in with provided credentials."
                )
        else: 
            raise serializers.ValidationError(
                "Must include 'email' and 'password'."
            )
               
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
                "new_password": "Password fields didn't match."
            })
        return attrs

class PasswordResetRequestSerializer(serializers.Serializer):
    """Request password reset email"""
    email = serializers.EmailField()

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