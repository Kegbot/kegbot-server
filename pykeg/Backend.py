from sqlobject import *

class Drink(SQLObject):
   class sqlmeta:
      table = 'drinks'
      lazyUpdate = True

   ticks = IntCol()
   volume = IntCol()
   starttime = IntCol()
   endtime = IntCol()
   user_id = ForeignKey('User')
   keg_id = ForeignKey('Keg')
   status = EnumCol(enumValues = ['valid','invalid'])

class Keg(SQLObject):
   class sqlmeta:
      table = 'kegs'
      lazyUpdate = True

   full_volume = IntCol()
   startdate = DateTimeCol()
   enddate = DateTimeCol()
   status = EnumCol(enumValues = ['online', 'offline', 'coming soon'])
   beername = StringCol()
   alccontent = FloatCol()
   description = StringCol()
   origcost = FloatCol()
   beerpalid = IntCol()
   ratebeerid = IntCol()
   calories_oz = FloatCol()

class Grant(SQLObject):
   class sqlmeta:
      table = 'grants'
      lazyUpdate = True

   foruid = ForeignKey('User')
   expiration = EnumCol(enumValues = ['none', 'time', 'ounces', 'drinks'])
   status = EnumCol(enumValues = ['active', 'expired', 'deleted'])
   forpolicy_id = ForeignKey('Policy')
   exp_volume = IntCol()
   exp_time = IntCol()
   exp_drinks = IntCol()
   total_volume = IntCol()
   total_drinks = IntCol()

   def AvailableVolume(self):
      """
      return how much volume is available with this grant, at this instant.
      """
      if self.IsExpired():
         return 0
      if self.expiration == 'volume':
         return max(0, self.exp_volume - self.total_volume)
      else:
         return -1

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
   class sqlmeta:
      table = 'users'
      lazyUpdate = True

   username = StringCol(length=32)
   email = StringCol()
   im_aim = StringCol()
   admin = EnumCol(enumValues = ['yes','no'])
   password = StringCol()
   gender = EnumCol(enumValues = ['male','female'])
   weight = FloatCol()
   image_url = StringCol()

class Policy(SQLObject):
   class sqlmeta:
      table = 'policies'
      lazyUpdate = True

   type = EnumCol(enumValues = ['fixed-cost','free'])
   unitcost = FloatCol()
   unitvolume = IntCol()
   description = StringCol()

class Token(SQLObject):
   class sqlmeta:
      table = 'tokens'
      lazyUpdate = True

   ownerid = ForeignKey('User')
   keyinfo = StringCol()
   created = DateTimeCol()

