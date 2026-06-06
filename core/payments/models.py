from django.db import models
from orders.models import Order

# Create your models here.
class PaymentMethod(models.Model):
    name = models.CharField(max_length=255)

class Payment(models.Model):
    method = models.ForeignKey(
        PaymentMethod,
        on_delete=models.CASCADE,
        related_name="payments"
    )
    amount = models.DecimalField(max_digits=20, decimal_places=6)
    order = models.ForeignKey(
        'orders.Order',
        on_delete=models.CASCADE,
        related_name="payments"
        
    )
    created_date = models.DateTimeField(auto_now_add=True)
    updated_date = models.DateTimeField(auto_now=True)
    is_successful = models.BooleanField(default=False)

class Coupon(models.Model):
    code = models.CharField(max_length=15)
    discount_percent = models.DecimalField(max_digits=3, decimal_places=2, default=0.00)
    max_limit = models.IntegerField()
    expiration_date = models.DateTimeField()
    created_date = models.DateTimeField(auto_now_add=True)
    updated_date = models.DateTimeField(auto_now=True)
    
    