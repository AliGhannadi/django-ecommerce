import django_filters
from django.db import models
from products.models import Product


class ProductFilter(django_filters.FilterSet):
    min_price = django_filters.NumberFilter(field_name="price", lookup_expr="gte")
    max_price = django_filters.NumberFilter(field_name="price", lookup_expr="lte")
    category_name = django_filters.CharFilter(field_name="category__name", lookup_expr="icontains")
    min_discount = django_filters.NumberFilter(field_name="discount_rate", lookup_expr="gte")
    max_discount = django_filters.NumberFilter(field_name="discount_rate", lookup_expr="lte")
    min_quantity = django_filters.NumberFilter(field_name="quantity", lookup_expr="gte")
    max_quantity = django_filters.NumberFilter(field_name="quantity", lookup_expr="lte")
    in_stock = django_filters.BooleanFilter(method="filter_in_stock")
    search = django_filters.CharFilter(method="filter_search")

    class Meta:
        model = Product
        fields = {
            "category": ["exact"],
            "title": ["exact", "icontains"],
            "is_published": ["exact"],
            "user": ["exact"],
        }

    def filter_in_stock(self, queryset, name, value):
        if value:
            return queryset.filter(quantity__gt=0)
        return queryset.filter(quantity=0)

    def filter_search(self, queryset, name, value):
        return queryset.filter(
            models.Q(title__icontains=value)
            | models.Q(description__icontains=value)
            | models.Q(brief_description__icontains=value)
        )
