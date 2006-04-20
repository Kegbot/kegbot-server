from datetime import datetime
import time
import sys

try:
   from sqlobject import *
except ImportError:
   print>>sys.stderr, 'Could not import sqlobject - do you have it installed?'
   print>>sys.stderr, 'Kegbot requires sqlobject version 0.7 or later. Exiting.'
   sys.exit(1)

import units
import util

SCHEMA_VERSION = 11

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


class User(SQLObject):
   """ Drinker information """
   class sqlmeta:
      table = 'users'

   username = StringCol(length=32, notNone=True)
   email = StringCol(default='')
   im_aim = StringCol(default='')
   admin = EnumCol(enumValues = ['yes','no'])
   password = StringCol(default='')
   gender = EnumCol(enumValues = ['male','female'])
   weight = FloatCol(default=180.0)


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
   created = DateTimeCol()


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
      binges = list(Binge.select("user_id=%i"%d.user.id,
         orderBy="-id", limit=1))

      # flush binge fetched if it is too old
      if len(binges) != 0:
         if binges[0].endtime < (d.endtime - (60*90)): # XXX fix constant
            binges = []

      # now find or create the current binge, and update it
      if len(binges) == 0:
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
   calories_oz = FloatCol()   # None is OK here, to indicate no data
   carbs_oz = FloatCol()      # None is OK here, to indicate no data
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

### defaults for this schema version
def set_defaults():
   # config table defaults
   cfgs = (('logging.logfile', 'keg.log'),
      ('logging.logformat', '%(asctime)s %(levelname)-8s (%(name)s) %(message)s'),
      ('logging.use_sql', 'false'),
      ('logging.logtable', 'logging'),
      ('logging.use_logfile', 'true'),
      ('logging.use_stream', 'true'),
      ('devices.lcd', '/dev/lcd'),
      ('devices.onewire', '/dev/onewire'),
      ('devices.thermo', '/dev/thermo'),
      ('devices.flow', '/dev/flow'),
      ('ui.keypad_pipe', '/dev/input/event0'),
      ('ui.use_lcd', 'true'),
      ('ui.translation_file', 'keymap.cfg'),
      ('ui.lcd_model', 'lk204-25'),
      ('timing.ib_refresh_timeout', '0.75'),
      ('timing.ib_idle_timeout', '60'),
      ('thermo.temp_max_low', '2.0'),
      ('thermo.temp_max_high', '4.5'),
      ('db.schema_version', str(SCHEMA_VERSION)),
   )
   for key, val in cfgs:
      obj = Config(id=key, value=val)
      obj.syncUpdate()   # inserts in sqlobject 0.7 are never lazy, tho

   # policy table defaults
   p = Policy(type='free', description='free')
   p.syncUpdate()



