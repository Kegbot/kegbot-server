# Pykeg main settings file.

# Note: YOU SHOULD NOT NEED TO EDIT THIS FILE.  Instead, see the instructions in
# local_settings.py.example.

# Grab flags for optional modules.
from pykeg.core.optional_modules import *

INSTALLED_APPS = (
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.humanize',
    'django.contrib.markup',
    'django.contrib.messages',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.staticfiles',

    'crispy_forms',
    'djcelery',
    'djkombu',
    'bootstrap-pagination',
    'imagekit',
    'pykeg.connections',
    'pykeg.connections.foursquare',
    'pykeg.connections.twitter',
    'pykeg.connections.untappd',
    'pykeg.contrib.soundserver',
    'pykeg.core',
    'pykeg.web',
    'pykeg.web.api',
    'pykeg.web.account',
    'pykeg.web.kegadmin',
    'pykeg.web.kegweb',
    'pykeg.web.setup_wizard',
    'gunicorn',
    'icanhaz',
    'registration',
    'socialregistration',
    'socialregistration.contrib.twitter',
    'socialregistration.contrib.facebook',
    'socialregistration.contrib.foursquare',
    'south',
    'django_nose', # must be after south
)

AUTH_PROFILE_MODULE = "core.UserProfile"
LOGIN_REDIRECT_URL = "/account/"

# List of finder classes that know how to find static files in
# various locations.
STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
)

### Kegweb specific stuff

ROOT_URLCONF = 'pykeg.web.urls'

TEMPLATE_DIRS = (
    'web/templates',
)

SITE_ID = 1

# Language code for this installation. All choices can be found here:
# http://www.w3.org/TR/REC-html40/struct/dirlang.html#langcodes
# http://blogs.law.harvard.edu/tech/stories/storyReader$15
LANGUAGE_CODE = 'en-us'

# Local time zone for this installation. All choices can be found here:
# http://www.postgresql.org/docs/8.1/static/datetime-keywords.html#DATETIME-TIMEZONE-SET-TABLE
TIME_ZONE = 'America/Los_Angeles'

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
# see pykeg.web.middleware.HttpHostMiddleware
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
    'pykeg.web.context_processors.enabled_features',
    'pykeg.web.context_processors.kbsite',
)

MIDDLEWARE_CLASSES = (
    'django.middleware.cache.UpdateCacheMiddleware',
    'django.middleware.gzip.GZipMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.middleware.transaction.TransactionMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',

    'pykeg.web.middleware.KegbotSiteMiddleware',
    'pykeg.web.middleware.HttpHostMiddleware',
    'pykeg.web.middleware.SiteActiveMiddleware',
    'pykeg.web.api.middleware.ApiRequestMiddleware',
    'pykeg.web.middleware.PrivacyMiddleware',

    'django.middleware.doc.XViewMiddleware',

    # Cache middleware should be last, except for ApiResponseMiddleWare,
    # which needs to be after it (in request order) so that it can
    # update the Cache-Control header before it (in reponse order).
    'django.middleware.cache.FetchFromCacheMiddleware',
    'pykeg.web.api.middleware.ApiResponseMiddleware',
)

AUTHENTICATION_BACKENDS = (
    'django.contrib.auth.backends.ModelBackend',
)

CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
        'LOCATION': 'cache',
    }
}

CACHE_MIDDLEWARE_ANONYMOUS_ONLY = True

INTERNAL_IPS = ('127.0.0.1',)

# Set to true if the database admin module should be enabled.
KEGBOT_ENABLE_ADMIN = False

### Celery
import djcelery
djcelery.setup_loader()
BROKER_URL = "django://"

CELERY_QUEUES = {
  'default' : {
    'exchange': 'default',
    'binding_key': 'default'
  },
}
CELERY_DEFAULT_QUEUE = "default"
CELERYD_CONCURRENCY = 3

### debug_toolbar

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
      'debug_toolbar.panels.settings_vars.SettingsVarsDebugPanel',
      'debug_toolbar.panels.headers.HeaderDebugPanel',
      'debug_toolbar.panels.request_vars.RequestVarsDebugPanel',
      'debug_toolbar.panels.template.TemplateDebugPanel',
      'debug_toolbar.panels.sql.SQLDebugPanel',
      'debug_toolbar.panels.signals.SignalDebugPanel',
      'debug_toolbar.panels.logger.LoggingPanel',
      #'debug_toolbar.panels.profiling.ProfilingDebugPanel',
  )

### logging

LOGGING = {
  'version': 1,
  'disable_existing_loggers': True,
  'root': {
    'level': 'WARNING',
    'handlers': ['console'],  # replaced with sentry later, if available.
  },
  'filters': {
    'require_debug_true': {
      '()': 'pykeg.core.logger.RequireDebugTrue',
    },
  },
  'handlers': {
    'console': {
      'level': 'DEBUG',
      'filters': ['require_debug_true'],
      'class': 'logging.StreamHandler',
    },
    'null': {
      'class': 'django.utils.log.NullHandler',
    },
    'cache': {
      'level': 'ERROR',
      'class': 'pykeg.core.logger.CacheHandler',
    },
  },
  'loggers': {
    'django': {
      'handlers': ['console', 'cache'],
    },
    'pykeg': {
      'handlers': ['console', 'cache'],
    },
    'raven': {
      'level': 'DEBUG',
      'handlers': ['console'],
      'propagate': False,
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

### django.contrib.messages
MESSAGE_STORAGE = 'django.contrib.messages.storage.fallback.FallbackStorage'

### django-registration
ACCOUNT_ACTIVATION_DAYS = 3

### E-mail
EMAIL_BACKEND = 'django.core.mail.backends.dummy.EmailBackend'

# Bogus default values (to prevent djangofb from choking if unavailable);
# replace with site-specific values in local_settings.py, if desired.
FACEBOOK_API_KEY = ''
FACEBOOK_SECRET_KEY = ''

### Twitter

TWITTER_CONSUMER_KEY = ''
TWITTER_CONSUMER_SECRET_KEY =''
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

TEST_RUNNER = 'django_nose.NoseTestSuiteRunner'
NOSE_ARGS = ['--exe']
SKIP_SOUTH_TESTS = True
SOUTH_TESTS_MIGRATE = False

ICANHAZ_APP_DIRNAMES = ['static/jstemplates', 'jstemplates']

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

### socialregistration (after importing common settings)

if FACEBOOK_API_KEY and FACEBOOK_SECRET_KEY:
  MIDDLEWARE_CLASSES += (
    'socialregistration.middleware.FacebookMiddleware',
  )
  AUTHENTICATION_BACKENDS += (
    'socialregistration.contrib.facebook.auth.FacebookAuth',
  )

if TWITTER_CONSUMER_KEY and TWITTER_CONSUMER_SECRET_KEY:
  AUTHENTICATION_BACKENDS += (
    'socialregistration.contrib.twitter.auth.TwitterAuth',
  )

if KEGBOT_ENABLE_ADMIN:
  INSTALLED_APPS += ('django.contrib.admin',)

