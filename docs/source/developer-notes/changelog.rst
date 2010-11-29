.. _changelog:

Changelog
=========

This changelog covers all Kegbot components (pykeg, kegweb, kegboard, docs).

Version 0.7.6 (2010-11-28)
--------------------------

*Note:* An update to the kegboard firmware is included in this version.
Reflashing your kegboard is recommended.

*Note:* It is recommended that you rebuild all session and statistical data
after updating to this version.
  $ kegbot-admin.py kb_regen_sessions
  $ kegbot-admin.py kb_regen_stats
  $ kegbot-admin.py kb_regen_events

Core/General
^^^^^^^^^^^^
* Improved token handling, resolving multiple bugs related to token timeouts and
  multi-tap authentication.
* Added SessionStats table.  Statistics are now continuously computed for
  drinking sessions, to go along with per-user and per-keg stats.
* Removed protobuf dependency.
* rfid_daemon: added ``--toggle_output`` option, to enable the external output
  whenever an ID is present.
* LCD daemon improvements.

Kegweb
^^^^^^
* Sessions can now be assigned a title, and have descriptive permalinks.
* Sessions are now prominently featured on Kegweb pages.  Various improvements
  to session display.
* Replaced Google image charts with javascript/SVG `Highcharts
  <http://highcharts.com>`_ package.
* Various bugfixes to the web API.
* Added an example WSGI configuration file.

Kegboard
^^^^^^^^
* Improved stability in kegboard_daemon when malformed or unknown messages are
  received.
* Added the :ref:`auth-token-message` type to the serial protocol.
* Fixed reporting for negative temperatures.
* Fixed kegboard reader/daemon to not crash when ``EAGAIN`` is received from the
  OS.
* Update Makefiles.

Version 0.7.5 (2010-09-11)
--------------------------

*Note:* Due to changes to the third-party ``socialregistration`` dependency,
existing users will need to issue the following command after updating::
  $ kegbot-admin.py migrate --fake socialregistration 0001
  $ kegbot-admin.py migrate

*Note:* If you have installed using ``./setup.py develop``, you will need to
issue that command again; new versions of some dependencies are required.

Core / General
^^^^^^^^^^^^^^
* Fixed a race condition which could cause the kegbot core to crash due to an
  erroneous watchdog error.
* Fixed a crash in ``kegbot_admin.py kb_regen_stats`` that would occur when
  computing stats for a keg with no recorded drinks.  (The workaround was to go
  have a beer..)
* Fixed issue #50 (do not record drinks below minimum volume threshold.)

Kegweb
^^^^^^
* Updated to use ``django-socialregistration`` version 0.4.2, and the official
  ``facebook-python-sdk`` package.  Removed mirror of pyfacebook.
* The number of recent pours shown on the main page is now configurable.  See
  ``KEGWEB_LAST_DRINK_COUNT`` in ``common_settings.py.example``


Version 0.7.4 (2010-09-08)
--------------------------

Core / General
^^^^^^^^^^^^^^
* Backend: extensive under-the-hood changes to support multiple sites in a
  single backend instance.  This isn't yet used by anything.
* Fixed issue with pykeg.core migration 0031.
* Improvements to session record keeping.
* Added new SystemEvent table.

Kegweb
^^^^^^
* Improved keg detail page, with better-looking sessions.


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
* Miscellaneous packaging fixes, which should make installation with ``pip`` work
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

