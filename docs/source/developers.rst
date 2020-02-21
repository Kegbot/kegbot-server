.. _Developers:

Developers
==========

These instructions are just for folks interested in hacking on or extending
``kegbot-server``.

Local environment
-----------------

Most likely, you'll want to run kegbot locally (outside of Docker) while
developing. We use `Pipenv` to manage the Python environment. Create
your development environment this way::

  $ pipenv install

This will fetch and install all dependencies, and create a virtual Python
environment.

Whenever you want to run code or tests, step into a development shell::

  $ pipenv shell
  (kegbot-server)
  $ ./bin/kegbot version
  1.3.0

Building docs
-------------

We use `Sphinx` to build docs. You can create them this way::

  $ pipenv shell
  (kegbot-server)
  $ cd docs
  $ make html
  $ open build/html/index.html

