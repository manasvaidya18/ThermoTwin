"""Django settings for ThermoTwin Core Backend.

Configured for:
- Zero migrations needed (no auth, no sessions, no contenttypes).
- Direct connection to SQLite (or PostgreSQL via environment variables).
- Serves /api/* endpoints and frontend static files directly.
"""
from __future__ import annotations

import os
import sys
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent  # django_backend/
REPO_ROOT = BASE_DIR.parent                        # repo root

for p in (BASE_DIR, REPO_ROOT, REPO_ROOT / "ml"):
    s = str(p)
    if s not in sys.path:
        sys.path.insert(0, s)

SECRET_KEY = os.environ.get("DJANGO_SECRET_KEY", "thermotwin-dev-secret-key-2026")
DEBUG = True
ALLOWED_HOSTS = ["*"]

# Minimal apps - NO auth, NO sessions, NO admin -> ZERO migrations needed
INSTALLED_APPS = [
    "django.contrib.staticfiles",
    "core",
]

MIDDLEWARE = [
    "core.middleware.NoCacheMiddleware",
    "django.middleware.common.CommonMiddleware",
]

ROOT_URLCONF = "tt_core.urls"

TEMPLATES = []

WSGI_APPLICATION = "tt_core.wsgi.application"
ASGI_APPLICATION = "tt_core.asgi.application"

# Database: SQLite by default; switches to PostgreSQL if configured
DB_PATH = REPO_ROOT / "db" / "thermotwin.db"

if os.environ.get("POSTGRES_DB"):
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.postgresql",
            "NAME": os.environ.get("POSTGRES_DB"),
            "USER": os.environ.get("POSTGRES_USER", "postgres"),
            "PASSWORD": os.environ.get("POSTGRES_PASSWORD", ""),
            "HOST": os.environ.get("POSTGRES_HOST", "127.0.0.1"),
            "PORT": os.environ.get("POSTGRES_PORT", "5432"),
        }
    }
else:
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.sqlite3",
            "NAME": str(DB_PATH),
        }
    }

LANGUAGE_CODE = "en-us"
TIME_ZONE = "UTC"
USE_I18N = False
USE_TZ = True

STATIC_URL = "/static/"
FRONTEND_DIR = REPO_ROOT / "frontend"
STATICFILES_DIRS = [str(FRONTEND_DIR)] if FRONTEND_DIR.exists() else []

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"
