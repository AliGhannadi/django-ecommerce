from django.contrib import admin

from .models import Cart, CartItem


class CartItemInline(admin.TabularInline):
    model = CartItem
    extra = 0
    autocomplete_fields = ("product",)
    readonly_fields = ("created_date", "updated_date")


@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "created_date", "updated_date")
    list_filter = ("created_date", "updated_date")
    search_fields = ("user__email", "user__phone_number")
    autocomplete_fields = ("user",)
    readonly_fields = ("created_date", "updated_date")
    inlines = (CartItemInline,)


@admin.register(CartItem)
class CartItemAdmin(admin.ModelAdmin):
    list_display = ("cart", "product", "quantity", "created_date", "updated_date")
    list_filter = ("created_date", "updated_date")
    search_fields = ("cart__user__email", "product__title")
    autocomplete_fields = ("cart", "product")
    readonly_fields = ("created_date", "updated_date")
