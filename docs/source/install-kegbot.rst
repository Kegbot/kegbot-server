.. _kegbot-install:

Install the Kegbot Server Package
=================================

In the previous section, you installed a database program that Kegbot will use
for data storage.  It is now time to install the Kegbot Server program.

Install dependencies
--------------------

On Ubuntu or Debian, use ``apt-get`` to install Kegbot's major dependencies::

  $ sudo apt-get install \
    build-essential \
    git-core \
    libjpeg-dev \
    libmysqlclient-dev \
    libsqlite3-0 \
    libsqlite3-dev \
    memcached \
    mysql-client \
    mysql-server \
    python-dev \
    python-imaging \
    python-mysqldb \
    python-pip \
    python-virtualenv \
    virtualenvwrapper


On Mac OS X, we recommend using MacPorts to install the tools::

  $ sudo port install python27 py27-virtualenv py27-pil py27-pip

.. _run-virtualenv:

Create a virtualenv
-------------------

The ``virtualenv`` tool creates a directory where Kegbot Server and all of its
Python dependencies will be stored.  It makes it easier to install and run
Kegbot Server without root privileges, and reduces the chance of Kegbot clashing
with your system's Python modules.

The first time you set up Kegbot, you will need to create a new virtualenv
"home" for Kegbot Server.  Any filesystem location is fine.  To create it, give
the directory name as the only argument.  The example below creates the Kegbot
virtualenv directory in your user's home directory::

  $ virtualenv ~/kb
  New python executable in /Users/mike/kb/bin/python
  Installing setuptools............done.
  Installing pip...............done.

Now that the virtualenv home has been created (at ``~/kb/``), there's one step 
to remember.  Each time you want to use the virtualenv home (either install 
Kegbot to it, or run Kegbot from it), you need to activate it for the current shell::

  $ source ~/kb/bin/activate
  (kb) $

Your shell prompt will be updated with ``(kb)`` when the virtualenv is active.
If you want to step out of the env for some reason, just call ``deactivate``::

  (kb) $ deactivate
  $

If you ever want to completely uninstall Kegbot Server, just delete the entire
``kb/`` directory -- there's nothing precious in it, and you can always recreate it
by following these steps again.

.. tip::
  You can install multiple versions of Kegbot simply by creating a new
  virtualenv for each one.

Install Kegbot Server
---------------------

There are two approaches to downloading and installing Kegbot:

* :ref:`From the latest release, using pip <install-release>`, the recommended
  way to quickly get going with the latest release.
* :ref:`From Git <install-git>`, to grab the latest, bleeding-edge development
  code.  Recommended for advanced users only.

If in doubt, proceed to the next section for the easiest method.  Be sure you
have activated your virtualenv first.


.. _install-release:

From Latest Release (Recommended)
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Use the ``pip`` tool to install the latest release of Kegbot Server, including
its dependencies::

	(kb) $ pip install kegbot

The command may take a few minutes as it downloads and installs everything.
When it finishes, confirm Kegbot was installed by trying the admin tool::

	(kb) $ kegbot-admin.py
	Type 'kegbot-admin.py help' for usage.


.. _install-git:

From Git (developers)
^^^^^^^^^^^^^^^^^^^^^

If you want to run Kegbot Server from the latest development version, follow
this section.

.. warning::
  Running from unreleased git sources is not recommended for production systems,
  since code can be very unstable and functionality may change suddenly.
  **Always** back up your valuable data.  As stated in Kegbot's license, we
  provide Kegbot with absolutely no warranty.

#. Check out the kegbot sources using ``git``::

	(kb) $ git clone https://github.com/Kegbot/kegbot.git

#. Step in to the new tree and run the setup command::

	(kb) $ cd kegbot/
	(kb) $ ./setup.py develop

The command may take a few minutes as it downloads and installs everything.
When it finishes, confirm Kegbot was installed by trying the admin tool::

	(kb) $ kegbot-admin.py
	Type 'kegbot-admin.py help' for usage.

