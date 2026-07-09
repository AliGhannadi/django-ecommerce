from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from django.db.models import Q
from .serializers import CouponSerializer
from accounts.api.permissions import IsVerified
from coupons.models import Coupon


class CouponViewSet(viewsets.ReadOnlyModelViewSet):
    permission_classes = [IsAuthenticated, IsVerified]
    serializer_class = CouponSerializer

    def get_queryset(self):
        user = self.request.user
        coupons = Coupon.objects.get_all_active_coupons()
        if user.is_staff:
            return coupons
        return coupons.filter(Q(is_general=True) | Q(user_assignments__user=user)).distinct()
