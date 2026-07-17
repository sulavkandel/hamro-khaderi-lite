"""Django settings for Hamro Khaderi-Lite.

Everything configurable is read from environment variables so the same
code runs in dev (SQLite), sandbox and production (PostgreSQL + Docker).
"""
import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = os.environ.get(
    "DJANGO_SECRET_KEY", "dev-insecure-key-change-in-production"
)
DEBUG = os.environ.get("DJANGO_DEBUG", "1") == "1"
ALLOWED_HOSTS = os.environ.get("DJANGO_ALLOWED_HOSTS", "*").split(",")

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    # third-party
    "rest_framework",
    "drf_spectacular",
    "corsheaders",
    "django_apscheduler",
    # local apps
    "districts",
    "ingestion",
    "spi",
    "api",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "corsheaders.middleware.CorsMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "config.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
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

WSGI_APPLICATION = "config.wsgi.application"

# --- Database -------------------------------------------------------------
# Default: PostgreSQL (production). Set USE_SQLITE=1 for a zero-dependency
# local/CI run — the schema is portable between the two.
if os.environ.get("USE_SQLITE", "0") == "1":
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.sqlite3",
            "NAME": BASE_DIR / "db.sqlite3",
        }
    }
else:
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.postgresql",
            "NAME": os.environ.get("POSTGRES_DB", "khaderi"),
            "USER": os.environ.get("POSTGRES_USER", "khaderi"),
            "PASSWORD": os.environ.get("POSTGRES_PASSWORD", "khaderi"),
            "HOST": os.environ.get("POSTGRES_HOST", "127.0.0.1"),
            "PORT": os.environ.get("POSTGRES_PORT", "5432"),
        }
    }

AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

LANGUAGE_CODE = "en-us"
TIME_ZONE = "Asia/Kathmandu"
USE_I18N = True
USE_TZ = True

STATIC_URL = "static/"
STATIC_ROOT = BASE_DIR / "staticfiles"

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# --- DRF ------------------------------------------------------------------
REST_FRAMEWORK = {
    "DEFAULT_SCHEMA_CLASS": "drf_spectacular.openapi.AutoSchema",
    "DEFAULT_RENDERER_CLASSES": ["rest_framework.renderers.JSONRenderer"],
    "DEFAULT_AUTHENTICATION_CLASSES": [
        "rest_framework.authentication.SessionAuthentication",
        "rest_framework.authentication.BasicAuthentication",
    ],
}

SPECTACULAR_SETTINGS = {
    "TITLE": "Hamro Khaderi-Lite API",
    "DESCRIPTION": "District-level SPI drought monitoring for Nepal's Terai (prototype).",
    "VERSION": "1.0.0",
    "SERVE_INCLUDE_SCHEMA": False,
}

CORS_ALLOW_ALL_ORIGINS = True  # prototype; restrict in production

# --- Project domain settings ----------------------------------------------
# Which weather provider adapter to use (see ingestion/sources/registry.py)
WEATHER_SOURCE = os.environ.get("WEATHER_SOURCE", "open_meteo")
# First date of the historical baseline used to fit SPI distributions.
HISTORY_START_DATE = os.environ.get("HISTORY_START_DATE", "2012-01-01")
# Open-Meteo archive lags realtime by ~5 days.
ARCHIVE_LAG_DAYS = int(os.environ.get("ARCHIVE_LAG_DAYS", "5"))
# QC: daily precipitation above this is treated as sensor error -> NULL.
PRECIP_MAX_MM_PER_DAY = float(os.environ.get("PRECIP_MAX_MM_PER_DAY", "500"))
# Start APScheduler inside the web process (set 0 for management commands/CI).
SCHEDULER_AUTOSTART = os.environ.get("SCHEDULER_AUTOSTART", "0") == "1"
