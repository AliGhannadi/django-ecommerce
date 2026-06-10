from django.contrib import admin

from .models import Comment, WishList


@admin.register(WishList)
class WishListAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "created_date", "updated_date")
    list_filter = ("created_date", "updated_date")
    search_fields = ("user__email", "user__phone_number", "products__title")
    autocomplete_fields = ("user", "products")
    readonly_fields = ("created_date", "updated_date")


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "message", "is_published")
    list_filter = ("is_published",)
    search_fields = ("user__email", "user__phone_number", "message")
    autocomplete_fields = ("user",)
