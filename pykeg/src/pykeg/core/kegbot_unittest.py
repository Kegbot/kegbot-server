#!/usr/bin/env python

"""Unittest for kegbot module"""

import commands
import datetime
import time
import logging
import socket
import unittest
import kegbot

from django.test import TestCase

from pykeg.core import defaults
from pykeg.core import event
from pykeg.core import models
from pykeg.core import kb_common
from pykeg.core import units
from pykeg.core.net import kegnet
from pykeg.core.net import kegnet_pb2

from pykeg.beerdb import models as bdb_models

LOGGER = logging.getLogger('unittest')

class KegbotTestCase(TestCase):
  def setUp(self):
    del logging.root.handlers[:]
    defaults.set_defaults()
    #defaults.gentestdata()

    models.Drink.objects.all().delete()

    self.keg_size = models.KegSize.objects.create(name='10Liter Keg',
        volume_ml=units.Quantity(10000))

    self.beer_style = bdb_models.BeerStyle.objects.create(name='test style')
    self.brewer = bdb_models.Brewer.objects.create(name='test brewer')
    self.beer_type = bdb_models.BeerType.objects.create(name='test beer type',
        brewer=self.brewer, style=self.beer_style, calories_oz=10.0,
        carbs_oz=2.0, abv=5.0)

    self.test_keg = models.Keg.objects.create(type=self.beer_type,
        size=self.keg_size, status='online', description='None')

    self.test_tap = models.KegTap.objects.create(name='Test Tap',
        meter_name='test_meter_name', ml_per_tick=(1000.0/2200.0),
        current_keg=self.test_keg)

    self.kegbot = kegbot.KegbotCoreApp()
    self.env = self.kegbot._env

    self.test_user = models.User.objects.create(username='tester')
    self.test_token = models.AuthenticationToken.objects.create(
        auth_device='core.onewire', token_value='feedfacedeadbeef',
        user=self.test_user)

    self.test_user_2 = models.User.objects.create(username='tester_2')
    self.test_token_2 = models.AuthenticationToken.objects.create(
        auth_device='core.onewire', token_value='baadcafebeeff00d',
        user=self.test_user_2)
    kb_common.AUTH_TOKEN_MAX_IDLE['core.onewire'] = 2

    # Kill the kegbot flow processing thread so we can single step it.
    self.service_thread = self.env._service_thread
    self.env._threads.remove(self.service_thread)

    self.kegbot._Setup()
    self.kegbot._StartThreads()

    self.client = kegnet.KegnetClient()
    while True:
      if self.client.Reconnect():
        break

  def tearDown(self):
    for thr in self.env.GetThreads():
      self.assert_(thr.isAlive(), "thread %s died unexpectedly" % thr.getName())
    self.kegbot.Quit()
    for thr in self.env.GetThreads():
      self.assert_(not thr.isAlive(), "thread %s stuck" % thr.getName())
    del self.kegbot
    del self.env

  def testSimpleFlow(self):
    # Synthesize a 2200-tick flow. The FlowManager should zero on the initial
    # reading of 1000.
    meter_name = self.test_tap.meter_name
    self.client.SendFlowStart(meter_name)
    self.client.SendMeterUpdate(meter_name, 1000)
    count = 0
    while count < 2200:
      count += 100
      self.client.SendMeterUpdate(meter_name, 1000+count)

    self.client.SendFlowStop(meter_name)
    self.service_thread._FlushEvents()

    drinks = self.test_keg.drink_set.all()
    self.assertEquals(len(drinks), 1)
    last_drink = drinks[0]

    LOGGER.info('last drink: %s' % (last_drink,))
    self.assertEquals(last_drink.ticks, 2200)

    self.assertEquals(last_drink.keg, self.test_keg)

    guest_user = self.env._backend.GetDefaultUser()
    self.assertEquals(last_drink.user, guest_user)

  def testAuthenticatedFlow(self):
    meter_name = self.test_tap.meter_name

    # Start a flow by pouring a few ticks.
    self.client.SendMeterUpdate(meter_name, 100)
    self.client.SendMeterUpdate(meter_name, 200)
    time.sleep(1.0)
    self.service_thread._FlushEvents()

    # The flow should be anonymous, since no user is authenticated.
    flow_mgr = self.env.GetFlowManager()
    flows = flow_mgr.GetActiveFlows()
    self.assertEquals(len(flows), 1)
    flow = flows[0]
    self.assertEquals(flow.GetUser(), None)

    # Now authenticate the user.
    # TODO(mikey): should use tap name rather than meter name.
    self.client.SendAuthTokenAdd(self.test_tap.meter_name,
        auth_device_name=self.test_token.auth_device,
        token_value=self.test_token.token_value)
    time.sleep(1.0) # TODO(mikey): need a synchronous wait
    self.service_thread._FlushEvents()
    self.assertEquals(flow.GetUser(), self.test_user)

    # If another user comes along, he takes over the flow.
    self.client.SendAuthTokenAdd(self.test_tap.meter_name,
        auth_device_name=self.test_token_2.auth_device,
        token_value=self.test_token_2.token_value)
    time.sleep(1.0) # TODO(mikey): need a synchronous wait
    self.service_thread._FlushEvents()

    flows = flow_mgr.GetActiveFlows()
    self.assertEquals(len(flows), 1)
    flow = flows[0]
    self.assertEquals(flow.GetUser(), self.test_user_2)

    self.client.SendMeterUpdate(meter_name, 300)
    time.sleep(1.0) # TODO(mikey): need a synchronous wait
    self.service_thread._FlushEvents()
    self.client.SendFlowStop(meter_name)
    time.sleep(1.0) # TODO(mikey): need a synchronous wait
    self.service_thread._FlushEvents()

    drinks = self.test_keg.drink_set.all().order_by('id')
    self.assertEquals(len(drinks), 2)
    self.assertEquals(drinks[0].user, self.test_user)
    self.assertEquals(drinks[1].user, self.test_user_2)

  def testIdleFlow(self):
    meter_name = self.test_tap.meter_name
    self.client.SendFlowStart(meter_name)
    self.client.SendMeterUpdate(meter_name, 0)
    self.client.SendMeterUpdate(meter_name, 100)
    time.sleep(1.0)
    self.service_thread._FlushEvents()

    flows = self.env.GetFlowManager().GetActiveFlows()
    self.assertEquals(len(flows), 1)

    # Rewind the flow activity clocks to simulate idleness.
    flows[0]._start_time -= datetime.timedelta(minutes=10)
    flows[0]._end_time = flows[0]._start_time

    # Wait for the heartbeat event to kick in.
    time.sleep(1.0)
    self.service_thread._FlushEvents()

    # Verify that the flow has been ended.
    flows = self.env.GetFlowManager().GetActiveFlows()
    self.assertEquals(len(flows), 0)

  def testTokenDebounce(self):
    meter_name = self.test_tap.meter_name
    self.client.SendFlowStart(meter_name)
    self.client.SendMeterUpdate(meter_name, 0)
    self.client.SendMeterUpdate(meter_name, 100)
    time.sleep(1.0)
    self.service_thread._FlushEvents()

    self.client.SendAuthTokenAdd(self.test_tap.meter_name,
        auth_device_name=self.test_token.auth_device,
        token_value=self.test_token.token_value)
    time.sleep(1.0) # TODO(mikey): need a synchronous wait
    self.service_thread._FlushEvents()

    flows = self.env.GetFlowManager().GetActiveFlows()
    self.assertEquals(len(flows), 1)
    flow = flows[0]
    self.assertEquals(flow.GetUser(), self.test_user)
    original_flow_id = flow.GetId()

    LOGGER.info('Removing token...')
    self.client.SendAuthTokenRemove(self.test_tap.meter_name,
        auth_device_name=self.test_token.auth_device,
        token_value=self.test_token.token_value)
    time.sleep(0.5)
    self.service_thread._FlushEvents()

    # The flow should still be active.
    flows = self.env.GetFlowManager().GetActiveFlows()
    self.assertEquals(len(flows), 1)
    flow = flows[0]
    self.assertEquals(flow.GetId(), original_flow_id)
    self.assertEquals(flow.GetState(), kegnet_pb2.FlowUpdate.ACTIVE)

    # Re-add the token; should be unchanged.
    self.client.SendAuthTokenAdd(self.test_tap.meter_name,
        auth_device_name=self.test_token.auth_device,
        token_value=self.test_token.token_value)
    time.sleep(0.5)
    self.service_thread._FlushEvents()

    # No change in flow
    flows = self.env.GetFlowManager().GetActiveFlows()
    self.assertEquals(len(flows), 1)
    flow = flows[0]
    self.assertEquals(flow.GetId(), original_flow_id)
    self.assertEquals(flow.GetState(), kegnet_pb2.FlowUpdate.ACTIVE)

    # Idle out. TODO(mikey): shift clock instead of sleeping.
    time.sleep(2.5)
    self.service_thread._FlushEvents()
    flows = self.env.GetFlowManager().GetActiveFlows()
    self.assertEquals(len(flows), 0)

if __name__ == '__main__':
  unittest.main()
