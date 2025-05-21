from aiogram import F
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message

from handlers.general import general
from keyboards.other import common_kb_by_role, get_navigate_kb
from models.fsm_states import StartState
from models.user_context import UserContext


async def show_start_menu(event: Message | CallbackQuery, user: UserContext):
    """
    Рисует стартовое меню (две кнопки: присоединиться / создать фирму).
    """
    # очищаем стек и вновь пушим сам экран,
    # чтобы даже изнутри show_start_menu «← Назад» возвращал сюда
    user.push_nav(show_start_menu, event, user)

    lang = user.lang
    role = user.get_role()

    if isinstance(event, CallbackQuery):
        # если мы редактируем существующее сообщение
        await event.message.edit_text("Что хотите сделать?",
                                      reply_markup=common_kb_by_role("start_menu", lang, role))
    else:
        # если это первое сообщение
        await event.answer("Добро пожаловать! Что хотите сделать?",
                           reply_markup=common_kb_by_role("start_menu", lang, role))


async def show_join_menu(event: Message, state: FSMContext, user: UserContext):
    """
    Отрисовывает форму ввода кода фирмы.
    """
    user.push_nav(show_join_menu, event, user)

    # data = await state.get_data()
    # if data.get("invite_code"):
    #     return await process_invite_code(event, state)

    await state.set_state(StartState.waiting_invite_code)
    await event.answer("Введите код фирмы:", reply_markup=get_navigate_kb(user.lang, 1))


@general.callback_query(F.data.startswith('lang_'))
async def get_selected_language(callback: CallbackQuery, user: UserContext):

    selected_language = callback.data.split("_")[1]
    await user.update_lang(selected_language)

    lang = user.lang
    await callback.answer(lang.language.accept_lang)
