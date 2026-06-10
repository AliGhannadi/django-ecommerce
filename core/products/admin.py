from django.contrib import admin

from .models import Category, Product


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("name", "slug", "parent")
    list_filter = ("parent",)
    search_fields = ("name", "slug", "parent__name")
    autocomplete_fields = ("parent",)


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = (
        "title",
        "category",
        "user",
        "price",
        "discount_rate",
    )
    list_filter = ("category", "discount_rate")
    search_fields = (
        "title",
        "description",
        "brief_description",
        "category__name",
        "user__email",
    )
    autocomplete_fields = ("user", "category")
