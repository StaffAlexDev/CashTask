import os

from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery
from dotenv import find_dotenv, load_dotenv
from aiogram import Router, F

from database.db_crud import get_financial_report
from keyboards.general import menu_by_role
from keyboards.superuser import period_by_report_kb

load_dotenv(find_dotenv())
superuser = Router()


# @superuser.message(F.text == os.getenv("SUPERADMIN_PASS"))
# async def admin_password(message: Message):
#     add_employees(message.from_user.id,
#              message.from_user.first_name,
#              message.from_user.last_name,
#              "super_admin")
#     await message.answer("Привет Superadmin", reply_markup=menu_by_role("super_admin"))


async def choice_period(callback_query: CallbackQuery, state: FSMContext):
    await callback_query.answer()
    await callback_query.message.answer("Выберите период", reply_markup=period_by_report_kb())


@superuser.callback_query(F.data.startswith('period_'))
async def choice_role(callback_query: CallbackQuery):
    await callback_query.answer()
    period = callback_query.data.split("_")[1]
    result = get_financial_report(period)
    print(result)
