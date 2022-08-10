.. _version-13-release-notes:

Kegbot Server Version 1.3 Release Notes
=======================================

Kegbot Server Version 1.3 is the first major new server release in many years.

This is a maintenance release, with no major new features (aside from some
much-needed upgrades to how the code works).

Special thanks to **Moad** and **Theo** for their help testing this release.

What's New
----------

Updated internal dependencies
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Kegbot Server now uses the latest version of Python and Django. In addition
almost all internal dependencies have been updated to the latest versions.

Simplified configuration from environment
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Previous releases required users to manage a ``local_settings.py`` file in the home
directory of the user running Kegbot. This made Kegbot hard to run in an environment
without a persistent disk (e.g. Heroku).

Now all configuration variables are given as environment variables; there is no need
for ``local_settings.py`` anywhere (it is ignored).

We have also reduced the number of configuration options that need to be set
in order to get things working.

Native Docker support
~~~~~~~~~~~~~~~~~~~~~

Kegbot now has an official ``Dockerfile``, and pre-built images are automatically
releases to our `package registry <https://github.com/Kegbot/kegbot-server/pkgs/container/server>`_.

Setup instructions are now in described as ``docker-compose`` steps, with an
example configuration included.

Experimental v2 API
~~~~~~~~~~~~~~~~~~~

This release includes a new REST API implementation that is intended to replace the
existing API in a future release. It is default-disabled. See :issue:`432` for more
discussion and especially if you're interested in testing/contributing.

Updated docs
~~~~~~~~~~~~

You're reading them! We've refreshed our documentation, and published a consolidated
docs site at `docs.kegbot.org <https://docs.kegbot.org/>`_.

Breaking Changes
----------------

We've removed a number of integrations to third-party services which we could not
keep maintained:

* Twitter
* Foursquare
* Untappd
* Sentry 

If you're interested in reviving and maintaining these plugins, please reach
out through the developer forums.
