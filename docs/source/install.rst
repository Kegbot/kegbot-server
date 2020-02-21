.. _install-local:

Install
=======

Kegbot Server is supported through Docker. If you don't have Docker installed,
you must install it before continuing. Follow the
`Docker installation guide <https://get.docker.sh/>`_ for your OS, then
return to these instructions.

Create the database
-------------------

If you're just installing Kegbot Server for the first time, you'll need to
create a database for it to use. On MySQL, the command to run is::

 $ mysqladmin -u root create kegbot

.. tip::
 If your MySQL server requires a password, add `-p` to these commands.

Create the data directory
-------------------------

Kegbot also needs a place to store certain other data, like media uploads.
Create a place on your filesystem and remember the path; we'll need this
in the next step::

 $ mkdir /home/user/kegbot-data

Create the config file
----------------------

Most Kegbot settings can be configured after Kegbot is running. However,
some settings are stored in the `kegbot.cfg` file. Create this file in
the kegbot directory, with the following contents::

 [config]

 KEGBOT_SETUP_ENABLED = True
 KEGBOT_DEBUG = True
 KEGBOT_SECRET_KEY = some-random-value

In the example above, replace ``some-random-value`` with a random / unguessable
value. See :ref:`settings` for a full description of available settings.

Run the server
--------------

Once you have the environment prepared, you're ready to run server. Use
the command below, but replace `/home/your-username/kegbot-data` with the
actual directory you created in the last step::

 $ docker run --rm -p 8000:8000 -v /home/your-username/kegbot-data:/kegbot-data kegbot:latest

Sit back and relax; this command will download and install the latest release
of Kegbot Server, then run it.
