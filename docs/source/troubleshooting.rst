.. _troubleshooting-server:

Troubleshooting Kegbot Server
=============================

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

