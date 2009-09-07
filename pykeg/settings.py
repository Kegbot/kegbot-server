# Pykeg main settings file.
# Note: YOU SHOULD NOT NEED TO EDIT THIS FILE.  Instead, see the instructions in
# common_settings.py.example.

INSTALLED_APPS = (
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.admin',
    'django.contrib.humanize',
    'django.contrib.markup',
    'pykeg.core',
    'pykeg.contrib.twitter',
)

AUTH_PROFILE_MODULE = "core.UserProfile"

try:
  import common_settings
  from common_settings import *
except ImportError:
  print 'Error: Could not find common_settings.py'
  print 'Most likely, this means kegbot has not been configured properly.'
  print 'Consult setup documentation.  Exiting...'
  import sys
  sys.exit(1)
