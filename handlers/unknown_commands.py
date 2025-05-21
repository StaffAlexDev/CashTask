from aiogram import Router, F
from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.types import Message

from keyboards.other import get_navigate_kb
from models.user_context import UserContext

unknown_cmd = Router()


# Отлавливаем белиберду которая не обработана другими хэндлерами
@unknown_cmd.message(F.text, ~StateFilter(None))
async def orders_menu(message: Message, user: UserContext):
    await message.reply(user.lang.info.unknown_action)


@unknown_cmd.message(StateFilter("*"), F.text.startswith("/") | F.text)
async def remind_pending_input(message: Message, state: FSMContext, user: UserContext):
    current = await state.get_state()

    pretty = {
        "StartState:waiting_company_name": "название компании",
        # добавьте сюда остальные mаппинги ваших состояний
    }.get(current, "нужные данные")
    await message.answer(
        f"❗ Я всё ещё жду от вас **{pretty}**.\n"
        f"Пожалуйста, введите это или отмените операцию командой /cancel.",
        reply_markup=get_navigate_kb(user.lang, 2)
    )
