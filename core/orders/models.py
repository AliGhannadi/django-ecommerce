from django.db import models
from accounts.models import User
# Create your models here.

class Order(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="orders"
    )
    status = models.BooleanField(default=False)
    address = models.CharField(max_length=200)
    zipcode = models.DecimalField(max_digits=9, decimal_places=0)
    city = models.CharField(max_length=200)
    total_price = models.DecimalField(max_digits=20, decimal_places=6)
    coupon = models.ForeignKey(
        'payments.Coupon',
        on_delete=models.SET_NULL,
        related_name="orders",
        null=True,
        blank=True
    )
    