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
import util

db_uri = 'mysql://%s:%s@%s/%s' % (dbuser, dbpass, dbhost, dbdb)
Backend.setup(db_uri)

LATEST_SCHEMA = Backend.SCHEMA_VERSION

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

class SchemaUpdate__8(Update):
   def Upgrade(self):
      self.log('adding channel column to kegs table')
      c = dbconn.cursor()
      c.execute("ALTER TABLE `kegs` ADD `channel` INT( 11 ) DEFAULT '0' NOT NULL AFTER `enddate`")
      SetCurrentSchema(8)
      return UPGRADE_PASS

class SchemaUpdate__9(Update):
   def Upgrade(self):
      SetCurrentSchema(9)
      return UPGRADE_PASS

class SchemaUpdate__10(Update):
   def Upgrade(self):
      self.log('changing config value col to TEXT type')
      c = dbconn.cursor()
      c.execute("ALTER TABLE `config` CHANGE `value` `value` TEXT NOT NULL");
      SetCurrentSchema(10)
      return UPGRADE_PASS

class SchemaUpdate__11(Update):
   def Upgrade(self):

      self.log('creating beertypes table')
      Backend.BeerType.createTable()
      self.log('creating brewers table')
      Backend.Brewer.createTable()
      Backend.Brewer(name='Unknown', comment='No brewer information')
      self.log('creating beerstyle table')
      Backend.BeerStyle.createTable()
      Backend.BeerStyle(name='Unknown')

      # migrate old rows
      self.log('starting keg migration')
      c = dbconn.cursor()
      q = 'select * from kegs order by id asc'
      res = c.execute(q)
      keg_type_map = {}
      for row in c:
         (id, fullvol, start, end, chan, status, beername, abv, descr, cost, beerpal, ratebeer, calories) = row
         calories = calories or 0.0
         abv = abv or 0.0
         print '-'*72
         print 'Migrating keg %s %s, %.1f%% ABV, %s calories/oz' % (id, beername, abv, calories)
         print ''
         types = list(Backend.BeerType.select())
         print 'Existing beer types:'
         print '\n'.join(['  [%i] %s (%s)' % (type.id, type.name, type.brewer.name) for type in types])
         print ''
         print 'Enter an id from above (if any), or "n" to create new'
         action = None
         while action not in ['n'] + [str(type.id) for type in types]:
            action = raw_input('beer type? ').strip()
         print ''
         if action == 'n':
            print 'OK, creating new beer type...'
            beername = util.prompt('beername', beername)
            calories_oz = util.prompt('calories/oz', '%.1f'%calories, float)
            carbs_oz = util.prompt('carbs/os', '0.0', float)
            abv = util.prompt('percent alcohol by volume', '%.1f'%abv, float)

            brewers = list(Backend.Brewer.select())
            print 'Existing brewers:'
            print '\n'.join(['  [%i] %s' % (brewer.id, brewer.name) for brewer in brewers])
            print ''
            print 'Enter an id from above (if any), or "n" to create new'
            brewer_id = None
            while brewer_id not in ['n'] + [str(b.id) for b in brewers]:
               brewer_id = raw_input('brewer? ').strip()
            print ''
            if brewer_id == 'n':
               brewname = util.prompt('brewer name','Generic Brewer')
               country = util.prompt('country', 'USA')
               state = util.prompt('state/province', 'California')
               city = util.prompt('city/other', 'Anytown')
               url = util.prompt('url','')
               dist = util.prompt('distribution (retail/homebrew)', 'retail')
               comment = util.prompt('comment','')

               brewer = Backend.Brewer(name=brewname, origin_country=country, origin_state=state, origin_city=city,
                     distribution=dist, url=url, comment=comment)
            else:
               brewer = Backend.Brewer.get(int(brewer_id))

            beer_type = Backend.BeerType(name=beername, brewer=brewer, calories_oz = float(calories_oz),
                  carbs_oz = float(carbs_oz), abv = float(abv))
         else:
            beer_type = Backend.BeerType.get(int(action))
         keg_type_map[id] = beer_type.id

      self.log('inserting type foreign key col')
      c.execute("ALTER TABLE  `kegs` ADD  `type_id` INT NOT NULL AFTER  `id`")

      self.log('dropping cols from old kegs table')
      c.execute("""ALTER TABLE `kegs`
                 DROP `beername`,
                 DROP `alccontent`,
                 DROP `beerpalid`,
                 DROP `ratebeerid`,
                 DROP `calories_oz`""");

      # update kegs table with user input
      self.log('updating old kegs with new type pointers')
      for k, v in keg_type_map.iteritems():
         k = Backend.Keg.get(k)
         k.type_id = v
         k.syncUpdate()

      self.log('adding thermo pref')
      try:
         Backend.Config(id='thermo.use_thermo', value='true')
      except:
         pass

      SetCurrentSchema(11)
      return UPGRADE_PASS


class SchemaUpdate__12(Update):
   def Upgrade(self):
      c = dbconn.cursor()
      self.log('scanning for previous admins')
      c.execute("select * from users")
      orig_admin_ids = []
      for row in c:
         if row[3] == 'yes':
            orig_admin_ids.append(row[0])
      self.log('dropping admin col from users db')
      c.execute('ALTER TABLE `users` DROP `admin`')
      self.log('adding UserLabel table')
      Backend.UserLabel.createTable()
      self.log('setting admin labels')
      for admin_id in orig_admin_ids:
         Backend.UserLabel(userID=admin_id, labelname='admin')

      self.log('creating guest user')
      guest_user = Backend.User(username='unknown')
      self.log('setting guest label')
      Backend.UserLabel(user=guest_user, labelname='guest')
      self.log('creating guest policy')
      guest_policy = Backend.Policy(type='free', description='__guest__')
      self.log('granting new policy to new guest user')
      Backend.Grant(user=guest_user, expiration='none', status='active', policy=guest_policy)
      SetCurrentSchema(12)
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
   print 'Latest available schema: %i' % LATEST_SCHEMA
   print ''

   if current == LATEST_SCHEMA:
      print 'Nothing to do, great!'
      sys.exit(0)
   else:
      doUpgrade(current, LATEST_SCHEMA)
      print 'Upgrade complete'


if __name__ == '__main__':
   Main()
