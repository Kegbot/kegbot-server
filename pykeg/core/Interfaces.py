"""
This library defines a set of interfaces used by parts of the kegbot.

In general, the interfaces defined here are nothing more than a well-known
class name and one or more function prototypes, which define the interface.

Modules wishing to advertise implementation of one or more of these interfaces
may do so by subclassing that interface. An implementation of a particular
interface must interface all functions defined by that interface.
"""

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


class IAuthDevice:
   """ Interface for an access control device """
   def AuthorizedUsers(self):
      """ Return a list of all newly authorized users """
      raise AbstractInterfaceError


class IDisplayDevice:
   """ A device that can handle alerts """
   def Activity(self):
      """ Register that some activity has occured at this instant in time """
      raise AbstractInterfaceError

   def Alert(self, message):
      """ A string message to raise """
      raise AbstractInterfaceError


class IFlowListener:
   """ Something that can listen to flow events """
   def FlowStart(self, flow):
      """ Called when a flow is started """
      raise AbstractInterfaceError

   def FlowUpdate(self, flow):
      """ Called periodically during the life of a flow """
      raise AbstractInterfaceError

   def FlowEnd(self, flow, drink):
      """ Called at the end of a flow """
      raise AbstractInterfaceError


class IThermoListener:
   """ Something interested in periodic temperature events """
   def ThermoUpdate(self, sensor, temperature):
      raise AbstractInterfaceError

class IEventListener:
  def PostEvent(self, ev):
    raise AbstractInterfaceError
