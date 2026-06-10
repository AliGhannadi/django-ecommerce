from django.db import models
from accounts.models import User
from products.models import Product
# Create your models here.
class WishList(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="wishlists"
    )
    products = models.ManyToManyField(Product, blank=True)
    created_date = models.DateTimeField(auto_now_add=True)
    updated_date = models.DateTimeField(auto_now=True)
    

class Comment(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="comments"
    )
    message = models.CharField(max_length=255)
    is_published = models.BooleanField(default=False)
    class Meta:
        verbose_name_plural = "Comments"