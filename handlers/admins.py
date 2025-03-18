import os

from aiogram import Router, types, F
from aiogram.fsm.context import FSMContext
from aiogram.filters import Command
from aiogram.filters import or_f
from dotenv import find_dotenv, load_dotenv

from settings import bot
from database.db_crud import add_order, get_user_cars
from database.state_models import OrderStates
from keyboards.admins import get_cars_keyboard, get_services_keyboard, get_confirmation_keyboard

load_dotenv(find_dotenv())
admin_router = Router()


@admin_router.message(F.text == os.getenv("ADMIN_PASS"))
async def admin_password(message: types.Message):
    await bot.send_message()
    await message.answer("вижу ты знаешь пароль администратора")


# Старт опросника
@admin_router.message(Command("order"))
async def start_order(message: types.Message, state: FSMContext):

    user_id = message.from_user.id
    cars = await get_user_cars(user_id)

    if not cars:
        await message.answer("У вас нет зарегистрированных автомобилей.")
        return

    await message.answer("Выберите автомобиль:", reply_markup=get_cars_keyboard(cars))
    await state.set_state(OrderStates.waiting_for_car)


# Обработка выбора автомобиля
@admin_router.callback_query(OrderStates.waiting_for_car, lambda c: c.data.startswith("car_"))
async def process_car_selection(callback_query: types.CallbackQuery, state: FSMContext):

    car_id = int(callback_query.data.split("_")[1])

    await state.update_data(car_id=car_id)
    await callback_query.message.answer("Выберите услугу:", reply_markup=get_services_keyboard())
    await state.set_state(OrderStates.waiting_for_service)


# Обработка выбора услуги
@admin_router.callback_query(OrderStates.waiting_for_service, lambda c: c.data.startswith("service_"))
async def process_service_selection(callback_query: types.CallbackQuery, state: FSMContext):
    service = callback_query.data.split("_")[1]
    await state.update_data(service=service)

    data = await state.get_data()
    car_id = data["car_id"]
    service = data["service"]

    await callback_query.message.answer(
        f"Вы выбрали:\n"
        f"Автомобиль: {car_id}\n"
        f"Услуга: {service}\n\n"
        f"Подтвердите заказ:",
        reply_markup=get_confirmation_keyboard()
    )
    await state.set_state(OrderStates.waiting_for_confirmation)


# Обработка подтверждения
@admin_router.callback_query(OrderStates.waiting_for_confirmation, F.data in ["confirm", "back", "cancel"])
async def process_confirmation(callback_query: types.CallbackQuery, state: FSMContext):
    if callback_query.data == "confirm":
        data = await state.get_data()
        car_id = data["car_id"]
        service = data["service"]

        await add_order(car_id=car_id, service=service, user_id=callback_query.from_user.id)

        await callback_query.message.answer("Заказ успешно оформлен!")
        await state.clear()
    elif callback_query.data == "back":
        await callback_query.message.answer("Выберите услугу:", reply_markup=get_services_keyboard())
        await state.set_state(OrderStates.waiting_for_service)
    else:
        await callback_query.message.answer("Заказ отменен.")
        await state.clear()


# Обработка возврата на предыдущий шаг
@admin_router.callback_query(F.data == "back",
                             or_f(OrderStates.waiting_for_service, OrderStates.waiting_for_confirmation)
                             )
async def process_back(callback_query: types.CallbackQuery, state: FSMContext):
    current_state = await state.get_state()

    if current_state == OrderStates.waiting_for_service:
        # Возвращаемся к выбору автомобиля
        user_id = callback_query.from_user.id
        cars = await get_user_cars(user_id)
        await callback_query.message.answer("Выберите автомобиль:", reply_markup=get_cars_keyboard(cars))
        await state.set_state(OrderStates.waiting_for_car)
    elif current_state == OrderStates.waiting_for_confirmation:
        # Возвращаемся к выбору услуги
        await callback_query.message.answer("Выберите услугу:", reply_markup=get_services_keyboard())
        await state.set_state(OrderStates.waiting_for_service)


# Обработка отмены
@admin_router.callback_query(F.data == "cancel")
async def process_cancel(callback_query: types.CallbackQuery, state: FSMContext):
    await callback_query.message.answer("Заказ отменен.")
    await state.clear()
