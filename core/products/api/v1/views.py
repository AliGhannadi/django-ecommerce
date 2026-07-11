from rest_framework import viewsets, status
from rest_framework.permissions import IsAuthenticatedOrReadOnly, IsAuthenticated
from rest_framework.decorators import action
from rest_framework.response import Response
from products.permissions import IsOwnerOrReadOnly, IsVendorOrReadOnly
from products.api.v1.serializers import ProductSerializer
from products.models import Product
from cart.models import CartItem, Cart
from django.utils.decorators import method_decorator
from django.views.decorators.vary import vary_on_headers
from django.views.decorators.cache import cache_page
from ...pagination import Pagination
from django_filters.rest_framework import DjangoFilterBackend
from products.filters import ProductFilter
class ProductViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticatedOrReadOnly, IsOwnerOrReadOnly, IsVendorOrReadOnly]
    serializer_class = ProductSerializer
    pagination_class = Pagination
    filter_backends = [DjangoFilterBackend]
    filterset_class = ProductFilter
    queryset = Product.objects.filter(is_published=True).select_related("user", "category")

    @method_decorator(cache_page(60 * 5, key_prefix='product_list'))
    @method_decorator(vary_on_headers("Accept", "Accept-Language"))
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    @action(detail=True, methods=['POST'], permission_classes=[IsAuthenticated])
    def add_to_cart(self, request, pk=None):
        user = request.user
        product = self.get_object()
        try:
            quantity = int(request.data.get("quantity", 1))
            if quantity <= 0:
                return Response({"error": "Quantity must be greater than 0."}, status=status.HTTP_400_BAD_REQUEST)
        except (ValueError, TypeError):
            return Response({"error": "Invalid quantity format."}, status=status.HTTP_400_BAD_REQUEST)

        cart, created = Cart.objects.get_or_create(user=user)
        cart_item, is_created = CartItem.objects.get_or_create(
            cart=cart, product=product, defaults={"quantity": quantity}
        )

        if not is_created:
            cart_item.quantity += quantity
            cart_item.save()
        return Response(
            {"detail": f"Added {quantity} x '{product.title}' to your cart successfully."},
            status=status.HTTP_201_CREATED
        )
