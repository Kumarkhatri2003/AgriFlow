from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'profile', views.UserProfileViewSet, basename='user-profile')

urlpatterns = [
    # Authentication URLs
    path('register/', views.RegisterView.as_view(), name='register'),
    path('login/', views.LoginView.as_view(), name='login'),
    path('token/refresh/', views.CustomTokenRefreshView.as_view(), name='token_refresh'),
    path('verify-email/', views.VerifyEmailView.as_view(), name='verify_email'),
    path('resend-verification/', views.ResendVerificationView.as_view(), name='resend_verification'),
    
    # Password reset URLs
    path('password-reset/', views.PasswordResetRequestView.as_view(), name='password_reset'),
    path('password-reset/confirm/', views.PasswordResetConfirmView.as_view(), name='password_reset_confirm'),
    path('change-password/', views.ChangePasswordView.as_view(), name='change_password'),
    
    # Terms URLs
    path('check-terms/', views.CheckTermsAcceptanceView.as_view(), name='check_terms'),
    path('accept-terms/', views.AcceptTermsView.as_view(), name='accept_terms'),
    
    # Account management URLs
    path('logout/', views.LogoutView.as_view(), name='logout'),
    path('delete-account/', views.DeleteAccountView.as_view(), name='delete_account'),
    
    path('', include(router.urls)),
]