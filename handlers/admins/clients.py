from aiogram import F
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery

from handlers.admins import admins


@admins.callback_query(F.data.startswith("add_"))
async def finance_income(callback_query: CallbackQuery, state: FSMContext):
    pass


@admins.callback_query(F.data.startswith("all_"))
async def finance_income(callback_query: CallbackQuery, state: FSMContext):
    pass
