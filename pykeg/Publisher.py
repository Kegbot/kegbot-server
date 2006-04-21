"""
XML-RPC Event Publisher for pykeg.

Pykeg can publish certain types of events to multiple XML-RPC listeners. This
is a publish-only interface; subscription to event streams must be done out of
band (ie, in the global config).

Remote clients of this data should immediately return after an event is
published. Any returned data will be discarded (TODO: return HANGUP?)

Several types of events are currently supported:

   KegbotEvent_Drink
      Published to report a drink, typically immediately after it has been
      poured.

      Fields:
         uint     id          // drink id
         uint     kegid       // keg id
         unit     userid      // drinker id
         string   username    // descriptive drinker name
         string   kegname     // descriptive keg name
         float    volume      // volume in mL
         datetime endtime     // time drink poured

   KegbotEvent_FlowStart
      Published when the kegbot has started a new flow.

      Fields:
         unit     channel     // channel on which the flow was started
         unit     userid      // id of user for whom flow was started
         uint     kegid       // id of keg on which flow was started
         string   username    // descriptive drinker name
         string   kegname     // descriptive keg name

   KegbotEvent_FlowUpdate
      Published when the kegbot has started a new flow.

      Fields:
         unit     channel     // channel on which the flow was started
         unit     userid      // id of user for whom flow was started
         uint     kegid       // id of keg on which flow was started
         string   username    // descriptive drinker name
         string   kegname     // descriptive keg name
         float    volume      // in mL

   // FlowEnd is currently not defined

   KegbotEvent_PeriodicTemperature
      Periodic reporting of the current temperature, if such data is available.

      Fields:
         string   name        // sensor name
         float    temp        // in C

   KegbotEvent_AlarmTemperature
      Published periodically while temperature is in alarm state, if such data
      is available.

      Fields:
         string   name        // sensor name
         float    temp        // in C
"""

import logging
import socket
import time
import units
import xmlrpclib


class Publisher:
   def __init__(self):
      self._subscribers = {}
      self.logger = logging.getLogger('publisher')
      self.logger.info('Event publisher started')

      self._last_publish = {}

      # for now, add localhost to all events. eventually this should be
      # in the global config
      self.AddSubscriber('Drink', 'http://localhost:9091/')
      self.AddSubscriber('FlowStart', 'http://localhost:9091/')
      self.AddSubscriber('FlowUpdate', 'http://localhost:9091/')
      self.AddSubscriber('PeriodicTemperature', 'http://localhost:9091/')
      self.AddSubscriber('AlarmTemperature', 'http://localhost:9091/')

   def AddSubscriber(self, event, addr):
      if not self._subscribers.has_key(event):
         self._subscribers[event] = list()
      subscriber = (addr, xmlrpclib.ServerProxy(addr))
      self._subscribers[event].append(subscriber)

   def GetSubscribers(self, event):
      return self._subscribers.get(event, list())

   # TODO: make me publish events to a worker thread (so callee won't block)
   def _DoPublish(self, event, args):
      self._last_publish[event] = time.time()
      func_name = 'KegbotEvent_' + event
      for addr, server in self.GetSubscribers(event):
         self.logger.info('Publishing %s to %s' % (event, addr))
         try:
            apply(getattr(server, func_name), args)
         except socket.error, e:
            self.logger.error('Error contacting %s: %s' % (addr, e))
         except xmlrpclib.Fault, e:
            self.logger.error('Fault encountered in XML-RPC with %s: %s' % (addr, e))

   ### pykeg publishing calls

   def PublishDrinkEvent(self, drink):
      args = (drink.id, drink.keg.id, drink.user.id, drink.user.username,
            drink.keg.description, drink.volume/units.MILLILITER,
            drink.endtime)
      self._DoPublish('Drink', args)

   def PublishFlowStart(self, flow):
      args = (flow.channel.chanid, flow.user.id, flow.channel.Keg().id,
            flow.user.username, flow.channel.Keg().description)
      self._DoPublish('FlowStart', args)

   def PublishFlowUpdate(self, flow):
      args = (flow.channel.chanid, flow.user.id, flow.channel.Keg().id,
            flow.user.username, flow.channel.Keg().description,
            units.ticks_to_volunits(flow.Ticks()))
      self._DoPublish('FlowUpdate', args)

   def PublishTemperature(self, name, temp):
      if time.time() - self._last_publish.get('PeriodicTemperature', 0) < 30:
         return
      args = (name, temp)
      self._DoPublish('PeriodicTemperature', args)

      # TODO: publish alarm temperature here if necessary
      #self._DoPublish('AlarmTemperature', args)


