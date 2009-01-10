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

### Addresses and ports

# Default port for JSON server
JSON_SERVER_PORT_DEFAULT = 9100

### Enums

KB_EVENT = util.Enum(*(
  'CHANNEL_ACTIVITY',
))
