from django.db import models
from accounts.models import User
from products.models import Product
# Create your models here.
class Cart(models.Model):
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name="cart"
    )
    created_date = models.DateTimeField(auto_now_add=True)
    updated_date = models.DateTimeField(auto_now=True)
    
    @property
    def total_price(self):
        return sum(item.total_line_price for item in self.cartitems.all())

class CartItem(models.Model):
    cart = models.ForeignKey(
        Cart,
        on_delete=models.CASCADE,
        related_name="cartitems"
    )
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name="cartitems"
    )
    quantity = models.IntegerField(default=1)
    created_date = models.DateTimeField(auto_now_add=True)
    updated_date = models.DateTimeField(auto_now=True)
    
    @property
    def total_line_price(self):
        return self.quantity * self.product.price
    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["cart", "product"],
                name="unique_product_in_cart"
            )
        ]
    
    