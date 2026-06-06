"""
Select settings module from DJANGO_ENV or explicit DJANGO_SETTINGS_MODULE suffix.

Defaults to development settings when DJANGO_SETTINGS_MODULE is ``core.settings``.
Use ``core.settings.prod`` or ``DJANGO_ENV=prod`` for production.
"""

import os

from .env import config

_module = os.environ.get("DJANGO_SETTINGS_MODULE", "core.settings")

if _module.endswith(".prod"):
    from .prod import *
elif _module.endswith(".dev"):
    from .dev import *
else:
    env = os.environ.get("DJANGO_ENV", config("DJANGO_ENV", default="dev"))
    if env in ("prod", "production"):
        from .prod import *  
    else:
        from .dev import *  
