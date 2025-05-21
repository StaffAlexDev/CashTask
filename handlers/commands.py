from aiogram import Router
from aiogram.filters import Command, CommandObject
from aiogram.fsm.context import FSMContext
from aiogram.types import Message
from aiogram.utils.keyboard import InlineKeyboardBuilder

from config.buttons_config import LANGUAGE_REGISTRY
from database.orders_pg import get_orders_by_worker
from handlers.general.other import show_join_menu, show_start_menu
from models.user_context import UserContext
from keyboards.other import common_kb_by_role
from utils.enums import Role

commands = Router()


# @commands.message(Command("start"))
# async def command_start(message: Message, command: CommandObject, user: UserContext, state: FSMContext):
#     lang = user.lang
#     role = user.get_role()
#     payload = command.args or ""
#
#     print(f"payload: {payload}")
#
#     await state.update_data(nav_stack=[])
#     await push_nav(state, command_start, message, state)
#
#     if payload:
#         if role == Role.UNKNOWN:
#             await message.answer(
#                 lang.greetings.unknown_user,
#                 reply_markup=enum_kb(Role.for_ui(), lang, "role")
#             )
#         else:
#             await message.answer(
#                 lang.greetings.welcome,
#                 reply_markup=common_kb_by_role("main_menu", lang, role)
#             )
#     else:
#         await message.answer(
#             lang.greetings.unknown_company,
#             reply_markup=common_kb_by_role("start_menu", lang, role)
#         )
@commands.message(Command("start"))  # Проверить обработку прохода по ссылке фирмы, исправил, но не проверял
async def command_start(
    message: Message,
    command: CommandObject,
    state: FSMContext,
    user: UserContext
):
    # 1) Сброс навигации
    await state.update_data(nav_stack=[])
    # 2) Сохраняем код из deep link (если есть)
    invite_code = (command.args or "").strip()
    if invite_code:
        await state.update_data(invite_code=invite_code)
        # Точка возврата – главный экран
        user.push_nav(show_start_menu, message)
        # Перенаправляем сразу в join-блок
        return await show_join_menu(message, state, user)

    # 3) Обычный /start
    user.push_nav(show_start_menu, message)
    return await show_start_menu(message, user)


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
        orders_list = get_orders_by_worker(user.company_id, user.telegram_id)
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



