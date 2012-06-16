.. _roadmap:

Roadmap and Known Issues
========================

Known Issues
------------

As of October 2009, the Kegbot software is undergoing a significant rewrite. As
a result, some features that worked previously do not.

Major known issues:

* Access-controlled kegbots (those using a solenoid valve to prevent
  unauthorized access) are not supported.
* "BAC" feature is broken.
* Kegweb is really ugly.


Target: v0.5.0
--------------
* Core: Verify kegboard version in kegboard_monitor.
* Core: Make authentication tokens easier to manage (publish or autocreate
  unknown tokens so that they can be associated with someone.)
* Core: Simplify starting the collection of daemons with a manager/monitor
  script.
* Core: Improve temperature recording, move to more rrdb/timeseries-like
  storage model (retain only summarized data after X hours).
* Kegweb: Fix temperature sensor chart recording.
* Kegweb: Photo upload for profiles.
* Kegweb: Clean up all the ugly CSS and HTML.
* Kegweb: Invite-based user registration.
* Kegweb: Easier-to-discover password reset.
* Kegweb: Configuration panel for all settings in KegbotConfig.


Target: v0.6.0
--------------
* Core: Reinstate support for access control devices (relay, etc).
* Core: Improve the LCD UI.
* Core: Remove "BAC", replace with generalized drink session binge rating;
  generate graphs based on predicted consumption rate & adjust to re-pours.
* Kegboard: Serial input commands (relay on/off, ping).
* Kegboard: EEPROM-backed configuration.
* Kegboard: Support watchdog/timeout feature.
* Kegboard: Add commands to trigger different buzzer tones/alarms.
* Twitter: Make the twitter agent less boring (tweet as user using OAuth,
  incorporate drinking session/group information for more complex tweets, etc.)


Target: v0.7.0
--------------
* Core: Kegnet event pub/sub (allow async notifications of flow updates, other
  events.)
* Core: Stabilize & document kegnet APIs.
* Core: Add centralized reporting mechanism.


Target: v0.8.0
--------------
* Core: More advanced access control mechanisms (time-of-day/calendar access
  restrictions).
* Core: Billing/accounting module, credit system, tie-in with access control.


Target: Future/Wishlist
-----------------------
* Alert manager -- generate alerts to a variety of configurable, per-user sinks
  (email, twitter, IM, SMS) on various events (keg change, new drinker record,
  temperature alerting, and so on.)
* Audio daemon -- kegnet client that can play certain sounds at certain trigger
  points in a flow (drinker authenticated, pour crossed certain threshold, and
  so on.)
* Facebook app -- shareable stats, drink updates, drink credit/payment.
* Android, iPhone apps -- user registration, mugshot creation, keg status (for
  users), keg control (for admins), kegnet client (act as authentication/display
  device when on same network as core.)
