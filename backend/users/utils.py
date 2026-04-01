# auth/utils.py
import uuid
from datetime import timedelta
from django.utils import timezone
from django.core.mail import EmailMultiAlternatives
from django.conf import settings

def generate_token():
    """Generate unique token"""
    return str(uuid.uuid4())

def get_frontend_url():
    """Get frontend URL from settings"""
    return getattr(settings, 'FRONTEND_URL', 'http://localhost:5173')

def send_verification_email(user, request=None):
    """Send email verification link"""
    token = user.email_verification_token
    
    # Get frontend URL
    frontend_url = get_frontend_url()
    verification_url = f"{frontend_url}/verify-email?token={token}"
    
    subject = "Verify Your Email - AgriFlow"
    
    # Plain text version
    text_content = f"""
Hello {user.get_full_name() or user.username or user.email},

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
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
</head>
<body style="font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; line-height: 1.6; margin: 0; padding: 20px; background-color: #f4f4f4;">
    <div style="max-width: 600px; margin: 0 auto; background: #ffffff; border-radius: 16px; overflow: hidden; box-shadow: 0 4px 20px rgba(0,0,0,0.1);">
        <div style="background: linear-gradient(135deg, #10B981 0%, #059669 100%); padding: 40px 30px; text-align: center;">
            <div style="width: 60px; height: 60px; background: white; border-radius: 30px; display: inline-flex; align-items: center; justify-content: center; margin-bottom: 20px;">
                <span style="font-size: 32px;">🌾</span>
            </div>
            <h1 style="color: white; margin: 0; font-size: 28px; font-weight: bold;">AgriFlow</h1>
            <p style="color: rgba(255,255,255,0.9); margin: 10px 0 0;">Smart Farming Solutions</p>
        </div>
        
        <div style="padding: 40px 30px;">
            <h2 style="color: #333; margin-top: 0; font-size: 24px;">Welcome to AgriFlow!</h2>
            <p style="color: #666; font-size: 16px;">Hello <strong style="color: #10B981;">{user.get_full_name() or user.username or user.email}</strong>,</p>
            <p style="color: #666; font-size: 16px;">Thank you for registering with AgriFlow. Please verify your email address to get started with smart farming solutions.</p>
            
            <div style="text-align: center; margin: 35px 0;">
                <a href="{verification_url}" style="background-color: #10B981; color: white; padding: 14px 35px; text-decoration: none; border-radius: 8px; font-weight: 600; font-size: 16px; display: inline-block; box-shadow: 0 2px 8px rgba(16,185,129,0.3);">
                    Verify Email Address
                </a>
            </div>
            
            <div style="background-color: #f8f9fa; padding: 15px; border-radius: 8px; margin: 20px 0;">
                <p style="color: #666; font-size: 13px; margin: 0; word-break: break-all;">
                    <strong>Or copy this link:</strong><br>
                    <a href="{verification_url}" style="color: #10B981; text-decoration: none;">{verification_url}</a>
                </p>
            </div>
            
            <p style="color: #999; font-size: 13px; margin: 20px 0 0;">This link will expire in 24 hours.</p>
            
            <hr style="margin: 30px 0 20px; border: none; border-top: 1px solid #eee;">
            
            <p style="color: #999; font-size: 13px; margin: 0;">
                If you didn't create an account with AgriFlow, please ignore this email.
            </p>
            <p style="color: #999; font-size: 13px; margin: 10px 0 0;">
                Happy Farming! 🌱<br>
                <strong style="color: #10B981;">AgriFlow Team</strong>
            </p>
        </div>
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
    print(f"🔗 Verification link: {verification_url}")

def send_password_reset_email(user, request=None):
    """Send password reset link"""
    token = generate_token()
    user.reset_password_token = token
    user.reset_password_expires = timezone.now() + timedelta(hours=24)
    user.save()
    
    # Get frontend URL
    frontend_url = get_frontend_url()
    reset_url = f"{frontend_url}/reset-password?token={token}"
    
    subject = "Reset Your Password - AgriFlow"
    
    # Plain text version
    text_content = f"""
Hello {user.get_full_name() or user.username or user.email},

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
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
</head>
<body style="font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; line-height: 1.6; margin: 0; padding: 20px; background-color: #f4f4f4;">
    <div style="max-width: 600px; margin: 0 auto; background: #ffffff; border-radius: 16px; overflow: hidden; box-shadow: 0 4px 20px rgba(0,0,0,0.1);">
        <div style="background: linear-gradient(135deg, #10B981 0%, #059669 100%); padding: 40px 30px; text-align: center;">
            <div style="width: 60px; height: 60px; background: white; border-radius: 30px; display: inline-flex; align-items: center; justify-content: center; margin-bottom: 20px;">
                <span style="font-size: 32px;">🔐</span>
            </div>
            <h1 style="color: white; margin: 0; font-size: 28px; font-weight: bold;">Password Reset</h1>
            <p style="color: rgba(255,255,255,0.9); margin: 10px 0 0;">AgriFlow Account Security</p>
        </div>
        
        <div style="padding: 40px 30px;">
            <h2 style="color: #333; margin-top: 0; font-size: 24px;">Reset Your Password</h2>
            <p style="color: #666; font-size: 16px;">Hello <strong style="color: #10B981;">{user.get_full_name() or user.username or user.email}</strong>,</p>
            <p style="color: #666; font-size: 16px;">We received a request to reset the password for your AgriFlow account. Click the button below to create a new password:</p>
            
            <div style="text-align: center; margin: 35px 0;">
                <a href="{reset_url}" style="background-color: #10B981; color: white; padding: 14px 35px; text-decoration: none; border-radius: 8px; font-weight: 600; font-size: 16px; display: inline-block; box-shadow: 0 2px 8px rgba(16,185,129,0.3);">
                    Reset Password
                </a>
            </div>
            
            <div style="background-color: #f8f9fa; padding: 15px; border-radius: 8px; margin: 20px 0;">
                <p style="color: #666; font-size: 13px; margin: 0; word-break: break-all;">
                    <strong>Or copy this link:</strong><br>
                    <a href="{reset_url}" style="color: #10B981; text-decoration: none;">{reset_url}</a>
                </p>
            </div>
            
            <p style="color: #999; font-size: 13px; margin: 20px 0 0;">This link will expire in 24 hours.</p>
            
            <hr style="margin: 30px 0 20px; border: none; border-top: 1px solid #eee;">
            
            <p style="color: #999; font-size: 13px; margin: 0;">
                If you didn't request a password reset, please ignore this email. Your password will remain unchanged.
            </p>
            <p style="color: #999; font-size: 13px; margin: 10px 0 0;">
                Happy Farming! 🌱<br>
                <strong style="color: #10B981;">AgriFlow Team</strong>
            </p>
        </div>
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