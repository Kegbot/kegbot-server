.. _settings:

Settings
========

Most Kegbot features and behaviors are controlled within the web application
by using your admin account. However, a handful of settings are managed outside
of the web application, and are described here.

Available settings
------------------

These values can be set in the shell environment of the server program.

.. data:: KEGBOT_ENV

  Controls debug mode and other settings. Should be ``production`` in production;
  default ``debug``.

.. data:: KEGBOT_DATA_DIR

  Filesystem path where Kegbot-specific data is stored and managed.
  Default: ``/kegbot-data``.

.. data:: KEGBOT_DATABASE_URL

  Credentials to the Kegbot database. Should be a value of the form
  ``mysql://USER:PASSWORD@HOST:PORT/NAME`` or ``postgres://USER:PASSWORD@HOST:PORT/NAME``.
  ``PORT`` and ``PASSWORD`` are optional.

  **Example:** ``mysql://kegbot@localhost/kegbot``

.. data:: KEGBOT_EMAIL_FROM_ADDRESS

  The "From:" address to use in emails from the system. No default.

.. data:: KEGBOT_EMAIL_URL

  SMTP configuration URL. Should be a value in the form
  ``smtp://USER:PASSWORD@HOST:PORT`` or ``submission://USER:PASSWORD@HOST:PORT``.
  Make sure to URL encode any special characters in USER and PASSWORD.

  **Gmail Example:** ``submission://kegbot%40kegbot.org:secretpassword@smtp.gmail.com``
  **Local Relay Example:** ``smtp:``

.. data:: KEGBOT_REDIS_URL

  URL to the Kegbot Redis instance, in the format ``redis://:PASSWORD@HOST:PORT/DATABASE``. ``PASSWORD`` and ``PORT`` are optional.

  **Example:** ``redis://localhost/0``

.. data:: KEGBOT_SECRET_KEY

    A random value, like a password, that will be used to generate and protect
    certain values used by the web service, such as cookies. Changing this
    value will cause all users to be logged out and will invalidate any
    pending invitations. Generally, you should only change this value if it has
    become compromised.

.. data:: KEGBOT_INSECURE_SHARED_API_KEY

    If set, a random value, like a password, that will always be accepted as
    an API key. As the name suggests, it is insecure to use this feature,
    which is intended only for use in special standalone/embedded installs
    (e.g. a single-user, offline Raspberry Pi) where there is no risk of exposure.

.. data:: KEGBOT_SETUP_ENABLED

    If set to ``true``, the server will enable "setup mode". The server can
    only be configured and upgraded when this mode is enabled. For security
    reasons, this mode is disabled by default and must be explicitly enabled
    by an administrator.


Configuration file
------------------

If you prefer, settings may be given in a config file instead. The
configuration file must be located at ``$KEGBOT_DATA_DIR/kegbot.cfg``.

The format is an `INI-style config file <https://en.wikipedia.org/wiki/INI_file>`_
with a single section named ``config``. Any environment value may be
given as a key in this section (with the exception of ``KEGBOT_DATA_DIR``,
which can never be read from this file).

Here is an example config file::

  [config]
  KEGBOT_SECRET_KEY = my-1337-s3kr3t
  KEGBOT_DATABASE_URL = mysql://my_user@localhost:password/kegbot_test
  KEGBOT_REDIS_URL = redis://localhost/0

Precedence of settings
----------------------

When a value is specified in both the environment `and` the config file,
the value from the environment takes precedence.
