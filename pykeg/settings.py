# Kegbot Server main settings file.
#
# YOU SHOULD NOT EDIT THIS FILE.

# --------------------------------------------------------------------------- #


import logging
import os

import dj_database_url
import dj_email_url

from pykeg import config
from pykeg.config import ENV_PRODUCTION, ENV_TEST
from pykeg.logging.logger import RedisLogger

logging.setLoggerClass(RedisLogger)

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

config.validate()

KEGBOT = config.all()
KEGBOT_ENV = KEGBOT["KEGBOT_ENV"]
DEBUG = KEGBOT_ENV != ENV_PRODUCTION

SECRET_KEY = KEGBOT["KEGBOT_SECRET_KEY"]
DATABASES = {
    "default": dj_database_url.parse(KEGBOT["DATABASE_URL"]),
}

INSTALLED_APPS = (
    "whitenoise.runserver_nostatic",
    "pykeg.core",
    "pykeg.web",
    "pykeg.web.api",
    "pykeg.web.account",
    "pykeg.web.kbregistration",
    "pykeg.web.kegadmin",
    "pykeg.web.kegweb",
    "pykeg.web.setup_wizard",
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.humanize",
    "django.contrib.messages",
    "django.contrib.sessions",
    "django.contrib.staticfiles",
    "crispy_forms",
    "bootstrap_pagination",
    "imagekit",
    "gunicorn",
    "corsheaders",
    "rest_framework",
    "django_rq",
)

LOGIN_REDIRECT_URL = "/account/"

KEGBOT_ADMIN_LOGIN_URL = "auth_login"

AUTH_USER_MODEL = "core.User"

# List of finder classes that know how to find static files in
# various locations.
STATICFILES_FINDERS = (
    "django.contrib.staticfiles.finders.FileSystemFinder",
    "django.contrib.staticfiles.finders.AppDirectoriesFinder",
)

if KEGBOT_ENV == ENV_TEST:
    # During tests, whitenoise's manifest will not be available and
    # errors will be thrown while trying to access static files.
    # Use the default static backend to work around this.
    STATICFILES_STORAGE = "django.contrib.staticfiles.storage.StaticFilesStorage"
else:
    STATICFILES_STORAGE = "whitenoise.storage.CompressedManifestStaticFilesStorage"

# Default session serialization.

SESSION_SERIALIZER = "django.contrib.sessions.serializers.PickleSerializer"

# Kegweb specific stuff

ROOT_URLCONF = "pykeg.web.urls"

SITE_ID = 1

# Language code for this installation. All choices can be found here:
# http://www.w3.org/TR/REC-html40/struct/dirlang.html#langcodes
# http://blogs.law.harvard.edu/tech/stories/storyReader$15
LANGUAGE_CODE = "en-us"

# Enable Django 1.4+ timezone support.  Do not disable this.
USE_TZ = True

# Absolute filesystem path to the directory that will hold user-uploaded files.
# Example: "/home/media/media.lawrence.com/media/"
MEDIA_ROOT = os.path.join(KEGBOT["KEGBOT_DATA_DIR"], "media")

# URL that handles the media served from MEDIA_ROOT. Make sure to use a
# trailing slash.
# Examples: "http://media.lawrence.com/media/", "http://example.com/media/"
MEDIA_URL = KEGBOT["KEGBOT_MEDIA_URL"] or "/media/"

# Absolute path to the directory static files should be collected to.
# Don't put anything in this directory yourself; store your static files
# in apps' "static/" subdirectories and in STATICFILES_DIRS.
# Example: "/home/media/media.lawrence.com/static/"
STATIC_ROOT = os.path.join(BASE_DIR, "staticfiles")

# URL prefix for static files.
# Example: "http://media.lawrence.com/static/"
STATIC_URL = "/static/"

# URL prefix for admin static files -- CSS, JavaScript and images.
# Make sure to use a trailing slash.
# Examples: "http://foo.com/static/admin/", "/static/admin/".
ADMIN_MEDIA_PREFIX = "/static/admin/"

# Disable Django's built in host checker.
ALLOWED_HOSTS = ["*"]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "corsheaders.middleware.CorsMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "pykeg.web.middleware.ErrorLoggingMiddleware",
    "pykeg.web.middleware.PathRewriteMiddleware",
    "pykeg.web.middleware.IsSetupMiddleware",
    "pykeg.web.middleware.CurrentRequestMiddleware",
    "pykeg.web.middleware.KegbotSiteMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "pykeg.web.api.middleware.ApiRequestMiddleware",
    "pykeg.web.middleware.PrivacyMiddleware",
]

AUTHENTICATION_BACKENDS = ("pykeg.web.auth.local.LocalAuthBackend",)

CACHES = {
    "default": {
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": KEGBOT["REDIS_URL"],
        "OPTIONS": {
            "CLIENT_CLASS": "django_redis.client.DefaultClient",
        },
        "KEY_PREFIX": "kb:cache",
    },
    "rq": {
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": KEGBOT["REDIS_URL"],
        "OPTIONS": {
            "CLIENT_CLASS": "django_redis.client.DefaultClient",
        },
        "KEY_PREFIX": "kb:rq",
    },
}

INTERNAL_IPS = ("127.0.0.1",)

# Set to true if the database admin module should be enabled.
KEGBOT_ENABLE_ADMIN = DEBUG

KEGBOT_PLUGINS = [
    "pykeg.contrib.webhook.plugin.WebhookPlugin",
]

# RQ (workers)

RQ_QUEUES = {
    "default": {
        "USE_REDIS_CACHE": "rq",
        "ASYNC": KEGBOT_ENV != ENV_TEST,
    },
    "stats": {
        "USE_REDIS_CACHE": "rq",
        "ASYNC": KEGBOT_ENV != ENV_TEST,
    },
}

# logging

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "filters": {
        "require_debug_true": {
            "()": "django.utils.log.RequireDebugTrue",
        },
    },
    "handlers": {
        "console": {
            "level": "DEBUG",
            "class": "logging.StreamHandler",
            "formatter": "verbosecolor",
        },
        "null": {
            "class": "logging.NullHandler",
        },
        "redis": {
            "level": "INFO",
            "class": "pykeg.logging.handlers.RedisListHandler",
            "key": "kb:log",
            "url": KEGBOT["REDIS_URL"],
            "max_messages": 100,
        },
    },
    "formatters": {
        "verbose": {"format": "%(asctime)s %(levelname)-8s (%(name)s) %(message)s"},
        "verbosecolor": {
            "format": "%(asctime)s %(levelname)-8s (%(name)s) %(message)s",
            "()": "coloredlogs.ColoredFormatter",
        },
        "simple": {"format": "%(levelname)s %(message)s"},
    },
    "loggers": {
        "raven": {
            "level": "INFO",
            "handlers": ["console", "redis"],
            "propagate": False,
        },
        "pykeg": {
            "level": "INFO",
            "handlers": ["console", "redis"],
            "propagate": False,
        },
        "django": {
            "level": "INFO" if DEBUG else "WARNING",
            "handlers": ["console", "redis"],
            "propagate": False,
        },
        "": {
            "level": "DEBUG" if DEBUG else "WARNING",
            "handlers": ["console", "redis"],
        },
    },
}

# django.contrib.messages
MESSAGE_STORAGE = "django.contrib.messages.storage.fallback.FallbackStorage"

# django-registration
ACCOUNT_ACTIVATION_DAYS = 3

# Statsd
STATSD_CLIENT = "django_statsd.clients.normal"

# Set to true to route statsd pings to the debug toolbar.
KEGBOT_STATSD_TO_TOOLBAR = False

# Notifications
NOTIFICATION_BACKENDS = ["pykeg.notification.backends.email.EmailNotificationBackend"]

# E-mail
EMAIL_BACKEND = "pykeg.core.mail.KegbotEmailBackend"

DEFAULT_FROM_EMAIL = "no-reply@example.com"
EMAIL_SUBJECT_PREFIX = ""

# Imagekit
IMAGEKIT_DEFAULT_IMAGE_CACHE_BACKEND = "imagekit.imagecache.NonValidatingImageCacheBackend"

# Storage
DEFAULT_FILE_STORAGE = "pykeg.web.kegweb.kbstorage.KegbotFileSystemStorage"

from pykeg.core.util import get_plugin_template_dirs

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": ["web/templates"] + get_plugin_template_dirs(KEGBOT_PLUGINS),
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.contrib.auth.context_processors.auth",
                "django.template.context_processors.debug",
                "django.template.context_processors.i18n",
                "django.template.context_processors.media",
                "django.template.context_processors.request",
                "django.template.context_processors.static",
                "django.template.context_processors.tz",
                "django.contrib.messages.context_processors.messages",
                "pykeg.web.context_processors.kbsite",
            ],
            "debug": DEBUG,
        },
    },
]

# Override any user-specified timezone: As of Kegbot 0.9.12, this is
# specified in site settings.
TIME_ZONE = "UTC"

DEFAULT_AUTO_FIELD = "django.db.models.AutoField"

REST_FRAMEWORK = {
    "DEFAULT_PAGINATION_CLASS": "pykeg.api.pagination.CursorPagination",
    "PAGE_SIZE": 10,
    "DEFAULT_PERMISSION_CLASSES": [
        "pykeg.api.permissions.IsAuthenticated",
    ],
    "DEFAULT_AUTHENTICATION_CLASSES": (
        "pykeg.api.auth.ApiKeyBasicAuth",
        "rest_framework.authentication.SessionAuthentication",
    ),
}

CORS_ALLOWED_ORIGINS = [
    "http://localhost:1234",
    "http://127.0.0.1:1234",
]
CSRF_TRUSTED_ORIGINS = [
    "localhost:1234",
]
CORS_ALLOW_CREDENTIALS = True
SESSION_COOKIE_SAMESITE = None

APPEND_SLASH = True
