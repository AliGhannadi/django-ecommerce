from django.db import models
from orders.models import Order
from django.utils import timezone
from django.contrib.auth import get_user_model

User = get_user_model()
# Create your models here.
# class PaymentMethod(models.Model):
#     name = models.CharField(max_length=255)


class Transaction(models.Model):
    class Status(models.TextChoices):
        PENDING = 'pending', 'Pending'
        COMPLETED = 'completed', 'Completed'
        FAILED = 'failed', 'Failed'
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='transactions')
    description = models.TextField()
    authority = models.CharField(max_length=100, unique=True)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.PENDING)
    created_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Transaction: {self.id} - {self.authority[:10]}... ({self.status})"

class Payment(models.Model):
    order = models.OneToOneField(
        'orders.Order',
        on_delete=models.CASCADE,
        related_name="payments"
        
    )
    transaction = models.OneToOneField(
        Transaction,
        on_delete=models.CASCADE,
        related_name="payments"
    )
    created_date = models.DateTimeField(auto_now_add=True)
    updated_date = models.DateTimeField(auto_now=True)
    is_successful = models.BooleanField(default=False)
    
    def __str__(self):
        return f"Payment {self.id} for Order {self.order_id} - Success: {self.is_successful}"

