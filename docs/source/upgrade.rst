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

    $ docker compose down

Step 2
~~~~~~

Next, fetch the latest images::

    $ docker compose pull

Step 3
~~~~~~

Next, restart just the database and redis::

    $ docker compose up -d mysql redis

Step 4
~~~~~~

Next, run the upgrade command::

    $ docker compose run kegbot upgrade

You will see upgrade progress, followed by the message  ``Upgrade complete!``. If
you see the message ``Version <version> is already installed.``, then no upgrade
was needed or performed.

Step 5
~~~~~~

Finally, restart the containers::

    $ docker compose up -d kegbot workers

.. _upgrade-legacy:

Upgrading from very old versions
--------------------------------

Backups created by Kegbot v1.1.x (the "format 1" zipfile format) can be
restored directly into this version; no intermediate v1.2/v1.3 installation
is needed.

Place the backup zipfile somewhere the container can read it — for example,
your ``kegbot-data`` directory — then, starting from a fresh (empty)
database::

    $ docker compose run kegbot restore /kegbot-data/my-old-backup.zip

The restore loads the old data, upgrades it in place, and regenerates
statistics.
