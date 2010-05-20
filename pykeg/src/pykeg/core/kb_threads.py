import asyncore
import datetime
import Queue
import time

import gflags

from pykeg.core import kb_common
from pykeg.core import util
from pykeg.core.net import kegnet
from pykeg.core.net import kegnet_pb2

FLAGS = gflags.FLAGS

### Base kegbot thread class

class CoreThread(util.KegbotThread):
  """ Convenience wrapper around a threading.Thread """
  def __init__(self, kb_env, name):
    util.KegbotThread.__init__(self, name)
    self._kb_env = kb_env

  ### Event listener methods
  def PostEvent(self, event):
    if isinstance(event, kegnet_pb2.QuitEvent):
      self._logger.info('got quit event, quitting')
      self.Quit()


class WatchdogThread(CoreThread):
  """Monitors all threads in _kb_env for crashes."""

  def ThreadMain(self):
    fault_detected = False
    while not self._quit:
      if not fault_detected:
        for thr in self._kb_env.GetThreads():
          if not thr.hasStarted():
            continue
          if not self._quit and not thr.isAlive():
            self._logger.error('Thread %s died unexpectedly' % thr.getName())
            event = kegnet_pb2.QuitEvent()
            self._kb_env.GetEventHub().PublishEvent(event)
            fault_detected = True
            break
      time.sleep(1.0)


class EventHubServiceThread(CoreThread):
  """Handles all event dispatches for the event hub."""

  def ThreadMain(self):
    hub = self._kb_env.GetEventHub()
    while not self._quit:
      hub.DispatchNextEvent(timeout=0.5)


class HeartbeatThread(CoreThread):
  """Generates periodic events."""

  def ThreadMain(self):
    hub = self._kb_env.GetEventHub()
    seconds = 0
    while not self._quit:
      time.sleep(1.0)
      seconds += 1
      event = kegnet_pb2.HeartbeatSecondEvent()
      hub.PublishEvent(event)
      if (seconds % 60) == 0:
        event = kegnet_pb2.HeartbeatMinuteEvent()
        hub.PublishEvent(event)
      if (seconds % 3600) == 0:
        event = kegnet_pb2.HeartbeatHourEvent()
        hub.PublishEvent(event)
        seconds = 0


class AlarmManagerThread(CoreThread):

  def ThreadMain(self):
    am = self._kb_env.GetAlarmManager()
    while not self._quit:
      alarm = am.WaitForNextAlarm(1.0)
      if alarm is not None:
        self._logger.info('firing alarm: %s' % alarm)
        event = alarm.event()
        self._kb_env.GetEventHub().PublishEvent(event)


class EventHandlerThread(CoreThread):
  """ Basic event handling thread. """
  def __init__(self, kb_env, name):
    CoreThread.__init__(self, kb_env, name)
    self._event_queue = Queue.Queue()
    self._event_handlers = set()
    self._all_event_map = {}

  def AddEventHandler(self, event_handler):
    self._event_handlers.add(event_handler)
    self._RefreshEventMap()

  def _RefreshEventMap(self):
    for svc in self._event_handlers:
      for event_type, callback_list in svc.GetEventHandlers().iteritems():
        if self._all_event_map.get(event_type) is None:
          self._all_event_map[event_type] = set()
        for cb in callback_list:
          self._all_event_map[event_type].add(cb)

  def GetStatus(self):
    lines = []
    for handler in self._event_handlers:
      handler_lines = handler.GetStatus()
      if handler_lines:
        name = handler.__class__.__name__
        lines.append('>> %s' % name)
        for h_line in handler_lines:
          lines.append('  %s' % h_line)
        lines.append('')
    return lines

  def ThreadMain(self):
    while not self._quit:
      self._Step(timeout=0.5)

  def _Step(self, timeout=0.5):
    event = self._WaitForEvent(timeout)
    if event is not None:
      self._ProcessEvent(event)
    return event

  def PostEvent(self, event):
    self._event_queue.put(event)

  def _GetCallbacksForEvent(self, event):
    return self._all_event_map.get(event.__class__, tuple())

  def _WaitForEvent(self, timeout=0.5):
    """ Block until an event is posted, then process it """
    try:
      ev = self._event_queue.get(timeout=timeout)
      return ev
    except Queue.Empty:
      return None

  def _ProcessEvent(self, event):
    """ Execute the event callback associated with the event, if present. """
    self._logger.debug('Processing event: %s' % event.DESCRIPTOR.name)
    if isinstance(event, kegnet_pb2.QuitEvent):
      self._logger.info('got quit event, quitting')
      self.Quit()
      return
    callbacks = self._GetCallbacksForEvent(event)
    for cb in callbacks:
      cb(event)

  def _FlushEvents(self):
    """ Process all events in the Queue immediately """
    while True:
      ev = self._Step(timeout=0.5)
      if ev is None:
        break


### Service threads
class NetProtocolThread(CoreThread):
  def ThreadMain(self):
    self._logger.info("network thread started")
    server = self._kb_env.GetKegnetServer()
    server.StartServer()
    while not self._quit:
      asyncore.loop(timeout=0.5, count=1)
    server.StopServer()
