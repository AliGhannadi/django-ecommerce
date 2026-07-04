from django.db import models
from orders.models import Order
from django.utils import timezone
from django.contrib.auth import get_user_model

User = get_user_model()
# Create your models here.
class PaymentMethod(models.Model):
    name = models.CharField(max_length=255)

# A model for transaction

class Transaction(models.Model):
    email = models.EmailField()
    phone_number = models.CharField(max_length=15)
    description = models.TextField()
    merchent_id = models.TextField()
    authority = models.CharField(max_length=100)
    status = models.CharField(max_length=20)


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
    transaction = models.ForeignKey(
        Transaction,
        on_delete=models.CASCADE,
        related_name="payments"
    )
    created_date = models.DateTimeField(auto_now_add=True)
    updated_date = models.DateTimeField(auto_now=True)
    is_successful = models.BooleanField(default=False)

