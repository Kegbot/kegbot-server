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

### Addresses and ports

# Default port for JSON server
JSON_SERVER_PORT_DEFAULT = 9100

### Enums

KB_EVENT = util.Enum(*(
  # Common events
  'QUIT',
  'START_COMPLETE',
  'HEARTBEAT_1S',
  'HEARTBEAT_10S',

  'CLIENT_CONNECTED',
  'CLIENT_DISCONNECTED',

  # DrinkDatabaseService-generated events
  'DRINK_CREATED',

  # FlowManagerService handled events
  'FLOW_DEV_REGISTER',
  'FLOW_DEV_UNREGISTER',
  'FLOW_DEV_ACTIVITY',
  'FLOW_DEV_IDLE',

  'START_FLOW',
  'END_FLOW',

  'FLOW_START',
  'FLOW_UPDATE',
  'FLOW_END',

  'THERMO_UPDATE',

  'AUTH_USER_ADDED',
  'AUTH_USER_REMOVED',
  'AUTH_TOKEN_ADDED',

))


KB_DEVICE_TYPE = util.Enum(*(
  'DEVICE_TYPE_UNKNOWN',
  'DEVICE_TYPE_FLOW_DEV',
  'DEVICE_TYPE_RELAY',
  'DEVICE_TYPE_THERMO',
))

### Exceptions

class ConfigurationError(Exception):
  """Raised when the system is misconfigured"""
