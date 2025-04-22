import os

from aiogram import Router, F
from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.types import Message
from aiogram.utils.keyboard import InlineKeyboardBuilder

from config import LANGUAGE_DIR, USER_ROLES
from database.db_crud import get_employee_by_telegram_id, get_role_by_telegram_id
from database.state_models import UserCookies, UserRegistrationObject
from keyboards.admins import get_type_finance_kb
from keyboards.general import roles_kb, menu_by_role, order_menu_kb, car_park_menu_kb

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

        await state.set_state(UserRegistrationObject.waiting_for_confirmation)

    else:
        user_role = user_db.get_role()
        await message.answer(lang.get("language").get("select_lang"), reply_markup=menu_by_role(user_role))


@commands.message(Command('menu'))
async def command_menu(message: Message):
    user_id = message.from_user.id
    role = get_role_by_telegram_id(user_id)
    user = UserCookies(user_id)
    lang = user.get_lang()
    if role is not None:
        await message.answer('Привет', reply_markup=menu_by_role(role))
    else:
        await message.answer("У вас нет доступа!")


@commands.message(Command('orders'))
async def orders_menu(message: Message):
    telegram_id = message.from_user.id
    role = get_role_by_telegram_id(telegram_id)
    if role in USER_ROLES[1:]:
        await message.answer('Что делаем?', reply_markup=order_menu_kb(role))
    else:
        await message.answer("У вас нет доступа!")


@commands.message(Command('clients'))
async def clients_menu(message: Message):
    telegram_id = message.from_user.id
    role = get_role_by_telegram_id(telegram_id)
    if role in USER_ROLES[1:]:
        await message.answer('Что показать?', reply_markup=order_menu_kb(role))
    else:
        await message.answer("У вас нет доступа!")


@commands.message(Command('finance'))
async def finance_menu(message: Message):
    user_id = message.from_user.id
    role = get_role_by_telegram_id(user_id)
    if role in USER_ROLES[1:]:
        await message.answer('Выберите тип финансов:', reply_markup=get_type_finance_kb(role))
    else:
        await message.answer("У вас нет доступа!")


@commands.message(Command('car_park'))
async def car_park_menu(message: Message):
    text = "Выбери действие"
    await message.answer(text, reply_markup=car_park_menu_kb())


@commands.message(Command("languages"))
async def command_language(message: Message):
    os.chdir(LANGUAGE_DIR)
    files = os.listdir()
    user_id = message.from_user.id
    user = get_employee_by_telegram_id(user_id)

    if user is not None:
        lang = UserCookies(user_id).get_lang()
        builder = InlineKeyboardBuilder()
        for file in files:
            if os.path.isfile(file):
                file_name, _ = os.path.splitext(file)
                builder.button(text=file_name, callback_data=f"lang_{file_name}")
        builder.adjust(2)
        lang_kb = builder.as_markup()

        await message.answer(lang.get("language").get("select_lang"), reply_markup=lang_kb)
    else:
        await message.answer("У вас нет доступа!")


# Отлавливаем белиберду которая не обработана другими хэндлерами
@commands.message(F.text, ~StateFilter(None))
async def orders_menu(message: Message):
    await message.reply("Это неизвестное действие")
