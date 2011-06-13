#!/usr/bin/env python
# kegweb.wsgi -- WSGI config for kegbot

import os, site, sys

# Partially cribbed from:
#   http://jmoiron.net/blog/deploying-django-mod-wsgi-virtualenv/
# WSGI configuration reference:
#   http://code.google.com/p/modwsgi/wiki/ConfigurationDirectives
#
# Basic instructions for use:
#
# (1) Copy this file to somewhere accessible by the webserver.  It should *not*
#     part of your site's DocumentRoot, for security reasons.
# (2) If you are using virtualenv, edit the VIRTUAL_ENV variable below to point
#     to the base directory of the virtualenv.
# (3) Edit your Apache config to point to this file.  Simple example settings
#     are shown below; you may need something fancier.
#
#     <VirtualHost>
#       # ...
#
#       WSGIDaemonProcess mykegbot
#       WSGIProcessGroup mykegbot
#       WSGIScriptAlias / /path/to/kegweb.wsgi
#
#       Alias /media /path/to/media_dir/
#       Alias /admin_media /path/to/django/contrib/admin/media/
#
#       # ...
#    </VirtualHost>

### Configuration section -- modify me for your install.

# If you are using a virtualenv, set the path to its base directory here.  If
# not (kegbot and all its dependencies are installed in the default Python
# path), leave it blank.
VIRTUAL_ENV = '/path/to/virtualenv/kb'

# The common_settings.py config needs to be on the PATH as well. By default,
# kegbot looks in # $HOME/.kegbot and /etc/kegbot.  Only change this if you are
# doing something different.
EXTRA_PATHS = [
    os.path.join(os.environ.get('HOME'), '.kegbot'),
    '/etc/kegbot',
]

### Main script -- should not need to edit past here.

_orig_sys_path = list(sys.path)

if VIRTUAL_ENV:
  # If we have a VIRTUAL_ENV, add it as a site dir.
  PYTHON_NAME = 'python%i.%i' % sys.version_info[:2]
  PACKAGES = os.path.join(VIRTUAL_ENV, 'lib', PYTHON_NAME, 'site-packages')
  site.addsitedir(PACKAGES)

# Add the kegbot common_settings.py locations to the path.
for path in EXTRA_PATHS:
  sys.path.append(path)

# Adjust so any new dirs are prepended.
_sys_path_prepend = [p for p in sys.path if p not in _orig_sys_path]
for item in _sys_path_prepend:
  sys.path.remove(item)
sys.path[:0] = _sys_path_prepend

# Import django (which must be done after any path adjustments), and start the
# handler.
from django.core.handlers.wsgi import WSGIHandler
os.environ['DJANGO_SETTINGS_MODULE'] = 'pykeg.settings'
application = WSGIHandler()

