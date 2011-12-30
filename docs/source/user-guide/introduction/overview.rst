.. _overview:

Overview
========

Kegbot is an **open-source** beer tap control and analysis system.  The Kegbot
Project provides free code and instructions to set up and monitor your kegs.
With a Kegbot system attached to your kegs, you can:

* instantly know much beer is left in the keg,
* share beer with multiple people and track each user's share,
* limit access to kegs and beverage depending on the user, time of day, or other
  factors,
* and much more!

Most importantly, Kegbot is a **free, open-source** project.  We provide code
and documentation with the hopes that you will use, enjoy, and maybe even
improve the project as a whole.


Kegbot Project mission
----------------------

The Kegbot Project mission is to:

* provide free, open source, high quality beer monitoring and control software;
* develop innovative new ways of monitoring and controlling access to beverages;
* foster a **fun**, knowlegable beer-loving project community.


History
-------

Kegbot was started one lazy, hazy summer in 2003.


Features
--------

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


License
-------

Kegbot is licensed under the `GNU General Public License v2.0
<http://www.gnu.org/licenses/gpl-2.0.html>`_.  In short, you are free to use and
extend Kegbot.

.. _getting_involved:

Getting Involved
----------------

Because Kegbot is not a commercial venture, we rely on users like you to help
make it better.  As with any open source project, we invite you to participate
in the Kegbot community and help us make Kegbot better.


Forums
^^^^^^

We are experimenting with discussion groups over at the `Kegbot Forums
<http://kegbot.org/kegbb/>`_.  The forums are open to all users, and we hope
they will be a resource of knowlege about building and running a Kegbot.  If you
are looking for help getting started, this should be your first stop.


Bug reports
^^^^^^^^^^^

Please visit the `Kegbot Bugs Database <http://b.kegbot.org/>`_ at Github to
browse and report bugs.  In addition to problem reports, we welcome patches and
improvements to the Kegbot code.


IRC
^^^

Kegbot maintains an IRC channel on the `Freenode 
<http://freenode.net>`_ network: #kegbot.  Drop by and say hi.


Developers
^^^^^^^^^^

We're hungry for contributors!  The best way to get involved is to submit a
patch or add a new feature.  If you would like to contribute but don't know why
to start, ask around in the forums or on IRC.  (We'd like to have a better
developer guide soon.)
