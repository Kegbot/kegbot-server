.. _running-kegbot:

Running the Kegbot Core
=======================

With your webserver online, you're now ready to start sending drink and sensor
data to it.  To do this, you must run the *Kegbot Core*.

The "core" itself is actually separated into two programs:

* ``kegbot_core.py``, the core kegbot daemon.  It listens for sensor data on a
  local network interface, and reports it to the Kegweb service.
* ``kegboard_daemon.py``, the program that talks to your kegboard.  When it
  receives sensor data, it reports it to kegbot_core.


Starting ``kegbot_core.py``
---------------------------

To launch kegbot_core, you will need to know two values:

* ``api_url``: the URL of your kegweb's API address, up to and including
  ``/api/``.
* ``api_key``: your secret API key, visible on the *Account* page.

Here's an example of successfully launching the core::

  % kegbot_core.py --api_url=http://localhost:8000/api/ --api_key=100000010457a3747caf2040b061851074517573
  2011-12-30 12:31:11,057 INFO     (main) Kegbot is starting up.
  2011-12-30 12:31:11,057 INFO     (env) Using web backend: http://localhost:8000/api/
  2011-12-30 12:31:11,064 INFO     (main) Querying backend liveness.
  2011-12-30 12:31:11,077 INFO     (main) Backend appears to be alive.
  2011-12-30 12:31:11,077 INFO     (main) Found 2 taps, adding to tap manager.
  2011-12-30 12:31:11,077 INFO     (tap-manager) Registering new tap: kegboard.flow0
  2011-12-30 12:31:11,077 INFO     (tap-manager) Registering new tap: kegboard.flow1
  2011-12-30 12:31:11,078 INFO     (main) Starting all service threads.
  2011-12-30 12:31:11,078 INFO     (main) starting thread "service-thread"
  2011-12-30 12:31:11,086 INFO     (main) starting thread "eventhub-thread"
  2011-12-30 12:31:11,086 INFO     (main) starting thread "net-thread"
  2011-12-30 12:31:11,086 INFO     (net-thread) network thread started
  2011-12-30 12:31:11,087 INFO     (kegnet) Starting server on ('localhost', 9805)
  2011-12-30 12:31:11,087 INFO     (main) starting thread "heartbeat-thread"
  2011-12-30 12:31:11,088 INFO     (main) starting thread "watchdog-thread"
  2011-12-30 12:31:11,088 INFO     (main) All threads started.

.. tip::
  You can get usage information from most kegbot command-line programs by
  running the command with ``--help``.
  
  Most kegbot programs support the following common flags: ``--daemon``,
  ``--verbose``, and several others, listed in the "pykeg.core.kb_app" section
  of ``--help``.

Testing your kegboard
---------------------
Before you start reporting data, make sure your kegboard is working.  Plug it
in, and run the monitor::

  % kegboard-monitor.py
  2011-12-30 12:52:09,219 INFO     (main) Setting up serial port...
  2011-12-30 12:52:09,236 INFO     (main) Starting reader loop...
  2011-12-30 12:52:09,239 INFO     (kegboard-reader) Packet framing broken (found '\x00', expected 'K'); reframing.
  2011-12-30 12:52:11,943 INFO     (kegboard-reader) Packet framing fixed.
  <HelloMessage: firmware_version=8>
  <TemperatureReadingMessage: sensor_name=thermo-7c0000009b596628 sensor_reading=22.875>

Running the monitor should cause your kegboard to reset and show something
similar to the above.  If you are having problems, you may need to specify
``--kegboard_device``.

Running ``kegboard_daemon.py``
------------------------------

You're now ready to run the Kegbot daemon::

  % kegboard_daemon.py 
  2011-12-30 12:55:41,064 INFO     (main) Starting all service threads.
  2011-12-30 12:55:41,064 INFO     (main) starting thread "kegboard-manager"
  2011-12-30 12:55:41,064 INFO     (kegboard-manager) Starting main loop.
  2011-12-30 12:55:41,065 INFO     (main) starting thread "device-io"
  2011-12-30 12:55:41,065 INFO     (device-io) Starting reader loop...
  2011-12-30 12:55:41,065 INFO     (main) starting thread "kegnet"
  2011-12-30 12:55:41,066 INFO     (kegnet) Connecting to localhost:9805
  2011-12-30 12:55:41,066 INFO     (main) All threads started.
  2011-12-30 12:55:41,067 INFO     (main) Running generic main loop (going to sleep).
  2011-12-30 12:55:41,067 INFO     (kegboard-reader) Packet framing broken (found '\n', expected 'K'); reframing.
  2011-12-30 12:55:41,068 INFO     (kegnet) Connected!
  2011-12-30 12:55:43,770 INFO     (kegboard-reader) Packet framing fixed.
  2011-12-30 12:55:43,771 INFO     (device-io) Found a Kegboard! Firmware version 8
  2011-12-30 12:55:43,780 INFO     (kegboard-manager) RX: <HelloMessage: firmware_version=8>
  2011-12-30 12:55:44,796 INFO     (kegboard-manager) RX: <TemperatureReadingMessage: sensor_name=thermo-7c0000009b596628 sensor_reading=24.1875>

As you can see, the daemon started up, connected to the ``kegbot_core.py``
process (listening on ``localhost:9805``), and started receiving messages.

Navigate back to your ``kegbot_core`` process.  You should see some new log
messages from the kegboard daemon::

  2011-12-30 12:55:41,068 INFO     (kegnet) Remote host connected: 127.0.0.1:58321
  2011-12-30 12:55:44,833 INFO     (thermo-manager) Recording temperature sensor=kegboard.thermo-7c0000009b596628 value=24.1875
  2011-12-30 12:55:44,833 INFO     (thermo-manager) Additional readings will only be shown with --verbose

If you're running the `standalone webserver <webserver-standalone>`_ in another
window, you should see the core posting new temperature readings via the web
api::

  [30/Dec/2011 12:55:45] "POST /api/thermo-sensors/kegboard.thermo-7c0000009b596628/ HTTP/1.1" 200 133
  [30/Dec/2011 12:55:47] "POST /api/thermo-sensors/kegboard.thermo-7c0000009b596628/ HTTP/1.1" 200 131

Now try pouring a drink!
