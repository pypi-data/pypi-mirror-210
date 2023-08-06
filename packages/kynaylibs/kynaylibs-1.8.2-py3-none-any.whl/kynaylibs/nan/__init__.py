import logging
import os
import sys
import time
from datetime import datetime
from logging.handlers import RotatingFileHandler

import pyrogram
from aiohttp import ClientSession
from naya.config import *
from pyrogram import Client, __version__, enums, filters
from pyrogram.enums import ParseMode
from pyrogram.handlers import MessageHandler
from pyromod import listen
from pytgcalls import GroupCallFactory

from .log import LOGGER


class Bot(Client):
    def __init__(self):
        super().__init__(
            name="ubot",
            api_hash=API_HASH,
            api_id=API_ID,
            bot_token=BOT_TOKEN,
            in_memory=True,
        )
        self.LOGGER = LOGGER

    async def start(self):
        await super().start()
        usr_bot_me = self.me
        self.LOGGER(__name__).info(
            f"@{usr_bot_me.username} based on Pyrogram v{__version__} "
        )

    async def stop(self, *args):
        await super().stop()
        self.LOGGER(__name__).info("Naya-Premium stopped. Bye.")


class Ubot(Client):
    __module__ = "pyrogram.client"
    _bots = []

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.group_call = GroupCallFactory(self).get_group_call()

    def on_message(self, filters=filters.Filter, group=-1):
        def decorator(func):
            for bot in self._bots:
                bot.add_handler(MessageHandler(func, filters), group)
            return func

        return decorator

    async def start(self):
        await super().start()
        if self not in self._bots:
            self._bots.append(self)

    async def stop(self, *args):
        await super().stop()
        if self not in self._bots:
            self._bots.append(self)
