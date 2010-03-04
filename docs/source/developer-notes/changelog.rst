.. _changelog:

Changelog
=========

This changelog covers all Kegbot components (pykeg, kegweb, kegboard, docs).

Current version (in development)
--------------------------------

Initial release. (Changes are since hg revision 500:525e06329039).

Core
^^^^
* Vastly improved authentication device support.
* New network protocol for Kegbot status and control (kegnet).
* Temperatures are once again recorded. Temperature sensors can be associated
  with a specific keg tap.
* Support for Phidgets RFID reader.
* Flowmeter resolution is now set on a tap-by-tap basis (in KegTap table).
* Twitter: added config option to suppress tweets for unknown users.
* Started using django-south for schema migrations.
* Sound playback on flow events: added the sound_server application.
* Added kegbot_master program, to control and monitor full suite of kegbot
  daemons.
* Improved support for CrystalFontz LCD devices; new support for Matrix-Orbital
  serial LCD displays.

Kegboard
^^^^^^^^
* Bumped firmware version to v5.
* Fixed packet CRCs.
* Added support for OneWire presence detect/authentication device.
* Improved DS1820 temperature sensing.
* Improved responsiveness of OneWire presence detect.
* Shrunk size of firmware significantly.
* Added experimental support for serial LCDs.

Kegweb
^^^^^^
* Fixed broken relative time display.
* Fixed bug on submitting new user registration.

Docs
^^^^
* Improved documentation.
* Added changelog :)

