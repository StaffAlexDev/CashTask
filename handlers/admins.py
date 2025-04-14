import os

from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.filters import or_f
from aiogram.types import CallbackQuery, Message
from dotenv import find_dotenv, load_dotenv

from keyboards.general import get_car_keyboard_from_list
from settings import bot
from database.db_crud import (add_order, get_client_cars, add_finance_by_car, get_car_id_by_license_plate,
                              get_cars_and_owner_by_model, get_client_id_by_phone_number)
from database.state_models import OrderStates, FinanceStates
from keyboards.admins import (get_cars_keyboard, get_services_keyboard, get_confirmation_keyboard,
                              get_finance_kb, order_type_kb)

from utils import is_likely_license_plate, is_phone_number, clean_phone_number

load_dotenv(find_dotenv())
admins = Router()


@admins.message(F.text == os.getenv("ADMIN_PASS"))
async def admin_password(message: Message):
    await bot.send_message()
    await message.answer("вижу ты знаешь пароль администратора")


# ----------------- ORDERS MENU ----------------------

@admins.message(F.data == "new_order")
async def order_menu(callback_query: CallbackQuery):
    await callback_query.answer()
    await callback_query.message.answer("Выбери тип", reply_markup=order_type_kb())


@admins.message(F.data.startswith("by_"))
async def order_menu(callback_query: CallbackQuery, state: FSMContext):
    await callback_query.answer()
    choice = callback_query.data.split("_")[1]
    match choice:
        case "client":
            await state.set_state(OrderStates.waiting_for_client)
            await callback_query.message.answer("Введи номер телефона клиента")
        case "car":
            await state.set_state(OrderStates.waiting_for_car)
            await callback_query.message.answer("Введи номер авто или модель")


# Обработка выбора автомобиля
@admins.callback_query(OrderStates.waiting_for_car)
async def process_car_selection(message: Message, state: FSMContext):
    data = message.text

    if is_likely_license_plate(data):

        car_id = get_car_id_by_license_plate(data)
        await state.update_data(car_id=car_id)
        await state.set_state(OrderStates.waiting_for_service)
        await message.answer("Введите работы: Можно список работ через запятую!\n"
                             "Также можете в скобках указать цену работ. Пример:\n"
                             "рихтовка(цена), ...")
    else:
        cars = get_cars_and_owner_by_model(data)

        if not cars:
            await message.answer("Простите, такой модели нет в базе")
        else:
            keyboard = get_car_keyboard_from_list(cars)
            await message.answer("Выберите автомобиль", reply_markup=keyboard)


@admins.callback_query(OrderStates.waiting_for_client)
async def process_car_selection_by_client(message: Message, state: FSMContext):
    phone = clean_phone_number(message.text)
    if is_phone_number(phone):

        client_id = get_client_id_by_phone_number(phone)
        client_cars = get_client_cars(client_id)

        if not client_cars:
            await message.answer("У клиента нет машин, нужно добавить хотя-бы одну машину")
            # TODO добавить опросник для создания автомобиля клиенту или переспросить клиента

        elif len(client_cars) == 1:
            car = client_cars[0]
            car_id = car["car_id"]
            await state.update_data(car_id=car_id)
            await state.set_state(OrderStates.waiting_for_service)
            await message.answer("Введите работы: Можно список работ через запятую!\n"
                                 "Также можете в скобках указать цену работ. Пример:\n"
                                 "рихтовка(цена), ...")

        elif len(client_cars) > 1:
            await message.answer("Выбери автомобиль клиента", reply_markup=get_car_keyboard_from_list(client_cars))


# Обработка выбора услуги
@admins.callback_query(OrderStates.waiting_for_service)
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
        cars = await get_client_cars(user_id)
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


# -----------------Finances-----------------------------------
@admins.callback_query(F.data.startswith("finance_"))
async def finance_income(callback_query: CallbackQuery, state: FSMContext):
    type_finance = callback_query.data.split("_")[1]
    if type_finance == "report":
        pass
    else:
        await state.update_data(type_finance=type_finance)
        await callback_query.message.edit_text("Выберите тип дохода!", reply_markup=get_finance_kb())
    await callback_query.answer()


@admins.callback_query(F.data == "from_car")
async def income_from_the_car(callback_query: CallbackQuery):
    await callback_query.answer()


@admins.callback_query(F.data == "general")
async def income_from_the_car(callback_query: CallbackQuery, state: FSMContext):
    await state.update_data(type_investments=callback_query.data)
    await state.set_state(FinanceStates.investments)
    await callback_query.answer()
    await callback_query.message.answer("Введите сумму и \nописание с новой строки:")


@admins.message(FinanceStates.investments)
async def wait_sum(message: Message, state: FSMContext):
    state_data = await state.get_data()
    type_finance = state_data["type_finance"]
    type_investments = state_data["type_investments"]  # TODO перепроверить последовательно состояния
    data = message.text.split("\n")
    amount = int(data[0])
    description = data[1]
    admin_id = message.from_user.id
    add_finance_by_car(amount=amount, finance_type=type_finance, description=description,  admin_id=admin_id)

    print(f"Сумма инвестиции: {amount}")
    await message.answer(f"Сумма {amount} сохранена!")
    await state.clear()

