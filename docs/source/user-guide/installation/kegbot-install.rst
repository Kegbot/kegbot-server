.. _kegbot-install:

Installing the Kegbot package
=============================

The Kegbot package includes the two main systems used in running a Kegbot:

* **Pykeg**, the core of the kegbot system.  Pykeg monitors the kegerator
  hardware, and saves drinks into the database.
* **Kegweb**, the web frontend to your kegbot.  Kegweb reads drinks from the
  database and displays them in HTML format.

Owing to the active nature of kegbot development, there are a few limitations
that you should be aware of:

* *No binary/prebuilt packages.*  We currently only support installing kegbot from
  source.
* *Install requires Mercurial.*  You need to download the source from version
  control; we don't currently have "tarball" releases available.
* *Local install only.*  You will be installing kegbot for a single user only, not
  for the whole system.

As Kegbot gets closer to a 1.0 release, we'll work towards removing these
limitations.


Download source from Mercurial (hg)
-----------------------------------

You can download the latest Kegbot code as source, using the `Mercurial
<http://mercurial.selenic.com/>`_ version control tool.  (If you're familiar
with Subversion, Mercurial is pretty similar.)

#. If you don't already have the ``hg`` program, start by installing it.  On Ubuntu, use the following::

	% sudo apt-get install mercurial

#. We recommend you create a directory to store your kegbot code.  The example
   below creates a ``kegbot`` directory in your homedir; we'll refer
   to this directory in later instructions as ``KEGBOT_HOME``::

	% export KEGBOT_HOME=$HOME/kegbot
	% mkdir $KEGBOT_HOME

#. Next, check out the kegbot sources into ``KEGBOT_HOME`` using the ``hg``
   command::

	% cd $KEGBOT_HOME
	% hg clone https://kegbot.googlecode.com/hg/ kegbot-hg

#. You should now have a complete working copy of the kegbot tree::

	% ls kegbot-hg
	controller/  docs/  kegweb/  pykeg/


Configure Pykeg
---------------

Pykeg needs a little bit of static configuration before it works.  At the
moment, Pykeg uses a `Django Settings file
<http://docs.djangoproject.com/en/dev/topics/settings/>`_ for all of its
configuration.  Mostly, you just need to tell Pykeg what kind of database to
use.

#. Create a new directory in your homedir to store kegbot settings::

	% mkdir ~/.kegbot

#. Copy the example settings file (from the ``pykeg/`` directory) into your new
   local directory::

	% cp common_settings.py.example ~/.kegbot/common_settings.py

#. Edit ``common_settings.py`` as appropriate for your installation.

Look at the comments in this file for an idea of what settings you will need to
change.  At minimum, you should set the ``DATABASE_`` variables.


Configure Kegweb
----------------


Run Tests
---------
