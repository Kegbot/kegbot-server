Planning your Kegbot
====================

Lager, IPA, or Porter?  Sierra or Dogfish Head?  Half Barrel or Pony?  As beer
drinkers, we all have different tastes -- and building your Kegbot system is no
different. (Gosh, that was cheesy.)

A Kegbot system can be built a variety of different ways, and with any of
several optional features enabled or disabled.  There are a number of decisions
you will need to make over the course of building your Kegbot.

Note that most of decisions you make on the topics below can be fluid. For
example, if you change your mind about access control or the number of taps you
want, it is easy enough to alter the Kegbot configuration after it has been
built.


Kegerator: Build vs Buy?
------------------------

Do you want to build a Kegerator from scratch (by installing beer hardware on a
freezer or refrigerator), or buy one off the shelf?

This question actually doesn't have much bearing on your Kegbot system; either choice
will work equally well.  Your author has done it both ways.

If you are on a limited budget, and especially if you already have the
refrigerator, going the conversion route could be much cheaper than purchasing a
totally new unit.

On the other hand, kegerators have become quite commonplace -- easy to find in
online shops, or at brick-and-mortar appliance stores like Best Buy.  If you
want to save time (and potentially end up with a nicer looking build), buying a
pre-built kegerator can be a good choice.

Build Kegerator first
---------------------

If you're building a Kegerator, do you want to use it without Kegbot first? (If
you already have a working kegerator, this section isn't very relevant.)

We often advise new users to start building a Kegbot by building (and enjoying!)
a functioning kegerator first.  Doing so allows you to get to know your beer
equipment, before you complicate it by adding Kegbot hardware.

The main work of installing Kegbot into a kegerator involves splicing a
flowmeter into the beer line.  You can always do this step later; enjoy a few
beers and work out any beer line/pressure/foam issues while preparing the rest
of the system.

Number of Taps
--------------

How many beer taps do you want to monitor?  This will affect the number of
meters, controller boards, fittings, and other accessories you will need to buy.

.. note::
  Though the Kegboard controller boards have a limited number of flowmeter
  inputs (2, or 6 if based on Arduino Mega), the Kegbot core can read from
  multiple controllers at once.

.. todo::
  Add reference to multiple controller board support in :ref:`user-guide`.

Authentication Support
----------------------

Do you want to make use of the per-user tracking in Kegbot?

Though it is the most popular Kegbot feature, authentication isn't required:
Kegbot will happily record drinks anonymously when pours occur with no user
involvement. Skipping this feature can simplify your build, and save you some
money (no need to buy id tokens.)

If you *do* want authentication, then you still have choices: what sort of
authentication device do you want to use?  At the moment, Kegbot supports two
forms of authentication: RFIDs, and iButtons.

.. todo::
  Add links to iButton and RFID setup instructions in :ref:`user-guide`.

Access Control (Solenoid Valve)
-------------------------------

How concerned are you about unauthorized access to your Kegbot?  This feature
increases the complexity of a pour by preventing unauthenticated users from
pouring.  It also means additional fittings in your beer line, and electric
relays in your controller board.

.. note::
  As of writing, access control support is temporarily broken (in core and
  controller).

.. todo::
  Remove note after access control is fixed.

