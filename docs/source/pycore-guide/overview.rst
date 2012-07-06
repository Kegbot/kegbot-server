Pycore Overview
===============

Architecture
------------

.. figure:: _static/pycore-architecture.png

Pycore consists of a single master program, **Kegbot Core**, and a collection of
accessory programs which talk to it.

Kegbot Core
^^^^^^^^^^^

Kegbot Core (``kegbot_core.py``) is the central dispatcher of a Pycore system.
It is the interface between the various accessory programs and the Kegbot
Server.

Kegbot Core doesn't do anything by itself; it needs to receive sensor and
authentication information from another program.  Once it does, the core
implements all of the policy and business logic of a Kegbot system.

Main responsibilities of the Kegbot Core:

* Sums flow sensor information into discrete drink events, which are then
  reported to the Kegbot Server;
* Processes authentication packets and decides whether to start a new flow;
* Sends messages to the Kegboard daemon in order to open and close valves;
* Sends flow-related events to connected accessory daemons while a pour is in
  progress, for instance to update the UI showing on the LCD;
* Interprets temperature sensor data and sends it to the Kegbot Server.

Kegnet Local API
^^^^^^^^^^^^^^^^

All accessory daemons communicate with the Kegbot Core using the Kegnet Local
API, a TCP protocol.

While you'd usually just run all accessory daemons on the same machine, this
protocol makes it possible to distribute Kegbot responsibilities across multiple
devices.

For developers, the Kegnet Local API means you can build new types of services
for Kegbot.  For example, you can write your own program to talk to a new
authentication device and provide its data the rest of the Kegbot system.

Kegboard Daemon
^^^^^^^^^^^^^^^

The Kegboard daemon attaches to a serial port, decodes incoming Kegboard
packets, and sends them onward to the Core for interpretation.

As shown in the diagram, you can actually run multiple instances of this
program, each one talking to its own Kegboard.  This is one way to scale up your
Kegbot system if you want to support many taps, or taps in different phyiscal
locations.

Life of a Pour
--------------

Here's an example of what happens when you swipe an RFID across Kegboard's RFID
reader and start a pour:

1. The Kegboard firmware reads the RFID sensor and sends an
   :ref:`Auth Token message <auth-token-message>` across the serial port.
2. The Kegboard daemon reads the raw packet off the serial port, decodes the
   individual fields, and sends a Kegnet message up to the Core.
3. The Core looks up the token (against the Kegbot Server REST API) and decides
   whether a new flow should be started for it.
4. If the token was authorized, Core sends a message down to the Kegboard daemon
   to open the tap's valve.  (If the tap doesn't have a valve, this message does
   nothing.)
5. The user starts pouring and periodic meter reading messages are sent up to
   the Core.
6. After the flow becomes idle or the user disconnects the auth token, Core
   closes the valve and records a new drink against the server.
