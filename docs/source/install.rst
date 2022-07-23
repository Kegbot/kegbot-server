.. _install-local:

Install
=======

Prerequisites
-------------

Kegbot Server is installed and supported through `Docker <https://docs.docker.com/get-docker/>`_
and `docker-compose <https://docs.docker.com/compose/>`_, which are available for Mac,
Windows, and Linux.

Ensure you have both of these installed before continuing.

Create the data directory
-------------------------

Kegbot needs a place to store certain data, like image uploads. Create a place
on your filesystem and remember the path; we'll need this in the next step:

.. code-block:: console
    
    $ mkdir /home/user/kegbot-data


Create the config file
----------------------

Kegbot and its essential services will be configured and launched using the
``docker-compose`` tool and a corresponding config file, ``docker-compose.yml``.

Create a new filed called ``docker-compose.yml`` starting with the following contents:

.. include:: ../../docker-compose.yml
   :literal:

.. note::
    **What it's doing:** This configuration file launches Kegbot Server, a MySQL database,
    and Redis.

You don't need to edit anything in this file yet, with one exception: Be sure to update the path
to the ``kegbot-data`` directory. Using the example path from the
previous step, you would change this line::

    volumes:
    - kegbot-data:/kegbot-data

To this::
    
    volumes:
    - /home/user/kegbot-data:/kegbot-data

Start the services
------------------

Now, ask ``docker-compose`` to launch these services. We will launch them in the
foreground::

    $ docker-compose up

This may take a while, as the Docker system works to download the images it needs.
Eventually, you should start seeing a series of output like the following::
    
    Attaching to kegbot-server-kegbot-1, kegbot-server-mysql-1, kegbot-server-redis-1, kegbot-server-workers-1
    kegbot-server-mysql-1    | 2022-07-23 17:20:14+00:00 [Note] [Entrypoint]: Entrypoint script for MySQL Server 8.0.29-1.el8 started.
    kegbot-server-redis-1    | 1:C 23 Jul 2022 17:20:14.333 # oO0OoO0OoO0Oo Redis is starting oO0OoO0OoO0Oo
    kegbot-server-redis-1    | 1:C 23 Jul 2022 17:20:14.334 # Redis version=7.0.4, bits=64, commit=00000000, modified=0, pid=1, just started
    kegbot-server-mysql-1    | 2022-07-23 17:20:14+00:00 [Note] [Entrypoint]: Switching to dedicated user 'mysql'
    kegbot-server-mysql-1    | 2022-07-23 17:20:14+00:00 [Note] [Entrypoint]: Entrypoint script for MySQL Server 8.0.29-1.el8 started.
    kegbot-server-mysql-1    | 2022-07-23 17:20:14+00:00 [Note] [Entrypoint]: Initializing database files
    kegbot-server-mysql-1    | 2022-07-23T17:20:14.439962Z 0 [System] [MY-013169] [Server] /usr/sbin/mysqld (mysqld 8.0.29) initializing of server in progress as process 41
    kegbot-server-mysql-1    | 2022-07-23T17:20:14.445084Z 1 [System] [MY-013576] [InnoDB] InnoDB initialization has started.
    kegbot-server-kegbot-1   | ██╗  ██╗███████╗ ██████╗ ██████╗  ██████╗ ████████╗
    kegbot-server-kegbot-1   | ██║ ██╔╝██╔════╝██╔════╝ ██╔══██╗██╔═══██╗╚══██╔══╝
    kegbot-server-kegbot-1   | █████╔╝ █████╗  ██║  ███╗██████╔╝██║   ██║   ██║
    kegbot-server-kegbot-1   | ██╔═██╗ ██╔══╝  ██║   ██║██╔══██╗██║   ██║   ██║
    kegbot-server-kegbot-1   | ██║  ██╗███████╗╚██████╔╝██████╔╝╚██████╔╝   ██║
    kegbot-server-kegbot-1   | ╚═╝  ╚═╝╚══════╝ ╚═════╝ ╚═════╝  ╚═════╝    ╚═╝

Congratulations! Your Kegbot Server, along with its MySQL database and Redis cache, have
been launched.

Run the setup wizard
--------------------

Now that the server is running, visit the Kegbot Server web page.
It should be running at: http://localhost:8000/

Once loaded, you should should see a series of steps to walk through.
Walk through each step until you have completed setup.

Restart in production mode
--------------------------

Once you have completed setup, you should restart the system so it runs
in the background.

Before we do that, let's enable *production mode*. First, press ``CTRL-C``
to shut down the running services. Next, in your config file,
change this line::

    KEGBOT_ENV: "debug"

To this::

    KEGBOT_ENV: "production"

This will cause the Kegbot server to launch with various setup and debug
features disabled, for security and performance purposes.

Finally, restart the services with the ``-d`` (detach) flag to launch
them in the background:

.. code-block:: console
    
    $ docker-compose up -d

This time, you should see only a few brief lines of output:

.. code-block:: console
    
    [+] Running 4/4
    ⠿ Container kegbot-server-kegbot-1   Started             0.6s
    ⠿ Container kegbot-server-mysql-1    Started             0.6s
    ⠿ Container kegbot-server-redis-1    Started             0.6s
    ⠿ Container kegbot-server-workers-1  Started             0.6s

You can verify everything is running with the ``docker-compose ps`` command:

.. code-block:: console
        
    $ docker-compose ps
    NAME                      COMMAND                  SERVICE     STATUS      PORTS
    kegbot-server-kegbot-1    "gunicorn pykeg.web.…"   kegbot      running     0.0.0.0:8000->8000/tcp
    kegbot-server-mysql-1     "docker-entrypoint.s…"   mysql       running     3306/tcp, 33060/tcp
    kegbot-server-redis-1     "docker-entrypoint.s…"   redis       running     6379/tcp
    kegbot-server-workers-1   "bin/kegbot run_work…"   workers     running     8000/tcp
