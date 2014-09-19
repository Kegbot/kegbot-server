 .. _kegbot-install:

Install Guide
=============

Install dependencies
--------------------

Before we begin, be sure Kegbot's major dependencies are available on your
your system.

On Ubuntu or Debian, use ``apt-get``::

  $ sudo apt-get install \
    python-dev \
    python-pip \
    libjpeg-dev \
    libmysqlclient-dev \
    redis-server \
    mysql-client \
    mysql-server \
    redis-server \
    supervisor \
    nginx


On Mac OS X, we recommend using `Homebrew <http://brew.sh>`_::

  $ brew install \
    python \
    mysql \
    libpng \
    jpeg \
    redis \
    nginx

Set up an environment
---------------------

The first thing you’ll need is the Python `virtualenv` package. You probably
already have this, but if not, you can install it with::

  $ sudo pip install virtualenv

Once that's done, chose a directory for the Kegbot Server environment and
create it with `virtualenv`. In our examples we'll use `/data/kb`::
  
  $ virtualenv /data/kb

Finally, activate your virtualenv::
  
  $ source /data/kb/bin/activate
  (kb) $

.. tip::
  You must activate your virtualenv before updating Kegbot, as well as before
  running any command-line Kegbot programs.


Install Kegbot Server
---------------------

Once you have the environment set up, you're ready to install Kegbot Server::
  
  (kb) $ pip install -U kegbot

Sit back and relax; this command will download and install the
`latest release <https://pypi.python.org/pypi/kegbot>`_, along with all of
its Python dependencies.


Create the database
-------------------

Create a new database to store your Kegbot data.  On MySQL, the command to
use is::
  
  $ mysqladmin -u root create kegbot

.. tip::
  If your MySQL server requires a password, add `-p` to these commands.

We also recommend creating a new MySQL user solely for Kegbot access.  Run the
following command, replacing "pw" with a password of your choice::
  
  $ mysql -u root -e '
    GRANT ALL PRIVILEGES ON kegbot.* TO kegbot@localhost
      IDENTIFIED BY "pw"; flush privileges;'


Run Redis
---------

If you installed Redis, it's probably already running.  Verify by pinging it:
  
  $ redis-cli ping
  PONG

.. warning::
  Kegbot uses Redis databases `0` and `1` by default.  If you are using the
  same Redis server for other programs, we recommend using separate databases.


Run the Setup Wizard
--------------------

The program ``setup-kegbot.py`` will help you:

* Configure Kegbot for the database you set up in the previous step;
* Create Kegbot's Media and Static Files directories;
* Install defaults into your new database.

Run the setup wizard::

  (kb) $ setup-kegbot.py

When finished, you should have a settings file in
``~/.kegbot/local_settings.py`` that you can examine.


About Media and Static Files
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

After running the wizard, two important settings should have been configured:
the *media* and *static files* directories.

**MEDIA_ROOT**
  This variable controls where Kegbot stores uploaded media: pictures added
  during account registration or pours, for example.

**STATIC_ROOT**
  This variable controls where Kegbot's static media is stored, such as built-in
  style sheets and images shown on the web page.

.. warning::
  **Never** place other content in ``STATIC_ROOT``, and always be sure it is set
  to a directory that Kegbot can completely overwrite.  For more information,
  see `Django's documentation for managing static files
  <https://docs.djangoproject.com/en/dev/howto/static-files/>`_.

.. _email-setup::

Configure E-Mail
----------------

Kegbot can send e-mail in several circumstances. These include:

* Initial account registration.
* Password recovery.
* Configurable notifications.

Before it can send e-mail, Kegbot must be configured with an e-mail
backend.  To use an SMTP server, add the following lines to your
``local_settings.py`` file and configure them as appropriate::
  
  # Tell Kegbot use the SMTP e-mail backend.
  EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'

  # SMTP server hostname (default: 'localhost') and port (default: 25).
  EMAIL_HOST = 'email.example.com'
  EMAIL_PORT = 25
  
  # Credentials for SMTP server.
  EMAIL_HOST_USER = 'username'
  EMAIL_HOST_PASSWORD = 'password'
  EMAIL_USE_SSL = False
  EMAIL_USE_TLS = False

  # "From" address for e-mails.
  EMAIL_FROM_ADDRESS = 'me@example.com'
