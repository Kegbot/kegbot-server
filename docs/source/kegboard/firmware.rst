=================
Kegboard Firmware
=================

Install Arduino software
========================

The Arduino project provides a free software development environment for Mac,
Windows, and Linux. It includes a basic text editor, avr microcontroller
toolchains, and many standard libraries. In short, it is everything you need to
program an arduino board.

Download the software from the `Arduino Downloads Page
<http://www.arduino.cc/en/Main/Software>`_. Packages are available for Linux,
Mac OS X, and Windows.

.. note::
  The recommended version is Arduino 1.0.

When unzipped you will have a single directory that contains all the arduino
software. The name will be something like ``arduino-1.0/`` (the version number
will be different for previous versions.)

Place this directory somewhere appropriate. For Mac users, you can drag it to
your Applications folder.

Compile and flash the firmware
==============================

A new Arduino board includes a basic bootloader on internal flash. The board
needs to be programmed with the custom Kegboard firmware.

Binary versions of the Kegboard firmware are not provided, so you need to build
it yourself. This process isn't too hard.  If you already have the Arduino
software installed, and you have a clone of the kegboard repository somewhere,
you're most of the way there

The latest version of the Kegboard firmware is available in the **kegboard**
distribution, under the directory ``src/kegboard/``.

You can also download the entire kegboard github repository as a zip file:
`Download kegboard repository <https://github.com/Kegbot/kegboard/zipball/master>`_.

The file ``kegboard.ino`` is the main source to the firmware. This file is a
C source file, using the file extension preferred by the Arduino development
tools.

Compile
-------

Open the file ``kegboard.ino`` in the Arduino studio application. You should see
a listing of the source.  You do not need to make any changes to the source.

Next, configure the Arduino environment to match your Arduino. In particular:

* Select the correct board type from menu :menuselection:`Tools --> Board`
* Select the serial port it is attached to from the menu
  :menuselection:`Tools --> Serial Port`

You now be ready to build the firmware. Select the menu item
:menuselection:`Sketch --> Verify/Compile`.


Flash
-----

To install the firmware, should select the menu
:menuselection:`File --> Upload to I/O Board` in the Arduino software.  The
firmware will be uploaded to you device.

Depending on your hardware, it may be necessary to reset the board using the
reset pushbutton when starting the upload.


Test the Kegboard
=================

The Pycore package includes two programs to monitor and test the Kegboard.  See
:ref:`pycore-guide` for install instructions.

Both command-line programs support various flags; see **--help**.

kegboard-monitor.py
-------------------

This program monitors the serial port given with the command line flag
**--kegboard_device**, printing any Kegboard packets it sees.

kegboard-tester.py
------------------

This program cycles through each relay on the Kegboard, opening and closing it.

Test pin
--------

To simulate a flow meter, you can connect Pin 12 to either of the two flow meter
pins with a short jumper wire.  This pin continuously outputs a slow stream of
pulses, much like a flow meter would do.
