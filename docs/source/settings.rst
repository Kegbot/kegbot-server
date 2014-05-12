.. _settings:

Appendix: Extra Settings
========================

This section lists settings that may be added to `local_settings.py`.
Most of these options serve uncommon needs.

.. data:: KEGBOT_BASE_URL
    :noindex:

    Ordinarily, Kegbot will infer your site's hostname from
    incoming requests.  This hostnamename is used to compose full URLs, for example
    when generating the links contained in outgoing e-mails and plugin posts.

    In some situations you may want to set this value explicitly, for example
    if your server is available on multiple hostnames.

    Default is unset.

    ::

        KEGBOT_BASE_URL = 'http://mykegbot.example:8001/'


.. data:: KEGBOT_ENABLE_ADMIN
    :noindex:

    When set to ``true``, the `Django Admin Site <https://docs.djangoproject.com/en/dev/ref/contrib/admin/>`
    will be enabled, allowing you to browse and edit raw Kegbot data through a web
    interface.

    **Warning:** Editing raw Kegbot data through the admin interface may leave
    your system in a corrupt or inconsistent state.

    Default is ``False``.

    ::

        KEGBOT_ENABLE_ADMIN = True

