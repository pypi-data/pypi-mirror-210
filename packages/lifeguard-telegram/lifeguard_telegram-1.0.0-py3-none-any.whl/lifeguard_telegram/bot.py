import os
import sys
from functools import wraps

from lifeguard.logger import lifeguard_logger as logger
from lifeguard.settings import LIFEGUARD_DIRECTORY
from telegram.ext import CommandHandler, Updater

from lifeguard_telegram.settings import LIFEGUARD_TELEGRAM_BOT_TOKEN

CONTEXT = {"updater": None}


def init_updater():
    """
    Init start polling
    """
    CONTEXT["updater"] = Updater(LIFEGUARD_TELEGRAM_BOT_TOKEN, use_context=True)

    load_bot_handlers()

    CONTEXT["updater"].start_polling()
    CONTEXT["updater"].idle()


def load_directory_with_handlers(module_prefix, bot_handler_file):
    if bot_handler_file.endswith("_bot_handler.py"):
        bot_handler_module_name = bot_handler_file.replace(".py", "")
        logger.info("loading bot handler %s", bot_handler_module_name)

        module = "{}.{}".format(module_prefix, bot_handler_module_name)
        if module not in sys.modules:
            __import__(module)


def load_bot_handlers():
    """
    Load bot handlers from application path
    """
    sys.path.append(LIFEGUARD_DIRECTORY)

    for bot_handler_file in os.listdir(
        os.path.join(os.path.dirname(os.path.realpath(__file__)), "bot_handlers")
    ):
        load_directory_with_handlers(
            "lifeguard_telegram.bot_handlers", bot_handler_file
        )

    if not os.path.exists(os.path.join(LIFEGUARD_DIRECTORY, "bot_handlers")):
        return

    for bot_handler_file in os.listdir(
        os.path.join(LIFEGUARD_DIRECTORY, "bot_handlers")
    ):
        load_directory_with_handlers("bot_handlers", bot_handler_file)


def bot_handler(command, load=True):
    """
    Decorator to configure a bot handler
    """

    def function_reference(decorated):
        @wraps(decorated)
        def wrapped(*args, **kwargs):
            return decorated(*args, **kwargs)

        if load:
            CONTEXT["updater"].dispatcher.add_handler(
                CommandHandler(command, decorated)
            )
        return wrapped

    return function_reference
