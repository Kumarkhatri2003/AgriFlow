from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User


@admin.register(User)
class UserAdmin(BaseUserAdmin):

    # Fields shown in the user list page
    list_display = (
        'email',
        'username',
        'is_farmer',
        'is_admin',
        'is_staff',
        'is_active',
        'is_email_verified',
        'created_at'
    )

    list_filter = (
        'is_farmer',
        'is_admin',
        'is_staff',
        'is_active',
        'is_email_verified'
    )

    search_fields = ('email', 'username', 'phone')
    ordering = ('-created_at',)

    # Field layout inside admin edit page
    fieldsets = (
        ('Authentication', {
            'fields': ('email', 'username', 'password')
        }),

        ('Personal Info', {
            'fields': ('first_name', 'last_name', 'phone', 'location', 'profile_picture')
        }),

        ('Roles', {
            'fields': ('is_farmer', 'is_admin', 'is_staff', 'is_superuser', 'is_active')
        }),

        ('Email Verification', {
            'fields': ('is_email_verified', 'email_verification_token')
        }),

        ('Password Reset', {
            'fields': ('reset_password_token', 'reset_password_expires')
        }),

        ('Permissions', {
            'fields': ('groups', 'user_permissions')
        }),

        ('Important Dates', {
            'fields': ('last_login', 'created_at', 'updated_at')
        }),
    )

    # Fields shown while creating a new user in admin
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': (
                'email',
                'username',
                'password1',
                'password2',
                'is_farmer',
                'is_admin',
                'is_staff',
                'is_active',
            ),
        }),
    )