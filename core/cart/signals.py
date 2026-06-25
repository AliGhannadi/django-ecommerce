from django.db.models import signals
from django.dispatch import receiver
from cart.models import CartItem
from django.contrib.auth import get_user_model


@receiver(signals.post_save, sender=CartItem)
def update_quantity_of_product(sender, instance, created, **kwargs):
    if created:
        product = instance.product
        product.quantity -= instance.quantity()
        product.save()
        
        

