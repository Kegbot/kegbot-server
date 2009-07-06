========================
Kegbot Architecture Tour
========================

This chapter discusses the design of Kegbot and how a Kegbot system works.

Overview
========

A running Kegbot system is really a distributed system of several components,
each with a specific role in the control and monitoring of your beer tap or beer
taps.

Regardless of the number of taps, each Kegbot system consists of the following
major components:

* :ref:`core-component`.  A service that acts as the central hub of drink
  processing, permissions management, and other essential services.  There is
  one Core per Kegbot system; most other components are connected to and
  communicate directly with only the Core, forming a star topology.

* :ref:`controller-component`.  A controller is the interface between the Core
  and physical flow hardware (such as a Kegboard).

* :ref:`frontend-component`.  A web application that shows recent drinks,
  per-keg stats, and other information.  It also provides some control features,
  such as the ability to add a new keg to the database.

* :ref:`auth-device-component`.

* :ref:`database-component`.  The database where all drink history, user
  permissions, and other data are stored.   Both the Core and Frontend have
  direct access to the backend.

This system is implemented as a handful of programs in the ``pykeg`` package.
For a typical Kegbot setup, you install ``pykeg`` on a single computer, and run
each of the essential programs as daemons on that computer.


Kegbot Software Components
==========================

.. _core-component:

Core
----

The Kegbot Core (``kb_core`` program) is the central manager of a Kegbot system.
Exactly one Kegbot Core must be running in a single Kegbot system.

The core can be thought of as the 'kernel', or 'brain' of your kegbot
installation.  It locates and connects the various components needed to perform
basic kegbot tasks, such as recording drinks.  The core listens to attached
:ref:`controller-component`, interprets events, and ultimately stores drink
information in the database.

Given the Core's role as the central coordinator of the Kegbot System, most
components connect directly to it, forming a star topology.  The Core runs a
simple but flexible RPC server, which implements the :ref:`kegnet`.

Because Kegnet connections are made over TCP/IP, Kegbot components need not be
located on the same computer.  In practical terms, this means you can build a 

.. _database-component:

Database
--------

The Kegbot Database stores all configuration data, drink history, and analysis
for a Kegbot Core.  Both the :ref:`core-component` and the
:ref:`frontend-component` connect directly to the backend.

The pykeg package can be configured to use either MySQL or sqlite as the
underlying database engine.  Pykeg uses Django to build and access tables from
Python programs.

.. _controller-component:

Kegboard Controller
-------------------

A Kegboard Controller is a host computer that is connected to a Kegboard.
The controller runs the ``kegboard_daemon`` program, which connects the device
to the :ref:`core-component`.  In complex systems, there may be multiple running
Kegboard Controllers, distributed across multiple machines.


.. _auth-device-component:

Authentication Device
---------------------

An authentication device is responsible for the security and user tracking in
the kegbot system; it notifies the core as users come and go.

There are many options available to a kegbot builder in authenticating your
users: you might prefer to use special hardware, such as iButtons.  You
could opt for something as simple as a web page text entry box, which does not
require additional hardware.  Or, you might want to support different methods
concurrently: hardware keys for good friends, and barcodes for party guests.

Because of the diversity of authentication choices, the notion of user presence
is left solely to the authentication device implementation: the
:ref:`core-component` will simply honor any presence/absence events an auth
device reports.  Standard authentication daemons are included.

.. todo:: describe standard daemons.

.. _frontend-component:

Frontend
--------

What good is recording pour data if you can't draw nifty charts and impress your
coworkers?  The frontend is the web home of your kegbot; it provides all sorts
of fun data, user management, and some limited system control capabilities.

Life of a Pour
==============

