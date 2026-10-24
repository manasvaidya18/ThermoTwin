"""Django settings for the ThermoTwin backend.

Values come from environment variables (see .env.example at the repo root).
Databases: PostgreSQL for application data (when POSTGRES_DB is set; SQLite otherwise, e.g. for quick tests) and
InfluxDB for time series (when INFLUX_URL and INFLUX_TOKEN are set; otherwise readings use a database table).
"""
from __future__ import annotations

import os
import sys
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent          # backend/
REPO_ROOT = BASE_DIR.parent

# The prediction engine is a sibling package; make it importable for the in-process fallback.
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))


def _env_file() -> None:
    """Load KEY=VALUE lines from .env at the repo root (if present) without overriding real env vars."""
    f = REPO_ROOT / ".env"
    if f.exists():
        for line in f.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                k, v = line.split("=", 1)
                os.environ.setdefault(k.strip(), v.strip())


_env_file()
os.environ.setdefault("LOKY_MAX_CPU_COUNT", "4")

SECRET_KEY = os.environ.get("DJANGO_SECRET_KEY", "dev-only-insecure-key-change-me")
DEBUG = os.environ.get("DJANGO_DEBUG", "1") == "1"
ALLOWED_HOSTS = os.environ.get("DJANGO_ALLOWED_HOSTS", "localhost,127.0.0.1,testserver").split(",")

INSTALLED_APPS = [
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.admin",
    "django.contrib.staticfiles",
    "rest_framework",
    "rest_framework.authtoken",
    "apps.accounts",
    "apps.organizations",
    "apps.facilities",
    "apps.telemetry",
    "apps.alerts",
    "apps.incidents",
    "apps.reports",
]

MIDDLEWARE = [
    "config.middleware.NoCacheMiddleware",
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
]

ROOT_URLCONF = "config.urls"
TEMPLATES = [{
    "BACKEND": "django.template.backends.django.DjangoTemplates",
    "DIRS": [],
    "APP_DIRS": True,
    "OPTIONS": {"context_processors": [
        "django.template.context_processors.request",
        "django.contrib.auth.context_processors.auth",
        "django.contrib.messages.context_processors.messages",
    ]},
}]
WSGI_APPLICATION = "config.wsgi.application"
ASGI_APPLICATION = "config.asgi.application"

if os.environ.get("POSTGRES_DB"):
    DATABASES = {"default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": os.environ["POSTGRES_DB"],
        "USER": os.environ.get("POSTGRES_USER", "postgres"),
        "PASSWORD": os.environ.get("POSTGRES_PASSWORD", ""),
        "HOST": os.environ.get("POSTGRES_HOST", "127.0.0.1"),
        "PORT": os.environ.get("POSTGRES_PORT", "5432"),
    }}
else:
    DATABASES = {"default": {"ENGINE": "django.db.backends.sqlite3",
                             "NAME": os.environ.get("TT_DB", str(BASE_DIR / "db.sqlite3"))}}

AUTH_PASSWORD_VALIDATORS = [{"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"}]

REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": [
        "rest_framework.authentication.TokenAuthentication",
        "rest_framework.authentication.SessionAuthentication",
    ],
    # Reading the dashboards is open in the demo; anything that changes data needs a login (or a device key).
    "DEFAULT_PERMISSION_CLASSES": ["rest_framework.permissions.IsAuthenticatedOrReadOnly"],
}

LANGUAGE_CODE = "en-us"
TIME_ZONE = "Asia/Kolkata"
USE_I18N = False
USE_TZ = True
STATIC_URL = "/static/"
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# ThermoTwin
FRONTEND_DIR = Path(os.environ.get("TT_FRONTEND", REPO_ROOT / "frontend"))
ENGINE_URL = os.environ.get("TT_ENGINE_URL", "")            # empty = run the prediction engine in-process
SCENARIO_PATH = Path(os.environ.get("TT_SCENARIO", BASE_DIR / "apps" / "telemetry" / "scenarios" / "pune_demo.json"))
ESCALATE_AFTER_MIN = int(os.environ.get("TT_ESCALATE_AFTER_MIN", 30))

# Time series: sensor readings and model outputs go to InfluxDB 2.x when configured, else to the database table.
INFLUX = dict(url=os.environ.get("INFLUX_URL", ""), token=os.environ.get("INFLUX_TOKEN", ""),
              org=os.environ.get("INFLUX_ORG", "thermotwin"), bucket=os.environ.get("INFLUX_BUCKET", "thermotwin"))
