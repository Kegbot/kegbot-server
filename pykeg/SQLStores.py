import MySQLdb
import time

class DrinkStore:
   """
   Storage of drink events.

   This class is used to store, lookup, and read individual drink events. This
   is used to abstract the backend from the keg system. This implementation
   provides SQL storage.
   """

   def __init__(self, dbinfo, table, minticks = 0):
      (host,user,password,db) = dbinfo
      self.dbconn = MySQLdb.connect(host=host,user=user,passwd=password,db=db)
      self.table = table
      self.minticks = minticks

   def setMinTicks(self,min):
      """
      Set the minimum number of ticks necessary for log/read operations.
      """
      self.minticks = min

   def logDrink(self, uid, ticks, start, end):
      """
      Record a drink event.

      Save the ticks, start time, end time, and user id that are passed in with
      a drink event.
      """
      c = self.dbconn.cursor()

      # only record ticks matching our minim threshhold
      if ticks >= self.minticks:
        q = 'INSERT INTO %s (ticks, starttime, endtime, user_id) VALUES ("%s",FROM_UNIXTIME(%s),FROM_UNIXTIME(%s),"%s")' % (self.table, ticks, int(start), int(end), uid)
        c.execute(q)

   def logFragment(self, drink_id, userid, bac, keg, starttime, endtime, ticks, frag, grant, grantticks):
      c = self.dbconn.cursor()
      if drink_id:
         q = ' INSERT INTO %s (id,frag,ticks,totalticks,starttime,endtime,bac,user_id,keg_id,grant_id) ' % (self.table,)
         q += 'VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)' % (drink_id,frag,grantticks,ticks,starttime,endtime,bac,userid,keg.id,grant.id)
      else:
         q = ' INSERT INTO %s (frag,ticks,totalticks,starttime,endtime,bac,user_id,keg_id,grant_id) ' % (self.table,)
         q += 'VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s)' % (frag,grantticks,ticks,starttime,endtime,bac,userid,keg.id,grant.id)

      c.execute(q)
      drink_id = c.insert_id()

      # also save the ounces poured with the grant
      ounces_for_grant = keg.getDrinkOunces(grantticks)
      q = "UPDATE `grants` SET `total_ounces` = `total_ounces`+'%s' WHERE `id`='%s' LIMIT 1" % (ounces_for_grant,grant.id)
      c.execute(q);

      return drink_id

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
   def __init__(self, dbinfo, table):
      (host,user,password,db) = dbinfo
      self.dbconn = MySQLdb.connect(host=host,user=user,passwd=password,db=db)
      self.table = table

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

   def addUser(self, username, email, im_aim):
      c = self.dbconn.cursor()
      q = 'INSERT INTO %s (username, email, im_aim) VALUES ("%s", "%s", "%s")' % (self.table,username,email,im_aim)
      c.execute(q)
      return c.insert_id()

class PolicyStore:
   def __init__(self, dbinfo, table):
      (host,user,password,db) = dbinfo
      self.dbconn = MySQLdb.connect(host=host,user=user,passwd=password,db=db)
      self.table = table

   def newPolicy(self, type="fixed-cost", unitcost="0.0", unitounces="0.0", description="unknown"):
      c = self.dbconn.cursor()
      q = "INSERT INTO `%s` (`type`,`unitcost`,`unitounces`,`description`) VALUES ('%s','%s','%s','%s')" % (self.table,type,unitcost,unitounces,description)
      c.execute(q)
      return self.getPolicy(c.insert_id())

   def getPolicy(self, policyid):
      c = self.dbconn.cursor()
      q = 'SELECT * FROM %s WHERE id=%s' % (self.table,policyid)
      c.execute(q)
      try:
         (id, type, unitcost, unitounces, descr) = c.fetchone()
         return Policy(id,type,unitcost,unitounces,descr)
      except:
         return None

class Policy:
   def __init__(self,id,type,unitcost,unitounces,descr):
      self.id = id
      self.ptype = type
      self.unitcost = unitcost
      self.unitounces = unitounces
      self.descr = descr

class KegStore:
   """
   Storage of keg info
   """
   def __init__(self, dbinfo, table):
      (host,user,password,db) = dbinfo
      self.dbconn = MySQLdb.connect(host=host,user=user,passwd=password,db=db)
      self.table = table

   def newKeg(self,tickmetric=68.08,startounces=1984.0,status="offline",beername="unknown",alccontent=0.0,description="unknown",origcost=0.0,beerpalid=0):
      c = self.dbconn.cursor()
      q = "INSERT INTO `%s` (`tickmetric`,`startounces`,`status`,`beername`,`alccontent`,`description`,`origcost`,`beerpalid`) VALUES ('%s','%s','%s','%s','%s','%s','%s','%s')" % (self.table,tickmetric,startounces,status,beername,alccontent,description,origcost,beerpalid)
      c.execute(q)
      return self.getKeg(c.insert_id())

   def activateKeg(self,id):
      c = self.dbconn.cursor()
      q = "UPDATE `%s` SET `status`='offline' WHERE `id` != '%s'" % (self.table,id)
      c.execute(q)
      q = "UPDATE `%s` SET `status`='online' WHERE `id` = '%s'" % (self.table,id)
      c.execute(q)

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
         return 0

class ThermoStore:
   """
   Storage of temperature sensor data.

   This sort of data is probably best stored in a round-robin database. We're
   probably only interested in recent temperatures for the day, and averages
   for the week, month, year.
   """
   def __init__(self, dbinfo, table):
      (host,user,password,db) = dbinfo
      self.dbconn = MySQLdb.connect(host=host,user=user,passwd=password,db=db)
      self.table = table

   def logTemp(self, temp, sensor, fs):
      c = self.dbconn.cursor()
      q = "INSERT INTO %s (`rectime`,`sensor`,`temp`,`fridgestatus`) VALUES ('%s','%s','%s','%s')" % (self.table,time.time(),sensor,temp,fs)
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
      c = self.dbconn.cursor()
      q = "UPDATE `%s` SET `rectime`='%s' ORDER BY `rectime` DESC LIMIT 1" % (self.table,int(time.time()))
      c.execute(q)

class Keg:
   def __init__(self,id,tickmetric,startounces,startdate,enddate,status,beername,alccontent,description,origcost,beerpalid,calories_oz):
      self.id = id
      self.tickmetric = tickmetric
      self.startounces = startounces
      self.startdate = startdate
      self.enddate = enddate
      self.beername = beername
      self.alccontent = alccontent
      self.description = description
      self.origcost = origcost
      self.beerpalid = beerpalid
      self.calories_oz = calories_oz

   def getDrinkOunces(self,ticks):
      return float(ticks)/self.tickmetric

   def getDrinkTicks(self,ounces):
      return int(ounces*self.tickmetric)

class GrantStore:
   """
   Storage of user info.
   """
   def __init__(self, dbinfo, table, pstore):
      (host,user,password,db) = dbinfo
      self.dbconn = MySQLdb.connect(host=host,user=user,passwd=password,db=db)
      self.pstore = pstore
      self.table = table

   def newGrant(self, foruid = 0, expiration = "none", status = "active", forpolicy=0,exp_ounces = 0,exp_time=0,exp_drinks=0,total_ounces=0,total_drinks=0):
      c = self.dbconn.cursor()
      q = "INSERT INTO `%s` (foruid,expiration,status,forpolicy,exp_ounces,exp_time,exp_drinks,total_ounces,total_drinks) VALUES ('%s','%s','%s','%s','%s','%s','%s','%s','%s')" % (self.table,foruid,expiration,status,forpolicy,exp_ounces,exp_time,exp_drinks,total_ounces,total_drinks)
      c.execute(q)
      return self.getGrant(c.insert_id())

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
            ( id,foruid,expiration,status,forpolicy,exp_ounces,exp_time,exp_drinks,total_ounces,total_drinks) = row
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

         curouncecost = round(grant.policy.unitcost / grant.policy.unitounces,3)

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
   def __init__(self,id,foruid,expiration,status,forpolicy,exp_ounces,exp_time,exp_drinks,total_ounces,total_drinks):
      self.id = id
      self.foruid = foruid
      self.expiration = expiration
      self.status = status
      self.forpolicy = forpolicy
      self.exp_ounces = exp_ounces
      self.exp_time = exp_time
      self.exp_drinks = exp_drinks
      self.total_ounces = total_ounces
      self.total_drinks = total_drinks

      self.policy = None

   def __str__(self):
      return "id: %s, exp: %s, status: %s, forpolicy: %s, exp_ounces: %s, exp_time: %s, exp_drinks: %s, total_ounces: %s, total_drinks: %s" % (self.id,self.expiration,self.status,self.forpolicy,self.exp_ounces,self.exp_time,self.exp_drinks,self.total_ounces,self.total_drinks)

   def setPolicy(self,p):
      self.policy = p

   def incrementTicks(self,amt):
      self.total_ounces += amt

   def isExpired(self, extraounces = 0):
      if self.status != 'active':
         return True
      if self.expiration == "none":
         return False
      elif self.expiration == "time":
         return self.exp_time < time.time()
      elif self.expiration == "ounces":
         return (extraounces + self.total_ounces) >= self.exp_ounces
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
   def __init__(self, dbinfo, table):
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
      return c.insert_id()


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

class Grant2:
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
   def __init__(self,id):
      pass

class DrinkRecord:
   """
   store and save a record of a drink.
   """
   def __init__(self,ds,userid,keg):
      self.drink_store = ds
      self.userid = userid
      self.keg = keg
      self.frags = []
      self.start = time.time()
      self.logged = False

   def addFragment(self, grant, grant_ticks):
      """
      assumption: addFragment will always be called with unique grant_ids. two
      consecutive calls with the same grant_id indicates an update to the last
      fragment
      """
      # maybe this is an "update" call...?
      if len(self.frags) != 0:
         if self.frags[-1][0].id == grant.id:
            self.frags[-1] = (grant,grant_ticks)
            return
      # otherwise...
      self.frags.append((grant,grant_ticks))

   def emit(self, final_ticks, grant, grant_ticks, bac):
      if self.logged:
         return
      else:
         self.logged = True

      endtime = time.time()

      drink_id = None
      for frag in range(0,len(self.frags)):
         (grant, gticks) = self.frags[frag]
         res = self.drink_store.logFragment(drink_id, self.userid, bac, self.keg, self.start, endtime, final_ticks, frag, grant, gticks)
         if frag == 0:
            drink_id = res

class User:
   def __init__(self,id,username,email,aim,weight=0.0,gender='male'):
      self.id = id
      self.username = username
      self.email = email
      self.aim = aim
      self.weight = weight
      self.gender = gender

   def getName(self):
      return self.username

   def isAdmin(self):
      return False
