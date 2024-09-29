from mailbox import Message

from aiogram.types import (ReplyKeyboardMarkup, KeyboardButton,
                           InlineKeyboardMarkup, InlineKeyboardButton)
from aiogram.utils.keyboard import ReplyKeyboardBuilder, InlineKeyboardBuilder

phone_number = ReplyKeyboardMarkup(
    keyboard = [
        [
            KeyboardButton(text="Send Phone Number 📱", request_contact=True)
        ],
    ],
    resize_keyboard=True,
    one_time_keyboard=True
)


int_or_local = ReplyKeyboardMarkup(
    keyboard = [
        [
            KeyboardButton(text="In Uzbekistan")
        ],
        [
            KeyboardButton(text="Abroad")
        ]
    ],
    resize_keyboard=True,
    one_time_keyboard=True
)

grade = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(text="At high school")
        ],
        [
            KeyboardButton(text="In a gap year")
        ],
    ],
    resize_keyboard=True,
    one_time_keyboard=True
)

private_public = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(text="Private")
        ],
        [
            KeyboardButton(text="Public")
        ],
    ],
    resize_keyboard=True,
    one_time_keyboard=True
)

skip = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(text="Skip")
        ],
    ],
    resize_keyboard=True,
    one_time_keyboard=True
)


confirmation = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(text="Confirm! ✅")
        ],
        [
            KeyboardButton(text="Edit ✏️")
        ]
    ],
    resize_keyboard=True,
    one_time_keyboard=True
)


