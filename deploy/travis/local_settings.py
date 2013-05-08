# Kegbot local settings, for travis-ci.org build

# NEVER set DEBUG to `True` in production.
import os

HOME = os.environ['HOME']

DEBUG = True
TEMPLATE_DEBUG = DEBUG

DATABASES = {'default': {'ENGINE': 'django.db.backends.sqlite3', 'NAME': HOME + '/kegbot-data/kegbot.sqlite'}}

KEGBOT_ROOT = HOME + '/kegbot-data'

MEDIA_ROOT = KEGBOT_ROOT  + '/media'

STATIC_ROOT = KEGBOT_ROOT + '/static'

TIME_ZONE = 'America/Los_Angeles'

CACHES = {'default': {'LOCATION': '127.0.0.1:11211', 'BACKEND': 'django.core.cache.backends.memcached.MemcachedCache'}}

SECRET_KEY = 'testkey'

