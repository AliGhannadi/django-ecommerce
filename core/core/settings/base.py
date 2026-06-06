"""
Shared Django settings for all environments.
"""

from datetime import timedelta
from pathlib import Path

from .env import config

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent.parent

SHOW_DEBUGGER_TOOLBAR = config(
    "SHOW_DEBUGGER_TOOLBAR", cast=bool, default=False
)

# Application definition

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "django.contrib.sites",
    "django.contrib.sitemaps",
    "rest_framework",
    "django_filters",
    "drf_spectacular",
    "corsheaders",
    "rest_framework_simplejwt.token_blacklist",
    "accounts",
    "cart",
    "orders",
    "payments",
    "products",
    "social",
    
]

SITE_ID = config("SITE_ID", cast=int, default=1)

MIDDLEWARE = [
    "django.middleware.gzip.GZipMiddleware",
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "corsheaders.middleware.CorsMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "core.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "core.wsgi.application"

# ASGI Configuration

# ASGI_APPLICATION = "core.asgi.application"
# CHANNEL_LAYERS = {
#     'default': {
#         'BACKEND': 'channels_redis.core.RedisChannelLayer',
#         'CONFIG': {
#             "hosts": [(config("CHANNEL_HOST", default='127.0.0.1'), config("CHANNEL_PORT", cast=int, default=6379))],
#         },
#     },
# }

# Password validation
# https://docs.djangoproject.com/en/5.2/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
]

# Internationalization
# https://docs.djangoproject.com/en/5.2/topics/i18n/

LANGUAGE_CODE = "en-us"

TIME_ZONE = config("TIME_ZONE", default="UTC")

USE_I18N = True

USE_L10N = True

USE_TZ = True

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/5.2/howto/static-files/

STATIC_URL = "/static/"
MEDIA_URL = "/media/"

STATIC_ROOT = BASE_DIR / "staticfiles"
MEDIA_ROOT = BASE_DIR / "media"

STATICFILES_DIRS = [
    BASE_DIR / "static",
]

# Default primary key field type
# https://docs.djangoproject.com/en/5.2/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# Email Configurations for production and development

EMAIL_BACKEND = config(
    "EMAIL_BACKEND", default="django.core.mail.backends.smtp.EmailBackend"
)
EMAIL_HOST = config("EMAIL_HOST", default="smtp4dev")
EMAIL_PORT = int(config("EMAIL_PORT", default=25))
EMAIL_HOST_USER = config("EMAIL_HOST_USER", default="")
EMAIL_HOST_PASSWORD = config("EMAIL_HOST_PASSWORD", default="")
EMAIL_USE_SSL = config("EMAIL_USE_SSL", cast=bool, default=False)
EMAIL_USE_TLS = config("EMAIL_USE_TLS", cast=bool, default=False)
DEFAULT_FROM_EMAIL = config("DEFAULT_FROM_EMAIL", default="info@example.com")

# Redis & Celery

REDIS_HOST = config("REDIS_HOST", default="127.0.0.1")
REDIS_PORT = config("REDIS_PORT", cast=int, default=6379)
REDIS_DB = config("REDIS_DB", cast=int, default=0)
REDIS_URL = config(
    "REDIS_URL",
    default=f"redis://{REDIS_HOST}:{REDIS_PORT}/{REDIS_DB}",
)

CACHES = {
    "default": {
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": REDIS_URL,
        "OPTIONS": {
            "CLIENT_CLASS": "django_redis.client.DefaultClient",
        },
    }
}

CELERY_BROKER_URL = config("CELERY_BROKER_URL", default=REDIS_URL)
CELERY_RESULT_BACKEND = config("CELERY_RESULT_BACKEND", default=REDIS_URL)
CELERY_ACCEPT_CONTENT = ["json"]
CELERY_TASK_SERIALIZER = "json"
CELERY_RESULT_SERIALIZER = "json"
CELERY_TIMEZONE = TIME_ZONE
CELERY_TASK_TRACK_STARTED = True
CELERY_BROKER_CONNECTION_RETRY_ON_STARTUP = True

REST_FRAMEWORK = {
    "DEFAULT_PERMISSION_CLASSES": [
        "rest_framework.permissions.AllowAny",
    ],
    "DEFAULT_AUTHENTICATION_CLASSES": [
        "rest_framework_simplejwt.authentication.JWTAuthentication"
    ],
    "DEFAULT_SCHEMA_CLASS": "drf_spectacular.openapi.AutoSchema",
    "EXCEPTION_HANDLER": "utils.core.exceptions.custom_exception_handler",
    "DEFAULT_FILTER_BACKENDS": [
        "django_filters.rest_framework.DjangoFilterBackend"
    ],
}
if config("DISABLE_BROWSEABLE_API", cast=bool, default=False):
    REST_FRAMEWORK["DEFAULT_RENDERER_CLASSES"] = (
        "rest_framework.renderers.JSONRenderer",
    )

# CORS settings
# CORS_ALLOW_ALL_ORIGINS = DEBUG  # Only allow all in dev
CORS_ALLOW_CREDENTIALS = True
CORS_ALLOWED_ORIGINS = config(
    "CORS_ALLOWED_ORIGINS",
    cast=lambda v: [s.strip() for s in v.split(",")],
    default="http://localhost:5173,http://127.0.0.1:8000,http://127.0.0.1:5173",
)

# swagger configs
SHOW_SWAGGER = config("SHOW_SWAGGER", cast=bool, default=True)
SPECTACULAR_SETTINGS = {
    "TITLE": "Your Project API",
    "DESCRIPTION": "Comprehensive documentation for Your Project API, including all endpoints, data models, and authentication mechanisms.",
    "VERSION": "1.0.0",
    "TOS": "https://yourproject.com/terms/",
    "CONTACT": {
        "name": "API Support",
        "url": "https://yourproject.com/support",
        "email": "support@yourproject.com",
    },
    "LICENSE": {
        "name": "MIT License",
        "url": "https://opensource.org/licenses/MIT",
    },
    "SERVERS": [
        {"url": "http://127.0.0.1:8000", "description": "local server"},
        # {"url": "https://staging.yourproject.com", "description": "Staging server"},
    ],
    "SERVE_INCLUDE_SCHEMA": True,
    "SCHEMA_PATH_PREFIX": "/api/v1",
    "COMPONENT_SPLIT_REQUEST": True,
    "SORT_OPERATIONS": True,
    "SORT_OPERATION_PARAMETERS": True,
    "APPEND_COMPONENTS": {},
    "ENUM_NAME_OVERRIDES": {},
    "PREPROCESSING_HOOKS": [],
    "POSTPROCESSING_HOOKS": [],
    "SCHEMA_GENERATOR_CLASS": "drf_spectacular.generators.SchemaGenerator",
    "SWAGGER_UI_SETTINGS": {
        "deepLinking": True,
        "persistAuthorization": True,
        "displayOperationId": True,
        "defaultModelsExpandDepth": 2,
        "defaultModelExpandDepth": 2,
        "defaultModelRendering": "example",
        "docExpansion": "list",
        "filter": True,
        "showExtensions": True,
        "showCommonExtensions": True,
    },
    "REDOC_SETTINGS": {
        "expandResponses": "200,201",
        "hideDownloadButton": False,
        "pathInMiddlePanel": True,
        "theme": {
            "spacing.unit": 8,
            "colors.primary.main": "#2E86C1",
        },
    },
}

# Simple JWT configuration (DEBUG-dependent keys set in dev/prod)
SIMPLE_JWT = {
    "ACCESS_TOKEN_LIFETIME": timedelta(
        minutes=config("ACCESS_TOKEN_LIFETIME_MINUTES", cast=int, default=15)
    ),
    "REFRESH_TOKEN_LIFETIME": timedelta(
        days=config("REFRESH_TOKEN_LIFETIME_DAYS", cast=int, default=7)
    ),
    "UPDATE_LAST_LOGIN": False,
    "AUTH_COOKIE": "access_token",
    "AUTH_COOKIE_REFRESH": "refresh_token",
    "AUTH_COOKIE_DOMAIN": config("AUTH_COOKIE_DOMAIN", default=None),
    "AUTH_COOKIE_HTTP_ONLY": True,
    "AUTH_COOKIE_PATH": "/",
    "AUTH_COOKIE_SAMESITE": config("AUTH_COOKIE_SAMESITE", default="Lax"),
    "AUTH_CSRF_AUTHENTICATION": config(
        "AUTH_CSRF_AUTHENTICATION", cast=bool, default=False
    ),
}

# django debug toolbar for docker usage
if SHOW_DEBUGGER_TOOLBAR:
    INSTALLED_APPS += [
        "debug_toolbar",
    ]
    MIDDLEWARE += [
        "debug_toolbar.middleware.DebugToolbarMiddleware",
    ]
    import socket  # only if you haven't already imported this

    hostname, _, ips = socket.gethostbyname_ex(socket.gethostname())
    INTERNAL_IPS = [ip[: ip.rfind(".")] + ".1" for ip in ips] + [
        "127.0.0.1",
        "10.0.2.2",
    ]

# accounts settings
AUTH_USER_MODEL = "accounts.User"
AUTH_PROFILE_MODULE = "accounts.User"

# gzip config
GZIP_MIN_LENGTH = 500
