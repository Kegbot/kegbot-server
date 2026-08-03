.. _changelog:

Changelog
=========

**Upgrade Procedure:** Please follow :ref:`upgrading` for general upgrade steps.


Version 2.0.0 (unreleased)
--------------------------

A modernization release. The runtime, framework, and toolchain were all
brought up to date.

**Highlights**

* Python 3.14 is now required (was 3.10).
* Django 5.2 LTS (was 3.2).
* Web server switched from gunicorn/gevent to waitress.
* Packaging moved from Poetry to uv; linting and formatting moved to ruff.
* protobuf upgraded to the 6.x series.
* Docker image rebuilt on ``python:3.14-slim`` with uv; images are published
  to ``ghcr.io/kegbot/server``.
* **Very old backups can now be restored directly.** ``kegbot restore``
  accepts legacy format-1 backups (created by Kegbot v1.1.x) and upgrades
  their data in one step; no intermediate 1.2/1.3 install is needed.
* Time zone choices are now derived from the system time zone database.
* **The legacy HTTP API (``/api/v1``) is deprecated.** It now serves only
  the endpoints used by kegbot-pycore (plus the events feed); every other
  endpoint returns ``410 Gone``, and all legacy responses carry a
  ``Deprecation`` header. Protocol Buffers are no longer used anywhere in
  the server.

**Upgrade notes**

* **Everyone is logged out once.** Sessions now use the JSON serializer, so
  existing session cookies are invalidated on upgrade. Users simply log in
  again.
* **Background jobs enqueue on database commit.** Stats and notification
  jobs are handed to the worker only after the surrounding database
  transaction commits. Ensure ``run_workers`` is running (unchanged) to
  process them.
* ``run_gunicorn`` was removed. Use ``kegbot run_server`` (now waitress).
* The Docker image no longer publishes a ``linux/arm/v7`` variant (amd64 and
  arm64 only).
* The legacy gflags-based Python API client was removed from the server
  package; it lives in the separate kegbot-api project.
* The old Kegbot mobile apps depended on now-retired API endpoints (device
  linking, registration, drink lists) and no longer work against this
  server.


Version 1.3.0 (2022-08-10)
--------------------------

For a detailed look at what's new in version 1.3, see :ref:`version-13-release-notes`.

**Breaking Changes**

Several features have been removed in order to lower code or documentation complexity, reduce maintenance, or both.

* Settings are no longer read from ``local_settings.py`` and must instead be supplied by env.
* The ``setup-kegbot.py`` tool is no longer supported.
* Built-in support and documentation for ``supervisor`` and ``nginx`` has been dropped.
* The Twitter, Foursquare, and Untappd plugins have been removed.
* Optional support for Sentry has been removed.
* Optional support for django-storages has been removed.
* Optional support for memcache has been removed.
* Optional support for statsd has been removed.
* Optional support for django-debug-toolbar has been removed.

**New features**

* Email configuration is now managed in the admin dashboard.
* Allow deletion of tokens from web (:issue:`337`)
* Add mini (5L) keg size (:issue:`331`)
* Add drinks tab to drinker details page (:issue:`347`)
* Allow deleting drinks from Kegbot Admin drinks page (:issue:`348`)
* Don't require user to be active in order to view the user's details and sessions (:issue:`350`)
* Add a create controller view (:issue:`364`)

**Bugfixes**

* Prevent divide by zero error when keg volume is set to zero (:issue:`353`)
* Fixed keg list error (:issue:`353`)
* Fix chart (:issue:`342`)
* Skip notifications for inactive users  (:issue:`349`)
* Fix compatibility with with MySQL versions later than v5.7.5 (:issue:`356`)
* Allow usernames with a period (:issue:`336`)
* Update stats and sessions when admin deletes a drink (:issue:`371`)
* Automatic checks for updates have been removed.
* Fixed pagination not rendering correctly in the dashboard.
* Media files are served in production mode (:issue:`415`)

**Other Changes**

* Upgraded to Python 3 and Django 3.
* Internal: Improved static file serving (:issue:`368`)
* Internal: Developer tests now use ``pytest``
* Internal: Now using ``rq`` for worker queue

Version 1.2.3 (2015-01-12)
--------------------------
* Allow users to change e-mail addresses.
* Added "bugreport" admin page.
* Fix invitation email footer.


Version 1.2.2 (2015-01-03)
--------------------------
* New command `kegbot bugreport` collects various system information.
* Bugfix: Crash on end keg button (:issue:`326`).
* Bugfix: Unicode error during `kegbot upgrade` (:issue:`328`).


Version 1.2.1 (2014-12-02)
--------------------------
* Fixed `run_gunicorn` launcher.


Version 1.2.0 (2014-12-01)
--------------------------
* Keg management improvements: The new "Keg Room" view shows kegs by status,
  and allows kegs to be manually moved between "available" and "finished"
  states.
* Fancy keg graphics.
* Backup file format has changed. Downgrade to v1.1 to restore from an
  earlier file format.
* Django 1.7 update.
* Flow sensing and multiuser features can be hidden.
* Statistics now properly consider local timezone (:issue:`199`).
* Some new keg sizes are supported (:issue:`318`).
* Keg full volume and beverage type can be edited (:issue:`279`).


Version 1.1.1 (2014-11-11)
--------------------------
* API: New endpoint: `drinks/last`.
* Newly-created meters now default to FT330-RJ calibration values.
* Kegadmin: Kegs can be deleted from the "Edit Keg" screen.
* The `kegbot restore` command can run against an unzipped directory.


Version 1.1.0 (2014-09-19)
--------------------------
* Fullscreen mode.
* New keg artwork.
* New internal beverage fields: IBU, SRM, star rating, and color.


Version 1.0.2 (2014-08-21)
--------------------------
* Bugfix: Issue #309 (cannot reset password on private sites).
* Redis logging backend is configurable; see :ref:`settings` (thanks Jared).
* Bugfix: Issue #313 (``link/`` matching on usernames).


Version 1.0.1 (2014-07-21)
--------------------------
* Bugfix: Issue #302 (api ``status/`` endpoint).


Version 1.0.0 (2014-06-24)
--------------------------
* Initial 1.0 release.
* See :ref:`upgrade_pre_10` for upgrade instructions.

For versions prior to 1.0, see :ref:`old-versions`.
