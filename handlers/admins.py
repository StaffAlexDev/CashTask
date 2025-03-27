import os

from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.filters import Command
from aiogram.filters import or_f
from aiogram.types import CallbackQuery, Message
from dotenv import find_dotenv, load_dotenv

from settings import bot
from database.db_crud import add_order, get_user_cars, add_finance_record
from database.state_models import OrderStates, FinanceStates
from keyboards.admins import (get_cars_keyboard, get_services_keyboard, get_confirmation_keyboard,
                              get_finance_income_kb, get_finance_expense_kb)

load_dotenv(find_dotenv())
admins = Router()


@admins.message(F.text == os.getenv("ADMIN_PASS"))
async def admin_password(message: Message):
    await bot.send_message()
    await message.answer("вижу ты знаешь пароль администратора")


@admins.callback_query(F.data == "income")
async def finance_income(callback_query: CallbackQuery):
    await callback_query.answer()
    await callback_query.message.answer("Выберите тип дохода!", reply_markup=get_finance_income_kb())


@admins.callback_query(F.data == "expense")
async def finance_income(callback_query: CallbackQuery):
    await callback_query.answer()
    await callback_query.message.answer("Выберите тип расхода!", reply_markup=get_finance_expense_kb())


@admins.callback_query(F.data == "from_the_car")
async def income_from_the_car(callback_query: CallbackQuery):
    await callback_query.answer()


@admins.callback_query(F.data == "investments")
async def income_from_the_car(callback_query: CallbackQuery, state: FSMContext):
    await state.update_data(type_finance=callback_query.data)
    await state.set_state(FinanceStates.investments)
    await callback_query.answer()
    await callback_query.message.answer("Введите сумму и \nописание с новой строки:")


@admins.message(FinanceStates.investments)
async def wait_sum(message: Message, state: FSMContext):
    state_data = await state.get_data()
    amount_type = state_data["type_finance"]
    data = message.text.split("\n")
    amount = data[0]
    description = data[1]
    admin_id = message.from_user.id
    add_finance_record(amount=amount, description=description, amount_type=amount_type, admin_id=admin_id)

    print(f"Сумма инвестиции: {amount}")
    await message.answer(f"Сумма {amount} сохранена!")
    await state.clear()


# Старт опросника
@admins.message(Command("order"))
async def start_order(message: Message, state: FSMContext):

    user_id = message.from_user.id
    cars = await get_user_cars(user_id)

    if not cars:
        await message.answer("У вас нет зарегистрированных автомобилей.")
        return

    await message.answer("Выберите автомобиль:", reply_markup=get_cars_keyboard(cars))
    await state.set_state(OrderStates.waiting_for_car)


# Обработка выбора автомобиля
@admins.callback_query(OrderStates.waiting_for_car, lambda c: c.data.startswith("car_"))
async def process_car_selection(callback_query: CallbackQuery, state: FSMContext):

    car_id = int(callback_query.data.split("_")[1])

    await state.update_data(car_id=car_id)
    await callback_query.message.answer("Выберите услугу:", reply_markup=get_services_keyboard())
    await state.set_state(OrderStates.waiting_for_service)


# Обработка выбора услуги
@admins.callback_query(OrderStates.waiting_for_service, lambda c: c.data.startswith("service_"))
async def process_service_selection(callback_query: CallbackQuery, state: FSMContext):
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
@admins.callback_query(F.data == ["confirm", "back", "cancel"], OrderStates.waiting_for_confirmation)
async def process_confirmation(callback_query: CallbackQuery, state: FSMContext):
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
@admins.callback_query(F.data == "back",
                       or_f(OrderStates.waiting_for_service, OrderStates.waiting_for_confirmation)
                       )
async def process_back(callback_query: CallbackQuery, state: FSMContext):
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
@admins.callback_query(F.data == "cancel")
async def process_cancel(callback_query: CallbackQuery, state: FSMContext):
    await callback_query.message.answer("Заказ отменен.")
    await state.clear()
