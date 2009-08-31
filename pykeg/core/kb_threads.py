import asyncore
import datetime
import Queue
import time

from pykeg.core import kb_common
from pykeg.core import util
from pykeg.core.net import kegnet
from pykeg.external.gflags import gflags

FLAGS = gflags.FLAGS

gflags.DEFINE_string('kegnet_server_bind_addr',
    kb_common.KEGNET_SERVER_BIND_ADDR,
    'Address that the kegnet server should bind to')

gflags.DEFINE_integer('kegnet_server_bind_port',
    kb_common.KEGNET_SERVER_BIND_PORT,
    'Port that the kegnet server should bind to',
    lower_bound=1,
    upper_bound=2**16 - 1)


### Base kegbot thread class

class CoreThread(util.KegbotThread):
  """ Convenience wrapper around a threading.Thread """
  def __init__(self, kb_env, name):
    util.KegbotThread.__init__(self, name)
    self._kb_env = kb_env

  ### Event listener methods
  def PostEvent(self, ev):
    if ev.name() == kb_common.KB_EVENT.QUIT:
      self._logger.info('got quit event, quitting')
      self.Quit()


class WatchdogThread(CoreThread):
  """Monitors all threads in _kb_env for crashes."""

  def run(self):
    fault_detected = False
    while not self._quit:
      if not fault_detected:
        for thr in self._kb_env.GetThreads():
          if not thr.hasStarted():
            continue
          if not self._quit and not thr.isAlive():
            self._logger.error('Thread %s died unexpectedly' % thr.getName())
            self._kb_env.GetEventHub().CreateAndPublishEvent(kb_common.KB_EVENT.QUIT)
            fault_detected = True
            break
      time.sleep(1.0)


class EventHubServiceThread(CoreThread):
  """Handles all event dispatches for the event hub."""

  def run(self):
    hub = self._kb_env.GetEventHub()
    while not self._quit:
      hub.DispatchNextEvent(timeout=0.5)


class FlowMonitorThread(CoreThread):
  """Watches flows for idleness."""

  def run(self):
    hub = self._kb_env.GetEventHub()
    max_idle = datetime.timedelta(seconds=10)
    while not self._quit:
      time.sleep(2.0)
      flows = self._kb_env.GetFlowManager().GetActiveFlows()
      for flow in flows:
        if flow.GetIdleTime() > max_idle:
          self._IdleOutFlow(flow)

  def _IdleOutFlow(self, flow):
    self._logger.info("Idling flow: %s" % flow)
    self._kb_env.GetEventHub().CreateAndPublishEvent(kb_common.KB_EVENT.FLOW_DEV_IDLE,
        device_name=flow.GetChannel().GetName())

class AlarmManagerThread(CoreThread):

  def run(self):
    am = self._kb_env.GetAlarmManager()
    while not self._quit:
      alarm = am.WaitForNextAlarm(1.0)
      if alarm is not None:
        self._logger.info('firing alarm: %s' % alarm)
        event = alarm.event()
        self._kb_env.GetEventHub().CreateAndPublishEvent(event)


class EventHandlerThread(CoreThread):
  """ Basic event handling thread. """
  def __init__(self, kb_env, name):
    CoreThread.__init__(self, kb_env, name)
    self._event_queue = Queue.Queue()
    self._services = set()
    self._all_event_map = {}

  def AddService(self, service):
    self._services.add(service)
    self._RefreshEventMap()

  def _RefreshEventMap(self):
    for svc in self._services:
      for event, cmd in svc.EventMap().iteritems():
        if self._all_event_map.get(event) is None:
          self._all_event_map[event] = set()
        self._all_event_map[event].add(cmd)

  def run(self):
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
    name = event.name()
    return self._all_event_map.get(name, tuple())

  def _WaitForEvent(self, timeout=0.5):
    """ Block until an event is posted, then process it """
    try:
      ev = self._event_queue.get(timeout=timeout)
      return ev
    except Queue.Empty:
      return None

  def _ProcessEvent(self, event):
    """ Execute the event callback associated with the event, if present. """
    if event.name() == kb_common.KB_EVENT.QUIT:
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
  def __init__(self, kb_env, name):
    CoreThread.__init__(self, kb_env, name)
    addr = (FLAGS.kegnet_server_bind_addr, FLAGS.kegnet_server_bind_port)
    self._server = kegnet.KegnetServer(name='kegnet', kb_env=self._kb_env,
        addr=addr)

  def run(self):
    self._logger.info("network thread started")
    self._server.StartServer()
    while not self._quit:
      asyncore.loop(timeout=0.5, count=1)
    self._server.StopServer()
