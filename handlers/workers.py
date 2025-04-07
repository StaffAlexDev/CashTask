from aiogram import Router, F
from aiogram.types import CallbackQuery

from database.db_crud import get_orders_by_worker, get_role_by_telegram_id
from keyboards.general import menu_by_role

worker = Router()


@worker.callback_query(F.data == 'car_in_work')
async def car_list_in_work(callback_query: CallbackQuery):
    worker_id = callback_query.from_user.id
    car_list = get_orders_by_worker(worker_id)
    role = get_role_by_telegram_id(worker_id)

    await callback_query.answer()

    if car_list is not None:
        await callback_query.message.answer("Вот ваши машины в работе:")
        for car in car_list:
            await callback_query.message.answer(f"car_brand: {car.get("car_brand")}"
                                                f"car_model: {car.get("car_model")}"
                                                f"license_plate: {car.get("license_plate")}"
                                                f"vin_code: {car.get("vin_code")}")
    else:
        await callback_query.message.answer("У вас нет машин в работе", reply_markup=menu_by_role(role))
