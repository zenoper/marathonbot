from aiogram import Router
from aiogram.filters import CommandStart
from aiogram.types import Message, ContentType, ReplyKeyboardRemove
from aiogram.fsm.context import FSMContext

from app.states import UserState
from run import bot, db
from app import keyboards
from config import ADMIN

import re
import asyncpg

entry_router = Router()


@entry_router.message(CommandStart())
async def send_welcome(message: Message, state: FSMContext):
    await message.answer(f"Welcome, {message.from_user.full_name}! 🙂\n \nPlease, fill in your full name!")
    await state.set_state(UserState.fullname)


@entry_router.message(UserState.fullname)
async def process_template(message: Message, state: FSMContext):
    if message.content_type == ContentType.TEXT:
        full_name = message.text
        if len(full_name) <= 5:
            await message.answer(
                "Please, fill in your name and surname completely!")
        else:
            await state.update_data({"fullname": full_name})
            await message.answer("Please, fill in your birthdate!")
            await state.set_state(UserState.date_of_birth)
    else:
        await message.answer("Please, only use letters!")


@entry_router.message(UserState.date_of_birth)
async def process_data(message: Message, state: FSMContext):
    if message.content_type == ContentType.TEXT:
        date_of_birth = message.text
        username = message.from_user.username
        telegram_id = message.from_user.id
        if username:
            if len(date_of_birth) <= 5:
                await message.answer(
                    "Please, fill in your 'complete' birthdate!")
            else:
                await state.update_data(
                    {"date_of_birth": date_of_birth, "username": username, "telegram_id": telegram_id})
                await message.answer(
                    "Do you live in Uzbekistan or abroad?",
                    reply_markup=keyboards.int_or_local)
                await state.set_state(UserState.int_local)
        else:
            await message.answer(
                "Please, add a username to your telegram profile. Then, we can contact you!")
    else:
        await message.answer("Please, only use numbers/letters!")


@entry_router.message(UserState.int_local)
async def int_local(message: Message, state: FSMContext):
    if message.content_type == ContentType.TEXT:
        if message.text == "In Uzbekistan":
            await message.answer(
                "Please, send your phone number! \nEither press 'send' button or fill in yourself! \nFor example, +998xx xxx xx xx",
                reply_markup=keyboards.phone_number)
            await state.set_state(UserState.phone_number)
        elif message.text == "Abroad":
            await message.answer(
                "Please, send your phone number! \nEither press 'send' button or fill in yourself!",
                reply_markup=keyboards.phone_number)
            await state.set_state(UserState.phone_number_int)
        else:
            await message.answer("Please, only use the buttons!")
    else:
        await message.answer("Please, only use the buttons!")

phone_number_regexp = "^[+]998[389][012345789][0-9]{7}$"


@entry_router.message(UserState.phone_number)
@entry_router.message(UserState.phone_number_int)
async def phone_number(message: Message, state: FSMContext):
    if message.content_type == ContentType.CONTACT:
        contact = message.contact.phone_number
        await state.update_data({'phone_number': contact})
        await message.answer("Choose one:", reply_markup=keyboards.grade)
        await state.set_state(UserState.grade)
    elif message.content_type == ContentType.TEXT:
        if re.match(phone_number_regexp, message.text):
            phonenumber = message.text
            await state.update_data({'phone_number': phonenumber})
            await message.answer("Choose one:", reply_markup=keyboards.grade)
            await state.set_state(UserState.grade)
        else:
            await message.answer("Wrong format!")
    else:
        await message.answer("Please, send contact or fill in correctly!")


@entry_router.message(UserState.grade)
async def grade(message: Message, state: FSMContext):
    if message.content_type == ContentType.TEXT:
        if message.text == "At high school":
            await state.update_data({'grade': "At high school"})
            await message.answer("Is your school private or public?", reply_markup=keyboards.private_public)
            await state.set_state(UserState.public_private)
        elif message.text == "In a gap year":
            await state.update_data({'grade': "In a gap year"})
            await message.answer("Was your school private or public?", reply_markup=keyboards.private_public)
            await state.set_state(UserState.public_private)
        else:
            await message.answer("Please, use buttons only!")
    else:
        await message.answer("Please, use buttons only!")


@entry_router.message(UserState.public_private)
async def private(message: Message, state: FSMContext):
    if message.content_type == ContentType.TEXT:
        if message.text == "Private":
            await state.update_data({'public_private': "Private"})
            await message.answer("What is your SAT score? \n\nIf you don't have one, click 'Skip' button", reply_markup=keyboards.skip)
            await state.set_state(UserState.SAT)
        elif message.text == "Public":
            await state.update_data({'public_private': "Public"})
            await message.answer("What is your SAT score? \n\nIf you don't have one, click 'Skip' button", reply_markup=keyboards.skip)
            await state.set_state(UserState.SAT)
        else:
            await message.answer("Please, use buttons only!")
    else:
        await message.answer("Please, use buttons only!")


@entry_router.message(UserState.SAT)
async def sat(message: Message, state: FSMContext):
    if message.content_type == ContentType.TEXT:
        if message.text == "Skip":
            await state.update_data({'SAT': "None"})
        else:
            await state.update_data({'SAT': message.text})
        await message.answer("What is your IELTS score? \n\nIf you don't have one, click 'Skip' button",
                             reply_markup=keyboards.skip)
        await state.set_state(UserState.IELTS)
    else:
        await message.answer("Only text accepted!")


@entry_router.message(UserState.IELTS)
async def sat(message: Message, state: FSMContext):
    if message.content_type == ContentType.TEXT:
        if message.text == "Skip":
            await state.update_data({'IELTS': "None"})
        else:
            await state.update_data({'IELTS': message.text})
        await message.answer("What is your Duolingo score? \n\nIf you don't have one, click 'Skip' button",
                             reply_markup=keyboards.skip)
        await state.set_state(UserState.Duolingo)
    else:
        await message.answer("Only text accepted!")


@entry_router.message(UserState.Duolingo)
async def sat(message: Message, state: FSMContext):
    if message.content_type == ContentType.TEXT:
        if message.text == "Skip":
            await state.update_data({'Duolingo': "None"})
        else:
            await state.update_data({'Duolingo': message.text})
        await message.answer("Do you have any previous Visa Rejections? \n\nIf yes, write how many and when.\n\nIf not, click 'Skip' button",
                             reply_markup=keyboards.skip)
        await state.set_state(UserState.visa)
    else:
        await message.answer("Only text accepted!")


@entry_router.message(UserState.visa)
async def sat(message: Message, state: FSMContext):
    if message.content_type == ContentType.TEXT:
        if message.text == "Skip":
            await state.update_data({'visa_rejection': "None"})
        else:
            await state.update_data({'visa_rejection': message.text})
        await message.answer("Please, provide information about your travel history \n\nIf you don't have, click 'Skip' button",
                             reply_markup=keyboards.skip)
        await state.set_state(UserState.travel_history)
    else:
        await message.answer("Only text accepted!")


@entry_router.message(UserState.travel_history)
async def sat(message: Message, state: FSMContext):
    if message.content_type == ContentType.TEXT:
        if message.text == "Skip":
            await state.update_data({'travel_history': "None"})
        else:
            await state.update_data({'travel_history': message.text})
        await message.answer("What is your average annual funding?")
        await state.set_state(UserState.average_funding)
    else:
        await message.answer("Only text accepted!")


@entry_router.message(UserState.average_funding)
async def sat(message: Message, state: FSMContext):
    if message.content_type == ContentType.TEXT:
        await state.update_data({'average_funding': message.text})

        data = await state.get_data()
        full_name = data.get("fullname")
        date_of_birth = data.get("date_of_birth")
        contact_number = data.get("phone_number")
        grade = data.get("grade")
        public_private = data.get("public_private")
        SAT = data.get("SAT")
        IELTS = data.get("IELTS")
        Duolingo = data.get("Duolingo")
        visa = data.get("visa_rejection")
        travel_history = data.get("travel_history")
        average_funding = data.get("average_funding")

        msg = "Please, confirm your personal info is correct! \n \n"
        msg += f"Full name - '{full_name}' \n\n"
        msg += f"Date of birth - '{date_of_birth}' \n\n"
        msg += f"Phone Number - '{contact_number}' \n\n"
        msg += f"Study year - '{grade}' \n\n"
        msg += f"Public or Private - '{public_private}' \n\n"
        msg += f"SAT - '{SAT}' \n\n"
        msg += f"IELTS - '{IELTS}' \n\n"
        msg += f"Duolingo - '{Duolingo}' \n\n"
        msg += f"Visa Rejection - '{visa}' \n\n"
        msg += f"Travel History - '{travel_history}' \n\n"
        msg += f"Average Funding - '{average_funding}' \n\n"

        await message.answer(msg, reply_markup=keyboards.confirmation)
        await state.set_state(UserState.confirmation)
    else:
        await message.answer("Only text accepted!")


@entry_router.message(UserState.confirmation)
async def sat(message: Message, state: FSMContext):
    if message.content_type == ContentType.TEXT:
        user_data = await state.get_data()
        if message.text == "Confirm! ✅":
            try:
                user = await db.add_user(
                    full_name=user_data.get("fullname"),
                    date_of_birth=user_data.get("date_of_birth"),
                    phone_number=user_data.get("phone_number"),
                    grade=user_data.get("grade"),
                    public_private=user_data.get("public_private"),
                    SAT=user_data.get("SAT"),
                    IELTS=user_data.get("IELTS"),
                    Duolingo=user_data.get("Duolingo"),
                    visa_rejection=user_data.get("visa_rejection"),
                    travel_history=user_data.get("travel_history"),
                    average_funding=user_data.get("average_funding"),
                    username=user_data.get("username"),
                    telegram_id=user_data.get("telegram_id")
                )
            except asyncpg.exceptions.UniqueViolationError:
                user = await db.select_user(telegram_id=user_data.get("telegram_id"))

            count = await db.count_users()
            msg = f"User '{user[1]}' has been added to User's database! We now have {count} users."
            await bot.send_message(chat_id=ADMIN[0], text=msg)

            await message.answer(
                "Thank you for cooperation! \nWe will reach out to you soon. 🙂",
                reply_markup=ReplyKeyboardRemove(selective=True))
            await state.clear()
        elif message.text == "Edit ✏️":
            await message.answer(f"Welcome back!\n \nPlease, fill in your full name!")
            await state.set_state(UserState.fullname)
        else:
            await message.answer("Use buttons only!")
    else:
        await message.answer("Use buttons only!")



