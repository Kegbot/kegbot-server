.. _kegboard-serial-protocol:

==================================
Kegboard Serial Protocol Reference
==================================

About this document
===================

This document describes the protocol implemented in the Kegboard firmware.  The
protocol is a simple serial protocol for exchanging data and commands with a
controller board.

.. note::
  Most users don't need to be too familiar with the Kegboard protocol.  This
  document is intended for someone building a new type of controller board, or
  attempting to extend the existing board.  For example, if you build a new type
  of controller board that speaks this protocol, you should be able to use the
  rest of the Kegboard software without further modification.

Protocol Overview
=================

The Kegboard Serial Protocol is a binary protocol between the kegboard and the
host PC. Data is delivered from the board in the **message frame format**
(described later). The host can also control and configure the board by sending
messages in the same format.

Messages arrive from the board *asynchronously*; the host does not need to
request updates to receive information about sensors. Similarly, the host can
issue commands to the board at any time.


Software Support
================

The pykeg software includes libraries for reading and writing KBSP packets. A
unittest with a sample packet capture is also included. See the code available
in ``pykeg/hw/kegboard``.


Message Frame Format
====================

Data from the Kegboard is always sent to the host in the `Kegboard Message`
frame format.  All messages take the same basic format::

  <header><payload><footer>

A single message includes:

* A 12-byte header section, identifying the message being sent.
* A variable-length payload section, typically in TLV (tag-length-value) format.
  The payload can be from zero to 112 bytes in size.
* A 4-byte footer section, containing a CRC of the entire packet.

Given the section sizes above, the maximum length of a complete message is 128
bytes.

Here are examples of two messages in a raw byte stream, showing two frames sent
from the Kegboard to the host. For each message, the first line is a
human-readable version of the message; the second line is a sequence of bytes
forming the complete message.::

  # <HelloMessage: protocol_version=3>
  \x4b\x42\x53\x50\x20\x76\x31\x3a\x01\x00\x04\x00\x01\x02\x03\x00\x2e\x54\x0d\x0a

  # <MeterStatusMessage: meter_name=flow1 meter_reading=4>
  \x4b\x42\x53\x50\x20\x76\x31\x3a\x10\x00\x0e\x00\x01\x06\x66\x6c\x6f\x77\x31\x00\x02\x04\x04\x00\x00\x00\x55\x0a\x0d\x0a


Header Section
--------------

Every message begins with a fixed-length 12-byte header section. An ASCII
representation is shown below::

  0                   1                   2                   3
  0 1 2 3 4 5 6 7 8 9 0 1 2 3 4 5 6 7 8 9 0 1 2 3 4 5 6 7 8 9 0 1
  +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
  |                            prefix (8)                         |
  |                                                               |
  +-------------------------------+-------------------------------|
  |        message_id (2)         |      payload_len (2)          |
  +-------------------------------+-------------------------------+


The `prefix` field is a constant 8-byte sequence to identify the start of the
packet. The value is always the ascii characters "``KBSP v1:``".  Software
attaching to a live kegboard serial port can search for this stream of
characters to determine the start of the next packet, with reasonable
confidence.

The `message_id` field is the type of the message (see types defined in
:ref:`message-types-section`.)

The `payload_len` field is the length, in bytes, of the payload section. Some
messages do not have a payload, in which case this section will read zero. Note
that this value only describes the length of the payload section (and not the
length of the footer section, which is constant.)

Payload Section
---------------

The payload of a message varies depending on the message type, described in
:ref:`message-types-section`.  The payload section may be empty, and has a
maximum length of 112 bytes.

All payloads are serialized in `type-length-value
<http://en.wikipedia.org/wiki/Type-length-value>`_ style. This format makes it
possible to extend the body of a payload in the future with a new tag number.
If a message parser encounters a tag it does not recognize, it should skip over
the unrecognized value according to the given length.

Footer Section
--------------

Each message includes a 4-byte footer section::

  0                   1                   2                   3
  0 1 2 3 4 5 6 7 8 9 0 1 2 3 4 5 6 7 8 9 0 1 2 3 4 5 6 7 8 9 0 1
  +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
  |           crc (2)             |         trailer (2)           |
  +-------------------------------+-------------------------------+

The `crc` field is a `CRC-16-CCITT
<http://en.wikipedia.org/wiki/Cyclic_redundancy_check>`_ of the header and
payload fields; in other words, the entire message up to the CRC. This CRC is
used by the host to verify the integrity of messages from the board.

The integrity of a message can be verified by performing the CRC calculation on
all data, up to and including the CRC (but not the trailer).  If correct, the
value will be zero.

The string ``\r\n`` is always written in the `trailer` field. This field is not
included in the CRC.


Field Types
===========

Fields in messages are described in terms of `field types`, which are analogous
to C types. Types used are described below. Note that all integer types are
serialized in **little-endian** format.

+--------------+--------+------------------------------------------------------+
| Type name    | Size   | Interpretation                                       |
+==============+========+======================================================+
| ``int8``     | 1      | 8-bit signed integer (aka char)                      |
+--------------+--------+------------------------------------------------------+
| ``int16``    | 2      | 16-bit signed integer                                |
+--------------+--------+------------------------------------------------------+
| ``int32``    | 4      | 32-bit signed integer                                |
+--------------+--------+------------------------------------------------------+
| ``uint8``    | 1      | 8-bit unsigned integer (aka uchar)                   |
+--------------+--------+------------------------------------------------------+
| ``uint16``   | 2      | 16-bit unsigned integer                              |
+--------------+--------+------------------------------------------------------+
| ``uint32``   | 4      | 32-bit unsigned integer                              |
+--------------+--------+------------------------------------------------------+
| ``uint64``   | 8      | 64-bit unsigned integer                              |
+--------------+--------+------------------------------------------------------+
| ``string``   | Varies | Null-terminated C string                             |
+--------------+--------+------------------------------------------------------+
| ``bytes``    | Varies | Raw collection of byte values.                       |
+--------------+--------+------------------------------------------------------+
| ``output_t`` | 1      | Boolean (0=disabled, 1=enabled); like ``uint8``      |
+--------------+--------+------------------------------------------------------+
| ``temp_t``   | 4      | 1/10^6 Degrees C; signed; like ``int32``             |
+--------------+--------+------------------------------------------------------+

.. _message-types-section:

Message Definitions
===================

This section summarizes messages which may arrive at the host from a board
implementing the protocol.

.. _hello-message:

``hello`` message (0x01)
------------------------

This message may be sent by the board to indicate that it is alive. The host may
request this message with the :ref:`ping-command`.

+---------+-----------------+----------+---------------------------------------+
| Tag ID  | Name            | Type     | Description                           |
+=========+=================+==========+=======================================+
| 0x01    | protocol_version| uint16   | Supported version of kegboard         |
|         |                 |          | serial protocol.                      |
+---------+-----------------+----------+---------------------------------------+

.. _board-configuration-message:

``board_configuration`` message (0x02)
--------------------------------------

A configuration message dumps the board's configuration data.  These values can
be programmed by sending a :ref:`set-configuration-command` with the same message
as payload.

+---------+--------------------+----------+---------------------------------------+
| Tag ID  | Name               | Type     | Description                           |
+=========+====================+==========+=======================================+
| 0x01    | board_name         | string   | Board descriptive name.               |
+---------+--------------------+----------+---------------------------------------+
| 0x02    | baud_rate          | uint16   | Serial port speed, in bits per second |
+---------+--------------------+----------+---------------------------------------+
| 0x03    | update_interval    | uint16   | Time in milliseconds between update   |
|         |                    |          | messages to the host.                 |
+---------+--------------------+----------+---------------------------------------+
| 0x04    | watchdog_timeout   | uint16   | Maximum time permitted between        |
|         |                    |          | commands from host before triggering  |
|         |                    |          | the watchdog alarm.                   |
+---------+--------------------+----------+---------------------------------------+

.. _meter-status-message:

``meter_status`` message (0x10)
-------------------------------

This message describes the instantaneous reading of a single flow meter channel.
For a kegboard with multiple flow meter inputs, multiple messages will be sent.

+---------+-----------------+----------+---------------------------------------+
| Tag ID  | Name            | Type     | Description                           |
+=========+=================+==========+=======================================+
| 0x01    | meter_name      | string   | Name of the meter reporting flow.     |
+---------+-----------------+----------+---------------------------------------+
| 0x02    | meter_reading   | uint32   | Total volume, in ticks.               |
+---------+-----------------+----------+---------------------------------------+

.. _temperature-reading-message:

``temperature_reading`` message (0x11)
--------------------------------------

This message describes the instantaneous reading of a single temperature sensor.
For a kegboard with multiple sensors, multiple messages may be sent.  Note that
the temperature is presumed to be valid at the time the message is sent.

The value of ``sensor_name`` will include the full 128-bit 1-wire device id, for
example, ``thermo-f800080012345610``.

+---------+-----------------+----------+---------------------------------------+
| Tag ID  | Name            | Type     | Description                           |
+=========+=================+==========+=======================================+
| 0x01    | sensor_name     | string   | Name of the sensor being repoted.     |
+---------+-----------------+----------+---------------------------------------+
| 0x02    | sensor_reading  | temp_t   | Temperature at the sensor.            |
+---------+-----------------+----------+---------------------------------------+

.. _output-status-message:

``output_status`` message (0x12)
--------------------------------

This message describes the status of a single general-purpose output on the
board.  An output could be connected a relay, or some other device to control
valves.

+---------+-----------------+----------+---------------------------------------+
| Tag ID  | Name            | Type     | Description                           |
+=========+=================+==========+=======================================+
| 0x01    | output_name     | string   | Name of the output being reported.    |
+---------+-----------------+----------+---------------------------------------+
| 0x02    | output_reading  | output_t | Status of the output.                 |
+---------+-----------------+----------+---------------------------------------+

.. _onewire-presence-message:

``onewire_presence`` message (0x13)
-----------------------------------

.. note::
  This message has been *deprecated*. It is no longer issued by kegboard, and
  has been replaced by :ref:`auth-token-message`.

When a 1-wire device is detected on the presence bus, this message is generated
and sent.

+---------+-----------------+----------+---------------------------------------+
| Tag ID  | Name            | Type     | Description                           |
+=========+=================+==========+=======================================+
| 0x01    | device_id       | uint64   | ID of 1-wire device now present.      |
+---------+-----------------+----------+---------------------------------------+
| 0x02    | status          | uint8    | 1 if present, 0 if removed.           |
+---------+-----------------+----------+---------------------------------------+


.. _auth-token-message:

``auth_token`` message (0x14)
-----------------------------------

When an authentication token is attached or removed from the kegboard, this
messages is sent.  The ``device_name`` field gives the name of the kegboard
peripheral producing the message; this will be `onewire` for iButtons.  The
``token`` field gives the raw, big-endian byte value of the token.

.. todo::
  Document update frequency and describe how to change it (it is the main loop
  update interval.)

+---------+-----------------+----------+---------------------------------------+
| Tag ID  | Name            | Type     | Description                           |
+=========+=================+==========+=======================================+
| 0x01    | device_name     | string   | Name of authentication device.        |
+---------+-----------------+----------+---------------------------------------+
| 0x02    | token           | bytes    | Raw token ID being reported.          |
+---------+-----------------+----------+---------------------------------------+
| 0x03    | status          | uint8    | 1 if present, 0 if removed.           |
+---------+-----------------+----------+---------------------------------------+



.. _last-event-message:

``last_events`` message (0x20)
------------------------------

Kegboard has a flow "event recall" feature, which stores a limited amount of
information about recent flows in the microcontroller's RAM.


.. todo:: Write this section.


.. _watchdog-alarm-message:

``watchdog_alarm`` message (0x30)
---------------------------------

This message indicates the status of the host-controller watchdog.

+---------+-----------------+----------+---------------------------------------+
| Tag ID  | Name            | Type     | Description                           |
+=========+=================+==========+=======================================+
| 0x01    | watchdog_status | uint_16  | Nonzer if watchdog is firing.         |
+---------+-----------------+----------+---------------------------------------+

Command Definitions
===================

This section summarizes messages which may be sent to a host implementing the
protocol.

.. _ping-command:

``ping`` command (0x81)
------------------------

This command is sent to the board to request a :ref:`hello-message`.  This can be
used to verify that the attached device is a Kegboard that speaks the serial
protocol.

There is no payload.

.. _get-configuration-command:

``get_configuration`` command (0x82)
------------------------------------

This command is sent to the board to request a
:ref:`board-configuration-message` from the board.

There is no payload.

.. _set-configuration-command:

``set_configuration`` command (0x83)
------------------------------------

This command sets persistent configuration values on the board. The payload is
identical to the :ref:`board-configuration-message`.

The configuration command is not acknowleged. Instead, the host should issue a
:ref:`get-configuration-command`, and inspect the resulting
:ref:`board-configuration-message`.

Note that the current kegboard implementation requires a manual reset for any of
the values to take effect.

``set_output`` command (0x84)
------------------------------------

This command is sent to the board to enable or disable a device output.

+---------+-----------------+----------+---------------------------------------+
| Tag ID  | Name            | Type     | Description                           |
+=========+=================+==========+=======================================+
| 0x01    | output_id       | uint8_t  | Numerical output id (0-15).           |
+---------+-----------------+----------+---------------------------------------+
| 0x02    | output_mode     | output_t | Mode to set the output.               |
+---------+-----------------+----------+---------------------------------------+

.. _get-events-command:

``get_events`` command (0x86)
-----------------------------

.. todo:: Write this section.

.. _clear-events-command:

``clear_events`` command (0x87)
-------------------------------

.. todo:: Write this section.

.. _pause-command:

``pause`` command (0x88)
------------------------

.. todo:: Write this section.

.. _resume-command:

``resume`` command (0x89)
-------------------------

.. todo:: Write this section.


Protocol Revision History
=========================

This section describes major updates to this protocol.

+---------+-----------------+--------------------------------------------------+
| Version | Date            | Remarks                                          |
+=========+=================+==================================================+
| 1       | current         | Initial version.                                 |
+---------+-----------------+--------------------------------------------------+
