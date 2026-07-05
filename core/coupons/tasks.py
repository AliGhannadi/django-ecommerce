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
from accounts.models import User

@shared_task
def send_welcome_coupon_task(user_id):
    try:
        user = User.objects.get(id=user_id)
        if user.is_verified:
            email = user.email
            user_coupon = UserCoupon.objects.assign_unique_welcome_coupon(user)
            coupon_code = user_coupon.coupon.code
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