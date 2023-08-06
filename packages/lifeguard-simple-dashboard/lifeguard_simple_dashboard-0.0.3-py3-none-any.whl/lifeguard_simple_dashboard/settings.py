from lifeguard.settings import SettingsManager

SETTINGS_MANAGER = SettingsManager(
    {
        "LIFEGUARD_DASHBOARD_PREFIX_PATH": {
            "default": "",
            "description": "Lifeguard dashboard prefix path",
        },
    }
)

LIFEGUARD_DASHBOARD_PREFIX_PATH = SETTINGS_MANAGER.read_value("LIFEGUARD_DASHBOARD_PREFIX_PATH")
