"""
Load environment variables from the repository ``envs/.env`` file.

Repository layout::

    shop/                 # REPO_ROOT
      envs/.env           # canonical env file (see envs/.env.sample)
      core/               # Django project (manage.py lives here)
        core/settings/
"""

from pathlib import Path

from decouple import AutoConfig

_SETTINGS_PACKAGE = Path(__file__).resolve().parent
DJANGO_PROJECT_ROOT = _SETTINGS_PACKAGE.parent.parent
REPO_ROOT = DJANGO_PROJECT_ROOT.parent
ENV_DIR = REPO_ROOT / "envs"
ENV_FILE = ENV_DIR / ".env"

# Prefer shop/envs/.env; fall back to walking from envs/ (finds .env inside it).
config = AutoConfig(search_path=str(ENV_DIR if ENV_FILE.is_file() else REPO_ROOT))
