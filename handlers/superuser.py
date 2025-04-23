import os

from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery
from dotenv import find_dotenv, load_dotenv
from aiogram import Router, F

from database.db_crud import get_financial_report, add_employee
from keyboards.general import menu_by_role
from keyboards.superuser import period_by_report_kb

load_dotenv(find_dotenv())
superuser = Router()


@superuser.message(F.text == os.getenv("SUPERADMIN_PASS"))
async def admin_password(message: Message):
    telegram_id = message.from_user.id
    first_name = message.from_user.first_name
    last_name = message.from_user.last_name
    role = "superadmin"

    add_employee(telegram_id=telegram_id,
                 first_name=first_name,
                 last_name=last_name,
                 role=role)

    await message.answer("Привет Superadmin", reply_markup=menu_by_role(role))


async def choice_period(callback_query: CallbackQuery):
    await callback_query.answer()
    await callback_query.message.answer("Выберите период", reply_markup=period_by_report_kb())


@superuser.callback_query(F.data.startswith('period_'))
async def choice_role(callback_query: CallbackQuery):

    period = callback_query.data.split("_")[1]
    period_map = get_financial_report(period)
    print(period_map)  # TODO дописать логику вывода данных по периоду
    text = f"""
        'period': {period_map.get("period")},\n
        'start_date': {period_map.get("start_date")},\n
        'end_date': {period_map.get("end_date")},\n
        'total_income': {period_map.get("total_income")},\n
        'total_expense': {period_map.get("total_expense")},\n
        'profit': {period_map.get("profit")},\n
        'summary': {period_map.get("summary")},\n
        'transactions': {period_map.get("transactions")}
    """
    await callback_query.answer(text, show_alert=True)

