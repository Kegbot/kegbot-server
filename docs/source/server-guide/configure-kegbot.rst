.. _configure-kegbot:

Configure Kegbot Server
=======================

In this section, you will point your new Kegbot Server installation to its database.

Create the settings file
------------------------

Kegbot Server needs a little bit of static configuration before it works.  At the
moment, Kegbot Server uses a `Django Settings file
<http://docs.djangoproject.com/en/dev/topics/settings/>`_ for all of its
configuration.  Mostly, you just need to tell Kegbot Server what kind of database to
use and where Kegbot Server will store files used by the webservice.

Kegbot will search for a settings file in two locations:

* ``~/.kegbot/local_settings.py``
* ``/etc/kegbot/local_settings.py``

You can use either location, but in these instructions we'll use `~/.kegbot/`.
Follow these steps to create and edit that file.

#. Create a new directory in your homedir to store kegbot settings::

	$ mkdir ~/.kegbot

#. Copy the example settings file (from the ``pykeg/`` directory) into your new
   local directory::

	$ cp local_settings.py.example ~/.kegbot/local_settings.py

Next, you need to edit the settings file for your Kegbot Server.

Configure Kegbot for MySQL
--------------------------

Follow this section if you will be using MySQL.

Open the file ``~/.kegbot/local_settings.py`` in your favorite text editor.
Look for the section labeled "Database Configuration", and edit it to have the
following lines to the file::

  DATABASES = {
    'default' : {
      'NAME' : 'kegbot',
      'ENGINE' : 'django.db.backends.mysql',
      'USER' : 'kegbot',
      'PASSWORD': 'your-password',
    },
  }

Replace the text `your-password` with the actual password you used in(
:ref:`create-mysql-user`).

Save the settings file.

Configure Kegbot for SQLite
---------------------------

Follow this section if you will be using SQLite.

Before you can use SQLite, you need to decide where on disk it should store the
database file. In this example, we assume the database will be stored at
``/home/kegbot/kegbot.sqlite``, though you can use any other location on the
filesystem.

Open the file ``~/.kegbot/local_settings.py`` in your favorite text editor.
Look for the section labeled "Database Configuration", and edit it to have the
following lines to the file::

  DATABASES = {
    'default' : {
      'NAME' : '/home/kegbot/kegbot.sqlite',
      'ENGINE' : 'django.db.backends.sqlite3',
    },
  }

Save the settings file.

Configure Kegbot Media and Static File Directories
--------------------------------------------------

Follow this section for all Kegbot Server installations.

Open the file ``~/.kegbot/local_settings.py`` in your favorite text editor.
Look for the section labeled "Media and Static Files", and edit the MEDIA_ROOT
and STATIC_ROOT directory locations.::

MEDIA_ROOT = '/path/to/media/'
STATIC_ROOT = '/path/to/static'

Save the settings file.

.. _populate-databases:

Populate databases
------------------

Run Kegbot's setup tool to load the database with various defaults::

  $ kegbot-admin.py kb_setup

And for the most important part, create your admin account!::

  $ kegbot-admin.py createsuperuser

