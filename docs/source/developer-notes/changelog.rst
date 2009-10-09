.. _changelog:

Changelog
=========

This changelog covers all Kegbot components (pykeg, kegweb, kegboard, docs).

Current version (in development)
--------------------------------

Initial release. (Changes are since hg revision 500:525e06329039).

Core
^^^^
* Preliminary support for Phidgets RFID reader.
* Added authentication device support.
* Flowmeter resolution is now set on a tap-by-tap basis (in KegTap table).
* Twitter: added config option to suppress tweets for unknown users.
* Started using django-south for schema migrations.

Kegboard
^^^^^^^^
* Bump to protocol version 2.
* Added support for OneWire presence detect/authentication device.
* Improved DS1820 temperature sensing.

Kegweb
^^^^^^
* Fixed broken relative time display.
* Fixed bug on submitting new user registration.

Docs
^^^^
* Improved documentation.
* Added changelog :)

