import logging
import time

from pykeg.core import models
import Interfaces

class FreezerConversion:
   def __init__(self, freezer_id, control_relay, temp_sensor, low_t, high_t):
      assert isinstance(control_relay, Interfaces.IRelay), \
            "control_relay must implement IRelay interface"
      assert isinstance(temp_sensor, Interfaces.ITemperatureSensor), \
            "temp_sensor must implement ITemperatureSensor interface"
      self.id = freezer_id
      self.relay = control_relay
      self.sensor = temp_sensor
      self._low_t = low_t
      self._high_t = high_t

      self.logger = logging.getLogger('freezer%s' % str(freezer_id))

   def Step(self):
      temp, temp_time = self.sensor.GetTemperature()
      if temp is None:
         return
      if temp > self.HighT():
         if self.relay.Status() == 'off':
            self.logger.info('temperature high (%.2f); enabling relay' % temp)
            self.relay.Enable()
      elif temp < self.LowT():
         if self.relay.Status() == 'on':
            self.logger.info('temperature low (%.2f); disabling relay' % temp)
            self.relay.Disable()

   def LowT(self):
      return self._low_t

   def HighT(self):
      return self._high_t


class ThermoLogger:
   LOG_INTERVAL = 30
   def __init__(self, name, temp_sensor):
      assert isinstance(temp_sensor, Interfaces.ITemperatureSensor), \
            "temp_sensor must implement ITemperatureSensor interface"
      self.name = name
      self.sensor = temp_sensor
      self._last_time = 0.0

   def Step(self):
      now = time.time()
      if now - self.LOG_INTERVAL < self._last_time:
         return

      self._last_time = now
      curr_temp, rec_time = self.sensor.GetTemperature()
      if curr_temp is not None:
         rec = models.ThermoLog(name=self.name, temp=curr_temp)
         rec.save()


class RelayLogger:
   def __init__(self, name, relay):
      assert isinstance(relay, Interfaces.IRelay), \
            "relay must implement IRelay interface"
      self.name = name
      self.relay = relay
      self._last_status = 0

   def Step(self):
      current_status = self.relay.RelayStatus()
      if self._last_status == current_status:
         return
      self._last_status = current_status
      status = {0: 'off', 1: 'on'}.get(current_status, 'unknown')
      rec = models.RelayLog(name=self.name, status=status)
      rec.save()

