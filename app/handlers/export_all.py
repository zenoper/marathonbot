from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message, BufferedInputFile

from run import bot, db

from io import BytesIO
import pandas as pd

from config import ADMIN

export_router = Router()


@export_router.message(Command("export_all"))
async def search(message: Message):
    admin_id = str(message.from_user.id)
    if admin_id in ADMIN:
        user_data = await db.select_all_users()
        if user_data:
            # Convert the list of user data to a DataFrame
            excel_file = pd.DataFrame(user_data)

            # Create a BytesIO object to store the Excel file in memory
            output = BytesIO()

            # Use the ExcelWriter context manager to write the DataFrame to Excel
            with pd.ExcelWriter(output, engine='openpyxl') as writer:
                excel_file.to_excel(writer, sheet_name='Users', index=False)

            # Get the bytes from the BytesIO object
            excel_bytes = output.getvalue()

            # Create a BufferedInputFile
            document = BufferedInputFile(excel_bytes, filename="UserInfo.xlsx")

            # Send the document
            await bot.send_document(chat_id=admin_id, document=document, caption="Here's your All User Info.")
        else:
            await bot.send_message(chat_id=ADMIN[0], text="No user data found.")
    else:
        await message.answer("You don't have permission")