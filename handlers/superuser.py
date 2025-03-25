import os

from dotenv import find_dotenv, load_dotenv
from aiogram import Router, types, F

from database.db_crud import add_user
from keyboards.general import menu_by_role

load_dotenv(find_dotenv())
superuser = Router()


@superuser.message(F.text == os.getenv("SUPERADMIN_PASS"))
async def admin_password(message: types.Message):
    add_user(message.from_user.id,
             message.from_user.first_name,
             message.from_user.last_name,
             "super_admin")
    await message.answer("Привет Superadmin", reply_markup=menu_by_role("super_admin"))
