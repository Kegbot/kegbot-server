.. _upgrading-kegbot:

Upgrade from a Previous Version
===============================

Upgrade notes
-------------

Occasionally we make changes to Kegbot that require special steps or attention
when upgrading.  Though the section below covers the most commonly-needed
upgrade steps, always read the upgrade notes in :ref:`the changelog <changelog>`
first.

Upgrade procedure
-----------------

.. warning::
  Always make a backup of your data prior to upgrading Kegbot.

1. If running from git, do a ``git pull``.

2. Step in to your virtualenv and upgrade to the new version.

  If you used ``pip`` last time::

    (kb) $ pip install --upgrade kegbot

  If you used ``setup.py`` last time::

    (kb) $ ./setup.py develop

3. Run the upgrade script::

    (kb) $ kegbot kb_upgrade

4. Restart the Kegbot web server.


