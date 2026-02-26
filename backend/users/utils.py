import uuid
from datetime import timedelta
from django.utils import timezone
from django.core.mail import send_mail
from django.conf import settings
from django.urls import reverse
from django.core.mail import EmailMultiAlternatives

def generate_token():
    """Generate unique token"""
    return str(uuid.uuid4())

def send_verification_email(user, request):
    """Send email verification link"""
    token = user.email_verification_token
    
    # Create verification link
    base_url = request.build_absolute_uri('/api/auth/verify-email/')
    verification_url = f"{base_url}?token={token}"
    
    subject = "Verify Your Email - AgriFlow"
    
    # Plain text version
    text_content = f"""
Hello {user.username or user.email},

Thank you for registering with AgriFlow!

Please verify your email address by clicking the link below:
{verification_url}

This link will expire in 24 hours.

If you didn't register for AgriFlow, please ignore this email.

Happy Farming! 🌱
AgriFlow Team
"""
    
    # HTML version
    html_content = f"""
<html>
<body style="font-family: Arial, sans-serif; line-height: 1.6;">
    <div style="max-width: 600px; margin: 0 auto; padding: 20px; border: 1px solid #ddd; border-radius: 10px;">
        <h2 style="color: #10B981;">Welcome to AgriFlow! 🌾</h2>
        <p>Hello <strong>{user.username or user.email}</strong>,</p>
        <p>Thank you for registering with AgriFlow. Please verify your email address by clicking the button below:</p>
        <div style="text-align: center; margin: 30px 0;">
            <a href="{verification_url}" style="background-color: #10B981; color: white; padding: 12px 30px; text-decoration: none; border-radius: 5px; font-weight: bold;">Verify Email</a>
        </div>
        <p>Or copy this link: <br><small>{verification_url}</small></p>
        <p>This link will expire in 24 hours.</p>
        <hr>
        <p style="color: #666; font-size: 0.9em;">Happy Farming! 🌱<br>AgriFlow Team</p>
    </div>
</body>
</html>
"""
    
    email = EmailMultiAlternatives(
        subject,
        text_content,
        settings.DEFAULT_FROM_EMAIL,
        [user.email]
    )
    email.attach_alternative(html_content, "text/html")
    email.send()
    
    print(f"✅ Verification email sent to {user.email}")
    print(f"🔗 Link: {verification_url}")

# ========== ADD THIS MISSING FUNCTION ==========
def send_password_reset_email(user, request):
    """Send password reset link"""
    token = generate_token()
    user.reset_password_token = token
    user.reset_password_expires = timezone.now() + timedelta(hours=24)
    user.save()
    
    # Create reset link
    base_url = request.build_absolute_uri('/reset-password/')
    reset_url = f"{base_url}?token={token}"
    
    subject = "Reset Your Password - AgriFlow"
    
    # Plain text version
    text_content = f"""
Hello {user.username or user.email},

You requested to reset your password for AgriFlow.

Click the link below to reset your password:
{reset_url}

This link will expire in 24 hours.

If you didn't request this, please ignore this email.

Happy Farming! 🌱
AgriFlow Team
"""
    
    # HTML version
    html_content = f"""
<html>
<body style="font-family: Arial, sans-serif; line-height: 1.6;">
    <div style="max-width: 600px; margin: 0 auto; padding: 20px; border: 1px solid #ddd; border-radius: 10px;">
        <h2 style="color: #10B981;">Password Reset - AgriFlow</h2>
        <p>Hello <strong>{user.username or user.email}</strong>,</p>
        <p>You requested to reset your password for AgriFlow. Click the button below to reset it:</p>
        <div style="text-align: center; margin: 30px 0;">
            <a href="{reset_url}" style="background-color: #10B981; color: white; padding: 12px 30px; text-decoration: none; border-radius: 5px; font-weight: bold;">Reset Password</a>
        </div>
        <p>Or copy this link: <br><small>{reset_url}</small></p>
        <p>This link will expire in 24 hours.</p>
        <hr>
        <p style="color: #666; font-size: 0.9em;">If you didn't request this, please ignore this email.</p>
        <p style="color: #666; font-size: 0.9em;">Happy Farming! 🌱<br>AgriFlow Team</p>
    </div>
</body>
</html>
"""
    
    email = EmailMultiAlternatives(
        subject,
        text_content,
        settings.DEFAULT_FROM_EMAIL,
        [user.email]
    )
    email.attach_alternative(html_content, "text/html")
    email.send()
    
    print(f"✅ Password reset email sent to {user.email}")
    print(f"🔗 Reset link: {reset_url}")