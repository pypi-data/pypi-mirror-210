"""
Builtin Handlers
"""
from lifeguard.repositories import ValidationRepository

from lifeguard_telegram.bot import bot_handler
from lifeguard_telegram.settings import LIFEGUARD_TELEGRAM_VALIDATIONS_HANDLER_ENABLED


@bot_handler("validations", load=LIFEGUARD_TELEGRAM_VALIDATIONS_HANDLER_ENABLED)
def recover_validations(update, _context):
    """
    send all validations status
    """
    for validation in ValidationRepository().fetch_all_validation_results():
        update.message.reply_text(
            "{}: {}".format(validation.validation_name, validation.status)
        )
