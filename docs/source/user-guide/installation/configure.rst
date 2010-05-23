.. _configure-kegbot:

Setup & Configure Kegbot
========================

In this section, you will point your new Kegbot installation to its database,
and get the development webserver up and running.

Create the settings file
------------------------

Pykeg needs a little bit of static configuration before it works.  At the
moment, Pykeg uses a `Django Settings file
<http://docs.djangoproject.com/en/dev/topics/settings/>`_ for all of its
configuration.  Mostly, you just need to tell Pykeg what kind of database to
use.

The kegbot core applications (`kegbot_admin.py`, `kegbot_core.py`, and so on)
will search for a settings file in two locations:

* `~/.kegbot/common_settings.py`
* `/etc/kegbot/common_settings.py`

You can use either location, but in these instructions we'll use `~/.kegbot/`.
Follow these steps to create and edit that file.

#. Create a new directory in your homedir to store kegbot settings::

	% mkdir ~/.kegbot

#. Copy the example settings file (from the ``pykeg/`` directory) into your new
   local directory::

	% cp common_settings.py.example ~/.kegbot/common_settings.py

Next, you need to edit the settings for your database.

Configure Kegbot for MySQL
--------------------------

Follow this section if you will be using MySQL.

Open the file ``~/.kegbot/common_settings.py`` in your favorite text editor.
Look for the section labeled "Database Configuration", and edit it to have the
following lines to the file::

  DATABASE_ENGINE = 'mysql'
  DATABASE_NAME = 'kegbot'
  DATABASE_USER = 'kegbot'
  DATABASE_PASSWORD = 'your-password'

Replace the text `your-password` with the actual password you used (in
:ref:`create-mysql-user`).

Configure Kegbot for SQLite
---------------------------

Follow this section if you will be using SQLite.

Before you can use SQLite, you need to decide where on disk it should store the
database file. In this example, we assume the database will be stored at
``/home/kegbot/kegbot.sqlite``, though you can use any other location on the
filesystem.

Open the file ``~/.kegbot/common_settings.py`` in your favorite text editor.
Look for the section labeled "Database Configuration", and edit it to have the
following lines to the file::

  DATABASE_ENGINE = 'sqlite'
  DATABASE_NAME = '/home/kegbot/kegbot.sqlite'

Save the settings file.


.. _populate-databases:

Populate Databases
------------------

Now that the database is ready, you must install the various kegbot tables and
defaults::

  % kegbot_admin.py kb_setup

And for the most important part, create your admin account!::

  % kegbot_admin.py createsuperuser

