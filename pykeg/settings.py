# Kegbot Server main settings file.
#
# YOU SHOULD NOT EDIT THIS FILE.

# --------------------------------------------------------------------------- #

from __future__ import absolute_import

from pykeg.config import all_values
import dj_database_url
import os
import logging
from pykeg.logging.logger import RedisLogger
logging.setLoggerClass(RedisLogger)

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

KEGBOT = all_values()
DEBUG = KEGBOT['KEGBOT_DEBUG']
SECRET_KEY = KEGBOT['KEGBOT_SECRET_KEY']
DATABASES = {
    'default': dj_database_url.parse(KEGBOT['KEGBOT_DATABASE_URL']),
}

INSTALLED_APPS = (
    'pykeg.core',
    'pykeg.web',
    'pykeg.web.api',
    'pykeg.web.account',
    'pykeg.web.kbregistration',
    'pykeg.web.kegadmin',
    'pykeg.web.kegweb',
    'pykeg.web.setup_wizard',

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

LOGIN_REDIRECT_URL = '/account/'

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
MEDIA_ROOT = os.path.join(KEGBOT['KEGBOT_DATA_DIR'], 'media')

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
    'django.contrib.sessions.middleware.SessionMiddleware',
    'pykeg.web.middleware.IsSetupMiddleware',
    'pykeg.web.middleware.CurrentRequestMiddleware',
    'pykeg.web.middleware.KegbotSiteMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'pykeg.web.api.middleware.ApiRequestMiddleware',
    'pykeg.web.middleware.PrivacyMiddleware',
]

AUTHENTICATION_BACKENDS = (
    'pykeg.web.auth.local.LocalAuthBackend',
)

CACHES = {
    'default': {
        'BACKEND': 'django_redis.cache.RedisCache',
        'LOCATION': KEGBOT['KEGBOT_REDIS_URL'],
        'OPTIONS': {
            'CLIENT_CLASS': 'django_redis.client.DefaultClient',
        }
    }
}

INTERNAL_IPS = ('127.0.0.1',)

# Set to true if the database admin module should be enabled.
KEGBOT_ENABLE_ADMIN = False

KEGBOT_PLUGINS = [
    'pykeg.contrib.foursquare.plugin.FoursquarePlugin',
    'pykeg.contrib.twitter.plugin.TwitterPlugin',
    'pykeg.contrib.untappd.plugin.UntappdPlugin',
    'pykeg.contrib.webhook.plugin.WebhookPlugin',
]

KEGBOT_BACKEND = 'pykeg.backend.backends.KegbotBackend'

# Celery

BROKER_URL = KEGBOT['KEGBOT_REDIS_URL']
CELERY_RESULT_BACKEND = KEGBOT['KEGBOT_REDIS_URL']

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

CELERY_DEFAULT_QUEUE = 'default'
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
            'class': 'logging.StreamHandler',
            'formatter': 'verbosecolor',
        },
        'null': {
            'class': 'logging.NullHandler',
        },
        'redis': {
            'level': 'INFO',
            'class': 'pykeg.logging.handlers.RedisListHandler',
            'key': 'kb:log',
            'url': KEGBOT['KEGBOT_REDIS_URL'],
            'max_messages': 100,
        },
    },
    'formatters': {
        'verbose': {
            'format': '%(asctime)s %(levelname)-8s (%(name)s) %(message)s'
        },
        'verbosecolor': {
            'format': '%(asctime)s %(levelname)-8s (%(name)s) %(message)s',
            '()': 'coloredlogs.ColoredFormatter',
        },
        'simple': {
            'format': '%(levelname)s %(message)s'
        },
    },
    'loggers': {
        'raven': {
            'level': 'INFO',
            'handlers': ['console', 'redis'],
            'propagate': False,
        },
        'pykeg': {
            'level': 'INFO',
            'handlers': ['console', 'redis'],
            'propagate': False,
        },
        'django': {
            'level': 'INFO' if DEBUG else 'WARNING',
            'handlers': ['console', 'redis'],
            'propagate': False,
        },
        '': {
            'level': 'INFO' if DEBUG else 'WARNING',
            'handlers': ['console', 'redis'],
        },
    },
}

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

# Imagekit
IMAGEKIT_DEFAULT_IMAGE_CACHE_BACKEND = 'imagekit.imagecache.NonValidatingImageCacheBackend'

TEST_RUNNER = 'pykeg.core.testutils.KegbotTestSuiteRunner'
NOSE_ARGS = [
    '--exe',
    '--rednose',
]

# Storage
DEFAULT_FILE_STORAGE = 'pykeg.web.kegweb.kbstorage.KegbotFileSystemStorage'

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
