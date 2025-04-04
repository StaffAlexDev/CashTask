import os

from aiogram import Router, F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery
from aiogram.utils.keyboard import InlineKeyboardBuilder

from database.db_crud import get_employee_by_telegram_id, add_employee_approval, get_approved_employees, add_employee
from database.state_models import UserCookies, UserRegistrationObject
from keyboards.general import roles_kb, get_access_confirmation, menu_by_role
from settings import bot

general = Router()


@general.callback_query(F.data.startswith('role_'))
async def choice_role(callback_query: CallbackQuery, state: FSMContext):
    await callback_query.answer()
    user_id = callback_query.message.from_user.id
    lang = UserCookies(user_id).get_lang()
    lng_message = lang.get("info").get("user_accept")
    msg_list = lng_message.split(":")
    message = msg_list[0] + callback_query.from_user.username + msg_list[1]
    user_role = F.data.split("_")[1]
    await state.update_data(user_role=user_role)

    # Уходит запрос на должность выше
    role_list = get_approved_employees(callback_query.data[5:])
    for telegram_id in role_list:
        await bot.send_message(chat_id=telegram_id,
                               text=message,
                               reply_markup=get_access_confirmation())

    lng_msg = lang.get('unknown_user').get('waiting_accept')
    msg_list = lng_msg.split(":")
    sec_message = msg_list[0] + callback_query.from_user.username + msg_list[1]
    await callback_query.message.answer(sec_message)


@general.callback_query(F.data.startswith('accept'), UserRegistrationObject.waiting_for_confirmation)
async def get_accept_by_user(callback_query: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    new_user = data.get("new_user")
    user_role = data.get("user_role")
    if not new_user:
        await callback_query.answer("Ошибка: нет данных о пользователе.")
        return

    # Добавляем пользователя в БД
    senior_telegram_id = callback_query.from_user.id

    # add_employees(new_user.get("telegram_id"),
    #          new_user.get("first_name"),
    #          new_user.get("last_name"),
    #          user_role)
    add_employee_approval(senior_telegram_id, new_user.get("telegram_id"))

    await callback_query.answer("Пользователь успешно подтверждён!")
    await bot.send_message(chat_id=new_user.get("telegram_id"),
                           text="Ваша заявка принята",
                           reply_markup=menu_by_role(user_role))
    await state.clear()


@general.callback_query(F.data.startswith('reject'), UserRegistrationObject.waiting_for_confirmation)
async def get_reject_by_wne_user(callback_query: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    new_user = data.get("new_user")
    await callback_query.answer("Пользователь отклонён!")
    await bot.send_message(chat_id=new_user.get("telegram_id"),
                           text="Ваша заявка отклонена")
    await state.clear()


@general.callback_query(F.data.startswith('lang_'))
async def get_selected_language(callback_query: CallbackQuery):
    user_id = callback_query.from_user.id
    user = UserCookies(user_id)
    new_selected_language = F.data.split("_")[1]
    user.set_lang(new_selected_language)
    lang = user.get_lang()
    await callback_query.answer(lang.get("language").get("accept_lang"))
