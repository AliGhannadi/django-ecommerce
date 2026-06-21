from rest_framework import serializers
from .models import Order
from django.core.exceptions import ValidationError
class OrderSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = ["id", "user", "status", "country", "city", "address", "zipcode", "total_price", "coupon", "cart", "total_price"]
        read_only_fields = ["id", "user", "cart", "total_price"]
    def create(self, validated_data):
        request = self.context.get("request")
        user = request.user
        cart = getattr(user, 'cart', None)
        if cart:
            validated_data["cart"] = cart
        else:
            raise serializers.ValidationError("You dont have on-going cart. create one first")
        
        if not cart.cartitems.exists():
            raise serializers.ValidationError("Your cart is empty. The order cant be processd.")
        
        validated_data["user"] = user
        validated_data["cart"] = cart
        return super().create(validated_data)

## We need a validation for coupon in orderserializer
