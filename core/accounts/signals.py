from django.db.models import signals
from django.dispatch import receiver
from accounts.models import Profile, User
from django.contrib.auth import get_user_model
from coupons.tasks import send_welcome_coupon_task

@receiver(signals.post_save, sender=User)
def create_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance, first_name="", last_name="", biography="")
    else:
        if hasattr(instance, 'profile'):
            instance.profile.save()
            

@receiver(signals.pre_save, sender=User)
def generate_welcome_coupon(sender, instance, **kwargs):
    if instance.id:
        old_instance = User.objects.get(id=instance.id)
    if not old_instance.is_verified and instance.is_verified:
        send_welcome_coupon_task.delay(instance.id)
        
