.. _kegbot-extras:

Extras and Add-Ons
==================

By now you've got a default Kegbot server running.  There are several more
features you can enable by installing and configuring optional components.

Sending E-Mail
--------------

Kegbot can send e-mail in several circumstances. These include:

* Initial account registration.
* Password recovery.
* Configurable notifications.

Before it can send e-mail, Kegbot must be configured with an e-mail
backend.  To use an SMTP server, add the following lines to your
``local_settings.py`` file and configure them as appropriate::
  
  # Tell Kegbot use the SMTP e-mail backend.
  EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'

  # SMTP server hostname (default: 'localhost') and port (default: 25).
  EMAIL_HOST = 'email.example.com'
  EMAIL_PORT = 25
  
  # Credentials for SMTP server.
  EMAIL_HOST_USER = 'username'
  EMAIL_HOST_PASSWORD = 'password'
  EMAIL_USE_SSL = False
  EMAIL_USE_TLS = False

  # "From" address for e-mails.
  EMAIL_FROM_ADDRESS = 'me@example.com'


Plugins
-------

Kegbot Server ships with a few built-in plugins. Most plugins require
configuration before they can be used.  To configure, see the 
*Extras* section of the admin tab.


Twitter
^^^^^^^

When enabled, the Twitter plugin can:

* Tweet when a keg is started or finished.
* Tweet when a new drinking session is started.
* Tweet when a new drink is poured.

Tweets can originate from a system account, per-user accounts, or both.

To configure the plugin, get a `Twitter developer account <https://dev.twitter.com/>`_
and set the *Consumer Key* and *Consumer Secret* through the Kegbot admin
page for Twitter.

After configuring, click *Link Account* to configure a system account.


Foursquare
^^^^^^^^^^

The Foursquare plugins allows your users to automatically check-in
to your own Foursquare venue the first time they pour in a session.

To configure, get a `Foursquare developer account <https://developer.foursquare.com/>`_
and input the *Client ID*, *Client Secret*, and *Venue ID* through the Kegbot
admin configuration page for Foursquare.

Users will also need to link their own Foursquare accounts (under the *Accounts* tab)
before the system will check in on their behalf.


Untappd
^^^^^^^

The Untappd plugin is similar to the Foursquare plugin: when the system
is configured and a drinker with a linked account pours, the plugin
will check the user in to that beer type.

The beer type must have an *Untappd ID* saved in your Kegbot beer
database; otherwise, Kegbot does not know which Untappd beer to log.

To configure, get `Untappd developer access <https://untappd.com/api/docs/>`_
and configure Kegbot with the credentials.  Users will need to link
their own Untappd accounts (under the *Account* tab) before the system
can check them in.


Web Hooks
^^^^^^^^^

You may wish to write your own service to respond to
Kegbot events. The Web Hooks plugin is an excellent way to
integrate with Kegbot, without being tightly coupled to the
server itself.

When activated, the Kegbot server will issue an HTTP ``POST``
to every configured URL whenever a system event occurs.
The body of the post data contains a single JSON message, which
includes the following fields:

* ``type``: The type of the message. Currently, this is always ``'event'``.
* ``data``: The payload of the message. This will be the system event object.

The system event JSON structure will be identical to those events
seen at the ``/api/events/`` endpoint.


Developer Extras
----------------

Certain add-ons provide enhanced developer/debugging functionality.
You probably won't be interested in these unless you're working on
Kegbot Server code.

Remote Error Logs (Sentry)
^^^^^^^^^^^^^^^^^^^^^^^^^^

Your Kegbot server can log internal errors and exceptions to a
`Sentry <https://github.com/getsentry/sentry>`_ web server. This is mostly
useful for monitoring a production site.  You can
`read the Sentry docs <http://sentry.readthedocs.org/>`_ to run your
own server, or you can `pay for a hosted Sentry server <https://www.getsentry.com/>`_.

Configuring Kegbot to log to your Sentry server is easy:

1. Be sure you have Raven, the sentry client, installed::

    (kb) pip install raven

2. In your ``local_settings.py``, add your Sentry URL (shown in your Sentry dashboard)::

    RAVEN_CONFIG = {
      'dsn': 'http://foo:bar@localhost:9000/2',
    }

Debug Toolbar
^^^^^^^^^^^^^

Developers can get extra information while Kegbot is running by
installing
`Django Debug Toolbar <https://github.com/django-debug-toolbar/django-debug-toolbar>`_.

To install::

  ### Required: Install the base package.
  (kb) $ pip install django-debug-toolbar

  ### Optional: Additional memcache stats panel.
  (kb) $ pip install django-debug-toolbar-memcache

When this package is installed and ``settings.DEBUG`` is ``True``, Kegbot will
automatically enable it; you don't need to do any additional configuration.

Stats Aggregation (StatsD)
^^^^^^^^^^^^^^^^^^^^^^^^^^

Kegbot can post server-related counters and other statistics to
`StatsD <https://github.com/etsy/statsd/>`_.  This is primarily of interest
to developers.  To install::

  (kb) $ pip install django-statsd-mozilla

Once installed, you may optionally change the default settings by adding entries
to ``local_settings.py``:

* ``STATSD_CLIENT`` (default is statsd.client)
* ``STATSD_HOST`` (default is ``localhost``)
* ``STATSD_PORT`` (default is 8125)
* ``STATSD_PREFIX`` (default is empty)

If you have the debug toolbar installed, you may instead route StatsD pings
to it by setting ``KEGBOT_STATSD_TO_TOOLBAR = True``.

Consult the `django-statsd configuration docs
<http://django-statsd.readthedocs.org/en/latest/index.html>`_ for more details.



