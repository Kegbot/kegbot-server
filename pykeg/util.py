import time
import os
import sys

class NoOpObject:
   def NoOp(self, *args, **kwargs):
      pass

   def __getattr__(self, name):
      return self.NoOp

class TimeStats:
   """
   Provide a time-bucketed counter.

   Count() will return the number of events within this counter's window,
   defined as interval*numslots. For example, if the sum of calls to Inc() was
   15 in the last 10 seconds, then Count() will return 15.

   This works but algo needs some tuning (TODO).
   """
   def __init__(self, numslots, interval=10):
      self.interval = interval
      self.numslots = numslots
      self.Clear()

   def Clear(self):
      self.slots = []
      for i in range(self.numslots):
         self.slots.append([0,0])
      self._last_time = 0

   def _Prune(self):
      for i in range(len(self.slots)):
         (amt, when) = self.slots[i]
         if when <= (int(time.time()) - (self.interval * self.numslots)):
            self.slots[i][0] = 0

   def Inc(self, amt):
      self._Prune()
      now = int(time.time())
      slot = self.slots[self._CurrSlot(now)]
      slot[0] += amt
      slot[1] = now

   def Count(self):
      self._Prune()
      x = 0
      for amt, when in self.slots:
         x += amt
      return x

   def _CurrSlot(self, when):
      slot = when % (self.interval * self.numslots)
      slot = slot / self.interval
      return slot

def daemonize():
   # Fork once
   if os.fork() != 0:
      os._exit(0)
   os.setsid()  # Create new session
   # Fork twice
   if os.fork() != 0:
      os._exit(0)
   #os.chdir("/")
   os.umask(0)

   os.close(sys.__stdin__.fileno())
   os.close(sys.__stdout__.fileno())
   os.close(sys.__stderr__.fileno())

   os.open('/dev/null', os.O_RDONLY)
   os.open('/dev/null', os.O_RDWR)
   os.open('/dev/null', os.O_RDWR)

def instantBAC(gender, weight, alcpct, ounces):
   # calculate weight in metric KGs
   if weight <= 0:
      return 0.0

   kg_weight = weight/2.2046

   # gender based water-weight
   if gender == 'male':
         waterp = 0.58
   else:
      waterp = 0.49

   # find total body water (in milliliters)
   bodywater = kg_weight * waterp * 1000.0

   # weight in grams of 1 oz alcohol
   alcweight = 29.57*0.79;

   # rate of alcohol per subject's total body water
   alc_per_body_ml = alcweight/bodywater

   # find alcohol concentration in blood (80.6% water)
   alc_per_blood_ml = alc_per_body_ml * 0.806

   # switch to "grams percent"
   grams_pct = alc_per_blood_ml * 100.0

   # determine how much we've really consumed
   alc_consumed = ounces * (alcpct/100.0)
   instant_bac = alc_consumed * grams_pct

   return instant_bac

def decomposeBAC(bac,seconds_ago,rate=0.02):
   return max(0.0,bac - (rate * (seconds_ago/3600.0)))

def toF(t):
   return ((9.0/5.0)*t) + 32

def MaxVolume(grants):
   """ return maximum volume pourable, in range [0, inf) """
   tot = 0
   for g in grants:
      vol = g.AvailableVolume()
      if vol == -1:
         return -1
      elif vol == 0:
         continue
      else:
         tot += vol
   return tot

def boolstr(s):
   if s.lower()[0] == 'y':
      return 1
   elif s.lower()[0] == 'n':
      return 0
   else:
      return None

def prompt(msg, default='', cast=str):
   ret = None
   while ret is None:
      ret = raw_input('%s [%s]: ' % (msg, default)).strip()
      if ret == '':
         ret = default
      try:
         ret = cast(ret)
      except:
         ret = None
   return ret
