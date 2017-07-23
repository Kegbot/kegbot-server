#!/usr/bin/env python
# kegweb.wsgi -- WSGI config for kegbot

import os
import site
import sys

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

# Configuration section -- modify me for your install.

# If you are using a virtualenv, set the path to its base directory here.  If
# not (kegbot and all its dependencies are installed in the default Python
# path), leave it blank.
VIRTUAL_ENV = '/path/to/virtualenv/kb'

# Main script -- should not need to edit past here.

if VIRTUAL_ENV:
    # If we have a VIRTUAL_ENV, add it as a site dir.
    PYTHON_NAME = 'python%i.%i' % sys.version_info[:2]
    PACKAGES = os.path.join(VIRTUAL_ENV, 'lib', PYTHON_NAME, 'site-packages')
    site.addsitedir(PACKAGES)


# Import django (which must be done after any path adjustments), and start the
# handler.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'pykeg.settings')
from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()
