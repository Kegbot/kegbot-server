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

   def quit(self):
      self.kegbot.quit()
