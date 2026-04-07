from django.urls import path
from . import views

urlpatterns = [
    # Public endpoints
    path('register/', views.RegisterView.as_view(), name='register'),
    
    path('terms/check/', views.CheckTermsAcceptanceView.as_view(), name='check-terms'),
    path('terms/accept/', views.AcceptTermsView.as_view(), name='accept-terms'),
    path('login/', views.LoginView.as_view(), name='login'),
    path('refresh-token/', views.RefreshTokenView.as_view(), name='refresh-token'),
    path('verify-email/', views.VerifyEmailView.as_view(), name='verify-email'),
    path('resend-verification/', views.ResendVerificationView.as_view(), name='resend-verification'),
    path('password-reset-request/', views.PasswordResetRequestView.as_view(), name='password-reset-request'),
    path('password-reset-confirm/', views.PasswordResetConfirmView.as_view(), name='password-reset-confirm'),
    
    # Protected endpoints 
    path('profile/', views.ProfileView.as_view(), name='profile'),
    path('change-password/', views.ChangePasswordView.as_view(), name='change-password'),
    path('logout/', views.LogoutView.as_view(), name='logout'),
    path('delete-account/', views.DeleteAccountView.as_view(), name='delete-account'),
    
]# users/urls.py
from django.urls import path
from . import views

urlpatterns = [
    # Public endpoints
    path('register/', views.RegisterView.as_view(), name='register'),
    path('login/', views.LoginView.as_view(), name='login'),
    path('refresh-token/', views.RefreshTokenView.as_view(), name='refresh-token'),
    path('verify-email/', views.VerifyEmailView.as_view(), name='verify-email'),
    path('resend-verification/', views.ResendVerificationView.as_view(), name='resend-verification'),
    path('password-reset-request/', views.PasswordResetRequestView.as_view(), name='password-reset-request'),
    path('password-reset-confirm/', views.PasswordResetConfirmView.as_view(), name='password-reset-confirm'),
    
    # Terms endpoints
    path('terms/check/', views.CheckTermsAcceptanceView.as_view(), name='check-terms'),
    path('terms/accept/', views.AcceptTermsView.as_view(), name='accept-terms'),
    
    # Protected endpoints 
    path('profile/', views.ProfileView.as_view(), name='profile'),
    path('change-password/', views.ChangePasswordView.as_view(), name='change-password'),
    path('logout/', views.LogoutView.as_view(), name='logout'),
    path('delete-account/', views.DeleteAccountView.as_view(), name='delete-account'),
]