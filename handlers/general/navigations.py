from aiogram import F
from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message

from handlers.general import general
from handlers.general.other import show_start_menu
from models.user_context import UserContext


@general.callback_query(StateFilter("*"), F.data == "back")
async def back_handler(query: CallbackQuery, user: UserContext):
    await query.answer()
    prev = user.pop_nav()
    if not prev:
        # если некуда назад — в старт
        return await show_start_menu(query, user)

    handler, args, kwargs = prev
    # вызываем тот же рендер-метод
    return await handler(*args, user, **kwargs)


@general.message(F.data == "cancel", StateFilter("*"))
async def cmd_cancel(message: Message, state: FSMContext):
    await state.clear()
    await message.answer("Операция отменена. Возвращаю вас в главное меню.")
