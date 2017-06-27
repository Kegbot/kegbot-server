 .. _kegbot-install:

Install Guide
=============

Install Docker
--------------

Kegbot Server is supported through Docker. If you don't have Docker installed,
you must install it before continuing. Follow the guide here:
https://get.docker.sh/


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

  $ mkdir /home/your-username/kegbot-data

Run the server
--------------

Once you have the environment prepared, you're ready to run server. Use
the command below, but replace `/home/your-username/kegbot-data` with the
actual directory you created in the last step::

  $ docker run --rm -p 8000:8000 -v /home/your-username/kegbot-data:/kegbot-data kegbot:latest

Sit back and relax; this command will download and install the latest release
of Kegbot Server, then run it.
