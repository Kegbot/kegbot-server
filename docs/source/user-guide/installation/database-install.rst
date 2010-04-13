.. _database-install:

Installing the database
=======================

Kegbot relies on a database system to store all data, including keg and drink
information.  This chapter covers installing an initializing a database for use
by Kegbot.

At the moment, Kegbot can support either `MySQL <http://www.mysql.org/>`_ or
`Sqlite <http://sqlite.org/>`_ as the database backend.  We've not tested the
`other databases supported by Django
<http://docs.djangoproject.com/en/dev/ref/databases/>`_, though they might also
work.

Using SQLite
------------

Follow this section if you want to use SQLite as the Kegbot database.  SQLite is
considerably simpler than MySQL to setup and maintain.

Install SQLite
^^^^^^^^^^^^^^

Since SQLite operates on a flat file database, it is considerably simpler to set
up.  Be sure you have the necessary libraries and command-line tools::

  % sudo apt-get install python-sqlite

Configure Kegbot for SQLite
^^^^^^^^^^^^^^^^^^^^^^^^^^^

Before you can use SQLite, you need to decide where on disk it should store the
database file. In this example, we assume the database will be store at
``/home/kegbot/kegbot.sqlite``, though you can use another location.

Open the file ``~/.kegbot/common_settings.py`` in your favorite text editor.
Look for the section labeled "Database Configuration", and edit it to have the
following lines to the file::

  DATABASE_ENGINE = 'sqlite'
  DATABASE_NAME = '/home/kegbot/kegbot.sqlite'

Save the settings file; you may now proceed to :ref:`populate-databases`.

Using MySQL
----------

Follow this section if you prefer to use MySQL as the Kegbot database.

.. note::
  This section is not intended to be a complete guide to installing and
  maintaining a MySQL server. Generally, there's not much to it, but if you're
  not already familiar with MySQL (or if you encounter problems), we suggest you
  consult the official documentation for your Linux distro and/or MySQL.


Installing MySQL
^^^^^^^^^^^^^^^^

If you do not already have a MySQL daemon running on your system, you will need
to install it. The following should work on (Debian/Ubuntu)::

	% sudo apt-get install mysql-server

Once MySQL is installed, confirm it is running by logging in as the 'root' MySQL
user::

	% mysql -u root -p
	Enter password: 

When prompted for the password, enter the password of the ``root`` MySQL user.
If you don't know what this is, or don't remember setting a password, just hit
enter. Depending on your installation, a password may not be required.

You should then see the MySQL welcome message and shell::

	Welcome to the MySQL monitor.  Commands end with ; or \g.
	Your MySQL connection id is 211
	Server version: 5.0.75-0ubuntu10.2 (Ubuntu)

	Type 'help;' or '\h' for help. Type '\c' to clear the buffer.

	mysql> 

Your MySQL system seems to be working. Exit the shell::

	mysql> exit
	Bye
	%


Creating the Kegbot database
^^^^^^^^^^^^^^^^^^^^^^^^^^^^

You now need to create a database within MySQL for Kegbot to use.  We will
create a new database, named ``kegbot``, with the following command::

	% mysqladmin -u root -p create kegbot
	Enter password: 
	%

That's it; unless you see an error message, the command was successful. Next,
verify that the database was created by trying to use it in a MySQL shell::

	% mysql -u root -p
	Enter password: 
	Welcome to the MySQL monitor.  Commands end with ; or \g.
	Your MySQL connection id is 218
	Server version: 5.0.75-0ubuntu10.2 (Ubuntu)

	Type 'help;' or '\h' for help. Type '\c' to clear the buffer.

	mysql> use kegbot
	Reading table information for completion of table and column names
	You can turn off this feature to get a quicker startup with -A

	Database changed
	mysql>

Creating the `kegbot` MySQL user
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Finally, create a new MySQL user named ``kegbot`` for MySQL access by the Kegbot
system::

	mysql> GRANT ALL PRIVILEGES ON kegbot.* to kegbot@localhost IDENTIFIED BY 'pw';
	Query OK, 0 rows affected (0.12 sec)
	
	mysql> flush privileges;
	Query OK, 0 rows affected (0.08 sec)
	
	mysql> exit
	Bye

Be sure to select a unique password and replace the text ``'pw'``.
You will need this password in the next chapter.

Test your new user account::

	% mysql -u kegbot -p kegbot
	Enter password:    <---- use password just created
	Reading table information for completion of table and column names
	You can turn off this feature to get a quicker startup with -A

	Welcome to the MySQL monitor.  Commands end with ; or \g.
	Your MySQL connection id is 320
	Server version: 5.0.75-0ubuntu10.2 (Ubuntu)

	Type 'help;' or '\h' for help. Type '\c' to clear the buffer.

	mysql> exit
	Bye

Configure Kegbot for MySQL
^^^^^^^^^^^^^^^^^^^^^^^^^^

Finally, you need to point Kegbot at your new database.

Open the file ``~/.kegbot/common_settings.py`` in your favorite text editor.
Look for the section labeled "Database Configuration", and edit it to have the
following lines to the file::

  DATABASE_ENGINE = 'mysql'
  DATABASE_NAME = 'kegbot'
  DATABASE_USER = 'kegbot'
  DATABASE_PASSWORD = 'your-password'

Done! You have successfully set up a MySQL database for Kegbot.

.. _populate-databases:

Populate Databases
------------------

Now that the database is ready, you must install the various kegbot tables and
defaults.  You will also set the admin account name and password in this step::

  % cd $KEGBOT_HOME/pykeg
  % make setup
  --- Logging to: /home/kegbot/hg/kegbot/pykeg/setup.log
  --- Installing database ...
  --- Creating super user
  Username (Leave blank to use 'admin'): admin
  E-mail address: admin@example.com
  Password: 
  Password (again): 
  Superuser created successfully.
  %


