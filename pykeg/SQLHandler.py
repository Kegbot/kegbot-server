import logging
import MySQLdb
import time

class SQLHandler(logging.Handler):
   """
   A logging handler for use with a MySQLdb backend.
   """
   def __init__(self, dbhost, dbuser, dbdb, dbtable, dbpassword):
      logging.Handler.__init__(self)
      self.dbconn = MySQLdb.connect(host=dbhost, user=dbuser, passwd=dbpassword, db=dbdb)
      self.table = dbtable

   def emit(self, record):
      """
      emit a record to an sql backend

      formats the record in to an sql query, and trys to append it to
      whatever table is selected. the columns of the table shall be:
      """
      # a SQL formatter should return a list of key->value pairs for the
      # insert DB
      db_keys = self.format(record)

      # add the current log time; disabled (add a timestamp column if
      # you want it)
      #db_keys["logtime"] = time.time()

      # build the query
      query_fields,query_values = [],[]
      for key in db_keys.keys():
         val = db_keys[key]
         if val: # if this entry is even useful..
            if key in ("name","pathname","msg","exc_info"):
               val = MySQLdb.escape_string(val)
            query_fields.append("`" + key + "`")
            query_values.append("'" + str(val) + "'")

      # now join the stuff together
      query = "INSERT INTO " + self.table + " "
      query = query + '(' + ', '.join(query_fields) + ') '
      query += "VALUES (" + ', '.join(query_values) + ") "

      c = self.dbconn.cursor()
      c.execute(query)

class SQLVerboseFormatter(logging.Formatter):
   """
   A formatter to log all of a LogRecord to an SQL backend.

   This formatter should be used with the SQLHandler for the logging
   package. The following is the suggested table layout for a target of
   the SQLHandler that uses this formatter:

   +----------+---------------------+------+-----+---------+----------------+
   | Field    | Type                | Null | Key | Default | Extra          |
   +----------+---------------------+------+-----+---------+----------------+
   | id       | bigint(20) unsigned |      | PRI | NULL    | auto_increment |
   | logtime  | timestamp(14)       | YES  |     | NULL    |                |
   | name     | text                |      |     |         |                |
   | lvl      | tinyint(2)          |      |     | 0       |                |
   | pathname | text                |      |     |         |                |
   | lineno   | int(10) unsigned    |      |     | 0       |                |
   | msg      | text                |      |     |         |                |
   | exc_info | text                |      |     |         |                |
   +----------+---------------------+------+-----+---------+----------------+

   The second field, logtime, is optional. If present, MySQL will
   automatically log the time of the record insert, to the nearest
   second.
   """
   def format(self,record):
      """
      Format a LogRecord for handling by an SQLHandler.

      Though most formatters return a string, the SQLHandler expects a
      dictionary whose keys correspond to SQL column names. Using the
      keys of the returned dictionary, the SQLHandler will construct an
      SQL INSERT query with the keys and values specified.
      """
      rec = {  "name": record.name,
               "lvl": record.levelno,
               "pathname": record.pathname,
               "lineno": record.lineno,
               "msg": record.getMessage(),
               "exc_info": record.exc_info }
      return rec

class SQLMinimalFormatter(logging.Formatter):
   """
   A formatter to log only the message and error level to an SQLHandler.

   This formatter operates in the same fashion as SQLVerboseFormatter,
   but only logs the numerical error level and LogRecord message. The
   suggested SQL structure is therefore a subset of that suggest for
   SQLVerboseFormatter:

   +----------+---------------------+------+-----+---------+----------------+
   | Field    | Type                | Null | Key | Default | Extra          |
   +----------+---------------------+------+-----+---------+----------------+
   | id       | bigint(20) unsigned |      | PRI | NULL    | auto_increment |
   | logtime  | timestamp(14)       | YES  |     | NULL    |                |
   | lvl      | tinyint(2)          |      |     | 0       |                |
   | msg      | text                |      |     |         |                |
   +----------+---------------------+------+-----+---------+----------------+

   The logtime field is optional, and (as with SQLVerboseFormatter) will
   be populated by MySQL if present.
   """
   def format(self, record):
      """
      Format a LogRecord for handling by an SQLHandler.

      Though most formatters return a string, the SQLHandler expects a
      dictionary whose keys correspond to SQL column names. Using the
      keys of the returned dictionary, the SQLHandler will construct an
      SQL INSERT query with the keys and values specified.
      """
      rec = {  "lvl": record.levelno,
               "msg": record.getMessage() }
      return rec

