.. _install-pycore:

Install Pycore
==============

.. note::
  Pycore needs to talk to a Kegbot Server.  If you haven't already done so, you
  will need to set one up.  Please follow the instructions in
  :ref:`kegbot-install`, then continue here.

Set up virtualenv
-----------------

.. note::
  If you've already installed Kegbot Server in its own virtualenv, you don't
  need to create a new one just for Pycore; it's perfectly fine to reuse the
  existing virtualenv.

The ``virtualenv`` tool creates a directory where Pycore and all of its Python
dependencies will be stored.  It makes it easier to install and run Pycore
without needing root privileges, and reduces the chance of Pycore clashing with
your system's Python modules.

The first time you set up Pycore, you will need to create a new virtualenv
"home" for it.  Any filesystem location is fine.  To create it, give the
directory name as the only argument.  The example below creates the Pycore
virtualenv directory in your user's home directory::

  $ virtualenv ~/pycore
  New python executable in /Users/mike/pycore/bin/python
  Installing setuptools............done.
  Installing pip...............done.

Now that the virtualenv home has been created (at ``~/pycore/``), there's one
step to remember.  Each time you want to use the virtualenv home (either install
Kegbot to it, or run Kegbot from it), you need to activate it for the current
shell::

  $ source ~/pycore/bin/activate
  (pycore) $

Your shell prompt will be updated with ``(pycore)`` when the virtualenv is
active.  If you want to step out of the env for some reason, just call
``deactivate``::

  (pycore) $ deactivate
  $

If you ever want to completely uninstall Pycore, just delete the entire
``pycore/`` directory -- there's nothing precious in it, and you can always
recreate it by following these steps again.

.. tip::
  You can install multiple versions of Pycore simply by creating a new
  virtualenv for each one.


Install Pycore
--------------

There are two approaches to downloading and installing Kegbot:

* :ref:`From the latest release, using pip <install-pycore-release>`, the
  recommended way to quickly get going with the latest release.
* :ref:`From Git <install-pycore-git>`, to grab the latest, bleeding-edge
  development code.  Recommended for advanced users only.

If in doubt, proceed to the next section for the easiest method.  Be sure you
have activated your virtualenv first.


.. _install-pycore-release:

From Latest Release (Recommended)
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Use the ``pip`` tool to install the latest release of Pycore, including its
dependencies::

	(pycore) $ pip install kegbot-pycore

The command may take a few minutes as it downloads and installs everything.


.. _install-pycore-git:

From Git (developers)
^^^^^^^^^^^^^^^^^^^^^

If you want to run Pycore from the latest development version, follow this
section.

.. warning::
  Running from unreleased git sources is not recommended for production systems,
  since code can be very unstable and functionality may change suddenly.
  **Always** back up your valuable data.  As stated in Kegbot's license, we
  provide Kegbot with absolutely no warranty.

#. Check out the Pycore sources using ``git``::

	(pycore) $ git clone https://github.com/Kegbot/kegbot-pycore.git

#. Step in to the new tree and run the setup command::

	(pycore) $ cd kegbot-pycore
	(pycore) $ ./setup.py develop

The command may take a few minutes as it downloads and installs everything.
