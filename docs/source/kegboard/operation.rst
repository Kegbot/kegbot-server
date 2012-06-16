Theory of Operation
===================

This chapter describes the internal design of the Kegboard firmware and how it
manages connected sensors.  If you're not interested, you can safely skip to the
next chapter.

Main event loop
---------------

Kegboard's two principle responsibilities are:

* Monitors and report status and events from attached sensors.
* Accept commands from the host to enable and disable output relays.

When the board is powered, it immediately begins listening to sensors and
sending events on the serial port.  If temperature sensing is enabled, the board
also periodically polls attached sensors.  Additionally, the host can send
commands the board at any time.  (Commands and events are detailed in
:ref:`kegboard-serial-protocol`.)


Flow sensing
------------

Each flow meter is connected to one of the Arduino's external interrupt pins.
On a normal Arduino, these are pins 2 and 3.

Kegboard supports "open collector" flow meters.  These meters are typically
built using hall effect sensors.  As liquid passes through the meter, a series
of pulses is emitted on its output pin.

Every pulse emitted by the meter corresponds to the same fixed volume of fluid,
therefore volume is determined simply by counting the pulses.  The exact volume
of a pulse is a physical property of the meter; the popular Vision 2000 meter
pulses 2200 times per liter.

In the interrupt service routine for each of these pins, Kegboard increments a
counter every time there is a pulse, keeping a running total of each meter's
volume (similar to an odometer).


OneWire presence and temperature sensing
----------------------------------------

The Kegboard firmware supports two distinct OneWire (1-wire) sensor busses: the
"thermo" bus, and the "presence" bus.

The "thermo" bus supports reading Dallas/Maxim DS18B20 and 18S20 OneWire
temperature sensors.  This bus is reserved exclusively for temperature sensors;
OneWire devices not matching the DS18B20 or DS18S20 family codes will be ignored
on this bus.  Any number of sensors may be attached.

The firmware also supports a second OneWire bus, which is continuously polled
for OneWire devices.  Whenever a OneWire device such as an iButton is connected,
its unique 64-bit OneWire device ID is reported as an authentication token using
:ref:`kegboard-serial-protocol`. 


Relays
------

When a relay is enabled, Kegboard enables the corresponding output and starts a
timer.  If the host has not re-activated the relay within that timer, Kegboard
automatically deactivated the output.  This prevents prolonged relay operation
if the host crashes unexpectedly.


Piezo buzzer
------------

A low-cost piezo buzzer can be connected to the :ref:`buzzer output pin
<pin-connections>`.  When connected, Kegboard will serenade you with some sweet
tunes.

+----------------------+-------------------------------------------------------+
| Event                | Sound                                                 |
+======================+=======================================================+
| Board power up       | Short musical tune (10 notes).                        |
+----------------------+-------------------------------------------------------+
| Auth Token Added     | Three-tone "added" sound.                             |
+----------------------+-------------------------------------------------------+

