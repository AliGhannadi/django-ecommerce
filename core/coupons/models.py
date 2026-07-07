import random
import string
from datetime import timedelta
from django.db import models, transaction
from orders.models import Order
from django.utils import timezone
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError

User = get_user_model()
# Create your models here.

class UserCouponManager(models.Manager):
    def assign_unique_welcome_coupon(self, user):
        letters_and_digits = string.ascii_uppercase + string.digits
        coupon_code = ''.join(random.choices(letters_and_digits, k=8))
        with transaction.atomic():
            coupon = Coupon.objects.create(
                code=coupon_code,
                discount_percent=15.00,
                expiration_date=timezone.now() + timedelta(days=30),
                max_global_usage=1,   
                max_usage_per_user=1
            )
            user_coupon = self.create(user=user, coupon=coupon)
            
            return user_coupon

class CouponManager(models.Manager):
    def find_active_coupon(self, code):
        return self.filter(
            code=code,
            expiration_date__gt=timezone.now()
        ).first()
        
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

    def clean(self):
        super().clean()
        if self.current_usages >= self.max_global_usage:
            raise ValidationError({'current_usages': "This coupon has reached its maximum global usage limit."})
        if timezone.now() > self.expiration_date:
            raise ValidationError({'expiration_date': "This coupon has already expired."})
        
    def save(self, *args, **kwargs):
        self.full_clean() 
        super().save(*args, **kwargs)
        
    def redeem(self):
        with transaction.atomic():
            try:
                locked_coupon = Coupon.objects.select_for_update().get(pk=self.pk)
                if locked_coupon.current_usages >= locked_coupon.max_global_usage:
                        raise ValidationError("This coupon just reached its limit.")
                locked_coupon.current_usages += 1
                locked_coupon.save()
            except Coupon.DoesNotExist:
                raise ValidationError({'Not found': "This coupon cant be found"})

    objects = CouponManager()
    

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
    is_used = models.BooleanField(default=False)
    used_at = models.DateTimeField(auto_now=True, null=True,blank=True)
    
    objects = UserCouponManager()
    