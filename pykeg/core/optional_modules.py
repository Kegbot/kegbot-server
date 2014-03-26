"""Defines HAVE_* flags for several optional packages."""

import imp

try:
    imp.find_module('debug_toolbar')
    HAVE_DEBUG_TOOLBAR = True
except ImportError:
    HAVE_DEBUG_TOOLBAR = False

try:
    imp.find_module('raven.contrib.django')
    HAVE_RAVEN = True
except ImportError:
    HAVE_RAVEN = False

try:
    imp.find_module('django_statsd')
    HAVE_STATSD = True
except ImportError:
    HAVE_STATSD = False

try:
    imp.find_module('storages')
    HAVE_STORAGES = True
except ImportError:
    HAVE_STORAGES = False

try:
    imp.find_module('memcache')
    HAVE_MEMCACHE = True
except ImportError:
    HAVE_MEMCACHE = False

try:
    imp.find_module('pylibmc')
    HAVE_PYLIBMC = True
except ImportError:
    HAVE_PYLIBMC = False

try:
    imp.find_module('debug_toolbar_memcache')
    HAVE_MEMCACHE_TOOLBAR = True
except ImportError:
    HAVE_MEMCACHE_TOOLBAR = False

try:
    imp.find_module('djcelery_email')
    HAVE_CELERY_EMAIL = True
except ImportError:
    HAVE_CELERY_EMAIL = False

try:
    imp.find_module('django_nose')
    HAVE_DJANGO_NOSE = True
except ImportError:
    HAVE_DJANGO_NOSE = False
