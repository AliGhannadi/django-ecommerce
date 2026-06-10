from django.db.models import signals
from django.dispatch import receiver
from accounts.models import Profile, User
from django.contrib.auth import get_user_model


@receiver(signals.post_save, sender=User)
def create_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance, first_name="", last_name="", biography="")
    else:
        if hasattr(instance, 'profile'):
            instance.profile.save()
