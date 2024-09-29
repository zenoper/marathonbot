import logging

from aiogram import Bot

from config import ADMIN


async def on_startup(bot: Bot):
    for admin in ADMIN:
        try:
            await bot.send_message(admin, "bot running!")

        except Exception as err:
            logging.exception(err)


async def on_shutdown(bot: Bot):
    for admin in ADMIN:
        try:
            await bot.send_message(admin, "bot stopped!")

        except Exception as err:
            logging.exception(err)
