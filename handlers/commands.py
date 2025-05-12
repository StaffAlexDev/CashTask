from aiogram import Router, F
from aiogram.filters import Command, StateFilter
from aiogram.types import Message
from aiogram.utils.keyboard import InlineKeyboardBuilder

from config.buttons_config import LANGUAGE_REGISTRY
from database.orders_pg import get_orders_by_worker
from database.state_models import UserContext
from keyboards.other import enum_kb, common_kb_by_role
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
            reply_markup=common_kb_by_role("main_menu", lang, role)
        )


@commands.message(Command("menu"))
async def command_menu(message: Message, user: UserContext):
    lang = user.lang
    role = user.get_role()
    if role == Role.UNKNOWN:
        await message.answer(user.lang.info.no_access)
    await message.answer(
        lang.greetings.welcome,
        reply_markup=common_kb_by_role("main_menu", lang, role)
    )


@commands.message(Command('orders'))
async def orders_menu(message: Message, user: UserContext):
    user_role = user.get_role()
    if user_role in [Role.ADMIN, Role.SUPERADMIN]:
        await message.answer('Что делаем?',
                             reply_markup=common_kb_by_role("orders", user.lang, user_role))

    elif user_role == Role.WORKER:
        orders_list = get_orders_by_worker(user.telegram_id)
        if orders_list:
            print(orders_list)
            # await message.answer('Вот список', reply_markup=get_cars_kb(orders_list))
        else:
            await message.answer('У вас нет выполняемых нарядов')
    else:
        await message.answer(user.lang.info.no_access)


@commands.message(Command('clients'))
async def clients_menu(message: Message, user: UserContext):
    role = user.get_role()
    if role in [Role.ADMIN, Role.SUPERADMIN]:
        await message.answer('Что показать?', reply_markup=common_kb_by_role("clients",
                                                                             user.lang, role))
    else:
        await message.answer(user.lang.info.no_access)


@commands.message(Command('finance'))
async def finance_menu(message: Message, user: UserContext):
    role = user.get_role()
    if role in [Role.ADMIN, Role.SUPERADMIN]:
        await message.answer('Выберите тип финансов:',
                             reply_markup=common_kb_by_role("finance",
                                                            user.lang,
                                                            role))
    else:
        await message.answer(user.lang.info.no_access)


@commands.message(Command('car_park'))
async def car_park_menu(message: Message, user: UserContext):
    await message.answer("Выбери действие",
                         reply_markup=common_kb_by_role("cars", user.lang, user.get_role()))


@commands.message(Command("languages"))
async def command_language(message: Message, user: UserContext):

    role = user.get_role()

    if role in [Role.WORKER, Role.ADMIN, Role.SUPERADMIN]:
        builder = InlineKeyboardBuilder()

        for code, (name, _) in LANGUAGE_REGISTRY.items():
            builder.button(text=name, callback_data=f"lang_{code}")

        builder.adjust(2)

        await message.answer(user.lang.language.select_lang, reply_markup=builder.as_markup())

    else:
        await message.answer(user.lang.info.no_access)


# Отлавливаем белиберду которая не обработана другими хэндлерами
@commands.message(F.text, ~StateFilter(None))
async def orders_menu(message: Message, user: UserContext):
    await message.reply(user.lang.info.unknown_action)
