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
pulses the input pin, an interrupt is generated in the Arduino.  The firmware's
interrupt service routine increments a counter for each interrupt, keeping a
running total of each meter's volume, similar to an odometer.


OneWire Presence and Temperature Sensing
========================================

The Kegboard firmware is configured to support two separate OneWire (1-wire)
busses: the "thermo" bus, and the "presence" bus.  Use of these features is
optional.

The "thermo" bus supports reading Dallas/Maxim DS18B20 OneWire temperature
sensors.  This bus is reserved exclusively for temperature sensors; OneWire
devices not matching the DS18B20 or DS18S20 family codes will be ignored on this
bus.  Any number of sensors may be attached.

The firmware also supports a second OneWire bus, which is continuously polled
for OneWire devices.  The OneWire device IDs seen on this bus are reported in a
:ref:`kegboard-serial-protocol` message. This allows the Kegboard to act as
an iButton reader authentication device.


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

