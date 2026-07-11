from rest_framework import viewsets, status
from rest_framework.permissions import IsAuthenticated
from django.db.models import Q
from .serializers import CouponSerializer
from accounts.api.permissions import IsVerified
from coupons.models import Coupon
from rest_framework.decorators import action

class CouponViewSet(viewsets.ReadOnlyModelViewSet):
    permission_classes = [IsAuthenticated, IsVerified]
    serializer_class = CouponSerializer

    def get_queryset(self):
        user = self.request.user
        coupons = Coupon.objects.get_all_active_coupons()
        if user.is_staff:
            return coupons
        return coupons.filter(Q(is_general=True) | Q(user_assignments__user=user)).distinct()
    
    @action(detail=True, methods=["get"])
    def validate_coupon(self, request, pk=None):
        coupon = self.get_object()
        is_valid = coupon.is_valid()
        if is_valid:
            return Response({
            "valid": True,
            "message": "Coupon is verified",
            "discount_percent": coupon.discount_percent
        }, status=status.HTTP_200_OK)
        else:
           return Response({
            "valid": False,
            "message": "This code is expired"
        }, status=status.HTTP_400_BAD_REQUEST)
            
        
        