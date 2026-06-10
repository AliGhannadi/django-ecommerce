from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from .serializers import ProductSerializer
from .models import Product


class ProductViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticatedOrReadOnly]
    serializer_class = ProductSerializer
    queryset = Product.objects.filter(is_published=True).select_related("user", "category")
