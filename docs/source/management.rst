.. _management:

Management
==========

Once your Kegbot Server is up and running, a number of settings and functions
can be configured and customized in the dashboard. This chapter describes
some things you can customize.

Sending e-mail
--------------

By default, your Kegbot Server is not configured to send email. You can
change this by providing email credentials.

Navigate to the *Admin* portion of the dashboard, and open *Advanced settings*.
The email configuration setting takes a URI string in a special format.

Generic SMTP server with TLS
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

To use an SMTP server with hostname ``example.com`` with a username and password,
over TLS, and with the default from email ``kegbot@example.com``::

    submission://username:password@example.com/?_default_from_email=kegbot@example.com

Be sure to replace ``kegbot@example.com`` with the "From:" address you'd like emails
to come from.

Gmail
~~~~~

To use a gmail account, you will first need to create an
`app-specific password <https://support.google.com/accounts/answer/185833?hl=en>`
for your gmail account. Then configure Kegbot as follows::

    submission://example@gmail.com:app-specific-password@smtp.gmail.com/?_default_from_email=example@gmail.com

Replace ``example@gmail.com`` with your gmail account name (two places), and
``app-specific-password`` with the app-specific password you generated.

Local SMTP server (advanced)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

To use the machine's local SMTP server or sendmail gateway (advanced users only)::

    smtp://?_default_from_email=kegbot@example.com

Be sure to replace ``kegbot@example.com`` with the "From:" address you'd like emails
to come from.

Disable emails
~~~~~~~~~~~~~~

To disable sending emails and simply log messages to console (default
configuration), use this setting::

    console:
