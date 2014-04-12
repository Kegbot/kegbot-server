.. _overview:

Kegbot Server Overview
======================

Kegbot Server is the web service behind Kegbot.  It serves as both a frontend for
visual navigaton of drinking activity, as well as the backend for all Kegbot
data.

Quick Install
-------------

Ultra-quick install instructions for the experienced and impatient::
  
  $ virtualenv ~/kb                 # create a new home for kegbot
  $ . ~/kb/bin/activate             # step into it
  (kb) $ pip install kegbot         # install the latest kegbot release
  (kb) $ setup-kegbot.py            # interactive configuration tool
  (kb) $ kegbot runserver           # run the dev web server
  Development server is running at http://127.0.0.1:8000/


Features
--------

You're probably already very familiar with what Kegbot Server does. Just in
case, these are the main features:

* **Keg and Tap Management:** Add and configure taps, assign kegs to taps, track
  remaining volume on active kegs, and mark empty kegs as finished.
  Kegbot has been designed with multi-tap systems in mind; a single install can
  support as many taps as you have.
* **Account System:** Full username/password account system, supporting
  registration, login, and password recovery.
* **Drinker Authentication:** Drinkers can be given physical tokens, such
  as RFIDs, to authenticate to the server during a pour.
* **Pour Authorization and Shutoff:** Optionally, your system can require that
  the server authorize each pour, only allowing access (by opening a valve)
  after the drinker is approved.
* **Stats and Charts:** Comprehensive statistics are calculated and recorded at
  each pour, and the web interface draws colorful charts.
* **Drinking Sessions:** As each drink is recorded, Kegbot assigns it to a
  discrete "drinking session" along with nearby drinks, and the server displays
  these sessions at a stable URL.  Did you throw a party? Share a single URL
  that shows all the people and activity from that session.
* **Database Backend:** All Kegbot data, from basic drink information to derived
  statistics and user accounts, gets stored in a database (MySQL, or any other
  database supported by Django).
* **JSON API:** You can build your own frontend or other client interface using
  the `Kegbot API <http://kegbot.org/docs/api/>`_.  Drinks, tap status, user
  information, and almost every other interesting object in Kegbot is exposed
  this way.  The same API is used for recording drinks.
* **Web Hooks:** The server can notify an arbitrary URL whenever there
  is activity such as a pour or new keg. You can bridge Kegbot to external
  services this way.
* **Image Support:** Users can upload profile pictures, and photos can be
  attached to drinks (something the Kegtab Android App does automatically).
* **Twitter, Facebook, Foursquare, and more:** Kegbot has hooks for a growing
  number of external/social sites.  Users can link their Twitter, Facebook,
  Foursquare, or Untappd accounts, and configure automatic posting for each
  drink poured (or just at the start of a new session).
* **Beer Database:** A built-in database lets tag kegs by brewer and beer type.
  You can add entries for commercial or homebrew beers.
* **Open Source:** It's free and open source!  Patches from the
  growing Kegbot community make Kegbot even better.

Dependencies
------------

Kegbot Server is built on a number of excellent open source projects.  The major
dependencies are:

* Python 2.7
* Django 1.4
* MySQL, Postgres, or SQLite
* Python-Imaging 1.7

In addition, Kegbot Server requires several small python modules which are
listed in its setup file.  You generally don't need to worry about these: they
get installed automatically by the Python package manager.


License
-------

Kegbot Server is licensed under the `GNU General Public License v2.0
<http://www.gnu.org/licenses/gpl-2.0.html>`_.  You must accept this license
before installing or using Kegbot Server.
