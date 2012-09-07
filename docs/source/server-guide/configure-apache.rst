.. _configure-apache:

Kegbot and Apache Setup
=======================

Apache configuration is more involved.

The below Apache configuration is if you are not using virtualenv for your kegbot instance.

Start with the following Apache configuration as a template::

  <VirtualHost *:80>
    ServerName kegbot.example.com

    # Replace with location to write logs.
    CustomLog /path/to/log combined

    # Replace with path to media and static folders.
    Alias /media /path/to/media
    Alias /static /path/to/static

    # Replace with path to Django admin media. To determine this, run
    # kegbot-admin.py shell
    # >>> from django.contrib import admin; print admin.__file__
    Alias /admin_media /usr/lib/python2.7/site-packages/django/contrib/admin/media/

    <Directory /path/to/media>
      AllowOverride All
      Order allow,deny
      Allow from all
    </Directory>

    <Directory /path/to/static>
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
      PythonPath "['/path/to/kegbot/lib/python2.7', '/etc/kegbot'] + sys.path"
    </Location>

    <Location "/media">
      SetHandler None
      Options -Indexes
    </Location>

    <Location "/static">
      SetHandler None
      Options -Indexes
    </Location>

    <Location "/admin_media">
      SetHandler None
      Options -Indexes
    </Location>

  </VirtualHost>


This Apache configuration is if you have a virtualenv configured for kegbot.
NOTE: you will need mod_wsgi enabled for Apache.

Start with the following Apache configuration as a template::

  <VirtualHost *:80>
    ServerName kegbot.example.com

    # Replace with location to write logs.
    CustomLog /path/to/log combined

    # Replace with path to media and static folders.
    Alias /media /path/to/media
    Alias /static /path/to/static

    # Replace with path to Django admin media. To determine this, run
    # kegbot-admin.py shell
    # >>> from django.contrib import admin; print admin.__file__
    Alias /admin_media /usr/lib/python2.7/site-packages/django/contrib/admin/media/

    <Directory /path/to/media>
      AllowOverride All
      Order allow,deny
      Allow from all
    </Directory>

    <Directory /path/to/static>
      AllowOverride All
      Order allow,deny
      Allow from all
    </Directory>

    # Setup mod_wsgi
    WSGIDaemonProcess kegweb display-name=kegweb user=www-data processes=2 threads=15
    WSGIScriptAlias / /path/to/kegbot/kegbot/pykeg/kegweb.wsgi

    <Location "/media">
      SetHandler None
      Options -Indexes
    </Location>

    <Location "/static">
      SetHandler None
      Options -Indexes
    </Location>

    <Location "/admin_media">
      SetHandler None
      Options -Indexes
    </Location>

  </VirtualHost>