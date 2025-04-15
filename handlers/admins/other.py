import os

from aiogram import F
from aiogram.types import Message

from handlers.admins import admins
from settings import bot


@admins.message(F.text == os.getenv("ADMIN_PASS"))
async def admin_password(message: Message):
    await bot.send_message()
    await message.answer("вижу ты знаешь пароль администратора")
