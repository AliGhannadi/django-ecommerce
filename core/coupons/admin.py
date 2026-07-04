from django.contrib import admin
from .models import Coupon
# Register your models here.

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