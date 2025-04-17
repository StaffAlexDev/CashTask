from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery

from database.db_crud import add_employee_approval, add_employee, get_approver_employees_telegram_id
from database.state_models import UserCookies, UserRegistrationObject
from keyboards.general import get_access_confirmation, menu_by_role
from settings import bot

general = Router()


@general.callback_query(F.data.startswith('role_'))
async def choice_role(callback_query: CallbackQuery, state: FSMContext):
    await callback_query.answer()
    print(f"tg: {callback_query.from_user.id}")
    print(f"name: {callback_query.from_user.first_name}")
    print(f"role: {callback_query.data.split("_")[1]}")
    user_id = callback_query.message.from_user.id
    lang = UserCookies(user_id).get_lang()
    lng_message = lang.get("info").get("user_accept")
    msg_list = lng_message.split(":")
    message = msg_list[0] + callback_query.from_user.first_name + msg_list[1]
    user_role = callback_query.data.split("_")[1]
    print(f"user_role: {user_role}")
    await state.update_data(user_role=user_role)
    new_worker = {
        "telegram_id": callback_query.from_user.id,
        "first_name": callback_query.from_user.first_name,
        "last_name": callback_query.from_user.last_name,
    }
    print(new_worker)
    await state.update_data(new_worker=new_worker)
    # Уходит запрос на должность выше
    role_list = get_approver_employees_telegram_id(user_role)
    print(f"role_list_id {role_list}")
    print(f"role_list_id {role_list[0]}")
    print(f"len role list: {len(role_list)}")
    for telegram_id in role_list:
        await bot.send_message(chat_id=telegram_id,
                               text=message,
                               reply_markup=get_access_confirmation())

    lng_msg = lang.get('unknown_user').get('waiting_accept')
    msg_list = lng_msg.split(":")
    sec_message = f"{msg_list[0]} {callback_query.data.split("_")[1]}{msg_list[1]}"
    print(f"msg_list {msg_list}")
    print(f"lng_msg {lng_msg}")
    print(f"callback_query {callback_query.from_user.first_name}")
    await callback_query.message.answer(sec_message)


# TODO Исправить передачу данных не через state, а напрямую через callback_data и создаваемой клавиатуре
@general.callback_query(F.data == 'accept')
async def get_accept_by_user(callback_query: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    new_user = data.get("new_worker")
    user_role = data.get("user_role")
    if not new_user:
        await callback_query.answer("Ошибка: нет данных о пользователе.")
        print(f"new_user object: {new_user}")
        return

    # Добавляем пользователя в БД
    senior_telegram_id = callback_query.from_user.id

    add_employee(new_user.get("telegram_id"),
                 new_user.get("first_name"),
                 user_role)
    add_employee_approval(senior_telegram_id, new_user.get("telegram_id"))

    await callback_query.answer("Пользователь успешно подтверждён!")
    await bot.send_message(chat_id=new_user.get("telegram_id"),
                           text="Ваша заявка принята",
                           reply_markup=menu_by_role(user_role))
    await state.clear()


@general.callback_query(F.data == 'reject')
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
    selected_language = F.data.split("_")[1]
    user.update_profile(lang=selected_language)
    lang = user.get_lang()
    await callback_query.answer(lang.get("language").get("accept_lang"))



