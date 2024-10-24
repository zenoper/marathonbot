from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message
from aiogram.fsm.context import FSMContext

help_router = Router()


@help_router.message(Command("help"))
async def search(message: Message, state: FSMContext):
    await state.clear()
    await message.answer(f"Available commands for user: \n\n/help - see the commands \n/fill_form - fill in the form \n/start - restart the bot")
