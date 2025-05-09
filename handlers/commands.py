from aiogram import Router, F
from aiogram.filters import Command, StateFilter
from aiogram.types import Message
from aiogram.utils.keyboard import InlineKeyboardBuilder

from config.buttons_config import SUPPORTED_LANGUAGES
from database.orders_pg import get_orders_by_worker
from database.state_models import UserContext
from keyboards.admins import get_type_finance_kb, clients_menu_kb
from keyboards.general.other import ui_buttons_for_role, enum_kb, order_menu_kb, car_park_menu_kb
from utils.enums import Role

commands = Router()


@commands.message(Command("start"))
async def command_start(message: Message, user: UserContext):
    lang = user.lang
    role = user.get_role()

    if role == Role.UNKNOWN:
        await message.answer(
            lang.greetings.unknown_user,
            reply_markup=enum_kb(Role.for_ui(), lang, "role")
        )
    else:
        await message.answer(
            lang.greetings.welcome,
            reply_markup=ui_buttons_for_role(role, lang)
        )


@commands.message(Command("menu"))
async def command_menu(message: Message, user: UserContext):
    lang = user.lang

    await message.answer(
        lang.greetings.welcome,
        reply_markup=ui_buttons_for_role(user.get_role(), lang)
    )


@commands.message(Command('orders'))
async def orders_menu(message: Message, user: UserContext):
    user_role = user.get_role()
    if user_role in [Role.ADMIN, Role.SUPERADMIN]:
        await message.answer('Что делаем?', reply_markup=order_menu_kb(user_role))

    elif user_role == Role.WORKER:
        orders_list = get_orders_by_worker(user.telegram_id)
        if orders_list:
            print(orders_list)
            # await message.answer('Вот список', reply_markup=get_cars_kb(orders_list))
        else:
            await message.answer('У вас нет выполняемых нарядов')
    else:
        await message.answer("У вас нет доступа!")


@commands.message(Command('clients'))
async def clients_menu(message: Message, user: UserContext):
    role = user.get_role()
    if role in [Role.ADMIN, Role.SUPERADMIN]:
        await message.answer('Что показать?', reply_markup=clients_menu_kb())
    else:
        await message.answer("У вас нет доступа!")


@commands.message(Command('finance'))
async def finance_menu(message: Message, user: UserContext):
    role = user.get_role()
    if role in [Role.ADMIN, Role.SUPERADMIN]:
        await message.answer('Выберите тип финансов:', reply_markup=get_type_finance_kb(role))
    else:
        await message.answer("У вас нет доступа!")


@commands.message(Command('car_park'))
async def car_park_menu(message: Message, user: UserContext):
    text = "Выбери действие"
    await message.answer(text, reply_markup=car_park_menu_kb())


@commands.message(Command("languages"))
async def command_language(message: Message, user: UserContext):

    role = user.get_role()

    if role in [Role.WORKER, Role.ADMIN, Role.SUPERADMIN]:
        builder = InlineKeyboardBuilder()

        for code, name in SUPPORTED_LANGUAGES.items():
            builder.button(text=name, callback_data=f"lang_{code}")

        builder.adjust(2)

        await message.answer(user.lang.Language.select_lang, reply_markup=builder.as_markup())

    else:
        await message.answer("У вас нет доступа!")


# Отлавливаем белиберду которая не обработана другими хэндлерами
@commands.message(F.text, ~StateFilter(None))
async def orders_menu(message: Message, user: UserContext):
    await message.reply("Это неизвестное действие")
