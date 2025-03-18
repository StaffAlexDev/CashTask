from aiogram import Router, types
from aiogram.filters import Command

service_router = Router()


@service_router.message(Command('carservice'))
async def admin_start(message: types.Message):
    await message.answer('I see service button!')
