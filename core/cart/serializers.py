from rest_framework import serializers

from products.models import Product
from products.serializers import ProductSerializer
from .models import Cart, CartItem



class CartIitemSerializer(serializers.ModelSerializer):
    product = serializers.PrimaryKeyRelatedField(
        queryset=Product.objects.filter(is_published=True)
    )
    product_detail = ProductSerializer(source="product", read_only=True)
    
    class Meta:
        model = CartItem
        fields = (
            "id",
            "product",
            "product_detail",
            "quantity",
            "total_line_price",
            "created_date",
            "updated_date",
        )
        read_only_fields = ("id", "line_total", "created_date", "updated_date")
    def validate(self, attrs): # Object level validation
          product = attrs.get("product")
          quantity = attrs.get("quantity")
          if quantity < 1:     
            raise serializers.ValidationError("Quantity must be at least 1.")
          if quantity > product.quantity:
            raise serializers.ValidationError("Out of stock for the provided number.")
          return attrs
        
# Cart Serializer

class CartSerializer(serializers.ModelSerializer):
    cartitems = CartIitemSerializer(read_only=True, many=True)
    
    class Meta:
        model = Cart
        fields = ("user", "cartitems", "total_price", "created_date", "updated_date")
        read_only_fields = ("user", "cartitems", "total_price", "created_date", "updated_date")
# cart item serializer

