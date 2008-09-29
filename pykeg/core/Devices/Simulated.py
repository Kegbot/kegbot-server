import time
import random

import Interfaces

class SpinningFlowmeter(Interfaces.IFlowmeter):
   """ A flowmeter that is constantly ticking away (for debugging) """
   def __init__(self):
      self.ticks = 0
   def GetTicks(self):
      self.ticks += random.randrange(5)
      return self.ticks
