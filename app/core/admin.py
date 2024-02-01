"""
Django admin customization
"""

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.translation import gettext_lazy as _

from core import models

class UserAdmin(BaseUserAdmin):
    """Define admin for custom User model with no email field."""

    # Define fields for user list page
    ordering = ['id']
    list_display = ['email', 'name', 'is_superuser']

    # Define fields for edit user page
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        (
            _('Personal info'),
            {'fields': ('name',)}
        ),
        (
            _( 'Permissions'),
            {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}
        ),
        (
            _('Important dates'),
            {'fields': ('last_login',)}
        )
    )

    readonly_fields = ['last_login']

    # Define fields for add user page
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'password1', 'password2', 'name', 'is_active', 'is_staff', 'is_superuser')}
        ),
    )

admin.site.register(models.User, UserAdmin)