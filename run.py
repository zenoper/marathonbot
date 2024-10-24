import asyncio
import logging

from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage

from config import TOKEN
from app.middlewares import ThrottlingMiddleware
from utils.notify_admin import on_startup, on_shutdown
from utils.bot_commands import set_default_commands
from utils.makon_db import Database

storage = MemoryStorage()

bot = Bot(token=TOKEN)
dp = Dispatcher(storage=storage)
db = Database()


async def main():
    from app.handlers.start import entry_router
    from app.handlers.export_all import export_router
    from app.handlers.fill_form import fill_form_router
    from app.handlers.help import help_router
    await db.create()
    # await db.drop_users()
    await db.create_table_users()
    await on_startup(bot)
    await set_default_commands(bot)

    dp.include_router(help_router)
    dp.include_router(entry_router)
    dp.include_router(fill_form_router)
    dp.include_router(export_router)
    dp.message.outer_middleware(ThrottlingMiddleware(limit=2, interval=1))
    await dp.start_polling(bot)
    await on_shutdown(bot)


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    asyncio.run(main())