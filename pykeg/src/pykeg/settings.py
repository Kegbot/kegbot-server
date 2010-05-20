# Pykeg main settings file.
# Note: YOU SHOULD NOT NEED TO EDIT THIS FILE.  Instead, see the instructions in
# common_settings.py.example.

INSTALLED_APPS = (
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.humanize',
    'django.contrib.markup',
    'django.contrib.sessions',
    'django.contrib.sites',
    'pykeg.beerdb',
    'pykeg.billing',
    'pykeg.contrib.facebook',
    'pykeg.contrib.soundserver',
    'pykeg.contrib.twitter',
    'pykeg.core',
    'pykeg.web.api',
    'pykeg.web.kegweb',
    'registration',
    'socialregistration',
    'south',
)

AUTH_PROFILE_MODULE = "core.UserProfile"
LOGIN_REDIRECT_URL = "/account/"

### Kegweb specific stuff

ROOT_URLCONF = 'pykeg.web.urls'

TEMPLATE_DIRS = (
    # Put strings here, like "/home/html/django_templates".
    # Always use forward slashes, even on Windows.
    "web/templates",
)

SITE_ID = 1

# Absolute path to the directory that holds media.
# Example: "/home/media/media.lawrence.com/"
MEDIA_ROOT = ''

# URL that handles the media served from MEDIA_ROOT.
# Example: "http://media.lawrence.com"
MEDIA_URL = ''

# URL prefix for admin media -- CSS, JavaScript and images. Make sure to use a
# trailing slash.
# Examples: "http://foo.com/media/", "/media/".
ADMIN_MEDIA_PREFIX = '/admin_media/'

# List of callables that know how to import templates from various sources.
TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.load_template_source',
    'django.template.loaders.app_directories.load_template_source',
)

TEMPLATE_CONTEXT_PROCESSORS = (
    'django.core.context_processors.auth',
    'django.core.context_processors.debug',
    'django.core.context_processors.i18n',
    'django.core.context_processors.media',
    'django.core.context_processors.request',
    'pykeg.web.context_processors.enabled_features',
)

MIDDLEWARE_CLASSES = (
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.middleware.doc.XViewMiddleware',
    'facebook.djangofb.FacebookMiddleware',
    'socialregistration.middleware.FacebookMiddleware',
)

AUTHENTICATION_BACKENDS = (
    'django.contrib.auth.backends.ModelBackend',
    'socialregistration.auth.FacebookAuth',
)

### django-registration
ACCOUNT_ACTIVATION_DAYS = 3

# Bogus default values (to prevent djangofb from choking if unavailable);
# replace with site-specific values in common_settings.py, if desired.
FACEBOOK_API_KEY = None
FACEBOOK_SECRET_KEY = None

try:
  import common_settings
  from common_settings import *
except ImportError:
  print 'Error: Could not find common_settings.py'
  print 'Most likely, this means kegbot has not been configured properly.'
  print 'Consult setup documentation.  Exiting...'
  import sys
  sys.exit(1)
