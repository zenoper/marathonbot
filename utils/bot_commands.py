from aiogram import Bot
from aiogram.types import BotCommand


async def set_default_commands(bot: Bot):
    await bot.set_my_commands(
        [
            BotCommand(command="start", description="Restart the bot"),
            BotCommand(command="check_my_referrals", description="Check my status"),
            BotCommand(command="top_referrers", description="Check top referrers"),
        ]
    )