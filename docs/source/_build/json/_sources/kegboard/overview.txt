=================
Kegboard Overview
=================

This page describes *Kegboard*, the Arduino-based controller board for Kegbot.

What is a Kegboard?
===================

Kegboard is the most important device in a Kegbot system.  Kegboard is the
device that monitors all sensors, including the flow sensors that are essential
in any Kegbot configuration.

Kegboard is based on and designed around Arduino.  Program an Arduino with our
firmware and attach your sensors to it, and you'll have a Kegboard!

Though not required, the Kegbot Project also provides schematics for a "shield"
board that you can attach to the Arduino.  The Kegboard Shield makes it a breeze
to wire up sensors on a new Kegboard.  For more information, see
http://kegbot.org/kegboard/.

Features
========

Over the years, we've noticed different Kegbotters want different features in
their systems.  The Kegbot firmware is designed for this flexibility: We try to
support as many features and add-on devices as possible in the core firmware,
while still keeping basic functionality tight and fast for the most common
configurations. 

Standard features of Kegboard on Arduino:

* **Flow Sensing:** Two independent flow meter inputs (or 6 on Arduino Mega),
  allowing you to monitor that many individual beer taps with just one board.
* **Temperature Sensing:** Dedicated OneWire bus for reading DS1820 (DS18S20 and
  DS18B20) temperature sensors.  An unlimited number of sensors can be
  connected, allowing you to independently track keg temperature and ambient
  temperature.
* **RFID Authenticaton:** Authenticate users with cheap 125kHz RFIDs by
  connecting the optional ID-12 RFID reader.
* **OneWire Authentication:** Authenticate users with durable iButtons.
* **Relay/Value Control:** Four general purpose outputs can be used
  to toggle external devices, such as a valve to prevent unauthorized access.
  Relays are monitored by an internal watchdog.
* **Buzzer:** Kegboard will play a short melody whenever an
  authentication token is connected or swiped.
* **Extensible Serial Protocol:** If you don't want to use the
  rest of the Kegbot software, you can still use Kegboard by implementing its
  simple and extensible serial protocol in your system.  (See
  :ref:`kegboard-serial-protocol`).

All features are optional:  Kegboard's firmware will operate correctly even if
you exclude parts for a certain feature, so you can save on cost by only
building what you want.
