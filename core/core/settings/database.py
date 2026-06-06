from .env import config


def build_database_config():
    return {
        "default": {
            "ENGINE": config(
                "POSTGRES_ENGINE", default="django.db.backends.postgresql"
            ),
            "NAME": config("POSTGRES_DB", default="shop"),
            "USER": config("POSTGRES_USER", default="shop"),
            "PASSWORD": config("POSTGRES_PASSWORD", default="shop"),
            "HOST": config("POSTGRES_HOST", default="127.0.0.1"),
            "PORT": config("POSTGRES_PORT", default="5432"),
        }
    }
