from .base import *
from .database import build_database_config
from .env import config

SECRET_KEY = config("SECRET_KEY")

DEBUG = config("DEBUG", cast=bool, default=False)

ALLOWED_HOSTS = [
    host.strip()
    for host in config("ALLOWED_HOSTS", default="127.0.0.1,localhost").split(",")
    if host.strip()
]

DATABASES = build_database_config()

SESSION_COOKIE_SECURE = config("SESSION_COOKIE_SECURE", cast=bool, default=not DEBUG)
CSRF_COOKIE_SECURE = config("CSRF_COOKIE_SECURE", cast=bool, default=not DEBUG)
SECURE_SSL_REDIRECT = config("SECURE_SSL_REDIRECT", cast=bool, default=False)
USE_X_FORWARDED_HOST = config("USE_X_FORWARDED_HOST", cast=bool, default=False)

SIMPLE_JWT["ROTATE_REFRESH_TOKENS"] = not DEBUG
SIMPLE_JWT["BLACKLIST_AFTER_ROTATION"] = not DEBUG
SIMPLE_JWT["AUTH_COOKIE_SECURE"] = config(
    "AUTH_COOKIE_SECURE", cast=bool, default=not DEBUG
)
