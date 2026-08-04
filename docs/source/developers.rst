.. _Developers:

Developers
==========

These instructions are just for folks interested in hacking on or extending
``kegbot-server``.

Local environment
-----------------

Most likely, you'll want to run kegbot locally (outside of Docker) while
developing. We use `uv <https://docs.astral.sh/uv/>`_ to manage the Python
environment. Create your development environment this way:

.. code-block:: console

  $ uv sync --all-groups

This will fetch and install all dependencies into a virtual Python
environment at ``.venv``.

A few settings are required even in development. A minimal configuration,
using sqlite and a local redis:

.. code-block:: console

  $ export KEGBOT_SECRET_KEY=changeme
  $ export DATABASE_URL=sqlite:///kegbot-dev.db
  $ export REDIS_URL=redis://localhost:6379/0

Run the server, or any other command, through ``uv run``:

.. code-block:: console

  $ uv run bin/kegbot version
  $ uv run bin/kegbot migrate

Running the dev servers
-----------------------

The web interface is a React single-page app in ``web-ui/``, built with
`bun <https://bun.sh/>`_ and vite. Install the frontend dependencies once:

.. code-block:: console

  $ bun install

For development, run two servers in separate terminals:

.. code-block:: console

  $ uv run bin/kegbot runserver   # django backend, on port 8001
  $ bun run dev                   # vite dev server, on port 8000

Then browse http://localhost:8000. The vite dev server serves the frontend
with hot reload and proxies ``/api``, ``/media``, and ``/static`` requests
to Django, so everything is same-origin and CSRF just works.

Other useful frontend commands:

.. code-block:: console

  $ bun run test                   # frontend tests
  $ bun run check                  # biome lint + tsc typecheck
  $ bun run build                  # production build (web-ui/dist)
  $ bun run generate-api           # regenerate the API client from the schema
  $ bun run generate-constants     # regenerate web-ui/lib/shared-constants.ts

Running tests
-------------

We use `pytest` to run tests. The test suite runs against sqlite and needs
no redis server:

.. code-block:: console

  $ uv run pytest

Code format and lint
--------------------

We use `ruff` to format and lint Python, and `biome` plus ``tsc`` for the
frontend:

.. code-block:: console

  $ uv run ruff format
  $ uv run ruff check
  $ bun run check

To run these checks automatically before each commit, install the
`pre-commit` hooks:

.. code-block:: console

  $ uv run pre-commit install

Building docs
-------------

We use `Sphinx` to build docs. You can create them this way:

.. code-block:: console

  $ uv run sphinx-build -b html docs/source docs/build/html
  $ open docs/build/html/index.html
