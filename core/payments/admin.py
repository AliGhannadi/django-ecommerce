from django.contrib import admin

from .models import Payment


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "order",
        "is_successful",
        "created_date",
        "updated_date",
    )
    list_filter = ("is_successful", "created_date", "updated_date")
    search_fields = ("order__user__email", "order__user__phone_number")
    autocomplete_fields = ("order",)
    readonly_fields = ("created_date", "updated_date")


