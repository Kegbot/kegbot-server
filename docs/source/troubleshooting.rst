.. _troubleshooting-server:

Troubleshooting Kegbot Server
=============================

Images and/or javascript not served when ``DEBUG = False``
----------------------------------------------------------

The built-in web servers (``kegbot runserver`` and ``kegbot run_gunicorn``)
do not serve static files -- any URLs beginning with ``/media`` and
``/static`` -- when ``DEBUG = False``.

This behavior is intentional: serving static files this way
is "grossly inefficient" and "probably insecure" according to the
`Django developers <https://docs.djangoproject.com/en/1.6/howto/static-files/#configuring-static-files>`_.
As a result, Kegbot will only do it when ``DEBUG = True``.

To fix, follow the :ref:`production setup guide <production-setup>`,
which configures these files to be served directly by the fronting
web server Nginx. Alternatively, accept the consequences of running
a non-production config and set ``DEBUG = True``.


Date errors while viewing sessions
----------------------------------

An error like this indicates a problem with MySQL::
  
  ValueError: Database returned an invalid value in QuerySet.dates(). Are time
  zone definitions and pytz installed?

This issue arsies when MySQL does not have complete time zone information,
and is discussed in
`Django ticket 21629 <https://code.djangoproject.com/ticket/21629>`_ and in
the `MySQL documentation <http://dev.mysql.com/doc/refman/5.5/en/mysql-tzinfo-to-sql.html>`_.

For most systems, the following command will fix the issue::
  
  $ mysql_tzinfo_to_sql /usr/share/zoneinfo | mysql -u root -p mysql


