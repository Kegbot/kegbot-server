.. _changelog:

Changelog
=========

**Upgrade Procedure:** Please follow :ref:`upgrading-kegbot` for general upgrade steps.

Version 1.2.2 (2015-01-03)
--------------------------
* New command `kegbot bugreport` collects various system information.
* Bugfix: Crash on end keg button (#326).
* Bugfix: Unicode error during `kegbot upgrade` (#328).


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
* Statistics now properly consider local timezone (#199).
* Some new keg sizes are supported (#318).
* Keg full volume and beverage type can be edited (#279).


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
