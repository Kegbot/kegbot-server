.. _changelog:

Changelog
=========

This changelog covers all Kegbot components (pykeg, kegweb, kegboard, docs).

Version 0.7.3 (2010-09-01)
--------------------------

*Note:* Existing users upgrading from a previous kegbot version will need to
issue the migrate command to update their database schema.  Also, statistics and
sessions need to be regenerated::
  $ kegbot_admin.py migrate
  $ kegbot_admin.py kb_regen_sessions
  $ kegbot_admin.py kb_regen_stats

Core / General
^^^^^^^^^^^^^^
* Fixed issue authentication tokens for consecutive pours not being reported
  correctly.
* Improved stats reporting; fixed drinker breakdown graph on keg detail page.
* Added a notes field for Keg records.
* Internal cleanups to the backend APIs.
* Schema change: Started record auth token details used for each pour.
* Schema change: Guest pours are now represented by a ``null`` user (rather than
  a specific guest account) in the database.

Kegweb
^^^^^^
* Fixed issue causing kegweb to break when used without proper Facebook
  credentials.
* Improvements to the currently undocumented kegweb API.

Kegboard
^^^^^^^^
* Update KegShield schematics to include Arduino and Arduino Mega shield
  designs.

Version 0.7.2 (2010-06-29)
--------------------------

Core / General
^^^^^^^^^^^^^^
* Django v1.2 is now **required**.
* Added new dependency on ``django_nose`` for running unittests; ``make test``
  works once again to run unittests
* Improved LCD UI; now shows tap status, last pour information.
* Fixed SoundServer, which had stopped working some time ago.
* Miscellanous packaging fixes, which should make installation with ``pip`` work
  a bit better.

Kegweb
^^^^^^
* Fix for bug #48: Facebook connect login broken.
* Fixed/update CSRF detection on forms for Django 1.2.
* Bugfixes for the Kegweb REST ('krest') API.

Twitter
^^^^^^^
* Moved Twitter add-on out of the core and into a new daemon,
  ``kegbot_twitter``, similar to Facebook app ``fb_publisher``.


Version 0.7.1 (2010-06-04)
--------------------------

Core / General
^^^^^^^^^^^^^^
* Added missing dependencies to `setup.py`.
* Removed a few locally-mirrored dependencies.
* Added protobuf source mirror to `setup.py`.

Kegweb
^^^^^^
* Reorganized account settings views.
* Add password reset forms.

Version 0.7.0 (2010-05-23)
--------------------------

Initial numbered release! (Changes are since hg revision 500:525e06329039).

Core / General
^^^^^^^^^^^^^^
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
* Added Facebook publisher add-on.
* Packaging improvements; `setup.py install` works.

Kegboard
^^^^^^^^
* Bumped firmware version to v5.
* Fixed packet CRCs.
* Added support for OneWire presence detect/authentication device.
* Improved DS1820 temperature sensing.
* Improved responsiveness of OneWire presence detect.
* Shrunk size of firmware significantly.
* Added experimental support for serial LCDs.
* Added schematic files for Kegboard Arduino shield.

Kegweb
^^^^^^
* Design refresh; new HTML/CSS and many more graphs and stats.
* Added keg administration tab.
* Added experimental support for Facebook connect.
* Fixed broken relative time display.
* Fixed bug on submitting new user registration.

Docs
^^^^
* Improved documentation.
* Added changelog :)

