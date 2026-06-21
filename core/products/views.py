from rest_framework import viewsets, status
from rest_framework.permissions import IsAuthenticatedOrReadOnly, IsAuthenticated
from rest_framework.decorators import action
from rest_framework.response import Response
from .permissions import IsOwnerOrReadOnly, IsVendorOrReadOnly
from .serializers import ProductSerializer
from .models import Product
from cart.models import CartItem, Cart
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page

class ProductViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticatedOrReadOnly, IsOwnerOrReadOnly, IsVendorOrReadOnly]
    serializer_class = ProductSerializer
    queryset = Product.objects.filter(is_published=True).select_related("user", "category")
    
    @method_decorator(cache_page(60 * 15, key_prefix='product_list'))
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)
    
    @action(detail=True, methods=['POST'], permission_classes=[IsAuthenticated])
    def add_to_cart(self, request, pk=None):
        user = request.user
        product = self.get_object()
        cart, created = Cart.objects.get_or_create(user=user)
        cart_item, is_created = CartItem.objects.get_or_create(
        cart=cart,
        product=product   
        )
        if not is_created:
            cart_item.quantity += 1
            cart_item.save()
        return Response(
            {"detail": "Product added to cart successfully. "},
            status=status.HTTP_201_CREATED
        )
        
        
    