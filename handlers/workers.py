from aiogram import Router, F
from aiogram.types import CallbackQuery

worker = Router()


@worker.callback_query(F.data == '')
async def car_list_in_work(callback: CallbackQuery):
    pass
