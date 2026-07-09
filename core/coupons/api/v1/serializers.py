from rest_framework import serializers
from coupons.models import Coupon


class CouponSerializer(serializers.ModelSerializer):
    is_valid_coupon = serializers.SerializerMethodField()

    class Meta:
        model = Coupon
        fields = (
            "id", "code", "discount_percent", "expiration_date",
            "max_global_usage", "current_usages", "max_usage_per_user",
            "is_general", "is_valid_coupon",
        )
        read_only_fields = ("id", "current_usages")

    def get_is_valid_coupon(self, obj):
        return obj.is_valid()
