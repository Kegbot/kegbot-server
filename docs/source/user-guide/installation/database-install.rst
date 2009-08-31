.. _database-install:

Installing the Kegbot database
==============================

Kegbot relies on the presence of a database system to store lots of data,
including keg and drink information.  Kegbot currently supports `all databases
supported by Django <http://docs.djangoproject.com/en/dev/ref/databases/>`_,
though we've only tested `MySQL
<http://docs.djangoproject.com/en/dev/ref/databases/>`_ and `SQLite
<http://www.sqlite.org/>`_.

This chapter covers selecting and installing a database for use by Kegbot.

Selecting a database system
---------------------------

We've found a basic Kegbot system can work fine with either MySQL or SQLite.

There are major, intentional differences between these two systems: MySQL is a
complete relational database server, while SQLite is a simple (but powerful)
embeddable SQL engine.

We think SQLite kicks ass, and is great for certain situations, but we recommend
MySQL as the default for new Kegbot systems.  Although it may take slightly more
work to set up, there is plenty of good documentation out there.

That said, there are no problems that we're aware of with SQLite.  Because it is
an embedded database engine, it will not be able to scale to high levels of
concurrency; you probably shouldn't launch a popular kegbot website using only
SQLite.  It is perfectly fine for tinkering with Kegbot, though.

Installing MySQL
----------------

First, you will need to install the MySQL software. The following should work on
(Debian/Ubuntu)::

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

Done! You have successfully set up a MySQL database for Kegbot.  In the next
chapter, you will install and configure Kegbot to use this database and populate
it with tables.


Installing SQLite
-----------------

Since SQLite operates on a flat file database, it is considerably simpler to set
up.  Be sure you have the necessary libraries and command-line tools::

	% sudo apt-get install python-sqlite

That's it.
