from rest_framework import status
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.views import APIView
from .utils import send_verification_email, send_password_reset_email
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import logout as django_logout
from .serializers import (
    RegisterSerializer, UserSerializer, LoginSerializer, 
    PasswordResetRequestSerializer, PasswordResetConfirmSerializer, 
    ChangePasswordSerializer
)
from .models import User
from django.utils import timezone
import uuid

# Create your views here.

class RegisterView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        
        if serializer.is_valid():
            user = serializer.save()
            send_verification_email(user, request)

            return Response({
                'success': True,
                'message': 'Registration successful! Please check your email to verify your account.',
                'user': UserSerializer(user).data
            }, status=status.HTTP_201_CREATED)
        
        return Response({
            'success': False,
            'error': serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)

class LoginView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = LoginSerializer(data=request.data)

        if serializer.is_valid():
            return Response({
                'success': True,
                'message': 'Login successful',
                **serializer.validated_data
            })
        
        return Response({
            'success': False,
            'errors': serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)

class RefreshTokenView(APIView):
    """Refresh JWT token"""
    permission_classes = [AllowAny]

    def post(self, request):
        refresh = request.data.get('refresh')

        if not refresh:
            return Response({
                'success': False,
                'error': 'Refresh token required'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            # FIXED: Use RefreshToken class, not the view
            token = RefreshToken(refresh)
            return Response({
                'success': True,
                'access': str(token.access_token)
            })
        except Exception as e:
            return Response({
                'success': False,
                'error': f'Invalid refresh token: {str(e)}'
            }, status=status.HTTP_401_UNAUTHORIZED)

class VerifyEmailView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        token = request.GET.get('token')

        if not token:
            return Response({
                'success': False,
                'error': 'Verification token required'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            user = User.objects.get(email_verification_token=token)

            if user.is_email_verified:
                return Response({
                    'success': False,
                    'message': 'Email already verified'
                })
            
            user.is_email_verified = True
            user.email_verification_token = None
            user.save()

            return Response({
                'success': True,
                'message': 'Email verified successfully! You can now login'
            })
        
        except User.DoesNotExist:
            return Response({
                'success': False,
                'error': 'Invalid or expired verification token'
            }, status=status.HTTP_400_BAD_REQUEST)

class ResendVerificationView(APIView):
    """Resend verification Email"""
    permission_classes = [AllowAny]

    def post(self, request):
        email = request.data.get('email')

        if not email:
            return Response({
                'success': False,
                'error': 'Email required'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            user = User.objects.get(email=email, is_email_verified=False)

            user.email_verification_token = str(uuid.uuid4())
            user.save()

            send_verification_email(user, request)

            return Response({
                'success': True,
                'message': 'Verification email sent. Please check your inbox'
            })
        
        except User.DoesNotExist:
            return Response({
                'success': False,
                'error': 'User not found or already verified'
            }, status=status.HTTP_404_NOT_FOUND)

class PasswordResetRequestView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = PasswordResetRequestSerializer(data=request.data)

        if serializer.is_valid():
            email = serializer.validated_data['email']

            try:
                user = User.objects.get(email=email)
                send_password_reset_email(user, request)
            except User.DoesNotExist:
                # Don't reveal that user doesn't exist (security)
                pass

            return Response({
                'success': True,
                'message': 'If an account exists with this email, you will receive password reset instructions.'
            })
        
        return Response({
            'success': False,
            'errors': serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)

class PasswordResetConfirmView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = PasswordResetConfirmSerializer(data=request.data)

        if serializer.is_valid():
            token = serializer.validated_data['token']
            new_password = serializer.validated_data['new_password']

            try:
                user = User.objects.get(
                    reset_password_token=token,
                    reset_password_expires__gt=timezone.now()
                )

                user.set_password(new_password)
                user.reset_password_token = None
                user.reset_password_expires = None
                user.save()

                return Response({
                    'success': True,
                    'message': 'Password reset successful. You can now login with your new password'
                })
            except User.DoesNotExist:
                return Response({
                    'success': False,
                    'error': 'Invalid or expired reset token'
                }, status=status.HTTP_400_BAD_REQUEST)
        
        # FIXED: This return is now properly outside the if block
        return Response({
            'success': False,
            'errors': serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)

# ==================== PROTECTED ENDPOINTS ====================

class ProfileView(APIView):
    """Get or update user profile"""
    permission_classes = [IsAuthenticated]

    def get(self, request):
        serializer = UserSerializer(request.user)
        return Response({
            'success': True,
            'data': serializer.data
        })

    def put(self, request):
        serializer = UserSerializer(request.user, data=request.data, partial=False)
        
        if serializer.is_valid():
            serializer.save()
            return Response({
                'success': True,
                'message': 'Profile updated successfully',
                'data': serializer.data
            })
        
        return Response({
            'success': False,
            'errors': serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)

    def patch(self, request):
        serializer = UserSerializer(request.user, data=request.data, partial=True)
        
        if serializer.is_valid():
            serializer.save()
            return Response({
                'success': True,
                'message': 'Profile updated successfully',
                'data': serializer.data
            })
        
        return Response({
            'success': False,
            'errors': serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)

class ChangePasswordView(APIView):
    """Change user password"""
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = ChangePasswordSerializer(data=request.data)
        
        if serializer.is_valid():
            user = request.user
            
            if not user.check_password(serializer.validated_data['old_password']):
                return Response({
                    'success': False,
                    'error': 'Old password is incorrect'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            user.set_password(serializer.validated_data['new_password'])
            user.save()
            
            return Response({
                'success': True,
                'message': 'Password changed successfully'
            })
        
        return Response({
            'success': False,
            'errors': serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)

class LogoutView(APIView):
    """Logout user (blacklist refresh token)"""
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            refresh_token = request.data.get('refresh')
            if refresh_token:
                token = RefreshToken(refresh_token)
                token.blacklist()
            
            
            
            return Response({
                'success': True,
                'message': 'Logout successful'
            })
        except Exception as e:
            return Response({
                'success': False,
                'error': f'Invalid token: {str(e)}'
            }, status=status.HTTP_400_BAD_REQUEST)

class DeleteAccountView(APIView):
    """Delete user account"""
    permission_classes = [IsAuthenticated]

    def delete(self, request):
        # This will work with both JSON and form data
        password = request.data.get('password')
        
        # If DRF didn't parse it, try manual parsing
        if not password and request.body:
            try:
                import json
                body_data = json.loads(request.body)
                password = body_data.get('password')
            except:
                pass
        
        if not password:
            return Response({
                'success': False,
                'error': 'Password required'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        user = request.user
        
        if not user.check_password(password):
            return Response({
                'success': False,
                'error': 'Invalid password'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        user.delete()
        
        return Response({
            'success': True,
            'message': 'Account deleted successfully'
        })