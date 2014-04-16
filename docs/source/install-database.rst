.. _database-install:

Install the Database
====================

Kegbot relies on a database system to store all data, including keg and drink
information.  This chapter covers installing and initializing a database for use
by Kegbot.

At the moment, Kegbot can support either `MySQL <http://www.mysql.org/>`_ or
`Postgres <http://www.postgresql.org/>`_ as the database backend.  We do not support
the `other databases supported by Django
<http://docs.djangoproject.com/en/dev/ref/databases/>`_, though they might also
work.

Using MySQL
-----------

Follow this section to set up and use a MySQL server as the Kegbot database.

.. note::
  This section is not intended to be a complete guide to installing and
  maintaining a MySQL server. If you're not already familiar with MySQL (or if
  you encounter problems), we suggest you consult the official documentation for
  your Linux distribution and/or MySQL.


Installing MySQL
^^^^^^^^^^^^^^^^

If you do not already have a MySQL daemon running on your system, you need to
install it. The following command should work on Debian/Ubuntu::

	$ sudo apt-get install mysql-server

Once MySQL is installed, confirm it is running by logging in as the 'root' MySQL
user::

	% mysql -u root -p
	Enter password: 

When prompted for the password, enter the password of the ``root`` MySQL user.
Depending on your installation, a password may not be required.
If you don't know what this is, or don't remember setting a password, just hit,
or run the command without the ``-p`` option.

You should see the MySQL welcome message and shell::

	Welcome to the MySQL monitor.  Commands end with ; or \g.
	Your MySQL connection id is 211
	Server version: 5.0.75-0ubuntu10.2 (Ubuntu)

	Type 'help;' or '\h' for help. Type '\c' to clear the buffer.

	mysql> 

Your MySQL system seems to be working. Exit the shell::

	mysql> exit
	Bye
	$


Creating the Kegbot database
^^^^^^^^^^^^^^^^^^^^^^^^^^^^

You now need to create a database within MySQL for Kegbot to use.
Create a new database named ``kegbot`` with the following command::

	$ mysqladmin -u root -p create kegbot
	Enter password: 
	$

That's it; unless you see an error message, the command was successful. Next,
verify that the database was created by trying to use it in a MySQL shell::

	$ mysql -u root -p
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

.. _create-mysql-user:

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

	$ mysql -u kegbot -p kegbot
	Enter password:    <---- use password just created
	Reading table information for completion of table and column names
	You can turn off this feature to get a quicker startup with -A

	Welcome to the MySQL monitor.  Commands end with ; or \g.
	Your MySQL connection id is 320
	Server version: 5.0.75-0ubuntu10.2 (Ubuntu)

	Type 'help;' or '\h' for help. Type '\c' to clear the buffer.

	mysql> exit
	Bye

Done! You have successfully set up a MySQL database for Kegbot.

