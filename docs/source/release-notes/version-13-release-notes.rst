.. _version-13-release-notes:

Kegbot Server Version 1.3 Release Notes
=======================================

Kegbot Server Version 1.3 is the first major new server release in 3 years.
The release is

What's New
----------

Simplified configuration from envrionment
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Previous releases required users to manage a ``local_settings.py`` file in the home
directory of the user running Kegbot. This made Kegbot hard to run in an environment
without a persistent disk (e.g. Heroku).

Now all configuration variables can be given as envrionment variables. Optionally,
a greatly simplified configuration file formal is supported, replacing
``local_settings.py``.


Native Docker support
~~~~~~~~~~~~~~~~~~~~~

Kegbot now has an official ``Dockerfile`` and corresponding images on Docker Hub.


Other Changes
~~~~~~~~~~~~~

* Kegbot Server has been updated to the latest versions of Django and other dependencies.
