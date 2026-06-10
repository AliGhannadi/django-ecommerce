from rest_framework import serializers
from products.models import Product
from accounts.api.v1.serializers.users import UserSerializer


class ProductSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    class Meta:
        model = Product
        fields = ("id", "title", "user", "category", "image", "description", "brief_description", "features", "price", "discount_rate",)
    def create(self, validated_data):
        request_user = self.context.get('request')
        user = request_user.user
        validated_data['user'] = user
        return super().create(validated_data)
    