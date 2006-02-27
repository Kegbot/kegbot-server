import os

class NoOpObject:
   def NoOp(self, *args, **kwargs):
      pass

   def __getattr__(self, name):
      return self.NoOp

def daemonize():
   # Fork once
   if os.fork() != 0:
      os._exit(0)
   os.setsid()  # Create new session
   # Fork twice
   if os.fork() != 0:
      os._exit(0)
   os.chdir("/")
   os.umask(0)

   try:
      maxfd = os.sysconf("SC_OPEN_MAX")
   except (AttributeError, ValueError):
      maxfd = 256

   for fd in range(0, maxfd):
      try:
         os.close(fd)
      except OSError:
         pass

   os.open('/dev/null', os.O_RDONLY)
   os.open('/dev/null', os.O_RDWR)
   os.open('/dev/null', os.O_RDWR)

def instantBAC(user, keg, ounces):
   # calculate weight in metric KGs
   if user.weight <= 0:
      return 0.0

   kg_weight = user.weight/2.2046

   # gender based water-weight
   if user.gender == 'male':
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
   alc_consumed = ounces * (keg.alccontent/100.0)
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

