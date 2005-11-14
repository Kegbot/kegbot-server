import MySQLdb
import time
import Queue
import thread

class DrinkStore:
   """
   Storage of drink events.

   This class is used to store, lookup, and read individual drink events. This
   is used to abstract the backend from the keg system. This implementation
   provides SQL storage.
   """

   def __init__(self, owner, dbinfo, table, minticks = 0):
      self.owner = owner
      (host,user,password,db) = dbinfo
      self.dbconn = MySQLdb.connect(host=host,user=user,passwd=password,db=db)
      self.table = table
      self.minticks = minticks

   def logDrink(self, uid, kegid, ticks, volunits, start, end):
      """
      Record a drink event.

      Save the ticks, start time, end time, and user id that are passed in with
      a drink event.
      """
      c = self.dbconn.cursor()

      # only record ticks matching our minim threshhold
      if ticks >= self.minticks:
        q = 'INSERT INTO %s (ticks, volume, starttime, endtime, user_id, keg_id) VALUES ("%s","%s","%s","%s","%s","%s")' % (self.table, ticks, volunits, int(start), int(end), uid, kegid)
        c.execute(q)

   def getLastDrink(self,userid):
      c = self.dbconn.cursor()
      q = 'SELECT bac,endtime from %s WHERE user_id=%s AND frag=0 ORDER BY endtime DESC' % (self.table,userid)
      c.execute(q)
      row = c.fetchone()
      drinks = []

      if row:
         return( (row[0],row[1]) )
      return (0.0,0.0)

   def readDrink(self, readinfo):
      """
      Find a drink, or multiple drink, with fields matching the dictionary readinfo.
      """
      pass

class UserStore:
   """
   Storage of user info.
   """
   def __init__(self, owner, dbinfo, table):
      self.owner = owner
      (host,user,password,db) = dbinfo
      self.dbconn = MySQLdb.connect(host=host,user=user,passwd=password,db=db)
      self.table = table

   def getAllUsers(self):
      c = self.dbconn.cursor()
      q = "SELECT id FROM %s" % (self.table,)
      c.execute(q)

      ret = []
      for row in c.fetchall():
         ret.append(self.getUser(row[0]))
      return ret

   def getUser(self, uid):
      """
      Get a User() object for a given uid.
      """
      c = self.dbconn.cursor()
      q = "SELECT id,username,email,im_aim,gender,weight FROM %s WHERE id='%s' LIMIT 1" % (self.table,uid)
      if c.execute(q):
         (uid,username,email,im_aim,gender,weight) = c.fetchone()
         return User(id = uid, username = username, email = email, aim = im_aim, gender = gender, weight = weight)
      return None

   def getUid(self, username):
      c = self.dbconn.cursor()
      q = 'SELECT id FROM %s WHERE username="%s" LIMIT 1' % (self.table,username)
      c.execute(q)
      return c.fetchone()[0]

   def getUserByName(self, username):
      c = self.dbconn.cursor()
      q = "SELECT id,username,email,im_aim,gender,weight FROM %s WHERE username='%s' LIMIT 1" % (self.table,username)
      if c.execute(q):
         (uid,username,email,im_aim,gender,weight) = c.fetchone()
         return User(id = uid, username = username, email = email, aim = im_aim, gender = gender, weight = weight)
      return None

   def addUser(self, username, email, im_aim):
      c = self.dbconn.cursor()
      q = 'INSERT INTO %s (username, email, im_aim) VALUES ("%s", "%s", "%s")' % (self.table,username,email,im_aim)
      c.execute(q)
      return self.dbconn.insert_id()

class PolicyStore:
   def __init__(self, owner, dbinfo, table):
      self.owner = owner
      (host,user,password,db) = dbinfo
      self.dbconn = MySQLdb.connect(host=host,user=user,passwd=password,db=db)
      self.table = table

   def newPolicy(self, type="fixed-cost", unitcost="0.0", unitvolume="0.0", description="unknown"):
      c = self.dbconn.cursor()
      q = "INSERT INTO `%s` (`type`,`unitcost`,`unitvolume`,`description`) VALUES ('%s','%s','%s','%s')" % (self.table,type,unitcost,unitvolume,description)
      c.execute(q)
      return self.getPolicy(self.dbconn.insert_id())

   def getPolicy(self, policyid):
      c = self.dbconn.cursor()
      q = 'SELECT * FROM %s WHERE id=%s' % (self.table,policyid)
      c.execute(q)
      try:
         (id, type, unitcost, unitvolume, descr) = c.fetchone()
         return Policy(id,type,unitcost,unitvolume,descr)
      except:
         return None

class Policy:
   def __init__(self,id,type,unitcost,unitvolume,descr):
      self.id = id
      self.ptype = type
      self.unitcost = unitcost
      self.unitvolume = unitvolume
      self.descr = descr

class KegStore:
   """
   Storage of keg info
   """
   def __init__(self, owner, dbinfo, table):
      self.owner = owner
      (host,user,password,db) = dbinfo
      self.dbconn = MySQLdb.connect(host=host,user=user,passwd=password,db=db)
      self.table = table

   def getKeg(self,id):
      c = self.dbconn.cursor()
      q = "SELECT * FROM %s WHERE `id`='%s'" % (self.table,id)
      c.execute(q)
      try:
         row = c.fetchone()
         return apply(Keg,row)
      except:
         return 0

   def getCurrentKeg(self):
      c = self.dbconn.cursor()
      q = "SELECT * FROM %s WHERE status='online' ORDER BY id DESC LIMIT 1" % (self.table,)
      c.execute(q)
      try:
         row = c.fetchone()
         return apply(Keg,row)
      except:
         return None

class ThermoStore:
   """
   Storage of temperature sensor data.

   This sort of data is probably best stored in a round-robin database. We're
   probably only interested in recent temperatures for the day, and averages
   for the week, month, year.
   """
   def __init__(self, owner, dbinfo, table):
      self.owner = owner
      (host,user,password,db) = dbinfo
      self.dbconn = MySQLdb.connect(host=host,user=user,passwd=password,db=db)
      self.table = table
      self.actions = Queue.Queue()
      thread.start_new_thread(self.logger,())

   def logger(self):
      while 1:
         q = self.actions.get()
         c = self.dbconn.cursor()
         c.execute(q)
         self.purgeOld()

   def logTemp(self, temp, sensor, fs):
      q = "INSERT INTO %s (`rectime`,`sensor`,`temp`,`fridgestatus`) VALUES ('%s','%s','%s','%s')" % (self.table,time.time(),sensor,temp,fs)
      self.actions.put(q)
      self.owner.info('ThermoStore','temperature now %.2f' % temp)

   def purgeOld(self,hours=6):
      c = self.dbconn.cursor()
      q = "DELETE FROM %s WHERE `rectime` < UNIX_TIMESTAMP(NOW()) - 60*60*%i" % (self.table,hours)
      c.execute(q)

   def updateLastTemp(self):
      """
      update the last entry in the database with the current time.

      this function will update the last row in the table with the current
      time. this is meant to save table space when, at some interval, a new
      temperature reading returns the same temperature as last recorded. the
      purpose is to update the timestamp to show we actually took a measurement
      at this time.
      """
      q = "UPDATE `%s` SET `rectime`='%s' ORDER BY `rectime` DESC LIMIT 1" % (self.table,int(time.time()))
      self.actions.put(q)

class Keg:
   def __init__(self,id,startvolume,startdate,enddate,status,beername,alccontent,description,origcost,beerpalid,ratebeerid,calories_oz):
      self.id = id
      self.startvolume = startvolume
      self.startdate = startdate
      self.enddate = enddate
      self.beername = beername
      self.alccontent = alccontent
      self.description = description
      self.origcost = origcost
      self.beerpalid = beerpalid
      self.ratebeerid= ratebeerid
      self.calories_oz = calories_oz

class GrantStore:
   """
   Storage of user info.
   """
   def __init__(self, owner, dbinfo, table, pstore):
      self.owner = owner
      (host,user,password,db) = dbinfo
      self.dbconn = MySQLdb.connect(host=host,user=user,passwd=password,db=db)
      self.pstore = pstore
      self.table = table

   def newGrant(self, foruid = 0, expiration = "none", status = "active", forpolicy=0,exp_volume = 0,exp_time=0,exp_drinks=0,total_volume=0,total_drinks=0):
      c = self.dbconn.cursor()
      q = "INSERT INTO `%s` (foruid,expiration,status,forpolicy,exp_volume,exp_time,exp_drinks,total_volume,total_drinks) VALUES ('%s','%s','%s','%s','%s','%s','%s','%s','%s')" % (self.table,foruid,expiration,status,forpolicy,exp_volume,exp_time,exp_drinks,total_volume,total_drinks)
      c.execute(q)
      return self.getGrant(self.dbconn.insert_id())

   def getGrant(self,id):
      c = self.dbconn.cursor()
      q = 'SELECT * FROM %s WHERE id ="%s"' % (self.table,id)
      c.execute(q)
      row = c.fetchone()
      g = apply(Grant,row)
      g.setPolicy(self.pstore.getPolicy(g.forpolicy))
      return g

   def getGrants(self, user):
      c = self.dbconn.cursor()
      q = 'SELECT * FROM %s WHERE foruid="%s" AND status!="deleted"' % (self.table,user.id)
      grants = []
      if c.execute(q):
         row = c.fetchone()
         while row:
            ( id,foruid,expiration,status,forpolicy,exp_volume,exp_time,exp_drinks,total_volume,total_drinks) = row
            newgrant = apply(Grant,row) # grant constructor takes those parameters above, in order
            newgrant.setPolicy(self.pstore.getPolicy(forpolicy))
            grants.append(newgrant)
            row = c.fetchone()
      return grants

   def orderGrants(self,grants):
      # priorities:
      #   - select grants with least cost
      #   - among those grants, select the one whose expiration comes soonest

      costtable = {}

      # first, organize the grants 
      for grant in grants:
         if not grant.policy or grant.status != 'active':
            continue

         curouncecost = round(grant.policy.unitcost / grant.policy.unitvolume,3)

         # see if we already have a space in this list for this ouncecost (unlikely, but possible)
         if not costtable.has_key(curouncecost):
            costtable[curouncecost] = []

         # add this grant to that cost bracket. (later, we will
         # figure out which grant, in this cost bracket, is best to use
         # first)
         costtable[curouncecost].append(grant)

      # now, we have a hash table with several lists of grants, indexed by
      # "cost per ounce". we need to flatten this out. so, for every "cost per
      # ounce" list (starting with the cheapest), select the best grant and add
      # it to our return list
      # for example:
      # costtable =  {  0.0: [g1, g4],
      #                 0.5: [g3]
      #                 0.1: [g2]
      #              }
      # supposing g4 expires before g1, the desired return would be:
      # retlist = [g4, g1, g2, g3]
      keys = costtable.keys()
      keys.sort()
      ret = []
      for key in keys:
         grants = costtable[key]
         grants.sort(self.grantExpCmp)
         for grant in grants:
            ret.append(grant)

      return ret

   def grantExpCmp(self,a,b):
      if a.expiresBefore(b):
         return 1
      elif b.expiresBefore(a):
         return -1
      else:
         return 0

class Grant:
   """
   A grant gives a user limited access to drink beer with a specific
   BillingPolicy.

   Grants and BillingPolicies can be related like this: a Grant will determine
   if a user may pour beer, and a BillingPolicy will determine how much that
   beer will cost.

   In the simplest system, there will be one BillingPolicy: a static,
   zero-cost-per-ounce BillingPolicy. Every user would then have a single Grant
   for this policy, and that grant would always be valid.

   But, more complicated situations may be desired, and can in fact be modeled.
   Some of the situations I want to account for are:

      - Different prices for different people: if I bought the keg, I want all
        my beer at cost.
      - Free Drink "Coupons": I should be able to give certain people free
        drink bonuses, say, when they sign up.
      - Time-based billing: depending on the time of day, beer should be
        cheaper or more expensive. (The "happy hour" effect..)
      - Predatory billing: take advantage of human behavior to maximize
        profits. For example, make the first 4 drinks more expensive, but make
        subsequent drinks in that period much cheaper. "The more you drink, the
        more you save!"

   All of these situations can be accounted for with combinations of grants and policys.

   Note that it is entirely plausible that a user may have multiple grants
   corresponding to unique, overlapping BillingPolicy objects. The beer flow
   maintenance loop will constantly allow flow based on "best-choice" grant
   selection.

   """
   def __init__(self,id,foruid,expiration,status,forpolicy,exp_volume,exp_time,exp_drinks,total_volume,total_drinks):
      self.id = id
      self.foruid = foruid
      self.expiration = expiration
      self.status = status
      self.forpolicy = forpolicy
      self.exp_volume = exp_volume
      self.exp_time = exp_time
      self.exp_drinks = exp_drinks
      self.total_volume = total_volume
      self.total_drinks = total_drinks

      self.policy = None

   def __str__(self):
      return "id: %s, exp: %s, status: %s, forpolicy: %s, exp_volume: %s, exp_time: %s, exp_drinks: %s, total_volume: %s, total_drinks: %s" % (self.id,self.expiration,self.status,self.forpolicy,self.exp_volume,self.exp_time,self.exp_drinks,self.total_volume,self.total_drinks)

   def setPolicy(self,p):
      self.policy = p

   def incrementTicks(self,amt):
      self.total_volume += amt

   def availableVolume(self):
      """
      return how much volume is available with this grant, at this instant.
      """
      if self.isExpired():
         return 0
      if self.expiration == 'volume':
         return max(0, self.exp_volume - self.total_volume)
      else:
         return -1

   def isExpired(self, extravolume = 0):
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

   def expiresBefore(self,other):
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

class KeyStore:
   """
   Storage of user info.
   """
   def __init__(self, owner, dbinfo, table):
      self.owner = owner
      (host,user,password,db) = dbinfo
      self.dbconn = MySQLdb.connect(host=host,user=user,passwd=password,db=db)
      self.table = table

   def getKey(self,keyinfo):
      """
      Return a Key() object, based on an exact match for keyinfo. Returns only one match.
      """
      c = self.dbconn.cursor()
      q = "SELECT id, ownerid, keyinfo, created FROM %s WHERE keyinfo='%s' LIMIT 1" % (self.table,MySQLdb.escape_string(keyinfo))
      if c.execute(q):
         (id,ownerid,keyinfo,created) = c.fetchone()
         return Key(keyinfo,ownerid)
      else:
         return None

   def addKey(self, ownerid, keyinfo):
      c = self.dbconn.cursor()
      q = 'INSERT INTO %s (ownerid, keyinfo) VALUES (%s, "%s")' % (self.table,ownerid,keyinfo)
      c.execute(q)
      return self.dbconn.insert_id()


   def knownKey(self,keyinfo):
      c = self.dbconn.cursor()
      q = 'SELECT ownerid FROM tokens WHERE keyinfo="%s" LIMIT 1' % (keyinfo)
      c.execute(q)
      return len(c.fetchall()) == 1

class Key:
   def __init__(self,keyinfo,ownerid):
      self.keyinfo = keyinfo
      self.ownerid = ownerid

   def getOwner(self):
      return self.ownerid

class BillingPolicy:
   """
   A BillingPolicy (or policy, for short) provides a dollar metric that
   represents the cost of beer

   The following policy types, or ptypes, shal be considered:

      - drink-static
        For every drink, there is a fixed cost. The unitcost will be some
        dollar amount, and a drink will cost that exact amount, regardless of
        the drink size.

      - ounce-static
        Cost is static per ounce. This will probably be the most common type of
        policy. For situations where the first N ounces shall be cheaper than
        the next M ounces, multiple policies should be created.

      - functional
        Not implemented, but perhaps would be useful to model a policy such as
         C = ceiling(1.0,ounces*metric+0.5)
        (charge metric cents per ounce, plus 50 cents; or charge $1, whichever is more)

   A policy will have the following variables associated with it:

      - ptype
        The "policy type", as described above

      - unitcost
        The cost per unit.

      - granularity
        A number, probably in ticks, which shall be the least billable unit in
        drink cost computations. For example, if 1000 ticks are in one ounce,
        then a granularity of 6000 will round drinks up to six-ounce values.
        (Probably kinda mean.)

   """
   def __init__(self,ptype,unitcost,granularity):
      self.ptype = ptype   # drink-static, ounce-static, date based, functional
      self.unitcost = unitcost     # unit cost (eg per ounce
      self.granularity = granularity

class User:
   def __init__(self,id,username,email,aim,weight=0.0,gender='male'):
      self.id = id
      self.username = username
      self.email = email
      self.aim = aim
      self.weight = weight
      self.gender = gender

   def __eq__(self, other):
      if type(other) != type(self):
         return False
      return self.username == other.username

   def getName(self):
      return self.username

   def isAdmin(self):
      return False
