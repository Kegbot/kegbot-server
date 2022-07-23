.. _Developers:

Developers
==========

These instructions are just for folks interested in hacking on or extending
``kegbot-server``.

Local environment
-----------------

Most likely, you'll want to run kegbot locally (outside of Docker) while
developing. We use `Poetry` to manage the Python environment. Create
your development environment this way:

.. code-block:: console

  $ poetry install

This will fetch and install all dependencies, and create a virtual Python
environment.

Whenever you want to run code or tests, step into a development shell:

.. code-block:: console

  $ poetry shell
  (kegbot-server) $ ./bin/kegbot version
  1.3.0

Running tests
-------------

We use `pytest` to run tests. Run all tests this way:

.. code-block:: console

  (kegbot-server) $ pytest


Code format
-----------

We use `black` to format all code. Run it this way:

.. code-block:: console

  $ poetry shell
  (kegbot-server) $ black pykeg/


Building docs
-------------

We use `Sphinx` to build docs. You can create them this way:

.. code-block:: console

  $ poetry shell
  (kegbot-server) $ cd docs
  (kegbot-server) $ make html
  (kegbot-server) $ open build/html/index.html

