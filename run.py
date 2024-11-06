from aiogram import Bot, Dispatcher, Router, types
from aiogram.fsm.storage.memory import MemoryStorage
import asyncpg
import asyncio
import logging
from dataclasses import dataclass

from marathonbot.config import BOT_TOKEN, MAIN_CHANNEL_ID, PRIVATE_CHANNEL_LINK, REQUIRED_REFERRALS, DB_PORT, DB_HOST, DB_USER, DB_NAME, DB_PASS, ADMIN

import config as Config
from utils.notify_admin import on_startup, on_shutdown
from utils.bot_commands import set_default_commands
from app.middlewares import ThrottlingMiddleware


async def main():
    # Configure logging
    from utils.postgresql import Database
    from app.handlers.start import ReferralBot
    logging.basicConfig(level=logging.INFO)

    storage = MemoryStorage()
    # Initialize bot and dispatcher
    bot = Bot(token=Config.BOT_TOKEN)
    # await bot.set_my_default_administrator_rights(
    #     rights=types.ChatAdministratorRights(
    #         can_invite_users=True,
    #         can_manage_chat=True
    #     ),
    #     for_channels=True
    # )
    dp = Dispatcher(storage=storage)
    # Initialize database
    db = await Database.create()
    await db.delete_db()
    await db.init_db()

    await on_startup(bot)
    await set_default_commands(bot)

    # Initialize bot instance
    referral_bot = ReferralBot(bot, db)
    dp.include_router(referral_bot.router)

    dp.message.outer_middleware(ThrottlingMiddleware(limit=2, interval=1))
    # Start polling
    await dp.start_polling(bot)
    await on_shutdown(bot)

if __name__ == "__main__":
    asyncio.run(main())