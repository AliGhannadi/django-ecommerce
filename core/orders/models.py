from django.db import models
from accounts.models import User
from django.core.validators import RegexValidator
from django.core.exceptions import ValidationError
from django_countries.fields import CountryField
from cart.models import Cart
from decimal import Decimal

# Create your models here.

def zipcode_validator(value):
    if len(value) > 12:
        raise ValidationError("The length of zipcode must be lower than 12")

def address_validator(value):
    value = value.strip()

    if len(value) < 10:
        raise ValidationError(
            "Address must contain at least 10 characters."
        )
        
city_validator = RegexValidator(
    regex=r'^[A-Za-z\s]+$',
    message='City name should contain only letters.'
)

class Order(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="orders"
    )
    status = models.BooleanField(default=False)
    country = CountryField()
    city = models.CharField(max_length=100)
    zipcode = models.DecimalField(max_digits=12, decimal_places=0)
    address = models.TextField()
    total_price = models.DecimalField(max_digits=20, decimal_places=6)
    coupon = models.ForeignKey(
        'payments.Coupon',
        on_delete=models.SET_NULL,
        related_name="orders",
        null=True,
        blank=True
    )
    cart = models.ForeignKey(
        'cart.Cart',
        on_delete=models.SET_NULL,
        related_name="orders",
        null=True,
        blank=True
    )
    is_paid = models.BooleanField(default=False)
    
    
    @property
    def calculate_total_price(self):
        cart_items = self.cart.cartitems.all()
        
        total_price = Decimal('0.00')
        for cart_item in cart_items:
            product_price = cart_item.product.price
            quantity = getattr(cart_item, "quantity", 1)
            total_price += product_price * quantity
        return total_price
            
    @property
    def calculate_final_price(self):
        base_total = self.calculate_total_price
        if not self.coupon:
            return base_total
        discount_amount = base_total * Decimal(self.coupon.discount_percent) / Decimal("100")
        return base_total - discount_amount
    
    
    def save(self, *args, **kwargs):
        self.total_price = self.calculate_final_price
        
        super().save(*args, **kwargs)
        