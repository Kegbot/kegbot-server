import MySQLdb

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

   def writeDrink(self, ticks, start, end, userid):
      """
      Record a drink event.

      Save the ticks, start time, end time, and user id that are passed in with
      a drink event.
      """
      c = self.dbconn.cursor()

      # only record ticks matching our minim threshhold
      if ticks >= self.minticks:
         c.execute(""" INSERT INTO %s (ticks, starttime, endtime, user_id) VALUES (%s,%s,%s,%s) """, (self.table, ticks, start, end, userid))

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
         return User(username = username, email = email, aim = im_aim)
      return None

   def addUser(self, username, email, im_aim):
      c = self.dbconn.cursor()
      q = 'INSERT INTO %s (username, email, im_aim) VALUES ("%s", "%s", "%s")' % (self.table,username,email,im_aim)
      print q
      c.execute(q)
      return c.insert_id()

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

class User:
   def __init__(self,username,email,aim):
      self.username = username
      self.email = email
      self.aim = aim

   def getName(self):
      return self.username

   def isAdmin(self):
      return False
