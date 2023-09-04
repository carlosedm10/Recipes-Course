"""
Django admin customization
"""

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.translation import gettext_lazy as _

from core import models


class UserAdmin(BaseUserAdmin):
    """Define the admin pages for users."""

    ordering = ["id"]
    list_display = ["email", "name"]
    fieldsets = (
        (None, {"fields": ("email", "password")}),  # first fieldset
        (_("Permissions"), {"fields": ("is_active", "is_staff", "is_superuser")}),
        (_("Important dates"), {"fields": ("last_login",)}),  # last fieldset
    )
    readonly_fields = ("last_login",)  # make last_login read only
    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),  # this changes the style of the form
                "fields": (
                    "email",
                    "password1",
                    "password2",
                    "name",
                    "is_active",
                    "is_staff",
                    "is_superuser",
                ),
            },
        ),  # first fieldset
    )


admin.site.register(models.User, UserAdmin)
admin.site.register(models.Recipe)

# Register your models here.
