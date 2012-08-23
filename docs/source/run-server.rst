.. _running-webserver:

Run Kegbot Server
=================

By now you have Kegbot and it's database installed; it's now time to run the
server!

Run the built-in web server
---------------------------

Kegbot Server includes a simple built-in web server (part of Django).  This
is not a high performance web server, but works well during testing.

Launch the web server with the following command::

  $ kegbot-admin.py runserver
  Validating models...

  0 errors found
  Django version 1.4, using settings 'pykeg.settings'
  Development server is running at http://127.0.0.1:8000/
  Quit the server with CONTROL-C.

Now try it out!  Navigate to http://localhost:8000/ . You should see the
overview page for your new Kegbot.

Kegbot Server is 100% functional when running under this development server, but
for better performance you'll want to run Kegbot with a "real" HTTP server.
When you're ready, see :ref:`configure-apache` for instructions.

Log in and configure Kegbot
---------------------------

Once your server is up and running, log in with the super user account you
just created.  This account has access to an additional tab in the
navigation bar: "Admin".

Head over to "Taps".  Taps define what beer is currently available in the
system.  By default, two taps are created, but you can add more if you need
them.  If you're only using one tap, don't worry about the second one.

Before you can pour a drink, you should add a new Keg to the tap.

Allowing external access
------------------------

By default, the built-in web server only accepts connections from the local
machine.  To allow external computers to reach this server, specify the bind
address when running it::

  $ kegbot-admin.py runserver 0.0.0.0:8000
