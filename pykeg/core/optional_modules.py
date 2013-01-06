"""Defines HAVE_* flags for several optional packages."""

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
  import sentry
  HAVE_SENTRY = True
except ImportError:
  HAVE_SENTRY = False

try:
  import celery
  HAVE_CELERY = True
except ImportError:
  HAVE_CELERY = False

try:
  import djcelery
  HAVE_DJCELERY = True
except ImportError:
  HAVE_DJCELERY = False

try:
  import djkombu
  HAVE_DJKOMBU = True
except ImportError:
  HAVE_DJKOMBU = False

try:
  import rjdj.djangotornado
  HAVE_DJANGOTORNADO = True
except ImportError:
  HAVE_DJANGOTORNADO = False
