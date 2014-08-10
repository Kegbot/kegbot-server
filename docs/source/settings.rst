.. _settings:

Appendix: Extra Settings
========================

This section lists settings that may be added to ``local_settings.py``.
Most of these options serve uncommon needs.

In addition to settings described here, any of
`Django's built-in settings <https://docs.djangoproject.com/en/dev/topics/settings/>`_
may be listed in ``local_settings.py``.

.. data:: ALLOWED_HOSTS
    :noindex:

    Lists allowed hostnames that the server will respond to.  See the
    `Django documentation for ALLOWED_HOSTS <https://docs.djangoproject.com/en/dev/ref/settings/#std:setting-ALLOWED_HOSTS>`_
    for more information.

    Default is ``['*']`` (any hostname accepted).

    ::

        ALLOWED_HOSTS = ['kegbot.example.com']


.. data:: KEGBOT_BASE_URL
    :noindex:

    Ordinarily, Kegbot will infer your site's hostname and base URL from
    incoming requests.  This hostname is used to compose full URLs, for example
    when generating the links in outgoing e-mails and plugin posts.

    In some situations you may want to set this value explicitly, for example
    if your server is available on multiple hostnames.

    Default is unset (automatic mode).

    ::

        KEGBOT_BASE_URL = 'http://mykegbot.example:8001/'


.. data:: KEGBOT_ENABLE_ADMIN
    :noindex:

    When set to ``true``, the `Django Admin Site <https://docs.djangoproject.com/en/dev/ref/contrib/admin/>`_
    will be enabled, allowing you to browse and edit raw Kegbot data through a web
    interface.

    **Warning:** Editing raw Kegbot data through the admin interface may leave
    your system in a corrupt or inconsistent state.

    Default is ``False``.

    ::

        KEGBOT_ENABLE_ADMIN = True

.. data:: LOGGING['handlers']['redis']['url']
    :noindex:

    When specified, this setting gives the URL of a redis instance to
    use for temporary log data.  The URL is parsed by `redis.from_url`.

    Default is ``redis://localhost:6379``.
