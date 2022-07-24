.. _commands:

Commands
========

This section describes commonly-used commands that are available from the
``kegbot`` command-line tool.

Running commands
----------------

When using ``docker-compose``, you can run the ``kegbot`` command line using
the following general invocation:

.. code-block:: console

    $ docker-compose run kegbot <command-name> [.. additional args ..]

For an example, see the :ref:`upgrading` section.

Available commands
------------------

Maintenance commands
~~~~~~~~~~~~~~~~~~~~

These are commands you might need to call in the course of maintaining your
Kegbot Server.

.. data:: upgrade

  Executes the upgrade process. Should only be called while the web process is
  stopped. See :ref:`upgrading`.

.. data:: regen_stats

  Regenerates all statistics.

.. data:: change_password <username>

  Change the password of the given user.


Internal commands
~~~~~~~~~~~~~~~~~

These commands are what makes the Kegbot Server run. When using ``docker-compose``,
you should not need to call these commands directly, as they're invoked by that
configuration when needed.

.. data:: run_server

  Runs the internal web server process.

.. data:: run_workers

    Runs the worker process. This needs to be running for any background tasks,
    such as See also ``run_all``.

.. data:: run_all

    Runs both the web service process (``run_server``) and the worker process
    (``run_workers``).

