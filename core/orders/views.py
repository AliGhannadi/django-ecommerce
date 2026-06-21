from django.shortcuts import render
from rest_framework import viewsets, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import action
from rest_framework.response import Response
from products.permissions import IsOwnerOrReadOnly, IsVendorOrReadOnly
from .serializers import OrderSerializer
from .models import Order
from cart.models import CartItem, Cart


# Create your views here.

########## Order
#### serializer for order
### gets information for order by user
### 

# View for order
# Serialize

class OrderViewSet(viewsets.ModelViewSet):
    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticated, IsOwnerOrReadOnly]
    queryset = Order.objects.all()
    
    