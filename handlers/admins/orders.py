from aiogram import F
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message

from database.clients_pg import get_car_by_id, get_car_id_by_license_plate, get_cars_and_owner_by_model, \
    get_client_cars, get_client_id_by_phone_number
from database.orders_pg import add_order
from database.state_models import OrderStates
from handlers.admins import admins
from keyboards.admins import order_type_kb, get_confirmation_kb
from utils.validators import is_likely_license_plate, normalize_number, is_phone_number


@admins.message(F.data == "new_order")
async def order_menu(callback: CallbackQuery):
    await callback.answer()
    await callback.message.answer("Выбери тип", reply_markup=order_type_kb())


@admins.message(F.data.startswith("by_"))
async def order_menu(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    choice = callback.data.split("_")[1]
    match choice:
        case "client":
            await state.set_state(OrderStates.waiting_for_client)
            await callback.message.answer("Введи номер телефона клиента")
        case "car":
            await state.set_state(OrderStates.waiting_for_car)
            await callback.message.answer("Введи номер авто или модель")


# Обработка выбора автомобиля
@admins.callback_query(OrderStates.waiting_for_car)
async def process_car_selection(message: Message, state: FSMContext):
    data = message.text

    if is_likely_license_plate(data):

        car_id = await get_car_id_by_license_plate(data)
        car = get_car_by_id(car_id)
        await state.update_data(car_id=car_id)
        await state.update_data(car=car)

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
    phone = normalize_number(message.text)
    if is_phone_number(phone):

        client_id = await get_client_id_by_phone_number(phone)
        client_cars = await get_client_cars(client_id)

        if not client_cars:
            await message.answer("У клиента нет машин, нужно добавить хотя-бы одну машину")
            # TODO добавить опросник для создания автомобиля клиенту или переспросить клиента

        elif len(client_cars) == 1:
            car = client_cars[0]
            car_id = car["car_id"]
            await state.update_data(car_id=car_id)
            await state.update_data(car=car)
            await state.set_state(OrderStates.waiting_for_service)
            await message.answer("Введите работы: Можно список работ через запятую!\n"
                                 "Также можете в скобках указать цену работ. Пример:\n"
                                 "рихтовка(цена), ...")

        elif len(client_cars) > 1:
            await message.answer("Выбери автомобиль клиента", reply_markup=get_car_keyboard_from_list(client_cars))


@admins.message(F.data.startswith("car_id_"))
async def order_menu(callback: CallbackQuery, state: FSMContext):
    car_id: int = int(callback.data.split("_")[2])
    car = await get_car_by_id(car_id)
    await state.update_data(car_id=car_id)
    await state.update_data(car=car)
    await state.set_state(OrderStates.waiting_for_service)
    await callback.message.answer("Введите работы: Можно список работ через запятую!\n"
                                  "Также можете в скобках указать цену работ. Пример:\n"
                                  "рихтовка(цена), ...")


@admins.callback_query(OrderStates.waiting_for_service)
async def process_service_selection(message: Message, state: FSMContext):
    service = message.text.split(",")
    await state.update_data(service=service)
    # await message.answer(
    #     f"Вы выбрали:\n"
    #     f"Автомобиль: {car_id}\n"
    #     f"Услуга: {" ".join(service)}\n"
    #     f"Подтвердите заказ-наряд:",
    #     reply_markup=get_confirmation_kb()
    # )
    await message.answer("Выберите сотрудника для выполнения", reply_markup=get_employer_kb())
    await state.set_state(OrderStates.waiting_for_employer)


@admins.callback_query(F.data.startswith("employer_"), OrderStates.waiting_for_employer)
async def process_employer_selection(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    car_model = data["car"]["car_model"]
    license_plate = data["car"]["license_plate"]
    service = data["service"]
    employees = callback.data.split("_")[1]
    await state.update_data(employer=employees)
    await callback.message.answer(
        f"Вы выбрали:\n"
        f"Автомобиль: {car_model}, {license_plate}\n"
        f"Услуга: {" ".join(service)}\n"
        f"Подтвердите заказ-наряд:",
        reply_markup=get_confirmation_kb()
    )


@admins.callback_query(F.data == "confirm", OrderStates.waiting_for_order_confirmation)
async def process_confirm(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    car_id = data["car_id"]
    description = data["service"]
    employees = data["employer"]
    await add_order(car_id=car_id, description=description, worker_id=employees)
    await callback.message.answer("Заказ успешно оформлен!")
    await state.clear()


@admins.callback_query(F.data == "back")
async def process_back(callback: CallbackQuery, state: FSMContext):
    current_state = await state.get_state()

    if current_state == OrderStates.waiting_for_service:
        # Возврат к выбору авто
        user_id = callback.from_user.id
        cars = await get_client_cars(user_id)
        await callback.message.answer("Выберите автомобиль:", reply_markup=get_cars_kb(cars))
        await state.set_state(OrderStates.waiting_for_car)

    elif current_state == OrderStates.waiting_for_order_confirmation:
        # Возврат к выбору услуги
        await callback.message.answer("Введите работы: Можно список работ через запятую!\n"
                                      "Также можете в скобках указать цену работ. Пример:\n"
                                      "рихтовка(цена), ...")
        await state.set_state(OrderStates.waiting_for_service)

    elif current_state == OrderStates.waiting_for_car:
        await callback.message.answer("Вы вернулись назад. Введи номер авто или модель.")
        await state.set_state(OrderStates.waiting_for_car)
    else:
        await callback.message.answer("Не удалось вернуться назад — неизвестное состояние.")


@admins.callback_query(F.data == "cancel", OrderStates.waiting_for_order_confirmation)
async def process_cancel_from_confirmation(callback: CallbackQuery, state: FSMContext):
    await callback.message.answer("Заказ отменен.")
    await state.clear()
