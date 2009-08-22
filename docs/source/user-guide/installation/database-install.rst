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

Installing SQLite
-----------------
