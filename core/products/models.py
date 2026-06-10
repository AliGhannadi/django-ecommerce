from django.db import models
from accounts.models import User

# Create your models here.
class Category(models.Model):
    slug = models.CharField(max_length=30)
    name = models.CharField(max_length=200)
    parent = models.ForeignKey(
        'self',
        on_delete=models.CASCADE,
        related_name="categories",
        null=True,
        blank=True
        )
    class Meta:
        verbose_name_plural = "Categories"
    
class Product(models.Model):
    title = models.CharField(max_length=255)
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="products"
    )
    category = models.ForeignKey(
        Category,
        on_delete=models.CASCADE,
        related_name="products"
    )
    image = models.ImageField(upload_to="product_images/")
    description = models.TextField()
    brief_description = models.CharField(max_length=255)
    features = models.JSONField(default=list)
    price = models.DecimalField(max_digits=20, decimal_places=6)
    discount_rate = models.DecimalField(max_digits=3, decimal_places=2, default=0.00)

