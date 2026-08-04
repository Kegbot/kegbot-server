.. _kegboards:

Kegboards
=========

Kegboard v4 controllers report to the server over HTTP using the kegboard
event protocol. The server receives batches of events — pours, temperature
readings, token presentments, and heartbeats — at::

  POST /api/kegboard-event

Configure the board with this URL (path included). Everything else is
driven from the server.

Pairing a board
---------------

Boards authenticate with a bearer token that the server provisions; you
never handle a credential yourself:

1. Point the board at your server's ``/api/kegboard-event`` URL.
2. Open **Admin → Controllers**. The board announces itself and appears
   in the *Kegboards* section within a few seconds, with its first-seen
   time and source address.
3. Click **Allow**. This creates a controller for the board and stages
   its token; the board picks it up on its next check-in (within
   seconds) and starts delivering events. Events that occurred before
   pairing were queued on the board and deliver afterwards.

Click **Deny** to refuse a board; it stays listed so the decision can be
reversed. To disconnect a paired board, delete its controller — this
also invalidates the board's token, so it reappears for pairing on its
next check-in (drinks are kept). Re-allowing a board always issues a
fresh token.

Use TLS for the reporting URL whenever possible: the token is a plain
bearer credential.

What gets recorded
------------------

* **Pours** become drinks on the tap bound to the reporting meter
  (bind meters to taps from each tap's admin page). The board's own
  calibrated volume is authoritative. Pours on unbound meters are
  logged and dropped.
* **Meters** are created automatically (``flow0``, ``flow1``, ...) from
  the board's status reports, including calibration.
* **Temperature readings** are logged against auto-created sensors named
  ``<controller>.<sensor>``.
* **Token presentments** are checked against the token database
  (**Admin → Tokens**): an active, assigned token authorizes pouring on
  the board's meters for 30 seconds; anything else is refused.
* **Heartbeats** drive the liveness, firmware, signal, and dropped-event
  columns in the Kegboards section.
