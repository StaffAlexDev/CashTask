from aiogram import F
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery

from database.companies_pg import add_company, get_company_by_code, get_company_by_id
from database.employees_pg import add_employee
from handlers.general import general
from handlers.general.other import show_start_menu
from keyboards.other import enum_kb, common_kb_by_role, get_navigate_kb
from models.fsm_states import StartState
from models.user_context import UserContext
from utils.enums import Role


@general.callback_query(F.data.startswith("company_"))
async def company_checked(callback: CallbackQuery, state: FSMContext, user: UserContext):
    await callback.answer()
    lang = user.lang
    action = callback.data.split("_")[1]

    match action:
        case "crate":
            await callback.message.edit_text("Введите название вашей компании!")
            await state.set_state(StartState.waiting_company_name)
        case "join":
            await callback.message.edit_text("Введите код-приглашения вашей компании!")
            await state.set_state(StartState.waiting_invite_code)


@general.message(StartState.waiting_company_name, ~(F.text.startswith('/')))
async def process_add_company(message: Message, state: FSMContext, user: UserContext):
    lang = user.lang
    company_name = message.text

    company_id, invite_code = await add_company(company_name)
    await add_employee(company_id, user.telegram_id, message.from_user.first_name, Role.SUPERVISOR)
    await message.answer(f"Вы зарегистрировали {company_name}")
    await message.answer(f"Ваша ссылка для приглашения сотрудников\n "
                         f"https://t.me/Garage_administrator_bot?start={invite_code}")
    await message.answer(
        lang.greetings.welcome,
        reply_markup=common_kb_by_role("main_menu", lang, user.role)
    )

    await state.clear()


@general.message(StartState.waiting_invite_code, ~(F.text.startswith('/')))
async def process_invite_code(message: Message, state: FSMContext, user: UserContext):
    code = message.text.strip() or (await state.get_data()).get("invite_code")
    company = await get_company_by_code(code)
    if not company:

        return await message.answer(
            "Код не найден. Нажмите «← Назад», чтобы вернуться.",
            reply_markup=get_navigate_kb(user.lang, 1)
        )

    # Успешно — добавляем работника и сбрасываем FSM
    await add_employee(user.company_id, message.from_user.id, message.from_user.first_name, user.role)
    await state.clear()
    # После регистрации снова возвращаемся в стартовое меню
    return await show_start_menu(message, state)


@general.callback_query(F.data == "get_my_company")
async def push_company_name(callback: CallbackQuery, user: UserContext):
    await callback.answer()
    lang = user.lang
    name, invite_code = get_company_by_id(user.company_id)
    await callback.message.edit_text(f"Название: {name}\n"
                                     f"Код для приглашения: {invite_code}\n"
                                     f"Прямая ссылка для новых пользователей:\n "
                                     f"https://t.me/Garage_administrator_bot?start={invite_code}",
                                     reply_markup=common_kb_by_role("main_menu", lang, user.role))
