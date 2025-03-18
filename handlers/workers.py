from aiogram import Router, types
from aiogram.filters import Command

from database.db_crud import get_user_by_telegram_id

workers_router = Router()


@workers_router.message(Command('washing'))
async def admin_start(message: types.Message):
    await message.answer('I see workers button!')
