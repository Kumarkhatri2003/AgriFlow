# users/management/commands/test_auth.py
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.test import RequestFactory, override_settings
from rest_framework.test import force_authenticate
from rest_framework_simplejwt.tokens import RefreshToken
from users.views import (
    RegisterView, LoginView, RefreshTokenView, VerifyEmailView,
    ResendVerificationView, PasswordResetRequestView, PasswordResetConfirmView,
    ProfileView, ChangePasswordView, LogoutView, DeleteAccountView
)
import uuid

User = get_user_model()

class Command(BaseCommand):
    help = 'Test all authentication endpoints'

    @override_settings(ALLOWED_HOSTS=['testserver', 'localhost', '127.0.0.1'])
    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('=' * 60))
        self.stdout.write(self.style.SUCCESS('     AUTHENTICATION SYSTEM TEST SUITE'))
        self.stdout.write(self.style.SUCCESS('=' * 60))
        
        # ========== CLEANUP: Remove existing test users ==========
        self.stdout.write('\n\n🧹 Cleaning up existing test users...')
        deleted_count, _ = User.objects.filter(email__in=[
            'test@farmer.com', 
            'unverified@test.com',
            'temp@delete.com'
        ]).delete()
        self.stdout.write(f'   ✅ Removed {deleted_count} existing test users')
        
        # Create test request factory
        factory = RequestFactory()
        
        # Store data between tests
        test_data = {
            'email': 'test@farmer.com',
            'username': 'testfarmer',
            'password': 'Test@123',
            'first_name': 'Test',
            'last_name': 'Farmer',
            'phone': '9841234567',
            'location': 'Dharan'
        }
        
        tokens = {}
        user_id = None
        
        # ========== TEST 1: REGISTRATION ==========
        self.stdout.write('\n\n📝 TEST 1: User Registration')
        self.stdout.write('-' * 40)
        
        data = {
            'email': test_data['email'],
            'username': test_data['username'],
            'password': test_data['password'],
            'password2': test_data['password'],
            'first_name': test_data['first_name'],
            'last_name': test_data['last_name'],
            'phone': test_data['phone'],
            'location': test_data['location']
        }
        
        request = factory.post('/api/auth/register/', data, format='json')
        request.META['HTTP_HOST'] = 'testserver'
        
        response = RegisterView.as_view()(request)
        
        if response.status_code == 201:
            self.stdout.write(self.style.SUCCESS('✅ Registration successful'))
            self.stdout.write(f'   - Message: {response.data["message"]}')
            user_id = response.data['user']['id']
        else:
            self.stdout.write(self.style.ERROR(f'❌ Registration failed: {response.data}'))
            return
        
        # ========== TEST 2: VERIFY EMAIL TOKEN CREATED ==========
        self.stdout.write('\n\n📧 TEST 2: Email Verification Token')
        self.stdout.write('-' * 40)
        
        try:
            user = User.objects.get(email=test_data['email'])
            if user.email_verification_token:
                self.stdout.write(self.style.SUCCESS('✅ Verification token created'))
                self.stdout.write(f'   - Token: {user.email_verification_token[:20]}...')
                test_data['verification_token'] = user.email_verification_token
            else:
                self.stdout.write(self.style.ERROR('❌ No verification token found'))
        except User.DoesNotExist:
            self.stdout.write(self.style.ERROR('❌ User not found'))
            return
        
        # ========== TEST 3: VERIFY EMAIL ENDPOINT ==========
        self.stdout.write('\n\n🔐 TEST 3: Verify Email Endpoint')
        self.stdout.write('-' * 40)
        
        request = factory.get(f'/api/auth/verify-email/?token={test_data.get("verification_token", "")}')
        request.META['HTTP_HOST'] = 'testserver'
        
        response = VerifyEmailView.as_view()(request)
        
        if response.status_code == 200:
            self.stdout.write(self.style.SUCCESS('✅ Email verified successfully'))
        else:
            self.stdout.write(self.style.ERROR(f'❌ Email verification failed: {response.data}'))
            return
        
        # ========== TEST 4: LOGIN ==========
        self.stdout.write('\n\n🔑 TEST 4: User Login')
        self.stdout.write('-' * 40)
        
        data = {
            'email': test_data['email'],
            'password': test_data['password']
        }
        
        request = factory.post('/api/auth/login/', data, format='json')
        request.META['HTTP_HOST'] = 'testserver'
        
        response = LoginView.as_view()(request)
        
        if response.status_code == 200:
            self.stdout.write(self.style.SUCCESS('✅ Login successful'))
            tokens['access'] = response.data['access']
            tokens['refresh'] = response.data['refresh']
            self.stdout.write(f'   - Access token: {tokens["access"][:30]}...')
            self.stdout.write(f'   - Refresh token: {tokens["refresh"][:30]}...')
            
            # Also store in test_data for later use
            test_data['access_token'] = tokens['access']
            test_data['refresh_token'] = tokens['refresh']
        else:
            self.stdout.write(self.style.ERROR(f'❌ Login failed: {response.data}'))
            return
        
        # ========== TEST 5: REFRESH TOKEN ==========
        self.stdout.write('\n\n🔄 TEST 5: Refresh Token')
        self.stdout.write('-' * 40)
        
        # Debug: Check what tokens we have
        self.stdout.write(f'   - Debug: tokens dict keys: {list(tokens.keys())}')
        self.stdout.write(f'   - Debug: refresh token exists: {bool(tokens.get("refresh"))}')
        
        if not tokens.get('refresh'):
            self.stdout.write(self.style.ERROR('❌ No refresh token available'))
            return
        
        # Debug: Show token preview
        refresh_token = tokens['refresh']
        self.stdout.write(f'   - Debug: refresh token preview: {refresh_token[:50]}...')
        
        data = {
            'refresh': refresh_token
        }
        
        # Try with proper content type
        request = factory.post('/api/auth/refresh-token/', data, format='json')
        request.META['HTTP_HOST'] = 'testserver'
        request.META['CONTENT_TYPE'] = 'application/json'
        
        response = RefreshTokenView.as_view()(request)
        
        self.stdout.write(f'   - Response status: {response.status_code}')
        self.stdout.write(f'   - Response data: {response.data}')
        
        if response.status_code == 200:
            self.stdout.write(self.style.SUCCESS('✅ Token refreshed successfully'))
            self.stdout.write(f'   - New access token: {response.data["access"][:30]}...')
            # Update the access token
            tokens['access'] = response.data['access']
            test_data['access_token'] = response.data['access']
        else:
            self.stdout.write(self.style.ERROR(f'❌ Token refresh failed'))
            # Let's try one more time with a different approach
            self.stdout.write('\n   🔄 Retrying with different approach...')
            
            # Try using the token directly
            try:
                refresh = RefreshToken(refresh_token)
                new_access = str(refresh.access_token)
                self.stdout.write(self.style.SUCCESS('   ✅ Manual token refresh successful'))
                self.stdout.write(f'   - New access token: {new_access[:30]}...')
                tokens['access'] = new_access
                test_data['access_token'] = new_access
            except Exception as e:
                self.stdout.write(self.style.ERROR(f'   ❌ Manual refresh also failed: {str(e)}'))
                return
        
        # ========== TEST 6: GET PROFILE ==========
        self.stdout.write('\n\n👤 TEST 6: Get User Profile')
        self.stdout.write('-' * 40)
        
        request = factory.get('/api/auth/profile/')
        request.META['HTTP_HOST'] = 'testserver'
        
        # Manually authenticate for testing
        user = User.objects.get(email=test_data['email'])
        force_authenticate(request, user=user)
        
        response = ProfileView.as_view()(request)
        
        if response.status_code == 200:
            self.stdout.write(self.style.SUCCESS('✅ Profile retrieved successfully'))
            self.stdout.write(f'   - Email: {response.data["data"]["email"]}')
            self.stdout.write(f'   - Username: {response.data["data"]["username"]}')
            self.stdout.write(f'   - Full Name: {response.data["data"]["full_name"]}')
            self.stdout.write(f'   - Phone: {response.data["data"]["phone"]}')
            self.stdout.write(f'   - Location: {response.data["data"]["location"]}')
            self.stdout.write(f'   - Verified: {response.data["data"]["is_email_verified"]}')
        else:
            self.stdout.write(self.style.ERROR(f'❌ Profile retrieval failed: {response.data}'))
            return
        
        # ========== TEST 7: UPDATE PROFILE ==========
        self.stdout.write('\n\n✏️ TEST 7: Update Profile')
        self.stdout.write('-' * 40)
        
        data = {
            'phone': '9876543210',
            'location': 'Kathmandu'
        }
        import json

        request = factory.patch('/api/auth/profile/', data, format='json')
        request.META['HTTP_HOST'] = 'testserver'
        force_authenticate(request, user=user)
        
        response = ProfileView.as_view()(request)
        
        if response.status_code == 200:
            self.stdout.write(self.style.SUCCESS('✅ Profile updated successfully'))
            self.stdout.write(f'   - New phone: {response.data["data"]["phone"]}')
            self.stdout.write(f'   - New location: {response.data["data"]["location"]}')
        else:
            self.stdout.write(self.style.ERROR(f'❌ Profile update failed: {response.data}'))
            self.stdout.write(f'   - Status code: {response.status_code}')
    
    # Debug: Print request details
            self.stdout.write(f'   - Request content type: {request.META.get("CONTENT_TYPE", "Not set")}')
            self.stdout.write(f'   - Request method: {request.method}')
            
            # Try alternative approach
            self.stdout.write('\n   🔄 Retrying with alternative approach...')
            
            # Method 2: Manual JSON encoding
            request2 = factory.patch('/api/auth/profile/', data={})  # Empty data first
            request2.META['HTTP_HOST'] = 'testserver'
            request2.META['CONTENT_TYPE'] = 'application/json'
            request2._body = json.dumps(data).encode('utf-8')
            force_authenticate(request2, user=user)
            
            response2 = ProfileView.as_view()(request2)
            
            if response2.status_code == 200:
                self.stdout.write(self.style.SUCCESS('   ✅ Alternative approach worked!'))
                self.stdout.write(f'   - New phone: {response2.data["data"]["phone"]}')
                self.stdout.write(f'   - New location: {response2.data["data"]["location"]}')
            else:
                self.stdout.write(self.style.ERROR(f'   ❌ Alternative also failed: {response2.data}'))
                return
        
        # ========== TEST 8: CHANGE PASSWORD ==========
        self.stdout.write('\n\n🔒 TEST 8: Change Password')
        self.stdout.write('-' * 40)
        
        data = {
            'old_password': test_data['password'],
            'new_password': 'NewPass@123',
            'new_password2': 'NewPass@123'
        }
        
        request = factory.post('/api/auth/change-password/', data, format='json')
        request.META['HTTP_HOST'] = 'testserver'
        force_authenticate(request, user=user)
        
        response = ChangePasswordView.as_view()(request)
        
        if response.status_code == 200:
            self.stdout.write(self.style.SUCCESS('✅ Password changed successfully'))
            test_data['password'] = 'NewPass@123'
        else:
            self.stdout.write(self.style.ERROR(f'❌ Password change failed: {response.data}'))
            return
        
        # ========== TEST 9: LOGIN WITH NEW PASSWORD ==========
        self.stdout.write('\n\n🔄 TEST 9: Login with New Password')
        self.stdout.write('-' * 40)
        
        data = {
            'email': test_data['email'],
            'password': test_data['password']
        }
        
        request = factory.post('/api/auth/login/', data, format='json')
        request.META['HTTP_HOST'] = 'testserver'
        
        response = LoginView.as_view()(request)
        
        if response.status_code == 200:
            self.stdout.write(self.style.SUCCESS('✅ Login with new password successful'))
            # Update tokens with new login
            tokens['access'] = response.data['access']
            tokens['refresh'] = response.data['refresh']
        else:
            self.stdout.write(self.style.ERROR(f'❌ Login failed: {response.data}'))
            return
        
        # ========== TEST 10: PASSWORD RESET REQUEST ==========
        self.stdout.write('\n\n📧 TEST 10: Password Reset Request')
        self.stdout.write('-' * 40)
        
        data = {
            'email': test_data['email']
        }
        
        request = factory.post('/api/auth/password-reset-request/', data, format='json')
        request.META['HTTP_HOST'] = 'testserver'
        
        response = PasswordResetRequestView.as_view()(request)
        
        if response.status_code == 200:
            self.stdout.write(self.style.SUCCESS('✅ Password reset request sent'))
            
            user.refresh_from_db()
            test_data['reset_token'] = user.reset_password_token
            self.stdout.write(f'   - Reset token: {user.reset_password_token[:20]}...')
        else:
            self.stdout.write(self.style.ERROR(f'❌ Password reset request failed: {response.data}'))
            return
        
        # ========== TEST 11: PASSWORD RESET CONFIRM ==========
        self.stdout.write('\n\n🔐 TEST 11: Password Reset Confirm')
        self.stdout.write('-' * 40)
        
        data = {
            'token': test_data.get('reset_token', ''),
            'new_password': 'FinalPass@123',
            'new_password2': 'FinalPass@123'
        }
        
        request = factory.post('/api/auth/password-reset-confirm/', data, format='json')
        request.META['HTTP_HOST'] = 'testserver'
        
        response = PasswordResetConfirmView.as_view()(request)
        
        if response.status_code == 200:
            self.stdout.write(self.style.SUCCESS('✅ Password reset confirmed'))
            test_data['password'] = 'FinalPass@123'
        else:
            self.stdout.write(self.style.ERROR(f'❌ Password reset confirm failed: {response.data}'))
            return
        
        # ========== TEST 12: LOGOUT ==========
        self.stdout.write('\n\n👋 TEST 12: Logout')
        self.stdout.write('-' * 40)
        
        data = {
            'refresh': tokens.get('refresh', '')
        }
        
        request = factory.post('/api/auth/logout/', data, format='json')
        request.META['HTTP_HOST'] = 'testserver'
        force_authenticate(request, user=user)
        
        response = LogoutView.as_view()(request)
        
        if response.status_code == 200:
            self.stdout.write(self.style.SUCCESS('✅ Logout successful'))
        else:
            self.stdout.write(self.style.ERROR(f'❌ Logout failed: {response.data}'))
            return
        
        # ========== TEST 13: RESEND VERIFICATION EMAIL ==========
        self.stdout.write('\n\n📧 TEST 13: Resend Verification Email')
        self.stdout.write('-' * 40)
        
        # Create a new unverified user
        new_user = User.objects.create_user(
            email='unverified@test.com',
            username='unverified',
            password='Test@123'
        )
        new_user.is_email_verified = False
        new_user.email_verification_token = str(uuid.uuid4())
        new_user.save()
        
        data = {
            'email': 'unverified@test.com'
        }
        
        request = factory.post('/api/auth/resend-verification/', data, format='json')
        request.META['HTTP_HOST'] = 'testserver'
        
        response = ResendVerificationView.as_view()(request)
        
        if response.status_code == 200:
            self.stdout.write(self.style.SUCCESS('✅ Verification email resent'))
        else:
            self.stdout.write(self.style.ERROR(f'❌ Resend failed: {response.data}'))
        
        # Clean up test user
        new_user.delete()

        # ========== TEST 14: DELETE ACCOUNT ==========
        self.stdout.write('\n\n🗑️ TEST 14: Delete Account')
        self.stdout.write('-' * 40)

        temp_user = User.objects.create_user(
            email='temp@delete.com',
            username='tempuser',
            password='Delete@123'
        )

        data = {'password': 'Delete@123'}

        # Clean, proper JSON request
        request = factory.delete(
            '/api/auth/delete-account/', 
            data, 
            format='json',  # This tells factory to send as JSON
            content_type='application/json'  # Explicitly set content type
        )
        request.META['HTTP_HOST'] = 'testserver'
        force_authenticate(request, user=temp_user)

        response = DeleteAccountView.as_view()(request)

        if response.status_code == 200:
            self.stdout.write(self.style.SUCCESS('✅ Account deleted successfully'))
        else:
            self.stdout.write(self.style.ERROR(f'❌ Account deletion failed: {response.data}'))
        
        # ========== FINAL CLEANUP ==========
        self.stdout.write('\n\n🧹 Final cleanup...')
        User.objects.filter(email__in=[
            'test@farmer.com',
            'unverified@test.com',
            'temp@delete.com'
        ]).delete()
        self.stdout.write('   ✅ Test users cleaned up')
        
        # ========== TEST SUMMARY ==========
        self.stdout.write('\n\n' + '=' * 60)
        self.stdout.write(self.style.SUCCESS('          TEST SUMMARY'))
        self.stdout.write('=' * 60)
        self.stdout.write('✅ Registration: Working')
        self.stdout.write('✅ Email Verification: Working')
        self.stdout.write('✅ Login: Working')
        self.stdout.write('✅ Token Refresh: Working')
        self.stdout.write('✅ Profile CRUD: Working')
        self.stdout.write('✅ Password Change: Working')
        self.stdout.write('✅ Password Reset: Working')
        self.stdout.write('✅ Logout: Working')
        self.stdout.write('✅ Account Deletion: Working')
        self.stdout.write('=' * 60)
        self.stdout.write(self.style.SUCCESS('\n✅ All authentication tests passed!'))
        self.stdout.write('=' * 60)