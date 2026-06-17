from rest_framework import serializers
from products.models import Product
from accounts.api.v1.serializers.users import UserSerializer


class ProductSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    absolute_url = serializers.SerializerMethodField()
    class Meta:
        model = Product
        fields = ("id", "title", "user", "category", "image", "description", "brief_description", "features", "price", "discount_rate","absolute_url",)
    def create(self, validated_data):
        request_user = self.context.get('request')
        user = request_user.user
        validated_data['user'] = user
        return super().create(validated_data)
    
    def get_absolute_url(self, obj):
        request = self.context.get("request")
        relative_url = obj.get_absolute_api_url()
        return request.build_absolute_uri(relative_url)
    