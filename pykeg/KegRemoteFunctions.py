import time

class KegRemoteFunctions:
   def __init__(self,kegbot,server):
      self.kegbot = kegbot
      self.server = server

   def getTemps(self):
      """ return a tuple of (last temperature, time recorded) """
      return (self.kegbot.last_temp,time.time())

   def isFreezerOn(self):
      if self.kegbot.freezer_status == 'on':
         return True
      else:
         return False

   def isValveOpen(self):
      return self.kegbot.flowmeter.valve_open

   def AuthUser(self, username):
      return self.kegbot.AuthUser(username)

   def StopFlow(self):
      return self.kegbot.StopFlow()

   def quit(self):
      return True # just gobble an event
