import os

from aiogram import Router
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import Message
from aiogram.utils.keyboard import InlineKeyboardBuilder

from database.db_crud import get_employee_by_telegram_id, get_role_by_telegram_id
from database.state_models import UserCookies, UserRegistrationObject
from keyboards.admins import get_type_finance_kb
from keyboards.general import roles_kb, menu_by_role
from settings import LANGUAGE_DIR

commands = Router()


@commands.message(Command("start"))
async def command_start(message: Message, state: FSMContext):
    user_id = message.from_user.id
    user_db = get_employee_by_telegram_id(user_id)
    user = UserCookies(user_id)
    lang = user.get_lang()
    print(user_db)

    if user_db is None:
        await message.answer(lang.get("unknown_user").get("greetings"), reply_markup=roles_kb())
        new_worker = {
            "telegram_id": message.from_user.id,
            "first_name": message.from_user.first_name,
            "last_name": message.from_user.last_name,
        }
        await state.update_data(new_worker=new_worker)
        await state.set_state(UserRegistrationObject.waiting_for_confirmation)

    else:
        user_role = user_db.get_role()
        await message.answer(lang.get("language").get("select_lang"), reply_markup=menu_by_role(user_role))


@commands.message(Command('finance'))
async def finance(message: Message):
    user_id = message.from_user.id
    role = get_role_by_telegram_id(user_id)
    await message.answer('Выберите тип финансов:', reply_markup=get_type_finance_kb(role))


@commands.message(Command("languages"))
async def command_language(message: Message):
    os.chdir(LANGUAGE_DIR)
    files = os.listdir()
    user_id = message.from_user.id
    lang = UserCookies(user_id).get_lang()
    print(lang)
    builder = InlineKeyboardBuilder()
    for file in files:
        if os.path.isfile(file):
            file_name, _ = os.path.splitext(file)
            builder.button(text=file_name, callback_data=f"lang_{file_name}")
    builder.adjust(2)
    lang_kb = builder.as_markup()

    await message.answer(lang.get("language").get("select_lang"), reply_markup=lang_kb)
