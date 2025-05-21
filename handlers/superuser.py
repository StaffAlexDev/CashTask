import os

from aiogram.types import Message, CallbackQuery
from dotenv import find_dotenv, load_dotenv
from aiogram import Router, F

from database.clients_pg import restore_car_by_id, restore_client_by_id
from database.employees_pg import add_employee
from database.finance_pg import get_financial_report
from models.user_context import UserContext
from keyboards.other import enum_kb
from utils.parsers import parse_enum_callback
from utils.enums import Period, Role

load_dotenv(find_dotenv())
superuser = Router()


@superuser.message(F.text == os.getenv("SUPERADMIN_PASS"))
async def admin_password(message: Message, user: UserContext):
    telegram_id = user.telegram_id
    first_name = message.from_user.first_name
    role = Role.SUPERVISOR

    await add_employee(telegram_id=telegram_id,
                       first_name=first_name,
                       role=role)

    await message.answer("Привет Superadmin")


@superuser.callback_query(F.data == "choose_period")
async def choose_period(callback: CallbackQuery, user: UserContext):
    await callback.message.edit_text(
        "Выберите период для отчета:",
        reply_markup=enum_kb(Period.for_ui(), user.lang, callback_prefix="period")
    )


@superuser.callback_query(F.data.startswith("period_"))
async def period_selected(callback: CallbackQuery, user: UserContext):
    period = parse_enum_callback(callback.data, "period", Period)

    if period is None:
        await callback.answer("❗ Ошибка выбора периода", show_alert=True)
        return

    report = get_financial_report(period=period.value)

    await callback.message.edit_text(f"Ваш отчет за период {period.display_name(user.lang)}:\n{report}")


@superuser.callback_query(F.data.startswith("item_") & F.data.endswith("_restore"))
async def handle_restore(callback: CallbackQuery, user: UserContext):
    _, item_type, item_id, _ = callback.data.split("_")
    item_id = int(item_id)

    if user.get_role().value != "superadmin":
        await callback.answer("⛔ Только для суперюзеров", show_alert=True)
        return

    if item_type == "client":
        success = restore_client_by_id(item_id)
        msg = "Клиент восстановлен" if success else "Не удалось восстановить клиента"
    elif item_type == "car":
        success = restore_car_by_id(item_id)
        msg = "Авто восстановлено" if success else "Не удалось восстановить авто"
    else:
        msg = "Невозможно восстановить этот тип"

    await callback.message.edit_text(f"✅ {msg}")
    await callback.answer()
