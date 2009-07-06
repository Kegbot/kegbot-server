============
Introduction
============

What is Kegbot?
===============

Kegbot is a **free, open-source** beer tap control and analysis system.  The
Kegbot Project provides free code and instructions to set up and monitor your
kegs. With a Kegbot system attached to your kegs, you can:

* instantly know much beer is left in the keg,
* share beer with multiple people and track each user's share,
* limit access to kegs and beverage depending on the user, time of day, or other
  factors,
* and much more!


Kegbot Project mission
======================

The Kegbot Project mission is to:

* provide free, open source, high quality beer monitoring and control software;
* develop innovative new ways of monitoring and controlling access to beverages;
* foster a **fun**, knowlegable beer-loving project community.


Features
========

The following is a partial list of Kegbot's major features.

* **Comprehensive drink tracking, analysis, and reporting.** Kegbot records
  every drop of fluid passing though a monitored meter into a central drinks
  database.  Built-in postprocessing modules attempt to group related drinks,
  estimate blood alcohol content, and perform other analysis.

* **Multi-tap support.** Kegbot supports single and multi-tap setups; mutliple
  kegs can be monitored in a single system, and kegs can be added and removed
  on-the-fly, without restarting the Kegbot system.

* **Full multi-user support.** Kegbot is designed to be used in an environment
  where multiple people may have access to the keg.  Kegbot has extensive
  support for various authentication and identification devices. Kegbot attempts
  to assign ownership to each pour based on these devices, falling back to an
  "anonymous" user when the owner can't be determined.

* **Extensible web frontend.** Drink details, keg status, user histories, and
  lots of other goodies are available through a web frontend, built on the
  Django framework.

* **Temperature recording and alarming.** Kegbot includes code to monitor any
  number of hardware temperature sensors.


Requirements
============

The following pieces of software are required:

* `Python <http://python.org>`_ version 2.4 or later
* `Django <http://www.djangoproject.org/>`_ version 1.0 or later
* `Mysql <http://www.mysql.org/>`_ or `Sqlite <http://www.sqlite.org/>`_

Getting Help
============
