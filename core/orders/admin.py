from django.contrib import admin

from .models import Order


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "user",
        "status",
        "city",
        "zipcode",
        "total_price",
        "coupon",
    )
    list_filter = ("status", "city", "coupon")
    search_fields = ("user__email", "user__phone_number", "address", "city", "zipcode")
    autocomplete_fields = ("user", "coupon")
