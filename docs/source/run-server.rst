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

  (kb) $ kegbot-admin.py runserver
  Validating models...

  0 errors found
  Django version 1.4, using settings 'pykeg.settings'
  Development server is running at http://127.0.0.1:8000/
  Quit the server with CONTROL-C.

Now try it out!  Navigate to http://localhost:8000/ .

The first time you start Kegbot, you will be prompted to finish installation by
running the Setup Wizard.  Follow the on-screen prompts to create your admin
account and finish installation.

Kegbot Server is 100% functional when running under this development server, but
for better performance you'll want to run Kegbot with a "real" HTTP server.
When you're ready, see :ref:`production-setup` for instructions.

Configure Kegbot
----------------

The admin account you just created has access to an additional tab in the
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

Next steps
----------

Congratulations!  Your Kegbot Server should be basically functional: ready to
accept new user registrations and drink reports.  In the next chapters, we'll go
over tweaking your setup for a long-running production environment.
