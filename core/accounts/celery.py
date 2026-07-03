from celery import Celery
import os
from core.settings.env import config

django_env = config("DJANGO_ENV", "dev")
if django_env == "dev":
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings.dev')
else:
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings.prod')
    
app = Celery('core')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()