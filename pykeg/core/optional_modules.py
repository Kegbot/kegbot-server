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
  import storages
  HAVE_STORAGES = True
except ImportError:
  HAVE_STORAGES = False