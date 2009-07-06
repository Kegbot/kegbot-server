=================
Kegboard Overview
=================

History
=======

The Kegboard is the most important device in a kegbot system; a reliable
Kegboard is essential to accurately recording all pour data. The current
Kegboard design, reflects improvements and lessons learned from earlier
attempts.

The current Kegboard design is based on the popular Arduino board.  Compared to
earlier, PIC-based designs, this board has several advantages, including:

* Onboard in FT232 serial-to-usb converter
* Completely programmable via USB; no special programmer needed
* Plenty of I/O, including two external interrupt pins (pulse counting)
* Free C compiler and large standard library
* Widely available, many cheap clones

In addition to all of the above advantages, we decided to use an Arduino (rather
than rolling our own controller board) simply because it takes a lot of hand
assembly, soldering, and debugging out of building a Kegbot.  You don't need to
be an experienced electrical engineer -- or even own a soldering iron -- to
build a working Kegboard!

Features
========

Basic features of Kegboard v3.0 include:

* Two independent flow sensing channels
* Two controllable relay outputs
* Up to two DS18S20 temperature sensors
* Standard serial protocol (:ref:`kegboard-serial-protocol`) for interfacing with
  software; supported by pykeg
* Easily built from widely-available Arduino board; no hardware programmer
  necessary


Parts List
==========


The full bill of materials (BOM) for a Kegboard setup is show below.

+-----+------------+----------------------------------------------------------+
| Qty | Cost Each  | Description                                              |
+=====+============+==========================================================+
| 1   | $35        | Arduino USB Board                                        |
+-----+------------+----------------------------------------------------------+
| 1   | $3         | USB cable                                                |
+-----+------------+----------------------------------------------------------+
| 2   | $35        | Vision-2000 Kegboard Flowmeter                           |
+-----+------------+----------------------------------------------------------+
| 2   | $5         | DS18B20 Temperature Sensor                               |
+-----+------------+----------------------------------------------------------+
| 4   | $0.25      | 10kohm Resistor (flowmeter and temperature sensor)       |
+-----+------------+----------------------------------------------------------+

A basic kegboard setup includes:

* One Arduino Decimilia (or similar) AVR microcontroller board. This board can
  be purchased for around $30 at `SparkFun <http://www.sparkfun.com>`_.
* (Optional) Up to two DS18S20 temperature sensors.


Pin Connections
===============

The following is the default Kegboard pin configuration:

* Pin 2: ``flow_0`` input
* Pin 3: ``flow_1`` input
* Pin 4: ``relay_0`` output
* Pin 5: ``relay_1`` output
* Pin 7: ``thermo_0`` 1-wire bus
* Pin 8: ``thermo_1`` 1-wire bus
* Pin 12: selftest jumper

