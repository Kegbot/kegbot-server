from pykeg.core import util

### Drink-related constants

# Don't record teeny drinks
MIN_VOLUME_TO_RECORD = 10

# Don't show small drinks
MIN_VOLUME_TO_DISPLAY = 10

# Idle seconds allowed before a user gets booted for inactivity
FLOW_IDLE_TIMEOUT = 30

# Maximum time between consecutive drinks to be considered in the same 'session'
# (see UserDrinkingSession table)
DRINK_SESSION_TIME_MINUTES = 90

# Maximum time between different UserDrinkingSession records to be considered
# 'concurrent' (see DrinkingSessionGroup table)
GROUP_SESSION_TIME_MINUTES = 90

# The maximum difference between consecutive meter readings that is considered
# valid.
MAX_METER_READING_DELTA = 2200*2

# Address the kegnet server should bind to.
KB_CORE_DEFAULT_ADDR = 'localhost:9805'

DEFAULT_NEW_USER_WEIGHT = 140
DEFAULT_NEW_USER_GENDER = 'male'

# String name for all taps
ALIAS_ALL_TAPS = '__all_taps__'

# Device names
AUTH_MODULE_CORE_ONEWIRE = 'core.onewire'
AUTH_MODULE_CONTRIB_PHIDGET_RFID = 'contrib.phidget.rfid'

# Maximum time in seconds an authentication token may be missing before the flow
# will be ended.  A value of 0 will cause the fow to be ended immediately when
# the token disappears.
# TODO(mikey): expose configuration in db.
AUTH_TOKEN_MAX_IDLE = {
  AUTH_MODULE_CORE_ONEWIRE: 0,
  AUTH_MODULE_CONTRIB_PHIDGET_RFID: 240,
}

# How often to record a thermo reading?
THERMO_RECORD_DELTA_SECONDS = 60

### Addresses and ports

# Default port for JSON server
JSON_SERVER_PORT_DEFAULT = 9100

### Enums

KB_DEVICE_TYPE = util.Enum(*(
  'DEVICE_TYPE_UNKNOWN',
  'DEVICE_TYPE_FLOW_DEV',
  'DEVICE_TYPE_RELAY',
  'DEVICE_TYPE_THERMO',
))

### Exceptions

class ConfigurationError(Exception):
  """Raised when the system is misconfigured"""
