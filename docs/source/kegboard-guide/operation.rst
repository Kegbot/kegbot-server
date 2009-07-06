===================
Theory of Operation
===================

Main Event Loop
===============

The kegboard has two principle responsibilities:

* It monitors and reports status and events from attached sensors;
* It accepts commands from the host to enable and disable output devices.

When the board is powered, it immediately begins listening to sensors and
sending events on the serial port.  If temperature sensing is enabled, the board
also periodically polls attached sensors.  Additionally, the host can send
commands the board at any time.  (Commands and events are detailed in
:ref:`kegboard-serial-protocol`.)


Flow Sensing
============

The Kegboard can be used with up to two hall-effect sensor flow meters.  As
fluid passes through the meter, a sequence of pulses is emitted on the output
pin of the meter.

Every pulse emitted by the meter corresponds to the same fixed volume of fluid,
therefore volume is determined simply by counting the pulses.  (The exact volume
of a pulse is a physical property of the meter; the popular Vision 2000 meter
pulses 2200 times per liter.)

Flow pulse lines are connected to digital inputs 2 and 3 on the Ardunio board.
These pins have hardware interrupt-on-pulse capability.  When the flowmeter
pulses the input pin, an interrupt is generated in the Arduino.  The firmare's
interrupt service routine increments a counter for each interrupt, keeping a
running total of each meter's volume, similar to an odometer.


Temperature Sensing
===================

The Kegboard firmware includes support for reading the Maxim DS18B20 1-wire
temperature sensors.  Two inputs on the Arduino are designated for temperature
sensors; the software assumes there will be at most one sensor attached to each
pin.  Temperature devices are polled and reported every 5 seconds.

.. note::
  The 1-wire protocol allows multiple sensors to share a single physical bus,
  but for simplicity this is not supported in the Kegboard firmware.  Patches
  welcome :-)


Host Watchdog
=============

To safeguard against a crashed host computer, the firmware supports an optional
failsafe feature.  If the watchdog is enabled, the host must continuously ping
the board.  If the host fails to ping the board in time, all outputs are
disabled, and the special "alarm" output is enabled.

You can use the alarm output pin to trigger a relay, LED, or something else.
See :ref:`pin-connections` for information on the alarm output pin.

.. todo:: Implement this feature.


Piezo Buzzer
============

An optional piezo buzzer can be connected to the :ref:`buzzer output pin
<pin-connections>`.  If connected, Kegboard will serenade you with some sweet
tunes.

+----------------------+-------------------------------------------------------+
| Event                | Sound                                                 |
+======================+=======================================================+
| Board power up       | Short musical tune (10 notes.)                        |
+----------------------+-------------------------------------------------------+
| Watchdog alarm       | Two-tone alternating "siren" and pause (continuous).  |
+----------------------+-------------------------------------------------------+

.. todo:: Implement me.

