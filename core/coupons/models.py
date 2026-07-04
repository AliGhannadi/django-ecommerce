from django.db import models
from django.db import models
from orders.models import Order
from django.utils import timezone
from django.contrib.auth import get_user_model
User = get_user_model()
# Create your models here.
class Coupon(models.Model):
    code = models.CharField(max_length=15)
    discount_percent = models.DecimalField(max_digits=3, decimal_places=2, default=0.00)
    expiration_date = models.DateTimeField()
    max_global_usage = models.PositiveIntegerField(default=1)
    current_usages = models.PositiveIntegerField(default=0)
    max_usage_per_user = models.PositiveIntegerField(default=1)
    is_general = models.BooleanField(default=False)
    created_date = models.DateTimeField(auto_now_add=True)
    updated_date = models.DateTimeField(auto_now=True)
    def is_valid(self):
        """Helper to quickly check if the coupon itself is still active."""
        if timezone.now() > self.expiration_date:
            return False
        if self.current_usages >= self.max_global_usages:
            return False
        return True

class UserCoupon(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="assigned_coupons"
    )
    coupon = models.ForeignKey(
            Coupon,
            on_delete=models.CASCADE,
            related_name="user_assignments"
    )
    
    