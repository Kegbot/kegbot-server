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

"""Kegbot service implementations.

This module contains KegbotService implementations (or "services").  Generally,
a service implementation is the glue between the core EventHub, and an
underlying manager implementation (which knows nothing of the EventHub).
"""

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

  def _CreateAndPublishEvent(self, event_name, **kwargs):
    """Convenience alias for EventHub.CreateAndPublishEvent"""
    self._kb_env.GetEventHub().CreateAndPublishEvent(event_name, **kwargs)


### Implementations

class DrinkDatabaseService(KegbotService):
  """ Saves drinks to the database and performs postprocessing """

  def _LoadEventMap(self):
    ret = {
        KB_EVENT.FLOW_ENDED: self._HandleFlowCompleteEvent,
        KB_EVENT.DRINK_CREATED : self._HandleDrinkCreatedEvent,
    }
    return ret

  def _HandleFlowCompleteEvent(self, ev):
    """Attempt to save a drink record and derived data for |flow|"""
    self._logger.info('Flow completed')
    flow = ev.flow

    ticks = flow.GetVolume()
    volume_native = units.Quantity(ticks, units.UNITS.KbMeterTick)
    volume_ml = volume_native.ConvertTo.Milliliter

    if volume_ml <= kb_common.MIN_VOLUME_TO_RECORD:
      self._logger.info('Not recording flow: volume (%i) <= '
        'MIN_VOLUME_TO_RECORD (%i)' % (volume_ml, kb_common.MIN_VOLUME_TO_RECORD))
      return

    keg = None
    user = flow.GetUser()
    if user is None:
      user = self._kb_env.GetBackend().GetDefaultUser()
      self._logger.info('User unknown, using default: %s' % (user.username,))

    # log the drink
    d = models.Drink(ticks=int(ticks),
                     volume=volume_native.Amount(units.RECORD_UNIT),
                     starttime=flow.GetStartTime(), endtime=flow.GetEndTime(), user=user,
                     keg=keg, status='valid')
    d.save()

    keg_id = None
    if d.keg:
      keg_id = d.keg.id

    self._logger.info('Logged drink %i user=%s keg=%s ounces=%s ticks=%i' % (
      d.id, d.user.username, keg_id, d.Volume().ConvertTo.Ounce,
      int(d.Volume())))

    # notify listeners
    self._CreateAndPublishEvent(KB_EVENT.DRINK_CREATED, drink=d, flow=flow)

  def _HandleDrinkCreatedEvent(self, ev):
    drink = ev.drink

    models.BAC.ProcessDrink(drink)
    self._logger.info('Processed BAC for drink %i' % (drink.id,))

    models.UserDrinkingSessionAssignment.RecordDrink(drink)
    self._logger.info('Processed UserDrinkGroupAssignment for drink %i' % (drink.id,))


class FlowManagerService(KegbotService):
  """ Bridges a FlowManager to the KegbotCore event hub."""

  def __init__(self, name, kb_env):
    super(FlowManagerService, self).__init__(name, kb_env)
    self._flow_manager = self._kb_env.GetFlowManager()

  def _LoadEventMap(self):
    ret = {
        KB_EVENT.FLOW_DEV_ACTIVITY : self._HandleFlowActivityEvent,
        KB_EVENT.FLOW_DEV_IDLE: self._HandleFlowIdleEvent,
        KB_EVENT.END_FLOW: self._HandleFlowEndFlowEvent,
    }
    return ret

  def _HandleFlowActivityEvent(self, ev):
    """Handles the FLOW_DEV_ACTIVITY event.

    The handler accquires the FlowManager, and calls FlowUpdate.  This may
    result in one of three outcomes:
      - New flow created. A FLOW_STARTED event is emitted, followed by a
        FLOW_UPDATE event.
      - Existing flow updated. A FLOW_UPDATE event is emitted.
      - Update refused.  The channel is unknown by the FlowManager.  No events
        are emitted.
    """
    flow_mgr = self._kb_env.GetFlowManager()
    flow_instance, is_new = flow_mgr.UpdateFlow(ev.device_name,
        ev.meter_reading)

  def _HandleFlowIdleEvent(self, ev):
    flow_mgr = self._kb_env.GetFlowManager()
    flow = flow_mgr.EndFlow(ev.device_name)
    self._CreateAndPublishEvent(KB_EVENT.FLOW_ENDED, flow=flow)

  def _HandleFlowEndFlowEvent(self, ev):
    flow_mgr = self._kb_env.GetFlowManager()
    flow = flow_mgr.EndFlow(ev.device_name)
    self._CreateAndPublishEvent(KB_EVENT.FLOW_ENDED, flow=flow)

