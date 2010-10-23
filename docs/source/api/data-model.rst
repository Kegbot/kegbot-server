.. _data-model:

===========================
Kegbot Data Model Reference
===========================

Overview
========

This document contains a reference of the most commonly used objects in the API.

.. _api-objects:

Objects
=======

This section lists all currently supported objects.

.. _model-authtoken:

AuthToken
---------

An AuthToken object represents a unique key that identifies a user.

Properties
^^^^^^^^^^

====================  ==============  ==========================================
Property              Type            Description
====================  ==============  ==========================================
id                    ``string``      The auth token value.  The format is
                                      ``<auth_device>|<id>``, where
                                      ``auth_device`` identifies the
                                      authentication device, and ``id`` is a
                                      unique key for the device.
*username*            ``string``      The username the token is bound to.
created_time          ``date``        The date the token was created or
                                      activated.
*expire_time*         ``date``        The date after which the token is no
                                      longer valid.
enabled               ``bool``        Whether the token is active.
====================  ==============  ==========================================

Example
^^^^^^^

.. code-block:: javascript
  
  {
    "id" : "core.onewire|6400000001020304",
    "username" : "mikey",
    "created_time" : "2010-08-14T04:00:00+0000",
    "expire_time" : "2011-08-14T04:00:00+0000",
    "enabled" : true
  }



.. _model-beerstyle:

BeerStyle
---------

A BeerStyle describes a particular style of beer.

Properties
^^^^^^^^^^

====================  ==============  ==========================================
Property              Type            Description
====================  ==============  ==========================================
id                    ``string``      An opaque, unique identifier for this beer
                                      style.
name                  ``string``      The name of this beer style.
====================  ==============  ==========================================

Example
^^^^^^^

.. code-block:: javascript
  
  {
    "id" : "5464",
    "name" : "Pale Ale"
  }



.. _model-beertype:

BeerType
--------

A BeerType identifies a specific beer, produced by a specific
:ref:`model-brewer`, and often in a particular :ref:`model-beerstyle`.  Several
traits of the beer, such as its alcohol content, may also be given.

Properties
^^^^^^^^^^

====================  ==============  ==========================================
Property              Type            Description
====================  ==============  ==========================================
id                    ``string``      An opaque, unique identifier for this beer
                                      type.
name                  ``string``      The brand name of the beer.
brewer_id             ``string``      The identifier for the :ref:`model-brewer`
                                      which produces this beer.
brewer                ``dict``        The :ref:`model-brewer` for this beer.
*style_id*            ``string``      The identifier for the style of this beer.
*style*               ``string``      The name of the beer style.
*edition*             ``string``      For seasonal or special edition version of
                                      a beers, the year or other indicative
                                      name.
*calories_oz*         ``float``       The number of calories per fluid ounce of
                                      beer.
*carbs_oz*            ``float``       Number of carbohydrates per ounce of
                                      beer.
*abv*                 ``float``       Alcohol by volume, as a percentage.
*original_gravity*    ``float``       Original gravity of this beer, if known.
*specific_gravity*    ``float``       Specific gravity of this beer, if known.
====================  ==============  ==========================================

Example
^^^^^^^

.. code-block:: javascript
  
  {
    "id": "20bd3f32-75eb-11df-80f2-00304833977c",
    "name": "Trumer Pils", 
    "style_id": "ff5cbb4c-75ea-11df-adf0-00304833977c", 
    "style": "Pilsner", 
    "brewer_id": "fc2884ec-75ea-11df-adf0-00304833977c", 
    "brewer": {
      "id": "fc2884ec-75ea-11df-adf0-00304833977c", 
      "name": "Privatbruerei Josef Sigl", 
      "origin_city": "CA", 
      "url": "", 
      "country": "USA", 
      "production": "commercial", 
      "origin_state": "Berkeley", 
      "description": ""
    }, 
    "edition": "", 
    "calories_oz": 12.5, 
    "abv": 4.9000000000000004
  }



.. _model-brewer:

Brewer
------

A Brewer is a producer of beer.

Properties
^^^^^^^^^^

====================  ==============  ==========================================
Property              Type            Description
====================  ==============  ==========================================
id                    ``string``      An opaque, unique identifier for this
                                      object.
name                  ``string``      Name of the brewer.
*country*             ``string``      Country where the brewer is based.
*origin_state*        ``string``      State or province where the brewer is
                                      based.
*origin_city*         ``string``      City where the brewer is based.
*production*          ``string``      Type of production, either "commercial" or
                                      "homebrew".
*url*                 ``url``         Homepage of the brewer.
*description*         ``string``      Free-form description of the brewer.
====================  ==============  ==========================================

Example
^^^^^^^

.. code-block:: javascript
  
  {
    "id" : "3415",
    "name" : "Deschutes Brewery",
    "country" : "USA",
    "origin_state" : "Oregon",
    "origin_city": "Bend",
    "production" : "commercial",
    "url" : "http://www.deschutesbrewery.com/",
    "description" : "Founded in 1988 in Bend, Oregon."
  }



.. _model-drink:

Drink
-----

Drink objects represent a specific pour.  Typically, but not always, the Drink
object lists the user known to have poured it, as well as the keg from which it
came.

Properties
^^^^^^^^^^

====================  ==============  ==========================================
Property              Type            Description
====================  ==============  ==========================================
id                    ``uint32``      A unique identifier for this object.
ticks                 ``uint32``      The number of flow meter ticks recorded
                                      for this drink.  Note that this value
                                      should never change once set, regardless
                                      of the volume_ml property.
volume_ml             ``float``       The volume of the pour, in milliliters.
session_id            ``string``      :ref:`model-session` that this drink
                                      belongs to.
pour_time             ``date``        The date of the pour.
is_valid              ``bool``        Whether the drink is considered valid.
*keg_id*              ``uint32``      The :ref:`model-keg` from which the drink
                                      was poured, if known.
*user_id*             ``string``      The :ref:`model-user` who poured the
                                      drink, if known.
====================  ==============  ==========================================

Example
^^^^^^^

.. code-block:: javascript
  
  {
    "id" : 101,
    "ticks" : 2200,
    "volume_ml" : 1.0,
    "session_id" : "17",
    "pour_time" : "2010-08-14T04:00:00+0000",
    "is_valid" : true,
    "keg_id" : 3,
    "user_id" : "mikey"
  }



.. _model-keg:

Keg
---

A Keg object records an instance of a particular type and quantity of beer.  In
a running system, a Keg will be instantiated and linked to an active
:ref:`model-kegtap`.  A :ref:`model-drink` recorded against that tap deducts
from the known remaining volume.

Properties
^^^^^^^^^^

====================  ==============  ==========================================
Property              Type            Description
====================  ==============  ==========================================
id                    ``uint32``      A unique identifier for this object.
status                ``string``      Current status of the keg; either "online"
                                      or "offline".
type_id               ``string``      The :ref:`model-beertype` for this beer.
size_id               ``string``      The :ref:`model-kegsize` of this keg.
started_time          ``date``        The time when the keg was first started,
                                      or tapped.
finished_time         ``date``        The time when the keg was finished, or
                                      emptied.  This value is undefined if the
                                      keg's status is not "offline".
*description*         ``string``      A site-specific description of this keg.
percent_full          ``float``       The amount of beer remaining, as a
                                      percentage.
volume_ml_remain      ``float``       Milliliters of beverage remaining.
====================  ==============  ==========================================

Example
^^^^^^^

.. code-block:: javascript
  
  {
    "id" : 3,
    "status" : "online",
    "type_id" : "1a2b",
    "size_id" : "5",
    "started_time" : "2010-01-01T02:00:00+0000",
    "finished_time" : "2010-01-01T02:00:00+0000",
    "description" : "Our New Year's keg.",
    "percent_full" : "20.0",
    "volume_ml_remain" : 11734.78
  }



.. _model-kegsize:

KegSize
-------

A KegSize is a small object that gives a name and a volume to a particular
quantity.

Properties
^^^^^^^^^^

====================  ==============  ==========================================
Property              Type            Description
====================  ==============  ==========================================
id                    ``uint32``      A unique identifier for this object.
name                  ``string``      Name of this size.
volume_ml             ``float``       Total volume of this size.
====================  ==============  ==========================================

Example
^^^^^^^

.. code-block:: javascript
  
  {
    "id" : 1,
    "name" : "Full Keg",
    "volume_ml" : 58673.8826552
  }



.. _model-kegtap:

KegTap
------

Every available beer tap in the system is modeled by a KegTap.

Properties
^^^^^^^^^^

====================  ==============  ==========================================
Property              Type            Description
====================  ==============  ==========================================
id                    ``string``      An opaque, unique identifier for this tap.
name                  ``string``      A short, descriptive name for the tap.
meter_name            ``string``      The name of the flow meter that is
                                      assigned to this tap.
ml_per_tick           ``float``       Volume to record per tick of the
                                      corresponding flow meter.
*description*         ``string``      A longer description of the tap.
*current_keg_id*      ``int``         The :ref:`model-keg` currently assigned to
                                      the tap, if any.
*thermo_sensor_id*    ``string``      The :ref:`model-thermosensor` assigned to
                                      the tap, if any.
====================  ==============  ==========================================

Example
^^^^^^^

.. code-block:: javascript
  
  {
    "id" : "1",
    "name" : "Main Tap",
    "meter_name" : "kegboard.flow0",
    "ml_per_tick" : 0.4545,
    "description" : "Primary kegboard, main tap.",
    "current_keg_id" : 1,
    "thermo_sensor_id" : "1",
  }



.. _model-session:

Session
-------

A Session is used to group drinks that are close to eachother in time.  Every
:ref:`model-drink` is assigned to a session.

Properties
^^^^^^^^^^

====================  ==============  ==========================================
Property              Type            Description
====================  ==============  ==========================================
id                    ``string``      An opaque, unique identifier for this
                                      session.
start_time            ``date``        The time of the first :ref:`model-drink`
                                      in the session.
end_time              ``date``        The time of the last (most recent)
                                      :ref:`model-drink` in the session.
volume_ml             ``float``       Total volume poured, among all drinks in
                                      the session.
====================  ==============  ==========================================

Example
^^^^^^^

.. code-block:: javascript
  
  {
    "id" : "17",
    "start_time" : "2010-08-14T04:00:00+0000",
    "end_time" : "2010-08-14T07:00:00+0000",
    "volume_ml" : 12000.0
  }



.. _model-thermolog:

ThermoLog
---------

Temperature sensors emit periodic data, which are recorded as ThermoLog records.

Properties
^^^^^^^^^^

====================  ==============  ==========================================
Property              Type            Description
====================  ==============  ==========================================
id                    ``string``      An opaque, unique identifier for this log
                                      entry.
sensor_id             ``string``      The :ref:`model-thermosensor` which
                                      recorded the entry.
temperature_c         ``float``       Temperature, in degrees celcius.
record_time           ``date``        Time of recording.
====================  ==============  ==========================================

Example
^^^^^^^

.. code-block:: javascript
  
  {
    "id" : "1234",
    "sensor_id" : "1",
    "temperature_c" : 23.0,
    "record_time" : "2010-06-06T16:00:00+0000"
  }



.. _model-thermosensor:

ThermoSensor
------------

Represents a temperature sensor in the Kegbot system.

Properties
^^^^^^^^^^

====================  ==============  ==========================================
Property              Type            Description
====================  ==============  ==========================================
id                    ``string``      An opaque, unique identifier for this
                                      sensor.
sensor_name           ``string``      The raw and unique name for the sensor.
nice_name             ``string``      A human-readable, descriptive name for the
                                      sensor.
====================  ==============  ==========================================

Example
^^^^^^^

.. code-block:: javascript
  
  {
    "id" : "1",
    "sensor_name" : "kegboard.thermo-fd0000009b90ac28",
    "nice_name" : "fridge sensor"
  }



.. _model-user:

User
----

This object models a User in the system.

Properties
^^^^^^^^^^

====================  ==============  ==========================================
Property              Type            Description
====================  ==============  ==========================================
username              ``username``    Unique identifier for the user.
is_active             ``bool``        True if this is an active user.
mugshot_url           ``url``         URL to the mugshot for this user.
is_staff              ``bool``        True if this user is a staff member.
is_superuser          ``bool``        True if this user is the keg master.
joined_time           ``date``        Date when the user first registered.
====================  ==============  ==========================================

Example
^^^^^^^

.. code-block:: javascript
  
  {
    "username" : "mikey",
    "is_active" : true,
    "mugshot_url" : "http://sfo.kegbot.net/media/mugshots/mikey/a12b-mikey-kegbot.jpg",
    "is_staff" : true,
    "is_superuser" : true,
    "joined_time" : "2004-01-01T12:00:00+0000"
  }



.. _model-usersession:

UserSession
-----------

A UserSession describe's a particular user's contribution to a
:ref:`model-session`.

Properties
^^^^^^^^^^

====================  ==============  ==========================================
Property              Type            Description
====================  ==============  ==========================================
id                    ``string``      An opaque, unique identifier for this
                                      sensor.
session_id            ``string``      The :ref:`model-session` which this is
                                      part of.
username              ``string``      Username of the :ref:`model-user`
                                      responsible for this portion.
start_time            ``date``        Time of the user's first activity.
end_time              ``date``        Time of the user's last activity.
volume_ml             ``float``       Total volume poured by this user in the
                                      session.
====================  ==============  ==========================================

Example
^^^^^^^

.. code-block:: javascript
  
  {
    "id" : "42",
    "session_id" : "17",
    "username" : "mikey",
    "start_time" : "2010-08-14T04:00:00+0000",
    "end_time" : "2010-08-14T04:00:00+0000",
    "volume_ml" : 2000.0
  }



