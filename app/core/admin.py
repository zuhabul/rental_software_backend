from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from core import models
from django.utils.translation import gettext_lazy as _


class UserAdmin(BaseUserAdmin):
    ordering = ["email"]
    list_display = ["email", "created_at", "updated_at"]
    list_filter = ("is_active", "is_staff", "is_superuser")
    search_fields = ("email",)
    fieldsets = (
        (None, {"fields": ("email", "password")}),
        (
            _("Permissions"),
            {
                "fields": (
                    "is_active",
                    "is_staff",
                    "is_superuser",
                    "groups",
                )
            },
        ),
        (_("Important dates"), {"fields": ("last_login",)}),
    )
    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),
                "fields": ("email", "password1", "password2", "groups"),
            },
        ),
    )


admin.site.site_header = "Rental Software"
admin.site.register(models.User, UserAdmin)
admin.site.register(models.ProductModel)
