.. _changelog:

Changelog
=========

**Upgrade Procedure:** Please follow :ref:`upgrading-kegbot` for general upgrade steps.


Current Version (in development)
--------------------------------

For a detailed look at what's new in version 1.3, see :ref:`version-13-release-notes`.

**Breaking Changes**

* Settings are no longer read from `local_settings.py` and must instead be supplied by env.
* The `setup-kegbot.py` tool is no longer supported.
* Built-in production support and documentation for `supervisor` and `nginx` has been droped.
* Optional support for Sentry has been removed.
* Optional support for django-storages has been removed.
* Optional support for memcache has been removed.
* Optional support for statsd has been removed.
* Optional support for django-debug-toolbar has been removed.

**New features**

* Allow deletion of tokens from web (:issue:`337`)
* Add mini (5L) keg size (:issue:`331`)
* Add drinks tab to drinker details page (:issue:`347`)
* Allow deleting drinks from Kegbot Admin drinks page (:issue:`348`)
* Don't require user to be active in order to view the user's details and sessions (:issue:`350`)
* Twitter plugin: option to tweet/disable system session join events (:issue:`363`)
* Add a create controller view (:issue:`364`)

**Bugfixes**

* Prevent divide by zero error when keg volume is set to zero (:issue:`353`)
* Fixed keg list error (:issue:`353`)
* Fix chart (:issue:`342`)
* Skip notifications for inactive users  (:issue:`349`)
* Fix compatibility with with MySQL versions later than v5.7.5 (:issue:`356`)
* Allow usernames with a period (:issue:`336`)
* Update stats and sessions when admin deletes a drink (:issue:`371`)

**Other Changes**

* Internal: Upgraded to Django 1.11.
* Internal: Improved static file serving (:issue:`368`)
* Internal: Developer tests now use ``pytest``
* Upgraded to Python 3.

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
