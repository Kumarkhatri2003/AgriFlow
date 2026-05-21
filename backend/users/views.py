from rest_framework import status, generics, viewsets, mixins
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.views import APIView
from rest_framework.decorators import action
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenRefreshView
from django.contrib.auth import logout as django_logout
from django.utils import timezone
from django.conf import settings

from users.permissions import IsAdminUser
from .utils import send_verification_email, send_password_reset_email
from .serializers import (
    RegisterSerializer, UserSerializer, LoginSerializer, 
    PasswordResetRequestSerializer, PasswordResetConfirmSerializer, 
    ChangePasswordSerializer, UpdateUserProfileSerializer, UserProfileSerializer,
     RoleUpdateSerializer, AdminUserCreateSerializer, UserListAdminSerializer

)
from .models import User
import uuid


# ==================== AUTHENTICATION VIEWS ====================

class RegisterView(generics.CreateAPIView):
    """User registration endpoint"""
    permission_classes = [AllowAny]
    serializer_class = RegisterSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        
        if serializer.is_valid():
            user = serializer.save()
            send_verification_email(user)

            return Response({
                'success': True,
                'message': 'Registration successful! Please check your email to verify your account.',
                'user': UserSerializer(user).data
            }, status=status.HTTP_201_CREATED)
        
        return Response({
            'success': False,
            'error': serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)


class LoginView(generics.GenericAPIView):
    """User login endpoint"""
    permission_classes = [AllowAny]
    serializer_class = LoginSerializer

    def post(self, request):
        serializer = self.get_serializer(data=request.data)

        if serializer.is_valid():
            # Generate notifications/reminders for the farmer on login if needed
            try:
                user_email = serializer.validated_data.get('user', {}).get('email')
                if user_email:
                    user = User.objects.get(email=user_email)
                    from notifications.utils import generate_user_alerts_and_reminders_if_needed
                    generate_user_alerts_and_reminders_if_needed(user)
            except Exception as e:
                print(f"Error generating alerts on login: {e}")

            return Response({
                'success': True,
                'message': 'Login successful',
                **serializer.validated_data
            })
        
        return Response({
            'success': False,
            'errors': serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)


class CustomTokenRefreshView(generics.GenericAPIView):
    """Refresh JWT token endpoint"""
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        refresh_token = request.data.get('refresh')
        
        print(f"Debug - Received refresh token: {refresh_token[:50] if refresh_token else 'None'}...")

        if not refresh_token:
            return Response({
                'success': False,
                'error': 'Refresh token required'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            # Create a RefreshToken object from the token string
            refresh = RefreshToken(refresh_token)
            
            # Get the new access token
            access_token = str(refresh.access_token)
            
            return Response({
                'success': True,
                'access': access_token
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            print(f"Debug - Refresh error: {str(e)}")
            return Response({
                'success': False,
                'error': f'Invalid refresh token: {str(e)}'
            }, status=status.HTTP_401_UNAUTHORIZED)


class VerifyEmailView(generics.GenericAPIView):
    """Email verification endpoint"""
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


class ResendVerificationView(generics.GenericAPIView):
    """Resend verification email endpoint"""
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


class PasswordResetRequestView(generics.GenericAPIView):
    """Password reset request endpoint"""
    permission_classes = [AllowAny]
    serializer_class = PasswordResetRequestSerializer

    def post(self, request):
        serializer = self.get_serializer(data=request.data)

        if serializer.is_valid():
            email = serializer.validated_data['email']

            try:
                user = User.objects.get(email=email)
                send_password_reset_email(user)
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


class PasswordResetConfirmView(generics.GenericAPIView):
    """Password reset confirmation endpoint"""
    permission_classes = [AllowAny]
    serializer_class = PasswordResetConfirmSerializer

    def post(self, request):
        serializer = self.get_serializer(data=request.data)

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
        
        return Response({
            'success': False,
            'errors': serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)


# ==================== USER PROFILE VIEWSET ====================

class UserProfileViewSet(mixins.RetrieveModelMixin,
                         mixins.UpdateModelMixin,
                         viewsets.GenericViewSet):
    """ViewSet for user profile operations"""
    permission_classes = [IsAuthenticated]
    serializer_class = UserProfileSerializer

    def get_object(self):
        return self.request.user

    def get_serializer_class(self):
        if self.action in ['update', 'partial_update']:
            return UpdateUserProfileSerializer
        return UserProfileSerializer

    def retrieve(self, request, *args, **kwargs):
        serializer = self.get_serializer(self.get_object())
        return Response({
            'success': True,
            'data': serializer.data
        })

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        
        if serializer.is_valid():
            serializer.save()
            profile_data = UserProfileSerializer(instance).data
            return Response({'success': True, 'data': profile_data})
        
        return Response({
            'success': False,
            'errors': serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)


# ==================== TERMS ACCEPTANCE VIEWS ====================

class CheckTermsAcceptanceView(generics.GenericAPIView):
    """Check if user has accepted latest terms"""
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        user = request.user
        current_terms_version = '1.0'
        current_privacy_version = '1.0'
        
        needs_terms_update = user.terms_version != current_terms_version
        needs_privacy_update = user.privacy_version != current_privacy_version
        
        return Response({
            'needs_terms_update': needs_terms_update,
            'needs_privacy_update': needs_privacy_update,
            'current_terms_version': current_terms_version,
            'current_privacy_version': current_privacy_version,
            'user_terms_version': user.terms_version,
            'user_privacy_version': user.privacy_version
        })


class AcceptTermsView(generics.GenericAPIView):
    """Accept latest terms"""
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        user = request.user
        terms_version = request.data.get('terms_version', '1.0')
        privacy_version = request.data.get('privacy_version', '1.0')
        
        user.terms_version = terms_version
        user.privacy_version = privacy_version
        user.terms_accepted_at = timezone.now()
        user.privacy_accepted_at = timezone.now()
        user.save()
        
        return Response({
            'success': True,
            'message': 'Terms accepted successfully'
        })


# ==================== PASSWORD MANAGEMENT ====================

class ChangePasswordView(generics.GenericAPIView):
    """Change user password"""
    permission_classes = [IsAuthenticated]
    serializer_class = ChangePasswordSerializer

    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        
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


# ==================== ACCOUNT MANAGEMENT ====================

class LogoutView(generics.GenericAPIView):
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


class DeleteAccountView(generics.DestroyAPIView):
    """Delete user account"""
    permission_classes = [IsAuthenticated]

    def get_object(self):
        return self.request.user

    def destroy(self, request, *args, **kwargs):
        password = request.data.get('password')
        
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
        
        user = self.get_object()
        
        if not user.check_password(password):
            return Response({
                'success': False,
                'error': 'Invalid password'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        self.perform_destroy(user)
        
        return Response({
            'success': True,
            'message': 'Account deleted successfully'
        })

    def perform_destroy(self, instance):
        instance.delete()
        
        
class ListUsersView(generics.ListAPIView):
    """List all users with role filtering (admin only)"""
    permission_classes = [IsAuthenticated, IsAdminUser]
    serializer_class = UserListAdminSerializer
    
    def get_queryset(self):
        queryset = User.objects.all().order_by('-date_joined')
        
        role = self.request.query_params.get('role')
        if role == 'admin':
            queryset = queryset.filter(is_admin=True)
        elif role == 'farmer':
            queryset = queryset.filter(is_farmer=True, is_admin=False)
        elif role == 'user':
            queryset = queryset.filter(is_admin=False, is_farmer=False)
        
        return queryset
    
    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        return Response({
            'success': True,
            'count': queryset.count(),
            'users': serializer.data
        })


class AdminUserCreateView(generics.CreateAPIView):
    """Create admin users (admin only)"""
    permission_classes = [IsAuthenticated, IsAdminUser]
    serializer_class = AdminUserCreateSerializer
    
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            return Response({
                'success': True,
                'message': 'Admin user created successfully',
                'user': UserSerializer(user).data
            }, status=status.HTTP_201_CREATED)
        return Response({
            'success': False,
            'errors': serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)


class UserRoleUpdateView(generics.GenericAPIView):
    """Update user role (admin only)"""
    permission_classes = [IsAuthenticated, IsAdminUser]
    serializer_class = RoleUpdateSerializer
    
    def patch(self, request, user_id):
        try:
            user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            return Response({
                'success': False,
                'error': 'User not found'
            }, status=status.HTTP_404_NOT_FOUND)
        
        # Prevent self role change
        if user.id == request.user.id:
            return Response({
                'success': False,
                'error': 'You cannot change your own role'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Prevent removing the last admin
        if user.is_admin and not request.data.get('is_admin', True):
            admin_count = User.objects.filter(is_admin=True).count()
            if admin_count <= 1:
                return Response({
                    'success': False,
                    'error': 'Cannot remove the last admin user'
                }, status=status.HTTP_400_BAD_REQUEST)
        
        serializer = self.get_serializer(data=request.data)
        
        if serializer.is_valid():
            validated_data = serializer.validated_data
            
            # Ensure cannot be both
            if validated_data.get('is_admin', False):
                user.is_admin = True
                user.is_farmer = False
            elif validated_data.get('is_farmer', False):
                user.is_farmer = True
                user.is_admin = False
            else:
                user.is_farmer = False
                user.is_admin = False
            
            user.save()
            
            # Log to admin_panel
            try:
                from admin_panel.models import AdminLog 
                AdminLog.objects.create(
                    admin_user=request.user,
                    action='UPDATE',
                    model_name='User',
                    object_id=str(user.id),
                    object_repr=user.get_full_name(),
                    changes={'new_role': 'admin' if user.is_admin else 'farmer' if user.is_farmer else 'user'},
                    ip_address=request.META.get('REMOTE_ADDR')
                )
            except ImportError:
                pass
            
            return Response({
                'success': True,
                'message': 'User role updated successfully',
                'user': {
                    'id': user.id,
                    'username': user.username,
                    'email': user.email,
                    'full_name': user.get_full_name(),
                    'is_farmer': user.is_farmer,
                    'is_admin': user.is_admin,
                    'user_type': 'admin' if user.is_admin else 'farmer' if user.is_farmer else 'user'
                }
            })
        
        return Response({
            'success': False,
            'errors': serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)


class PromoteToAdminView(generics.GenericAPIView):
    """Promote a farmer to admin (admin only)"""
    permission_classes = [IsAuthenticated, IsAdminUser]
    
    def post(self, request, user_id):
        try:
            user = User.objects.get(id=user_id, is_farmer=True, is_admin=False)
        except User.DoesNotExist:
            return Response({'error': 'Farmer not found'}, status=status.HTTP_404_NOT_FOUND)
        
        if user.id == request.user.id:
            return Response({'error': 'You are already an admin'}, status=status.HTTP_400_BAD_REQUEST)
        
        user.is_admin = True
        user.is_farmer = False
        user.save()
        
        return Response({
            'success': True,
            'message': f'{user.get_full_name()} has been promoted to Admin'
        })


class DemoteAdminView(generics.GenericAPIView):
    """Demote an admin to regular user (admin only)"""
    permission_classes = [IsAuthenticated, IsAdminUser]
    
    def post(self, request, user_id):
        try:
            user = User.objects.get(id=user_id, is_admin=True)
        except User.DoesNotExist:
            return Response({'error': 'Admin user not found'}, status=status.HTTP_404_NOT_FOUND)
        
        if user.id == request.user.id:
            return Response({'error': 'You cannot demote yourself'}, status=status.HTTP_400_BAD_REQUEST)
        
        if User.objects.filter(is_admin=True).count() <= 1:
            return Response({'error': 'Cannot demote the last admin user'}, status=status.HTTP_400_BAD_REQUEST)
        
        user.is_admin = False
        user.is_farmer = False
        user.save()
        
        return Response({
            'success': True,
            'message': f'{user.get_full_name()} has been demoted to regular user'
        })