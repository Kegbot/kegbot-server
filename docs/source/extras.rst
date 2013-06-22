.. _kegbot-extras:

Extras and Add-Ons
==================

By now you've got a default Kegbot server running.  There are several more
features you can enable by installing and configuring optional components.

Remote Error Logs (Sentry)
--------------------------

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
-------------

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
--------------------------

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



