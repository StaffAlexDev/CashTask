import os

from aiogram import Router, F
from aiogram.filters import Command, StateFilter
from aiogram.types import Message
from aiogram.utils.keyboard import InlineKeyboardBuilder

from config.constants import LANGUAGE_DIR
from database.db_crud import get_employee_by_telegram_id, get_role_by_telegram_id, get_orders_by_worker
from database.state_models import UserCookies
from keyboards.admins import get_type_finance_kb, clients_menu_kb

commands = Router()


@commands.message(Command("start"))
async def command_start(message: Message):
    user_id = message.from_user.id
    user = UserCookies(user_id)
    user_role = user.get_role()
    lang = user.get_lang()

    print(user.get_role())
    print(message.from_user.first_name)
    print(message.from_user.last_name)

    if user_role is None:
        await message.answer(lang.get("unknown_user").get("greetings"), reply_markup=roles_kb())

    else:
        await message.answer(lang.get("language").get("select_lang"), reply_markup=menu_by_role(user_role))


@commands.message(Command('menu'))
async def command_menu(message: Message):
    user_id = message.from_user.id
    user = UserCookies(user_id)
    user_role = user.get_role()
    lang = user.get_lang()
    if user_role is not None:
        await message.answer('Привет', reply_markup=menu_by_role(user_role))
    else:
        await message.answer("У вас нет доступа!")


@commands.message(Command('orders'))
async def orders_menu(message: Message):
    telegram_id = message.from_user.id
    user = UserCookies(telegram_id)
    user_role = user.get_role()
    if user_role in USER_ROLES[1:]:
        await message.answer('Что делаем?', reply_markup=order_menu_kb(user_role))
    elif user_role == USER_ROLES[0]:
        orders_list = get_orders_by_worker(telegram_id)

        if orders_list:
            print(orders_list)
            # await message.answer('Вот список', reply_markup=get_cars_kb(orders_list))
        else:
            await message.answer('У вас нет выполняемых нарядов')
    else:
        await message.answer("У вас нет доступа!")


@commands.message(Command('clients'))
async def clients_menu(message: Message):
    telegram_id = message.from_user.id
    role = get_role_by_telegram_id(telegram_id)
    if role in USER_ROLES[1:]:
        await message.answer('Что показать?', reply_markup=clients_menu_kb())
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
