"""
Lifeguard TinyDB Settings
"""
from lifeguard.settings import SettingsManager

SETTINGS_MANAGER = SettingsManager(
    {
        "LIFEGUARD_TINYDB_LOCATION": {
            "default": "lifeguard.json",
            "description": "Path to database file",
        },
    }
)

LIFEGUARD_TINYDB_LOCATION = SETTINGS_MANAGER.read_value("LIFEGUARD_TINYDB_LOCATION")
