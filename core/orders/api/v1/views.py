from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from orders.api.v1.serializers import OrderSerializer
from orders.models import Order


class OrderViewSet(viewsets.ModelViewSet):
    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Order.objects.filter(user=self.request.user)
