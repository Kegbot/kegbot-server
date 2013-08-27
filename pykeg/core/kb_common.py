# Where to look for local_settings.py
LOCAL_SETTINGS_SEARCH_DIRS = (
    '~/.kegbot/',
    '/etc/kegbot/',
    '/usr/local/etc/kegbot',
)

### Drink-related constants

# SF800 default (5400 ticks/Liter == 5.4 ticks/mL == 1/5.4 mL/tick)
ML_PER_TICK = (1/5.4)

# Don't record teeny drinks
MIN_VOLUME_TO_RECORD = 10

# Don't show small drinks
MIN_VOLUME_TO_DISPLAY = 10

# Minimum session size, in milliliters, to display
MIN_SESSION_VOLUME_DISPLAY_ML = 177  # 6 ounces

# Maximum time between consecutive drinks to be considered in the same 'session'
# (see UserDrinkingSession table)
DRINK_SESSION_TIME_MINUTES = 3 * 60

# The maximum difference between consecutive meter readings that is considered
# valid.
MAX_METER_READING_DELTA = 2200*2

# Minimum and maximum thermo sensor readings (degrees C).
THERMO_SENSOR_RANGE = (-20.0, 80.0)

# Maximum number of readings to keep.
THERMO_SENSOR_HISTORY_MINUTES = 60 * 24

# Address the kegnet server should bind to.
KB_CORE_DEFAULT_ADDR = 'localhost:9805'

# String name for all taps
ALIAS_ALL_TAPS = '__all_taps__'

# Device names
AUTH_MODULE_CORE_ONEWIRE = 'core.onewire'
AUTH_MODULE_CORE_RFID = 'core.rfid'
AUTH_MODULE_CONTRIB_PHIDGET_RFID = AUTH_MODULE_CORE_RFID

# Auth modules whose token values should be interpreted as lower-case hex.
AUTH_MODULE_NAMES_HEX_VALUES = (AUTH_MODULE_CORE_ONEWIRE, AUTH_MODULE_CORE_RFID)

# Flag which determines whether an auth device is captive or non-captive.  A
# captive device is one which captures the authentication token, and provides a
# very reliable signal when the token is detached.
#
# For a device marked as captive, the AuthenticationManager will immediately end
# any active flows when a token is removed.  For non-captive (or contactless)
# devices, such as an RFID reader, the authentication manager does nothing when
# the token is removed (see flow timeout, next).
AUTH_DEVICE_CAPTIVE = {
  AUTH_MODULE_CORE_ONEWIRE: True,
  AUTH_MODULE_CORE_RFID: False,
  'default': True
}

# Maximum idle time for new flows, based on initiating auth device.  "Idle" is
# defined as seconds elapsed without any flow meter activity.
#
# This varies on a per-auth-device basis due to the distinction between captive
# and non-captive devices: we want flows initiated with a contactless auth
# device, like an RFID, to timeout sooner.
AUTH_DEVICE_MAX_IDLE_SECS = {
  AUTH_MODULE_CORE_ONEWIRE: 120,
  AUTH_MODULE_CORE_RFID: 20,
  'default': 10
}

# How often to record a thermo reading?
THERMO_RECORD_DELTA_SECONDS = 60

### Addresses and ports

# Default port for JSON server
JSON_SERVER_PORT_DEFAULT = 9100

### Exceptions

class ConfigurationError(Exception):
    """Raised when the system is misconfigured"""
