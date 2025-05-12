from aiogram import F
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message

from database.clients_pg import get_car_by_id, get_client_cars, get_client_id_by_phone_number
from database.employees_pg import get_all_employees
from database.orders_pg import add_order
from database.state_models import OrderStates, UserContext
from handlers.admins import admins
from keyboards.other import common_kb_by_role
from keyboards.paginations import get_paginated_list
from utils.validators import is_likely_license_plate, normalize_number, is_phone_number


@admins.message(F.data == "new_order")
async def order_menu(callback: CallbackQuery, user: UserContext):
    await callback.answer()
    lang = user.lang
    await callback.message.answer(lang.orders.order_types,
                                  reply_markup=common_kb_by_role("order_types", lang, user.get_role()))


@admins.message(F.data.startswith("by_"))
async def order_menu(callback: CallbackQuery, state: FSMContext, user: UserContext):
    await callback.answer()
    lang = user.lang
    choice = callback.data.split("_")[1]
    match choice:
        case "client":
            await state.set_state(OrderStates.waiting_for_client)
            await callback.message.answer(lang.orders.phone_client)
        case "car":
            await state.set_state(OrderStates.waiting_for_car)
            await callback.message.answer("Введи номер авто или модель")


# Обработка выбора автомобиля
@admins.callback_query(OrderStates.waiting_for_client)
async def process_car_selection_by_client(message: Message, state: FSMContext, user: UserContext):
    phone = normalize_number(message.text)
    if not is_phone_number(phone):
        return await message.answer("Неверный формат номера.")

    client_id = await get_client_id_by_phone_number(phone)
    cars = await get_client_cars(client_id)
    await state.update_data(client_cars=cars)  # сохраним список для пагинации

    if not cars:
        return await message.answer("У клиента нет машин, добавьте сначала авто.")

    # Если одна машина — сразу продолжаем…
    if len(cars) == 1:
        # … ваш код для единственной машины …
        return

    # Если несколько — показываем первую страницу
    text, keyboard = get_paginated_list(
        get_items_func=lambda **kw: cars,
        build_button_text=lambda c: f"{c['car_brand']} {c['car_model']} — {c['license_plate']}",
        callback_prefix="car",        # в callback ваши кнопки будут "car_1_\<id\>"
        back_callback="cancel",       # куда возвращаться по кнопке «🔙 Выйти»
        page=1,
        per_page=5,
        title="Выберите автомобиль клиента"
    )
    await message.answer(text, reply_markup=keyboard)
    await state.set_state(OrderStates.waiting_for_car)


@admins.callback_query(OrderStates.waiting_for_client)
async def process_car_selection_by_client(message: Message, state: FSMContext, user: UserContext):
    phone = normalize_number(message.text)
    if is_phone_number(phone):

        client_id = await get_client_id_by_phone_number(phone)
        client_cars = await get_client_cars(client_id)

        if not client_cars:
            await message.answer("У клиента нет машин, нужно добавить хотя-бы одну машину")
            # TODO добавить опросник для создания автомобиля клиенту или переспросить клиента

        elif len(client_cars) == 1:
            car_id = client_cars["car_id"]
            await state.update_data(car_id=car_id)
            await state.update_data(car=client_cars)
            await state.set_state(OrderStates.waiting_for_service)
            await message.answer("Введите работы: Можно список работ через запятую!\n"
                                 "Также можете в скобках указать цену работ. Пример:\n"
                                 "рихтовка(цена), ...")

        elif len(client_cars) > 1:
            text, keyboard = get_paginated_list(
                # передаём список из state
                get_items_func=lambda **kw: client_cars,
                # как рисовать каждую кнопку
                build_button_text=lambda car: f"{car['car_brand']} {car['car_model']} — {car['license_plate']}",
                # префикс для callback’ов: prev_1_client_car, next_1_client_car
                callback_prefix="client_car",
                # куда вернуться кнопкой “🔙 Выйти” или “Отмена”
                back_callback="cancel",
                # заголовок сообщения
                title="Выберите автомобиль клиента",
                # показываем первую страницу
                page=1,
                # сколько записей на странице
                per_page=5
            )
            await message.answer(text, reply_markup=keyboard)


@admins.message(F.data.startswith("car_id_"))
async def order_menu(callback: CallbackQuery, state: FSMContext, user: UserContext):
    car_id: int = int(callback.data.split("_")[2])
    car = await get_car_by_id(car_id)
    await state.update_data(car_id=car_id)
    await state.update_data(car=car)
    await state.set_state(OrderStates.waiting_for_service)
    await callback.message.answer("Введите работы: Можно список работ через запятую!\n"
                                  "Также можете в скобках указать цену работ. Пример:\n"
                                  "рихтовка(цена), ...")


@admins.message(OrderStates.waiting_for_service)
async def process_service_selection(
    message: Message,
    state: FSMContext,
    user: UserContext
):
    # Разбираем список услуг и сохраняем
    service = [s.strip() for s in message.text.split(",")]
    await state.update_data(service=service)

    # 1) Получаем полный список сотрудников (без фильтра или с учётом роли, если нужно)
    employees = await get_all_employees()

    # 2) Сохраняем в state, чтобы при листании не обращаться повторно к БД
    await state.update_data(employees_list=employees)

    # 3) Строим первую страницу
    text, keyboard = get_paginated_list(
        get_items_func=lambda **kw: employees,
        build_button_text=lambda e: f"{e['first_name']} {e['last_name']} — роль: {e['role']}",
        callback_prefix="assign",       # префикс для callback_data: prev_1_assign, next_1_assign
        back_callback="cancel",         # callback, на который уйдёт «🔙 Выйти»
        title="Выберите сотрудника для выполнения",
        page=1,
        per_page=5                     # сколько сотрудников показывать на одной странице
    )

    # 4) Отправляем сообщение с пагинацией
    await message.answer(text, reply_markup=keyboard)

    # 5) Устанавливаем следующий стейт — отлавливать выбор нужно в callback-обработчике
    await state.set_state(OrderStates.waiting_for_employer)


@admins.callback_query(F.data.startswith("item_") & F.data.endswith("_assign"))
async def assign_executor(callback: CallbackQuery, state: FSMContext):
    _, prefix, page_str, emp_id_str = callback.data.split("_", 3)
    emp_id = int(emp_id_str)

    # Извлекаем state один раз
    data = await state.get_data()
    employees = data.get("employees_list", [])

    # Находим выбранного сотрудника
    employee = next(
        (e for e in employees
         if e.get("user_id") == emp_id or e.get("telegram_id") == emp_id),
        None
    )
    if not employee:
        return await callback.answer("Сотрудник не найден.")

    # Сохраняем выбор и переходим к подтверждению
    await state.update_data(assigned_to=emp_id, executor=employee)
    await state.set_state(OrderStates.waiting_for_order_confirmation)

    # Достаём список услуг из state
    services = data.get("service", [])

    # Формируем текст и отсылаем
    text = (
        f"Выбран: {employee['first_name']} {employee['last_name']}\n"
        f"Услуга: {', '.join(services)}\n"
        "Подтвердите заказ-наряд:"
    )
    await callback.message.edit_text(
        text,
        # reply_markup=get_access_confirmation()  # Сделать клавиатуру «Подтвердить/Отменить»
    )


@admins.callback_query(F.data.startswith("employer_"), OrderStates.waiting_for_employer)
async def process_employer_selection(callback: CallbackQuery, state: FSMContext, user: UserContext):
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
        reply_markup=common_kb_by_role("control", user.lang, user.get_role())
    )


@admins.callback_query(F.data == "confirm", OrderStates.waiting_for_order_confirmation)
async def process_confirm(callback: CallbackQuery, state: FSMContext, user: UserContext):
    data = await state.get_data()
    car_id = data["car_id"]
    description = data["service"]
    employees = data["employer"]
    await add_order(car_id=car_id, description=description, worker_id=employees)
    await callback.message.answer("Заказ успешно оформлен!")
    await state.clear()


# @admins.callback_query(F.data == "back")
# async def process_back(callback: CallbackQuery, state: FSMContext, user: UserContext):
#     current_state = await state.get_state()
#
#     if current_state == OrderStates.waiting_for_service:
#         # Возврат к выбору авто
#         user_id = callback.from_user.id
#         cars = await get_client_cars(user_id)
#         text, keyboard = get_paginated_list(cars)
#
#         await callback.message.answer(text, reply_markup=keyboard)
#         await state.set_state(OrderStates.waiting_for_car)
#
#     elif current_state == OrderStates.waiting_for_order_confirmation:
#         # Возврат к выбору услуги
#         await callback.message.answer("Введите работы: Можно список работ через запятую!\n"
#                                       "Также можете в скобках указать цену работ. Пример:\n"
#                                       "рихтовка(цена), ...")
#         await state.set_state(OrderStates.waiting_for_service)
#
#     elif current_state == OrderStates.waiting_for_car:
#         await callback.message.answer("Вы вернулись назад. Введи номер авто или модель.")
#         await state.set_state(OrderStates.waiting_for_car)
#     else:
#         await callback.message.answer("Не удалось вернуться назад — неизвестное состояние.")


@admins.callback_query(F.data == "cancel", OrderStates.waiting_for_order_confirmation)
async def process_cancel_from_confirmation(callback: CallbackQuery, state: FSMContext, user: UserContext):
    await callback.message.answer("Заказ отменен.")
    await state.clear()
