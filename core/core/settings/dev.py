from decouple import config

from .base import *
from .database import build_database_config

SECRET_KEY = "dev-secret-key"

DEBUG = True

ALLOWED_HOSTS = ["*"]

DATABASES = build_database_config()

SIMPLE_JWT["ROTATE_REFRESH_TOKENS"] = not DEBUG
SIMPLE_JWT["BLACKLIST_AFTER_ROTATION"] = not DEBUG
SIMPLE_JWT["AUTH_COOKIE_SECURE"] = config(
    "AUTH_COOKIE_SECURE", cast=bool, default=not DEBUG
)
