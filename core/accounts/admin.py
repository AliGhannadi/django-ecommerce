from django.contrib.auth.admin import UserAdmin
from django.contrib import admin

from .models import Profile, User


class ProfileInline(admin.StackedInline):
    model = Profile
    extra = 0
    can_delete = False


class UserAdminConfig(UserAdmin):
    model = User
    search_fields = ("email", "phone_number", "username")
    list_filter = ("is_active", "is_staff", "is_verified", "created_date")
    ordering = ("-created_date",)
    list_display = (
        "email",
        "username",
        "phone_number",
        "is_active",
        "is_staff",
        "is_verified",
        "is_vendor",
        "created_date",
    )
    readonly_fields = ("created_date", "updated_date", "last_login")
    inlines = (ProfileInline,)
    fieldsets = (
        ("Authentication", {"fields": ("email", "username", "phone_number", "password")}),
        ("Permissions", {"fields": ("is_staff", "is_active", "is_verified", "is_vendor")}),
        (
            "Group Permissions",
            {
                "fields": (
                    "groups",
                    "user_permissions",
                )
            },
        ),
        ("Important dates", {"fields": ("last_login", "created_date", "updated_date")}),
    )
    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),
                "fields": (
                    "email",
                    "password1",
                    "password2",
                    "is_active",
                    "is_staff",
                    "is_verified",
                    "is_vendor",
                    "phone_number",
                    "username",
                ),
            },
        ),
    )


class ProfileAdminConfig(admin.ModelAdmin):
    model = Profile
    list_display = ("user", "first_name", "last_name", "created_date", "updated_date")
    search_fields = ("user__email", "user__phone_number", "first_name", "last_name")
    list_filter = ("created_date", "updated_date")
    readonly_fields = ("created_date", "updated_date")
    autocomplete_fields = ("user",)


admin.site.register(User, UserAdminConfig)
admin.site.register(Profile, ProfileAdminConfig)

