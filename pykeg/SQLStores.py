import MySQLdb
import time

class DrinkStore:
   """
   Storage of drink events.

   This class is used to store, lookup, and read individual drink events. This
   is used to abstract the backend from the keg system. This implementation
   provides SQL storage.
   """

   def __init__(self, dbinfo, minticks = 0):
      (host,user,password,db,table) = dbinfo
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

   def logFragment(self, drink_id, userid, bac, kegid, starttime, endtime, ticks, frag, grantid, grantticks):
      c = self.dbconn.cursor()
      if drink_id:
         q = ' INSERT INTO %s (id,frag,ticks,totalticks,starttime,endtime,bac,user_id,keg_id,grant_id) ' % (self.table,)
         q += 'VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)' % (drink_id,frag,grantticks,ticks,starttime,endtime,bac,userid,kegid,grantid)
      else:
         q = ' INSERT INTO %s (frag,ticks,totalticks,starttime,endtime,bac,user_id,keg_id,grant_id) ' % (self.table,)
         q += 'VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s)' % (frag,grantticks,ticks,starttime,endtime,bac,userid,kegid,grantid)

      c.execute(q)

      return c.insert_id()

   def readDrink(self, readinfo):
      """
      Find a drink, or multiple drink, with fields matching the dictionary readinfo.
      """
      pass

class UserStore:
   """
   Storage of user info.
   """
   def __init__(self, dbinfo):
      (host,user,password,db,table) = dbinfo
      self.dbconn = MySQLdb.connect(host=host,user=user,passwd=password,db=db)
      self.table = table

   def getUser(self, uid):
      """
      Get a User() object for a given uid.
      """
      c = self.dbconn.cursor()
      q = "SELECT uid,username,email,im_aim FROM %s WHERE uid='%s' LIMIT 1" % (self.table,uid)
      if c.execute(q):
         (uid,username,email,im_aim) = c.fetchone()
         return User(id = uid, username = username, email = email, aim = im_aim)
      return None

   def getUid(self, username):
      c = self.dbconn.cursor()
      q = 'SELECT uid FROM %s WHERE username="%s" LIMIT 1' % (self.table,username)
      c.execute(q)
      return c.fetchone()[0]

   def addUser(self, username, email, im_aim):
      c = self.dbconn.cursor()
      q = 'INSERT INTO %s (username, email, im_aim) VALUES ("%s", "%s", "%s")' % (self.table,username,email,im_aim)
      c.execute(q)
      return c.insert_id()

class PolicyStore:
   def __init__(self, dbinfo):
      (host,user,password,db,table) = dbinfo
      self.dbconn = MySQLdb.connect(host=host,user=user,passwd=password,db=db)
      self.table = table
   def getPolicy(self, policyid):
      c = self.dbconn.cursor()
      q = 'SELECT * FROM %s WHERE id=%s' % (self.table,policyid)
      c.execute(q)
      (id, type, unitcost, unitticks, descr) = c.fetchone()
      return Policy(id,type,unitcost,unitticks,descr)

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
   def __init__(self, dbinfo):
      (host,user,password,db,table) = dbinfo
      self.dbconn = MySQLdb.connect(host=host,user=user,passwd=password,db=db)
      self.table = table
   def getCurrentKeg(self):
      c = self.dbconn.cursor()
      q = "SELECT id FROM %s WHERE status='online' ORDER BY id DESC LIMIT 1" % (self.table,)
      c.execute(q)
      try:
         return c.fetchone()[0]
      except:
         return 0

class GrantStore:
   """
   Storage of user info.
   """
   def __init__(self, dbinfo, pstore):
      (host,user,password,db,table) = dbinfo
      self.dbconn = MySQLdb.connect(host=host,user=user,passwd=password,db=db)
      self.pstore = pstore
      self.table = table

   def getGrants(self, user):
      c = self.dbconn.cursor()
      q = 'SELECT * FROM %s WHERE foruid="%s"' % (self.table,user.id)
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

   def setPolicy(self,p):
      self.policy = p

   def incrementTicks(self,amt):
      self.total_ounces += amt

   def isExpired(self, extraticks = 0):
      if self.expiration == "none":
         return False
      elif self.expiration == "time":
         return self.exp_time < time.time()
      elif self.expiration == "ticks":
         return (extraticks + self.total_ounces) >= self.exp_ounces
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
   def __init__(self, dbinfo):
      (host,user,password,db,table) = dbinfo
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
   def __init__(self,ds,userid,kegid):
      self.drink_store = ds
      self.userid = userid
      self.kegid = kegid
      self.frags = []
      self.start = time.time()

   def addFragment(self, grantid, grant_ticks):
      last_record = self.frags[-1:]
      self.frags.append((grantid,grant_ticks))

   def done(self, final_ticks, grantid, grant_ticks):
      endtime = time.time()
      if len(self.frags) == 0:
         self.frags.append((grantid,final_ticks))
      elif self.frags[-1] == grantid:
         # replace the last record with this one
         # this could happen, say, if a grant has expired, we've logged it, and
         # a few more ticks have been recorded since
         self.frags[-1] = (grantid, grant_ticks)
      else:
         self.frags.append((grandid,grant_ticks))

      drink_id = None
      bac = 0.0
      for frag in range(0,len(self.frags)):
         (grantid, gticks) = self.frags[frag]
         res = self.drink_store.logFragment(drink_id, self.userid, bac, self.kegid, self.start, endtime, final_ticks, frag, grantid, gticks)
         if frag == 0:
            drink_id = res

      #self.drink_store.logDrink(self.userid, final_ticks, drink_start, time.time())

class User:
   def __init__(self,id,username,email,aim):
      self.id = id
      self.username = username
      self.email = email
      self.aim = aim

   def getName(self):
      return self.username

   def isAdmin(self):
      return False
