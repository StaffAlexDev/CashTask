from aiogram import Router, F
from aiogram.types import CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton

from database.db_crud import get_orders_by_worker, get_role_by_telegram_id

worker = Router()


@worker.callback_query(F.data == 'order_in_work')
async def car_list_in_work(callback: CallbackQuery):
    worker_id = callback.from_user.id
    car_list = get_orders_by_worker(worker_id)
    role = get_role_by_telegram_id(worker_id)

    await callback.answer()

    if car_list:
        await callback.message.answer("Вот ваши машины в работе:")
        for car in car_list:

            button_text = f"{car.get('car_brand')} {car.get('car_model')} {car.get('license_plate')}"
            if len(button_text) > 64:
                button_text = button_text[:60] + "..."

            keyboard = InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text=button_text, callback_data=f"car_{car.get('id')}")]
            ])
            await callback.message.answer("Выберите машину:", reply_markup=keyboard)
    else:
        await callback.message.answer("У вас нет машин в работе", reply_markup=menu_by_role(role))
