import logging

import Flow
import Interfaces
from Devices import Kegboard, Generic

def configure(kegbot, config):
   # our kegboard controller, will be used by a few implementations
   controller = Kegboard.Kegboard(config.get('devices','flow'),
         kegbot.MakeLogger('kegboard', logging.INFO))
   kegbot.controller = controller
   controller.start()

   # config & install first beer channel
   channel_1 = Flow.Channel(1,
         controller.i_relay_0,
         controller.i_flowmeter,
         kegbot.MakeLogger('channel1', logging.INFO),
   )
   kegbot.AddChannel(channel_1)

   # config & install fridge control
   freezer = Generic.FreezerConversion(1,
         controller.i_relay_1,
         controller.i_thermo,
         kegbot.MakeLogger('freezer', logging.INFO),
         config.getfloat('thermo', 'temp_max_low'),
         config.getfloat('thermo', 'temp_max_high'),
   )
   kegbot.AddDevice(freezer)

   # enable temperature logging
   thermologger = Generic.ThermoLogger('main',
         controller.i_thermo,
   )
   kegbot.AddDevice(thermologger)

