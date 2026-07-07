
from django.shortcuts import render
from rest_framework import viewsets, status, mixins
from rest_framework.permissions import IsAuthenticated
from .permissions import IsOwner
from rest_framework.decorators import action
from rest_framework.response import Response
from .serializers import CartSerializer
from cart.models import CartItem, Cart
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from django.shortcuts import redirect, render
# Create your views here.
class CartViewSet(mixins.ListModelMixin, viewsets.GenericViewSet):
    permission_classes = [IsAuthenticated, IsOwner]
    serializer_class = CartSerializer
    def get_queryset(self):
        return Cart.objects.filter(user=self.request.user).prefetch_related("cartitems__product")
    
    @method_decorator(cache_page(60 * 15, key_prefix='cart_list'))
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)
    
    @action(detail=False, methods=["patch"])
    def update_item(self, request):
        item_id = request.data.get("item_id")
        quantity = request.data.get("quantity")
        item = CartItem.objects.get(
            id=item_id,
            cart__user=request.user
        )
        item.quantity = quantity
        item.save()
        return Response({"detail": "Quantity updated"}, status=status.HTTP_200_OK)
    
    @action(detail=False, methods=["delete"])
    def delete_item(self, request):
        item_id = request.data.get("item_id")
        item = CartItem.objects.get(
            id=item_id,
            cart__user=request.user
        )
        item.delete()
        
        return Response({"detail": "Item deleted"}, status=status.HTTP_200_OK)
    
    @action(detail=False, methods=["delete"])
    def clear(self, request):
        cart = request.user.cart
        cart.cartitems.all().delete()
        return Response({"message": "Cart cleared"})
    
    @action(detail=False, methods=["get"])
    def add_to_order(self, request):
        return redirect('/orders/')
        
    
    