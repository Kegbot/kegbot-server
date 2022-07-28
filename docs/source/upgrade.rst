.. _upgrading:

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

Step 1
~~~~~~

First, ensure the system has been stopped::

    $ docker-compose down

Step 2
~~~~~~

Next, fetch the latest images::

    $ docker-compose build --pull

Step 3
~~~~~~

Next, restart just the database and redis::

    $ docker-compose up -d mysql redis

Step 4
~~~~~~

Finally, run the upgrade command::

    $ docker-compose run kegbot upgrade

You will see upgrade progress, followed by the message  ``Upgrade complete!``. If
you see the message ``Version <version> is already installed.``, then no upgrade
was needed or performed.