from celery import shared_task
from django.core.mail import send_mail

@shared_task
def welcome_message(username, email, verification_link):
    email_body = (
        f"Hi {username},\n\n"
        "We hope you enjoy your time!\n"
        f"Please verify your email from this link: {verification_link}"
    )
    send_mail(
        subject=f'Welcome to our website, Dear {username}',
        message=email_body,
        from_email='info@example.com',
        recipient_list=[email],        
        fail_silently=False,
    )
