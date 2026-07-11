from rest_framework import serializers
from orders.models import Order


class OrderSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = ["id", "user", "status", "country", "city", "address", "zipcode", "total_price", "coupon", "cart"]
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
    
    def validate_coupon(self, value):
            if value and not value.is_valid():
                raise serializers.ValidationError("The coupon is not valid")
            value.redeem()
            return value
