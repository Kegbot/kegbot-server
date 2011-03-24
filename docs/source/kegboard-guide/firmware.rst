=================
Kegboard Firmware
=================

Getting Arduino Software
========================

The Arduino project provides a free software development environment for Mac,
Windows, and Linux. It includes a basic text editor, avr microcontroller
toolchains, and many standard libraries. In short, it is everything you need to
program an arduino board.

Download the software from the `Arduino Downloads Page
<http://www.arduino.cc/en/Main/Software>`_. Packages are available for Linux,
Mac OS X, and Windows.

.. note::
  The minimum supported version is Arduino 0018.

When unzipped you will have a single directory that contains all the arduino
software. The name will be something like ``arduino-0018/`` (the version number
may be different.)

Place this directory somewhere appropriate. For Mac users, you can drag it to
your Applications folder.

Building firmware
=================

A new Arduino board includes a basic bootloader on internal flash. The board
needs to be programmed with the custom Kegboard firmware.

Binary versions of the Kegboard firmware are not generally available, so you
will need to build it yourself. This process isn't too hard; if you already have
the Arduino software installed, and you have a pykeg software tree somewhere,
then you're most of the way there.

The latest version of the Kegboard firmware is available in the **kegbot**
distribution, under the directory ``controller/kegboard/``.

The file ``kegboard.pde`` is the main source to the firmware. This file is a
C source file, using the file extension preferred by the Arduino development
tools.

Build and Flash: Command Line
-----------------------------

Building on the command line is pretty easy.  First, find your **kegbot** tree
and navigate to the firmware's home:

.. code-block:: none

  cd kegbot/controller/kegboard

Before we can build, we need to know where the arduino software is installed.
Locate the path to the ``arduino-xxxx/`` directory and export it as shown below:

.. code-block:: none

  ### Mac example
  export ARDUINO_DIR=/Applications/arduino-0018

  ### Linux example
  export ARDUINO_DIR=/usr/local/arduino-0018

Finally, perform the build:

.. code-block:: none

  make && echo SUCCESS || echo FAILURE

If the build worked, you should now have a file called
``build-cli/kegboard.hex``; this is the compiled kegboard assembly. You're
ready to upload!

To upload, run the following command:

.. code-block:: none

  make upload && echo SUCCESS || echo FAILURE


Build and Flash: GUI
--------------------

Open the file ``kegboard.pde`` in the Arduino studio. You should see a listing
of the source.

You should not need to make any changes to the source file to have a working
kegboard. (Nothing should stop you from editing this file, however; feel free to
add features and send us a patch!)

Be sure to configure the Arduino environment. In particular:

* Select the correct board type from menu :menuselection:`Tools --> Board`
* Select the corresponding serial port from the menu
  :menuselection:`Tools --> Serial Port`

To build the firmware, select the menu item
:menuselection:`Sketch --> Verify/Compile`.


Installing firmware
-------------------

To install the firmware after building, you should select the menu
:menuselection:`File --> Upload to I/O Board` in the Arduino software. Note that
it is sometimes necessary to reset the board (via the reset pushbutton on the
board) at the same time; this is because the AVR needs to be in bootloader mode
to rewrite the program.


Testing the board
=================

Kegboard includes a built-in "selftest" feature. This mode might be useful if
you'd like to test your board without hooking it up to a flowmeter; maybe you
don't have a meter, or don't want to waste precious beer testing it.

To test your board, connect pin 12 to one of the flowmeter inputs. Pin 12
generates a steady stream of pulses, similar to what a real flowmeter would do.

