# Kegbot Server main settings file.
#
# YOU SHOULD NOT EDIT THIS FILE.  Instead, run `setup-kegbot.py` and override
# any settings in the local_settings.py file it installs.

# --------------------------------------------------------------------------- #

from __future__ import absolute_import

# Grab flags for optional modules.
from pykeg.core.optional_modules import *

import os
import logging
from pykeg.logging.logger import RedisLogger
logging.setLoggerClass(RedisLogger)

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

INSTALLED_APPS = (
    'pykeg.core',
    'pykeg.web',
    'pykeg.web.api',
    'pykeg.web.account',
    'pykeg.web.kbregistration',
    'pykeg.web.kegadmin',
    'pykeg.web.kegweb',
    'pykeg.web.setup_wizard',
    'pykeg.contrib.demomode',

    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.humanize',
    'django.contrib.messages',
    'django.contrib.sessions',
    'django.contrib.staticfiles',

    'crispy_forms',
    'django_nose',
    'bootstrap_pagination',
    'imagekit',
    'gunicorn',
)

LOGIN_REDIRECT_URL = "/account/"

KEGBOT_ADMIN_LOGIN_URL = 'auth_login'

AUTH_USER_MODEL = 'core.User'

# List of finder classes that know how to find static files in
# various locations.
STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
)

STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

# Default session serialization.
# Note: Twitter plugin requires Pickle (not JSON serializable).

SESSION_SERIALIZER = 'django.contrib.sessions.serializers.PickleSerializer'

# Kegweb specific stuff

ROOT_URLCONF = 'pykeg.web.urls'

SITE_ID = 1

# Language code for this installation. All choices can be found here:
# http://www.w3.org/TR/REC-html40/struct/dirlang.html#langcodes
# http://blogs.law.harvard.edu/tech/stories/storyReader$15
LANGUAGE_CODE = 'en-us'

# Enable Django 1.4+ timezone support.  Do not disable this.
USE_TZ = True

# Absolute filesystem path to the directory that will hold user-uploaded files.
# Example: "/home/media/media.lawrence.com/media/"
MEDIA_ROOT = ''

# URL that handles the media served from MEDIA_ROOT. Make sure to use a
# trailing slash.
# Examples: "http://media.lawrence.com/media/", "http://example.com/media/"
MEDIA_URL = '/media/'

# Absolute path to the directory static files should be collected to.
# Don't put anything in this directory yourself; store your static files
# in apps' "static/" subdirectories and in STATICFILES_DIRS.
# Example: "/home/media/media.lawrence.com/static/"
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')

# URL prefix for static files.
# Example: "http://media.lawrence.com/static/"
STATIC_URL = '/static/'

# URL prefix for admin static files -- CSS, JavaScript and images.
# Make sure to use a trailing slash.
# Examples: "http://foo.com/static/admin/", "/static/admin/".
ADMIN_MEDIA_PREFIX = '/static/admin/'

# Disable Django's built in host checker.
ALLOWED_HOSTS = ['*']

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'pykeg.web.middleware.CurrentRequestMiddleware',
    'pykeg.web.middleware.KegbotSiteMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'pykeg.contrib.demomode.middleware.DemoModeMiddleware',
    'pykeg.web.api.middleware.ApiRequestMiddleware',
    'pykeg.web.middleware.PrivacyMiddleware',
]

AUTHENTICATION_BACKENDS = (
    'pykeg.web.auth.local.LocalAuthBackend',
)

CACHES = {
    'default': {
        'BACKEND': 'django_redis.cache.RedisCache',
        'LOCATION': '127.0.0.1:6379:1',
        'OPTIONS': {
            'CLIENT_CLASS': 'django_redis.client.DefaultClient',
        }
    }
}

INTERNAL_IPS = ('127.0.0.1',)

# Set to true if the database admin module should be enabled.
KEGBOT_ENABLE_ADMIN = False

# Add plugins in local_settings.py
KEGBOT_PLUGINS = [
    'pykeg.contrib.foursquare.plugin.FoursquarePlugin',
    'pykeg.contrib.twitter.plugin.TwitterPlugin',
    'pykeg.contrib.untappd.plugin.UntappdPlugin',
    'pykeg.contrib.webhook.plugin.WebhookPlugin',
]

# You probably don't want to turn this on.
DEMO_MODE = False
EMBEDDED = False

KEGBOT_BACKEND = 'pykeg.backend.backends.KegbotBackend'

# Celery

BROKER_URL = 'redis://localhost:6379/0'
CELERY_RESULT_BACKEND = 'redis://localhost:6379/0'

CELERY_QUEUES = {
    'default': {
        'exchange': 'default',
        'binding_key': 'default'
    },
    'stats': {
        'exchange': 'default',
        'binding_key': 'stats'
    },
}

CELERY_DEFAULT_QUEUE = "default"
CELERYD_CONCURRENCY = 3

from datetime import timedelta
CELERYBEAT_SCHEDULER = 'pykeg.util.celery.RedisScheduler'
CELERYBEAT_SCHEDULE = {
    'checkin': {
        'task': 'checkin',
        'schedule': timedelta(hours=12),
    }
}


# logging

LOGGING = {
    'version': 1,
    'disable_existing_loggers': True,
    'filters': {
        'require_debug_true': {
            '()': 'django.utils.log.RequireDebugTrue',
        },
    },
    'handlers': {
        'console': {
            'level': 'DEBUG',
            'filters': ['require_debug_true'],
            'class': 'logging.StreamHandler',
            'formatter': 'verbose',
        },
        'null': {
            'class': 'logging.NullHandler',
        },
        'redis': {
            'level': 'INFO',
            'class': 'pykeg.logging.handlers.RedisListHandler',
            'key': 'kb:log',
            'max_messages': 100,
        },
    },
    'formatters': {
        'verbose': {
            'format': '%(asctime)s %(levelname)-8s (%(name)s) %(message)s'
        },
        'simple': {
            'format': '%(levelname)s %(message)s'
        },
    },
    'loggers': {
        'raven': {
            'level': 'DEBUG',
            'handlers': ['console'],
            'propagate': False,
        },
        'pykeg': {
            'level': 'INFO',
            'handlers': ['console', 'redis'],
            'propagate': False,
        },
        '': {
            'level': 'INFO',
            'handlers': ['console'],
            'formatter': 'verbose',
        },
    },
}

# raven

if HAVE_RAVEN:
    INSTALLED_APPS += (
        'raven.contrib.django.raven_compat',
    )

    LOGGING['root']['handlers'] = ['sentry']
    LOGGING['handlers']['sentry'] = {
        'level': 'ERROR',
        'class': 'raven.contrib.django.raven_compat.handlers.SentryHandler',
    }

# django-storages
if HAVE_STORAGES:
    INSTALLED_APPS += ('storages',)

# django.contrib.messages
MESSAGE_STORAGE = 'django.contrib.messages.storage.fallback.FallbackStorage'

# django-registration
ACCOUNT_ACTIVATION_DAYS = 3

# Statsd
STATSD_CLIENT = 'django_statsd.clients.normal'

# Set to true to route statsd pings to the debug toolbar.
KEGBOT_STATSD_TO_TOOLBAR = False

# Notifications
NOTIFICATION_BACKENDS = [
    'pykeg.notification.backends.email.EmailNotificationBackend'
]

# E-mail
EMAIL_BACKEND = 'django.core.mail.backends.dummy.EmailBackend'
EMAIL_FROM_ADDRESS = ''
EMAIL_SUBJECT_PREFIX = ''

# Bogus default values (to prevent djangofb from choking if unavailable);
# replace with site-specific values in local_settings.py, if desired.
FACEBOOK_API_KEY = ''
FACEBOOK_SECRET_KEY = ''

# Twitter

TWITTER_CONSUMER_KEY = ''
TWITTER_CONSUMER_SECRET_KEY = ''
TWITTER_REQUEST_TOKEN_URL = 'https://api.twitter.com/oauth/request_token'
TWITTER_ACCESS_TOKEN_URL = 'https://api.twitter.com/oauth/access_token'
TWITTER_AUTHORIZATION_URL = 'https://api.twitter.com/oauth/authorize'

# Foursquare

FOURSQUARE_CLIENT_ID = ''
FOURSQUARE_CLIENT_SECRET = ''
FOURSQUARE_REQUEST_PERMISSIONS = ''

# Untappd

UNTAPPD_CLIENT_ID = ''
UNTAPPD_CLIENT_SECRET = ''

# Imagekit
IMAGEKIT_DEFAULT_IMAGE_CACHE_BACKEND = 'imagekit.imagecache.NonValidatingImageCacheBackend'

TEST_RUNNER = 'pykeg.core.testutils.KegbotTestSuiteRunner'
NOSE_ARGS = [
    '--exe',
    '--rednose',
]

# Storage
DEFAULT_FILE_STORAGE = 'pykeg.web.kegweb.kbstorage.KegbotFileSystemStorage'

from pykeg.core import importhacks
try:
    from local_settings import *
except ImportError:
    msg = "Could not find local_settings.py; has Kegbot been set up?\n"
    msg += 'Tried: ' + ' '.join(importhacks.SEARCH_DIRS) + '\n\n'
    msg += 'Run setup-kegbot.py or set KEGBOT_SETTINGS_DIR to the settings directory.'
    import sys
    print>>sys.stderr, msg
    sys.exit(1)

from pykeg.core.util import get_plugin_template_dirs
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': ['web/templates'] + get_plugin_template_dirs(KEGBOT_PLUGINS),
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.contrib.auth.context_processors.auth',
                'django.template.context_processors.debug',
                'django.template.context_processors.i18n',
                'django.template.context_processors.media',
                'django.template.context_processors.request',
                'django.template.context_processors.static',
                'django.template.context_processors.tz',
                'django.contrib.messages.context_processors.messages',
                'pykeg.web.context_processors.kbsite',
            ],
            'debug': DEBUG,
        },
    },
]

# Override any user-specified timezone: As of Kegbot 0.9.12, this is
# specified in site settings.
TIME_ZONE = 'UTC'

# Update email addresses.
DEFAULT_FROM_EMAIL = EMAIL_FROM_ADDRESS

if KEGBOT_ENABLE_ADMIN:
    INSTALLED_APPS += ('django.contrib.admin',)

# djcelery_email

if HAVE_CELERY_EMAIL:
    CELERY_EMAIL_BACKEND = EMAIL_BACKEND
    INSTALLED_APPS += ('djcelery_email',)
    EMAIL_BACKEND = 'djcelery_email.backends.CeleryEmailBackend'
