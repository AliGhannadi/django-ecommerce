from django.core.mail import send_mail

send_mail(
    'Celery Test Email',
    'If you see this, your SMTP settings are working!',
    'info@example.com',
    ['test@receiver.com'],
    fail_silently=False,
)