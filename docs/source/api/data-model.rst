.. _data-model:

===========================
Kegbot Data Model Reference
===========================

This document contains a reference of the most commonly used objects in the API.

.. _api-objects:

Object Types
============

.. _model-authtoken:

AuthToken
---------

An AuthToken object represents a unique key that identifies a user.

====================  ==============  ==========================================
Property              Type            Description
====================  ==============  ==========================================
id                    ``string``      An opaque, unique identifier for this
                                      object.
auth_device           ``string``      The name of the authentication device
                                      owning this token (for example,
                                      *"onewire"*).
token_value           ``string``      The device-specific token value.  For
                                      instance, on onewire devices, the token
                                      value will be a hexadecimal string giving
                                      the unique 64-bit id.
username              ``string``      The username the token is bound to, or
                                      ``null`` if the token is unassigned.
nice_name             ``string``      An admin-configurable "nice name", or
                                      alias, for this token instance. May be
                                      ``null`` if the token does not have a nice
                                      name.
enabled               ``bool``        Whether the token is active.
created_time          ``date``        The date the token was created or
                                      activated.
expire_time           ``date``        The date after which the token is no
                                      longer valid, or ``null`` if there is no
                                      expiration.
====================  ==============  ==========================================

.. _model-beerstyle:

BeerStyle
---------

A BeerStyle describes a particular style of beer.

====================  ==============  ==========================================
Property              Type            Description
====================  ==============  ==========================================
id                    ``string``      An opaque, unique identifier for this
                                      object.
name                  ``string``      The name of this beer style.
====================  ==============  ==========================================

.. _model-beertype:

BeerType
--------

A BeerType identifies a specific beer, produced by a specific
:ref:`model-brewer`, and often in a particular :ref:`model-beerstyle`.  Several
traits of the beer, such as its alcohol content, may also be given.

====================  ==============  ==========================================
Property              Type            Description
====================  ==============  ==========================================
id                    ``string``      An opaque, unique identifier for this
                                      object.
name                  ``string``      The brand name of the beer.
brewer_id             ``string``      The identifier for the :ref:`model-brewer`
                                      which produces this beer.
style_id              ``string``      The identifier for the style of this beer.
edition               ``string``      For seasonal or special edition version of
                                      a beers, the year or other indicative
                                      name; ``null`` otherwise.
calories_oz           ``float``       The number of calories per fluid ounce of
                                      beer, or ``null`` if not known.
carbs_oz              ``float``       Number of carbohydrates per ounce of
                                      beer, or ``null`` if not known.
abv                   ``float``       Alcohol by volume, as as percentage value
                                      between 0.0 and 100.0, or ``null`` if not
                                      known.
original_gravity      ``float``       Original gravity of this beer, or ``null``
                                      if not known.
specific_gravity      ``float``       Specific gravity of this beer, or ``null``
                                      if not known.
====================  ==============  ==========================================

.. _model-brewer:

Brewer
------

A Brewer is a producer of beer.

====================  ==============  ==========================================
Property              Type            Description
====================  ==============  ==========================================
id                    ``string``      An opaque, unique identifier for this
                                      object.
name                  ``string``      Name of the brewer
country               ``string``      Country where the brewer is based; may be
                                      an empty string.
origin_state          ``string``      State or province where the brewer is
                                      based; may be an empty string.
origin_city           ``string``      City where the brewer is based; may be an
                                      empty string.
production            ``string``      Type of production, either "commercial" or
                                      "homebrew"; may be an empty string.
url                   ``url``         Homepage of the brewer; may be an empty
                                      string.
description           ``string``      Free-form description of the brewer; may
                                      be an empty string.
====================  ==============  ==========================================

.. _model-drink:

Drink
-----

Drink objects represent a specific pour.  Typically, but not always, the Drink
object lists the user known to have poured it, as well as the keg from which it
came.

====================  ==============  ==========================================
Property              Type            Description
====================  ==============  ==========================================
id                    ``string``      An opaque, unique identifier for this
                                      object.
ticks                 ``uint32``      The number of flow meter ticks recorded
                                      for this drink.  Note that this value
                                      should never change once set, regardless
                                      of the volume_ml property.
volume_ml             ``float``       The volume of the pour, in milliliters.
session_id            ``string``      :ref:`model-session` that this drink
                                      belongs to.
pour_time             ``date``        The date of the pour.
duration              ``int``         The duration of the pour, in seconds, or
                                      ``null`` if not known.
status                ``string``      The status of the drink: one of "valid" or
                                      "invalid".
keg_id                ``string``      The :ref:`model-keg` from which the drink
                                      was poured, or ``null`` if not known.
user_id               ``string``      The :ref:`model-user` who poured the
                                      drink, or ``null`` if not known.
auth_token_id         ``string``      The :ref:`model-authtoken` used to pour
                                      the drink, or ``null`` if not known.
====================  ==============  ==========================================

.. _model-keg:

Keg
---

A Keg object records an instance of a particular type and quantity of beer.  In
a running system, a Keg will be instantiated and linked to an active
:ref:`model-kegtap`.  A :ref:`model-drink` recorded against that tap deducts
from the known remaining volume.

====================  ==============  ==========================================
Property              Type            Description
====================  ==============  ==========================================
id                    ``string``      An opaque, unique identifier for this
                                      object.
type_id               ``string``      The :ref:`model-beertype` for this beer.
size_id               ``string``      The :ref:`model-kegsize` of this keg.
size_name             ``string``      The name of the :ref:`model-kegsize` of
                                      this keg.
size_volume_ml        ``float``       The total volume, in milliliters, for the
                                      :ref:`model-kegsize` of this keg.
volume_ml_remain      ``float``       The total volume remaining, in
                                      milliliters.
percent_full          ``float``       The total volume remaining, as a
                                      percentage value between 0.0 and 100.0.
started_time          ``date``        The time when the keg was first started,
                                      or tapped.
finished_time         ``date``        The time when the keg was finished, or
                                      emptied.  This value is undefined if the
                                      keg's status is not "offline".
status                ``string``      Current status of the keg; either "online"
                                      or "offline".
description           ``string``      A site-specific description of this keg,
                                      or ``null`` if not known.
spilled_ml            ``float``       Total volume marked as spilled, in
                                      milliliters.
====================  ==============  ==========================================


.. _model-kegsize:

KegSize
-------

A KegSize is a small object that gives a name and a volume to a particular
quantity.

====================  ==============  ==========================================
Property              Type            Description
====================  ==============  ==========================================
id                    ``string``      An opaque, unique identifier for this
                                      object.
name                  ``string``      Name of this size.
volume_ml             ``float``       Total volume of this size, in
                                      milliliters.
====================  ==============  ==========================================


.. _model-kegtap:

KegTap
------

Every available beer tap in the system is modeled by a KegTap.

====================  ==============  ==========================================
Property              Type            Description
====================  ==============  ==========================================
id                    ``string``      An opaque, unique identifier for this
                                      object.
name                  ``string``      A short, descriptive name for the tap.
meter_name            ``string``      The name of the flow meter that is
                                      assigned to this tap.
ml_per_tick           ``float``       Volume to record per tick of the
                                      corresponding flow meter, in milliliters.
description           ``string``      A longer description of the tap, or
                                      ``null`` if not known.
current_keg_id        ``string``      The :ref:`model-keg` currently assigned to
                                      the tap, or ``null``.
thermo_sensor_id      ``string``      The :ref:`model-thermosensor` assigned to
                                      the tap, or ``null``.
last_temperature      ``float```      The last recorded temperature of the
                                      attached temperature sensor, in degrees C,
                                      or ``null`` if no sensor configured.
====================  ==============  ==========================================

.. _model-session:

Session
-------

A Session is used to group drinks that are close to eachother in time.  Every
:ref:`model-drink` is assigned to a session.

====================  ==============  ==========================================
Property              Type            Description
====================  ==============  ==========================================
id                    ``string``      An opaque, unique identifier for this
                                      object.
start_time            ``date``        The time of the first :ref:`model-drink`
                                      in the session.
end_time              ``date``        The time of the last (most recent)
                                      :ref:`model-drink` in the session.
volume_ml             ``float``       Total volume poured, among all drinks in
                                      the session.
name                  ``string``      A descriptive name for the session; may be
                                      empty if no name has been set.
slug                  ``string``      A variation of the ``name`` field; may be
                                      empty if no name has been set.
====================  ==============  ==========================================

.. _model-systemevent:

System Event
------------

This object describes a system-wide event. System events are generated in
response to drink and keg configuration activity.

====================  ==============  ==========================================
Property              Type            Description
====================  ==============  ==========================================
id                    ``string``      An opaque, unique identifier for this
                                      object.
type                  ``string``      The type of system event.
                                      Currently-defined event types:
                                      drink_poured, session_started,
                                      session_joined, keg_tapped, keg_ended.
time                  ``date``        The time of the event.
drink_id              ``string``      The :ref:`model-drink` that this event
                                      concerns; may be ``null``.
keg_id                ``string``      The :ref:`model-keg` that this event
                                      concerns; may be ``null``.
session_id            ``string``      The :ref:`model-session` that this event
                                      concerns; may be ``null``.
user_id               ``string``      The :ref:`model-user` that this event
                                      concerns; may be ``null``.
====================  ==============  ==========================================

.. _model-thermolog:

ThermoLog
---------

Temperature sensors emit periodic data, which are recorded as ThermoLog records.

====================  ==============  ==========================================
Property              Type            Description
====================  ==============  ==========================================
id                    ``string``      An opaque, unique identifier for this
                                      object.
sensor_id             ``string``      The :ref:`model-thermosensor` which
                                      recorded the entry.
temperature_c         ``float``       Temperature, in degrees celcius.
record_time           ``date``        Time of recording.
====================  ==============  ==========================================


.. _model-thermosensor:

ThermoSensor
------------

Represents a temperature sensor in the Kegbot system.

====================  ==============  ==========================================
Property              Type            Description
====================  ==============  ==========================================
id                    ``string``      An opaque, unique identifier for this
                                      object.
sensor_name           ``string``      The raw and unique name for the sensor.
nice_name             ``string``      A human-readable, descriptive name for the
                                      sensor.
====================  ==============  ==========================================

.. _model-user:

User
----

This object models a User in the system.

====================  ==============  ==========================================
Property              Type            Description
====================  ==============  ==========================================
username              ``username``    Unique identifier for the user.
mugshot_url           ``url``         URL to the mugshot for this user.
is_active             ``bool``        True if this is an active user.
====================  ==============  ==========================================

.. _model-usersession:

UserSession
-----------

A UserSession describe's a particular user's contribution to a
:ref:`model-session`, for a particular :ref:`model-keg`.

====================  ==============  ==========================================
Property              Type            Description
====================  ==============  ==========================================
id                    ``string``      An opaque, unique identifier for this
                                      object.
session_id            ``string``      The :ref:`model-session` that was
                                      contributed to.
username              ``string``      The :ref:`model-user`.
keg_id                ``string``      The :ref:`model-keg` that was contributed
                                      to.
start_time            ``date``        Time of the user's first activity.
end_time              ``date``        Time of the user's last activity.
volume_ml             ``float``       Total volume poured by this user in the
                                      session.
====================  ==============  ==========================================

