.. _upgrading-kegbot:

Upgrading
=========

Upgrade notes
-------------

Occasionally we make changes to Kegbot that require special steps or attention
when upgrading.  Though the section below covers the most commonly-needed
upgrade steps, always read the upgrade notes in :ref:`the changelog <changelog>`
first.

Upgrade procedure
-----------------

First, ensure the system has been stopped::

    $ docker-compose down

Next, restart just the database and redis::

    $ docker-compose up -d mysql redis

Next, run the upgrade command::

    $ docker-compose run kegbot upgrade

You will see upgrade progress, followed by the message  ``Upgrade complete!``. If
you see the message ``Version <version> is already installed.``, then no upgrade
was needed or performed.