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


### UPDATES TABLE

def GetInstalledSchema():
   """ determine current schema version. quite stupid for now """
   c = dbconn.cursor()
   q = """SELECT `value` from `config` where `id`='db.schema_version'"""
   c.execute(q)
   r = c.fetchone()
   return r[0]

# convention: SchemaUpdate__X contains all necessary operations (if any) to
# upgrade a DB schema from version X-1 to version X
UPGRADE_PASS = 0
UPGRADE_FAIL = 1

class SchemaUpdate__2:
   """ upgrade to schema 2 """
   def Upgrade(self):
      return UPGRADE_PASS

class SchemaUpdate__3:
   """ upgrade to schema 3 """
   def Upgrade(self):
      return UPGRADE_PASS

def doUpgrade(current, latest):
   for new_schema in range(current+1, latest+1):
      print '>>> Upgrading to schema %i' % new_schema

      ret = 0
      cls = 'SchemaUpdate__%i' % new_schema
      if not globals().has_key(cls):
         print '!!! No upgrade found, assuming OK'
         return

      updater = globals()[cls]()
      ret = updater.Upgrade()
      if ret != UPGRADE_PASS:
         print '!!! schema upgrade failed'
         sys.exit(1)
      print '<<< Upgrade to schema %i done' % new_schema
      print ''

def Main():

   # print current schema
   try:
      current = int(GetInstalledSchema())
   except:
      print '!!! ERROR: could not get currently installed schema'
      raise
   print 'Currently installed schema: %i' % current

   print ''

   latest = 4
   if current == latest:
      print 'Nothing to do, great!'
      sys.exit(0)
   else:
      doUpgrade(current, latest)
      print 'Upgrade complete'


if __name__ == '__main__':
   Main()
