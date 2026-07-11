from django.db.models import signals
from django.dispatch import receiver
from django.db.models import F
from cart.models import CartItem, Cart
from django.contrib.auth import get_user_model
from django.core.cache import cache
from products.models import Product
from django.core.exceptions import ObjectDoesNotExist
from rest_framework.response import Response
from rest_framework.status import status

@receiver(signals.pre_save, sender=CartItem)
def update_quantity_of_product_on_save(sender, instance, **kwargs):
    if instance.id is None: # if cartitem is not created
        Product.objects.filter(id=instance.product.id).update(quantity=F("quantity") - instance.quantity)
    else:
        try:
                old_cart_item = CartItem.objects.get(id=instance.id)
                old_quantity = old_cart_item.quantity
                new_quantity = instance.quantity
                if new_quantity > old_quantity:
                    delta =  new_quantity - old_quantity
                    Product.objects.filter(id=instance.product.id).update(quantity=F("quantity") - delta)
                elif new_quantity < old_quantity:
                    delta = old_quantity - new_quantity
                    Product.objects.filter(id=instance.product.id).update(quantity=F("quantity") + delta)
        except CartItem.DoesNotExist:
                return Response({"error": "Cart item not found"}, status=status.HTTP_404_NOT_FOUND)
        
@receiver(signals.post_delete, sender=CartItem)
def update_quantity_of_product_on_delete(sender, instance, **kwargs):
        Product.objects.filter(id=instance.product.id).update(quantity=F("quantity") + instance.quantity)
        
@receiver([signals.post_save, signals.post_delete], sender=Cart)
def invalidate_cart_cache(sender, instance, **kwargs):
    cache.delete_pattern('*cart_list*')
        
        

