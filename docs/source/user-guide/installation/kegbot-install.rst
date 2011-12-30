.. _kegbot-install:

Installing the Kegbot package
=============================

The two major software components of a Kegbot system are included in the Kegbot
package: the core program, which runs and monitors your hardware, and the web
frontend.  Both can be easily installed in a few minutes.

You can select from one of a few ways to install:

* :ref:`Automatically, using easy_install <install-easy>`, the recommended way to
  quickly get going with the latest release.
* :ref:`Using Git <install-git>`, to grab the latest, bleed-edge development
  code from version control.

If in doubt, proceed to the next section for the easiest method.

.. _install-easy:

Install automatically, with pip/easy_install (recommended)
----------------------------------------------------------

The latest Kegbot package is available in the Python Package Index. The package
name is `Kegbot <http://pypi.python.org/pypi/kegbot/>`_.  Follow these
steps to install Kegbot, and all of its Python dependencies, using the Python
package installer.

.. note::
  The instructions below use a tool called `pip <http://pip.openplans.org/>`_,
  which replaces a similar tool called `easy_install`.  If your system does not
  have pip, you can substitute easy_install, which supports the same commands.

#. If you don't already have it, install `pip <http://pip.openplans.org/>`_ on
   your system::

	% sudo apt-get install python-pip

#. Use pip to install the kegbot package::

	% sudo pip install kegbot

#. You should now have the Kegbot python modules installed, and a handful of
   command line tools which use them. Confirm everything was installed by
   attempting to use one of the tools::

	% kegbot-admin.py
	Type 'kegbot-admin.py help' for usage.

Easy, right? We hope so! You're now ready to skip to :ref:`configure-kegbot`.


.. _install-git:

Install with Git (developers)
-----------------------------

You can download the latest Kegbot code as source, using git.

#. If you don't already have the ``git`` program, start by installing it.  On Ubuntu, use the following::

	% sudo apt-get install git-core

#. Next, check out the kegbot sources using the ``git`` command::

	% git clone https://github.com/Kegbot/kegbot.git

#. You should now have a complete working copy of the kegbot tree in ``kegbot/``.

Continue on to :ref:`using-virtualenv`, which is the recommended way to install
and run kegbot without installing it system-wide.

.. _using-virtualenv:

Using virtualenv
----------------

The `virtualenv` tool is a handy and popular way to simulate a real source
install, but without affecting the rest of your system.  With the kegbot
development sources or a source release, this allows you to install and use
kegbot locally, as if it was installed on your system.

#. Install the `virtualenv` tool if you don't already have it::

	% sudo apt-get install python-virtualenv

#. Use `virtualenv` to create a home for a fake installation of kegbot
   (in `~/kb/`)::

	% virtualenv ~/kb/
	New python executable in /home/kegbot/kb/bin/python
	Installing setuptools.............done.

#. Step in to the virtual environment with the `activate` script::

	% source ~/kb/bin/activate
	% which python
	/home/kegbot/kb/bin/python

#. From within your source tree, use `setup.py` to "install" kegbot into the
   virtualenv home.  Two commands are shown: The `develop` command is similar to
   `install`, but installs in development mode -- the installation will simply
   point to the source tree, so you can change the kegbot code without
   reinstalling. Run one of the following::

	# Full install (copies all kegbot source files).
	% ./setup.py install --prefix=$HOME/kb
	[...]
	
	# Development install (links to kegbot source files).
	% ./setup.py develop --prefix=$HOME/kb
	[...]

#. Confirm that the tools are now installed::

	% which kegbot-admin.py
	/home/kegbot/kb/bin/kegbot-admin.py
	
	% kegbot-admin.py
	Type 'kegbot-admin.py help' for usage.

When using virtualenv, remember to step into the environment (by running
``source ~/kb/bin/activate``) before attempting to use any kegbot programs.
