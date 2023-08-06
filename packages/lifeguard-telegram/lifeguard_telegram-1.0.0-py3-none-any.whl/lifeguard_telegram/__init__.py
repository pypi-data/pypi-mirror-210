"""
Lifeguard integration with Telegram
"""
import _thread
import os

from lifeguard.logger import lifeguard_logger as logger

from lifeguard_telegram.bot import load_bot_handlers, init_updater


class LifeguardTelegramPlugin:
    """
    Telegram Plugin
    """

    def __init__(self, lifeguard_context):
        self.lifeguard_context = lifeguard_context
        init_updater()


def init(lifeguard_context):
    newpid = os.fork()
    if newpid == 0:
        logger.info("starting telegram process")
        LifeguardTelegramPlugin(lifeguard_context)
