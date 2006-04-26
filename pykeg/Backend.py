from datetime import datetime
import time
import sys

try:
   from sqlobject import *
except ImportError:
   print>>sys.stderr, '!!! Could not import sqlobject - do you have it installed?'
   print>>sys.stderr, '!!! Kegbot requires sqlobject version 0.7 or later. Exiting.'
try:
   import MySQLdb
except ImportError:
   print>>sys.stderr, '!!! Could not import MySQLdb - do you have it installed?'
   print>>sys.stderr, '!!! MySQLdb is required to use sqlobject with kegbot. Exiting.'

import units
import util

SCHEMA_VERSION = 12

### utility functions

def setup(db_uri):
   """ Set default connection """
   connection = connectionForURI(db_uri)
   sqlhub.processConnection = connection

def drop_and_create(tbl):
   try:
      tbl.dropTable()
   except:
      pass
   tbl.createTable()


### table definitions

class Config(SQLObject):
   """ stores string key -> string value config data for python """
   class sqlmeta:
      table = 'config'
      idType = str

   value = StringCol(notNone=True)

   def createTable(cls, ifNotExists=False, createJoinTables=True,
                   createIndexes=True,
                   connection=None):
      conn = connection or cls._connection
      if ifNotExists and conn.tableExists(cls.sqlmeta.table):
         return
      conn.query(cls.createTableSQL())
   createTable = classmethod(createTable)

   def createTableSQL(cls, createJoinTables=True, connection=None,
                      createIndexes=True):
      conn = connection or cls._connection
      q = """
CREATE TABLE %s (
    %s VARCHAR(64) PRIMARY KEY NOT NULL,
    value TEXT NOT NULL
) """ % (cls.sqlmeta.table, cls.sqlmeta.idName)
      return q
   createTableSQL = classmethod(createTableSQL)


class Drink(SQLObject):
   """ Raw drink data: how much, when, pointers to user and keg """
   class sqlmeta:
      table = 'drinks'

   ticks = IntCol(default=0, notNone=True)
   volume = IntCol(default=0, notNone=True)
   starttime = IntCol(notNone=True)
   endtime = IntCol(notNone=True)
   user = ForeignKey('User', notNone=True)
   keg = ForeignKey('Keg', notNone=True)
   status = EnumCol(enumValues=['valid','invalid'], default='valid', notNone=True)


class Keg(SQLObject):
   """ One row for each keg used """
   class sqlmeta:
      table = 'kegs'

   # default full_volume = 15.5 gallons in mL
   type = ForeignKey('BeerType', notNone=True)
   full_volume = IntCol(default=58673, notNone=True)
   startdate = DateTimeCol(notNone=True)
   enddate = DateTimeCol(notNone=True)
   channel = IntCol(default=0, notNone=True)
   status = EnumCol(enumValues=['online', 'offline', 'coming soon'], default='online')
   description = StringCol(default='', notNone=True)
   origcost = FloatCol(default=0, notNone=True)


class Grant(SQLObject):
   """ Maps a policy (cost of pouring beer) to a user, with restrictions """
   class sqlmeta:
      table = 'grants'

   user = ForeignKey('User', notNone=True)
   expiration = EnumCol(enumValues=['none', 'time', 'volume', 'drinks'],
         default='volume', notNone=True)
   status = EnumCol(enumValues=['active', 'expired', 'deleted'],
         default='active', notNone=True)
   policy = ForeignKey('Policy', notNone=True)
   exp_volume = IntCol(default=0, notNone=True)
   exp_time = IntCol(default=0, notNone=True)
   exp_drinks = IntCol(default=0, notNone=True)
   total_volume = IntCol(default=0, notNone=True)
   total_drinks = IntCol(default=0, notNone=True)

   def AvailableVolume(self):
      """
      return how much volume is available with this grant, at this instant.
      """
      if self.IsExpired():
         return 0
      if self.expiration == 'volume':
         return max(0, self.exp_volume - self.total_volume)
      else:
         return sys.maxint

   def IsExpired(self, extravolume = 0):
      if self.status != 'active':
         return True
      if self.expiration == "none":
         return False
      elif self.expiration == "time":
         return self.exp_time < time.time()
      elif self.expiration == "volume":
         return (extravolume + self.total_volume) >= self.exp_volume
      else:
         return True

   def IncVolume(self, volume):
      self.total_volume += volume
      if self.expiration == 'volume':
         if self.total_volume >= self.exp_volume:
            self.status = 'expired'
      self.syncUpdate()

   def ExpiresBefore(self,other):
      """
      determine if this grant will expire sooner than the given one.

      intuitively, this should return 'true' if this grant should be used
      BEFORE the other one (ie, it expires sooner)
      """
      if self.expiration == 'time':
         if other.expiration == 'time':
            return self.exp_time < other.exp_time
         elif other.expiration == 'none':
            return True
      elif self.expiration == 'none':
         return False

      # fall-thru, XXX
      return False

   def MaxVolume(cls, user):
      """ return maximum volume pourable, in range [0, sys.maxint = infty) """
      grants = user.grants
      tot = 0
      for g in grants:
         vol = g.AvailableVolume()
         if vol == sys.maxint:   # unlimited
            return vol
         else:
            tot += vol
      return tot
   MaxVolume = classmethod(MaxVolume)


class User(SQLObject):
   """ Drinker information """
   class sqlmeta:
      table = 'users'

   username = StringCol(length=32, notNone=True)
   email = StringCol(default='')
   im_aim = StringCol(default='')
   password = StringCol(default='')
   gender = EnumCol(enumValues = ['male','female'], default='male')
   weight = FloatCol(default=180.0)

   grants = MultipleJoin('Grant', joinColumn='user_id')
   tokens = MultipleJoin('Token', joinColumn='user_id')
   labels = MultipleJoin('UserLabel', joinColumn='user_id')

   def HasLabel(self, lblname):
      return lblname in [lbl.labelname for lbl in self.labels]

   def MaxVolume(self):
      return Grant.MaxVolume(self)


class Policy(SQLObject):
   """ Specify cost function(s) for arbitrary volumes of beer """
   class sqlmeta:
      table = 'policies'

   type = EnumCol(enumValues = ['fixed-cost','free'], notNone=True)
   unitcost = FloatCol(default=0.0, notNone=True)
   unitvolume = IntCol(default=0, notNone=True)
   description = StringCol(default='', notNone=True)

   def Cost(self, volume):
      if self.type == 'free':
         return 0.0
      elif self.type == 'fixed-cost':
         return self.unitcost / self.unitvolume * volume


class Token(SQLObject):
   """ Maps an arbitrary ID (such as an 1-wire address) to a user, for auth """
   class sqlmeta:
      table = 'tokens'

   user = ForeignKey('User', notNone=True)
   keyinfo = StringCol(notNone=True)
   created = DateTimeCol(default=datetime.now)


class BAC(SQLObject):
   """ Generated table of historic blood-alcohol level estimates """
   class sqlmeta:
      table = 'bacs'

   user = ForeignKey('User')
   drink = ForeignKey('Drink')
   rectime = IntCol(notNone=True)
   bac = FloatCol(notNone=True)

   def ProcessDrink(cls, d):
      """ Store a BAC value given a recent drink """
      prev_bac = 0.0

      matches = BAC.select('user_id=%i' % d.user.id, orderBy='-rectime')
      if matches.count():
         last_bac = matches[0]
         prev_bac = util.decomposeBAC(last_bac.bac, d.endtime - last_bac.rectime)

      now = util.instantBAC(d.user.gender, d.user.weight, d.keg.type.abv,
            units.to_ounces(d.volume))
      # TODO(mikey): fix this factor
      #now = util.decomposeBAC(now, units.to_ounces(d.volume)/12.0*(30*60))

      b = BAC(user=d.user, drink=d.id, rectime=d.endtime, bac=now+prev_bac)
      d.syncUpdate()
   ProcessDrink = classmethod(ProcessDrink)


class GrantCharge(SQLObject):
   """ Records that a portion of a specific Grant was applied to a specific Drink """
   class sqlmeta:
      table = 'grantcharges'

   grant = ForeignKey('Grant')
   drink = ForeignKey('Drink')
   user = ForeignKey('User')
   volume = IntCol(default=0)


class Binge(SQLObject):
   """ Generated table caching uninterrupted groups of pours, plus total volume """
   class sqlmeta:
      table = 'binges'

   user = ForeignKey('User', notNone=True)
   startdrink = ForeignKey('Drink')
   enddrink = ForeignKey('Drink')
   volume = IntCol(default=0, notNone=True)
   starttime = IntCol(notNone=True)
   endtime = IntCol(notNone=True)

   def Assign(cls, d):
      """ Create or update a binge given a recent drink """
      min_end = d.endtime - 60*90
      binges = Binge.select("user_id=%i AND endtime >= %i"% (d.user.id, min_end), orderBy="-id", limit=1)

      # now find or create the current binge, and update it
      if binges.count() == 0:
         last_binge = Binge(user=d.user, startdrink=d,
               enddrink=d, volume=d.volume, starttime=d.endtime,
               endtime=d.endtime)
         last_binge.syncUpdate()
      else:
         last_binge = binges[0]
         last_binge.volume += d.volume
         last_binge.enddrink = d
         last_binge.endtime = d.endtime
         last_binge.syncUpdate()
      return last_binge.id
   Assign = classmethod(Assign)


class Userpic(SQLObject):
   """ User can store his image in SQL (mostly for frontend use) """
   class sqlmeta:
      table = 'userpics'

   user = ForeignKey('User', notNone=True)
   filetype = EnumCol(enumValues=['png','jpeg'], default='png', notNone=True)
   modified = DateTimeCol(default=datetime.now)
   data = BLOBCol(length=2**24)


class ThermoLog(SQLObject):
   """ Log of temperatures, indexed by arbitrary sensor name """
   class sqlmeta:
      table = 'thermolog'

   name = StringCol(notNone=True, default='')
   temp = FloatCol(notNone=True, default=0.0)
   time = DateTimeCol(notNone=True, default=datetime.now)


class RelayLog(SQLObject):
   """ Log of relay events, indicated by arbitrary relay name """
   class sqlmeta:
      table = 'relaylog'

   name = StringCol(notNone=True, default='')
   status = EnumCol(enumValues=['unknown','on','off'], default='unknown', notNone=True)
   time = DateTimeCol(notNone=True, default=datetime.now)


class BeerType(SQLObject):
   """ Describes a specific beer by name, brewer, style, and content """
   class sqlmeta:
      table = 'beertypes'

   name = StringCol(notNone=True, default='')
   brewer = ForeignKey('Brewer', notNone=True)
   style = ForeignKey('BeerStyle', notNone=True, default=1)
   calories_oz = FloatCol(default=None)   # None is OK here, to indicate no data
   carbs_oz = FloatCol(default=None)      # None is OK here, to indicate no data
   abv = FloatCol(notNone=True, default=4.5)


class Brewer(SQLObject):
   """ Dynamic table of beer brewer information """
   class sqlmeta:
      table = 'brewers'

   name = StringCol(notNone=True, default='')
   origin_country = StringCol(notNone=True, default='')
   origin_state = StringCol(notNone=True, default='')
   origin_city = StringCol(notNone=True, default='')
   distribution = EnumCol(notNone=True, enumValues=['retail', 'homebrew', 'unknown'], default='unknown')
   url = StringCol(notNone=True, default='')
   comment = StringCol(notNone=True, default='')


class BeerStyle(SQLObject):
   """ Dynamic table of beer style information """
   class sqlmeta:
      table = 'beerstyles'

   name = StringCol(notNone=True)


class UserLabel(SQLObject):
   """ A dynamic enumerations column for the users table """
   class sqlmeta:
      table = 'userlabels'

   # XXX TODO: should have primary key(user, labelname)
   user = ForeignKey('User', notNone=True)
   labelname = StringCol(notNone=True)


### maintenance-related functions

def all_tables():
   """ return all tables (ie all classes derived from SQLObject) """
   import inspect
   classes = [x for x in globals().values() if inspect.isclass(x) and issubclass(x, SQLObject) and x is not SQLObject]
   return classes

def create_tables():
   """ attempt to create all tables """
   for c in all_tables():
      c.createTable()

def set_defaults():
   """ default values (contents may change with schema) """
   # config table defaults
   Config(id='logging.logfile', value='keg.log'),
   Config(id='logging.logformat', value='%(asctime)s %(levelname)-8s (%(name)s) %(message)s'),
   Config(id='logging.use_sql', value='false'),
   Config(id='logging.logtable', value='logging'),
   Config(id='logging.use_logfile', value='true'),
   Config(id='logging.use_stream', value='true'),
   Config(id='devices.lcd', value='/dev/lcd'),
   Config(id='devices.onewire', value='/dev/onewire'),
   Config(id='devices.thermo', value='/dev/thermo'),
   Config(id='devices.flow', value='/dev/flow'),
   Config(id='ui.keypad_pipe', value='/dev/input/event0'),
   Config(id='ui.use_lcd', value='true'),
   Config(id='ui.translation_file', value='keymap.cfg'),
   Config(id='ui.lcd_model', value='lk204-25'),
   Config(id='timing.ib_refresh_timeout', value='0.75'),
   Config(id='timing.ib_idle_timeout', value='60'),
   Config(id='thermo.use_thermo', value='true'),
   Config(id='thermo.temp_max_low', value='2.0'),
   Config(id='thermo.temp_max_high', value='4.5'),
   Config(id='db.schema_version', value=str(SCHEMA_VERSION)),

   # user defaults
   import md5
   admin_user = User(username='admin', password=md5.md5('admin').hexdigest())
   guest_user = User(username='unknown')

   # policy table defaults
   free_policy = Policy(type='free', description='free')
   guest_policy = Policy(type='free', description='__guest__')

   # grant defaults
   Grant(user=admin_user, expiration='none', status='active', policy=free_policy)
   Grant(user=guest_user, expiration='none', status='active', policy=free_policy)

   # brewer defaults
   unk_brewer = Brewer(name='Unknown')

   # beerstyle defaults
   unk_style = BeerStyle(name='Unknown')

   # beertype defaults
   BeerType(name="unknown", brewer=unk_brewer, style=unk_style)

   # userlabel defaults
   UserLabel(user=admin_user, labelname='admin')
   UserLabel(user=guest_user, labelname='guest')

