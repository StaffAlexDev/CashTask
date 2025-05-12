
from aiogram import Router, F
from aiogram.types import CallbackQuery

from database.employees_pg import get_approver_employees_telegram_id, add_employee, add_employee_approval
from database.general_pg import add_temporary_data, get_temporary_data
from database.state_models import UserContext
from keyboards.other import get_access_confirmation, common_kb_by_role
from utils.parsers import parse_enum_callback
from settings import bot
from utils.enums import Role

general = Router()


@general.callback_query(F.data.startswith('role_'))
async def choice_role(callback: CallbackQuery, user: UserContext):
    await callback.answer()
    role = parse_enum_callback(callback.data, "role", Role)
    user_name = callback.from_user.first_name
    lang = user.lang
    message = lang.info.new_user_info_notif.format(name=user_name, position=role.value)
    print(f"message: {message}")
    telegram_id = callback.from_user.id
    first_name = callback.from_user.first_name

    new_worker_data = {
                       "telegram_id": telegram_id,
                       "first_name": first_name,
                       "role": role.value
                       }
    print(new_worker_data)
    key = await add_temporary_data(new_worker_data)
    print(f" key: {key}")
    # Уходит запрос на должность выше
    list_of_confirmers = await get_approver_employees_telegram_id(role, user.telegram_id)

    for tele_id in list_of_confirmers:
        user_confirmers = UserContext(tele_id)
        lang_user_confirmers = user_confirmers.lang
        await bot.send_message(chat_id=tele_id,
                               text=message,
                               reply_markup=get_access_confirmation(key, lang_user_confirmers))

    msg_for_new_user = lang.greetings.waiting_accept

    await callback.message.edit_text(msg_for_new_user)


@general.callback_query(F.data.startswith('access_'))
async def get_accept_by_new_user(callback: CallbackQuery, user: UserContext):
    await callback.answer()
    callback_data = callback.data.split("_")
    print(f"callback_data после split: {callback_data}")
    action = callback_data[1]
    lang = user.lang
    key = callback_data[2]
    print(f"Key: {key}")
    new_user_data = await get_temporary_data(key)

    print(f"Type: {type(new_user_data)}")
    print(f"Data: {new_user_data}")

    if not new_user_data:
        await callback.answer(lang.err.no_user_data)
        print(f"new_user object: {new_user_data}")
        return

    telegram_id: int = new_user_data.get("telegram_id")
    first_name = new_user_data.get("first_name")
    user_role = new_user_data.get("role")

    if not new_user_data:
        await callback.answer(lang.err.no_user_data)
        print(f"new_user object: {new_user_data}")
        return
    match action:
        case "accept":
            senior_telegram_id = user.telegram_id
            lang = user.lang
            await add_employee(telegram_id=telegram_id,
                               first_name=first_name,
                               role=user_role)

            await add_employee_approval(senior_telegram_id, telegram_id)

            await callback.answer(lang.info.user_accept)
            lang_by_new_user = UserContext(telegram_id).lang
            role_by_new_user = UserContext(telegram_id).get_role()
            await bot.send_message(chat_id=telegram_id,
                                   text=lang_by_new_user.info.user_accept_confirm,
                                   reply_markup=common_kb_by_role("main_menu", lang_by_new_user, role_by_new_user))

        case "reject":
            await callback.answer(lang.info.user_rejected)
            await bot.send_message(chat_id=telegram_id,
                                   text=lang.info.your_been_rejected)


@general.callback_query(F.data.startswith('lang_'))
async def get_selected_language(callback: CallbackQuery, user: UserContext):
    await callback.answer()
    selected_language = callback.data.split("_", 1)[1]
    await user.update_lang(selected_language)
    lang = user.lang
    await callback.answer(lang.language.accept_lang)
