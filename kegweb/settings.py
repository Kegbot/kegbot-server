# Kegweb main settings file.
# Note: YOU SHOULD NOT NEED TO EDIT THIS FILE.  Instead, see the instructions in
# common_settings.py.example in the pykeg package.

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
ADMIN_MEDIA_PREFIX = '/media/'

# List of callables that know how to import templates from various sources.
TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.load_template_source',
    'django.template.loaders.app_directories.load_template_source',
)

MIDDLEWARE_CLASSES = (
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.middleware.doc.XViewMiddleware',
)

ROOT_URLCONF = 'kegweb.urls'

TEMPLATE_DIRS = (
    # Put strings here, like "/home/html/django_templates".
    # Always use forward slashes, even on Windows.
    "templates",
)

INSTALLED_APPS = (
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.admin',
    'django.contrib.humanize',
    'django.contrib.markup',
    'pykeg.core',
    'kegweb.accounting',
    'kegweb.kegweb',
    'registration',
)

AUTH_PROFILE_MODULE = "core.UserProfile"
LOGIN_REDIRECT_URL = "/account/"

### Begin importhacks excerpt

import os
import sys

SYSTEM_SETTINGS_DIR = "/etc/kegbot"
HOME_DIR = os.environ.get('HOME')
USER_SETTINGS_DIR = os.path.join(HOME_DIR, '.kegbot')

# Greatest precedence: $HOME/.kegbot/
if USER_SETTINGS_DIR not in sys.path:
  sys.path.append(USER_SETTINGS_DIR)

# Next precedence: /etc/kegbot
if SYSTEM_SETTINGS_DIR not in sys.path:
  sys.path.append(SYSTEM_SETTINGS_DIR)

### End importhacks excerpt


# Import local common settings
try:
  import common_settings
  from common_settings import *
except ImportError:
  print 'Error: Could not find common_settings.py'
  print 'Most likely, this means kegbot has not been configured properly.'
  print 'Consult setup documentation.  Exiting...'
  raise
  import sys
  sys.exit(1)

# Import local kegweb settings (todo)
