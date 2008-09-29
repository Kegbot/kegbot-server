from pykeg.core import Interfaces

class Relay(Interfaces.IRelay):
   def Enable(self):
      pass

   def Disable(self):
      pass

   def Status(self):
      return Interfaces.IRelay.STATUS_UNKNOWN

class Flowmeter(Interfaces.IFlowmeter):
   def GetTicks(self):
      return 0
