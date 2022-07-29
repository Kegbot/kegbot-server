.. _settings:

Settings
========

Most Kegbot features and behaviors are controlled within the web application
by using your admin account. However, a handful of settings are managed outside
of the web application, as environment variables, and are described here.

Available settings
------------------

This section lists all settings (environment variables) the server recognizes.

Required settings
~~~~~~~~~~~~~~~~~

These settings have no default and must be set by you. (When you use ``docker-compose``
with the example configuration in these docs, all required values will be set.)

.. data:: DATABASE_URL

  Credentials to the Kegbot database. Should be a value of the form
  ``mysql://USER:PASSWORD@HOST:PORT/NAME`` or ``postgres://USER:PASSWORD@HOST:PORT/NAME``.
  ``PORT`` and ``PASSWORD`` are optional.

  **Example:** ``mysql://kegbot@localhost/kegbot``

.. data:: REDIS_URL

  URL to the Kegbot Redis instance, in the format ``redis://:PASSWORD@HOST:PORT/DATABASE``.
  ``PASSWORD`` and ``PORT`` are optional.

  **Example:** ``redis://localhost/0``

.. data:: KEGBOT_SECRET_KEY

  A random value, like a password, that will be used to generate and protect
  certain values used by the web service, such as cookies. Changing this
  value will cause all users to be logged out and will invalidate any
  pending invitations. Generally, you should only change this value if it has
  become compromised.

Optional settings
~~~~~~~~~~~~~~~~~

These settings all have defaults, which you may override.

.. data:: KEGBOT_ENV

  Controls debug mode and other settings. Should be ``production`` in production;
  default ``debug``.

.. data:: KEGBOT_DATA_DIR

  Filesystem path where Kegbot-specific data is stored and managed.
  Default: ``/kegbot-data``.

.. data:: KEGBOT_BASE_URL
  
  The base public URL of this Kegbot system, for example
  ``https://kegbot.example.com/``. If set, Kegbot will use this when
  creating links to media and other events. If left blank (default),
  the system will attempt to guess the correct address when needed.

.. data:: KEGBOT_INSECURE_SHARED_API_KEY

  If set, a random value, like a password, that will always be accepted as
  an API key. As the name suggests, it is insecure to use this feature,
  which is intended only for use in special standalone/embedded installs
  (e.g. a single-user, offline Raspberry Pi) where there is no risk of exposure.

Advanced and experimental settings
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

These settings control experimental features. They are subject to
change and should only be needed by advanced users.

.. data:: KEGBOT_MEDIA_URL

  If specified, images and other media served by Kegbot will
  be prefixed by this URL. Otherwise, media will be served from
  the same host as the server itself, under ``/media``. You may use
  this setting to e.g. serve media links through a CDN.

.. data:: KEGBOT_ENABLE_V2_API

  If set to ``true``, the new Kegbot Server API will be enabled (at
  path ``/api/v2/...``). This API will replace the existing API implementation
  in a future major Kegbot release. It is currently unfinished. Enable this
  if you are a developer intending to work on or with this API.
