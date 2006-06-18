"""
This file defines the local hardware configuration. You may need to customize
it for your setup.

You must implemente the `configure` function; this function takes two arguments:
   'kegbot' - the Kegbot instance created by the main pykeg program
   'config' - the SQLObjectConfigParser instance

Within configure, the following calls may be used:
   kegbot.AddChannel(obj)
      Use this to add a Flow.Channel instance to the pykeg program. A
      Flow.Channel object represents a single path of beer. If your setup has
      three beer taps under pykeg control, for instance, you will instantiate
      three Flow.Channel objects in configure() and make three calls to
      kegbot.AddChannel() (one for each Flow.Channel object)

   kegbot.AddDevice(obj)
      This will add a device to the pykeg control loop. Devices are objects that
      perform work periodically; for example, in Devices/Generic, there is a
      FreezerController device that you can instantiate in the body of
      configure() and add with kegbot.AddDevice().
"""
import logging

import Auth
import Flow
import Interfaces
from Devices import Kegboard, Generic
import Publisher

import KegUI
import lcdui
import pycfz

def configure(kegbot, config):
   """
   Stock configure() function; you may need to customize this.

   This function does the following:
      - instantiates a Kegboard controller object based on the config
      - creates a Flow.Channel connected to the relay and flowmeter on the
        Kegboard object
      - creates a FreezerConversion device connected to another relay and a
        temperature sensor on the Kegboard
      - creates a ThermoLogger object, again using the same interface of the
        Kegboard object for temperature data

   If you do not have a freezer conversion, you can simply comment out the call
   to kegbot.AddDevice(freezer). Similarly, if you do not want to log
   temperatures, comment out the call to kegbot.AddDevice(thermologger)
   """

   # our kegboard controller, will be used by a few implementations
   controller = Kegboard.Kegboard(config.get('devices','flow'))
   controller.start()

   # config & install first beer channel
   channel_0 = Flow.Channel(chanid = 0,
         valve_relay = controller.i_relay_1,
         flow_meter = controller.i_flowmeter,
   )
   kegbot.AddChannel(channel_0)

   # config & install fridge control
   freezer = Generic.FreezerConversion(freezer_id = 0,
         control_relay = controller.i_relay_0,
         temp_sensor = controller.i_thermo,
         low_t = config.getfloat('thermo', 'temp_max_low'),
         high_t = config.getfloat('thermo', 'temp_max_high'),
   )
   kegbot.AddDevice(freezer)
   kegbot.AddDevice(controller.i_thermo)

   # enable temperature logging
   if config.getboolean('thermo', 'use_thermo'):
      thermologger = Generic.ThermoLogger(name='main',
            temp_sensor = controller.i_thermo
      )
      kegbot.AddDevice(thermologger)

   ### standard config stuff below (TODO: move me)

   # publisher
   # TODO: fixme, datetime cols break me
   #kegbot.AddDevice(Publisher.Publisher())

   ui = KegUI.KegUI(pycfz.Display('/dev/tts/USB1'))
   kegbot.AddDevice(ui)
   ui.start()

   # optional module: usb ibutton auth
   if config.getboolean('auth','usb_ib'):
      timeout = config.getfloat('timing','ib_refresh_timeout')
      usb_ibauth = Auth.USBIBAuth('usb', timeout, kegbot.QUIT)
      usb_ibauth.start()
      kegbot.AddDevice(usb_ibauth)

   # optional module: serial ibutton auth
   if config.getboolean('auth','serial_ib'):
      dev = config.get('devices','onewire')
      timeout = config.getfloat('timing','ib_refresh_timeout')
      serial_ibauth = Auth.SerialIBAuth(dev, timeout, kegbot.QUIT)
      serial_ibauth.start()
      kegbot.AddDevice(serial_ibauth)

