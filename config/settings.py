import os
from pathlib import Path

import dj_database_url

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = os.getenv("DJANGO_SECRET_KEY", "change-me-in-production")
DEBUG = os.getenv("DJANGO_DEBUG", "1") == "1"

# Admin batch actions on ~700 journal rows need headroom above Django's default of 1000.
DATA_UPLOAD_MAX_NUMBER_FIELDS = 10000

_default_hosts = ["127.0.0.1", "localhost"]
if os.getenv("VERCEL"):
    _default_hosts.extend([".vercel.app", "connorbrown.net", "www.connorbrown.net"])
# Local phone testing via Cloudflare quick tunnels (DEBUG only).
if DEBUG:
    _default_hosts.append(".trycloudflare.com")

ALLOWED_HOSTS = os.getenv("DJANGO_ALLOWED_HOSTS", ",".join(_default_hosts)).split(",")
# Local phone / tunnel testing: accept any Host header while DEBUG is on.
if DEBUG and not os.getenv("DJANGO_ALLOWED_HOSTS"):
    ALLOWED_HOSTS = ["*"]

_default_csrf_origins = []
if os.getenv("VERCEL"):
    _default_csrf_origins.extend(
        [
            "https://connorbrown.net",
            "https://www.connorbrown.net",
        ]
    )
if DEBUG:
    _default_csrf_origins.append("https://*.trycloudflare.com")

CSRF_TRUSTED_ORIGINS = _default_csrf_origins + [
    origin.strip()
    for origin in os.getenv("CSRF_TRUSTED_ORIGINS", "").split(",")
    if origin.strip()
]

# Cloudflare Tunnel terminates TLS; Django still sees http://127.0.0.1.
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "pages",
    "playground",
    "portfolio",
    "writing",
    "journal",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
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
    }
]

WSGI_APPLICATION = "config.wsgi.application"
ASGI_APPLICATION = "config.asgi.application"

if os.getenv("DATABASE_URL"):
    DATABASES = {
        "default": dj_database_url.parse(
            os.environ["DATABASE_URL"],
            conn_max_age=600,
            conn_health_checks=True,
        ),
    }
else:
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.postgresql",
            "NAME": os.getenv("PGDATABASE", "connor_site"),
            "USER": os.getenv("PGUSER", ""),
            "PASSWORD": os.getenv("PGPASSWORD", ""),
            "HOST": os.getenv("PGHOST", "localhost"),
            "PORT": os.getenv("PGPORT", "5432"),
        },
    }

if os.getenv("PLAYGROUND_DATABASE_URL"):
    DATABASES["playground"] = dj_database_url.parse(
        os.environ["PLAYGROUND_DATABASE_URL"],
        conn_max_age=600,
        conn_health_checks=True,
    )
elif os.getenv("DATABASE_URL"):
    playground_config = dj_database_url.parse(
        os.environ["DATABASE_URL"],
        conn_max_age=600,
        conn_health_checks=True,
    )
    playground_config["NAME"] = os.getenv("PLAYGROUND_DB_NAME", "sql_playground")
    DATABASES["playground"] = playground_config
else:
    DATABASES["playground"] = {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": os.getenv("PLAYGROUND_PGDATABASE", "sql_playground"),
        "USER": os.getenv("PLAYGROUND_PGUSER", os.getenv("PGUSER", "")),
        "PASSWORD": os.getenv("PLAYGROUND_PGPASSWORD", os.getenv("PGPASSWORD", "")),
        "HOST": os.getenv("PLAYGROUND_PGHOST", os.getenv("PGHOST", "localhost")),
        "PORT": os.getenv("PLAYGROUND_PGPORT", os.getenv("PGPORT", "5432")),
    }

DATABASE_ROUTERS = ["playground.db_router.PlaygroundRouter"]

AUTH_PASSWORD_VALIDATORS = []

LANGUAGE_CODE = "en-us"
TIME_ZONE = "UTC"
USE_I18N = True
USE_TZ = True

STATIC_URL = "/static/"
STATICFILES_DIRS = [BASE_DIR / "static"]
STATIC_ROOT = BASE_DIR / "staticfiles"
STATICFILES_STORAGE = "whitenoise.storage.CompressedManifestStaticFilesStorage"

MEDIA_URL = "/media/"
MEDIA_ROOT = BASE_DIR / "media"

if os.getenv("AWS_STORAGE_BUCKET_NAME"):
    STORAGES = {
        "default": {
            "BACKEND": "storages.backends.s3boto3.S3Boto3Storage",
        },
        "staticfiles": {
            "BACKEND": "whitenoise.storage.CompressedManifestStaticFilesStorage",
        },
    }
    AWS_ACCESS_KEY_ID = os.getenv("AWS_ACCESS_KEY_ID")
    AWS_SECRET_ACCESS_KEY = os.getenv("AWS_SECRET_ACCESS_KEY")
    AWS_STORAGE_BUCKET_NAME = os.getenv("AWS_STORAGE_BUCKET_NAME")
    AWS_S3_REGION_NAME = os.getenv("AWS_S3_REGION_NAME", "auto")
    AWS_S3_ENDPOINT_URL = os.getenv("AWS_S3_ENDPOINT_URL") or None
    AWS_S3_ADDRESSING_STYLE = os.getenv("AWS_S3_ADDRESSING_STYLE", "path")
    AWS_S3_SIGNATURE_VERSION = "s3v4"
    AWS_DEFAULT_ACL = None
    AWS_QUERYSTRING_AUTH = False
    AWS_S3_FILE_OVERWRITE = True
    AWS_S3_CUSTOM_DOMAIN = os.getenv("AWS_S3_CUSTOM_DOMAIN", "").removeprefix("https://").removeprefix("http://").rstrip("/")
    if AWS_S3_CUSTOM_DOMAIN:
        MEDIA_URL = f"https://{AWS_S3_CUSTOM_DOMAIN}/"

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

LOGIN_URL = "/writing/login/"
LOGIN_REDIRECT_URL = "/writing/"

PLAYGROUND_STATEMENT_TIMEOUT_MS = int(os.getenv("PLAYGROUND_STATEMENT_TIMEOUT_MS", "3000"))
PLAYGROUND_ROW_LIMIT = int(os.getenv("PLAYGROUND_ROW_LIMIT", "100"))
