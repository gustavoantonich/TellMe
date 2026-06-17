from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User


class CustomUserAdmin(UserAdmin):
    fieldsets = UserAdmin.fieldsets + (
        ("Información adicional", {
            "fields": ("bio", "avatar", "location", "website", "created_at"),
        }),
    )
    readonly_fields = ("created_at",)


admin.site.register(User, CustomUserAdmin)
