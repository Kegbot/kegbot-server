 .. _digitalocean-install:

HOWTO: Install Kegbot Server on Digital Ocean
=============================================

**Set up Kegbot on a cloud server in under 15 minutes.**  This guide will walk
you through deploying Kegbot Server on `Digital Ocean <https://www.digitalocean.com/?refcode=de16cdb7ddb2>`_,
although the steps may work on other cloud providers.


Step 1: Create a new Digital Ocean droplet
------------------------------------------

`Sign Up for Digital Ocean <https://www.digitalocean.com/?refcode=de16cdb7ddb2>`_, add
your billing information, then create a new droplet (virtual server).

* Under *Droplet Hostname*, enter a name like `my-kegbot`.
* Under *Size*, you may select the smallest size droplet; larger servers will
  perform better.
* Under *Select Image*, select **Ubuntu 14.04 x64**.

Press **Create Droplet**. You will receive a mail from Digital Ocean with the
root password to your droplet.


Step 2: Connect to your droplet
-------------------------------

Connect to your droplet using the `ssh` command-line tool (Mac, Linux) or
using `Putty <http://www.chiark.greenend.org.uk/~sgtatham/putty/download.html>`_
on Windows::

  ssh root@192.168.1.2

Replace ``192.168.1.2`` with the IP address of your Droplet.

You will be asked for permission to connect, type ``yes``, then enter the root
password from the email Digital Ocean sent you when the Droplet was set up.


Step 3: Install Kegbot Server using the Kegberry script
-------------------------------------------------------

Paste and run the following commands exactly as shown below::
  
  root@my-kegbot:~# export INSTALLFLAGS="--nopycore --allow_root"
  root@my-kegbot:~# bash -c "$(curl -fsSL https://raw.github.com/Kegbot/kegberry/master/install.sh)"

While running, the script will:

* Install all Ubuntu system dependencies (nginx, redis, and so on).
* Create a new user named ``kegbot`` and home directory ``/home/kegbot``.
* Create and install the Kegbot MySQL database named ``kegbot``.
* Install the Kegbot daemons and start the server.


Step 4: Complete the setup wizard
---------------------------------

Navigate to the IP address of your system: ``http://your-ip/``.  You should be
greeted by the Kegbot Setup wizard.  Complete the install and you're ready to go!


Next steps
----------

The ``kegbot`` user
~~~~~~~~~~~~~~~~~~~

*Important:* The server is installed under the ``kegbot`` user, so to update
or modify the Kegbot install, you need to become the ``kegbot`` user first
using ``sudo``::

  root@my-kegbot:~# su - kegbot
  kegbot@my-kegbot:~$

To run kegbot commands such as ``kegbot upgrade``, you also need to activate the
virtualenv before running any command::
  
  root@my-kegbot:~# su - kegbot
  kegbot@my-kegbot:~$ . kegbot-server.venv/bin/activate
  (kegbot-server.venv)kegbot@my-kegbot:~$ kegbot version
  kegbot-server 1.1.0

Disable ``DEBUG`` mode
~~~~~~~~~~~~~~~~~~~~~~

Once you've finished setting up the system, it's a good idea to disable ``DEBUG``
mode.  Open the ``local_settings.py`` file in an editor::

  root@my-kegbot:~# su - kegbot
  kegbot@my-kegbot:~$ nano ~/.kegbot/local_settings.py

Find ``DEBUG = True`` and replace with ``DEBUG = False``, save and close the file.


Configure e-mail
~~~~~~~~~~~~~~~~

Unlike most Kegbot options, e-mail configuration cannot be done in the
browser.  See :ref:`email-setup` for instructions.

