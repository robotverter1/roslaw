from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import User


class CustomUserAdmin(UserAdmin):
    list_display = (
        "username",
        "get_full_name",
        "email",
        "role",
        "sex",
        "birth_date",
        "region",
        "organization",
        "position",
        "phone",
        "is_active",
    )
    list_filter = ("role", "sex", "region", "organization", "is_active")
    search_fields = (
        "username",
        "email",
        "first_name",
        "last_name",
        "patronymic",
        "organization",
        "region",
    )

    fieldsets = UserAdmin.fieldsets + (
        ("Роль и статус", {"fields": ("role",)}),
        (
            "Личная информация",
            {
                "fields": (
                    "patronymic",
                    "sex",
                    "birth_date",
                    "region",
                    "address",
                    "organization",
                    "position",
                    "phone",
                )
            },
        ),
    )

    add_fieldsets = UserAdmin.add_fieldsets + (
        ("Роль и статус", {"fields": ("role",)}),
        (
            "Личная информация",
            {
                "fields": (
                    "first_name",
                    "last_name",
                    "patronymic",
                    "sex",
                    "birth_date",
                    "region",
                    "address",
                    "organization",
                    "position",
                    "phone",
                    "email",
                )
            },
        ),
    )

    def get_full_name(self, obj):
        full_name = f"{obj.last_name} {obj.first_name}"
        if obj.patronymic:
            full_name += f" {obj.patronymic}"
        return full_name.strip()

    get_full_name.short_description = "ФИО"


admin.site.register(User, CustomUserAdmin)
