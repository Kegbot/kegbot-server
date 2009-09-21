=================
Kegboard Overview
=================

History
=======

The Kegboard is the most important device in a kegbot system; a reliable
Kegboard is essential to accurately recording all pour data.

The current Kegboard is based on the popular Arduino AVR development board, and
reflects several improvements from previous designs::

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
* Documented protocol (:ref:`kegboard-serial-protocol`) for interfacing with
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

