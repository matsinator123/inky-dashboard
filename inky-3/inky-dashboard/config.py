import os

# Basic configuration with environment overrides

# Location for weather
LAT = float(os.getenv("INKY_LAT", "58.1624"))
LON = float(os.getenv("INKY_LON", "7.9983"))

# Bluetooth speaker name for media key listener
SPEAKER_NAME = os.getenv("INKY_SPEAKER_NAME", "VAPPEBY")

# Logging level for the main app (INFO, DEBUG, WARNING, etc.)
LOG_LEVEL = os.getenv("INKY_LOG_LEVEL", "INFO")


