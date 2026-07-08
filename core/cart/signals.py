from django.db.models import signals
from django.dispatch import receiver
from cart.models import CartItem, Cart
from django.contrib.auth import get_user_model
from django.core.cache import cache

@receiver(signals.post_save, sender=CartItem)
def update_quantity_of_product(sender, instance, created, **kwargs):
    if created:
        product = instance.product
        product.quantity -= instance.quantity
        product.save()
        
        
@receiver([signals.post_save, signals.post_delete], sender=Cart)
def invalidate_cart_cache(sender, instance, created, **kwargs):
    cache.delete_pattern('*cart_list*')
        
        

