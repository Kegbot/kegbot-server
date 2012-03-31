# Pykeg main settings file.
# Note: YOU SHOULD NOT NEED TO EDIT THIS FILE.  Instead, see the instructions in
# common_settings.py.example.

INSTALLED_APPS = (
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.humanize',
    'django.contrib.markup',
    'django.contrib.messages',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.staticfiles',

    'debug_toolbar',
    'django_extensions',
    'bootstrapform',
    'imagekit',
    'pykeg.beerdb',
    'pykeg.connections',
    'pykeg.connections.foursquare',
    'pykeg.connections.twitter',
    'pykeg.connections.untappd',
    'pykeg.contrib.soundserver',
    'pykeg.core',
    'pykeg.web',
    'pykeg.web.api',
    'pykeg.web.account',
    'pykeg.web.charts',
    'pykeg.web.kegweb',
    'icanhaz',
    'raven.contrib.django',
    'registration',
    'sentry',
    'socialregistration',
    'socialregistration.contrib.twitter',
    'socialregistration.contrib.facebook',
    'socialregistration.contrib.foursquare',


    # Celery and dependencies.
    'djcelery',
    'djkombu',

    # Tornado
    'rjdj.djangotornado',

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
    # Put strings here, like "/home/html/django_templates".
    # Always use forward slashes, even on Windows.
    "web/templates",
)

SITE_ID = 1

# Absolute filesystem path to the directory that will hold user-uploaded files.
# Example: "/home/media/media.lawrence.com/media/"
MEDIA_ROOT = ''

# URL that handles the media served from MEDIA_ROOT. Make sure to use a
# trailing slash.
# Examples: "http://media.lawrence.com/media/", "http://example.com/media/"
MEDIA_URL = ''

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

# List of callables that know how to import templates from various sources.
TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.Loader',
    'django.template.loaders.app_directories.Loader',
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
    'pykeg.web.middleware.SiteActiveMiddleware',
    'django.middleware.doc.XViewMiddleware',
    'django.middleware.cache.FetchFromCacheMiddleware',
    'debug_toolbar.middleware.DebugToolbarMiddleware',
)

AUTHENTICATION_BACKENDS = (
    'django.contrib.auth.backends.ModelBackend',
)

CACHES = {
    #'default': {
    #    'BACKEND': 'django.core.cache.backends.db.DatabaseCache',
    #    'LOCATION': 'cache',
    #}
}

CACHE_MIDDLEWARE_ANONYMOUS_ONLY = True

### debug_toolbar

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

INTERNAL_IPS = ('127.0.0.1',)

### django.contrib.messages
MESSAGE_STORAGE = 'django.contrib.messages.storage.fallback.FallbackStorage'

### django-registration
ACCOUNT_ACTIVATION_DAYS = 3

# Bogus default values (to prevent djangofb from choking if unavailable);
# replace with site-specific values in common_settings.py, if desired.
FACEBOOK_API_KEY = ''
FACEBOOK_SECRET_KEY = ''

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

TEST_RUNNER = 'django_nose.NoseTestSuiteRunner'
NOSE_ARGS = ['--exe']
SKIP_SOUTH_TESTS = True
SOUTH_TESTS_MIGRATE = False

ICANHAZ_APP_DIRNAMES = ['static/jstemplates', 'jstemplates']

try:
  import common_settings
  from common_settings import *
except ImportError:
  msg = """ Error: Could not find common_settings.py
  Most likely, this means kegbot has not been configured properly.
  Consult setup documentation.  Exiting..."""
  raise ImportError(msg)

### Optional stuff
if FACEBOOK_API_KEY and FACEBOOK_SECRET_KEY:
  #INSTALLED_APPS += ('pykeg.contrib.facebook',)
  MIDDLEWARE_CLASSES += (
    'socialregistration.middleware.FacebookMiddleware',
  )
  AUTHENTICATION_BACKENDS += (
    'socialregistration.contrib.facebook.auth.FacebookAuth',
  )

if TWITTER_CONSUMER_KEY and TWITTER_CONSUMER_SECRET_KEY:
  AUTHENTICATION_BACKENDS += (
    'socialregistration.auth.TwitterAuth',
  )
