"""Defines HAVE_* flags for several optional packages."""

import imp
from django.core.exceptions import ImproperlyConfigured

try:
    import debug_toolbar
    HAVE_DEBUG_TOOLBAR = True
except ImportError:
    HAVE_DEBUG_TOOLBAR = False

try:
    import raven.contrib.django
    HAVE_RAVEN = True
except ImportError:
    HAVE_RAVEN = False

try:
    import django_statsd
    HAVE_STATSD = True
except ImproperlyConfigured:
    # Good enough; statsd is fussy on import.
    HAVE_STATSD = True
except ImportError:
    HAVE_STATSD = False

try:
    import storages
    HAVE_STORAGES = True
except ImportError:
    HAVE_STORAGES = False

try:
    import memcache
    HAVE_MEMCACHE = True
except ImportError:
    HAVE_MEMCACHE = False

try:
    import pylibmc
    HAVE_PYLIBMC = True
except ImportError:
    HAVE_PYLIBMC = False

try:
    import debug_toolbar_memcache
    HAVE_MEMCACHE_TOOLBAR = True
except ImportError:
    HAVE_MEMCACHE_TOOLBAR = False

try:
    import johnny
    HAVE_JOHNNY_CACHE = True
except ImportError:
    HAVE_JOHNNY_CACHE = False

try:
    import djcelery_email
    HAVE_CELERY_EMAIL = True
except ImportError:
    HAVE_CELERY_EMAIL = False
