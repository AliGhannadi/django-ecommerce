from django.urls import include, path
from rest_framework.routers import DefaultRouter
from coupons.api.v1.views import CouponViewSet

router = DefaultRouter()
router.register(r"", CouponViewSet, basename="coupon")

urlpatterns = [
    path("", include(router.urls))
]
