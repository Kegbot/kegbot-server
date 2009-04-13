# Copyright 2008 Mike Wakerly <opensource@hoho.com>
#
# This file is part of the Pykeg package of the Kegbot project.
# For more information on Pykeg or Kegbot, see http://kegbot.org/
#
# Pykeg is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 2 of the License, or
# (at your option) any later version.
#
# Pykeg is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Pykeg.  If not, see <http://www.gnu.org/licenses/>.

"""Kegbot service implementations."""

import logging

from pykeg.core import event
from pykeg.core import kb_common
from pykeg.core import manager
from pykeg.core import models
from pykeg.core import units

KB_EVENT = kb_common.KB_EVENT

### Base class

class KegbotService(object):
  def __init__(self, name, kb_env):
    self._name = name
    self._logger = logging.getLogger(self._name)
    self._kb_env = kb_env
    self._event_map = {
        KB_EVENT.QUIT : self._HandleQuitEvent,
    }
    self._event_map.update(self._LoadEventMap())

  def _LoadEventMap(self):
    """ Return a mapping of event names to callbacks """
    return {}

  def _SetEventMap(self, d):
    """ Set the event mapping to the given dict """
    self._event_map = d

  def _HandleQuitEvent(self, event):
    self._quit = True

  def EventMap(self):
    return self._event_map


### Implementations

class DrinkDatabaseService(KegbotService):
  """ Saves drinks to the database and performs postprocessing """

  def _LoadEventMap(self):
    ret = {
        KB_EVENT.FLOW_COMPLETE : self._HandleFlowCompleteEvent,
        KB_EVENT.DRINK_CREATED : self._HandleDrinkCreatedEvent,
    }
    return ret

  def _HandleFlowCompleteEvent(self, ev):
    """Attempt to save a drink record and derived data for |flow|"""
    self._logger.info('Flow completed')
    flow = ev.flow

    volume = flow.GetVolume()
    volume_ml = volume.ConvertTo.Milliliter
    if volume_ml <= kb_common.MIN_VOLUME_TO_RECORD:
      self._logger.info('Not recording flow: volume (%i) <= '
        'MIN_VOLUME_TO_RECORD (%i)' % (volume_ml, kb_common.MIN_VOLUME_TO_RECORD))
      return

    keg = flow.GetKeg()
    user = flow.GetUser()
    if user is None:
      user = self._kb_env.GetBackend().GetDefaultUser()
      self._logger.info('User unknown, using default: %s' % (user.username,))

    # log the drink
    d = models.Drink(ticks=int(volume),
                     volume=volume.Amount(units.RECORD_UNIT),
                     starttime=flow.GetStartTime(), endtime=flow.GetEndTime(), user=user,
                     keg=keg, status='valid')
    d.save()

    keg_id = None
    if d.keg:
      keg_id = d.keg.id
    self._logger.info('Logged drink %i user:%s keg:%s ounces:%.2f' % (
      d.id, d.user.username, keg_id, d.Volume().ConvertTo.Ounce))

    # notify listeners
    ev = event.Event(kb_common.KB_EVENT.DRINK_CREATED, drink=d, flow=flow)
    self._kb_env.GetEventHub().PublishEvent(ev)

  def _HandleDrinkCreatedEvent(self, ev):
    drink = ev.drink

    models.BAC.ProcessDrink(drink)
    self._logger.info('Processed BAC for drink %i' % (drink.id,))

    models.UserDrinkingSessionAssignment.RecordDrink(drink)
    self._logger.info('Processed UserDrinkGroupAssignment for drink %i' % (drink.id,))


class FlowManagerService(KegbotService):
  """ Bridges a FlowManager to the KegbotCore event hub. """

  def __init__(self, name, kb_env):
    super(FlowManagerService, self).__init__(name, kb_env)
    self._flow_manager = self._kb_env.GetFlowManager()

  def _LoadEventMap(self):
    ret = {
        KB_EVENT.FLOW_DEV_ACTIVITY : self._HandleFlowDevActivityEvent,
        KB_EVENT.FLOW_DEV_IDLE : self._HandleFlowDevIdleEvent,
        KB_EVENT.FLOW_END: self._HandleFlowEndEvent,
    }
    return ret

  def _HandleFlowDevActivityEvent(self, ev):
    self._logger.debug('Handling activity event')
    try:
      flow, is_new = self._flow_manager.UpdateDeviceReading(name=ev.device_name,
          value=ev.meter_reading)
      self._logger.debug('Got flow %s %s' % (is_new, flow))
    except (manager.FlowManagerError, e):
      self._logger.error('Activity error: %s' % e)
      return

    if is_new:
      self._kb_env.GetEventHub().CreateAndPublishEvent(kb_common.KB_EVENT.FLOW_START,
          flow=flow)
    self._kb_env.GetEventHub().CreateAndPublishEvent(kb_common.KB_EVENT.FLOW_UPDATE,
        flow=flow)


  def _HandleFlowDevIdleEvent(self, ev):
    pass

  def _HandleFlowEndEvent(self, ev):
    flow = self._flow_manager.EndFlow(name=ev.device_name)
    if not flow:
      return
    ev = event.Event(kb_common.KB_EVENT.FLOW_COMPLETE, flow=flow)
    self._kb_env.GetEventHub().PublishEvent(ev)

