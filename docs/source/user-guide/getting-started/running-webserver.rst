.. _running-webserver:

Running the Kegweb web service
==============================

The *Kegweb* web service is an essential part of Kegbot. It needs to be
running at all times.  The web service has two roles:

* *Frontend*: The kegweb service is the user-facing web site where you can see
  keg status, user statistics, and manage your system.
* *Backend and API*: The web service provides the `Kegbot API <api>`_, which
  talks to the database and records and processes drinks.

There are multiple ways to configure and run the service; we will cover two:

* `Standalone mode <webserver-standalone>`_, a simple and lightweight server,
  ideal if you're just getting started.
* `Apache mode <webserver-apache>`_, running as part of your production apache
  web server.

If you're just getting started, continue to standalone mode.  You can always
reconfigure to use Apache later.

.. _webserver-standalone:

Running the standalone server
-----------------------------

The standalone server is a simple, single-client, low-performance web server
built into ``kegbot-admin.py``. It is intended for debugging and very light
loads, but it is otherwise fully functional.

To run the standalone server, use ``kegbot-admin.py``::

  % kegbot-admin.py runserver
  Validating models...

  0 errors found
  Django version 1.3, using settings 'pykeg.settings'
  Development server is running at http://127.0.0.1:8000/
  Quit the server with CONTROL-C.

That's it! Try navigating to http://127.0.0.1:8000/; you should see the main
page of the Kegweb site.

By default, the server runs on port 8000 and is only accesible to the local
machine.  You can add arguments to listen on all IP addresses, or on another
port::

  % kegbot-admin.py runserver 0.0.0.0:8001
  Validating models...

  0 errors found
  Django version 1.3, using settings 'pykeg.settings'
  Development server is running at http://0.0.0.0:8001/
  Quit the server with CONTROL-C.

You're now ready to move on to :ref:`logging-in`.

.. _webserver-apache:

Running in an Apache server
---------------------------

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


.. _logging-in:

Logging in and configuration
----------------------------

Once your server is up and running, log in with the super user account you
created previously.  The super user has access to an additional tab in the
navigation bar: "Admin".

Navigate to "Account".  You should see a section called "API Key". Make note of
this value; you'll need it in the next section.

Head over to "Taps".  Taps define what beer is currently available in the
system.  By default, two taps are created, but you can add more if you need
them.  If you're only using one tap, don't worry about the second one.

Before you can pour a drink, you should add a new Keg to the tap.
