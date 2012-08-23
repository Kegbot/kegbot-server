.. _configure-apache:

Kegbot and Apache Setup
=======================

Apache configuration is more involved.

Start with the following Apache configuration as a template::

  <VirtualHost *:80>
    ServerName kegbot.example.com
    CustomLog /path/to/log combined      # Replace with location to write logs.

    Alias /media /path/to/media          # Create me somewhere.

    # Replace with path to Django admin media. To determine this, run
    # kegbot-admin.py shell
    # >>> from django.contrib import admin; print admin.__file__
    Alias /admin_media /usr/lib/python2.7/site-packages/django/contrib/admin/media/

    <Directory /path/to/media>
      AllowOverride All
      Order allow,deny
      Allow from all
    </Directory>

    <Location "/">
      SetHandler python-program
      PythonHandler django.core.handlers.modpython
      SetEnv DJANGO_SETTINGS_MODULE pykeg.settings
      SetEnv TZ America/Los_Angeles        # Replace with your preferred time zone.
      PythonOption django.root
      PythonDebug On
      PythonPath "['/path/to/kegbot', '/etc/kegbot'] + sys.path"
    </Location>

    <Location "/media">
      SetHandler None
      Options -Indexes
    </Location>

    <Location "/admin_media">
      SetHandler None
      Options -Indexes
    </Location>

  </VirtualHost>


