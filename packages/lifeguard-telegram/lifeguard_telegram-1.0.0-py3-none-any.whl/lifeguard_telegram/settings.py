"""
Lifeguard Telegram Settings
"""
from lifeguard.settings import SettingsManager

SETTINGS_MANAGER = SettingsManager(
    {
        "LIFEGUARD_TELEGRAM_BOT_TOKEN": {
            "default": "",
            "description": "Telegram bot token",
        },
        "LIFEGUARD_TELEGRAM_VALIDATIONS_HANDLER": {
            "default": "true",
            "description": "Enable telegram validations handler",
        },
    }
)

LIFEGUARD_TELEGRAM_BOT_TOKEN = SETTINGS_MANAGER.read_value(
    "LIFEGUARD_TELEGRAM_BOT_TOKEN"
)
LIFEGUARD_TELEGRAM_VALIDATIONS_HANDLER_ENABLED = (
    SETTINGS_MANAGER.read_value("LIFEGUARD_TELEGRAM_VALIDATIONS_HANDLER_ENABLED")
    == "true"
)
