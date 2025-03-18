from aiogram import Router, F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery

from database.db_crud import get_user_by_telegram_id, get_approvers_for_role, approve_user
from database.state_models import UserCookies, UserRegistrationObject
from keyboards.general import roles_kb, get_access_confirmation
from settings import bot

general = Router()


@general.message(Command("start"))
async def admin_start(message: Message, state: FSMContext):
    user_id = message.from_user.id
    user_db = get_user_by_telegram_id(user_id)
    lang = UserCookies(user_id).get_lang()
    print(user_db)

    if user_db is None:
        await message.answer(lang.get("unknown_user").get("greetings"), reply_markup=roles_kb())
        new_user = {
            "telegram_id": message.from_user.id,
            "first_name": message.from_user.first_name,
            "last_name": message.from_user.last_name,
        }
        await state.update_data(new_user=new_user)
        await state.set_state(UserRegistrationObject.waiting_for_confirmation)

    else:
        pass


@general.callback_query(F.data.startswith('role_'))
async def choice_role(callback_query: CallbackQuery):
    await callback_query.answer()
    user_id = callback_query.message.from_user.id
    lang = UserCookies(user_id).get_lang()
    lng_message = lang.get("info").get("user_accept")
    msg_list = lng_message.split(":")
    message = msg_list[0] + callback_query.from_user.username + msg_list[1]

    role_list = get_approvers_for_role(callback_query.data[5:])
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

    if not new_user:
        await callback_query.answer("Ошибка: нет данных о пользователе.")
        return

    # Добавляем пользователя в БД
    senior_telegram_id = callback_query.from_user.id
    approve_user(new_user.get("telegram_id"), senior_telegram_id)

    await callback_query.answer("Пользователь успешно подтверждён!")
    await bot.send_message(chat_id=new_user.get("telegram_id"),
                           text="Ваша заявка принята",)
                           # reply_markup=)
    await state.clear()

