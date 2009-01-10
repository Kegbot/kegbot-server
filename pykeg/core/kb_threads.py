import logging
import Queue
import threading

from pykeg.core import Interfaces
from pykeg.core import kb_common
from pykeg.core import models
from pykeg.core import units

### Base kegbot thread class

class KegbotThread(threading.Thread):
  def __init__(self, name):
    threading.Thread.__init__(self)
    self.setDaemon(True)
    self.setName(name)
    self._quit = False
    self._logger = logging.getLogger(self.getName())

  def Quit(self):
    self._quit = True


### Service threads

class FlowProcessingThread(KegbotThread):
  """Worker thread that saves drinks to the backend"""
  def __init__(self, kb):
    KegbotThread.__init__(self, 'flowproc')
    self._work_queue = Queue.Queue()
    self._kegbot = kb

  def QueueFlow(self, flow):
    """Add |flow| to the queue of work to process"""
    self._work_queue.put(flow)

  def Quit(self):
    KegbotThread.Quit(self)
    # Push a special value (None) onto the workqueue to unblock it; self._quit
    # is now set and the thread will exit soon.
    self._work_queue.put(None)

  def run(self):
    while not self._quit:
      ev = self._work_queue.get()
      # Pushing None onto the work queue does nothing; this is used by Quit() to
      # unblock the blocking get (above).
      if ev is None:
        continue
      self._ProcessFlow(ev)

  def _ProcessFlow(self, flow):
    """Attempt to save a drink record and derived data for |flow|"""

    volume = flow.Volume()
    volume_ml = volume.ConvertTo.Milliliter
    if volume_ml <= kb_common.MIN_VOLUME_TO_RECORD:
      self._logger.debug('Not recording flow: volume (%i) <= '
        'MIN_VOLUME_TO_RECORD (%i)' % (volume_ml, kb_common.MIN_VOLUME_TO_RECORD))
      return

    # log the drink
    d = models.Drink(ticks=flow.Ticks(),
                     volume=volume.Amount(units.RECORD_UNIT),
                     starttime=flow.start, endtime=flow.end, user=flow.user,
                     keg=flow.keg(), status='valid')
    d.save()

    keg_id = None
    if d.keg:
      keg_id = d.keg.id
    self._logger.info('Logged drink %i user:%s keg:%s ounces:%.2f' % (
      d.id, d.user.username, keg_id, d.Volume().ConvertTo.Ounce))

    models.BAC.ProcessDrink(d)
    self._logger.info('Processed BAC for drink %i' % (d.id,))

    models.UserDrinkingSessionAssignment.RecordDrink(d)
    self._logger.info('Processed UserDrinkGroupAssignment for drink %i' % (d.id,))

    # notify listeners
    for dev in self._kegbot.IterDevicesImplementing(Interfaces.IFlowListener):
       dev.FlowEnd(flow, d)
