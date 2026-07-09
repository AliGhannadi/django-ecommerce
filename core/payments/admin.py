from django.contrib import admin

from .models import Payment, Transaction


@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "user",
        "authority",
        "status",
        "created_date",
    )
    list_filter = ("status", "created_date")
    search_fields = ("user__email", "user__phone_number", "authority")
    readonly_fields = ("created_date",)


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


