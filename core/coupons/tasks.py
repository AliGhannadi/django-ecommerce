import random
import string
from celery import shared_task
from django.core.mail import send_mail
from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
from .models import Coupon, UserCoupon
from orders.models import Order 
from django.utils import timezone
from datetime import timedelta

User = get_user_model()

def generate_random_code():
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))

@shared_task
def send_welcome_coupon_task(user_id):
    try:
        user = User.objects.get(id=user_id)
        if user.is_verified:
            email = user.email
            coupon_code = generate_random_code()
            coupon = Coupon.objects.create(discount_percent=15.00, code=coupon_code, expiration_date=timezone.now() + timedelta(days=30))
            UserCoupon.objects.create(user=user, coupon=coupon)
            send_mail(
                subject="Welcome! Your exclusive discount code is ready!",
                message=f"Hi {user.username}, use code {coupon_code} for 15% off your first order!",
                from_email="info@example.com",
                recipient_list=[user.email],
                fail_silently=False,
            )
            return f"Successfully sent welcome coupon to user {user.id}"
        else:
            return f"{user_id} must be verified first."
    except User.DoesNotExist:
        return f"User with ID {user_id} not found."