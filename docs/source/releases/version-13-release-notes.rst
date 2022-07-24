.. _version-13-release-notes:

Kegbot Server Version 1.3 Release Notes
=======================================

Kegbot Server Version 1.3 is the first major new server release in many years.

This is a maintenance release, with no major new features (aside from some
much-needed upgrades to how the code works).

What's New
----------

Simplified configuration from environment
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Previous releases required users to manage a ``local_settings.py`` file in the home
directory of the user running Kegbot. This made Kegbot hard to run in an environment
without a persistent disk (e.g. Heroku).

Now all configuration variables are given as environment variables; there is no need
for ``local_settings.py`` anywhere (it is ignored).


Native Docker support
~~~~~~~~~~~~~~~~~~~~~

Kegbot now has an official ``Dockerfile`` and corresponding images on Docker Hub.
All instructions are now in described as ``docker-compose`` steps.


Other Changes
~~~~~~~~~~~~~

* Kegbot Server has been updated to the latest versions of Django and other dependencies.
