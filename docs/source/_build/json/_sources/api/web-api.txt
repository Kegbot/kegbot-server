.. _web-api:

.. |webapi-version| replace:: 1.0

==============
Kegbot Web API
==============

.. warning::
  The Kegbot Web API is a work in progress. It will not be considered stable
  until Kegbot v1.0 is released.

.. warning::
  Example responses need to be updated. Consult a live Kegbot instance if in
  doubt.

Overview
========

The Kegbot Web API aims to provide a simple, HTTP-accessible interface to the
most commonly-needed Kegbot system data.  The API is modeled after popular APIs
from `Twitter <http://apiwiki.twitter.com/>`_, `Facebook
<http://developers.facebook.com/>`_, and others.

This document describes the current verison of the web API, version
|webapi-version|.  For a summary of changes, see :ref:`api-changelog`

Core Concepts
=============

URL Scheme
----------

This document describes several endpoints, which are HTTP URLs serviced by the API.
Each endpoint corresponds some function or query against the Kegbot system.

Endpoints follow a predictable URL scheme whenever possible. The general
convention is ``/<noun>/<id>/``, or ``/<noun>/<id>/<subresource>/``. The
``noun`` portion is typically a pluralized core Kegbot data type: "kegs",
"drinks", and so on.  The ``id`` portion is a unique identifier for that type of
noun (typically a string or opaque id).

For example, ``/users/mikey`` returns basic information about that user, and
``/users/mikey/drinks`` returns his detailed drink list.

Data Format
-----------

The response from an endpoint is a well-formed JSON dictionary.  Under normal
circumstances, the response dictionary will consist of a single top-level entry
named ``result``, containing the endpoint's specific response data.  The actual
contents of the ``result`` field vary, and are determined by the endpoint.

Dates and times are always expressed in the UTC time zone.

Error Handling
--------------

If an error occurred or the request could not be processed, the response will
instead have the top-level field ``error``, as shown below:

.. code-block:: javascript
  
  {
    "error" : {
      "code" : "PermissionDenied",
      "message" : "You do not have permission to view this resource."
    }
  }

The ``code`` field lists a specific error code, and the ``message`` field
contains a human-readable explanation.  For a complete list of possible error
codes, see :ref:`api-error-codes`.

In addition to the Kegbot error codes, the API server will also use HTTP status
codes to indicate success (200) or failure (400).  Clients *must* handle
non-200 responses, which may be caused by heavy load, server error, or other
exceptional circumstances.

.. _api-pagination:

Pagination
----------

In some cases, Kegbot limits the number of records it will return in a single
query.  For these queries, an additional top-level field ``paging`` will appear
in a successful response.  See the :ref:`api-drink-list` section for an
example.

Most endpoints do *not* paginate their results; those that do must specify this
behavior.


.. _api-security:

Security & Authentication
-------------------------

Most endpoints are considered **Public**, and can be accessed by any HTTP
client without authentication.

Some endpoints and actions, such as publishing a drink, require a secret key
in order to be processed, called the *api_key*.  All registered staff and
superuser accounts have api access.  The key can be determined by logging in to
your account profile and navigating to ``/account/``.  Example value:

  100000018fe5b1e373a18d7dbb3e51917058aaa7

When required, the token should be given as either an HTTP ``GET`` or ``POST``
parameter named ``api_key``.

Publishing
----------

In addition to reading and querying data, the web API can be used for inserting
and modifying records.  These are implemented as HTTP ``POST`` operations.

.. _api-endpoints:

GET Endpoints
=============

The following endpoints provide read access to various Kegbot data.  All are
accessible with HTTP GET operations.


.. _api-drink-list:

``/drinks``
-----------

Listing of a drinks poured on the current Kegbot system.  The results *may* be
paginated; see :ref:`api-pagination` for details.  Results are sorted by drink
id, in decreasing order.

**Default Access:** Public

Arguments
^^^^^^^^^

====================  ==========================================================
Argument              Description
====================  ==========================================================
start                 First drink ID to show. *Default will start with the most
                      recent drink.*
====================  ==========================================================

Response
^^^^^^^^

====================  =======================  ==========================================
Property              Type                     Description
====================  =======================  ==========================================
drinks                :ref:`model-drinkset`    A sequence of :ref:`model-drink` objects
====================  =======================  ==========================================

Example
^^^^^^^

.. code-block:: javascript
  
  // curl http://sfo.kegbot.net/api/drinks/?start=2000
  {
    "result": {
      "paging": {
        "total": 2716, 
        "limit": 100, 
        "pos": 2000
      }, 
      "drinks": [
        {
          "volume_ml": 490.24793744200002, 
          "user_id": "capn", 
          "ticks": 1321, 
          "session_id": "386", 
          "is_valid": true, 
          "pour_time": "2009-10-03T17:13:16", 
          "duration": 15, 
          "keg_id": 13, 
          "id": 2000
        }, 
        {
          "volume_ml": 451.651582034, 
          "user_id": "boysdontcall", 
          "ticks": 1217, 
          "session_id": "386", 
          "is_valid": true, 
          "pour_time": "2009-10-03T17:12:27", 
          "duration": 14, 
          "keg_id": 13, 
          "id": 1999
        }, 
        // ...
      ]
    }
  }


.. _api-drink-detail:

``/drinks/<id>/``
-----------------

Detailed information about a single specific drink.

**Default Access:** Public

Response
^^^^^^^^

====================  ==============  ==========================================
Property              Type            Description
====================  ==============  ==========================================
drink                 ``dict``        The :ref:`model-drink` object
                                      corresponding to this drink
keg                   ``dict``        The :ref:`model-keg` object
                                      corresponding to this drink
user                  ``dict``        The :ref:`model-user` object
                                      corresponding to this drink
session               ``dict``        The :ref:`model-session` object
                                      corresponding to this drink
====================  ==============  ==========================================

Example
^^^^^^^

.. code-block:: javascript
  
  // curl http://sfo.kegbot.net/api/drinks/2000/
  {
    "result": {
      "keg": {
        "status": "offline", 
        "volume_ml_remain": 590.74554188041657, 
        "finished_time": "2009-10-17T19:34:06", 
        "description": "Racer 5", 
        "type_id": "50ad52bc-35fb-4441-a5bf-f56a55608057", 
        "started_time": "2009-09-06T14:46:00", 
        "size_id": 1, 
        "percent_full": 0.010068330147789123, 
        "id": 13
      }, 
      "drink": {
        "volume_ml": 490.24793744200002, 
        "user_id": "capn", 
        "ticks": 1321, 
        "session_id": "386", 
        "is_valid": true, 
        "pour_time": "2009-10-03T17:13:16", 
        "duration": 15, 
        "keg_id": 13, 
        "id": 2000
      }, 
      "user": {
        "username": "capn", 
        "joined_time": "2004-05-22T20:24:16", 
        "mugshot_url": "mugshots/brian-wtf-hula-thing.jpg", 
        "is_active": true, 
        "is_superuser": false, 
        "is_staff": false
      }, 
      "session": {
        "start_time": "2009-10-03T16:33:07", 
        "volume_ml": 0.0, 
        "id": "386", 
        "end_time": "2009-10-03T20:26:24"
      }
    }
  } 


``/taps/``
----------

Listing of all taps in the system.

**Default Access:** Public

Response
^^^^^^^^

*Note:* The response is a list with property name *taps*, containing zero or
more of the following structure.

====================  ==============  ==========================================
Property              Type            Description
====================  ==============  ==========================================
tap                   ``dict``        The :ref:`model-kegtap` objects itself
keg                   ``dict``        A :ref:`model-keg` object for the current
                                      keg, or *null*.
beverage              ``dict``        A :ref:`model-beertype` object for the
                                      current keg, or *null*.
====================  ==============  ==========================================

Example
^^^^^^^

.. code-block:: javascript
  
  // curl http://sfo.kegbot.net/api/taps/
  {
    "result": {
      "taps": [
        {
          "keg": {
            "status": "online", 
            "volume_ml_remain": 299.24664065039542, 
            "finished_time": "2010-06-11T23:25:16", 
            "description": "Celebrating the World Cup, and international relations, with a beer that's part Austria / part Berkeley.", 
            "type_id": "20bd3f32-75eb-11df-80f2-00304833977c", 
            "started_time": "2010-06-11T23:25:16", 
            "size_id": 1, 
            "percent_full": 0.0051001891001911156, 
            "id": 17
          }, 
          "tap": {
            "meter_name": "kegboard.flow0", 
            "name": "main tap", 
            "ml_per_tick": 0.37111880200000003, 
            "thermo_sensor_id": "1", 
            "current_keg_id": 17, 
            "id": "1"
          }
        }
      ]
    }
  }


.. _api-tap-detail:

``/taps/<id>/``
---------------

Shows detailed information about a single tap.

**Default Access:** Public

Response
^^^^^^^^

====================  ==============  ==========================================
Property              Type            Description
====================  ==============  ==========================================
tap                   ``dict``        The :ref:`model-kegtap` objects itself
keg                   ``dict``        A :ref:`model-keg` object for the current
                                      keg, or *null*.
====================  ==============  ==========================================

Example
^^^^^^^

.. code-block:: javascript
  
  // curl http://sfo.kegbot.net/api/taps/kegboard.flow0/
  {
    "result": {
      "keg": {
        "status": "online", 
        "volume_ml_remain": 299.24664065039542, 
        "finished_time": "2010-06-11T23:25:16", 
        "description": "Celebrating the World Cup, and international relations, with a beer that's part Austria / part Berkeley.", 
        "type_id": "20bd3f32-75eb-11df-80f2-00304833977c", 
        "started_time": "2010-06-11T23:25:16", 
        "size_id": 1, 
        "percent_full": 0.0051001891001911156, 
        "id": 17
      }, 
      "tap": {
        "meter_name": "kegboard.flow0", 
        "name": "main tap", 
        "ml_per_tick": 0.37111880200000003, 
        "thermo_sensor_id": "1", 
        "current_keg_id": 17, 
        "id": "1"
      }
    }


``/kegs/``
----------

Lists all kegs known by the system. The response to this query *may* be
paginated.

**Default Access:** Public

Response
^^^^^^^^

====================  ==============  ==========================================
Property              Type            Description
====================  ==============  ==========================================
keg                   ``dict``        A :ref:`model-keg` object corresponding
                                      to the keg.
====================  ==============  ==========================================

Example
^^^^^^^

.. code-block:: javascript
  
  // curl http://sfo.kegbot.net/api/kegs/
  {
    "result": {
      "kegs": [
        {
          "status": "online", 
          "volume_ml_remain": 299.24664065039542, 
          "finished_time": "2010-06-11T23:25:16", 
          "description": "Celebrating the World Cup, and international relations, with a beer that's part Austria / part Berkeley.", 
          "type_id": "20bd3f32-75eb-11df-80f2-00304833977c", 
          "started_time": "2010-06-11T23:25:16", 
          "size_id": 1, 
          "percent_full": 0.0051001891001911156, 
          "id": 17
        }, 
        {
          "status": "offline", 
          "volume_ml_remain": -13363.120936177656, 
          "finished_time": "2010-05-29T13:01:20", 
          "description": "Memorial Day keg.", 
          "type_id": "e29a5d90-6b5c-11df-bcbc-00304833977c", 
          "started_time": "2010-05-29T13:01:20", 
          "size_id": 1, 
          "percent_full": -0.22775341302110927, 
          "id": 16
        }, 
        // ...
      ]
    }
  }

.. _api-keg-detail:

``/kegs/<id>/``
---------------

Detailed information about a specific keg.

**Default Access:** Public

Response
^^^^^^^^

====================  ==============  ==========================================
Property              Type            Description
====================  ==============  ==========================================
keg                   ``multiple``    The :ref:`model-keg` object for this keg.
type                  ``dict``        The :ref:`model-beertype` object for this
                                      keg, or *null*
size                  ``dict``        The :ref:`model-kegsize` object for this
                                      keg, or *null*
drinks                ``multiple``    A listing of individual :ref:`model-drink`
                                      objects poured on this keg.
====================  ==============  ==========================================

Example
^^^^^^^

.. code-block:: javascript
  
  // curl http://sfo.kegbot.neg/api/kegs/13/
  {
    "result": {
      "keg": {
        "status": "offline", 
        "volume_ml_remain": 590.74554188041657, 
        "finished_time": "2009-10-17T19:34:06", 
        "description": "Racer 5", 
        "type_id": "50ad52bc-35fb-4441-a5bf-f56a55608057", 
        "started_time": "2009-09-06T14:46:00", 
        "size_id": 1, 
        "percent_full": 0.010068330147789123, 
        "id": 13
      }, 
      "type": {
        "name": "Racer 5", 
        "style_id": "8afc60f5-2ee0-40a2-a53a-39c6f43ed4bf", 
        "calories_oz": 12.5, 
        "abv": 7.2000000000000002, 
        "brewer_id": "4360bae4-5522-4fca-8e3a-0edebfc457a5", 
        "id": "50ad52bc-35fb-4441-a5bf-f56a55608057"
      }, 
      "size": {
        "volume_ml": 58673.636363636397, 
        "id": 1, 
        "name": "15.5 gallon keg"
      }
      "drinks": [
        {
          "volume_ml": 55.667820300000002, 
          "user_id": "scarfjerk", 
          "ticks": 150, 
          "session_id": "390", 
          "is_valid": true, 
          "pour_time": "2009-10-17T19:34:06", 
          "duration": 7, 
          "keg_id": 13, 
          "id": 2054
        }, 
        {
          "volume_ml": 441.63137438000001, 
          "user_id": null, 
          "ticks": 1190, 
          "session_id": "390", 
          "is_valid": true, 
          "user": null, 
          "pour_time": "2009-10-17T19:02:55", 
          "duration": 11, 
          "keg_id": 13, 
          "id": 2053
        }, 
        // ...
      ], 
    }
  }

``/kegs/<id>/drinks/``
----------------------

Lists all drinks assigned to a specific keg.  This is the same content as the
*drinks* portion of the :ref:`api-keg-detail` endpoint.

* **Default Access:** Public

Response
^^^^^^^^

====================  ==============  ==========================================
Property              Type            Description
====================  ==============  ==========================================
drinks                ``multiple``    A listing of individual :ref:`model-drink`
                                      objects poured on this keg.
====================  ==============  ==========================================

Example
^^^^^^^

.. code-block:: javascript
  
  // curl http://sfo.kegbot.net/api/kegs/13/drinks/
  {
    "result": {
      "drinks": [
        {
          "volume_ml": 55.667820300000002, 
          "user_id": "scarfjerk", 
          "ticks": 150, 
          "session_id": "390", 
          "is_valid": true, 
          "pour_time": "2009-10-17T19:34:06", 
          "duration": 7, 
          "keg_id": 13, 
          "id": 2054
        }, 
        {
          "volume_ml": 441.63137438000001, 
          "user_id": null, 
          "ticks": 1190, 
          "session_id": "390", 
          "is_valid": true, 
          "user": null, 
          "pour_time": "2009-10-17T19:02:55", 
          "duration": 11, 
          "keg_id": 13, 
          "id": 2053
        }, 
      ]
    }
  }

``/kegs/<id>/sessions/``
------------------------

Lists all sessions involving specific keg.

**Default Access:** Public

Response
^^^^^^^^

====================  ==============  ==========================================
Property              Type            Description
====================  ==============  ==========================================
sessions              ``multiple``    A listing of individual
                                      :ref:`model-session` objects involving
                                      this keg.
====================  ==============  ==========================================

``/users/<id>/``
----------------

Lists detail about a single user.

**Default Access:** Public

Response
^^^^^^^^

====================  ==============  ==========================================
Property              Type            Description
====================  ==============  ==========================================
user                  ``dict``        A :ref:`model-user` object corresponding
                                      to the user.
====================  ==============  ==========================================

Example
^^^^^^^

.. code-block:: javascript

  // curl http://sfo.kegbot.net/api/users/mikey/
  {
    "result": {
      "user": {
        "username": "mikey", 
        "joined_time": "2004-05-22T20:22:39Z", 
        "mugshot_url": "mugshots/mikey/a12b-mikey-kegbot.jpg", 
        "is_active": true, 
      }
    }
  }

``/users/<id>/drinks/``
-----------------------

Lists all drinks by a specific user.

**Default Access:** Public

Response
^^^^^^^^

====================  ==============  ==========================================
Property              Type            Description
====================  ==============  ==========================================
drinks                ``multiple``    A listing of individual :ref:`model-drink`
                                      objects poured on this keg.
====================  ==============  ==========================================

Example
^^^^^^^

.. code-block:: javascript
  
  // curl http://sfo.kegbot.net/api/users/mikey/drinks/
  {
    "result": {
      "drinks": [
        {
          "volume_ml": 453.13605724199999, 
          "user_id": "mikey", 
          "ticks": 1221, 
          "session_id": "421", 
          "is_valid": true, 
          "pour_time": "2010-08-22T02:55:53Z", 
          "duration": 12, 
          "keg_id": 17, 
          "id": 2694
        }, 
        {
          "volume_ml": 333.26468419600002, 
          "user_id": "mikey", 
          "ticks": 898, 
          "session_id": "420", 
          "is_valid": true, 
          "pour_time": "2010-08-15T18:35:20Z", 
          "duration": 8, 
          "keg_id": 17, 
          "id": 2686
        }, 
        // ...
      ]
    }
  }


..
  System stats: ``/stats/``
  -------------------------
  
  Gives general statistics about the system, similar to a global leader board.


``/auth-tokens/<id>/``
----------------------

Gives detail about an auth token.

* **Default Access:** Protected

Response
^^^^^^^^

====================  ==============  ==========================================
Property              Type            Description
====================  ==============  ==========================================
token                 ``dict``        A :ref:`model-authtoken` object
                                      corresponding to the user.
====================  ==============  ==========================================

Example
^^^^^^^

.. code-block:: javascript

  // curl -F api_key=1000...aaa7 http://sfo.kegbot.net/api/auth-tokens/test.testval/
  {
    "result": {
      "token": {
        "auth_device": "test", 
        "created_time": "2010-10-13T00:41:01Z", 
        "enabled": true, 
        "id": "test|testval", 
        "token_value": "testval"
      }
    }
  }

.. _api-thermo-detail:

``/thermo-sensors/<id>/``
-------------------------

Gives detail about a thermo sensor in the system.

* **Default Access:** Public


POST Endpoints
==============

Record a Drink
--------------

* **Endpoint:** ``/tap/<id>/``
* **Default Access:** Protected

Posting to a Tap endpoint will record a new drink.

Publish Format
^^^^^^^^^^^^^^

====================  ==============  ==========================================
POST Argument         Format          Description
====================  ==============  ==========================================
ticks                 ``integer``     The number of ticks recorded by the flow
                                      meter on this tap.
volume_ml             ``float``       *Optional.*  If specified, overrides the
                                      default volume calculation (based on the
                                      ticks field) with a specific volume in
                                      milliliters.
username              ``string``      *Optional.*  Gives the username of the
                                      user responsible for the pour.  If
                                      auth_token was also given, the backend
                                      gives precendence to the username field.
pour_time             ``integer``     *Optional.* Unix timestamp corresponding
                                      to the date the pour was completed.  If
                                      this field is given, the field 'now' must
                                      also be given.  If this field is not
                                      given, the backend will use the current
                                      time when the request is processed.
now                   ``integer``     *Optional.* Unix timestamp corresponding
                                      to the current time; the backend uses this
                                      to compensate for any skew in system
                                      clocks.  Only meaningful when 'pour_time'
                                      is also given, dicarded otherwise.
duration              ``integer``     *Optional.*  Gives the time taken, in
                                      seconds, to complete the pour.  This is
                                      used purely for trivia/statistical
                                      purposes.
auth_token            ``string``      *Optional.*  If known, gives the auth
                                      token ID used during the pour.  If
                                      username is not specified, this value will
                                      be used by the backend to attempt to
                                      resolve to a user.  Regardless, the value
                                      is stored with the drink record.  (It can
                                      be useful for 'claiming' drinks poured
                                      with an unassigned auth token.)
spilled               ``boolean``     *Optional.*  If true, the pour is recorded
                                      as "spilled": no drink record will be
                                      generated, and the username, pour_time,
                                      auth_token, now, and duration fields are
                                      all ignored.  The volumed will be added to
                                      the spilled total for the tap's current
                                      keg.
====================  ==============  ==========================================

If the tap has an active keg assigned to it, the new drink will be recorded and
accounted for against that keg.  If not, the drink will not be associated with
any keg.

Response
^^^^^^^^

A new drink record is returned on success, in the same format as
:ref:`api-drink-detail`.

Record a temperature
--------------------

* **Endpoint:** ``/thermo-sensor/<id>/``
* **Default Access:** Protected

Posting to a thermo sensor endpoint will record a new temperature sensor
reading.

Publish Format
^^^^^^^^^^^^^^

====================  ==============  ==========================================
POST Argument         Format          Description
====================  ==============  ==========================================
temp_c                ``float``       Temperature, in degrees celcius.
====================  ==============  ==========================================

Response
^^^^^^^^

A new thermo sensor record is returned on success, in the same format as
:ref:`api-thermo-detail`.

Note that the Kegbot backend will record at most one reading, per sensor, per
minute.  If multiple readings are received within a minute, the most recent one
received wins.

.. _api-error-codes:

Error Codes
===========

========================  ======================================================
Error Code                Meaning
========================  ======================================================
Error                     A generic error.
NotFoundError             The object being requested does not exist.  This is
                          served instead of an HTTP 404.
ServerError               The server had a problem serving the request.  This is
                          served instead of an HTTP 500 error code, and probably
                          indicates a bug or temporary server issue.
BadRequestError           The request was incomplete or malformed. For example,
                          when POSTing, this will be thrown when a required
                          value is missing, or when a field's format is
                          incorrect.
NoAuthTokenError          The resource/query is protected and requires
                          an auth token to proceed. (See
                          :ref:`api-security`).
BadAuthTokenError         The provided auth token was invalid.
PermissionDeniedError     The auth token provided does not have permission to
                          perform this operation.
========================  ======================================================

.. _api-changelog:

Version History
===============

============  ===========  ============================================
Date          Version      Comments
============  ===========  ============================================
2010-10-18    0.1          Initial version.
============  ===========  ============================================
