"""
updatedb.py - tool for updating kegbot database
"""

import MySQLdb
import ConfigParser

config = ConfigParser.RawConfigParser()
config.read('keg.cfg')
dbhost = config.get('DB','host')
dbuser = config.get('DB','user')
dbdb   = config.get('DB','db')
dbpass = config.get('DB','password')
dbconn = MySQLdb.connect(host=dbhost, user=dbuser, passwd=dbpass, db=dbdb)

def GetInstalledSchema():
   """ determine current schema version. quite stupid for now """
   c = dbconn.cursor()
   q = """SELECT `value` from `config` where `key`='db.schema_version'"""
   c.execute(q)
   r = c.fetchone()
   return r[0]

def GetLatestSchema():
   """ determine what version of kegbot.sql we have """
   f = open('kegbot.sql')
   firstline = f.readline()
   f.close()
   if not firstline.startswith('-- KEGBOT_SCHEMA_VERSION'):
      return -1
   k, v = firstline.strip().split('=')
   v = int(v)
   return v

def BuildConfig():
   """ build mysql config table from a ConfigParser object """
   for section in config.sections():
      print section
      for option in config.options(section):
         k = '%s.%s' % (section, option)
         k = k.lower()
         v = config.get(section, option)
         k = MySQLdb.escape_string(k)
         v = MySQLdb.escape_string(v)
         if section != 'DB':
            c.execute("""INSERT INTO `config` (`key`,`value`) VALUES ('%s', '%s') """ % (k, v))

def Main():

   # print latest schema
   latest = int(GetLatestSchema())
   print 'Latest available schema:    %i' % latest

   # print current schema
   try:
      current = int(GetInstalledSchema())
   except:
      print '!!! ERROR: could not get currently installed schema'
      raise
   print 'Currently installed schema: %i' % current

   print ''

   if latest == current:
      print 'Nothing to do, great!'
   else:
      print 'Shoot, work to do..'


if __name__ == '__main__':
   Main()
