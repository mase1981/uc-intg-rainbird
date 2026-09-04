"""Constants for the Rain Bird integration."""

# Device reachability state.
STATE_ON = "ON"
STATE_UNAVAILABLE = "UNAVAILABLE"

# Rain delay bounds (days) - matches the Rain Bird LNK module range.
RAIN_DELAY_MIN = 0
RAIN_DELAY_MAX = 14

# Zone irrigation duration bounds (minutes).
DURATION_MIN = 1
DURATION_MAX = 240
DEFAULT_DURATION = 10

# Poll cadence - the LNK module handles one request at a time, so each poll
# runs a short serial sequence of calls.
POLL_INTERVAL = 30

# Rain-sensor sensor values.
RAIN_WET = "Wet"
RAIN_DRY = "Dry"

# Active-zone sensor value when nothing is running.
ZONE_NONE = "None"
