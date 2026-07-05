from django.contrib import admin

from .models import Payment, PaymentMethod


@admin.register(PaymentMethod)
class PaymentMethodAdmin(admin.ModelAdmin):
    list_display = ("name",)
    search_fields = ("name",)


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "method",
        "order",
        "amount",
        "is_successful",
        "created_date",
        "updated_date",
    )
    list_filter = ("method", "is_successful", "created_date", "updated_date")
    search_fields = ("order__user__email", "order__user__phone_number", "method__name")
    autocomplete_fields = ("method", "order")
    readonly_fields = ("created_date", "updated_date")


