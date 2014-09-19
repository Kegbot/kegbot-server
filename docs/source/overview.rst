.. _overview:

Kegbot Server Overview
======================

Kegbot Server is the web service behind Kegbot.  It serves as both a frontend for
visual navigaton of drinking activity, as well as the backend for all Kegbot
data.


Quick Install
-------------

**New:** The easiest way to get going is by following the
:ref:`Digital Ocean Install Instructions <digitalocean-install>`.

For those already familiar with Linux, these ultra-quick install instructions
may suffice::
  
  $ virtualenv ~/kb                 # create a new home for kegbot
  $ . ~/kb/bin/activate             # step into it
  (kb) $ pip install kegbot         # install the latest kegbot release
  (kb) $ setup-kegbot.py            # interactive configuration tool
  (kb) $ kegbot runserver           # run the dev web server
  Development server is running at http://127.0.0.1:8000/

Read on for detailed, step-by-step instructions.

Dependencies
------------

Kegbot Server is built on a number of open source projects.  The major
dependencies are:

* `Python <https://www.python.org/>`_ 2.7
* `MySQL <http://www.mysql.com/>`_ or `PostgreSQL <http://www.postgresql.org/>`_
* `Redis <http://redis.io/>`_ 2.8 or newer

In addition, Kegbot Server requires several Python modules which are
installed automatically by the Python package manager.


Supported Operating Systems
---------------------------

Kegbot Server should run on any UNIX-based operating system.  Since there are
many possible distributions, the examples in this document are
written for Debian/Ubuntu and Mac OS X
(`Homebrew <http://brew.sh/>`_) package managers.


License
-------

Kegbot Server is licensed under the `GNU General Public License v2.0
<http://www.gnu.org/licenses/gpl-2.0.html>`_.  You must accept this license
before installing or using Kegbot Server.
