.. _kegbot-howto-overview:

Build a Kegbot: Overview
========================

Your author can guarantee that building your Kegbot will be more fun than doing
that lawn work or taking up knitting.  Your new gizmo will be the life of your
next party, an endless source of new ideas, and just plain nerdy-cool.

However, your author has also seen many eager-eyed metered-beer-lovers get
stalled by malaise, overwhelmed by the steps involved, or put off by
shortcomings in documentation.  This section is an attempt to get you started,
with some tips we've learned along the way.

Major Components
----------------

Though Kegbot's operating principles are quite simple, Kegbot is a hardware and
software system of several components.

.. graph:: components

  mode=hier
  rankdir=BT
  "Database" [shape=box3d];
  "Core" [style="filled,rounded", shape=box];
  "Kegweb" [style="filled,rounded", shape=box];
  "Controller" [style="filled,rounded", shape=box];
  "Core" -- "Database";
  "Kegweb" -- "Database";
  "Controller" -- "Core";


**Core**
  The `Core` is the main brain of a Kegbot system.  It is the software program
  that monitors the Kegbot hardware, manages authentication of users, and
  records sequences of flowmeter data into discrete drinks in the database.

  No matter how many beer taps you intend to run, nor where the taps are
  located, every Kegbot system needs just one Core.  (The :ref:`user-guide`
  covers building and running the core.)

**Controller / Kegboard**
  The `controller` (or sometimes, `kegboard`), refers to the
  microcontroller-based hardware that is used to monitor the flow sensors in a
  Kegbot system.

  We have written firmware for the Arduino AVR platform to act as a controller
  board, capable of reading multiple flow meters and temperature sensors.  We
  call our Arduino board and firmware `Kegboard`.  (Kegboard is described in
  depth in the :ref:`kegboard-guide` doc.)

**Database**
  All drink data, as well as derived statistics, user accounts, and most
  configuration data, is stored in a database.  This one is pretty
  straightforward: Kegbot requires either MySQL or SQLite as its database
  backend.

**Kegweb**
  If you've ever seen a Kegbot web page, then you're already familiar with
  `Kegweb`: our web frontend to the Kegbot system.

  Kegweb reads data directly from the database.  Using Kegbot's built-in user
  account system, Kegbot users can log in to a the Kegweb frontend and adjust
  their profile and other settings.  (Installation of Kegweb is covered in the
  :ref:`user-guide`.)

Common Questions
----------------

Before we begin, we will answer the most common questions new Kegbot builders
often have.

How much will it cost?
^^^^^^^^^^^^^^^^^^^^^^

For the most basic system, you can expect the following primary expenses:

* $0-$1000 -- Refrigerator.  Any fridge large enough to accommodate a keg will
  work; fancy commercial kegerators look nice but cost much more.
* $40 -- Kegboard (Arduino board.)
* $0-$300 -- Linux computer.  You won't need anything fancy, so an old PC or
  laptop installed with your favorite Linux distro will do the trick.
* $50 -- Flow meter.
* $0-$100 -- Flow hardware.


How long will it take to build?
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

It should be possible to find and assemble all the parts in a week.  No
guarantees yet, though: here at Kegbot HQ, we're still learning how to make
things easier for others.


What skills do I need to build one?
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

The minimum skills necessary to build a Kegbot system are:

* **Linux.** You will need to set up and run the Kegbot software on a Linux
  machine.  If you can find an old computer and make Ubuntu run on it, you're
  good to go.
* **Wiring.** You do *not* need to know how to solder, but you will need to
  connect a few signal wires together to get your Kegboard working.  If you know
  how to build Ikea furniture or Lego kits, it's the same sort of effort.

