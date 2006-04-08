class AbstractInterfaceError(Exception):
   pass


class IRelay:
   def Enable(self):
      raise AbstractInterfaceError

   def Disable(self):
      raise AbstractInterfaceError

   def Status(self):
      raise AbstractInterfaceError


class ITemperatureSensor:
   def GetTemperature(self):
      """
      Get the last recorded temperature.

      Returns a tuple of (float temp_in_c, float last_reading_timestamp). If
      last_reading_timestamp is not none, then it is the approximate timestamp
      of the last temperature reading.
      """
      raise AbstractInterfaceError


class IFlowmeter:
   def GetTicks(self):
      """
      Get monotonically increasing tick value. Returns integer.
      """
      raise AbstractInterfaceError

