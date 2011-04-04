
.. _data-model:

===========================
Kegbot Data Model Reference
===========================

This document contains a reference of the most commonly used objects in the API.

.. _api-objects:

Object Types
============
.. _model-authenticationtoken:

AuthenticationToken
===================

An authentication token, which a drinker uses to authenticate to the system.


Fields
------

============  =======  ===================================================================================================================
Name          Type     Description
============  =======  ===================================================================================================================
id            string   The unique identifier for this token.
auth_device   string   The name of the auth device that owns this token, such as ``core.onewire`` or ``contrib.phidget.rfid``.
token_value   string   The unique key.
username      string   *(optional)* The user owning the token.
nice_name     string   *(optional)* An optional human-readable name for this token.
enabled       boolean  *(optional)* True if the token is enabled.
created_time  string   The date the token was created, as an ISO8061 UTC timestamp.
expire_time   string   *(optional)* The date after which the token is invalid, as an ISO8061 UTC timestamp. Only available to admin users.
pin           string   *(optional)* The token's pin, if any. Only available to admin users.
============  =======  ===================================================================================================================


.. _model-beerstyle:

BeerStyle
=========

A named beer style of beer, such as "India Pale Ale".


Fields
------

====  ======  ==========================================
Name  Type    Description
====  ======  ==========================================
id    string  The unique identifier for this beer style.
name  string  The name of the beer style.
====  ======  ==========================================


.. _model-beertype:

BeerType
========

A specific kind of beer: describes the beer's name, style, and brewer.


Fields
------

================  ==================  =====================================================================================
Name              Type                Description
================  ==================  =====================================================================================
id                string              The unique identifier for this beer type.
name              string              The brand name of the beer.
brewer_id         string              Brewer information for the beer.  May refer to an 'unknown' or generic brewer record.
style_id          string              Style information for the beer.  May refer to an 'unknown' or generic beer style.
edition           string              *(optional)* For seasonal or special edition beers, the year or other edition name.
abv               float               *(optional)* Alcohol by volume, as a percentage of the total volume.
calories_oz       float               *(optional)* Number of calories per ounce of beverage.
carbs_oz          float               *(optional)* Number of carbohydrates per ounce of beverage.
specific_gravity  float               *(optional)* Specific/final gravity of the beer, if known.
original_gravity  float               *(optional)* Original gravity of the beer, if known.
image             :ref:`model-image`  *(optional)* Image for this beer.
================  ==================  =====================================================================================


.. _model-brewer:

Brewer
======

A specific producer of our favorite beverage.


Fields
------

============  ==================  ========================================================================
Name          Type                Description
============  ==================  ========================================================================
id            string              The unique identifier for this beer type.
name          string              The name of the brewer.
country       string              *(optional)* The country of the brewer's headquarters.
origin_state  string              *(optional)* The state of the brewer's headquarters.
origin_city   string              *(optional)* The city of the brewer's headquarters.
production    string              *(optional)* Type of production (usually either 'retail' or 'homebrew').
url           string              *(optional)* URL of brewer.
description   string              *(optional)* Free-form description.
image         :ref:`model-image`  *(optional)* Image or logo for this brewer.
============  ==================  ========================================================================


.. _model-drink:

Drink
=====

Describes a single recorded pour from the Kegbot.


Fields
------

=============  =======  ===============================================================================================================
Name           Type     Description
=============  =======  ===============================================================================================================
id             string   The unique identifier for this drink.
ticks          integer  The number of meter ticks recorded for the drink.
volume_ml      float    The volume of the drink, in milliliters.
session_id     string   The session this drink belongs to.
pour_time      string   UTC time when the drink was poured, as an ISO8061 UTC timestamp.
duration       integer  *(optional)* Duration, in seconds, of the pour.
status         string   Status of the drink.
keg_id         string   *(optional)* The Keg from which the drink was poured.  May be unset if the drink was not associated with a keg.
user_id        string   *(optional)* The User that poured the drink.  Snset if the drinker was unknown (anonymous pour).
auth_token_id  string   *(optional)* Auth token value used to pour the drink, if known.
=============  =======  ===============================================================================================================


.. _model-image:

Image
=====

Describes an image.


Fields
------

======  =======  ===============================================
Name    Type     Description
======  =======  ===============================================
url     string   The URL of the original image.
width   integer  *(optional)* The width of the image in pixels.
height  integer  *(optional)* The height of the image in pixels.
======  =======  ===============================================


.. _model-keg:

Keg
===

A single instance of a Keg that was attached to the Kegbot.


Fields
------

================  ======  =======================================================================================================================================================================================================
Name              Type    Description
================  ======  =======================================================================================================================================================================================================
id                string  The unique identifier for this keg.
type_id           string  The kind of beer within the keg.
size_id           string  The size of the keg.
size_name         string  *(optional)* The name of the keg size.
size_volume_ml    float   *(optional)* The volume of the keg size.
volume_ml_remain  float   Volume remaining in the keg, in milliliters.
percent_full      float   Percentage of the keg that remains, as a value between 0 and 100.
started_time      string  UTC time when the keg was started or tapped, as an ISO8061 UTC timestamp.
finished_time     string  Local time when the keg was completed, as an ISO8061 UTC timestamp.  This should be no sooner than the time of the most recent drink.  If the keg's `status` is not 'offline', this value is undefined.
status            string  The keg's current status.  Typically either "online" or "offline".
description       string  *(optional)* The adminstrator's description of this keg.
spilled_ml        float   *(optional)* Total portion of the original volume that was spoiled, in milliliters. Spilled volume is not attributed to any drink, but deducts from the keg total.
================  ======  =======================================================================================================================================================================================================


.. _model-kegsize:

KegSize
=======

A common keg size.


Fields
------

=========  ======  =====================================================
Name       Type    Description
=========  ======  =====================================================
id         string  The unique identifier for this keg size.
name       string  The name of the size ("Half Barrel", "Pony keg", ...)
volume_ml  float   The volume of the size, in milliliters.
=========  ======  =====================================================


.. _model-kegtap:

KegTap
======

Describes a tap which is available for pouring beer.


Fields
------

================  ======================  ================================================================================================
Name              Type                    Description
================  ======================  ================================================================================================
id                string                  The unique identifier for this tap.
name              string                  The name of the tap, a free-form string ("Main tap", "Wet bar", ...)
meter_name        string                  The name of the flow meter assigned to this tap.
relay_name        string                  *(optional)* The relay name of the tap.
ml_per_tick       float                   Size of each flowmeter tick, in milliliters.
description       string                  *(optional)* A longer description of the tap.
current_keg_id    string                  *(optional)* The Keg currently assigned to the tap.  May be unset if there is no keg configured.
thermo_sensor_id  string                  *(optional)* The temperature sensor for the tap, if any.
last_temperature  :ref:`model-thermolog`  *(optional)* The last temperature log, if any.
================  ======================  ================================================================================================


.. _model-session:

Session
=======

A session is a group of drinks occuring within the same time window.  Every
poured drink will be associated with exactly one session.


Fields
------

==========  ======  ===============================================================
Name        Type    Description
==========  ======  ===============================================================
id          string  The unique identifier for this session.
start_time  string  The time this session was started, as an ISO8061 UTC timestamp.
end_time    string  The time this session ended, as an ISO8061 UTC timestamp.
volume_ml   float   Total volume poured during this session, in milliliters.
name        string  *(optional)* A name for this session.
slug        string  *(optional)* The slugified name of this session.
==========  ======  ===============================================================


.. _model-thermolog:

ThermoLog
=========

A log entry for a temperature sensor.


Fields
------

=============  ======  ================================================
Name           Type    Description
=============  ======  ================================================
id             string  The unique identifier for this log entry.
sensor_id      string  The sensor id that produced this log entry.
temperature_c  float   The temperature, in degrees C.
record_time    string  The recording date, as an ISO8061 UTC timestamp.
=============  ======  ================================================


.. _model-thermosensor:

ThermoSensor
============

A temperature sensor configured in the system.


Fields
------

===========  ======  ==================================================
Name         Type    Description
===========  ======  ==================================================
id           string  The unique identifier for this temperature sensor.
sensor_name  string  The raw/unique name of the sensor.
nice_name    string  *(optional)* The friendly name for the sensor.
===========  ======  ==================================================


.. _model-thermosummarylog:

ThermoSummaryLog
================

A summarized log for a collection of temperature sensor events.


Fields
------

============  =======  ========================================================================
Name          Type     Description
============  =======  ========================================================================
id            string   The unique identifier for this log.
sensor_id     string   The id of the sensor described by this summary.
date          string   The start date that is covered by this log, as an ISO8061 UTC timestamp.
period        string   The number of seconds follow ``date`` that are captured by this summary.
num_readings  integer  The number of readings in this summary.
min_temp      float    The minimum temperature observed.
max_temp      float    The maximum temperature observed.
mean_temp     float    The mean of all temperatures observed.
============  =======  ========================================================================


.. _model-user:

User
====

A drinker registered in the kegbot system.


Fields
------

============  ==================  =========================================================================================================
Name          Type                Description
============  ==================  =========================================================================================================
username      string              The user's unique username.
image         :ref:`model-image`  *(optional)* The profile picture of the user.  May be unset if the user does not have a profile picture.
is_active     boolean             True if the user is active.  This value will be false for accounts which have been disabled by the admin.
first_name    string              *(optional)* The first name of the user. Not currently used.
last_name     string              *(optional)* The last name of the user. Not currently used.
email         string              *(optional)* The email address of the user. Only available to admin users.
password      string              *(optional)* The password of the user. Only available to admin users.
is_staff      boolean             *(optional)* True if the user is a member of the system's staff. Only available to admin users.
is_superuser  boolean             *(optional)* True if the user is an administrator. Only available to admin users.
last_login    string              *(optional)* UTC time for the user's last login, as ISO8061 string. Only available to admin users.
date_joined   string              *(optional)* UTC time for the user's registration, as ISO8061 string. Only available to admin users.
============  ==================  =========================================================================================================


.. _model-userprofile:

UserProfile
===========

Extended information about a specific user.
Only available to admin users.


Fields
------

========  ======  ===============================================
Name      Type    Description
========  ======  ===============================================
username  string  The user for this profile.
gender    string  *(optional)* The gender of the user.
weight    float   *(optional)* The weight of the user, in pounds.
========  ======  ===============================================


.. _model-sessionchunk:

SessionChunk
============

A SessionChunk describes a specific user's contribution to a specific Keg, in
a specific Session.


Fields
------

==========  ======  =========================================================================
Name        Type    Description
==========  ======  =========================================================================
id          string  The unique identifier for this chunk.
session_id  string  The session id that this chunk corresponds to.
username    string  The username that this chunk corresponds to.
keg_id      string  The keg id that this chunk corresponds to.
start_time  string  The time this user joined this session, as an ISO8061 UTC timestamp.
end_time    string  The last activity for this user in this session, as an ISO8061 timestamp.
volume_ml   float   The total volume poured by the user.
==========  ======  =========================================================================


.. _model-systemevent:

SystemEvent
===========

Describes various events that happen in the system.


Fields
------

==========  ======  ===========================================================================================================================================================================================
Name        Type    Description
==========  ======  ===========================================================================================================================================================================================
id          string  The unqiue identifier for this event.
kind        string  The kind of the event being reported. Current values: ``drink_poured``, ``session_started``, ``session_joined``, ``keg_tapped``, ``keg_ended``.
time        string  The time of this event, as an ISO8061 UTC timestamp.
drink_id    string  *(optional)* If a drink caused this event (as in ``drink_poured``, ``session_started``, and ``session_joined``), this field gives its id.
keg_id      string  *(optional)* If this event relates to a specific keg (as in most events), this field gives its id.
session_id  string  *(optional)* If this event relates to a specific session (as in ``drink_poured``, ``session_started``, and ``session_joined``), this field gives its id.
user_id     string  *(optional)* If this event relates to a specific user (as in ``drink_poured``, ``session_started``, and ``session_joined`` when the user is not anonymous), this field gives the user's id.
==========  ======  ===========================================================================================================================================================================================


.. _model-soundevent:

SoundEvent
==========

An administrator-defined sound file to play for certain pour events.


Fields
------

===============  ======  ================================================================================
Name             Type    Description
===============  ======  ================================================================================
event_name       string  The name of this event.
event_predicate  string  *(optional)* The predicate for the event. Not currently used.
sound_url        string  The URL for the sound file to play during this event.
user             string  *(optional)* A specific username that this event applies to. Not currently used.
===============  ======  ================================================================================


.. _model-paging:

Paging
======

Common


Fields
------

=====  =======  =============
Name   Type     Description
=====  =======  =============
total  integer  *(optional)* 
limit  integer  *(optional)* 
pos    integer  *(optional)* 
=====  =======  =============


.. _model-drinkset:

DrinkSet
========

Responses


Fields
------

======  =======================  ================================================
Name    Type                     Description
======  =======================  ================================================
drinks  :ref:`model-drink` list  A list of :ref:`model-drink` objects
paging  :ref:`model-paging`      *(optional)* A single :ref:`model-paging` object
======  =======================  ================================================


.. _model-kegset:

KegSet
======

Fields
------

======  =====================  ================================================
Name    Type                   Description
======  =====================  ================================================
kegs    :ref:`model-keg` list  A list of :ref:`model-keg` objects
paging  :ref:`model-paging`    *(optional)* A single :ref:`model-paging` object
======  =====================  ================================================


.. _model-sessionset:

SessionSet
==========

Fields
------

========  =========================  ================================================
Name      Type                       Description
========  =========================  ================================================
sessions  :ref:`model-session` list  A list of :ref:`model-session` objects
paging    :ref:`model-paging`        *(optional)* A single :ref:`model-paging` object
========  =========================  ================================================


.. _model-systemeventset:

SystemEventSet
==============

Fields
------

======  =============================  ================================================
Name    Type                           Description
======  =============================  ================================================
events  :ref:`model-systemevent` list  A list of :ref:`model-systemevent` objects
paging  :ref:`model-paging`            *(optional)* A single :ref:`model-paging` object
======  =============================  ================================================


.. _model-systemeventdetailset:

SystemEventDetailSet
====================

Fields
------

======  ===================================  ================================================
Name    Type                                 Description
======  ===================================  ================================================
events  :ref:`model-systemeventdetail` list  A list of :ref:`model-systemeventdetail` objects
paging  :ref:`model-paging`                  *(optional)* A single :ref:`model-paging` object
======  ===================================  ================================================


.. _model-systemeventhtmlset:

SystemEventHtmlSet
==================

Fields
------

======  =================================  ================================================
Name    Type                               Description
======  =================================  ================================================
events  :ref:`model-systemeventhtml` list  A list of :ref:`model-systemeventhtml` objects
paging  :ref:`model-paging`                *(optional)* A single :ref:`model-paging` object
======  =================================  ================================================


.. _model-soundeventset:

SoundEventSet
=============

Fields
------

======  ============================  ================================================
Name    Type                          Description
======  ============================  ================================================
events  :ref:`model-soundevent` list  A list of :ref:`model-soundevent` objects
paging  :ref:`model-paging`           *(optional)* A single :ref:`model-paging` object
======  ============================  ================================================


.. _model-tapdetailset:

TapDetailSet
============

Fields
------

======  ===========================  ================================================
Name    Type                         Description
======  ===========================  ================================================
taps    :ref:`model-tapdetail` list  A list of :ref:`model-tapdetail` objects
paging  :ref:`model-paging`          *(optional)* A single :ref:`model-paging` object
======  ===========================  ================================================


.. _model-drinkdetailhtmlset:

DrinkDetailHtmlSet
==================

Fields
------

======  =================================  ================================================
Name    Type                               Description
======  =================================  ================================================
drinks  :ref:`model-drinkdetailhtml` list  A list of :ref:`model-drinkdetailhtml` objects
paging  :ref:`model-paging`                *(optional)* A single :ref:`model-paging` object
======  =================================  ================================================


.. _model-thermosensorset:

ThermoSensorSet
===============

Fields
------

=======  ==============================  ================================================
Name     Type                            Description
=======  ==============================  ================================================
sensors  :ref:`model-thermosensor` list  A list of :ref:`model-thermosensor` objects
paging   :ref:`model-paging`             *(optional)* A single :ref:`model-paging` object
=======  ==============================  ================================================


.. _model-thermologset:

ThermoLogSet
============

Fields
------

======  ===========================  ================================================
Name    Type                         Description
======  ===========================  ================================================
logs    :ref:`model-thermolog` list  A list of :ref:`model-thermolog` objects
paging  :ref:`model-paging`          *(optional)* A single :ref:`model-paging` object
======  ===========================  ================================================


.. _model-tapdetail:

TapDetail
=========

Fields
------

=========  =====================  ==================================================
Name       Type                   Description
=========  =====================  ==================================================
tap        :ref:`model-kegtap`    A single :ref:`model-kegtap` object
keg        :ref:`model-keg`       *(optional)* A single :ref:`model-keg` object
beer_type  :ref:`model-beertype`  *(optional)* A single :ref:`model-beertype` object
brewer     :ref:`model-brewer`    *(optional)* A single :ref:`model-brewer` object
=========  =====================  ==================================================


.. _model-drinkdetail:

DrinkDetail
===========

Fields
------

=======  ====================  =================================================
Name     Type                  Description
=======  ====================  =================================================
drink    :ref:`model-drink`    A single :ref:`model-drink` object
user     :ref:`model-user`     *(optional)* A single :ref:`model-user` object
keg      :ref:`model-keg`      *(optional)* A single :ref:`model-keg` object
session  :ref:`model-session`  *(optional)* A single :ref:`model-session` object
=======  ====================  =================================================


.. _model-sessiondetail:

SessionDetail
=============

Fields
------

=======  =====================  ====================================
Name     Type                   Description
=======  =====================  ====================================
session  :ref:`model-session`   A single :ref:`model-session` object
stats    string                 *(optional)* 
kegs     :ref:`model-keg` list  A list of :ref:`model-keg` objects
=======  =====================  ====================================


.. _model-kegdetail:

KegDetail
=========

Fields
------

========  =========================  ==================================================
Name      Type                       Description
========  =========================  ==================================================
keg       :ref:`model-keg`           A single :ref:`model-keg` object
type      :ref:`model-beertype`      *(optional)* A single :ref:`model-beertype` object
size      :ref:`model-kegsize`       *(optional)* A single :ref:`model-kegsize` object
drinks    :ref:`model-drink` list    A list of :ref:`model-drink` objects
sessions  :ref:`model-session` list  A list of :ref:`model-session` objects
========  =========================  ==================================================


.. _model-userdetail:

UserDetail
==========

Fields
------

====  =================  =================================
Name  Type               Description
====  =================  =================================
user  :ref:`model-user`  A single :ref:`model-user` object
====  =================  =================================


.. _model-systemeventdetail:

SystemEventDetail
=================

Fields
------

=====  ========================  ===============================================
Name   Type                      Description
=====  ========================  ===============================================
event  :ref:`model-systemevent`  A single :ref:`model-systemevent` object
image  :ref:`model-image`        *(optional)* A single :ref:`model-image` object
=====  ========================  ===============================================


.. _model-systemeventhtml:

SystemEventHtml
===============

Fields
------

====  ======  =============
Name  Type    Description
====  ======  =============
id    string  
html  string  *(optional)* 
====  ======  =============


.. _model-thermosensordetail:

ThermoSensorDetail
==================

Fields
------

=========  =========================  =========================================
Name       Type                       Description
=========  =========================  =========================================
sensor     :ref:`model-thermosensor`  A single :ref:`model-thermosensor` object
last_temp  float                      *(optional)* 
last_time  string                     *(optional)* 
=========  =========================  =========================================


.. _model-drinkdetailhtml:

DrinkDetailHtml
===============

Fields
------

========  ======  ===========
Name      Type    Description
========  ======  ===========
id        string  
box_html  string  
========  ======  ===========


