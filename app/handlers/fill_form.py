from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message
from aiogram.fsm.context import FSMContext

from app.states import UserState

from run import bot, db

from io import BytesIO
import pandas as pd

from config import ADMIN

fill_form_router = Router()


@fill_form_router.message(Command("fill_form"))
async def search(message: Message, state: FSMContext):
    await message.answer(f"Welcome, {message.from_user.full_name}! 🙂\n \nPlease, fill in your full name!")
    await state.set_state(UserState.fullname)
