# Kegbot Server main settings file.
#
# YOU SHOULD NOT EDIT THIS FILE.  Instead, run `setup-kegbot.py` and override
# any settings in the local_settings.py file it installs.

# --------------------------------------------------------------------------- #

from __future__ import absolute_import

# Grab flags for optional modules.
from pykeg.core.optional_modules import *

import logging
from pykeg.logging.logger import RedisLogger
logging.setLoggerClass(RedisLogger)

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
    'bootstrap-pagination',
    'imagekit',
    'gunicorn',
    'south',
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

### Default session serialization.
# Note: Twitter plugin requires Pickle (not JSON serializable).

SESSION_SERIALIZER = 'django.contrib.sessions.serializers.PickleSerializer'

### Kegweb specific stuff

ROOT_URLCONF = 'pykeg.web.urls'

TEMPLATE_DIRS = [
    'web/templates',
]

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
STATIC_ROOT = ''

# URL prefix for static files.
# Example: "http://media.lawrence.com/static/"
STATIC_URL = '/static/'

# URL prefix for admin static files -- CSS, JavaScript and images.
# Make sure to use a trailing slash.
# Examples: "http://foo.com/static/admin/", "/static/admin/".
ADMIN_MEDIA_PREFIX = '/static/admin/'

# Disable Django's built in host checker.
ALLOWED_HOSTS = ['*']

# List of callables that know how to import templates from various sources.
TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.Loader',
    'django.template.loaders.app_directories.Loader',
    'django.template.loaders.eggs.Loader',
)

TEMPLATE_CONTEXT_PROCESSORS = (
    'django.core.context_processors.debug',
    'django.core.context_processors.i18n',
    'django.core.context_processors.media',
    'django.core.context_processors.static',
    'django.core.context_processors.request',
    'django.contrib.auth.context_processors.auth',
    'django.contrib.messages.context_processors.messages',
    'pykeg.web.context_processors.kbsite',
)

MIDDLEWARE_CLASSES = (
    # CurrentRequest and KegbotSite middlewares added first

    'django.middleware.cache.UpdateCacheMiddleware',
    'django.middleware.gzip.GZipMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',

    'pykeg.contrib.demomode.middleware.DemoModeMiddleware',
    'pykeg.web.api.middleware.ApiRequestMiddleware',
    'pykeg.web.middleware.PrivacyMiddleware',

    'django.middleware.doc.XViewMiddleware',

    # Cache middleware should be last, except for ApiResponseMiddleWare,
    # which needs to be after it (in request order) so that it can
    # update the Cache-Control header before it (in reponse order).
    'django.middleware.cache.FetchFromCacheMiddleware',

    # ApiResponseMiddleware added last.
)

AUTHENTICATION_BACKENDS = (
    'pykeg.web.auth.local.LocalAuthBackend',
)

CACHES = {
    'default': {
        'BACKEND': 'redis_cache.cache.RedisCache',
        'LOCATION': '127.0.0.1:6379:1',
        'OPTIONS': {
            'CLIENT_CLASS': 'redis_cache.client.DefaultClient',
        }
    }
}

CACHE_MIDDLEWARE_ANONYMOUS_ONLY = True

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

### Celery

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


### logging

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
            'class': 'django.utils.log.NullHandler',
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

### raven

if HAVE_RAVEN:
    INSTALLED_APPS += (
        'raven.contrib.django.raven_compat',
    )

    LOGGING['root']['handlers'] = ['sentry']
    LOGGING['handlers']['sentry'] = {
        'level': 'ERROR',
        'class': 'raven.contrib.django.raven_compat.handlers.SentryHandler',
    }

### django-storages
if HAVE_STORAGES:
    INSTALLED_APPS += ('storages',)

### django-nose
if HAVE_DJANGO_NOSE:
    INSTALLED_APPS += ('django_nose',)

### django.contrib.messages
MESSAGE_STORAGE = 'django.contrib.messages.storage.fallback.FallbackStorage'

### django-registration
ACCOUNT_ACTIVATION_DAYS = 3

### Statsd
STATSD_CLIENT = 'django_statsd.clients.normal'

# Set to true to route statsd pings to the debug toolbar.
KEGBOT_STATSD_TO_TOOLBAR = False

### Notifications
NOTIFICATION_BACKENDS = [
    'pykeg.notification.backends.email.EmailNotificationBackend'
]

### E-mail
EMAIL_BACKEND = 'django.core.mail.backends.dummy.EmailBackend'
EMAIL_FROM_ADDRESS = ''
EMAIL_SUBJECT_PREFIX = ''

# Bogus default values (to prevent djangofb from choking if unavailable);
# replace with site-specific values in local_settings.py, if desired.
FACEBOOK_API_KEY = ''
FACEBOOK_SECRET_KEY = ''

### Twitter

TWITTER_CONSUMER_KEY = ''
TWITTER_CONSUMER_SECRET_KEY = ''
TWITTER_REQUEST_TOKEN_URL = 'https://api.twitter.com/oauth/request_token'
TWITTER_ACCESS_TOKEN_URL = 'https://api.twitter.com/oauth/access_token'
TWITTER_AUTHORIZATION_URL = 'https://api.twitter.com/oauth/authorize'

### Foursquare

FOURSQUARE_CLIENT_ID = ''
FOURSQUARE_CLIENT_SECRET = ''
FOURSQUARE_REQUEST_PERMISSIONS = ''

### Untappd

UNTAPPD_CLIENT_ID = ''
UNTAPPD_CLIENT_SECRET = ''

### Imagekit
IMAGEKIT_DEFAULT_IMAGE_CACHE_BACKEND = 'imagekit.imagecache.NonValidatingImageCacheBackend'

TEST_RUNNER = 'pykeg.core.testutils.KegbotTestSuiteRunner'
NOSE_ARGS = ['--exe']
SKIP_SOUTH_TESTS = True
SOUTH_TESTS_MIGRATE = False

ICANHAZ_APP_DIRNAMES = ['static/jstemplates', 'jstemplates']

### Storage
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

# Override any user-specified timezone: As of Kegbot 0.9.12, this is
# specified in site settings.
TIME_ZONE = 'UTC'

# Update email addresses.
DEFAULT_FROM_EMAIL = EMAIL_FROM_ADDRESS

### socialregistration (after importing common settings)

if KEGBOT_ENABLE_ADMIN:
    INSTALLED_APPS += ('django.contrib.admin',)

### djcelery_email

if HAVE_CELERY_EMAIL:
    CELERY_EMAIL_BACKEND = EMAIL_BACKEND
    INSTALLED_APPS += ('djcelery_email',)
    EMAIL_BACKEND = 'djcelery_email.backends.CeleryEmailBackend'

### debug_toolbar

if DEBUG:
    if HAVE_DEBUG_TOOLBAR:
        INSTALLED_APPS += (
            'debug_toolbar',
        )
        MIDDLEWARE_CLASSES += (
            'debug_toolbar.middleware.DebugToolbarMiddleware',
        )
        DEBUG_TOOLBAR_PANELS = (
            'debug_toolbar.panels.version.VersionDebugPanel',
            'debug_toolbar.panels.timer.TimerDebugPanel',
            'debug_toolbar.panels.settings.SettingsPanel',
            'debug_toolbar.panels.headers.HeaderDebugPanel',
            'debug_toolbar.panels.request_vars.RequestVarsDebugPanel',
            'debug_toolbar.panels.template.TemplateDebugPanel',
            'debug_toolbar.panels.sql.SQLDebugPanel',
            'debug_toolbar.panels.signals.SignalDebugPanel',
            'debug_toolbar.panels.logging.LoggingPanel',
            #'debug_toolbar.panels.profiling.ProfilingDebugPanel',
        )
        if HAVE_MEMCACHE_TOOLBAR:
            INSTALLED_APPS += ('debug_toolbar_memcache',)
            if HAVE_MEMCACHE:
                DEBUG_TOOLBAR_PANELS += ('debug_toolbar_memcache.panels.memcache.MemcachePanel',)
            elif HAVE_PYLIBMC:
                DEBUG_TOOLBAR_PANELS += ('debug_toolbar_memcache.panels.pylibmc.PylibmcPanel',)

# Add all plugin template dirs to search path.
from pykeg.core.util import get_plugin_template_dirs
TEMPLATE_DIRS += get_plugin_template_dirs(KEGBOT_PLUGINS)

### Statsd

# Needs SECRET_KEY so must be imported after local settings.

STATSD_PATCHES = [
    'django_statsd.patches.db',
    'django_statsd.patches.cache',
]

if HAVE_STATSD:
    MIDDLEWARE_CLASSES = (
        'django_statsd.middleware.GraphiteRequestTimingMiddleware',
        'django_statsd.middleware.GraphiteMiddleware',
    ) + MIDDLEWARE_CLASSES

    INSTALLED_APPS += ('django_statsd',)

if DEBUG and HAVE_DEBUG_TOOLBAR and KEGBOT_STATSD_TO_TOOLBAR:
    MIDDLEWARE_CLASSES = (
        'debug_toolbar.middleware.DebugToolbarMiddleware',
    ) + MIDDLEWARE_CLASSES
    DEBUG_TOOLBAR_PANELS = (
        'django_statsd.panel.StatsdPanel',
    ) + DEBUG_TOOLBAR_PANELS
    STATSD_CLIENT = 'django_statsd.clients.toolbar'

### First/last middlewares.

MIDDLEWARE_CLASSES = (
    'pykeg.web.middleware.CurrentRequestMiddleware',
    'pykeg.web.middleware.KegbotSiteMiddleware',
) + MIDDLEWARE_CLASSES

MIDDLEWARE_CLASSES += ('pykeg.web.api.middleware.ApiResponseMiddleware',)
