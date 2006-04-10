"""
updatedb.py - tool for updating kegbot database
"""

import sys

import MySQLdb
import ConfigParser

config = ConfigParser.RawConfigParser()
config.read('keg.cfg')
dbhost = config.get('DB','host')
dbuser = config.get('DB','user')
dbdb   = config.get('DB','db')
dbpass = config.get('DB','password')
dbconn = MySQLdb.connect(host=dbhost, user=dbuser, passwd=dbpass, db=dbdb)

sys.path.append('.')
import Backend

db_uri = 'mysql://%s:%s@%s/%s' % (dbuser, dbpass, dbhost, dbdb)
Backend.setup(db_uri)

LATEST_SCHEMA = 7

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

def SetCurrentSchema(num):
   v = Backend.Config.get('db.schema_version')
   v.value = num
   v.syncUpdate()

class Update:
   def log(self, msg):
      print '--- %s' % msg

### BEGIN SCHEMA UPDATES

class SchemaUpdate__5(Update):
   def Upgrade(self):
      self.log('creating thermolog table')
      Backend.ThermoLog.createTable()
      SetCurrentSchema(5)
      return UPGRADE_PASS

class SchemaUpdate__6(Update):
   def Upgrade(self):
      self.log('creating relaylog table')
      Backend.RelayLog.createTable()
      SetCurrentSchema(6)
      return UPGRADE_PASS

class SchemaUpdate__7(Update):
   def Upgrade(self):
      self.log('updating log format')
      v = Backend.Config.get('logging.logformat')
      oldfmt = '%(asctime)s %(levelname)s %(message)s'
      newfmt = '%(asctime)s %(levelname)-8s (%(name)s) %(message)s'
      if v.value == oldfmt:
         v.value = newfmt
         v.syncUpdate()
      SetCurrentSchema(7)
      return UPGRADE_PASS

### END SCHEMA UPDATES

def doUpgrade(current, latest):
   for new_schema in range(current+1, latest+1):
      print '>>> Upgrading to schema %i' % new_schema

      ret = 0
      cls = 'SchemaUpdate__%i' % new_schema
      if not globals().has_key(cls):
         print '<<< No upgrade found, assuming OK'
         print ''
         continue

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
   print 'Latest available schemta: %i' % LATEST_SCHEMA
   print ''

   if current == LATEST_SCHEMA:
      print 'Nothing to do, great!'
      sys.exit(0)
   else:
      doUpgrade(current, LATEST_SCHEMA)
      print 'Upgrade complete'


if __name__ == '__main__':
   Main()
