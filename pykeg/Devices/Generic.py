import time

import Backend

class FreezerConversion:
   def __init__(self, freezer_id, control_relay, temp_sensor, logger,
         low_t, high_t):
      self.id = freezer_id
      self.relay = control_relay
      self.sensor = temp_sensor
      self.logger = logger

      self._low_t = low_t
      self._high_t = high_t

   def Step(self):
      temp = self.sensor.GetTemperature()
      if temp is None:
         return
      if temp > self.HighT():
         if self.relay.Status() == 'off':
            self.logger.info('temperature high (%.2f); enabling relay' % temp)
            self.relay.Enable()
      elif temp < self.LowT():
         if self.relay.Status() == 'on':
            self.logger.info('temperature low (%.2f); disbling relay' % temp)
            self.relay.Disable()

   def LowT(self):
      return self._low_t

   def HighT(self):
      return self._high_t


class ThermoLogger:
   LOG_INTERVAL = 30
   def __init__(self, name, sensor):
      self.name = name
      self.sensor = sensor
      self._last_time = 0.0

   def Step(self):
      now = time.time()
      if now - self.LOG_INTERVAL < self._last_time:
         return

      self._last_time = now
      curr_temp = self.sensor.GetTemperature()
      rec = Backend.ThermoLog(name = self.name, temp = curr_temp)
      rec.syncUpdate()

