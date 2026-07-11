from rest_framework import status, viewsets, mixins
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import action
from rest_framework.response import Response
from cart.api.v1.serializers import CartSerializer
from cart.models import CartItem, Cart
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from django.shortcuts import redirect
from django.db import transaction

class CartViewSet(mixins.ListModelMixin, viewsets.GenericViewSet):
    permission_classes = [IsAuthenticated]
    serializer_class = CartSerializer

    def get_queryset(self):
        return Cart.objects.filter(user=self.request.user).prefetch_related("cartitems__product")
    
    @method_decorator(cache_page(60 * 15, key_prefix='cart_list'))
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    @action(detail=False, methods=["patch"])
    def update_item(self, request):
        item_id = request.data.get("item_id")
        quantity = int(request.data.get("quantity"))
        try:
            with transaction.atomic():
                    item = CartItem.objects.get(id=item_id, cart__user=request.user)
                    item.quantity = quantity
                    item.save()
                    return Response({"detail": "Quantity updated"}, status=status.HTTP_200_OK)
        except CartItem.DoesNotExist:
                    return Response({"error": "Cart item not found"}, status=status.HTTP_404_NOT_FOUND)
            
    @action(detail=False, methods=["delete"])
    def delete_item(self, request):
        item_id = request.data.get("item_id")
        try:
            with transaction.atomic():
                item = CartItem.objects.get(id=item_id, cart__user=request.user)
                item.delete()
                return Response({"detail": "Item deleted"}, status=status.HTTP_200_OK)
        except CartItem.DoesNotExist:
                    return Response({"error": "Cart item not found"}, status=status.HTTP_404_NOT_FOUND)
            
    @action(detail=False, methods=["delete"])
    def clear(self, request):
        with transaction.atomic():
            cart = request.user.cart
            cart.cartitems.all().delete()
            return Response({"message": "Cart cleared"})

    @action(detail=False, methods=["get"])
    def add_to_order(self, request):
        return redirect('/orders/')
