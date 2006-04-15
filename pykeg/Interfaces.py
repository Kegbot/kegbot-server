class AbstractInterfaceError(Exception):
   pass


class IRelay:
   """ Relay interface """
   STATUS_ENABLED = 1
   STATUS_DISABLED = 0
   STATUS_UNKNOWN = -1
   def Enable(self):
      raise AbstractInterfaceError

   def Disable(self):
      raise AbstractInterfaceError

   def Status(self):
      raise AbstractInterfaceError


class ITemperatureSensor:
   def SensorName(self):
      """ Return a descriptive string name """
      raise AbstractInterfaceError

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


class IAuthPresence:
   """ Interface for a presence-based (stateful) access control device """
   def PresenceCheck(self):
      """ Return a username if newly present, otherwise None """
      raise AbstractInterfaceError

   def AbsenceCheck(self):
      """ Return a username if newly absent, otherwise None """
      raise AbstractInterfaceError

