from django.contrib import admin
from .models import Coupon, UserCoupon


@admin.register(Coupon)
class CouponAdmin(admin.ModelAdmin):
    list_display = (
        "code",
        "discount_percent",
        "max_global_usage",
        "current_usages",
        "is_general",
        "max_usage_per_user",
        "expiration_date",
        "created_date",
        "updated_date",
    )
    list_filter = ("expiration_date", "created_date", "updated_date")
    search_fields = ("code",)
    readonly_fields = ("created_date", "updated_date")


@admin.register(UserCoupon)
class UserCouponAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "coupon", "is_used", "used_at")
    list_filter = ("is_used", "used_at")
    search_fields = ("user__email", "coupon__code")
    autocomplete_fields = ("user", "coupon")